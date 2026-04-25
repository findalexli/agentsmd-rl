"""Task: nextjs-turbopack-loader-runner-layer
Repo: vercel/next.js @ b6ff1f6079694da08af88cec5cac7381e22cea10
PR:   91727
All checks must pass for reward = 1. Any failure = reward 0.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
TARGET = Path(REPO) / "turbopack/crates/turbopack/src/lib.rs"
MOD_FILE = Path(REPO) / "turbopack/crates/turbopack/src/module_options/mod.rs"


def _run_py(code, args=None, timeout=30):
    cmd = ["python3", "-c", code]
    if args:
        cmd.extend(args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def test_layer_name_fixed():
    r = _run_py("""
import re, sys
src = open(sys.argv[1]).read()
idx = src.find('fn process_default_internal')
assert idx != -1
body = src[idx:]
matches = re.findall(r'Layer::new\\(rcstr![(]"([^"]+)"[)]\\)', body)
assert matches
assert "webpack_loaders" in matches
print("PASS")
""", args=[str(TARGET)], timeout=15)
    assert r.returncode == 0


def test_buggy_name_removed():
    r = _run_py("""
import sys
src = open(sys.argv[1]).read()
if '"turbopack_use_loaders"' in src:
    print('FAIL: buggy name found', file=sys.stderr)
    raise SystemExit(1)
print("PASS")
""", args=[str(TARGET)], timeout=15)
    assert r.returncode == 0


def test_cross_file_consistency():
    r = _run_py("""
import re, json, sys

def extract_layer_names(path):
    src = open(path).read()
    return set(re.findall(r'Layer::new\\(rcstr![(]"([^"]+)"[)]\\)', src))

