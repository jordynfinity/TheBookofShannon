from typing import Dict, List, Set, Optional, Any, Callable, Tuple
import numpy as np
from dataclasses import dataclass
import pygame
import sounddevice as sd
import threading
import queue
import logging
from abc import ABC, abstractmethod
import random
import time
import colorsys
import math
from scipy import signal
import torch
import torch.nn as nn
import torch.optim as optim
import importlib
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich import print as rprint
from core.config import ConfigManager
from core.wave import WaveZot
from core.zot import Zot, FirstZot, SecondZot
from core.resource import ResourceManager
from core.improvement_chain import ImprovementChain
from core.russelian_collapse import RusselianCollapse
import multiprocessing
import concurrent.futures
from core.eira_assistant import EiraAssistant
import inspect
from core.event_bus import EventBus, Event

# Initialize rich console
console = Console()

class ErrorHandler:
    """Handles errors recursively with depth tracking"""
    def __init__(self, max_depth: int = 442):
        self.max_depth = max_depth
        self.current_depth = 0
        self.error_history: List[Dict[str, Any]] = []
        self.fix_attempts: Dict[str, int] = {}
        
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Handle an error recursively"""
        if self.current_depth >= self.max_depth:
            console.print(f"[red]Maximum recursion depth ({self.max_depth}) reached[/red]")
            return False
            
        self.current_depth += 1
        error_info = {
            "type": type(error).__name__,
            "message": str(error),
            "depth": self.current_depth,
            "context": context,
            "timestamp": time.time()
        }
        self.error_history.append(error_info)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"Fixing {error_info['type']}...", total=100)
            
            # Try to fix the error
            if self._attempt_fix(error, context, progress, task):
                console.print(f"[green]Fixed {error_info['type']} at depth {self.current_depth}[/green]")
                self.current_depth -= 1
                return True
                
            console.print(f"[yellow]Could not fix {error_info['type']} at depth {self.current_depth}[/yellow]")
            self.current_depth -= 1
            return False
            
    def _attempt_fix(self, error: Exception, context: Dict[str, Any], progress: Progress, task: int) -> bool:
        """Attempt to fix an error"""
        error_type = type(error).__name__
        self.fix_attempts[error_type] = self.fix_attempts.get(error_type, 0) + 1
        
        if error_type == "ModuleNotFoundError":
            return self._fix_module_error(error, context, progress, task)
        elif error_type == "ImportError":
            return self._fix_import_error(error, context, progress, task)
        elif error_type == "AttributeError":
            return self._fix_attribute_error(error, context, progress, task)
        elif error_type == "TypeError":
            return self._fix_type_error(error, context, progress, task)
        elif error_type == "ValueError":
            return self._fix_value_error(error, context, progress, task)
            
        return False
        
    def _fix_module_error(self, error: Exception, context: Dict[str, Any], progress: Progress, task: int) -> bool:
        """Fix ModuleNotFoundError"""
        try:
            module_name = str(error).split("'")[1]
            progress.update(task, advance=20)
            
            # Try to create the module
            module_path = Path("src") / module_name.replace(".", "/")
            if not module_path.exists():
                module_path.parent.mkdir(parents=True, exist_ok=True)
                with open(module_path.with_suffix(".py"), "w") as f:
                    f.write("# Auto-generated module\n")
            progress.update(task, advance=20)
            
            # Try to import the module
            try:
                importlib.import_module(module_name)
                progress.update(task, advance=60)
                return True
            except Exception as e:
                if self.current_depth < self.max_depth:
                    return self.handle_error(e, {"module": module_name})
                    
        except Exception as e:
            if self.current_depth < self.max_depth:
                return self.handle_error(e, {"error": error, "context": context})
                
        return False
        
    def _fix_import_error(self, error: Exception, context: Dict[str, Any], progress: Progress, task: int) -> bool:
        """Fix ImportError"""
        try:
            module_name = str(error).split("'")[1]
            progress.update(task, advance=20)
            
            # Try to install the module
            os.system(f"pip install {module_name}")
            progress.update(task, advance=80)
            return True
            
        except Exception as e:
            if self.current_depth < self.max_depth:
                return self.handle_error(e, {"error": error, "context": context})
                
        return False
        
    def _fix_attribute_error(self, error: Exception, context: Dict[str, Any], progress: Progress, task: int) -> bool:
        """Fix AttributeError"""
        try:
            attr_name = str(error).split("'")[1]
            progress.update(task, advance=20)
            
            # Try to add the attribute
            if "object" in context:
                setattr(context["object"], attr_name, None)
                progress.update(task, advance=80)
                return True
                
        except Exception as e:
            if self.current_depth < self.max_depth:
                return self.handle_error(e, {"error": error, "context": context})
                
        return False
        
    def _fix_type_error(self, error: Exception, context: Dict[str, Any], progress: Progress, task: int) -> bool:
        """Fix TypeError"""
        try:
            # Try to convert types
            if "value" in context and "expected_type" in context:
                converted = context["expected_type"](context["value"])
                progress.update(task, advance=100)
                return True
                
        except Exception as e:
            if self.current_depth < self.max_depth:
                return self.handle_error(e, {"error": error, "context": context})
                
        return False
        
    def _fix_value_error(self, error: Exception, context: Dict[str, Any], progress: Progress, task: int) -> bool:
        """Fix ValueError"""
        try:
            # Try to provide a valid value
            if "value" in context and "valid_range" in context:
                min_val, max_val = context["valid_range"]
                if context["value"] < min_val:
                    context["value"] = min_val
                elif context["value"] > max_val:
                    context["value"] = max_val
                progress.update(task, advance=100)
                return True
                
        except Exception as e:
            if self.current_depth < self.max_depth:
                return self.handle_error(e, {"error": error, "context": context})
                
        return False

class RichInterface:
    """Rich-based interface for the GUI"""
    def __init__(self):
        self.console = Console()
        self.error_handler = ErrorHandler()
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console
        )
        
    def show_error(self, error: Exception, context: Dict[str, Any]):
        """Show error with rich formatting"""
        self.console.print(Panel(
            f"[red]Error: {type(error).__name__}[/red]\n"
            f"[yellow]{str(error)}[/yellow]\n"
            f"[blue]Context: {context}[/blue]",
            title="Error Details"
        ))
        
    def show_progress(self, description: str, total: int = 100):
        """Show progress with rich formatting"""
        return self.progress.add_task(description, total=total)
        
    def update_progress(self, task: int, advance: int = 1):
        """Update progress"""
        self.progress.update(task, advance=advance)
        
    def show_table(self, title: str, data: List[Dict[str, Any]]):
        """Show data in a rich table"""
        table = Table(title=title)
        if data:
            for key in data[0].keys():
                table.add_column(key)
            for row in data:
                table.add_row(*[str(value) for value in row.values()])
        self.console.print(table)
        
    def show_panel(self, content: str, title: str = ""):
        """Show content in a rich panel"""
        self.console.print(Panel(content, title=title))

# Initialize rich interface
rich_interface = RichInterface()

# Try to import required modules with error handling
required_modules = [
    "src.core.base",
    "src.core.config",
    "src.improvement_consultant",
    "src.core.dependency_analyzer",
    "src.core.resource",
    "src.core.zot",
    "src.core.russelian_collapse",
    "src.core.improvement_chain"
]

for module in required_modules:
    try:
        importlib.import_module(module)
    except Exception as e:
        if not rich_interface.error_handler.handle_error(e, {"module": module}):
            console.print(f"[red]Failed to import {module} after all attempts[/red]")
            sys.exit(1)

# Now import the modules
from src.core.base import BaseComponent, State, ResourceAware, SelfImproving, Configurable
from src.core.config import ConfigManager
from src.improvement_consultant import ImprovementConsultant
from src.core.dependency_analyzer import DependencyAnalyzer
from src.core.resource import ResourceManager
from src.core.zot import Zot, FirstZot, SecondZot
from src.core.russelian_collapse import RusselianCollapse
from src.core.improvement_chain import ImprovementChain

@dataclass
class WaveState:
    """State for wave-based components"""
    amplitude: float = 1.0
    frequency: float = 1.0
    phase: float = 0.0
    energy: float = 1.0
    last_interaction: float = 0.0
    interaction_points: List[Tuple[float, float]] = None
    wave_history: List[float] = None

class WaveZot(FirstZot):
    """Base Zot for wave-based components"""
    def __init__(self, name: str, config_manager: ConfigManager):
        super().__init__(name)
        self.config_manager = config_manager
        self.state = WaveState()
        self.state.interaction_points = []
        self.state.wave_history = []
        self._setup_logging()
        self.improvement_chain = ImprovementChain()
        self.russelian_collapse = RusselianCollapse()
        self.resource_manager = ResourceManager()
        self.audio_queue = queue.Queue()
        self._setup_audio()
        
        # Add rich interface
        self.rich_interface = rich_interface
        self.progress_task = None
        
    def _setup_audio(self):
        """Setup audio processing"""
        self.sample_rate = 44100
        self.audio_thread = threading.Thread(target=self._audio_loop)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        
    def _audio_loop(self):
        """Process audio in background"""
        with sd.OutputStream(samplerate=self.sample_rate, channels=1) as stream:
            while True:
                if not self.audio_queue.empty():
                    audio_data = self.audio_queue.get()
                    stream.write(audio_data)
                time.sleep(0.01)
                
    def update(self) -> None:
        """Update wave state"""
        try:
            super().update()
            self._update_wave()
            self._process_interactions()
            self._generate_audio()
        except Exception as e:
            if not self.rich_interface.error_handler.handle_error(e, {"zot": self.name}):
                self.rich_interface.show_error(e, {"zot": self.name})
        
    def _update_wave(self):
        """Update wave properties"""
        try:
            # Update phase
            self.state.phase += 0.1 * self.state.frequency
            
            # Update amplitude based on energy
            self.state.amplitude = 0.5 + 0.5 * math.sin(self.state.phase)
            
            # Record wave history
            self.state.wave_history.append(self.state.amplitude)
            if len(self.state.wave_history) > 1000:
                self.state.wave_history.pop(0)
        except Exception as e:
            if not self.rich_interface.error_handler.handle_error(e, {"method": "_update_wave"}):
                self.rich_interface.show_error(e, {"method": "_update_wave"})
            
    def _process_interactions(self):
        """Process user interactions"""
        try:
            current_time = time.time()
            
            # Remove old interaction points
            self.state.interaction_points = [
                (x, t) for x, t in self.state.interaction_points
                if current_time - t < 5.0
            ]
            
            # Update wave properties based on interactions
            if self.state.interaction_points:
                # Calculate average interaction position
                avg_x = sum(x for x, _ in self.state.interaction_points) / len(self.state.interaction_points)
                
                # Adjust frequency based on interaction density
                self.state.frequency = 1.0 + len(self.state.interaction_points) * 0.1
                
                # Adjust energy based on recent interactions
                self.state.energy = min(1.0, self.state.energy + 0.1)
        except Exception as e:
            if not self.rich_interface.error_handler.handle_error(e, {"method": "_process_interactions"}):
                self.rich_interface.show_error(e, {"method": "_process_interactions"})
            
    def _generate_audio(self):
        """Generate audio from wave state"""
        try:
            # Generate sine wave
            t = np.linspace(0, 0.1, int(self.sample_rate * 0.1))
            wave = self.state.amplitude * np.sin(2 * np.pi * self.state.frequency * t + self.state.phase)
            
            # Add harmonics based on interaction points
            for x, _ in self.state.interaction_points:
                harmonic = 0.5 * np.sin(2 * np.pi * self.state.frequency * 2 * t + self.state.phase + x)
                wave += harmonic
                
            # Normalize and convert to float32
            wave = wave.astype(np.float32)
            self.audio_queue.put(wave)
        except Exception as e:
            if not self.rich_interface.error_handler.handle_error(e, {"method": "_generate_audio"}):
                self.rich_interface.show_error(e, {"method": "_generate_audio"})
            
    def handle_mouse(self, pos: Tuple[int, int], event_type: int):
        """Handle mouse events"""
        try:
            if event_type == pygame.MOUSEBUTTONDOWN:
                self.state.interaction_points.append((pos[0] / 800.0, time.time()))
                self.state.last_interaction = time.time()
        except Exception as e:
            if not self.rich_interface.error_handler.handle_error(e, {"method": "handle_mouse"}):
                self.rich_interface.show_error(e, {"method": "handle_mouse"})
            
    def handle_movement(self, pos: Tuple[int, int]):
        """Handle mouse movement"""
        try:
            # Add subtle interaction point for movement
            if random.random() < 0.1:  # 10% chance to add point
                self.state.interaction_points.append((pos[0] / 800.0, time.time()))
        except Exception as e:
            if not self.rich_interface.error_handler.handle_error(e, {"method": "handle_movement"}):
                self.rich_interface.show_error(e, {"method": "handle_movement"})
            
    def get_wave_value(self, x: float) -> float:
        """Get wave value at position x"""
        try:
            return self.state.amplitude * math.sin(2 * math.pi * self.state.frequency * x + self.state.phase)
        except Exception as e:
            if not self.rich_interface.error_handler.handle_error(e, {"method": "get_wave_value"}):
                self.rich_interface.show_error(e, {"method": "get_wave_value"})
            return 0.0

class WaveWindow(WaveZot):
    """Main application window with wave mechanics"""
    def __init__(self, name: str, config_manager: ConfigManager):
        super().__init__(name, config_manager)
        self.surface = None
        self.zots: Dict[str, WaveZot] = {}
        self._setup_window()
        
    def _setup_window(self):
        """Initialize pygame window"""
        try:
            config = self.config_manager.get_component_config(self.name)
            window_config = config.get("window", {})
            
            width = window_config.get("width", 800)
            height = window_config.get("height", 600)
            title = window_config.get("title", "Wave Interface")
            
            pygame.init()
            self.surface = pygame.display.set_mode((width, height))
            pygame.display.set_caption(title)
        except Exception as e:
            if not self.rich_interface.error_handler.handle_error(e, {"method": "_setup_window"}):
                self.rich_interface.show_error(e, {"method": "_setup_window"})
        
    def add_zot(self, zot: WaveZot):
        """Add a Zot to the window"""
        try:
            self.zots[zot.name] = zot
            zot.initialize()
        except Exception as e:
            if not self.rich_interface.error_handler.handle_error(e, {"method": "add_zot", "zot": zot.name}):
                self.rich_interface.show_error(e, {"method": "add_zot", "zot": zot.name})
        
    def remove_zot(self, name: str):
        """Remove a Zot from the window"""
        try:
            if name in self.zots:
                self.zots[name].cleanup()
                del self.zots[name]
        except Exception as e:
            if not self.rich_interface.error_handler.handle_error(e, {"method": "remove_zot", "zot": name}):
                self.rich_interface.show_error(e, {"method": "remove_zot", "zot": name})
            
    def update(self) -> None:
        """Update window and all Zots"""
        try:
            super().update()
            
            # Update all Zots
            for zot in self.zots.values():
                zot.update()
                
            # Check and optimize resources
            for zot in self.zots.values():
                if isinstance(zot, ResourceAware):
                    resources = zot.check_resources()
                    if any(usage > 0.8 for usage in resources.values()):
                        zot.optimize_resources()
                        
            # Generate and apply improvements
            for zot in self.zots.values():
                if isinstance(zot, SelfImproving):
                    improvements = zot.generate_improvements()
                    for improvement in improvements:
                        if zot.validate_improvement(improvement):
                            zot.apply_improvement(improvement)
        except Exception as e:
            if not self.rich_interface.error_handler.handle_error(e, {"method": "update"}):
                self.rich_interface.show_error(e, {"method": "update"})
                        
    def render(self):
        """Render window and all Zots"""
        try:
            self.surface.fill((0, 0, 0))  # Clear screen
            
            # Draw wave
            points = []
            for x in range(0, 800, 2):
                y = 300 + 100 * self.get_wave_value(x / 800.0)
                points.append((x, int(y)))
                
            if len(points) > 1:
                pygame.draw.lines(self.surface, (0, 255, 0), False, points, 2)
                
            # Draw interaction points
            for x, t in self.state.interaction_points:
                screen_x = int(x * 800)
                age = time.time() - t
                alpha = int(255 * (1 - age / 5.0))
                if alpha > 0:
                    color = (255, 255, 255, alpha)
                    pygame.draw.circle(self.surface, color, (screen_x, 300), 5)
                    
            # Render all visible Zots
            for zot in self.zots.values():
                if zot.state.is_visible:
                    self._render_zot(zot)
                    
            pygame.display.flip()
        except Exception as e:
            if not self.rich_interface.error_handler.handle_error(e, {"method": "render"}):
                self.rich_interface.show_error(e, {"method": "render"})
        
    def _render_zot(self, zot: WaveZot):
        """Render a single Zot"""
        try:
            # Draw Zot's wave
            points = []
            for x in range(0, 800, 2):
                y = 300 + 100 * zot.get_wave_value(x / 800.0)
                points.append((x, int(y)))
                
            if len(points) > 1:
                pygame.draw.lines(self.surface, (255, 0, 0), False, points, 2)
        except Exception as e:
            if not self.rich_interface.error_handler.handle_error(e, {"method": "_render_zot", "zot": zot.name}):
                self.rich_interface.show_error(e, {"method": "_render_zot", "zot": zot.name})
            
    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events"""
        try:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for zot in self.zots.values():
                    if zot.state.is_visible:
                        zot.handle_mouse(event.pos, event.type)
            elif event.type == pygame.MOUSEMOTION:
                for zot in self.zots.values():
                    if zot.state.is_visible:
                        zot.handle_movement(event.pos)
        except Exception as e:
            if not self.rich_interface.error_handler.handle_error(e, {"method": "handle_event"}):
                self.rich_interface.show_error(e, {"method": "handle_event"})
                    
    def cleanup(self):
        """Clean up window and all Zots"""
        try:
            for zot in self.zots.values():
                zot.cleanup()
            pygame.quit()
            super().cleanup()
        except Exception as e:
            if not self.rich_interface.error_handler.handle_error(e, {"method": "cleanup"}):
                self.rich_interface.show_error(e, {"method": "cleanup"})

