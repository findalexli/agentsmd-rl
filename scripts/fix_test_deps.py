#!/usr/bin/env python3
"""Auto-fix Change 2A: install Python linters/formatters that tests invoke
but are missing from the Dockerfile.

Conservative: only handles pip-installable Python tools via an idempotent
`RUN pip install` block INJECTED at the end of the Dockerfile (safe — just
pulls extra packages into the image). Does NOT modify base image / apt steps.

Covers:  ruff, black, isort, mypy, pyright, pylint, codespell, typos,
         pre-commit, validate-pyproject, flake8, pycodestyle, autopep8

NOT covered (these need hand-written Dockerfile edits — different install
paths: apt-get, rustup, curl|sh):
   cargo, clippy, rustfmt, gofmt, golangci-lint, node, npx, pnpm, yarn,
   bun, deno, dotnet, clang-format, shellcheck, cmake-format

Usage:
    .venv/bin/python scripts/fix_test_deps.py --dry-run
    .venv/bin/python scripts/fix_test_deps.py --apply
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from taskforge.task_lint import lint_test_deps_in_dockerfile  # noqa: E402

HARBOR_TASKS = ROOT / "harbor_tasks"

PIP_INSTALLABLE = frozenset({
    "ruff", "black", "isort", "mypy", "pyright", "pylint",
    "codespell", "typos",  # typos has both a binary and pip pkg; pip is fine
    "pre-commit", "validate-pyproject",
    "flake8", "pycodestyle", "autopep8",
})

MARKER = "# auto-installed (scaffold Change 2A retrofit 2026-04-24)"


def missing_pip_tools(task_dir: Path) -> list[str]:
    findings = lint_test_deps_in_dockerfile(task_dir)
    if not findings:
        return []
    tools = {t.strip() for t in findings[0].snippet.split(",")}
    return sorted(t for t in tools if t in PIP_INSTALLABLE)


def apply_fix(task_dir: Path, tools: list[str]) -> bool:
    if not tools:
        return False
    df = task_dir / "environment" / "Dockerfile"
    text = df.read_text()
    if MARKER in text:
        return False  # idempotent
    # Find the last `FROM` so we ensure we append RUN after the final stage.
    # For single-stage Dockerfiles this is just the only FROM.
    tool_list = " ".join(tools)
    addition = (
        f"\n\n{MARKER}\n"
        f"RUN pip install --no-cache-dir --break-system-packages {tool_list} 2>/dev/null "
        f"|| pip install --no-cache-dir {tool_list}\n"
    )
    df.write_text(text.rstrip() + addition)
    return True


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()
    if not (args.dry_run or args.apply):
        p.error("Must pass --dry-run or --apply")

    fixable = 0
    unfixable = 0
    sample = []
    for td in sorted(HARBOR_TASKS.iterdir()):
        if not td.is_dir():
            continue
        findings = lint_test_deps_in_dockerfile(td)
        if not findings:
            continue
        all_missing = {t.strip() for t in findings[0].snippet.split(",")}
        pip_ok = [t for t in sorted(all_missing) if t in PIP_INSTALLABLE]
        if not pip_ok:
            unfixable += 1
            continue
        if args.apply:
            if apply_fix(td, pip_ok):
                fixable += 1
        else:
            fixable += 1
            if len(sample) < 5:
                sample.append(f"{td.name}: +{pip_ok}")

    action = "APPLIED" if args.apply else "DRY-RUN"
    print(f"\n=== {action} summary ===")
    print(f"  Tasks auto-fixable: {fixable}")
    print(f"  Tasks needing manual (non-pip deps): {unfixable}")
    if sample:
        print("  Sample:")
        for s in sample: print(f"    {s}")


if __name__ == "__main__":
    main()
