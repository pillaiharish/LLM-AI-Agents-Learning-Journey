#!/bin/bash
# Quick setup script for Linux systems

echo "=========================================="
echo "Stress Test Setup for Linux"
echo "=========================================="
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install:"
    echo "   sudo apt-get install python3"
    exit 1
fi
echo "✓ Python 3 found"

# Check for nvidia-smi
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ nvidia-smi not found. Please install NVIDIA drivers"
    exit 1
fi
echo "✓ nvidia-smi found"

# Check for sensors
if ! command -v sensors &> /dev/null; then
    echo "⚠️  lm-sensors not found. Installing..."
    sudo apt-get update
    sudo apt-get install -y lm-sensors
    sudo sensors-detect --auto
fi
echo "✓ lm-sensors configured"

# Create logs directory
mkdir -p logs
echo "✓ Logs directory created"

# Test sensors
echo ""
echo "Testing sensor reading..."
sensors | grep -i "temp\|fan" | head -5

echo ""
echo "Testing GPU query..."
nvidia-smi --query-gpu=temperature.gpu,power.draw --format=csv,noheader,nounits

echo ""
echo "=========================================="
echo "✓ Setup complete!"
echo "=========================================="
echo ""
echo "Download stress test tools:"
echo "  • Prime95: https://www.mersenne.org/download/"
echo "  • FurMark: https://geeks3d.com/furmark/"
echo ""
echo "Then run: python3 stress_test_monitor.py"
