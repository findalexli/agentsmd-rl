"""Test outputs for sui-analytics-indexer package cache migration."""

import subprocess
import sys
import os

REPO = "/workspace/sui"
CRATE_PATH = f"{REPO}/crates/sui-analytics-indexer"


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
