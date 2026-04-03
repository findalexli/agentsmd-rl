"""
Task: nextjs-turbo-persistence-sst-no-hash
Repo: vercel/next.js @ d5a88ba4eb50fa9fcc2c06a68da54783d615b017
PR:   88938

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/next.js"
SST_FILE = Path(REPO) / "turbopack/crates/turbo-persistence/src/static_sorted_file.rs"
BUILDER_FILE = Path(REPO) / "turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs"
README_FILE = Path(REPO) / "turbopack/crates/turbo-persistence/README.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Rust files must exist and contain valid Rust structure."""
    for path in [SST_FILE, BUILDER_FILE]:
        src = path.read_text()
        # Basic Rust structure sanity: must have fn, use, pub keywords
        assert "fn " in src, f"{path.name} missing function definitions"
        assert "use " in src, f"{path.name} missing use statements"
    readme = README_FILE.read_text()
    assert "Key Block" in readme, "README missing Key Block section"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_two_key_block_types_defined():
    """Both BLOCK_TYPE_KEY_WITH_HASH and BLOCK_TYPE_KEY_NO_HASH must be defined."""
    src = SST_FILE.read_text()
    # Must define two distinct key block type constants
    match_with = re.search(r'pub\s+const\s+BLOCK_TYPE_KEY_WITH_HASH\s*:\s*u8\s*=\s*1\s*;', src)
    match_no = re.search(r'pub\s+const\s+BLOCK_TYPE_KEY_NO_HASH\s*:\s*u8\s*=\s*2\s*;', src)
    assert match_with, "BLOCK_TYPE_KEY_WITH_HASH: u8 = 1 not found"
    assert match_no, "BLOCK_TYPE_KEY_NO_HASH: u8 = 2 not found"


# [pr_diff] fail_to_pass
def test_compare_hash_key_function():
    """A compare_hash_key function must exist to handle hash-or-hashless comparison."""
    src = SST_FILE.read_text()
    # Must define compare_hash_key that takes entry_hash as byte slice
    assert "fn compare_hash_key" in src, "compare_hash_key function not found"
    # Function must handle the empty-hash case (recompute from key)
    assert "is_empty()" in src, "compare_hash_key must handle empty hash case"


# [pr_diff] fail_to_pass
def test_get_key_entry_variable_hash_len():
    """get_key_entry must accept a hash_len parameter for variable hash sizes."""
    src = SST_FILE.read_text()
    # Find the get_key_entry function signature
    match = re.search(r'fn\s+get_key_entry[^{]*hash_len\s*:\s*u8', src, re.DOTALL)
    assert match, "get_key_entry must have a hash_len: u8 parameter"
    # Must use hash_len to compute offsets instead of hardcoded 8
    assert "hash_len_usize" in src, "get_key_entry must convert hash_len to usize for indexing"


# [pr_diff] fail_to_pass
def test_use_hash_threshold():
    """Builder must have a use_hash function with 32-byte key length threshold."""
    src = BUILDER_FILE.read_text()
    # Must define use_hash function
    match = re.search(r'fn\s+use_hash\s*\(\s*max_key_len\s*:\s*usize\s*\)\s*->\s*bool', src)
    assert match, "use_hash(max_key_len: usize) -> bool not found in builder"
    # Must use 32 as the threshold
    assert re.search(r'max_key_len\s*>\s*32', src), \
        "use_hash should use 32 as the key length threshold"


# [pr_diff] fail_to_pass
def test_builder_conditional_hash_write():
    """KeyBlockBuilder must conditionally write hashes via a write_hash method."""
    src = BUILDER_FILE.read_text()
    # Builder struct must have has_hash field
    assert re.search(r'has_hash\s*:\s*bool', src), \
        "KeyBlockBuilder must have has_hash: bool field"
    # Must have write_hash method that checks has_hash
    assert "fn write_hash" in src, "KeyBlockBuilder must have write_hash method"
    # put_small etc. must call write_hash instead of direct hash write
    assert "self.write_hash(" in src, "Entry methods must use write_hash"


# [pr_diff] fail_to_pass
def test_lookup_handles_both_block_types():
    """The lookup path must match on both KEY_WITH_HASH and KEY_NO_HASH block types."""
    src = SST_FILE.read_text()
    # The match arm should handle both types
    assert re.search(
        r'BLOCK_TYPE_KEY_WITH_HASH\s*\|\s*BLOCK_TYPE_KEY_NO_HASH', src
    ), "Lookup must match on BLOCK_TYPE_KEY_WITH_HASH | BLOCK_TYPE_KEY_NO_HASH"
    # Must compute has_hash from block_type
    assert "block_type == BLOCK_TYPE_KEY_WITH_HASH" in src, \
        "Must determine has_hash by comparing block_type"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_index_block_type_preserved():
    """BLOCK_TYPE_INDEX must still be defined for index blocks."""
    src = SST_FILE.read_text()
    assert re.search(r'pub\s+const\s+BLOCK_TYPE_INDEX\s*:\s*u8\s*=\s*0\s*;', src), \
        "BLOCK_TYPE_INDEX: u8 = 0 must still be defined"


# [static] pass_to_pass
def test_entry_types_preserved():
    """Key block entry type constants must still be defined."""
    src = SST_FILE.read_text()
    for name in ["KEY_BLOCK_ENTRY_TYPE_SMALL", "KEY_BLOCK_ENTRY_TYPE_MEDIUM",
                  "KEY_BLOCK_ENTRY_TYPE_BLOB", "KEY_BLOCK_ENTRY_TYPE_DELETED"]:
        assert f"pub const {name}" in src, f"{name} constant must still be defined"
