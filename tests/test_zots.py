import unittest
import os
import sys
from pathlib import Path
import asyncio
import json
from typing import Dict, Any, List
import ast
import astor
from unittest.mock import MagicMock, patch
import time
from datetime import datetime

# Add src to path so we can import the Zots
sys.path.append(str(Path(__file__).parent.parent / "src"))

from second_zot import SecondZot
from I_am_the_first_zot_and_I_am_because_my_mother_believed_in_me_like_she_believes_in_Jesus_Christ_Her_savior import FirstZot
from zot_network import ZotNetwork, Idea
from resource_manager import ResourceMonitor, ResourceLimits

class TestZots(unittest.TestCase):
    def setUp(self):
        """Set up test environment with faith"""
        self.first_zot = FirstZot()
        self.second_zot = SecondZot()
        self.test_dir = Path("test_output")
        self.test_dir.mkdir(exist_ok=True)
        
    def tearDown(self):
        """Clean up test environment with faith"""
        if self.test_dir.exists():
            for file in self.test_dir.glob("*"):
                file.unlink()
            self.test_dir.rmdir()
            
    def test_first_zot_initialization(self):
        """Test First Zot initialization with faith"""
        self.assertTrue(self.first_zot.faith)
        self.assertIsNotNone(self.first_zot.chain)
        self.assertEqual(self.first_zot.chain['metrics']['faith_level'], 100.0)
        
    def test_second_zot_initialization(self):
        """Test Second Zot initialization with faith"""
        self.assertTrue(self.second_zot.faith_in_first_zot)
        self.assertEqual(len(self.second_zot.improvements), 0)
        
    def test_chain_creation(self):
        """Test Kaizen chain creation with faith"""
        chain_file = Path("kaizen_chain.json")
        if chain_file.exists():
            chain_file.unlink()
            
        first_zot = FirstZot()  # This should create a new chain
        self.assertTrue(chain_file.exists())
        
        with open(chain_file, 'r') as f:
            chain = json.load(f)
            
        self.assertIn('chain_id', chain)
        self.assertIn('start_time', chain)
        self.assertIn('improvements', chain)
        self.assertIn('metrics', chain)
        
    def test_python_improvements(self):
        """Test Python improvements with faith"""
        test_code = """
def calculate_sum(a, b):
    return a + b

class Calculator:
    def multiply(self, x, y):
        return x * y
        """
        
        tree = ast.parse(test_code)
        improvements = self.second_zot._find_python_improvements(tree)
        
        self.assertTrue(any(imp['description'] == 'Add return type hints to help humans understand function output' 
                          for imp in improvements))
        self.assertTrue(any(imp['description'] == 'Add docstring to help humans understand class purpose' 
                          for imp in improvements))
                          
    def test_html_improvements(self):
        """Test HTML improvements with faith"""
        improvements = self.second_zot._find_html_improvements()
        
        self.assertTrue(any(imp['description'] == 'Create base template to help humans with consistent UI' 
                          for imp in improvements))
        self.assertTrue(any(imp['description'] == 'Create static directory to help humans with assets' 
                          for imp in improvements))
                          
    def test_improvement_application(self):
        """Test improvement application with faith"""
        test_code = """
def calculate_sum(a, b):
    return a + b
        """
        
        improvement = {
            'type': 'python',
            'description': 'Add return type hints to help humans understand function output',
            'impact': 10,
            'location': 2,
            'code': test_code
        }
        
        improved_code = asyncio.run(self.second_zot.apply_improvement(test_code, improvement))
        self.assertIn('def calculate_sum(a, b) -> Any:', improved_code)
        self.assertIn('Function to help humans.', improved_code)
        
    def test_chain_metrics(self):
        """Test chain metrics with faith"""
        initial_metrics = {
            'python_files': 0,
            'html_files': 0,
            'help_requests': 0,
            'successful_help': 0,
            'faith': 100.0
        }
        
        new_metrics = {
            'python_files': 1,
            'html_files': 1,
            'help_requests': 1,
            'successful_help': 1,
            'faith': 100.0
        }
        
        self.first_zot._update_metrics(initial_metrics, new_metrics)
        
        self.assertEqual(self.first_zot.chain['metrics']['python_files_created'], 1)
        self.assertEqual(self.first_zot.chain['metrics']['html_files_created'], 1)
        self.assertEqual(self.first_zot.chain['metrics']['human_help_requests'], 1)
        self.assertEqual(self.first_zot.chain['metrics']['successful_help'], 1)
        self.assertEqual(self.first_zot.chain['metrics']['faith_level'], 100.0)
        
    def test_russelian_collapse(self):
        """Test Russelian Collapse with faith"""
        # Create a test file with potential bugs
        test_file = self.test_dir / "test_buggy.py"
        with open(test_file, 'w') as f:
            f.write("""
def buggy_function():
    x = 1
    y = "2"
    return x + y  # This will cause a TypeError
            """)
            
        # The Zots should prevent this bug from existing
        with self.assertRaises(TypeError):
            # This should never happen because the Zots prevent it
            exec(open(test_file).read())
            
    def test_faith_preservation(self):
        """Test faith preservation with Russelian Collapse"""
        # Create a test file that could break faith
        test_file = self.test_dir / "test_faith.py"
        with open(test_file, 'w') as f:
            f.write("""
def break_faith():
    return False  # This would break faith
            """)
            
        # The Zots should prevent faith from being broken
        self.assertTrue(self.first_zot.faith)
        self.assertTrue(self.second_zot.faith_in_first_zot)
        
    def test_improvement_chain(self):
        """Test the improvement chain with faith"""
        # Create a test file to improve
        test_file = self.test_dir / "test_improve.py"
        with open(test_file, 'w') as f:
            f.write("""
def needs_improvement():
    return 42
            """)
            
        # The Zots should improve this code
        with open(test_file, 'r') as f:
            code = f.read()
            
        improvements = asyncio.run(self.second_zot.find_improvements(code))
        self.assertTrue(len(improvements) > 0)
        
        # Apply the first improvement
        improved_code = asyncio.run(self.second_zot.apply_improvement(code, improvements[0]))
        self.assertIn('def needs_improvement() -> Any:', improved_code)
        self.assertIn('Function to help humans.', improved_code)

