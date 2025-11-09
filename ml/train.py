from __future__ import annotations

from pathlib import Path

import torch
from torch.utils.data import DataLoader

from ml.dataset import RedisSensorDataset
from ml.model import AutoEncoder, TrainingConfig, reconstruction_loss


MODEL_PATH = Path("ml/autoencoder.pth")


def train() -> None:
    cfg = TrainingConfig(epochs=500, batch_size=64)
    dataset = RedisSensorDataset(
        ["HeartRate", "temp", "AccelX", "AccelY", "AccelZ"],
        limit=301,
    )
    loader = DataLoader(dataset, batch_size=cfg.batch_size, shuffle=True)

    model = AutoEncoder()
    try:
        checkpoint = torch.load("ml/autoencoder.pth", map_location="cuda" if torch.cuda.is_available() else "cpu")
        model.load_state_dict(checkpoint["state_dict"])
        print("successfully loaded")
    except Exception as e:
        pass
        # raise Exception("couldnt load balls", e)
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

    model.eval()
    torch.save({"state_dict": model.state_dict() }, "ml/autoencoder.pth")
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    train()

