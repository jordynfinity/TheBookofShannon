"""
A client for interacting with OpenAI's Assistant API with McTavish's Crochet thread model,
providing nonlinear thread management and configuration loading.
"""

import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from src.lib.pioneer.gestarum.lib.assistant_manager import AssistantManager
from src.lib.pioneer.gestarum.lib.crochet_thread import CrochetThread

load_dotenv()

class CrochetAssistantClient:
    """
    A ChatGPT client that loads an assistant by name and maintains a nonlinear thread.

    This client handles:
    - Loading OpenAI API credentials from environment variables
    - Managing assistant configurations from a specified directory
    - Creating and maintaining nonlinear Crochet threads
    - Sending messages and receiving responses from multiple character perspectives
    """

    def __init__(
        self, 
        assistant_name: str, 
        config_directory: str = "src/lib/pioneer/config",
        character_ids: Optional[List[str]] = None,
    ):
        """Initialize the assistant client.
        
        Args:
            assistant_name: Name of the assistant configuration to load
            config_directory: Path to the directory containing assistant configurations
            character_ids: Optional list of character IDs to use for responses
        
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

        self.character_ids = character_ids or ["shannon_default"]
        
        self.thread_name = "Default Thread"
        self.thread_id = None
        self.crochet_threads: Dict[str, CrochetThread] = {}
        
        for thread_id, thread in self.assistant.threads.items():
            if thread.name == self.thread_name:
                self.thread_id = thread_id
                print(f"Thread '{self.thread_name}' found with ID: {thread_id}")
                
                crochet_thread = CrochetThread(
                    thread_id=thread_id,
                    name=self.thread_name,
                    storage_dir=self.assistant.config.threads_dir,
                )
                
                for message in thread.messages:
                    character_id = None
                    if message["role"] == "assistant":
                        character_id = self.character_ids[0]  # Default to first character
                    
                    crochet_thread.add_message(
                        role=message["role"],
                        content=message["content"],
                        character_id=character_id,
                    )
                
                self.crochet_threads[thread_id] = crochet_thread
                break
        
        if not self.thread_id:
            self.thread_id = self.assistant.create_thread(name=self.thread_name)
            print(f"Created new thread with ID: {self.thread_id}")
            
            crochet_thread = CrochetThread(
                thread_id=self.thread_id,
                name=self.thread_name,
                storage_dir=self.assistant.config.threads_dir,
            )
            self.crochet_threads[self.thread_id] = crochet_thread
    
    def chat(self, message: str, character_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Sends a message to the assistant and returns responses from all characters.
        
        Args:
            message: The message to send to the assistant
            character_id: Optional character ID to filter responses
            
        Returns:
            Dictionary with character IDs as keys and responses as values
        """
        self.crochet_threads[self.thread_id].add_message(
            role="user",
            content=message,
        )
        
        response = self.assistant.send_message(self.thread_id, message)
        
        responses = {}
        
        for char_id in self.character_ids:
            if character_id and char_id != character_id:
                continue
                
            node_id = self.crochet_threads[self.thread_id].add_character_response(
                character_id=char_id,
                content=response,
            )
            
            responses[char_id] = {
                "content": response,
                "node_id": node_id,
            }
        
        self.crochet_threads[self.thread_id].save()
        
        return responses
    
    def get_conversation_history(self, character_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Gets the conversation history, optionally filtered by character.
        
        Args:
            character_id: Optional character ID to filter responses
            
        Returns:
            List of messages in chronological order
        """
        if self.thread_id not in self.crochet_threads:
            return []
            
        messages = self.crochet_threads[self.thread_id].get_linear_conversation()
        
        if character_id:
            messages = [
                msg for msg in messages
                if msg["role"] != "assistant" or msg.get("character_id") == character_id
            ]
            
        return messages
