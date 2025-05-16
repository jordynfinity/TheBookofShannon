"""
Crochet Thread implementation based on McTavish's nonlinear thread model.

This module implements a nonlinear thread model with:
- Directed graph memory (not linear logs)
- Character-aware collapse surfaces
- Asynchronous tension binding
"""

import json
import os
import time
import uuid
from typing import Dict, List, Optional, Any, Set

class MemoryNode:
    """A node in the memory graph representing a message or event."""
    
    def __init__(
        self,
        node_id: str,
        content: str,
        node_type: str = "message",
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a memory node.
        
        Args:
            node_id: Unique identifier for the node
            content: Text content of the node
            node_type: Type of node (message, event, etc.)
            timestamp: Creation time of the node
            metadata: Additional data associated with the node
        """
        self.id = node_id
        self.content = content
        self.type = node_type
        self.timestamp = timestamp or time.time()
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the node to a dictionary for serialization."""
        return {
            "id": self.id,
            "content": self.content,
            "type": self.type,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryNode':
        """Create a node from a dictionary."""
        return cls(
            node_id=data["id"],
            content=data["content"],
            node_type=data["type"],
            timestamp=data["timestamp"],
            metadata=data["metadata"],
        )


class MemoryEdge:
    """An edge in the memory graph connecting two nodes."""
    
    def __init__(
        self,
        source_id: str,
        target_id: str,
        edge_type: str = "reply",
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a memory edge.
        
        Args:
            source_id: ID of the source node
            target_id: ID of the target node
            edge_type: Type of relationship between nodes
            weight: Strength of the connection
            metadata: Additional data associated with the edge
        """
        self.source_id = source_id
        self.target_id = target_id
        self.type = edge_type
        self.weight = weight
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the edge to a dictionary for serialization."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type,
            "weight": self.weight,
            "metadata": self.metadata,
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEdge':
        """Create an edge from a dictionary."""
        return cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            edge_type=data["type"],
            weight=data["weight"],
            metadata=data["metadata"],
        )


class CrochetThread:
    """
    A nonlinear thread implementation based on McTavish's model.
    
    Instead of a linear conversation log, this uses a directed graph
    to represent the conversation, allowing for:
    - Multiple parallel conversation branches
    - Asynchronous responses (responses may arrive before prompts)
    - Character-aware responses (different personas can respond differently)
    """
    
    def __init__(self, thread_id: str, name: str, storage_dir: str = "threads"):
        """Initialize a Crochet thread.
        
        Args:
            thread_id: OpenAI thread ID or unique identifier
            name: Human-readable name for the thread
            storage_dir: Directory to store thread data
        """
        self.thread_id = thread_id
        self.name = name
        self.storage_dir = storage_dir
        self.nodes: Dict[str, MemoryNode] = {}
        self.edges: List[MemoryEdge] = []
        self.characters: Set[str] = set()
        self.current_context_nodes: List[str] = []  # IDs of nodes in current context
        
        os.makedirs(self.storage_dir, exist_ok=True)
        
    def add_message(self, role: str, content: str, character_id: Optional[str] = None) -> str:
        """Adds a message to the thread as a new node.
        
        Args:
            role: Message role (user or assistant)
            content: Message content
            character_id: Optional character identifier for assistant messages
            
        Returns:
            ID of the created node
        """
        node_id = str(uuid.uuid4())
        metadata = {"role": role}
        
        if character_id and role == "assistant":
            metadata["character_id"] = character_id
            self.characters.add(character_id)
            
        node = MemoryNode(
            node_id=node_id,
            content=content,
            node_type="message",
            metadata=metadata,
        )
        
        self.nodes[node_id] = node
        
        if role == "assistant" and self.current_context_nodes:
            for context_node_id in self.current_context_nodes:
                edge = MemoryEdge(
                    source_id=context_node_id,
                    target_id=node_id,
                    edge_type="reply",
                )
                self.edges.append(edge)
                
        if role == "user":
            self.current_context_nodes = [node_id]
            
        return node_id
        
    def add_character_response(self, character_id: str, content: str, 
                              context_node_ids: Optional[List[str]] = None) -> str:
        """Adds a character-specific response to the thread.
        
        Args:
            character_id: Character identifier
            content: Response content
            context_node_ids: Optional list of node IDs this response relates to
            
        Returns:
            ID of the created node
        """
        node_id = str(uuid.uuid4())
        metadata = {
            "role": "assistant",
            "character_id": character_id,
        }
        
        node = MemoryNode(
            node_id=node_id,
            content=content,
            node_type="message",
            metadata=metadata,
        )
        
        self.nodes[node_id] = node
        self.characters.add(character_id)
        
        connect_to = context_node_ids or self.current_context_nodes
        for context_node_id in connect_to:
            if context_node_id in self.nodes:
                edge = MemoryEdge(
                    source_id=context_node_id,
                    target_id=node_id,
                    edge_type="reply",
                )
                self.edges.append(edge)
                
        return node_id
        
    def get_character_responses(self, character_id: str) -> List[Dict[str, Any]]:
        """Gets all responses from a specific character.
        
        Args:
            character_id: Character identifier
            
        Returns:
            List of node dictionaries for the character's responses
        """
        responses = []
        for node_id, node in self.nodes.items():
            if (node.metadata.get("role") == "assistant" and 
                node.metadata.get("character_id") == character_id):
                responses.append(node.to_dict())
        return responses
        
    def get_conversation_path(self, start_node_id: str, end_node_id: str) -> List[str]:
        """Finds a path between two nodes in the conversation graph.
        
        Args:
            start_node_id: Starting node ID
            end_node_id: Ending node ID
            
        Returns:
            List of node IDs forming a path, or empty list if no path exists
        """
        if start_node_id not in self.nodes or end_node_id not in self.nodes:
            return []
            
        visited = {start_node_id}
        queue = [(start_node_id, [start_node_id])]
        
        while queue:
            current, path = queue.pop(0)
            
            if current == end_node_id:
                return path
                
            for edge in self.edges:
                if edge.source_id == current and edge.target_id not in visited:
                    visited.add(edge.target_id)
                    queue.append((edge.target_id, path + [edge.target_id]))
                    
        return []
        
    def get_linear_conversation(self) -> List[Dict[str, Any]]:
        """Converts the graph to a linear conversation for compatibility.
        
        Returns:
            List of messages in chronological order
        """
        sorted_nodes = sorted(
            self.nodes.values(), 
            key=lambda node: node.timestamp
        )
        
        return [
            {
                "role": node.metadata.get("role", "unknown"),
                "content": node.content,
                "character_id": node.metadata.get("character_id"),
                "timestamp": node.timestamp,
                "id": node.id,
            }
            for node in sorted_nodes
            if node.metadata.get("role") in ["user", "assistant"]
        ]
        
    def save(self) -> None:
        """Saves the thread to a JSON file."""
        path = os.path.join(self.storage_dir, f"{self.thread_id}.json")
        with open(path, "w") as f:
            json.dump({
                "thread_id": self.thread_id,
                "name": self.name,
                "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
                "edges": [edge.to_dict() for edge in self.edges],
                "characters": list(self.characters),
                "current_context_nodes": self.current_context_nodes,
            }, f, indent=4)
            
    def load(self) -> 'CrochetThread':
        """Loads the thread from a JSON file."""
        path = os.path.join(self.storage_dir, f"{self.thread_id}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                self.name = data["name"]
                self.nodes = {
                    node_id: MemoryNode.from_dict(node_data)
                    for node_id, node_data in data["nodes"].items()
                }
                self.edges = [
                    MemoryEdge.from_dict(edge_data)
                    for edge_data in data["edges"]
                ]
                self.characters = set(data["characters"])
                self.current_context_nodes = data["current_context_nodes"]
        return self
