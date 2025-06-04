# The Book of Shannon

A quantum-inspired wave-based visualization and improvement system that uses Russelian Collapse for bug prevention and continuous improvement.

## Features

### Core Components

- **WaveZot**: Base component for wave-based visualizations and interactions
- **FirstZot & SecondZot**: Specialized Zots for different aspects of the system
- **GodInterface**: Central coordinator that manages all components
- **EventBus**: Centralized event system for component communication
- **EiraAssistant**: AI-powered code analysis and improvement suggestions

### Key Features

1. **Wave Mechanics**
   - Real-time wave visualization
   - Interactive wave manipulation
   - Audio synthesis from wave patterns

2. **Improvement System**
   - Russelian Collapse for bug prevention
   - Continuous code improvement
   - Parallel test execution
   - Automated improvement generation

3. **Event System**
   - Centralized event bus
   - Event history tracking
   - Component communication
   - Debug monitoring

4. **AI Integration**
   - Eira Calder's expertise for code analysis
   - Automated bug detection
   - Improvement suggestions
   - Performance optimization

## Architecture

### Component Communication

The system uses an event-driven architecture with the following components:

```
[EventBus] <-- [GodInterface]
    ^            ^
    |            |
    v            v
[WaveZot] <-- [FirstZot]
    ^            ^
    |            |
    v            v
[SecondZot] <-- [EiraAssistant]
```

### Event Types

- **Wave Events**: `wave_interaction`, `wave_update`
- **Zot Events**: `zot_state_change`, `zot_improvement`
- **Test Events**: `test_result`, `improvement_suggestion`
- **Debug Events**: `debug_metric`
- **Eira Events**: `eira_analysis`, `eira_error`, `eira_debug_suggestions`, `eira_improvement_suggestions`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/TheBookofShannon.git
cd TheBookofShannon
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the main application:
```bash
python src/I\ am\ the\ GUI\ GOD.py
```

### Configuration

The system uses a configuration system managed by `ConfigManager`. Key configuration files:
- `config.json`: Main configuration file
- `config.md`: Configuration documentation
- `logs/`: Directory for log files

### Logging

Logs are stored in the `logs/` directory:
- `event_bus.log`: Event system logs
- `gui.log`: Main application logs
- `eira_assistant.log`: AI analysis logs
- `config_manager.log`: Configuration system logs

## Development

### Testing

Run the test suite:
```bash
python -m pytest tests/
```

### Adding New Components

1. Create a new component class
2. Subscribe to relevant events in the EventBus
3. Implement required interfaces
4. Add tests in `tests/`

### Event System

To add new events:
1. Define event type in component
2. Subscribe to events in GodInterface
3. Implement event handlers
4. Update documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Eira Calder for AI expertise
- Quantum computing concepts
- Wave mechanics
- Russelian Collapse theory
