"""
Task: next.js-turbopersistence-add-crc32-block-checksums
Repo: next.js @ 82db94494ad41bec61b97ff7a95a6707745a3434
PR:   90754

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

def test_checksum_crate_dependency():
    """crc32fast must be added as a dependency for CRC32 computation."""
    workspace_toml = Path(f"{REPO}/Cargo.toml").read_text()
    crate_toml = Path(f"{CRATE}/Cargo.toml").read_text()
    assert "crc32fast" in workspace_toml, \
        "crc32fast must be in workspace dependencies"
    assert "crc32fast" in crate_toml, \
        "crc32fast must be in turbo-persistence dependencies"


def test_checksum_computation_added():
    """CRC32 checksum computation must be added to the crate."""
    src_dir = Path(f"{CRATE}/src")
    all_rs = "\n".join(f.read_text() for f in sorted(src_dir.rglob("*.rs")))

    assert "crc32fast" in all_rs, \
        "crc32fast must be used for CRC32 computation in the source"
    assert re.search(r"fn\s+\w*checksum\w*", all_rs) or "crc32fast::hash" in all_rs, \
        "A checksum computation function must be defined"


def test_block_header_includes_checksum():
    """Block header must be expanded to 8 bytes (4B length + 4B checksum)."""
    builder_rs = Path(f"{CRATE}/src/static_sorted_file_builder.rs").read_text()

    match = re.search(r"BLOCK_HEADER_SIZE\s*:\s*usize\s*=\s*(\d+)", builder_rs)
    assert match is not None, "BLOCK_HEADER_SIZE constant must be defined"
    assert match.group(1) == "8", \
        f"BLOCK_HEADER_SIZE must be 8 (4B length + 4B checksum), got {match.group(1)}"


def test_read_path_verifies_checksum():
    """Read path must verify CRC32 checksums and detect corruption."""
    ssf_rs = Path(f"{CRATE}/src/static_sorted_file.rs").read_text()
    ssf_lower = ssf_rs.lower()

    assert "checksum" in ssf_lower, \
        "static_sorted_file.rs must include checksum verification logic"
    assert "corruption" in ssf_lower or "mismatch" in ssf_lower, \
        "Read path must report corruption when checksum doesn't match"
    assert "BLOCK_HEADER_SIZE" in ssf_rs or "block_start + 8" in ssf_rs, \
        "Read path must account for the expanded 8-byte block header"


def test_blob_file_checksum():
    """Blob file write and read must include CRC32 checksum verification."""
    write_batch_rs = Path(f"{CRATE}/src/write_batch.rs").read_text()
    db_rs = Path(f"{CRATE}/src/db.rs").read_text()

    assert "checksum" in write_batch_rs.lower() or "crc32" in write_batch_rs.lower(), \
        "Blob write path must compute a checksum"
    assert "checksum" in db_rs.lower() or "crc32" in db_rs.lower(), \
        "Blob read path must verify checksum"
    assert "corruption" in db_rs.lower() or "mismatch" in db_rs.lower(), \
        "Blob read must detect and report corruption"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression tests
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — README documentation updates
# ---------------------------------------------------------------------------


    assert "checksum" in readme_lower or "crc32" in readme_lower, \
        "README must document the CRC32 checksum feature"
    assert "checksum" in readme_lower and "block" in readme_lower, \
        "README must describe checksums as part of the block format"
    assert re.search(r"4\s*bytes?\s+.*checksum", readme_lower) or \
           re.search(r"checksum.*4\s*bytes?", readme_lower), \
        "README should document the 4-byte checksum field in block headers"



    blob_idx = readme_lower.find("blob file")
    assert blob_idx != -1, "README must have a blob file section"
    blob_section = readme_lower[blob_idx:blob_idx + 800]

    assert "checksum" in blob_section or "crc32" in blob_section, \
        "Blob file section must document the checksum in the header"
    assert "header" in blob_section or "bytes" in blob_section, \
        "Blob section should describe the structured header format"
