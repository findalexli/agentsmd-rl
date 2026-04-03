#!/usr/bin/env python3
"""Fix config test placeholders in agentmd tasks.

For tasks where the LLM left the test_config_rule placeholder:
1. If the task has OTHER real config-related tests → remove the placeholder
2. If the task has NO real config tests → flag for enrichment

Also fixes eval_manifest.yaml to remove the placeholder check.
"""

import re
import yaml
from pathlib import Path

TASK_DIR = Path("harbor_tasks_agentmd_edits")

# Regex for the placeholder function
PLACEHOLDER_RE = re.compile(
    r'\ndef test_config_rule\(\):\n'
    r'    """TODO.*?""".*?\n'
    r'    # Only include.*?\n'
    r'    # Soft/subjective.*?\n'
    r'    raise NotImplementedError.*?\n',
    re.DOTALL,
)

# Check if a test function reads a config file
CONFIG_FILE_PATTERNS = [
    r'README\.md', r'CLAUDE\.md', r'AGENTS\.md', r'SKILL\.md',
    r'CONTRIBUTING\.md', r'CONVENTIONS\.md', r'copilot-instructions\.md',
    r'\.cursorrules',
]
CONFIG_RE = re.compile('|'.join(CONFIG_FILE_PATTERNS), re.IGNORECASE)


def has_real_config_tests(test_content: str) -> bool:
    """Check if test_outputs.py has real config file tests (not placeholders)."""
    # Find all test functions
    functions = re.findall(r'(def test_\w+\(.*?\n(?:(?!def test_).*\n)*)', test_content)
    for func in functions:
        if 'NotImplementedError' in func:
            continue
        if CONFIG_RE.search(func) and ('read_text' in func or 'open(' in func):
            return True
    return False


def fix_task(task_dir: Path) -> str:
    """Fix a single task. Returns status."""
    test_py = task_dir / "tests" / "test_outputs.py"
    manifest = task_dir / "eval_manifest.yaml"

    if not test_py.exists():
        return "no_test_py"

    content = test_py.read_text()

    if 'raise NotImplementedError' not in content:
        return "already_clean"

    has_real = has_real_config_tests(content)

    # Remove placeholder
    new_content = PLACEHOLDER_RE.sub('\n', content)

    # Also remove any other NotImplementedError test functions
    new_content = re.sub(
        r'\ndef test_\w+\(\):\n'
        r'(?:    (?:""".*?"""|#.*?|raise NotImplementedError.*?)\n)*',
        lambda m: '' if 'NotImplementedError' in m.group() else m.group(),
        new_content,
    )

    if new_content != content:
        test_py.write_text(new_content)

    # Fix manifest — remove check for config_rule if it exists
    if manifest.exists():
        try:
            m = yaml.safe_load(manifest.read_text())
            checks = m.get("checks", [])
            new_checks = [c for c in checks if c.get("id") != "config_rule"]
            if len(new_checks) != len(checks):
                m["checks"] = new_checks
                manifest.write_text(yaml.dump(m, default_flow_style=False, sort_keys=False))
        except:
            pass

    if has_real:
        return "fixed_has_real_tests"
    else:
        return "needs_enrichment"


def main():
    results = {}
    for d in sorted(TASK_DIR.iterdir()):
        if not d.is_dir():
            continue
        status = fix_task(d)
        results[status] = results.get(status, 0) + 1

    print("Results:")
    for status, count in sorted(results.items()):
        print(f"  {status}: {count}")

    # Count tasks that still need config edit tests
    needs_enrichment = []
    for d in sorted(TASK_DIR.iterdir()):
        if not d.is_dir():
            continue
        test_py = d / "tests" / "test_outputs.py"
        if not test_py.exists():
            continue
        content = test_py.read_text()
        if not has_real_config_tests(content):
            needs_enrichment.append(d.name)

    print(f"\nTasks needing config test enrichment: {len(needs_enrichment)}")
    if needs_enrichment:
        with open("needs_config_enrichment.txt", "w") as f:
            for name in needs_enrichment:
                f.write(name + "\n")
        print(f"  Written to needs_config_enrichment.txt")


if __name__ == "__main__":
    main()
