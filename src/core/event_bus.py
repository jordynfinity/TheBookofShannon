import logging
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
import time

@dataclass
class Event:
    """Represents an event in the system"""
    type: str
    data: Any
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class EventBus:
    """Central event bus for component communication"""
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Event] = []
        self.max_history = 1000
        self.logger = logging.getLogger("EventBus")
        self.logger.setLevel(logging.DEBUG)
        self._setup_logging()
        
    def _setup_logging(self):
        """Set up logging configuration"""
        log_dir = "logs"
        import os
        os.makedirs(log_dir, exist_ok=True)
        
        handler = logging.FileHandler(f"{log_dir}/event_bus.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        self.logger.debug(f"Subscribed to event type: {event_type}")
        
    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from an event type"""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)
            self.logger.debug(f"Unsubscribed from event type: {event_type}")
            
    def publish(self, event_type: str, data: Any = None):
        """Publish an event to all subscribers"""
        event = Event(type=event_type, data=data)
        self.event_history.append(event)
        
        # Trim history if needed
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
            
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(event.data)
                except Exception as e:
                    self.logger.error(f"Error in event handler for {event_type}: {str(e)}")
                    
        self.logger.debug(f"Published event: {event_type}")
        
    def get_event_history(self, event_type: str = None, limit: int = None) -> List[Event]:
        """Get event history, optionally filtered by type"""
        events = self.event_history
        if event_type:
            events = [e for e in events if e.type == event_type]
        if limit:
            events = events[-limit:]
        return events
        
    def clear_history(self):
        """Clear event history"""
        self.event_history.clear()
        self.logger.debug("Event history cleared")
        
    def get_subscriber_count(self, event_type: str = None) -> int:
        """Get number of subscribers for an event type or total"""
        if event_type:
            return len(self.subscribers.get(event_type, []))
        return sum(len(subscribers) for subscribers in self.subscribers.values()) 