#!/usr/bin/env python3
"""Deploy standalone LLM judge into all harbor tasks.

For each task that has eval_manifest.yaml with rubric or distractors:
1. Copies eval_manifest.yaml into tests/ (so harbor mounts it)
2. Copies standalone_judge.py into tests/
3. Appends judge invocation snippet to test.sh (after reward.txt is written)

The judge writes Track 3/4 results to /logs/verifier/ as separate JSON files.
It does NOT modify reward.txt — programmatic tests remain the primary signal.

Dry-run by default. Pass --write to apply.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
HARBOR_TASKS = ROOT / "harbor_tasks"
JUDGE_SRC = ROOT / "taskforge" / "standalone_judge.py"

# Marker to detect if judge is already appended
JUDGE_MARKER = "# --- LLM Judge (Track 3 + Track 4) ---"

JUDGE_SNIPPET = """
# --- LLM Judge (Track 3 + Track 4) ---
if [ -f /tests/eval_manifest.yaml ] && [ -f /tests/standalone_judge.py ]; then
    # Capture agent diff
    mkdir -p /logs/verifier
    _repo_dir=""
    for candidate in /workspace/*/ /repo /app /src; do
        if [ -d "${candidate}/.git" ]; then
            _repo_dir="$candidate"
            break
        fi
    done
    if [ -z "$_repo_dir" ]; then
        _repo_dir=$(find /workspace /repo /app /src -maxdepth 3 -type d -name .git 2>/dev/null | head -1 | xargs -r dirname)
    fi
    if [ -n "$_repo_dir" ] && [ -d "$_repo_dir/.git" ]; then
        (cd "$_repo_dir" && git add -A 2>/dev/null && git diff --cached > /logs/verifier/agent.diff 2>/dev/null) || true
    fi

    # Install PyYAML if needed (lightweight, <1s)
    python3 -c "import yaml" 2>/dev/null || \\
        python3 -m pip install -q pyyaml 2>/dev/null || \\
        pip3 install -q --break-system-packages pyyaml 2>/dev/null || true

    # Run LLM judge (writes track3_rubric.json + track4_distractors.json)
    python3 /tests/standalone_judge.py /tests/eval_manifest.yaml /logs/verifier/agent.diff 2>&1 || true
fi
"""


def has_rubric_or_distractors(manifest_path: Path) -> bool:
    """Quick check if manifest has rubric or distractors."""
    try:
        import yaml
        data = yaml.safe_load(manifest_path.read_text())
        return bool(data.get("rubric")) or bool(data.get("distractors"))
    except Exception:
        # Fallback: grep
        text = manifest_path.read_text()
        return "\nrubric:" in text or "\ndistractors:" in text


def deploy_task(task_dir: Path, write: bool) -> str | None:
    """Deploy judge to one task. Returns status or None if skipped."""
    manifest = task_dir / "eval_manifest.yaml"
    test_sh = task_dir / "tests" / "test.sh"
    tests_dir = task_dir / "tests"

    if not manifest.exists() or not test_sh.exists():
        return None

    if not has_rubric_or_distractors(manifest):
        return None

    # Check if already deployed
    test_sh_text = test_sh.read_text()
    if JUDGE_MARKER in test_sh_text:
        return "already_deployed"

    if not write:
        return "would_deploy"

    # 1. Copy eval_manifest.yaml into tests/
    shutil.copy2(manifest, tests_dir / "eval_manifest.yaml")

    # 2. Copy standalone_judge.py into tests/
    shutil.copy2(JUDGE_SRC, tests_dir / "standalone_judge.py")

    # 3. Append judge snippet to test.sh
    test_sh.write_text(test_sh_text.rstrip() + "\n" + JUDGE_SNIPPET)

    return "deployed"


def main():
    write = "--write" in sys.argv

    deployed = 0
    already = 0
    skipped = 0
    would = 0

    for d in sorted(HARBOR_TASKS.iterdir()):
        if not d.is_dir():
            continue

        result = deploy_task(d, write)
        if result is None:
            skipped += 1
        elif result == "already_deployed":
            already += 1
        elif result == "would_deploy":
            would += 1
            if would <= 5:
                print(f"  WOULD DEPLOY  {d.name}")
        elif result == "deployed":
            deployed += 1
            if deployed <= 5:
                print(f"  DEPLOYED  {d.name}")

    total = deployed + would
    print(f"\nSummary:")
    print(f"  {total} tasks {'deployed' if write else 'would deploy'}")
    print(f"  {already} already deployed")
    print(f"  {skipped} skipped (no rubric/distractors)")

    if not write and total > 0:
        print(f"\nRun with --write to apply to all {total} tasks")


if __name__ == "__main__":
    main()
