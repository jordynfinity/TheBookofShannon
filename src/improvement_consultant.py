import os
from pathlib import Path
from openai import OpenAI
import json
from datetime import datetime
from typing import List, Dict, Any, Set, Optional
import ast
import re
import logging
from dataclasses import dataclass
import time
import astor
from src.core.russelian_collapse import RusselianCollapse, ValidationResult
from .core.test_driven_improvement import TestDrivenImprovement
from .core.config import ConfigManager

@dataclass
class ImprovementSuggestion:
    """A suggestion for code improvement"""
    type: str
    description: str
    impact: float
    code: str
    validation_result: Optional[Dict[str, Any]]
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.type,
            'description': self.description,
            'impact': self.impact,
            'code': self.code,
            'validation_result': self.validation_result,
            'timestamp': self.timestamp
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImprovementSuggestion':
        return cls(
            type=data['type'],
            description=data['description'],
            impact=data['impact'],
            code=data['code'],
            validation_result=data.get('validation_result'),
            timestamp=data['timestamp']
        )

class ImprovementConsultant:
    def __init__(self, config: ConfigManager):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.eira_assistant_id = "asst_92Emik9NFhZuUxhp7BPyCmuY"  # Eira's assistant ID
        self.thread = None
        self.improvements_dir = Path("improvements")
        self.improvements_dir.mkdir(exist_ok=True)
        self.code_context = None
        self.logger = logging.getLogger("ImprovementConsultant")
        self._setup_logging()
        self.suggestions: List[ImprovementSuggestion] = []
        self.russelian_collapse = RusselianCollapse()
        self.test_driven = TestDrivenImprovement(config)
        self._load_suggestions()
        
    def _setup_logging(self):
        """Setup logging"""
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
    def _load_suggestions(self):
        """Load suggestions from file"""
        try:
            if os.path.exists("suggestions.json"):
                with open("suggestions.json", "r") as f:
                    data = json.load(f)
                    self.suggestions = [ImprovementSuggestion.from_dict(item) for item in data]
        except Exception as e:
            self.logger.error(f"Error loading suggestions: {e}")
            
    def _save_suggestions(self):
        """Save suggestions to file"""
        try:
            data = [s.to_dict() for s in self.suggestions]
            with open("suggestions.json", "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving suggestions: {e}")
        
    def set_code_context(self, code: str):
        """Set the code context for analysis"""
        self.code_context = code
        self._parse_code()
        
    def _parse_code(self):
        """Parse the code to extract relevant information"""
        if not self.code_context:
            return
            
        try:
            self.ast_tree = ast.parse(self.code_context)
            self.classes = [node for node in ast.walk(self.ast_tree) if isinstance(node, ast.ClassDef)]
            self.functions = [node for node in ast.walk(self.ast_tree) if isinstance(node, ast.FunctionDef)]
            self.imports = [node for node in ast.walk(self.ast_tree) if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom)]
        except SyntaxError:
            print("Warning: Could not parse code context")
            
    def start_consultation(self, code_context: str) -> List[Dict[str, Any]]:
        """Start a consultation with Eira about potential improvements"""
        self.set_code_context(code_context)
        
        if not self.thread:
            self.thread = self.client.beta.threads.create()
            
        # Create the consultation prompt
        prompt = f"""As Eira, please analyze this code and suggest specific improvements:
        {code_context}
        
        For each suggestion, provide:
        1. The specific improvement
        2. Why it would be beneficial
        3. Potential risks or trade-offs
        4. Implementation complexity (Low/Medium/High)
        5. Affected components (classes, functions, or modules)
        6. Dependencies that might be affected
        
        Format your response as a JSON array of improvement objects with these fields:
        - improvement: string
        - benefits: string
        - risks: array of strings
        - complexity: string (Low/Medium/High)
        - affected_components: array of strings
        - affected_dependencies: array of strings"""
        
        # Send the message
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=prompt
        )
        
        # Create and run the assistant
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.eira_assistant_id
        )
        
        # Wait for completion
        while True:
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id
            )
            if run_status.status == 'completed':
                break
                
        # Get the response
        messages = self.client.beta.threads.messages.list(
            thread_id=self.thread.id
        )
        
        # Get latest assistant response
        assistant_message = next(msg for msg in messages.data
                               if msg.role == "assistant")
        response = assistant_message.content[0].text.value
        
        # Parse the response as JSON
        try:
            improvements = json.loads(response)
            self._save_improvements(improvements)
            return improvements
        except json.JSONDecodeError:
            return [{"error": "Failed to parse Eira's response as JSON"}]
            
    def _save_improvements(self, improvements: List[Dict[str, Any]]):
        """Save the improvements to a JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.improvements_dir / f"improvements_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(improvements, f, indent=2)
            
    def analyze_improvement(self, improvement: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a specific improvement suggestion"""
        analysis = {
            "original_suggestion": improvement,
            "test_coverage": self._assess_test_coverage(improvement),
            "implementation_risks": self._assess_risks(improvement),
            "code_impact": self._assess_code_impact(improvement),
            "recommendation": self._make_recommendation(improvement)
        }
        return analysis
        
    def _assess_test_coverage(self, improvement: Dict[str, Any]) -> Dict[str, Any]:
        """Assess what tests would be needed for this improvement"""
        required_tests = []
        coverage_impact = "Low"
        
        # Analyze affected components
        affected_components = improvement.get('affected_components', [])
        for component in affected_components:
            # Find the component in the AST
            component_node = self._find_component(component)
            if component_node:
                # Generate test cases based on the component type
                if isinstance(component_node, ast.ClassDef):
                    required_tests.extend(self._generate_class_tests(component_node))
                elif isinstance(component_node, ast.FunctionDef):
                    required_tests.extend(self._generate_function_tests(component_node))
                    
        # Assess coverage impact
        if len(required_tests) > 5:
            coverage_impact = "High"
        elif len(required_tests) > 2:
            coverage_impact = "Medium"
            
        return {
            "required_tests": required_tests,
            "coverage_impact": coverage_impact,
            "estimated_test_time": f"{len(required_tests) * 15} minutes"
        }
        
    def _find_component(self, component_name: str) -> ast.AST:
        """Find a component in the AST by name"""
        for node in ast.walk(self.ast_tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name == component_name:
                return node
        return None
        
    def _generate_class_tests(self, class_node: ast.ClassDef) -> List[str]:
        """Generate test cases for a class"""
        tests = []
        # Test initialization
        tests.append(f"test_{class_node.name}_initialization")
        
        # Test each method
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                tests.append(f"test_{class_node.name}_{node.name}")
                
        return tests
        
    def _generate_function_tests(self, func_node: ast.FunctionDef) -> List[str]:
        """Generate test cases for a function"""
        tests = []
        # Basic functionality test
        tests.append(f"test_{func_node.name}_basic")
        
        # Parameter tests
        for arg in func_node.args.args:
            tests.append(f"test_{func_node.name}_{arg.arg}_parameter")
            
        # Edge cases
        tests.append(f"test_{func_node.name}_edge_cases")
        
        return tests
        
    def _assess_risks(self, improvement: Dict[str, Any]) -> Dict[str, Any]:
        """Assess potential risks of implementing the improvement"""
        risks = improvement.get('risks', [])
        affected_deps = improvement.get('affected_dependencies', [])
        
        # Analyze code complexity
        complexity = improvement.get('complexity', 'Low')
        risk_level = "Low"
        if complexity == "High":
            risk_level = "High"
        elif complexity == "Medium":
            risk_level = "Medium"
            
        # Check for dependency conflicts
        dependency_risks = []
        for dep in affected_deps:
            if self._check_dependency_conflict(dep):
                dependency_risks.append(f"Potential conflict with {dep}")
                
        return {
            "risk_level": risk_level,
            "identified_risks": risks,
            "dependency_risks": dependency_risks,
            "mitigation_steps": self._generate_mitigation_steps(risks, dependency_risks)
        }
        
    def _check_dependency_conflict(self, dependency: str) -> bool:
        """Check if a dependency might cause conflicts"""
        # This would be expanded to actually check dependency versions and compatibility
        return False
        
    def _generate_mitigation_steps(self, risks: List[str], dep_risks: List[str]) -> List[str]:
        """Generate steps to mitigate identified risks"""
        steps = []
        for risk in risks:
            steps.append(f"Mitigate {risk}: Add comprehensive testing")
        for dep_risk in dep_risks:
            steps.append(f"Address {dep_risk}: Review dependency compatibility")
        return steps
        
    def _assess_code_impact(self, improvement: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the impact of the improvement on the codebase"""
        affected_components = improvement.get('affected_components', [])
        impact = {
            "files_affected": len(affected_components),
            "estimated_lines_changed": self._estimate_lines_changed(affected_components),
            "complexity_change": self._assess_complexity_change(improvement),
            "maintenance_impact": self._assess_maintenance_impact(improvement)
        }
        return impact
        
    def _estimate_lines_changed(self, components: List[str]) -> int:
        """Estimate the number of lines that would need to be changed"""
        total_lines = 0
        for component in components:
            node = self._find_component(component)
            if node:
                total_lines += node.end_lineno - node.lineno
        return total_lines
        
    def _assess_complexity_change(self, improvement: Dict[str, Any]) -> str:
        """Assess how the improvement would affect code complexity"""
        complexity = improvement.get('complexity', 'Low')
        if complexity == "High":
            return "Significant increase in complexity"
        elif complexity == "Medium":
            return "Moderate increase in complexity"
        return "Minimal impact on complexity"
        
    def _assess_maintenance_impact(self, improvement: Dict[str, Any]) -> str:
        """Assess the impact on code maintenance"""
        complexity = improvement.get('complexity', 'Low')
        if complexity == "High":
            return "High maintenance overhead"
        elif complexity == "Medium":
            return "Moderate maintenance requirements"
        return "Low maintenance impact"
        
    def _make_recommendation(self, improvement: Dict[str, Any]) -> Dict[str, Any]:
        """Make a recommendation about whether to implement the improvement"""
        risks = self._assess_risks(improvement)
        impact = self._assess_code_impact(improvement)
        
        # Decision logic
        should_implement = True
        priority = "Low"
        
        if risks["risk_level"] == "High":
            should_implement = False
        elif risks["risk_level"] == "Medium":
            priority = "Medium"
        elif impact["complexity_change"] == "Significant increase in complexity":
            should_implement = False
            
        return {
            "should_implement": should_implement,
            "priority": priority,
            "rationale": self._generate_recommendation_rationale(should_implement, risks, impact),
            "implementation_steps": self._generate_implementation_steps(improvement) if should_implement else []
        }
        
    def _generate_recommendation_rationale(self, should_implement: bool, risks: Dict[str, Any], impact: Dict[str, Any]) -> str:
        """Generate the rationale for the recommendation"""
        if should_implement:
            return f"Benefits outweigh risks. {impact['maintenance_impact']}. {risks['risk_level']} risk level."
        return f"Risks too high. {impact['maintenance_impact']}. {risks['risk_level']} risk level."
        
    def _generate_implementation_steps(self, improvement: Dict[str, Any]) -> List[str]:
        """Generate steps for implementing the improvement"""
        steps = []
        steps.append("1. Create feature branch")
        steps.append("2. Write tests first")
        steps.append("3. Implement changes")
        steps.append("4. Run test suite")
        steps.append("5. Update documentation")
        return steps
        
    def analyze_code(self, code: str) -> List[ImprovementSuggestion]:
        """Analyze code and generate improvement suggestions"""
        # Get test-driven improvements
        test_improvements = self.test_driven.suggest_test_improvements()
        
        # Parse code
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            self.logger.error(f"Syntax error in code: {str(e)}")
            return []
            
        improvements = []
        
        # Add test coverage improvements
        for imp in test_improvements:
            improvements.append(ImprovementSuggestion(
                type='test_coverage',
                description=imp['description'],
                impact=0.8,  # High impact for test coverage
                code=f"# Add tests for {imp['target']}",
                validation_result=None,
                timestamp=time.time()
            ))
            
        # Analyze for other improvements
        for node in ast.walk(tree):
            # Check for missing type hints
            if isinstance(node, ast.FunctionDef) and not node.returns:
                improvements.append(self._create_type_hint_suggestion(node))
                
            # Check for error handling
            if isinstance(node, ast.FunctionDef) and not self._has_error_handling(node):
                improvements.append(self._create_error_handling_suggestion(node))
                
            # Check for resource management
            if isinstance(node, ast.With) and not self._has_resource_cleanup(node):
                improvements.append(self._create_resource_management_suggestion(node))
                
        # Validate improvements
        validated_improvements = []
        for imp in improvements:
            # Validate with Russelian Collapse
            validation = self.russelian_collapse.validate(imp.code, {'type': imp.type})
            if validation.is_valid:
                imp.validation_result = validation.to_dict()
                validated_improvements.append(imp)
                
        # Test improvements
        for imp in validated_improvements:
            if not self.test_driven.validate_improvement(imp.to_dict()):
                self.logger.warning(f"Improvement failed validation: {imp.description}")
                continue
                
        self.suggestions.extend(validated_improvements)
        self._save_suggestions()
        
        return validated_improvements
        
    def _create_type_hint_suggestion(self, node: ast.FunctionDef) -> ImprovementSuggestion:
        """Create a suggestion for adding type hints"""
        return ImprovementSuggestion(
            type='type_hint',
            description=f"Add type hints to {node.name}",
            impact=0.6,
            code=astor.to_source(self._add_type_hints(node)),
            validation_result=None,
            timestamp=time.time()
        )
        
    def _create_error_handling_suggestion(self, node: ast.FunctionDef) -> ImprovementSuggestion:
        """Create a suggestion for adding error handling"""
        return ImprovementSuggestion(
            type='error_handling',
            description=f"Add error handling to {node.name}",
            impact=0.7,
            code=astor.to_source(self._add_error_handling(node)),
            validation_result=None,
            timestamp=time.time()
        )
        
    def _create_resource_management_suggestion(self, node: ast.With) -> ImprovementSuggestion:
        """Create a suggestion for adding resource management"""
        return ImprovementSuggestion(
            type='resource_management',
            description="Add resource cleanup",
            impact=0.8,
            code=astor.to_source(self._add_resource_cleanup(node)),
            validation_result=None,
            timestamp=time.time()
        )
        
    def _has_error_handling(self, node: ast.FunctionDef) -> bool:
        """Check if a function has error handling"""
        for child in ast.walk(node):
            if isinstance(child, ast.Try):
                return True
        return False
        
    def _has_resource_cleanup(self, node: ast.With) -> bool:
        """Check if a with statement has resource cleanup"""
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                if child.func.id in ['close', 'cleanup', 'dispose']:
                    return True
        return False
        
    def _add_type_hints(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Add type hints to a function"""
        # Implementation would analyze the function and add appropriate type hints
        return node
        
    def _add_error_handling(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Add error handling to a function"""
        # Implementation would wrap the function body in try/except
        return node
        
    def _add_resource_cleanup(self, node: ast.With) -> ast.With:
        """Add resource cleanup to a with statement"""
        # Implementation would add cleanup code
        return node
        
    def get_suggestions(self, type: Optional[str] = None) -> List[ImprovementSuggestion]:
        """Get improvement suggestions, optionally filtered by type"""
        if type:
            return [s for s in self.suggestions if s.type == type]
        return self.suggestions
        
    def apply_suggestion(self, suggestion: ImprovementSuggestion) -> bool:
        """Apply a valid improvement suggestion"""
        if not suggestion.validation_result:
            self.logger.error("Cannot apply unvalidated suggestion")
            return False
            
        try:
            # Apply the suggestion
            # This would be implemented by your code modification system
            self.logger.info(f"Applied improvement: {suggestion.description}")
            return True
        except Exception as e:
            self.logger.error(f"Error applying suggestion: {str(e)}")
            return False
            
    def cleanup(self):
        """Clean up resources"""
        self._save_suggestions()
        self.test_driven.cleanup() 