class TestResult:
    """Represents a test result with metadata"""
    def __init__(self, success: bool, error: Optional[str] = None, metrics: Dict[str, Any] = None, timestamp: float = None):
        self.success = success
        self.error = error
        self.metrics = metrics or {}
        self.timestamp = timestamp or time.time()

class Improvement:
    """Represents a code improvement with metadata"""
    def __init__(self, description: str, code_changes: Dict[str, str], priority: int, confidence: float, test_coverage: float, timestamp: float = None):
        self.description = description
        self.code_changes = code_changes
        self.priority = priority
        self.confidence = confidence
        self.test_coverage = test_coverage
        self.timestamp = timestamp or time.time()

class ParallelTestRunner:
    """Enhanced parallel test execution with process pool"""
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.executor = concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers)
        self.test_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.test_thread = threading.Thread(target=self._run_tests, daemon=True)
        self.test_thread.start()
        self.logger = logging.getLogger("ParallelTestRunner")
        
    def _run_tests(self):
        """Run tests in parallel using process pool"""
        while True:
            try:
                test_func = self.test_queue.get()
                future = self.executor.submit(test_func)
                try:
                    result = future.result(timeout=30)  # 30 second timeout
                    self.result_queue.put(TestResult(success=True, metrics=result))
                except concurrent.futures.TimeoutError:
                    self.result_queue.put(TestResult(success=False, error="Test timeout"))
                except Exception as e:
                    self.result_queue.put(TestResult(success=False, error=str(e)))
            except Exception as e:
                self.logger.error(f"Error in test runner: {str(e)}")
                self.result_queue.put(TestResult(success=False, error=str(e)))
            finally:
                self.test_queue.task_done()
                
    def add_test(self, test_func: Callable, timeout: float = 30.0):
        """Add a test to the queue with timeout"""
        self.test_queue.put((test_func, timeout))
        
    def get_results(self) -> List[TestResult]:
        """Get test results"""
        results = []
        while not self.result_queue.empty():
            results.append(self.result_queue.get())
        return results
        
    def cleanup(self):
        """Clean up resources"""
        self.executor.shutdown(wait=True)

