# Agent Configuration File
# This file configures the multi-model agent system.
# You can comment/uncomment lines to easily enable/disable options.

planner_model = "qwen3:14b-q4_K_M"
executor_model = "qwen3-coder:30b-a3b-q4_K_M"
helper_model = "rnj-1:8b-instruct-q4_K_M"
ollama_host = "http://localhost:11434"
max_iters = 12
planner_options = {
    "temperature": 0.2,      # Randomness (0.0-2.0, lower = more deterministic)
    "num_ctx": 8192,        # Context window size (tokens)
    "num_predict": 4096,     # Max tokens to generate per response
    # "top_p": 0.9,         # Nucleus sampling (0.0-1.0)
    # "top_k": 40,          # Top-k sampling
    # "repeat_penalty": 1.1, # Penalty for repetition (1.0-1.5)
    # "seed": None,          # Random seed for reproducibility
}
executor_options = {
    "temperature": 0.1,      # Very low for deterministic code
    "num_ctx": 16384,        # Larger context for code files
    "num_predict": 8192,     # Allow longer code responses
    "repeat_penalty": 1.1,   # Reduce repetition in code
    # "top_p": 0.95,
    # "top_k": 40,
    # "seed": None,
}
helper_options = {
    "temperature": 0.1,      # Low temperature for consistent reviews
    "num_predict": 2048,       # Short, focused reviews
    # "num_ctx": 4096,
    # "top_p": 0.9,
    # "top_k": 40,
    # "repeat_penalty": 1.1,
    # "seed": None,
}
