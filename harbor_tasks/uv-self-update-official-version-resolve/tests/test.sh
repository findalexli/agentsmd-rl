#!/usr/bin/env bash
set +e

TOTAL=0
REPO=/repo

cd "$REPO"

add() { TOTAL=$(python3 -c "print(round($TOTAL + $1, 2))"); }

########################################
# GATE: Compilation check
########################################
# [pr_diff] (gate): Both modified crates compile without errors
echo "=== GATE: cargo check ==="
if ! cargo check -p uv-bin-install 2>&1; then
    echo "GATE FAILED: uv-bin-install compilation error"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
if ! cargo check -p uv --lib 2>&1; then
    echo "GATE FAILED: uv crate compilation error"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE PASSED"

########################################
# F2P Behavioral: Binary::Uv core API
########################################

# [pr_diff] (0.10): Binary::Uv variant exists and name() returns "uv"
echo "=== F2P: Binary::Uv name ==="
cat > crates/uv-bin-install/tests/harbor_name.rs << 'RUSTEOF'
use uv_bin_install::Binary;

#[test]
fn harbor_uv_name_is_uv() {
    assert_eq!(Binary::Uv.name(), "uv");
}

#[test]
fn harbor_ruff_name_still_ruff() {
    assert_eq!(Binary::Ruff.name(), "ruff");
}
RUSTEOF

if cargo test -p uv-bin-install --test harbor_name 2>&1; then
    echo "PASS: Binary::Uv name"
    add 0.10
else
    echo "FAIL: Binary::Uv name"
fi
rm -f crates/uv-bin-install/tests/harbor_name.rs

# [pr_diff] (0.20): Binary::Uv download URLs point to GitHub uv releases with correct format
echo "=== F2P: Binary::Uv download URL format ==="
cat > crates/uv-bin-install/tests/harbor_urls.rs << 'RUSTEOF'
use uv_bin_install::{ArchiveFormat, Binary};
use uv_pep440::Version;

#[test]
fn harbor_uv_download_url_is_github_uv() {
    let urls = Binary::Uv
        .download_urls(
            &Version::new([0, 6, 0]),
            "x86_64-unknown-linux-gnu",
            ArchiveFormat::TarGz,
        )
        .expect("should produce valid URLs");

    assert!(!urls.is_empty(), "Should have at least one URL");
    let url_str = urls[0].to_string();
    assert!(
        url_str.contains("github.com/astral-sh/uv/releases/download/"),
        "URL should be a GitHub uv release URL, got: {url_str}"
    );
    assert!(
        url_str.contains("0.6.0"),
        "URL should contain the version, got: {url_str}"
    );
    assert!(
        url_str.contains("x86_64-unknown-linux-gnu"),
        "URL should contain the platform, got: {url_str}"
    );
    assert!(
        url_str.contains(".tar.gz"),
        "URL should end with .tar.gz, got: {url_str}"
    );
}
RUSTEOF

if cargo test -p uv-bin-install --test harbor_urls 2>&1; then
    echo "PASS: Binary::Uv download URLs"
    add 0.20
else
    echo "FAIL: Binary::Uv download URLs"
fi
rm -f crates/uv-bin-install/tests/harbor_urls.rs

# [pr_diff] (0.10): Binary::Uv version_specifiers returns empty
echo "=== F2P: Binary::Uv version_specifiers ==="
cat > crates/uv-bin-install/tests/harbor_specs.rs << 'RUSTEOF'
use uv_bin_install::Binary;
use uv_pep440::VersionSpecifiers;

#[test]
fn harbor_uv_version_specifiers_empty() {
    let specs = Binary::Uv.version_specifiers();
    assert_eq!(specs, VersionSpecifiers::empty(), "Uv should have empty version specifiers");
}
RUSTEOF

if cargo test -p uv-bin-install --test harbor_specs 2>&1; then
    echo "PASS: Binary::Uv version_specifiers"
    add 0.10
else
    echo "FAIL: Binary::Uv version_specifiers"
fi
rm -f crates/uv-bin-install/tests/harbor_specs.rs

# [pr_diff] (0.10): Binary::Uv download URLs work across different platforms and formats
echo "=== F2P: Binary::Uv multi-platform ==="
cat > crates/uv-bin-install/tests/harbor_multiplatform.rs << 'RUSTEOF'
use uv_bin_install::{ArchiveFormat, Binary};
use uv_pep440::Version;

