"""
Test outputs for chroma-core/chroma#6768
Re-export ReadLevel for rust client
"""
import subprocess
import sys
import os

REPO = "/workspace/chroma"
RUST_CHROMA = f"{REPO}/rust/chroma"


def test_readlevel_re_exported_in_types():
    """
    Fail-to-pass: ReadLevel must be re-exported from chroma::types module.
    This test verifies that the re-export statement exists and is syntactically correct.
    """
    types_file = f"{RUST_CHROMA}/src/types.rs"
    with open(types_file, 'r') as f:
        content = f.read()

    # Check that ReadLevel is re-exported from chroma_types::plan
    assert "pub use chroma_types::plan::ReadLevel;" in content,         "ReadLevel is not re-exported in types.rs - expected 'pub use chroma_types::plan::ReadLevel;'"


def test_readlevel_publicly_accessible():
    """
    Fail-to-pass: ReadLevel must be accessible via chroma::types::ReadLevel.
    This verifies the Rust module system properly exposes the type.
    """
    # Create a test file that imports ReadLevel from chroma::types
    test_code = '''
use chroma::types::ReadLevel;

fn main() {
    // Verify we can access the enum variants
    let _ = ReadLevel::default();
}
'''
    test_file = f"{RUST_CHROMA}/examples/test_readlevel.rs"
    os.makedirs(os.path.dirname(test_file), exist_ok=True)

    with open(test_file, 'w') as f:
        f.write(test_code)

    try:
        # Try to check/compile the test program
        result = subprocess.run(
            ["cargo", "check", "--example", "test_readlevel"],
            cwd=RUST_CHROMA,
            capture_output=True,
            text=True,
            timeout=120
        )

        # Clean up
        os.remove(test_file)

        assert result.returncode == 0,             f"ReadLevel is not accessible via chroma::types::ReadLevel:\n{result.stderr}"
    finally:
        # Ensure cleanup happens even on timeout/assertion error
        if os.path.exists(test_file):
            os.remove(test_file)


def test_collection_docs_use_correct_import():
    """
    Pass-to-pass: Documentation in collection.rs must use chroma::types::ReadLevel.
    The doc examples should reference the re-exported path, not the internal path.
    """
    collection_file = f"{RUST_CHROMA}/src/collection.rs"
    with open(collection_file, 'r') as f:
        content = f.read()

    # The doc examples should use the re-exported path
    # They should NOT use chroma_types::plan::ReadLevel in examples
    # Count both direct imports and grouped imports that include ReadLevel from chroma::types
    direct_count = content.count("use chroma::types::ReadLevel")
    grouped_count = content.count("chroma::types::{SearchPayload, ReadLevel}")
    import_count = direct_count + grouped_count
    wrong_import_count = content.count("use chroma_types::plan::ReadLevel")

    # After fix, we expect chroma::types::ReadLevel in doc examples
    assert import_count >= 2,         f"Doc examples should use 'use chroma::types::ReadLevel' at least twice, found {import_count} (direct: {direct_count}, grouped: {grouped_count})"

    # The old import should not appear in the examples anymore
    assert wrong_import_count == 0,         f"Doc examples should NOT use 'use chroma_types::plan::ReadLevel', found {wrong_import_count} occurrences"


def test_rust_compiles_cleanly():
    """
    Pass-to-pass: The rust/chroma crate must compile without errors.
    This ensures the re-export doesn't break any existing code.
    """
    result = subprocess.run(
        ["cargo", "check"],
        cwd=RUST_CHROMA,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0,         f"Rust compilation failed:\n{result.stderr}"


def test_all_re_exports_present():
    """
    Pass-to-pass: Verify all expected re-exports are present in types.rs.
    This is a structural check to ensure the file maintains its expected exports.
    """
    types_file = f"{RUST_CHROMA}/src/types.rs"
    with open(types_file, 'r') as f:
        content = f.read()

    expected_exports = [
        "pub use chroma_types::plan::ReadLevel;",
        "pub use chroma_types::plan::SearchPayload;",
    ]

    for export in expected_exports:
        assert export in content, f"Expected re-export not found: {export}"


def test_cargo_fmt():
    """
    Pass-to-pass: Repo Rust code must be properly formatted.
    Runs cargo fmt --check to verify formatting follows Rust style guidelines.
    """
    result = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0,         f"Rust formatting check failed:\n{result.stderr or result.stdout}"


def test_cargo_metadata():
    """
    Pass-to-pass: Repo Cargo.toml files must be valid.
    Runs cargo metadata to verify workspace configuration is valid.
    """
    result = subprocess.run(
        ["cargo", "metadata", "--format-version", "1"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0,         f"Cargo metadata check failed (invalid Cargo.toml):\n{result.stderr[-500:]}"


def test_chroma_crate_clippy():
    """
    Pass-to-pass: Repo chroma crate must pass clippy lints.
    Runs cargo clippy --package chroma to verify no lint warnings.
    """
    result = subprocess.run(
        ["cargo", "clippy", "--package", "chroma", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0,         f"Clippy check failed for chroma crate:\n{result.stderr[-500:]}"


def test_chroma_crate_doc():
    """
    Pass-to-pass: Repo chroma crate documentation must build.
    Runs cargo doc to verify documentation compiles without errors.
    """
    result = subprocess.run(
        ["cargo", "doc", "--package", "chroma", "--no-deps"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0,         f"Documentation build failed for chroma crate:\n{result.stderr[-500:]}"


def test_cargo_doc_test():
    """
    Pass-to-pass: Rust doctests must pass.
    Runs cargo test --doc to verify code examples in documentation work.
    This is from the repo's CI (_rust-tests.yml).
    """
    result = subprocess.run(
        ["cargo", "test", "--doc", "--package", "chroma"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, f"Rust doctest failed:\n{result.stderr[-500:]}"

def test_cargo_unit_tests():
    """
    Pass-to-pass: Repo chroma crate unit tests pass.
    Runs cargo test on the chroma crate library code, skipping k8s integration tests
    that fail outside of the Tilt environment.
    """
    result = subprocess.run(
        ["cargo", "test", "--package", "chroma", "--lib", "--", "--skip", "k8s_integration"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )

    assert result.returncode == 0, \
        f"Unit tests failed for chroma crate:\n{result.stderr[-500:]}"
