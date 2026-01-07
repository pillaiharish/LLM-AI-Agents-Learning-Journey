#!/usr/bin/env python3
"""
Safe GPU/CPU Stress Test Monitor for RTX 5070 Ti 16GB & Ryzen 9900X
Monitors temperatures and enforces safety thresholds
"""

import subprocess
import time
import csv
import os
import sys
from datetime import datetime
from collections import deque
import json

class SafetyMonitor:
    def __init__(self, config_file='config.json'):
        """Initialize safety monitor with hardware-specific thresholds"""
        self.config = self.load_config(config_file)
        self.log_file = None
        self.csv_writer = None
        self.running = False
        
        # Safety threshold history (for sustained violations)
        self.cpu_temp_history = deque(maxlen=10)  # 10 seconds
        self.gpu_temp_history = deque(maxlen=10)
        self.gpu_hotspot_history = deque(maxlen=10)
        self.gpu_power_history = deque(maxlen=10)
        self.throttle_history = deque(maxlen=10)
        
        # Maximum values for summary
        self.max_cpu_temp = 0
        self.max_gpu_temp = 0
        self.max_gpu_hotspot = 0
        self.max_cpu_power = 0
        self.max_gpu_power = 0
        self.throttle_detected = False
        
    def load_config(self, config_file):
        """Load or create default configuration"""
        default_config = {
            "safety_thresholds": {
                "cpu_temp_max": 90,  # Conservative for Ryzen 9900X (spec is 95°C)
                "gpu_temp_max": 83,  # Conservative for RTX 5070 Ti (spec is 87°C)
                "gpu_hotspot_max": 100,  # Conservative (spec is 105°C)
                "gpu_power_max": 285,  # RTX 5070 Ti TDP is ~285W
                "sustained_violation_seconds": 10
            },
            "test_stages": {
                "idle_duration": 120,
                "cpu_blend_duration": 300,
                "cpu_smallfft_duration": 300,
                "gpu_stress_duration": 600,
                "combined_duration": 600,
                "cooldown_duration": 120
            },
            "monitoring": {
                "poll_interval": 1.0,
                "log_directory": "logs"
            },
            "hardware": {
                "cpu_model": "AMD Ryzen 9900X",
                "gpu_model": "NVIDIA RTX 5070 Ti 16GB"
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except:
                print(f"Warning: Could not load {config_file}, using defaults")
        else:
            # Save default config
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Created default config: {config_file}")
        
        return default_config
    
    def init_logging(self):
        """Initialize CSV logging"""
        log_dir = self.config['monitoring']['log_directory']
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_path = os.path.join(log_dir, f'stress_test_{timestamp}.csv')
        
        self.log_file = open(log_path, 'w', newline='')
        self.csv_writer = csv.writer(self.log_file)
        
        # Write header
        self.csv_writer.writerow([
            'Timestamp', 'Stage', 'CPU_Temp_C', 'CPU_Power_W', 'CPU_Usage_%',
            'GPU_Temp_C', 'GPU_Hotspot_C', 'GPU_Power_W', 'GPU_Usage_%',
            'GPU_Fan_RPM', 'CPU_Throttle', 'Safety_Status'
        ])
        self.log_file.flush()
        
        print(f"Logging to: {log_path}")
        return log_path
    
    def get_nvidia_stats(self):
        """Query NVIDIA GPU stats using nvidia-smi"""
        try:
            # nvidia-smi query for RTX 5070 Ti
            cmd = [
                'nvidia-smi',
                '--query-gpu=temperature.gpu,power.draw,utilization.gpu,fan.speed,clocks.current.graphics',
                '--format=csv,noheader,nounits'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                values = result.stdout.strip().split(',')
                return {
                    'gpu_temp': float(values[0].strip()),
                    'gpu_power': float(values[1].strip()),
                    'gpu_usage': float(values[2].strip()),
                    'gpu_fan': float(values[3].strip()),
                    'gpu_clock': float(values[4].strip())
                }
        except Exception as e:
            print(f"Warning: Could not query NVIDIA GPU: {e}")
        
        return None
    
    def get_cpu_stats(self):
        """Query CPU stats (platform-dependent)"""
        # This is a placeholder - actual implementation depends on platform
        # On Windows, you'd parse HWiNFO64 CSV or use WMI
        # On Linux, you'd read from /sys/class/hwmon or use lm-sensors
        
        try:
            # Try to get CPU temperature from Linux sensors
            if sys.platform.startswith('linux'):
                # Look for k10temp (AMD Ryzen sensor)
                cmd = ['sensors', '-u']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    cpu_temp = None
                    
                    for line in lines:
                        # Look for Tctl or Tdie
                        if 'Tctl_input' in line or 'Tdie_input' in line:
                            cpu_temp = float(line.split(':')[1].strip())
                            break
                    
                    # Get CPU usage from /proc/stat
                    with open('/proc/stat', 'r') as f:
                        line = f.readline()
                        values = [int(x) for x in line.split()[1:]]
                        idle = values[3]
                        total = sum(values)
                        cpu_usage = 100 * (1 - idle / total) if total > 0 else 0
                    
                    return {
                        'cpu_temp': cpu_temp if cpu_temp else 0,
                        'cpu_power': 0,  # Not easily available on Linux without specialized tools
                        'cpu_usage': cpu_usage,
                        'throttle': False  # Would need to check throttle flags
                    }
        except Exception as e:
            print(f"Warning: Could not query CPU stats: {e}")
        
        return None
    
    def check_safety(self, cpu_stats, gpu_stats):
        """Check if safety thresholds are violated"""
        thresholds = self.config['safety_thresholds']
        violations = []
        
        if cpu_stats and cpu_stats['cpu_temp'] > 0:
            self.cpu_temp_history.append(cpu_stats['cpu_temp'] >= thresholds['cpu_temp_max'])
            if cpu_stats['cpu_temp'] > self.max_cpu_temp:
                self.max_cpu_temp = cpu_stats['cpu_temp']
        
        if gpu_stats:
            self.gpu_temp_history.append(gpu_stats['gpu_temp'] >= thresholds['gpu_temp_max'])
            self.gpu_power_history.append(gpu_stats['gpu_power'] >= thresholds['gpu_power_max'])
            
            if gpu_stats['gpu_temp'] > self.max_gpu_temp:
                self.max_gpu_temp = gpu_stats['gpu_temp']
            if gpu_stats['gpu_power'] > self.max_gpu_power:
                self.max_gpu_power = gpu_stats['gpu_power']
        
        if cpu_stats and cpu_stats.get('throttle', False):
            self.throttle_history.append(True)
            self.throttle_detected = True
        
        # Check for sustained violations (>10 seconds)
        sustained_secs = thresholds['sustained_violation_seconds']
        
        if len(self.cpu_temp_history) >= sustained_secs:
            if sum(self.cpu_temp_history) >= sustained_secs:
                violations.append(f"CPU temp ≥{thresholds['cpu_temp_max']}°C for {sustained_secs}s")
        
        if len(self.gpu_temp_history) >= sustained_secs:
            if sum(self.gpu_temp_history) >= sustained_secs:
                violations.append(f"GPU temp ≥{thresholds['gpu_temp_max']}°C for {sustained_secs}s")
        
        if len(self.gpu_power_history) >= sustained_secs:
            if sum(self.gpu_power_history) >= sustained_secs:
                violations.append(f"GPU power ≥{thresholds['gpu_power_max']}W for {sustained_secs}s")
        
        if len(self.throttle_history) >= sustained_secs:
            if sum(self.throttle_history) >= sustained_secs:
                violations.append(f"CPU throttling for {sustained_secs}s")
        
        return violations
    
    def log_metrics(self, stage, cpu_stats, gpu_stats, safety_status):
        """Log current metrics to CSV"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        row = [
            timestamp,
            stage,
            cpu_stats['cpu_temp'] if cpu_stats else 0,
            cpu_stats['cpu_power'] if cpu_stats else 0,
            cpu_stats['cpu_usage'] if cpu_stats else 0,
            gpu_stats['gpu_temp'] if gpu_stats else 0,
            0,  # GPU hotspot (not available via nvidia-smi basic query)
            gpu_stats['gpu_power'] if gpu_stats else 0,
            gpu_stats['gpu_usage'] if gpu_stats else 0,
            gpu_stats['gpu_fan'] if gpu_stats else 0,
            cpu_stats.get('throttle', False) if cpu_stats else False,
            safety_status
        ]
        
        self.csv_writer.writerow(row)
        self.log_file.flush()
    
    def monitor_stage(self, stage_name, duration_seconds):
        """Monitor a test stage for the specified duration"""
        print(f"\n{'='*60}")
        print(f"Stage: {stage_name}")
        print(f"Duration: {duration_seconds} seconds")
        print(f"{'='*60}")
        
        start_time = time.time()
        poll_interval = self.config['monitoring']['poll_interval']
        
        while (time.time() - start_time) < duration_seconds:
            # Get current stats
            cpu_stats = self.get_cpu_stats()
            gpu_stats = self.get_nvidia_stats()
            
            # Check safety
            violations = self.check_safety(cpu_stats, gpu_stats)
            
            if violations:
                safety_status = "VIOLATION: " + "; ".join(violations)
                print(f"\n⚠️  SAFETY VIOLATION DETECTED!")
                for v in violations:
                    print(f"   - {v}")
                self.log_metrics(stage_name, cpu_stats, gpu_stats, safety_status)
                return False  # Stop test
            
            safety_status = "OK"
            
            # Display current stats
            elapsed = int(time.time() - start_time)
            remaining = duration_seconds - elapsed
            
            print(f"\r[{elapsed:4d}/{duration_seconds}s] ", end='')
            if cpu_stats:
                print(f"CPU: {cpu_stats['cpu_temp']:.1f}°C ", end='')
            if gpu_stats:
                print(f"GPU: {gpu_stats['gpu_temp']:.1f}°C {gpu_stats['gpu_power']:.1f}W ", end='')
            print(f"Status: {safety_status}    ", end='', flush=True)
            
            # Log to CSV
            self.log_metrics(stage_name, cpu_stats, gpu_stats, safety_status)
            
            time.sleep(poll_interval)
        
        print()  # New line after stage completes
        return True  # Stage completed successfully
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Hardware: {self.config['hardware']['cpu_model']}")
        print(f"          {self.config['hardware']['gpu_model']}")
        print()
        print(f"Max CPU Temperature:    {self.max_cpu_temp:.1f}°C")
        print(f"Max GPU Temperature:    {self.max_gpu_temp:.1f}°C")
        print(f"Max GPU Hotspot:        {self.max_gpu_hotspot:.1f}°C")
        print(f"Max CPU Power:          {self.max_cpu_power:.1f}W")
        print(f"Max GPU Power:          {self.max_gpu_power:.1f}W")
        print(f"Throttling Detected:    {'YES ⚠️' if self.throttle_detected else 'NO'}")
        print("="*60)
        
        # Safety margin analysis
        thresholds = self.config['safety_thresholds']
        cpu_margin = thresholds['cpu_temp_max'] - self.max_cpu_temp
        gpu_margin = thresholds['gpu_temp_max'] - self.max_gpu_temp
        
        print("\nSafety Margins:")
        print(f"  CPU: {cpu_margin:.1f}°C below threshold")
        print(f"  GPU: {gpu_margin:.1f}°C below threshold")
        
        if cpu_margin < 5 or gpu_margin < 5:
            print("\n⚠️  Warning: Low safety margin detected!")
            print("   Consider improving cooling or reducing load.")
        else:
            print("\n✓ Good thermal performance with adequate safety margins")
    
    def cleanup(self):
        """Clean up resources"""
        if self.log_file:
            self.log_file.close()


def main():
    """Main stress test workflow"""
    print("="*60)
    print("Safe GPU/CPU Stress Test for RTX 5070 Ti & Ryzen 9900X")
    print("="*60)
    print()
    print("⚠️  IMPORTANT: Before starting:")
    print("   1. Close all unnecessary applications")
    print("   2. Ensure good ventilation/cooling")
    print("   3. Monitor the test and stay near the computer")
    print("   4. Press Ctrl+C to stop at any time")
    print()
    
    response = input("Ready to start monitoring? (yes/no): ")
    if response.lower() != 'yes':
        print("Test cancelled.")
        return
    
    monitor = SafetyMonitor()
    log_path = monitor.init_logging()
    
    print("\n📊 Monitoring active. Log file:", log_path)
    print("\nNOTE: This script monitors only. You must manually start:")
    print("  - Prime95 for CPU stress")
    print("  - FurMark or Unigine Superposition for GPU stress")
    print()
    
    try:
        # Stage A: Idle baseline
        if not monitor.monitor_stage("Idle Baseline", 
                                     monitor.config['test_stages']['idle_duration']):
            print("\n❌ Test stopped due to safety violation during idle (check cooling!)")
            return
        
        print("\n✓ Idle baseline complete")
        print("\n📝 Now start Prime95 in 'Blend' mode and press Enter...")
        input()
        
        # Stage B1: CPU Blend
        if not monitor.monitor_stage("CPU Blend", 
                                     monitor.config['test_stages']['cpu_blend_duration']):
            print("\n❌ Test stopped due to safety violation")
            return
        
        print("\n✓ CPU Blend complete. Cooling down...")
        if not monitor.monitor_stage("Cooldown", 
                                     monitor.config['test_stages']['cooldown_duration']):
            return
        
        print("\n📝 Switch Prime95 to 'Small FFTs' mode and press Enter...")
        input()
        
        # Stage B2: CPU Small FFTs
        if not monitor.monitor_stage("CPU Small FFTs", 
                                     monitor.config['test_stages']['cpu_smallfft_duration']):
            print("\n❌ Test stopped due to safety violation")
            return
        
        print("\n✓ CPU Small FFTs complete. Cooling down...")
        print("   Stop Prime95 now.")
        if not monitor.monitor_stage("Cooldown", 
                                     monitor.config['test_stages']['cooldown_duration']):
            return
        
        print("\n📝 Now start GPU stress test (FurMark or Superposition) and press Enter...")
        input()
        
        # Stage C: GPU stress
        if not monitor.monitor_stage("GPU Stress", 
                                     monitor.config['test_stages']['gpu_stress_duration']):
            print("\n❌ Test stopped due to safety violation")
            return
        
        print("\n✓ GPU stress complete. Cooling down...")
        if not monitor.monitor_stage("Cooldown", 
                                     monitor.config['test_stages']['cooldown_duration']):
            return
        
        print("\n📝 Now start BOTH Prime95 (Blend) + GPU stress and press Enter...")
        input()
        
        # Stage D: Combined stress
        if not monitor.monitor_stage("Combined CPU+GPU", 
                                     monitor.config['test_stages']['combined_duration']):
            print("\n❌ Test stopped due to safety violation")
            return
        
        print("\n✓ Combined stress complete!")
        print("   Stop all stress tests now.")
        
        # Final cooldown
        monitor.monitor_stage("Final Cooldown", 
                            monitor.config['test_stages']['cooldown_duration'])
        
        print("\n✅ All test stages completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    finally:
        monitor.print_summary()
        monitor.cleanup()
        print(f"\n📊 Full log saved to: {log_path}")


if __name__ == '__main__':
    main()
