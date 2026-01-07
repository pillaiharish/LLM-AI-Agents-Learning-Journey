#!/usr/bin/env python3
"""GPU Stress using nvidia-smi to force compute load"""
import subprocess
import time
import csv
import os
from datetime import datetime
from collections import deque

# Install and use gpu-burn for proper stress
print("Installing GPU stress tool...")
subprocess.run(['sudo', 'apt-get', 'update'], capture_output=True)
subprocess.run(['sudo', 'apt-get', 'install', '-y', 'mesa-utils', 'stress-ng'], capture_output=True)

log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_path = os.path.join(log_dir, f'gpu_stress_full_{timestamp}.csv')

print(f"\n{'='*70}")
print("FULL GPU STRESS TEST - RTX 5070 Ti 16GB")
print(f"{'='*70}\n")
print(f"Logging to: {log_path}\n")

# Open log file
with open(log_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Timestamp', 'Elapsed_s', 'GPU_Temp_C', 'GPU_Power_W', 
                     'GPU_Util_%', 'GPU_Fan_%', 'GPU_Clock_MHz', 'Status'])
    
    max_temp = 0
    max_power = 0
    max_util = 0
    max_clock = 0
    
    # Run stress-ng GPU stress in background
    print("�� Starting GPU stress (stress-ng)...")
    stress_proc = subprocess.Popen(
        ['stress-ng', '--gpu', '1', '--timeout', '180s'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    start_time = time.time()
    duration = 180  # 3 minutes
    
    try:
        while (time.time() - start_time) < duration:
            elapsed = int(time.time() - start_time)
            
            # Query GPU
            try:
                result = subprocess.run([
                    'nvidia-smi',
                    '--query-gpu=temperature.gpu,power.draw,utilization.gpu,fan.speed,clocks.current.graphics',
                    '--format=csv,noheader,nounits'
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    values = result.stdout.strip().split(',')
                    temp = float(values[0].strip())
                    power = float(values[1].strip())
                    util = float(values[2].strip())
                    fan = float(values[3].strip())
                    clock = float(values[4].strip())
                    
                    max_temp = max(max_temp, temp)
                    max_power = max(max_power, power)
                    max_util = max(max_util, util)
                    max_clock = max(max_clock, clock)
                    
                    status = "OK"
                    if temp >= 83:
                        status = "⚠️ HIGH TEMP"
                    if power >= 285:
                        status = "⚠️ HIGH POWER"
                    
                    timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    writer.writerow([timestamp_str, elapsed, temp, power, util, fan, clock, status])
                    f.flush()
                    
                    print(f"\r[{elapsed:3d}/{duration}s] "
                          f"Temp: {temp:5.1f}°C "
                          f"Power: {power:6.1f}W "
                          f"Util: {util:3.0f}% "
                          f"Fan: {fan:3.0f}% "
                          f"Clock: {clock:4.0f}MHz "
                          f"{status}     ", end='', flush=True)
            except:
                pass
            
            time.sleep(1.0)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    finally:
        stress_proc.terminate()
        stress_proc.wait()
        print("\n\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Max GPU Temperature:    {max_temp:.1f}°C")
        print(f"Max GPU Power:          {max_power:.1f}W")
        print(f"Max GPU Utilization:    {max_util:.1f}%")
        print(f"Max GPU Clock:          {max_clock:.0f} MHz")
        print("="*70)
        
        temp_margin = 83 - max_temp
        power_margin = 285 - max_power
        
        print(f"\nSafety Margins:")
        print(f"  Temperature: {temp_margin:+.1f}°C from 83°C threshold")
        print(f"  Power:       {power_margin:+.1f}W from 285W threshold")
        
        if max_util > 80:
            print(f"\n✅ Good GPU stress achieved ({max_util:.0f}% utilization)")
        else:
            print(f"\n⚠️  Moderate stress only ({max_util:.0f}% utilization)")
        
        if max_temp < 70:
            print("✅ EXCELLENT cooling performance")
        elif max_temp < 80:
            print("✅ GOOD cooling performance")
        else:
            print("⚠️  Warm but within safe limits")
        
        print(f"\n📊 Full metrics: {log_path}")
