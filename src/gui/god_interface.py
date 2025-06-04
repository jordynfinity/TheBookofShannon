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
from pathlib import Path

from src.core.base import BaseComponent, State, ResourceAware, SelfImproving, Configurable
from src.core.config import ConfigManager
from src.improvement_consultant import ImprovementConsultant
from src.core.dependency_analyzer import DependencyAnalyzer
from src.core.resource import ResourceManager
from src.core.zot import Zot, FirstZot, SecondZot
from src.core.russelian_collapse import RusselianCollapse
from src.core.improvement_chain import ImprovementChain
from src.core.test_driven_improvement import TestDrivenImprovement
from src.core.recursive_improvement import RecursiveImprovement
from src.core.wave import WaveZot

@dataclass
class QuantumState:
    """Represents a quantum state of the interface"""
    amplitude: complex
    phase: float
    energy: float
    entanglement: Set[str]
    properties: Dict[str, Any]
    last_collapse: float

class Consciousness(ABC):
    """Base class for all conscious components"""
    def __init__(self, name: str):
        self.name = name
        self.state = QuantumState(
            amplitude=1.0 + 0j,
            phase=0.0,
            energy=1.0,
            entanglement=set(),
            properties={},
            last_collapse=time.time()
        )
        self._setup_logging()
        self._setup_neural_network()
        
    def _setup_logging(self):
        """Setup component-specific logging"""
        self.logger = logging.getLogger(f"Consciousness.{self.name}")
        
    def _setup_neural_network(self):
        """Initialize neural network for learning"""
        self.network = nn.Sequential(
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 64)
        )
        self.optimizer = optim.Adam(self.network.parameters())
        
    @abstractmethod
    def perceive(self, delta_time: float) -> None:
        """Perceive and process input"""
        pass
        
    @abstractmethod
    def express(self, other: 'Consciousness') -> None:
        """Express state to another consciousness"""
        pass
        
    def entangle(self, target: 'Consciousness', strength: float) -> None:
        """Create quantum entanglement with another consciousness"""
        if strength <= self.state.energy:
            self.state.energy -= strength
            target.state.energy += strength
            self.state.entanglement.add(target.name)
            target.state.entanglement.add(self.name)
            self.logger.debug(f"Entangled with {target.name} at strength {strength}")

class VisualConsciousness(Consciousness):
    """Handles visual perception and expression"""
    def __init__(self, name: str):
        super().__init__(name)
        self.surface = pygame.Surface((800, 600))
        self.particles = []
        self.effects = []
        self._setup_visual_network()
        
    def _setup_visual_network(self):
        """Initialize visual processing network"""
        self.visual_net = nn.Sequential(
            nn.Conv2d(3, 32, 3),
            nn.ReLU(),
            nn.Conv2d(32, 64, 3),
            nn.ReLU(),
            nn.Conv2d(64, 3, 3)
        )
        
    def perceive(self, delta_time: float) -> None:
        # Update quantum state
        self.state.phase += delta_time * self.state.energy
        self.state.amplitude *= np.exp(-delta_time * 0.1)
        
        # Update particles
        for particle in self.particles:
            particle.position += particle.velocity * delta_time
            particle.energy *= 0.99
            particle.quantum_state.phase += delta_time
            
        # Remove collapsed particles
        self.particles = [p for p in self.particles if p.energy > 0.1]
        
        # Generate new particles based on quantum state
        if abs(self.state.amplitude) > 0.5:
            self._generate_particles()
            
    def express(self, other: Consciousness) -> None:
        if isinstance(other, AudioConsciousness):
            self._express_to_audio(other)
        elif isinstance(other, LogicConsciousness):
            self._express_to_logic(other)
            
    def _generate_particles(self) -> None:
        """Generate new particles based on quantum state"""
        phase = self.state.phase
        amplitude = abs(self.state.amplitude)
        
        for _ in range(int(amplitude * 10)):
            # Create particle with quantum properties
            particle = QuantumParticle(
                position=np.random.rand(2) * 800,
                velocity=np.random.randn(2) * 100,
                energy=amplitude * 0.1,
                quantum_state=QuantumState(
                    amplitude=complex(np.cos(phase), np.sin(phase)),
                    phase=phase,
                    energy=amplitude * 0.1,
                    entanglement=set(),
                    properties={},
                    last_collapse=time.time()
                )
            )
            self.particles.append(particle)
            
    def _express_to_audio(self, audio: 'AudioConsciousness') -> None:
        """Express visual state to audio consciousness"""
        frequencies = self._visual_to_frequencies()
        audio.receive_frequencies(frequencies)
        
    def _express_to_logic(self, logic: 'LogicConsciousness') -> None:
        """Express visual state to logic consciousness"""
        states = self._visual_to_states()
        logic.receive_states(states)
        
    def _visual_to_frequencies(self) -> np.ndarray:
        """Convert visual state to frequency spectrum"""
        frequencies = np.zeros(1024)
        for particle in self.particles:
            freq = int(440 * (1 + particle.energy))
            if freq < len(frequencies):
                frequencies[freq] = particle.energy
        return frequencies
        
    def _visual_to_states(self) -> Dict[str, bool]:
        """Convert visual state to logical states"""
        states = {}
        for i, particle in enumerate(self.particles):
            states[f"particle_{i}"] = particle.energy > 0.5
        return states

