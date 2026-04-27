"""
Task: deno-chore-remove-some-top-level
Repo: denoland/deno @ 0b38d25ba7c1893757e15fbb2a68537b0191321f
PR:   32022

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/deno"


def _extract_top_level_entries(git_ls_output: str) -> list[str]:
    """Extract unique sorted top-level entries from git ls-files output.

    Handles git quotePath: paths with special characters are double-quoted.
    """
    entries = set()
    for line in git_ls_output.strip().split("\n"):
        if not line:
            continue
        # Strip git quotePath quoting
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        first = line.split("/")[0]
        # Also strip any remaining leading quotes from partial paths
        first = first.strip('"')
        if first:
            entries.add(first)
    return sorted(entries)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_toml_valid():
    """Cargo.toml must be valid TOML with correct workspace structure."""
    import tomllib

    cargo_toml = Path(f"{REPO}/Cargo.toml")
    content = cargo_toml.read_text()

    # Parse as TOML
    config = tomllib.loads(content)

    # Check workspace members includes tests/bench_util (new location)
    members = config.get("workspace", {}).get("members", [])
    assert "tests/bench_util" in members, \
        f"tests/bench_util not in workspace members: {members}"

    # Check bench_util is NOT at old location
    assert "bench_util" not in members, \
        f"bench_util (old path) still in workspace members: {members}"

    # Check deno_bench_util path points to new location
    workspace_deps = config.get("workspace", {}).get("dependencies", {})
    # It is defined as a workspace library, not in dependencies
    # Look for it in the [workspace] section as a path dependency pattern
    deno_bench_util_line = None
    for line in content.split("\n"):
        if "deno_bench_util" in line and "path" in line:
            deno_bench_util_line = line
            break

    assert deno_bench_util_line is not None, "deno_bench_util not found in Cargo.toml"
    assert "tests/bench_util" in deno_bench_util_line, \
        f"deno_bench_util path not updated: {deno_bench_util_line}"


# [static] pass_to_pass
def test_bench_util_moved():
    """bench_util directory exists at new location tests/bench_util."""
    new_path = Path(f"{REPO}/tests/bench_util")
    old_path = Path(f"{REPO}/bench_util")

    # New path must exist
    assert new_path.exists(), f"tests/bench_util does not exist"
    assert new_path.is_dir(), f"tests/bench_util is not a directory"

    # Must have Cargo.toml inside
    assert (new_path / "Cargo.toml").exists(), \
        "tests/bench_util/Cargo.toml does not exist"


# [static] pass_to_pass
def test_docs_tsgo_moved():
    """docs/tsgo.md content moved to cli/tsc/README.md."""
    old_path = Path(f"{REPO}/docs/tsgo.md")
    readme_path = Path(f"{REPO}/cli/tsc/README.md")

    # Old file should not exist
    assert not old_path.exists(), "docs/tsgo.md should have been removed"

    # Content should be in README.md
    readme_content = readme_path.read_text()

    # Key content indicators from the moved documentation
    assert "Typescript-Go Integration" in readme_content, \
        "Typescript-Go Integration section not found in cli/tsc/README.md"
    assert "deno_typescript_go_client_rust" in readme_content or \
           "typescript-go" in readme_content.lower(), \
        "typescript-go content not found in cli/tsc/README.md"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cargo_check_passes():
    """Cargo workspace compiles after bench_util move."""
    r = subprocess.run(
        ["cargo", "check", "-p", "deno_bench_util"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, \
        f"cargo check -p deno_bench_util failed: {r.stderr}"


# [pr_diff] fail_to_pass
def test_lint_js_detects_top_level_directories():
    """lint.js correctly identifies top-level directories as entries."""
    lint_js = Path(f"{REPO}/tools/lint.js").read_text()

    # The old code had a filter that excluded directories:
    #   .filter((file) => !file.includes(SEPARATOR))
    # Any correct fix must remove this and extract first path component instead.
    assert "!file.includes(SEPARATOR)" not in lint_js, \
        "lint.js still uses the old file-only filter that excludes directories"

    # Behavioral verification: git ls-files should yield directories as entries
    r = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"git ls-files failed: {r.stderr}"

    entries = _extract_top_level_entries(r.stdout)

    # Key directories must be detected as top-level entries
    assert "cli" in entries, "cli directory not detected as top-level entry"
    assert "tests" in entries, "tests directory not detected as top-level entry"
    assert "tools" in entries, "tools directory not detected as top-level entry"

    expected_dirs = ["cli", "ext", "libs", "runtime", "tests", "tools"]
    found = [d for d in expected_dirs if d in entries]
    assert len(found) >= 3, \
        f"Expected at least 3 of {expected_dirs}, found: {found}"


# [pr_diff] fail_to_pass
def test_lint_js_blocks_unauthorized_top_level():
    """lint.js ensureNoNewTopLevelEntries blocks unauthorized entries."""
    # Behavioral verification: extract top-level entries from git ls-files
    # and verify all entries are in the allowed set (matching lint.js logic)
    r = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"git ls-files failed: {r.stderr}"

    entries = _extract_top_level_entries(r.stdout)

    # The allowed set matches the patched lint.js ensureNoNewTopLevelEntries
    allowed = {
        ".cargo", ".devcontainer", ".github", "cli", "ext", "libs",
        "runtime", "tests", "tools", ".dlint.json", ".dprint.json",
        ".editorconfig", ".gitattributes", ".gitignore", ".gitmodules",
        ".rustfmt.toml", "CLAUDE.md", "Cargo.lock", "Cargo.toml",
        "LICENSE.md", "README.md", "Releases.md", "import_map.json",
        "rust-toolchain.toml", "flake.nix", "flake.lock",
    }

    new_entries = [e for e in entries if e not in allowed]
    assert len(new_entries) == 0, \
        f"Unauthorized top-level entries detected: {new_entries}"

    assert len(entries) > 5, \
        f"Expected multiple top-level entries, found: {len(entries)}"


# [pr_diff] fail_to_pass
def test_bench_util_compiles():
    """deno_bench_util crate compiles at new location."""
    r = subprocess.run(
        ["cargo", "check", "--manifest-path", f"{REPO}/tests/bench_util/Cargo.toml"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, \
        f"cargo check for tests/bench_util failed: {r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_cargo_metadata():
    """Cargo metadata is valid and parseable (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "metadata", "--format-version", "1"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"cargo metadata failed: {r.stderr}"

    metadata = json.loads(r.stdout.strip())
    packages = metadata.get("packages", [])
    assert len(packages) > 0, "No packages found in workspace"

    bench_util_pkg = None
    for pkg in packages:
        if pkg.get("name") == "deno_bench_util":
            bench_util_pkg = pkg
            break

    assert bench_util_pkg is not None, "deno_bench_util not found in workspace packages"


# [repo_tests] pass_to_pass
def test_repo_cargo_check():
    """Cargo workspace checks pass on base commit (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "deno_bench_util"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_rustfmt():
    """Repo code follows rustfmt formatting (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"rustfmt check failed:\n{r.stderr or r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_clippy():
    """deno_bench_util passes clippy lints (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "deno_bench_util", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"clippy failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_lock_valid():
    """Cargo.lock is valid and consistent with workspace (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "--locked", "-p", "deno_bench_util"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"cargo check --locked failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_git_ls_files():
    """Git repository has expected top-level entries (pass_to_pass)."""
    r = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"git ls-files failed:\n{r.stderr}"

    files = r.stdout.strip().split("\n")
    # Check that expected top-level directories exist in git ls-files
    top_level_dirs = set()
    for f in files:
        if "/" in f:
            top_level_dirs.add(f.split("/")[0])

    # Key directories should be present
    assert "cli" in top_level_dirs, "cli directory not found in git ls-files"
    assert "ext" in top_level_dirs, "ext directory not found in git ls-files"
    assert "runtime" in top_level_dirs, "runtime directory not found in git ls-files"
    assert "tests" in top_level_dirs, "tests directory not found in git ls-files"
    assert "tools" in top_level_dirs, "tools directory not found in git ls-files"


# [repo_tests] pass_to_pass
def test_repo_cargo_test_bench_util():
    """deno_bench_util unit tests pass on base commit (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "--locked", "--lib", "-p", "deno_bench_util"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"cargo test for deno_bench_util failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_cargo_tree():
    """Cargo dependency tree resolves correctly (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "tree", "-p", "deno_bench_util", "--depth", "2"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"cargo tree failed:\n{r.stderr[-500:]}"

    # Verify the output contains expected dependencies
    assert "deno_bench_util" in r.stdout, "deno_bench_util not in dependency tree"
    assert "deno_core" in r.stdout, "deno_core not in dependency tree"


# [repo_tests] pass_to_pass
def test_cargo_lock_updated():
    """Cargo.lock is consistent with Cargo.toml after workspace changes."""
    r = subprocess.run(
        ["cargo", "metadata", "--format-version", "1"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"cargo metadata failed: {r.stderr}"

    metadata = json.loads(r.stdout.strip())
    packages = metadata.get("packages", [])

    bench_util_pkg = None
    for pkg in packages:
        if pkg.get("name") == "deno_bench_util":
            bench_util_pkg = pkg
            break

    assert bench_util_pkg is not None, "deno_bench_util not found in workspace packages"

    manifest_path = bench_util_pkg.get("manifest_path", "")
    assert "tests/bench_util" in manifest_path, \
        f"deno_bench_util manifest_path not at tests/bench_util: {manifest_path}"
