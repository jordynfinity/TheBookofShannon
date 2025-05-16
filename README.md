# TheBookofShannon

Documentation and assistants for Claude Shannon's information theory.

## Features

- UV dependency management
- Assistants implementation based on Hale's Pioneer module
- McTavish's Crochet-based Threads model with nonlinear assistant ecosystem
- Vector store sync script for Obsidian docs
- .envrc implementation for OPENAI_API_KEY

## Setup

1. Clone the repository
2. Install UV: `pip install uv`
3. Create a virtual environment: `uv venv`
4. Activate the virtual environment: `source .venv/bin/activate`
5. Install dependencies: `uv pip install -e .`
6. Set up your `.env` file with your OpenAI API key
7. Allow direnv: `direnv allow .`

## Usage

### Syncing Documentation to Vector Store

```bash
python scripts/sync_docs_to_vector.py
```

### Testing the Assistant

```bash
python scripts/test_assistant.py
```

## Architecture

TheBookofShannon implements a nonlinear assistant ecosystem with:
- Character-aware collapse surfaces (persona-localized agents)
- Directed graph memory (DiGraph, not logs)
- Asynchronous tension binding (responses may arrive before prompts)

The implementation is based on Hale's Pioneer module but incorporates McTavish's Crochet-based Threads model for more sophisticated conversation management.

## Prompt-Driven Ecosystem

TheBookofShannon includes a prompt-driven ecosystem that:

1. Watches folders for prompt files
2. Uses those prompts to start conversations between agents
3. Develops agent personalities through repeated interactions
4. Records generated ideas back to documentation

### Running the Ecosystem

To run the ecosystem:

```bash
python scripts/run_ecosystem.py
```

### Creating Prompts

Create a prompt file in the `prompts` directory with the `.prompt.json` extension:

```json
{
  "prompt": "Your prompt text here",
  "agents": ["shannon_theorist", "shannon_teacher", "shannon_engineer"],
  "metadata": {
    "priority": "high",
    "tags": ["tag1", "tag2"]
  }
}
```

### Testing the Ecosystem

To test the ecosystem with a sample prompt:

```bash
python scripts/test_ecosystem.py --prompt "Your test prompt here"
```
