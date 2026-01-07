#!/bin/bash
# Real GPU stress test - push to 300W

echo "Installing GPU stress tools..."
sudo apt-get update -qq
sudo apt-get install -y git build-essential cuda-toolkit-* 2>/dev/null || sudo apt-get install -y git build-essential

# Clone and build gpu-burn (proper CUDA stress test)
if [ ! -d "gpu-burn" ]; then
    git clone https://github.com/wilicc/gpu-burn.git
    cd gpu-burn
    make
    cd ..
fi

echo "Starting AGGRESSIVE GPU stress test..."
echo "Target: Push GPU to 300W for 2 minutes"
echo ""

# Start gpu-burn in background for 2 minutes
cd gpu-burn
./gpu_burn 120 &
GPU_BURN_PID=$!
cd ..

echo "GPU stress started (PID: $GPU_BURN_PID)"
echo "Monitoring for 2 minutes..."
