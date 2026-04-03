"""
Task: react-client-json-parse-optimization
Repo: facebook/react @ 3a2bee26d23a21cfb04313372a0c0ca46101b785
PR:   #35776 — [Flight] Walk parsed JSON instead of using reviver for parsing RSC payload

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: ReactFlightClient.js uses Flow type syntax and cannot be executed directly
by node or Python. Structural analysis is used for source-level checks.
# AST-only because: Flow-typed JS with custom module resolution cannot be executed standalone
"""

import re
import subprocess
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
# Pass-to-pass (repo_tests) — upstream test suite
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_flight_client_tests_pass():
    """React Flight client upstream tests still pass after the change."""
    r = subprocess.run(
        ["yarn", "test", "--silent", "--no-watchman", "ReactFlight-test"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    stderr = r.stderr.decode(errors="replace")
    stdout = r.stdout.decode(errors="replace")
    assert r.returncode == 0, (
        f"ReactFlight-test failed (exit {r.returncode}):\n{stdout[-2000:]}\n{stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core structural tests
# AST-only because: Flow-typed JS cannot be parsed by Python ast or plain node
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_parse_model_no_reviver():
    """parseModel must call JSON.parse without a reviver callback (two-step parsing)."""
    src = _read(REACT_CLIENT)
    body = _extract_function_body(src, "function parseModel")
    assert body is not None, "parseModel function not found"
    # Must call JSON.parse without a reviver (second arg)
    assert re.search(r"JSON\.parse\(\s*json\s*\)", body), (
        "parseModel must call JSON.parse(json) without a reviver argument"
    )
    # Must NOT reference the old _fromJSON callback
    assert "_fromJSON" not in body, "parseModel must not use _fromJSON"


# [pr_diff] fail_to_pass
def test_revive_model_exists_with_walk_logic():
    """A manual walk function (reviveModel or equivalent) replaces the reviver callback."""
    src = _read(REACT_CLIENT)
    # The fix introduces a walk function that handles strings, arrays, objects
    # It must exist as a named function (not inline in parseModel)
    body = _extract_function_body(src, "function parseModel")
    assert body is not None, "parseModel function not found"

    # parseModel must delegate to a separate walk/revive function
    # Find what function parseModel calls after JSON.parse
    call_match = re.search(r"JSON\.parse\(\s*json\s*\).*?(\w+)\(", body, re.DOTALL)
    assert call_match is not None, (
        "parseModel must call a walk/revive function after JSON.parse"
    )
    walk_fn_name = call_match.group(1)

    # That function must be defined in the file
    walk_body = _extract_function_body(src, f"function {walk_fn_name}(")
    if walk_body is None:
        walk_body = _extract_function_body(src, f"function {walk_fn_name}<")
    assert walk_body is not None, (
        f"Walk function '{walk_fn_name}' called by parseModel is not defined"
    )

    # Walk function must handle different value types
    assert "typeof" in walk_body, "Walk function must branch on typeof value"
    assert "isArray(" in walk_body or "Array.isArray(" in walk_body, (
        "Walk function must handle arrays"
    )
    assert re.search(r"\bfor\b", walk_body), (
        "Walk function must iterate (for loop) over object keys or array elements"
    )

    # Walk function must have multiple return paths (not a stub)
    returns = re.findall(r"\breturn\b", walk_body)
    assert len(returns) >= 3, (
        f"Walk function has {len(returns)} return(s); expected >=3 "
        "(string, non-object, array, object paths)"
    )


# [pr_diff] fail_to_pass
def test_from_json_field_removed():
    """_fromJSON callback field is removed from Response type and constructor."""
    src = _read(REACT_CLIENT)
    # Should not assign _fromJSON in the constructor
    assert "this._fromJSON" not in src, (
        "ResponseInstance still assigns this._fromJSON"
    )
    # Should not declare _fromJSON in the type
    lines_with_fromjson = [
        l for l in src.splitlines()
        if "_fromJSON" in l and not l.strip().startswith("//")
    ]
    assert len(lines_with_fromjson) == 0, (
        f"_fromJSON still referenced in {len(lines_with_fromjson)} non-comment line(s)"
    )


# [pr_diff] fail_to_pass
def test_no_op_setter_for_strict_mode():
    """No-op setters added to getter-only property descriptors for strict-mode compat."""
    src = _read(REACT_CLIENT)
    # Both defineLazyGetter and the inline descriptor in parseModelString need setters
    # Match various formatting: set: function() {}, set() {}, set: () => {}
    setter_pattern = r"set\s*[:(]\s*(?:function\s*)?\(\s*\)\s*(?:=>)?\s*\{?\s*\}?"
    matches = re.findall(setter_pattern, src)
    assert len(matches) >= 2, (
        f"Expected >=2 no-op setters for strict-mode compat, found {len(matches)}. "
        "Both defineLazyGetter and parseModelString descriptors need set: function() {}."
    )


# [pr_diff] fail_to_pass
def test_create_from_json_callback_removed():
    """createFromJSONCallback is removed — the walk function replaces it."""
    src = _read(REACT_CLIENT)
    assert "function createFromJSONCallback" not in src, (
        "createFromJSONCallback still defined"
    )
    assert "createFromJSONCallback(" not in src, (
        "createFromJSONCallback is still being called"
    )


# [pr_diff] fail_to_pass
def test_walk_function_proto_safety():
    """The walk function deletes __proto__ keys to prevent prototype pollution."""
    src = _read(REACT_CLIENT)

    # Find the walk function (same approach as test_revive_model_exists)
    body = _extract_function_body(src, "function parseModel")
    assert body is not None
    call_match = re.search(r"JSON\.parse\(\s*json\s*\).*?(\w+)\(", body, re.DOTALL)
    assert call_match is not None
    walk_fn_name = call_match.group(1)

    walk_body = _extract_function_body(src, f"function {walk_fn_name}(")
    if walk_body is None:
        walk_body = _extract_function_body(src, f"function {walk_fn_name}<")
    assert walk_body is not None

    # Must handle __proto__ / __PROTO__
    assert "__PROTO__" in walk_body or "__proto__" in walk_body, (
        "Walk function must guard against __proto__ keys"
    )
    assert "delete" in walk_body, "Walk function must delete __proto__ keys"


# [pr_diff] fail_to_pass
def test_noop_renderer_cleaned_up():
    """ReactNoopFlightClient parseModel override using _fromJSON is removed."""
    src = _read(NOOP_CLIENT)
    assert "_fromJSON" not in src, (
        "ReactNoopFlightClient still references _fromJSON"
    )


# [pr_diff] fail_to_pass
def test_walk_handles_dollar_prefix_strings():
    """Walk function routes strings starting with '$' to parseModelString."""
    src = _read(REACT_CLIENT)

    body = _extract_function_body(src, "function parseModel")
    assert body is not None
    call_match = re.search(r"JSON\.parse\(\s*json\s*\).*?(\w+)\(", body, re.DOTALL)
    assert call_match is not None
    walk_fn_name = call_match.group(1)

    walk_body = _extract_function_body(src, f"function {walk_fn_name}(")
    if walk_body is None:
        walk_body = _extract_function_body(src, f"function {walk_fn_name}<")
    assert walk_body is not None

    # Must check for '$' prefix on string values
    assert "'$'" in walk_body or '"$"' in walk_body, (
        "Walk function must check for '$' prefix to route to parseModelString"
    )
    assert "parseModelString" in walk_body, (
        "Walk function must call parseModelString for special string values"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — formatting per .claude/skills/verify/SKILL.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .claude/skills/fix/SKILL.md:1-10 @ 3a2bee26
def test_prettier_formatting():
    """Modified files must pass prettier formatting (per React's verify workflow)."""
    r = subprocess.run(
        ["yarn", "prettier", "--check",
         "packages/react-client/src/ReactFlightClient.js",
         "packages/react-noop-renderer/src/ReactNoopFlightClient.js"],
        cwd=REPO,
        capture_output=True,
        timeout=60,
    )
    stdout = r.stdout.decode(errors="replace")
    stderr = r.stderr.decode(errors="replace")
    # prettier --check exits 0 if files are formatted, 1 if not
    assert r.returncode == 0, (
        f"Prettier check failed — files not formatted:\n{stdout[-1000:]}\n{stderr[-1000:]}"
    )
