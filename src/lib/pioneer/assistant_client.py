"""
A client for interacting with OpenAI's Assistant API, providing persistent thread management 
and configuration loading.
"""

import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from src.lib.pioneer.gestarum.lib.assistant_manager import AssistantManager

load_dotenv()

class AssistantClient:
    """
    A ChatGPT client that loads an assistant by name and maintains a persistent thread.

    This client handles:
    - Loading OpenAI API credentials from environment variables
    - Managing assistant configurations from a specified directory
    - Creating and maintaining persistent chat threads
    - Sending messages and receiving responses
    """

    def __init__(self, assistant_name: str, config_directory: str = "src/lib/pioneer/config"):
        """Initialize the assistant client.
        
        Args:
            assistant_name: Name of the assistant configuration to load
            config_directory: Path to the directory containing assistant configurations
        
        Raises:
            ValueError: If OPENAI_API_KEY is not set or the assistant is not found
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
            
        self.client = OpenAI(api_key=api_key)
        
        os.makedirs(config_directory, exist_ok=True)
        
        self.manager = AssistantManager(self.client, config_directory=config_directory)
        self.assistant = self.manager.assistant_index.get(assistant_name)
        
        if not self.assistant:
            print(f"Assistant '{assistant_name}' not found, creating it")
            config_data = {
                "name": assistant_name,
                "instructions": "You are an assistant specializing in Claude Shannon's information theory. Help users understand Shannon's concepts and theories.",
                "model": "gpt-4o",
                "tools": [{"type": "file_search"}],
                "files": [],
            }
            assistant_id = self.manager.create_assistant(config_data)
            self.assistant = self.manager.get_assistant(assistant_id)

        self.thread_name = "Default Thread"
        self.thread_id = None
        
        for thread_id, thread in self.assistant.threads.items():
            if thread.name == self.thread_name:
                self.thread_id = thread_id
                print(f"Thread '{self.thread_name}' found with ID: {thread_id}")
                break
        
        if not self.thread_id:
            self.thread_id = self.assistant.create_thread(name=self.thread_name)
            print(f"Created new thread with ID: {self.thread_id}")
    
    def chat(self, message: str) -> str:
        """
        Sends a message to the assistant and returns the response.
        
        Args:
            message: The message to send to the assistant
            
        Returns:
            The assistant's response
        """
        return self.assistant.send_message(self.thread_id, message)
