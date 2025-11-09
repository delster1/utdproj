import asyncio, time
from server.redis import SensorLogStore
from ml.model import AutoEncoder, anomaly_score
from ml.rag_memory import VectorMemory  # you'll write this
from datetime import datetime, timezone

async def monitor_sensors(model, memory, interval=5):
    store = SensorLogStore()
    while True:
        for sensor in ["HeartRate", "Temp", "AccelX", "AccelY", "AccelZ"]:
            readings = store.fetch_recent(sensor, limit=64)
            values = [r.sensor_output for r in readings]
            if not values: continue

            x = torch.tensor(values, dtype=torch.float32)
            with torch.no_grad():
                recon = model(x)
                score = anomaly_score(recon, x).mean().item()

            memory.add_entry(sensor, score, values, datetime.now(timezone.utc))
            if score > 0.1:  # adjust threshold
                print(f"🚨 Detected anomaly in {sensor}: {score:.4f}")
                # Trigger the agent to analyze context
                agent.invoke({"input": f"Analyze {sensor} with anomaly score {score}"})
        await asyncio.sleep(interval)

