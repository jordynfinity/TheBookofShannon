#!/usr/bin/env python3
"""
Test script for the Shannon assistant with Crochet thread model.
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.lib.pioneer.assistant_client_crochet import CrochetAssistantClient

def main():
    """Test the Shannon assistant with Crochet thread model."""
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it in the .env file or export it in your shell")
        sys.exit(1)
    
    try:
        print("Creating Crochet assistant client...")
        client = CrochetAssistantClient(
            assistant_name="shannon_assistant",
            config_directory="src/lib/pioneer/config",
            character_ids=["shannon_theorist", "shannon_engineer", "shannon_teacher"]
        )
        
        print("Sending test message to assistant...")
        responses = client.chat("Tell me about Claude Shannon's information theory.")
        
        print("\nResponses from assistant characters:")
        for character_id, response in responses.items():
            print(f"\n--- {character_id} ---")
            print(response["content"])
        
        print("\nConversation history:")
        history = client.get_conversation_history()
        for msg in history:
            role = msg["role"]
            character = f" ({msg['character_id']})" if role == "assistant" and "character_id" in msg else ""
            print(f"{role}{character}: {msg['content'][:50]}...")
        
        print("\nAssistant test completed successfully!")
    except Exception as e:
        print(f"Error testing assistant: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