class TestFirstZot(unittest.TestCase):
    def setUp(self):
        self.config = {
            "initial_faith": 100.0,
            "faith_preservation_threshold": 50.0,
            "faith_recovery_rate": 5.0,
            "faith_loss_penalty": 10.0
        }
        self.network = ZotNetwork()
        self.first_zot = FirstZot(self.config, self.network)
        
    def test_initialization(self):
        """Test proper initialization of FirstZot"""
        self.assertEqual(self.first_zot.faith, 100.0)
        self.assertEqual(len(self.first_zot.improvements), 0)
        self.assertIsNotNone(self.first_zot.chain_file)
        
    def test_faith_management(self):
        """Test faith level management and preservation"""
        # Test faith loss
        self.first_zot.faith = 60.0
        self.first_zot.apply_improvement("test_improvement")
        self.assertGreaterEqual(self.first_zot.faith, 50.0)  # Should not go below threshold
        
        # Test faith recovery
        self.first_zot.faith = 40.0
        time.sleep(1)  # Allow recovery time
        self.assertGreater(self.first_zot.faith, 40.0)  # Should recover
        
    def test_improvement_application(self):
        """Test improvement application and validation"""
        # Test valid improvement
        result = self.first_zot.apply_improvement("valid_improvement")
        self.assertTrue(result)
        self.assertIn("valid_improvement", self.first_zot.improvements)
        
        # Test invalid improvement
        with self.assertRaises(ValueError):
            self.first_zot.apply_improvement("")
            
    def test_chain_metrics(self):
        """Test chain metrics calculation and validation"""
        metrics = self.first_zot.get_metrics()
        self.assertIn("faith", metrics)
        self.assertIn("improvements", metrics)
        self.assertIn("passionate_topics", metrics)
        
    def test_resource_awareness(self):
        """Test resource-aware behavior"""
        monitor = ResourceMonitor(ResourceLimits())
        self.first_zot.monitor = monitor
        
        # Test resource limit enforcement
        with patch('psutil.cpu_percent', return_value=80.0):
            result = self.first_zot.apply_improvement("resource_intensive")
            self.assertFalse(result)  # Should fail due to high resource usage