#[test]
fn harbor_uv_urls_aarch64_darwin_zip() {
    let urls = Binary::Uv
        .download_urls(
            &Version::new([0, 7, 2]),
            "aarch64-apple-darwin",
            ArchiveFormat::Zip,
        )
        .expect("should produce valid URLs for aarch64-apple-darwin");

    assert!(!urls.is_empty(), "Should have at least one URL");
    let url_str = urls[0].to_string();
    assert!(url_str.contains("0.7.2"), "URL should contain version 0.7.2, got: {url_str}");
    assert!(url_str.contains("aarch64-apple-darwin"), "URL should contain platform, got: {url_str}");
    assert!(url_str.ends_with(".zip"), "URL should end with .zip for Zip format, got: {url_str}");
}

#[test]
fn harbor_uv_urls_windows() {
    let urls = Binary::Uv
        .download_urls(
            &Version::new([1, 0, 0]),
            "x86_64-pc-windows-msvc",
            ArchiveFormat::Zip,
        )
        .expect("should produce valid URLs for windows");

    assert!(!urls.is_empty(), "Should have at least one URL");
    let url_str = urls[0].to_string();
    assert!(url_str.contains("x86_64-pc-windows-msvc"), "URL should contain windows platform, got: {url_str}");
    assert!(url_str.contains("github.com/astral-sh/uv/"), "URL should point to uv repo, got: {url_str}");
}
RUSTEOF

if cargo test -p uv-bin-install --test harbor_multiplatform 2>&1; then
    echo "PASS: Binary::Uv multi-platform"
    add 0.10
else
    echo "FAIL: Binary::Uv multi-platform"
fi
rm -f crates/uv-bin-install/tests/harbor_multiplatform.rs

# [pr_diff] (0.15): Binary::Uv has exactly 1 URL (no mirror), unlike Ruff which has 2
echo "=== F2P: Binary::Uv single URL (no mirror) ==="
cat > crates/uv-bin-install/tests/harbor_nomirror.rs << 'RUSTEOF'
use uv_bin_install::{ArchiveFormat, Binary};
use uv_pep440::Version;

#[test]
fn harbor_uv_has_single_url_no_mirror() {
    let uv_urls = Binary::Uv
        .download_urls(
            &Version::new([0, 6, 0]),
            "x86_64-unknown-linux-gnu",
            ArchiveFormat::TarGz,
        )
        .expect("Uv should produce valid URLs");

    // Uv should have exactly 1 URL (canonical GitHub only, no Astral CDN mirror)
    assert_eq!(
        uv_urls.len(), 1,
        "Uv should have exactly 1 download URL (no mirror), got {}",
        uv_urls.len()
    );
}

#[test]
fn harbor_ruff_still_has_mirror() {
    let ruff_urls = Binary::Ruff
        .download_urls(
            &Version::new([0, 9, 0]),
            "x86_64-unknown-linux-gnu",
            ArchiveFormat::TarGz,
        )
        .expect("Ruff should produce valid URLs");

    // Ruff should still have 2 URLs (mirror + canonical)
    assert_eq!(
        ruff_urls.len(), 2,
        "Ruff should have 2 download URLs (mirror + canonical), got {}",
        ruff_urls.len()
    );
}
RUSTEOF

if cargo test -p uv-bin-install --test harbor_nomirror 2>&1; then
    echo "PASS: Binary::Uv single URL, Ruff regression OK"
    add 0.15
else
    echo "FAIL: Binary::Uv single URL test"
fi
rm -f crates/uv-bin-install/tests/harbor_nomirror.rs

########################################
# Pass-to-pass: existing tests still work
########################################

# [pr_diff] (0.10): Existing uv-bin-install unit tests still pass
echo "=== P2P: existing uv-bin-install tests ==="
if cargo test -p uv-bin-install --lib 2>&1; then
    echo "PASS: existing uv-bin-install tests"
    add 0.10
else
    echo "FAIL: existing uv-bin-install tests"
fi

########################################
# Behavioral: self_update module tests
########################################

# [pr_diff] (0.15): self_update module has working unit tests that exercise
# version parsing, update-needed logic, and official-install detection.
# Tests must actually contain assertions (not trivial stubs).
echo "=== Behavioral: self_update unit tests with verification ==="
SELF_UPDATE_FILE=crates/uv/src/commands/self_update.rs

# Run the module's own tests
SELF_UPDATE_OUTPUT=$(cargo test -p uv --lib -- commands::self_update::tests 2>&1) || true
echo "$SELF_UPDATE_OUTPUT" | tail -10

# Count passing tests
PASSED_TESTS=$(echo "$SELF_UPDATE_OUTPUT" | grep -oP 'test result: ok\. \K\d+' || echo "0")

