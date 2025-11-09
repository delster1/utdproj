"""Synthetic data generation utilities for sensor experimentation.

The goal of this module is twofold:

1. Provide quick helpers for producing realistic sensor streams when we do
   not yet have access to hardware measurements.
2. Offer a simple path for seeding Redis with predictable values so that the
   training code can be exercised end-to-end on a new machine.

The functions intentionally use friendly naming and extensive docstrings so
that new collaborators can understand how the pieces fit together without a
strong data science background.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Sequence

import numpy as np

from server.redis import SensorLogStore, SensorReading


@dataclass
class SensorSpec:
    """Describes the healthy operating range of a physical sensor."""

    name: str
    mean: float
    std_dev: float
    minimum: float
    maximum: float

    def sample(self) -> float:
        """Draw a random value that respects the configured limits."""

        value = random.gauss(self.mean, self.std_dev)
        return float(np.clip(value, self.minimum, self.maximum))


DEFAULT_SENSORS: Dict[str, SensorSpec] = {
    "temperature": SensorSpec("temperature", mean=65.0, std_dev=1.5, minimum=60.0, maximum=70.0),
    "pressure": SensorSpec("pressure", mean=32.5, std_dev=0.8, minimum=30.0, maximum=35.0),
    "humidity": SensorSpec("humidity", mean=40.0, std_dev=3.0, minimum=30.0, maximum=50.0),
}


def generate_readings(
    *,
    sensors: Sequence[SensorSpec] = tuple(DEFAULT_SENSORS.values()),
    samples_per_sensor: int = 128,
) -> List[SensorReading]:
    """Generate a batch of synthetic readings.

    Each reading carries the current UTC timestamp so that the resulting data
    looks similar to what the live system will produce.
    """

    now = datetime.now(timezone.utc)
    readings: List[SensorReading] = []
    for sensor in sensors:
        for _ in range(samples_per_sensor):
            readings.append(
                SensorReading(
                    sensor_name=sensor.name,
                    sensor_output=sensor.sample(),
                    timestamp=now,
                )
            )
    return readings


def seed_redis_with_synthetic_data(
    store: SensorLogStore,
    *,
    sensors: Sequence[SensorSpec] = tuple(DEFAULT_SENSORS.values()),
    samples_per_sensor: int = 128,
) -> None:
    """Populate Redis so that model training can start immediately.

    Parameters
    ----------
    store:
        Instance of :class:`~server.redis.SensorLogStore` used to push data.
    sensors:
        Collection of :class:`SensorSpec` definitions that describe the target
        sensors.  Defaults to three simple specs that cover temperature,
        pressure, and humidity.
    samples_per_sensor:
        Number of readings to generate for each sensor.
    """

    readings = generate_readings(sensors=sensors, samples_per_sensor=samples_per_sensor)
    store.bulk_push(readings)


def rolling_window(values: Sequence[float], window_size: int) -> Iterable[Sequence[float]]:
    """Yield consecutive windows of ``window_size`` from ``values``."""

    for start in range(0, len(values) - window_size + 1):
        yield values[start : start + window_size]


def sample_training_windows(
    readings: Sequence[SensorReading],
    *,
    window_size: int = 5,
) -> np.ndarray:
    """Convert raw readings into a 2D NumPy array of sliding windows.

    This helper is useful for quickly checking how a sensor sequence will be
    consumed by the neural network.  Each row of the returned array contains
    ``window_size`` consecutive readings.
    """

    values = [reading.sensor_output for reading in readings]
    windows = list(rolling_window(values, window_size))
    return np.asarray(windows, dtype=np.float32)


__all__ = [
    "SensorSpec",
    "DEFAULT_SENSORS",
    "generate_readings",
    "seed_redis_with_synthetic_data",
    "rolling_window",
    "sample_training_windows",
]
