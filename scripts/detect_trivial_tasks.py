#!/usr/bin/env python3
"""Detect trivial / extremely-easy tasks for quarantine.

Counts FUNCTIONAL changed lines in the gold patch — excluding:
- Pure-whitespace and blank lines
- Single-character bracket lines  ({, }, [, ], (, ))
- Comment-only lines (# ..., // ..., /* */, * ...)
- Import statements
- Type-annotation-only changes

A task is "trivial" if functional adds + removes < THRESHOLD across
non-docs files.

Usage:
    detect_trivial_tasks.py harbor_tasks/ [--threshold 5] [--quarantine]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Patch parsing
# ---------------------------------------------------------------------------

# Capture EVERYTHING between `git apply - <<'PATCH'`, `patch -p1 << 'PATCH'`,
# `cat <<'EOF' > ...`, etc. and the closing delimiter.
_HEREDOC_RE = re.compile(
    r"(?:git\s+apply|patch\b[^\n]*|cat\s)[^\n]*<<\s*['\"]?(\w+)['\"]?\s*[^\n]*\n(.*?)\n\1\b",
    re.DOTALL,
)

_HUNK_FILE_RE = re.compile(r"^\+\+\+\s+b/([^\s\n]+)", re.MULTILINE)

_DOCS_SUFFIXES = (".md", ".rst", ".txt", ".adoc")
_DOCS_BASENAMES = {
    "CHANGELOG", "CHANGES", "HISTORY", "NOTES", "README",
    "CLAUDE", "AGENTS", "CONTRIBUTING", "LICENSE", "NOTICE", "AUTHORS",
    "CONVENTIONS",
}


def _is_docs(path: str) -> bool:
    p = path.lower()
    if any(p.endswith(s) for s in _DOCS_SUFFIXES):
        return True
    base = path.rsplit("/", 1)[-1].split(".")[0].upper()
    return base in _DOCS_BASENAMES


# Lines we don't count as "functional"
_BRACKET_ONLY = re.compile(r"^[\s{}\[\]()<>;,]*$")
_PY_COMMENT  = re.compile(r"^\s*#")
_C_COMMENT   = re.compile(r"^\s*(//|/\*|\*/?\s|\*$)")
_PY_IMPORT   = re.compile(r"^\s*(from\s+\S+\s+import|import\s+\S)")
_JS_IMPORT   = re.compile(r"^\s*(import\s|export\s+\{|export\s+from|require\s*\()")
_RS_IMPORT   = re.compile(r"^\s*use\s+\S")
_GO_IMPORT   = re.compile(r"^\s*import\s+[\"(]")
_TYPE_ONLY   = re.compile(r"^[\s\w:,?<>|\[\].]*[:|][\s\w?<>|\[\].]+\s*$")  # rough


def _is_trivial_line(line: str) -> bool:
    """Return True if this line contributes nothing meaningful to a fix."""
    body = line[1:] if line and line[0] in "+-" else line
    if not body.strip():
        return True
    if _BRACKET_ONLY.match(body):
        return True
    if _PY_COMMENT.match(body) or _C_COMMENT.match(body):
        return True
    if _PY_IMPORT.match(body) or _JS_IMPORT.match(body) or _RS_IMPORT.match(body) \
       or _GO_IMPORT.match(body):
        return True
    return False


# ---------------------------------------------------------------------------
# Per-task analysis
# ---------------------------------------------------------------------------


def analyze_task(task_dir: Path) -> dict:
    """Extract patch from solve.sh, count functional line changes per file."""
    sv = task_dir / "solution" / "solve.sh"
    if not sv.exists():
        return {"name": task_dir.name, "error": "no solve.sh"}
    text = sv.read_text(errors="ignore")

    # Collect ALL heredoc bodies (some tasks have multiple `git apply` blocks)
    bodies = [m.group(2) for m in _HEREDOC_RE.finditer(text)]
    if not bodies:
        return {"name": task_dir.name, "error": "no patch heredoc"}
    body = "\n".join(bodies)

    # Per-hunk file path (from +++ b/path lines)
    files = _HUNK_FILE_RE.findall(body)
    docs_files = [f for f in set(files) if _is_docs(f)]
    code_files = [f for f in set(files) if not _is_docs(f)]

    # Walk the body line-by-line, tracking current file
    cur = None
    per_file_func: dict[str, int] = {}
    total_adds = 0
    total_removes = 0
    func_adds = 0
    func_removes = 0

    for line in body.splitlines():
        m = re.match(r"^\+\+\+\s+b/(.+)$", line)
        if m:
            cur = m.group(1).strip()
            continue
        if line.startswith("---") or line.startswith("@@") or line.startswith("diff "):
            continue
        if line.startswith("+") and not line.startswith("+++"):
            total_adds += 1
            if not _is_trivial_line(line):
                func_adds += 1
                if cur:
                    per_file_func[cur] = per_file_func.get(cur, 0) + 1
        elif line.startswith("-") and not line.startswith("---"):
            total_removes += 1
            if not _is_trivial_line(line):
                func_removes += 1
                if cur:
                    per_file_func[cur] = per_file_func.get(cur, 0) + 1

    func_total = func_adds + func_removes
    code_func = sum(n for f, n in per_file_func.items() if not _is_docs(f))

    return {
        "name": task_dir.name,
        "files_total": len(set(files)),
        "files_code": len(code_files),
        "files_docs": len(docs_files),
        "raw_adds": total_adds,
        "raw_removes": total_removes,
        "func_adds": func_adds,
        "func_removes": func_removes,
        "func_total": func_total,
        "code_func_lines": code_func,
        "per_file_func": per_file_func,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus", type=Path)
    ap.add_argument("--threshold", type=int, default=5,
                    help="Tasks with code_func_lines below this are TRIVIAL")
    ap.add_argument("--quarantine", action="store_true",
                    help="Move trivial tasks to harbor_tasks_quarantine/")
    ap.add_argument("--out", type=Path, default=Path("/tmp/trivial_analysis.json"))
    args = ap.parse_args()

    rows = []
    for d in sorted(args.corpus.iterdir()):
        if not d.is_dir():
            continue
        rows.append(analyze_task(d))

    # Trivial candidates = parse-succeeded AND any of:
    #   - code_func_lines < threshold (small fix)
    #   - files_code == 0 AND files_docs > 0 (docs-only)
    trivial = [r for r in rows if "error" not in r
               and r["files_total"] > 0
               and (r["code_func_lines"] < args.threshold
                    or (r["files_code"] == 0 and r["files_docs"] > 0))]
    no_patch = [r for r in rows if "error" in r]
    healthy  = [r for r in rows if "error" not in r and r["code_func_lines"] >= args.threshold]

    print(f"=== Corpus: {args.corpus} ===")
    print(f"  total      : {len(rows)}")
    print(f"  no patch   : {len(no_patch)}")
    print(f"  trivial   : {len(trivial)}  (code_func_lines < {args.threshold})")
    print(f"  healthy    : {len(healthy)}")

    # Bucket trivial by line count
    buckets = {}
    for r in trivial:
        buckets[r["code_func_lines"]] = buckets.get(r["code_func_lines"], 0) + 1
    print("\nTrivial line-count distribution:")
    for k in sorted(buckets):
        print(f"  {k} func line(s) of code: {buckets[k]} tasks")

    args.out.write_text(json.dumps(
        {"trivial": trivial, "no_patch": no_patch, "summary": {
            "trivial": len(trivial), "no_patch": len(no_patch),
            "healthy": len(healthy), "total": len(rows),
        }},
        indent=2,
    ))
    print(f"\nFull analysis → {args.out}")

    if args.quarantine:
        quarantine_dir = Path("harbor_tasks_quarantine")
        quarantine_dir.mkdir(exist_ok=True)
        manifest_path = quarantine_dir / "MANIFEST.json"
        manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

        moved = 0
        for r in trivial:
            src = args.corpus / r["name"]
            dst = quarantine_dir / r["name"]
            if not src.exists() or dst.exists():
                continue
            src.rename(dst)
            manifest.setdefault(r["name"], [])
            if "trivial_pr" not in manifest[r["name"]]:
                manifest[r["name"]].append("trivial_pr")
            moved += 1

        manifest_path.write_text(json.dumps(dict(sorted(manifest.items())), indent=2))
        # Refresh INDEX.txt
        all_q = sorted([d.name for d in quarantine_dir.iterdir()
                        if d.is_dir() and not d.name.startswith("_")])
        (quarantine_dir / "INDEX.txt").write_text("\n".join(all_q) + "\n")
        print(f"\nQuarantined {moved} trivial tasks. Total quarantine: {len(all_q)}")


if __name__ == "__main__":
    main()
