#!/bin/bash
# RTX 5070 Ti Docker Environment - Rebuild and Start

echo "🚀 RTX 5070 Ti Docker Environment Setup"
echo "======================================="

cd "$(dirname "$0")"

echo "🛑 Stopping any existing containers..."
docker compose down 2>/dev/null || true

echo "🏗️  Building RTX 5070 Ti compatible environment..."
echo "   • PyTorch nightly builds with sm_120 support"
echo "   • CUDA 12.8 runtime"

docker compose build --no-cache

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "🚀 Starting container..."
    docker compose up -d
    
    echo "⏳ Waiting for container to start..."
    sleep 3
    
    echo "🧪 Testing PyTorch CUDA support..."
    docker compose exec ml-gpu python3 -c "
import torch
print('PyTorch version:', torch.__version__)
print('CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('GPU:', torch.cuda.get_device_name(0))
    print('CUDA capability:', torch.cuda.get_device_capability(0))
"
    echo ""
    echo "✅ Container ready! Access it with:"
    echo "   docker compose exec ml-gpu bash"
else
    echo "❌ Build failed!"
fi