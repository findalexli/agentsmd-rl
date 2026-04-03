"""
Task: lotti-feat-prevent-gap-detection-for
Repo: lotti @ 5d434148cd4a4be9c10451cc7fdb2fbece7a1244
PR:   2508

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/lotti"
SERVICE_FILE = Path(REPO) / "lib/features/sync/sequence/sync_sequence_log_service.dart"
README_FILE = Path(REPO) / "lib/features/sync/README.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Dart files must be syntactically valid (balanced braces)."""
    src = SERVICE_FILE.read_text()
    # Basic structural check: balanced braces
    open_braces = src.count("{")
    close_braces = src.count("}")
    assert open_braces == close_braces, (
        f"Unbalanced braces in service file: {open_braces} open vs {close_braces} close"
    )
    # File must contain the class definition
    assert "class SyncSequenceLogService" in src, "Service class definition missing"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests (code)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_gap_detection_checks_host_online_status():
    """Gap detection must check host online status via getHostLastSeen before
    deciding whether to detect gaps for that host."""
    src = SERVICE_FILE.read_text()
    # The code must call getHostLastSeen for hosts in the VC loop
    assert "getHostLastSeen" in src, (
        "Service must call getHostLastSeen to check if a host has been seen online"
    )
    # The call must happen in the recordReceivedEntry method context
    # Find the method and check getHostLastSeen is used within it
    method_match = re.search(
        r"Future<List.*?recordReceivedEntry\b.*?\{(.*)",
        src,
        re.DOTALL,
    )
    assert method_match is not None, "recordReceivedEntry method not found"
    method_body = method_match.group(1)
    # Truncate at next top-level method (Future<...> at start of line after class indent)
    next_method = re.search(r"\n  Future<", method_body)
    if next_method:
        method_body = method_body[: next_method.start()]
    assert "getHostLastSeen" in method_body, (
        "getHostLastSeen must be called within recordReceivedEntry"
    )


# [pr_diff] fail_to_pass
def test_gap_detection_gated_by_online_status():
    """The gap detection condition must be gated so that offline hosts
    (getHostLastSeen returns null) do NOT trigger gap detection."""
    src = SERVICE_FILE.read_text()
    # There must be a boolean variable or condition that combines the
    # host-last-seen check with the gap detection logic
    # The original code has: if (lastSeen != null && counter > lastSeen + 1)
    # The fix must add an additional guard before or around this condition
    #
    # Check that there's a variable or inline condition that gates gap detection
    # based on whether the host has been seen online
    has_gate = (
        # Pattern 1: explicit boolean variable (shouldDetectGaps or similar)
        re.search(r"(shouldDetectGaps|detectGaps|isOnline|hostOnline)\b", src) is not None
        # Pattern 2: the gap detection if-condition includes a check related to hostLastSeen/hostLastOnline
        or re.search(
            r"if\s*\(.*(?:hostLastOnline|hostLastSeen|shouldDetect|isOnline).*&&.*counter\s*>",
            src,
        ) is not None
        # Pattern 3: separate if block that skips when host not online
        or re.search(
            r"if\s*\(\s*!.*(?:shouldDetectGaps|detectGaps|isOnline)", src
        ) is not None
    )
    assert has_gate, (
        "Gap detection must be gated by host online status — offline hosts "
        "should not trigger gap detection"
    )


# [pr_diff] fail_to_pass
def test_originator_always_considered_online():
    """The originating host must always be considered online for gap detection,
    even if not previously in the HostActivity table."""
    src = SERVICE_FILE.read_text()
    # The base code already has `hostId == originatingHostId` for recording entries.
    # The fix must add a SECOND usage in a boolean/conditional context for gap
    # detection gating (e.g., `|| hostId == originatingHostId` or similar).
    # Check that originatingHostId appears in a boolean OR expression (gap gate)
    has_originator_gate = (
        # Pattern: ... != null || hostId == originatingHostId (boolean OR)
        re.search(r"\|\|\s*hostId\s*==\s*originatingHostId", src) is not None
        # Pattern: hostId == originatingHostId || ... (boolean OR, other order)
        or re.search(r"hostId\s*==\s*originatingHostId\s*\|\|", src) is not None
        # Pattern: ternary or inline condition with originatingHostId in gap context
        or re.search(r"(shouldDetectGaps|detectGaps|isOnline).*originatingHostId", src) is not None
    )
    assert has_originator_gate, (
        "The originating host must be explicitly treated as online in the gap "
        "detection gate (e.g., via a boolean OR with the host-last-seen check)"
    )


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must mention the concept of online/offline host filtering for gap detection.
    # The base README already mentions "online" in a different context (HostActivity table),
    # so we check for phrases specific to the new guard behavior.
    has_online_guard = any(
        phrase in content_lower
        for phrase in [
            "false positive",
            "offline hosts",
            "hosts we've never communicated",
            "host guard",
            "gap detection is only performed",
        ]
    )
    assert has_online_guard, (
        "README must document the Online Host Guard — that gap detection is "
        "only performed for hosts that have been seen online, preventing false "
        "positives for never-communicated hosts"
    )

    # Must mention that the originating host is always considered online
    assert any(
        phrase in content_lower
        for phrase in [
            "originating host is always considered online",
            "originating host is always",
            "originator is always",
        ]
    ), (
        "README must document that the originating host is always considered online"
    )

    # Must mention that sequence entries are still recorded for offline hosts
    assert any(
        phrase in content_lower
        for phrase in [
            "still recorded",
            "still record",
            "sequence entries are still",
        ]
    ), (
        "README must document that sequence entries are still recorded for offline hosts"
    )


# [config_edit] fail_to_pass

    # The logging section should include the skipGapDetection log line
    assert "skipGapDetection" in content, (
        "README Logging section must document the 'skipGapDetection' log line"
    )
    # It should appear near other log line examples (gapDetected, handleBackfillRequest, etc.)
    assert "gapDetected" in content, "README should still document existing gapDetected log"


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass

    # If the code references getHostLastSeen, the README should mention the concept
    if "getHostLastSeen" in src:
        readme_lower = readme.lower()
        assert any(
            term in readme_lower
            for term in ["online", "host activity", "last seen", "hostactivity"]
        ), (
            "README must mention host online/activity concepts that are in the code"
        )
