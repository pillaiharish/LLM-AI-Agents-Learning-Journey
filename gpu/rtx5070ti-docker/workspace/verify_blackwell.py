#!/usr/bin/env python3
import torch

print("=" * 70)
print("BLACKWELL / sm_120 VERIFICATION")
print("=" * 70)

print("torch:", torch.__version__)
print("torch.version.cuda:", torch.version.cuda)
print("cuda available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("gpu:", torch.cuda.get_device_name(0))
    print("capability:", torch.cuda.get_device_capability(0))
    print("arch list:", torch.cuda.get_arch_list())
    print("\nTip: For RTX 50-series (Blackwell), you want arch list to include sm_120.")
else:
    print("\nCUDA is not available inside the container.")
    print("Check: NVIDIA driver on host + NVIDIA Container Toolkit + docker compose GPU settings.")
