# GPU/CPU Stress Test & Benchmark Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![NVIDIA GPU](https://img.shields.io/badge/NVIDIA-GPU-76B900.svg)](https://www.nvidia.com/)

**A universal, safe, and configurable stress testing tool for NVIDIA GPUs and CPUs.** This tool automatically detects your hardware, sets conservative safety thresholds, and provides real-time monitoring with detailed metrics logging.

## ✨ Features

- 🔍 **Automatic Hardware Detection** - Detects GPU model, specs, and safe temperature limits
- 🛡️ **Built-in Safety Mechanisms** - Automatically stops if temperatures exceed thresholds (default: 90% of GPU spec)
- ⚙️ **Fully Configurable** - Set custom durations (2/5/10 min or custom), temperature limits, and power caps
- 📊 **Real-time Monitoring** - Live display of temperature, power, utilization, fan speed, and clock speeds
- 💾 **CSV Logging** - All metrics saved for analysis and graphing
- 🎯 **Multiple Test Modes** - GPU only, CPU only, or combined stress tests
- 🚀 **Easy to Use** - One-command setup and execution with interactive configuration

## 🎯 Use Cases

- **System Validation** - Test new builds or overclocks for stability
- **Thermal Testing** - Verify cooling performance under maximum load
- **Benchmarking** - Compare GPU performance across different systems
- **Before Gaming/Workloads** - Ensure your system can handle sustained loads
- **Quality Assurance** - Stress test before deploying systems

## 📋 Requirements

### Hardware
- NVIDIA GPU (any model supported by nvidia-smi)
- Linux operating system (Ubuntu, Fedora, Arch, etc.)
- CUDA-capable GPU for stress testing

### Software
- **Python 3.7+** (usually pre-installed on Linux)
- **NVIDIA Drivers** with nvidia-smi utility
- **CUDA Toolkit** (for compiling gpu-burn)
- **git** (for downloading dependencies)
- **make** and **g++** (for building gpu-burn)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/gpu-stress-test.git
cd gpu-stress-test

# Run the easy launcher (checks all dependencies and starts the tool)
./run-benchmark.sh
```

The launcher script will:
1. ✅ Check for Python 3
2. ✅ Verify NVIDIA drivers and detect your GPU
3. ✅ Download and compile gpu-burn if needed
4. ✅ Create necessary directories
5. 🚀 Launch the interactive configuration

### Basic Usage

**Interactive Mode (Recommended):**
```bash
./run-benchmark.sh
```

You'll be prompted to configure:
- Test type (GPU only / CPU only / Both)
- Duration (2, 5, 10 minutes, or custom)
- Temperature safety threshold (default: 90% of GPU spec)
- Optional power limit

**Command-Line Mode:**
```bash
# Quick 5-minute test with auto-detected safe defaults
python3 benchmark.py --duration 5 --non-interactive

# Custom settings
python3 benchmark.py --duration 10 --temp 80 --type gpu

# Full custom stress test
python3 benchmark.py --duration 15 --temp 75 --power 250 --type gpu
```

### Command-Line Options

```
--duration MINUTES    Test duration in minutes (default: 2)
--temp CELSIUS        GPU temperature threshold in °C (default: 90% of spec)
--power WATTS         GPU power limit in Watts (default: unlimited)
--type {gpu,cpu,both} Test type (default: gpu)
--non-interactive     Run with defaults without prompts
```

## 📊 Understanding the Output

### Real-Time Monitoring Display

```
======================================================================
Time(s)  Temp(°C)   Power(W)   Util(%)    Fan(%)     Status         
======================================================================
0        45         120.5      100        50         OK
1        48         285.3      100        55         OK
2        52         289.7      100        60         OK
...
```

### Metrics Explained

| Metric | Description |
|--------|-------------|
| **Time(s)** | Elapsed time since test start |
| **Temp(°C)** | GPU core temperature |
| **Power(W)** | GPU power consumption |
| **Util(%)** | GPU utilization percentage |
| **Fan(%)** | Fan speed percentage |
| **Status** | OK, WARNING, or CRITICAL |

### CSV Log Files

All metrics are saved to `logs/stress_test_TIMESTAMP.csv` for later analysis:

```csv
Timestamp,Elapsed_s,GPU_Temp_C,GPU_Power_W,GPU_Util_%,GPU_Fan_%,GPU_Clock_MHz,Status
2026-01-03T10:30:00,0,45.0,120.50,100,50,1800,OK
2026-01-03T10:30:01,1,48.0,285.30,100,55,1950,OK
```

## 🛡️ Safety Features

### Automatic Temperature Protection

The tool implements multiple safety layers:

1. **Conservative Defaults** - Sets threshold to 90% of GPU's rated maximum (≥10% safety margin)
2. **Sustained Violation Detection** - Requires 10 consecutive seconds above threshold before stopping
3. **Instant Stop on Critical** - Immediate shutdown if temperature is dangerously high
4. **Real-time Monitoring** - Checks metrics every second

### Temperature Threshold Examples

| GPU Model | Spec Max | Default Threshold (90%) |
|-----------|----------|-------------------------|
| RTX 4090 | 90°C | 81°C |
| RTX 4080 | 88°C | 79°C |
| RTX 4070 | 87°C | 78°C |
| RTX 3080 | 93°C | 84°C |
| RTX 3060 | 93°C | 84°C |

You can override these with custom values, but **we strongly recommend staying ≤10% below GPU spec**.

## 🔧 Advanced Configuration

### Manual Threshold Setting

If auto-detection fails or you want custom limits:

```bash
# Conservative for 24/7 stress testing
python3 benchmark.py --temp 70 --duration 30

