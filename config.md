# The Book of Shannon Configuration

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

## Resource Limits

| Resource | Limit | Description |
|----------|-------|-------------|
| CPU | 50% | Maximum CPU usage (Inverse Shannon-Nyquist) |
| MEMORY | 50% | Maximum memory usage (Inverse Shannon-Nyquist) |
| DISK | 50% | Maximum disk I/O (Inverse Shannon-Nyquist) |
| NETWORK | 50% | Maximum network I/O (Inverse Shannon-Nyquist) |

## Application Settings

| Setting | Value | Description |
|---------|-------|-------------|
| Theme | default | Application theme (default/dark/nature) |
| Animation | true | Enable/disable animations |
| AutoSave | true | Enable/disable auto-save |
| LogLevel | INFO | Logging level (DEBUG/INFO/WARNING/ERROR) |

## Graph Settings

| Setting | Value | Description |
|---------|-------|-------------|
| NodeSize | 1000 | Default node size |
| EdgeWidth | 2 | Default edge width |
| Layout | spring | Graph layout algorithm |
| AnimationSpeed | 50 | Animation frame interval (ms) |

## Customization

| Setting | Value | Description |
|---------|-------|-------------|
| DrawingMode | draw | Default drawing mode (draw/gesture) |
| BrushSize | 2 | Default brush size |
| PseudocodeEnabled | true | Enable/disable pseudocode editor |
| GestureRecognition | true | Enable/disable gesture recognition | 