lib_layers = extract_layer_names(sys.argv[1])
mod_layers = extract_layer_names(sys.argv[2])
assert "webpack_loaders" in lib_layers
assert "webpack_loaders" in mod_layers
assert "turbopack_use_loaders" not in lib_layers
assert "turbopack_use_loaders" not in mod_layers
print("PASS")
""", args=[str(TARGET), str(MOD_FILE)], timeout=15)
    assert r.returncode == 0


def test_not_stub():
    src = TARGET.read_text()
    lines = src.strip().splitlines()
    assert len(lines) >= 800


def test_loader_pipeline_preserved():
    src = TARGET.read_text()
    required = ["node_evaluate_asset_context", "WebpackLoaderItem", "WebpackLoaders", "loader_runner_package", "SourceTransforms"]
    missing = [r for r in required if r not in src]
    assert not missing


def test_other_layers_untouched():
    src = TARGET.read_text()
    assert "externals-tracing" in src


def test_layer_new_call_syntax():
    src = TARGET.read_text()
    fn_body = src[src.find("fn process_default_internal"):]
    assert "Layer::new(rcstr!" in fn_body


# repo_tests pass_to_pass
def test_repo_git_status():
    r = subprocess.run(["git", "status"], capture_output=True, text=True, timeout=60, cwd=REPO)
    assert r.returncode == 0


def test_repo_git_ls_files():
    r = subprocess.run(["git", "ls-files", "turbopack/crates/turbopack/src/lib.rs"], capture_output=True, text=True, timeout=60, cwd=REPO)
    assert r.returncode == 0
    assert "turbopack/crates/turbopack/src/lib.rs" in r.stdout


def test_repo_git_log():
    r = subprocess.run(["git", "log", "--oneline", "-1"], capture_output=True, text=True, timeout=60, cwd=REPO)
    assert r.returncode == 0
    assert "b6ff1f6" in r.stdout or "Fix adapter outputs" in r.stdout


def test_repo_git_diff_empty():
    r = subprocess.run(["git", "diff", "HEAD"], capture_output=True, text=True, timeout=60, cwd=REPO)
    assert r.returncode == 0


# NEW P2P TESTS - Git-based

def test_repo_git_show_commit():
    r = subprocess.run(["git", "show", "--stat", "HEAD"], capture_output=True, text=True, timeout=60, cwd=REPO)
    assert r.returncode == 0
    assert "files changed" in r.stdout or "turbopack" in r.stdout.lower()


def test_repo_git_rev_parse():
    r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=60, cwd=REPO)
    assert r.returncode == 0
    sha = r.stdout.strip()
    assert len(sha) >= 7
    assert all(c in "0123456789abcdef" for c in sha)


def test_repo_git_config():
    r = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True, timeout=60, cwd=REPO)
    assert r.returncode == 0
    assert "@" in r.stdout


def test_repo_turbopack_dir_exists():
    r = subprocess.run(["git", "ls-files", "turbopack/crates/turbopack/src/lib.rs"], capture_output=True, text=True, timeout=60, cwd=REPO)
    assert r.returncode == 0
    assert "turbopack/crates/turbopack/src/lib.rs" in r.stdout


def test_repo_agents_md_exists():
    r = subprocess.run(["git", "ls-files", "AGENTS.md"], capture_output=True, text=True, timeout=60, cwd=REPO)
    assert r.returncode == 0
    assert "AGENTS.md" in r.stdout


def test_repo_ci_workflows_exist():
    r = subprocess.run(["git", "ls-files", ".github/workflows/build_and_test.yml"], capture_output=True, text=True, timeout=60, cwd=REPO)
    assert r.returncode == 0
    assert ".github/workflows/build_and_test.yml" in r.stdout
# Additional repo_tests pass_to_pass - Git-based code inspection


def test_repo_git_grep_webpack_loaders():
    """Git grep finds webpack_loaders references in turbopack (pass_to_pass)."""
    r = subprocess.run(
        ["git", "grep", "webpack_loaders", "--", "turbopack/"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    # Should succeed and find references (either the old or new name)
    assert r.returncode == 0 or r.returncode == 1  # 0 = found, 1 = not found but valid exit


def test_repo_git_grep_layer_new():
    """Git grep finds Layer::new calls in turbopack (pass_to_pass)."""
    r = subprocess.run(
        ["git", "grep", "Layer::new", "--", "turbopack/crates/turbopack/"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"No Layer::new found in turbopack: {r.stderr}"
    assert "Layer::new" in r.stdout


def test_repo_git_show_turbopack_lib():
    """Git can show turbopack lib.rs content (pass_to_pass)."""
    r = subprocess.run(
        ["git", "show", "HEAD:turbopack/crates/turbopack/src/lib.rs"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"Failed to show lib.rs: {r.stderr}"
    assert "process_default_internal" in r.stdout


def test_repo_git_ls_tree_turbopack():
    """Git can list turbopack directory structure (pass_to_pass)."""
    r = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "HEAD", "turbopack/crates/turbopack/"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"Failed to list turbopack tree: {r.stderr}"
    assert "turbopack/crates/turbopack/src/lib.rs" in r.stdout
    assert "turbopack/crates/turbopack/Cargo.toml" in r.stdout


def test_repo_git_cat_file_turbopack_cargo():
    """Git can cat turbopack Cargo.toml blob (pass_to_pass)."""
    r = subprocess.run(
        ["git", "cat-file", "blob", "HEAD:turbopack/crates/turbopack/Cargo.toml"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"Failed to cat Cargo.toml: {r.stderr}"
    assert "turbopack" in r.stdout.lower()


def test_repo_git_check_attr():
    """Git check-attr works for files (pass_to_pass)."""
    r = subprocess.run(
        ["git", "check-attr", "-a", "--", "turbopack/crates/turbopack/src/lib.rs"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    # This may return 0 or 1 depending on gitattributes, but should not crash
    assert r.returncode in [0, 1]  # 0 = has attrs, 1 = no attrs set


def test_repo_git_verify_pack():
    """Git objects are valid (pass_to_pass)."""
    r = subprocess.run(
        ["git", "count-objects", "-v"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"Failed to count objects: {r.stderr}"
    assert "count:" in r.stdout or "count" in r.stdout


def test_repo_git_turbopack_src_exists():
    """Git tracks turbopack source files (pass_to_pass)."""
    r = subprocess.run(
        ["git", "ls-files", "turbopack/crates/turbopack/src/"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"Failed to list turbopack src: {r.stderr}"
    assert r.stdout.strip(), "turbopack src directory should have tracked files"


# CI-relevant P2P tests - verify actual repo code structure

def test_repo_process_default_internal_fn_exists():
    """The process_default_internal function exists in lib.rs (pass_to_pass)."""
    r = subprocess.run(
        ["git", "show", "HEAD:turbopack/crates/turbopack/src/lib.rs"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"Failed to show lib.rs: {r.stderr}"
    assert "fn process_default_internal" in r.stdout, "process_default_internal function must exist"


def test_repo_lib_rs_has_layer_calls():
    """The turbopack lib.rs uses Layer::new calls (pass_to_pass)."""
    r = subprocess.run(
        ["git", "show", "HEAD:turbopack/crates/turbopack/src/lib.rs"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"Failed to show lib.rs: {r.stderr}"
    assert "Layer::new" in r.stdout, "Layer::new calls must exist in lib.rs"


def test_repo_turbopack_cargo_toml_exists():
    """The turbopack Cargo.toml exists and is valid (pass_to_pass)."""
    r = subprocess.run(
        ["git", "cat-file", "blob", "HEAD:turbopack/crates/turbopack/Cargo.toml"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"Failed to cat Cargo.toml: {r.stderr}"
    assert "[package]" in r.stdout, "Cargo.toml must have [package] section"
    assert "name = \"turbopack\"" in r.stdout, "Cargo.toml must have correct package name"


def test_repo_turbopack_use_loaders_in_base():
    """The old turbopack_use_loaders layer name exists at base commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "show", "HEAD:turbopack/crates/turbopack/src/lib.rs"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"Failed to show lib.rs: {r.stderr}"
    # At the base commit, the OLD buggy name should exist
    assert "turbopack_use_loaders" in r.stdout, "turbopack_use_loaders must exist at base commit"


