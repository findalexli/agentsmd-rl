"""
Task: playwright-chorecli-allow-both-selectors-and
Repo: microsoft/playwright @ 35f853d5c293c901ea66a9aa3f56f6879a94e66a
PR:   39708

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/playwright"
TAB_TS = Path(REPO) / "packages/playwright-core/src/tools/backend/tab.ts"
SKILL_MD = Path(REPO) / "packages/playwright-core/src/tools/cli-client/skill/SKILL.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files have balanced braces and expected structure."""
    content = TAB_TS.read_text()
    assert content.count("{") == content.count("}"), "Unbalanced braces in tab.ts"
    assert "export class Tab" in content, "Tab class must be defined"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_tab_imports_locator_parser():
    """tab.ts must import locatorOrSelectorAsSelector from locatorParser."""
    content = TAB_TS.read_text()
    assert "locatorOrSelectorAsSelector" in content, \
        "tab.ts must import locatorOrSelectorAsSelector"
    assert "locatorParser" in content, \
        "tab.ts must import from the locatorParser module"


# [pr_diff] fail_to_pass
def test_tab_calls_locator_or_selector():
    """resolveElements must call locatorOrSelectorAsSelector to convert input."""
    content = TAB_TS.read_text()
    # Must invoke the function (not just import it)
    assert "locatorOrSelectorAsSelector(" in content, \
        "Must call locatorOrSelectorAsSelector() to convert selector/locator input"
    # Must pass testIdAttribute config so getByTestId works
    assert "testIdAttribute" in content, \
        "Must pass testIdAttribute to locatorOrSelectorAsSelector"


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config edit tests (config_edit) — SKILL.md documentation updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass


# [static] pass_to_pass
def test_tab_ref_handling_intact():
    """tab.ts must still handle ref-based element resolution."""
    content = TAB_TS.read_text()
    assert "aria-ref=" in content, \
        "tab.ts must still handle aria-ref based element targeting"
    assert "param.ref" in content, \
        "tab.ts must still access param.ref"
