"""
Task: supabase-chore-reacthookform-best-practices
Repo: supabase/supabase @ fba5a8a001b0fb775e3e8054e57b1c7a9cba8a0c
PR:   44221

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/supabase"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file existence / validity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must still exist and be non-empty."""
    files = [
        ".cursor/rules/studio/forms/RULE.md",
        "apps/design-system/content/docs/ui-patterns/forms.mdx",
        "apps/design-system/content/docs/ui-patterns/modality.mdx",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} must exist"
        content = p.read_text()
        assert len(content) > 100, f"{f} must not be empty or truncated"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — documentation content tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_forms_mdx_destructure_guidance():
    """forms.mdx best practice #5 must mention destructuring isDirty from formState."""
    forms = Path(REPO) / "apps/design-system/content/docs/ui-patterns/forms.mdx"
    content = forms.read_text()
    # The key addition: guidance to destructure formState values
    assert "destructure" in content.lower() or "const {" in content, \
        "forms.mdx should mention destructuring formState values"
    # Must still reference isDirty in the dirty state section
    assert "isDirty" in content, \
        "forms.mdx should reference isDirty"


# [pr_diff] fail_to_pass
def test_modality_code_example_destructures():
    """modality.mdx code example must destructure isDirty from form.formState."""
    modality = Path(REPO) / "apps/design-system/content/docs/ui-patterns/modality.mdx"
    content = modality.read_text()
    # Check that the code example shows destructuring isDirty from formState
    assert re.search(r"\{\s*isDirty\s*\}.*form\.formState", content) or \
           re.search(r"const\s+\{\s*isDirty\s*\}\s*=\s*form\.formState", content), \
        "modality.mdx should show destructuring isDirty from form.formState"


# [pr_diff] fail_to_pass
def test_modality_checkisdirty_uses_destructured():
    """modality.mdx checkIsDirty callback must use destructured isDirty, not form.formState.isDirty."""
    modality = Path(REPO) / "apps/design-system/content/docs/ui-patterns/modality.mdx"
    content = modality.read_text()

    # Find the checkIsDirty pattern in the Studio implementation
    match = re.search(
        r"checkIsDirty:\s*\(\)\s*=>\s*(\S+)",
        content,
    )
    assert match, "modality.mdx should contain a checkIsDirty callback"
    value = match.group(1).rstrip(",")
    # Should be just 'isDirty', not 'form.formState.isDirty'
    assert value == "isDirty", \
        f"checkIsDirty should use destructured 'isDirty', got '{value}'"


# [pr_diff] fail_to_pass
def test_modality_formstate_proxy_comment():
    """modality.mdx should explain WHY destructuring is needed (proxy/reactivity)."""
    modality = Path(REPO) / "apps/design-system/content/docs/ui-patterns/modality.mdx"
    content = modality.read_text().lower()
    # The comment should explain that formState values won't update without destructuring
    has_explanation = (
        ("destructure" in content and ("update" in content or "react" in content)) or
        ("formstate" in content and "won't" in content)
    )
    assert has_explanation, \
        "modality.mdx should explain why destructuring formState values is needed"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — cursor rule update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
