"""
Task: opencode-vouch-trust-management
Repo: anomalyco/opencode @ 31f893f8cb7cbec11ae743b4ead806c201a396b7
PR:   12640

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import yaml
from pathlib import Path

REPO = "/workspace/opencode"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_workflow_syntax_valid():
    """All workflow YAML files must be valid and parseable."""
    workflows_dir = Path(REPO) / ".github" / "workflows"
    workflow_files = [
        "vouch-check-issue.yml",
        "vouch-check-pr.yml",
        "vouch-manage-by-issue.yml",
        "compliance-close.yml",
    ]

    for wf in workflow_files:
        wf_path = workflows_dir / wf
        content = wf_path.read_text()
        # Must parse as valid YAML
        parsed = yaml.safe_load(content)
        assert parsed is not None, f"{wf} is not valid YAML"
        # Must have 'name' field
        assert "name" in parsed, f"{wf} missing 'name' field"
        # Must have 'on' (triggers) field
        assert "on" in parsed, f"{wf} missing 'on' (triggers) field"


# [static] pass_to_pass
def test_vouched_td_syntax_valid():
    """VOUCHED.td file must exist and follow expected format."""
    vouched_path = Path(REPO) / ".github" / "VOUCHED.td"
    assert vouched_path.exists(), "VOUCHED.td must exist"

    content = vouched_path.read_text()
    lines = content.strip().split("\n")

    # Check header comments
    assert "# Vouched contributors" in content, "VOUCHED.td must have header comment"
    assert "mitchellh/vouch" in content, "VOUCHED.td must reference vouch documentation"
    assert "Syntax:" in content, "VOUCHED.td must document the syntax"

    # Check that vouched usernames exist (non-empty file with entries)
    user_lines = [l for l in lines if l.strip() and not l.strip().startswith("#")]
    assert len(user_lines) >= 1, "VOUCHED.td must have at least one vouched user"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests for workflows
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_vouch_check_issue_workflow_structure():
    """vouch-check-issue.yml must have correct structure for checking denounced users."""
    wf_path = Path(REPO) / ".github" / "workflows" / "vouch-check-issue.yml"
    assert wf_path.exists(), "vouch-check-issue.yml must exist"

    content = wf_path.read_text()
    parsed = yaml.safe_load(content)

    # Must trigger on issues opened
    assert "issues" in parsed.get("on", {}), "Must trigger on issues"
    assert "opened" in parsed["on"]["issues"].get("types", []), "Must trigger on issue opened"

    # Must have job named 'check'
    assert "jobs" in parsed, "Must have jobs section"
    assert "check" in parsed["jobs"], "Must have 'check' job"

    # Must use github-script to interact with API
    job = parsed["jobs"]["check"]
    assert "steps" in job, "Must have steps"
    step_names = [s.get("name", "") for s in job["steps"]]
    assert any("denounced" in n.lower() for n in step_names), "Must check for denounced users"


# [pr_diff] fail_to_pass
def test_vouch_check_pr_workflow_structure():
    """vouch-check-pr.yml must have correct structure for checking PR authors."""
    wf_path = Path(REPO) / ".github" / "workflows" / "vouch-check-pr.yml"
    assert wf_path.exists(), "vouch-check-pr.yml must exist"

    content = wf_path.read_text()
    parsed = yaml.safe_load(content)

    # Must trigger on pull_request_target opened
    assert "pull_request_target" in parsed.get("on", {}), "Must trigger on pull_request_target"

    # Must have correct permissions (read contents, write pull-requests)
    perms = parsed.get("permissions", {})
    assert perms.get("contents") == "read", "Must have contents: read permission"
    assert perms.get("pull-requests") == "write", "Must have pull-requests: write permission"


# [pr_diff] fail_to_pass
def test_compliance_close_workflow_structure():
    """compliance-close.yml must check for issues/PRs with needs:compliance label."""
    wf_path = Path(REPO) / ".github" / "workflows" / "compliance-close.yml"
    assert wf_path.exists(), "compliance-close.yml must exist"

    content = wf_path.read_text()
    parsed = yaml.safe_load(content)

    # Must have schedule trigger
    assert "schedule" in parsed.get("on", {}), "Must have schedule trigger"

    # Must reference needs:compliance label
    assert "needs:compliance" in content, "Must reference needs:compliance label"
    assert "2-hour" in content or "2 hour" in content, "Must mention 2-hour window"


# [pr_diff] fail_to_pass
def test_duplicate_issues_workflow_updated():
    """duplicate-issues.yml must be updated with compliance check logic."""
    wf_path = Path(REPO) / ".github" / "workflows" / "duplicate-issues.yml"
    content = wf_path.read_text()

    # Must have the compliance check content added
    assert "CONTRIBUTING GUIDELINES COMPLIANCE CHECK" in content, \
        "Must include compliance check section"
    assert "issue-compliance" in content, \
        "Must reference issue-compliance marker"
    assert "needs:compliance" in content, \
        "Must reference needs:compliance label"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests (REQUIRED)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_contributing_md_documents_vouch_system():
    """CONTRIBUTING.md must document the vouch trust management system."""
    contributing_path = Path(REPO) / "CONTRIBUTING.md"
    assert contributing_path.exists(), "CONTRIBUTING.md must exist"

    content = contributing_path.read_text()

    # Must have Trust & Vouch System section
    assert "Trust & Vouch System" in content, \
        "CONTRIBUTING.md must have Trust & Vouch System section"

    # Must explain how it works
    assert "Vouched users" in content, "Must explain vouched users"
    assert "Denounced users" in content, "Must explain denounced users"

    # Must document maintainer commands
    assert "vouch" in content.lower(), "Must document vouch command"
    assert "denounce" in content.lower(), "Must document denounce command"

    # Must reference VOUCHED.td file
    assert "VOUCHED.td" in content, "Must reference VOUCHED.td file"


# [pr_diff] fail_to_pass
def test_contributing_md_documents_issue_requirements():
    """CONTRIBUTING.md must document issue template requirements."""
    contributing_path = Path(REPO) / "CONTRIBUTING.md"
    content = contributing_path.read_text()

    # Must have Issue Requirements section
    assert "Issue Requirements" in content, \
        "CONTRIBUTING.md must have Issue Requirements section"

    # Must mention blank issues not allowed
    assert "Blank issues" in content or "blank issues" in content.lower(), \
        "Must mention blank issues policy"

    # Must mention the 2-hour compliance window
    assert "2 hours" in content or "2 hour" in content, \
        "Must mention 2-hour compliance window"

    # Must list the required templates
    assert "Bug report" in content, "Must mention Bug report template"
    assert "Feature request" in content, "Must mention Feature request template"


# [pr_diff] fail_to_pass
def test_issue_template_config_disables_blank_issues():
    """ISSUE_TEMPLATE/config.yml must disable blank issues."""
    config_path = Path(REPO) / ".github" / "ISSUE_TEMPLATE" / "config.yml"
    assert config_path.exists(), "ISSUE_TEMPLATE/config.yml must exist"

    content = config_path.read_text()
    parsed = yaml.safe_load(content)

    # Must have blank_issues_enabled: false
    assert parsed.get("blank_issues_enabled") == False, \
        "blank_issues_enabled must be false"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_vouch_workflows_not_empty():
    """Vouch workflow files must have substantial content, not just stubs."""
    workflows = [
        ".github/workflows/vouch-check-issue.yml",
        ".github/workflows/vouch-check-pr.yml",
        ".github/workflows/vouch-manage-by-issue.yml",
        ".github/workflows/compliance-close.yml",
    ]

    for wf in workflows:
        wf_path = Path(REPO) / wf
        assert wf_path.exists(), f"{wf} must exist"

        content = wf_path.read_text()
        lines = content.strip().split("\n")

        # Must have at least 20 lines (not a stub)
        assert len(lines) >= 20, f"{wf} appears to be a stub (too few lines)"

        # Must have jobs section with actual content
        parsed = yaml.safe_load(content)
        assert "jobs" in parsed, f"{wf} must have jobs section"
        assert len(parsed["jobs"]) >= 1, f"{wf} must have at least one job"


# [static] pass_to_pass
def test_contributing_section_not_stub():
    """CONTRIBUTING.md vouch section must have substantial content."""
    contributing_path = Path(REPO) / "CONTRIBUTING.md"
    content = contributing_path.read_text()

    # Find the Trust & Vouch System section and verify it's substantial
    if "Trust & Vouch System" in content:
        # Split content and look at lines after the heading
        lines = content.split("\n")
        vouch_idx = None
        for i, line in enumerate(lines):
            if "Trust & Vouch System" in line:
                vouch_idx = i
                break

        if vouch_idx is not None:
            # Count lines until next ## heading or end
            section_lines = 0
            for line in lines[vouch_idx + 1:]:
                if line.startswith("## ") and "Trust" not in line:
                    break
                if line.strip():
                    section_lines += 1

            # Section should have at least 15 content lines
            assert section_lines >= 15, \
                "Trust & Vouch System section is too short (likely a stub)"
