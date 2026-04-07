"""
Task: goose-remove-clippy-lint-decompose-functions
Repo: block/goose @ 948cb91d5402b6175d4ff6386e8e02beea6b86cd
PR:   7064

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/goose"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_build_session_decomposed():
    """build_session must be refactored into focused helper functions."""
    builder = Path(f"{REPO}/crates/goose-cli/src/session/builder.rs")
    content = builder.read_text()

    # The original monolithic build_session should now delegate to helpers
    required_helpers = [
        "fn resolve_provider_and_model",
        "fn resolve_session_id",
        "fn handle_resumed_session_workdir",
        "fn resolve_and_load_extensions",
        "fn configure_session_prompts",
    ]

    for helper in required_helpers:
        assert helper in content, f"Missing helper function: {helper}"

    # build_session must call the helpers (not just define them)
    assert "resolve_provider_and_model(" in content, \
        "build_session must call resolve_provider_and_model"
    assert "resolve_session_id(" in content, \
        "build_session must call resolve_session_id"
    assert "handle_resumed_session_workdir(" in content, \
        "build_session must call handle_resumed_session_workdir"


def test_clippy_toml_created():
    """clippy.toml must exist with too-many-lines-threshold setting."""
    clippy_toml = Path(f"{REPO}/clippy.toml")
    assert clippy_toml.exists(), "clippy.toml must exist"
    content = clippy_toml.read_text()
    assert "too-many-lines-threshold" in content, \
        "clippy.toml must contain too-many-lines-threshold"
    match = re.search(r"too-many-lines-threshold\s*=\s*(\d+)", content)
    assert match, "too-many-lines-threshold must have a numeric value"
    threshold = int(match.group(1))
    assert threshold > 0, "too-many-lines-threshold must be positive"


def test_old_infrastructure_removed():
    """Old custom clippy scripts and baseline files must be removed."""
    assert not Path(f"{REPO}/scripts/clippy-lint.sh").exists(), \
        "scripts/clippy-lint.sh must be removed"
    assert not Path(f"{REPO}/scripts/clippy-baseline.sh").exists(), \
        "scripts/clippy-baseline.sh must be removed"
    assert not Path(f"{REPO}/clippy-baselines/too_many_lines.txt").exists(), \
        "clippy-baselines/too_many_lines.txt must be removed"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config / pr_diff) — config file update tests
# ---------------------------------------------------------------------------


def test_agents_md_standard_clippy():
    """AGENTS.md must reference standard cargo clippy, not ./scripts/clippy-lint.sh."""
    agents_md = Path(f"{REPO}/AGENTS.md")
    content = agents_md.read_text()

    assert "./scripts/clippy-lint.sh" not in content, \
        "AGENTS.md should not reference ./scripts/clippy-lint.sh"
    assert "cargo clippy --all-targets" in content, \
        "AGENTS.md must reference 'cargo clippy --all-targets'"
    assert "Merge without running clippy" in content, \
        "AGENTS.md 'Never' rule should use generic clippy reference"


def test_copilot_instructions_updated():
    """.github/copilot-instructions.md must use standard cargo clippy."""
    copilot = Path(f"{REPO}/.github/copilot-instructions.md")
    content = copilot.read_text()

    assert "./scripts/clippy-lint.sh" not in content, \
        "copilot-instructions.md should not reference ./scripts/clippy-lint.sh"
    assert "cargo clippy --all-targets" in content, \
        "copilot-instructions.md must reference 'cargo clippy --all-targets'"
    assert "CI handles this (clippy)" in content, \
        "copilot-instructions.md should reference standard clippy in skip section"


def test_doc_files_consistent():
    """HOWTOAI.md, CONTRIBUTING.md, and Justfile must use standard clippy."""
    # HOWTOAI.md
    howtoai = Path(f"{REPO}/HOWTOAI.md")
    content = howtoai.read_text()
    assert "./scripts/clippy-lint.sh" not in content, \
        "HOWTOAI.md should not reference ./scripts/clippy-lint.sh"
    assert "cargo clippy --all-targets" in content, \
        "HOWTOAI.md must reference standard clippy command"
    assert "clippy.toml" in content, \
        "HOWTOAI.md should reference clippy.toml (not clippy-baselines/)"

    # CONTRIBUTING.md
    contributing = Path(f"{REPO}/CONTRIBUTING.md")
    content = contributing.read_text()
    assert "./scripts/clippy-lint.sh" not in content, \
        "CONTRIBUTING.md should not reference ./scripts/clippy-lint.sh"
    assert "cargo clippy --all-targets" in content, \
        "CONTRIBUTING.md must reference standard clippy command"

    # Justfile
    justfile = Path(f"{REPO}/Justfile")
    content = justfile.read_text()
    assert "./scripts/clippy-lint.sh" not in content, \
        "Justfile should not reference ./scripts/clippy-lint.sh"
    assert "cargo clippy --all-targets" in content, \
        "Justfile must reference standard clippy command"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + syntax checks
# ---------------------------------------------------------------------------


def test_rust_syntax_valid():
    """builder.rs must have valid Rust function syntax (balanced braces, fn declarations)."""
    builder = Path(f"{REPO}/crates/goose-cli/src/session/builder.rs")
    content = builder.read_text()

    open_braces = content.count("{")
    close_braces = content.count("}")
    assert open_braces == close_braces, \
        f"Unbalanced braces in builder.rs: {open_braces} open, {close_braces} close"

    fn_pattern = r"(?:pub\s+)?(?:async\s+)?fn\s+\w+"
    functions = re.findall(fn_pattern, content)
    assert len(functions) >= 10, \
        f"builder.rs should have at least 10 function declarations, found {len(functions)}"
