import unittest
import ast
from pathlib import Path
import networkx as nx
from typing import Dict, Set, List
import logging

class TestLinkageDensity(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.src_dir = Path("src")
        self.logger = logging.getLogger(__name__)
        
    def test_code_linkage(self):
        """Test that code has sufficient linkage density"""
        # Build dependency graph
        graph = self._build_dependency_graph()
        
        # Calculate linkage density
        density = nx.density(graph)
        self.assertGreater(density, 0.3, "Code linkage density too low")
        
        # Check for isolated components
        components = list(nx.connected_components(graph.to_undirected()))
        self.assertEqual(len(components), 1, "Code has isolated components")
        
    def test_circular_dependencies(self):
        """Test for absence of circular dependencies"""
        graph = self._build_dependency_graph()
        cycles = list(nx.simple_cycles(graph))
        self.assertEqual(len(cycles), 0, f"Circular dependencies found: {cycles}")
        
    def test_interface_cohesion(self):
        """Test that interfaces are cohesive"""
        interfaces = self._find_interfaces()
        for interface in interfaces:
            cohesion = self._calculate_interface_cohesion(interface)
            self.assertGreater(cohesion, 0.7, f"Interface {interface} has low cohesion")
            
    def test_implementation_coupling(self):
        """Test that implementations are properly coupled"""
        implementations = self._find_implementations()
        for impl in implementations:
            coupling = self._calculate_implementation_coupling(impl)
            self.assertLess(coupling, 0.5, f"Implementation {impl} has high coupling")
            
    def test_abstract_method_coverage(self):
        """Test that abstract methods are properly implemented"""
        abstract_classes = self._find_abstract_classes()
        for cls in abstract_classes:
            coverage = self._calculate_abstract_method_coverage(cls)
            self.assertEqual(coverage, 1.0, f"Abstract class {cls} has incomplete implementation")
            
    def _build_dependency_graph(self) -> nx.DiGraph:
        """Build a directed graph of code dependencies"""
        graph = nx.DiGraph()
        
        for file_path in self.src_dir.rglob("*.py"):
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            # Add nodes for classes and functions
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                    graph.add_node(f"{file_path.stem}.{node.name}")
                    
            # Add edges for dependencies
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            graph.add_edge(f"{file_path.stem}.{node.name}", base.id)
                            
        return graph
        
    def _find_interfaces(self) -> Set[str]:
        """Find all interface classes in the codebase"""
        interfaces = set()
        
        for file_path in self.src_dir.rglob("*.py"):
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if any(isinstance(base, ast.Name) and base.id == 'ABC' for base in node.bases):
                        interfaces.add(f"{file_path.stem}.{node.name}")
                        
        return interfaces
        
    def _find_implementations(self) -> Set[str]:
        """Find all implementation classes in the codebase"""
        implementations = set()
        
        for file_path in self.src_dir.rglob("*.py"):
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if not any(isinstance(base, ast.Name) and base.id == 'ABC' for base in node.bases):
                        implementations.add(f"{file_path.stem}.{node.name}")
                        
        return implementations
        
    def _find_abstract_classes(self) -> Set[str]:
        """Find all abstract classes in the codebase"""
        abstract_classes = set()
        
        for file_path in self.src_dir.rglob("*.py"):
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if any(isinstance(base, ast.Name) and base.id == 'ABC' for base in node.bases):
                        abstract_classes.add(f"{file_path.stem}.{node.name}")
                        
        return abstract_classes
        
    def _calculate_interface_cohesion(self, interface: str) -> float:
        """Calculate the cohesion of an interface"""
        # Count methods that share common parameters or return types
        shared_params = 0
        total_params = 0
        
        for file_path in self.src_dir.rglob("*.py"):
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and f"{file_path.stem}.{node.name}" == interface:
                    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    for i, m1 in enumerate(methods):
                        for m2 in methods[i+1:]:
                            if self._methods_share_params(m1, m2):
                                shared_params += 1
                            total_params += 1
                            
        return shared_params / total_params if total_params > 0 else 1.0
        
    def _calculate_implementation_coupling(self, implementation: str) -> float:
        """Calculate the coupling of an implementation"""
        # Count external dependencies
        external_deps = 0
        total_deps = 0
        
        for file_path in self.src_dir.rglob("*.py"):
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and f"{file_path.stem}.{node.name}" == implementation:
                    for child in ast.walk(node):
                        if isinstance(child, ast.Name):
                            if child.id not in self._get_internal_names(node):
                                external_deps += 1
                            total_deps += 1
                            
        return external_deps / total_deps if total_deps > 0 else 0.0
        
    def _calculate_abstract_method_coverage(self, abstract_class: str) -> float:
        """Calculate the coverage of abstract methods"""
        abstract_methods = set()
        implemented_methods = set()
        
        for file_path in self.src_dir.rglob("*.py"):
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if f"{file_path.stem}.{node.name}" == abstract_class:
                        # Find abstract methods
                        for child in node.body:
                            if isinstance(child, ast.FunctionDef):
                                if any(isinstance(d, ast.Name) and d.id == 'abstractmethod' 
                                     for d in child.decorator_list):
                                    abstract_methods.add(child.name)
                    else:
                        # Check for implementations
                        for base in node.bases:
                            if isinstance(base, ast.Name) and base.id == abstract_class.split('.')[-1]:
                                for child in node.body:
                                    if isinstance(child, ast.FunctionDef):
                                        implemented_methods.add(child.name)
                                        
        return len(implemented_methods) / len(abstract_methods) if abstract_methods else 1.0
        
    def _methods_share_params(self, m1: ast.FunctionDef, m2: ast.FunctionDef) -> bool:
        """Check if two methods share common parameters"""
        params1 = {arg.arg for arg in m1.args.args}
        params2 = {arg.arg for arg in m2.args.args}
        return bool(params1 & params2)
        
    def _get_internal_names(self, node: ast.ClassDef) -> Set[str]:
        """Get all internal names defined in a class"""
        names = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                names.add(child.id)
        return names

if __name__ == '__main__':
    unittest.main() 