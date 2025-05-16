import json
import os
from typing import List, Dict, Any
from pathlib import Path

from openai import OpenAI

class FileManagement:
    """Handles file uploads and ensures compliance with OpenAI's 20-file limit."""

    def __init__(self, client: OpenAI, storage_dir: str = "files"):
        """Initialize file management.
        
        Args:
            client: OpenAI client instance
            storage_dir: Directory to store file metadata
        """
        self.client = client
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self.uploaded_files = self.load_files()

    def upload_files(self, file_paths: List[str]) -> List[str]:
        """Uploads files while managing OpenAI's file constraints.
        
        Args:
            file_paths: List of paths to files to upload
            
        Returns:
            List of uploaded file IDs
        """
        while len(self.uploaded_files) + len(file_paths) > 20:
            self.delete_oldest_files(keep_latest=20 - len(file_paths))

        new_files = []
        for file_path in file_paths:
            if not os.path.exists(file_path):
                print(f"Warning: File {file_path} does not exist, skipping")
                continue
                
            try:
                file = self.client.files.create(
                    file=open(file_path, "rb"), purpose="assistants"
                )
                new_files.append(file.id)
                print(f"Uploaded file {file_path} with ID {file.id}")
            except Exception as e:
                print(f"Error uploading file {file_path}: {e}")

        self.uploaded_files.extend(new_files)
        self.save_files()
        return new_files

    def delete_oldest_files(self, keep_latest: int = 20) -> None:
        """Deletes the oldest files to ensure compliance with OpenAI's file limit.
        
        Args:
            keep_latest: Number of newest files to keep
        """
        while len(self.uploaded_files) > keep_latest:
            oldest_file = self.uploaded_files.pop(0)
            try:
                self.client.files.delete(oldest_file)
                print(f"Deleted file with ID {oldest_file}")
            except Exception as e:
                print(f"Error deleting file with ID {oldest_file}: {e}")

        self.save_files()

    def list_uploaded_files(self) -> List[str]:
        """Returns a list of uploaded file IDs."""
        return self.uploaded_files

    def save_files(self) -> None:
        """Saves the list of uploaded files to a JSON file."""
        path = os.path.join(self.storage_dir, "uploaded_files.json")
        with open(path, "w") as f:
            json.dump(self.uploaded_files, f, indent=4)

    def load_files(self) -> List[str]:
        """Loads the list of uploaded files from a JSON file."""
        path = os.path.join(self.storage_dir, "uploaded_files.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return []
