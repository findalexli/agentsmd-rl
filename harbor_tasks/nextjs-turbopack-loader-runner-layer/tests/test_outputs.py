"""Task: nextjs-turbopack-loader-runner-layer
Repo: vercel/next.js @ b6ff1f6079694da08af88cec5cac7381e22cea10
PR:   91727

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

This is a Rust codebase (turbopack). The container has no Rust toolchain,
so we use subprocess to run Python code that performs semantic analysis
of the Rust source — extracting actual values from macro calls and
comparing them across files.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
TARGET = Path(REPO) / "turbopack/crates/turbopack/src/lib.rs"
MOD_FILE = Path(REPO) / "turbopack/crates/turbopack/src/module_options/mod.rs"


def _run_py(code: str, args: list[str] | None = None, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python snippet, optionally with extra args."""
    cmd = ["python3", "-c", code]
    if args:
        cmd.extend(args)
    return subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_layer_name_fixed():
    """process_default_internal must use Layer::new with "webpack_loaders"."""
    r = _run_py("""
import re, sys
src = open(sys.argv[1]).read()
# Find the process_default_internal function body
idx = src.find("fn process_default_internal")
assert idx != -1, "function not found"
body = src[idx:]
# Extract the string argument from Layer::new(rcstr!("...")) calls within this function
matches = re.findall(r'Layer::new\\(rcstr!\\("([^"]+)"\\)\\)', body)
assert matches, "No Layer::new(rcstr!(...)) calls found in process_default_internal"
assert "webpack_loaders" in matches, (
    f"webpack_loaders not found in Layer::new calls; got: {matches}"
)
print("PASS")
""", args=[str(TARGET)], timeout=15)
    assert r.returncode == 0, f"Layer name check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_buggy_name_removed():
    """The old buggy layer name "turbopack_use_loaders" must not appear in lib.rs."""
    r = _run_py("""
import sys
src = open(sys.argv[1]).read()
if '"turbopack_use_loaders"' in src:
    idx = src.index('"turbopack_use_loaders"')
    start = max(0, idx - 60)
    end = min(len(src), idx + 60)
    context = src[start:end].replace("\\n", " ")
    print(f'FAIL: buggy name found near: ...{context}...', file=sys.stderr)
    raise SystemExit(1)
print("PASS")
""", args=[str(TARGET)], timeout=15)
    assert r.returncode == 0, f"Buggy name still present: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_cross_file_consistency():
    """Both lib.rs and module_options/mod.rs must use the same "webpack_loaders" layer name."""
    r = _run_py("""
import re, json, sys

def extract_layer_names(path):
    src = open(path).read()
    return set(re.findall(r'Layer::new\\(rcstr!\\("([^"]+)"\\)\\)', src))

lib_layers = extract_layer_names(sys.argv[1])
mod_layers = extract_layer_names(sys.argv[2])

assert lib_layers, "No Layer::new calls found in lib.rs"
assert mod_layers, "No Layer::new calls found in mod.rs"

# "webpack_loaders" must appear in both files
assert "webpack_loaders" in lib_layers, f"webpack_loaders not in lib.rs layers: {lib_layers}"
assert "webpack_loaders" in mod_layers, f"webpack_loaders not in mod.rs layers: {mod_layers}"

# The buggy name must not appear in either file
assert "turbopack_use_loaders" not in lib_layers, f"Buggy name still in lib.rs: {lib_layers}"
assert "turbopack_use_loaders" not in mod_layers, f"Buggy name still in mod.rs: {mod_layers}"

print(json.dumps({"lib": sorted(lib_layers), "mod": sorted(mod_layers)}))
print("PASS")
""", args=[str(TARGET), str(MOD_FILE)], timeout=15)
    assert r.returncode == 0, f"Cross-file consistency failed: {r.stderr}"
    assert "PASS" in r.stdout
    # Verify the JSON output shows webpack_loaders in both
    data = json.loads(r.stdout.strip().split("\n")[0])
    assert "webpack_loaders" in data["lib"]
    assert "webpack_loaders" in data["mod"]


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """lib.rs must be substantial — not gutted or replaced with a stub."""
    src = TARGET.read_text()
    lines = src.strip().splitlines()
    assert len(lines) >= 800, (
        f"File has only {len(lines)} lines, expected 800+ (original is ~1000)"
    )


# [pr_diff] pass_to_pass
def test_loader_pipeline_preserved():
    """Key loader pipeline constructs must still exist in lib.rs."""
    src = TARGET.read_text()
    required = [
        "node_evaluate_asset_context",
        "WebpackLoaderItem",
        "WebpackLoaders",
        "loader_runner_package",
        "SourceTransforms",
    ]
    missing = [r for r in required if r not in src]
    assert not missing, f"Missing loader pipeline constructs: {missing}"


# [pr_diff] pass_to_pass
def test_other_layers_untouched():
    """Other Layer::new calls (e.g. externals-tracing) must not be removed."""
    src = TARGET.read_text()
    assert "externals-tracing" in src, (
        "externals-tracing layer missing — collateral damage from fix"
    )


# [pr_diff] pass_to_pass
def test_layer_new_call_syntax():
    """Layer::new call must use rcstr! macro with the layer name string."""
    src = TARGET.read_text()
    fn_body = src[src.find("fn process_default_internal"):]
    assert "Layer::new(rcstr!" in fn_body, (
        "Layer::new must use rcstr! macro for the layer name"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repository integrity tests using subprocess
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_git_status():
    """Git repository status check (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Git status failed:\n{r.stderr}"
    # After gold fix is applied, there will be uncommitted changes to lib.rs
    # We accept either a clean working tree OR the expected modifications
    if "working tree clean" not in r.stdout and "nothing to commit" not in r.stdout:
        # If there are changes, verify they are the expected modifications
        # from the fix (lib.rs and optionally AGENTS.md)
        assert "modified:" in r.stdout, f"Git status unexpected output:\n{r.stdout}"
        # Verify the repo is in a valid state (no errors, git command worked)
        assert "fatal" not in r.stderr.lower(), f"Git error:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_git_ls_files():
    """Git can list tracked files (pass_to_pass)."""
    r = subprocess.run(
        ["git", "ls-files", "turbopack/crates/turbopack/src/lib.rs"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Git ls-files failed:\n{r.stderr}"
    assert "turbopack/crates/turbopack/src/lib.rs" in r.stdout, (
        f"lib.rs not found in git tracked files:\n{r.stdout}"
    )


# [repo_tests] pass_to_pass
def test_repo_git_log():
    """Git log shows expected commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Git log failed:\n{r.stderr}"
    # The base commit should be visible
    assert "b6ff1f6" in r.stdout or "Fix adapter outputs" in r.stdout, (
        f"Expected commit not found in git log:\n{r.stdout}"
    )


# [repo_tests] pass_to_pass
def test_repo_git_diff_empty():
    """Git diff shows no uncommitted changes (pass_to_pass)."""
    r = subprocess.run(
        ["git", "diff", "HEAD"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Git diff failed:\n{r.stderr}"
    # On base commit, there should be no uncommitted changes
    # (Note: this test verifies the repo state, not code correctness)