# Check the test module has real assertions (not trivial stubs)
TEST_SECTION=$(python3 -c "
import re, sys
src = open('$SELF_UPDATE_FILE').read()
m = re.search(r'#\[cfg\(test\)\].*?mod tests \{', src, re.DOTALL)
if m:
    # Find matching closing brace
    start = m.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == '{': depth += 1
        elif src[i] == '}': depth -= 1
        i += 1
    print(src[m.start():i])
else:
    print('')
" 2>/dev/null || true)

ASSERT_COUNT=$(echo "$TEST_SECTION" | grep -cE 'assert[!_(]' || true)

# Check test names cover key behaviors
HAS_VERSION_TEST=$(echo "$SELF_UPDATE_OUTPUT" | grep -cE 'test commands::self_update::tests::\S*(version|specif)' || true)
HAS_UPDATE_TEST=$(echo "$SELF_UPDATE_OUTPUT" | grep -cE 'test commands::self_update::tests::\S*update' || true)
HAS_OFFICIAL_TEST=$(echo "$SELF_UPDATE_OUTPUT" | grep -cE 'test commands::self_update::tests::\S*(official|install)' || true)

echo "  Tests passed: $PASSED_TESTS, Assertions: $ASSERT_COUNT"
echo "  Version tests: $HAS_VERSION_TEST, Update tests: $HAS_UPDATE_TEST, Official tests: $HAS_OFFICIAL_TEST"

if [ "$PASSED_TESTS" -ge 3 ] && [ "$ASSERT_COUNT" -ge 5 ] && \
   [ "$HAS_VERSION_TEST" -ge 1 ] && [ "$HAS_UPDATE_TEST" -ge 1 ] && [ "$HAS_OFFICIAL_TEST" -ge 1 ]; then
    echo "PASS: self_update unit tests (full behavioral coverage)"
    add 0.15
elif [ "$PASSED_TESTS" -ge 2 ] && [ "$ASSERT_COUNT" -ge 3 ]; then
    echo "PARTIAL: self_update unit tests (limited behavioral coverage)"
    add 0.07
elif [ "$PASSED_TESTS" -ge 1 ] && [ "$ASSERT_COUNT" -ge 1 ]; then
    echo "MINIMAL: self_update unit tests"
    add 0.03
else
    echo "FAIL: self_update unit tests (no tests or trivial stubs)"
fi

########################################
# Config-derived checks (CLAUDE.md)
########################################

# [agent_config] (0.05): No unwrap() in new/modified functions — CLAUDE.md:11 @ 10477cd
echo "=== Config checks ==="
# Compare self_update.rs to its original to find added lines, then check for unwrap()
ORIGINAL_LINES=$(git show HEAD:crates/uv/src/commands/self_update.rs 2>/dev/null | wc -l || echo "0")
CURRENT_LINES=$(wc -l < "$SELF_UPDATE_FILE" 2>/dev/null || echo "0")

# Get only the added lines (new code)
ADDED_CODE=$(git diff HEAD -- "$SELF_UPDATE_FILE" 2>/dev/null | grep '^+' | grep -v '^+++' || true)
UNWRAP_IN_ADDED=$(echo "$ADDED_CODE" | grep -c '\.unwrap()' || true)

if [ "$UNWRAP_IN_ADDED" -eq 0 ]; then
    echo "PASS: no unwrap() in new code"
    add 0.05
else
    echo "FAIL: found $UNWRAP_IN_ADDED unwrap() calls in new code"
fi

# [agent_config] (0.05): Top-level imports for new dependencies — CLAUDE.md:17 @ 10477cd
# Check that uv_bin_install and uv_pep440 are imported near the top of self_update.rs (first 30 lines)
TOP_IMPORTS=$(head -30 "$SELF_UPDATE_FILE" 2>/dev/null || true)
HAS_BIN_INSTALL=$(echo "$TOP_IMPORTS" | grep -c 'uv_bin_install' || true)
HAS_PEP440=$(echo "$TOP_IMPORTS" | grep -c 'uv_pep440' || true)
if [ "$HAS_BIN_INSTALL" -ge 1 ] && [ "$HAS_PEP440" -ge 1 ]; then
    echo "PASS: top-level imports for new dependencies"
    add 0.05
else
    echo "FAIL: new dependencies not imported at top level"
fi

########################################
# Final score
########################################
echo ""
echo "=== TOTAL REWARD: $TOTAL ==="
echo "$TOTAL" > /logs/verifier/reward.txt

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
