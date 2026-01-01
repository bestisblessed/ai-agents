#!/usr/bin/env python3
import sys, os, json, re, tempfile, subprocess
from urllib.request import Request, urlopen

repo_root = os.path.abspath(os.path.expanduser(sys.argv[1]))
task = sys.argv[2]

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
if not OLLAMA_HOST.startswith(("http://", "https://")):
    OLLAMA_HOST = "http://" + OLLAMA_HOST

PLANNER  = os.environ.get("PLANNER_MODEL",  "qwen3:30b-a3b-q4_K_M")
EXECUTOR = os.environ.get("EXECUTOR_MODEL", "qwen3-coder:30b-a3b-q4_K_M")
HELPER   = os.environ.get("HELPER_MODEL",   "rnj-1:8b-instruct-q4_K_M")

planner_sys = (
    "You are the Planner. Output ONLY JSON:\n"
    "{\n"
    '  "plan": ["... up to 8 steps ..."],\n'
    '  "next": {"instruction": "the next concrete step for the executor"}\n'
    "}"
)

executor_sys = (
    "You are the Executor. Use tools via JSON ONLY.\n"
    "Either:\n"
    "{\n"
    '  "action": "tool",\n'
    '  "tool": "list|read|write|grep",\n'
    '  "args": { ... }\n'
    "}\n"
    "OR:\n"
    "{\n"
    '  "action": "done",\n'
    '  "summary": "what you changed / what to do next"\n'
    "}"
)

helper_sys = (
    "You are the Helper/Reviewer. Output ONLY JSON:\n"
    "{\n"
    '  "verdict": "ok" or "needs_fix",\n'
    '  "issues": ["..."],\n'
    '  "next_instruction": "if needs_fix, tell planner what to change"\n'
    "}"
)

req = Request(
    OLLAMA_HOST + "/api/chat",
    data=json.dumps({
        "model": PLANNER,
        "messages": [
            {"role": "system", "content": planner_sys},
            {"role": "user", "content": task},
        ],
        "stream": False,
        "options": {"temperature": 0.2},
    }).encode(),
    headers={"Content-Type": "application/json"},
)

plan_raw = urlopen(req).read().decode("utf-8", errors="replace")
plan_txt = json.loads(plan_raw).get("message", {}).get("content", "")
m = re.search(r"\{.*\}", plan_txt, re.S)
plan = json.loads(m.group(0))

print("PLAN:")
for i, s in enumerate(plan["plan"], 1):
    print(f"{i}. {s}")

instruction = plan["next"]["instruction"]

while True:
    req = Request(
        OLLAMA_HOST + "/api/chat",
        data=json.dumps({
            "model": EXECUTOR,
            "messages": [
                {"role": "system", "content": executor_sys},
                {"role": "user", "content": instruction},
            ],
            "stream": False,
            "options": {"temperature": 0.1},
        }).encode(),
        headers={"Content-Type": "application/json"},
    )

    ex_raw = urlopen(req).read().decode("utf-8", errors="replace")
    ex_txt = json.loads(ex_raw).get("message", {}).get("content", "")
    m = re.search(r"\{.*\}", ex_txt, re.S)
    ex = json.loads(m.group(0))

    if ex["action"] == "tool":
        if ex["tool"] == "write":
            tmp = tempfile.NamedTemporaryFile(delete=False)
            tmp.write(ex["args"]["content"].encode())
            tmp.close()
            instruction = subprocess.check_output(
                ["python3", "tool.py", repo_root, "write", ex["args"]["path"], tmp.name],
                text=True,
            )
            continue

        cmd = ["python3", "tool.py", repo_root, ex["tool"]]
        for v in ex["args"].values():
            cmd.append(str(v))
        instruction = subprocess.check_output(cmd, text=True)
        continue

    if ex["action"] == "done":
        print("\nEXECUTOR DONE:\n", ex["summary"])

        req = Request(
            OLLAMA_HOST + "/api/chat",
            data=json.dumps({
                "model": HELPER,
                "messages": [
                    {"role": "system", "content": helper_sys},
                    {"role": "user", "content": ex["summary"]},
                ],
                "stream": False,
                "options": {"temperature": 0.1},
            }).encode(),
            headers={"Content-Type": "application/json"},
        )

        h_raw = urlopen(req).read().decode("utf-8", errors="replace")
        h_txt = json.loads(h_raw).get("message", {}).get("content", "")
        h = json.loads(re.search(r"\{.*\}", h_txt, re.S).group(0))

        print("\nHELPER:", h["verdict"])
        if h["verdict"] == "ok":
            sys.exit(0)

        instruction = h["next_instruction"]
