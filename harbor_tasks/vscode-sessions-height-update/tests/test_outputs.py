"""
Task: vscode-sessions-height-update
Repo: microsoft/vscode @ 0dad7e0453d4d5a72113c59e8220aaf45020b9e7
PR:   unknown

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

# AST-only because: TypeScript — not Python, cannot import/call directly;
# VS Code codebase requires full build pipeline not available in test env.

import re
from pathlib import Path

REPO = "/workspace/vscode"
TARGET = f"{REPO}/src/vs/sessions/contrib/sessions/browser/views/sessionsList.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — sanity checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_target_file_exists():
    """Target file must exist and be non-empty."""
    p = Path(TARGET)
    assert p.exists(), f"Target file not found: {TARGET}"
    assert p.stat().st_size > 1000, "Target file looks truncated or empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_delegate_extracted_as_variable():
    """delegate must be stored in a const before the tree constructor call."""
    # Base: new SessionsTreeDelegate(approvalModel) is passed inline
    # Fix: const delegate = new SessionsTreeDelegate(approvalModel)
    content = Path(TARGET).read_text()
    assert re.search(r'const\s+delegate\s*=\s*new\s+SessionsTreeDelegate', content), (
        "Expected 'const delegate = new SessionsTreeDelegate(...)' but it was not found. "
        "The delegate must be extracted to a named variable before tree construction."
    )


# [pr_diff] fail_to_pass
def test_delegate_not_constructed_inline_in_tree():
    """SessionsTreeDelegate must not be instantiated directly inside the tree constructor args."""
    # Base: createInstance(..., new SessionsTreeDelegate(approvalModel), [...renderers...])
    # Fix: createInstance(..., delegate, [...renderers...])
    content = Path(TARGET).read_text()
    # The buggy pattern: new SessionsTreeDelegate followed (after closing paren) by comma + [
    bad_pattern = re.search(
        r'new\s+SessionsTreeDelegate\s*\([^)]*\)\s*,\s*\[',
        content,
        re.DOTALL,
    )
    assert bad_pattern is None, (
        "SessionsTreeDelegate must not be constructed inline as a tree constructor argument. "
        "Extract it to a variable and pass the variable instead."
    )


# [pr_diff] fail_to_pass
def test_getheight_called_in_height_update_handler():
    """updateElementHeight must call delegate.getHeight(session), not pass undefined."""
    # Base: this.tree.updateElementHeight(session, undefined)
    # Fix: this.tree.updateElementHeight(session, delegate.getHeight(session))
    content = Path(TARGET).read_text()
    assert "delegate.getHeight(session)" in content, (
        "Expected 'delegate.getHeight(session)' to be used as the height argument "
        "in updateElementHeight, but it was not found."
    )


# [pr_diff] fail_to_pass
def test_undefined_not_passed_to_update_element_height():
    """updateElementHeight must not receive undefined as the height argument."""
    # Base: this.tree.updateElementHeight(session, undefined) — passes undefined
    # Fix: the height is computed via delegate.getHeight(session)
    content = Path(TARGET).read_text()
    bad_calls = re.findall(
        r'updateElementHeight\s*\(\s*\w+\s*,\s*undefined\s*\)',
        content,
    )
    assert len(bad_calls) == 0, (
        f"Found {len(bad_calls)} call(s) to updateElementHeight with undefined height: {bad_calls}. "
        "The height must be computed from the delegate, not passed as undefined."
    )
