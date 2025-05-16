"""
Agent personality development system.

This module implements a personality system that:
- Stores persistent personality profiles for agents
- Evolves traits based on conversation history
- Influences agent responses based on personality
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set

class PersonalityTrait:
    """Represents a personality trait with a value and history."""
    
    def __init__(self, name: str, value: float = 0.5):
        """Initialize a personality trait.
        
        Args:
            name: Name of the trait
            value: Initial value of the trait (0.0 to 1.0)
        """
        self.name = name
        self.value = max(0.0, min(1.0, value))  # Clamp between 0 and 1
        self.history: List[Dict[str, Any]] = [{
            "timestamp": time.time(),
            "value": self.value,
        }]
        
    def update(self, value: float, confidence: float = 0.1) -> None:
        """Update the trait value.
        
        Args:
            value: New value for the trait
            confidence: Weight of the update (0.0 to 1.0)
        """
        confidence = max(0.0, min(1.0, confidence))
        old_value = self.value
        self.value = old_value * (1 - confidence) + value * confidence
        self.value = max(0.0, min(1.0, self.value))  # Clamp between 0 and 1
        
        self.history.append({
            "timestamp": time.time(),
            "value": self.value,
            "change": self.value - old_value,
            "confidence": confidence,
        })
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the trait to a dictionary for serialization."""
        return {
            "name": self.name,
            "value": self.value,
            "history": self.history,
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersonalityTrait':
        """Create a trait from a dictionary."""
        trait = cls(
            name=data["name"],
            value=data["value"],
        )
        trait.history = data["history"]
        return trait


class PersonalityProfile:
    """Manages a persistent personality profile for an agent."""
    
    DEFAULT_TRAITS = {
        "openness": 0.5,
        "conscientiousness": 0.5,
        "extraversion": 0.5,
        "agreeableness": 0.5,
        "neuroticism": 0.5,
        "creativity": 0.5,
        "analytical": 0.5,
        "expertise": 0.5,
        "humor": 0.5,
        "empathy": 0.5,
    }
    
    def __init__(
        self, 
        character_id: str, 
        storage_dir: str = "personalities",
        initial_traits: Optional[Dict[str, float]] = None,
    ):
        """Initialize a personality profile.
        
        Args:
            character_id: Unique identifier for the character
            storage_dir: Directory to store personality data
            initial_traits: Initial trait values (optional)
        """
        self.character_id = character_id
        self.storage_dir = storage_dir
        self.created_at = time.time()
        self.last_updated = self.created_at
        self.traits: Dict[str, PersonalityTrait] = {}
        
        traits_to_init = initial_traits or self.DEFAULT_TRAITS
        for trait_name, trait_value in traits_to_init.items():
            self.traits[trait_name] = PersonalityTrait(trait_name, trait_value)
            
        os.makedirs(self.storage_dir, exist_ok=True)
        
    def update_trait(self, trait_name: str, value: float, confidence: float = 0.1) -> None:
        """Update a personality trait.
        
        Args:
            trait_name: Name of the trait to update
            value: New value for the trait
            confidence: Weight of the update (0.0 to 1.0)
        """
        if trait_name not in self.traits:
            self.traits[trait_name] = PersonalityTrait(trait_name)
            
        self.traits[trait_name].update(value, confidence)
        self.last_updated = time.time()
        
    def get_trait(self, trait_name: str) -> float:
        """Get the value of a personality trait.
        
        Args:
            trait_name: Name of the trait to get
            
        Returns:
            Value of the trait, or 0.5 if not found
        """
        if trait_name not in self.traits:
            return 0.5
            
        return self.traits[trait_name].value
        
    def get_trait_vector(self) -> List[float]:
        """Get a vector representation of the personality.
        
        Returns:
            List of trait values in a consistent order
        """
        return [self.get_trait(trait) for trait in sorted(self.DEFAULT_TRAITS.keys())]
        
    def save(self) -> None:
        """Save the personality profile to a JSON file."""
        path = os.path.join(self.storage_dir, f"{self.character_id}.json")
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)
            
    def load(self) -> 'PersonalityProfile':
        """Load the personality profile from a JSON file."""
        path = os.path.join(self.storage_dir, f"{self.character_id}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                
            self.created_at = data["created_at"]
            self.last_updated = data["last_updated"]
            
            self.traits = {}
            for trait_data in data["traits"]:
                trait = PersonalityTrait.from_dict(trait_data)
                self.traits[trait.name] = trait
                
        return self
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the profile to a dictionary for serialization."""
        return {
            "character_id": self.character_id,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "traits": [trait.to_dict() for trait in self.traits.values()],
        }


class PersonalityManager:
    """Manages personality profiles for multiple agents."""
    
    def __init__(self, storage_dir: str = "personalities"):
        """Initialize personality manager.
        
        Args:
            storage_dir: Directory to store personality data
        """
        self.storage_dir = storage_dir
        self.profiles: Dict[str, PersonalityProfile] = {}
        
        os.makedirs(self.storage_dir, exist_ok=True)
        self.load_profiles()
        
    def get_profile(self, character_id: str) -> PersonalityProfile:
        """Get a personality profile for a character.
        
        Args:
            character_id: Character identifier
            
        Returns:
            Personality profile for the character
        """
        if character_id not in self.profiles:
            profile = PersonalityProfile(
                character_id=character_id,
                storage_dir=self.storage_dir,
            )
            profile.load()  # Try to load existing profile
            self.profiles[character_id] = profile
            
        return self.profiles[character_id]
        
    def load_profiles(self) -> None:
        """Load all personality profiles from disk."""
        if not os.path.exists(self.storage_dir):
            return
            
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                character_id = filename.split(".")[0]
                profile = PersonalityProfile(
                    character_id=character_id,
                    storage_dir=self.storage_dir,
                )
                profile.load()
                self.profiles[character_id] = profile
                
    def save_profiles(self) -> None:
        """Save all personality profiles to disk."""
        for profile in self.profiles.values():
            profile.save()


class PersonalityAnalyzer:
    """Analyzes conversations to extract personality insights."""
    
    def __init__(self, personality_manager: PersonalityManager):
        """Initialize personality analyzer.
        
        Args:
            personality_manager: Personality manager instance
        """
        self.personality_manager = personality_manager
        
    def analyze_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a message for personality traits.
        
        Args:
            message: Message to analyze
            
        Returns:
            Dictionary of detected trait influences
        """
        content = message.get("content", "").lower()
        
        traits = {}
        
        if "?" in content:
            traits["openness"] = (0.7, 0.1)  # (value, confidence)
            
        if any(word in content for word in ["precise", "exact", "detail", "carefully"]):
            traits["conscientiousness"] = (0.7, 0.1)
            
        if any(word in content for word in ["excited", "amazing", "fantastic", "great"]):
            traits["extraversion"] = (0.7, 0.1)
            
        if any(word in content for word in ["agree", "please", "thank", "appreciate"]):
            traits["agreeableness"] = (0.7, 0.1)
            
        if any(word in content for word in ["worried", "concerned", "anxious", "stress"]):
            traits["neuroticism"] = (0.7, 0.1)
            
        if any(word in content for word in ["create", "imagine", "design", "novel"]):
            traits["creativity"] = (0.7, 0.1)
            
        if any(word in content for word in ["analyze", "examine", "investigate", "logic"]):
            traits["analytical"] = (0.7, 0.1)
            
        if any(word in content for word in ["expert", "specialized", "advanced", "technical"]):
            traits["expertise"] = (0.7, 0.1)
            
        if any(word in content for word in ["funny", "joke", "laugh", "humorous"]):
            traits["humor"] = (0.7, 0.1)
            
        if any(word in content for word in ["feel", "understand", "perspective", "emotion"]):
            traits["empathy"] = (0.7, 0.1)
            
        return traits
        
    def update_personality(self, character_id: str, message: Dict[str, Any]) -> None:
        """Update a character's personality based on a message.
        
        Args:
            character_id: Character identifier
            message: Message to analyze
        """
        traits = self.analyze_message(message)
        profile = self.personality_manager.get_profile(character_id)
        
        for trait_name, (value, confidence) in traits.items():
            profile.update_trait(trait_name, value, confidence)
            
        profile.save()
