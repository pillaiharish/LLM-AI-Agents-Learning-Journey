#!/usr/bin/env python3
"""
Prometheus Metrics Exporter for GPU/CPU Monitoring Dashboard
Converts the monitoring dashboard API data to Prometheus metrics format
"""

import time
import requests
import logging
from prometheus_client import start_http_server, Gauge, Info
import os
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
MONITOR_API_URL = os.environ.get('MONITOR_API_URL', 'http://localhost:5000')
EXPORTER_PORT = int(os.environ.get('EXPORTER_PORT', '8080'))
SCRAPE_INTERVAL = int(os.environ.get('SCRAPE_INTERVAL', '30'))

# SSL configuration - disable verification for self-signed certs
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Dashboard URL patterns to try (fallbacks)
DASHBOARD_URL_PATTERNS = [
    MONITOR_API_URL,
    'http://localhost:5000',
    'https://localhost:5000',
    'http://127.0.0.1:5000',
    'https://127.0.0.1:5000'
]

# Prometheus metrics
# CPU metrics
cpu_usage_percent = Gauge('cpu_usage_percent', 'CPU usage percentage')
cpu_usage_per_core = Gauge('cpu_usage_per_core_percent', 'CPU usage per core', ['core'])
cpu_temperature = Gauge('cpu_temperature_celsius', 'CPU temperature in Celsius')
cpu_frequency = Gauge('cpu_frequency_mhz', 'CPU frequency in MHz', ['type'])

# Memory metrics
memory_total_gb = Gauge('memory_total_gb', 'Total memory in GB')
memory_used_gb = Gauge('memory_used_gb', 'Used memory in GB')
memory_available_gb = Gauge('memory_available_gb', 'Available memory in GB')
memory_usage_percent = Gauge('memory_usage_percent', 'Memory usage percentage')
swap_total_gb = Gauge('swap_total_gb', 'Total swap in GB')
swap_used_gb = Gauge('swap_used_gb', 'Used swap in GB')
swap_usage_percent = Gauge('swap_usage_percent', 'Swap usage percentage')

# GPU metrics
gpu_utilization = Gauge('gpu_utilization_percent', 'GPU utilization percentage', ['gpu_id', 'gpu_name'])
gpu_memory_utilization = Gauge('gpu_memory_utilization_percent', 'GPU memory utilization percentage', ['gpu_id', 'gpu_name'])
gpu_memory_total_gb = Gauge('gpu_memory_total_gb', 'GPU memory total in GB', ['gpu_id', 'gpu_name'])
gpu_memory_used_gb = Gauge('gpu_memory_used_gb', 'GPU memory used in GB', ['gpu_id', 'gpu_name'])
gpu_memory_free_gb = Gauge('gpu_memory_free_gb', 'GPU memory free in GB', ['gpu_id', 'gpu_name'])
gpu_temperature = Gauge('gpu_temperature_celsius', 'GPU temperature in Celsius', ['gpu_id', 'gpu_name'])
gpu_power_watts = Gauge('gpu_power_watts', 'GPU power consumption in Watts', ['gpu_id', 'gpu_name'])
gpu_fan_speed_percent = Gauge('gpu_fan_speed_percent', 'GPU fan speed percentage', ['gpu_id', 'gpu_name'])

# Disk metrics
disk_total_gb = Gauge('disk_total_gb', 'Total disk space in GB')
disk_used_gb = Gauge('disk_used_gb', 'Used disk space in GB')
disk_free_gb = Gauge('disk_free_gb', 'Free disk space in GB')
disk_usage_percent = Gauge('disk_usage_percent', 'Disk usage percentage')

# System metrics
system_uptime_seconds = Gauge('system_uptime_seconds', 'System uptime in seconds')
system_load_average = Gauge('system_load_average', 'System load average', ['period'])

# System info
system_info = Info('system_info', 'System information')

def safe_float(value, default=0.0):
    """Safely convert value to float"""
    if value is None or value == 'N/A' or value == 'unknown':
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    """Safely convert value to int"""
    if value is None or value == 'N/A' or value == 'unknown':
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def parse_uptime(uptime_str):
    """Parse uptime string to seconds"""
    if not uptime_str or uptime_str == 'unknown':
        return 0
    
    try:
        # Handle formats like "1:23:45" or "1 day, 2:34:56"
        if 'day' in uptime_str:
            parts = uptime_str.split(', ')
            days = int(parts[0].split()[0])
            time_part = parts[1] if len(parts) > 1 else '0:00:00'
        else:
            days = 0
            time_part = uptime_str
        
        time_parts = time_part.split(':')
        hours = int(time_parts[0]) if len(time_parts) > 0 else 0
        minutes = int(time_parts[1]) if len(time_parts) > 1 else 0
        seconds = int(time_parts[2]) if len(time_parts) > 2 else 0
        
        return days * 86400 + hours * 3600 + minutes * 60 + seconds
    except Exception:
        return 0

