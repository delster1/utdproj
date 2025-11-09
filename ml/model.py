"""Neural network architectures used for sensor forecasting and anomaly detection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import torch
from torch import nn


def _build_mlp(dims: Sequence[int]) -> nn.Sequential:
    """Create a simple feed-forward network following ``dims`` dimensions."""

    layers = []
    for in_features, out_features in zip(dims[:-1], dims[1:]):
        layers.append(nn.Linear(in_features, out_features))
    return nn.Sequential(*layers)



class AutoEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(5, 8),
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
            nn.Linear(8, 5)
        )

    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z)


    def forward(self, x: torch.Tensor) -> torch.Tensor:  # noqa: D401 - standard forward
        """Encode ``x`` into the latent space and reconstruct it."""

        latent = self.encoder(x)
        return self.decoder(latent)


def reconstruction_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """Mean squared reconstruction error used for training and scoring."""

    mse = torch.mean((pred - target) ** 2)
    mae = torch.mean(torch.abs(pred - target))
    return mse + 0.1 * mae


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
    "AutoEncoder",
    "TrainingConfig",
    "anomaly_score",
    "count_parameters",
]
