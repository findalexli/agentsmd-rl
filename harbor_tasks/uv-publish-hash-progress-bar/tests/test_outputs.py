"""
Task: uv-publish-hash-progress-bar
Repo: astral-sh/uv @ 7c2f6c696bdeb6b04166982b33b8fdca87578391
PR:   18752

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/repo"
LIB_RS = Path(f"{REPO}/crates/uv-publish/src/lib.rs")
PUBLISH_RS = Path(f"{REPO}/crates/uv/src/commands/publish.rs")
REPORTERS_RS = Path(f"{REPO}/crates/uv/src/commands/reporters.rs")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """uv-publish and uv crates must compile."""
    # Structural checks (Rust, can't import from Python)
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-publish", "-p", "uv"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo check failed:\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_reporter_trait_has_hash_methods():
    """Reporter trait must include hash lifecycle methods (start/progress/complete)."""
    # Structural: Rust trait, can't import from Python
    content = LIB_RS.read_text()
    m = re.search(
        r"(?:pub\s+)?trait\s+Reporter\b[^{]*\{(.*?)\n\}", content, re.DOTALL
    )
    assert m, "Reporter trait not found in lib.rs"
    trait_body = m.group(1)
    methods = re.findall(r"fn\s+(\w+)", trait_body)
    hash_methods = [name for name in methods if "hash" in name.lower()]
    # Base has 3 upload methods; fix adds at least 3 hash methods
    assert len(hash_methods) >= 3, (
        f"Expected >=3 hash methods in Reporter trait, found {hash_methods}"
    )
    # Verify lifecycle coverage: start, progress, complete
    joined = " ".join(hash_methods).lower()
    assert "start" in joined, f"Missing hash start method; found {hash_methods}"
    assert "progress" in joined or "inc" in joined, (
        f"Missing hash progress method; found {hash_methods}"
    )
    assert "complete" in joined or "finish" in joined or "end" in joined, (
        f"Missing hash complete method; found {hash_methods}"
    )


# [pr_diff] fail_to_pass
def test_hash_file_accepts_reporter():
    """hash_file function must accept a reporter/progress parameter."""
    # Structural: Rust function signature, can't import from Python
    content = LIB_RS.read_text()
    m = re.search(r"(?:async\s+)?fn\s+hash_file\s*\(([^)]*)\)", content, re.DOTALL)
    assert m, "hash_file function not found"
    params = m.group(1).lower()
    assert any(
        term in params for term in ("reporter", "progress", "callback", "observer")
    ), f"hash_file params lack reporting parameter: {params}"


# [pr_diff] fail_to_pass
def test_hash_file_accepts_filename():
    """hash_file must accept a filename parameter for reporter display."""
    # Structural: Rust function signature, can't import from Python
    content = LIB_RS.read_text()
    m = re.search(r"(?:async\s+)?fn\s+hash_file\s*\(([^)]*)\)", content, re.DOTALL)
    assert m, "hash_file function not found"
    params = m.group(1).lower()
    assert "filename" in params or "distfilename" in params or "dist_filename" in params, (
        f"hash_file params lack filename parameter for display: {params}"
    )


# [pr_diff] fail_to_pass
def test_publish_shows_hashing_before_upload():
    """publish.rs must display 'Hashing' before the 'Uploading' message."""
    # Structural: Rust string literals, can't import from Python
    content = PUBLISH_RS.read_text()
    hash_pos = content.find('"Hashing"')
    upload_pos = content.find('"Uploading"')
    assert hash_pos != -1, "No 'Hashing' status string found in publish.rs"
    assert upload_pos != -1, "No 'Uploading' status string found in publish.rs"
    assert hash_pos < upload_pos, (
        f"'Hashing' (pos {hash_pos}) should appear before 'Uploading' (pos {upload_pos}) "
        "in the code flow"
    )


# [pr_diff] fail_to_pass
def test_direction_enum_has_hash_variant():
    """Direction enum in reporters.rs must have a Hash variant."""
    # Structural: Rust enum, can't import from Python
    content = REPORTERS_RS.read_text()
    m = re.search(r"enum\s+Direction\s*\{([^}]*)\}", content, re.DOTALL)
    assert m, "Direction enum not found in reporters.rs"
    variants = m.group(1)
    assert re.search(r"\bHash\b", variants), (
        f"Direction enum missing Hash variant. Found: {variants.strip()}"
    )


# [pr_diff] fail_to_pass
def test_direction_hash_display_text():
    """Direction::Hash must map to a display string containing 'Hash'."""
    # Structural: Rust match arm, can't import from Python
    content = REPORTERS_RS.read_text()
    assert re.search(
        r"Hash\s*=>\s*\"[Hh]ash", content
    ), "Direction::Hash must map to a 'Hashing'/'Hashed' display string"


# [pr_diff] fail_to_pass
def test_publish_reporter_implements_hash_methods():
    """PublishReporter must implement hash reporter methods with real delegation."""
    # Structural: Rust impl block, can't import from Python
    content = REPORTERS_RS.read_text()
    m = re.search(
        r"impl\s+(?:\w+::)*Reporter\s+for\s+PublishReporter[^{]*\{(.*)",
        content,
        re.DOTALL,
    )
    assert m, "No Reporter impl for PublishReporter found"
    impl_body = m.group(1)
    hash_methods = re.findall(
        r"fn\s+(on_hash\w*|hash_\w+)\s*\([^)]*\)[^{]*\{([^}]*)\}",
        impl_body,
    )
    assert len(hash_methods) >= 3, (
        f"Expected >=3 hash method impls, found {len(hash_methods)}"
    )
    for name, body in hash_methods:
        assert len(body.strip()) >= 5, f"Method {name} appears to be a stub"


# [pr_diff] fail_to_pass
def test_form_metadata_read_accepts_reporter():
    """FormMetadata::read_from_file must accept a reporter parameter."""
    # Structural: Rust function signature, can't import from Python
    content = LIB_RS.read_text()
    m = re.search(
        r"(?:pub\s+)?(?:async\s+)?fn\s+read_from_file\s*\(([^)]*)\)",
        content, re.DOTALL,
    )
    assert m, "FormMetadata::read_from_file not found"
    params = m.group(1).lower()
    assert "reporter" in params, (
        f"read_from_file params lack reporter: {params}"
    )


# [pr_diff] fail_to_pass
def test_check_url_accepts_reporter():
    """check_url function must accept a reporter parameter."""
    # Structural: Rust function signature, can't import from Python
    content = LIB_RS.read_text()
    m = re.search(
        r"(?:pub\s+)?(?:async\s+)?fn\s+check_url\s*\(([^)]*)\)",
        content, re.DOTALL,
    )
    assert m, "check_url function not found"
    params = m.group(1).lower()
    assert "reporter" in params, (
        f"check_url params lack reporter: {params}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_cargo_test_uv_publish():
    """Existing uv-publish unit tests must still pass."""
    r = subprocess.run(
        ["cargo", "test", "-p", "uv-publish"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"uv-publish tests failed:\n{r.stderr.decode()[-2000:]}"
    )


# [pr_diff] pass_to_pass
def test_upload_methods_preserved():
    """Existing upload reporter methods must not be removed."""
    # Structural: Rust trait methods, can't import from Python
    content = LIB_RS.read_text()
    for method in ("on_upload_start", "on_upload_progress", "on_upload_complete"):
        assert f"fn {method}" in content, f"Upload method {method} missing from Reporter"


# [pr_diff] pass_to_pass
def test_direction_retains_existing_variants():
    """Direction enum must still have Upload, Download, and Extract variants."""
    # Structural: Rust enum, can't import from Python
    content = REPORTERS_RS.read_text()
    m = re.search(r"enum\s+Direction\s*\{([^}]*)\}", content, re.DOTALL)
    assert m, "Direction enum not found"
    variants = m.group(1)
    for v in ("Upload", "Download", "Extract"):
        assert v in variants, f"Direction enum missing {v} variant"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:7 @ 7c2f6c696bdeb6b04166982b33b8fdca87578391
def test_no_unsafe_patterns_in_hash_code():
    """CLAUDE.md:7 - AVOID panic!, unreachable!, .unwrap(), unsafe in new hash code."""
    # Structural: Rust function bodies, can't import from Python
    content = LIB_RS.read_text()
    hash_fns = re.findall(
        r"(?:async\s+)?fn\s+\w*hash\w*\b.*?\n\}", content, re.DOTALL
    )
    assert hash_fns, "No hash functions found (prerequisite check)"
    for fn_text in hash_fns:
        assert ".unwrap()" not in fn_text, (
            "Found .unwrap() in hash function — violates CLAUDE.md:7"
        )
        # Allow panic/unreachable in test code only
        if "#[cfg(test)]" not in fn_text and "#[test]" not in fn_text:
            assert "panic!" not in fn_text, (
                "Found panic! in hash function — violates CLAUDE.md:7"
            )
            assert "unreachable!" not in fn_text, (
                "Found unreachable! in hash function — violates CLAUDE.md:7"
            )
