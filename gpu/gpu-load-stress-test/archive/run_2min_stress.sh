#!/bin/bash
# 2-minute GPU stress test with full monitoring

LOG_FILE="logs/gpu_2min_stress_$(date +%Y%m%d_%H%M%S).csv"
mkdir -p logs

echo "=========================================="
echo "GPU STRESS TEST - 2 MINUTES"
echo "=========================================="
echo "Starting: $(date)"
echo "Target: 300W sustained at full GPU load"
echo "Duration: 120 seconds"
echo ""

# Start gpu-burn in background
cd gpu-burn
./gpu_burn 120 > /tmp/gpu_burn.log 2>&1 &
GPU_BURN_PID=$!
cd ..

echo "GPU stress started (PID: $GPU_BURN_PID)"
sleep 2  # Let it ramp up

# Monitor with nvidia-smi
echo ""
echo "Real-time Monitoring:"
echo "Time(s)  Temp(C)  Power(W)  Util(%)  Fan(%)  Clock(MHz)  Status"
echo "=========================================================="

{
  echo "Timestamp,Elapsed_s,GPU_Temp_C,GPU_Power_W,GPU_Util_%,GPU_Fan_%,GPU_Clock_MHz,Status"
  
  START_TIME=$(date +%s)
  
  for i in {1..120}; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    
    if [ $ELAPSED -gt 120 ]; then
      break
    fi
    
    # Query GPU every second
    RESULT=$(nvidia-smi --query-gpu=timestamp,temperature.gpu,power.draw,utilization.gpu,fan.speed,clocks.current.graphics --format=csv,noheader,nounits 2>/dev/null)
    
    if [ ! -z "$RESULT" ]; then
      TEMP=$(echo "$RESULT" | cut -d',' -f2)
      POWER=$(echo "$RESULT" | cut -d',' -f3)
      UTIL=$(echo "$RESULT" | cut -d',' -f4)
      FAN=$(echo "$RESULT" | cut -d',' -f5)
      CLOCK=$(echo "$RESULT" | cut -d',' -f6)
      
      # Status check
      STATUS="OK"
      if (( $(echo "$POWER >= 300" | bc -l) )); then
        STATUS="⚠️ 300W+"
      fi
      if (( $(echo "$TEMP >= 87" | bc -l) )); then
        STATUS="🚨 CRITICAL"
        break
      fi
      
      # Print real-time
      printf "%3d      %.0f       %.1f      %.0f       %.0f      %.0f        %s\n" $ELAPSED $TEMP $POWER $UTIL $FAN $CLOCK "$STATUS"
      
      # Log to CSV
      TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
      echo "$TIMESTAMP,$ELAPSED,$TEMP,$POWER,$UTIL,$FAN,$CLOCK,$STATUS"
    fi
    
    sleep 1
  done
} | tee -a "$LOG_FILE"

# Wait for gpu-burn to finish
wait $GPU_BURN_PID 2>/dev/null

echo ""
echo "=========================================="
echo "TEST COMPLETE"
echo "=========================================="
echo "Ended: $(date)"
echo ""
echo "📊 Full log: $LOG_FILE"
echo ""
