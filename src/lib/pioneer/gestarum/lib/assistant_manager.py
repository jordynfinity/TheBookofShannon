import os
import json
from typing import Dict, List, Optional, Tuple, Any

from openai import OpenAI

from src.lib.pioneer.gestarum.lib.assistant_configuration import AssistantConfiguration
from src.lib.pioneer.gestarum.lib.assistant import Assistant

class AssistantManager:
    """Manages multiple assistants from stored configurations."""

    def __init__(self, client: OpenAI, config_directory: str = "assistants"):
        """Initialize assistant manager.
        
        Args:
            client: OpenAI client instance
            config_directory: Directory containing assistant configurations
        """
        self.client = client
        self.config_directory = config_directory
        os.makedirs(self.config_directory, exist_ok=True)
        self.assistants: Dict[str, Assistant] = {}

        self.load_assistants()

    def list_assistants(self) -> List[Tuple[str, str]]:
        """Returns a list of assistant names and IDs."""
        return [
            (assistant.config.name, assistant_id)
            for assistant_id, assistant in self.assistants.items()
        ]

    @property
    def assistant_index(self) -> Dict[str, Assistant]:
        """Returns a dictionary of assistants indexed by name."""
        return {
            assistant_name: self.get_assistant(assistant_id)
            for assistant_name, assistant_id in self.list_assistants()
        }

    def load_assistants(self) -> None:
        """Loads all assistant configurations from the config directory."""
        for filename in os.listdir(self.config_directory):
            if filename.endswith(".json"):
                path = os.path.join(self.config_directory, filename)
                try:
                    with open(path, "r") as f:
                        config_data = json.load(f)
                        assistant_config = AssistantConfiguration(
                            name=config_data["name"],
                            instructions=config_data["instructions"],
                            model=config_data["model"],
                            tools=config_data["tools"],
                            files=config_data["files"],
                            assistant_id=config_data["assistant_id"],
                            storage_dir=self.config_directory,
                        )
                        assistant = Assistant(self.client, assistant_config)
                        self.assistants[assistant.config.assistant_id] = assistant
                except Exception as e:
                    print(f"Error loading assistant config {path}: {e}")

    def save_assistants(self) -> None:
        """Saves the state of all managed assistants."""
        for assistant in self.assistants.values():
            assistant.config.save()

    def create_assistant(self, config_data: Dict[str, Any]) -> str:
        """Creates a new assistant from a configuration dictionary.
        
        Args:
            config_data: Assistant configuration data
            
        Returns:
            Assistant ID
        """
        assistant_config = AssistantConfiguration(
            name=config_data["name"],
            instructions=config_data["instructions"],
            model=config_data.get("model", "gpt-4o"),
            tools=config_data.get("tools", []),
            files=config_data.get("files", []),
            storage_dir=self.config_directory,
        )
        assistant = Assistant(self.client, assistant_config)
        self.assistants[assistant.config.assistant_id] = assistant
        assistant.config.save()
        return assistant.config.assistant_id

    def get_assistant(self, assistant_id: str) -> Optional[Assistant]:
        """Retrieves an assistant by its ID.
        
        Args:
            assistant_id: Assistant ID
            
        Returns:
            Assistant object or None if not found
        """
        return self.assistants.get(assistant_id)
