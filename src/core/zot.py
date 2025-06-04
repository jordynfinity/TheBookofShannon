from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
from dataclasses import dataclass
import time

@dataclass
class ZotState:
    """State for Zot components"""
    is_active: bool = True
    is_visible: bool = True
    last_update: float = 0.0
    metrics: Dict[str, float] = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}

class Zot(ABC):
    """Base class for all Zots"""
    def __init__(self, name: str):
        self.name = name
        self.state = ZotState()
        self.logger = logging.getLogger(f"Zot.{name}")
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging for Zot"""
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
    @abstractmethod
    def update(self) -> None:
        """Update Zot state"""
        pass
        
    def initialize(self) -> None:
        """Initialize Zot"""
        self.state.last_update = time.time()
        self.logger.info(f"Initialized {self.name}")
        
    def cleanup(self) -> None:
        """Clean up Zot"""
        self.state.is_active = False
        self.logger.info(f"Cleaned up {self.name}")

class FirstZot(Zot):
    """First level Zot with basic functionality"""
    def __init__(self, name: str):
        super().__init__(name)
        self.improvements: List[Dict[str, Any]] = []
        
    def update(self) -> None:
        """Update FirstZot state"""
        self.state.last_update = time.time()
        self._check_improvements()
        
    def _check_improvements(self) -> None:
        """Check for possible improvements"""
        if not self.improvements:
            return
            
        for improvement in self.improvements:
            if self._validate_improvement(improvement):
                self._apply_improvement(improvement)
                
    def _validate_improvement(self, improvement: Dict[str, Any]) -> bool:
        """Validate an improvement"""
        try:
            required_fields = ['type', 'description', 'impact']
            return all(field in improvement for field in required_fields)
        except Exception as e:
            self.logger.error(f"Error validating improvement: {e}")
            return False
            
    def _apply_improvement(self, improvement: Dict[str, Any]) -> None:
        """Apply an improvement"""
        try:
            self.logger.info(f"Applying improvement: {improvement['description']}")
            # Implementation specific to improvement type
        except Exception as e:
            self.logger.error(f"Error applying improvement: {e}")

class SecondZot(FirstZot):
    """Second level Zot with advanced functionality"""
    def __init__(self, name: str):
        super().__init__(name)
        self.dependencies: Dict[str, Zot] = {}
        
    def add_dependency(self, zot: Zot) -> None:
        """Add a dependency"""
        self.dependencies[zot.name] = zot
        
    def remove_dependency(self, name: str) -> None:
        """Remove a dependency"""
        if name in self.dependencies:
            del self.dependencies[name]
            
    def update(self) -> None:
        """Update SecondZot state"""
        # Update dependencies first
        for zot in self.dependencies.values():
            zot.update()
            
        # Then update self
        super().update()
        
    def cleanup(self) -> None:
        """Clean up SecondZot"""
        # Clean up dependencies first
        for zot in self.dependencies.values():
            zot.cleanup()
            
        # Then clean up self
        super().cleanup() 