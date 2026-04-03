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
def test_upstream_hoistable_cleanup():
    """Run the upstream Jest test verifying hoistable cleanup behavior.

    This injects the test case from PR #35741 into store-test.js and runs it.
    The test creates two components sharing a deduplicated <style> hoistable,
    unmounts one, and verifies the remaining component's element is still
    tracked in the DevTools store — which fails on the base commit due to
    the wrong Map.set() argument order.
    """
    test_file = Path(f"{REPO}/packages/react-devtools-shared/src/__tests__/store-test.js")
    content = test_file.read_text()

    if "cleans up host hoistables" not in content:
        # Inject the test from PR #35741 before the final closing `});`
        test_case = """
  // @reactVersion >= 19
  it('cleans up host hoistables', async () => {
    function Left() {
      return (
        <style href="test.css" precedence="medium">
          {'* {color:black}'}
        </style>
      );
    }

    function Right() {
      return (
        <style href="test.css" precedence="medium">
          {'* {color:black}'}
        </style>
      );
    }

    await actAsync(() => {
      render(
        <>
          <Left />
          <Right />
        </>,
      );
    });

    // Ensure we're still testing deduplicated hoistables.
    expect(document.head.querySelectorAll('style')).toHaveLength(1);
    let style = document.head.querySelector('style');
    let styleID = agent.getIDForHostInstance(style).id;
    expect(store.containsElement(styleID)).toBe(true);

    await actAsync(() => {
      render(
        <>
          <Right />
        </>,
      );
    });

    style = document.head.querySelector('style');
    styleID = agent.getIDForHostInstance(style).id;
    expect(store.containsElement(styleID)).toBe(true);
  });
"""
        # Insert before the last `});` that closes the describe block
        last_close = content.rfind("\n});")
        assert last_close != -1, "Could not find closing of describe block in store-test.js"
        content = content[:last_close] + test_case + content[last_close:]
        test_file.write_text(content)

    r = subprocess.run(
        [
            "yarn", "test", "--silent", "--no-watchman",
            "--testPathPattern", "store-test",
            "--testNamePattern", "cleans up host hoistables",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=180,
    )
    stdout = r.stdout.decode()[-3000:]
    stderr = r.stderr.decode()[-3000:]
    assert r.returncode == 0, (
        f"Upstream 'cleans up host hoistables' test failed:\n{stdout}\n{stderr}"
    )


# Structural checks below because releaseHostResource is module-internal
# and cannot be imported/called without React's full fiber reconciliation
# infrastructure — the upstream Jest test above is the behavioral verification.

# [pr_diff] fail_to_pass
def test_correct_map_set_key():
    """publicInstanceToDevToolsInstanceMap.set() must use publicInstance as key.

    The fix swaps the first argument from firstInstance to publicInstance.
    The map key must be the public host instance (DOM element), not a
    DevTools internal instance.
    """
    content = Path(RENDERER).read_text()

    # Find the Map.set() call inside the for-of loop over resourceInstances
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
        "The map key must be the public host instance (DOM element)."
    )


# [pr_diff] fail_to_pass
def test_buggy_pattern_absent():
    """The buggy set(firstInstance, nearestInstance) call must not be present.

    On the base commit, Map.set() passes (firstInstance, nearestInstance) —
    wrong key and wrong value. After the fix, this pattern must be gone.
    """
    content = Path(RENDERER).read_text()

    buggy = re.compile(
        r"publicInstanceToDevToolsInstanceMap\.set\(\s*"
        r"firstInstance\s*,\s*nearestInstance",
        re.DOTALL,
    )
    assert not buggy.search(content), (
        "Buggy Map.set() argument order still present: "
        "set(firstInstance, nearestInstance). "
        "Should be set(publicInstance, firstInstance)."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_function_exists():
    """releaseHostResource function must still be defined."""
    content = Path(RENDERER).read_text()
    assert "function releaseHostResource(" in content, (
        "releaseHostResource() function not found in renderer.js"
    )


# [static] pass_to_pass
def test_map_set_call_exists():
    """The publicInstanceToDevToolsInstanceMap.set() call must still exist
    inside releaseHostResource — prevents solutions that simply delete it."""
    content = Path(RENDERER).read_text()

    # Find releaseHostResource function body and verify Map.set call is present
    fn_start = content.find("function releaseHostResource(")
    assert fn_start != -1, "releaseHostResource not found"

    # Look for the Map.set call after the function definition
    fn_body = content[fn_start:fn_start + 3000]
    assert "publicInstanceToDevToolsInstanceMap.set(" in fn_body, (
        "publicInstanceToDevToolsInstanceMap.set() call missing from "
        "releaseHostResource — the function must update the map, not delete the call."
    )
