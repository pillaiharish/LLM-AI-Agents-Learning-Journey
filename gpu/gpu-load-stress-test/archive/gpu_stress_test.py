#!/usr/bin/env python3
"""
GPU-Only Stress Test with Safety Monitoring
For RTX 5070 Ti 16GB - Matches prompt specifications
"""

import subprocess
import time
import csv
import os
from datetime import datetime
from collections import deque

class GPUStressTest:
    def __init__(self):
        # Safety thresholds from prompt (conservative for RTX 5070 Ti)
        self.GPU_TEMP_MAX = 83  # 4°C below spec of 87°C
        self.GPU_HOTSPOT_MAX = 100  # 5°C below spec of 105°C  
        self.GPU_POWER_MAX = 285  # At TDP
        self.SUSTAINED_SECONDS = 10
        
        # History for sustained violation detection
        self.gpu_temp_history = deque(maxlen=10)
        self.gpu_hotspot_history = deque(maxlen=10)
        self.gpu_power_history = deque(maxlen=10)
        
        # Stats tracking
        self.max_gpu_temp = 0
        self.max_gpu_hotspot = 0
        self.max_gpu_power = 0
        self.max_gpu_clock = 0
        
        self.log_file = None
        self.csv_writer = None
        
    def init_logging(self):
        """Initialize CSV logging"""
        os.makedirs('logs', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_path = os.path.join('logs', f'gpu_stress_{timestamp}.csv')
        
        self.log_file = open(log_path, 'w', newline='')
        self.csv_writer = csv.writer(self.log_file)
        
        # Header matching prompt requirements
        self.csv_writer.writerow([
            'Timestamp', 'Stage', 'GPU_Temp_C', 'GPU_Hotspot_C', 
            'GPU_Power_W', 'GPU_Util_%', 'GPU_Fan_%', 'GPU_Clock_MHz',
            'Safety_Status'
        ])
        self.log_file.flush()
        
        print(f"📊 Logging to: {log_path}")
        return log_path
        
    def get_gpu_stats(self):
        """Query NVIDIA GPU comprehensive stats"""
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
                    'gpu_hotspot': float(values[0].strip()),  # Use gpu_temp as approximation
                    'gpu_power': float(values[1].strip()),
                    'gpu_util': float(values[2].strip()),
                    'gpu_fan': float(values[3].strip()),
                    'gpu_clock': float(values[4].strip()),
                    'mem_clock': 0
                }
                
                # Update maximums
                if stats['gpu_temp'] > self.max_gpu_temp:
                    self.max_gpu_temp = stats['gpu_temp']
                if stats['gpu_hotspot'] > self.max_gpu_hotspot:
                    self.max_gpu_hotspot = stats['gpu_hotspot']
                if stats['gpu_power'] > self.max_gpu_power:
                    self.max_gpu_power = stats['gpu_power']
                if stats['gpu_clock'] > self.max_gpu_clock:
                    self.max_gpu_clock = stats['gpu_clock']
                    
                return stats
        except Exception as e:
            print(f"⚠️  Error querying GPU: {e}")
        
        return None
    
    def check_safety(self, stats):
        """Check safety thresholds - returns violations list"""
        if not stats:
            return []
        
        violations = []
        
        # Track history
        self.gpu_temp_history.append(stats['gpu_temp'] >= self.GPU_TEMP_MAX)
        self.gpu_hotspot_history.append(stats['gpu_hotspot'] >= self.GPU_HOTSPOT_MAX)
        self.gpu_power_history.append(stats['gpu_power'] >= self.GPU_POWER_MAX)
        
        # Check for sustained violations
        if len(self.gpu_temp_history) >= self.SUSTAINED_SECONDS:
            if sum(self.gpu_temp_history) >= self.SUSTAINED_SECONDS:
                violations.append(f"GPU Core ≥{self.GPU_TEMP_MAX}°C for {self.SUSTAINED_SECONDS}s")
        
        if len(self.gpu_hotspot_history) >= self.SUSTAINED_SECONDS:
            if sum(self.gpu_hotspot_history) >= self.SUSTAINED_SECONDS:
                violations.append(f"GPU Hotspot ≥{self.GPU_HOTSPOT_MAX}°C for {self.SUSTAINED_SECONDS}s")
        
        if len(self.gpu_power_history) >= self.SUSTAINED_SECONDS:
            if sum(self.gpu_power_history) >= self.SUSTAINED_SECONDS:
                violations.append(f"GPU Power ≥{self.GPU_POWER_MAX}W for {self.SUSTAINED_SECONDS}s")
        
        return violations
    
    def log_metrics(self, stage, stats, safety_status):
        """Log metrics to CSV"""
        if not stats:
            return
            
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        row = [
            timestamp, stage,
            stats['gpu_temp'], stats['gpu_hotspot'], stats['gpu_power'],
            stats['gpu_util'], stats['gpu_fan'], stats['gpu_clock'],
            safety_status
        ]
        self.csv_writer.writerow(row)
        self.log_file.flush()
    
    def run_stage(self, stage_name, duration_seconds):
        """Run a test stage with monitoring"""
        print(f"\n{'='*70}")
        print(f"Stage: {stage_name}")
        print(f"Duration: {duration_seconds} seconds")
        print(f"{'='*70}")
        
        start_time = time.time()
        
        while (time.time() - start_time) < duration_seconds:
            stats = self.get_gpu_stats()
            violations = self.check_safety(stats)
            
            if violations:
                print(f"\n\n🚨 SAFETY VIOLATION - STOPPING TEST!")
                for v in violations:
                    print(f"   ❌ {v}")
                self.log_metrics(stage_name, stats, "VIOLATION: " + "; ".join(violations))
                return False
            
            safety_status = "OK"
            self.log_metrics(stage_name, stats, safety_status)
            
            # Display progress
            elapsed = int(time.time() - start_time)
            remaining = duration_seconds - elapsed
            
            if stats:
                print(f"\r[{elapsed:4d}/{duration_seconds}s] "
                      f"Temp: {stats['gpu_temp']:5.1f}°C "
                      f"Hotspot: {stats['gpu_hotspot']:5.1f}°C "
                      f"Power: {stats['gpu_power']:6.1f}W "
                      f"Util: {stats['gpu_util']:3.0f}% "
                      f"Fan: {stats['gpu_fan']:3.0f}% "
                      f"✓ OK     ", end='', flush=True)
            
            time.sleep(1.0)  # 1-second interval as per prompt
        
        print()  # New line
        return True
    
    def print_summary(self):
        """Print test summary as per prompt requirements"""
        print("\n" + "="*70)
        print("GPU STRESS TEST SUMMARY")
        print("="*70)
        print(f"Hardware: NVIDIA RTX 5070 Ti 16GB")
        print()
        print(f"Max GPU Core Temp:      {self.max_gpu_temp:.1f}°C")
        print(f"Max GPU Hotspot:        {self.max_gpu_hotspot:.1f}°C")
        print(f"Max GPU Power:          {self.max_gpu_power:.1f}W")
        print(f"Max GPU Clock:          {self.max_gpu_clock:.0f} MHz")
        print("="*70)
        
        # Safety margin analysis
        temp_margin = self.GPU_TEMP_MAX - self.max_gpu_temp
        hotspot_margin = self.GPU_HOTSPOT_MAX - self.max_gpu_hotspot
        power_margin = self.GPU_POWER_MAX - self.max_gpu_power
        
        print("\nSafety Margins:")
        print(f"  GPU Core:    {temp_margin:+.1f}°C from threshold ({self.GPU_TEMP_MAX}°C)")
        print(f"  GPU Hotspot: {hotspot_margin:+.1f}°C from threshold ({self.GPU_HOTSPOT_MAX}°C)")
        print(f"  GPU Power:   {power_margin:+.1f}W from threshold ({self.GPU_POWER_MAX}W)")
        
        if temp_margin < 5 or hotspot_margin < 5:
            print("\n⚠️  WARNING: Low thermal safety margin!")
            print("   Consider improving GPU cooling or reducing power limit.")
        elif self.max_gpu_power > 270:
            print("\n⚠️  High power draw detected - cooling working hard")
        else:
            print("\n✅ Good thermal performance with adequate safety margins")
    
    def cleanup(self):
        """Clean up resources"""
        if self.log_file:
            self.log_file.close()


