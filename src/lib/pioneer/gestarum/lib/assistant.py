import json
import os
import time
from typing import Dict, List, Optional, Any

from openai import OpenAI
from openai.types.beta.threads import ThreadMessage

from src.lib.pioneer.gestarum.lib.assistant_configuration import AssistantConfiguration
from src.lib.pioneer.gestarum.lib.file_management import FileManagement
from src.lib.pioneer.gestarum.lib.thread import Thread

class Assistant:
    """Implements Assistant behavior with persistent state management."""

    def __init__(self, client: OpenAI, config: AssistantConfiguration):
        """Initialize assistant.
        
        Args:
            client: OpenAI client instance
            config: Assistant configuration
        """
        self.client = client
        self.config = config
        self.threads: Dict[str, Thread] = {}  # Tracks thread instances
        self.file_manager = FileManagement(client, storage_dir=self.config.file_dir)

        if self.config.assistant_id is None:
            self.create_assistant()
        else:
            self.load_assistant()

    def create_assistant(self) -> None:
        """Creates a new assistant and uploads files."""
        uploaded_files = self.file_manager.upload_files(self.config.files)

        assistant = self.client.beta.assistants.create(
            name=self.config.name,
            instructions=self.config.instructions,
            model=self.config.model,
            tools=self.config.tools,
            tool_resources=(
                {"file_search": {"file_ids": uploaded_files}} if uploaded_files else {}
            ),
        )

        self.config.assistant_id = assistant.id
        self.config.save()
        print(f"Created new assistant with ID {assistant.id}")

    def create_thread(self, name: str) -> str:
        """Creates a new thread, tracks it, and saves it persistently.
        
        Args:
            name: Human-readable name for the thread
            
        Returns:
            Thread ID
        """
        thread = self.client.beta.threads.create()
        thread_obj = Thread(
            thread_id=thread.id, name=name, storage_dir=self.config.threads_dir
        )
        self.threads[thread.id] = thread_obj
        thread_obj.save()
        return thread.id

    def send_message(self, thread_id: str, message: str) -> str:
        """Sends a message to a thread and retrieves the assistant's response.
        
        Args:
            thread_id: Thread ID
            message: Message content
            
        Returns:
            Assistant's response
        """
        if thread_id not in self.threads:
            raise ValueError(f"Thread ID {thread_id} not found.")

        self.threads[thread_id].add_message("user", message)
        
        self.client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=message
        )
        
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.config.assistant_id,
            tools=[{"type": "file_search"}],
        )
        
        while run.status in ["queued", "in_progress"]:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id, 
                run_id=run.id
            )
            time.sleep(1)
            
        print(f"Run completed with status: {run.status}")
        
        if run.status == "completed":
            messages = self.client.beta.threads.messages.list(
                thread_id=thread_id,
                order="desc",
                limit=1,
            )
            
            if len(messages.data) > 0 and messages.data[0].role == "assistant":
                message = messages.data[0]
                if message.content and len(message.content) > 0:
                    content = message.content[0].text.value
                    self.threads[thread_id].add_message("assistant", content)
                    self.threads[thread_id].save()
                    return content
                
        return f"Error: Run completed with status {run.status}"

    def get_state(self) -> Dict[str, Any]:
        """Retrieves assistant state, including stored threads and metadata."""
        return {
            "id": self.config.assistant_id,
            "name": self.config.name,
            "instructions": self.config.instructions,
            "model": self.config.model,
            "tools": self.config.tools,
            "files": self.file_manager.list_uploaded_files(),
            "threads": {
                thread_id: thread.name for thread_id, thread in self.threads.items()
            },
        }

    def load_assistant(self) -> None:
        """Loads an assistant's state from JSON, including threads."""
        try:
            self.client.beta.assistants.retrieve(self.config.assistant_id)
        except Exception as e:
            print(f"Error retrieving assistant: {e}")
            print("Creating a new assistant instead")
            self.config.assistant_id = None
            self.create_assistant()
            return
            
        threads_path = os.path.join(self.config.threads_dir)
        if os.path.exists(threads_path):
            for filename in os.listdir(threads_path):
                if filename.endswith(".json"):
                    thread_id = filename.split(".")[0]
                    thread = Thread(
                        thread_id=thread_id,
                        name="",  # Will be loaded from file
                        storage_dir=self.config.threads_dir,
                    ).load()
                    self.threads[thread_id] = thread
