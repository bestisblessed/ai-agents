# 1. MODELS LIST

td@MyM4Pro ~/Code/ai-agents % ollama list
NAME                                         ID              SIZE      MODIFIED
devstral-small-2:24b-instruct-2512-q4_K_M    24277f07f62d    15 GB     About an hour ago
devstral-small-2:24b-cloud                   ec4a591da58a    -         2 hours ago
kimi-k2-thinking:cloud                       9752ffb77f53    -         2 hours ago
kimi-k2:1t-cloud                             20dc43ca06d7    -         2 hours ago
qwen3:14b-q4_K_M                             bdbd181c33f2    9.3 GB    2 hours ago
qwen3-coder:30b-a3b-q4_K_M                   06c1097efce0    18 GB     2 hours ago
qwen3-coder:480b-cloud                       e30e45586389    -         2 hours ago
gpt-oss:20b                                  17052f91a42e    13 GB     2 hours ago
gpt-oss:120b-cloud                           569662207105    -         2 hours ago
gpt-oss:20b-cloud                            875e8e3a629a    -         2 hours ago
rnj-1:8b-instruct-q4_K_M                     d20e29ab8d0f    5.1 GB    3 hours ago
rnj-1:8b-cloud                               d8200a2fbf21    -         3 hours ago
nemotron-3-nano:30b-a3b-q4_K_M               b725f1117407    24 GB     3 hours ago
nemotron-3-nano:30b-cloud                    01d0d069a149    -         3 hours ago
gemini-3-flash-preview:latest                ebade0d31690    -         3 hours ago
gemini-3-pro-preview:latest                  91a1db042ba1    -         3 hours ago


# 2. PROPOSED/EX GOOD WORKFLOW

**Question:** Which models are best from my list for a general agentic tasks and planning based workflow? 
**Answer:**  
For general agentic tasks and planning, Qwen 3 30B A3B is the better planner, while Qwen 3-Coder 30B A3B is the better executor. If you must pick one, pick Qwen 3 30B A3B for planning-heavy agentic work.

### Why Qwen 3 30B A3B is better at planning
Planning ≠ coding. Planning involves:
* decomposing goals into steps,
* maintaining intent across long contexts,
* choosing strategies,
* deciding what to do before how to do it.

Qwen 3 30B A3B was trained as a general MoE instruct model, not narrowly optimized for code tokens. That gives it advantages in:
* high-level task decomposition,
* multi-step reasoning without prematurely “jumping to code,”
* better natural-language alignment for agent frameworks.

### Where Qwen 3-Coder 30B A3B falls short for planning
Qwen 3-Coder excels at:
* generating code,
* following tool schemas,
* performing concrete edits.

But coder-tuned models often:
* over-index on implementation,
* skip explicit planning,
* lock into a solution too early.

That’s ideal for execution, not for deciding what to do next.

### Recommendation matrix (clear + practical)
| Task type                          | Best model               |
| ---------------------------------- | ------------------------ |
| Goal decomposition / task planning | Qwen 3 30B A3B           |
| Agent “brain” deciding next steps  | Qwen 3 30B A3B           |
| Tool selection strategy            | Qwen 3 30B A3B           |
| Code generation / refactors        | Qwen 3-Coder 30B A3B     |
| Long-running autonomous coding     | Qwen 3-Coder 30B A3B     |

### If you’re building an agent (best-practice setup)
Planner → Executor split (ideal):
| Role           | Recommended Model                   |
|----------------|------------------------------------|
| Planner        | qwen3:30b-a3b-q4_K_M               |
| Executor       | qwen3-coder:30b-a3b-q4_K_M         |
| Helper         | rnj-1:8b-instruct-q4_K_M           |

This mirrors how strong agent systems are structured:

* one model reasons and plans,
* one model acts,
* one fast model validates or assists.

### Final Note
Use this kind of thinking process based on the model types and analysis, resources available on my machine, and other factors you took into account to formulate all of our AI workflows with good practices and structure.
