import ast
import astor
from typing import Dict, Any, List, Optional
import re
from pathlib import Path

class ImprovementImplementer:
    def __init__(self):
        self.improvements = {
            "optimize_performance": self._optimize_performance,
            "improve_error_handling": self._improve_error_handling,
            "add_validation": self._add_validation,
            "optimize_memory": self._optimize_memory,
            "improve_security": self._improve_security,
            "add_caching": self._add_caching,
            "optimize_io": self._optimize_io,
            "improve_concurrency": self._improve_concurrency
        }
        
    def implement_improvement(self, code: str, improvement: Dict[str, Any]) -> Optional[str]:
        """Implement a specific improvement on the code"""
        improvement_type = self._identify_improvement_type(improvement)
        if improvement_type in self.improvements:
            return self.improvements[improvement_type](code, improvement)
        return None
        
    def _identify_improvement_type(self, improvement: Dict[str, Any]) -> str:
        """Identify the type of improvement from the suggestion"""
        suggestion = improvement["improvement"].lower()
        
        if any(word in suggestion for word in ["performance", "speed", "optimize"]):
            return "optimize_performance"
        elif any(word in suggestion for word in ["error", "exception", "handle", "robust"]):
            return "improve_error_handling"
        elif any(word in suggestion for word in ["validate", "validation", "check", "verify"]):
            return "add_validation"
        elif any(word in suggestion for word in ["memory", "leak", "garbage"]):
            return "optimize_memory"
        elif any(word in suggestion for word in ["security", "vulnerability", "injection"]):
            return "improve_security"
        elif any(word in suggestion for word in ["cache", "memoize"]):
            return "add_caching"
        elif any(word in suggestion for word in ["io", "file", "network"]):
            return "optimize_io"
        elif any(word in suggestion for word in ["concurrent", "parallel", "thread", "async"]):
            return "improve_concurrency"
            
        return "unknown"
        
    def _optimize_performance(self, code: str, improvement: Dict[str, Any]) -> str:
        """Optimize code performance"""
        tree = ast.parse(code)
        
        class PerformanceVisitor(ast.NodeTransformer):
            def visit_For(self, node):
                # Convert list comprehensions to generator expressions
                if isinstance(node.target, ast.Name) and isinstance(node.iter, ast.Call):
                    if isinstance(node.iter.func, ast.Name) and node.iter.func.id == "range":
                        return ast.Expr(value=ast.GeneratorExp(
                            elt=node.body[0].value,
                            generators=[
                                ast.comprehension(
                                    target=node.target,
                                    iter=node.iter,
                                    ifs=[]
                                )
                            ]
                        ))
                return node

            def visit_Call(self, node):
                # Optimize string operations
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == "join" and isinstance(node.func.value, ast.Str):
                        # Convert string join to f-string
                        return ast.JoinedStr(values=[node.func.value])
                return node

        visitor = PerformanceVisitor()
        modified_tree = visitor.visit(tree)
        return astor.to_source(modified_tree)
        
    def _improve_error_handling(self, code: str, improvement: Dict[str, Any]) -> str:
        """Add robust error handling"""
        tree = ast.parse(code)
        
        class ErrorHandlingVisitor(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                # Add context-specific error handling
                try_block = ast.Try(
                    body=node.body,
                    handlers=[
                        ast.ExceptHandler(
                            type=ast.Name(id="ValueError"),
                            name="e",
                            body=[
                                ast.Expr(value=ast.Call(
                                    func=ast.Name(id="print"),
                                    args=[ast.Str(s=f"Invalid value in {node.name}: ")],
                                    keywords=[]
                                )),
                                ast.Raise()
                            ]
                        ),
                        ast.ExceptHandler(
                            type=ast.Name(id="IOError"),
                            name="e",
                            body=[
                                ast.Expr(value=ast.Call(
                                    func=ast.Name(id="print"),
                                    args=[ast.Str(s=f"IO error in {node.name}: ")],
                                    keywords=[]
                                )),
                                ast.Raise()
                            ]
                        )
                    ],
                    orelse=[],
                    finalbody=[]
                )
                node.body = [try_block]
                return node
                
        visitor = ErrorHandlingVisitor()
        modified_tree = visitor.visit(tree)
        return astor.to_source(modified_tree)
        
    def _add_validation(self, code: str, improvement: Dict[str, Any]) -> str:
        """Add input validation"""
        tree = ast.parse(code)
        
        class ValidationVisitor(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                # Add parameter validation
                for arg in node.args.args:
                    validation = ast.If(
                        test=ast.Compare(
                            left=ast.Name(id=arg.arg),
                            ops=[ast.Is()],
                            comparators=[ast.Name(id="None")]
                        ),
                        body=[
                            ast.Raise(
                                exc=ast.Call(
                                    func=ast.Name(id="ValueError"),
                                    args=[ast.Str(s=f"Parameter {arg.arg} cannot be None")],
                                    keywords=[]
                                )
                            )
                        ],
                        orelse=[]
                    )
                    node.body.insert(0, validation)
                return node
                
        visitor = ValidationVisitor()
        modified_tree = visitor.visit(tree)
        return astor.to_source(modified_tree)
        
    def _optimize_memory(self, code: str, improvement: Dict[str, Any]) -> str:
        """Optimize memory usage"""
        tree = ast.parse(code)
        
        class MemoryVisitor(ast.NodeTransformer):
            def visit_For(self, node):
                # Convert list comprehensions to generator expressions
                if isinstance(node.target, ast.Name) and isinstance(node.iter, ast.Call):
                    if isinstance(node.iter.func, ast.Name) and node.iter.func.id == "range":
                        return ast.Expr(value=ast.GeneratorExp(
                            elt=node.body[0].value,
                            generators=[
                                ast.comprehension(
                                    target=node.target,
                                    iter=node.iter,
                                    ifs=[]
                                )
                            ]
                        ))
                return node

            def visit_Call(self, node):
                # Optimize string operations
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == "join" and isinstance(node.func.value, ast.Str):
                        return ast.JoinedStr(values=[node.func.value])
                return node

        visitor = MemoryVisitor()
        modified_tree = visitor.visit(tree)
        return astor.to_source(modified_tree)
        
    def _improve_security(self, code: str, improvement: Dict[str, Any]) -> str:
        """Improve code security"""
        tree = ast.parse(code)
        
        class SecurityVisitor(ast.NodeTransformer):
            def visit_Call(self, node):
                # Add input sanitization
                if isinstance(node.func, ast.Name):
                    if node.func.id in ["eval", "exec"]:
                        return ast.Call(
                            func=ast.Name(id="ast.literal_eval"),
                            args=node.args,
                            keywords=node.keywords
                        )
                return node

        visitor = SecurityVisitor()
        modified_tree = visitor.visit(tree)
        return astor.to_source(modified_tree)
        
    def _add_caching(self, code: str, improvement: Dict[str, Any]) -> str:
        """Add caching to expensive operations"""
        tree = ast.parse(code)
        
        class CachingVisitor(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                # Add caching decorator
                decorator = ast.Call(
                    func=ast.Name(id="functools.lru_cache"),
                    args=[],
                    keywords=[]
                )
                node.decorator_list.append(decorator)
                return node

        visitor = CachingVisitor()
        modified_tree = visitor.visit(tree)
        return astor.to_source(modified_tree)
        
    def _optimize_io(self, code: str, improvement: Dict[str, Any]) -> str:
        """Optimize I/O operations"""
        tree = ast.parse(code)
        
        class IOVisitor(ast.NodeTransformer):
            def visit_With(self, node):
                # Add buffering to file operations
                if isinstance(node.items[0].context_expr, ast.Call):
                    if isinstance(node.items[0].context_expr.func, ast.Name):
                        if node.items[0].context_expr.func.id == "open":
                            node.items[0].context_expr.keywords.append(
                                ast.keyword(arg="buffering", value=ast.Num(n=8192))
                            )
                return node

        visitor = IOVisitor()
        modified_tree = visitor.visit(tree)
        return astor.to_source(modified_tree)
        
    def _improve_concurrency(self, code: str, improvement: Dict[str, Any]) -> str:
        """Improve concurrency"""
        tree = ast.parse(code)
        
        class ConcurrencyVisitor(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                # Add async/await support
                if any(isinstance(child, ast.Call) for child in ast.walk(node)):
                    node.name = f"async_{node.name}"
                    node.body.insert(0, ast.Expr(value=ast.Call(
                        func=ast.Name(id="asyncio.sleep"),
                        args=[ast.Num(n=0)],
                        keywords=[]
                    )))
                return node

        visitor = ConcurrencyVisitor()
        modified_tree = visitor.visit(tree)
        return astor.to_source(modified_tree) 