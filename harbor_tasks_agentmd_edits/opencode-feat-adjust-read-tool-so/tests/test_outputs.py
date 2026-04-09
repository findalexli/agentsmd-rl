"""
Task: opencode-feat-adjust-read-tool-so
Repo: opencode-ai/opencode @ 170c7ad67abd840fd89aef3c79b5eff32e3aec5c
PR:   73

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
TARGET_FILE = f"{REPO}/internal/llm/provider/anthropic.go"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compiles():
    """Modified code compiles without errors."""
    r = subprocess.run(
        ["go", "build", "./internal/llm/provider/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_error_logs_instead_of_event():
    """Accumulation errors are logged as warnings instead of sending error events."""
    src = Path(TARGET_FILE).read_text()

    # Find the stream function and check the error handling pattern
    # Old (buggy): eventChan <- ProviderEvent{Type: EventError, Error: err}
    # New (fixed): logging.Warn("Error accumulating message", "error", err)

    # Check that the buggy pattern is NOT present
    assert 'eventChan <- ProviderEvent{Type: EventError, Error: err}' not in src, \
        "Buggy error event pattern still present - should use logging.Warn instead"

    # Check that the correct pattern IS present after Accumulate
    # Find the section around accumulatedMessage.Accumulate(event)
    lines = src.split('\n')
    for i, line in enumerate(lines):
        if 'accumulatedMessage.Accumulate(event)' in line:
            # Look at the next few lines for error handling
            context = '\n'.join(lines[i:i+5])
            assert 'logging.Warn' in context, \
                f"Error handling should use logging.Warn, found:\n{context}"
            assert 'Error accumulating message' in context, \
                f"Warning message should contain 'Error accumulating message', found:\n{context}"
            return

    raise AssertionError("Could not find accumulatedMessage.Accumulate(event) call")


# [pr_diff] fail_to_pass
def test_stream_continues_on_accumulate_error():
    """Stream continues processing after accumulation error instead of breaking."""
    src = Path(TARGET_FILE).read_text()

    # In the fix, after logging the warning, the code continues (not break/return)
    # We verify the structure: if err != nil { logging.Warn(...); continue }
    lines = src.split('\n')
    for i, line in enumerate(lines):
        if 'accumulatedMessage.Accumulate(event)' in line and i + 4 < len(lines):
            # Check the error handling block structure
            context_lines = lines[i:i+5]
            context = '\n'.join(context_lines)

            # Should have: if err != nil { ... continue }
            assert 'if err != nil' in context, "Missing error check after Accumulate"
            assert 'continue' in context, "Should continue processing, not break stream"

            # Should NOT have EventError in this context
            assert 'EventError' not in context, \
                "Should not send EventError in accumulation error handling"
            return

    raise AssertionError("Could not verify stream continuation behavior")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_no_regressions():
    """Go vet passes with no issues."""
    r = subprocess.run(
        ["go", "vet", "./internal/llm/provider/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"go vet failed:\n{r.stderr}"


# [static] pass_to_pass
def test_imports_present():
    """Required logging import is present."""
    src = Path(TARGET_FILE).read_text()

    # Check that logging package is imported
    assert '"github.com/opencode-ai/opencode/internal/logging"' in src, \
        "logging package import is missing"
