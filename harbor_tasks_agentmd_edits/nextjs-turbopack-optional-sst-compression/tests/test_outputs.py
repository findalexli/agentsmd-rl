"""Tests for turbopack optional SST compression feature.

This PR makes compression in SST files optional:
1. ArcSlice renamed to ArcBytes with mmap support
2. Compression is now optional using 7/8 heuristic from LevelDB/RocksDB
3. README.md updated to document block compression format

Tests use a mix of:
- subprocess.run() for behavioral tests (cargo check, compilation)
- File content inspection for structural verification
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/nextjs")
PERSISTENCE = REPO / "turbopack" / "crates" / "turbo-persistence"
README = PERSISTENCE / "README.md"


def test_code_compiles():
    """The crate should compile successfully (behavioral test via cargo check)."""
    result = subprocess.run(
        ["cargo", "check", "--lib"],
        cwd=PERSISTENCE,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Compilation failed:\n{result.stderr}"


def test_cargo_check_lib():
    """Repo's cargo check --lib passes (pass_to_pass gate for CI)."""
    r = subprocess.run(
        ["cargo", "check", "--lib"],
        cwd=PERSISTENCE,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"cargo check --lib failed:\n{r.stderr[-500:]}"


def test_cargo_check_tests():
    """Repo's cargo check --tests passes (pass_to_pass gate for CI)."""
    r = subprocess.run(
        ["cargo", "check", "--tests"],
        cwd=PERSISTENCE,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"cargo check --tests failed:\n{r.stderr[-500:]}"


def test_cargo_clippy_lib():
    """Repo's cargo clippy --lib passes (pass_to_pass gate for CI linting)."""
    r = subprocess.run(
        ["cargo", "clippy", "--lib"],
        cwd=PERSISTENCE,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"cargo clippy --lib failed:\n{r.stderr[-500:]}"


def test_cargo_fmt_check():
    """Repo's cargo fmt --check passes (pass_to_pass gate for code formatting)."""
    r = subprocess.run(
        ["cargo", "fmt", "--check"],
        cwd=PERSISTENCE,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"cargo fmt --check failed:\n{r.stderr[-500:]}"


def test_arc_bytes_exports_correctly():
    """ArcBytes should be exported from lib.rs and usable by dependent code."""
    test_code = """
use turbo_persistence::ArcBytes;

fn test_arc_bytes() {
    let data: ArcBytes = ArcBytes::from(Box::new([1u8, 2, 3, 4, 5]) as Box<[u8]>);
    assert_eq!(&*data, &[1, 2, 3, 4, 5]);
}
"""
    tests_dir = PERSISTENCE / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    test_file = tests_dir / "test_arc_bytes_export.rs"
    test_file.write_text(test_code)
    try:
        result = subprocess.run(
            ["cargo", "test", "--test", "test_arc_bytes_export", "--", "--nocapture"],
            cwd=PERSISTENCE,
            capture_output=True,
            text=True,
            timeout=120
        )
        result_compile = subprocess.run(
            ["cargo", "check", "--tests"],
            cwd=PERSISTENCE,
            capture_output=True,
            text=True,
            timeout=120
        )
        assert result_compile.returncode == 0, f"Test file compilation failed:\n{result_compile.stderr}"
    finally:
        test_file.unlink(missing_ok=True)


def test_arc_bytes_has_mmap_api():
    """ArcBytes should have the mmap-related API methods."""
    arc_bytes = PERSISTENCE / "src" / "arc_bytes.rs"
    content = arc_bytes.read_text()
    assert "is_mmap_backed" in content, "ArcBytes should have is_mmap_backed() method"
    assert "from_mmap" in content, "ArcBytes should have from_mmap() constructor"
    assert "Backing::Mmap" in content or "Backing::Arc" in content, \
        "ArcBytes should have Backing enum with Mmap variant"


def test_arc_slice_replaced_by_arc_bytes():
    """ArcSlice should be replaced by ArcBytes in all module exports."""
    lib_rs = PERSISTENCE / "src" / "lib.rs"
    content = lib_rs.read_text()
    assert "pub use arc_bytes::ArcBytes" in content, "lib.rs should export ArcBytes"
    assert "arc_slice" not in content, "lib.rs should not reference arc_slice module"
    assert "ArcSlice" not in content, "lib.rs should not reference ArcSlice type"


def test_compression_config_enum_exists():
    """static_sorted_file_builder.rs should have CompressionConfig enum with correct variants."""
    builder = PERSISTENCE / "src" / "static_sorted_file_builder.rs"
    content = builder.read_text()
    assert "CompressionConfig" in content, "Should have CompressionConfig enum"
    assert "TryCompress" in content, "Should have TryCompress variant"
    assert "Uncompressed" in content, "Should have Uncompressed variant"


def test_entry_value_uses_medium_raw():
    """EntryValue enum should use MediumRaw instead of MediumCompressed."""
    builder = PERSISTENCE / "src" / "static_sorted_file_builder.rs"
    content = builder.read_text()
    assert "MediumRaw" in content, "Should use MediumRaw instead of MediumCompressed"


def test_index_blocks_use_uncompressed():
    """Index blocks should be written uncompressed (not worth compressing)."""
    builder = PERSISTENCE / "src" / "static_sorted_file_builder.rs"
    content = builder.read_text()
    assert "CompressionConfig::Uncompressed" in content, \
        "Index blocks should use CompressionConfig::Uncompressed"


def test_7_8_compression_heuristic_implemented():
    """Code should implement 7/8 compression threshold heuristic from LevelDB/RocksDB."""
    builder = PERSISTENCE / "src" / "static_sorted_file_builder.rs"
    content = builder.read_text()
    heuristic_patterns = [
        "block.len() / 8",
        "7/8",
        "0.875",
        "smaller than the original",
        "smaller than block.len()",
    ]
    found = any(pattern in content for pattern in heuristic_patterns)
    assert found, "Should implement 7/8 compression threshold heuristic"


def test_decompress_into_arc_has_debug_assert():
    """decompress_into_arc should have debug_assert for uncompressed_length > 0."""
    compression = PERSISTENCE / "src" / "compression.rs"
    content = compression.read_text()
    assert "debug_assert!" in content, "Should have debug_assert"
    assert "uncompressed_length > 0" in content, \
        "decompress_into_arc should assert that uncompressed_length > 0"


def test_readme_documents_compression_format():
    """README.md should document block compression format."""
    content = README.read_text()
    assert "#### Block Compression" in content or "Block Compression" in content, \
        "README should have Block Compression section"


def test_readme_explains_sentinel_value():
    """README.md should explain uncompressed_size=0 sentinel value."""
    content = README.read_text()
    assert "Header > 0" in content or "Header = 0" in content or \
           "header > 0" in content.lower() or "header = 0" in content.lower(), \
        "README should document header/sentinel mechanism (0 = uncompressed, >0 = compressed)"


def test_static_sorted_file_uses_arc_bytes():
    """StaticSortedFile should use ArcBytes instead of ArcSlice."""
    ssf = PERSISTENCE / "src" / "static_sorted_file.rs"
    content = ssf.read_text()
    assert "ArcBytes" in content, "static_sorted_file.rs should use ArcBytes"
    assert "use crate::arc_bytes::ArcBytes" in content or "ArcBytes" in content, \
        "Should import ArcBytes"


def test_block_weighter_handles_mmap():
    """BlockWeighter should handle mmap-backed blocks differently."""
    ssf = PERSISTENCE / "src" / "static_sorted_file.rs"
    content = ssf.read_text()
    assert "is_mmap_backed" in content, "BlockWeighter should check is_mmap_backed"
    assert "64" in content, "Mmap-backed blocks should have small fixed weight (64)"


def test_db_returns_arc_bytes():
    """Database get methods should return ArcBytes instead of ArcSlice."""
    db = PERSISTENCE / "src" / "db.rs"
    content = db.read_text()
    assert "use crate::arc_bytes::ArcBytes" in content or "ArcBytes" in content, \
        "db.rs should use ArcBytes"
    assert "Result<Option<ArcBytes>>" in content, \
        "get() and multi_get() should return ArcBytes"


def test_arc_bytes_file_exists():
    """arc_bytes.rs module file should exist."""
    arc_bytes = PERSISTENCE / "src" / "arc_bytes.rs"
    assert arc_bytes.exists(), "arc_bytes.rs should exist"


def test_arc_slice_file_removed():
    """arc_slice.rs module file should be removed (replaced by arc_bytes.rs)."""
    arc_slice = PERSISTENCE / "src" / "arc_slice.rs"
    assert not arc_slice.exists(), "arc_slice.rs should not exist (replaced by arc_bytes.rs)"
