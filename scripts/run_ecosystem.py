#!/usr/bin/env python3
"""
Script to run the prompt-driven ecosystem.

This script initializes and runs the ecosystem controller,
which watches for prompt files and generates conversations and ideas.
"""

import os
import sys
import time
import argparse
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.lib.pioneer.ecosystem.controller import EcosystemController


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run the prompt-driven ecosystem"
    )
    parser.add_argument(
        "--prompt-dirs",
        type=str,
        nargs="+",
        default=["prompts"],
        help="Directories to watch for prompts",
    )
    parser.add_argument(
        "--docs-dir",
        type=str,
        default="docs/obsidian/The Book of Shannon",
        help="Path to the documentation directory",
    )
    parser.add_argument(
        "--assistant-name",
        type=str,
        default="shannon_assistant",
        help="Name of the assistant configuration to load",
    )
    parser.add_argument(
        "--config-directory",
        type=str,
        default="src/lib/pioneer/config",
        help="Path to the directory containing assistant configurations",
    )
    return parser.parse_args()


def main():
    """Main function to run the ecosystem."""
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it in the .env file or export it in your shell")
        sys.exit(1)
        
    args = parse_args()
    
    for prompt_dir in args.prompt_dirs:
        os.makedirs(prompt_dir, exist_ok=True)
        
    controller = EcosystemController(
        prompt_dirs=args.prompt_dirs,
        docs_dir=args.docs_dir,
        assistant_name=args.assistant_name,
        config_directory=args.config_directory,
    )
    
    try:
        controller.start()
        
        print("Ecosystem running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping ecosystem...")
        controller.stop()
        print("Ecosystem stopped")
    except Exception as e:
        print(f"Error running ecosystem: {e}")
        controller.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
