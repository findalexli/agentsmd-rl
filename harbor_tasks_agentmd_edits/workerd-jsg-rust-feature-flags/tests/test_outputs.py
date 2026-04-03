"""
Task: workerd-jsg-rust-feature-flags
Repo: cloudflare/workerd @ d6046133f33e986f27c166556e9036efd2c1ec85
PR:   6281

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/workerd"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_feature_flags_module_exists():
    """feature_flags.rs must exist with FeatureFlags struct and from_bytes constructor."""
    ff_rs = Path(REPO) / "src" / "rust" / "jsg" / "feature_flags.rs"
    assert ff_rs.exists(), "src/rust/jsg/feature_flags.rs must exist"
    content = ff_rs.read_text()
    assert "pub struct FeatureFlags" in content, \
        "feature_flags.rs must define a public FeatureFlags struct"
    assert "fn from_bytes" in content, \
        "FeatureFlags must have a from_bytes constructor"
    assert "fn reader" in content, \
        "FeatureFlags must have a reader() method"


# [pr_diff] fail_to_pass
def test_lib_exports_feature_flags():
    """lib.rs must declare the feature_flags module and re-export FeatureFlags."""
    lib_rs = Path(REPO) / "src" / "rust" / "jsg" / "lib.rs"
    content = lib_rs.read_text()
    assert "pub mod feature_flags" in content, \
        "lib.rs must declare 'pub mod feature_flags'"
    assert "pub use feature_flags::FeatureFlags" in content, \
        "lib.rs must re-export FeatureFlags"


# [pr_diff] fail_to_pass
def test_realm_create_accepts_feature_flags():
    """realm_create FFI function must accept feature_flags_data parameter."""
    lib_rs = Path(REPO) / "src" / "rust" / "jsg" / "lib.rs"
    content = lib_rs.read_text()
    # The CXX bridge declaration and the impl must both accept feature flags data
    assert "feature_flags_data" in content, \
        "realm_create must accept a feature_flags_data parameter"
    # Verify it's a byte slice parameter
    assert re.search(r"fn realm_create\(.*feature_flags_data:\s*&\[u8\]", content, re.DOTALL), \
        "realm_create must accept feature_flags_data as &[u8]"


# [pr_diff] fail_to_pass
def test_lock_has_feature_flags_method():
    """Lock must expose a feature_flags() method returning the capnp reader."""
    lib_rs = Path(REPO) / "src" / "rust" / "jsg" / "lib.rs"
    content = lib_rs.read_text()
    assert re.search(r"pub fn feature_flags\(", content), \
        "Lock must have a pub fn feature_flags() method"
    assert "compatibility_flags::Reader" in content, \
        "feature_flags() must return a compatibility_flags::Reader"


# [pr_diff] fail_to_pass
def test_realm_stores_feature_flags():
    """Realm struct must have a feature_flags field of type FeatureFlags."""
    lib_rs = Path(REPO) / "src" / "rust" / "jsg" / "lib.rs"
    content = lib_rs.read_text()
    # Check the Realm struct has a feature_flags field
    assert re.search(r"struct Realm\s*\{[^}]*feature_flags:\s*FeatureFlags", content, re.DOTALL), \
        "Realm struct must contain a feature_flags: FeatureFlags field"


# [pr_diff] fail_to_pass
def test_worker_cpp_passes_feature_flags():
    """C++ worker initialization must canonicalize and pass feature flags to realm_create."""
    worker_cpp = Path(REPO) / "src" / "workerd" / "io" / "worker.c++"
    content = worker_cpp.read_text()
    assert "canonicalize" in content and "getFeatureFlags" in content, \
        "worker.c++ must canonicalize feature flags from api.getFeatureFlags()"
    assert re.search(r"realm_create\([^)]*featureFlags", content, re.DOTALL), \
        "worker.c++ must pass feature flags bytes to realm_create()"


# [pr_diff] fail_to_pass
def test_build_bazel_has_capnp_deps():
    """jsg BUILD.bazel must depend on compatibility-date capnp and capnp crate."""
    build = Path(REPO) / "src" / "rust" / "jsg" / "BUILD.bazel"
    content = build.read_text()
    assert "compatibility-date_capnp_rust" in content, \
        "jsg BUILD.bazel must depend on compatibility-date_capnp_rust"
    assert "capnp" in content, \
        "jsg BUILD.bazel must depend on the capnp crate"


# ---------------------------------------------------------------------------
# Config/doc update tests (config_edit) — REQUIRED for agentmd-edit
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_feature_flags_not_stub():
    """feature_flags.rs must have real implementation, not just struct definition."""
    ff_rs = Path(REPO) / "src" / "rust" / "jsg" / "feature_flags.rs"
    content = ff_rs.read_text()
    # Must import capnp
    assert "capnp" in content, "feature_flags.rs must use the capnp crate"
    # from_bytes must have assertion logic
    assert "assert!" in content or "assert_eq!" in content, \
        "from_bytes must validate input data"
    # Must store the parsed message
    assert "message" in content and "Reader" in content, \
        "FeatureFlags must store a capnp message Reader"
    # Must have tests
    assert "#[cfg(test)]" in content, \
        "feature_flags.rs should include unit tests"


# [agent_config] pass_to_pass
