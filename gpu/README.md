# GPU Tools - Clean and Simple Setup

This directory contains essential GPU tools with RTX 5070 Ti support and monitoring capabilities.

## 🗂️ Directory Structure

```
gpu-clean/
├── rtx5070ti-docker/     # RTX 5070 Ti compatible ML environment
├── monitoring/           # GPU monitoring solutions
└── README.md            # This file
```

## 🚀 Quick Start

### RTX 5070 Ti ML Environment

**Problem**: RTX 5070 Ti (Blackwell architecture) requires PyTorch nightly builds with sm_120 CUDA capability support.

**Solution**: 
```bash
cd gpu-clean/rtx5070ti-docker
./start.sh
```

This will:
- Build Docker image with PyTorch nightly + CUDA 12.8
- Start ML container with GPU access
- Test PyTorch CUDA functionality

**Access Container**:
```bash
docker compose exec ml-gpu bash
```

### GPU Monitoring

**Option 1: Simple Dashboard** (Lightweight)
```bash
cd gpu-clean/monitoring
./start_simple.sh
# Access: http://localhost:5000
```

**Option 2: Full Stack** (Historical metrics)
```bash
cd gpu-clean/monitoring
./start_stack.sh
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
```

## 🔧 What Was Fixed

### RTX 5070 Ti Compatibility
- **Error**: `CUDA error: no kernel image is available` for sm_120
- **Fix**: Updated to PyTorch nightly builds with Blackwell support
- **Files**: `Dockerfile`, `docker-compose.yml`, `start.sh`

### Directory Cleanup
- **Problem**: 45+ redundant shell scripts, multiple monitoring solutions
- **Solution**: Consolidated to 2 essential directories with clear purposes
- **Removed**: `.history` directories, `.DS_Store` files, duplicate scripts

## 📁 Essential Files Only

### RTX 5070 Ti Docker (`rtx5070ti-docker/`)
```
Dockerfile              # PyTorch nightly + CUDA 12.8
docker-compose.yml      # GPU access configuration  
start.sh               # One-command setup
workspace/             # Test scripts
```

### Monitoring (`monitoring/`)
```
simple_dashboard.py     # Flask web dashboard
start_simple.sh        # Quick dashboard
start_stack.sh         # Full Prometheus/Grafana
docker-compose.yml     # Monitoring stack
requirements.txt       # Python dependencies
```

## 🎯 Usage Patterns

**For ML Development**:
1. `cd gpu-clean/rtx5070ti-docker && ./start.sh`
2. `docker compose exec ml-gpu bash`
3. Run your PyTorch/CUDA code

**For GPU Monitoring**:
1. **Quick**: `cd gpu-clean/monitoring && ./start_simple.sh`
2. **Advanced**: `cd gpu-clean/monitoring && ./start_stack.sh`

## 🧹 Cleanup Summary

**Removed**:
- 25+ redundant shell scripts
- Multiple `.history` directories  
- Development artifacts (`.DS_Store`, `__pycache__`)
- Duplicate monitoring solutions

**Kept**:
- Working RTX 5070 Ti Docker environment
- Essential monitoring tools (2 options)
- Clear documentation and startup scripts

**Result**: From 45+ files across 3 directories to 15 essential files in 2 directories.

## 🔍 Troubleshooting

**RTX 5070 Ti Issues**:
- Ensure NVIDIA Docker runtime is installed
- Verify CUDA 12.4+ drivers are present
- Check `docker info | grep nvidia`

**Monitoring Issues**:
- Flask dashboard: Check port 5000 availability
- Full stack: Verify Docker Compose v2 is installed
- Permissions: Ensure scripts are executable (`chmod +x *.sh`)

## 📦 Dependencies

**RTX 5070 Ti Docker**:
- Docker with NVIDIA runtime
- CUDA 12.4+ drivers

**Monitoring**:
- Python 3.8+
- Docker (for full stack)
- Packages: flask, psutil, pynvml, prometheus_client