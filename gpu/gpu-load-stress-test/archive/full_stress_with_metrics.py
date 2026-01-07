#!/usr/bin/env python3
"""
FULL GPU STRESS TEST - Push to 300W and collect metrics
"""
import subprocess
import time
import csv
import os
from datetime import datetime
import signal
import sys

log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_path = os.path.join(log_dir, f'gpu_300W_stress_{timestamp}.csv')

print("="*70)
print("REAL GPU STRESS TEST - PUSHING TO 300W")
print("="*70)
print(f"Target: 300W sustained for 2 minutes")
print(f"Logging to: {log_path}\n")

gpu_burn_proc = None

def cleanup(signum=None, frame=None):
    global gpu_burn_proc
    if gpu_burn_proc:
        gpu_burn_proc.terminate()
        gpu_burn_proc.wait()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

# Start gpu-burn
print("🔥 Starting GPU-BURN (real CUDA stress)...")
gpu_burn_proc = subprocess.Popen(
    ['./gpu-burn/gpu_burn', '120'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

time.sleep(2)  # Let it ramp up

# Open CSV
with open(log_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        'Timestamp', 'Elapsed_s', 'GPU_Temp_C', 'GPU_Power_W',
        'GPU_Util_%', 'GPU_Fan_%', 'GPU_Clock_MHz', 'Mem_Clock_MHz', 'Status'
    ])
    
    max_temp = 0
    max_power = 0
    max_util = 0
    
    start_time = time.time()
    duration = 125  # Run for full duration
    
    print("\nMonitoring GPU metrics every second...\n")
    print(f"{'Time':>5} {'Temp':>6} {'Power':>8} {'Util':>5} {'Fan':>5} {'Clock':>7} Status")
    print("-" * 70)
    
    try:
        while (time.time() - start_time) < duration and gpu_burn_proc.poll() is None:
            elapsed = int(time.time() - start_time)
            
            try:
                result = subprocess.run([
                    'nvidia-smi',
                    '--query-gpu=temperature.gpu,power.draw,utilization.gpu,fan.speed,clocks.current.graphics,clocks.current.memory',
                    '--format=csv,noheader,nounits'
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    values = result.stdout.strip().split(',')
                    temp = float(values[0].strip())
                    power = float(values[1].strip())
                    util = float(values[2].strip())
                    fan = float(values[3].strip())
                    clock = float(values[4].strip())
                    mem_clock = float(values[5].strip())
                    
                    max_temp = max(max_temp, temp)
                    max_power = max(max_power, power)
                    max_util = max(max_util, util)
                    
                    # Safety check
                    status = "OK"
                    if temp >= 83:
                        status = "⚠️ TEMP HIGH"
                    if power >= 300:
                        status = "⚠️ 300W+"
                    if temp >= 87:
                        status = "🚨 CRITICAL TEMP"
                        print(f"\n🚨 CRITICAL: GPU ≥87°C - STOPPING!")
                        break
                    
                    timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    writer.writerow([timestamp_str, elapsed, temp, power, util, fan, clock, mem_clock, status])
                    f.flush()
                    
                    print(f"{elapsed:>4}s {temp:>5.0f}°C {power:>7.1f}W {util:>4.0f}% {fan:>4.0f}% {clock:>6.0f}MHz {status}")
            except Exception as e:
                print(f"Error: {e}")
            
            time.sleep(1.0)
    
    finally:
        if gpu_burn_proc:
            gpu_burn_proc.terminate()
            gpu_burn_proc.wait()
        
        print("\n" + "="*70)
        print("TEST RESULTS")
        print("="*70)
        print(f"Max GPU Temperature:    {max_temp:.1f}°C")
        print(f"Max GPU Power:          {max_power:.1f}W")
        print(f"Max GPU Utilization:    {max_util:.0f}%")
        print("="*70)
        
        if max_power >= 280:
            print(f"\n✅ SUCCESS: Reached {max_power:.0f}W (target: 300W)")
            print("   GPU was properly stressed!")
        elif max_power >= 250:
            print(f"\n✅ GOOD: Reached {max_power:.0f}W")
            print("   Close to target, good stress achieved")
        else:
            print(f"\n⚠️  Only reached {max_power:.0f}W")
        
        if max_temp < 75:
            print(f"   🌡️  Temps excellent ({max_temp:.0f}°C) - cooling is great!")
        elif max_temp < 83:
            print(f"   🌡️  Temps good ({max_temp:.0f}°C) - within safe limits")
        else:
            print(f"   🌡️  Temps warm ({max_temp:.0f}°C) - approaching threshold")
        
        print(f"\n📊 Full log: {log_path}")
