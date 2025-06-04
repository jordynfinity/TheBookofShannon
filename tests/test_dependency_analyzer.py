import unittest
from pathlib import Path
import tempfile
import shutil
import ast
from src.core.dependency_analyzer import DependencyAnalyzer, ModuleInfo

class TestDependencyAnalyzer(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.analyzer = DependencyAnalyzer(root_dir=self.test_dir)
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
        
    def _create_test_file(self, filename: str, content: str) -> Path:
        """Create a test Python file with given content"""
        file_path = Path(self.test_dir) / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)
        return file_path
        
    def test_analyze_simple_file(self):
        """Test analyzing a simple Python file"""
        content = """
import os
from pathlib import Path
from typing import List, Dict

class TestClass:
    def test_method(self):
        pass
"""
        self._create_test_file("test_module.py", content)
        self.assertTrue(self.analyzer.analyze_codebase())
        
        module_info = self.analyzer.get_module_info("test_module")
        self.assertIsNotNone(module_info)
        self.assertEqual(module_info.name, "test_module")
        self.assertEqual(module_info.classes, {"TestClass"})
        self.assertEqual(module_info.functions, {"test_method"})
        self.assertEqual(module_info.imports, {"os", "pathlib", "typing"})
        
    def test_detect_circular_dependency(self):
        """Test detection of circular dependencies"""
        # Create two modules that import each other
        module_a = """
from module_b import ClassB

class ClassA:
    def __init__(self):
        self.b = ClassB()
"""
        module_b = """
from module_a import ClassA

class ClassB:
    def __init__(self):
        self.a = ClassA()
"""
        self._create_test_file("module_a.py", module_a)
        self._create_test_file("module_b.py", module_b)
        
        # Analysis should fail due to circular dependency
        self.assertFalse(self.analyzer.analyze_codebase())
        
    def test_validate_import(self):
        """Test import validation"""
        # Create a simple module
        self._create_test_file("module_a.py", "class A: pass")
        self._create_test_file("module_b.py", "class B: pass")
        
        self.assertTrue(self.analyzer.analyze_codebase())
        self.assertTrue(self.analyzer.validate_import("module_a", "module_b"))
        
        # Create circular dependency
        self._create_test_file("module_c.py", "from module_d import D")
        self._create_test_file("module_d.py", "from module_c import C")
        
        self.assertFalse(self.analyzer.analyze_codebase())
        self.assertFalse(self.analyzer.validate_import("module_c", "module_d"))
        
    def test_get_dependency_path(self):
        """Test getting dependency paths"""
        # Create a chain of dependencies
        self._create_test_file("a.py", "from b import B")
        self._create_test_file("b.py", "from c import C")
        self._create_test_file("c.py", "class C: pass")
        
        self.assertTrue(self.analyzer.analyze_codebase())
        path = self.analyzer.get_dependency_path("a", "c")
        self.assertEqual(path, ["a", "b", "c"])
        
    def test_get_module_dependencies(self):
        """Test getting module dependencies"""
        content = """
from pathlib import Path
import os
from typing import List
from .local_module import LocalClass
"""
        self._create_test_file("test_module.py", content)
        self._create_test_file("local_module.py", "class LocalClass: pass")
        
        self.assertTrue(self.analyzer.analyze_codebase())
        deps = self.analyzer.get_module_dependencies("test_module")
        self.assertEqual(deps, {"pathlib", "os", "typing", "local_module"})
        
    def test_get_reverse_dependencies(self):
        """Test getting reverse dependencies"""
        self._create_test_file("base.py", "class Base: pass")
        self._create_test_file("derived.py", "from base import Base")
        
        self.assertTrue(self.analyzer.analyze_codebase())
        rev_deps = self.analyzer.get_reverse_dependencies("base")
        self.assertEqual(rev_deps, {"derived"})
        
    def test_analyze_complex_file(self):
        """Test analyzing a complex Python file with nested structures"""
        content = """
import os
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class ComplexClass:
    name: str
    items: List[str]
    
    def process_items(self) -> Dict[str, int]:
        return {item: len(item) for item in self.items}
        
    class NestedClass:
        def __init__(self):
            self.value = 42
            
def complex_function(param: Optional[str] = None) -> List[str]:
    if param:
        return [param]
    return []
"""
        self._create_test_file("complex_module.py", content)
        self.assertTrue(self.analyzer.analyze_codebase())
        
        module_info = self.analyzer.get_module_info("complex_module")
        self.assertIsNotNone(module_info)
        self.assertEqual(module_info.classes, {"ComplexClass", "NestedClass"})
        self.assertEqual(module_info.functions, {"process_items", "__init__", "complex_function"})
        
    def test_parallel_analysis(self):
        """Test parallel analysis of multiple files"""
        # Create multiple files
        for i in range(10):
            content = f"""
from typing import List
class TestClass{i}:
    def test_method(self):
        return {i}
"""
            self._create_test_file(f"module_{i}.py", content)
            
        self.assertTrue(self.analyzer.analyze_codebase())
        self.assertEqual(len(self.analyzer.get_all_modules()), 10)
        
    def test_error_handling(self):
        """Test error handling in analysis"""
        # Create a file with syntax error
        self._create_test_file("error.py", "def broken_function()")
        
        # Analysis should handle the error gracefully
        self.assertFalse(self.analyzer.analyze_codebase())
        
    def test_dependency_tree(self):
        """Test getting complete dependency tree"""
        # Create a tree of dependencies
        self._create_test_file("root.py", "from child_a import A")
        self._create_test_file("child_a.py", "from grandchild import G")
        self._create_test_file("child_b.py", "from grandchild import G")
        self._create_test_file("grandchild.py", "class G: pass")
        
        self.assertTrue(self.analyzer.analyze_codebase())
        tree = self.analyzer.get_dependency_tree()
        
        self.assertIn("root", tree)
        self.assertIn("child_a", tree)
        self.assertIn("child_b", tree)
        self.assertIn("grandchild", tree)
        
        self.assertEqual(tree["root"], ["child_a"])
        self.assertEqual(tree["child_a"], ["grandchild"])
        self.assertEqual(tree["child_b"], ["grandchild"])
        self.assertEqual(tree["grandchild"], [])

if __name__ == '__main__':
    unittest.main() 