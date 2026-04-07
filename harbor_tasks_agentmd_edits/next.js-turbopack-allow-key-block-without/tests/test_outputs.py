"""
Task: next.js-turbopack-allow-key-block-without
Repo: vercel/next.js @ d5a88ba4eb50fa9fcc2c06a68da54783d615b017
PR:   88938

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
CRATE = f"{REPO}/turbopack/crates/turbo-persistence"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """turbo-persistence crate compiles without errors."""
    result = subprocess.run(
        ["cargo", "check", "-p", "turbo-persistence"],
        capture_output=True, text=True, cwd=REPO, timeout=600,
    )
    assert result.returncode == 0, f"cargo check failed:\n{result.stderr[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_block_type_no_hash_defined():
    """BLOCK_TYPE_KEY_NO_HASH must be defined as constant 2 and BLOCK_TYPE_KEY_WITH_HASH as 1."""
    ssf_rs = Path(f"{CRATE}/src/static_sorted_file.rs").read_text()

    assert re.search(r"BLOCK_TYPE_KEY_WITH_HASH\s*:\s*u8\s*=\s*1", ssf_rs), \
        "BLOCK_TYPE_KEY_WITH_HASH = 1 not found in static_sorted_file.rs"
    assert re.search(r"BLOCK_TYPE_KEY_NO_HASH\s*:\s*u8\s*=\s*2", ssf_rs), \
        "BLOCK_TYPE_KEY_NO_HASH = 2 not found in static_sorted_file.rs"
    # Old constant must not exist
    assert not re.search(r"pub\s+const\s+BLOCK_TYPE_KEY\s*:", ssf_rs), \
        "Old BLOCK_TYPE_KEY constant should be renamed to BLOCK_TYPE_KEY_WITH_HASH"


# [pr_diff] fail_to_pass
def test_use_hash_function():
    """use_hash function must exist with 32-byte threshold for omitting hashes."""
    builder_rs = Path(f"{CRATE}/src/static_sorted_file_builder.rs").read_text()

    match = re.search(r"fn\s+use_hash\s*\(\s*max_key_len\s*:\s*usize\s*\)\s*->\s*bool", builder_rs)
    assert match, "use_hash function not found in static_sorted_file_builder.rs"

    # Check the threshold is 32
    func_start = match.start()
    func_snippet = builder_rs[func_start:func_start + 200]
    assert "32" in func_snippet, \
        "use_hash must use 32-byte threshold for deciding hash storage"


# [pr_diff] fail_to_pass
def test_compare_hash_key_function():
    """compare_hash_key function must exist for hash-aware key comparison."""
    ssf_rs = Path(f"{CRATE}/src/static_sorted_file.rs").read_text()

    assert re.search(r"fn\s+compare_hash_key", ssf_rs), \
        "compare_hash_key function not found in static_sorted_file.rs"
    # Must handle both empty hash (recompute) and stored hash cases
    assert "entry_hash.is_empty()" in ssf_rs or "hash.is_empty()" in ssf_rs, \
        "compare_hash_key must handle empty hash case (recompute from key)"


# [pr_diff] fail_to_pass
def test_builder_conditional_hash():
    """KeyBlockBuilder must conditionally write hash based on has_hash field."""
    builder_rs = Path(f"{CRATE}/src/static_sorted_file_builder.rs").read_text()

    # has_hash field must exist in KeyBlockBuilder
    assert re.search(r"has_hash\s*:\s*bool", builder_rs), \
        "KeyBlockBuilder must have a has_hash: bool field"

    # KeyBlockBuilder::new must accept has_hash parameter
    assert re.search(r"fn\s+new\s*\([^)]*has_hash\s*:\s*bool", builder_rs), \
        "KeyBlockBuilder::new must accept has_hash parameter"

    # write_hash method must conditionally write
    assert re.search(r"fn\s+write_hash", builder_rs), \
        "KeyBlockBuilder must have a write_hash method for conditional hash writing"


# [pr_diff] fail_to_pass
def test_get_key_entry_hash_len_param():
    """get_key_entry must accept hash_len parameter for variable hash size."""
    ssf_rs = Path(f"{CRATE}/src/static_sorted_file.rs").read_text()

    assert re.search(r"fn\s+get_key_entry.*hash_len\s*:\s*u8", ssf_rs), \
        "get_key_entry must accept hash_len: u8 parameter"

    # Return type must use slice instead of u64 for hash
    assert re.search(r"hash\s*:\s*&.*\[u8\]", ssf_rs), \
        "GetKeyEntryResult.hash should be a byte slice, not u64"


# ---------------------------------------------------------------------------
# Config-edit — README documentation updates
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_readme_documents_block_type_2():
    """README must document block type 2 (key block without hash)."""
    readme = Path(f"{CRATE}/README.md").read_text()
    readme_lower = readme.lower()

    assert "block type" in readme_lower and "without hash" in readme_lower, \
        "README must document block type 2 as key block without hash"
    assert re.search(r"2\s*:\s*key block without hash", readme_lower) or \
           re.search(r"block type 2.*no hash", readme_lower) or \
           re.search(r"2: key block without hash", readme), \
        "README must specify block type 2 = key block without hash"


# [pr_diff] fail_to_pass
def test_readme_conditional_hash_format():
    """README entry formats must show hash is conditional on block type."""
    readme = Path(f"{CRATE}/README.md").read_text()

    assert "if block type 1" in readme or "if block type" in readme.lower(), \
        "README entry formats must indicate hash is conditional on block type"
    # Must document the threshold
    assert "32" in readme or "≤ 32" in readme, \
        "README must mention the 32-byte key length threshold for hash omission"


# [pr_diff] fail_to_pass
def test_readme_no_hash_todo():
    """README must not contain the old TODO about inefficient hashes."""
    readme = Path(f"{CRATE}/README.md").read_text()

    assert "TODO: 8 bytes key hash is a bit inefficient" not in readme, \
        "Old TODO about inefficient key hashes should be removed"
    assert "TODO" not in readme or "inefficient" not in readme.lower(), \
        "README should not have the old TODO about hash inefficiency"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_tests_pass():
    """All existing cargo tests for turbo-persistence must still pass."""
    result = subprocess.run(
        ["cargo", "test", "-p", "turbo-persistence"],
        capture_output=True, text=True, cwd=REPO, timeout=600,
    )
    assert result.returncode == 0, \
        f"cargo test failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"
    assert "test result: ok" in result.stdout, \
        f"No test results found in output:\n{result.stdout[-500:]}"
