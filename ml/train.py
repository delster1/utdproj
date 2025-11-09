import torch
from torch.utils.data import DataLoader
from ml.model import AutoEncoder, reconstruction_loss, TrainingConfig
from ml.dataset import RedisSensorDataset

def train():
    cfg = TrainingConfig(epochs=40, batch_size=64)
    dataset = RedisSensorDataset(["HeartRate", "temp", "AccelX","AccelY","AccelZ"], limit=301, augment_factor=20)
    loader = DataLoader(dataset, batch_size=cfg.batch_size, shuffle=True)

    model = AutoEncoder()
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.learning_rate)

    for epoch in range(cfg.epochs):
        total_loss = 0
        for x, _ in loader:
            print("Input batch shape:", x.shape)
            pred = model(x)
            loss = reconstruction_loss(pred, x)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1}/{cfg.epochs}, Loss: {total_loss/len(loader):.4f}")

    torch.save(model.state_dict(), "ml/autoencoder.pth")
    print("Model saved to ml/autoencoder.pth")

if __name__ == "__main__":
    train()

