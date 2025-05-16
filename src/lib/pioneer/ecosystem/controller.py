"""
Main controller for the prompt-driven ecosystem.

This module implements the central controller that:
- Initializes and coordinates all ecosystem components
- Handles prompt detection and processing
- Manages the lifecycle of conversations and ideas
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

from src.lib.pioneer.ecosystem.folder_watcher import FolderWatcher
from src.lib.pioneer.ecosystem.conversation import ConversationManager
from src.lib.pioneer.ecosystem.personality import PersonalityManager
from src.lib.pioneer.ecosystem.idea_recorder import IdeaRecorder


class EcosystemController:
    """Controls the prompt-driven ecosystem."""
    
    def __init__(
        self,
        prompt_dirs: List[str] = ["prompts"],
        docs_dir: str = "docs/obsidian/The Book of Shannon",
        assistant_name: str = "shannon_assistant",
        config_directory: str = "src/lib/pioneer/config",
        conversation_dir: str = "conversations",
        personality_dir: str = "personalities",
        ideas_subdir: str = "Generated Ideas",
        prompt_extension: str = ".prompt.json",
    ):
        """Initialize ecosystem controller.
        
        Args:
            prompt_dirs: List of directories to watch for prompts
            docs_dir: Path to the documentation directory
            assistant_name: Name of the assistant configuration to load
            config_directory: Path to the directory containing assistant configurations
            conversation_dir: Directory to store conversation data
            personality_dir: Directory to store personality data
            ideas_subdir: Subdirectory for generated ideas
            prompt_extension: File extension for prompt files
        """
        self.prompt_dirs = prompt_dirs
        self.docs_dir = docs_dir
        self.assistant_name = assistant_name
        self.config_directory = config_directory
        self.conversation_dir = conversation_dir
        self.personality_dir = personality_dir
        self.ideas_subdir = ideas_subdir
        self.prompt_extension = prompt_extension
        
        for prompt_dir in self.prompt_dirs:
            os.makedirs(prompt_dir, exist_ok=True)
            
        self.conversation_manager = ConversationManager(
            assistant_name=self.assistant_name,
            config_directory=self.config_directory,
            conversation_dir=self.conversation_dir,
            personality_dir=self.personality_dir,
        )
        
        self.idea_recorder = IdeaRecorder(
            docs_dir=self.docs_dir,
            ideas_subdir=self.ideas_subdir,
        )
        
        self.folder_watcher = FolderWatcher(
            watch_dirs=self.prompt_dirs,
            prompt_callback=self.handle_prompt,
            prompt_extension=self.prompt_extension,
        )
        
        self.active_conversations: Dict[str, Dict[str, Any]] = {}
        
    def handle_prompt(self, file_path: str, prompt_data: Dict[str, Any]) -> None:
        """Handle a detected prompt.
        
        Args:
            file_path: Path to the prompt file
            prompt_data: Prompt data
        """
        try:
            print(f"Processing prompt from {file_path}: {prompt_data.get('prompt', '')[:50]}...")
            
            conversation_id = self.conversation_manager.create_conversation(prompt_data)
            self.active_conversations[conversation_id] = {
                "file_path": file_path,
                "prompt_data": prompt_data,
                "created_at": time.time(),
            }
            
            conversation = self.conversation_manager.get_conversation(conversation_id)
            
            recorded_files = self.idea_recorder.process_conversation(conversation)
            
            self._update_prompt_file(file_path, {
                "conversation_id": conversation_id,
                "recorded_ideas": recorded_files,
                "processed_at": time.time(),
            })
            
            print(f"Processed prompt and recorded {len(recorded_files)} ideas")
        except Exception as e:
            print(f"Error handling prompt {file_path}: {e}")
            
    def _update_prompt_file(self, file_path: str, update_data: Dict[str, Any]) -> None:
        """Update a prompt file with processing results.
        
        Args:
            file_path: Path to the prompt file
            update_data: Data to add to the prompt file
        """
        try:
            with open(file_path, "r") as f:
                prompt_data = json.load(f)
                
            prompt_data.update(update_data)
            
            with open(file_path, "w") as f:
                json.dump(prompt_data, f, indent=4)
        except Exception as e:
            print(f"Error updating prompt file {file_path}: {e}")
            
    def start(self) -> None:
        """Start the ecosystem controller."""
        print("Starting prompt-driven ecosystem controller...")
        
        self.folder_watcher.start()
        
        self.folder_watcher.scan_existing_prompts()
        
        print("Ecosystem controller started")
        
    def stop(self) -> None:
        """Stop the ecosystem controller."""
        print("Stopping prompt-driven ecosystem controller...")
        
        self.folder_watcher.stop()
        
        print("Ecosystem controller stopped")
