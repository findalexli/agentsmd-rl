"""
Task: opencode-smarter-changelog
Repo: anomalyco/opencode @ 057848deb847d59250e7db08ab2402f4a69bfcda
PR:   20138

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/opencode"


def _run_bun(script: str, extra_args: list[str] = None, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a bun script in the repo directory."""
    args = ["bun", script] + (extra_args or [])
    return subprocess.run(
        args,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (code behavior) — subprocess execution
# ---------------------------------------------------------------------------


def test_raw_changelog_runs():
    """script/raw-changelog.ts exists and --help outputs usage info."""
    result = _run_bun("script/raw-changelog.ts", ["--help"])
    assert result.returncode == 0, f"raw-changelog.ts --help failed:\n{result.stderr}"
    assert "Starting version" in result.stdout, f"Missing 'Starting version' in help:\n{result.stdout}"


def test_changelog_wrapper_flags():
    """script/changelog.ts --help shows new --variant and --quiet flags."""
    result = _run_bun("script/changelog.ts", ["--help"])
    assert result.returncode == 0, f"changelog.ts --help failed:\n{result.stderr}"
    assert "--variant" in result.stdout, f"Missing --variant flag in help:\n{result.stdout}"
    assert "--quiet" in result.stdout, f"Missing --quiet flag in help:\n{result.stdout}"
    assert "--print" in result.stdout, f"Missing --print flag in help:\n{result.stdout}"


def test_version_uses_bun_script():
    """script/version.ts calls bun script/changelog.ts instead of opencode run."""
    content = Path(f"{REPO}/script/version.ts").read_text()
    assert "bun script/changelog.ts" in content, \
        "version.ts should call 'bun script/changelog.ts'"


# ---------------------------------------------------------------------------
# Fail-to-pass (config update) — instruction file changes
# ---------------------------------------------------------------------------


def test_command_uses_raw_changelog():
    """changelog.md command uses raw-changelog.ts for input generation."""
    content = Path(f"{REPO}/.opencode/command/changelog.md").read_text()
    assert "raw-changelog.ts" in content, \
        "changelog.md should reference raw-changelog.ts as the input source"


def test_command_user_focus_guidance():
    """changelog.md includes user-focused guidance about understanding flow-on effects."""
    content = Path(f"{REPO}/.opencode/command/changelog.md").read_text()
    content_lower = content.lower()
    assert ("flow on effect" in content_lower or
            "flow-on effect" in content_lower or
            "users will skim" in content_lower), \
        "changelog.md should include guidance about user focus and flow-on effects"


def test_command_wraps_input_in_tags():
    """changelog.md wraps the changelog input in <changelog_input> tags."""
    content = Path(f"{REPO}/.opencode/command/changelog.md").read_text()
    assert "<changelog_input>" in content, \
        "changelog.md should wrap input in <changelog_input> tags"
    assert "</changelog_input>" in content, \
        "changelog.md should close the <changelog_input> tag"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------


def test_raw_changelog_has_sections():
    """raw-changelog.ts defines section mapping for all product areas."""
    content = Path(f"{REPO}/script/raw-changelog.ts").read_text()
    for section in ["Core", "TUI", "Desktop", "SDK", "Extensions"]:
        assert section in content, f"raw-changelog.ts missing section: {section}"


def test_command_preserves_attribution_rules():
    """changelog.md preserves deterministic attribution rules from original."""
    content = Path(f"{REPO}/.opencode/command/changelog.md").read_text()
    assert "(@username)" in content, \
        "changelog.md should preserve (@username) attribution rule"
    assert "Do not derive" in content, \
        "changelog.md should preserve 'Do not derive' rule"