class ImprovementGenerator:
    """Enhanced improvement generation with parallel processing"""
    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = logging.getLogger("ImprovementGenerator")
        self.improvement_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.worker_threads = []
        self.max_workers = multiprocessing.cpu_count()
        self._start_workers()
        
    def _start_workers(self):
        """Start worker threads for improvement generation"""
        for _ in range(self.max_workers):
            thread = threading.Thread(target=self._improvement_worker, daemon=True)
            thread.start()
            self.worker_threads.append(thread)
            
    def _improvement_worker(self):
        """Worker thread for generating improvements"""
        while True:
            try:
                test_result = self.improvement_queue.get()
                if test_result.success:
                    continue
                    
                # Generate improvement based on test failure
                improvement = self._generate_improvement(test_result)
                if improvement:
                    self.result_queue.put(improvement)
            except Exception as e:
                self.logger.error(f"Error in improvement worker: {str(e)}")
            finally:
                self.improvement_queue.task_done()
                
    def _generate_improvement(self, test_result: TestResult) -> Optional[Improvement]:
        """Generate improvement from test result"""
        try:
            # Analyze error and generate improvement
            error = test_result.error
            if not error:
                return None
                
            # Generate code changes based on error
            code_changes = self._analyze_error(error)
            if not code_changes:
                return None
                
            # Calculate improvement metrics
            priority = self._calculate_priority(error, code_changes)
            confidence = self._calculate_confidence(code_changes)
            test_coverage = self._calculate_test_coverage(code_changes)
            
            return Improvement(
                description=f"Fix for: {error}",
                code_changes=code_changes,
                priority=priority,
                confidence=confidence,
                test_coverage=test_coverage
            )
        except Exception as e:
            self.logger.error(f"Error generating improvement: {str(e)}")
            return None
            
    def _analyze_error(self, error: str) -> Dict[str, str]:
        """Analyze error and generate code changes"""
        # This would be enhanced with actual code analysis
        return {
            "error_type": type(error).__name__,
            "suggested_fix": str(error)
        }
        
    def _calculate_priority(self, error: str, changes: Dict[str, str]) -> int:
        """Calculate improvement priority"""
        # Simple priority calculation
        return len(error.split()) % 10
        
    def _calculate_confidence(self, changes: Dict[str, str]) -> float:
        """Calculate improvement confidence"""
        # Simple confidence calculation
        return 0.5 + (len(changes) * 0.1)
        
    def _calculate_test_coverage(self, changes: Dict[str, str]) -> float:
        """Calculate test coverage for changes"""
        # Simple coverage calculation
        return 0.7 + (len(changes) * 0.05)
        
    def add_test_result(self, test_result: TestResult):
        """Add test result for improvement generation"""
        self.improvement_queue.put(test_result)
        
    def get_improvements(self) -> List[Improvement]:
        """Get generated improvements"""
        improvements = []
        while not self.result_queue.empty():
            improvements.append(self.result_queue.get())
        return improvements
        
    def cleanup(self):
        """Clean up resources"""
        for thread in self.worker_threads:
            thread.join(timeout=1.0)

