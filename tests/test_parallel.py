import unittest
import time
import threading
from src.I_am_the_GUI_GOD import ParallelTestRunner, ImprovementGenerator, TestResult, Improvement, DebugMonitor
from src.core.config import ConfigManager

class TestParallelComponents(unittest.TestCase):
    def setUp(self):
        self.config = ConfigManager()
        self.test_runner = ParallelTestRunner()
        self.improvement_generator = ImprovementGenerator(self.config)
        self.debug_monitor = DebugMonitor()
        
    def tearDown(self):
        self.test_runner.cleanup()
        self.improvement_generator.cleanup()
        
    def test_parallel_test_runner(self):
        """Test parallel test execution"""
        def success_test():
            return {"result": "success"}
            
        def failure_test():
            raise ValueError("Test failure")
            
        def timeout_test():
            time.sleep(2)
            return {"result": "timeout"}
            
        # Add tests
        self.test_runner.add_test(success_test)
        self.test_runner.add_test(failure_test)
        self.test_runner.add_test(timeout_test)
        
        # Get results
        results = self.test_runner.get_results()
        
        # Verify results
        self.assertEqual(len(results), 3)
        success_results = [r for r in results if r.success]
        failure_results = [r for r in results if not r.success]
        
        self.assertEqual(len(success_results), 1)
        self.assertEqual(len(failure_results), 2)
        
    def test_improvement_generator(self):
        """Test improvement generation"""
        # Create test results
        test_result = TestResult(
            success=False,
            error="Test failure",
            metrics={"severity": "high"}
        )
        
        # Add test result
        self.improvement_generator.add_test_result(test_result)
        
        # Get improvements
        improvements = self.improvement_generator.get_improvements()
        
        # Verify improvements
        self.assertTrue(len(improvements) > 0)
        improvement = improvements[0]
        self.assertIsInstance(improvement, Improvement)
        self.assertIn("error_type", improvement.code_changes)
        self.assertIn("suggested_fix", improvement.code_changes)
        self.assertTrue(0 <= improvement.priority <= 10)
        self.assertTrue(0 <= improvement.confidence <= 1)
        self.assertTrue(0 <= improvement.test_coverage <= 1)
        
    def test_debug_monitor(self):
        """Test debug monitoring"""
        # Test FPS updates
        self.debug_monitor.update_fps(60.0)
        self.assertEqual(self.debug_monitor.current_fps, 60.0)
        
        # Test Zot tracking
        self.debug_monitor.add_zot("test_zot")
        self.assertIn("test_zot", self.debug_monitor.active_zots)
        self.assertEqual(len(self.debug_monitor.active_zots), 1)
        
        self.debug_monitor.remove_zot("test_zot")
        self.assertNotIn("test_zot", self.debug_monitor.active_zots)
        self.assertEqual(len(self.debug_monitor.active_zots), 0)
        
        # Test improvement counting
        self.assertEqual(self.debug_monitor.improvement_count, 0)
        self.debug_monitor.increment_improvements()
        self.assertEqual(self.debug_monitor.improvement_count, 1)
        
        # Test metrics collection
        metrics = self.debug_monitor.metrics
        self.assertIn("fps", metrics)
        self.assertIn("memory_usage", metrics)
        self.assertIn("cpu_usage", metrics)
        self.assertIn("active_zots", metrics)
        self.assertIn("improvement_count", metrics)
        
    def test_concurrent_improvements(self):
        """Test concurrent improvement generation"""
        def generate_improvements():
            for i in range(5):
                test_result = TestResult(
                    success=False,
                    error=f"Test failure {i}",
                    metrics={"severity": "high"}
                )
                self.improvement_generator.add_test_result(test_result)
                
        # Start multiple threads generating improvements
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=generate_improvements)
            thread.start()
            threads.append(thread)
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        # Get improvements
        improvements = self.improvement_generator.get_improvements()
        
        # Verify improvements
        self.assertTrue(len(improvements) > 0)
        self.assertTrue(all(isinstance(imp, Improvement) for imp in improvements))
        
    def test_test_result_metadata(self):
        """Test test result metadata"""
        # Create test result with metadata
        test_result = TestResult(
            success=True,
            metrics={"performance": 0.95, "memory": 100},
            timestamp=time.time()
        )
        
        # Verify metadata
        self.assertTrue(test_result.success)
        self.assertIsNone(test_result.error)
        self.assertIn("performance", test_result.metrics)
        self.assertIn("memory", test_result.metrics)
        self.assertIsNotNone(test_result.timestamp)
        
    def test_improvement_metadata(self):
        """Test improvement metadata"""
        # Create improvement with metadata
        improvement = Improvement(
            description="Test improvement",
            code_changes={"file": "test.py", "changes": "test changes"},
            priority=5,
            confidence=0.8,
            test_coverage=0.9,
            timestamp=time.time()
        )
        
        # Verify metadata
        self.assertEqual(improvement.description, "Test improvement")
        self.assertIn("file", improvement.code_changes)
        self.assertIn("changes", improvement.code_changes)
        self.assertEqual(improvement.priority, 5)
        self.assertEqual(improvement.confidence, 0.8)
        self.assertEqual(improvement.test_coverage, 0.9)
        self.assertIsNotNone(improvement.timestamp)

if __name__ == '__main__':
    unittest.main() 