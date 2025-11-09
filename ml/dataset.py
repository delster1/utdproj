"""Dataset abstractions used for model training."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

import numpy as np
import torch
from torch.utils.data import Dataset

from server.redis import SensorLogStore, SensorReading


@dataclass
class WindowedSample:
    """Represents a slice of sequential readings and the next expected value."""

    features: np.ndarray
    target: np.ndarray


class RedisSensorDataset(Dataset):
    """Loads sequential sensor data from Redis and prepares training samples.

    The dataset forms sliding windows of ``window_size`` readings and trains the
    model to predict the reading that follows each window.  During inference, a
    high prediction error indicates that the latest data point may be
    anomalous compared to the recent history.
    """

    def __init__(
        self,
        store: SensorLogStore,
        sensor_name: str,
        *,
        window_size: int = 5,
        sequence_length: int = 512,
    ) -> None:
        self.window_size = window_size
        self.sensor_name = sensor_name
        readings = store.fetch_recent(sensor_name, limit=sequence_length)
        self.samples = self._build_samples(readings)

    def _build_samples(self, readings: Sequence[SensorReading]) -> List[WindowedSample]:
        if len(readings) <= self.window_size:
            raise ValueError(
                "Not enough readings to build a dataset. Generate more synthetic data "
                "or reduce `window_size`."
            )

        values = np.asarray([reading.sensor_output for reading in readings], dtype=np.float32)
        features: List[np.ndarray] = []
        targets: List[np.ndarray] = []
        for start in range(len(values) - self.window_size):
            end = start + self.window_size
            features.append(values[start:end])
            targets.append(np.asarray([values[end]], dtype=np.float32))
        return [WindowedSample(feature, target) for feature, target in zip(features, targets)]

    # ------------------------------------------------------------------
    # PyTorch dataset protocol
    # ------------------------------------------------------------------
    def __len__(self) -> int:  # pragma: no cover - thin wrapper
        return len(self.samples)

    def __getitem__(self, index: int) -> Tuple[torch.Tensor, torch.Tensor]:
        sample = self.samples[index]
        features = torch.from_numpy(sample.features)
        target = torch.from_numpy(sample.target)
        return features, target


def numpy_batch(batch: Iterable[Tuple[torch.Tensor, torch.Tensor]]) -> Tuple[np.ndarray, np.ndarray]:
    """Convert a batch of PyTorch tensors back into NumPy arrays.

    This is helpful for quickly debugging model inputs and outputs without
    writing the tensors to disk.
    """

    features, targets = zip(*batch)
    return (
        torch.stack(list(features)).cpu().numpy(),
        torch.stack(list(targets)).cpu().numpy(),
    )


__all__ = ["RedisSensorDataset", "WindowedSample", "numpy_batch"]
