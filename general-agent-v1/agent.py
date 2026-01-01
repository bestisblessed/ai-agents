#!/usr/bin/env python3
"""
Minimal multi-model local agent for Ollama.

Planner  -> qwen3:30b-a3b-q4_K_M
Executor -> qwen3-coder:30b-a3b-q4_K_M
Helper   -> rnj-1:8b-instruct-q4_K_M

Requires: Python 3.9+ (standard library only). No external deps.
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

_raw_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
DEFAULT_OLLAMA = _raw_host if _raw_host.startswith(("http://", "https://")) else f"http://{_raw_host}"


def ollama_chat(
    model: str,
    messages: List[Dict[str, str]],
    *,
    host: str = DEFAULT_OLLAMA,
    temperature: float = 0.2,
    num_ctx: Optional[int] = None,
    stream: bool = False,
    timeout_s: int = 600,
) -> str:
    """Calls Ollama's /api/chat endpoint and returns assistant content."""
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": stream,
        "options": {"temperature": temperature},
    }
    if num_ctx is not None:
        payload["options"]["num_ctx"] = int(num_ctx)

    data = json.dumps(payload).encode("utf-8")
    req = Request(
        url=f"{host}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=timeout_s) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except HTTPError as e:
        raise RuntimeError(
            f"Ollama HTTPError {e.code}: {e.read().decode('utf-8', errors='replace')}"
        ) from e
    except URLError as e:
        raise RuntimeError(f"Could not reach Ollama at {host}. Is `ollama serve` running? ({e})") from e

    try:
        obj = json.loads(body)
        return obj.get("message", {}).get("content", "")
    except json.JSONDecodeError:
        return body


@dataclass
class ToolResult:
    ok: bool
    output: str


class RepoTools:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def _safe_path(self, rel: str) -> Path:
        p = (self.root / rel).resolve()
        if not str(p).startswith(str(self.root)):
            raise ValueError("Path escapes repo root.")
        return p

    def list_files(self, subdir: str = ".", limit: int = 200) -> ToolResult:
        base = self._safe_path(subdir)
        if not base.exists():
            return ToolResult(False, f"Not found: {subdir}")
        out: List[str] = []
        for i, p in enumerate(sorted(base.rglob("*"))):
            if i >= limit:
                out.append(f"... (truncated at {limit})")
                break
            if p.is_file():
                out.append(str(p.relative_to(self.root)))
        return ToolResult(True, "\n".join(out))

    def read_file(self, path: str, max_bytes: int = 120_000) -> ToolResult:
        p = self._safe_path(path)
        if not p.exists() or not p.is_file():
            return ToolResult(False, f"Not found: {path}")
        b = p.read_bytes()
        suffix = "\n... (truncated)\n" if len(b) > max_bytes else ""
        b = b[:max_bytes]
        return ToolResult(True, b.decode("utf-8", errors="replace") + suffix)

    def write_file(self, path: str, content: str) -> ToolResult:
        p = self._safe_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return ToolResult(True, f"Wrote {path} ({len(content)} chars)")

    def grep(self, pattern: str, subdir: str = ".", limit: int = 50) -> ToolResult:
        base = self._safe_path(subdir)
        if not base.exists():
            return ToolResult(False, f"Not found: {subdir}")
        rx = re.compile(pattern)
        hits: List[str] = []
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for ln, line in enumerate(text.splitlines(), start=1):
                if rx.search(line):
                    hits.append(f"{p.relative_to(self.root)}:{ln}: {line[:240]}")
                    if len(hits) >= limit:
                        hits.append(f"... (truncated at {limit})")
                        return ToolResult(True, "\n".join(hits))
        return ToolResult(True, "\n".join(hits) if hits else "(no matches)")


def extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    """Find first JSON object in a text blob."""
    t = text.strip()
    if t.startswith("{") and t.endswith("}"):
        try:
            return json.loads(t)
        except json.JSONDecodeError:
            pass

    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    for i in range(start, len(text)):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                chunk = text[start : i + 1]
                try:
                    return json.loads(chunk)
                except json.JSONDecodeError:
                    return None
    return None


PLANNER_SYS = """You are the Planner. Produce a short plan and decide the next concrete step.
You MUST output a single JSON object with this schema:
{
  "plan": ["step 1", "step 2", "..."],
  "next": {"action": "ask_executor", "instruction": "<what the executor should do next>"},
  "notes": "<optional>"
}
Keep the plan <= 8 steps. Make next instruction specific and verifiable.
"""

EXECUTOR_SYS = """You are the Executor. Implement the next step using available tools.
You MUST output a single JSON object:

Option A (tool call):
{
  "action": "tool",
  "tool": "<list_files|read_file|write_file|grep>",
  "args": { ... },
  "why": "<1 sentence>"
}

Option B (done):
{
  "action": "done",
  "summary": "<what changed / what to do next>",
  "files_changed": ["path1", "path2"]
}

Never invent file contents. If you need context, call read_file or list_files first.
"""

HELPER_SYS = """You are the Helper/Reviewer. Review the executor result and catch mistakes.
You MUST output a single JSON object:
{
  "verdict": "ok" | "needs_fix",
  "issues": ["..."],
  "suggestions": ["..."]
}
Be concise and concrete.
"""


@dataclass
class Models:
    planner: str
    executor: str
    helper: str


def dispatch_tool(tools: RepoTools, tool: str, args: Dict[str, Any]) -> ToolResult:
    if tool == "list_files":
        return tools.list_files(subdir=str(args.get("subdir", ".")), limit=int(args.get("limit", 200)))
    if tool == "read_file":
        return tools.read_file(path=str(args["path"]), max_bytes=int(args.get("max_bytes", 120_000)))
    if tool == "write_file":
        return tools.write_file(path=str(args["path"]), content=str(args.get("content", "")))
    if tool == "grep":
        return tools.grep(pattern=str(args["pattern"]), subdir=str(args.get("subdir", ".")), limit=int(args.get("limit", 50)))
    return ToolResult(False, f"Unknown tool: {tool}")


def run_workflow(repo_root: Path, task: str, models: Models, host: str = DEFAULT_OLLAMA, max_iters: int = 12) -> None:
    tools = RepoTools(repo_root)

    # Planner
    planner_msgs = [
        {"role": "system", "content": PLANNER_SYS},
        {"role": "user", "content": f"Task: {task}\nRepo root: {repo_root}"},
    ]
    plan_obj = extract_json_object(ollama_chat(models.planner, planner_msgs, host=host, temperature=0.2))
    if not plan_obj:
        raise RuntimeError("Planner did not return valid JSON.")
    plan = plan_obj.get("plan", [])
    instruction = (plan_obj.get("next") or {}).get("instruction", "") or task

    print("=== PLAN ===")
    for i, s in enumerate(plan, start=1):
        print(f"{i}. {s}")
    print("\n=== EXECUTE ===")

    files_changed: List[str] = []
    executor_history: List[Dict[str, str]] = [{"role": "system", "content": EXECUTOR_SYS}]
    helper_history: List[Dict[str, str]] = [{"role": "system", "content": HELPER_SYS}]

    for it in range(1, max_iters + 1):
        executor_history.append({"role": "user", "content": f"Iteration {it}. Instruction: {instruction}"})
        raw = ollama_chat(models.executor, executor_history, host=host, temperature=0.1)
        obj = extract_json_object(raw) or {"action": "done", "summary": f"Executor returned non-JSON:\n{raw[:1000]}", "files_changed": []}

        if obj.get("action") == "tool":
            tool = obj.get("tool", "")
            args = obj.get("args", {}) or {}
            tr = dispatch_tool(tools, tool, args)

            executor_history.append({"role": "assistant", "content": raw})
            executor_history.append({"role": "user", "content": f"Tool result ({tool}):\n{tr.output}"})

            if tool == "write_file" and isinstance(args, dict) and "path" in args:
                files_changed.append(str(args["path"]))
            continue

        if obj.get("action") == "done":
            files_changed = list(dict.fromkeys(files_changed + (obj.get("files_changed") or [])))
            summary = obj.get("summary", "(no summary)")
            print(summary)

            # Helper review
            helper_history.append({"role": "user", "content": f"Task: {task}\nExecutor summary:\n{summary}\nFiles changed: {files_changed}"})
            hraw = ollama_chat(models.helper, helper_history, host=host, temperature=0.1)
            hobj = extract_json_object(hraw) or {"verdict": "needs_fix", "issues": ["Helper returned non-JSON"], "suggestions": []}

            print("\n=== REVIEW ===")
            print(f"Verdict: {hobj.get('verdict')}")
            for x in hobj.get("issues", []):
                print(f"- {x}")
            if hobj.get("suggestions"):
                print("Suggestions:")
                for x in hobj["suggestions"]:
                    print(f"- {x}")

            if hobj.get("verdict") == "ok":
                print("\n✅ Done.")
                return

            # Ask planner for updated instruction
            planner_msgs.append({"role": "assistant", "content": json.dumps(plan_obj)})
            planner_msgs.append({"role": "user", "content": f"Helper verdict needs_fix. Issues: {hobj.get('issues')}. Update next instruction."})
            plan_obj2 = extract_json_object(ollama_chat(models.planner, planner_msgs, host=host, temperature=0.2))
            if plan_obj2 and (plan_obj2.get("next") or {}).get("instruction"):
                plan_obj = plan_obj2
                instruction = plan_obj2["next"]["instruction"]
                print("\n=== UPDATED INSTRUCTION ===")
                print(instruction)
                continue

            instruction = "Fix the issues: " + "; ".join(hobj.get("issues") or ["unknown"])
            continue

        raise RuntimeError(f"Unknown executor action: {obj.get('action')}")

    raise RuntimeError(f"Max iterations reached ({max_iters}).")


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print("Usage: agent.py <task...>")
        return 2

    repo_root = Path.cwd()
    task = " ".join(argv[1:]).strip()

    models = Models(
        planner=os.environ.get("PLANNER_MODEL", "qwen3:14b-q4_K_M"),
        executor=os.environ.get("EXECUTOR_MODEL", "qwen3-coder:30b-a3b-q4_K_M"),
        helper=os.environ.get("HELPER_MODEL", "rnj-1:8b-instruct-q4_K_M"),
    )

    print(f"Ollama host: {DEFAULT_OLLAMA}")
    print(f"Planner:  {models.planner}")
    print(f"Executor: {models.executor}")
    print(f"Helper:   {models.helper}")
    run_workflow(repo_root, task, models)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
