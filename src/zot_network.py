import asyncio
from typing import List, Dict, Set, Optional
import psutil
import time
from datetime import datetime
import json
from pathlib import Path
import logging
from dataclasses import dataclass
import random

@dataclass
class Idea:
    """Represents a passionate idea shared between Zots"""
    content: str
    passion_level: float  # 0.0 to 1.0
    timestamp: datetime
    source_zot: str
    tags: Set[str]
    energy_impact: float  # Estimated resource impact (0.0 to 1.0)

class ResourceMonitor:
    """Monitors system resources and manages pruning"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.cpu_threshold = config.get('cpu_threshold', 80.0)  # Percentage
        self.memory_threshold = config.get('memory_threshold', 80.0)  # Percentage
        self.disk_threshold = config.get('disk_threshold', 80.0)  # Percentage
        self.last_prune_time = time.time()
        self.prune_cooldown = config.get('prune_cooldown', 300)  # 5 minutes
        
    def should_prune(self) -> bool:
        """Check if system resources need pruning"""
        if time.time() - self.last_prune_time < self.prune_cooldown:
            return False
            
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent
        
        return (cpu_percent > self.cpu_threshold or 
                memory_percent > self.memory_threshold or 
                disk_percent > self.disk_threshold)
                
    def get_resource_usage(self) -> Dict[str, float]:
        """Get current resource usage"""
        return {
            'cpu': psutil.cpu_percent(),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent
        }
        
    def mark_pruned(self):
        """Mark that pruning has occurred"""
        self.last_prune_time = time.time()

class ZotNetwork:
    """Manages Zot interactions and idea sharing"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.resource_monitor = ResourceMonitor(config)
        self.ideas: List[Idea] = []
        self.active_zots: Dict[str, float] = {}  # zot_id -> last_active_time
        self.idea_history: Dict[str, List[Idea]] = {}  # zot_id -> list of ideas
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for the network"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            filename=log_dir / "zot_network.log",
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("ZotNetwork")
        
    async def share_idea(self, zot_id: str, idea: Idea) -> bool:
        """Share a passionate idea with the network"""
        try:
            # Check resources before sharing
            if self.resource_monitor.should_prune():
                await self.prune_network()
                
            # Add idea to history
            if zot_id not in self.idea_history:
                self.idea_history[zot_id] = []
            self.idea_history[zot_id].append(idea)
            
            # Add to global ideas
            self.ideas.append(idea)
            
            # Update active zots
            self.active_zots[zot_id] = time.time()
            
            # Log the idea
            self.logger.info(f"Zot {zot_id} shared idea: {idea.content[:50]}... "
                           f"(Passion: {idea.passion_level:.2f})")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sharing idea: {str(e)}")
            return False
            
    async def get_passionate_ideas(self, zot_id: str, 
                                 min_passion: float = 0.7,
                                 limit: int = 5) -> List[Idea]:
        """Get the most passionate ideas from the network"""
        try:
            # Filter ideas by passion level and exclude own ideas
            passionate_ideas = [
                idea for idea in self.ideas
                if idea.passion_level >= min_passion and idea.source_zot != zot_id
            ]
            
            # Sort by passion level and timestamp
            passionate_ideas.sort(
                key=lambda x: (x.passion_level, x.timestamp),
                reverse=True
            )
            
            return passionate_ideas[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting passionate ideas: {str(e)}")
            return []
            
    async def prune_network(self):
        """Prune the network to manage resources"""
        try:
            self.logger.info("Starting network pruning...")
            
            # Remove old ideas
            current_time = time.time()
            self.ideas = [
                idea for idea in self.ideas
                if (current_time - idea.timestamp.timestamp()) < self.config.get('idea_retention', 86400)
            ]
            
            # Remove inactive zots
            inactive_threshold = self.config.get('inactive_threshold', 3600)  # 1 hour
            self.active_zots = {
                zot_id: last_active
                for zot_id, last_active in self.active_zots.items()
                if (current_time - last_active) < inactive_threshold
            }
            
            # Clean up idea history
            for zot_id in list(self.idea_history.keys()):
                if zot_id not in self.active_zots:
                    del self.idea_history[zot_id]
                    
            # Mark pruning complete
            self.resource_monitor.mark_pruned()
            
            self.logger.info("Network pruning completed")
            
        except Exception as e:
            self.logger.error(f"Error during pruning: {str(e)}")
            
    def get_network_stats(self) -> Dict:
        """Get current network statistics"""
        return {
            'active_zots': len(self.active_zots),
            'total_ideas': len(self.ideas),
            'resource_usage': self.resource_monitor.get_resource_usage(),
            'average_passion': sum(idea.passion_level for idea in self.ideas) / len(self.ideas) if self.ideas else 0
        }
        
    async def save_state(self, filepath: str):
        """Save network state to file"""
        try:
            state = {
                'ideas': [
                    {
                        'content': idea.content,
                        'passion_level': idea.passion_level,
                        'timestamp': idea.timestamp.isoformat(),
                        'source_zot': idea.source_zot,
                        'tags': list(idea.tags),
                        'energy_impact': idea.energy_impact
                    }
                    for idea in self.ideas
                ],
                'active_zots': self.active_zots,
                'idea_history': {
                    zot_id: [
                        {
                            'content': idea.content,
                            'passion_level': idea.passion_level,
                            'timestamp': idea.timestamp.isoformat(),
                            'source_zot': idea.source_zot,
                            'tags': list(idea.tags),
                            'energy_impact': idea.energy_impact
                        }
                        for idea in ideas
                    ]
                    for zot_id, ideas in self.idea_history.items()
                }
            }
            
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
                
            self.logger.info(f"Network state saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving network state: {str(e)}")
            
    async def load_state(self, filepath: str):
        """Load network state from file"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
                
            self.ideas = [
                Idea(
                    content=idea['content'],
                    passion_level=idea['passion_level'],
                    timestamp=datetime.fromisoformat(idea['timestamp']),
                    source_zot=idea['source_zot'],
                    tags=set(idea['tags']),
                    energy_impact=idea['energy_impact']
                )
                for idea in state['ideas']
            ]
            
            self.active_zots = state['active_zots']
            
            self.idea_history = {
                zot_id: [
                    Idea(
                        content=idea['content'],
                        passion_level=idea['passion_level'],
                        timestamp=datetime.fromisoformat(idea['timestamp']),
                        source_zot=idea['source_zot'],
                        tags=set(idea['tags']),
                        energy_impact=idea['energy_impact']
                    )
                    for idea in ideas
                ]
                for zot_id, ideas in state['idea_history'].items()
            }
            
            self.logger.info(f"Network state loaded from {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error loading network state: {str(e)}") 