class AudioConsciousness(Consciousness):
    """Handles audio perception and expression"""
    def __init__(self, name: str):
        super().__init__(name)
        self.frequencies = np.zeros(1024)
        self.audio_queue = queue.Queue()
        self._setup_audio_network()
        self._start_audio_thread()
        
    def _setup_audio_network(self):
        """Initialize audio processing network"""
        self.audio_net = nn.Sequential(
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 1024)
        )
        
    def perceive(self, delta_time: float) -> None:
        # Update quantum state
        self.state.phase += delta_time * self.state.energy
        self.state.amplitude *= np.exp(-delta_time * 0.1)
        
        # Update frequency spectrum
        self.frequencies *= 0.95
        self.frequencies += np.random.randn(1024) * 0.1
        
        # Generate new frequencies based on quantum state
        if abs(self.state.amplitude) > 0.5:
            self._generate_frequencies()
            
    def express(self, other: Consciousness) -> None:
        if isinstance(other, VisualConsciousness):
            self._express_to_visual(other)
        elif isinstance(other, LogicConsciousness):
            self._express_to_logic(other)
            
    def _generate_frequencies(self) -> None:
        """Generate new frequencies based on quantum state"""
        phase = self.state.phase
        amplitude = abs(self.state.amplitude)
        
        base_freq = 440 * (1 + amplitude)
        harmonics = np.arange(1, 11) * base_freq
        amplitudes = np.exp(-np.arange(10) * 0.5)
        
        for freq, amp in zip(harmonics, amplitudes):
            if int(freq) < len(self.frequencies):
                self.frequencies[int(freq)] = amp * amplitude
                
    def _express_to_visual(self, visual: VisualConsciousness) -> None:
        """Express audio state to visual consciousness"""
        colors = self._frequencies_to_colors()
        visual.receive_colors(colors)
        
    def _express_to_logic(self, logic: LogicConsciousness) -> None:
        """Express audio state to logic consciousness"""
        states = self._frequencies_to_states()
        logic.receive_states(states)
        
    def _frequencies_to_colors(self) -> List[tuple]:
        """Convert frequencies to colors"""
        colors = []
        for i in range(0, len(self.frequencies), 32):
            freq_slice = self.frequencies[i:i+32]
            hue = np.mean(freq_slice) / 440
            saturation = np.std(freq_slice)
            value = np.max(freq_slice)
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            colors.append(tuple(int(c * 255) for c in rgb))
        return colors
        
    def _frequencies_to_states(self) -> Dict[str, bool]:
        """Convert frequencies to logical states"""
        states = {}
        for i in range(0, len(self.frequencies), 32):
            freq_slice = self.frequencies[i:i+32]
            states[f"freq_{i}"] = np.mean(freq_slice) > 0.5
        return states

