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
        # Skip the activation on the final layer – the caller decides.
        if out_features != dims[-1]:
            layers.append(nn.ReLU())
    return nn.Sequential(*layers)


class AutoEncoder(nn.Module):
    """A compact autoencoder that adapts to the dimensionality of the data."""

    def __init__(self, input_dim: int, hidden_dims: Iterable[int] | None = None) -> None:
        super().__init__()
        if input_dim <= 0:
            raise ValueError("input_dim must be a positive integer")

        if hidden_dims is None:
            # Create a small pyramid that halves the dimensionality at each step.
            hidden_dims = []
            width = input_dim
            while width > 3:
                width = max(width // 2, 2)
                hidden_dims.append(width)
            if not hidden_dims:
                hidden_dims = [max(input_dim // 2, 1)]
        else:
            hidden_dims = [int(d) for d in hidden_dims if int(d) > 0]
            if not hidden_dims:
                raise ValueError("hidden_dims must contain positive integers")

        encoder_dims = [input_dim, *hidden_dims]
        decoder_dims = [hidden_dims[-1], *reversed(hidden_dims[:-1]), input_dim]

        self.encoder = _build_mlp(encoder_dims)
        self.decoder = _build_mlp(decoder_dims)

    def forward(self, x: torch.Tensor) -> torch.Tensor:  # noqa: D401 - standard forward
        """Encode ``x`` into the latent space and reconstruct it."""

        latent = self.encoder(x)
        return self.decoder(latent)


def reconstruction_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """Mean squared reconstruction error used for training and scoring."""

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
    "AutoEncoder",
    "TrainingConfig",
    "anomaly_score",
    "count_parameters",
]
