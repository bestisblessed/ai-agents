#!/usr/bin/env python3
import sys, re
from pathlib import Path

repo_root = Path(sys.argv[1]).expanduser().resolve()
tool = sys.argv[2]

if tool == "list":
    subdir = sys.argv[3] if len(sys.argv) > 3 else "."
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 200
    base = (repo_root / subdir).resolve()
    out = []
    i = 0
    for p in sorted(base.rglob("*")):
        if p.is_file():
            out.append(str(p.relative_to(repo_root)))
            i += 1
            if i >= limit:
                out.append(f"... (truncated at {limit})")
                break
    print("\n".join(out))
    sys.exit(0)

if tool == "read":
    rel = sys.argv[3]
    max_bytes = int(sys.argv[4]) if len(sys.argv) > 4 else 120000
    p = (repo_root / rel).resolve()
    b = p.read_bytes()
    suffix = "\n... (truncated)\n" if len(b) > max_bytes else ""
    sys.stdout.write(b[:max_bytes].decode("utf-8", errors="replace") + suffix)
    sys.exit(0)

if tool == "write":
    rel = sys.argv[3]
    content_file = sys.argv[4]
    p = (repo_root / rel).resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    content = Path(content_file).read_text(encoding="utf-8", errors="replace")
    p.write_text(content, encoding="utf-8")
    print(f"WROTE {rel}")
    sys.exit(0)

if tool == "grep":
    pattern = sys.argv[3]
    subdir = sys.argv[4] if len(sys.argv) > 4 else "."
    limit = int(sys.argv[5]) if len(sys.argv) > 5 else 50
    base = (repo_root / subdir).resolve()
    rx = re.compile(pattern)
    hits = []
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        ln = 0
        for line in text.splitlines():
            ln += 1
            if rx.search(line):
                hits.append(f"{p.relative_to(repo_root)}:{ln}: {line[:240]}")
                if len(hits) >= limit:
                    hits.append(f"... (truncated at {limit})")
                    print("\n".join(hits))
                    sys.exit(0)
    print("\n".join(hits) if hits else "(no matches)")
    sys.exit(0)

print("unknown tool")
sys.exit(1)
