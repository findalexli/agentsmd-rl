"""
Task: react-flight-encodeReply-jsx-root
Repo: facebook/react @ 2dd9b7cf76c31df5d7e26e5199e3c362c3e94f95
PR:   35730

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

AST-only because: ReactFlightReplyClient.js and ReactFlightClient.js use
Flow type annotations that node cannot execute directly without stripping.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
REPLY_CLIENT = REPO + "/packages/react-client/src/ReactFlightReplyClient.js"
FLIGHT_CLIENT = REPO + "/packages/react-client/src/ReactFlightClient.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file existence and syntax
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_files_exist():
    """Both modified files must exist at expected paths."""
    assert Path(REPLY_CLIENT).exists(), f"Missing: {REPLY_CLIENT}"
    assert Path(FLIGHT_CLIENT).exists(), f"Missing: {FLIGHT_CLIENT}"


# [static] pass_to_pass
def test_js_syntax_reply_client():
    """ReactFlightReplyClient.js must be readable and non-empty."""
    src = Path(REPLY_CLIENT).read_text()
    # File must have substantial content (not stubbed out)
    assert len(src.splitlines()) > 100, "ReactFlightReplyClient.js is too short — likely stubbed"
    # Key structural elements must remain
    for marker in ("processReply", "REACT_ELEMENT_TYPE", "temporaryReferences", "serializeTemporaryReferenceMarker"):
        assert marker in src, f"ReactFlightReplyClient.js missing expected symbol: {marker}"


# [static] pass_to_pass
def test_js_syntax_flight_client():
    """ReactFlightClient.js must be readable and non-empty."""
    src = Path(FLIGHT_CLIENT).read_text()
    assert len(src.splitlines()) > 100, "ReactFlightClient.js is too short — likely stubbed"
    for marker in ("moveDebugInfoFromChunkToInnerValue", "addAsyncInfo", "_debugInfo", "Object.defineProperty"):
        assert marker in src, f"ReactFlightClient.js missing expected symbol: {marker}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_modelroot_jsx_root_check():
    """encodeReply must detect JSX as root model and emit a temporary reference marker.

    The fix adds: if (temporaryReferences !== undefined && modelRoot === value)
    inside the REACT_ELEMENT_TYPE handler so JSX passed directly to encodeReply
    is serialized as a temporary reference instead of throwing.
    """
    src = Path(REPLY_CLIENT).read_text()
    # Core check: modelRoot === value must be present
    assert "modelRoot === value" in src, (
        "modelRoot === value check not found in ReactFlightReplyClient.js — "
        "JSX root will throw instead of being serialized as a temporary reference"
    )
    # Must be guarded by temporaryReferences check (prevents false positive for missing ref case)
    lines = src.splitlines()
    modelroot_check_line = next(
        (i for i, l in enumerate(lines) if "modelRoot === value" in l), None
    )
    assert modelroot_check_line is not None
    context = "\n".join(lines[max(0, modelroot_check_line - 2):modelroot_check_line + 8])
    assert "temporaryReferences" in context, (
        "modelRoot === value check is not guarded by temporaryReferences !== undefined"
    )
    # Must return serializeTemporaryReferenceMarker() in same block
    assert "serializeTemporaryReferenceMarker" in context, (
        "modelRoot === value block does not return serializeTemporaryReferenceMarker()"
    )


# [pr_diff] fail_to_pass
def test_modelroot_nulled_after_emit():
    """modelRoot must be set to null after emitting the temporary reference marker.

    Without this, a nested visit to the same root value could re-emit the marker,
    causing double-processing of the JSX root.
    """
    src = Path(REPLY_CLIENT).read_text()
    lines = src.splitlines()
    modelroot_check_line = next(
        (i for i, l in enumerate(lines) if "modelRoot === value" in l), None
    )
    assert modelroot_check_line is not None, "modelRoot === value check not found"
    # modelRoot = null must appear within 5 lines after the check
    window = "\n".join(lines[modelroot_check_line:modelroot_check_line + 6])
    assert "modelRoot = null" in window, (
        "modelRoot is not set to null after emitting the marker — "
        f"context around check:\n{window}"
    )


# [pr_diff] fail_to_pass
def test_frozen_guard_in_move_debug_info():
    """moveDebugInfoFromChunkToInnerValue must guard Object.defineProperty with Object.isFrozen.

    Without this, attaching _debugInfo to a frozen React element (e.g. a client
    reference exported as JSX) throws: TypeError: Cannot define property _debugInfo,
    object is not extensible.
    """
    src = Path(FLIGHT_CLIENT).read_text()
    assert "Object.isFrozen" in src, (
        "Object.isFrozen not found in ReactFlightClient.js"
    )
    lines = src.splitlines()
    # Find the moveDebugInfoFromChunkToInnerValue function region
    fn_start = next(
        (i for i, l in enumerate(lines) if "moveDebugInfoFromChunkToInnerValue" in l and "function" in l),
        None,
    )
    assert fn_start is not None, "moveDebugInfoFromChunkToInnerValue function not found"
    # Look for Object.isFrozen in the vicinity of the function (within 60 lines)
    region = "\n".join(lines[fn_start: fn_start + 60])
    assert "Object.isFrozen" in region, (
        "Object.isFrozen guard not found in moveDebugInfoFromChunkToInnerValue — "
        "frozen elements will crash when receiving debug info"
    )
    # The guard must wrap an else branch that contains Object.defineProperty
    assert "Object.defineProperty" in region, (
        "Object.defineProperty not found in moveDebugInfoFromChunkToInnerValue — "
        "unexpected structural change"
    )


# [pr_diff] fail_to_pass
def test_frozen_guard_in_add_async_info():
    """addAsyncInfo must guard Object.defineProperty with Object.isFrozen.

    Same frozen-element crash occurs in addAsyncInfo when a chunk resolves to a
    frozen React element and debug info needs to be attached.
    """
    src = Path(FLIGHT_CLIENT).read_text()
    lines = src.splitlines()
    fn_start = next(
        (i for i, l in enumerate(lines) if "function addAsyncInfo" in l),
        None,
    )
    assert fn_start is not None, "addAsyncInfo function not found"
    region = "\n".join(lines[fn_start: fn_start + 40])
    assert "Object.isFrozen" in region, (
        "Object.isFrozen guard not found in addAsyncInfo — "
        "frozen elements will crash when receiving async debug info"
    )
    assert "Object.defineProperty" in region, (
        "Object.defineProperty not found in addAsyncInfo — unexpected structural change"
    )


# [pr_diff] fail_to_pass
def test_isFrozen_count():
    """ReactFlightClient.js must have at least 2 Object.isFrozen guards (one per def site)."""
    src = Path(FLIGHT_CLIENT).read_text()
    import re
    occurrences = re.findall(r"Object\.isFrozen", src)
    assert len(occurrences) >= 2, (
        f"Expected >=2 Object.isFrozen guards, found {len(occurrences)} — "
        "one guard in moveDebugInfoFromChunkToInnerValue, one in addAsyncInfo"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_error_preserved_for_non_temp_ref_jsx():
    """The original throw for JSX without a TemporaryReferenceSet must be preserved.

    The fix only handles the case where temporaryReferences is provided AND the
    value is the model root. JSX without temp refs should still throw.
    """
    src = Path(REPLY_CLIENT).read_text()
    assert "React Element cannot be passed to Server Functions" in src, (
        "Original error message for non-temp-ref JSX was removed — "
        "invalid JSX would silently misbehave instead of throwing"
    )
    assert "temporary reference set" in src, (
        "Error message mentioning 'temporary reference set' not found"
    )


# [static] pass_to_pass
def test_not_stub():
    """Neither modified file has been replaced with a stub."""
    for path, min_lines, key_fn in [
        (REPLY_CLIENT, 200, "processReply"),
        (FLIGHT_CLIENT, 500, "moveDebugInfoFromChunkToInnerValue"),
    ]:
        src = Path(path).read_text()
        lines = src.splitlines()
        assert len(lines) >= min_lines, (
            f"{path}: only {len(lines)} lines — expected >= {min_lines}"
        )
        assert key_fn in src, f"{path}: key function '{key_fn}' missing"
