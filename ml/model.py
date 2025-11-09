"""Neural network architectures used for sensor forecasting."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple

import torch
from torch import nn, optim
from torchvision import datasets, transforms
import matplotlib.pyplot as plt

class AutoEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(4, 8),
            nn.ReLU(),
            nn.Linear(8, 4),
            nn.ReLU(),
            nn.Linear(4, 2)   # latent bottleneck
        )
        self.decoder = nn.Sequential(
            nn.Linear(2, 4),
            nn.ReLU(),
            nn.Linear(4, 8),
            nn.ReLU(),
            nn.Linear(8, 4),
        )

    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z)

def reconstruction_loss(pred, target):
    return torch.mean((pred - target) ** 2)


@dataclass
class TrainingConfig:
    """Groups common hyperparameters for readability."""

    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    epochs: int = 100
    batch_size: int = 64


def anomaly_score(predictions: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
    """Compute a simple anomaly score based on absolute prediction error."""

    return (predictions - targets).abs()


def count_parameters(model: nn.Module) -> int:
    """Return the number of trainable parameters."""

    return sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)


__all__ = [
    "SensorPredictor",
    "TrainingConfig",
    "anomaly_score",
    "count_parameters",
]
