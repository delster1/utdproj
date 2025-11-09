from __future__ import annotations

import time
import argparse
import json
import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence

from langchain_nvidia_ai_endpoints import ChatNVIDIA

from tool.sensor_tool import detect_anomalies, sensor_data_retriever

DEFAULT_MODEL = "nvidia/nvidia-nemotron-nano-9b-v2"

SYSTEM_PROMPT = """
You are an agent that monitors sensors. 
You have access to tools:
- sensor_data_retriever(sensor_name): gets data for a given sensor.
- detect_anomalies(sensor_name): detects anomalies in a sensor's data.

When asked for a summary or to analyze something, always specify which sensor to use.
Example:
Call `sensor_data_retriever(sensor_name="HeartRate")`.
Your options for sensor names are HeartRate, AccelY, Temp, AccelX, and AccelZ you must choose one whenever you analyze something.
"""



def _coerce_content(message: Any) -> str:
    """Extract a string body from LangChain chat model responses."""

    if isinstance(message, str):
        return message

    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content

    if isinstance(content, Iterable):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, Mapping):
                text = item.get("text")
                if text:
                    parts.append(str(text))
            else:
                parts.append(str(item))
        return "".join(parts)

    return str(content)


def _extract_json_object(payload: str) -> Optional[Dict[str, Any]]:
    """Locate the first JSON object inside ``payload`` and parse it."""

    text = payload.strip()
    if text.startswith("```"):
        # Strip fenced code blocks such as ```json { ... }
        text = re.sub(r"^```\w*", "", text)
        text = text.strip("`\n ")

    if text.startswith("{") and text.endswith("}"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

    return None


def _format_tool_summary(event: Mapping[str, Any]) -> str:
    args = event.get("args") or {}
    result = event.get("result")
    reason = event.get("reasoning")

    summary = f"- {event['name']} called with {json.dumps(args, ensure_ascii=False)}"
    if reason:
        summary += f"\n  rationale: {reason}"
    if result is not None:
        summary += f"\n  result: {str(result)[:500]}"
    return summary


@dataclass
class SimpleReactiveAgent:
    """A minimal agent that can decide when to call tools."""

    llm: ChatNVIDIA
    tools: Dict[str, Any]
    system_prompt: str
    max_iterations: int = 3

    def run(self, question: str) -> str:
        """Answer ``question`` using the configured tools when helpful."""

        events: list[Dict[str, Any]] = []

        for _ in range(self.max_iterations):
            prompt = self._build_prompt(question, events)
            response = _coerce_content(self.llm.invoke(prompt))
            payload = _extract_json_object(response)

            if not payload:
                # The LLM ignored the instructions – return the raw text.
                return response.strip()

            action = str(payload.get("action", "")).strip()
            content = str(payload.get("content", "")).strip()

            if action == "final":
                return content or response.strip()

            if action in self.tools:
                args = payload.get("args") or {}
                event: Dict[str, Any] = {"name": action, "args": args}
                if content:
                    event["reasoning"] = content

                try:
                    result = self._invoke_tool(action, args)
                except Exception as exc:  # pragma: no cover - defensive branch
                    result = f"Tool execution failed: {exc}"

                event["result"] = str(result)
                events.append(event)
                continue

            # Unknown action – fall back to whatever prose the model produced.
            return content or response.strip()

        return (
            "Unable to complete the request within the allotted tool calls. "
            "Please try asking a more specific question."
        )

    def invoke(self, query: Any) -> str:
        """Compatibility wrapper for LangChain-style calls."""

        if isinstance(query, Mapping):
            if "input" in query:
                return self.run(str(query["input"]))
            if "messages" in query:
                return self.run(str(query["messages"]))

        return self.run(str(query))

    async def ainvoke(self, query: Any) -> str:  # pragma: no cover - simple passthrough
        return self.invoke(query)

    def _build_prompt(self, question: str, events: Sequence[Mapping[str, Any]]) -> str:
        lines = [self.system_prompt.strip(), "", "Available tools:"]

        for name, tool in self.tools.items():
            description = getattr(tool, "description", "") or "(no description provided)"
            lines.append(f"- {name}: {description}")

        lines.extend(
            [
                "",
                "You follow a two phase loop: (1) decide whether a tool is required,",
                "(2) call a tool or provide the final answer.",
            ]
        )

        if events:
            lines.append("")
            lines.append("Tool results collected so far:")
            for event in events:
                lines.append(_format_tool_summary(event))

        lines.extend(
            [
                "",
                f"User question: {question}",
                "",
                "Respond strictly as JSON with keys 'action', 'content', and optional 'args'.",
                "Set 'action' to one of the tool names when requesting a tool,",
                "otherwise respond with 'final'. Use 'content' to explain your reasoning",
                "or to deliver the final answer. When calling a tool, include all required",
                "arguments inside 'args'.",
            ]
        )

        return "\n".join(lines)

    def _invoke_tool(self, name: str, args: Any) -> Any:
        tool = self.tools[name]
        func = getattr(tool, "func", tool)

        if isinstance(args, Mapping):
            kwargs: Dict[str, Any] = dict(args)
            return func(**kwargs)

        if isinstance(args, Sequence) and not isinstance(args, (str, bytes, bytearray)):
            return func(*args)

        if args in (None, ""):
            return func()

        return func(args)


def build_agent(*, max_iterations: int = 3, model: Optional[str] = None) -> SimpleReactiveAgent:
    llm = ChatNVIDIA(model=model or DEFAULT_MODEL, temperature=0.6)
    tool_map = {tool.name: tool for tool in (sensor_data_retriever, detect_anomalies)}
    return SimpleReactiveAgent(
        llm=llm,
        tools=tool_map,
        system_prompt=SYSTEM_PROMPT,
        max_iterations=max_iterations,
    )


AGENT = build_agent()


def main() -> None:
    parser = argparse.ArgumentParser(description="Continuously monitor sensors.")
    parser.add_argument("--interval", type=int, default=10,
                        help="Polling interval in seconds.")
    parser.add_argument("--max-steps", type=int, default=3,
                        help="Maximum number of tool invocations per cycle.")
    args = parser.parse_args()

    sensors = ["HeartRate", "AccelY", "Temp", "AccelX", "AccelZ"]
    agent = build_agent(max_iterations=args.max_steps)

    print("🔁 Starting continuous sensor monitoring...\n")
    while True:
        for sensor in sensors:
            question = f"Summarize the most recent status for {sensor}."
            try:
                answer = agent.run(question)
                print(f"\n[{sensor}] {answer}")
            except Exception as exc:
                print(f"⚠️ Error on {sensor}: {exc}")
        time.sleep(args.interval)

if __name__ == "__main__":  # pragma: no cover
    main()

