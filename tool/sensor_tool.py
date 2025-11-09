from langchain.tools import tool
import torch
from ml.model import AutoEncoder, reconstruction_loss
from server.redis import SensorLogStore
from datetime import datetime, timezone

@tool("detect_anomalies")
def detect_anomalies(sensor_name: str, limit: int = 50) -> str:
    """
    Checks recent sensor readings for anomalies using the trained autoencoder.
    Returns the average reconstruction error and whether it's abnormal.
    """
    store = SensorLogStore()
    readings = store.fetch_recent(sensor_name, limit=limit)
    if not readings:
        return f"No readings found for {sensor_name}"

    model = AutoEncoder()
    model.load_state_dict(torch.load("ml/autoencoder.pth"))
    model.eval()

    X = torch.tensor([[r.sensor_output for r in readings]]).float()
    with torch.no_grad():
        pred = model(X)
        loss = reconstruction_loss(pred, X).item()

    status = "⚠️ anomaly detected" if loss > 0.1 else "✅ normal"
    return f"Sensor {sensor_name}: reconstruction_error={loss:.4f}, status={status}"

