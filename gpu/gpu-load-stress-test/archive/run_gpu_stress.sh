#!/bin/bash
# Quick GPU Stress Test Runner
# This script uses glmark2 as a free GPU stress test tool for Linux

echo "=========================================="
echo "GPU Stress Test Quick Start"
echo "=========================================="
echo ""

# Check if glmark2 is installed
if ! command -v glmark2 &> /dev/null; then
    echo "Installing glmark2 (free OpenGL benchmark/stress tool)..."
    sudo apt-get update
    sudo apt-get install -y glmark2
fi

echo "Starting GPU stress test in 5 seconds..."
echo "The monitor script will track safety and stop if needed."
echo ""
echo "To stop: Press Ctrl+C in the monitor window"
echo ""
sleep 2

# Run glmark2 in background (GPU stress)
echo "Launching GPU stress tool (glmark2)..."
glmark2 --fullscreen --run-forever &
GLMARK_PID=$!

echo "GPU stress tool started (PID: $GLMARK_PID)"
echo ""
echo "Now run the monitor in another terminal:"
echo "  python3 gpu_stress_test.py"
echo ""
echo "Or press Enter to stop GPU stress..."
read

# Stop glmark2
kill $GLMARK_PID 2>/dev/null
echo "GPU stress stopped."
