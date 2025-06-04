import multiprocessing
import subprocess
import sys
import os
import time
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
from pathlib import Path
from .test_driven_improvement import TestDrivenImprovement
from .config import ConfigManager
from .russelian_collapse import RusselianCollapse

@dataclass
class ImprovementAttempt:
    """Represents an attempt to improve the code"""
    attempt_id: str
    error: Optional[str]
    fixes_applied: List[Dict[str, Any]]
    test_results: Optional[Dict[str, Any]]
    success: bool
    timestamp: float
    process_id: int

class RecursiveImprovement:
    """Implements a self-improving loop with process spawning"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self._setup_logging()
        self.test_driven = TestDrivenImprovement(config)
        self.russelian_collapse = RusselianCollapse()
        self.max_attempts = config.get("improvement", {}).get("max_attempts", 10)
        self.max_processes = config.get("improvement", {}).get("max_processes", 4)
        self.attempts_dir = Path("improvement_attempts")
        self.attempts_dir.mkdir(exist_ok=True)
        self.active_processes: Dict[int, multiprocessing.Process] = {}
        self.attempts: List[ImprovementAttempt] = []
        
    def _setup_logging(self):
        """Set up logging for the recursive improvement system"""
        self.logger = logging.getLogger('RecursiveImprovement')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('logs/recursive_improvement.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
    def start_improvement_loop(self, target_file: str):
        """Start the recursive improvement loop"""
        self.logger.info(f"Starting improvement loop for {target_file}")
        
        # Initial test run
        test_result = self.test_driven.run_tests()
        if test_result.passed:
            self.logger.info("Initial tests passed, no improvements needed")
            return True
            
        # Start improvement processes
        attempt_id = self._generate_attempt_id()
        self._spawn_improvement_process(target_file, attempt_id)
        
        # Monitor processes
        while self.active_processes:
            self._check_processes()
            if len(self.active_processes) < self.max_processes:
                # Spawn more processes if needed
                attempt_id = self._generate_attempt_id()
                self._spawn_improvement_process(target_file, attempt_id)
            time.sleep(1)
            
        # Check final results
        return self._check_improvement_success()
        
    def _spawn_improvement_process(self, target_file: str, attempt_id: str):
        """Spawn a new improvement process"""
        if len(self.active_processes) >= self.max_processes:
            return
            
        process = multiprocessing.Process(
            target=self._improvement_worker,
            args=(target_file, attempt_id)
        )
        process.start()
        self.active_processes[process.pid] = process
        self.logger.info(f"Spawned improvement process {process.pid}")
        
    def _improvement_worker(self, target_file: str, attempt_id: str):
        """Worker process for attempting improvements"""
        try:
            # Load the file
            with open(target_file, 'r') as f:
                code = f.read()
                
            # Get improvement suggestions
            improvements = self.test_driven.suggest_test_improvements()
            
            # Apply improvements
            fixes_applied = []
            for imp in improvements:
                if self._apply_improvement(imp):
                    fixes_applied.append(imp)
                    
            # Run tests
            test_result = self.test_driven.run_tests()
            
            # Save attempt
            attempt = ImprovementAttempt(
                attempt_id=attempt_id,
                error=None,
                fixes_applied=fixes_applied,
                test_results=test_result.__dict__,
                success=test_result.passed,
                timestamp=time.time(),
                process_id=os.getpid()
            )
            self._save_attempt(attempt)
            
        except Exception as e:
            self.logger.error(f"Error in improvement worker: {str(e)}")
            attempt = ImprovementAttempt(
                attempt_id=attempt_id,
                error=str(e),
                fixes_applied=[],
                test_results=None,
                success=False,
                timestamp=time.time(),
                process_id=os.getpid()
            )
            self._save_attempt(attempt)
            
    def _check_processes(self):
        """Check status of active processes"""
        for pid, process in list(self.active_processes.items()):
            if not process.is_alive():
                process.join()
                del self.active_processes[pid]
                self.logger.info(f"Process {pid} completed")
                
    def _check_improvement_success(self) -> bool:
        """Check if any improvement attempt was successful"""
        for attempt in self.attempts:
            if attempt.success:
                self.logger.info(f"Successful improvement found in attempt {attempt.attempt_id}")
                return True
        return False
        
    def _apply_improvement(self, improvement: Dict[str, Any]) -> bool:
        """Apply a single improvement"""
        try:
            # Validate with Russelian Collapse
            validation = self.russelian_collapse.validate(
                improvement['code'],
                {'type': improvement['type']}
            )
            if not validation.is_valid:
                return False
                
            # Apply the improvement
            # This would be implemented by your code modification system
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying improvement: {str(e)}")
            return False
            
    def _save_attempt(self, attempt: ImprovementAttempt):
        """Save an improvement attempt"""
        self.attempts.append(attempt)
        file_path = self.attempts_dir / f"attempt_{attempt.attempt_id}.json"
        with open(file_path, 'w') as f:
            json.dump(attempt.__dict__, f, indent=2)
            
    def _generate_attempt_id(self) -> str:
        """Generate a unique attempt ID"""
        return f"{int(time.time())}_{len(self.attempts)}"
        
    def cleanup(self):
        """Clean up resources"""
        # Terminate any remaining processes
        for process in self.active_processes.values():
            if process.is_alive():
                process.terminate()
                process.join()
                
        # Save final state
        state = {
            'total_attempts': len(self.attempts),
            'successful_attempts': sum(1 for a in self.attempts if a.success),
            'last_attempt': self.attempts[-1].__dict__ if self.attempts else None
        }
        with open(self.attempts_dir / 'improvement_state.json', 'w') as f:
            json.dump(state, f, indent=2) 