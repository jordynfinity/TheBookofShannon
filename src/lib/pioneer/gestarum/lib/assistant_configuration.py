import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

class AssistantConfiguration:
    """Stores and persists assistant configuration data."""

    def __init__(
        self,
        name: str,
        instructions: str,
        model: str = "gpt-4o",
        tools: Optional[List[Dict[str, Any]]] = None,
        files: Optional[List[str]] = None,
        assistant_id: Optional[str] = None,
        storage_dir: str = "assistants",
        threads_dir: str = "threads",
        file_dir: str = "files",
    ):
        """Initialize assistant configuration.
        
        Args:
            name: Name of the assistant
            instructions: Behavioral instructions for the assistant
            model: OpenAI model to use
            tools: Tools the assistant can use
            files: Files to attach to the assistant
            assistant_id: ID of existing assistant (None for new assistant)
            storage_dir: Directory to store assistant configurations
            threads_dir: Directory to store thread data
            file_dir: Directory to store file metadata
        """
        self.name = name
        self.instructions = instructions
        self.model = model
        self.tools = tools or []
        self.files = files or []
        self.assistant_id = assistant_id  # None means a new assistant needs to be created
        self.storage_dir = storage_dir
        self.threads_dir = threads_dir
        self.file_dir = file_dir
        
        os.makedirs(self.storage_dir, exist_ok=True)
        os.makedirs(self.threads_dir, exist_ok=True)
        os.makedirs(self.file_dir, exist_ok=True)

    def get_assistant_id(self) -> Optional[str]:
        """Returns the assistant ID if it exists."""
        return self.assistant_id

    def save(self) -> None:
        """Saves the assistant configuration to a JSON file."""
        path = os.path.join(self.storage_dir, f"{self.assistant_id or self.name}.json")
        with open(path, "w") as f:
            json.dump(self.to_json(), f, indent=4)

    def load(self, assistant_id: str) -> None:
        """Loads the assistant configuration from a JSON file."""
        path = os.path.join(self.storage_dir, f"{assistant_id}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                self.name = data["name"]
                self.instructions = data["instructions"]
                self.model = data["model"]
                self.tools = data["tools"]
                self.files = data["files"]
                self.assistant_id = assistant_id

    def to_json(self) -> Dict[str, Any]:
        """Returns a JSON-serializable representation of the assistant configuration."""
        return {
            "name": self.name,
            "instructions": self.instructions,
            "model": self.model,
            "tools": self.tools,
            "files": self.files,
            "assistant_id": self.assistant_id,
        }