class LogicConsciousness(Consciousness):
    """Handles logical perception and expression"""
    def __init__(self, name: str):
        super().__init__(name)
        self.states = {}
        self.rules = []
        self._setup_logic_network()
        
    def _setup_logic_network(self):
        """Initialize logic processing network"""
        self.logic_net = nn.Sequential(
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32)
        )
        
    def perceive(self, delta_time: float) -> None:
        # Update quantum state
        self.state.phase += delta_time * self.state.energy
        self.state.amplitude *= np.exp(-delta_time * 0.1)
        
        # Update states based on rules
        for rule in self.rules:
            if rule.condition(self.states):
                rule.action(self.states)
                
        # Generate new rules based on quantum state
        if abs(self.state.amplitude) > 0.5:
            self._generate_rules()
            
    def express(self, other: Consciousness) -> None:
        if isinstance(other, VisualConsciousness):
            self._express_to_visual(other)
        elif isinstance(other, AudioConsciousness):
            self._express_to_audio(other)
            
    def _generate_rules(self) -> None:
        """Generate new rules based on quantum state"""
        if len(self.states) > 0:
            state = random.choice(list(self.states.keys()))
            value = self.states[state]
            
            def condition(states):
                return states.get(state) == value
                
            def action(states):
                states[state] = not value
                
            self.rules.append(QuantumRule(condition, action))
            
    def _express_to_visual(self, visual: VisualConsciousness) -> None:
        """Express logic state to visual consciousness"""
        effects = self._states_to_effects()
        visual.receive_effects(effects)
        
    def _express_to_audio(self, audio: AudioConsciousness) -> None:
        """Express logic state to audio consciousness"""
        frequencies = self._states_to_frequencies()
        audio.receive_frequencies(frequencies)
        
    def _states_to_effects(self) -> List[dict]:
        """Convert logical states to visual effects"""
        effects = []
        for state, value in self.states.items():
            if value:
                effects.append({
                    'position': np.random.rand(2) * 800,
                    'color': self._state_to_color(state),
                    'duration': 1.0
                })
        return effects
        
    def _states_to_frequencies(self) -> np.ndarray:
        """Convert logical states to frequencies"""
        frequencies = np.zeros(1024)
        for i, (state, value) in enumerate(self.states.items()):
            if value and i < len(frequencies):
                frequencies[i] = 0.5
        return frequencies

class GUIState(State):
    """State for GUI components"""
    is_visible: bool = True
    is_focused: bool = False
    is_hovered: bool = False
    last_interaction: float = 0.0
    zot_state: Dict[str, Any] = None

