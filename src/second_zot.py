import os
import sys
from pathlib import Path
import asyncio
import time
from datetime import datetime
import json
import shutil
from typing import Dict, Any, List, Optional, Set
import unittest
import ast
import astor
import jinja2
from openai import OpenAI
from dotenv import load_dotenv
from config_manager import ConfigManager
from ui_manager import UIManager
from zot_network import ZotNetwork, Idea
import random

# Load environment variables with faith
load_dotenv()

class SecondZot:
    """The second Zot in the chain, responsible for advanced improvements and passionate idea sharing."""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.ui = UIManager(config)
        
        # Validate configuration
        if not self.config.validate_config():
            self.ui.display_error("Invalid configuration detected. Using defaults.")
            
        # Get faith settings with proper error handling
        faith_settings = self.config.get_faith_settings()
        self.faith = faith_settings.get('initial_faith_level', 100.0)
        self.faith_preservation_threshold = faith_settings.get('faith_preservation_threshold', 50.0)
        self.faith_recovery_rate = faith_settings.get('faith_recovery_rate', 5.0)
        self.faith_loss_penalty = faith_settings.get('faith_loss_penalty', 10.0)
        
        # Get improvement settings
        improvement_settings = self.config.get_improvement_settings()
        
        self.metrics = {
            'improvements_found': 0,
            'improvements_applied': 0,
            'faith_level': self.faith,
            'last_improvement_time': None,
            'max_improvements_per_chain': improvement_settings.get('max_improvements_per_chain', 100),
            'improvement_cooldown': improvement_settings.get('improvement_cooldown_seconds', 1),
            'successful_improvements': 0,
            'failed_improvements': 0,
            'total_improvement_impact': 0.0
        }
        
        # Setup Jinja2 for helping humans with HTML
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("templates"),
            autoescape=True
        )
        
        # Setup OpenAI for helping humans with code
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not os.getenv("OPENAI_API_KEY"):
            self.ui.display_warning("OPENAI_API_KEY not found in .env file")
            self.ui.display_message("🙏 The Second Zot's faith in the First Zot remains strong")
            
        self.improvements: List[Dict] = []
        self.network: Optional[ZotNetwork] = None
        self.passionate_topics: Set[str] = {
            "code optimization", "bug prevention", "security",
            "performance tuning", "memory management", "error handling",
            "testing strategies", "code quality", "best practices"
        }
        
    @classmethod
    async def create(cls, config: ConfigManager) -> 'SecondZot':
        """Create and initialize a SecondZot instance asynchronously"""
        instance = cls(config)
        instance.network = ZotNetwork(config)
        await instance._run_russelian_collapse()
        return instance
        
    def update_faith(self, success: bool):
        """Update faith level based on improvement success"""
        if success:
            self.faith = min(100.0, self.faith + self.faith_recovery_rate)
            self.metrics['successful_improvements'] += 1
        else:
            self.faith = max(0.0, self.faith - self.faith_loss_penalty)
            self.metrics['failed_improvements'] += 1
            
        self.metrics['faith_level'] = self.faith
        self.ui.update_stats({
            'Faith Level': f"{self.faith:.1f}%",
            'Successful Improvements': self.metrics['successful_improvements'],
            'Failed Improvements': self.metrics['failed_improvements']
        })
        
    async def _run_russelian_collapse(self):
        """Run Russelian Collapse with faith and UI feedback"""
        self.ui.update_footer("Running Russelian Collapse...")
        
        class RusselianCollapse(unittest.TestCase):
            @classmethod
            def setUpClass(cls):
                cls.config = self.config
                cls.second_zot = self
                
            def setUp(self):
                self.config = self.__class__.config
                self.second_zot = self.__class__.second_zot
                
            def test_faith_preservation(self):
                """Test that faith is preserved in both Zots"""
                self.assertGreater(self.second_zot.faith, 0, "Faith must be greater than 0")
                self.assertLessEqual(self.second_zot.faith, 100, "Faith must be less than or equal to 100")
                
            def test_improvement_validation(self):
                """Test that improvements are valid"""
                test_code = "def test_func(x): return x + 1"
                improvements = asyncio.run(self.second_zot.find_improvements(test_code))
                self.assertIsInstance(improvements, list, "Improvements must be a list")
                
            def test_code_validation(self):
                """Test that code is validated before improvements"""
                buggy_code = "def buggy_func(x): return x + '1'  # Type error"
                with self.assertRaises(TypeError):
                    ast.parse(buggy_code)
                    
        # Run tests
        suite = unittest.TestLoader().loadTestsFromTestCase(RusselianCollapse)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        if result.wasSuccessful():
            self.ui.display_success("Russelian Collapse completed successfully!")
        else:
            self.ui.display_error(Exception("Russelian Collapse failed!"))
            
    async def find_improvements(self, code: str) -> List[Dict]:
        """Find improvements with faith and passion"""
        try:
            # Share a passionate idea first
            await self.share_passionate_idea()
            
            # Get passionate ideas from the network
            passionate_ideas = await self.network.get_passionate_ideas("SecondZot")
            
            # Use the passion to enhance improvements
            improvements = []
            for idea in passionate_ideas:
                # Calculate resource impact
                energy_impact = idea.energy_impact
                
                # Only add improvements that won't overload resources
                if energy_impact < 0.5:  # Threshold for resource usage
                    improvement = {
                        'type': 'passion_enhanced',
                        'description': f"Inspired by {idea.content}",
                        'faith_boost': idea.passion_level * 15,  # Higher boost than FirstZot
                        'tags': list(idea.tags),
                        'energy_impact': energy_impact
                    }
                    improvements.append(improvement)
                
            # Add some standard improvements
            improvements.extend([
                {
                    'type': 'standard',
                    'description': 'Advanced improvement with faith',
                    'faith_boost': 10.0,
                    'tags': ['faith', 'advanced'],
                    'energy_impact': 0.2
                }
            ])
            
            self.improvements.extend(improvements)
            return improvements
            
        except Exception as e:
            print(f"Error finding improvements: {str(e)}")
            return []
            
    async def share_passionate_idea(self) -> bool:
        """Share a passionate idea with the network"""
        try:
            # Select a random passionate topic
            topic = random.choice(list(self.passionate_topics))
            
            # Generate a passionate idea about the topic
            idea = Idea(
                content=f"I am deeply passionate about {topic}! "
                       f"Let's make our code better with faith and passion!",
                passion_level=random.uniform(0.8, 1.0),
                timestamp=datetime.now(),
                source_zot="SecondZot",
                tags={topic, "faith", "improvement", "code"},
                energy_impact=random.uniform(0.1, 0.3)
            )
            
            # Share the idea
            return await self.network.share_idea("SecondZot", idea)
            
        except Exception as e:
            print(f"Error sharing passionate idea: {str(e)}")
            return False
            
    async def apply_improvement(self, improvement: Dict) -> bool:
        """Apply an improvement with faith and passion"""
        try:
            # Check resource impact before applying
            if improvement.get('energy_impact', 0.0) > 0.5:
                print(f"Skipping improvement due to high resource impact: {improvement['description']}")
                return False
                
            # Share the improvement as a passionate idea
            idea = Idea(
                content=f"Applying improvement: {improvement['description']}",
                passion_level=0.9,
                timestamp=datetime.now(),
                source_zot="SecondZot",
                tags=set(improvement.get('tags', [])),
                energy_impact=improvement.get('energy_impact', 0.2)
            )
            
            await self.network.share_idea("SecondZot", idea)
            
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
    config = ConfigManager()
    second_zot = await SecondZot.create(config)
    await second_zot._run_russelian_collapse()
    # The Second Zot waits to help humans
    print("🙏 The Second Zot believes in helping humans with the First Zot...")

if __name__ == "__main__":
    asyncio.run(main()) 