#!/bin/bash

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Error: Ollama server is not running."
    echo "Please start it manually with: ollama serve"
    echo "Then run this script again."
    exit 1
fi

echo "Ollama server is running. Starting agent..."

# Run the agent with provided arguments
python3 agent.py "$@"

### 1. Run it on a repo
# ```bash
# python3 agent.py ~/Code/ai-agents "Create a responsive landing page in index.html with hero, 3 feature cards, pricing, and FAQ accordion. No frameworks."
# ./run.sh ~/Code/ai-agents "Create a responsive landing page in index.html with hero, 3 feature cards, pricing, and FAQ accordion. No frameworks."
# ```

### 2. Swap in smaller planning models (when 30B is too heavy)
# You can keep the same workflow, just change env vars:
# Fast planner:
# ```bash
# export PLANNER_MODEL="qwen3:8b-q4_K_M"
# ```
# Smaller “thinking” planner:
# ```bash
# export PLANNER_MODEL="qwen3:4b-thinking-2507-q4_K_M"
# ```
# Then run again.

### 3. Make it feel “agentic”
# What makes it agentic is **tool loops**. The executor will repeatedly:
# * `list_files` → discover structure
# * `read_file` → gather context
# * `write_file` → apply changes
# * `grep` → verify / find references
#   …and the helper will gate quality.
# Next upgrade (if you want it): add an `apply_patch` tool (unified diff) and a `run_tests` tool (limited allowlist), so the executor can modify code without rewriting full files and can validate changes automatically.
