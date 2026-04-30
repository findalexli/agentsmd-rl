"""
Task: uv-repair-sdist-cargo-lock
Repo: uv @ c5977cc4ae4cd1cf8b97c7193e927f7b2a9c4e87
PR:   18831

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import os
import subprocess
import tarfile
import tempfile
from pathlib import Path

REPO = "/workspace/uv"
SCRIPT = f"{REPO}/scripts/repair-sdist-cargo-lock.py"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_rejects_non_tarfile():
    """Script must exit with non-zero status when given a non-tarball file."""
    assert os.path.exists(SCRIPT), f"Script not found at {SCRIPT}"
    with tempfile.NamedTemporaryFile(suffix=".tar.gz") as f:
        f.write(b"this is not a real tarball at all")
        f.flush()
        r = subprocess.run(
            ["python3", SCRIPT, f.name],
            capture_output=True, timeout=30,
        )
        assert r.returncode != 0, (
            "Script should fail on non-tarball input but exited 0"
        )
        assert "not a valid tar" in r.stderr.decode(), (
            f"Expected 'not a valid tar' in stderr, got: {r.stderr.decode()}"
        )


# [pr_diff] fail_to_pass
def test_rejects_missing_cargo_lock():
    """Script must exit with non-zero status when sdist has no Cargo.lock."""
    assert os.path.exists(SCRIPT), f"Script not found at {SCRIPT}"
    with tempfile.TemporaryDirectory() as tmpdir:
        pkg_dir = os.path.join(tmpdir, "fake_pkg-0.1.0")
        os.makedirs(os.path.join(pkg_dir, "src"))
        Path(os.path.join(pkg_dir, "Cargo.toml")).write_text(
            '[package]\nname = "fake_pkg"\nversion = "0.1.0"\nedition = "2021"\n'
        )
        Path(os.path.join(pkg_dir, "src", "lib.rs")).write_text("")

        tarball = os.path.join(tmpdir, "fake_pkg-0.1.0.tar.gz")
        with tarfile.open(tarball, "w:gz") as tar:
            tar.add(pkg_dir, arcname="fake_pkg-0.1.0")

        r = subprocess.run(
            ["python3", SCRIPT, tarball],
            capture_output=True, timeout=30,
        )
        assert r.returncode != 0, (
            "Script should fail when Cargo.lock is missing but exited 0"
        )
        assert "no Cargo.lock found" in r.stderr.decode(), (
            f"Expected 'no Cargo.lock found' in stderr, got: {r.stderr.decode()}"
        )


# [pr_diff] fail_to_pass
def test_rejects_multi_toplevel():
    """Script must error when tarball has multiple top-level directories."""
    assert os.path.exists(SCRIPT), f"Script not found at {SCRIPT}"
    with tempfile.TemporaryDirectory() as tmpdir:
        for name in ("dir_alpha", "dir_beta"):
            os.makedirs(os.path.join(tmpdir, name))
            Path(os.path.join(tmpdir, name, "dummy.txt")).write_text("x")

        tarball = os.path.join(tmpdir, "multi.tar.gz")
        with tarfile.open(tarball, "w:gz") as tar:
            tar.add(os.path.join(tmpdir, "dir_alpha"), arcname="dir_alpha")
            tar.add(os.path.join(tmpdir, "dir_beta"), arcname="dir_beta")

        r = subprocess.run(
            ["python3", SCRIPT, tarball],
            capture_output=True, timeout=30,
        )
        assert r.returncode != 0, (
            "Script should fail on tarball with multiple top-level dirs"
        )
        assert "expected one top-level directory" in r.stderr.decode(), (
            f"Expected 'expected one top-level directory' in stderr, got: {r.stderr.decode()}"
        )


# [pr_diff] fail_to_pass
def test_repairs_and_repacks_sdist():
    """Script prunes stale entries from Cargo.lock and repacks the tarball."""
    assert os.path.exists(SCRIPT), f"Script not found at {SCRIPT}"
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a minimal Cargo project
        pkg_dir = os.path.join(tmpdir, "test_crate-0.1.0")
        src_dir = os.path.join(pkg_dir, "src")
        os.makedirs(src_dir)

        Path(os.path.join(pkg_dir, "Cargo.toml")).write_text(
            '[package]\nname = "test_crate"\nversion = "0.1.0"\nedition = "2021"\n'
        )
        Path(os.path.join(src_dir, "lib.rs")).write_text("")

        # Generate a valid Cargo.lock, then inject a stale phantom entry
        subprocess.run(
            ["cargo", "generate-lockfile"],
            cwd=pkg_dir, check=True, capture_output=True, timeout=60,
        )
        lock_path = os.path.join(pkg_dir, "Cargo.lock")
        original_lock = Path(lock_path).read_text()
        Path(lock_path).write_text(
            original_lock
            + '\n[[package]]\nname = "phantom_workspace_crate"\nversion = "0.0.0"\n'
        )

        # Sanity: the phantom entry is in the lockfile
        assert "phantom_workspace_crate" in Path(lock_path).read_text()

        # Tar it up
        tarball = os.path.join(tmpdir, "test_crate-0.1.0.tar.gz")
        with tarfile.open(tarball, "w:gz") as tar:
            tar.add(pkg_dir, arcname="test_crate-0.1.0")

        # Run the repair script
        r = subprocess.run(
            ["python3", SCRIPT, tarball],
            capture_output=True, timeout=120,
        )
        assert r.returncode == 0, f"Repair script failed:\n{r.stderr.decode()}"

        # Extract repacked tarball and verify phantom entry was pruned
        out_dir = os.path.join(tmpdir, "repacked")
        with tarfile.open(tarball, "r:gz") as tar:
            tar.extractall(out_dir)

        repacked_lock = Path(
            os.path.join(out_dir, "test_crate-0.1.0", "Cargo.lock")
        ).read_text()
        assert "phantom_workspace_crate" not in repacked_lock, (
            "Stale phantom package should have been pruned from Cargo.lock"
        )


# [pr_diff] fail_to_pass
def test_cli_argument_parsing():
    """Script provides a proper CLI with --help."""
    assert os.path.exists(SCRIPT), f"Script not found at {SCRIPT}"
    r = subprocess.run(
        ["python3", SCRIPT, "--help"],
        capture_output=True, timeout=10,
    )
    assert r.returncode == 0, "Script --help should exit 0"
    help_text = r.stdout.decode().lower()
    assert "sdist" in help_text or "tar" in help_text or "cargo" in help_text, (
        f"Help text should reference sdist/tar/cargo, got:\n{r.stdout.decode()}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md rules
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:16 @ c5977cc4ae4cd1cf8b97c7193e927f7b2a9c4e87
def test_top_level_imports():
    """All imports in the repair script must be at module level (AGENTS.md line 16)."""
    assert os.path.exists(SCRIPT), f"Script not found at {SCRIPT}"
    source = Path(SCRIPT).read_text()
    assert len(source.strip()) > 0, "Script file is empty"
    tree = ast.parse(source)

    top_level_imports = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            top_level_imports.append(node)

    assert len(top_level_imports) > 0, (
        "Script must have at least one top-level import statement "
        "(AGENTS.md requires top-level imports)"
    )

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in ast.walk(node):
                if isinstance(child, (ast.Import, ast.ImportFrom)):
                    assert False, (
                        f"Import found inside function '{node.name}' — "
                        "AGENTS.md requires top-level imports"
                    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base AND fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — cargo check on uv-build crate
def test_repo_cargo_check_uv_build():
    """uv-build crate compiles cleanly (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check -p uv-build failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — cargo fmt check
def test_repo_cargo_fmt():
    """Rust code formatting is correct (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt --check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — cargo clippy on uv-build crate
def test_repo_cargo_clippy_uv_build():
    """uv-build crate passes clippy linting (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "uv-build", "--", "-D", "warnings"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo clippy -p uv-build failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Python syntax check on scripts
def test_repo_python_syntax():
    """Python scripts in scripts/ have valid syntax (pass_to_pass)."""
    scripts_dir = Path(REPO) / "scripts"
    py_files = list(scripts_dir.glob("*.py"))

    for py_file in py_files:
        r = subprocess.run(
            ["python3", "-m", "py_compile", str(py_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, (
            f"Python syntax error in {py_file.name}:\n{r.stderr[-500:]}"
        )


# [repo_tests] pass_to_pass — ruff lint check on scripts
def test_repo_ruff_lint():
    """Python scripts in scripts/ pass ruff linting (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "--break-system-packages"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["ruff", "check", f"{REPO}/scripts/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — ruff format check on scripts
def test_repo_ruff_format():
    """Python scripts in scripts/ pass ruff format check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "--break-system-packages"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["ruff", "format", "--diff", f"{REPO}/scripts/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff format --diff failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — cargo deny bans check on uv-build
def test_repo_cargo_deny_uv_build():
    """uv-build crate passes cargo deny bans check (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "install", "cargo-deny", "--version", "0.18.3", "--locked"],
        capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"Failed to install cargo-deny:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["cargo", "deny", "check", "bans"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/crates/uv-build",
    )
    assert r.returncode == 0, f"cargo deny check bans failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"



# [repo_tests] pass_to_pass — cargo shear for unused dependencies
def test_repo_cargo_shear():
    """No unused dependencies found via cargo-shear (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "install", "cargo-shear", "--locked"],
        capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"Failed to install cargo-shear:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["cargo", "shear", "--deny-warnings"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo shear --deny-warnings failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
