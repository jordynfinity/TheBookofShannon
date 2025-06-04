import unittest
import sys
import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import coverage
import ast
from .russelian_collapse import RusselianCollapse
from .config import ConfigManager

@dataclass
class TestResult:
    """Results from running tests"""
    passed: bool
    coverage: float
    failed_tests: List[str]
    error_messages: List[str]
    coverage_report: Dict[str, float]

class TestDrivenImprovement:
    """Integrates testing into the improvement cycle"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self._setup_logging()
        self.coverage = coverage.Coverage()
        self.russelian_collapse = RusselianCollapse()
        self.test_suite = unittest.TestLoader().discover('tests')
        
    def _setup_logging(self):
        """Set up logging for the test-driven improvement system"""
        self.logger = logging.getLogger('TestDrivenImprovement')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('logs/test_driven_improvement.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
    def run_tests(self) -> TestResult:
        """Run all tests with coverage tracking"""
        self.coverage.start()
        runner = unittest.TextTestRunner()
        result = runner.run(self.test_suite)
        self.coverage.stop()
        
        # Get coverage report
        coverage_report = {}
        for file in self.coverage.get_data().measured_files():
            coverage_report[file] = self.coverage.report(file)
            
        return TestResult(
            passed=result.wasSuccessful(),
            coverage=self.coverage.report(),
            failed_tests=[str(test) for test in result.failures + result.errors],
            error_messages=[str(error) for error in result.errors],
            coverage_report=coverage_report
        )
        
    def validate_improvement(self, improvement: Dict[str, Any]) -> bool:
        """Validate an improvement against tests"""
        # Run tests before improvement
        before_result = self.run_tests()
        
        # Apply improvement
        try:
            # Apply the improvement (this would be implemented by the improvement system)
            self._apply_improvement(improvement)
            
            # Run tests after improvement
            after_result = self.run_tests()
            
            # Validate that improvement didn't break anything
            if not after_result.passed:
                self.logger.error(f"Improvement broke tests: {after_result.failed_tests}")
                return False
                
            # Check if coverage improved
            if after_result.coverage < before_result.coverage:
                self.logger.warning("Improvement reduced test coverage")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying improvement: {str(e)}")
            return False
            
    def suggest_test_improvements(self) -> List[Dict[str, Any]]:
        """Suggest improvements based on test coverage gaps"""
        self.coverage.start()
        self.run_tests()
        self.coverage.stop()
        
        improvements = []
        for file in self.coverage.get_data().measured_files():
            # Get uncovered lines
            uncovered = self.coverage.analysis(file)[2]
            if uncovered:
                # Parse file to get context
                with open(file, 'r') as f:
                    tree = ast.parse(f.read())
                    
                # Find functions/methods that need testing
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        if any(line in uncovered for line in range(node.lineno, node.end_lineno)):
                            improvements.append({
                                'type': 'test_coverage',
                                'file': file,
                                'target': node.name,
                                'lines': list(range(node.lineno, node.end_lineno)),
                                'description': f"Add tests for {node.name} in {file}"
                            })
                            
        return improvements
        
    def _apply_improvement(self, improvement: Dict[str, Any]):
        """Apply an improvement (to be implemented by improvement system)"""
        # This would be implemented by your improvement system
        pass
        
    def cleanup(self):
        """Clean up resources"""
        self.coverage.save()
        self.coverage.erase() 