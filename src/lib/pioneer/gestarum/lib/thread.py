import json
import os
from typing import Dict, List, Optional, Any

class Thread:
    """Manages a persistent thread for an assistant conversation."""

    def __init__(self, thread_id: str, name: str, storage_dir: str = "threads"):
        """Initialize thread.
        
        Args:
            thread_id: OpenAI thread ID
            name: Human-readable name for the thread
            storage_dir: Directory to store thread data
        """
        self.thread_id = thread_id
        self.name = name
        self.storage_dir = storage_dir
        self.messages: List[Dict[str, str]] = []
        os.makedirs(self.storage_dir, exist_ok=True)

    def add_message(self, role: str, content: str) -> None:
        """Adds a message to the thread history.
        
        Args:
            role: Message role (user or assistant)
            content: Message content
        """
        self.messages.append({
            "role": role,
            "content": content,
        })

    def save(self) -> None:
        """Saves the thread to a JSON file."""
        path = os.path.join(self.storage_dir, f"{self.thread_id}.json")
        with open(path, "w") as f:
            json.dump({
                "thread_id": self.thread_id,
                "name": self.name,
                "messages": self.messages,
            }, f, indent=4)
            
    def load(self) -> 'Thread':
        """Loads the thread from a JSON file."""
        path = os.path.join(self.storage_dir, f"{self.thread_id}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                self.name = data["name"]
                self.messages = data["messages"]
        return self
