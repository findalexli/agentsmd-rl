"""
Task: gradio-custom-component-reload
Repo: gradio-app/gradio @ 4a0fe6e5aec1df710bd843f2f328d43fb7cfa7ef
PR:   12968

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/gradio"
MOUNT_CUSTOM = Path(REPO) / "js/core/src/MountCustomComponent.svelte"
MOUNT_COMPONENTS = Path(REPO) / "js/core/src/MountComponents.svelte"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# AST-only because: Svelte components cannot be executed in Python
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_effect_returns_cleanup():
    """$effect must return a cleanup function instead of using onDestroy."""
    content = MOUNT_CUSTOM.read_text()

    # Must have a return () => { ... } pattern inside $effect
    assert re.search(r"return\s*\(\)\s*=>", content), (
        "$effect does not return a cleanup function"
    )
    # Must NOT use onDestroy (the old broken pattern)
    assert "onDestroy" not in content, (
        "onDestroy is still present — cleanup should be returned from $effect"
    )


# [pr_diff] fail_to_pass
def test_effect_remounts_on_rerun():
    """Effect must re-mount component on every run, not guard with !comp."""
    content = MOUNT_CUSTOM.read_text()

    # Base code had `let comp; ... if (!comp)` which prevents re-mounting
    # when the app reloads in dev mode. The fix removes this guard so the
    # effect re-runs (and re-mounts) whenever reactive deps change.
    assert not re.search(r"!\s*comp\b", content), (
        "Found !comp guard — effect won't re-mount component on reload"
    )
    # Must not have a module-level `let comp` holding stale mount state
    assert not re.search(r"\blet\s+comp\b", content), (
        "Module-level 'comp' variable prevents effect from re-triggering"
    )


# [pr_diff] fail_to_pass
def test_no_inspect_debug():
    """$inspect(node) debug call must be removed from MountComponents.svelte."""
    if not MOUNT_COMPONENTS.exists():
        return  # File may have been refactored away — that's fine
    content = MOUNT_COMPONENTS.read_text()
    assert "$inspect" not in content, (
        "$inspect debug call still present in MountComponents.svelte"
    )


# [pr_diff] fail_to_pass
def test_unmount_spelling():
    """The 'umount' typo must be fixed to 'unmount' in the runtime type."""
    content = MOUNT_CUSTOM.read_text()
    assert "unmount" in content, (
        "'unmount' not found — the typo has not been corrected"
    )
    assert not re.search(r"\bumount\b", content), (
        "'umount' typo still present — should be 'unmount'"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """MountCustomComponent.svelte must have real mounting logic."""
    content = MOUNT_CUSTOM.read_text()
    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
    assert len(lines) > 10, "File is too short — likely a stub"
    assert "mount" in content.lower(), "No mount call found"
    assert "$effect" in content, "No $effect block found"
    assert "target" in content, "No target element reference found"
