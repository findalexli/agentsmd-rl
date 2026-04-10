"""Tests for the task - including pass_to_pass and fail_to_pass tests."""

import subprocess
import sys

# Docker-internal path to the repo (from Dockerfile WORKDIR)
REPO = "/workspace/opencode"


def test_repo_typecheck():
    """TypeScript typecheck passes on the repo (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "run", "typecheck"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


def test_repo_app_typecheck():
    """TypeScript typecheck passes on packages/app (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "--cwd", "packages/app", "typecheck"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"App typecheck failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_app_unit_tests():
    """Unit tests pass for packages/app (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "--cwd", "packages/app", "test:unit"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"App unit tests failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


def test_repo_hello_script():
    """Basic bun script execution works (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "run", "hello"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Hello script failed:\n{r.stderr}"
    assert "Hello World!" in r.stdout, f"Expected 'Hello World!' in output, got: {r.stdout}"


# Fail-to-pass tests for PR #21822: compaction should retain recent conversation context

def test_compaction_has_tail_constants():
    """FAIL-TO-PASS: Compaction module has tail constants for recent context retention.

    PR #21822 fix adds DEFAULT_TAIL_TURNS, MIN_TAIL_TOKENS, MAX_TAIL_TOKENS constants.
    These are needed to determine how many recent conversation turns to preserve.
    """
    # Read the compaction.ts file and verify the constants exist
    compaction_file = f"{REPO}/packages/opencode/src/session/compaction.ts"
    with open(compaction_file, "r") as f:
        content = f.read()

    assert "DEFAULT_TAIL_TURNS" in content, \
        "Missing DEFAULT_TAIL_TURNS constant - compaction won't know how many turns to preserve"
    assert "MIN_TAIL_TOKENS" in content, \
        "Missing MIN_TAIL_TOKENS constant - compaction won't have minimum token budget"
    assert "MAX_TAIL_TOKENS" in content, \
        "Missing MAX_TAIL_TOKENS constant - compaction won't have maximum token limit"


def test_compaction_has_tail_budget_function():
    """FAIL-TO-PASS: Compaction module has tailBudget function for calculating tail size.

    PR #21822 fix adds a tailBudget function that calculates how much of the conversation
    context to reserve for recent turns. Without this, all context may be compacted away.
    """
    compaction_file = f"{REPO}/packages/opencode/src/session/compaction.ts"
    with open(compaction_file, "r") as f:
        content = f.read()

    assert "function tailBudget" in content, \
        "Missing tailBudget function - compaction can't calculate budget for recent turns"


def test_compaction_has_select_function():
    """FAIL-TO-PASS: Compaction module has select function for choosing messages to preserve.

    PR #21822 fix adds a select function that chooses which messages to preserve vs compact.
    This is the core logic that ensures recent conversation context is retained.
    """
    compaction_file = f"{REPO}/packages/opencode/src/session/compaction.ts"
    with open(compaction_file, "r") as f:
        content = f.read()

    assert "function select" in content or "const select" in content, \
        "Missing select function - compaction can't select which messages to preserve"
    assert "tail_start_id" in content, \
        "Missing tail_start_id handling - compaction can't track where tail starts"


def test_compaction_prompt_updated():
    """FAIL-TO-PASS: Compaction prompt mentions retaining recent turns.

    PR #21822 fix updates the compaction prompt to clarify that recent turns are preserved.
    The old prompt didn't mention this, leading to confusion in the summary.
    """
    compaction_file = f"{REPO}/packages/opencode/src/session/compaction.ts"
    with open(compaction_file, "r") as f:
        content = f.read()

    # The fix updates the prompt to mention that recent turns are retained verbatim
    assert "retained recent turns" in content or "recent turns will remain verbatim" in content or \
           "recent turns outside this summary" in content.lower(), \
        "Compaction prompt doesn't mention retaining recent turns - agents won't know context is preserved"


def test_compaction_imports_provider_transform():
    """FAIL-TO-PASS: Compaction module imports ProviderTransform for token calculations.

    PR #21822 fix imports ProviderTransform to calculate max output tokens for budget.
    Without this import, the tailBudget function can't calculate usable tokens.
    """
    compaction_file = f"{REPO}/packages/opencode/src/session/compaction.ts"
    with open(compaction_file, "r") as f:
        content = f.read()

    assert "ProviderTransform" in content, \
        "Missing ProviderTransform import - tailBudget can't calculate usable context"


def test_config_has_compaction_tail_settings():
    """FAIL-TO-PASS: Config schema supports compaction tail_turns and tail_tokens.

    PR #21822 fix adds tail_turns and tail_tokens to the compaction config schema.
    These settings allow users to configure how many recent turns to preserve.
    """
    config_file = f"{REPO}/packages/opencode/src/config/config.ts"
    with open(config_file, "r") as f:
        content = f.read()

    assert "tail_turns" in content, \
        "Config schema missing tail_turns - users can't configure turns to preserve"
    assert "tail_tokens" in content, \
        "Config schema missing tail_tokens - users can't configure token budget for tail"
