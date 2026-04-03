"""
Task: next.js-turbopack-optional-sst-compression
Repo: vercel/next.js @ b2f193b0964212c3ef0213efb74fe40dfd5be43b
PR:   89309

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
CRATE = f"{REPO}/turbopack/crates/turbo-persistence"
SRC = f"{CRATE}/src"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_rust_files_valid_syntax():
    """All modified .rs files must be valid UTF-8 and contain Rust syntax."""
    modified_files = [
        "arc_bytes.rs",
        "lib.rs",
        "db.rs",
        "compression.rs",
        "lookup_entry.rs",
        "static_sorted_file.rs",
        "static_sorted_file_builder.rs",
    ]
    for fname in modified_files:
        p = Path(SRC) / fname
        if p.exists():
            content = p.read_text()
            # Basic check: must contain Rust keywords
            assert "fn " in content or "use " in content or "mod " in content, \
                f"{fname} does not appear to contain valid Rust code"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_arc_bytes_replaces_arc_slice():
    """ArcSlice must be replaced by ArcBytes as the public type for byte slices."""
    lib_rs = Path(SRC) / "lib.rs"
    content = lib_rs.read_text()

    # ArcBytes module must be declared
    assert re.search(r"mod\s+arc_bytes", content), \
        "lib.rs must declare mod arc_bytes"

    # ArcBytes must be publicly exported
    assert re.search(r"pub\s+use\s+arc_bytes::ArcBytes", content), \
        "lib.rs must re-export ArcBytes publicly"

    # The old ArcSlice module should not be declared
    assert not re.search(r"mod\s+arc_slice", content), \
        "lib.rs should not declare the old arc_slice module"

    # arc_bytes.rs must exist
    arc_bytes = Path(SRC) / "arc_bytes.rs"
    assert arc_bytes.exists(), "arc_bytes.rs must exist"

    # arc_slice.rs must not exist
    arc_slice = Path(SRC) / "arc_slice.rs"
    assert not arc_slice.exists(), "arc_slice.rs should be removed"


# [pr_diff] fail_to_pass
def test_arc_bytes_has_mmap_support():
    """ArcBytes must support memory-mapped file backing."""
    arc_bytes = Path(SRC) / "arc_bytes.rs"
    content = arc_bytes.read_text()

    # Must have mmap-related imports
    assert "memmap2" in content or "Mmap" in content, \
        "arc_bytes.rs must use memmap2::Mmap"

    # Must have from_mmap constructor
    assert "fn from_mmap" in content, \
        "ArcBytes must have a from_mmap constructor"

    # Must have is_mmap_backed method
    assert "fn is_mmap_backed" in content, \
        "ArcBytes must have an is_mmap_backed method"

    # Must have a Backing enum or similar with Mmap variant
    assert "Mmap" in content and "Arc" in content, \
        "ArcBytes must support both Arc and Mmap backing"


# [pr_diff] fail_to_pass
def test_optional_compression_in_builder():
    """SST file builder must support writing blocks without compression."""
    builder = Path(SRC) / "static_sorted_file_builder.rs"
    content = builder.read_text()

    # Must have a way to write uncompressed blocks (CompressionConfig or similar)
    has_uncompressed_option = (
        "Uncompressed" in content or
        "uncompressed" in content.lower().split("fn write_index_block")[0]  # before the function
    )
    # The write_block function must handle both compressed and uncompressed
    assert "Uncompressed" in content or "uncompressed_size, 0" in content or \
        re.search(r"\(0,\s*block\)", content), \
        "Builder must support writing uncompressed blocks (sentinel size=0)"

    # Index blocks must be written without compression
    # write_index_block should NOT pass a compression dictionary
    idx_match = re.search(
        r"fn\s+write_index_block\s*\(\s*&mut\s+self\s*,\s*block\s*:\s*&\[u8\]\s*\)",
        content
    )
    assert idx_match, \
        "write_index_block should take only block (no dict parameter)"

    # The 7/8 compression threshold should be present
    assert "block.len() / 8" in content or "block.len() >> 3" in content or \
        "12.5%" in content or "7/8" in content, \
        "Builder must implement compression savings threshold (7/8 or 12.5%)"


# [pr_diff] fail_to_pass
def test_read_path_handles_uncompressed_blocks():
    """Reader must handle uncompressed blocks (header=0) via zero-copy mmap."""
    ssf = Path(SRC) / "static_sorted_file.rs"
    content = ssf.read_text()

    # The read_block function must check for uncompressed_length == 0
    assert "uncompressed_length == 0" in content or \
        "uncompressed_length == 0u32" in content or \
        re.search(r"if\s+uncompressed_length\s*==\s*0", content), \
        "read_block must handle uncompressed blocks (uncompressed_length == 0)"

    # Must use from_mmap for zero-copy reads of uncompressed blocks
    assert "from_mmap" in content, \
        "Uncompressed blocks should be returned as mmap-backed ArcBytes"

    # The old get_compressed_block should be renamed to get_raw_block or similar
    assert "get_raw_block" in content or "get_block" in content, \
        "get_compressed_block should be renamed since blocks can be uncompressed"

    # BlockWeighter must handle mmap-backed blocks differently
    assert "is_mmap_backed" in content, \
        "BlockWeighter should check is_mmap_backed for cache weight"


# [pr_diff] fail_to_pass
def test_medium_raw_variant_replaces_medium_compressed():
    """MediumCompressed EntryValue variant must be renamed to MediumRaw."""
    builder = Path(SRC) / "static_sorted_file_builder.rs"
    content = builder.read_text()

    # MediumRaw must exist
    assert "MediumRaw" in content, \
        "EntryValue must have a MediumRaw variant (renamed from MediumCompressed)"

    # MediumCompressed should not exist
    assert "MediumCompressed" not in content, \
        "MediumCompressed should be renamed to MediumRaw"

    # The variant must document that uncompressed_size=0 means uncompressed
    lookup = Path(SRC) / "lookup_entry.rs"
    lookup_content = lookup.read_text()
    assert "MediumRaw" in lookup_content, \
        "lookup_entry.rs must use MediumRaw instead of MediumCompressed"


# ---------------------------------------------------------------------------
# Config file update tests (config_edit) — README documentation
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must have a section about block compression
    assert "Block Compression" in content or "block compression" in content, \
        "README should have a Block Compression section"

    # Must document the header=0 sentinel for uncompressed blocks
    assert "Header = 0" in content or "header = 0" in content or \
        "header is 0" in content.lower() or "uncompressed" in content.lower(), \
        "README should document that header=0 means uncompressed"

    # Must document that header > 0 means LZ4 compressed
    assert "Header > 0" in content or "header > 0" in content or \
        "LZ4" in content, \
        "README should document that header>0 means LZ4 compressed"

    # Must describe block data format (compressed or uncompressed)
    assert "block data" in content.lower() or "block header" in content.lower(), \
        "README should describe the block data format"


# [config_edit] fail_to_pass

    # The old format said "4 bytes uncompressed block length" + "compressed data".
    # The new format should describe the header as able to indicate either compressed
    # or uncompressed blocks. Check for the NEW phrasing:
    assert "block header" in content.lower() or "header value" in content.lower(), \
        "README should describe the 4-byte field as a 'block header' (not just 'uncompressed block length')"

    # The old "compressed data" should be replaced with something that acknowledges
    # both compressed and uncompressed possibilities
    assert "block data" in content.lower(), \
        "README should use 'block data' (not just 'compressed data') to reflect optional compression"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_arc_bytes_not_stub():
    """arc_bytes.rs must have a real implementation, not a stub."""
    arc_bytes = Path(SRC) / "arc_bytes.rs"
    if not arc_bytes.exists():
        # If it doesn't exist, the F2P test above will catch it
        return
    content = arc_bytes.read_text()
    lines = [l for l in content.splitlines() if l.strip() and not l.strip().startswith("//")]
    # A real implementation should have substantial code
    assert len(lines) > 50, \
        f"arc_bytes.rs has only {len(lines)} non-comment lines — looks like a stub"

    # Must implement Deref, Hash, Clone for ArcBytes
    assert "impl Deref for ArcBytes" in content, "ArcBytes must implement Deref"
    assert "impl Hash for ArcBytes" in content, "ArcBytes must implement Hash"
    assert "impl Clone" in content or "#[derive(Clone)]" in content, \
        "ArcBytes must implement Clone"
