import numpy as np
import logging
from typing import Optional, List, Tuple

class WaveZot:
    """Wave generation and interaction class"""
    
    def __init__(self, 
                 amplitude: float = 50.0,
                 frequency: float = 0.1,
                 phase: float = 0.0,
                 interaction_decay: float = 0.95):
        """Initialize wave parameters"""
        self._setup_logging()
        self.amplitude = amplitude
        self.frequency = frequency
        self.phase = phase
        self.interaction_decay = interaction_decay
        self.interactions: List[Tuple[float, float, float]] = []  # (x, y, time)
        self.logger.info("WaveZot initialized with parameters: "
                        f"amplitude={amplitude}, frequency={frequency}, "
                        f"phase={phase}, interaction_decay={interaction_decay}")
        
    def _setup_logging(self):
        """Set up logging"""
        self.logger = logging.getLogger("WaveZot")
        self.logger.setLevel(logging.DEBUG)
        
    def get_wave(self, x: np.ndarray) -> np.ndarray:
        """Generate wave values for given x coordinates"""
        try:
            # Base wave
            y = self.amplitude * np.sin(2 * np.pi * self.frequency * x + self.phase)
            
            # Add interaction effects
            for ix, iy, itime in self.interactions:
                # Calculate distance from interaction point
                dx = x - ix
                # Add decaying interaction effect
                y += iy * np.exp(-self.interaction_decay * np.abs(dx))
                
            return y
        except Exception as e:
            self.logger.error(f"Error generating wave: {str(e)}")
            return np.zeros_like(x)
            
    def interact(self, x: float, y: float):
        """Add an interaction point"""
        try:
            self.interactions.append((x, y, 0.0))  # Add new interaction
            # Remove old interactions that have decayed too much
            self.interactions = [(ix, iy, itime) for ix, iy, itime in self.interactions
                               if abs(iy) > 0.01]
            self.logger.debug(f"Added interaction at ({x}, {y})")
        except Exception as e:
            self.logger.error(f"Error adding interaction: {str(e)}")
            
    def update(self, dt: float):
        """Update wave state"""
        try:
            # Update interaction times
            self.interactions = [(ix, iy, itime + dt) for ix, iy, itime in self.interactions]
            # Remove old interactions
            self.interactions = [(ix, iy, itime) for ix, iy, itime in self.interactions
                               if itime < 5.0]  # Keep interactions for 5 seconds
        except Exception as e:
            self.logger.error(f"Error updating wave: {str(e)}")
            
    def get_audio(self, sample_rate: int = 44100, duration: float = 1.0) -> np.ndarray:
        """Generate audio samples from wave"""
        try:
            t = np.linspace(0, duration, int(sample_rate * duration))
            x = np.linspace(-1, 1, len(t))
            y = self.get_wave(x)
            # Normalize audio
            y = y / np.max(np.abs(y))
            return y
        except Exception as e:
            self.logger.error(f"Error generating audio: {str(e)}")
            return np.zeros(int(sample_rate * duration)) 