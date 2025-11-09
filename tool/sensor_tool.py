from __future__ import annotations

from datetime import timezone
from pathlib import Path
from typing import Tuple

import torch
from langchain.tools import tool

from ml.model import AutoEncoder, reconstruction_loss
from server.redis2 import SensorLogStore


MODEL_PATH = Path("ml/autoencoder.pth")
DEFAULT_THRESHOLD = 0.1


def _load_model() -> Tuple[AutoEncoder, int]:
    checkpoint = torch.load(MODEL_PATH, map_location="cpu")

    if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
        state_dict = checkpoint["state_dict"]
        input_dim = int(checkpoint.get("input_dim") or next(iter(state_dict.values())).shape[1])
    else:  # Backwards compatibility with older checkpoints that only stored weights.
        state_dict = checkpoint
        first_layer_weight = next(iter(state_dict.values()))
        input_dim = int(first_layer_weight.shape[1])

    model = AutoEncoder(input_dim=input_dim)
    model.load_state_dict(state_dict)
    model.eval()
    return model, input_dim


def _prepare_window(values: torch.Tensor, window_size: int) -> torch.Tensor:
    if len(values) >= window_size:
        window = values[-window_size:]
    elif len(values) > 0:
        pad_value = values[-1]
        padding = pad_value.repeat(window_size - len(values))
        window = torch.cat([padding, values])
    else:
        window = torch.zeros(window_size)
    return window.unsqueeze(0)


@tool("detect_anomalies")
def detect_anomalies(sensor_name: str, limit: int = 128) -> str:
    """Check recent readings for anomalies using the trained autoencoder."""

    if not MODEL_PATH.exists():
        return "No trained autoencoder found. Please run `ml/train.py` first."

    store = SensorLogStore()
    readings = store.fetch_recent(sensor_name, limit=limit)
    if not readings:
        return f"No readings found for {sensor_name}"

    model, input_dim = _load_model()
    values = torch.tensor([r.sensor_output for r in readings], dtype=torch.float32)
    batch = _prepare_window(values, input_dim)

    with torch.no_grad():
        reconstruction = model(batch)
        loss = reconstruction_loss(reconstruction, batch).item()

    if loss > DEFAULT_THRESHOLD:
        status = "⚠️ anomaly detected" 
        os.environ["ANOMALY_STATUS"] = "1"
    else:
        os.environ["ANOMALY_STATUS"] = "0"
        status = "✅ normal"
    latest_timestamp = readings[-1].timestamp
    if latest_timestamp.tzinfo is None:
        latest_timestamp = latest_timestamp.replace(tzinfo=timezone.utc)
    else:
        latest_timestamp = latest_timestamp.astimezone(timezone.utc)
    return (
        f"Sensor {sensor_name} @ {latest_timestamp.isoformat()}: "
        f"reconstruction_error={loss:.4f}, status={status}"
    )

@tool("sensor_data_retriever")
def sensor_data_retriever(sensor_name: str, limit: int = 10) -> str:
    """Return a compact table with the latest sensor readings."""

    store = SensorLogStore()
    readings = store.fetch_recent(sensor_name, limit=limit)
    if not readings:
        return f"No readings found for {sensor_name}"

    lines = ["timestamp,value"]
    for reading in readings[-limit:]:
        timestamp = reading.timestamp
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        else:
            timestamp = timestamp.astimezone(timezone.utc)
        lines.append(f"{timestamp.isoformat()},{reading.sensor_output:.4f}")
    return "\n".join(lines)

