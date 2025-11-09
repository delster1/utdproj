# ml/rag_agent.py
from langgraph.prebuilt import create_react_agent
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from tool.sensor_tool import detect_anomalies
from tool.sensor_tool import sensor_data_retriever  # from before

llm = ChatNVIDIA(model="nvidia/nvidia-nemotron-nano-9b-v2", temperature=0.6)
SYSTEM_PROMPT = (
    "You are a diagnostic AI monitoring system.\n"
    "- Use 'sensor_data_retriever' to see current values.\n"
    "- Use 'detect_anomalies' to check for abnormal behavior.\n"
    "- Correlate multiple sensor readings when reasoning.\n"
    "- Respond with concise technical summaries."
)

AGENT = create_react_agent(
    model=llm,
    tools=[sensor_data_retriever, detect_anomalies],
    prompt=SYSTEM_PROMPT,
)

