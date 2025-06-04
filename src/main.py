import os
import sys
from pathlib import Path
import json
from datetime import datetime
import subprocess
import shutil
from typing import List, Dict, Any

from improvement_consultant import ImprovementConsultant

class CodeImprover:
    def __init__(self):
        self.consultant = ImprovementConsultant()
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
    def backup_codebase(self):
        """Create a backup of the current codebase"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        # Copy all Python files
        for py_file in Path("src").rglob("*.py"):
            rel_path = py_file.relative_to(Path("src"))
            target_path = backup_path / rel_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(py_file, target_path)
            
        return backup_path
        
    def run_tests(self) -> bool:
        """Run the test suite and return success status"""
        try:
            result = subprocess.run(
                ["pytest", "--cov=src", "--cov-report=term-missing"],
                capture_output=True,
                text=True
            )
            print("\nTest Results:")
            print(result.stdout)
            return result.returncode == 0
        except Exception as e:
            print(f"Error running tests: {e}")
            return False
            
    def apply_improvement(self, improvement: Dict[str, Any]) -> bool:
        """Apply a specific improvement to the codebase"""
        try:
            # Create a new branch for the improvement
            branch_name = f"improvement_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            subprocess.run(["git", "checkout", "-b", branch_name], check=True)
            
            # Apply the changes
            # This would be expanded based on the specific improvement
            # For now, we'll just create a placeholder implementation
            
            # Run tests to verify the change
            if not self.run_tests():
                print("Tests failed after applying improvement. Rolling back...")
                subprocess.run(["git", "checkout", "main"], check=True)
                subprocess.run(["git", "branch", "-D", branch_name], check=True)
                return False
                
            # Commit the changes
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(
                ["git", "commit", "-m", f"Apply improvement: {improvement['improvement']}"],
                check=True
            )
            
            return True
            
        except Exception as e:
            print(f"Error applying improvement: {e}")
            return False
            
    def analyze_and_improve(self):
        """Main method to analyze and improve the codebase"""
        print("Starting codebase improvement process...")
        
        # Create backup
        backup_path = self.backup_codebase()
        print(f"Created backup at: {backup_path}")
        
        # Run initial tests
        print("\nRunning initial tests...")
        if not self.run_tests():
            print("Initial tests failed. Aborting improvement process.")
            return
            
        # Get code context
        code_context = self._get_code_context()
        
        # Get improvement suggestions
        print("\nConsulting with Eira about improvements...")
        improvements = self.consultant.start_consultation(code_context)
        
        # Analyze and apply improvements
        successful_improvements = []
        for improvement in improvements:
            print(f"\nAnalyzing improvement: {improvement['improvement']}")
            analysis = self.consultant.analyze_improvement(improvement)
            
            if analysis["recommendation"]["should_implement"]:
                print(f"Applying improvement: {improvement['improvement']}")
                if self.apply_improvement(improvement):
                    successful_improvements.append(improvement)
                    print("Improvement applied successfully!")
                else:
                    print("Failed to apply improvement.")
            else:
                print("Skipping improvement based on analysis.")
                
        # Generate final report
        self._generate_final_report(successful_improvements)
        
    def _get_code_context(self) -> str:
        """Get the current code context"""
        code_context = []
        for py_file in Path("src").rglob("*.py"):
            with open(py_file, 'r') as f:
                code_context.append(f"# File: {py_file.relative_to(Path('src'))}\n{f.read()}\n")
        return "\n".join(code_context)
        
    def _generate_final_report(self, improvements: List[Dict[str, Any]]):
        """Generate a final report of applied improvements"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = Path("reports") / f"improvement_report_{timestamp}.html"
        report_path.parent.mkdir(exist_ok=True)
        
        # Generate HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Code Improvement Report</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container py-5">
                <h1>Code Improvement Report</h1>
                <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                
                <h2>Applied Improvements</h2>
                <div class="row">
                    {self._generate_improvement_cards(improvements)}
                </div>
                
                <h2>Test Coverage</h2>
                <pre>{self._get_test_coverage()}</pre>
            </div>
        </body>
        </html>
        """
        
        with open(report_path, 'w') as f:
            f.write(html_content)
            
        print(f"\nImprovement report generated at: {report_path}")
        
    def _generate_improvement_cards(self, improvements: List[Dict[str, Any]]) -> str:
        """Generate HTML cards for each improvement"""
        cards = []
        for improvement in improvements:
            card = f"""
            <div class="col-md-6 mb-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">{improvement['improvement']}</h5>
                        <p class="card-text">{improvement['benefits']}</p>
                        <div class="mt-3">
                            <h6>Impact:</h6>
                            <ul>
                                <li>Complexity: {improvement['complexity']}</li>
                                <li>Components Affected: {', '.join(improvement['affected_components'])}</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            """
            cards.append(card)
        return "\n".join(cards)
        
    def _get_test_coverage(self) -> str:
        """Get the current test coverage report"""
        try:
            result = subprocess.run(
                ["pytest", "--cov=src", "--cov-report=term-missing"],
                capture_output=True,
                text=True
            )
            return result.stdout
        except Exception as e:
            return f"Error getting test coverage: {e}"

def main():
    improver = CodeImprover()
    improver.analyze_and_improve()

if __name__ == "__main__":
    main() 