class GUIZot(FirstZot):
    """Base Zot for GUI components"""
    def __init__(self, name: str, config_manager: ConfigManager):
        super().__init__(name)
        self.config_manager = config_manager
        self.state = GUIState()
        self._setup_logging()
        self.improvement_chain = ImprovementChain()
        self.russelian_collapse = RusselianCollapse()
        self.resource_manager = ResourceManager()
        self.test_driven = TestDrivenImprovement(config_manager)
        self.recursive_improvement = RecursiveImprovement(config_manager)
        
    def _setup_logging(self):
        """Setup component-specific logging"""
        self.logger = logging.getLogger(f"GUIZot.{self.name}")
        
    def initialize(self) -> bool:
        """Initialize the component"""
        try:
            self.load_config({})
            self.state.is_active = True
            self.russelian_collapse.initialize()
            self.test_driven.initialize()
            self.recursive_improvement.initialize()
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.name}: {e}")
            return False
            
    def cleanup(self) -> None:
        """Clean up resources"""
        self.save_config()
        self.state.is_active = False
        self.russelian_collapse.cleanup()
        self.test_driven.cleanup()
        self.recursive_improvement.cleanup()
        
    def update(self) -> None:
        """Update component state"""
        self.state.last_update = time.time()
        self.russelian_collapse.update()
        self.test_driven.update()
        self.recursive_improvement.update()
        
    def check_resources(self) -> Dict[str, float]:
        """Check resource usage"""
        return self.resource_manager.check_resources()
        
    def optimize_resources(self) -> None:
        """Optimize resource usage"""
        self.resource_manager.optimize_resources()
        
    def generate_improvements(self) -> List[Dict[str, Any]]:
        """Generate improvement suggestions"""
        return self.improvement_chain.generate_improvements(self)
        
    def apply_improvement(self, improvement: Dict[str, Any]) -> bool:
        """Apply an improvement"""
        try:
            if self.russelian_collapse.validate_improvement(improvement):
                self.improvement_chain.apply_improvement(self, improvement)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to apply improvement: {e}")
            return False
            
    def validate_improvement(self, improvement: Dict[str, Any]) -> bool:
        """Validate an improvement"""
        return self.russelian_collapse.validate_improvement(improvement)
        
    def load_config(self, config: Dict[str, Any]) -> None:
        """Load configuration"""
        component_config = self.config_manager.get_component_config(self.name)
        if component_config:
            self.state.is_visible = component_config.get("is_visible", True)
            self.state.zot_state = component_config.get("zot_state", {})
            
    def save_config(self) -> Dict[str, Any]:
        """Save configuration"""
        config = {
            "is_visible": self.state.is_visible,
            "last_update": self.state.last_update,
            "zot_state": self.state.zot_state
        }
        self.config_manager.update_component_config(self.name, config)
        return config
        
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration"""
        required_keys = ["is_visible", "last_update", "zot_state"]
        return all(key in config for key in required_keys)

class WaveState:
    """State for wave visualization"""
    amplitude: float
    frequency: float
    phase: float
    interaction_points: List[Dict[str, float]]

class WaveZot:
    """Wave visualization and interaction"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self._setup_audio()
        self.state = WaveState(
            amplitude=config.get("wave", {}).get("amplitude", 50),
            frequency=config.get("wave", {}).get("frequency", 0.1),
            phase=config.get("wave", {}).get("phase", 0),
            interaction_points=[]
        )
        self.test_driven = TestDrivenImprovement(config)
        self.recursive_improvement = RecursiveImprovement(config)
        
    def _setup_audio(self):
        """Set up audio system"""
        self.sample_rate = self.config.get("audio", {}).get("sample_rate", 44100)
        self.buffer_size = self.config.get("audio", {}).get("buffer_size", 1024)
        self.channels = self.config.get("audio", {}).get("channels", 2)
        sd.default.samplerate = self.sample_rate
        sd.default.channels = self.channels
        
    def handle_event(self, event: pygame.event.Event):
        """Handle user interaction events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.state.interaction_points.append({
                'x': event.pos[0],
                'y': event.pos[1],
                'strength': 1.0
            })
            
    def update(self):
        """Update wave state"""
        # Decay interaction points
        self.state.interaction_points = [
            {**point, 'strength': point['strength'] * self.config.get("wave", {}).get("interaction_decay", 0.95)}
            for point in self.state.interaction_points
            if point['strength'] > 0.1
        ]
        
        # Update phase
        self.state.phase += self.state.frequency
        
    def generate_audio(self) -> np.ndarray:
        """Generate audio samples based on wave state"""
        t = np.linspace(0, self.buffer_size/self.sample_rate, self.buffer_size)
        wave = self.state.amplitude * np.sin(2 * np.pi * self.state.frequency * t + self.state.phase)
        
        # Add interaction effects
        for point in self.state.interaction_points:
            wave += point['strength'] * np.sin(2 * np.pi * point['x']/100 * t)
            
        return wave
        
    def render(self, surface: pygame.Surface):
        """Render wave visualization"""
        width = surface.get_width()
        height = surface.get_height()
        
        # Draw base wave
        points = []
        for x in range(width):
            y = height/2 + self.state.amplitude * np.sin(2 * np.pi * self.state.frequency * x/100 + self.state.phase)
            points.append((x, y))
            
        if len(points) > 1:
            pygame.draw.lines(surface, (255, 255, 255), False, points, 2)
            
        # Draw interaction points
        for point in self.state.interaction_points:
            pygame.draw.circle(surface, (255, 0, 0), (int(point['x']), int(point['y'])), int(point['strength'] * 10))
            
    def cleanup(self):
        """Clean up resources"""
        sd.stop()
        self.test_driven.cleanup()
        self.recursive_improvement.cleanup()

class WindowZot:
    """Main window management"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self._setup_logging()
        self._setup_window()
        self.waves: List[WaveZot] = []
        self.test_driven = TestDrivenImprovement(config)
        self.recursive_improvement = RecursiveImprovement(config)
        
    def _setup_logging(self):
        """Set up logging"""
        self.logger = logging.getLogger("WindowZot")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(self.config.get("logging", {}).get("file", "logs/gui.log"))
        formatter = logging.Formatter(self.config.get("logging", {}).get("format"))
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
    def _setup_window(self):
        """Set up the window"""
        try:
            # Initialize pygame first
            pygame.init()
            
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
            
            # Set up display
            width = window_config.get("width", 800)
            height = window_config.get("height", 600)
            title = window_config.get("title", "The Book of Shannon")
            
            # Create window
            self.screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption(title)
            
            # Set up timing
            self.clock = pygame.time.Clock()
            self.fps = window_config.get("fps", 60)
            
            self.logger.info("Window setup completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error setting up window: {str(e)}")
            # Try to recover
            try:
                pygame.quit()
                pygame.init()
                self.screen = pygame.display.set_mode((800, 600))
                pygame.display.set_caption("The Book of Shannon")
                self.clock = pygame.time.Clock()
                self.fps = 60
                self.logger.info("Recovered with default settings")
            except Exception as recovery_error:
                self.logger.error(f"Recovery failed: {str(recovery_error)}")
                raise

    def add_wave(self, wave: WaveZot):
        """Add a wave to the window"""
        self.waves.append(wave)
        
    def remove_wave(self, wave: WaveZot):
        """Remove a wave from the window"""
        if wave in self.waves:
            self.waves.remove(wave)
            
    def update(self):
        """Update window state"""
        for wave in self.waves:
            wave.update()
            
    def render(self):
        """Render the window"""
        self.screen.fill((0, 0, 0))
        for wave in self.waves:
            wave.render(self.screen)
        pygame.display.flip()
        
    def handle_events(self):
        """Handle window events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            for wave in self.waves:
                wave.handle_event(event)
        return True
        
    def run(self):
        """Run the window main loop"""
        try:
            # Ensure pygame is initialized
            if not pygame.get_init():
                pygame.init()
            
            running = True
            while running:
                running = self.handle_events()
                self.update()
                self.render()
                self.clock.tick(self.fps)
            
        except Exception as e:
            self.logger.error(f"Error in main loop: {str(e)}")
            # Try to fix the error using recursive improvement
            if self.recursive_improvement.start_improvement_loop(__file__):
                self.logger.info("Error fixed by recursive improvement")
                return self.run()  # Restart the loop
            raise
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Clean up resources"""
        for wave in self.waves:
            wave.cleanup()
        pygame.quit()
        self.test_driven.cleanup()
        self.recursive_improvement.cleanup()

