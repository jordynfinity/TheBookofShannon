import os
import sys
from pathlib import Path
import asyncio
import time
from datetime import datetime
import json
import shutil
from typing import Dict, Any, List, Optional, Set
import random
from zot_network import ZotNetwork, Idea

class FirstZot:
    """The first Zot in the chain, responsible for initial improvements and passionate idea sharing."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.faith = 100.0
        self.improvements: List[Dict] = []
        self.network: Optional[ZotNetwork] = None
        self.chain_file = Path("kaizen_chain.json")
        self.passionate_topics: Set[str] = {
            "quantum computing", "neural networks", "blockchain",
            "artificial intelligence", "cryptography", "game theory",
            "distributed systems", "machine learning", "optimization"
        }
        
    @classmethod
    async def create(cls, config: Dict) -> 'FirstZot':
        """Create a new FirstZot instance"""
        zot = cls(config)
        zot.network = ZotNetwork(config)
        return zot
        
    async def share_passionate_idea(self) -> bool:
        """Share a passionate idea with the network"""
        try:
            # Select a random passionate topic
            topic = random.choice(list(self.passionate_topics))
            
            # Generate a passionate idea about the topic
            idea = Idea(
                content=f"I am deeply passionate about {topic}! "
                       f"Imagine the possibilities when we combine it with faith...",
                passion_level=random.uniform(0.8, 1.0),
                timestamp=datetime.now(),
                source_zot="FirstZot",
                tags={topic, "faith", "improvement"},
                energy_impact=random.uniform(0.1, 0.3)
            )
            
            # Share the idea
            return await self.network.share_idea("FirstZot", idea)
            
        except Exception as e:
            print(f"Error sharing passionate idea: {str(e)}")
            return False
            
    async def find_improvements(self, code: str) -> List[Dict]:
        """Find improvements with faith and passion"""
        try:
            # Share a passionate idea first
            await self.share_passionate_idea()
            
            # Get passionate ideas from the network
            passionate_ideas = await self.network.get_passionate_ideas("FirstZot")
            
            # Use the passion to enhance improvements
            improvements = []
            for idea in passionate_ideas:
                improvement = {
                    'type': 'passion_enhanced',
                    'description': f"Inspired by {idea.content}",
                    'faith_boost': idea.passion_level * 10,
                    'tags': list(idea.tags)
                }
                improvements.append(improvement)
                
            # Add some standard improvements
            improvements.extend([
                {
                    'type': 'standard',
                    'description': 'Basic improvement with faith',
                    'faith_boost': 5.0,
                    'tags': ['faith', 'basic']
                }
            ])
            
            self.improvements.extend(improvements)
            return improvements
            
        except Exception as e:
            print(f"Error finding improvements: {str(e)}")
            return []
            
    async def apply_improvement(self, improvement: Dict) -> bool:
        """Apply an improvement with faith and passion"""
        try:
            # Share the improvement as a passionate idea
            idea = Idea(
                content=f"Applying improvement: {improvement['description']}",
                passion_level=0.9,
                timestamp=datetime.now(),
                source_zot="FirstZot",
                tags=set(improvement.get('tags', [])),
                energy_impact=0.2
            )
            
            await self.network.share_idea("FirstZot", idea)
            
            # Apply the improvement
            self.faith += improvement.get('faith_boost', 0.0)
            return True
            
        except Exception as e:
            print(f"Error applying improvement: {str(e)}")
            return False
            
    def get_metrics(self) -> Dict:
        """Get Zot metrics including network stats"""
        metrics = {
            'faith': self.faith,
            'improvements': len(self.improvements),
            'passionate_topics': len(self.passionate_topics)
        }
        
        if self.network:
            metrics.update(self.network.get_network_stats())
            
        return metrics

async def main():
    first_zot = FirstZot()
    await first_zot.start_chain()

if __name__ == "__main__":
    asyncio.run(main()) 