# Aggressive for short burst testing
python3 benchmark.py --temp 85 --duration 5

# With power limiting
python3 benchmark.py --temp 80 --power 300 --duration 10
```

### Test Duration Guidelines

| Duration | Use Case |
|----------|----------|
| **2 minutes** | Quick validation, thermal ramp test |
| **5 minutes** | Standard stability test |
| **10 minutes** | Thorough stability verification |
| **15-30 minutes** | Extended burn-in, cooling performance |

## 📚 Libraries & Dependencies

### Core Dependencies

| Library/Tool | Purpose | Installation |
|--------------|---------|--------------|
| **Python 3.7+** | Main scripting language | Pre-installed on most Linux |
| **nvidia-smi** | GPU monitoring and metrics | Included with NVIDIA drivers |
| **gpu-burn** | CUDA GPU stress generator | Auto-downloaded and compiled |
| **CUDA Toolkit** | Required to compile gpu-burn | `apt install nvidia-cuda-toolkit` |

### Python Standard Libraries Used

- `subprocess` - Running external commands (nvidia-smi, gpu-burn)
- `csv` - Logging metrics to CSV files
- `argparse` - Command-line argument parsing
- `json` - Configuration management
- `datetime` - Timestamp generation
- `collections.deque` - Efficient rolling history for safety checks
- `time` - Sleep intervals and elapsed time tracking

**No external Python packages required!** - Uses only standard library.

### GPU Stress Tool: gpu-burn

[gpu-burn](https://github.com/wilicc/gpu-burn) is an open-source CUDA-based GPU stress testing tool that:
- Generates maximum GPU load using CUDA matrix operations
- Validates computation accuracy (detects GPU errors)
- Supports all CUDA-capable NVIDIA GPUs
- Lightweight and efficient

The tool is automatically downloaded and compiled by `run-benchmark.sh`.

## 🏗️ Project Structure

```
gpu-stress-test/
├── benchmark.py           # Main stress testing tool
├── run-benchmark.sh       # Easy launcher with dependency checking
├── setup.sh              # Manual setup script (alternative)
├── README.md             # This file
├── LICENSE               # MIT License
├── CONTRIBUTING.md       # Contribution guidelines
├── EXAMPLE_RESULTS.md    # Sample test outputs
├── .gitignore            # Git ignore rules
├── config.template.json  # Configuration template
├── verify-components.sh  # Component verification script
├── gpu-burn/             # GPU stress tool (auto-downloaded)
│   └── gpu_burn          # Compiled binary
└── logs/                 # Test results and CSV logs
    └── stress_test_*.csv
```

## 🐛 Troubleshooting

### "nvidia-smi not found"

**Solution:** Install NVIDIA drivers
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install nvidia-driver-535  # Or latest version

# Check installation
nvidia-smi
```

### "nvcc not found" (CUDA Toolkit)

**Solution:** Install CUDA toolkit
```bash
# Ubuntu/Debian
sudo apt-get install nvidia-cuda-toolkit

# Verify
nvcc --version
```

### "gpu-burn compilation failed"

**Solution:** Install build dependencies
```bash
# Ubuntu/Debian
sudo apt-get install build-essential g++ make

# Then re-run
./run-benchmark.sh
```

### "Temperature threshold too high" warning

**Solution:** The tool detected your custom threshold exceeds GPU spec. Either:
- Accept the warning and continue (not recommended)
- Use the recommended 90% threshold (safer)
- Manually verify your GPU's maximum temperature spec

### Test stops immediately with "CRITICAL"

**Cause:** Your GPU temperature or power is already at/above threshold before test starts.

**Solution:**
1. Let your system cool down (5-10 minutes)
2. Check cooling (clean fans, reapply thermal paste if needed)
3. Verify ambient temperature is reasonable
4. Check if GPU is under load from other applications

## 📈 Example Results

For sample outputs and performance comparisons, see [EXAMPLE_RESULTS.md](EXAMPLE_RESULTS.md).

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Reporting bugs
- Suggesting features
- Submitting pull requests
- Code style and testing

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Tools

- **gpu-burn** - [MIT License](https://github.com/wilicc/gpu-burn/blob/master/LICENSE)
- **NVIDIA drivers and CUDA** - [NVIDIA Software License](https://www.nvidia.com/en-us/drivers/nvidia-license/)

## ⚠️ Disclaimer

**This tool generates maximum load on your GPU which may cause:**
- High temperatures (within safe limits)
- Maximum power consumption
- Increased fan noise
- Accelerated component wear (minimal for short tests)

**Use at your own risk.** While this tool implements safety mechanisms, the authors are not responsible for any hardware damage. Always:
- Ensure adequate cooling
- Monitor your system during tests
- Use conservative thresholds for extended testing
- Stop immediately if you notice unusual behavior

## 🙏 Acknowledgments

- **gpu-burn** by Ville Timonen - GPU stress testing tool
- **NVIDIA** - nvidia-smi monitoring utility
- **The Linux Community** - Various testing and monitoring tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/gpu-stress-test/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/gpu-stress-test/discussions)
- **Documentation**: Check this README and inline code comments

---

**Made with ❤️ for GPU enthusiasts, overclockers, and system builders**

Happy stress testing! 🚀🔥
