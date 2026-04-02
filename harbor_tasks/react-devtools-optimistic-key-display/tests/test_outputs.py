"""
Task: react-devtools-optimistic-key-display
Repo: facebook/react @ 57b79b0388b755096216b2b5308113e54eac3be8
PR:   35760

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

All tests are AST-only because: renderer.js is Flow-typed JavaScript with
complex React monorepo build dependencies — it cannot be executed directly.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"
RENDERER = f"{REPO}/packages/react-devtools-shared/src/backend/fiber/renderer.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_exists():
    """renderer.js must exist at the expected path."""
    assert Path(RENDERER).exists(), f"renderer.js not found at {RENDERER}"


# [static] pass_to_pass
def test_react_optimistic_key_constant_imported():
    """REACT_OPTIMISTIC_KEY constant must be referenced in renderer.js."""
    # AST-only because: Flow-typed JS with complex monorepo build system
    src = Path(RENDERER).read_text()
    assert "REACT_OPTIMISTIC_KEY" in src, \
        "REACT_OPTIMISTIC_KEY is not referenced in renderer.js"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_keystring_handles_optimistic_key():
    """keyString computation must map REACT_OPTIMISTIC_KEY → 'React.optimisticKey'.

    The tree view calls getElementAtIndex which computes keyString for display.
    Before the fix: const keyString = key === null ? null : String(key)
    After the fix:  also checks key === REACT_OPTIMISTIC_KEY first.
    """
    # AST-only because: Flow-typed JS with complex monorepo build system
    src = Path(RENDERER).read_text()

    # Find the keyString assignment block (greedy enough to capture the ternary)
    match = re.search(r"const keyString\s*=[\s\S]{0,400}?;", src)
    assert match, "Could not find 'const keyString' assignment in renderer.js"
    block = match.group(0)

    # Must check for the optimistic key
    assert "REACT_OPTIMISTIC_KEY" in block, (
        "keyString computation does not check REACT_OPTIMISTIC_KEY — "
        "optimistic key will be stringified as Symbol(...) instead of 'React.optimisticKey'"
    )
    # Must return the human-readable display string
    assert "'React.optimisticKey'" in block, (
        "keyString computation does not return 'React.optimisticKey' — "
        "tree view will display wrong string for optimistic key"
    )
    # Must still handle the general case with String(key)
    assert "String(key)" in block, (
        "keyString computation lost the String(key) fallback for normal keys"
    )


# [pr_diff] fail_to_pass
def test_fiber_key_not_null_for_optimistic():
    """fiber.key === REACT_OPTIMISTIC_KEY must return 'React.optimisticKey', not null.

    Used in getElementAtIndex for the component inspection panel.
    Before the fix: fiber.key === REACT_OPTIMISTIC_KEY ? null : fiber.key
    After the fix:  returns 'React.optimisticKey' instead of null.
    """
    # AST-only because: Flow-typed JS with complex monorepo build system
    src = Path(RENDERER).read_text()

    # Old broken pattern must be gone
    old_pattern = r"fiber\.key\s*===\s*REACT_OPTIMISTIC_KEY\s*\?\s*null"
    assert not re.search(old_pattern, src), (
        "Old broken pattern still present: `fiber.key === REACT_OPTIMISTIC_KEY ? null` — "
        "inspection panel will show null instead of 'React.optimisticKey'"
    )

    # New pattern must show the readable display string near fiber.key check
    assert re.search(
        r"fiber\.key\s*===\s*REACT_OPTIMISTIC_KEY[\s\S]{0,120}?'React\.optimisticKey'",
        src,
    ), "fiber.key === REACT_OPTIMISTIC_KEY block does not return 'React.optimisticKey'"


# [pr_diff] fail_to_pass
def test_component_info_key_not_null_for_optimistic():
    """componentInfo.key === REACT_OPTIMISTIC_KEY must return 'React.optimisticKey'.

    Used for Server Components / component info in the inspection panel.
    Before the fix: componentInfo.key == null || componentInfo.key === REACT_OPTIMISTIC_KEY ? null
    After the fix:  returns 'React.optimisticKey' instead of null.
    """
    # AST-only because: Flow-typed JS with complex monorepo build system
    src = Path(RENDERER).read_text()

    # Must reference REACT_OPTIMISTIC_KEY in the componentInfo.key context
    match = re.search(
        r"componentInfo\.key[\s\S]{0,300}?REACT_OPTIMISTIC_KEY",
        src,
    )
    assert match, "componentInfo.key block does not reference REACT_OPTIMISTIC_KEY"

    # 'React.optimisticKey' must appear near that block
    start = match.start()
    window = src[start : start + 400]
    assert "'React.optimisticKey'" in window, (
        "componentInfo.key block does not return 'React.optimisticKey' — "
        "Server Component with optimistic key will show null"
    )


# [pr_diff] fail_to_pass
def test_inspect_element_key_not_null_for_optimistic():
    """inspectElementInternal key field must return 'React.optimisticKey', not null.

    This is the 4th location: the key field inside the inspectElementInternal return.
    Before the fix: key != null && key !== REACT_OPTIMISTIC_KEY ? key : null
    After the fix:  key === REACT_OPTIMISTIC_KEY maps to 'React.optimisticKey'.
    """
    # AST-only because: Flow-typed JS with complex monorepo build system
    src = Path(RENDERER).read_text()

    # The old broken pattern collapses optimistic key to null
    old_pattern = (
        r"key\s*!=\s*null\s*&&\s*key\s*!==\s*REACT_OPTIMISTIC_KEY\s*\?\s*key\s*:\s*null"
    )
    assert not re.search(old_pattern, src), (
        "Old broken pattern still present: `key != null && key !== REACT_OPTIMISTIC_KEY ? key : null` — "
        "inspectElementInternal will return null for optimistic key"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression guards
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_null_key_still_returns_null():
    """Normal null keys must still produce null keyString (regression guard)."""
    # AST-only because: Flow-typed JS with complex monorepo build system
    src = Path(RENDERER).read_text()

    match = re.search(r"const keyString\s*=[\s\S]{0,400}?;", src)
    assert match, "Could not find 'const keyString' in renderer.js"
    block = match.group(0)

    # The null branch must still be present
    assert re.search(r"key\s*===\s*null[\s\S]{0,20}?\bnull\b", block), (
        "keyString computation no longer maps null key → null (regression)"
    )


# [static] fail_to_pass
def test_four_display_string_occurrences():
    """'React.optimisticKey' must appear in all 4 key-handling locations in renderer.js."""
    # AST-only because: Flow-typed JS with complex monorepo build system
    src = Path(RENDERER).read_text()
    count = src.count("'React.optimisticKey'")
    assert count >= 4, (
        f"Expected 'React.optimisticKey' in at least 4 locations, found {count}. "
        "The fix must handle: keyString, fiber.key, componentInfo.key, inspectElementInternal."
    )
