"""
Task: uv-trampoline-pe-write-error
Repo: astral-sh/uv @ 8b1a15eae6aa51f25f7dfefd247d5592201b78a0
PR:   #18710

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: All tests are structural (regex on Rust source) because the Docker
image has no Rust toolchain — AST-only because: no cargo/rustc installed.
"""

import re
from pathlib import Path

REPO = "/home/user/uv"
LIB = Path(REPO) / "crates/uv-trampoline-builder/src/lib.rs"


def _read_lib():
    return LIB.read_text()


def _error_enum_body(src: str) -> str:
    m = re.search(r"pub\s+enum\s+Error\s*\{(.*?)\n\}", src, re.DOTALL)
    assert m, "Error enum not found in lib.rs"
    return m.group(1)


def _write_resources_fn_body(src: str) -> str:
    m = re.search(r"fn write_resources\(.*?\n\}", src, re.DOTALL)
    assert m, "write_resources function not found in lib.rs"
    return m.group(0)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_write_resources_variant_exists():
    """Error enum has a WriteResources struct variant with PathBuf and io::Error fields."""
    src = _read_lib()
    enum_body = _error_enum_body(src)

    assert re.search(r"WriteResources\s*\{", enum_body), (
        "WriteResources struct variant not found in Error enum"
    )

    # Extract the variant body
    m = re.search(r"WriteResources\s*\{([^}]+)\}", enum_body)
    assert m, "Could not parse WriteResources variant body"
    body = m.group(1)

    assert re.search(r":\s*PathBuf", body), "WriteResources has no PathBuf field"
    assert re.search(r"io::Error", body), "WriteResources has no io::Error field"


# [pr_diff] fail_to_pass
def test_write_resources_has_source_attr():
    """WriteResources has a #[source] attribute on the io::Error field."""
    src = _read_lib()
    enum_body = _error_enum_body(src)
    m = re.search(r"WriteResources\s*\{([^}]+)\}", enum_body)
    assert m, "WriteResources variant not found"
    assert "#[source]" in m.group(1), "WriteResources missing #[source] attribute"


# [pr_diff] fail_to_pass
def test_error_display_includes_path():
    """The #[error(...)] attribute for WriteResources references the path field."""
    src = _read_lib()
    # thiserror #[error("...")] before WriteResources should mention path
    pattern = r'#\[error\(.*?\b(path|file)\b.*?\)\]\s*(?:#\[.*?\]\s*)*WriteResources'
    assert re.search(pattern, src, re.DOTALL), (
        "WriteResources error display does not reference the file path"
    )


# [pr_diff] fail_to_pass
def test_write_resources_used_in_function():
    """write_resources maps errors to WriteResources (not Error::Io for OS errors)."""
    src = _read_lib()
    body = _write_resources_fn_body(src)

    # WriteResources must appear in the function body
    assert re.search(r"(Error::)?WriteResources", body), (
        "WriteResources not used in write_resources function"
    )

    # Error::Io(io::Error::from_raw_os_error...) must NOT appear — it should be replaced
    assert not re.search(
        r"Error::Io\s*\(\s*io::Error::from_raw_os_error", body, re.DOTALL
    ), "Error::Io(io::Error::from_raw_os_error...) still used in write_resources"

    # Must still have error handling — at least 3 map_err/WriteResources refs
    # (prevents gaming by deleting error handling entirely)
    refs = len(re.findall(r"map_err|WriteResources", body))
    assert refs >= 3, (
        f"Insufficient error handling ({refs} map_err/WriteResources refs, need >=3)"
    )


# [pr_diff] fail_to_pass
def test_write_resources_captures_path():
    """WriteResources construction references the path parameter."""
    src = _read_lib()
    body = _write_resources_fn_body(src)

    # Look for WriteResources { ... path ... } either direct or via closure
    ws_blocks = re.findall(r"WriteResources\s*\{([^}]+)\}", body)
    if not ws_blocks:
        # May be via a closure: |...| Error::WriteResources { ... }
        closures = re.findall(
            r"\|[^|]*\|\s*(?:Error::)?WriteResources\s*\{([^}]+)\}", body
        )
        assert closures, "No WriteResources construction found in write_resources"
        ws_blocks = closures

    path_captured = any(re.search(r"\bpath\b", block) for block in ws_blocks)
    assert path_captured, "WriteResources does not capture the path parameter"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_original_variants_preserved():
    """Original Error enum variants must not be removed."""
    src = _read_lib()
    required = [
        "Io(",
        "InvalidPath",
        "UnsupportedWindowsArch",
        "NotWindows",
        "UnprocessableMetadata",
        "ResourceTooLarge",
    ]
    for variant in required:
        assert variant in src, f"Missing original Error variant: {variant}"


