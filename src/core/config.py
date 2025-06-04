import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigManager:
    """Manages configuration settings"""
    
    def __init__(self, config_file: str = "config/config.json"):
        self._setup_logging()
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self._load_config()
        
    def _setup_logging(self):
        """Set up logging"""
        self.logger = logging.getLogger("ConfigManager")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler("logs/config_manager.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
    def _load_config(self):
        """Load configuration from file"""
        try:
            # Ensure config directory exists
            config_dir = os.path.dirname(self.config_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
                
            # Load config file if it exists
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                self.logger.info("Configuration loaded successfully")
            else:
                # Create default config
                self.config = {
                    "window": {
                        "width": 800,
                        "height": 600,
                        "title": "The Book of Shannon",
                        "fps": 60
                    },
                    "wave": {
                        "amplitude": 50,
                        "frequency": 0.1,
                        "phase": 0,
                        "interaction_decay": 0.95
                    },
                    "audio": {
                        "sample_rate": 44100,
                        "buffer_size": 1024,
                        "channels": 2
                    },
                    "resource_management": {
                        "optimization_threshold": 0.8,
                        "max_history": 1000
                    },
                    "logging": {
                        "level": "DEBUG",
                        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        "file": "logs/gui.log"
                    },
                    "improvement": {
                        "max_attempts": 10,
                        "max_processes": 4,
                        "timeout": 300,
                        "coverage_threshold": 0.8,
                        "validation_depth": 3,
                        "auto_apply": True,
                        "save_attempts": True,
                        "log_level": "DEBUG"
                    }
                }
                self._save_config()
                self.logger.info("Default configuration created")
                
        except Exception as e:
            self.logger.error(f"Error loading configuration: {str(e)}")
            # Set default config on error
            self.config = {
                "window": {
                    "width": 800,
                    "height": 600,
                    "title": "The Book of Shannon",
                    "fps": 60
                }
            }
            
    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            self.logger.info("Configuration saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {str(e)}")
            
    def get(self, section: str, default: Any = None) -> Any:
        """Get configuration section"""
        try:
            return self.config.get(section, default)
        except Exception as e:
            self.logger.error(f"Error getting config section {section}: {str(e)}")
            return default
            
    def set(self, section: str, value: Any):
        """Set configuration section"""
        try:
            self.config[section] = value
            self._save_config()
        except Exception as e:
            self.logger.error(f"Error setting config section {section}: {str(e)}")
            
    def update(self, section: str, key: str, value: Any):
        """Update specific configuration value"""
        try:
            if section not in self.config:
                self.config[section] = {}
            self.config[section][key] = value
            self._save_config()
        except Exception as e:
            self.logger.error(f"Error updating config {section}.{key}: {str(e)}")
            
    def get_value(self, section: str, key: str, default: Any = None) -> Any:
        """Get specific configuration value"""
        try:
            return self.config.get(section, {}).get(key, default)
        except Exception as e:
            self.logger.error(f"Error getting config value {section}.{key}: {str(e)}")
            return default 