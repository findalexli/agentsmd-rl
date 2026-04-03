"""
Task: payload-template-remove-cloud-refs
Repo: payloadcms/payload @ 39bead7e4c6c05644ad9987a6224fb8de34928de
PR:   14484

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/payload"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code: BeforeDashboard component cleanup
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_website_dashboard_no_cloud_mention():
    """Website BeforeDashboard component must not reference Payload Cloud."""
    tsx = Path(REPO) / "templates/website/src/components/BeforeDashboard/index.tsx"
    content = tsx.read_text()
    assert "Payload Cloud" not in content, \
        "BeforeDashboard still mentions 'Payload Cloud'"
    assert "GitHub Scope" not in content, \
        "BeforeDashboard still mentions 'GitHub Scope'"


# [pr_diff] fail_to_pass
def test_vercel_website_dashboard_no_cloud_mention():
    """with-vercel-website BeforeDashboard must not reference Payload Cloud."""
    tsx = Path(REPO) / "templates/with-vercel-website/src/components/BeforeDashboard/index.tsx"
    content = tsx.read_text()
    assert "Payload Cloud" not in content, \
        "with-vercel-website BeforeDashboard still mentions 'Payload Cloud'"
    assert "GitHub Scope" not in content, \
        "with-vercel-website BeforeDashboard still mentions 'GitHub Scope'"


# [pr_diff] fail_to_pass
def test_website_dashboard_preserves_other_items():
    """BeforeDashboard must still contain the other list items (seed, modify, commit)."""
    tsx = Path(REPO) / "templates/website/src/components/BeforeDashboard/index.tsx"
    content = tsx.read_text()
    assert "SeedButton" in content, "SeedButton reference should be preserved"
    assert "Modify your" in content or "collections" in content, \
        "Modify-your-collections list item should be preserved"
    assert "Welcome to your dashboard" in content, \
        "Welcome banner should be preserved"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass — regression: key content preserved
# ---------------------------------------------------------------------------

# [static] pass_to_pass


# [static] pass_to_pass


# [static] pass_to_pass


# [static] pass_to_pass
