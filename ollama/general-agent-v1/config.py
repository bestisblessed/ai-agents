# Agent Configuration File
# This file configures the multi-model agent system.
# You can comment/uncomment lines to easily enable/disable options.

# planner_model - Model name for planning
# executor_model - Model name for execution
# helper_model - Model name for review
# ollama_host - Ollama server URL
# temperature - Randomness (0.0-2.0, lower = more deterministic)
# num_ctx - Context window size (e.g., 4096, 8192, 32768)
# num_predict - Max tokens to generate (e.g., 512, 1024, 2048)
# top_p - Nucleus sampling (0.0-1.0, typically 0.9-0.95)
# top_k - Top-k sampling (e.g., 40, 50)
# repeat_penalty - Penalty for repetition (1.0-1.5, typically 1.1-1.2)
# seed - Random seed for reproducibility
# Workflow Options:
# max_iters - Maximum iterations before timeout (default: 12)

#planner_model = "qwen3:14b-q4_K_M"
planner_model = "gpt-oss:20b"
# executor_model = "qwen3-coder:30b-a3b-q4_K_M"
executor_model = "qwen3:14b-q4_K_M"
# executor_model = "rnj-1:8b-instruct-q4_K_M"
# executor_model = "rnj-1:8b-instruct-q4_K_M"
# executor_model = "qwen3-coder:480b-cloud"
helper_model = "rnj-1:8b-instruct-q4_K_M"
ollama_host = "http://localhost:11434"
max_iters = 12
planner_options = {
    "temperature": 0.2,
    "num_ctx": 4096,
    "num_predict": 4096,
    # "top_p": 0.9,
    # "top_k": 40,
    # "repeat_penalty": 1.1,
    # "seed": None,
}
executor_options = {
    "temperature": 0.2,
    "num_ctx": 4096,
    "num_predict": 4096,
    "repeat_penalty": 1.1,
    # "top_p": 0.95,
    # "top_k": 40,
    # "seed": None,
}
helper_options = {
    "temperature": 0.2,
    "num_predict": 4096,
    # "num_ctx": 4096,
    # "top_p": 0.9,
    # "top_k": 40,
    # "repeat_penalty": 1.1,
    # "seed": None,
}
