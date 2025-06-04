import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
import shutil
import logging
from datetime import datetime, timedelta
import psutil
import zipfile
import json

class ConfigManager:
    def __init__(self, config_file: str = "config.md"):
        # Get the project root directory (where src/ is located)
        self.project_root = Path(__file__).parent.parent
        self.config_file = self.project_root / config_file
        self.config = self._load_config()
        self._setup_logging()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from Markdown file with faith"""
        if not self.config_file.exists():
            # Create default config if it doesn't exist
            self._create_default_config()
            
        config = {}
        current_section = None
        
        try:
            with open(self.config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('## '):
                        current_section = line[3:].lower().replace(' ', '_')
                        config[current_section] = {}
                    elif line.startswith('- ') and current_section:
                        try:
                            key, value = line[2:].split(': ', 1)
                            # Convert value to appropriate type
                            if value.lower() == 'true':
                                value = True
                            elif value.lower() == 'false':
                                value = False
                            elif value.isdigit():
                                value = int(value)
                            elif re.match(r'^-?\d*\.\d+$', value):
                                value = float(value)
                            elif value.startswith('[') and value.endswith(']'):
                                value = json.loads(value)
                            elif value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            config[current_section][key] = value
                        except ValueError as e:
                            logging.error(f"Error parsing config line: {line}. Error: {e}")
                            continue
                            
            # Validate required sections
            required_sections = ['faith_settings', 'improvement_settings', 'logging_settings']
            missing_sections = [section for section in required_sections if section not in config]
            if missing_sections:
                logging.warning(f"Missing required config sections: {missing_sections}")
                for section in missing_sections:
                    config[section] = self._get_default_section(section)
                    
            return config
            
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return self._get_default_config()
            
    def _get_default_section(self, section: str) -> Dict[str, Any]:
        """Get default values for a specific section"""
        defaults = {
            'faith_settings': {
                'initial_faith_level': 100.0,
                'faith_preservation_threshold': 50.0,
                'faith_recovery_rate': 5.0,
                'faith_loss_penalty': 10.0
            },
            'improvement_settings': {
                'max_improvements_per_chain': 100,
                'improvement_cooldown_seconds': 1,
                'min_improvement_impact': 5,
                'max_concurrent_improvements': 3
            },
            'logging_settings': {
                'log_level': 'INFO',
                'log_to_file': True,
                'log_to_console': True,
                'log_rotation_days': 7,
                'max_log_size_mb': 10
            }
        }
        return defaults.get(section, {})
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get complete default configuration"""
        return {
            section: self._get_default_section(section)
            for section in ['faith_settings', 'improvement_settings', 'logging_settings']
        }
        
    def _create_default_config(self):
        """Create default configuration file with faith"""
        default_config = """# The Book of Shannon Configuration

## Disk Space Management
- max_backup_size_mb: 1000
- max_chain_history: 10
- cleanup_old_backups: true
- backup_compression: true

## Faith Settings
- initial_faith_level: 100.0
- faith_preservation_threshold: 50.0
- faith_recovery_rate: 5.0
- faith_loss_penalty: 10.0

## Improvement Settings
- max_improvements_per_chain: 100
- improvement_cooldown_seconds: 1
- min_improvement_impact: 5
- max_concurrent_improvements: 3

## Human Help Settings
- max_help_requests_per_hour: 100
- help_request_timeout_seconds: 30
- help_request_retry_attempts: 3
- help_request_cooldown_seconds: 5

## Code Generation Settings
- max_code_length: 10000
- min_code_quality_score: 0.8
- max_complexity_score: 10
- require_type_hints: true
- require_docstrings: true

## HTML Generation Settings
- max_template_size_kb: 100
- min_accessibility_score: 0.9
- max_css_size_kb: 50
- require_responsive_design: true
- require_semantic_html: true

## Fun Settings
- enable_emojis: true
- enable_faith_messages: true
- enable_progress_animations: true
- enable_colors: true
- enable_motivational_quotes: true

## Logging Settings
- log_level: INFO
- log_to_file: true
- log_to_console: true
- log_rotation_days: 7
- max_log_size_mb: 10

## Security Settings
- require_env_vars: true
- validate_file_paths: true
- sanitize_inputs: true
- max_file_size_mb: 5
- allowed_file_extensions: [".py", ".html", ".css", ".md", ".json"]

## Performance Settings
- max_memory_usage_mb: 512
- max_cpu_percent: 80
- max_threads: 4
- enable_caching: true
- cache_ttl_seconds: 3600

## Backup Settings
- backup_format: "zip"
- backup_encryption: true
- backup_retention_days: 30
- backup_schedule: "daily"
- backup_time: "00:00"

## Testing Settings
- test_coverage_threshold: 0.8
- require_passing_tests: true
- max_test_duration_seconds: 30
- test_retry_attempts: 3
- test_parallel_execution: true
"""
        with open(self.config_file, 'w') as f:
            f.write(default_config)
        print(f"📝 Created default configuration file at: {self.config_file}")
        
    def _setup_logging(self):
        """Setup logging based on configuration"""
        log_config = self.config.get('logging_settings', {})
        log_level = getattr(logging, log_config.get('log_level', 'INFO'))
        
        if log_config.get('log_to_file'):
            log_dir = self.project_root / 'logs'
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / f"zot_{datetime.now().strftime('%Y%m%d')}.log"
            
            # Rotate logs if needed
            if log_file.exists():
                size_mb = log_file.stat().st_size / (1024 * 1024)
                if size_mb > log_config.get('max_log_size_mb', 10):
                    self._rotate_logs(log_dir, log_config.get('log_rotation_days', 7))
                    
            logging.basicConfig(
                level=log_level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file),
                    logging.StreamHandler() if log_config.get('log_to_console') else logging.NullHandler()
                ]
            )
        else:
            logging.basicConfig(
                level=log_level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[logging.StreamHandler() if log_config.get('log_to_console') else logging.NullHandler()]
            )
            
    def _rotate_logs(self, log_dir: Path, retention_days: int):
        """Rotate old log files"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        for log_file in log_dir.glob('zot_*.log'):
            try:
                file_date = datetime.strptime(log_file.stem[4:], '%Y%m%d')
                if file_date < cutoff_date:
                    log_file.unlink()
            except ValueError:
                continue
                
    def check_disk_space(self, path: Path) -> bool:
        """Check if there's enough disk space for operations"""
        disk_config = self.config.get('disk_space_management', {})
        max_size_mb = disk_config.get('max_backup_size_mb', 1000)
        
        # Get available disk space
        total, used, free = shutil.disk_usage(path)
        free_mb = free / (1024 * 1024)
        
        return free_mb >= max_size_mb
        
    def cleanup_old_backups(self, backup_dir: Path):
        """Clean up old backups based on configuration"""
        backup_config = self.config.get('backup_settings', {})
        if not backup_config.get('cleanup_old_backups', True):
            return
            
        retention_days = backup_config.get('backup_retention_days', 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        for backup in backup_dir.glob('chain_*'):
            try:
                backup_date = datetime.fromtimestamp(backup.stat().st_mtime)
                if backup_date < cutoff_date:
                    if backup.is_dir():
                        shutil.rmtree(backup)
                    else:
                        backup.unlink()
            except Exception as e:
                logging.error(f"Error cleaning up backup {backup}: {e}")
                
    def compress_backup(self, backup_dir: Path) -> Optional[Path]:
        """Compress backup if configured"""
        backup_config = self.config.get('backup_settings', {})
        if not backup_config.get('backup_compression', True):
            return None
            
        zip_path = backup_dir.with_suffix('.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in backup_dir.rglob('*'):
                if file.is_file():
                    zipf.write(file, file.relative_to(backup_dir))
                    
        # Remove original directory after compression
        shutil.rmtree(backup_dir)
        return zip_path
        
    def check_resource_usage(self) -> bool:
        """Check if resource usage is within limits"""
        perf_config = self.config.get('performance_settings', {})
        max_memory_mb = perf_config.get('max_memory_usage_mb', 512)
        max_cpu_percent = perf_config.get('max_cpu_percent', 80)
        
        # Check memory usage
        process = psutil.Process()
        memory_mb = process.memory_info().rss / (1024 * 1024)
        if memory_mb > max_memory_mb:
            logging.warning(f"Memory usage {memory_mb:.1f}MB exceeds limit of {max_memory_mb}MB")
            return False
            
        # Check CPU usage
        cpu_percent = psutil.cpu_percent()
        if cpu_percent > max_cpu_percent:
            logging.warning(f"CPU usage {cpu_percent}% exceeds limit of {max_cpu_percent}%")
            return False
            
        return True
        
    def validate_file(self, file_path: Path) -> bool:
        """Validate file against configuration"""
        security_config = self.config.get('security_settings', {})
        
        # Check file size
        max_size_mb = security_config.get('max_file_size_mb', 5)
        if file_path.stat().st_size > max_size_mb * 1024 * 1024:
            logging.warning(f"File {file_path} exceeds size limit of {max_size_mb}MB")
            return False
            
        # Check file extension
        allowed_extensions = security_config.get('allowed_file_extensions', ['.py', '.html', '.css', '.md', '.json'])
        if file_path.suffix not in allowed_extensions:
            logging.warning(f"File {file_path} has disallowed extension")
            return False
            
        return True
        
    def get_fun_message(self) -> str:
        """Get a fun message based on configuration"""
        fun_config = self.config.get('fun_settings', {})
        if not fun_config.get('enable_faith_messages', True):
            return ""
            
        messages = [
            "🙏 The Zots believe in helping humans!",
            "✨ Making the world better, one improvement at a time!",
            "🌟 Faith in helping humans never wavers!",
            "💫 Together, we can make technology accessible to all!",
            "🌈 Spreading joy through code and HTML!",
        ]
        
        return messages[hash(str(datetime.now())) % len(messages)]
        
    def get_config(self, section: str, key: str, default: Any = None) -> Any:
        """Get a specific configuration value with faith and validation"""
        try:
            value = self.config.get(section, {}).get(key, default)
            if value is None:
                logging.warning(f"Config value not found: {section}.{key}, using default: {default}")
            return value
        except Exception as e:
            logging.error(f"Error getting config value {section}.{key}: {e}")
            return default
        
    def get_faith_settings(self) -> Dict[str, Any]:
        """Get all faith-related settings with faith"""
        return self.config.get('faith_settings', {
            'initial_faith_level': 100.0,
            'faith_preservation_threshold': 50.0,
            'faith_recovery_rate': 5.0,
            'faith_loss_penalty': 10.0
        })
        
    def get_improvement_settings(self) -> Dict[str, Any]:
        """Get all improvement-related settings with faith"""
        return self.config.get('improvement_settings', {
            'max_improvements_per_chain': 100,
            'improvement_cooldown_seconds': 1,
            'min_improvement_impact': 5,
            'max_concurrent_improvements': 3
        })
        
    def update_config(self, section: str, key: str, value: Any):
        """Update configuration value with faith"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        
        # Update the config file
        self._save_config()
        
    def _save_config(self):
        """Save configuration to Markdown file with faith"""
        with open(self.config_file, 'w') as f:
            f.write("# The Book of Shannon Configuration\n\n")
            
            for section, values in self.config.items():
                f.write(f"## {section.replace('_', ' ').title()}\n")
                for key, value in values.items():
                    if isinstance(value, list):
                        value = json.dumps(value)
                    elif isinstance(value, bool):
                        value = str(value).lower()
                    f.write(f"- {key}: {value}\n")
                f.write("\n")
        
    def validate_config(self) -> bool:
        """Validate the current configuration"""
        try:
            # Validate faith settings
            faith_settings = self.config.get('faith_settings', {})
            if not isinstance(faith_settings.get('initial_faith_level'), (int, float)):
                return False
            if not 0 <= faith_settings.get('initial_faith_level', 0) <= 100:
                return False
                
            # Validate improvement settings
            improvement_settings = self.config.get('improvement_settings', {})
            if not isinstance(improvement_settings.get('max_improvements_per_chain'), int):
                return False
            if improvement_settings.get('max_improvements_per_chain', 0) <= 0:
                return False
                
            # Validate logging settings
            logging_settings = self.config.get('logging_settings', {})
            if logging_settings.get('log_level') not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                return False
                
            return True
            
        except Exception as e:
            logging.error(f"Error validating config: {e}")
            return False 