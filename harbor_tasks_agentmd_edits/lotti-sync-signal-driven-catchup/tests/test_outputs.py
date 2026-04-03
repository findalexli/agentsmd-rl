"""
Task: lotti-sync-signal-driven-catchup
Repo: matthiasn/lotti @ 392b12196ef1c1c1b7fb7d49fac0635da9a60b61
PR:   2371

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/lotti"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structure checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Dart files have balanced braces."""
    files = [
        "lib/features/sync/matrix/pipeline/catch_up_strategy.dart",
        "lib/features/sync/matrix/pipeline/matrix_stream_consumer.dart",
    ]
    for rel in files:
        p = Path(REPO) / rel
        content = p.read_text()
        assert content.count("{") == content.count("}"), \
            f"Unbalanced curly braces in {rel}"
        assert content.count("(") == content.count(")"), \
            f"Unbalanced parens in {rel}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code behavior tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_catchup_escalates_when_snapshot_full():
    """needsMore() must continue escalating when snapshot is full (events.length >= limit)."""
    strategy = Path(REPO) / "lib/features/sync/matrix/pipeline/catch_up_strategy.dart"
    content = strategy.read_text()

    # The fix adds a check: return events.length >= limit
    # This ensures catch-up continues when the snapshot is full (hasn't reached timeline end)
    assert "events.length >= limit" in content, \
        "catch_up_strategy.dart must check events.length >= limit to continue escalation"

    # The old code just returned needCount || needSinceTs without the full-snapshot check.
    # Verify the fix structure: pre-context check returns early, then full-snapshot check
    # Find the needsMore function body
    needs_more_match = re.search(
        r'bool needsMore\(\)\s*\{(.*?)\n\s*\}',
        content,
        re.DOTALL,
    )
    assert needs_more_match, "needsMore() function not found"
    body = needs_more_match.group(1)

    # The pre-context check should be separate from the full-snapshot check
    assert "needCount || needSinceTs" in body, \
        "Pre-context check (needCount || needSinceTs) must still be present"
    assert "events.length >= limit" in body, \
        "Full-snapshot escalation check must be in needsMore()"


# [pr_diff] fail_to_pass
def test_signal_driven_catchup_with_guard():
    """Stream consumer uses _catchUpInFlight guard and always triggers catch-up on signals."""
    consumer = Path(REPO) / "lib/features/sync/matrix/pipeline/matrix_stream_consumer.dart"
    content = consumer.read_text()

    # Must have the in-flight guard field
    assert "_catchUpInFlight" in content, \
        "Consumer must declare _catchUpInFlight guard"

    # Old conditional flags must be gone
    assert "_initialCatchUpCompleted" not in content, \
        "Old _initialCatchUpCompleted flag must be removed"
    assert "_firstStreamEventCatchUpTriggered" not in content, \
        "Old _firstStreamEventCatchUpTriggered flag must be removed"

    # Must call forceRescan with includeCatchUp on signal
    assert "forceRescan(includeCatchUp:" in content or \
           "forceRescan(includeCatchUp :" in content, \
        "Consumer must call forceRescan(includeCatchUp: ...) on stream signal"

    # The in-flight guard pattern: set true before, reset in whenComplete
    assert "whenComplete" in content, \
        "Consumer must reset _catchUpInFlight in whenComplete callback"


# [pr_diff] fail_to_pass
def test_self_origin_suppression():
    """Consumer suppresses self-origin events using senderId comparison."""
    consumer = Path(REPO) / "lib/features/sync/matrix/pipeline/matrix_stream_consumer.dart"
    content = consumer.read_text()

    # The fix adds: final isSelfOrigin = e.senderId == _client.userID;
    # and: final suppressed = _sentEventRegistry.consume(eventId) || isSelfOrigin;
    # At base, senderId only appears in a log string — the fix introduces it as
    # a suppression condition combined with the sent-event registry check.
    assert "isSelfOrigin" in content, \
        "Consumer must declare an isSelfOrigin variable for self-origin suppression"

    # Verify the suppression combines registry + self-origin check
    assert "|| isSelfOrigin" in content or "||isSelfOrigin" in content, \
        "Suppression must combine sentEventRegistry.consume with isSelfOrigin"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — documentation / config file updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must describe the new signal-driven catch-up behavior
    assert "signal-driven" in content.lower() or "signal driven" in content.lower(), \
        "README should describe signal-driven ingestion"

    # Must mention in-flight guard preventing overlapping catch-ups
    assert "in-flight" in content.lower() or "inflight" in content.lower() or \
           "overlap" in content.lower(), \
        "README should mention the in-flight guard or overlap prevention"

    # Must mention forceRescan with catch-up
    assert "forceRescan" in content or "force rescan" in content.lower() or \
           "forcescan" in content.lower(), \
        "README should reference forceRescan behavior"

    # Must mention marker advancement only from ordered slices
    assert "marker" in content.lower() and ("ordered" in content.lower() or "slice" in content.lower()), \
        "README should explain marker advancement from ordered slices"


# [config_edit] fail_to_pass

    # The key helpers section must use the new paths
    assert "matrix/pipeline/catch_up_strategy.dart" in content, \
        "README should reference matrix/pipeline/catch_up_strategy.dart"
    assert "matrix/pipeline/attachment_index.dart" in content, \
        "README should reference matrix/pipeline/attachment_index.dart"

    # The old pipeline_v2/ references for catch_up_strategy should NOT appear
    # (Note: pipeline_v2 might still appear in other contexts like docs reference,
    #  but the key helpers section should be updated)
    helpers_section = content[content.find("Key helpers:"):]
    assert "pipeline_v2/catch_up_strategy" not in helpers_section, \
        "README Key helpers section should not reference old pipeline_v2/ path"


# [config_edit] fail_to_pass

    # Must document the signal-driven catch-up change
    assert "signal-driven" in content.lower() or "signal driven" in content.lower(), \
        "sync_summary.md should document signal-driven catch-up"

    # Must document forceRescan with includeCatchUp
    assert "forceRescan" in content or "includeCatchUp" in content, \
        "sync_summary.md should mention forceRescan/includeCatchUp"

    # Must document backlog completion escalation
    assert "backlog" in content.lower() or "escalat" in content.lower(), \
        "sync_summary.md should document backlog completion or escalation"

    # Must mention in-flight guard
    assert "in-flight" in content.lower() or "inflight" in content.lower(), \
        "sync_summary.md should mention the in-flight guard"
