"""
Task: uv-self-update-quiet-stderr-important
Repo: astral-sh/uv @ 262a50bb4c952cf2461d4073ae21081ed516f21c
PR:   astral-sh/uv#18645

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/repo"
PRINTER = f"{REPO}/crates/uv/src/printer.rs"
SELF_UPDATE = f"{REPO}/crates/uv/src/commands/self_update.rs"


# ---------------------------------------------------------------------------
# Helpers — parse Rust match arms
# ---------------------------------------------------------------------------

def _extract_method_body(src: str, method_name: str, return_type: str) -> str | None:
    """Extract the body of a method `fn <name>(self) -> <return_type> { ... }`."""
    # Match method signature and opening brace
    pattern = rf"fn\s+{re.escape(method_name)}\s*\(\s*self\s*\)\s*->\s*{re.escape(return_type)}\s*\{{"
    m = re.search(pattern, src)
    if not m:
        return None
    # Balance braces to find end
    start = m.end() - 1
    depth = 0
    for i in range(start, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[start + 1 : i]
    return None


def _parse_match_arms(body: str) -> dict[str, str]:
    """Parse match arms in a Rust method body, returning {variant: return_value}.

    Handles patterns like:
        Self::Quiet => Stderr::Enabled,
        Printer::Quiet => Stderr::Enabled,
        Self::Silent | Self::Quiet => Stderr::Disabled,
        _ => Stderr::Enabled,
    """
    ALL_VARIANTS = ("Silent", "Quiet", "Default", "Verbose", "NoProgress")
    arms: dict[str, str] = {}
    wildcard_value: str | None = None

    # Find match arms: variant(s) => value
    for m in re.finditer(
        r"((?:(?:Self|Printer)\s*::\s*\w+\s*\|?\s*)+|_)\s*=>\s*([\w:]+)",
        body,
    ):
        lhs = m.group(1).strip()
        value = m.group(2).strip().split("::")[-1]  # e.g., "Enabled" from "Stderr::Enabled"
        if lhs == "_":
            wildcard_value = value
        else:
            for v in re.findall(r"(?:Self|Printer)\s*::\s*(\w+)", lhs):
                arms[v] = value

    # Apply wildcard to any unmatched known variants
    if wildcard_value is not None:
        for v in ALL_VARIANTS:
            if v not in arms:
                arms[v] = wildcard_value

    return arms


def _find_new_stderr_method(src: str) -> tuple[str, str] | None:
    """Find a method on Printer returning Stderr that is NOT named 'stderr'.

    Returns (method_name, body) or None.
    """
    for m in re.finditer(
        r"fn\s+(\w+)\s*\(\s*self\s*\)\s*->\s*Stderr\s*\{",
        src,
    ):
        name = m.group(1)
        if name == "stderr":
            continue
        body = _extract_method_body(src, name, "Stderr")
        if body is not None:
            return name, body
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_rust_syntax():
    """Modified Rust files must exist and contain expected structures."""
    for path in [PRINTER, SELF_UPDATE]:
        assert Path(path).exists(), f"{path} not found"
        content = Path(path).read_text()
        assert len(content) > 100, f"{path} is suspiciously small"

    printer_src = Path(PRINTER).read_text()
    assert "enum Printer" in printer_src, "Printer enum not found in printer.rs"
    assert "fn stderr" in printer_src, "stderr method not found in printer.rs"

    su_src = Path(SELF_UPDATE).read_text()
    assert "fn self_update" in su_src, "self_update function not found"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_new_method_quiet_enabled():
    """New Printer method returns Stderr::Enabled for Quiet (the core fix)."""
    src = Path(PRINTER).read_text()
    result = _find_new_stderr_method(src)
    assert result is not None, "No new method found on Printer returning Stderr (besides stderr())"
    name, body = result
    arms = _parse_match_arms(body)
    assert "Quiet" in arms, f"Method {name} has no match arm for Quiet"
    assert arms["Quiet"] == "Enabled", (
        f"Method {name} returns {arms['Quiet']} for Quiet, expected Enabled"
    )


# [pr_diff] fail_to_pass
def test_new_method_silent_disabled():
    """New method returns Stderr::Disabled for Silent (double-quiet suppresses all)."""
    src = Path(PRINTER).read_text()
    result = _find_new_stderr_method(src)
    assert result is not None, "No new method found on Printer returning Stderr"
    name, body = result
    arms = _parse_match_arms(body)
    assert "Silent" in arms, f"Method {name} has no match arm for Silent"
    assert arms["Silent"] == "Disabled", (
        f"Method {name} returns {arms['Silent']} for Silent, expected Disabled"
    )


# [pr_diff] fail_to_pass
def test_new_method_all_non_silent_enabled():
    """New method returns Enabled for Default, Verbose, and NoProgress too."""
    src = Path(PRINTER).read_text()
    result = _find_new_stderr_method(src)
    assert result is not None, "No new method found on Printer returning Stderr"
    name, body = result
    arms = _parse_match_arms(body)
    for variant in ("Default", "Verbose", "NoProgress"):
        assert variant in arms, f"Method {name} has no match arm for {variant}"
        assert arms[variant] == "Enabled", (
            f"Method {name} returns {arms[variant]} for {variant}, expected Enabled"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_stderr_quiet_still_disabled():
    """Original stderr() must still return Disabled for Quiet (no regression)."""
    src = Path(PRINTER).read_text()
    body = _extract_method_body(src, "stderr", "Stderr")
    assert body is not None, "stderr() method not found on Printer"
    arms = _parse_match_arms(body)
    assert arms.get("Quiet") == "Disabled", (
        f"stderr() returns {arms.get('Quiet')} for Quiet, expected Disabled (regression!)"
    )
    assert arms.get("Silent") == "Disabled", (
        f"stderr() returns {arms.get('Silent')} for Silent, expected Disabled (regression!)"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — wiring
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_self_update_wiring():
    """self_update.rs uses the new method for important messages (>=3 call sites)."""
    su_src = Path(SELF_UPDATE).read_text()
    printer_src = Path(PRINTER).read_text()
    result = _find_new_stderr_method(printer_src)
    assert result is not None, "No new method found on Printer returning Stderr"
    method_name = result[0]

    # Strip comments and string literals to avoid false matches
    cleaned = re.sub(r"//[^\n]*", "", su_src)
    cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'"(?:[^"\\]|\\.)*"', '""', cleaned)

    calls = re.findall(rf"\.{re.escape(method_name)}\(\)", cleaned)
    assert len(calls) >= 3, (
        f"self_update.rs uses .{method_name}() only {len(calls)} times, expected >= 3"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_new_method_not_stub():
    """New method has real branching logic, not a trivial stub."""
    src = Path(PRINTER).read_text()
    result = _find_new_stderr_method(src)
    assert result is not None, "No new method found"
    name, body = result
    has_branching = bool(re.search(r"\b(match|if)\b", body))
    has_both = "Enabled" in body and "Disabled" in body
    lines = [l.strip() for l in body.strip().splitlines() if l.strip()]
    assert has_branching, f"Method {name} has no branching logic (match/if)"
    assert has_both, f"Method {name} doesn't have both Enabled and Disabled variants"
    assert len(lines) >= 2, f"Method {name} body is too short ({len(lines)} lines)"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — CLAUDE.md:7 @ 262a50bb
def test_no_panic_unwrap_in_new_method():
    """New method must not use panic!, unreachable!, or .unwrap() (CLAUDE.md rule)."""
    src = Path(PRINTER).read_text()
    result = _find_new_stderr_method(src)
    assert result is not None, "Could not find new method body to check"
    name, body = result
    assert not re.search(r"(panic!|unreachable!|\.unwrap\(\))", body), (
        f"Method {name} uses panic!/unreachable!/unwrap() — violates CLAUDE.md:7"
    )


# [agent_config] fail_to_pass — CLAUDE.md:7 @ 262a50bb
def test_no_unsafe_in_new_method():
    """New method must not use unsafe code (CLAUDE.md rule)."""
    src = Path(PRINTER).read_text()
    result = _find_new_stderr_method(src)
    assert result is not None, "Could not find new method body to check"
    name, body = result
    assert not re.search(r"\bunsafe\b", body), (
        f"Method {name} uses unsafe — violates CLAUDE.md:7"
    )


# [agent_config] pass_to_pass — CLAUDE.md:16 @ 262a50bb4c952cf2461d4073ae21081ed516f21c
def test_no_local_imports_in_new_method():
    """New method must not use local 'use' imports — prefer top-level imports (CLAUDE.md rule)."""
    src = Path(PRINTER).read_text()
    result = _find_new_stderr_method(src)
    assert result is not None, "Could not find new method body to check"
    name, body = result
    assert not re.search(r"\buse\s+", body), (
        f"Method {name} contains a local 'use' statement — violates CLAUDE.md:16"
    )


# [agent_config] fail_to_pass — CLAUDE.md:10 @ 262a50bb
def test_no_allow_attribute_in_new_code():
    """New code must not use #[allow(...)] — prefer #[expect()] (CLAUDE.md rule)."""
    src = Path(PRINTER).read_text()
    result = _find_new_stderr_method(src)
    assert result is not None, "Could not find new method to check"
    name, body = result
    # Also check for attributes on the method itself
    pattern = rf"((?:#\[[^\]]*\]\s*)*fn\s+{re.escape(name)}\(self\)\s*->\s*Stderr\s*\{{)"
    m = re.search(pattern, src)
    method_header = m.group(1) if m else ""
    assert not re.search(r"#\[allow\(", method_header + body), (
        f"Method {name} uses #[allow(...)] — prefer #[expect()] per CLAUDE.md:10"
    )
