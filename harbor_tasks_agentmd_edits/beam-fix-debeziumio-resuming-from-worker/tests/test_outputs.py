"""
Task: beam-fix-debeziumio-resuming-from-worker
Repo: apache/beam @ 06dd48e9313ca81d8d0739b03d0850f129c08e56
PR:   37689

DebeziumIO crash-loops on worker restart because startTime is a static field
that becomes null when a new DoFn instance is created. The poll loop also
never exits when records are non-empty. The README documents internal
KafkaSourceConsumerFn constructors that no longer exist after the refactor.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/beam"
DEBEZIUM_SRC = f"{REPO}/sdks/java/io/debezium/src"
KSC_PATH = f"{DEBEZIUM_SRC}/main/java/org/apache/beam/io/debezium/KafkaSourceConsumerFn.java"
DIO_PATH = f"{DEBEZIUM_SRC}/main/java/org/apache/beam/io/debezium/DebeziumIO.java"
README_PATH = f"{DEBEZIUM_SRC}/README.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — source files exist and are non-empty
# ---------------------------------------------------------------------------

def test_source_files_exist():
    """Modified source files must exist and be non-empty."""
    for path in [KSC_PATH, DIO_PATH, README_PATH]:
        p = Path(path)
        assert p.exists(), f"{path} does not exist"
        assert p.stat().st_size > 100, f"{path} is too small"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_starttime_not_static():
    """startTime must not be a static field — static startTime causes NPE on worker restart.

    In the base commit, startTime is declared as 'private static DateTime startTime'.
    When a worker restarts, a new DoFn instance is created but the static field
    is null, causing a NullPointerException in the time-elapsed calculation.
    The fix makes it an instance field (non-static).
    """
    src = Path(KSC_PATH).read_text()
    # Find the startTime field declaration (not in comments or strings)
    lines = src.split("\n")
    for line in lines:
        stripped = line.strip()
        # Skip comments and blank lines
        if stripped.startswith("//") or stripped.startswith("*") or stripped.startswith("/*"):
            continue
        # Look for startTime field declaration
        if "DateTime" in stripped and "startTime" in stripped and not stripped.startswith("//"):
            assert "static" not in stripped or "static final" in stripped, (
                f"startTime must not be static (found: {stripped!r}). "
                "A static startTime causes NPE when a worker restarts."
            )


def test_starttime_initialized_in_setup():
    """startTime must be initialized in a @Setup lifecycle method, not in getInitialRestriction.

    The @Setup method runs once per DoFn instance (including after restart),
    ensuring startTime is always initialized before process() uses it.
    In the base commit, startTime was set in getInitialRestriction which only
    runs during initial restriction creation, not on worker restart.
    """
    src = Path(KSC_PATH).read_text()

    # Find @Setup annotation followed by a method that sets startTime
    setup_pattern = re.compile(
        r'@Setup\s+.*?public\s+void\s+\w+\s*\(\s*\)\s*\{[^}]*startTime\s*=',
        re.DOTALL,
    )
    assert setup_pattern.search(src), (
        "startTime must be initialized in a @Setup-annotated method. "
        "This ensures it is set on every worker restart."
    )

    # Verify getInitialRestriction does NOT set startTime
    gir_match = re.search(
        r'public\s+OffsetHolder\s+getInitialRestriction\b[^{]*\{(.*?)\n\s*\}',
        src,
        re.DOTALL,
    )
    if gir_match:
        gir_body = gir_match.group(1)
        assert "startTime" not in gir_body, (
            "startTime should not be set in getInitialRestriction — "
            "it must be in @Setup to survive worker restarts."
        )


def test_polling_timeout_configurable():
    """DebeziumIO.Read must expose a withPollingTimeout method.

    The poll loop needs a configurable timeout so users can tune latency vs throughput.
    The base commit has no such configuration — the poll runs with hardcoded behavior.
    """
    src = Path(DIO_PATH).read_text()
    assert "withPollingTimeout" in src, (
        "DebeziumIO.Read must have a withPollingTimeout method"
    )
    # Verify it's a public method, not just a reference
    assert re.search(r'public\s+Read<T>\s+withPollingTimeout\s*\(', src), (
        "withPollingTimeout must be a public method on Read<T>"
    )


def test_poll_loop_timeout_based():
    """The poll loop in process() must be timeout-based, not infinite.

    In the base commit, the inner loop is 'while (records != null && !records.isEmpty())'
    with 'records = task.poll()' at the end — this loops forever if poll() keeps
    returning non-empty results. The fix uses a timeout-based loop that exits
    after the polling timeout elapses.
    """
    src = Path(KSC_PATH).read_text()

    # The process method should NOT have the old pattern of re-polling at end of loop
    process_match = re.search(
        r'public\s+ProcessContinuation\s+process\b.*?\n\s*\}(?=\s*\n\s*public)',
        src,
        re.DOTALL,
    )
    assert process_match, "Could not find process() method"
    process_body = process_match.group(0)

    # Old pattern: 'records = task.poll()' at end of the while loop body
    # counts how many times task.poll() is called in process()
    poll_calls = re.findall(r'task\.poll\(\)', process_body)
    assert len(poll_calls) <= 1, (
        f"task.poll() should be called at most once per loop iteration (found {len(poll_calls)} calls). "
        "The old code re-polled at the end of the loop, causing it to never exit."
    )

    # Should have some form of timeout tracking
    assert "remainingTimeout" in process_body or "timeout" in process_body.lower() or "Stopwatch" in process_body, (
        "process() should use a timeout mechanism for the poll loop"
    )


def test_experimental_warning_removed():
    """The 'experimental' known-issue warning must be removed from DebeziumIO javadoc.

    The base commit has a javadoc paragraph warning that DebeziumIO is experimental
    and doesn't preserve offsets on restart. Since the fix resolves this issue,
    the warning should be removed.
    """
    src = Path(DIO_PATH).read_text()
    assert "currently experimental" not in src.lower(), (
        "The 'currently experimental' warning should be removed — the restart issue is fixed"
    )
    assert "does not\n * preserve the offset" not in src and "does not preserve the offset" not in src, (
        "The warning about not preserving offsets on restart should be removed"
    )


def test_tryclaim_no_time_check():
    """OffsetTracker.tryClaim must not reference startTime or check elapsed time.

    In the base commit, tryClaim accessed the static startTime to enforce time limits.
    After the fix, time-based stopping is handled in process() using the instance
    startTime, and tryClaim only checks record count limits.
    """
    src = Path(KSC_PATH).read_text()
    # Find tryClaim method
    tryclaim_match = re.search(
        r'public\s+boolean\s+tryClaim\b[^{]*\{(.*?)\n\s{4}\}',
        src,
        re.DOTALL,
    )
    assert tryclaim_match, "Could not find tryClaim method"
    tryclaim_body = tryclaim_match.group(1)

    # Should not reference startTime
    assert "startTime" not in tryclaim_body, (
        "tryClaim should not reference startTime — time checking moved to process()"
    )


# ---------------------------------------------------------------------------
# Config file update tests (config_edit) — README documentation
# ---------------------------------------------------------------------------


    The base commit README has a markdown table documenting:
      KafkaSourceConsumerFn(connectorClass, recordMapper, maxRecords)
      KafkaSourceConsumerFn(connectorClass, recordMapper, timeToRun)
    These constructors no longer exist after the refactor — the README must be
    updated to remove this outdated API documentation.
    """
    content = Path(README_PATH).read_text()
    assert "KafkaSourceConsumerFn(connectorClass, recordMapper, maxRecords)" not in content, (
        "README should not document the old KafkaSourceConsumerFn(connectorClass, recordMapper, maxRecords) constructor"
    )
    assert "KafkaSourceConsumerFn(connectorClass, recordMapper, timeToRun)" not in content, (
        "README should not document the old KafkaSourceConsumerFn(connectorClass, recordMapper, timeToRun) constructor"
    )



    After the refactor, users configure poll timeout and time-to-run through the
    DebeziumIO.Read transform builder, not through KafkaSourceConsumerFn constructors.
    The README should reflect this new API surface.
    """
    content = Path(README_PATH).read_text()
    # Check that README mentions the Read transform for configuration
    # Accept various wordings: "DebeziumIO.Read", "Read transform", etc.
    has_read_ref = (
        "DebeziumIO.Read" in content
        or "Read transform" in content
        or ".Read transform" in content
    )
    assert has_read_ref, (
        "README should reference DebeziumIO.Read transform as the way to configure "
        "time-based restrictions (replacing the old constructor documentation)"
    )
