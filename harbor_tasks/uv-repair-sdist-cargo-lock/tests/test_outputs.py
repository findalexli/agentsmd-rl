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


# [pr_diff] fail_to_pass
def test_rejects_missing_cargo_lock():
    """Script must exit with non-zero status when sdist has no Cargo.lock."""
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


# [pr_diff] fail_to_pass
def test_rejects_multi_toplevel():
    """Script must error when tarball has multiple top-level directories."""
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


# [pr_diff] fail_to_pass
def test_repairs_and_repacks_sdist():
    """Script prunes stale entries from Cargo.lock and repacks the tarball."""
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
    source = Path(SCRIPT).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in ast.walk(node):
                if isinstance(child, (ast.Import, ast.ImportFrom)):
                    assert False, (
                        f"Import found inside function '{node.name}' — "
                        "AGENTS.md requires top-level imports"
                    )
