"""
Task: react-client-json-parse-optimization
Repo: facebook/react @ 3a2bee26d23a21cfb04313372a0c0ca46101b785
PR:   #35776 — [Flight] Walk parsed JSON instead of using reviver for parsing RSC payload

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: ReactFlightClient.js uses Flow type syntax (not valid plain JS), so behavioral
tests use structural analysis (file content / regex) rather than node execution.
# AST-only because: Flow-typed JS cannot be parsed by Python ast or plain node --check
"""

import re
from pathlib import Path

REPO = "/workspace/react"
REACT_CLIENT = f"{REPO}/packages/react-client/src/ReactFlightClient.js"
NOOP_CLIENT = f"{REPO}/packages/react-noop-renderer/src/ReactNoopFlightClient.js"


def _read(path):
    return Path(path).read_text(encoding="utf-8")


def _extract_function_body(src, func_token):
    """Extract the full body (incl. braces) of the first function containing func_token."""
    start = src.find(func_token)
    if start == -1:
        return None
    brace_start = src.find("{", start)
    if brace_start == -1:
        return None
    depth = 0
    for i, ch in enumerate(src[brace_start:], brace_start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return src[brace_start : i + 1]
    return None


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral / structural tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_revive_model_function_defined():
    """reviveModel function is added to replace the JSON.parse reviver approach."""
    src = _read(REACT_CLIENT)
    assert "function reviveModel(" in src, "reviveModel function not found in ReactFlightClient.js"
    # Must accept response and value parameters
    m = re.search(r"function reviveModel\(([^)]+)\)", src)
    assert m is not None, "reviveModel signature not found"
    params = m.group(1)
    assert "response" in params, "reviveModel must accept 'response' param"
    assert "value" in params, "reviveModel must accept 'value' param"


# [pr_diff] fail_to_pass
def test_parse_model_two_step_parsing():
    """parseModel uses two-step parsing: JSON.parse then reviveModel, not a reviver callback."""
    src = _read(REACT_CLIENT)
    body = _extract_function_body(src, "function parseModel<T>")
    assert body is not None, "parseModel function not found"
    # Must call JSON.parse without a second argument (no reviver)
    assert "JSON.parse(json)" in body, "parseModel must call JSON.parse(json) without a reviver"
    # Must delegate to reviveModel
    assert "reviveModel(response," in body, "parseModel must delegate to reviveModel"
    # Must NOT use the old _fromJSON callback
    assert "response._fromJSON" not in body, "parseModel must not use response._fromJSON"


# [pr_diff] fail_to_pass
def test_from_json_field_removed():
    """_fromJSON callback field is removed from Response constructor and type definition."""
    src = _read(REACT_CLIENT)
    assert "this._fromJSON =" not in src, "ResponseInstance still assigns this._fromJSON"
    assert "_fromJSON:" not in src, "_fromJSON still appears as a field declaration in the type"


# [pr_diff] fail_to_pass
def test_no_op_setter_for_strict_mode():
    """No-op setters added to getter-only property descriptors to prevent strict-mode TypeErrors."""
    src = _read(REACT_CLIENT)
    # Both defineLazyGetter and the inline descriptor in parseModelString need no-op setters.
    matches = re.findall(r"set:\s*function\s*\(\s*\)\s*\{\s*\}", src)
    assert len(matches) >= 2, (
        f"Expected >=2 no-op setters for strict-mode compat, found {len(matches)}. "
        "Both defineLazyGetter and the parseModelString inline descriptor need set: function() {}."
    )


# [pr_diff] fail_to_pass
def test_create_from_json_callback_removed():
    """createFromJSONCallback is removed — reviveModel replaces it entirely."""
    src = _read(REACT_CLIENT)
    assert "function createFromJSONCallback" not in src, (
        "createFromJSONCallback still defined; it should be removed"
    )
    assert "createFromJSONCallback(" not in src, (
        "createFromJSONCallback is still being called somewhere"
    )


# [pr_diff] fail_to_pass
def test_revive_model_proto_safety():
    """reviveModel deletes __proto__ keys rather than returning undefined like the old reviver."""
    src = _read(REACT_CLIENT)
    body = _extract_function_body(src, "function reviveModel(")
    assert body is not None, "reviveModel function not found"
    # Proto pollution prevention: must delete the key, not just return undefined
    assert "__PROTO__" in body, "reviveModel must guard against __PROTO__ key"
    assert "delete " in body, "reviveModel must delete __PROTO__ keys"


# [pr_diff] fail_to_pass
def test_noop_renderer_cleaned_up():
    """ReactNoopFlightClient parseModel override using response._fromJSON is removed."""
    src = _read(NOOP_CLIENT)
    assert "_fromJSON" not in src, (
        "ReactNoopFlightClient still references _fromJSON; "
        "the parseModel override should have been removed"
    )


# [pr_diff] fail_to_pass
def test_revive_model_handles_all_value_types():
    """reviveModel has branches for strings ($ prefix), arrays (isArray), and plain objects."""
    src = _read(REACT_CLIENT)
    body = _extract_function_body(src, "function reviveModel(")
    assert body is not None, "reviveModel function not found"
    # String branch: check for $ prefix before calling parseModelString
    assert "value[0] === '$'" in body or "value[0] ===" in body, (
        "reviveModel must short-circuit strings starting with '$'"
    )
    # Array branch: must use isArray
    assert "isArray(" in body, "reviveModel must handle arrays with isArray()"
    # Object branch: must iterate keys
    assert "for " in body, "reviveModel must iterate object keys for the plain-object branch"


# ---------------------------------------------------------------------------
# Fail-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_revive_model_has_substantial_body():
    """reviveModel is not a stub — has multiple return paths, typeof checks, real walk logic."""
    src = _read(REACT_CLIENT)
    body = _extract_function_body(src, "function reviveModel(")
    assert body is not None, "reviveModel function not found"
    returns = re.findall(r"\breturn\b", body)
    assert len(returns) >= 3, (
        f"reviveModel has only {len(returns)} return statement(s); "
        "expected >=3 (early returns for string/non-object/array plus object return)"
    )
    assert "typeof value" in body, "reviveModel must branch on typeof value"