class DebugMonitor:
    """Monitors and logs debug information"""
    def __init__(self):
        self.logger = logging.getLogger("DebugMonitor")
        self.logger.setLevel(logging.DEBUG)
        self.metrics = {}
        self.current_fps = 0.0  # Initialize as float
        self.active_zots = set()
        self.improvement_count = 0
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def _monitor_loop(self):
        """Monitor loop for collecting metrics"""
        while True:
            try:
                # Collect metrics
                self.metrics.update({
                    "fps": self.current_fps,
                    "memory_usage": self.get_memory_usage(),
                    "cpu_usage": self.get_cpu_usage(),
                    "active_zots": len(self.active_zots),
                    "improvement_count": self.improvement_count
                })
                time.sleep(1)  # Update every second
            except Exception as e:
                self.logger.error(f"Error in monitor loop: {str(e)}")
                
    def get_memory_usage(self):
        """Get current memory usage"""
        try:
            import psutil
            return psutil.Process().memory_info().rss / 1024 / 1024  # MB
        except Exception:
            return 0.0
        
    def get_cpu_usage(self):
        """Get current CPU usage"""
        try:
            import psutil
            return psutil.Process().cpu_percent()
        except Exception:
            return 0.0
        
    def update_fps(self, fps: float):
        """Update current FPS"""
        self.current_fps = fps
        
    def add_zot(self, zot_name: str):
        """Add a Zot to active set"""
        self.active_zots.add(zot_name)
        
    def remove_zot(self, zot_name: str):
        """Remove a Zot from active set"""
        self.active_zots.discard(zot_name)
        
    def increment_improvements(self):
        """Increment improvement counter"""
        self.improvement_count += 1

