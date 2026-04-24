#!/usr/bin/env python3
"""Auto-fix Change 5: if tests/test_outputs.py uses linters/formatters but
instruction.md never mentions them, append a short paragraph so agents know
style is graded.

Target rubric: lint_requirement_stated (Tier B warn)

Fix: append a `## Code Style Requirements` section to instruction.md listing
the linters the tests invoke. Idempotent — skips tasks where the section
already exists.

Usage:
    .venv/bin/python scripts/fix_lint_requirement.py --dry-run
    .venv/bin/python scripts/fix_lint_requirement.py --apply
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from taskforge.task_lint import lint_lint_requirement_stated  # noqa: E402

HARBOR_TASKS = ROOT / "harbor_tasks"

# Human-readable tool names + canonical install/invocation hint for instruction
_TOOL_DESC = {
    "ruff":      "ruff format and ruff check",
    "black":     "black (Python formatter)",
    "prettier":  "prettier (JS/TS/JSON/Markdown formatter)",
    "eslint":    "eslint (JS/TS linter)",
    "stylelint": "stylelint (CSS linter)",
    "clippy":    "cargo clippy (Rust linter)",
    "cargo_fmt": "cargo fmt (Rust formatter)",
    "gofmt":     "gofmt (Go formatter)",
    "golangci":  "golangci-lint (Go linter)",
    "mypy":      "mypy (Python type checker)",
    "pyright":   "pyright (Python type checker)",
    "pylint":    "pylint (Python linter)",
    "typos":     "typos (spell-check)",
}

SECTION_HEADER = "## Code Style Requirements"


def build_section(tools: list[str]) -> str:
    bullet_lines = [f"- `{_TOOL_DESC.get(t, t)}`" for t in tools]
    return (
        f"\n\n{SECTION_HEADER}\n\n"
        f"Your solution will be checked by the repository's existing "
        f"linters/formatters. All modified files must pass:\n\n"
        + "\n".join(bullet_lines) + "\n"
    )


def fix_task(task_dir: Path) -> tuple[bool, list[str]]:
    """Apply fix if needed. Returns (changed, tools_added)."""
    findings = lint_lint_requirement_stated(task_dir)
    if not findings:
        return False, []
    tools = [t.strip() for t in findings[0].snippet.split(",") if t.strip()]
    if not tools:
        return False, []
    instr_path = task_dir / "instruction.md"
    current = instr_path.read_text()
    # Idempotent
    if SECTION_HEADER in current:
        return False, []
    new = current.rstrip() + build_section(tools)
    instr_path.write_text(new)
    return True, tools


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--tasks", default="")
    args = p.parse_args()
    if not (args.dry_run or args.apply):
        p.error("Must pass --dry-run or --apply")

    explicit = [t for t in args.tasks.split(",") if t] if args.tasks else None
    if explicit:
        dirs = [HARBOR_TASKS / t for t in explicit if (HARBOR_TASKS / t).is_dir()]
    else:
        dirs = [td for td in sorted(HARBOR_TASKS.iterdir()) if td.is_dir()]

    fixed = 0
    would_fix = 0
    sample_logs = []
    for td in dirs:
        findings = lint_lint_requirement_stated(td)
        if not findings:
            continue
        tools = [t.strip() for t in findings[0].snippet.split(",") if t.strip()]
        if not tools:
            continue
        if args.apply:
            ok, _ = fix_task(td)
            if ok:
                fixed += 1
        else:
            would_fix += 1
            if len(sample_logs) < 5:
                sample_logs.append(f"{td.name}: +{tools}")

    action = "APPLIED" if args.apply else "DRY-RUN"
    print(f"\n=== {action} summary ===")
    print(f"  Tasks augmented: {fixed if args.apply else would_fix}")
    if sample_logs:
        print("  Sample:")
        for s in sample_logs:
            print(f"    {s}")


if __name__ == "__main__":
    main()
