import torch
import random

def add_gaussian_noise(x: torch.Tensor, std: float = 0.02) -> torch.Tensor:
    """Add small Gaussian noise to simulate sensor noise."""
    noise = torch.randn_like(x) * std
    return x + noise

def random_scale(x: torch.Tensor, scale_range: tuple = (0.95, 1.05)) -> torch.Tensor:
    """Randomly scale sensor values to simulate calibration drift."""
    scale = random.uniform(*scale_range)
    return x * scale

def random_shift(x: torch.Tensor, shift_range: tuple = (-0.05, 0.05)) -> torch.Tensor:
    """Add small random offset (bias shift)."""
    shift = random.uniform(*shift_range)
    return x + shift

def temporal_jitter(x: torch.Tensor, jitter_strength: int = 3) -> torch.Tensor:
    """Simulate temporal reordering / jitter by rolling samples."""
    if x.ndim == 1:
        shift = random.randint(-jitter_strength, jitter_strength)
        return torch.roll(x, shifts=shift, dims=0)
    return x

def augment_tensor(x: torch.Tensor, n_augments: int = 5) -> torch.Tensor:
    """Generate n_augments synthetic variations of x."""
    augmented = []
    for _ in range(n_augments):
        x_aug = add_gaussian_noise(x)
        x_aug = random_scale(x_aug)
        x_aug = random_shift(x_aug)
        x_aug = temporal_jitter(x_aug)
        augmented.append(x_aug)
    return torch.stack(augmented)

