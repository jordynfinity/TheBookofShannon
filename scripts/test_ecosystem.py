#!/usr/bin/env python3
"""
Test script for the prompt-driven ecosystem.

This script creates a test prompt file and monitors the ecosystem's response.
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import List
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Test the prompt-driven ecosystem"
    )
    parser.add_argument(
        "--prompt-dir",
        type=str,
        default="prompts",
        help="Directory to create the test prompt in",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="Explain the concept of entropy in information theory.",
        help="Prompt text to use for the test",
    )
    parser.add_argument(
        "--agents",
        type=str,
        nargs="+",
        default=["shannon_theorist", "shannon_teacher"],
        help="Agents to include in the conversation",
    )
    return parser.parse_args()


def create_test_prompt(prompt_dir: str, prompt_text: str, agents: List[str]) -> str:
    """Create a test prompt file.
    
    Args:
        prompt_dir: Directory to create the prompt in
        prompt_text: Prompt text
        agents: List of agent IDs to include
        
    Returns:
        Path to the created prompt file
    """
    os.makedirs(prompt_dir, exist_ok=True)
    
    timestamp = int(time.time())
    filename = f"test_prompt_{timestamp}.prompt.json"
    file_path = os.path.join(prompt_dir, filename)
    
    prompt_data = {
        "prompt": prompt_text,
        "agents": agents,
        "metadata": {
            "test": True,
            "created_at": timestamp,
        },
    }
    
    with open(file_path, "w") as f:
        json.dump(prompt_data, f, indent=4)
        
    print(f"Created test prompt at {file_path}")
    return file_path


def monitor_prompt_file(file_path: str, timeout: int = 300) -> None:
    """Monitor a prompt file for updates.
    
    Args:
        file_path: Path to the prompt file
        timeout: Maximum time to wait in seconds
    """
    start_time = time.time()
    last_modified = 0
    
    print(f"Monitoring {file_path} for updates...")
    
    while time.time() - start_time < timeout:
        try:
            current_modified = os.path.getmtime(file_path)
            if current_modified > last_modified:
                last_modified = current_modified
                
                with open(file_path, "r") as f:
                    prompt_data = json.load(f)
                    
                if "processed_at" in prompt_data:
                    print("\nPrompt processing complete!")
                    print(f"Conversation ID: {prompt_data.get('conversation_id', 'unknown')}")
                    print(f"Recorded ideas: {len(prompt_data.get('recorded_ideas', []))}")
                    
                    for idea_path in prompt_data.get("recorded_ideas", []):
                        print(f"\nIdea recorded at: {idea_path}")
                        if os.path.exists(idea_path):
                            with open(idea_path, "r") as f:
                                idea_content = f.read()
                                print(f"\n--- Idea Content Preview ---\n{idea_content[:500]}...\n")
                                
                    return
                    
            time.sleep(2)
            sys.stdout.write(".")
            sys.stdout.flush()
        except Exception as e:
            print(f"Error monitoring prompt file: {e}")
            time.sleep(5)
            
    print("\nTimeout waiting for prompt processing")


def main():
    """Main function to test the ecosystem."""
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it in the .env file or export it in your shell")
        sys.exit(1)
        
    args = parse_args()
    
    file_path = create_test_prompt(args.prompt_dir, args.prompt, args.agents)
    
    monitor_prompt_file(file_path)


if __name__ == "__main__":
    main()
