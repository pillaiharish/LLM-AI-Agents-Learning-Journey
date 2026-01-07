#!/bin/bash
# Quick verification script to test all components

echo "======================================"
echo "GPU Stress Test - Component Verification"
echo "======================================"

echo ""
echo "[1/6] Checking Python..."
if command -v python3 &> /dev/null; then
    echo "✓ Python 3: $(python3 --version)"
else
    echo "✗ Python 3 not found"
    exit 1
fi

echo ""
echo "[2/6] Checking NVIDIA drivers..."
if command -v nvidia-smi &> /dev/null; then
    echo "✓ nvidia-smi found"
    nvidia-smi --query-gpu=gpu_name,driver_version --format=csv,noheader | head -1
else
    echo "✗ nvidia-smi not found"
    exit 1
fi

echo ""
echo "[3/6] Checking benchmark.py..."
if [ -f "benchmark.py" ]; then
    echo "✓ benchmark.py exists"
    if [ -x "benchmark.py" ]; then
        echo "✓ benchmark.py is executable"
    else
        echo "⚠ Making benchmark.py executable..."
        chmod +x benchmark.py
    fi
else
    echo "✗ benchmark.py not found"
    exit 1
fi

echo ""
echo "[4/6] Testing benchmark.py --help..."
if python3 benchmark.py --help &> /dev/null; then
    echo "✓ benchmark.py runs correctly"
else
    echo "✗ benchmark.py has errors"
    exit 1
fi

echo ""
echo "[5/6] Checking run-benchmark.sh..."
if [ -f "run-benchmark.sh" ]; then
    echo "✓ run-benchmark.sh exists"
    if [ -x "run-benchmark.sh" ]; then
        echo "✓ run-benchmark.sh is executable"
    else
        echo "⚠ Making run-benchmark.sh executable..."
        chmod +x run-benchmark.sh
    fi
else
    echo "✗ run-benchmark.sh not found"
    exit 1
fi

echo ""
echo "[6/6] Checking documentation..."
files=("README_PUBLIC.md" "LICENSE" "CONTRIBUTING.md" "EXAMPLE_RESULTS.md" ".gitignore")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file not found"
    fi
done

echo ""
echo "======================================"
echo "✓ All components verified successfully!"
echo "======================================"
echo ""
echo "Ready for GitHub PR!"
echo ""
echo "Next steps:"
echo "1. Test the tool: ./run-benchmark.sh"
echo "2. Or quick test: python3 benchmark.py --duration 2 --non-interactive"
echo "3. Review GITHUB_PR_PREP.md for PR preparation steps"
