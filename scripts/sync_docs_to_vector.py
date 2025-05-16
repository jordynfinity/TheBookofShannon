#!/usr/bin/env python3
"""
Script to sync Obsidian documentation to OpenAI's vector store.

This script scans the Obsidian vault, extracts markdown files,
and uploads them to OpenAI for use with the file_search tool.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Sync Obsidian documentation to OpenAI's vector store"
    )
    parser.add_argument(
        "--docs-dir",
        type=str,
        default="docs/obsidian/The Book of Shannon",
        help="Path to the Obsidian documentation directory",
    )
    parser.add_argument(
        "--config-file",
        type=str,
        default="src/lib/pioneer/config/shannon_assistant.json",
        help="Path to the assistant configuration file",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reupload even if files are already in the configuration",
    )
    return parser.parse_args()

def find_markdown_files(directory: str) -> List[str]:
    """Find all markdown files in the given directory.
    
    Args:
        directory: Path to the directory to search
        
    Returns:
        List of paths to markdown files
    """
    markdown_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                if ".obsidian" in root:
                    continue
                markdown_files.append(os.path.join(root, file))
    return markdown_files

def upload_files_to_openai(api_key: str, file_paths: List[str]) -> List[str]:
    """Upload files to OpenAI for use with the file_search tool.
    
    Args:
        api_key: OpenAI API key
        file_paths: List of paths to files to upload
        
    Returns:
        List of uploaded file IDs
    """
    client = OpenAI(api_key=api_key)
    file_ids = []
    
    for file_path in file_paths:
        try:
            with open(file_path, "rb") as file:
                response = client.files.create(
                    file=file,
                    purpose="assistants"
                )
                file_ids.append(response.id)
                print(f"Uploaded {file_path} with ID {response.id}")
        except Exception as e:
            print(f"Error uploading {file_path}: {e}")
    
    return file_ids

def update_assistant_config(config_file: str, file_ids: List[str]) -> None:
    """Update the assistant configuration with the uploaded file IDs.
    
    Args:
        config_file: Path to the assistant configuration file
        file_ids: List of uploaded file IDs
    """
    import json
    
    with open(config_file, "r") as f:
        config = json.load(f)
    
    config["files"] = file_ids
    
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"Updated assistant configuration with {len(file_ids)} files")

def main():
    """Main function to sync docs to OpenAI's vector store."""
    args = parse_args()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it in the .env file or export it in your shell")
        sys.exit(1)
    
    docs_dir = args.docs_dir
    if not os.path.exists(docs_dir):
        print(f"Error: Documentation directory {docs_dir} not found")
        sys.exit(1)
    
    markdown_files = find_markdown_files(docs_dir)
    print(f"Found {len(markdown_files)} markdown files in {docs_dir}")
    
    file_ids = upload_files_to_openai(api_key, markdown_files)
    print(f"Uploaded {len(file_ids)} files to OpenAI")
    
    update_assistant_config(args.config_file, file_ids)

if __name__ == "__main__":
    main()
