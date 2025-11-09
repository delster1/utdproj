"""Neural network architectures used for sensor forecasting."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple

import torch
from torch import nn


class SensorPredictor(nn.Module):
    """A lightweight feed-forward network for sequence forecasting.

    The model receives a vector of ``window_size`` consecutive readings and
    predicts the next reading.  Two fully-connected hidden layers keep the
    network easy to train on commodity GPUs while still being expressive enough
    to model gradual sensor drift.
    """

    def __init__(self, window_size: int, hidden_size: int = 64) -> None:
        super().__init__()
        self.window_size = window_size
        self.hidden_size = hidden_size

        self.net = nn.Sequential(
            nn.Linear(window_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, 1),
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:  # pragma: no cover - trivial wrapper
        return self.net(features)


@dataclass
class TrainingConfig:
    """Groups common hyperparameters for readability."""

    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    epochs: int = 10
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
