"""
Task: uv-cpuinfo-aarch64-hardfloat-detect
Repo: astral-sh/uv @ 87950df2cce7a219a617a1efc4807d8075986e5b
PR:   18530

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess

import pytest
from pathlib import Path

REPO = "/workspace"
SRC_PATH = Path(REPO) / "crates/uv-platform/src/cpuinfo.rs"


# ---------------------------------------------------------------------------
# Helpers: extract and compile feature detection logic from cpuinfo.rs
# ---------------------------------------------------------------------------

def _extract_braced_body(src: str, open_brace_pos: int) -> tuple:
    """Return (body_content, end_pos) for the braced block starting at open_brace_pos."""
    depth = 0
    for i in range(open_brace_pos, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[open_brace_pos + 1 : i], i + 1
    return None, len(src)


def _strip_tests_and_comments(source: str) -> str:
    test_start = source.find("#[cfg(test)]")
    non_test = source[:test_start] if test_start >= 0 else source
    lines = [l for l in non_test.split("\n")
             if not l.strip().startswith("//") and not l.strip().startswith("///")]
    return "\n".join(lines)


def _compile_rust(rust_source: str) -> str | None:
    """Compile Rust source, return path to binary or None."""
    src_path = "/tmp/test_cpuinfo_hardfloat.rs"
    bin_path = "/tmp/test_cpuinfo_hardfloat"
    Path(src_path).write_text(rust_source)
    r = subprocess.run(["rustc", "-o", bin_path, src_path],
                       capture_output=True, text=True, timeout=60)
    return bin_path if r.returncode == 0 else None


MAIN_TEMPLATE = """
fn main() {{
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 3 {{
        eprintln!("Usage: {{}} <features> <expected:true|false>", args[0]);
        std::process::exit(2);
    }}
    let features = &args[1];
    let expected = args[2] == "true";
    let result = {fn_call};
    if result != expected {{
        eprintln!("features={{:?}} expected={{}} got={{}}", features, expected, result);
        std::process::exit(1);
    }}
}}
"""


def _build_test_binary() -> str:
    """Extract feature detection from cpuinfo.rs, compile a test binary.

    The binary takes (features_string, expected_bool) as CLI args, exits 0 on match.
    Three extraction strategies handle different valid implementations.
    """
    source = SRC_PATH.read_text()
    clean = _strip_tests_and_comments(source)

    # Strategy 1: standalone fn(features: &str) -> bool
    helper_pat = re.compile(
        r"(?:#\[cfg\([^\]]*\)\]\s*\n\s*)?"
        r"(?:pub(?:\(crate\))?\s+)?"
        r"fn\s+(\w+)\s*\(\s*\w+\s*:\s*&str\s*\)\s*->\s*bool",
        re.MULTILINE,
    )
    match = helper_pat.search(clean)
    if match:
        fn_name = match.group(1)
        fn_keyword_pos = clean.rfind("fn", 0, match.end())
        fn_start = fn_keyword_pos
        preceding = clean[:fn_start].rstrip()
        if preceding.endswith("]"):
            attr_start = preceding.rfind("#[")
            if attr_start >= 0:
                fn_start = attr_start
        brace_pos = clean.index("{", match.end() - 5)
        _, fn_end = _extract_braced_body(clean, brace_pos)
        fn_code = clean[fn_start:fn_end]
        fn_code = re.sub(r"#\[cfg\([^\]]*\)\]\s*\n", "", fn_code)
        fn_code = re.sub(r"pub(?:\(crate\))?\s+", "", fn_code, count=1)

        rust_src = fn_code + "\n" + MAIN_TEMPLATE.format(fn_call=f"{fn_name}(features)")
        bin_path = _compile_rust(rust_src)
        if bin_path:
            return bin_path

    # Strategy 2: extract logic from detect_hardware_floating_point_support
    detect_match = re.search(
        r"(?:#\[cfg\([^\]]*\)\]\s*\n\s*)?"
        r"(?:pub(?:\(crate\))?\s+)?"
        r"fn\s+detect_hardware_floating_point_support[^{]*\{",
        clean, re.DOTALL,
    )
    if detect_match:
        detect_body, _ = _extract_braced_body(
            clean, clean.index("{", detect_match.start())
        )
        if detect_body:
            # 2a: .any(|param| expr) or .find(|param| expr)
            closure_match = re.search(
                r"\.(?:any|find)\(\s*\|(\w+)\|\s*(.+?)\s*\)",
                detect_body, re.DOTALL,
            )
            if closure_match:
                param = closure_match.group(1)
                expr = closure_match.group(2).strip()
                fn_code = (
                    f"fn test_features(features: &str) -> bool {{\n"
                    f"    features.split_whitespace().any(|{param}| {expr})\n"
                    f"}}\n"
                )
                rust_src = fn_code + MAIN_TEMPLATE.format(fn_call="test_features(features)")
                bin_path = _compile_rust(rust_src)
                if bin_path:
                    return bin_path

            # 2b: for-loop over split_whitespace()
            for_match = re.search(
                r"for\s+(\w+)\s+in\s+(\w+)\.split_whitespace\(\)\s*\{",
                detect_body,
            )
            if for_match:
                loop_var = for_match.group(1)
                brace_start = detect_body.index("{", for_match.start())
                loop_body, _ = _extract_braced_body(detect_body, brace_start)
                if loop_body:
                    cleaned = (loop_body
                               .replace("return Ok(true)", "return true")
                               .replace("return Ok(false)", "return false"))
                    fn_code = (
                        f"fn test_features(features: &str) -> bool {{\n"
                        f"    for {loop_var} in features.split_whitespace() {{{cleaned}}}\n"
                        f"    false\n"
                        f"}}\n"
                    )
                    rust_src = fn_code + MAIN_TEMPLATE.format(fn_call="test_features(features)")
                    bin_path = _compile_rust(rust_src)
                    if bin_path:
                        return bin_path

    pytest.fail(
        "Could not extract and compile feature detection logic from cpuinfo.rs. "
        "The fix must implement feature matching via: (a) a helper fn(&str) -> bool, "
        "(b) .any()/.find() closure on split_whitespace(), or (c) a for-loop."
    )


@pytest.fixture(scope="session")
def detection_binary():
    """Compile the feature detection binary once for all tests."""
    return _build_test_binary()


def _check(binary: str, features: str, expected: bool):
    """Run the compiled binary with given features, assert expected result."""
    r = subprocess.run(
        [binary, features, str(expected).lower()],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, (
        f"Detection mismatch for features={features!r}: "
        f"expected={expected}\n{r.stderr}"
    )


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_crate_compiles():
    """uv-platform crate compiles without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-platform"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_aarch64_fp_detected(detection_binary):
    """AArch64 kernel running arm32 userspace: 'fp' flag indicates hard-float."""
    _check(
        detection_binary,
        "fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics fphp asimdhp cpuid asimdrdm",
        True,
    )


