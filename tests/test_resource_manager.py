import unittest
from unittest.mock import MagicMock, patch
import time
import psutil
from src.resource_manager import (
    ResourceLimits,
    ResourceMonitor,
    ResourceAwareExecutor,
    ResourceConfig
)

class TestResourceLimits(unittest.TestCase):
    def setUp(self):
        self.limits = ResourceLimits()
        
    def test_initial_limits(self):
        """Test initial resource limits"""
        self.assertEqual(self.limits.cpu_percent, 50.0)
        self.assertEqual(self.limits.memory_percent, 50.0)
        self.assertEqual(self.limits.disk_io_percent, 50.0)
        self.assertEqual(self.limits.network_io_percent, 50.0)
        
    def test_thread_process_limits(self):
        """Test thread and process limits based on CPU count"""
        cpu_count = psutil.cpu_count(logical=False)
        expected_threads = max(1, cpu_count // 2)
        expected_processes = max(1, cpu_count // 2)
        
        self.assertEqual(self.limits.max_threads, expected_threads)
        self.assertEqual(self.limits.max_processes, expected_processes)

class TestResourceMonitor(unittest.TestCase):
    def setUp(self):
        self.limits = ResourceLimits()
        self.monitor = ResourceMonitor(self.limits)
        
    def test_initial_state(self):
        """Test initial monitor state"""
        self.assertFalse(self.monitor._monitoring)
        self.assertIsNone(self.monitor._monitor_thread)
        self.assertEqual(len(self.monitor._active_tasks), 0)
        self.assertEqual(len(self.monitor._task_resources), 0)
        
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    def test_resource_monitoring(self, mock_memory, mock_cpu):
        """Test resource monitoring"""
        # Mock resource usage
        mock_cpu.return_value = 60.0  # Above limit
        mock_memory.return_value = MagicMock(percent=40.0)  # Below limit
        
        # Start monitoring
        self.monitor.start_monitoring()
        self.assertTrue(self.monitor._monitoring)
        
        # Register a task
        task_id = "test_task"
        resources = {"cpu": 20.0, "memory": 10.0}
        self.monitor.register_task(task_id, resources)
        
        # Wait for monitoring cycle
        time.sleep(2)
        
        # Check if task was throttled
        task_resources = self.monitor.get_task_resources(task_id)
        self.assertLess(task_resources["cpu"], 20.0)  # Should be reduced
        
        # Stop monitoring
        self.monitor.stop_monitoring()
        self.assertFalse(self.monitor._monitoring)
        
    def test_task_registration(self):
        """Test task registration and unregistration"""
        task_id = "test_task"
        resources = {"cpu": 20.0, "memory": 10.0}
        
        # Register task
        self.monitor.register_task(task_id, resources)
        self.assertIn(task_id, self.monitor._active_tasks)
        self.assertEqual(self.monitor._task_resources[task_id], resources)
        
        # Unregister task
        self.monitor.unregister_task(task_id)
        self.assertNotIn(task_id, self.monitor._active_tasks)
        self.assertNotIn(task_id, self.monitor._task_resources)

class TestResourceAwareExecutor(unittest.TestCase):
    def setUp(self):
        self.limits = ResourceLimits()
        self.monitor = ResourceMonitor(self.limits)
        self.executor = ResourceAwareExecutor(self.monitor)
        
    def tearDown(self):
        self.executor.shutdown()
        
    def test_task_submission(self):
        """Test task submission and execution"""
        def test_task(task_id):
            return f"Task {task_id} completed"
            
        # Submit task
        future = self.executor.submit("test_task", test_task)
        result = future.result()
        
        self.assertEqual(result, "Task test_task completed")
        self.assertNotIn("test_task", self.monitor._active_tasks)
        
    def test_concurrent_tasks(self):
        """Test concurrent task execution"""
        def slow_task(task_id):
            time.sleep(0.1)
            return f"Task {task_id} completed"
            
        # Submit multiple tasks
        futures = []
        for i in range(5):
            future = self.executor.submit(f"task_{i}", slow_task)
            futures.append(future)
            
        # Check results
        for i, future in enumerate(futures):
            result = future.result()
            self.assertEqual(result, f"Task task_{i} completed")

class TestResourceConfig(unittest.TestCase):
    def setUp(self):
        self.config = ResourceConfig("test_config.md")
        
    def tearDown(self):
        # Clean up test config file
        try:
            import os
            os.remove("test_config.md")
        except:
            pass
            
    def test_config_loading(self):
        """Test loading configuration from markdown"""
        # Create test config
        with open("test_config.md", "w") as f:
            f.write("""# Resource Configuration

| Resource | Limit | Description |
|----------|-------|-------------|
| CPU | 40% | Maximum CPU usage |
| MEMORY | 45% | Maximum memory usage |
| DISK | 30% | Maximum disk I/O |
| NETWORK | 35% | Maximum network I/O |
""")
            
        # Load config
        self.config.load_config()
        
        # Check limits
        self.assertEqual(self.config.limits.cpu_percent, 40.0)
        self.assertEqual(self.config.limits.memory_percent, 45.0)
        self.assertEqual(self.config.limits.disk_io_percent, 30.0)
        self.assertEqual(self.config.limits.network_io_percent, 35.0)
        
    def test_config_saving(self):
        """Test saving configuration to markdown"""
        # Update limits
        self.config.update_limit("cpu", 40.0)
        self.config.update_limit("memory", 45.0)
        
        # Save config
        self.config.save_config()
        
        # Reload and check
        new_config = ResourceConfig("test_config.md")
        new_config.load_config()
        
        self.assertEqual(new_config.limits.cpu_percent, 40.0)
        self.assertEqual(new_config.limits.memory_percent, 45.0)
        
    def test_limit_enforcement(self):
        """Test Inverse Shannon-Nyquist limit enforcement"""
        # Try to set limit above 50%
        self.config.update_limit("cpu", 60.0)
        self.assertEqual(self.config.limits.cpu_percent, 50.0)
        
        # Try to set limit below 50%
        self.config.update_limit("memory", 30.0)
        self.assertEqual(self.config.limits.memory_percent, 30.0)

if __name__ == '__main__':
    unittest.main() 