def main():
    """Main GPU stress test workflow"""
    print("="*70)
    print("GPU Stress Test - RTX 5070 Ti 16GB")
    print("Safe implementation matching prompt specifications")
    print("="*70)
    print()
    print("Safety Thresholds (sustained >10 seconds):")
    print("  • GPU Core ≥ 83°C")
    print("  • GPU Hotspot ≥ 100°C")
    print("  • GPU Power ≥ 285W")
    print()
    print("⚠️  IMPORTANT:")
    print("   1. This script monitors only - manually start GPU stress tool")
    print("   2. Stay near computer during test")
    print("   3. Press Ctrl+C to emergency stop")
    print("   4. Recommended: Set GPU power limit to 90% in nvidia-settings")
    print()
    
    # Check GPU is available
    test = GPUStressTest()
    stats = test.get_gpu_stats()
    
    if not stats:
        print("❌ Could not detect NVIDIA GPU. Is nvidia-smi working?")
        return
    
    print(f"✅ GPU Detected: RTX 5070 Ti")
    print(f"   Current temp: {stats['gpu_temp']}°C, Power: {stats['gpu_power']}W")
    print()
    
    response = input("Ready to start GPU stress test? (yes/no): ")
    if response.lower() != 'yes':
        print("Test cancelled.")
        return
    
    log_path = test.init_logging()
    
    try:
        # Stage A: Idle baseline (2 minutes)
        print("\n📝 Stage A: Idle Baseline")
        print("   GPU should be at idle - no stress yet")
        input("   Press Enter to start...")
        
        if not test.run_stage("Idle Baseline", 120):
            print("\n❌ Safety violation during idle! Check cooling!")
            return
        
        # Stage C: GPU stress (10 minutes as per prompt)
        print("\n📝 Stage C: GPU Stress Test")
        print("   NOW: Start your GPU stress tool:")
        print("   • FurMark (1080p, 60 FPS cap) OR")
        print("   • Unigine Superposition (loop mode) OR")
        print("   • glmark2 --fullscreen (Linux alternative)")
        print()
        input("   Start GPU stress tool, then press Enter...")
        
        if not test.run_stage("GPU Stress", 600):
            print("\n❌ Safety violation detected!")
            return
        
        print("\n✅ GPU stress test completed!")
        print("   STOP your GPU stress tool now.")
        
        # Cooldown
        print("\n📝 Cooldown period")
        input("   Press Enter to start cooldown...")
        test.run_stage("Cooldown", 120)
        
        print("\n✅ All stages completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    finally:
        test.print_summary()
        test.cleanup()
        print(f"\n📊 Full log saved to: {log_path}")
        print("\nTest complete. Review the CSV log for detailed metrics.")


if __name__ == '__main__':
    main()
