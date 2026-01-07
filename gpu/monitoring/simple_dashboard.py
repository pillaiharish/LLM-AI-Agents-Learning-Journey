#!/usr/bin/env python3
"""
GPU and CPU Monitoring Dashboard
A web-based monitoring system for GPU and CPU stats including temperature and utilization.
"""

from flask import Flask, render_template, jsonify
import psutil
import time
import json
from datetime import datetime
import pynvml
import logging
import os
import socket
from waitress import serve

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize NVIDIA GPU monitoring
try:
    pynvml.nvmlInit()
    GPU_AVAILABLE = True
    logger.info("NVIDIA GPU monitoring initialized successfully")
except Exception as e:
    GPU_AVAILABLE = False
    logger.warning(f"NVIDIA GPU not available: {e}")

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # Method 1: Connect to a remote host to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            # Method 2: Get hostname and resolve it
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            if ip.startswith('127.'):
                # Method 3: Try to get first non-loopback interface
                import subprocess
                result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
                if result.returncode == 0:
                    ips = result.stdout.strip().split()
                    for ip in ips:
                        if not ip.startswith('127.') and not ip.startswith('169.254.'):
                            return ip
            return ip
        except Exception:
            return "127.0.0.1"

def get_cpu_info():
    """Get CPU usage, temperature, and frequency information"""
    cpu_info = {
        'usage_percent': 0,
        'usage_per_core': [],
        'core_count': 0,
        'physical_cores': 0,
        'frequency': {},
        'temperature': {'current': 'N/A', 'high': 'N/A', 'critical': 'N/A'}
    }
    
    try:
        # Get CPU usage
        cpu_info['usage_percent'] = psutil.cpu_percent(interval=1)
        cpu_info['usage_per_core'] = psutil.cpu_percent(percpu=True)
        cpu_info['core_count'] = psutil.cpu_count(logical=True)
        cpu_info['physical_cores'] = psutil.cpu_count(logical=False)
    except Exception as e:
        logger.warning(f"Could not get CPU usage info: {e}")
    
    # Get CPU frequency
    try:
        freq = psutil.cpu_freq()
        if freq:
            cpu_info['frequency'] = {
                'current': round(freq.current, 2),
                'min': round(freq.min, 2),
                'max': round(freq.max, 2)
            }
    except Exception as e:
        logger.warning(f"Could not get CPU frequency: {e}")
    
    # Get CPU temperature
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            # Try different common sensor names
            temp_sensors = ['coretemp', 'cpu_thermal', 'acpi', 'k10temp']
            for sensor_name in temp_sensors:
                if sensor_name in temps:
                    cpu_temps = temps[sensor_name]
                    if cpu_temps:
                        # Get the first available temperature reading
                        cpu_info['temperature'] = {
                            'current': round(cpu_temps[0].current, 1),
                            'high': cpu_temps[0].high if cpu_temps[0].high else 'N/A',
                            'critical': cpu_temps[0].critical if cpu_temps[0].critical else 'N/A'
                        }
                        break
    except Exception as e:
        logger.warning(f"Could not get CPU temperature: {e}")
    
    return cpu_info

def get_memory_info():
    """Get system memory information"""
    try:
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total': round(memory.total / (1024**3), 2),  # GB
            'available': round(memory.available / (1024**3), 2),  # GB
            'used': round(memory.used / (1024**3), 2),  # GB
            'percent': memory.percent,
            'swap_total': round(swap.total / (1024**3), 2),  # GB
            'swap_used': round(swap.used / (1024**3), 2),  # GB
            'swap_percent': swap.percent
        }
    except Exception as e:
        logger.error(f"Error getting memory info: {e}")
        return {
            'total': 0,
            'available': 0,
            'used': 0,
            'percent': 0,
            'swap_total': 0,
            'swap_used': 0,
            'swap_percent': 0
        }

def get_gpu_info():
    """Get GPU information including temperature, utilization, and memory usage"""
    if not GPU_AVAILABLE:
        return []
    
    gpu_list = []
    try:
        device_count = pynvml.nvmlDeviceGetCount()
        
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            
            # Get GPU name
            name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
            
            # Get memory info
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            # Get utilization
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            
            # Get temperature
            try:
                temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            except Exception:
                temp = 'N/A'
            
            # Get power usage
            try:
                power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
            except Exception:
                power = 'N/A'
            
            # Get fan speed
            try:
                fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
            except Exception:
                fan_speed = 'N/A'
            
            gpu_info = {
                'index': i,
                'name': name,
                'temperature': temp,
                'utilization': {
                    'gpu': util.gpu,
                    'memory': util.memory
                },
                'memory': {
                    'total': round(mem_info.total / (1024**3), 2),  # GB
                    'used': round(mem_info.used / (1024**3), 2),   # GB
                    'free': round(mem_info.free / (1024**3), 2),   # GB
                    'percent': round((mem_info.used / mem_info.total) * 100, 1)
                },
                'power': power,
                'fan_speed': fan_speed
            }
            
            gpu_list.append(gpu_info)
            
    except Exception as e:
        logger.error(f"Error getting GPU info: {e}")
    
    return gpu_list

