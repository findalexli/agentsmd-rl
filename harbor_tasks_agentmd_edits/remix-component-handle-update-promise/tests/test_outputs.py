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
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------


def test_handle_update_returns_promise():
    """Handle.update() must return Promise<AbortSignal> instead of accepting task callback."""
    src = Path(COMPONENT_TS).read_text()

    # Type signature must be Promise<AbortSignal>, not void with optional task
    assert "update(): Promise<AbortSignal>" in src, (
        "Handle interface must declare update(): Promise<AbortSignal>"
    )

    # Implementation must create a new Promise (not just call scheduleUpdate)
    assert "new Promise" in src, (
        "update() implementation must create a new Promise that resolves with signal"
    )

    # The old task parameter must be removed from the interface
    assert "update(task?" not in src, (
        "Handle.update() must not accept a task parameter"
    )


def test_cascading_update_guard():
    """Scheduler must detect and stop infinite cascading update loops."""
    src = Path(SCHEDULER_TS).read_text()

    # Must define a max threshold constant
    assert "MAX_CASCADING_UPDATES" in src, (
        "Scheduler must define a MAX_CASCADING_UPDATES threshold"
    )

    # Must increment a counter on each flush
    assert "cascadingUpdateCount" in src, (
        "Scheduler must track cascading update count"
    )

    # Must detect the infinite loop and dispatch an error
    assert "infinite loop detected" in src, (
        "Scheduler must detect and report infinite cascading update loops"
    )

    # Must dispatch an error (not just console.log)
    assert "dispatchError" in src or "dispatchError(error)" in src, (
        "Scheduler must dispatch an error event when cascading limit is exceeded"
    )


def test_render_ctrl_cleanup():
    """Component remove() must abort renderCtrl alongside connectedCtrl."""
    src = Path(COMPONENT_TS).read_text()

    # The remove function must abort renderCtrl
    assert "renderCtrl" in src, (
        "remove() must abort renderCtrl when component is removed"
    )

    # Must use optional chaining (renderCtrl may be undefined)
    lines_with_render_ctrl_abort = [
        line for line in src.split("\n")
        if "renderCtrl" in line and "abort" in line
    ]
    assert len(lines_with_render_ctrl_abort) > 0, (
        "remove() must call renderCtrl?.abort()"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------


def test_agents_md_promise_api():
    """AGENTS.md must document handle.update() as returning Promise<AbortSignal>."""
    content = Path(AGENTS_MD).read_text()

    # The heading must not include the old (task?) parameter
    assert "handle.update(task?)" not in content, (
        "AGENTS.md must not reference the old handle.update(task?) signature"
    )

    # Must document the Promise/AbortSignal return value
    has_promise = "promise" in content.lower() or "Promise" in content
    has_signal = "AbortSignal" in content or "abort signal" in content.lower()
    assert has_promise and has_signal, (
        "AGENTS.md must document that handle.update() returns a Promise<AbortSignal>"
    )

    # Must show await-based usage pattern instead of callback
    has_await = "await handle.update()" in content
    assert has_await, (
        "AGENTS.md must show the await handle.update() usage pattern"
    )


def test_readme_md_promise_api():
    """README.md must document the new Promise-based update() API."""
    content = Path(README_MD).read_text()

    # Must not reference the old task callback signature
    assert "handle.update(task?)" not in content, (
        "README.md must not reference the old handle.update(task?) signature"
    )

    # Must mention await or Promise or AbortSignal in context of update
    has_new_api = (
        "await" in content
        or "Promise" in content
        or "AbortSignal" in content
        or "await handle.update()" in content
    )
    assert has_new_api, (
        "README.md must document the new Promise-based handle.update() API"
    )

    # The API reference line must not mention "task" in the update description
    # Find the line describing handle.update()
    update_lines = [
        line for line in content.split("\n")
        if "handle.update" in line and "**`handle.update" in line
    ]
    for line in update_lines:
        assert "(task" not in line, (
            f"README.md API reference must not include task parameter: {line.strip()}"
        )


def test_handle_md_promise_api():
    """docs/handle.md must reflect the Promise-based handle.update() API."""
    content = Path(HANDLE_MD).read_text()

    # Must not reference the old task callback signature
    assert "handle.update(task?)" not in content, (
        "docs/handle.md must not reference the old handle.update(task?) signature"
    )

    # Must document the Promise return type
    has_promise = "promise" in content.lower() or "Promise" in content
    has_signal = "AbortSignal" in content or "abort signal" in content.lower()
    assert has_promise or has_signal, (
        "docs/handle.md must document the Promise<AbortSignal> return from handle.update()"
    )

    # Must show await-based usage
    has_await = "await handle.update()" in content
    assert has_await, (
        "docs/handle.md must show the await handle.update() usage pattern"
    )
