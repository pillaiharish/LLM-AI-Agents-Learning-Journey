#!/bin/bash
# GPU Monitoring - Full Prometheus/Grafana Stack

echo "📊 Starting Full GPU Monitoring Stack"
echo "====================================="

cd "$(dirname "$0")"

echo "🛑 Stopping any existing monitoring services..."
docker compose down 2>/dev/null || true

echo "🚀 Starting monitoring stack..."
echo "   • Prometheus: http://localhost:9090"
echo "   • Grafana: http://localhost:3000 (admin/admin)"
echo "   • Metrics Exporter: http://localhost:8080/metrics"

docker compose up -d

echo "⏳ Waiting for services to start..."
sleep 5

echo "✅ Monitoring stack started!"
echo ""
echo "🎯 Access Points:"
echo "   • Grafana Dashboard: http://localhost:3000"
echo "   • Prometheus: http://localhost:9090"
echo "   • Raw Metrics: http://localhost:8080/metrics"