# [pr_diff] fail_to_pass
def test_standalone_fp_detected(detection_binary):
    """Standalone 'fp' token is recognized as hard-float."""
    _check(detection_binary, "fp", True)


# [pr_diff] fail_to_pass
def test_fp_at_end_detected(detection_binary):
    """'fp' at end of features string is recognized as hard-float."""
    _check(detection_binary, "asimd evtstrm fp", True)


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests / static)
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_native_arm32_vfp_detected(detection_binary):
    """Native ARM32 with 'vfp' flag is still detected as hard-float."""
    _check(
        detection_binary,
        "half thumb fastmult vfp edsp neon vfpv3 tls vfpv4 idiva idivt vfpd32 lpae evtstrm crc32",
        True,
    )


# [pr_diff] pass_to_pass
def test_standalone_vfp_detected(detection_binary):
    """Standalone 'vfp' token is recognized as hard-float."""
    _check(detection_binary, "vfp", True)


# [pr_diff] pass_to_pass
def test_fphp_no_false_positive(detection_binary):
    """'fphp' alone must NOT match as discrete 'fp' — no false positives."""
    _check(detection_binary, "asimd fphp asimdhp", False)


# [pr_diff] pass_to_pass
def test_no_float_features(detection_binary):
    """Features with no float support return soft-float."""
    _check(detection_binary, "swp half thumb fastmult edsp", False)


# [pr_diff] pass_to_pass
def test_empty_features(detection_binary):
    """Empty features string returns soft-float."""
    _check(detection_binary, "", False)


# [repo_tests] pass_to_pass
def test_cargo_test_uv_platform():
    """Upstream tests in uv-platform crate still pass."""
    r = subprocess.run(
        ["cargo", "test", "-p", "uv-platform"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"cargo test failed:\n{r.stdout}\n{r.stderr}"


# [static] pass_to_pass
def test_not_stub():
    """Feature detection has real string processing logic, not a constant return."""
    source = SRC_PATH.read_text()
    test_start = source.find("#[cfg(test)]")
    non_test = source[:test_start] if test_start >= 0 else source

    assert '"vfp"' in non_test, "Missing 'vfp' string literal in detection code"
    assert '"fp"' in non_test, "Missing 'fp' string literal in detection code"

    clean = "\n".join(
        l for l in non_test.split("\n") if not l.strip().startswith("//")
    )
    has_processing = bool(
        re.search(r"\w+\.(split_whitespace|split|contains|any|find|iter|match)", clean)
    ) or bool(
        re.search(r"\w+\(\s*\w+\s*\)", clean)
    )
    assert has_processing, "No string processing operations found in detection code"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — CLAUDE.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:7 @ 87950df
def test_no_unwrap_panic():
    """No unwrap/panic/unreachable/unsafe/clippy-ignores in cpuinfo.rs production code (CLAUDE.md line 7)."""
    source = SRC_PATH.read_text()
    test_start = source.find("#[cfg(test)]")
    non_test = source[:test_start] if test_start >= 0 else source

    lines = [l for l in non_test.split("\n")
             if not l.strip().startswith("//") and not l.strip().startswith("///")]
    code = "\n".join(lines)

    violations = re.findall(r"\.unwrap\(\)|\.expect\(|panic!|unreachable!", code)
    assert len(violations) == 0, f"Found {len(violations)} forbidden call(s): {violations}"

    unsafe_uses = re.findall(r"\bunsafe\b", code)
    assert len(unsafe_uses) == 0, f"Found {len(unsafe_uses)} 'unsafe' usage(s) — CLAUDE.md forbids unsafe code"

    allow_clippy = re.findall(r"#\[allow\(clippy::", code)
    assert len(allow_clippy) == 0, (
        f"Found {len(allow_clippy)} #[allow(clippy::...)] — CLAUDE.md says use #[expect()] instead"
    )
