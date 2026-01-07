#!/usr/bin/env python3
"""
Fully Automated GPU Stress Test with Built-in Load Generation
Uses CUDA/OpenGL to stress GPU directly
"""

import subprocess
import time
import csv
import os
import signal
import sys
from datetime import datetime
from collections import deque

class AutomatedGPUTest:
    def __init__(self):
        # Safety thresholds
        self.GPU_TEMP_MAX = 83
        self.GPU_HOTSPOT_MAX = 100
        self.GPU_POWER_MAX = 285
        self.SUSTAINED_SECONDS = 10
        
        self.gpu_temp_history = deque(maxlen=10)
        self.gpu_power_history = deque(maxlen=10)
        
        self.max_gpu_temp = 0
        self.max_gpu_power = 0
        self.max_gpu_clock = 0
        self.max_gpu_util = 0
        
        self.log_file = None
        self.csv_writer = None
        self.stress_process = None
        
    def init_logging(self):
        os.makedirs('logs', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_path = os.path.join('logs', f'gpu_automated_{timestamp}.csv')
        
        self.log_file = open(log_path, 'w', newline='')
        self.csv_writer = csv.writer(self.log_file)
        self.csv_writer.writerow([
            'Timestamp', 'Stage', 'GPU_Temp_C', 'GPU_Power_W', 
            'GPU_Util_%', 'GPU_Fan_%', 'GPU_Clock_MHz', 'Safety_Status'
        ])
        self.log_file.flush()
        
        print(f"📊 Logging to: {log_path}")
        return log_path
        
    def get_gpu_stats(self):
        try:
            cmd = [
                'nvidia-smi',
                '--query-gpu=temperature.gpu,power.draw,utilization.gpu,fan.speed,clocks.current.graphics',
                '--format=csv,noheader,nounits'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                values = result.stdout.strip().split(',')
                stats = {
                    'gpu_temp': float(values[0].strip()),
                    'gpu_power': float(values[1].strip()),
                    'gpu_util': float(values[2].strip()),
                    'gpu_fan': float(values[3].strip()),
                    'gpu_clock': float(values[4].strip())
                }
                
                if stats['gpu_temp'] > self.max_gpu_temp:
                    self.max_gpu_temp = stats['gpu_temp']
                if stats['gpu_power'] > self.max_gpu_power:
                    self.max_gpu_power = stats['gpu_power']
                if stats['gpu_clock'] > self.max_gpu_clock:
                    self.max_gpu_clock = stats['gpu_clock']
                if stats['gpu_util'] > self.max_gpu_util:
                    self.max_gpu_util = stats['gpu_util']
                    
                return stats
        except Exception as e:
            print(f"Error: {e}")
        return None
    
    def check_safety(self, stats):
        if not stats:
            return []
        
        violations = []
        self.gpu_temp_history.append(stats['gpu_temp'] >= self.GPU_TEMP_MAX)
        self.gpu_power_history.append(stats['gpu_power'] >= self.GPU_POWER_MAX)
        
        if len(self.gpu_temp_history) >= self.SUSTAINED_SECONDS:
            if sum(self.gpu_temp_history) >= self.SUSTAINED_SECONDS:
                violations.append(f"GPU ≥{self.GPU_TEMP_MAX}°C for {self.SUSTAINED_SECONDS}s")
        
        if len(self.gpu_power_history) >= self.SUSTAINED_SECONDS:
            if sum(self.gpu_power_history) >= self.SUSTAINED_SECONDS:
                violations.append(f"Power ≥{self.GPU_POWER_MAX}W for {self.SUSTAINED_SECONDS}s")
        
        return violations
    
    def log_metrics(self, stage, stats, safety_status):
        if not stats:
            return
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        row = [
            timestamp, stage, stats['gpu_temp'], stats['gpu_power'],
            stats['gpu_util'], stats['gpu_fan'], stats['gpu_clock'], safety_status
        ]
        self.csv_writer.writerow(row)
        self.log_file.flush()
    
    def start_gpu_load(self):
        """Start GPU stress using nvidia-smi compute mode or glxgears"""
        try:
            # Try to use CUDA stress if available
            cmd = ['nvidia-smi', 'compute', 'set', '-i', '0', '-m', 'EXCLUSIVE_PROCESS']
            subprocess.run(cmd, capture_output=True)
            
            # Use a simple CUDA/OpenGL load generator
            # First try glxgears (basic but works)
            self.stress_process = subprocess.Popen(
                ['glxgears', '-fullscreen'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("✓ Started GPU load (glxgears)")
            return True
        except:
            try:
                # Fallback: use vblank_mode=0 glxgears for more stress
                self.stress_process = subprocess.Popen(
                    ['vblank_mode=0', 'glxgears'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    shell=True
                )
                print("✓ Started GPU load (glxgears unlimited)")
                return True
            except Exception as e:
                print(f"⚠️  Could not start automatic GPU load: {e}")
                print("   Please manually start a GPU stress tool")
                return False
    
    def stop_gpu_load(self):
        if self.stress_process:
            self.stress_process.terminate()
            time.sleep(1)
            if self.stress_process.poll() is None:
                self.stress_process.kill()
            print("✓ Stopped GPU load")
    
    def run_stage(self, stage_name, duration_seconds, with_load=False):
        print(f"\n{'='*70}")
        print(f"Stage: {stage_name}")
        print(f"Duration: {duration_seconds} seconds")
        print(f"{'='*70}")
        
        if with_load:
            self.start_gpu_load()
            time.sleep(2)  # Let load ramp up
        
        start_time = time.time()
        
        while (time.time() - start_time) < duration_seconds:
            stats = self.get_gpu_stats()
            violations = self.check_safety(stats)
            
            if violations:
                print(f"\n\n🚨 SAFETY VIOLATION!")
                for v in violations:
                    print(f"   ❌ {v}")
                self.log_metrics(stage_name, stats, "VIOLATION: " + "; ".join(violations))
                if with_load:
                    self.stop_gpu_load()
                return False
            
            safety_status = "OK"
            self.log_metrics(stage_name, stats, safety_status)
            
            elapsed = int(time.time() - start_time)
            
            if stats:
                print(f"\r[{elapsed:4d}/{duration_seconds}s] "
                      f"Temp: {stats['gpu_temp']:5.1f}°C "
                      f"Power: {stats['gpu_power']:6.1f}W "
                      f"Util: {stats['gpu_util']:3.0f}% "
                      f"Fan: {stats['gpu_fan']:3.0f}% "
                      f"Clock: {stats['gpu_clock']:4.0f}MHz "
                      f"✓ OK   ", end='', flush=True)
            
            time.sleep(1.0)
        
        print()
        if with_load:
            self.stop_gpu_load()
        return True
    
    def print_summary(self):
        print("\n" + "="*70)
        print("GPU STRESS TEST SUMMARY - AUTOMATED RUN")
        print("="*70)
        print(f"Hardware: NVIDIA RTX 5070 Ti 16GB")
        print()
        print(f"Max GPU Temperature:    {self.max_gpu_temp:.1f}°C")
        print(f"Max GPU Power Draw:     {self.max_gpu_power:.1f}W")
        print(f"Max GPU Utilization:    {self.max_gpu_util:.1f}%")
        print(f"Max GPU Clock:          {self.max_gpu_clock:.0f} MHz")
        print("="*70)
        
        temp_margin = self.GPU_TEMP_MAX - self.max_gpu_temp
        power_margin = self.GPU_POWER_MAX - self.max_gpu_power
        
        print("\nSafety Analysis:")
        print(f"  Temperature Margin:  {temp_margin:+.1f}°C from threshold ({self.GPU_TEMP_MAX}°C)")
        print(f"  Power Margin:        {power_margin:+.1f}W from threshold ({self.GPU_POWER_MAX}W)")
        
        print("\nPerformance Analysis:")
        if self.max_gpu_util < 50:
            print("  ⚠️  Low GPU utilization - stress test may not have worked properly")
        elif self.max_gpu_util < 90:
            print("  ℹ️  Moderate GPU load achieved")
        else:
            print("  ✓ Full GPU load achieved")
        
        if temp_margin < 5:
            print("\n⚠️  WARNING: Low thermal safety margin!")
            print("   Recommendation: Improve cooling or reduce power limit")
        elif self.max_gpu_temp < 70:
            print("\n✅ EXCELLENT: GPU stayed cool under load")
            print("   Your cooling solution is working very well")
        else:
            print("\n✅ GOOD: Adequate thermal performance with safety margins")
        
        if self.max_gpu_power > 250:
            print(f"\n💡 Power Draw: {self.max_gpu_power:.1f}W is near TDP (285W)")
        else:
            print(f"\n💡 Power Draw: {self.max_gpu_power:.1f}W - reasonable for load")
    
    def cleanup(self):
        self.stop_gpu_load()
        if self.log_file:
            self.log_file.close()


def main():
    print("="*70)
    print("AUTOMATED GPU STRESS TEST - RTX 5070 Ti")
    print("="*70)
    print("\nThis will automatically stress your GPU and monitor safety.")
    print(f"Test duration: ~3 minutes (short test for verification)")
    print()
    print("Safety thresholds:")
    print("  • GPU Temperature: 83°C")
    print("  • GPU Power: 285W")
    print()
    
    test = AutomatedGPUTest()
    
    # Verify GPU is accessible
    stats = test.get_gpu_stats()
    if not stats:
        print("❌ Cannot detect GPU. Check nvidia-smi.")
        return
    
    print(f"✅ GPU Detected")
    print(f"   Idle: {stats['gpu_temp']}°C, {stats['gpu_power']}W")
    print()
    
    log_path = test.init_logging()
    
    try:
        # Short test cycle for verification
        print("\n🔵 Starting automated test...")
        
        # Idle baseline (30s)
        if not test.run_stage("Idle Baseline", 30, with_load=False):
            return
        
        # GPU stress (60s)
        print("\n🔥 Starting GPU stress...")
        if not test.run_stage("GPU Stress", 60, with_load=True):
            return
        
        # Cooldown (30s)
        print("\n❄️  Cooldown...")
        test.run_stage("Cooldown", 30, with_load=False)
        
        print("\n✅ Test completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
    finally:
        test.print_summary()
        test.cleanup()
        print(f"\n📊 Full log: {log_path}")


if __name__ == '__main__':
    main()
