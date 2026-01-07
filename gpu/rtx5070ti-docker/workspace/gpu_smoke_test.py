#!/usr/bin/env python3
import torch
import time

print("torch:", torch.__version__)
print("torch cuda:", torch.version.cuda)

if not torch.cuda.is_available():
    print("CUDA not available -> CPU only")
    raise SystemExit(0)

print("GPU:", torch.cuda.get_device_name(0))

try:
    # Small matmul test
    a = torch.randn(2048, 2048, device="cuda")
    b = torch.randn(2048, 2048, device="cuda")
    torch.cuda.synchronize()

    t0 = time.time()
    c = a @ b
    torch.cuda.synchronize()
    t1 = time.time()

    print("CUDA matmul OK")
    print("Time:", round(t1 - t0, 4), "sec")
except Exception as e:
    print("CUDA op FAILED (likely sm_120 torch mismatch):")
    print(e)
