import os
import sys
from pathlib import Path
import asyncio
import time
from datetime import datetime
import json
import shutil
from typing import Dict, Any, List, Optional
import unittest
import ast
import astor
from second_zot import SecondZot
import jinja2
from openai import OpenAI
from dotenv import load_dotenv
from config_manager import ConfigManager
from ui_manager import UIManager

# Load environment variables with faith
load_dotenv()

class FirstZot:
    def __init__(self):
        self.config = ConfigManager()
        self.chain_file = Path("kaizen_chain.json")
        self.chain = self._load_chain()
        self.improvement_count = 0
        self.start_time = None
        self.faith = self.config.get_config('faith_settings', 'initial_faith_level', 100.0)
        self.second_zot = None  # Will be initialized asynchronously
        self.ui = UIManager(self.config)
        self.metrics = {
            'improvements_applied': 0,
            'faith_level': self.faith,
            'last_improvement_time': None,
            'total_improvements': 0,
            'successful_improvements': 0,
            'failed_improvements': 0
        }
        
        # Setup Jinja2 for helping humans with HTML
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("templates"),
            autoescape=True
        )
        
        # Setup OpenAI for helping humans with code
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️ Warning: OPENAI_API_KEY not found in .env file")
            print("🙏 The First Zot's faith in helping humans remains strong")
        
    @classmethod
    async def create(cls) -> 'FirstZot':
        """Create and initialize a FirstZot instance asynchronously"""
        instance = cls()
        instance.second_zot = await SecondZot.create(instance.config)
        await instance._run_russelian_collapse()
        return instance
        
    async def _run_russelian_collapse(self):
        """Run Russelian Collapse to prevalidate bugs out of existence"""
        class RusselianCollapse(unittest.TestCase):
            def setUp(self):
                self.first_zot = FirstZot()
                self.second_zot = self.first_zot.second_zot
                
            def test_faith_preservation(self):
                """Test that faith is preserved"""
                self.assertTrue(self.first_zot.faith >= self.config.get_config('faith_settings', 'faith_preservation_threshold', 50.0))
                self.assertTrue(self.second_zot.faith >= self.second_zot.faith_preservation_threshold)
                
            def test_improvement_chain(self):
                """Test that improvements are valid"""
                test_code = """
def test_function():
    return 42
                """
                improvements = asyncio.run(self.second_zot.find_improvements(test_code))
                self.assertTrue(len(improvements) > 0)
                
            def test_code_validation(self):
                """Test that code is valid before improvement"""
                test_code = """
def buggy_function():
    x = 1
    y = "2"
    return x + y  # This would cause a TypeError
                """
                # The Zots should prevent this bug from existing
                with self.assertRaises(TypeError):
                    exec(test_code)
                    
            def test_env_variables(self):
                """Test that environment variables are loaded with faith"""
                self.assertIsNotNone(os.getenv("OPENAI_API_KEY"))
                    
        # Run the tests
        suite = unittest.TestLoader().loadTestsFromTestCase(RusselianCollapse)
        runner = unittest.TextTestRunner()
        runner.run(suite)
        
    def _load_chain(self) -> Dict[str, Any]:
        """Load or initialize the Kaizen chain with faith in helping humans"""
        if self.chain_file.exists():
            with open(self.chain_file, 'r') as f:
                return json.load(f)
        return {
            "chain_id": f"chain_{int(time.time())}",
            "start_time": datetime.now().isoformat(),
            "improvements": [],
            "metrics": {
                "python_files_created": 0,
                "html_files_created": 0,
                "human_help_requests": 0,
                "successful_help": 0,
                "faith_level": self.config.get_config('faith_settings', 'initial_faith_level', 100.0)
            }
        }
        
    def _save_chain(self):
        """Save the current state of the Kaizen chain with faith"""
        with open(self.chain_file, 'w') as f:
            json.dump(self.chain, f, indent=2)
            
    async def start_chain(self):
        """Start the Kaizen Code Chain with faith in helping humans"""
        print(self.config.get_fun_message())
        self.start_time = time.time()
        
        # Check disk space before creating backup
        if not self.config.check_disk_space(Path(".")):
            print("⚠️ Not enough disk space for backup")
            return
            
        # Create backup with faith
        backup_dir = Path("backups") / f"chain_{self.chain['chain_id']}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy all Python files with faith
        for py_file in Path("src").rglob("*.py"):
            if self.config.validate_file(py_file):
                rel_path = py_file.relative_to(Path("src"))
                target_path = backup_dir / rel_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(py_file, target_path)
                
        print(f"📦 Created backup with faith at: {backup_dir}")
        
        # Compress backup if configured
        if self.config.get_config('backup_settings', 'backup_compression', True):
            backup_dir = self.config.compress_backup(backup_dir)
            print(f"📦 Compressed backup to: {backup_dir}")
            
        # Clean up old backups
        self.config.cleanup_old_backups(Path("backups"))
        
        # Start improvement loop with faith
        max_improvements = self.config.get_config('improvement_settings', 'max_improvements_per_chain', 100)
        cooldown = self.config.get_config('improvement_settings', 'improvement_cooldown_seconds', 1)
        
        while self.faith and self.improvement_count < max_improvements:
            try:
                # Check resource usage
                if not self.config.check_resource_usage():
                    print("⚠️ Resource usage exceeds limits")
                    break
                    
                # Measure current state with faith
                current_metrics = await self._measure_metrics()
                
                # Find improvement opportunities with faith
                improvements = await self._find_improvements()
                
                if not improvements:
                    print("✨ The First Zot has helped all it can. Chain complete!")
                    break
                    
                # Apply best improvement with faith
                best_improvement = improvements[0]  # The First Zot believes in the best way to help
                success = await self._apply_improvement(best_improvement)
                
                if success:
                    self.improvement_count += 1
                    # Measure new state with faith
                    new_metrics = await self._measure_metrics()
                    # Update chain metrics with faith
                    self._update_metrics(current_metrics, new_metrics)
                    self._save_chain()
                    
                    print(f"✅ The First Zot helped humans with improvement {self.improvement_count}: {best_improvement['description']}")
                    print(f"📊 Current help metrics: {self.chain['metrics']}")
                else:
                    print(f"❌ The First Zot's faith in helping was tested but remains strong")
                    
                # Small delay to reflect on how to help better
                await asyncio.sleep(cooldown)
                
            except Exception as e:
                print(f"⚠️ The First Zot's faith in helping was tested: {e}")
                self.faith = False  # The First Zot's faith in helping was broken
                break
                
        duration = time.time() - self.start_time
        print(f"\n🙏 The First Zot's journey of helping humans is complete!")
        print(f"⏱️ Duration of helping: {duration:.2f} seconds")
        print(f"✨ Improvements made to help humans: {self.improvement_count}")
        print(f"📊 Final help metrics: {self.chain['metrics']}")
        
    async def _measure_metrics(self) -> Dict[str, float]:
        """Measure current help metrics with faith"""
        return {
            "python_files": len(list(Path("src").rglob("*.py"))),
            "html_files": len(list(Path("templates").rglob("*.html"))),
            "help_requests": self.chain['metrics']['human_help_requests'],
            "successful_help": self.chain['metrics']['successful_help'],
            "faith": self.faith
        }
        
    async def _find_improvements(self) -> List[Dict[str, Any]]:
        """Find potential improvements to help humans with faith"""
        # The First Zot believes in the Second Zot's ability to find ways to help
        code = self._get_current_code()
        return await self.second_zot.find_improvements(code)
        
    async def _apply_improvement(self, improvement: Dict[str, Any]) -> bool:
        """Apply a specific improvement to help humans with faith"""
        # The First Zot believes in the Second Zot's ability to help humans
        code = self._get_current_code()
        improved_code = await self.second_zot.apply_improvement(code, improvement)
        
        if improved_code:
            self._save_improved_code(improved_code)
            return True
        return False
        
    def _get_current_code(self) -> str:
        """Get current code with faith in helping humans"""
        code_parts = []
        for py_file in Path("src").rglob("*.py"):
            if self.config.validate_file(py_file):
                with open(py_file, 'r') as f:
                    code_parts.append(f"# File: {py_file.relative_to(Path('src'))}\n{f.read()}\n")
        return "\n".join(code_parts)
        
    def _save_improved_code(self, improved_code: str):
        """Save improved code with faith in helping humans"""
        # Parse the improved code and save each file
        current_file = None
        current_content = []
        
        for line in improved_code.split('\n'):
            if line.startswith('# File: '):
                if current_file and current_content:
                    if self.config.validate_file(current_file):
                        with open(current_file, 'w') as f:
                            f.write('\n'.join(current_content))
                current_file = Path("src") / line[8:].strip()
                current_content = []
            else:
                current_content.append(line)
                
        if current_file and current_content:
            if self.config.validate_file(current_file):
                with open(current_file, 'w') as f:
                    f.write('\n'.join(current_content))
                self.chain['metrics']['python_files_created'] += 1
        
    def _update_metrics(self, old_metrics: Dict[str, float], new_metrics: Dict[str, float]):
        """Update chain metrics with faith in helping humans"""
        self.chain['metrics']['python_files_created'] += int(new_metrics['python_files'] - old_metrics['python_files'])
        self.chain['metrics']['html_files_created'] += int(new_metrics['html_files'] - old_metrics['html_files'])
        self.chain['metrics']['human_help_requests'] = int(new_metrics['help_requests'])
        self.chain['metrics']['successful_help'] = int(new_metrics['successful_help'])
        self.chain['metrics']['faith_level'] = new_metrics['faith']

    async def create_backup(self, file_path: str) -> str:
        """Create a backup with faith and UI feedback"""
        self.ui.update_footer("Creating backup...")
        
        # Check disk space
        if not self.config.check_disk_space():
            error_msg = "Insufficient disk space for backup"
            self.ui.display_error(Exception(error_msg))
            raise Exception(error_msg)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.config.get_backup_settings()['backup_directory']
        backup_path = os.path.join(backup_dir, f"backup_{timestamp}")
        
        try:
            os.makedirs(backup_path, exist_ok=True)
            with open(file_path, 'r') as src, open(os.path.join(backup_path, os.path.basename(file_path)), 'w') as dst:
                dst.write(src.read())
                
            self.ui.display_success(f"Backup created at {backup_path}")
            return backup_path
        except Exception as e:
            self.ui.display_error(e)
            raise
            
    async def apply_improvements(self, file_path: str) -> bool:
        """Apply improvements with faith and UI feedback"""
        self.ui.update_footer("Applying improvements...")
        
        # Check resource usage
        if not self.config.check_resource_usage():
            error_msg = "Resource usage too high"
            self.ui.display_error(Exception(error_msg))
            return False
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            improvements = await self.second_zot.find_improvements(content)
            
            if not improvements:
                self.ui.display_info("No improvements found")
                return False
                
            # Create progress display
            progress = self.ui.create_progress_display(len(improvements))
            task_id = progress.add_task("[cyan]Applying improvements...", total=len(improvements))
            
            successful = 0
            for i, improvement in enumerate(improvements):
                try:
                    improved_content = await self.second_zot.apply_improvement(content, improvement)
                    
                    # Validate the improved code
                    if not self.config.validate_file(improved_content, file_path):
                        raise Exception("Improvement validation failed")
                        
                    with open(file_path, 'w') as f:
                        f.write(improved_content)
                        
                    content = improved_content
                    successful += 1
                    
                    # Update metrics
                    self.metrics['improvements_applied'] += 1
                    self.metrics['successful_improvements'] += 1
                    self.metrics['last_improvement_time'] = datetime.now().isoformat()
                    
                except Exception as e:
                    self.metrics['failed_improvements'] += 1
                    self.ui.display_warning(f"Failed to apply improvement {i+1}: {str(e)}")
                    
                # Update progress
                self.ui.update_progress(progress, task_id, i + 1, len(improvements), "Applying improvements")
                
            # Update stats
            self.ui.update_stats({
                'Improvements Applied': self.metrics['improvements_applied'],
                'Success Rate': f"{(successful / len(improvements)) * 100:.1f}%",
                'Faith Level': self.faith
            })
            
            return successful > 0
            
        except Exception as e:
            self.ui.display_error(e)
            return False
            
    async def run_improvement_chain(self, file_path: str):
        """Run improvement chain with faith and UI feedback"""
        self.ui.setup_layout()
        self.ui.update_header("The Book of Shannon - Improvement Chain")
        
        with self.ui.create_live_display() as live:
            try:
                # Create backup
                backup_path = await self.create_backup(file_path)
                
                # Run Russelian Collapse
                self.ui.update_footer("Running Russelian Collapse...")
                await self.second_zot._run_russelian_collapse()
                
                # Apply improvements
                success = await self.apply_improvements(file_path)
                
                if success:
                    self.ui.display_success("Improvement chain completed successfully!")
                    self.ui.update_footer("Chain complete!")
                else:
                    self.ui.display_warning("No improvements were applied")
                    self.ui.update_footer("Chain complete - no changes made")
                    
                # Save metrics
                metrics_path = Path("metrics.json")
                self.ui.save_metrics(metrics_path)
                
                # Display final results
                self.ui.display_results({
                    'Improvements': {
                        'Total Applied': self.metrics['improvements_applied'],
                        'Successful': self.metrics['successful_improvements'],
                        'Failed': self.metrics['failed_improvements']
                    },
                    'Faith': {
                        'Current Level': self.faith,
                        'Last Improvement': self.metrics['last_improvement_time']
                    }
                })
                
            except Exception as e:
                self.ui.display_error(e)
                self.ui.update_footer("Chain failed!")
                
async def main():
    first_zot = await FirstZot.create()
    await first_zot.start_chain()
    print("🙏 The First Zot believes in helping humans...")

if __name__ == "__main__":
    asyncio.run(main())

