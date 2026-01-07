#!/usr/bin/env python3
"""
GPU/CPU Stress Test & Benchmark Tool
Universal stress testing tool for any NVIDIA GPU and CPU with configurable parameters
"""

import subprocess
import time
import csv
import os
import sys
import json
import argparse
from datetime import datetime
from collections import deque

class HardwareDetector:
    """Automatically detect GPU and CPU specifications"""
    
    @staticmethod
    def get_gpu_info():
        """Detect GPU model and maximum temperature"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=gpu_name,temperature.gpu.tlimit', 
                 '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split(',')
                gpu_name = parts[0].strip()
                # tlimit is the throttle temperature, usually we want 10% below
                gpu_max_temp = int(parts[1].strip()) if len(parts) > 1 else 87
                return gpu_name, gpu_max_temp
        except Exception as e:
            print(f"Warning: Could not detect GPU info: {e}")
        
        return "Unknown NVIDIA GPU", 87  # Default safe temperature
    
    @staticmethod
    def get_cpu_info():
        """Detect CPU model and specifications"""
        try:
            # Try lscpu on Linux
            result = subprocess.run(['lscpu'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Model name:' in line:
                        cpu_name = line.split(':', 1)[1].strip()
                        # Detect CPU type for temperature defaults
                        if 'AMD' in cpu_name.upper() or 'RYZEN' in cpu_name.upper():
                            return cpu_name, 95  # AMD default Tjmax
                        elif 'INTEL' in cpu_name.upper():
                            return cpu_name, 100  # Intel default Tjmax
                        return cpu_name, 95
        except Exception:
            pass
        
        return "Unknown CPU", 95  # Default safe temperature

class StressTester:
    """Main stress testing and monitoring class"""
    
    def __init__(self, config):
        self.config = config
        self.log_file = None
        self.csv_writer = None
        self.running = False
        self.start_time = None
        
        # Safety monitoring history
        self.gpu_temp_history = deque(maxlen=10)
        self.gpu_power_history = deque(maxlen=10)
        
        # Statistics
        self.max_gpu_temp = 0
        self.max_gpu_power = 0
        self.max_cpu_temp = 0
        
    def initialize_logging(self):
        """Setup CSV logging for metrics"""
        os.makedirs(self.config['log_directory'], exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(
            self.config['log_directory'],
            f"stress_test_{timestamp}.csv"
        )
        
        self.log_file = open(log_path, 'w', newline='')
        self.csv_writer = csv.writer(self.log_file)
        self.csv_writer.writerow([
            'Timestamp', 'Elapsed_s', 'GPU_Temp_C', 'GPU_Power_W',
            'GPU_Util_%', 'GPU_Fan_%', 'GPU_Clock_MHz', 'Status'
        ])
        self.log_file.flush()
        
        print(f"\n📊 Logging to: {log_path}")
        return log_path
    
    def get_gpu_metrics(self):
        """Query GPU metrics using nvidia-smi"""
        try:
            result = subprocess.run([
                'nvidia-smi',
                '--query-gpu=temperature.gpu,power.draw,utilization.gpu,fan.speed,clocks.gr',
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0:
                values = [v.strip() for v in result.stdout.strip().split(',')]
                return {
                    'temp': float(values[0]) if values[0] != 'N/A' else 0,
                    'power': float(values[1]) if values[1] != 'N/A' else 0,
                    'util': float(values[2]) if values[2] != 'N/A' else 0,
                    'fan': float(values[3]) if values[3] != 'N/A' else 0,
                    'clock': float(values[4]) if values[4] != 'N/A' else 0
                }
        except Exception as e:
            print(f"Warning: GPU metrics query failed: {e}")
        
        return None
    
    def check_safety(self, metrics):
        """Check if current metrics violate safety thresholds"""
        if not metrics:
            return True, "No metrics"
        
        temp_threshold = self.config['safety']['gpu_temp_max']
        power_threshold = self.config['safety'].get('gpu_power_max', 999)
        
        # Track history for sustained violations
        self.gpu_temp_history.append(metrics['temp'])
        self.gpu_power_history.append(metrics['power'])
        
        # Update max values
        self.max_gpu_temp = max(self.max_gpu_temp, metrics['temp'])
        self.max_gpu_power = max(self.max_gpu_power, metrics['power'])
        
        # Check for sustained violations (>10 consecutive samples)
        sustained_temp_violation = all(t >= temp_threshold for t in self.gpu_temp_history)
        sustained_power_violation = all(p >= power_threshold for p in self.gpu_power_history)
        
        if sustained_temp_violation:
            return False, f"CRITICAL: GPU temperature sustained ≥{temp_threshold}°C"
        
        if sustained_power_violation:
            return False, f"CRITICAL: GPU power sustained ≥{power_threshold}W"
        
        # Warning status
        if metrics['temp'] >= temp_threshold:
            return True, f"WARNING: Temp={metrics['temp']}°C"
        
        return True, "OK"
    
    def monitor_loop(self, duration_seconds):
        """Main monitoring loop during stress test"""
        self.start_time = time.time()
        elapsed = 0
        
        print("\n" + "="*70)
        print(f"{'Time(s)':<8} {'Temp(°C)':<10} {'Power(W)':<10} {'Util(%)':<10} {'Fan(%)':<10} {'Status':<15}")
        print("="*70)
        
        while elapsed < duration_seconds and self.running:
            metrics = self.get_gpu_metrics()
            
            if metrics:
                safe, status = self.check_safety(metrics)
                
                # Log to CSV
                if self.csv_writer:
                    self.csv_writer.writerow([
                        datetime.now().isoformat(),
                        int(elapsed),
                        f"{metrics['temp']:.1f}",
                        f"{metrics['power']:.2f}",
                        f"{metrics['util']:.0f}",
                        f"{metrics['fan']:.0f}",
                        f"{metrics['clock']:.0f}",
                        status
                    ])
                    self.log_file.flush()
                
                # Console output
                print(f"{int(elapsed):<8} {metrics['temp']:<10.1f} {metrics['power']:<10.1f} "
                      f"{metrics['util']:<10.0f} {metrics['fan']:<10.0f} {status:<15}")
                
                if not safe:
                    print(f"\n🚨 SAFETY VIOLATION: {status}")
                    return False
            
            time.sleep(1)
            elapsed = time.time() - self.start_time
        
        return True
    
    def run_gpu_stress(self, duration_minutes):
        """Run GPU stress test using gpu-burn"""
        duration_seconds = int(duration_minutes * 60)
        
        print(f"\n🔥 Starting GPU Stress Test")
        print(f"Duration: {duration_minutes} minutes ({duration_seconds} seconds)")
        print(f"Safety threshold: {self.config['safety']['gpu_temp_max']}°C")
        print(f"Test type: {self.config['test_type']}")
        
        # Check if gpu-burn exists
        gpu_burn_path = os.path.join(os.path.dirname(__file__), 'gpu-burn', 'gpu_burn')
        if not os.path.exists(gpu_burn_path):
            print(f"\n❌ Error: gpu-burn not found at {gpu_burn_path}")
            print("Please run: ./setup.sh to install dependencies")
            return False
        
        log_path = self.initialize_logging()
        self.running = True
        
        # Start gpu-burn in background
        print(f"\n🚀 Launching gpu-burn...")
        try:
            gpu_process = subprocess.Popen(
                [gpu_burn_path, str(duration_seconds)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            print(f"✓ GPU stress process started (PID: {gpu_process.pid})")
            
            # Monitor during the test
            success = self.monitor_loop(duration_seconds)
            
            # Wait for gpu-burn to complete
            gpu_process.wait(timeout=10)
            
            if success:
                self.print_summary()
                return True
            else:
                print("\n⚠️  Test stopped due to safety violation")
                gpu_process.terminate()
                return False
                
        except Exception as e:
            print(f"\n❌ Error during stress test: {e}")
            return False
        finally:
            if self.log_file:
                self.log_file.close()
            self.running = False
    
    def print_summary(self):
        """Print test summary statistics"""
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        print(f"Maximum GPU Temperature: {self.max_gpu_temp:.1f}°C")
        print(f"Maximum GPU Power:       {self.max_gpu_power:.1f}W")
        print(f"Safety Threshold:        {self.config['safety']['gpu_temp_max']}°C")
        print(f"Thermal Margin:          {self.config['safety']['gpu_temp_max'] - self.max_gpu_temp:.1f}°C")
        
        if self.max_gpu_temp < self.config['safety']['gpu_temp_max']:
            print("\n✅ Test completed successfully within safety limits!")
        else:
            print("\n⚠️  Test approached or exceeded safety limits")
        print("="*70)

def get_user_config():
    """Interactive configuration from user"""
    print("\n" + "="*70)
    print("🔧 GPU/CPU STRESS TEST CONFIGURATOR")
    print("="*70)
    
    # Detect hardware
    print("\n🔍 Detecting hardware...")
    gpu_name, gpu_spec_temp = HardwareDetector.get_gpu_info()
    cpu_name, cpu_spec_temp = HardwareDetector.get_cpu_info()
    
    print(f"  GPU: {gpu_name} (Spec Max: {gpu_spec_temp}°C)")
    print(f"  CPU: {cpu_name} (Spec Max: {cpu_spec_temp}°C)")
    
    # Test type selection
    print("\n📋 Select test type:")
    print("  1. GPU only (recommended)")
    print("  2. CPU only")
    print("  3. Both GPU + CPU (maximum stress)")
    
    test_choice = input("\nEnter choice [1-3, default=1]: ").strip() or "1"
    test_types = {"1": "GPU", "2": "CPU", "3": "Both"}
    test_type = test_types.get(test_choice, "GPU")
    
    # Duration selection
    print("\n⏱️  Select test duration:")
    print("  1. 2 minutes (quick test)")
    print("  2. 5 minutes (standard)")
    print("  3. 10 minutes (thorough)")
    print("  4. Custom duration")
    
    duration_choice = input("\nEnter choice [1-4, default=1]: ").strip() or "1"
    duration_map = {"1": 2, "2": 5, "3": 10}
    
    if duration_choice == "4":
        duration = float(input("Enter duration in minutes: "))
    else:
        duration = duration_map.get(duration_choice, 2)
    
    # Temperature threshold (conservative: 10% below spec)
    default_gpu_threshold = int(gpu_spec_temp * 0.9)
    print(f"\n🌡️  GPU temperature safety threshold:")
    print(f"  GPU Spec Max: {gpu_spec_temp}°C")
    print(f"  Recommended (90% of spec): {default_gpu_threshold}°C")
    
    gpu_threshold_input = input(f"\nEnter GPU temp threshold [default={default_gpu_threshold}°C]: ").strip()
    gpu_threshold = int(gpu_threshold_input) if gpu_threshold_input else default_gpu_threshold
    
    # Validate threshold
    if gpu_threshold > gpu_spec_temp:
        print(f"⚠️  Warning: {gpu_threshold}°C exceeds GPU spec ({gpu_spec_temp}°C)!")
        confirm = input("Continue anyway? [y/N]: ").strip().lower()
        if confirm != 'y':
            gpu_threshold = default_gpu_threshold
            print(f"Using recommended threshold: {gpu_threshold}°C")
    
    # Power limit (optional)
    print(f"\n⚡ GPU power limit (optional):")
    print("  Press Enter to skip power limiting")
    power_input = input("Enter max power in Watts [default=unlimited]: ").strip()
    power_limit = int(power_input) if power_input else 999
    
    # Summary
    print("\n" + "="*70)
    print("📋 CONFIGURATION SUMMARY")
    print("="*70)
    print(f"Test Type:           {test_type}")
    print(f"Duration:            {duration} minutes")
    print(f"GPU Threshold:       {gpu_threshold}°C (spec: {gpu_spec_temp}°C)")
    print(f"Power Limit:         {power_limit}W" if power_limit < 999 else "Power Limit:         Unlimited")
    print(f"Hardware:            {gpu_name}")
    print("="*70)
    
    confirm = input("\nProceed with this configuration? [Y/n]: ").strip().lower()
    if confirm == 'n':
        print("Configuration cancelled.")
        sys.exit(0)
    
    return {
        'test_type': test_type,
        'duration_minutes': duration,
        'safety': {
            'gpu_temp_max': gpu_threshold,
            'gpu_power_max': power_limit
        },
        'log_directory': 'logs',
        'hardware': {
            'gpu_name': gpu_name,
            'gpu_spec_temp': gpu_spec_temp,
            'cpu_name': cpu_name,
            'cpu_spec_temp': cpu_spec_temp
        }
    }

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='GPU/CPU Stress Test & Benchmark Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 benchmark.py                    # Interactive mode
  python3 benchmark.py --duration 5       # 5-minute test with defaults
  python3 benchmark.py --temp 80 --duration 10  # Custom settings
        """
    )
    parser.add_argument('--duration', type=float, help='Test duration in minutes')
    parser.add_argument('--temp', type=int, help='GPU temperature threshold in °C')
    parser.add_argument('--power', type=int, help='GPU power limit in Watts')
    parser.add_argument('--type', choices=['gpu', 'cpu', 'both'], default='gpu',
                       help='Test type (default: gpu)')
    parser.add_argument('--non-interactive', action='store_true',
                       help='Run with defaults without prompts')
    
    args = parser.parse_args()
    
    # Get configuration
    if args.non_interactive:
        # Auto-detect and use safe defaults
        gpu_name, gpu_spec_temp = HardwareDetector.get_gpu_info()
        config = {
            'test_type': args.type.upper(),
            'duration_minutes': args.duration or 2,
            'safety': {
                'gpu_temp_max': args.temp or int(gpu_spec_temp * 0.9),
                'gpu_power_max': args.power or 999
            },
            'log_directory': 'logs',
            'hardware': {'gpu_name': gpu_name}
        }
        print(f"\n🤖 Running in non-interactive mode with detected settings")
        print(f"GPU: {gpu_name}, Threshold: {config['safety']['gpu_temp_max']}°C")
    else:
        config = get_user_config()
    
    # Run the test
    tester = StressTester(config)
    
    try:
        success = tester.run_gpu_stress(config['duration_minutes'])
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user (Ctrl+C)")
        tester.running = False
        sys.exit(130)

if __name__ == '__main__':
    main()
