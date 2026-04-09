"""
Task: react-enableViewTransition-native-fb
Repo: react @ b4546cd0d4db2b913d8e7503bee86e1844073b2e
PR:   36106

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"

FORK_DIR = f"{REPO}/packages/shared/forks"
FLAG = "enableViewTransition"

FILES_CHANGED = [
    f"{FORK_DIR}/ReactFeatureFlags.native-fb.js",
    f"{FORK_DIR}/ReactFeatureFlags.test-renderer.native-fb.js",
    f"{FORK_DIR}/ReactFeatureFlags.test-renderer.www.js",
]


def _get_flag_value(filepath: str, flag_name: str) -> bool:
    """Extract a boolean flag value from a JS feature flag file."""
    content = Path(filepath).read_text()
    # Match both typed and untyped exports:
    #   export const enableViewTransition: boolean = false;
    #   export const enableViewTransition = false;
    pattern = rf'export\s+const\s+{flag_name}(?:\s*:\s*\w+)?\s*=\s*(true|false)'
    match = re.search(pattern, content)
    assert match, f"Flag '{flag_name}' not found in {filepath}"
    return match.group(1) == "true"


def _get_flag_line(filepath: str, flag_name: str) -> str:
    """Return the full source line declaring the flag."""
    content = Path(filepath).read_text()
    for line in content.splitlines():
        if re.search(rf'export\s+const\s+{flag_name}', line):
            return line.strip()
    return ""


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_js_syntax_valid():
    """All modified flag files must be syntactically valid JS (node --check)."""
    for filepath in FILES_CHANGED:
        r = subprocess.run(
            ["node", "--check", filepath],
            capture_output=True, timeout=30,
        )
        assert r.returncode == 0, (
            f"Syntax error in {filepath}:\n{r.stderr.decode()}"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_native_fb_view_transition_enabled():
    """enableViewTransition must be true in ReactFeatureFlags.native-fb.js."""
    value = _get_flag_value(FILES_CHANGED[0], FLAG)
    assert value is True, (
        f"enableViewTransition is disabled in native-fb fork"
    )


# [pr_diff] fail_to_pass
def test_test_renderer_native_view_transition_enabled():
    """enableViewTransition must be true in test-renderer.native-fb.js."""
    value = _get_flag_value(FILES_CHANGED[1], FLAG)
    assert value is True, (
        f"enableViewTransition is disabled in test-renderer.native-fb fork"
    )


# [pr_diff] fail_to_pass
def test_test_renderer_www_view_transition_enabled():
    """enableViewTransition must be true in test-renderer.www.js."""
    value = _get_flag_value(FILES_CHANGED[2], FLAG)
    assert value is True, (
        f"enableViewTransition is disabled in test-renderer.www fork"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_flag_type_annotation_preserved():
    """Typed files must retain ': boolean' annotation style."""
    # native-fb and test-renderer.www use typed annotations
    typed_files = [FILES_CHANGED[0], FILES_CHANGED[2]]
    for filepath in typed_files:
        line = _get_flag_line(filepath, FLAG)
        assert ": boolean" in line, (
            f"Type annotation ': boolean' missing from {filepath}: {line}"
        )


# [static] pass_to_pass
def test_other_flags_unchanged():
    """Adjacent flags must remain at their original values."""
    # Verify enableGestureTransition is still false in all 3 files
    for filepath in FILES_CHANGED:
        value = _get_flag_value(filepath, "enableGestureTransition")
        assert value is False, (
            f"enableGestureTransition was unexpectedly changed to true in {filepath}"
        )
    # Verify enableScrollEndPolyfill is still true
    for filepath in FILES_CHANGED:
        value = _get_flag_value(filepath, "enableScrollEndPolyfill")
        assert value is True, (
            f"enableScrollEndPolyfill was unexpectedly changed in {filepath}"
        )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from SKILL.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .claude/skills/feature-flags/SKILL.md @ base commit
def test_all_rn_fork_files_updated():
    """All RN/test-renderer fork files must have enableViewTransition enabled.

    Per SKILL.md: 'New flags must be added to ALL fork files, not just the
    main one.' When enabling a flag, every relevant fork must be updated.
    """
    values = [_get_flag_value(f, FLAG) for f in FILES_CHANGED]
    assert all(values), (
        f"Not all RN fork files have enableViewTransition enabled: "
        f"{dict(zip(['native-fb', 'test-renderer.native-fb', 'test-renderer.www'], values))}"
    )
