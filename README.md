# Sensor Analytics Starter Kit

This repository now provides everything required to capture sensor readings,
store them in Redis, and train a simple forecasting model that can highlight
anomalous behaviour.  The code is split into two main areas:

* `server/` – Flask endpoints and Redis helpers for receiving and persisting
  sensor telemetry.
* `ml/` – Synthetic data generation utilities together with a PyTorch training
  pipeline that can run on GPU-enabled machines such as your Vultr instance.

## How the pieces work together

1. **Sensor ingestion**: Hardware devices send JSON payloads to the Flask app
   (`server/server.py`).  Each payload is converted into a structured
   `SensorReading` and stored in Redis using the helpers from `server/redis.py`.
2. **Synthetic bootstrapping**: When no real data is available you can generate
   realistic streams of readings with `ml.data_generation.seed_redis_with_synthetic_data`.
   This keeps the rest of the pipeline working while hardware and wiring are
   still being finalised.
3. **Model training**: `ml/train.py` loads the recent Redis history, forms small
   sliding windows of readings, and teaches a lightweight neural network to
   predict the next value.  Large prediction errors become a signal that the
   sensor is operating outside its usual range.

The following diagram summarises the flow:

```
Sensors → Flask receiver → Redis (sensor history) → PyTorch model training
                ↑                                  ↓
         Synthetic data generator        Forecasting + anomaly scores
```

## Getting started

1. **Install dependencies**

   ```bash
   pip install flask redis torch numpy requests
   ```

2. **(Optional) Generate baseline data**

   ```bash
   python -m ml.train --bootstrap --samples 512
   ```

   The `--bootstrap` flag asks the script to create generic temperature,
   pressure, and humidity readings before training.  Feel free to customise the
   defaults in `ml/data_generation.py` to match your hardware envelope.

3. **Train on a GPU node**

   ```bash
   python -m ml.train --sensor temperature --epochs 20 --checkpoint checkpoints/temp.pt
   ```

   The script automatically detects CUDA availability, so running it on your
   Vultr GPU instance will offload the heavy lifting.  The optional
   `--checkpoint` argument stores the trained weights for later inference.

## Understanding the model

* `ml/model.py` defines `SensorPredictor`, a three-layer fully connected network
  that balances simplicity and expressive power.
* `ml/dataset.py` pulls time ordered readings from Redis and turns them into
  supervised training examples (historical window → next reading).
* `ml/train.py` contains a compact training loop with verbose print-outs so you
  can monitor loss values without additional tooling.
* `ml/data_generation.py` lets you generate synthetic telemetry while fine-tuning
  sensor ranges.  The `SensorSpec` dataclass keeps the configuration readable.

All modules are documented with docstrings and comments aimed at readers who
may be new to machine learning, making this codebase a friendly starting point
for experimentation.
