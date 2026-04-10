"""
Task: workerd-add-feature-flags-to-jsg-rust
Repo: cloudflare/workerd @ d6046133f33e986f27c166556e9036efd2c1ec85
PR:   6281

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/workerd"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_rust_files_parse():
    """Modified Rust files must be syntactically valid (balanced braces/parens)."""
    # We can't run cargo check (needs full Bazel build), so validate basic structure
    # via subprocess: run a Python script that checks balanced delimiters in Rust files.
    validator_script = r'''
import sys
for path in sys.argv[1:]:
    with open(path) as f:
        content = f.read()
    stack = []
    pairs = {")": "(", "]": "[", "}": "{"}
    in_line_comment = False
    prev = ""
    for ch in content:
        if ch == "\n":
            in_line_comment = False
            prev = ch
            continue
        if in_line_comment:
            prev = ch
            continue
        if prev == "/" and ch == "/":
            in_line_comment = True
            prev = ch
            continue
        if ch in "({[":
            stack.append(ch)
        elif ch in ")}]":
            if not stack or stack[-1] != pairs[ch]:
                print(f"FAIL: unbalanced '{ch}' in {path}")
                sys.exit(1)
            stack.pop()
        prev = ch
    if stack:
        print(f"FAIL: unclosed delimiters in {path}: {stack}")
        sys.exit(1)
print("OK")
'''
    files = [
        f"{REPO}/src/rust/jsg/feature_flags.rs",
        f"{REPO}/src/rust/jsg/lib.rs",
    ]
    for f in files:
        assert Path(f).exists(), f"{f} does not exist"
    result = subprocess.run(
        ["python3", "-c", validator_script] + files,
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Rust file validation failed: {result.stdout}{result.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_feature_flags_module_exists():
    """feature_flags.rs must exist with FeatureFlags struct, from_bytes, and reader."""
    ff_path = Path(REPO) / "src" / "rust" / "jsg" / "feature_flags.rs"
    assert ff_path.exists(), "src/rust/jsg/feature_flags.rs must exist"
    content = ff_path.read_text()
    # Struct definition
    assert re.search(r"pub\s+struct\s+FeatureFlags", content), \
        "feature_flags.rs must define pub struct FeatureFlags"
    # from_bytes constructor
    assert re.search(r"fn\s+from_bytes\s*\(", content), \
        "FeatureFlags must have from_bytes constructor"
    # reader method returning compatibility_flags::Reader
    assert re.search(r"fn\s+reader\s*\(", content), \
        "FeatureFlags must have reader() method"
    # Must use capnp for deserialization
    assert "capnp" in content, "feature_flags.rs must use capnp crate"
    # Must have tests
    assert "#[cfg(test)]" in content, "feature_flags.rs must have unit tests"


# [pr_diff] fail_to_pass
def test_lock_has_feature_flags_method():
    """Lock must expose a public feature_flags() method returning a capnp Reader."""
    lib_path = Path(REPO) / "src" / "rust" / "jsg" / "lib.rs"
    content = lib_path.read_text()
    # Check pub fn feature_flags on Lock
    assert re.search(r"pub\s+fn\s+feature_flags\s*\(", content), \
        "lib.rs must define pub fn feature_flags() on Lock"
    # Return type should reference compatibility_flags
    assert "compatibility_flags" in content, \
        "feature_flags() return type must reference compatibility_flags"


# [pr_diff] fail_to_pass
def test_realm_stores_feature_flags():
    """Realm struct must have a feature_flags field and accept it in constructor."""
    lib_path = Path(REPO) / "src" / "rust" / "jsg" / "lib.rs"
    content = lib_path.read_text()
    # Realm struct should have feature_flags field
    assert re.search(r"feature_flags\s*:\s*FeatureFlags", content), \
        "Realm struct must have a feature_flags: FeatureFlags field"
    # realm_create must accept feature_flags_data parameter
    assert re.search(r"fn\s+realm_create\s*\([^)]*feature_flags", content), \
        "realm_create() must accept feature_flags_data parameter"


# [pr_diff] fail_to_pass
def test_realm_create_ffi_updated():
    """realm_create FFI bridge must declare the new feature_flags_data parameter."""
    lib_path = Path(REPO) / "src" / "rust" / "jsg" / "lib.rs"
    content = lib_path.read_text()
    # The CXX bridge declaration should have the new signature
    # Find the ffi module block and check realm_create has feature_flags_data
    ffi_match = re.search(r"mod\s+ffi\s*\{(.*?)\n\}", content, re.DOTALL)
    assert ffi_match, "lib.rs must have a mod ffi block"
    ffi_block = ffi_match.group(1)
    assert re.search(r"realm_create.*feature_flags", ffi_block, re.DOTALL), \
        "CXX bridge realm_create must include feature_flags_data parameter"


# [pr_diff] fail_to_pass
def test_cpp_passes_feature_flags():
    """C++ worker.c++ must canonicalize and pass feature flags to realm_create."""
    worker_path = Path(REPO) / "src" / "workerd" / "io" / "worker.c++"
    content = worker_path.read_text()
    assert "canonicalize" in content and "getFeatureFlags" in content, \
        "worker.c++ must canonicalize feature flags via capnp::canonicalize(api.getFeatureFlags())"
    # realm_create call must pass the serialized flags
    assert re.search(r"realm_create\s*\([^)]*featureFlags", content, re.DOTALL), \
        "realm_create call in worker.c++ must pass feature flags bytes"


# [pr_diff] fail_to_pass
def test_build_deps_include_capnp():
    """jsg BUILD.bazel must depend on compatibility-date capnp Rust bindings and capnp crate."""
    build_path = Path(REPO) / "src" / "rust" / "jsg" / "BUILD.bazel"
    content = build_path.read_text()
    assert "compatibility-date_capnp_rust" in content, \
        "jsg BUILD.bazel must depend on compatibility-date_capnp_rust"
    assert "capnp" in content, \
        "jsg BUILD.bazel must depend on capnp crate"


# ---------------------------------------------------------------------------
# Config/documentation update tests (agentmd-edit)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:9 @ d6046133f33e986f27c166556e9036efd2c1ec85
def test_agents_md_crate_table_updated():
    """src/rust/AGENTS.md crate table must list FeatureFlags for jsg crate."""
    agents_path = Path(REPO) / "src" / "rust" / "AGENTS.md"
    content = agents_path.read_text()
    # The jsg row in the crate table must now mention FeatureFlags
    # Find the line for jsg/ crate
    for line in content.splitlines():
        if "| `jsg/`" in line or "| jsg/" in line:
            assert "FeatureFlags" in line, \
                "AGENTS.md crate table jsg/ row must mention FeatureFlags"
            break
    else:
        raise AssertionError("AGENTS.md must have a jsg/ row in the crate table")


# [agent_config] fail_to_pass — AGENTS.md:9 @ d6046133f33e986f27c166556e9036efd2c1ec85
def test_agents_md_feature_flags_convention():
    """src/rust/AGENTS.md CONVENTIONS must document the feature flags pattern."""
    agents_path = Path(REPO) / "src" / "rust" / "AGENTS.md"
    content = agents_path.read_text().lower()
    assert "feature flag" in content or "feature_flags" in content, \
        "AGENTS.md must document the feature flags convention"
    assert "lock" in content and "feature_flags" in content, \
        "AGENTS.md convention must mention Lock::feature_flags()"


# [pr_diff] fail_to_pass
def test_jsg_readme_documents_feature_flags():
    """src/rust/jsg/README.md must have a Feature Flags section."""
    readme_path = Path(REPO) / "src" / "rust" / "jsg" / "README.md"
    content = readme_path.read_text()
    assert "Feature Flags" in content or "feature flags" in content.lower(), \
        "README.md must document Feature Flags"
    # Must document the key API: Lock::feature_flags()
    assert "feature_flags()" in content, \
        "README.md must document Lock::feature_flags() method"
    # Must mention realm_create takes feature_flags_data
    assert "feature_flags_data" in content, \
        "README.md must document realm_create's feature_flags_data parameter"


# [pr_diff] fail_to_pass
def test_jsg_readme_updated_ffi_example():
    """README.md FFI example must show realm_create with the new signature."""
    readme_path = Path(REPO) / "src" / "rust" / "jsg" / "README.md"
    content = readme_path.read_text()
    # The existing realm_create example must be updated to include feature_flags_data
    assert re.search(r"realm_create.*feature_flags", content, re.DOTALL), \
        "README.md realm_create example must show feature_flags_data parameter"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub + regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_feature_flags_not_stub():
    """feature_flags.rs FeatureFlags must have real logic, not just empty methods."""
    ff_path = Path(REPO) / "src" / "rust" / "jsg" / "feature_flags.rs"
    content = ff_path.read_text()
    # from_bytes must have assertions (validation logic)
    assert "assert!" in content, "from_bytes must validate input data"
    # reader must call get_root (actual deserialization)
    assert "get_root" in content, "reader() must call get_root for capnp deserialization"
    # Must have meaningful test coverage
    test_count = len(re.findall(r"#\[test\]", content))
    assert test_count >= 3, f"feature_flags.rs must have at least 3 unit tests, found {test_count}"


# [static] pass_to_pass
def test_lib_rs_module_declaration():
    """lib.rs must declare and re-export the feature_flags module."""
    lib_path = Path(REPO) / "src" / "rust" / "jsg" / "lib.rs"
    content = lib_path.read_text()
    assert "pub mod feature_flags;" in content, \
        "lib.rs must declare pub mod feature_flags"
    assert re.search(r"pub\s+use\s+feature_flags::FeatureFlags", content), \
        "lib.rs must re-export FeatureFlags"


# [repo_tests] pass_to_pass
def test_repo_rust_syntax_valid():
    """Modified Rust files have valid syntax (pass_to_pass)."""
    # Simpler check: verify braces are balanced
    validator = """
