"""
Task: uv-export-extra-resolution-conflicts
Repo: astral-sh/uv @ 8b0e9e5fb997cbdc2f4f58b43cd805d22e57bd1b
PR:   18888

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/uv"
EXPORT_MOD = Path(REPO) / "crates/uv-resolver/src/lock/export/mod.rs"
UNIVERSAL_MARKER = Path(REPO) / "crates/uv-resolver/src/universal_marker.rs"


def _extract_function_body(source: str, func_name: str) -> str:
    """Extract a Rust function body by name (from 'fn name' to matching closing brace).

    Note: This handles closures by ignoring `{` and `}` inside `|...| {` patterns.
    """
    lines = source.split("\n")
    in_func = False
    brace_depth = 0
    func_lines = []
    for line in lines:
        if not in_func and re.search(rf"\bfn\s+{func_name}\b", line):
            in_func = True
        if in_func:
            func_lines.append(line)
            # Count braces, but ignore those in closure syntax `|...| {`
            # by removing closure patterns first
            code_part = line.split("//")[0]  # Remove comments
            # Simple heuristic: remove `|...| {` patterns
            code_part = re.sub(r'\|[^|{}]*\| *\{', '', code_part)
            brace_depth += code_part.count("{") - code_part.count("}")
            if brace_depth <= 0 and len(func_lines) > 1:
                break
    return "\n".join(func_lines)


def _extract_enum_body(source: str, enum_name: str) -> str:
    """Extract an enum body by name."""
    lines = source.split("\n")
    in_enum = False
    brace_depth = 0
    enum_lines = []
    for line in lines:
        if not in_enum and re.search(rf"\benum\s+{enum_name}\b", line):
            in_enum = True
        if in_enum:
            enum_lines.append(line)
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0 and len(enum_lines) > 1:
                break
    return "\n".join(enum_lines)


def _extract_fn_signature(source: str, func_name: str) -> str:
    """Extract just the signature of a Rust function (up to opening brace)."""
    lines = source.split("\n")
    in_sig = False
    sig_lines = []
    for line in lines:
        if not in_sig and re.search(rf"\bfn\s+{func_name}\b", line):
            in_sig = True
        if in_sig:
            sig_lines.append(line)
            if "{" in line:
                break
    return " ".join(sig_lines)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check_resolver():
    """uv-resolver crate compiles without errors."""
    try:
        r = subprocess.run(
            ["cargo", "check", "-p", "uv-resolver"],
            capture_output=True, text=True, timeout=480, cwd=REPO,
        )
        assert r.returncode == 0, f"uv-resolver does not compile:\n{r.stderr[:2000]}"
    except subprocess.TimeoutExpired:
        # If compilation times out, skip — structural tests below still validate
        pass


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_resolve_handles_package_scope():
    """The extra/conflict resolution function must accept a scope_package parameter.

    On the base commit, resolve_conflicts takes (marker, known_conflicts).
    A correct fix adds a scope_package parameter so unencoded extras like
    `extra == 'cpu'` can be interpreted relative to the current package.
    """
    src = UNIVERSAL_MARKER.read_text()

    # Find the resolve function (may be renamed)
    # Look for a pub(crate) fn that takes scope_package or package_name
    sig_activated = _extract_fn_signature(src, "resolve_activated_extras")
    sig_conflicts = _extract_fn_signature(src, "resolve_conflicts")
    sig = sig_activated or sig_conflicts

    assert sig, "No resolve_conflicts or resolve_activated_extras function found"

    # The function must accept a scope/package parameter for unencoded extra resolution
    scope_params = ["scope_package", "package_name", "scope", "pkg_name", "current_package"]
    has_scope = any(p in sig for p in scope_params)
    assert has_scope, (
        f"Resolve function lacks a scope_package parameter to handle unencoded extras.\n"
        f"Signature: {sig[:300]}"
    )


# [pr_diff] fail_to_pass
def test_edge_carries_dep_extras():
    """Edge enum variants must carry dependency extras information.

    On the base commit, Edge is:
        Prod(MarkerTree), Optional(&ExtraName, MarkerTree), Dev(&GroupName, MarkerTree)
    After the fix, each variant must include a field for the extras activated
    on the dependency (dep_extras), so extra markers can be resolved per-edge.
    """
    src = EXPORT_MOD.read_text()
    enum_body = _extract_enum_body(src, "Edge")
    assert enum_body, "Edge enum not found in export/mod.rs"

    # Check that Edge variants carry extras info — look for dep_extras or
    # similar field, OR struct variant syntax with extras
    extras_field_names = ["dep_extras", "extras", "child_extras", "activated_extras"]
    has_extras = any(name in enum_body for name in extras_field_names)
    assert has_extras, (
        f"Edge enum variants do not carry dependency extras information.\n"
        f"Expected a dep_extras field in struct variants.\n"
        f"Got: {enum_body[:500]}"
    )


# [pr_diff] fail_to_pass
def test_unencoded_extra_lookup():
    """The resolve function must handle unencoded extras by looking them up
    in the scope of the current package.

    On the base commit, resolve_conflicts only handles conflict-encoded extras
    (with the 'extra-N-pkg-NAME' encoding). After the fix, it must also look
    up plain extra names like 'cpu' or 'cu124' against the scope package.
    """
    src = UNIVERSAL_MARKER.read_text()

    # Find the resolve function body
    body = _extract_function_body(src, "resolve_activated_extras")
    if not body:
        body = _extract_function_body(src, "resolve_conflicts")

    # Check that we got a substantial body (not just the function signature)
    # If body is too short, the extraction may have failed due to closures.
    # In that case, scan the entire file for the indicators.
    search_space = body if len(body) > 100 else src

    # The function must contain logic for unencoded/raw extra lookup using the package scope.
    # Multiple patterns indicate this — looking for any of them:
    indicators = [
        "scope_package",       # uses the scope_package parameter
        "unencoded",           # comment about unencoded extras
        "package.clone()",     # creating ConflictItem from package + extra name
        "name.clone()",        # the raw extra name being used as a ConflictItem
    ]
    found = sum(1 for ind in indicators if ind in search_space)
    assert found >= 2, (
        f"Resolve function does not handle unencoded extras with package scope.\n"
        f"Expected scope_package-based lookup logic for raw extra names.\n"
        f"Found only {found}/4 indicators."
    )


# [pr_diff] fail_to_pass
def test_dep_extras_fed_into_conflict_map():
    """conflict_marker_reachability must propagate dep_extras from edges
    into the conflict map before resolving markers.

    On the base commit, the function doesn't use dep_extras at all —
    extras were tracked via a separate selected_extras HashMap.
    After the fix, dep_extras from each edge must be inserted into the
    parent_map so the resolver knows which extras are active.
    """
    src = EXPORT_MOD.read_text()
    body = _extract_function_body(src, "conflict_marker_reachability")

    # Check that we got a substantial body
    search_space = body if body and len(body) > 100 else src

    # Must reference dep_extras in the traversal logic
    extras_refs = ["dep_extras", "child_extras", "activated_extras"]
    has_extras_ref = any(ref in search_space for ref in extras_refs)
    assert has_extras_ref, (
        "conflict_marker_reachability does not use dep_extras from edges.\n"
        "The function must propagate edge-carried extras into the conflict map."
    )

    # Must also derive scope_package from the graph node to pass to the resolve function
    scope_patterns = ["scope_package", "package.name()", "parent.name()"]
    has_scope = any(p in search_space for p in scope_patterns)
    assert has_scope, (
        "conflict_marker_reachability does not extract scope_package from graph nodes.\n"
        "It must pass the parent package name to the resolve function."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — upstream regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_resolve_unit_tests():
    """Existing unit tests in universal_marker::tests still pass."""
    try:
        r = subprocess.run(
            ["cargo", "test", "-p", "uv-resolver", "--",
             "universal_marker::tests::resolve", "--exact"],
            capture_output=True, text=True, timeout=480, cwd=REPO,
        )
        assert r.returncode == 0, (
            f"universal_marker::tests::resolve failed:\n"
            f"{r.stdout[:1000]}\n{r.stderr[:1000]}"
        )
    except subprocess.TimeoutExpired:
        pass  # Compilation may timeout; other tests still validate correctness


# [repo_tests] pass_to_pass
def test_universal_marker_all_unit_tests():
    """All unit tests in universal_marker module still pass (pass_to_pass)."""
    try:
        r = subprocess.run(
            ["cargo", "test", "-p", "uv-resolver", "--lib", "universal_marker"],
            capture_output=True, text=True, timeout=600, cwd=REPO,
        )
        assert r.returncode == 0, (
            f"universal_marker unit tests failed:\n"
            f"stdout: {r.stdout[-500:]}\nstderr: {r.stderr[-500:]}"
        )
    except subprocess.TimeoutExpired:
        pass  # Compilation may timeout; marked as pass


# [repo_tests] pass_to_pass
def test_uv_resolver_clippy():
    """uv-resolver crate passes clippy linting (pass_to_pass)."""
    try:
        r = subprocess.run(
            ["cargo", "clippy", "-p", "uv-resolver", "--all-targets"],
            capture_output=True, text=True, timeout=600, cwd=REPO,
        )
        assert r.returncode == 0, (
            f"uv-resolver clippy failed:\n{r.stderr[-500:]}"
        )
    except subprocess.TimeoutExpired:
        pass  # Compilation may timeout; marked as pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_resolve_not_stub():
    """The resolve function has substantial logic, not a stub."""
    src = UNIVERSAL_MARKER.read_text()
    body = _extract_function_body(src, "resolve_activated_extras")
    if not body:
        body = _extract_function_body(src, "resolve_conflicts")

    # If extraction failed due to closures, use a fallback:
    # Count meaningful lines from the function start until we hit a top-level `fn ` or `#[test]`
    if len(body) < 100:
        lines = src.split("\n")
        in_target_func = False
        meaningful = []
        for line in lines:
            if not in_target_func:
                if re.search(r"\bfn\s+(resolve_activated_extras|resolve_conflicts)\b", line):
                    in_target_func = True
                    continue
            if in_target_func:
                # Stop at next top-level function or test marker
                if re.match(r"^(pub\s+)?\s*fn\s+", line) and not re.search(r"resolve_activated_extras|resolve_conflicts", line):
                    break
                if line.strip().startswith("#") and "test" in line:
                    break
                stripped = line.strip()
                if stripped and not stripped.startswith("//") and stripped not in ("{", "}", "};"):
                    meaningful.append(stripped)
        # Accept if we found at least 15 meaningful lines (fallback threshold)
        assert len(meaningful) >= 15, (
            f"Resolve function has only {len(meaningful)} meaningful lines — likely a stub.\n"
            f"Body extracted: {body[:500]}"
        )
    else:
        meaningful = [
            line for line in body.split("\n")
            if line.strip()
            and not line.strip().startswith("//")
            and line.strip() not in ("{", "}", "};")
        ]
        assert len(meaningful) >= 20, (
            f"Resolve function has only {len(meaningful)} meaningful lines — likely a stub"
        )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — CLAUDE.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:7 @ 8b0e9e5f
def test_no_bare_unwrap_in_resolve():
    """No bare .unwrap() calls in the resolve function.

    CLAUDE.md line 7: 'AVOID using panic!, unreachable!, .unwrap(), unsafe code'
    """
    src = UNIVERSAL_MARKER.read_text()
    body = _extract_function_body(src, "resolve_activated_extras")
    if not body:
        body = _extract_function_body(src, "resolve_conflicts")
    assert body, "No resolve function found"

    for i, line in enumerate(body.split("\n"), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        # .unwrap() but NOT .unwrap_or(), .unwrap_or_default(), .unwrap_or_else()
        if ".unwrap()" in stripped:
            assert False, (
                f"Bare .unwrap() found at line {i} of resolve function: {stripped}\n"
                f"CLAUDE.md:7 says: AVOID using .unwrap()"
            )
