import psutil
import logging
from typing import Dict, Any, Optional, List
import os
import time
from dataclasses import dataclass

@dataclass
class ResourceMetrics:
    """Metrics for resource usage"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, float]
    timestamp: float

class ResourceManager:
    """Manages system resources and optimization"""
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_history: List[ResourceMetrics] = []
        self.optimization_threshold = 0.8  # 80% usage triggers optimization
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging for resource manager"""
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
    def get_metrics(self) -> ResourceMetrics:
        """Get current resource metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            metrics = ResourceMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=disk.percent,
                network_io={
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv
                },
                timestamp=time.time()
            )
            
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > 1000:  # Keep last 1000 metrics
                self.metrics_history.pop(0)
                
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting metrics: {e}")
            return ResourceMetrics(0, 0, 0, {}, time.time())
            
    def check_resources(self) -> Dict[str, float]:
        """Check if resources need optimization"""
        metrics = self.get_metrics()
        return {
            'cpu': metrics.cpu_percent / 100.0,
            'memory': metrics.memory_percent / 100.0,
            'disk': metrics.disk_percent / 100.0
        }
        
    def optimize_resources(self) -> bool:
        """Attempt to optimize resource usage"""
        try:
            metrics = self.get_metrics()
            
            # Optimize memory if needed
            if metrics.memory_percent > self.optimization_threshold * 100:
                self._optimize_memory()
                
            # Optimize CPU if needed
            if metrics.cpu_percent > self.optimization_threshold * 100:
                self._optimize_cpu()
                
            # Optimize disk if needed
            if metrics.disk_percent > self.optimization_threshold * 100:
                self._optimize_disk()
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error optimizing resources: {e}")
            return False
            
    def _optimize_memory(self):
        """Optimize memory usage"""
        try:
            # Clear memory caches
            if os.name == 'nt':  # Windows
                os.system('powershell -Command "Clear-RecycleBin -Force"')
            else:  # Unix-like
                os.system('sync; echo 3 > /proc/sys/vm/drop_caches')
                
            # Force garbage collection
            import gc
            gc.collect()
            
        except Exception as e:
            self.logger.error(f"Error optimizing memory: {e}")
            
    def _optimize_cpu(self):
        """Optimize CPU usage"""
        try:
            # Set process priority
            process = psutil.Process()
            process.nice(10)  # Lower priority
            
        except Exception as e:
            self.logger.error(f"Error optimizing CPU: {e}")
            
    def _optimize_disk(self):
        """Optimize disk usage"""
        try:
            # Clear temporary files
            temp_dir = os.path.join(os.environ.get('TEMP', '/tmp'))
            for file in os.listdir(temp_dir):
                try:
                    file_path = os.path.join(temp_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error optimizing disk: {e}")
            
    def get_resource_trends(self) -> Dict[str, List[float]]:
        """Get resource usage trends"""
        if not self.metrics_history:
            return {'cpu': [], 'memory': [], 'disk': []}
            
        return {
            'cpu': [m.cpu_percent for m in self.metrics_history],
            'memory': [m.memory_percent for m in self.metrics_history],
            'disk': [m.disk_percent for m in self.metrics_history]
        }
        
    def cleanup(self):
        """Clean up resource manager"""
        try:
            self.metrics_history.clear()
        except Exception as e:
            self.logger.error(f"Error cleaning up resource manager: {e}") 