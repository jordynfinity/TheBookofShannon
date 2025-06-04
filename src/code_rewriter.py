import ast
from pathlib import Path
import networkx as nx
from typing import Dict, Set, List, Tuple
import logging
import random
import subprocess
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor

class CodeRewriter:
    """Rewrites code to increase linkage density while maintaining test coverage"""
    
    def __init__(self, src_dir: str = "src", test_dir: str = "tests"):
        self.src_dir = Path(src_dir)
        self.test_dir = Path(test_dir)
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('code_rewriter.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def increase_linkage_density(self, iterations: int = 10) -> bool:
        """Attempt to increase code linkage density over multiple iterations"""
        for i in range(iterations):
            self.logger.info(f"Starting iteration {i+1}/{iterations}")
            
            # Get current state
            current_density = self._calculate_linkage_density()
            self.logger.info(f"Current linkage density: {current_density:.3f}")
            
            # Generate potential improvements
            improvements = self._generate_improvements()
            
            # Try each improvement
            for improvement in improvements:
                if self._apply_improvement(improvement):
                    new_density = self._calculate_linkage_density()
                    if new_density > current_density:
                        self.logger.info(f"Successfully increased density to {new_density:.3f}")
                        return True
                        
            self.logger.info("No improvements found in this iteration")
            
        return False
        
    def _calculate_linkage_density(self) -> float:
        """Calculate current code linkage density"""
        graph = self._build_dependency_graph()
        return nx.density(graph)
        
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
        
    def _generate_improvements(self) -> List[Tuple[str, ast.AST]]:
        """Generate potential code improvements"""
        improvements = []
        
        # Find potential interface extractions
        for file_path in self.src_dir.rglob("*.py"):
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Look for common method patterns
                    common_methods = self._find_common_methods(node)
                    if common_methods:
                        interface = self._create_interface(common_methods)
                        improvements.append((file_path, interface))
                        
        return improvements
        
    def _find_common_methods(self, node: ast.ClassDef) -> List[ast.FunctionDef]:
        """Find methods that could be extracted into an interface"""
        common_methods = []
        
        # Look for methods with similar signatures
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        for i, m1 in enumerate(methods):
            for m2 in methods[i+1:]:
                if self._methods_share_pattern(m1, m2):
                    common_methods.extend([m1, m2])
                    
        return list(set(common_methods))
        
    def _methods_share_pattern(self, m1: ast.FunctionDef, m2: ast.FunctionDef) -> bool:
        """Check if two methods share a common pattern"""
        # Check parameter count
        if len(m1.args.args) != len(m2.args.args):
            return False
            
        # Check return type hints
        if not (m1.returns and m2.returns):
            return False
            
        return True
        
    def _create_interface(self, methods: List[ast.FunctionDef]) -> ast.ClassDef:
        """Create an interface from common methods"""
        return ast.ClassDef(
            name=f"I{methods[0].name.capitalize()}",
            bases=[ast.Name(id='ABC', ctx=ast.Load())],
            keywords=[],
            body=[
                ast.FunctionDef(
                    name=m.name,
                    args=m.args,
                    body=[ast.Pass()],
                    decorator_list=[ast.Name(id='abstractmethod', ctx=ast.Load())],
                    returns=m.returns
                ) for m in methods
            ],
            decorator_list=[]
        )
        
    def _apply_improvement(self, improvement: Tuple[Path, ast.AST]) -> bool:
        """Apply a code improvement and verify it works"""
        file_path, new_node = improvement
        
        # Create temporary copy
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_src = Path(temp_dir) / "src"
            temp_test = Path(temp_dir) / "tests"
            shutil.copytree(self.src_dir, temp_src)
            shutil.copytree(self.test_dir, temp_test)
            
            # Apply improvement
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            # Add new node
            tree.body.append(new_node)
            
            # Write modified file
            with open(temp_src / file_path.relative_to(self.src_dir), 'w', encoding='utf-8') as f:
                f.write(ast.unparse(tree))
                
            # Run tests
            try:
                result = subprocess.run(
                    ['python', '-m', 'unittest', 'discover', str(temp_test)],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # If tests pass, apply the change
                if result.returncode == 0:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(ast.unparse(tree))
                    return True
                    
            except subprocess.CalledProcessError:
                self.logger.warning("Tests failed after applying improvement")
                
        return False
        
    def _run_tests(self) -> bool:
        """Run the test suite"""
        try:
            result = subprocess.run(
                ['python', '-m', 'unittest', 'discover', str(self.test_dir)],
                capture_output=True,
                text=True,
                check=True
            )
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False

if __name__ == '__main__':
    rewriter = CodeRewriter()
    if rewriter.increase_linkage_density():
        print("Successfully increased code linkage density")
    else:
        print("Failed to increase code linkage density") 