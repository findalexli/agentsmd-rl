"""
Task: payload-i18n-race-fix-triage-skill
Repo: payloadcms/payload @ d3b12a1b06eff5831dca3bbb15f2ad064e663102
PR:   15206

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/payload"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript file and skill file must be valid."""
    test_file = Path(REPO) / "test" / "i18n" / "e2e.spec.ts"
    assert test_file.exists(), "test/i18n/e2e.spec.ts must exist"
    content = test_file.read_text()
    assert "describe('i18n'" in content or 'describe("i18n"' in content, \
        "i18n test suite must be present"
    assert "setUserLanguage" in content, "setUserLanguage helper must exist"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code fix: race condition in setUserLanguage
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_wait_for_server_action_completion():
    """setUserLanguage must wait for server action/response after language selection."""
    test_file = Path(REPO) / "test" / "i18n" / "e2e.spec.ts"
    content = test_file.read_text()

    # Find the setUserLanguage function region
    func_start = content.find("function setUserLanguage")
    assert func_start != -1, "setUserLanguage function must exist"

    # Extract a reasonable chunk covering the function body
    func_region = content[func_start:func_start + 2000]

    # Must contain some form of waiting for network response/server action
    wait_patterns = [
        "waitForResponse",
        "waitForEvent",
        "waitForLoadState",
        "waitForURL",
        "waitForNavigation",
    ]
    has_wait = any(pattern in func_region for pattern in wait_patterns)
    assert has_wait, (
        "setUserLanguage must explicitly wait for server action completion "
        "(e.g., waitForResponse, waitForEvent) after language selection "
        "to avoid race conditions in CI"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — new skill file
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    content = skill_path.read_text()
    assert len(content) > 200, "Skill file must have substantial content"

    # Must have YAML frontmatter
    assert content.startswith("---"), "Skill file must start with YAML frontmatter"
    frontmatter_end = content.find("---", 3)
    assert frontmatter_end > 3, "Frontmatter must be closed with ---"

    frontmatter = content[3:frontmatter_end]
    assert "name:" in frontmatter, "Frontmatter must include name field"
    assert "description:" in frontmatter, "Frontmatter must include description field"


# [config_edit] fail_to_pass

    # Must cover reproduction as a primary concept
    assert "reproduc" in content, \
        "Skill must discuss reproduction of CI failures"

    # Must cover the dev vs prod/bundled distinction
    assert "dev" in content and ("prod" in content or "bundl" in content), \
        "Skill must cover dev vs prod/bundled testing"

    # Must discuss common CI failure patterns
    has_patterns = (
        "race condition" in content
        or "flak" in content
        or "timing" in content
    )
    assert has_patterns, \
        "Skill must discuss common CI failure patterns (race conditions, flakiness, timing)"

    # Must reference Playwright as the e2e testing framework
    assert "playwright" in content, \
        "Skill must reference Playwright testing framework"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_tests_preserved():
    """All existing i18n test cases must still be present."""
    test_file = Path(REPO) / "test" / "i18n" / "e2e.spec.ts"
    content = test_file.read_text()

    expected_tests = [
        "ensure i18n labels and useTranslation hooks display correct translation",
        "ensure translations update correctly when switching language",
        "should show translated document field label",
        "should show translated pill field label",
        "should show fallback pill field label",
        "should show translated field label in where builder",
        "should display translated collections and globals config options",
    ]
    for test_name in expected_tests:
        assert test_name in content, \
            f"Test '{test_name}' must still exist in the file"
