"""
Task: uv-index-cache-control-header-error
Repo: astral-sh/uv @ 1b6b7befb1b7160ff32c8692bbf24ef98aae3fa7
PR:   18657

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

import pytest

REPO = "/src"
INDEX_RS = Path(REPO) / "crates/uv-distribution-types/src/index.rs"
CACHED_CLIENT_RS = Path(REPO) / "crates/uv-client/src/cached_client.rs"

# ---------------------------------------------------------------------------
# Rust tests injected into index.rs to verify deserialization validation.
# Appended as a second #[cfg(test)] module so they have access to crate deps.
# ---------------------------------------------------------------------------
VERIFIER_RUST_TESTS = r'''
#[cfg(test)]
mod __verifier_cache_control {
    use super::*;

    // --- fail-to-pass: invalid values rejected at deserialization ---
    // Use Rust \\n so that the TOML parser sees \n escape → newline byte in value.
    // TOML basic strings reject literal newlines, so we must use TOML escapes.

    #[test]
    fn newline_in_api_rejected() {
        let toml_str = "name = \"test\"\nurl = \"https://x.com/simple\"\n[cache-control]\napi = \"max-age=600\\n\"\n";
        assert!(toml::from_str::<Index>(toml_str).is_err(),
            "Cache-control.api with newline should be rejected");
    }

    #[test]
    fn cr_in_api_rejected() {
        let toml_str = "name = \"test\"\nurl = \"https://x.com/simple\"\n[cache-control]\napi = \"max-age=600\\r\"\n";
        assert!(toml::from_str::<Index>(toml_str).is_err(),
            "Cache-control.api with CR should be rejected");
    }

    #[test]
    fn null_in_api_rejected() {
        let toml_str = "name = \"test\"\nurl = \"https://x.com/simple\"\n[cache-control]\napi = \"max-age=600\\u0000\"\n";
        assert!(toml::from_str::<Index>(toml_str).is_err(),
            "Cache-control.api with null byte should be rejected");
    }

    #[test]
    fn del_in_api_rejected() {
        let toml_str = "name = \"test\"\nurl = \"https://x.com/simple\"\n[cache-control]\napi = \"max-age=600\\u007f\"\n";
        assert!(toml::from_str::<Index>(toml_str).is_err(),
            "Cache-control.api with DEL should be rejected");
    }

    #[test]
    fn newline_in_files_rejected() {
        let toml_str = "name = \"test\"\nurl = \"https://x.com/simple\"\n[cache-control]\nfiles = \"max-age=3600\\n\"\n";
        assert!(toml::from_str::<Index>(toml_str).is_err(),
            "Cache-control.files with newline should be rejected");
    }

    #[test]
    fn null_in_files_rejected() {
        let toml_str = "name = \"test\"\nurl = \"https://x.com/simple\"\n[cache-control]\nfiles = \"max-age=3600\\u0000\"\n";
        assert!(toml::from_str::<Index>(toml_str).is_err(),
            "Cache-control.files with null byte should be rejected");
    }

    // --- pass-to-pass: valid values still accepted ---

    #[test]
    fn valid_both_fields() {
        let toml_str = r#"
            name = "test"
            url = "https://x.com/simple"
            [cache-control]
            api = "max-age=600"
            files = "max-age=3600"
        "#;
        assert!(toml::from_str::<Index>(toml_str).is_ok(), "Both fields valid should parse");
    }

    #[test]
    fn valid_directives() {
        for directive in &[
            "no-cache",
            "no-store",
            "max-age=0",
            "private, max-age=3600, must-revalidate",
            "public, s-maxage=31536000",
            "max-age=365000000, immutable, public",
        ] {
            let toml_str = format!(
                "name = \"test\"\nurl = \"https://x.com/simple\"\n\
                 [cache-control]\napi = \"{}\"\n",
                directive
            );
            assert!(toml::from_str::<Index>(&toml_str).is_ok(),
                "Valid directive '{}' should be accepted", directive);
        }
    }

    #[test]
    fn api_only() {
        let toml_str = r#"
            name = "test"
            url = "https://x.com/simple"
            [cache-control]
            api = "max-age=300"
        "#;
        assert!(toml::from_str::<Index>(toml_str).is_ok(), "API-only should parse");
    }

    #[test]
    fn files_only() {
        let toml_str = r#"
            name = "test"
            url = "https://x.com/simple"
            [cache-control]
            files = "no-cache"
        "#;
        assert!(toml::from_str::<Index>(toml_str).is_ok(), "Files-only should parse");
    }

    // --- pass-to-pass: round-trip ---

    #[test]
    fn roundtrip_both_fields() {
        let toml_str = "name = \"test\"\nurl = \"https://test.example.com/simple\"\n\
                         [cache-control]\napi = \"max-age=600\"\nfiles = \"no-cache, must-revalidate\"\n";
        let index: Index = toml::from_str(toml_str).unwrap();
        let ser = toml::to_string(&index).unwrap();
        let index2: Index = toml::from_str(&ser).unwrap();
        let ser2 = toml::to_string(&index2).unwrap();
        assert_eq!(ser, ser2, "Round-trip serialization should be stable");
    }

    #[test]
    fn roundtrip_api_only() {
        let toml_str = "name = \"test\"\nurl = \"https://test.example.com/simple\"\n\
                         [cache-control]\napi = \"max-age=300\"\n";
        let index: Index = toml::from_str(toml_str).unwrap();
        let ser = toml::to_string(&index).unwrap();
        assert!(ser.contains("max-age=300"), "Serialized output should preserve the api value");
    }
}
'''


@pytest.fixture(scope="session")
def behavioral_results():
    """Inject verifier Rust tests into index.rs, compile and run, then restore."""
    original = INDEX_RS.read_text()
    try:
        INDEX_RS.write_text(original + VERIFIER_RUST_TESTS)
        r = subprocess.run(
            ["cargo", "test", "-p", "uv-distribution-types", "__verifier_cache_control"],
            cwd=REPO,
            capture_output=True,
            timeout=300,
        )
        return r.stdout.decode() + r.stderr.decode(), r.returncode
    finally:
        INDEX_RS.write_text(original)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- compilation
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_compilation():
    """Modified crates must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-distribution-types", "-p", "uv-client"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- invalid cache-control rejected at deserialization
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_invalid_api_cache_control_rejected(behavioral_results):
    """Invalid HTTP header values in cache-control.api are rejected during deserialization.

    Tests newline, CR, null, and DEL bytes. On the base commit, SmallString
    accepts these silently; a correct fix validates via HeaderValue and rejects.
    """
    output, _ = behavioral_results
    for name in ["newline_in_api_rejected", "cr_in_api_rejected",
                 "null_in_api_rejected", "del_in_api_rejected"]:
        assert f"{name} ... ok" in output, (
            f"Invalid api cache-control test '{name}' failed:\n{output[-2000:]}"
        )


