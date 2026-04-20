#!/usr/bin/env python3
"""Fix structural test assertions that overfit to specific syntax.

Targets assertions that check for specific keywords (if/else, for/while)
rather than testing behavior. Replaces with more flexible checks that
accept equivalent alternatives.

Dry-run by default. Pass --write to apply fixes.
"""
import re
import sys
from pathlib import Path

HARBOR_TASKS = Path(__file__).parent.parent / "harbor_tasks"

# Patterns to fix and their replacements
FIXES = [
    {
        "name": "if/else conditional check",
        "pattern": r'assert\s+"if"\s+in\s+(\w+)\s+and\s+"else"\s+in\s+\1\s*,\s*\(\s*\n\s*"([^"]+)"\s*\n\s*\)',
        "replacement": lambda m: (
            f'# Must have conditional logic (if/else, ternary, or logical operator)\n'
            f'    has_conditional = (\n'
            f'        ("if" in {m.group(1)} and "else" in {m.group(1)})\n'
            f'        or ("?" in {m.group(1)} and ":" in {m.group(1)})  # ternary\n'
            f'        or ("&&" in {m.group(1)})                   # logical AND pattern\n'
            f'    )\n'
            f'    assert has_conditional, (\n'
            f'        "{m.group(2)}"\n'
            f'    )'
        ),
    },
    {
        "name": "if/else simple one-liner",
        "pattern": r'assert\s+"if"\s+in\s+(\w+)\s+and\s+"else"\s+in\s+\1\s*,\s*"([^"]+)"',
        "replacement": lambda m: (
            f'assert ("if" in {m.group(1)} and "else" in {m.group(1)}) '
            f'or ("?" in {m.group(1)} and ":" in {m.group(1)}) '
            f'or ("&&" in {m.group(1)}), '
            f'"{m.group(2)}"'
        ),
    },
    {
        "name": "for loop requirement (should accept while/iterator too)",
        "pattern": r'assert\s+"for"\s+in\s+(\w+)\s*,\s*"([^"]*(?:loop|iteration|iterate)[^"]*)"',
        "replacement": lambda m: (
            f'assert "for" in {m.group(1)} or "while" in {m.group(1)} '
            f'or "map" in {m.group(1)} or "forEach" in {m.group(1)} '
            f'or "iter" in {m.group(1)}, '
            f'"{m.group(2)}"'
        ),
    },
    {
        "name": "exact variable assignment (let x = value)",
        "pattern": r'assert\s+"let\s+(\w+)\s*=\s*(true|false)"\s+in\s+(\w+)',
        "replacement": lambda m: (
            f'assert "{m.group(1)}" in {m.group(3)}, '
            f'f"Variable {m.group(1)} should be defined"'
        ),
    },
]


def fix_file(path: Path, write: bool) -> list[str]:
    """Apply fixes to a single test file. Returns list of fix descriptions."""
    text = path.read_text()
    applied = []
    new_text = text

    for fix in FIXES:
        matches = list(re.finditer(fix["pattern"], new_text))
        for match in reversed(matches):  # reverse to preserve indices
            replacement = fix["replacement"](match)
            new_text = new_text[:match.start()] + replacement + new_text[match.end():]
            applied.append(f"{fix['name']}: line ~{text[:match.start()].count(chr(10)) + 1}")

    if applied and write:
        path.write_text(new_text)

    return applied


def main():
    write = "--write" in sys.argv

    total_fixed = 0
    files_touched = 0

    for d in sorted(HARBOR_TASKS.iterdir()):
        if not d.is_dir():
            continue
        test_py = d / "tests" / "test_outputs.py"
        if not test_py.exists():
            continue

        fixes = fix_file(test_py, write)
        if fixes:
            files_touched += 1
            total_fixed += len(fixes)
            action = "FIXED" if write else "WOULD FIX"
            print(f"  {action} {d.name}:")
            for f in fixes:
                print(f"    - {f}")

    print(f"\nSummary: {total_fixed} fixes in {files_touched} files")
    if not write and total_fixed > 0:
        print("Run with --write to apply fixes")


if __name__ == "__main__":
    main()
