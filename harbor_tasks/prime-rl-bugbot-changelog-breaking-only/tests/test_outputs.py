"""Behavioral tests for prime-rl PR #2191: scope changelog + bugbot to breaking changes only."""
from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path("/workspace/prime-rl")
BUGBOT = REPO / ".cursor" / "BUGBOT.md"
CHANGELOG = REPO / "CHANGELOG.md"


def _read(p: Path) -> str:
    assert p.exists(), f"missing file: {p}"
    return p.read_text()


# --- Track 1: signal-line greps on the tier-1 markdown. ---
# Each test maps 1:1 to a check id in eval_manifest.yaml.

def test_bugbot_scope_is_breaking_only():
    """The Changelog Enforcement section must scope the rule to **breaking** changes."""
    body = _read(BUGBOT)
    assert "**breaking**" in body, (
        "BUGBOT.md must use **breaking** (bolded) when describing the new "
        "enforcement scope; saw:\n" + body
    )


def test_bugbot_lists_three_breaking_categories():
    """BUGBOT.md must enumerate the three breaking-change categories as bullets."""
    body = _read(BUGBOT)
    for cat in ("**Renamed**", "**Removed**", "**Moved**"):
        assert cat in body, (
            f"BUGBOT.md is missing the {cat} bullet for breaking categories; "
            f"got:\n{body}"
        )


def test_bugbot_excludes_additive_and_default_changes():
    """BUGBOT.md must explicitly say additive + default-value changes do NOT require an entry."""
    body = _read(BUGBOT)
    assert "Additive" in body, "BUGBOT.md must mention 'Additive' changes as excluded"
    assert "default value" in body, "BUGBOT.md must call out 'default value' changes as excluded"
    assert "do **not** require" in body, (
        "BUGBOT.md must contain the exclusion phrase 'do **not** require'"
    )


def test_bugbot_references_current_config_path():
    """BUGBOT.md must point to the current config path src/prime_rl/configs/."""
    body = _read(BUGBOT)
    assert "src/prime_rl/configs/" in body, (
        "BUGBOT.md must reference 'src/prime_rl/configs/' (the current config "
        "package); the stale per-file paths should be gone."
    )


def test_changelog_header_describes_breaking_scope():
    """CHANGELOG.md description (line 3) must announce the breaking-only scope."""
    lines = _read(CHANGELOG).splitlines()
    assert len(lines) >= 3, f"CHANGELOG.md too short: {lines}"
    assert lines[0] == "# Changelog", f"unexpected heading: {lines[0]!r}"
    desc = lines[2]
    assert "**breaking**" in desc, (
        f"CHANGELOG.md header description must use **breaking**; got: {desc!r}"
    )


def test_changelog_entries_preserved():
    """Pass-to-pass: the historical CHANGELOG entries below the header must be untouched."""
    body = _read(CHANGELOG)
    # Anchor on a known historical entry from the base commit.
    assert "**`log.file` and `log.env_worker_logs` removed**" in body, (
        "Historical CHANGELOG entries must remain — only the header description changes."
    )
    assert "**`trainer.log.ranks_filter` (NEW)**" in body
    assert "**`model.lora`**: Moved from `model.experimental.lora`" in body


# --- Pass-to-pass: repo invariants that must hold before AND after. ---

def test_bugbot_file_is_valid_utf8_markdown():
    """Tier-1 file remains a non-empty UTF-8 markdown file with the expected H1/H2."""
    body = _read(BUGBOT)
    assert body.strip(), "BUGBOT.md must not be empty"
    assert body.startswith("# BugBot Instructions"), (
        f"BUGBOT.md must keep its top-level heading; got first line: {body.splitlines()[0]!r}"
    )
    assert "## Changelog Enforcement" in body, (
        "BUGBOT.md must keep the '## Changelog Enforcement' subsection heading"
    )


def test_repo_git_state_clean_or_modified_only():
    """Repo working tree must only contain modifications to the two target files (no new files,
    no deletions of unrelated files)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"
    allowed = {".cursor/BUGBOT.md", "CHANGELOG.md"}
    for line in r.stdout.splitlines():
        # Format: "XY path"
        path = line[3:].strip()
        if not path:
            continue
        assert path in allowed, (
            f"unexpected modification to '{path}'; this task should only "
            f"modify {sorted(allowed)}. Full git status:\n{r.stdout}"
        )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_unit_tests_run_tests():
    """pass_to_pass | CI job 'Unit tests' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'PYTEST_OUTPUT_DIR=/tmp/outputs uv run pytest tests/unit -m "not gpu"'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")