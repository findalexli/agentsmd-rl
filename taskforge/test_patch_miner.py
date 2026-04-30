#!/usr/bin/env python3
"""Mine test_patch from a task's solve.sh: extract the gold patch, identify test
files added/modified, and emit per-test f2p signals.

Output JSON shape (per task):
  {
    "task": "...",
    "test_files": [{
        "path": "tests/test_foo.py",
        "added_tests": [
          {"name": "test_bug_fix",         "kind": "f2p", "framework": "pytest"},
          {"name": "test_already_existed", "kind": "p2p", "framework": "pytest"},
        ]
    }, ...],
    "n_added_tests": 5,
    "errors": []
  }

We do NOT distinguish base/merge here (no API calls). We assume:
  - PURELY ADDED tests in test_*.py / *.test.ts → f2p (the PR added them
    specifically to gate the fix)
  - MODIFIED existing tests → could be either. Default p2p; if the modification
    flips an `assert ... == X` to `assert ... == Y`, mark f2p.

Recognized frameworks: pytest, unittest, jest/vitest (`it("...")`,
`describe("...", () => ...)`, `test("...")`), Rust (`#[test]`, `#[tokio::test]`),
Go (`func TestX(t *testing.T)`).

This module is API-free — purely parses files on disk.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Patch extraction (handles all three observed forms in our solve.sh files)
# ---------------------------------------------------------------------------

def extract_patch(solve_sh_text: str, task_dir: Path | None = None) -> str:
    """Return the gold-patch diff body, or "" if not found.

    Forms handled:
      1) `git apply <<'PATCH' ... PATCH`           (most common)
      2) `cat <<'PATCH' | git apply -` ... PATCH   (variant)
      3) `git apply /solution/patch.diff`          (external file at task_dir/solution/patch.diff)
      4) Multiple `cat > <path> <<'EOF' ... EOF`  (file-by-file gen, no diff)
    """
    # Form 1
    m = re.search(r"git\s+apply.*?<<\s*'(\w+)'\n(.*?)\n\1\b", solve_sh_text, re.S)
    if m:
        return m.group(2)
    # Form 2 (cat ... | git apply -)
    m = re.search(r"cat\s+<<\s*'(\w+)'\s*\|\s*git\s+apply\s*-?\s*\n(.*?)\n\1\b",
                  solve_sh_text, re.S)
    if m:
        return m.group(2)
    # Form 3 (external patch.diff)
    if task_dir:
        for cand in ("solution/patch.diff", "patch.diff"):
            p = task_dir / cand
            if p.exists():
                try: return p.read_text()
                except: pass
    # Form 4 (multi-cat) — fabricate a synthetic patch from the cat blocks
    blocks = list(re.finditer(r"cat\s*>\s*([^\s]+)\s*<<\s*'(\w+)'\n(.*?)\n\2\b",
                              solve_sh_text, re.S))
    if blocks:
        out_parts = []
        for m in blocks:
            path = m.group(1).strip().lstrip("/")
            content = m.group(3)
            # Synthesize a unified diff (assume new file)
            out_parts.append(f"diff --git a/{path} b/{path}\nnew file mode 100644\n--- /dev/null\n+++ b/{path}\n")
            for line in content.splitlines():
                out_parts.append("+" + line + "\n")
        return "".join(out_parts)
    return ""


# ---------------------------------------------------------------------------
# Per-line file extraction + per-test-name parsing
# ---------------------------------------------------------------------------

_TEST_FILE_PAT = re.compile(
    r"(?:^|/)(?:test_[\w\-]+\.py|tests?/[\w\-/]+\.py|"
    r"[\w\-]+\.(?:test|spec)\.(?:ts|tsx|js|jsx|cjs|mjs)|"
    r"__tests?__/[\w\-/]+\.(?:ts|tsx|js|jsx|py|rs)|"
    r"[\w\-/]+_test\.go|"
    r"tests/[\w\-/]+\.rs)$",
    re.IGNORECASE,
)


def is_test_file(path: str) -> bool:
    return bool(_TEST_FILE_PAT.search(path))


def file_framework(path: str) -> str:
    p = path.lower()
    if p.endswith(".py"): return "pytest"
    if p.endswith((".ts", ".tsx", ".cjs", ".mjs", ".js", ".jsx")):
        if "vitest" in p or ".vitest." in p: return "vitest"
        if "jest" in p or ".jest." in p: return "jest"
        return "vitest_or_jest"
    if p.endswith(".rs"): return "cargo_test"
    if p.endswith(".go"): return "go_test"
    return "unknown"


# Test-function name patterns by framework
_TEST_NAME_PATTERNS = {
    "pytest":           re.compile(r"^\+\s*def\s+(test_\w+)\s*\("),
    "vitest_or_jest":   re.compile(r"^\+\s*(?:it|test)\s*\(\s*['\"`]([^'\"`]+)['\"`]"),
    "jest":             re.compile(r"^\+\s*(?:it|test)\s*\(\s*['\"`]([^'\"`]+)['\"`]"),
    "vitest":           re.compile(r"^\+\s*(?:it|test)\s*\(\s*['\"`]([^'\"`]+)['\"`]"),
    "cargo_test":       re.compile(r"^\+\s*(?:#\[(?:tokio::)?test\][\s\S]?)\s*fn\s+(\w+)"),
    "go_test":          re.compile(r"^\+\s*func\s+(Test\w+)\s*\("),
    "unknown":          re.compile(r"^\+\s*(?:def\s+(test_\w+)|"
                                   r"(?:it|test)\s*\(\s*['\"`]([^'\"`]+)['\"`]|"
                                   r"func\s+(Test\w+))"),
}


def parse_added_tests(file_path: str, file_diff_block: str) -> list[dict]:
    """Given the diff hunks for ONE file, return {name, framework, kind} for
    every test the PR adds OR modifies.

    "Added" = the `def test_X` / `it("X", ...)` line appears as a `+` line.
    "Modified" = the test function exists at base (so its def line is unchanged)
    BUT some `+` or `-` line falls inside its body. Both qualify as f2p candidates
    because the PR changes their behaviour either way.

    Detection of "modified" works by walking the post-image lines of the patch
    in order: track the current enclosing test name (parsed from any line that
    matches the framework pattern, regardless of `+`/space prefix), then mark
    that test as touched whenever a `+` or `-` line is encountered.
    """
    fw = file_framework(file_path)
    pat = _TEST_NAME_PATTERNS.get(fw, _TEST_NAME_PATTERNS["unknown"])
    # Same pattern but match against any prefix (not just `+`)
    pat_any = re.compile(pat.pattern.replace(r"^\+\s*", r"^[+ ]\s*"))

    added: list[str] = []     # names with `+` def line — strict adds
    touched: set[str] = set()  # names enclosing any +/- line (modifies)
    cur_test: str | None = None
    for line in file_diff_block.splitlines():
        if line.startswith("+++") or line.startswith("---"): continue
        # Detect a test-name line (regardless of +/space prefix)
        m = pat_any.match(line)
        if m:
            name = next((g for g in m.groups() if g), None)
            if name:
                cur_test = name
                if line.startswith("+"):
                    added.append(name)
                continue
        # `+` or `-` body line under the current test → mark touched
        if cur_test and (line.startswith("+") or line.startswith("-")):
            touched.add(cur_test)

    seen = set()
    out: list[dict] = []
    for name in added:
        if name in seen: continue
        seen.add(name)
        out.append({"name": name, "framework": fw, "kind": "f2p", "origin": "added"})
    for name in touched:
        if name in seen: continue
        seen.add(name)
        out.append({"name": name, "framework": fw, "kind": "f2p", "origin": "modified"})
    return out


def split_patch_by_file(patch: str) -> dict[str, str]:
    """Return {file_path: file_diff_block}."""
    out: dict[str, str] = {}
    cur_path = None
    cur_lines: list[str] = []
    for line in patch.splitlines():
        if line.startswith("diff --git"):
            if cur_path:
                out[cur_path] = "\n".join(cur_lines)
            cur_lines = []
            m = re.search(r"diff --git a/(\S+) b/(\S+)", line)
            cur_path = m.group(2) if m else None
        elif line.startswith("+++ b/"):
            cur_path = line[len("+++ b/"):].strip()
            cur_lines.append(line)
        else:
            if cur_path is not None:
                cur_lines.append(line)
    if cur_path:
        out[cur_path] = "\n".join(cur_lines)
    return out


# ---------------------------------------------------------------------------
# Top-level miner
# ---------------------------------------------------------------------------

def mine_test_patch(task_dir: Path) -> dict:
    """Mine added test functions from a task's solve.sh."""
    out: dict = {"task": task_dir.name, "test_files": [], "n_added_tests": 0, "errors": []}
    sol = task_dir / "solution" / "solve.sh"
    if not sol.exists():
        out["errors"].append("no solve.sh"); return out
    try:
        text = sol.read_text()
    except Exception as e:
        out["errors"].append(f"read error: {e}"); return out

    patch = extract_patch(text, task_dir)
    if not patch:
        out["errors"].append("could not extract patch")
        return out

    by_file = split_patch_by_file(patch)
    for path, block in by_file.items():
        if not is_test_file(path): continue
        added = parse_added_tests(path, block)
        if added:
            out["test_files"].append({
                "path": path,
                "framework": file_framework(path),
                "added_tests": added,
            })
            out["n_added_tests"] += len(added)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", help="Single task name in markdown_following/")
    ap.add_argument("--task-dir", default="markdown_following")
    ap.add_argument("--out", help="Output JSONL (one line per task)")
    args = ap.parse_args()

    if args.task:
        spec = mine_test_patch(ROOT / args.task_dir / args.task)
        print(json.dumps(spec, indent=2)); return 0
    # All tasks
    out_path = Path(args.out or "pipeline_logs/test_patch_mining.jsonl")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n_total = n_with_tests = total_funcs = 0
    with out_path.open("w") as f:
        for d in sorted((ROOT / args.task_dir).iterdir()):
            if not d.is_dir(): continue
            spec = mine_test_patch(d)
            f.write(json.dumps(spec) + "\n")
            n_total += 1
            if spec["n_added_tests"] >= 1:
                n_with_tests += 1
                total_funcs += spec["n_added_tests"]
    print(f"Mined {n_total} tasks. {n_with_tests} have ≥1 added test ({100*n_with_tests/max(n_total,1):.1f}%). "
          f"Total added test functions: {total_funcs}")
    print(f"→ {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
