"""
Task: nextjs-turbo-persistence-optional-compression
Repo: vercel/next.js @ b2f193b0964212c3ef0213efb74fe40dfd5be43b
PR:   89309

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

No Rust toolchain in Docker image — tests use git diff (subprocess)
and source file analysis to verify the code changes.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
CRATE = "turbopack/crates/turbo-persistence/src"
BUILDER_REL = f"{CRATE}/static_sorted_file_builder.rs"
SST_REL = f"{CRATE}/static_sorted_file.rs"
ARC_BYTES_REL = f"{CRATE}/arc_bytes.rs"
ARC_SLICE_REL = f"{CRATE}/arc_slice.rs"
LIB_REL = f"{CRATE}/lib.rs"
README_REL = "turbopack/crates/turbo-persistence/README.md"


def _git_diff(*rel_paths: str) -> str:
    """Get diff between HEAD and working tree via subprocess."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--", *rel_paths],
        capture_output=True, text=True, cwd=REPO, timeout=30,
    )
    assert r.returncode == 0, f"git diff failed: {r.stderr}"
    return r.stdout


def _diff_lines(diff: str, kind: str) -> list[str]:
    """Extract stripped added (+) or removed (-) lines from a unified diff."""
    prefix = "+" if kind == "added" else "-"
    skip = "+++" if kind == "added" else "---"
    return [
        line[1:].strip()
        for line in diff.splitlines()
        if line.startswith(prefix) and not line.startswith(skip)
    ]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via git diff
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_arc_bytes_replaces_arc_slice():
    """ArcSlice<T> replaced by ArcBytes with Mmap backing support.

    arc_slice.rs must be deleted, arc_bytes.rs must be created with
    Mmap-backed storage variant.
    """
    arc_bytes = Path(REPO) / ARC_BYTES_REL
    arc_slice = Path(REPO) / ARC_SLICE_REL

    assert arc_bytes.exists(), "arc_bytes.rs must exist"
    assert not arc_slice.exists(), "arc_slice.rs must be deleted"

    content = arc_bytes.read_text()
    assert "struct ArcBytes" in content, "ArcBytes struct must be defined"
    assert "Mmap" in content, "ArcBytes must support Mmap backing"
    assert "fn from_mmap" in content or "from_mmap" in content, \
        "ArcBytes must have from_mmap constructor"
    assert "fn is_mmap_backed" in content or "is_mmap_backed" in content, \
        "ArcBytes must expose is_mmap_backed method"


# [pr_diff] fail_to_pass
def test_compression_config_optional():
    """CompressionConfig enum added with Uncompressed variant.

    The builder must define CompressionConfig with at least TryCompress
    and Uncompressed variants to allow blocks to skip compression.
    """
    builder = Path(REPO) / BUILDER_REL
    content = builder.read_text()

    assert "CompressionConfig" in content, \
        "CompressionConfig enum must exist in the builder"
    assert "Uncompressed" in content, \
        "CompressionConfig must have an Uncompressed variant"
    assert "TryCompress" in content, \
        "CompressionConfig must have a TryCompress variant"


# [pr_diff] fail_to_pass
def test_index_blocks_skip_compression():
    """Index blocks must use Uncompressed config (not TryCompress).

    Index blocks are minimally compressible (hash→block-index pairs)
    so the write_index_block method should use Uncompressed.
    """
    builder = Path(REPO) / BUILDER_REL
    content = builder.read_text()

    # Find the write_index_block function and check it uses Uncompressed
    match = re.search(
        r'fn\s+write_index_block\b.*?\{(.*?)\n\s{4}\}',
        content, re.DOTALL,
    )
    assert match is not None, "write_index_block function must exist"
    body = match.group(1)
    assert "Uncompressed" in body, \
        "write_index_block must use CompressionConfig::Uncompressed"
    # Must NOT pass a compression dictionary for index blocks
    assert "dict" not in body.lower() or "Uncompressed" in body, \
        "Index blocks should skip compression dictionary"