import sys
from pathlib import Path

files = [\"/workspace/workerd/src/rust/jsg/lib.rs\"]

for path in files:
    content = Path(path).read_text()
    brace_depth = 0
    for ch in content:
        if ch == \"{\":
            brace_depth += 1
        elif ch == \"}\":
            brace_depth -= 1
            if brace_depth < 0:
                print(f\"Unbalanced brace in {path}\")
                sys.exit(1)
    if brace_depth != 0:
        print(f\"Unclosed braces in {path}: depth {brace_depth}\")
        sys.exit(1)
    print(f\"OK: {path}\")

print(\"All Rust files valid\")
"""
    r = subprocess.run(
        ["python3", "-c", validator],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Rust syntax check failed: {r.stderr} {r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_no_trailing_whitespace():
    """Modified files have no trailing whitespace (pass_to_pass)."""
    files = [
        "src/rust/jsg/lib.rs",
        "src/rust/jsg/BUILD.bazel",
        "src/workerd/io/worker.c++",
        "src/rust/AGENTS.md",
        "src/rust/jsg/README.md",
    ]
    for f in files:
        path = Path(REPO) / f
        if not path.exists():
            continue
        r = subprocess.run(
            ["grep", "-n", "[[:space:]]$", str(path)],
            capture_output=True, text=True,
        )
        assert r.returncode != 0, f"Trailing whitespace found in {f}: {r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_no_crlf():
    """Modified files use Unix line endings (pass_to_pass)."""
    files = [
        "src/rust/jsg/lib.rs",
        "src/rust/jsg/BUILD.bazel",
        "src/rust/AGENTS.md",
        "src/rust/jsg/README.md",
    ]
    for f in files:
        path = Path(REPO) / f
        if not path.exists():
            continue
        content = path.read_bytes()
        if b"\r\n" in content:
            raise AssertionError(f"CRLF line endings found in {f}")


# [repo_tests] pass_to_pass
def test_repo_jsg_build_bazel_valid():
    """jsg BUILD.bazel has valid structure (pass_to_pass)."""
    # Check BUILD.bazel has proper structure
    build_path = Path(REPO) / "src" / "rust" / "jsg" / "BUILD.bazel"
    content = build_path.read_text()

    # Must have wd_rust_crate rule
    assert "wd_rust_crate(" in content, "BUILD.bazel must have wd_rust_crate rule"
    # Must have proper cxx_bridge
    assert "cxx_bridge" in content, "BUILD.bazel must reference cxx_bridge"
    # Check balanced parentheses
    open_count = content.count("(")
    close_count = content.count(")")
    assert open_count == close_count, f"Unbalanced parentheses: {open_count} vs {close_count}"
    # Check balanced brackets
    open_bracket = content.count("[")
    close_bracket = content.count("]")
    assert open_bracket == close_bracket, f"Unbalanced brackets: {open_bracket} vs {close_bracket}"
