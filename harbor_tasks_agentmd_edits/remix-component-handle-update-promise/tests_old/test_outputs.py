"""
Task: remix-component-handle-update-promise
Repo: remix-run/remix @ 649aecadeb54fc3027a2b6a85020dd31421b5327
PR:   11060

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/remix"
COMPONENT_TS = f"{REPO}/packages/component/src/lib/component.ts"
SCHEDULER_TS = f"{REPO}/packages/component/src/lib/scheduler.ts"
AGENTS_MD = f"{REPO}/packages/component/AGENTS.md"
README_MD = f"{REPO}/packages/component/README.md"
HANDLE_MD = f"{REPO}/packages/component/docs/handle.md"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral type check
# ---------------------------------------------------------------------------


def test_handle_update_returns_promise():
    """handle.update() returns Promise<AbortSignal> — verified via TypeScript type check."""
    # Write a TS file that ONLY compiles when update() returns Promise<AbortSignal>.
    # On base commit update() returns void, so assigning await result to AbortSignal errors.
    check_file = Path(f"{REPO}/packages/component/src/test/_eval_typecheck.ts")
    check_file.write_text(
        "import type { Handle } from '../lib/component.ts'\n"
        "\n"
        "// Compiles only if update() returns Promise<AbortSignal>\n"
        "async function _check(handle: Handle): Promise<AbortSignal> {\n"
        "    return await handle.update()\n"
        "}\n"
        "void _check\n"
    )
    try:
        r = subprocess.run(
            ["npx", "tsc", "--noEmit", "--project",
             "packages/component/tsconfig.json"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, (
            "TypeScript type check failed — update() must return "
            f"Promise<AbortSignal>:\n{r.stdout}\n{r.stderr}"
        )
    finally:
        check_file.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — structural code checks
# ---------------------------------------------------------------------------


def test_cascading_update_guard():
    """Scheduler detects and stops infinite cascading update loops."""
    src = Path(SCHEDULER_TS).read_text()

    assert "MAX_CASCADING_UPDATES" in src, (
        "Scheduler must define a MAX_CASCADING_UPDATES threshold"
    )
    assert "cascadingUpdateCount" in src, (
        "Scheduler must track cascading update count"
    )
    assert "infinite loop detected" in src, (
        "Scheduler must report an 'infinite loop detected' error"
    )


def test_render_ctrl_cleanup():
    """Component remove() aborts renderCtrl alongside connectedCtrl."""
    src = Path(COMPONENT_TS).read_text()
    lines = src.split("\n")

    # Find the remove() function definition
    remove_start = None
    for i, line in enumerate(lines):
        if "function remove()" in line:
            remove_start = i
            break

    assert remove_start is not None, "Could not find remove() function"

    # Check the body (next 10 lines) for renderCtrl abort
    remove_body = "\n".join(lines[remove_start:remove_start + 10])
    assert "renderCtrl" in remove_body and "abort" in remove_body, (
        "remove() must abort renderCtrl when component is removed"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — documentation update checks
# ---------------------------------------------------------------------------


def test_agents_md_promise_api():
    """AGENTS.md documents handle.update() as returning Promise<AbortSignal>."""
    content = Path(AGENTS_MD).read_text()

    assert "handle.update(task?)" not in content, (
        "AGENTS.md must not reference the old handle.update(task?) signature"
    )
    assert "await handle.update()" in content, (
        "AGENTS.md must show the await handle.update() usage pattern"
    )


def test_readme_md_promise_api():
    """README.md documents the new Promise-based update() API."""
    content = Path(README_MD).read_text()

    assert "handle.update(task?)" not in content, (
        "README.md must not reference the old handle.update(task?) signature"
    )
    assert "await handle.update()" in content, (
        "README.md must show the await handle.update() usage pattern"
    )


def test_handle_md_promise_api():
    """docs/handle.md reflects the Promise-based handle.update() API."""
    content = Path(HANDLE_MD).read_text()

    assert "handle.update(task?)" not in content, (
        "docs/handle.md must not reference the old handle.update(task?) signature"
    )
    assert "await handle.update()" in content, (
        "docs/handle.md must show the await handle.update() usage pattern"
    )