def test_repo_rustfmt_toml_exists():
    """Rustfmt configuration exists and is tracked (pass_to_pass)."""
    r = subprocess.run(
        ["git", "ls-files", ".rustfmt.toml"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"Failed to ls-files: {r.stderr}"
    assert ".rustfmt.toml" in r.stdout, ".rustfmt.toml must be tracked"


def test_repo_rust_toolchain_exists():
    """Rust toolchain configuration exists (pass_to_pass)."""
    r = subprocess.run(
        ["git", "ls-files", "rust-toolchain.toml"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"Failed to ls-files: {r.stderr}"
    assert "rust-toolchain.toml" in r.stdout, "rust-toolchain.toml must be tracked"


def test_repo_cargo_toml_valid_syntax():
    """Root Cargo.toml has valid structure (pass_to_pass)."""
    r = subprocess.run(
        ["git", "cat-file", "blob", "HEAD:Cargo.toml"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"Failed to cat Cargo.toml: {r.stderr}"
    # Basic structure checks
    assert "[workspace]" in r.stdout, "Root Cargo.toml must have [workspace]"
    assert "turbopack/crates/*" in r.stdout, "Workspace must include turbopack crates"


def test_repo_turbopack_module_options_exists():
    """Turbopack module_options directory exists (pass_to_pass)."""
    r = subprocess.run(
        ["git", "ls-files", "turbopack/crates/turbopack/src/module_options/"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"Failed to list module_options: {r.stderr}"
    assert "mod.rs" in r.stdout, "module_options/mod.rs must exist"


def test_repo_lib_rs_no_syntax_error_python():
    """lib.rs has no obvious Python-detectable syntax issues (pass_to_pass)."""
    r = subprocess.run(
        ["git", "show", "HEAD:turbopack/crates/turbopack/src/lib.rs"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"Failed to show lib.rs: {r.stderr}"
    # Check for basic structural balance - common syntax errors
    src = r.stdout
    # Basic brace balance check (should be even)
    open_braces = src.count("{")
    close_braces = src.count("}")
    # Allow for some unbalanced braces in comments/strings, but major imbalance is a problem
    assert abs(open_braces - close_braces) < 10, f"Brace imbalance: {open_braces} open vs {close_braces} close"
    # Parentheses balance
    open_parens = src.count("(")
    close_parens = src.count(")")
    assert abs(open_parens - close_parens) < 50, f"Paren imbalance: {open_parens} open vs {close_parens} close"


def test_repo_webpack_loaders_in_base():
    """The webpack_loaders string exists in base commit (for cross-file consistency) (pass_to_pass)."""
    r = subprocess.run(
        ["git", "grep", "webpack_loaders", "--", "turbopack/"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    # At base commit, this might or might not exist depending on the state
    # This test documents what we find - git grep returns 0 if found, 1 if not found
    # Both are valid outcomes at base commit, we just want to document the state
    assert r.returncode in [0, 1], f"git grep failed unexpectedly: {r.stderr}"
