from torch.utils.data import Dataset
import torch
from server.redis import SensorLogStore

class RedisSensorDataset(Dataset):
    def __init__(self, sensor_names, limit=256, augment_factor=1):
        self.store = SensorLogStore()
        self.sensor_names = sensor_names
        self.limit = limit
        self.augment_factor = augment_factor
        self.samples = self._load_data()

    def _load_data(self):
        print(f"📡 Fetching {self.limit} samples for sensors: {self.sensor_names}")
        data = []

        # Fetch aligned data for all sensors
        all_series = {}
        for name in self.sensor_names:
            readings = self.store.fetch_recent(name, limit=self.limit)
            all_series[name] = [r.sensor_output for r in readings]

        # Ensure all sensors returned data
        empty_sensors = [s for s, v in all_series.items() if len(v) == 0]
        if empty_sensors:
            print(f"⚠️ Warning: No data for sensors: {empty_sensors}")
        
        valid_lengths = [len(v) for v in all_series.values() if len(v) > 0]
        if not valid_lengths:
            print("❌ No valid data found in Redis — returning dummy dataset.")
            return torch.randn(100, len(self.sensor_names))  # fallback fake data

        min_len = min(valid_lengths)
        print(f"✅ Aligned to {min_len} samples across sensors.")

        # Construct feature matrix
        for i in range(min_len):
            row = [all_series[name][i] if i < len(all_series[name]) else 0.0 for name in self.sensor_names]
            data.append(row)

        data = torch.tensor(data, dtype=torch.float32)
        return data

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx], 0

