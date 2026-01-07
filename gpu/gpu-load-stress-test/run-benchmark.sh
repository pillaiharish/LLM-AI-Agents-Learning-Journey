#!/bin/bash
# GPU/CPU Stress Test - Easy Launcher Script
# This script checks dependencies and runs the stress test

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}    GPU/CPU STRESS TEST & BENCHMARK TOOL${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

# Check Python
echo -e "\n${YELLOW}[1/4] Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found!${NC}"
    echo "Please install Python 3.7 or higher:"
    echo "  Ubuntu/Debian: sudo apt-get install python3"
    echo "  Fedora/RHEL:   sudo dnf install python3"
    echo "  Arch:          sudo pacman -S python"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"

# Check nvidia-smi
echo -e "\n${YELLOW}[2/4] Checking NVIDIA drivers...${NC}"
if ! command -v nvidia-smi &> /dev/null; then
    echo -e "${RED}❌ nvidia-smi not found!${NC}"
    echo "Please install NVIDIA drivers:"
    echo "  Ubuntu: sudo apt-get install nvidia-driver-XXX"
    echo "  Or download from: https://www.nvidia.com/download/index.aspx"
    exit 1
fi
GPU_INFO=$(nvidia-smi --query-gpu=gpu_name --format=csv,noheader | head -1)
echo -e "${GREEN}✓ NVIDIA drivers found${NC}"
echo -e "  Detected GPU: ${BLUE}${GPU_INFO}${NC}"

# Check gpu-burn
echo -e "\n${YELLOW}[3/4] Checking gpu-burn...${NC}"
if [ ! -f "gpu-burn/gpu_burn" ]; then
    echo -e "${YELLOW}⚠️  gpu-burn not found. Installing...${NC}"
    
    # Check for build dependencies
    if ! command -v nvcc &> /dev/null; then
        echo -e "${RED}❌ CUDA toolkit (nvcc) not found!${NC}"
        echo "Please install CUDA toolkit:"
        echo "  Ubuntu: sudo apt-get install nvidia-cuda-toolkit"
        echo "  Or download from: https://developer.nvidia.com/cuda-downloads"
        exit 1
    fi
    
    # Clone and build gpu-burn
    if [ ! -d "gpu-burn" ]; then
        git clone https://github.com/wilicc/gpu-burn.git
    fi
    
    cd gpu-burn
    make
    cd ..
    
    if [ -f "gpu-burn/gpu_burn" ]; then
        echo -e "${GREEN}✓ gpu-burn compiled successfully${NC}"
    else
        echo -e "${RED}❌ Failed to compile gpu-burn${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ gpu-burn found${NC}"
fi

# Create logs directory
echo -e "\n${YELLOW}[4/4] Setting up directories...${NC}"
mkdir -p logs
echo -e "${GREEN}✓ logs/ directory ready${NC}"

# Make benchmark script executable
chmod +x benchmark.py

# Ready to run
echo -e "\n${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}    All dependencies satisfied!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"

echo -e "\n${BLUE}Starting benchmark tool...${NC}\n"

# Run the benchmark tool
python3 benchmark.py "$@"
