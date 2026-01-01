# Minimal Ollama Agent (Planner → Executor → Helper)

## Requirements
- Python 3.9+
- Ollama running locally

## Setup
```bash
brew install ollama
ollama serve
ollama pull qwen3:30b-a3b-q4_K_M
ollama pull qwen3-coder:30b-a3b-q4_K_M
ollama pull rnj-1:8b-instruct-q4_K_M
```

## Make executable
```bash
chmod +x agent.py tool.py
```

## Run example
```bash
python3 agent.py ~/Code/test-repo "Create index.html with a hero section and pricing table"
```

## Swap planner (optional)
```bash
export PLANNER_MODEL=qwen3:8b-q4_K_M
```