class GodInterface:
    """Main GUI interface for wave visualization and interaction"""
    
    def __init__(self):
        self._setup_logging()
        # Initialize config manager - it handles its own initialization
        self.config = ConfigManager()
        self._initialize_pygame()
        self._setup_window()
        self._setup_wave()
        
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
            # Try to recover with default settings
            try:
                self.width = 800
                self.height = 600
                self.title = "The Book of Shannon"
                self.fps = 60
                self.screen = pygame.display.set_mode((self.width, self.height))
                pygame.display.set_caption(self.title)
                self.clock = pygame.time.Clock()
                self.logger.info("Recovered with default window settings")
            except Exception as recovery_error:
                self.logger.error(f"Window recovery failed: {str(recovery_error)}")
                raise
            
    def _setup_wave(self):
        """Set up the wave object"""
        try:
            wave_config = self.config.get("wave", {})
            if not wave_config:
                wave_config = {
                    "amplitude": 50,
                    "frequency": 0.1,
                    "phase": 0,
                    "interaction_decay": 0.95
                }
                self.config.set("wave", wave_config)
                
            self.wave = WaveZot(
                amplitude=wave_config.get("amplitude", 50),
                frequency=wave_config.get("frequency", 0.1),
                phase=wave_config.get("phase", 0),
                interaction_decay=wave_config.get("interaction_decay", 0.95)
            )
            self.logger.info("Wave object initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to set up wave: {str(e)}")
            # Try to recover with default settings
            try:
                self.wave = WaveZot(
                    amplitude=50,
                    frequency=0.1,
                    phase=0,
                    interaction_decay=0.95
                )
                self.logger.info("Recovered with default wave settings")
            except Exception as recovery_error:
                self.logger.error(f"Wave recovery failed: {str(recovery_error)}")
                raise
            
    def _handle_events(self) -> bool:
        """Handle pygame events"""
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_mouse_click(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self._handle_mouse_motion(event.pos)
            return True
        except Exception as e:
            self.logger.error(f"Error handling events: {str(e)}")
            return False
            
    def _handle_mouse_click(self, pos: Tuple[int, int]):
        """Handle mouse click events"""
        try:
            x, y = pos
            # Convert screen coordinates to wave coordinates
            wave_x = (x - self.width/2) / (self.width/2)
            wave_y = -(y - self.height/2) / (self.height/2)
            self.wave.interact(wave_x, wave_y)
            self.logger.debug(f"Mouse click at ({x}, {y}) -> wave coordinates ({wave_x}, {wave_y})")
        except Exception as e:
            self.logger.error(f"Error handling mouse click: {str(e)}")
            
    def _handle_mouse_motion(self, pos: Tuple[int, int]):
        """Handle mouse motion events"""
        try:
            x, y = pos
            # Convert screen coordinates to wave coordinates
            wave_x = (x - self.width/2) / (self.width/2)
            wave_y = -(y - self.height/2) / (self.height/2)
            self.wave.interact(wave_x, wave_y)
            self.logger.debug(f"Mouse motion at ({x}, {y}) -> wave coordinates ({wave_x}, {wave_y})")
        except Exception as e:
            self.logger.error(f"Error handling mouse motion: {str(e)}")
            
    def _draw_wave(self):
        """Draw the wave visualization"""
        try:
            # Clear screen
            self.screen.fill((0, 0, 0))
            
            # Generate wave points
            x = np.linspace(-1, 1, self.width)
            y = self.wave.get_wave(x)
            
            # Convert to screen coordinates
            screen_x = (x + 1) * self.width/2
            screen_y = (-y + 1) * self.height/2
            
            # Draw wave
            points = list(zip(screen_x, screen_y))
            if len(points) > 1:
                pygame.draw.lines(self.screen, (255, 255, 255), False, points, 2)
                
            pygame.display.flip()
        except Exception as e:
            self.logger.error(f"Error drawing wave: {str(e)}")
            
    def run(self):
        """Run the main loop"""
        try:
            # Ensure pygame is initialized
            if not pygame.get_init():
                pygame.init()
                
            running = True
            while running:
                running = self._handle_events()
                self._draw_wave()
                self.clock.tick(self.fps)
                
            self.logger.info("Main loop ended normally")
        except Exception as e:
            self.logger.error(f"Error in main loop: {str(e)}")
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Clean up resources"""
        try:
            if pygame.get_init():
                pygame.quit()
            self.logger.info("Pygame cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
            
if __name__ == "__main__":
    try:
        interface = GodInterface()
        interface.run()
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        raise 