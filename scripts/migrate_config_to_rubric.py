#!/usr/bin/env python3
"""Migrate config_edit checks from binary tests → rubric rules.

For each task in harbor_tasks_agentmd_edits/:
1. Parse solve.sh → extract config file diffs (README.md, CLAUDE.md, etc.)
2. Move config_edit checks from `checks` → `rubric` in eval_manifest.yaml
3. Remove corresponding test_* functions from test_outputs.py
4. Add extracted gold diff snippet to each rubric rule as context

The gold patch stays complete. Binary reward = code tests only.
Config edit quality = LLM-judged rubric (separate signal).
"""

from __future__ import annotations

import re
import yaml
from pathlib import Path

TASK_DIR = Path("harbor_tasks_agentmd_edits")

# Config file patterns for splitting diffs
CONFIG_PATTERNS = [
    r"README\.md", r"CLAUDE\.md", r"AGENTS\.md", r"SKILL\.md",
    r"CONTRIBUTING\.md", r"CONVENTIONS\.md", r"CHANGELOG\.md",
    r"copilot-instructions\.md", r"\.cursorrules", r"\.cursor/rules",
    r"\.mdc$",
]
CONFIG_RE = re.compile("|".join(CONFIG_PATTERNS), re.IGNORECASE)


def extract_config_diffs(solve_sh: str) -> dict[str, str]:
    """Extract config file hunks from the embedded patch in solve.sh.

    Returns {filepath: diff_hunk} for each config file in the patch.
    """
    # Find the patch content between <<'PATCH' and PATCH (or <<'EOF' and EOF, etc.)
    # Support various heredoc delimiters
    heredoc_match = re.search(
        r"<<\s*'?(\w+)'?\s*\n(.*?)\n\1",
        solve_sh,
        re.DOTALL,
    )
    if not heredoc_match:
        # Try curl-based patches
        return {}

    patch_text = heredoc_match.group(2)

    # Split into per-file hunks
    file_hunks: dict[str, str] = {}
    current_file = None
    current_lines: list[str] = []

    for line in patch_text.split("\n"):
        if line.startswith("diff --git"):
            # Save previous hunk
            if current_file and CONFIG_RE.search(current_file):
                file_hunks[current_file] = "\n".join(current_lines)
            # Parse new file path
            match = re.match(r"diff --git a/(.*?) b/(.*)", line)
            if match:
                current_file = match.group(2)
            else:
                current_file = None
            current_lines = [line]
        else:
            current_lines.append(line)

    # Don't forget last hunk
    if current_file and CONFIG_RE.search(current_file):
        file_hunks[current_file] = "\n".join(current_lines)

    return file_hunks


def extract_added_lines(diff_hunk: str) -> str:
    """Extract just the added lines from a diff hunk (for rubric context)."""
    added = []
    for line in diff_hunk.split("\n"):
        if line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:])  # Strip the leading +
    return "\n".join(added).strip()


def remove_test_function(test_content: str, func_name: str) -> str:
    """Remove a test function from test_outputs.py."""
    # Match the function and its body (including docstring and all indented lines)
    pattern = re.compile(
        rf'\ndef {re.escape(func_name)}\(.*?\):\n'
        rf'(?:    .*\n)*',
    )
    return pattern.sub('\n', test_content)


