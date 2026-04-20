#!/usr/bin/env python3
"""Fix task.toml files to be compatible with Harbor's TaskConfig.

Issues fixed:
1. Double-quoted strings: source_repo = ""repo"" → source_repo = "repo"
2. [source] tables: convert to flat top-level keys, remove the table
3. Other common TOML syntax errors

Dry-run by default. Pass --write to actually modify files.
"""
import re
import sys
import tomllib
from pathlib import Path

HARBOR_TASKS = Path(__file__).parent.parent / "harbor_tasks"


def fix_double_quotes(text: str) -> str:
    """Fix ""value"" → "value" pattern."""
    return re.sub(r'= ""([^"]+)""', r'= "\1"', text)


def fix_source_table(text: str) -> str:
    """Convert [source] table to flat keys prefixed with source_."""
    lines = text.splitlines(keepends=True)
    out = []
    in_source = False
    source_keys = []

    for line in lines:
        stripped = line.strip()
        if stripped == "[source]":
            in_source = True
            continue
        if in_source:
            if stripped.startswith("[") or stripped == "":
                in_source = stripped == ""
                if stripped == "":
                    continue  # skip blank line after [source]
                out.append(line)
                continue
            # Convert source table key to flat key
            # e.g., pr = "..." → source_pr = "..."
            # Skip if already exists at top level
            match = re.match(r'(\w+)\s*=', stripped)
            if match:
                key = match.group(1)
                # Don't prefix if already has source_ prefix
                if not key.startswith("source_"):
                    new_key = f"source_{key}"
                else:
                    new_key = key
                source_keys.append((key, new_key, line))
            continue
        out.append(line)

    # Insert source keys at the top (after version line if present)
    if source_keys:
        insert_idx = 0
        for i, line in enumerate(out):
            if line.strip().startswith("version"):
                insert_idx = i + 1
                break
            if line.strip().startswith("["):
                insert_idx = i
                break
            if line.strip() and "=" in line:
                insert_idx = i + 1

        for key, new_key, orig_line in reversed(source_keys):
            new_line = orig_line.replace(f"{key} =", f"{new_key} =", 1)
            out.insert(insert_idx, new_line)

    return "".join(out)


def validate_toml(text: str) -> tuple[bool, str]:
    """Check if TOML parses and source is not a dict."""
    try:
        t = tomllib.loads(text)
        if isinstance(t.get("source"), dict):
            return False, "[source] is a table"
        return True, ""
    except Exception as e:
        return False, str(e)


def main():
    write = "--write" in sys.argv

    fixed = 0
    still_broken = 0
    already_ok = 0

    for d in sorted(HARBOR_TASKS.iterdir()):
        if not d.is_dir():
            continue
        toml_f = d / "task.toml"
        if not toml_f.exists():
            continue

        text = toml_f.read_text()
        ok, err = validate_toml(text)

        if ok:
            already_ok += 1
            continue

        # Apply fixes
        new_text = text
        new_text = fix_double_quotes(new_text)
        new_text = fix_source_table(new_text)

        ok2, err2 = validate_toml(new_text)
        if ok2:
            fixed += 1
            if write:
                toml_f.write_text(new_text)
                print(f"  FIXED  {d.name}")
            else:
                print(f"  WOULD FIX  {d.name}  (was: {err})")
        else:
            still_broken += 1
            print(f"  BROKEN {d.name}: {err2}")

    print(f"\nSummary: {already_ok} OK, {fixed} {'fixed' if write else 'fixable'}, {still_broken} still broken")
    if not write and fixed > 0:
        print("Run with --write to apply fixes")


if __name__ == "__main__":
    main()
