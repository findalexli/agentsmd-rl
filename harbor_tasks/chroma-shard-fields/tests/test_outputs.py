"""Tests for PR 6810: Add shard_index, num_shards and log_upper_bound_offset fields."""

import subprocess
import sys
import os

REPO = "/workspace/chroma"
RUST_TYPES_PATH = f"{REPO}/rust/types/src/execution/operator.rs"
PROTO_PATH = f"{REPO}/idl/chromadb/proto/query_executor.proto"


def test_scan_struct_has_shard_fields():
    """Verify Scan struct has all three new fields: shard_index, num_shards, log_upper_bound_offset."""
    with open(RUST_TYPES_PATH, "r") as f:
        content = f.read()

    # Check for struct definition and the new fields
    assert "pub struct Scan" in content, "Scan struct not found"
    assert "pub shard_index: u32" in content, "shard_index field missing or incorrect type"
    assert "pub num_shards: u32" in content, "num_shards field missing or incorrect type"
    assert "pub log_upper_bound_offset: i64" in content, "log_upper_bound_offset field missing or incorrect type"


def test_scan_operator_proto_has_fields():
    """Verify ScanOperator protobuf message has all three new fields."""
    with open(PROTO_PATH, "r") as f:
        content = f.read()

    # Check for the fields in the proto message with correct types and field numbers
    assert "uint32 shard_index = 8" in content, "shard_index field missing or incorrect"
    assert "uint32 num_shards = 9" in content, "num_shards field missing or incorrect"
    assert "int64 log_upper_bound_offset = 10" in content, "log_upper_bound_offset field missing or incorrect"


def test_scan_try_from_proto_conversion():
    """Verify TryFrom<ScanOperator> for Scan correctly converts all new fields."""
    with open(RUST_TYPES_PATH, "r") as f:
        content = f.read()

    # Check that try_from implementation sets the fields from proto values
    assert "shard_index: value.shard_index" in content, "shard_index not mapped from proto"
    assert "log_upper_bound_offset: value.log_upper_bound_offset" in content, "log_upper_bound_offset not mapped from proto"

    # Check num_shards handling (should use max(1, value) for backward compatibility)
    assert "let num_shards = value.num_shards.max(1)" in content, "num_shards backward compatibility handling missing"
    assert "num_shards," in content, "num_shards field not set in TryFrom result"


def test_scan_try_into_proto_conversion():
    """Verify TryFrom<Scan> for chroma_proto::ScanOperator correctly converts all new fields."""
    with open(RUST_TYPES_PATH, "r") as f:
        content = f.read()

    # Find the TryFrom<Scan> for chroma_proto::ScanOperator impl block
    impl_start = content.find("impl TryFrom<Scan> for chroma_proto::ScanOperator")
    assert impl_start != -1, "TryFrom<Scan> for ScanOperator implementation not found"

    # Get the implementation block content (simplified extraction)
    impl_content = content[impl_start:impl_start + 2000]

    assert "shard_index: value.shard_index" in impl_content, "shard_index not mapped to proto"
    assert "num_shards: value.num_shards" in impl_content, "num_shards not mapped to proto"
    assert "log_upper_bound_offset: value.log_upper_bound_offset" in impl_content, "log_upper_bound_offset not mapped to proto"


def test_num_shards_backward_compatibility():
    """Verify num_shards defaults to 1 when proto field is 0 (backward compatibility)."""
    with open(RUST_TYPES_PATH, "r") as f:
        content = f.read()

    # The key logic: num_shards = value.num_shards.max(1)
    # This ensures 0 becomes 1, and any other value stays as-is
    assert "value.num_shards.max(1)" in content, "Backward compatibility logic for num_shards not found"


def test_code_compiles():
    """Verify Rust code compiles successfully."""
    result = subprocess.run(
        ["cargo", "check", "-p", "chroma-types"],
        cwd=f"{REPO}/rust",
        capture_output=True,
        timeout=180
    )

    if result.returncode != 0:
        stderr = result.stderr.decode()
        # Only fail for actual compilation errors, not warnings
        if "error" in stderr.lower():
            raise AssertionError(f"Code failed to compile:\n{stderr}")

    assert result.returncode == 0, f"Compilation failed with return code {result.returncode}"


def test_repo_cargo_check():
    """Repo's cargo check passes for chroma-types (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "chroma-types"],
        cwd=f"{REPO}",
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"Cargo check failed:\n{r.stderr[-1000:]}"


def test_repo_cargo_clippy():
    """Repo's cargo clippy passes for chroma-types (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "chroma-types", "--", "-D", "warnings"],
        cwd=f"{REPO}",
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"Cargo clippy failed:\n{r.stderr[-1000:]}"


def test_repo_cargo_test_types():
    """Repo's cargo test passes for chroma-types library (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "chroma-types", "--lib", "--", "--test-threads=1"],
        cwd=f"{REPO}",
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"Cargo test failed:\n{r.stderr[-1000:]}"


def test_repo_cargo_fmt():
    """Repo's cargo fmt check passes for chroma-types (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "-p", "chroma-types", "--", "--check"],
        cwd=f"{REPO}",
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Cargo fmt check failed:\n{r.stderr[-500:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