# [pr_diff] pass_to_pass
def test_write_resources_signature_unchanged():
    """write_resources function signature must take path: &Path."""
    src = _read_lib()
    assert re.search(r"fn\s+write_resources\s*\(\s*path\s*:\s*&Path", src), (
        "write_resources function signature changed"
    )


# [pr_diff] pass_to_pass
def test_resource_too_large_still_used():
    """ResourceTooLarge error is still used inside write_resources."""
    src = _read_lib()
    body = _write_resources_fn_body(src)
    assert "ResourceTooLarge" in body, "ResourceTooLarge removed from write_resources"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — CLAUDE.md:7 @ 8b1a15eae6aa51f25f7dfefd247d5592201b78a0
def test_no_unwrap_panic_in_write_resources():
    """No unwrap(), panic!(), unreachable!(), or unsafe in write_resources (CLAUDE.md line 7)."""
    src = _read_lib()
    body = _write_resources_fn_body(src)
    for line in body.split("\n"):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        assert ".unwrap()" not in stripped, f"Found .unwrap() in: {stripped}"
        assert not re.search(r"\bpanic!\b", stripped), f"Found panic! in: {stripped}"
        assert not re.search(r"\bunreachable!\b", stripped), (
            f"Found unreachable! in: {stripped}"
        )
        # unsafe blocks are banned unless with SAFETY comment (CLAUDE.md lines 7, 9)
        if re.search(r"\bunsafe\b", stripped):
            # Check preceding line for SAFETY comment
            idx = body.split("\n").index(line)
            prev_lines = body.split("\n")[max(0, idx - 2) : idx]
            has_safety = any("SAFETY" in pl for pl in prev_lines)
            assert has_safety, f"Found unsafe without SAFETY comment in: {stripped}"


# [agent_config] pass_to_pass — CLAUDE.md:7 @ 8b1a15eae6aa51f25f7dfefd247d5592201b78a0
def test_no_new_allow_clippy():
    """No new #[allow(clippy::...)] in Error enum or write_resources (CLAUDE.md line 7).
    Existing allow attributes at base commit are excluded."""
    src = _read_lib()
    body = _write_resources_fn_body(src)
    enum_body = _error_enum_body(src)
    # The base commit has one: #[allow(clippy::unnecessary_wraps, unused_variables)]
    # on write_resources itself — that's pre-existing. Check for NEW ones inside the body.
    for region_name, region in [("write_resources body", body), ("Error enum", enum_body)]:
        for line in region.split("\n"):
            stripped = line.strip()
            if stripped.startswith("//"):
                continue
            # Allow the pre-existing attribute on the fn signature line
            if "clippy::unnecessary_wraps" in stripped:
                continue
            if re.search(r"#\[allow\(clippy::", stripped):
                raise AssertionError(
                    f"New #[allow(clippy::...)] found in {region_name}: {stripped}. "
                    "Use #[expect()] instead (CLAUDE.md line 10)"
                )


# [agent_config] pass_to_pass — CLAUDE.md:16 @ 8b1a15eae6aa51f25f7dfefd247d5592201b78a0
def test_simplified_import_top_level():
    """If Simplified trait is used, it must be imported at top level (CLAUDE.md line 16)."""
    src = _read_lib()

    # Check if Simplified methods are used anywhere
    if not re.search(r"user_display|simplified", src):
        return  # Not used → N/A → pass

    # If used, must be imported at top level (not inside a function)
    lines = src.split("\n")
    in_fn = False
    for line in lines:
        if re.match(r"^(pub\s+)?fn\s", line) or re.match(r"^\s+(pub\s+)?fn\s", line):
            in_fn = True
        if not in_fn and re.search(r"use\s+.*Simplified", line):
            return  # Found top-level import → pass

    raise AssertionError("Simplified trait used but not imported at top level")
