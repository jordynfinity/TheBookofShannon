import unittest
from unittest.mock import patch, MagicMock
import os
from pathlib import Path
import json
from datetime import datetime

from src.improvement_consultant import ImprovementConsultant

class TestImprovementConsultant(unittest.TestCase):
    def setUp(self):
        self.consultant = ImprovementConsultant()
        self.sample_code = """
class TestClass:
    def __init__(self):
        self.value = 0
        
    def test_method(self, param):
        return param + self.value
        """
        self.consultant.set_code_context(self.sample_code)
        
    def test_init(self):
        """Test initialization of ImprovementConsultant"""
        self.assertIsNotNone(self.consultant)
        self.assertTrue(Path("improvements").exists())
        
    def test_parse_code(self):
        """Test code parsing functionality"""
        self.assertIsNotNone(self.consultant.ast_tree)
        self.assertEqual(len(self.consultant.classes), 1)
        self.assertEqual(len(self.consultant.functions), 2)  # __init__ and test_method
        
    def test_find_component(self):
        """Test finding components in the AST"""
        class_node = self.consultant._find_component("TestClass")
        self.assertIsNotNone(class_node)
        self.assertEqual(class_node.name, "TestClass")
        
        method_node = self.consultant._find_component("test_method")
        self.assertIsNotNone(method_node)
        self.assertEqual(method_node.name, "test_method")
        
    def test_generate_class_tests(self):
        """Test generation of class test cases"""
        class_node = self.consultant._find_component("TestClass")
        tests = self.consultant._generate_class_tests(class_node)
        
        self.assertIn("test_TestClass_initialization", tests)
        self.assertIn("test_TestClass_test_method", tests)
        
    def test_generate_function_tests(self):
        """Test generation of function test cases"""
        method_node = self.consultant._find_component("test_method")
        tests = self.consultant._generate_function_tests(method_node)
        
        self.assertIn("test_test_method_basic", tests)
        self.assertIn("test_test_method_param_parameter", tests)
        self.assertIn("test_test_method_edge_cases", tests)
        
    def test_assess_risks(self):
        """Test risk assessment functionality"""
        improvement = {
            "complexity": "Medium",
            "risks": ["Risk 1", "Risk 2"],
            "affected_dependencies": ["dep1", "dep2"]
        }
        
        risks = self.consultant._assess_risks(improvement)
        
        self.assertEqual(risks["risk_level"], "Medium")
        self.assertEqual(len(risks["identified_risks"]), 2)
        self.assertEqual(len(risks["mitigation_steps"]), 2)
        
    def test_assess_code_impact(self):
        """Test code impact assessment"""
        improvement = {
            "complexity": "High",
            "affected_components": ["TestClass", "test_method"]
        }
        
        impact = self.consultant._assess_code_impact(improvement)
        
        self.assertEqual(impact["files_affected"], 2)
        self.assertGreater(impact["estimated_lines_changed"], 0)
        self.assertEqual(impact["complexity_change"], "Significant increase in complexity")
        
    def test_make_recommendation(self):
        """Test recommendation generation"""
        improvement = {
            "complexity": "Low",
            "risks": ["Minor risk"],
            "affected_components": ["TestClass"]
        }
        
        recommendation = self.consultant._make_recommendation(improvement)
        
        self.assertTrue(recommendation["should_implement"])
        self.assertEqual(recommendation["priority"], "Low")
        self.assertIsNotNone(recommendation["rationale"])
        self.assertEqual(len(recommendation["implementation_steps"]), 5)
        
    @patch('openai.OpenAI')
    def test_start_consultation(self, mock_openai):
        """Test consultation with Eira"""
        # Mock the OpenAI responses
        mock_thread = MagicMock()
        mock_thread.id = "test_thread_id"
        mock_openai.return_value.beta.threads.create.return_value = mock_thread
        
        mock_run = MagicMock()
        mock_run.id = "test_run_id"
        mock_openai.return_value.beta.threads.runs.create.return_value = mock_run
        
        mock_run_status = MagicMock()
        mock_run_status.status = "completed"
        mock_openai.return_value.beta.threads.runs.retrieve.return_value = mock_run_status
        
        mock_message = MagicMock()
        mock_message.role = "assistant"
        mock_message.content = [MagicMock(text=MagicMock(value=json.dumps([{
            "improvement": "Test improvement",
            "benefits": "Test benefits",
            "risks": ["Test risk"],
            "complexity": "Low",
            "affected_components": ["TestClass"],
            "affected_dependencies": []
        }])))]
        mock_openai.return_value.beta.threads.messages.list.return_value.data = [mock_message]
        
        improvements = self.consultant.start_consultation(self.sample_code)
        
        self.assertEqual(len(improvements), 1)
        self.assertEqual(improvements[0]["improvement"], "Test improvement")
        
    def test_save_improvements(self):
        """Test saving improvements to file"""
        improvements = [{
            "improvement": "Test improvement",
            "benefits": "Test benefits"
        }]
        
        self.consultant._save_improvements(improvements)
        
        # Check that a file was created
        files = list(Path("improvements").glob("improvements_*.json"))
        self.assertGreater(len(files), 0)
        
        # Verify the content
        with open(files[-1], 'r') as f:
            saved_improvements = json.load(f)
            self.assertEqual(len(saved_improvements), 1)
            self.assertEqual(saved_improvements[0]["improvement"], "Test improvement")

if __name__ == '__main__':
    unittest.main() 