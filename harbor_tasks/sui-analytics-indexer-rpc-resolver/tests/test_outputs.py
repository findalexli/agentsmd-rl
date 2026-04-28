"""Test outputs for sui-analytics-indexer package cache migration."""

import subprocess
import sys
import os

import pytest

REPO = "/workspace/sui"
CRATE_PATH = f"{REPO}/crates/sui-analytics-indexer"


# ============================================================================
# Pass-to-Pass Tests - Repo CI Checks
# ============================================================================


def test_repo_format_check():
    """Repo code formatting passes (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "fmt", "--check"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Format check failed:\n{result.stderr.decode()[-500:]}"


def test_repo_license_headers():
    """Repo license headers are valid (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "xlint"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert result.returncode == 0, f"License check failed:\n{result.stderr.decode()[-500:]}"


def test_repo_git_checks():
    """Repo git checks pass (pass_to_pass)."""
    # Skip this test due to pre-existing bad filenames in the repo
    # (control_exp_autocomplete.ide~ and control_exp_autocomplete.move~)
    pytest.skip("Pre-existing bad filenames in repo - not related to this PR")


def test_repo_clippy():
    """Repo clippy lints pass (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "xclippy"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert result.returncode == 0, f"Clippy failed:\n{result.stderr.decode()[-500:]}"


def test_repo_cargo_check():
    """Repo compilation check for sui-analytics-indexer passes (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "check", "-p", "sui-analytics-indexer"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert result.returncode == 0, f"Cargo check failed:\n{result.stderr.decode()[-500:]}"




def test_repo_cargo_check_tests():
    """Repo cargo check --tests for sui-analytics-indexer passes (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "check", "-p", "sui-analytics-indexer", "--tests"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert result.returncode == 0, f"Cargo check --tests failed:\n{result.stderr.decode()[-500:]}"


def test_repo_cargo_manifest():
    """Repo Cargo.toml for sui-analytics-indexer is valid (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "read-manifest", "--manifest-path", f"{CRATE_PATH}/Cargo.toml"],
        cwd=REPO,
        capture_output=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Cargo read-manifest failed:\n{result.stderr.decode()[-500:]}"
    # Verify it'''s valid JSON and has expected fields
    import json
    manifest = json.loads(result.stdout.decode())
    assert manifest.get("name") == "sui-analytics-indexer", "Manifest should be for sui-analytics-indexer"

# ============================================================================
# Fail-to-Pass Tests - Task Requirements
# ============================================================================


def test_cargo_check_passes():
    """F2P: Verify the crate compiles successfully after migration."""
    result = subprocess.run(
        ["cargo", "check", "-p", "sui-analytics-indexer"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert result.returncode == 0, f"cargo check failed:\n{result.stderr.decode()}"


def test_system_package_eviction_module_exists():
    """F2P: Verify the new SystemPackageEviction handler module exists."""
    module_path = f"{CRATE_PATH}/src/handlers/system_package_eviction.rs"
    assert os.path.exists(module_path), f"Module not found: {module_path}"

    with open(module_path, "r") as f:
        content = f.read()

    # Verify key components exist
    assert "pub struct SystemPackageEviction" in content, "SystemPackageEviction struct not found"
    assert "impl Processor for SystemPackageEviction" in content, "Processor trait impl not found"
    assert "impl sequential::Handler for SystemPackageEviction" in content, "Handler trait impl not found"
    assert "PackageStoreWithLruCache<RpcPackageStore>" in content, "PackageStoreWithLruCache type not found"
    assert "evict(SYSTEM_PACKAGE_ADDRESSES" in content, "Cache eviction logic not found"


def test_old_package_cache_removed():
    """F2P: Verify the old PackageCache module is removed."""
    old_module_path = f"{CRATE_PATH}/src/package_store/mod.rs"
    assert not os.path.exists(old_module_path), f"Old module should be removed: {old_module_path}"


def test_package_store_not_in_lib():
    """F2P: Verify package_store is no longer declared in lib.rs."""
    lib_path = f"{CRATE_PATH}/src/lib.rs"
    with open(lib_path, "r") as f:
        content = f.read()

    assert "pub mod package_store" not in content, "package_store should not be in lib.rs"


def test_handlers_use_new_resolver():
    """F2P: Verify handlers use PackageStoreWithLruCache instead of PackageCache."""
    handlers = ["df.rs", "event.rs", "object.rs", "wrapped_object.rs"]

    for handler in handlers:
        handler_path = f"{CRATE_PATH}/src/handlers/tables/{handler}"
        with open(handler_path, "r") as f:
            content = f.read()

        # Should use new resolver types
        assert "PackageStoreWithLruCache<RpcPackageStore>" in content, \
            f"{handler}: Should use PackageStoreWithLruCache<RpcPackageStore>"

        # Should NOT use old PackageCache
        assert "PackageCache" not in content, \
            f"{handler}: Should not reference old PackageCache"


def test_object_processor_has_rpc_client():
    """F2P: Verify ObjectProcessor has the new rpc_client field."""
    object_path = f"{CRATE_PATH}/src/handlers/tables/object.rs"
    with open(object_path, "r") as f:
        content = f.read()

    assert "rpc_client: Client" in content, "ObjectProcessor should have rpc_client field"
    assert "get_original_package_id" in content, "ObjectProcessor should have get_original_package_id method"


def test_cargo_toml_dependencies_updated():
    """F2P: Verify Cargo.toml has correct dependencies."""
    cargo_toml_path = f"{CRATE_PATH}/Cargo.toml"
    with open(cargo_toml_path, "r") as f:
        content = f.read()

    # Should have new dependency
    assert "sui-rpc-resolver" in content, "Cargo.toml should include sui-rpc-resolver"

    # Should NOT have old dependencies
    assert "lru" not in content, "Cargo.toml should not include lru dependency"
    assert "typed-store" not in content, "Cargo.toml should not include typed-store dependency"
    assert "tempfile" not in content, "Cargo.toml should not include tempfile dependency"


def test_indexer_uses_rpc_package_store():
    """F2P: Verify indexer.rs uses RpcPackageStore with cache."""
    indexer_path = f"{CRATE_PATH}/src/indexer.rs"
    with open(indexer_path, "r") as f:
        content = f.read()

    # Should use new package store
    assert "RpcPackageStore::new" in content, "indexer.rs should use RpcPackageStore::new"
    assert ".with_cache()" in content, "indexer.rs should call .with_cache()"

    # Should NOT use old PackageCache
    assert "PackageCache::new" not in content, "indexer.rs should not use PackageCache::new"

    # Should register SystemPackageEviction
    assert "SystemPackageEviction::new" in content, "indexer.rs should register SystemPackageEviction"


def test_pipeline_signature_updated():
    """F2P: Verify pipeline.rs has updated function signature."""
    pipeline_path = f"{CRATE_PATH}/src/pipeline.rs"
    with open(pipeline_path, "r") as f:
        content = f.read()

    # Should have updated function signature with rpc_url parameter
    assert "rpc_url: &str" in content, "pipeline.rs should have rpc_url parameter"

    # Should pass rpc_url to ObjectProcessor::new
    assert "ObjectProcessor::new(\n                        package_cache.clone(),\n                        rpc_url," in content, \
        "pipeline.rs should pass rpc_url to ObjectProcessor"


if __name__ == "__main__":
    pytest_main = ["-v", __file__]
    if len(sys.argv) > 1:
        pytest_main.insert(1, "-k")
        pytest_main.insert(2, sys.argv[1])
    subprocess.run(["python3", "-m", "pytest"] + pytest_main)

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_license_check_run_license_check():
    """pass_to_pass | CI job 'license-check' → step 'Run license check'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo xlint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run license check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_windows_cli_tests_cargo_test():
    """pass_to_pass | CI job 'windows-cli-tests' → step 'cargo test'"""
    r = subprocess.run(
        ["bash", "-lc", "cargo nextest run --profile ci --cargo-quiet -E '!package(sui-bridge) and !package(sui-bridge-indexer)'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'cargo test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_windows_build_cargo_build():
    """pass_to_pass | CI job 'windows-build' → step 'cargo build'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo build --all-features'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'cargo build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_tree_sitter___run_tests_run_tests_sh():
    """pass_to_pass | CI job 'Tree Sitter - run tests' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", './run-tests.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_move_formatter___run_tests_npm():
    """pass_to_pass | CI job 'Move Formatter - run tests' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm i && npm test'], cwd=os.path.join(REPO, 'external-crates/move/tooling/prettier-move'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_move_formatter___check_formatt_npx():
    """pass_to_pass | CI job 'Move Formatter - check formatting' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npx prettier-move -c **/*.move'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_external_crates_test_external_crates_tests():
    """pass_to_pass | CI job 'external-crates-test' → step 'External crates tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo xtest'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'External crates tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint__build__and_test_build():
    """pass_to_pass | CI job 'Lint, Build, and Test' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=os.path.join(REPO, './docs/site'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_docs_run_afdocs_check():
    """pass_to_pass | CI job 'check-docs' → step 'Run afdocs check'"""
    r = subprocess.run(
        ["bash", "-lc", 'OUTPUT=$(npx --yes afdocs@0.6.0 check "$URL" --max-links 1000 2>&1) || true\necho "result<<EOF" >> $GITHUB_OUTPUT\necho "$OUTPUT" >> $GITHUB_OUTPUT\necho "EOF" >> $GITHUB_OUTPUT'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run afdocs check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")