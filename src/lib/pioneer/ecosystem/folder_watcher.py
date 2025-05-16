"""
Folder watching interface that monitors directories for prompt files.

This module implements a watching system that:
- Monitors directories for new or modified files
- Detects prompt files based on file patterns
- Triggers conversations between agents
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent

class PromptFileHandler(FileSystemEventHandler):
    """Handles file system events for prompt files."""
    
    def __init__(
        self, 
        prompt_callback: Callable[[str, Dict[str, Any]], None],
        prompt_extension: str = ".prompt.json",
    ):
        """Initialize prompt file handler.
        
        Args:
            prompt_callback: Callback function to handle detected prompts
            prompt_extension: File extension for prompt files
        """
        self.prompt_callback = prompt_callback
        self.prompt_extension = prompt_extension
        self.processed_files: Dict[str, float] = {}  # Path -> timestamp
        
    def on_created(self, event):
        """Handle file created event."""
        if not isinstance(event, FileCreatedEvent):
            return
            
        self._process_file(event.src_path)
            
    def on_modified(self, event):
        """Handle file modified event."""
        if not isinstance(event, FileModifiedEvent):
            return
            
        self._process_file(event.src_path)
            
    def _process_file(self, file_path: str) -> None:
        """Process a potential prompt file.
        
        Args:
            file_path: Path to the file to process
        """
        if not file_path.endswith(self.prompt_extension):
            return
            
        current_time = time.time()
        if file_path in self.processed_files:
            if current_time - self.processed_files[file_path] < 5:  # 5 second debounce
                return
                
        try:
            with open(file_path, "r") as f:
                prompt_data = json.load(f)
                
            self.processed_files[file_path] = current_time
            
            prompt_text = prompt_data.get("prompt", "")
            if prompt_text:
                self.prompt_callback(file_path, prompt_data)
                print(f"Processed prompt from {file_path}")
        except Exception as e:
            print(f"Error processing prompt file {file_path}: {e}")


class FolderWatcher:
    """Watches folders for prompt files."""
    
    def __init__(
        self, 
        watch_dirs: List[str],
        prompt_callback: Callable[[str, Dict[str, Any]], None],
        prompt_extension: str = ".prompt.json",
    ):
        """Initialize folder watcher.
        
        Args:
            watch_dirs: List of directories to watch
            prompt_callback: Callback function to handle detected prompts
            prompt_extension: File extension for prompt files
        """
        self.watch_dirs = [Path(d).absolute() for d in watch_dirs]
        self.observer = Observer()
        self.handler = PromptFileHandler(prompt_callback, prompt_extension)
        
        for watch_dir in self.watch_dirs:
            if not watch_dir.exists():
                os.makedirs(watch_dir, exist_ok=True)
            self.observer.schedule(self.handler, str(watch_dir), recursive=True)
            
        self.running = False
        
    def start(self) -> None:
        """Start watching folders."""
        if self.running:
            return
            
        self.observer.start()
        self.running = True
        print(f"Started watching directories: {', '.join(str(d) for d in self.watch_dirs)}")
        
    def stop(self) -> None:
        """Stop watching folders."""
        if not self.running:
            return
            
        self.observer.stop()
        self.observer.join()
        self.running = False
        print("Stopped watching directories")
        
    def scan_existing_prompts(self) -> None:
        """Scan existing prompt files in watched directories."""
        for watch_dir in self.watch_dirs:
            for prompt_file in watch_dir.glob(f"**/*{self.handler.prompt_extension}"):
                self.handler._process_file(str(prompt_file))