# [pr_diff] fail_to_pass
def test_invalid_files_cache_control_rejected(behavioral_results):
    """Invalid HTTP header values in cache-control.files are also rejected."""
    output, _ = behavioral_results
    for name in ["newline_in_files_rejected", "null_in_files_rejected"]:
        assert f"{name} ... ok" in output, (
            f"Invalid files cache-control test '{name}' failed:\n{output[-2000:]}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) -- valid values still accepted
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_valid_cache_control_accepted(behavioral_results):
    """Valid cache-control values (various directives) are accepted after the fix."""
    output, _ = behavioral_results
    for name in ["valid_both_fields", "valid_directives", "api_only", "files_only"]:
        assert f"{name} ... ok" in output, (
            f"Valid cache-control test '{name}' failed:\n{output[-2000:]}"
        )


# [pr_diff] pass_to_pass
def test_cache_control_roundtrip(behavioral_results):
    """Cache-control values survive serialize/deserialize round-trip."""
    output, _ = behavioral_results
    for name in ["roundtrip_both_fields", "roundtrip_api_only"]:
        assert f"{name} ... ok" in output, (
            f"Round-trip test '{name}' failed:\n{output[-2000:]}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) -- existing upstream tests
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_existing_upstream_tests():
    """Existing cache-control unit tests in the repo still pass."""
    r = subprocess.run(
        ["cargo", "test", "-p", "uv-distribution-types", "--", "test_index_cache_control"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert "test result: ok" in output, (
        f"Upstream cache-control tests failed:\n{output[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) -- CLAUDE.md rules
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass -- CLAUDE.md:7 @ 1b6b7befb1b7160ff32c8692bbf24ef98aae3fa7
def test_no_expect_on_header_conversion():
    """No panicking .expect()/.unwrap() on cache-control header value conversion.

    Rule: "AVOID using panic!, unreachable!, .unwrap(), unsafe code" (CLAUDE.md:7)
    The base commit has .expect("Cache-Control header must be valid UTF-8") which panics
    on invalid header values. The fix must remove this panic path.
    """
    content = CACHED_CLIENT_RS.read_text()
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if ".expect(" in line or (".unwrap()" in line and "try_clone" not in line):
            context = "\n".join(lines[max(0, i - 3) : i + 4]).lower()
            if "cache" in context or "headervalue" in context or "header_value" in context:
                assert False, (
                    f"Found panicking call near cache-control/header context at line {i + 1}:\n"
                    f"  {line.strip()}"
                )
