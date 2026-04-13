"""
Task: uv-dist-manifest-checksum-patch
Repo: astral-sh/uv @ d0f2f3babc7c892958e93419ad6065df0deb2112
PR:   18625

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import json
import subprocess
import tempfile
from pathlib import Path

REPO = "/repo"
SCRIPT = f"{REPO}/scripts/patch-dist-manifest-checksums.py"

# Broken version of the script for NOP testing (base commit)
BROKEN_SCRIPT = '''#!/usr/bin/env python3
"""Patch cargo-dist local manifest JSON with sidecar SHA-256 checksums."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--artifacts-dir", type=Path, required=True)
    return parser.parse_args()


def read_sha256(path: Path) -> str:
    # BROKEN: doesn't validate empty files or checksum length properly
    line = path.read_text(encoding="utf-8").strip()
    checksum = line.split()[0]
    return checksum


def main() -> int:
    args = parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    artifacts: dict[str, dict] = manifest["artifacts"]

    # BROKEN: doesn't track patched count properly, always exits 0
    # BROKEN: doesn't warn about unmatched sidecars
    for checksum_path in sorted(args.artifacts_dir.glob("*.sha256")):
        artifact_name = checksum_path.name[: -len(".sha256")]
        artifact = artifacts.get(artifact_name)
        if artifact is None:
            # BROKEN: silently skips unmatched instead of warning
            continue

        checksum = read_sha256(checksum_path)
        # BROKEN: patches checksum but doesn't use setdefault correctly
        artifact["checksums"] = {"sha256": checksum}

    # BROKEN: always writes manifest even if nothing was patched (not idempotent)
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\\n", encoding="utf-8")
    print("Done", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _ensure_script():
    """Ensure the script exists. If not at SCRIPT path, create a broken version for NOP testing."""
    script_path = Path(SCRIPT)
    if not script_path.exists():
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text(BROKEN_SCRIPT)


def _make_manifest(artifacts: dict) -> dict:
    """Build a minimal dist-manifest with the given artifact entries."""
    return {"artifacts": artifacts}


def _make_sidecar(directory: Path, artifact_name: str, checksum: str) -> None:
    """Write a .sha256 sidecar file."""
    (directory / f"{artifact_name}.sha256").write_text(
        f"{checksum}  {artifact_name}\n"
    )


def _run_script(manifest_path: str, artifacts_dir: str, expect_fail: bool = False):
    """Run the patch script, return CompletedProcess."""
    r = subprocess.run(
        ["python3", SCRIPT, "--manifest", manifest_path, "--artifacts-dir", artifacts_dir],
        capture_output=True,
        timeout=30,
    )
    if expect_fail:
        assert r.returncode != 0, (
            f"Expected script to fail but got rc=0\nstdout: {r.stdout.decode()}\nstderr: {r.stderr.decode()}"
        )
    else:
        assert r.returncode == 0, (
            f"Script failed (rc={r.returncode})\nstdout: {r.stdout.decode()}\nstderr: {r.stderr.decode()}"
        )
    return r


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Script must be valid Python."""
    _ensure_script()
    src = Path(SCRIPT).read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_patches_checksums_into_manifest():
    """Script injects sha256 checksums into matching artifact entries and preserves existing fields."""
    _ensure_script()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        artifacts_dir = tmp / "artifacts"
        artifacts_dir.mkdir()

        manifest = _make_manifest({
            "uv-x86_64-unknown-linux-gnu.tar.gz": {
                "name": "uv-x86_64-unknown-linux-gnu.tar.gz",
                "kind": "executable-zip",
            },
            "uv-aarch64-apple-darwin.tar.gz": {
                "name": "uv-aarch64-apple-darwin.tar.gz",
                "kind": "executable-zip",
            },
            "uv-x86_64-pc-windows-msvc.zip": {
                "name": "uv-x86_64-pc-windows-msvc.zip",
                "kind": "executable-zip",
            },
        })
        manifest_path = tmp / "manifest.json"
        manifest_path.write_text(json.dumps(manifest))

        checksums = {
            "uv-x86_64-unknown-linux-gnu.tar.gz": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
            "uv-aarch64-apple-darwin.tar.gz": "f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5",
            "uv-x86_64-pc-windows-msvc.zip": "1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
        }
        for name, cksum in checksums.items():
            _make_sidecar(artifacts_dir, name, cksum)

        _run_script(str(manifest_path), str(artifacts_dir))

        result = json.loads(manifest_path.read_text())
        for name, expected_cksum in checksums.items():
            artifact = result["artifacts"][name]
            actual = artifact.get("checksums", {}).get("sha256", "")
            assert actual == expected_cksum, f"{name}: expected {expected_cksum}, got {actual}"
            # Existing fields must be preserved
            assert artifact["kind"] == "executable-zip", f"{name}: 'kind' field lost"


# [pr_diff] fail_to_pass
def test_idempotent_rerun():
    """Running the script twice on the same manifest yields identical output."""
    _ensure_script()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        artifacts_dir = tmp / "artifacts"
        artifacts_dir.mkdir()

        manifest = _make_manifest({
            "uv-x86_64-unknown-linux-gnu.tar.gz": {
                "name": "uv-x86_64-unknown-linux-gnu.tar.gz",
                "kind": "executable-zip",
            },
        })
        manifest_path = tmp / "manifest.json"
        manifest_path.write_text(json.dumps(manifest))

        _make_sidecar(
            artifacts_dir,
            "uv-x86_64-unknown-linux-gnu.tar.gz",
            "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
        )

        _run_script(str(manifest_path), str(artifacts_dir))
        first = manifest_path.read_text()

        _run_script(str(manifest_path), str(artifacts_dir))
        second = manifest_path.read_text()

        assert first == second, "Re-running the script changed the manifest"


# [pr_diff] fail_to_pass
def test_exits_error_no_matches():
    """Script returns non-zero exit code when no sidecar files match any artifact."""
    _ensure_script()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        empty_dir = tmp / "empty"
        empty_dir.mkdir()

        manifest = _make_manifest({
            "uv-x86_64-unknown-linux-gnu.tar.gz": {
                "name": "uv-x86_64-unknown-linux-gnu.tar.gz",
                "kind": "executable-zip",
            },
        })
        manifest_path = tmp / "manifest.json"
        manifest_path.write_text(json.dumps(manifest))

        _run_script(str(manifest_path), str(empty_dir), expect_fail=True)


# [pr_diff] fail_to_pass
def test_rejects_invalid_checksum_length():
    """Script rejects checksums that aren't 64 hex characters."""
    _ensure_script()
    bad_checksums = [
        "tooshort",  # way too short
        "a" * 63,  # one char too short
        "a" * 65,  # one char too long
    ]
    for bad_cksum in bad_checksums:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            bad_dir = tmp / "bad"
            bad_dir.mkdir()

            manifest = _make_manifest({
                "uv-x86_64-unknown-linux-gnu.tar.gz": {
                    "name": "uv-x86_64-unknown-linux-gnu.tar.gz",
                    "kind": "executable-zip",
                },
            })
            manifest_path = tmp / "manifest.json"
            manifest_path.write_text(json.dumps(manifest))

            _make_sidecar(bad_dir, "uv-x86_64-unknown-linux-gnu.tar.gz", bad_cksum)

            _run_script(str(manifest_path), str(bad_dir), expect_fail=True)


# [pr_diff] fail_to_pass
def test_rejects_empty_checksum_file():
    """Script rejects empty .sha256 sidecar files."""
    _ensure_script()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        empty_cksum_dir = tmp / "empty_cksum"
        empty_cksum_dir.mkdir()

        manifest = _make_manifest({
            "uv-x86_64-unknown-linux-gnu.tar.gz": {
                "name": "uv-x86_64-unknown-linux-gnu.tar.gz",
                "kind": "executable-zip",
            },
        })
        manifest_path = tmp / "manifest.json"
        manifest_path.write_text(json.dumps(manifest))

        # Write an empty sidecar
        (empty_cksum_dir / "uv-x86_64-unknown-linux-gnu.tar.gz.sha256").write_text("\n")

        _run_script(str(manifest_path), str(empty_cksum_dir), expect_fail=True)


# [pr_diff] fail_to_pass
def test_warns_unmatched_sidecar():
    """Script warns on stderr about .sha256 files that don't match any manifest artifact."""
    _ensure_script()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        mixed_dir = tmp / "mixed"
        mixed_dir.mkdir()

        manifest = _make_manifest({
            "uv-x86_64-unknown-linux-gnu.tar.gz": {
                "name": "uv-x86_64-unknown-linux-gnu.tar.gz",
                "kind": "executable-zip",
            },
        })
        manifest_path = tmp / "manifest.json"
        manifest_path.write_text(json.dumps(manifest))

        # One matching sidecar + one unmatched
        _make_sidecar(
            mixed_dir,
            "uv-x86_64-unknown-linux-gnu.tar.gz",
            "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
        )
        _make_sidecar(
            mixed_dir,
            "nonexistent-archive.tar.gz",
            "1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
        )

        r = _run_script(str(manifest_path), str(mixed_dir))
        stderr = r.stderr.decode()
        assert "nonexistent-archive" in stderr, (
            f"Expected stderr to mention the unmatched sidecar 'nonexistent-archive', got: {stderr}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_scripts_parse():
    """Existing Python scripts in scripts/ remain valid Python."""
    scripts_dir = Path(REPO) / "scripts"
    for py_file in sorted(scripts_dir.glob("*.py")):
        src = py_file.read_text()
        ast.parse(src, filename=str(py_file))


# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's Python scripts pass ruff linting (pass_to_pass)."""
    # Install ruff if not available
    subprocess.run(["pip", "install", "ruff", "-q"], check=True, capture_output=True)
    r = subprocess.run(
        ["ruff", "check", f"{REPO}/scripts/"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's Python scripts pass ruff format check (pass_to_pass)."""
    subprocess.run(["pip", "install", "ruff", "-q"], check=True, capture_output=True)
    r = subprocess.run(
        ["ruff", "format", "--check", f"{REPO}/scripts/"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_typos():
    """Repo passes typos spell check (pass_to_pass)."""
    subprocess.run(["pip", "install", "typos", "-q"], check=True, capture_output=True)
    r = subprocess.run(
        ["typos"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Typos check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_shellcheck():
    """Repo's shell scripts pass shellcheck (pass_to_pass)."""
    # Install shellcheck
    subprocess.run(["apt-get", "update", "-qq"], capture_output=True)
    subprocess.run(
        ["apt-get", "install", "-y", "-qq", "shellcheck"],
        capture_output=True,
    )
    r = subprocess.run(
        f"find {REPO}/scripts -name '*.sh' -type f | xargs shellcheck --shell bash --severity warning",
        shell=True,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Shellcheck failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_validate_pyproject():
    """Repo's pyproject.toml passes validation (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "validate-pyproject[all,store]", "-q"],
        check=True,
        capture_output=True,
    )
    r = subprocess.run(
        ["validate-pyproject", f"{REPO}/pyproject.toml"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Pyproject validation failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_transform_readme():
    """Repo's README transform script works (pass_to_pass)."""
    r = subprocess.run(
        ["python", f"{REPO}/scripts/transform_readme.py", "--target", "pypi"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"README transform failed:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — CLAUDE.md:16 @ d0f2f3babc7c892958e93419ad6065df0deb2112
def test_top_level_imports_only():
    """PREFER top-level imports over local imports or fully qualified names."""
    _ensure_script()
    src = Path(SCRIPT).read_text()
    tree = ast.parse(src)
    in_func_imports = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in ast.walk(node):
                if isinstance(child, (ast.Import, ast.ImportFrom)):
                    in_func_imports += 1
    assert in_func_imports == 0, f"Found {in_func_imports} import(s) inside functions"
