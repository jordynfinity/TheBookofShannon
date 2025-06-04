import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple
import networkx as nx
from dataclasses import dataclass
import logging
from concurrent.futures import ThreadPoolExecutor
import threading

@dataclass
class ModuleInfo:
    """Information about a Python module"""
    name: str
    path: Path
    imports: Set[str]
    classes: Set[str]
    functions: Set[str]
    dependencies: Set[str]

class DependencyAnalyzer:
    """Analyzes code dependencies using AST"""
    def __init__(self, root_dir: str = "src"):
        self.root_dir = Path(root_dir)
        self.modules: Dict[str, ModuleInfo] = {}
        self.graph = nx.DiGraph()
        self._setup_logging()
        self._lock = threading.Lock()
        
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('dependency_analyzer.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def analyze_codebase(self) -> bool:
        """Analyze the entire codebase for dependencies"""
        try:
            # Find all Python files
            python_files = list(self.root_dir.rglob("*.py"))
            
            # Analyze each file in parallel
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(self._analyze_file, file) for file in python_files]
                for future in futures:
                    module_info = future.result()
                    if module_info:
                        self.modules[module_info.name] = module_info
                        
            # Build dependency graph
            self._build_dependency_graph()
            
            # Check for circular dependencies
            cycles = list(nx.simple_cycles(self.graph))
            if cycles:
                self.logger.error(f"Circular dependencies detected: {cycles}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error analyzing codebase: {e}")
            return False
            
    def _analyze_file(self, file_path: Path) -> ModuleInfo:
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            # Extract module name
            module_name = file_path.relative_to(self.root_dir).stem
            
            # Initialize module info
            module_info = ModuleInfo(
                name=module_name,
                path=file_path,
                imports=set(),
                classes=set(),
                functions=set(),
                dependencies=set()
            )
            
            # Analyze AST
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        module_info.imports.add(name.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_info.imports.add(node.module)
                elif isinstance(node, ast.ClassDef):
                    module_info.classes.add(node.name)
                elif isinstance(node, ast.FunctionDef):
                    module_info.functions.add(node.name)
                    
            # Process imports to get dependencies
            for imp in module_info.imports:
                if imp.startswith('.'):
                    # Handle relative imports
                    rel_path = file_path.parent / imp.replace('.', '/')
                    if rel_path.exists():
                        module_info.dependencies.add(rel_path.stem)
                else:
                    # Handle absolute imports
                    module_info.dependencies.add(imp.split('.')[0])
                    
            return module_info
            
        except Exception as e:
            self.logger.error(f"Error analyzing file {file_path}: {e}")
            return None
            
    def _build_dependency_graph(self):
        """Build a directed graph of module dependencies"""
        self.graph.clear()
        
        # Add nodes
        for module_name in self.modules:
            self.graph.add_node(module_name)
            
        # Add edges
        for module_name, module_info in self.modules.items():
            for dep in module_info.dependencies:
                if dep in self.modules:
                    self.graph.add_edge(module_name, dep)
                    
    def get_dependency_path(self, source: str, target: str) -> List[str]:
        """Get the dependency path between two modules"""
        try:
            return nx.shortest_path(self.graph, source, target)
        except nx.NetworkXNoPath:
            return []
            
    def get_module_dependencies(self, module_name: str) -> Set[str]:
        """Get all dependencies for a module"""
        if module_name in self.modules:
            return self.modules[module_name].dependencies
        return set()
        
    def get_reverse_dependencies(self, module_name: str) -> Set[str]:
        """Get all modules that depend on the given module"""
        return set(self.graph.predecessors(module_name))
        
    def validate_import(self, source_module: str, target_module: str) -> bool:
        """Validate if an import is allowed (no circular dependency)"""
        try:
            # Add temporary edge
            self.graph.add_edge(source_module, target_module)
            
            # Check for cycles
            has_cycle = bool(list(nx.simple_cycles(self.graph)))
            
            # Remove temporary edge
            self.graph.remove_edge(source_module, target_module)
            
            return not has_cycle
            
        except Exception as e:
            self.logger.error(f"Error validating import: {e}")
            return False
            
    def get_module_info(self, module_name: str) -> ModuleInfo:
        """Get information about a specific module"""
        return self.modules.get(module_name)
        
    def get_all_modules(self) -> List[str]:
        """Get list of all modules"""
        return list(self.modules.keys())
        
    def get_dependency_tree(self) -> Dict[str, List[str]]:
        """Get the complete dependency tree"""
        return {node: list(self.graph.successors(node)) for node in self.graph.nodes()} 