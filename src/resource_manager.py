import psutil
import threading
import time
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
import json
import os
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

@dataclass
class ResourceLimits:
    """Resource usage limits based on Inverse Shannon-Nyquist"""
    cpu_percent: float = 50.0  # Maximum CPU usage (50%)
    memory_percent: float = 50.0  # Maximum memory usage (50%)
    disk_io_percent: float = 50.0  # Maximum disk I/O (50%)
    network_io_percent: float = 50.0  # Maximum network I/O (50%)
    max_threads: int = 0  # Will be set based on CPU count
    max_processes: int = 0  # Will be set based on CPU count
    
    def __post_init__(self):
        """Set thread and process limits based on CPU count"""
        cpu_count = psutil.cpu_count(logical=False)
        self.max_threads = max(1, cpu_count // 2)  # Half of physical cores
        self.max_processes = max(1, cpu_count // 2)  # Half of physical cores

class ResourceMonitor:
    """Monitors system resources and enforces limits"""
    
    def __init__(self, limits: Optional[ResourceLimits] = None):
        self.limits = limits or ResourceLimits()
        self._lock = threading.Lock()
        self._active_tasks: Set[str] = set()
        self._task_resources: Dict[str, Dict[str, float]] = {}
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        
    def start_monitoring(self):
        """Start resource monitoring"""
        if not self._monitoring:
            self._monitoring = True
            self._monitor_thread = threading.Thread(target=self._monitor_resources)
            self._monitor_thread.daemon = True
            self._monitor_thread.start()
            
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join()
            
    def _monitor_resources(self):
        """Monitor system resources and enforce limits"""
        while self._monitoring:
            try:
                with self._lock:
                    # Check CPU usage
                    cpu_percent = psutil.cpu_percent(interval=1)
                    if cpu_percent > self.limits.cpu_percent:
                        self._throttle_tasks("cpu", cpu_percent)
                        
                    # Check memory usage
                    memory = psutil.virtual_memory()
                    if memory.percent > self.limits.memory_percent:
                        self._throttle_tasks("memory", memory.percent)
                        
                    # Check disk I/O
                    disk_io = psutil.disk_io_counters()
                    if disk_io:
                        disk_usage = (disk_io.read_bytes + disk_io.write_bytes) / (1024 * 1024)  # MB
                        if disk_usage > self.limits.disk_io_percent:
                            self._throttle_tasks("disk", disk_usage)
                            
                    # Check network I/O
                    net_io = psutil.net_io_counters()
                    if net_io:
                        net_usage = (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024)  # MB
                        if net_usage > self.limits.network_io_percent:
                            self._throttle_tasks("network", net_usage)
                            
            except Exception as e:
                logging.error(f"Error monitoring resources: {e}")
                
            time.sleep(1)  # Check every second
            
    def _throttle_tasks(self, resource: str, usage: float):
        """Throttle tasks when resource usage exceeds limits"""
        with self._lock:
            for task_id in self._active_tasks:
                if task_id in self._task_resources:
                    # Reduce task resource allocation
                    self._task_resources[task_id][resource] *= 0.8  # Reduce by 20%
                    
    def register_task(self, task_id: str, resources: Dict[str, float]):
        """Register a new task and its resource requirements"""
        with self._lock:
            self._active_tasks.add(task_id)
            self._task_resources[task_id] = resources.copy()
            
    def unregister_task(self, task_id: str):
        """Unregister a completed task"""
        with self._lock:
            self._active_tasks.discard(task_id)
            self._task_resources.pop(task_id, None)
            
    def get_task_resources(self, task_id: str) -> Dict[str, float]:
        """Get current resource allocation for a task"""
        with self._lock:
            return self._task_resources.get(task_id, {}).copy()

class ResourceAwareExecutor:
    """Executes tasks with resource awareness"""
    
    def __init__(self, resource_monitor: ResourceMonitor):
        self.monitor = resource_monitor
        self.thread_pool = ThreadPoolExecutor(
            max_workers=self.monitor.limits.max_threads,
            thread_name_prefix="ResourceAware"
        )
        
    def submit(self, task_id: str, fn, *args, **kwargs):
        """Submit a task for execution"""
        # Register task with estimated resource usage
        self.monitor.register_task(task_id, {
            "cpu": 10.0,  # Initial estimate
            "memory": 10.0,
            "disk": 0.0,
            "network": 0.0
        })
        
        # Submit task to thread pool
        future = self.thread_pool.submit(self._wrap_task, task_id, fn, *args, **kwargs)
        return future
        
    def _wrap_task(self, task_id: str, fn, *args, **kwargs):
        """Wrap task execution with resource monitoring"""
        try:
            result = fn(*args, **kwargs)
            return result
        finally:
            self.monitor.unregister_task(task_id)
            
    def shutdown(self, wait=True):
        """Shutdown the executor"""
        self.thread_pool.shutdown(wait=wait)

class ResourceConfig:
    """Manages resource configuration from markdown"""
    
    def __init__(self, config_path: str = "config.md"):
        self.config_path = config_path
        self.limits = ResourceLimits()
        self.load_config()
        
    def load_config(self):
        """Load resource configuration from markdown"""
        try:
            with open(self.config_path, 'r') as f:
                content = f.read()
                
            # Extract resource limits from markdown
            for line in content.split('\n'):
                if line.startswith('|') and 'Resource' in line:
                    continue  # Skip header
                if '|' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 3:
                        resource = parts[1]
                        limit = float(parts[2].replace('%', ''))
                        if limit > 50:  # Enforce Inverse Shannon-Nyquist
                            limit = 50.0
                        setattr(self.limits, f"{resource.lower()}_percent", limit)
                        
        except Exception as e:
            logging.error(f"Error loading resource config: {e}")
            
    def save_config(self):
        """Save resource configuration to markdown"""
        try:
            # Create markdown table
            content = """# Resource Configuration

| Resource | Limit | Description |
|----------|-------|-------------|
"""
            for attr in dir(self.limits):
                if attr.endswith('_percent'):
                    resource = attr.replace('_percent', '').upper()
                    limit = getattr(self.limits, attr)
                    content += f"| {resource} | {limit}% | Maximum {resource.lower()} usage |\n"
                    
            with open(self.config_path, 'w') as f:
                f.write(content)
                
        except Exception as e:
            logging.error(f"Error saving resource config: {e}")
            
    def update_limit(self, resource: str, limit: float):
        """Update a resource limit"""
        if limit > 50:  # Enforce Inverse Shannon-Nyquist
            limit = 50.0
        setattr(self.limits, f"{resource.lower()}_percent", limit)
        self.save_config()

# Example usage:
if __name__ == "__main__":
    # Initialize resource management
    config = ResourceConfig()
    monitor = ResourceMonitor(config.limits)
    executor = ResourceAwareExecutor(monitor)
    
    # Start monitoring
    monitor.start_monitoring()
    
    try:
        # Example task
        def example_task(task_id: str):
            resources = monitor.get_task_resources(task_id)
            print(f"Task {task_id} running with resources: {resources}")
            time.sleep(2)
            
        # Submit tasks
        futures = []
        for i in range(5):
            task_id = f"task_{i}"
            future = executor.submit(task_id, example_task, task_id)
            futures.append(future)
            
        # Wait for completion
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Task failed: {e}")
                
    finally:
        # Cleanup
        executor.shutdown()
        monitor.stop_monitoring() 