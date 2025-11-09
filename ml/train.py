from __future__ import annotations

from pathlib import Path

import torch
from torch.utils.data import DataLoader

from ml.dataset import RedisSensorDataset
from ml.model import AutoEncoder, TrainingConfig, reconstruction_loss


MODEL_PATH = Path("ml/autoencoder.pth")


def train() -> None:
    cfg = TrainingConfig(epochs=40, batch_size=64)
    dataset = RedisSensorDataset(
        ["HeartRate", "temp", "AccelX", "AccelY", "AccelZ"],
        limit=301,
        window_size=32,
        stride=1,
        augment_factor=20,
    )
    loader = DataLoader(dataset, batch_size=cfg.batch_size, shuffle=True)

    model = AutoEncoder(input_dim=dataset.input_dim)
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.learning_rate)

    for epoch in range(cfg.epochs):
        total_loss = 0.0
        for batch, _ in loader:
            pred = model(batch)
            loss = reconstruction_loss(pred, batch)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        epoch_loss = total_loss / len(loader)
        print(f"Epoch {epoch + 1}/{cfg.epochs}, Loss: {epoch_loss:.4f}")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"state_dict": model.state_dict(), "input_dim": dataset.input_dim}, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    train()

