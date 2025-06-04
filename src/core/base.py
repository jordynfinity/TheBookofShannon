from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class State:
    """Base class for component state"""
    last_update: datetime
    is_active: bool
    metadata: Dict[str, Any]

class BaseComponent(ABC):
    """Base class for all components"""
    def __init__(self):
        self.state = State(
            last_update=datetime.now(),
            is_active=False,
            metadata={}
        )
        
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the component"""
        pass
        
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources"""
        pass
        
    @abstractmethod
    def update(self) -> None:
        """Update component state"""
        pass
        
    def get_state(self) -> State:
        """Get current component state"""
        return self.state
        
    def set_state(self, new_state: Dict[str, Any]) -> None:
        """Update component state"""
        self.state.metadata.update(new_state)
        self.state.last_update = datetime.now()

class ResourceAware(ABC):
    """Interface for resource-aware components"""
    @abstractmethod
    def check_resources(self) -> Dict[str, float]:
        """Check resource usage"""
        pass
        
    @abstractmethod
    def optimize_resources(self) -> None:
        """Optimize resource usage"""
        pass

class SelfImproving(ABC):
    """Interface for self-improving components"""
    @abstractmethod
    def generate_improvements(self) -> List[Dict[str, Any]]:
        """Generate improvement suggestions"""
        pass
        
    @abstractmethod
    def apply_improvement(self, improvement: Dict[str, Any]) -> bool:
        """Apply an improvement"""
        pass
        
    @abstractmethod
    def validate_improvement(self, improvement: Dict[str, Any]) -> bool:
        """Validate an improvement"""
        pass

class Configurable(ABC):
    """Interface for configurable components"""
    @abstractmethod
    def load_config(self, config: Dict[str, Any]) -> None:
        """Load configuration"""
        pass
        
    @abstractmethod
    def save_config(self) -> Dict[str, Any]:
        """Save configuration"""
        pass
        
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration"""
        pass 