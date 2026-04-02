"""
Task: react-devtools-hoistable-memory-leak
Repo: facebook/react @ 49c3b270f9991fbecbe2b9c29c27e19a54fb4466
PR:   35741

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Bug: In releaseHostResource(), publicInstanceToDevToolsInstanceMap.set()
has wrong argument order — set(firstInstance, nearestInstance) instead of
set(publicInstance, firstInstance) — causing memory leaks when hoistables
(e.g. deduplicated <style> tags) are unmounted.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"
RENDERER = f"{REPO}/packages/react-devtools-shared/src/backend/fiber/renderer.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """renderer.js must parse without syntax errors."""
    r = subprocess.run(
        ["node", "--check", RENDERER],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"Syntax error in renderer.js:\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_correct_map_set_order():
    """publicInstanceToDevToolsInstanceMap.set() must have publicInstance as first arg.

    The fix swaps the arguments from set(firstInstance, nearestInstance)
    to set(publicInstance, firstInstance). This ensures the map correctly
    indexes by DOM element (publicInstance) rather than DevTools instance.
    """
    content = Path(RENDERER).read_text()

    # Locate the Map.set() call inside the for-loop over resourceInstances
    # and extract the first argument passed to it.
    pattern = re.compile(
        r"for\s*\(\s*const\s+firstInstance\s+of\s+resourceInstances\s*\)"
        r".*?publicInstanceToDevToolsInstanceMap\.set\(\s*(\w+)",
        re.DOTALL,
    )
    m = pattern.search(content)
    assert m is not None, (
        "Could not find publicInstanceToDevToolsInstanceMap.set() call "
        "inside the 'for (const firstInstance of resourceInstances)' loop"
    )
    first_arg = m.group(1)
    assert first_arg == "publicInstance", (
        f"Map.set() first arg is '{first_arg}', expected 'publicInstance'. "
        "The map key must be the public host instance (DOM element), not a DevTools instance."
    )


# [pr_diff] fail_to_pass
def test_buggy_pattern_absent():
    """The buggy set(firstInstance, nearestInstance) call must not be present.

    On the base commit, Map.set() passes (firstInstance, nearestInstance) —
    wrong key and wrong value. After the fix, this pattern must be gone.
    """
    content = Path(RENDERER).read_text()

    # The original buggy call: set(firstInstance, nearestInstance)
    buggy = re.compile(
        r"publicInstanceToDevToolsInstanceMap\.set\(\s*firstInstance\s*,\s*nearestInstance",
        re.DOTALL,
    )
    assert not buggy.search(content), (
        "Buggy Map.set() argument order still present: "
        "set(firstInstance, nearestInstance) — key and value are both wrong. "
        "Should be set(publicInstance, firstInstance)."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_function_exists():
    """releaseHostResource function must still be defined (not deleted or renamed)."""
    content = Path(RENDERER).read_text()
    assert "function releaseHostResource(" in content, (
        "releaseHostResource() function not found in renderer.js — "
        "it must not be deleted or renamed."
    )