# [pr_diff] fail_to_pass
def test_uncompressed_block_zero_copy_mmap():
    """read_block returns zero-copy mmap slice for uncompressed blocks.

    When uncompressed_length == 0, the block is stored uncompressed
    and should be served directly from the mmap via ArcBytes::from_mmap.
    """
    sst = Path(REPO) / SST_REL
    content = sst.read_text()

    # get_compressed_block should be renamed to get_raw_block
    assert "fn get_raw_block" in content, \
        "get_compressed_block must be renamed to get_raw_block"
    assert "fn get_compressed_block" not in content, \
        "get_compressed_block should no longer exist (renamed to get_raw_block)"

    # read_block must handle uncompressed_length == 0 with from_mmap
    fn_match = re.search(
        r'fn\s+read_block\b.*?\n\s{4}\}',
        content, re.DOTALL,
    )
    assert fn_match is not None, "read_block function must exist"
    fn_body = fn_match.group(0)
    assert "uncompressed_length == 0" in fn_body or "uncompressed_length == 0" in fn_body.replace(" ", ""), \
        "read_block must check for uncompressed_length == 0"
    assert "from_mmap" in fn_body, \
        "read_block must use ArcBytes::from_mmap for uncompressed blocks"


# [pr_diff] fail_to_pass
def test_compression_threshold_78():
    """Compression uses 7/8 threshold (LevelDB/RocksDB pattern).

    Blocks are only stored compressed if the result is < 7/8 of the
    original size. Check for the threshold calculation.
    """
    builder = Path(REPO) / BUILDER_REL
    content = builder.read_text()

    # The threshold is: compressed < original - (original / 8)
    # or equivalently: compressed < original * 7/8
    assert "block.len() / 8" in content or "block.len()/8" in content, \
        "Must use 7/8 compression threshold (block.len() - block.len() / 8)"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — README update required
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass — CLAUDE.md:44-46 @ b2f193b0964212c3ef0213efb74fe40dfd5be43b
def test_readme_documents_block_compression():
    """README.md must document the new block compression format.

    CLAUDE.md lines 44-46 require reading/maintaining README files.
    The SST format section must be updated to explain that blocks can
    be compressed or uncompressed, with header=0 meaning uncompressed.
    """
    readme = Path(REPO) / README_REL
    content = readme.read_text()

    # Must have a section about block compression
    assert "block compression" in content.lower() or "Block Compression" in content, \
        "README must document block compression"

    # Must document that header=0 means uncompressed
    assert "uncompressed" in content.lower(), \
        "README must explain uncompressed block handling"

    # Must mention the header semantics (0 = uncompressed, >0 = compressed length)
    has_header_zero = ("header = 0" in content.lower()
                       or "header == 0" in content.lower()
                       or "= 0" in content and "uncompressed" in content.lower())
    assert has_header_zero, \
        "README must document that header value 0 means uncompressed"

    # Must document LZ4 compression
    assert "lz4" in content.lower(), \
        "README must mention LZ4 as the compression algorithm"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — module rename
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_lib_exports_arc_bytes():
    """lib.rs must export ArcBytes (renamed from ArcSlice).

    The module declaration and pub use must reference arc_bytes, not arc_slice.
    """
    lib = Path(REPO) / LIB_REL
    content = lib.read_text()

    assert "mod arc_bytes" in content, \
        "lib.rs must declare mod arc_bytes"
    assert "pub use arc_bytes::ArcBytes" in content, \
        "lib.rs must export ArcBytes"
    assert "arc_slice" not in content, \
        "lib.rs must not reference arc_slice (renamed to arc_bytes)"


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config + static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — CLAUDE.md:44-46 @ b2f193b0964212c3ef0213efb74fe40dfd5be43b
def test_readme_has_sst_format_section():
    """README must retain the SST file on-disk format documentation.

    CLAUDE.md lines 44-46 establish README files as important documentation.
    The README must keep the SST file format section intact.
    """
    readme = Path(REPO) / README_REL
    content = readme.read_text()

    assert "SST file" in content or "sst file" in content.lower(), \
        "README must document the SST file format"
    assert "on disk format" in content.lower() or "On disk format" in content, \
        "README must have the 'On disk format' section"
    assert "Index Block" in content, \
        "README must document Index Block format"
    assert "Key Block" in content, \
        "README must document Key Block format"
    assert "Value Block" in content, \
        "README must document Value Block format"


# [static] pass_to_pass
def test_anti_stub_builder():
    """static_sorted_file_builder.rs has substantial content."""
    builder = Path(REPO) / BUILDER_REL
    line_count = len(builder.read_text().splitlines())
    assert line_count > 400, \
        f"Builder has only {line_count} lines — expected >400"
