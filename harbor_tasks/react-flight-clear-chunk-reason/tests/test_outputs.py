"""
Task: react-flight-clear-chunk-reason
Repo: facebook/react @ 1e3152365df2f7a23a5ad947e83f40914413be16

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Fix: After a chunk is successfully initialized, its `reason` property must be
cleared to null so the stream-close handler doesn't misinterpret a stale
reentrant error as a FlightStreamController.
"""

import re
from pathlib import Path

REPO = "/workspace/react"

CLIENT_FILE = Path(f"{REPO}/packages/react-client/src/ReactFlightClient.js")
SERVER_FILE = Path(f"{REPO}/packages/react-server/src/ReactFlightReplyServer.js")


def _extract_function(src: str, func_name: str) -> str:
    """Extract a top-level function body up to the next top-level function."""
    m = re.search(
        rf'(function {re.escape(func_name)}\b.*?)(?=\nfunction |\Z)',
        src,
        re.DOTALL,
    )
    assert m, f"Function {func_name!r} not found"
    return m.group(1)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# AST-only because: React source uses Flow types; files cannot be imported or
# executed directly in Python or plain Node without a transpiler step.
def test_model_chunk_clears_reason():
    """initializeModelChunk must set chunk.reason=null after successful init.

    Without the fix, a stale error left in `reason` by a reentrant readChunk
    call causes the stream-close handler to crash (TypeError: reason.error is
    not a function).
    """
    src = CLIENT_FILE.read_text()
    body = _extract_function(src, "initializeModelChunk")

    assert "initializedChunk.reason = null" in body, (
        "initializeModelChunk does not clear chunk.reason after successful initialization"
    )

    # Ordering: reason=null must follow the value assignment
    value_pos = body.find("initializedChunk.value = value")
    reason_pos = body.find("initializedChunk.reason = null")
    assert value_pos != -1, "initializedChunk.value assignment not found in initializeModelChunk"
    assert reason_pos > value_pos, (
        "initializedChunk.reason = null must come after initializedChunk.value = value"
    )


# [pr_diff] fail_to_pass
# AST-only because: same as above — Flow-typed JS, no transpiler available.
def test_module_chunk_clears_reason():
    """initializeModuleChunk must set chunk.reason=null after successful init.

    Mirrors the model chunk fix; both functions share the same reentrancy
    vulnerability and must clear reason on the success path.
    """
    src = CLIENT_FILE.read_text()
    body = _extract_function(src, "initializeModuleChunk")

    assert "initializedChunk.reason = null" in body, (
        "initializeModuleChunk does not clear chunk.reason after successful initialization"
    )

    value_pos = body.find("initializedChunk.value = value")
    reason_pos = body.find("initializedChunk.reason = null")
    assert value_pos != -1, "initializedChunk.value assignment not found in initializeModuleChunk"
    assert reason_pos > value_pos, (
        "initializedChunk.reason = null must come after initializedChunk.value = value"
    )


# [pr_diff] fail_to_pass
# AST-only because: Flow-typed JS in react-server package, same constraint.
def test_reply_server_clears_reason():
    """loadServerReference must set promise.reason=null after successful init.

    ReactFlightReplyServer.js has the same pattern: after resolving a bound
    reference, the initializedPromise.reason must be cleared.
    """
    src = SERVER_FILE.read_text()
    body = _extract_function(src, "loadServerReference")

    assert "initializedPromise.reason = null" in body, (
        "loadServerReference does not clear promise.reason after successful initialization"
    )

    value_pos = body.find("initializedPromise.value = resolvedValue")
    reason_pos = body.find("initializedPromise.reason = null")
    assert value_pos != -1, "initializedPromise.value assignment not found in loadServerReference"
    assert reason_pos > value_pos, (
        "initializedPromise.reason = null must come after initializedPromise.value = resolvedValue"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub / regression guard
# ---------------------------------------------------------------------------

# [static] pass_to_pass
# AST-only because: Flow-typed JS cannot be imported; text presence check is
# the lightest guard that all three functions were not accidentally removed.
def test_functions_not_removed():
    """All three modified functions must still exist after the fix."""
    client_src = CLIENT_FILE.read_text()
    server_src = SERVER_FILE.read_text()

    assert "function initializeModelChunk" in client_src, (
        "initializeModelChunk was removed from ReactFlightClient.js"
    )
    assert "function initializeModuleChunk" in client_src, (
        "initializeModuleChunk was removed from ReactFlightClient.js"
    )
    assert "function loadServerReference" in server_src, (
        "loadServerReference was removed from ReactFlightReplyServer.js"
    )
