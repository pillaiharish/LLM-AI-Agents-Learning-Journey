#!/bin/bash
# GPU Monitoring - Simple Flask Dashboard

echo "🖥️  Starting Simple GPU Monitoring Dashboard"
echo "==========================================="

cd "$(dirname "$0")"

# Install requirements if needed
if [ ! -f "venv/bin/activate" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "🚀 Starting Flask dashboard on port 5000..."
echo "   Access: http://localhost:5000"

python3 simple_dashboard.py