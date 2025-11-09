"""Entry point for training the starter forecasting model.

The script intentionally keeps the training loop compact so it can serve as a
reference for teammates who may be new to machine learning.  A typical workflow
looks like this:

1. Use :func:`ml.data_generation.seed_redis_with_synthetic_data` to populate
   Redis with baseline sensor readings.
2. Run this script on a GPU-enabled machine (for example the Vultr instance).
3. Inspect the logged loss values and adjust hyperparameters as needed.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from ml.data_generation import DEFAULT_SENSORS, seed_redis_with_synthetic_data
from ml.dataset import RedisSensorDataset
from ml.model import SensorPredictor, TrainingConfig
from server.redis import SensorLogStore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the sensor forecasting model.")
    parser.add_argument(
        "sensor",
        help="Name of the sensor to train on. Defaults to 'temperature'.",
        nargs="?",
        default="temperature",
    )
    parser.add_argument("--window-size", type=int, default=5, help="Number of readings per input window.")
    parser.add_argument("--epochs", type=int, default=10, help="Training epochs to run.")
    parser.add_argument("--batch-size", type=int, default=64, help="Mini-batch size.")
    parser.add_argument("--learning-rate", type=float, default=1e-3, help="Optimizer learning rate.")
    parser.add_argument("--weight-decay", type=float, default=1e-4, help="L2 weight decay regularization.")
    parser.add_argument("--bootstrap", action="store_true", help="Generate synthetic data before training.")
    parser.add_argument(
        "--samples",
        type=int,
        default=256,
        help="Number of synthetic readings to generate per sensor when --bootstrap is used.",
    )
    parser.add_argument(
        "--sequence-length",
        type=int,
        default=1024,
        help="Maximum number of readings to pull from Redis for training.",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="Optional path for saving the trained model weights.",
    )
    return parser.parse_args()


def maybe_seed_redis(store: SensorLogStore, *, bootstrap: bool, samples: int) -> None:
    if not bootstrap:
        return
    print(f"[bootstrap] Generating {samples} readings per sensor…")
    seed_redis_with_synthetic_data(store, sensors=tuple(DEFAULT_SENSORS.values()), samples_per_sensor=samples)


def create_dataloader(
    store: SensorLogStore,
    sensor_name: str,
    *,
    window_size: int,
    batch_size: int,
    sequence_length: int,
) -> DataLoader:
    dataset = RedisSensorDataset(
        store,
        sensor_name,
        window_size=window_size,
        sequence_length=sequence_length,
    )
    return DataLoader(dataset, batch_size=batch_size, shuffle=True)


def train_one_epoch(
    model: SensorPredictor,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: torch.nn.Module,
    device: torch.device,
) -> float:
    model.train()
    running_loss = 0.0
    for features, target in loader:
        features = features.to(device)
        target = target.to(device)

        optimizer.zero_grad()
        prediction = model(features)
        loss = criterion(prediction, target)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * features.size(0)
    return running_loss / len(loader.dataset)


def main() -> None:
    args = parse_args()

    store = SensorLogStore()
    maybe_seed_redis(store, bootstrap=args.bootstrap, samples=args.samples)

    dataloader = create_dataloader(
        store,
        args.sensor,
        window_size=args.window_size,
        batch_size=args.batch_size,
        sequence_length=args.sequence_length,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    model = SensorPredictor(window_size=args.window_size)
    model.to(device)

    config = TrainingConfig(
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        epochs=args.epochs,
        batch_size=args.batch_size,
    )

    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
    criterion = torch.nn.MSELoss()

    for epoch in range(1, config.epochs + 1):
        loss = train_one_epoch(model, dataloader, optimizer, criterion, device)
        print(f"Epoch {epoch}/{config.epochs} - loss: {loss:.6f}")

    if args.checkpoint:
        args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
        torch.save(model.state_dict(), args.checkpoint)
        print(f"Saved checkpoint to {args.checkpoint}")


if __name__ == "__main__":
    main()
