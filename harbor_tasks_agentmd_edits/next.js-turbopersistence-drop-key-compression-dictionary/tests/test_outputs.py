"""
Task: next.js-turbopersistence-drop-key-compression-dictionary
Repo: vercel/next.js @ 9d13b676e8a3f8f8f8ecc35df7e2ea94ab95bbd3
PR:   90608

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/next.js"
CRATE = Path(REPO) / "turbopack" / "crates" / "turbo-persistence"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_zstd_removed_from_cargo_toml():
    """Cargo.toml must not list zstd as a dependency."""
    cargo_toml = (CRATE / "Cargo.toml").read_text()
    # The base commit has: zstd = { version = "0.13.2", features = ["zdict_builder"] }
    assert "zstd" not in cargo_toml, \
        "Cargo.toml still lists zstd as a dependency"


# [pr_diff] fail_to_pass
def test_compress_function_simplified():
    """compress_into_buffer must not accept dict or long_term parameters."""
    src = (CRATE / "src" / "compression.rs").read_text()
    # The fixed version should have: pub fn compress_into_buffer(block: &[u8], buffer: &mut Vec<u8>)
    # The base version has: pub fn compress_into_buffer(block: &[u8], dict: Option<&[u8]>, _long_term: bool, buffer: &mut Vec<u8>)
    assert "dict: Option" not in src, \
        "compress_into_buffer still accepts a dict parameter"
    assert "long_term: bool" not in src and "_long_term: bool" not in src, \
        "compress_into_buffer still accepts a long_term parameter"


# [pr_diff] fail_to_pass
def test_decompress_function_simplified():
    """decompress_into_arc must not accept compression_dictionary parameter."""
    src = (CRATE / "src" / "compression.rs").read_text()
    # The fixed version: pub fn decompress_into_arc(uncompressed_length: u32, block: &[u8])
    # The base version: pub fn decompress_into_arc(uncompressed_length: u32, block: &[u8], compression_dictionary: Option<&[u8]>, _long_term: bool)
    assert "compression_dictionary" not in src, \
        "decompress_into_arc still accepts a compression_dictionary parameter"


# [pr_diff] fail_to_pass
def test_meta_data_no_dictionary_field():
    """StaticSortedFileMetaData must not have key_compression_dictionary_length field."""
    src = (CRATE / "src" / "static_sorted_file.rs").read_text()
    assert "key_compression_dictionary_length" not in src, \
        "StaticSortedFileMetaData still has key_compression_dictionary_length field"


# [pr_diff] fail_to_pass
def test_no_zstd_imports():
    """compression.rs must not import from zstd or use decompress_with_dict."""
    src = (CRATE / "src" / "compression.rs").read_text()
    assert "decompress_with_dict" not in src, \
        "compression.rs still imports decompress_with_dict"
    # Should use plain lz4 decompress only
    assert "decompress" in src, \
        "compression.rs should still use lz4 decompress"


# ---------------------------------------------------------------------------
# Pass-to-pass — structural integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compression_module_exists():
    """compression.rs must still exist and have both compress and decompress functions."""
    src = (CRATE / "src" / "compression.rs").read_text()
    assert "fn decompress_into_arc" in src, \
        "decompress_into_arc function missing from compression.rs"
    assert "fn compress_into_buffer" in src, \
        "compress_into_buffer function missing from compression.rs"


# [static] pass_to_pass
def test_lz4_compression_used():
    """compression.rs must use lz4 for compression."""
    src = (CRATE / "src" / "compression.rs").read_text()
    assert "lz4" in src.lower() or "lzzzz" in src, \
        "compression.rs should reference lz4/lzzzz compression library"


# ---------------------------------------------------------------------------
# Config/doc update tests (config_edit) — README must reflect format changes
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
