"""
Task: react-devtools-inspected-root-empty-state
Repo: facebook/react @ 705055d7ac3da03927758b22d8aea4b2e5913961
PR:   35769

InspectedElementSuspendedBy component must show an empty state for root
elements that have no suspended components, instead of returning null.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/react"
TARGET = Path(f"{REPO}/packages/react-devtools-shared/src/devtools/views/Components/InspectedElementSuspendedBy.js")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_exists():
    """Target file exists and is non-empty."""
    assert TARGET.exists(), f"File missing: {TARGET}"
    assert TARGET.stat().st_size > 0, "File is empty"


# [static] pass_to_pass
def test_no_wildcard_imports():
    """File does not use wildcard imports (import * from ...)."""
    # AST-only because: Flow-typed JS file cannot be executed without babel transform
    src = TARGET.read_text()
    wildcard_imports = re.findall(r'import\s+\*\s+from', src)
    assert len(wildcard_imports) == 0, f"Found wildcard import(s): {wildcard_imports}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_elementtyperoot_imported():
    """ElementTypeRoot is imported from react-devtools-shared/src/frontend/types."""
    # AST-only because: Flow-typed JS file cannot be executed without babel transform
    src = TARGET.read_text()
    # The fix adds this specific named import
    assert "ElementTypeRoot" in src, (
        "ElementTypeRoot not imported — needed to check if inspected element is a root"
    )
    # Verify it's a named import, not some other reference
    assert re.search(
        r"import\s*\{[^}]*ElementTypeRoot[^}]*\}\s*from",
        src,
    ), "ElementTypeRoot must be a named import with curly brace syntax"


# [pr_diff] fail_to_pass
def test_root_type_conditional_check():
    """Component checks inspectedElement.type === ElementTypeRoot before showing empty state."""
    # AST-only because: Flow-typed JS file cannot be executed without babel transform
    src = TARGET.read_text()
    assert "inspectedElement.type === ElementTypeRoot" in src, (
        "Missing conditional: inspectedElement.type === ElementTypeRoot\n"
        "The component must detect root elements to show the empty state."
    )


# [pr_diff] fail_to_pass
def test_empty_state_message_present():
    """Empty state message 'Nothing suspended the initial paint.' is rendered for roots."""
    # AST-only because: Flow-typed JS file cannot be executed without babel transform
    src = TARGET.read_text()
    assert "Nothing suspended the initial paint." in src, (
        "Missing empty state message: 'Nothing suspended the initial paint.'\n"
        "Root elements with no suspenders must show an informative message."
    )


# [pr_diff] fail_to_pass
def test_empty_state_uses_combined_header_empty_style():
    """Empty state applies both Header and Empty CSS classes for consistent styling."""
    # AST-only because: Flow-typed JS file cannot be executed without babel transform
    src = TARGET.read_text()
    # The fix uses: className={`${styles.Header} ${styles.Empty}`}
    # This ensures the empty state uses consistent styling with the rest of DevTools UI
    assert re.search(
        r"\$\{styles\.Header\}\s+\$\{styles\.Empty\}",
        src,
    ), (
        "Empty state must apply both styles.Header and styles.Empty classes together.\n"
        "Expected: className={`${styles.Header} ${styles.Empty}`}"
    )


# [pr_diff] fail_to_pass
def test_root_empty_state_inside_no_suspenders_block():
    """Root empty state logic is placed inside the 'no suspenders' guard block."""
    # AST-only because: Flow-typed JS file cannot be executed without babel transform
    # The PR moves the logic from `return null` to a root-type check
    # inside the suspenders.length === 0 / unknownSuspenders === NONE block.
    # We verify the root check appears AFTER the suspenders length check,
    # not as a top-level standalone conditional.
    src = TARGET.read_text()
    # Both patterns must exist and root check must come after suspenders check
    # (positional check: index of root condition > index of suspenders check)
    suspenders_check_pos = src.find("UNKNOWN_SUSPENDERS_NONE")
    root_check_pos = src.find("inspectedElement.type === ElementTypeRoot")
    assert suspenders_check_pos != -1, "Missing UNKNOWN_SUSPENDERS_NONE guard"
    assert root_check_pos != -1, "Missing ElementTypeRoot condition"
    assert root_check_pos > suspenders_check_pos, (
        "Root type check must appear inside (after) the 'no suspenders' guard block"
    )