def collect_metrics():
    """Collect metrics from the monitoring API"""
    for url in DASHBOARD_URL_PATTERNS:
        try:
            logger.info(f"Attempting to connect to {url}/api/stats")
            response = requests.get(f"{url}/api/stats", timeout=15, verify=False)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Successfully retrieved data from {url}")
            
            # CPU metrics
            if 'cpu' in data:
                cpu_data = data['cpu']
                cpu_usage_percent.set(safe_float(cpu_data.get('usage_percent')))
                
                # Per-core CPU usage
                cpu_usage_per_core.clear()
                for i, usage in enumerate(cpu_data.get('usage_per_core', [])):
                    cpu_usage_per_core.labels(core=str(i)).set(safe_float(usage))
                
                # CPU temperature
                temp_data = cpu_data.get('temperature', {})
                if isinstance(temp_data, dict) and 'current' in temp_data:
                    cpu_temperature.set(safe_float(temp_data['current']))
                
                # CPU frequency
                freq_data = cpu_data.get('frequency', {})
                if isinstance(freq_data, dict):
                    for freq_type, freq_value in freq_data.items():
                        cpu_frequency.labels(type=freq_type).set(safe_float(freq_value))
            
            # Memory metrics
            if 'memory' in data:
                mem_data = data['memory']
                memory_total_gb.set(safe_float(mem_data.get('total')))
                memory_used_gb.set(safe_float(mem_data.get('used')))
                memory_available_gb.set(safe_float(mem_data.get('available')))
                memory_usage_percent.set(safe_float(mem_data.get('percent')))
                swap_total_gb.set(safe_float(mem_data.get('swap_total')))
                swap_used_gb.set(safe_float(mem_data.get('swap_used')))
                swap_usage_percent.set(safe_float(mem_data.get('swap_percent')))
            
            # GPU metrics
            if 'gpu' in data and data['gpu']:
                # Clear previous GPU metrics
                gpu_utilization.clear()
                gpu_memory_utilization.clear()
                gpu_memory_total_gb.clear()
                gpu_memory_used_gb.clear()
                gpu_memory_free_gb.clear()
                gpu_temperature.clear()
                gpu_power_watts.clear()
                gpu_fan_speed_percent.clear()
                
                for gpu in data['gpu']:
                    gpu_id = str(gpu.get('index', 0))
                    gpu_name = gpu.get('name', 'Unknown')
                    
                    # Utilization
                    util_data = gpu.get('utilization', {})
                    gpu_utilization.labels(gpu_id=gpu_id, gpu_name=gpu_name).set(safe_float(util_data.get('gpu')))
                    gpu_memory_utilization.labels(gpu_id=gpu_id, gpu_name=gpu_name).set(safe_float(util_data.get('memory')))
                    
                    # Memory
                    mem_data = gpu.get('memory', {})
                    gpu_memory_total_gb.labels(gpu_id=gpu_id, gpu_name=gpu_name).set(safe_float(mem_data.get('total')))
                    gpu_memory_used_gb.labels(gpu_id=gpu_id, gpu_name=gpu_name).set(safe_float(mem_data.get('used')))
                    gpu_memory_free_gb.labels(gpu_id=gpu_id, gpu_name=gpu_name).set(safe_float(mem_data.get('free')))
                    
                    # Temperature, power, fan
                    gpu_temperature.labels(gpu_id=gpu_id, gpu_name=gpu_name).set(safe_float(gpu.get('temperature')))
                    gpu_power_watts.labels(gpu_id=gpu_id, gpu_name=gpu_name).set(safe_float(gpu.get('power')))
                    gpu_fan_speed_percent.labels(gpu_id=gpu_id, gpu_name=gpu_name).set(safe_float(gpu.get('fan_speed')))
            
            # Disk metrics
            if 'disk' in data:
                disk_data = data['disk']
                disk_total_gb.set(safe_float(disk_data.get('total')))
                disk_used_gb.set(safe_float(disk_data.get('used')))
                disk_free_gb.set(safe_float(disk_data.get('free')))
                disk_usage_percent.set(safe_float(disk_data.get('percent')))
            
            # System metrics
            if 'system' in data:
                sys_data = data['system']
                
                # Uptime
                uptime_str = sys_data.get('uptime', '')
                system_uptime_seconds.set(parse_uptime(uptime_str))
                
                # Load average
                load_avg = sys_data.get('load_average')
                if load_avg and load_avg != 'N/A' and isinstance(load_avg, list):
                    periods = ['1min', '5min', '15min']
                    for i, period in enumerate(periods):
                        if i < len(load_avg):
                            system_load_average.labels(period=period).set(safe_float(load_avg[i]))
                
                # System info
                system_info.info({
                    'hostname': sys_data.get('hostname', 'unknown'),
                    'platform': sys_data.get('platform', 'unknown'),
                    'architecture': sys_data.get('architecture', 'unknown'),
                    'boot_time': sys_data.get('boot_time', 'unknown')
                })
            
            logger.info("Metrics updated successfully")
            return  # Successfully collected metrics, exit function
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from {url}: {e}")
            continue  # Try next URL
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response from {url}: {e}")
            continue  # Try next URL
        except Exception as e:
            logger.error(f"Unexpected error collecting metrics from {url}: {e}")
            continue  # Try next URL

    # If we get here, all URLs failed
    logger.error("All dashboard URLs failed, metrics not updated")

def main():
    """Main function"""
    logger.info(f"Starting Prometheus exporter on port {EXPORTER_PORT}")
    logger.info(f"Monitoring API URL: {MONITOR_API_URL}")
    logger.info(f"Scrape interval: {SCRAPE_INTERVAL} seconds")
    
    # Start HTTP server
    start_http_server(EXPORTER_PORT)
    
    # Collect metrics in loop
    while True:
        try:
            collect_metrics()
            time.sleep(SCRAPE_INTERVAL)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(SCRAPE_INTERVAL)

if __name__ == '__main__':
    main()