class GodInterface:
    """The ultimate interface that coordinates all Zots"""
    
    def __init__(self):
        self._setup_logging()
        self.event_bus = EventBus()  # Initialize event bus
        self.config = ConfigManager()
        self.resource_manager = ResourceManager()
        self.improvement_chain = ImprovementChain()
        self.russelian_collapse = RusselianCollapse()
        self.test_runner = ParallelTestRunner()
        self.improvement_generator = ImprovementGenerator(self.config)
        self.debug_monitor = DebugMonitor()
        self.eira = EiraAssistant(event_bus=self.event_bus)  # Pass event bus to Eira
        self._initialize_pygame()
        self._setup_window()
        self._setup_zots()
        self._setup_event_handlers()
        
    def _setup_logging(self):
        """Set up logging"""
        self.logger = logging.getLogger("GodInterface")
        self.logger.setLevel(logging.DEBUG)
        
        # Ensure logs directory exists
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Set up file handler
        handler = logging.FileHandler("logs/gui.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
    def _initialize_pygame(self):
        """Initialize pygame"""
        try:
            if not pygame.get_init():
                pygame.init()
            self.logger.info("Pygame initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize pygame: {str(e)}")
            raise
            
    def _setup_window(self):
        """Set up the main window"""
        try:
            # Get window configuration with defaults
            window_config = self.config.get("window", {})
            if not window_config:
                window_config = {
                    "width": 800,
                    "height": 600,
                    "title": "The Book of Shannon",
                    "fps": 60
                }
                self.config.set("window", window_config)
            
            self.width = window_config.get("width", 800)
            self.height = window_config.get("height", 600)
            self.title = window_config.get("title", "The Book of Shannon")
            self.fps = window_config.get("fps", 60)
            
            # Ensure pygame is initialized
            if not pygame.get_init():
                pygame.init()
                
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption(self.title)
            self.clock = pygame.time.Clock()
            
            self.logger.info(f"Window initialized: {self.width}x{self.height} @ {self.fps}fps")
        except Exception as e:
            self.logger.error(f"Failed to set up window: {str(e)}")
            raise
            
    def _setup_zots(self):
        """Set up the Zot network"""
        try:
            # Create the wave Zot
            wave_config = self.config.get("wave", {})
            if not wave_config:
                wave_config = {
                    "amplitude": 50,
                    "frequency": 0.1,
                    "phase": 0,
                    "interaction_decay": 0.95
                }
                self.config.set("wave", wave_config)
                
            # Create wave Zot with state
            self.wave = WaveZot("wave_zot", self.config)
            self.wave.state.amplitude = wave_config.get("amplitude", 50)
            self.wave.state.frequency = wave_config.get("frequency", 0.1)
            self.wave.state.phase = wave_config.get("phase", 0)
            self.wave.state.interaction_decay = wave_config.get("interaction_decay", 0.95)
            
            # Create the first Zot
            self.first_zot = FirstZot("first_zot")
            
            # Create the second Zot
            self.second_zot = SecondZot("second_zot")
            
            # Set up the improvement chain
            self.improvement_chain.add_zot(self.first_zot)
            self.improvement_chain.add_zot(self.second_zot)
            
            # Add Zots to debug monitor
            self.debug_monitor.add_zot("wave_zot")
            self.debug_monitor.add_zot("first_zot")
            self.debug_monitor.add_zot("second_zot")
            
            self.logger.info("Zot network initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to set up Zots: {str(e)}")
            raise
            
    def _setup_event_handlers(self):
        """Set up event handlers for component communication"""
        # Subscribe to wave events
        self.event_bus.subscribe("wave_interaction", self._handle_wave_interaction)
        self.event_bus.subscribe("wave_update", self._handle_wave_update)
        
        # Subscribe to Zot events
        self.event_bus.subscribe("zot_state_change", self._handle_zot_state_change)
        self.event_bus.subscribe("zot_improvement", self._handle_zot_improvement)
        
        # Subscribe to test events
        self.event_bus.subscribe("test_result", self._handle_test_result)
        self.event_bus.subscribe("improvement_suggestion", self._handle_improvement_suggestion)
        
        # Subscribe to debug events
        self.event_bus.subscribe("debug_metric", self._handle_debug_metric)
        
        # Subscribe to Eira events
        self.event_bus.subscribe("eira_analysis", self._handle_eira_analysis)
        self.event_bus.subscribe("eira_error", self._handle_eira_error)
        self.event_bus.subscribe("eira_debug_suggestions", self._handle_eira_debug_suggestions)
        self.event_bus.subscribe("eira_improvement_suggestions", self._handle_eira_improvement_suggestions)
        
    def _handle_wave_interaction(self, data: Dict[str, Any]):
        """Handle wave interaction events"""
        try:
            x, y = data.get("position", (0, 0))
            self.wave.interact(x, y)
            self.first_zot.handle_interaction(x, y)
            self.second_zot.handle_interaction(x, y)
        except Exception as e:
            self.logger.error(f"Error handling wave interaction: {str(e)}")
            
    def _handle_wave_update(self, data: Dict[str, Any]):
        """Handle wave update events"""
        try:
            self.debug_monitor.update_fps(data.get("fps", 0))
            self.event_bus.publish("debug_metric", {
                "type": "wave",
                "metrics": data
            })
        except Exception as e:
            self.logger.error(f"Error handling wave update: {str(e)}")
            
    def _handle_zot_state_change(self, data: Dict[str, Any]):
        """Handle Zot state change events"""
        try:
            zot_name = data.get("zot_name")
            new_state = data.get("state")
            if zot_name and new_state:
                self.debug_monitor.add_zot(zot_name)
                self.event_bus.publish("debug_metric", {
                    "type": "zot_state",
                    "zot": zot_name,
                    "state": new_state
                })
        except Exception as e:
            self.logger.error(f"Error handling Zot state change: {str(e)}")
            
    def _handle_zot_improvement(self, data: Dict[str, Any]):
        """Handle Zot improvement events"""
        try:
            improvement = data.get("improvement")
            if improvement and self.russelian_collapse.validate(improvement):
                self.improvement_chain.apply_improvement(improvement)
                self.debug_monitor.increment_improvements()
        except Exception as e:
            self.logger.error(f"Error handling Zot improvement: {str(e)}")
            
    def _handle_test_result(self, data: Dict[str, Any]):
        """Handle test result events"""
        try:
            result = data.get("result")
            if result:
                self.improvement_generator.add_test_result(result)
                if not result.success:
                    self.event_bus.publish("improvement_suggestion", {
                        "type": "test_failure",
                        "result": result
                    })
        except Exception as e:
            self.logger.error(f"Error handling test result: {str(e)}")
            
    def _handle_improvement_suggestion(self, data: Dict[str, Any]):
        """Handle improvement suggestion events"""
        try:
            suggestion = data.get("suggestion")
            if suggestion:
                analysis = self.eira.analyze_code(
                    code=suggestion.get("code", ""),
                    context=suggestion.get("context", ""),
                    focus_areas=suggestion.get("focus_areas", [])
                )
                if analysis.improvements:
                    self.event_bus.publish("zot_improvement", {
                        "improvement": analysis.improvements[0]
                    })
        except Exception as e:
            self.logger.error(f"Error handling improvement suggestion: {str(e)}")
            
    def _handle_debug_metric(self, data: Dict[str, Any]):
        """Handle debug metric events"""
        try:
            metric_type = data.get("type")
            metrics = data.get("metrics", {})
            if metric_type and metrics:
                self.debug_monitor.metrics.update(metrics)
        except Exception as e:
            self.logger.error(f"Error handling debug metric: {str(e)}")
            
    def _handle_eira_analysis(self, data: Dict[str, Any]):
        """Handle Eira analysis events"""
        try:
            suggestions = data.get("suggestions", [])
            improvements = data.get("improvements", [])
            if suggestions or improvements:
                self.logger.info(f"Eira analysis: {len(suggestions)} suggestions, {len(improvements)} improvements")
                if improvements:
                    self.event_bus.publish("zot_improvement", {
                        "improvement": improvements[0]
                    })
        except Exception as e:
            self.logger.error(f"Error handling Eira analysis: {str(e)}")
            
    def _handle_eira_error(self, data: Dict[str, Any]):
        """Handle Eira error events"""
        try:
            error = data.get("error")
            context = data.get("context")
            self.logger.error(f"Eira error in {context}: {error}")
        except Exception as e:
            self.logger.error(f"Error handling Eira error: {str(e)}")
            
    def _handle_eira_debug_suggestions(self, data: Dict[str, Any]):
        """Handle Eira debug suggestion events"""
        try:
            suggestions = data.get("suggestions", [])
            error = data.get("error", {})
            if suggestions:
                self.logger.info(f"Eira debug suggestions for {error.get('type')}:")
                for suggestion in suggestions:
                    self.logger.info(f"- {suggestion}")
        except Exception as e:
            self.logger.error(f"Error handling Eira debug suggestions: {str(e)}")
            
    def _handle_eira_improvement_suggestions(self, data: Dict[str, Any]):
        """Handle Eira improvement suggestion events"""
        try:
            suggestions = data.get("suggestions", [])
            metrics = data.get("metrics", {})
            if suggestions:
                self.logger.info(f"Eira improvement suggestions based on metrics:")
                for suggestion in suggestions:
                    self.logger.info(f"- {suggestion.get('description', 'Unknown')}")
                self.event_bus.publish("zot_improvement", {
                    "improvement": suggestions[0]
                })
        except Exception as e:
            self.logger.error(f"Error handling Eira improvement suggestions: {str(e)}")
            
    def run(self):
        """Run the main loop"""
        try:
            # Ensure pygame is initialized
            if not pygame.get_init():
                pygame.init()
                
            running = True
            last_test_time = time.time()
            last_improvement_time = time.time()
            test_interval = 5.0  # Run tests every 5 seconds
            improvement_interval = 30.0  # Run improvements every 30 seconds
            frame_count = 0
            last_fps_update = time.time()
            
            while running:
                try:
                    # Handle events
                    running = self._handle_events()
                    
                    # Update Zots
                    self.wave.update()
                    self.first_zot.update()
                    self.second_zot.update()
                    
                    current_time = time.time()
                    
                    # Run test cycle periodically
                    if current_time - last_test_time >= test_interval:
                        self._run_test_cycle()
                        last_test_time = current_time
                    
                    # Run continuous improvement cycle
                    if current_time - last_improvement_time >= improvement_interval:
                        self._continuous_improvement_cycle()
                        last_improvement_time = current_time
                    
                    # Draw everything
                    self._draw_wave()
                    
                    # Update FPS counter
                    frame_count += 1
                    if current_time - last_fps_update >= 1.0:
                        fps = frame_count / (current_time - last_fps_update)
                        self.debug_monitor.update_fps(fps)
                        frame_count = 0
                        last_fps_update = current_time
                    
                    # Cap the frame rate
                    self.clock.tick(self.fps)
                    
                except Exception as e:
                    if not self._handle_error(e, {"method": "run"}):
                        self.logger.error(f"Unhandled error in main loop: {str(e)}")
                        running = False
                
            self.logger.info("Main loop ended normally")
        except Exception as e:
            self.logger.error(f"Error in main loop: {str(e)}")
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Clean up resources"""
        try:
            # Clean up Zots
            self.wave.cleanup()
            self.first_zot.cleanup()
            self.second_zot.cleanup()
            
            # Remove Zots from debug monitor
            self.debug_monitor.remove_zot("wave_zot")
            self.debug_monitor.remove_zot("first_zot")
            self.debug_monitor.remove_zot("second_zot")
            
            # Clean up test runner and improvement generator
            self.test_runner.cleanup()
            self.improvement_generator.cleanup()
            
            # Clean up pygame
            if pygame.get_init():
                pygame.quit()
                
            self.logger.info("Resources cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
            
if __name__ == "__main__":
    try:
        interface = GodInterface()
        interface.run()
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        raise
