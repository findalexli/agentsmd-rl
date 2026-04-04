#!/usr/bin/env python3
"""Relabel config-related checks in eval_manifest.yaml to origin: config_edit.

Scans test_outputs.py for tests that read config files (README.md, CLAUDE.md, etc.)
and updates the corresponding check's origin in eval_manifest.yaml.
"""

import re
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from taskforge.config import CONFIG_RE

TASK_DIR = Path("harbor_tasks_agentmd_edits")


def get_config_test_ids(test_content: str) -> set[str]:
    """Find test function names that read config files."""
    ids = set()
    # Split into functions
    functions = re.split(r'\ndef (test_\w+)', test_content)
    for i in range(1, len(functions), 2):
        fname = functions[i]
        body = functions[i + 1] if i + 1 < len(functions) else ""
        if CONFIG_RE.search(body) and ("read_text" in body or "open(" in body):
            ids.add(fname)
    return ids


def main():
    relabeled = 0
    tasks_fixed = 0

    for d in sorted(TASK_DIR.iterdir()):
        if not d.is_dir():
            continue
        test_py = d / "tests" / "test_outputs.py"
        manifest = d / "eval_manifest.yaml"
        if not test_py.exists() or not manifest.exists():
            continue

        config_test_ids = get_config_test_ids(test_py.read_text())
        if not config_test_ids:
            continue

        try:
            m = yaml.safe_load(manifest.read_text())
        except:
            continue

        checks = m.get("checks", [])
        changed = False
        for check in checks:
            check_id = check.get("id", "")
            # Match test_X to check id X
            if f"test_{check_id}" in config_test_ids and check.get("origin") != "config_edit":
                check["origin"] = "config_edit"
                changed = True
                relabeled += 1

        if changed:
            manifest.write_text(yaml.dump(m, default_flow_style=False, sort_keys=False))
            tasks_fixed += 1

    print(f"Tasks fixed: {tasks_fixed}")
    print(f"Checks relabeled to config_edit: {relabeled}")

    # Verify
    total_config_edit = 0
    tasks_with = 0
    for d in sorted(TASK_DIR.iterdir()):
        if not d.is_dir():
            continue
        manifest = d / "eval_manifest.yaml"
        if not manifest.exists():
            continue
        try:
            m = yaml.safe_load(manifest.read_text())
            ce = [c for c in m.get("checks", []) if c.get("origin") == "config_edit"]
            total_config_edit += len(ce)
            if ce:
                tasks_with += 1
        except:
            pass
    print(f"\nAfter fix: {tasks_with} tasks have config_edit checks ({total_config_edit} total)")


if __name__ == "__main__":
    main()