def migrate_task(task_dir: Path) -> dict:
    """Migrate one task. Returns stats."""
    manifest_path = task_dir / "eval_manifest.yaml"
    test_path = task_dir / "tests" / "test_outputs.py"
    solve_path = task_dir / "solution" / "solve.sh"

    if not all(p.exists() for p in [manifest_path, test_path, solve_path]):
        return {"status": "missing_files"}

    # Load manifest
    try:
        manifest = yaml.safe_load(manifest_path.read_text())
    except Exception:
        return {"status": "bad_manifest"}

    checks = manifest.get("checks", [])
    existing_rubric = manifest.get("rubric", [])

    # Find config_edit checks
    config_checks = [c for c in checks if c.get("origin") == "config_edit"]
    if not config_checks:
        return {"status": "no_config_checks"}

    # Extract config diffs from solve.sh
    solve_text = solve_path.read_text()
    config_diffs = extract_config_diffs(solve_text)

    # Build new rubric rules from config_edit checks
    new_rubric_rules = []
    test_funcs_to_remove = []

    for check in config_checks:
        check_id = check["id"]
        description = check.get("description", "")
        source = check.get("source", {})

        # Find the matching config diff for context
        config_path = source.get("path", "") if source else ""
        gold_diff = ""
        gold_additions = ""

        # Try exact match first, then partial
        if config_path and config_path in config_diffs:
            gold_diff = config_diffs[config_path]
            gold_additions = extract_added_lines(gold_diff)
        else:
            # Try partial match (e.g., "README.md" matches "packages/foo/README.md")
            for diff_path, diff_hunk in config_diffs.items():
                if config_path and config_path in diff_path:
                    gold_diff = diff_hunk
                    gold_additions = extract_added_lines(gold_diff)
                    break
            else:
                # Use all config diffs as context
                all_additions = []
                for dp, dh in config_diffs.items():
                    added = extract_added_lines(dh)
                    if added:
                        all_additions.append(f"# {dp}\n{added}")
                gold_additions = "\n\n".join(all_additions)

        # Build rubric rule
        rule = {
            "rule": description,
        }
        if source:
            rule["source"] = source
        if gold_additions:
            # Truncate to keep manifest readable
            rule["reference"] = gold_additions[:500]

        new_rubric_rules.append(rule)
        test_funcs_to_remove.append(f"test_{check_id}")

    # Update manifest: remove config_edit from checks, add to rubric
    manifest["checks"] = [c for c in checks if c.get("origin") != "config_edit"]
    manifest["rubric"] = existing_rubric + new_rubric_rules

    # Write updated manifest
    manifest_path.write_text(yaml.dump(manifest, default_flow_style=False, sort_keys=False))

    # Remove config test functions from test_outputs.py
    test_content = test_path.read_text()
    original_len = len(test_content)
    for func_name in test_funcs_to_remove:
        test_content = remove_test_function(test_content, func_name)

    if len(test_content) != original_len:
        test_path.write_text(test_content)

    return {
        "status": "migrated",
        "checks_moved": len(config_checks),
        "diffs_found": len(config_diffs),
        "tests_removed": len(test_funcs_to_remove),
        "config_files": list(config_diffs.keys()),
    }


def main():
    stats = {"migrated": 0, "no_config_checks": 0, "missing_files": 0, "bad_manifest": 0}
    total_checks_moved = 0
    total_diffs_found = 0

    for d in sorted(TASK_DIR.iterdir()):
        if not d.is_dir():
            continue
        result = migrate_task(d)
        status = result["status"]
        stats[status] = stats.get(status, 0) + 1

        if status == "migrated":
            total_checks_moved += result["checks_moved"]
            total_diffs_found += result["diffs_found"]

    print(f"Migration results:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")
    print(f"\nTotal checks moved to rubric: {total_checks_moved}")
    print(f"Total config diffs extracted: {total_diffs_found}")

    # Verify: count remaining checks and rubric rules
    total_checks = 0
    total_rubric = 0
    tasks_with_rubric = 0
    rubric_with_ref = 0

    for d in sorted(TASK_DIR.iterdir()):
        if not d.is_dir():
            continue
        manifest_path = d / "eval_manifest.yaml"
        if not manifest_path.exists():
            continue
        try:
            m = yaml.safe_load(manifest_path.read_text())
            total_checks += len(m.get("checks", []))
            rubric = m.get("rubric", [])
            total_rubric += len(rubric)
            if rubric:
                tasks_with_rubric += 1
            rubric_with_ref += sum(1 for r in rubric if r.get("reference"))
        except:
            pass

    print(f"\nAfter migration:")
    print(f"  Total binary checks: {total_checks}")
    print(f"  Total rubric rules: {total_rubric}")
    print(f"  Tasks with rubric: {tasks_with_rubric}")
    print(f"  Rubric rules with gold reference: {rubric_with_ref}")


if __name__ == "__main__":
    main()
