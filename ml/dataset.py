from __future__ import annotations

from typing import Iterable, List

import torch
from torch.utils.data import Dataset

from ml.data_augmentor import augment_tensor
from server.redis import SensorLogStore


class RedisSensorDataset(Dataset):
    """Create sliding windows of sensor readings fetched from Redis."""

    def __init__(
        self,
        sensor_names: Iterable[str],
        *,
        limit: int = 500,
        window_size: int = 32,
        stride: int = 1,
        augment_factor: int = 10,
    ) -> None:
        store = SensorLogStore()
        windows: List[torch.Tensor] = []

        for name in sensor_names:
            readings = store.fetch_recent(name, limit=limit)
            values = torch.tensor([r.sensor_output for r in readings], dtype=torch.float32)
            if len(values) < window_size:
                continue
            # ``unfold`` creates a view of size [num_windows, window_size]
            sensor_windows = values.unfold(0, window_size, stride).contiguous()
            windows.append(sensor_windows)

        if not windows:
            raise ValueError("No sensor data found in Redis with enough history for the chosen window size")

        X = torch.cat(windows, dim=0)

        if augment_factor > 0:
            augmented = torch.cat([augment_tensor(row, n_augments=augment_factor) for row in X], dim=0)
            self.X = torch.cat([X, augmented], dim=0)
        else:
            self.X = X

        self.window_size = window_size
        self.input_dim = self.X.shape[1]

    def __len__(self) -> int:
        return len(self.X)

    def __getitem__(self, idx: int):
        sample = self.X[idx]
        return sample, sample

