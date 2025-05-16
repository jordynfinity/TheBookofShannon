"""
Agent conversation orchestration system.

This module implements a conversation system that:
- Manages interactions between multiple agents
- Structures conversations based on prompts
- Monitors conversation flow and patterns
"""

import json
import os
import time
import uuid
from typing import Dict, List, Optional, Any, Set, Tuple

from src.lib.pioneer.assistant_client_crochet import CrochetAssistantClient
from src.lib.pioneer.ecosystem.personality import PersonalityManager, PersonalityAnalyzer


class ConversationManager:
    """Manages conversations between agents."""
    
    def __init__(
        self, 
        assistant_name: str = "shannon_assistant",
        config_directory: str = "src/lib/pioneer/config",
        conversation_dir: str = "conversations",
        personality_dir: str = "personalities",
    ):
        """Initialize conversation manager.
        
        Args:
            assistant_name: Name of the assistant configuration to load
            config_directory: Path to the directory containing assistant configurations
            conversation_dir: Directory to store conversation data
            personality_dir: Directory to store personality data
        """
        self.assistant_name = assistant_name
        self.config_directory = config_directory
        self.conversation_dir = conversation_dir
        self.personality_dir = personality_dir
        
        self.conversations: Dict[str, Dict[str, Any]] = {}
        self.personality_manager = PersonalityManager(storage_dir=personality_dir)
        self.personality_analyzer = PersonalityAnalyzer(self.personality_manager)
        
        os.makedirs(self.conversation_dir, exist_ok=True)
        
    def select_agents_for_prompt(self, prompt_data: Dict[str, Any]) -> List[str]:
        """Select appropriate agents for a prompt.
        
        Args:
            prompt_data: Prompt data including optional agent preferences
            
        Returns:
            List of character IDs to include in the conversation
        """
        if "agents" in prompt_data and prompt_data["agents"]:
            return prompt_data["agents"]
            
        default_agents = ["shannon_theorist", "shannon_engineer", "shannon_teacher"]
        
        prompt_text = prompt_data.get("prompt", "").lower()
        
        if "theory" in prompt_text or "concept" in prompt_text:
            return ["shannon_theorist", "shannon_teacher"]
        elif "implement" in prompt_text or "code" in prompt_text or "build" in prompt_text:
            return ["shannon_engineer", "shannon_theorist"]
        elif "explain" in prompt_text or "teach" in prompt_text:
            return ["shannon_teacher", "shannon_theorist"]
            
        return default_agents
        
    def create_conversation(self, prompt_data: Dict[str, Any]) -> str:
        """Create a new conversation based on a prompt.
        
        Args:
            prompt_data: Prompt data including the prompt text and optional settings
            
        Returns:
            Conversation ID
        """
        conversation_id = str(uuid.uuid4())
        prompt_text = prompt_data.get("prompt", "")
        
        character_ids = self.select_agents_for_prompt(prompt_data)
        
        client = CrochetAssistantClient(
            assistant_name=self.assistant_name,
            config_directory=self.config_directory,
            character_ids=character_ids,
        )
        
        self.conversations[conversation_id] = {
            "id": conversation_id,
            "prompt": prompt_text,
            "created_at": time.time(),
            "last_updated": time.time(),
            "character_ids": character_ids,
            "client": client,
            "thread_id": client.thread_id,
            "messages": [],
            "completed": False,
            "metadata": prompt_data.get("metadata", {}),
        }
        
        self._send_message(conversation_id, prompt_text)
        
        return conversation_id
        
    def _send_message(self, conversation_id: str, message: str) -> Dict[str, Any]:
        """Send a message to the conversation.
        
        Args:
            conversation_id: Conversation ID
            message: Message to send
            
        Returns:
            Dictionary of responses by character ID
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation ID {conversation_id} not found")
            
        conversation = self.conversations[conversation_id]
        client = conversation["client"]
        
        user_message = {
            "id": str(uuid.uuid4()),
            "role": "user",
            "content": message,
            "timestamp": time.time(),
        }
        conversation["messages"].append(user_message)
        
        responses = client.chat(message)
        
        for character_id, response in responses.items():
            response_message = {
                "id": response["node_id"],
                "role": "assistant",
                "character_id": character_id,
                "content": response["content"],
                "timestamp": time.time(),
            }
            conversation["messages"].append(response_message)
            
            self.personality_analyzer.update_personality(character_id, response_message)
            
        conversation["last_updated"] = time.time()
        self._save_conversation(conversation_id)
        
        return responses
        
    def continue_conversation(self, conversation_id: str, follow_up: str) -> Dict[str, Any]:
        """Continue an existing conversation with a follow-up message.
        
        Args:
            conversation_id: Conversation ID
            follow_up: Follow-up message
            
        Returns:
            Dictionary of responses by character ID
        """
        return self._send_message(conversation_id, follow_up)
        
    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation data.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation data dictionary
        """
        if conversation_id not in self.conversations:
            conversation = self._load_conversation(conversation_id)
            if not conversation:
                raise ValueError(f"Conversation ID {conversation_id} not found")
                
            client = CrochetAssistantClient(
                assistant_name=self.assistant_name,
                config_directory=self.config_directory,
                character_ids=conversation["character_ids"],
            )
            conversation["client"] = client
            self.conversations[conversation_id] = conversation
            
        return self.conversations[conversation_id]
        
    def _save_conversation(self, conversation_id: str) -> None:
        """Save conversation data to disk.
        
        Args:
            conversation_id: Conversation ID
        """
        if conversation_id not in self.conversations:
            return
            
        conversation = self.conversations[conversation_id]
        path = os.path.join(self.conversation_dir, f"{conversation_id}.json")
        
        serializable = conversation.copy()
        serializable.pop("client", None)
        
        with open(path, "w") as f:
            json.dump(serializable, f, indent=4)
            
    def _load_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Load conversation data from disk.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation data dictionary, or None if not found
        """
        path = os.path.join(self.conversation_dir, f"{conversation_id}.json")
        if not os.path.exists(path):
            return None
            
        with open(path, "r") as f:
            return json.load(f)