def get_disk_info():
    """Get disk usage information"""
    try:
        disk_usage = psutil.disk_usage('/')
        return {
            'total': round(disk_usage.total / (1024**3), 2),  # GB
            'used': round(disk_usage.used / (1024**3), 2),   # GB
            'free': round(disk_usage.free / (1024**3), 2),   # GB
            'percent': round((disk_usage.used / disk_usage.total) * 100, 1)
        }
    except Exception as e:
        logger.error(f"Error getting disk info: {e}")
        return {
            'total': 0,
            'used': 0,
            'free': 0,
            'percent': 0
        }

def get_system_info():
    """Get general system information"""
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        # Try multiple methods to get hostname
        hostname = 'unknown'
        try:
            hostname = socket.gethostname()
            if not hostname or hostname == 'localhost':
                # Try reading from /etc/hostname
                with open('/etc/hostname', 'r') as f:
                    hostname = f.read().strip()
        except Exception:
            try:
                hostname = os.uname().nodename
            except Exception:
                hostname = 'admin1-MS-7D75'  # fallback
        
        return {
            'hostname': hostname,
            'platform': psutil.uname().system,
            'architecture': psutil.uname().machine,
            'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S'),
            'uptime': str(uptime).split('.')[0],  # Remove microseconds
            'load_average': list(os.getloadavg()) if hasattr(os, 'getloadavg') else 'N/A'
        }
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return {
            'hostname': 'admin1-MS-7D75',
            'platform': 'Linux',
            'architecture': 'x86_64',
            'boot_time': 'unknown',
            'uptime': 'unknown',
            'load_average': 'N/A'
        }

@app.route('/')
def dashboard():
    """Serve the main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """API endpoint to get all system stats"""
    try:
        stats = {
            'timestamp': datetime.now().isoformat(),
            'cpu': get_cpu_info(),
            'memory': get_memory_info(),
            'gpu': get_gpu_info(),
            'disk': get_disk_info(),
            'system': get_system_info()
        }
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/debug')
def debug_info():
    """Debug endpoint to test individual components"""
    debug_data = {}
    
    try:
        debug_data['cpu'] = get_cpu_info()
        debug_data['cpu_status'] = 'OK'
    except Exception as e:
        debug_data['cpu_status'] = f'ERROR: {str(e)}'
        debug_data['cpu'] = None
    
    try:
        debug_data['memory'] = get_memory_info()
        debug_data['memory_status'] = 'OK'
    except Exception as e:
        debug_data['memory_status'] = f'ERROR: {str(e)}'
        debug_data['memory'] = None
    
    try:
        debug_data['gpu'] = get_gpu_info()
        debug_data['gpu_status'] = 'OK'
    except Exception as e:
        debug_data['gpu_status'] = f'ERROR: {str(e)}'
        debug_data['gpu'] = None
    
    try:
        debug_data['disk'] = get_disk_info()
        debug_data['disk_status'] = 'OK'
    except Exception as e:
        debug_data['disk_status'] = f'ERROR: {str(e)}'
        debug_data['disk'] = None
    
    try:
        debug_data['system'] = get_system_info()
        debug_data['system_status'] = 'OK'
    except Exception as e:
        debug_data['system_status'] = f'ERROR: {str(e)}'
        debug_data['system'] = None
    
    return jsonify(debug_data)

if __name__ == '__main__':
    # Get the local IP address
    local_ip = get_local_ip()
    port = int(os.environ.get('MONITOR_PORT', 5000))
    
    # SSL/HTTPS configuration
    ssl_cert = os.environ.get('SSL_CERT_PATH', '/home/admin1/work/gpu-monitoring/ssl/cert.pem')
    ssl_key = os.environ.get('SSL_KEY_PATH', '/home/admin1/work/gpu-monitoring/ssl/key.pem')
    use_https = os.environ.get('USE_HTTPS', 'true').lower() == 'true'
    
    logger.info(f"Starting GPU/CPU monitoring dashboard...")
    logger.info(f"Detected local IP: {local_ip}")
    
    if use_https and os.path.exists(ssl_cert) and os.path.exists(ssl_key):
        logger.info(f"HTTPS enabled")
        logger.info(f"Local access: https://127.0.0.1:{port}")
        logger.info(f"Network access: https://{local_ip}:{port}")
        logger.info(f"Starting HTTPS server on 0.0.0.0:{port}")
        
        # Use waitress with SSL
        from waitress.server import create_server
        server = create_server(app, host='0.0.0.0', port=port, threads=4,
                             ssl_context=(ssl_cert, ssl_key))
        server.run()
    else:
        logger.info(f"HTTP mode (SSL certificates not found or HTTPS disabled)")
        logger.info(f"Local access: http://127.0.0.1:{port}")
        logger.info(f"Network access: http://{local_ip}:{port}")
        logger.info(f"Starting HTTP server on 0.0.0.0:{port}")
        
        # Use waitress for production-ready WSGI server
        serve(app, host='0.0.0.0', port=port, threads=4)