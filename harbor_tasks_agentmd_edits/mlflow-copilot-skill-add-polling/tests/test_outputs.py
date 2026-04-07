"""
Task: mlflow-copilot-skill-add-polling
Repo: mlflow/mlflow @ 91ce5a5514917a562304c7946c9c6313b88cce40
PR:   21684

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
from pathlib import Path

import yaml

REPO = "/workspace/mlflow"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / YAML validity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_skill_frontmatter_valid():
    """SKILL.md has valid YAML frontmatter."""
    skill_md = Path(REPO) / ".claude" / "skills" / "copilot" / "SKILL.md"
    content = skill_md.read_text()
    assert content.startswith("---"), "SKILL.md must start with YAML frontmatter"
    end = content.index("---", 3)
    frontmatter = content[3:end].strip()
    data = yaml.safe_load(frontmatter)
    assert "name" in data
    assert "allowed-tools" in data


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — poll.sh code tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_poll_script_exists_executable():
    """poll.sh exists and is executable."""
    poll_sh = Path(REPO) / ".claude" / "skills" / "copilot" / "poll.sh"
    assert poll_sh.exists(), "poll.sh must exist"
    assert os.access(poll_sh, os.X_OK), "poll.sh must be executable"


# [pr_diff] fail_to_pass
def test_poll_script_syntax_valid():
    """poll.sh passes bash syntax check."""
    poll_sh = Path(REPO) / ".claude" / "skills" / "copilot" / "poll.sh"
    r = subprocess.run(
        ["bash", "-n", str(poll_sh)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"bash -n failed: {r.stderr}"


# [pr_diff] fail_to_pass
def test_poll_script_requires_args():
    """poll.sh fails when invoked without required arguments."""
    poll_sh = Path(REPO) / ".claude" / "skills" / "copilot" / "poll.sh"
    r = subprocess.run(
        ["bash", str(poll_sh)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode != 0, "poll.sh should fail without arguments"


# [pr_diff] fail_to_pass
def test_poll_script_api_and_event():
    """poll.sh uses the GitHub timeline API and checks for copilot_work_finished."""
    poll_sh = Path(REPO) / ".claude" / "skills" / "copilot" / "poll.sh"
    content = poll_sh.read_text()
    assert "timeline" in content, "poll.sh must use the GitHub timeline API"
    assert "copilot_work_finished" in content, \
        "poll.sh must check for copilot_work_finished event"
    assert "1800" in content or "max_seconds" in content, \
        "poll.sh must have a timeout mechanism"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — SKILL.md config update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_allows_poll_tool():
    """SKILL.md allowed-tools includes poll.sh."""
    skill_md = Path(REPO) / ".claude" / "skills" / "copilot" / "SKILL.md"
    content = skill_md.read_text()
    end = content.index("---", 3)
    frontmatter = content[3:end].strip()
    data = yaml.safe_load(frontmatter)
    tools = data.get("allowed-tools", [])
    assert any("poll.sh" in t for t in tools), \
        f"allowed-tools must include poll.sh, got: {tools}"


# [pr_diff] fail_to_pass
def test_skill_polling_docs():
    """SKILL.md has a polling for completion section with usage instructions."""
    skill_md = Path(REPO) / ".claude" / "skills" / "copilot" / "SKILL.md"
    content = skill_md.read_text()
    content_lower = content.lower()
    assert "polling" in content_lower, \
        "SKILL.md must have a polling section"
    assert "poll.sh" in content, \
        "SKILL.md must reference poll.sh in the polling section"
