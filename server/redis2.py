"""Utility helpers for reading and writing sensor logs in Redis.
2
The module wraps basic Redis operations so that other parts of the
codebase can store structured sensor readings without having to worry
about Redis-specific commands.  It exposes a small `SensorLogStore`
class that knows how to push and retrieve JSON encoded readings.
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List, Optional

try:  # pragma: no cover - optional dependency for documentation builds
    import redis
except ImportError as exc:  # pragma: no cover - handled at runtime
    raise ImportError(
        "The `redis` package is required to use server.redis. Install it via\n"
        "`pip install redis` on your development machine."
    ) from exc


@dataclass
class SensorReading:
    """Represents one measurement produced by a physical sensor.

    Attributes
    ----------
    sensor_name:
        Human readable identifier for the sensor (for example "pump_1").
    sensor_output:
        Numeric value produced by the sensor.
    timestamp:
        Moment when the reading was recorded.  A timezone aware UTC
        timestamp keeps downstream processing simple.
    """

    sensor_name: str
    sensor_output: float
    timestamp: datetime

    def to_json(self) -> str:
        """Serialize the reading to a JSON string for storage."""
        payload = {
            "sensor_name": self.sensor_name,
            "sensor_output": self.sensor_output,
            "timestamp": self.timestamp.isoformat(),
        }
        return json.dumps(payload)

    @classmethod
    def from_json( cls, payload: str, sensor_name : str) -> "SensorReading":
        """Restore a :class:`SensorReading` from its JSON representation."""
        data = json.loads(payload)
        print(f"DATA: {data}")
        # timestamp = datetime.fromisoformat(data["timestamp"]).astimezone(timezone.utc)
        timestamp = datetime.now()
        return cls(
            sensor_name=sensor_name,
            sensor_output=float(data),
            timestamp=timestamp,
        )


class SensorLogStore:
    """High level wrapper around Redis lists used for sensor history.

    Each sensor is stored under a dedicated Redis key following the pattern
    ``"{namespace}:{sensor_name}"``.  New readings are pushed to the head of
    the list so that ``LRANGE`` can quickly return the most recent values.
    """

    def __init__(
        self,
        redis_client: Optional["redis.Redis"] = None,
        *,
        namespace: str = "",
    ) -> None:
        self._redis = redis_client or create_redis_client()
        self._namespace = namespace

    # ------------------------------------------------------------------
    # Redis connection helpers
    # ------------------------------------------------------------------
    def _key(self, sensor_name: str) -> str:
        return f"{self._namespace}{sensor_name}"

    def fetch_recent(self, sensor_name: str, limit: int = 256) -> List[SensorReading]:
        """Return the most recent readings for ``sensor_name``.

        Parameters
        ----------
        sensor_name:
            Identifier for the desired sensor.
        limit:
            Maximum number of readings to return.
        """
        for key in self._redis.lrange(self._key(sensor_name), 0, limit - 1):
            print(key)
        raw_entries = self._redis.lrange(self._key(sensor_name), 0, limit - 1)
        print(raw_entries)
        readings = [SensorReading.from_json( entry.decode("utf-8"), sensor_name) for entry in raw_entries]
        # Redis returns items in reverse chronological order because we push to
        # the head of the list.  Reverse them so downstream code sees
        # chronological sequences.
        return list(reversed(readings))


def create_redis_client() -> "redis.Redis":
    """Create a Redis client using environment variables for configuration."""

    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", "6379"))
    db = int(os.getenv("REDIS_DB", "0"))
    password = os.getenv("REDIS_PASSWORD")

    return redis.Redis(host=host, port=port, db=db, password=password, decode_responses=False, username="default")


def reading_from_dict(payload: dict) -> SensorReading:
    """Convenience helper to create readings from plain dictionaries.

    This makes it easy to convert JSON received by ``server.server`` into the
    dataclass used by the training pipeline.
    """

    return SensorReading(
        sensor_name=str(payload["sensor_name"]),
        sensor_output=float(payload["sensor_output"]),
        timestamp=datetime.now(timezone.utc),
    )

def get_latest_sensor_data(redis_host, limit=6):

    sensor_names = ["HeartRate", "Temperature", "AccelX", "AccelY", "AccelZ"]
    my_json = {}

    for sensor_name in sensor_names:
        readings = r.scan_iter("*")
        values = [r.sensor_output for r in readings]
        my_json[sensor_name] = values  # store as array of floats

    return json.dumps({"sensor_outputs": my_json})


__all__ = [
    "SensorReading",
    "SensorLogStore",
    "create_redis_client",
    "reading_from_dict",
]
