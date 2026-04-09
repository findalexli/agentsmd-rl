"""Tests for sui-indexer-alt-reader batch fetch optimization.

This test module verifies that:
1. The checkpoints module uses try_join_all for concurrent fetching (fail_to_pass)
2. The events module uses batch_get_transactions instead of sequential calls (fail_to_pass)
3. The futures import is present for try_join_all (fail_to_pass)
4. The modified Rust files have valid syntax and formatting (pass_to_pass)

Note: cargo check is not performed due to heavy C++ dependencies (rocksdb)
that require significant disk space for compilation.
"""

import subprocess
from pathlib import Path

REPO = Path("/workspace/sui")
CHECKPOINTS_FILE = REPO / "crates/sui-indexer-alt-reader/src/checkpoints.rs"
EVENTS_FILE = REPO / "crates/sui-indexer-alt-reader/src/events.rs"


def test_checkpoints_try_join_all_import():
    """Verify futures::future::try_join_all is imported in checkpoints.rs (fail_to_pass).

    The fix requires importing try_join_all to enable concurrent checkpoint fetching.
    """
    content = CHECKPOINTS_FILE.read_text()
    assert "use futures::future::try_join_all;" in content, \
        "Missing required import: use futures::future::try_join_all;"


def test_checkpoints_concurrent_fetch_pattern():
    """Verify checkpoints use try_join_all instead of sequential loop (fail_to_pass).

    The original code used a for loop over keys; the fix should use try_join_all
    with futures created from keys.iter().map().
    """
    content = CHECKPOINTS_FILE.read_text()

    # Check for try_join_all usage
    assert "try_join_all(futures)" in content, \
        "Missing try_join_all(futures) call for concurrent checkpoint fetching"

    # Check that futures are created from keys
    assert "keys.iter().map(|key| async" in content, \
        "Missing concurrent pattern: keys.iter().map(|key| async"

    # Verify the old sequential pattern is removed
    assert "for key in keys {" not in content, \
        "Old sequential for loop still present - should be replaced with try_join_all"


def test_events_batch_fetch_pattern():
    """Verify events use batch_get_transactions instead of sequential get_transaction (fail_to_pass).

    The original code made individual get_transaction calls in a loop;
    the fix should use batch_get_transactions with digests collected upfront.
    """
    content = EVENTS_FILE.read_text()

    # Check for batch request pattern
    assert "BatchGetTransactionsRequest" in content, \
        "Missing BatchGetTransactionsRequest for batch transaction fetching"

    # Check for digests collection
    assert "let digests = keys.iter().map(|key| key.0.to_string()).collect();" in content, \
        "Missing digests collection pattern for batch request"

    # Check for batch_get_transactions call
    assert "batch_get_transactions(request)" in content or "batch_get_transactions(request).await" in content, \
        "Missing batch_get_transactions call"

    # Verify old sequential pattern is removed
    assert "get_transaction(request).await" not in content, \
        "Old sequential get_transaction call still present - should use batch_get_transactions"

    # Verify the old for loop over keys is removed
    assert "for key in keys {" not in content, \
        "Old sequential for loop still present in events.rs"


def test_events_result_processing():
    """Verify events properly process batch response results (fail_to_pass).

    The fix should filter and map the batch response transactions correctly.
    """
    content = EVENTS_FILE.read_text()

    # Check for filter_map on transactions
    assert ".transactions" in content and "into_iter()" in content, \
        "Missing transaction result iteration pattern"

    # Check for proper error handling in batch processing
    assert "collect::<anyhow::Result<_>>()" in content, \
        "Missing proper Result collection for batch transaction processing"


def test_checkpoints_error_handling():
    """Verify checkpoints handle NotFound errors correctly in concurrent context (fail_to_pass).

    The fix should convert NotFound errors to Ok(None) and other errors to Err.
    """
    content = CHECKPOINTS_FILE.read_text()

    # Check for NotFound handling returning Ok(None)
    assert "Ok(None)" in content, \
        "Missing Ok(None) pattern for NotFound error handling in concurrent context"

    # Check that errors are properly propagated
    assert "Err(Error::from(e))" in content or "Err(e.into())" in content, \
        "Missing proper error propagation in concurrent futures"


# =============================================================================
# Pass-to-Pass Tests (Repo CI Gates)
# =============================================================================
# These tests verify that the repo's CI checks pass on both base and fixed
# commits, ensuring the fix doesn't break existing functionality.


def test_repo_rustfmt_checkpoints():
    """Repo's rustfmt check passes on checkpoints.rs (pass_to_pass).

    Verifies that the checkpoints.rs file has valid Rust syntax and
    follows the project's formatting standards.
    """
    r = subprocess.run(
        ["rustfmt", "--check", "--edition", "2024", str(CHECKPOINTS_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"rustfmt check failed for checkpoints.rs:\n{r.stderr or r.stdout}"


def test_repo_rustfmt_events():
    """Repo's rustfmt check passes on events.rs (pass_to_pass).

    Verifies that the events.rs file has valid Rust syntax and
    follows the project's formatting standards.
    """
    r = subprocess.run(
        ["rustfmt", "--check", "--edition", "2024", str(EVENTS_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"rustfmt check failed for events.rs:\n{r.stderr or r.stdout}"


def test_repo_checkpoints_syntax_valid():
    """Checkpoints.rs has valid Rust syntax (pass_to_pass).

    Parses the file to ensure it compiles as valid Rust syntax.
    This catches syntax errors without requiring full compilation.
    """
    # Try to parse the file with rustfmt which validates syntax
    r = subprocess.run(
        ["rustfmt", "--check", "--edition", "2024", str(CHECKPOINTS_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    # rustfmt returns 0 if file is valid and formatted, 1 if needs formatting
    # A syntax error would return a different exit code or error message
    assert r.returncode in (0, 1), \
        f"Syntax error in checkpoints.rs:\n{r.stderr}"
    assert "error" not in r.stderr.lower(), \
        f"Syntax error detected in checkpoints.rs:\n{r.stderr}"


def test_repo_events_syntax_valid():
    """Events.rs has valid Rust syntax (pass_to_pass).

    Parses the file to ensure it compiles as valid Rust syntax.
    This catches syntax errors without requiring full compilation.
    """
    # Try to parse the file with rustfmt which validates syntax
    r = subprocess.run(
        ["rustfmt", "--check", "--edition", "2024", str(EVENTS_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    # rustfmt returns 0 if file is valid and formatted, 1 if needs formatting
    # A syntax error would return a different exit code or error message
    assert r.returncode in (0, 1), \
        f"Syntax error in events.rs:\n{r.stderr}"
    assert "error" not in r.stderr.lower(), \
        f"Syntax error detected in events.rs:\n{r.stderr}"