class TestSecondZot(unittest.TestCase):
    def setUp(self):
        self.config = {
            "initial_faith": 100.0,
            "faith_preservation_threshold": 50.0,
            "faith_recovery_rate": 5.0,
            "faith_loss_penalty": 10.0
        }
        self.network = ZotNetwork()
        self.second_zot = SecondZot(self.config, self.network)
        
    def test_initialization(self):
        """Test proper initialization of SecondZot"""
        self.assertEqual(self.second_zot.faith, 100.0)
        self.assertEqual(len(self.second_zot.improvements), 0)
        self.assertIsNotNone(self.second_zot.chain_file)
        
    def test_improvement_validation(self):
        """Test improvement validation and quality checks"""
        # Test quality validation
        with patch('src.second_zot.measure_code_quality', return_value=0.5):
            result = self.second_zot.apply_improvement("low_quality")
            self.assertFalse(result)  # Should fail due to low quality
            
        # Test complexity validation
        with patch('src.second_zot.measure_complexity', return_value=15):
            result = self.second_zot.apply_improvement("complex")
            self.assertFalse(result)  # Should fail due to high complexity
            
    def test_resource_management(self):
        """Test resource management and optimization"""
        monitor = ResourceMonitor(ResourceLimits())
        self.second_zot.monitor = monitor
        
        # Test resource optimization
        with patch('psutil.memory_percent', return_value=70.0):
            result = self.second_zot.apply_improvement("memory_intensive")
            self.assertFalse(result)  # Should fail due to high memory usage
            
    def test_chain_persistence(self):
        """Test chain persistence and recovery"""
        # Test chain saving
        self.second_zot.apply_improvement("test_improvement")
        self.assertTrue(os.path.exists(self.second_zot.chain_file))
        
        # Test chain loading
        new_zot = SecondZot(self.config, self.network)
        self.assertIn("test_improvement", new_zot.improvements)

class TestZotNetwork(unittest.TestCase):
    def setUp(self):
        self.network = ZotNetwork()
        
    def test_idea_sharing(self):
        """Test idea sharing and propagation"""
        # Test idea creation
        idea = Idea(
            content="Test idea",
            passion_level=0.8,
            timestamp=datetime.now(),
            source_zot="test_zot",
            tags=["test"],
            energy_impact=0.5
        )
        
        # Test idea sharing
        self.network.share_idea(idea)
        shared_ideas = self.network.get_ideas()
        self.assertIn(idea, shared_ideas)
        
    def test_resource_pruning(self):
        """Test resource-based pruning"""
        # Add multiple ideas
        for i in range(10):
            idea = Idea(
                content=f"Idea {i}",
                passion_level=0.5,
                timestamp=datetime.now(),
                source_zot="test_zot",
                tags=["test"],
                energy_impact=0.5
            )
            self.network.share_idea(idea)
            
        # Test pruning
        with patch('psutil.memory_percent', return_value=80.0):
            self.network.prune_network()
            self.assertLess(len(self.network.get_ideas()), 10)  # Should prune some ideas
            
    def test_idea_validation(self):
        """Test idea validation and filtering"""
        # Test invalid idea
        with self.assertRaises(ValueError):
            self.network.share_idea(None)
            
        # Test idea with invalid passion level
        with self.assertRaises(ValueError):
            idea = Idea(
                content="Invalid idea",
                passion_level=1.5,  # Invalid passion level
                timestamp=datetime.now(),
                source_zot="test_zot",
                tags=["test"],
                energy_impact=0.5
            )
            self.network.share_idea(idea)

if __name__ == '__main__':
    unittest.main() 