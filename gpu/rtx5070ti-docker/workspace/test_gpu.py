#!/usr/bin/env python3
import torch
import sys

print("=" * 60)
print("GPU Test in Docker Container")
print("=" * 60)

print(f"\nPyTorch Version: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA Version: {torch.version.cuda}")
    print(f"Number of GPUs: {torch.cuda.device_count()}")

    print(f"\nGPU 0: {torch.cuda.get_device_name(0)}")
    print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

    print("\nTesting GPU computation...")
    x = torch.randn(1000, 1000, device="cuda")
    y = torch.randn(1000, 1000, device="cuda")
    z = x @ y
    print("✓ Matrix multiplication successful!")

    print(f"\nCurrent GPU Memory Allocated: {torch.cuda.memory_allocated(0) / 1e6:.2f} MB")
    print("\n✅ GPU is working correctly in Docker!")
else:
    print("\n❌ CUDA not available. Check Docker GPU setup.")
    sys.exit(1)
