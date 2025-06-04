from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass
import time
import json
import os

@dataclass
class Improvement:
    """Represents a single improvement"""
    type: str
    description: str
    impact: float
    dependencies: List[str]
    timestamp: float
    status: str = "pending"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": self.type,
            "description": self.description,
            "impact": self.impact,
            "dependencies": self.dependencies,
            "timestamp": self.timestamp,
            "status": self.status
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Improvement':
        """Create from dictionary"""
        return cls(
            type=data["type"],
            description=data["description"],
            impact=data["impact"],
            dependencies=data["dependencies"],
            timestamp=data["timestamp"],
            status=data.get("status", "pending")
        )

class ImprovementChain:
    """Manages a chain of improvements"""
    def __init__(self):
        self.improvements: List[Improvement] = []
        self.logger = logging.getLogger("ImprovementChain")
        self._setup_logging()
        self._load_improvements()
        
    def _setup_logging(self):
        """Setup logging"""
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
    def _load_improvements(self):
        """Load improvements from file"""
        try:
            if os.path.exists("improvements.json"):
                with open("improvements.json", "r") as f:
                    data = json.load(f)
                    self.improvements = [Improvement.from_dict(item) for item in data]
        except Exception as e:
            self.logger.error(f"Error loading improvements: {e}")
            
    def _save_improvements(self):
        """Save improvements to file"""
        try:
            data = [imp.to_dict() for imp in self.improvements]
            with open("improvements.json", "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving improvements: {e}")
            
    def add_improvement(self, improvement: Improvement) -> None:
        """Add an improvement to the chain"""
        self.improvements.append(improvement)
        self._save_improvements()
        
    def remove_improvement(self, index: int) -> None:
        """Remove an improvement from the chain"""
        if 0 <= index < len(self.improvements):
            self.improvements.pop(index)
            self._save_improvements()
            
    def get_next_improvement(self) -> Optional[Improvement]:
        """Get the next improvement to apply"""
        for imp in self.improvements:
            if imp.status == "pending":
                # Check if dependencies are satisfied
                if all(dep in [i.type for i in self.improvements if i.status == "completed"]
                      for dep in imp.dependencies):
                    return imp
        return None
        
    def mark_completed(self, improvement: Improvement) -> None:
        """Mark an improvement as completed"""
        for imp in self.improvements:
            if (imp.type == improvement.type and 
                imp.description == improvement.description and 
                imp.timestamp == improvement.timestamp):
                imp.status = "completed"
                self._save_improvements()
                break
                
    def get_metrics(self) -> Dict[str, Any]:
        """Get chain metrics"""
        total = len(self.improvements)
        completed = sum(1 for imp in self.improvements if imp.status == "completed")
        pending = sum(1 for imp in self.improvements if imp.status == "pending")
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "completion_rate": completed / total if total > 0 else 0
        }
        
    def cleanup(self):
        """Clean up the chain"""
        self._save_improvements() 