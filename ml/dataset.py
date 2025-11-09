import torch
from torch.utils.data import Dataset
from server.redis import SensorLogStore
from ml.data_augmentor import augment_tensor

class RedisSensorDataset(Dataset):
    def __init__(self, sensor_names, limit=500, augment_factor=10):
        store = SensorLogStore()
        samples = []

        for name in sensor_names:
            print(name)
            readings = store.fetch_recent(name, limit=limit)
            vals = [r.sensor_output for r in readings]
            if len(vals) > 0:
                samples.append(vals)

        
        if not samples:
            raise ValueError("No sensor data found in Redis")

        # transpose → shape [num_samples, num_sensors]
        X = torch.tensor(list(zip(*samples))).float()
        
        augmented = []
        for row in X:
            augmented.append(augment_tensor(row, n_augments=augment_factor))
        augmented = torch.cat(augmented, dim=0)

        self.X = torch.cat([X, augmented], dim=0)
        print(f"Dataset size after augmentation: {len(self.X)}")

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.X[idx]

