"""
Task: sglang-wheel-metadata-cuda-suffix
Repo: sgl-project/sglang @ 80389fec004394db409e9d04aef263465a3b235c
PR:   21111

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import hashlib
import base64
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

SCRIPT = "/repo/sgl-kernel/rename_wheels.sh"
REPO = "/repo"

# Cleanup any leftover fake CUDA dirs from previous test runs
_CUDA_DIRS_TO_MANAGE = [
    "/usr/local/cuda-12.4",
    "/usr/local/cuda-12.8",
    "/usr/local/cuda-13.0",
]


def _record_hash(filepath):
    data = open(filepath, "rb").read()
    digest = hashlib.sha256(data).digest()
    b64 = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return f"sha256={b64},{len(data)}"


def _create_mock_wheel(pkg_name, version, platform, dest_dir):
    """Create a minimal valid .whl with correct RECORD hashes."""
    tag = f"cp312-cp312-{platform}"
    dist_info = f"{pkg_name}-{version}.dist-info"

    with tempfile.TemporaryDirectory() as tmpdir:
        pkg_dir = os.path.join(tmpdir, pkg_name)
        di_dir = os.path.join(tmpdir, dist_info)
        os.makedirs(pkg_dir)
        os.makedirs(di_dir)

        init_path = os.path.join(pkg_dir, "__init__.py")
        with open(init_path, "w") as f:
            f.write("# placeholder\n")

        meta_path = os.path.join(di_dir, "METADATA")
        with open(meta_path, "w") as f:
            f.write(
                f"Metadata-Version: 2.1\nName: {pkg_name}\nVersion: {version}\n"
            )

        wheel_path = os.path.join(di_dir, "WHEEL")
        with open(wheel_path, "w") as f:
            f.write(
                f"Wheel-Version: 1.0\nGenerator: test\n"
                f"Root-Is-Purelib: false\nTag: {tag}\n"
            )

        record_path = os.path.join(di_dir, "RECORD")
        lines = []
        for rel in [
            f"{pkg_name}/__init__.py",
            f"{dist_info}/METADATA",
            f"{dist_info}/WHEEL",
        ]:
            lines.append(f"{rel},{_record_hash(os.path.join(tmpdir, rel))}")
        lines.append(f"{dist_info}/RECORD,,")
        with open(record_path, "w") as f:
            f.write("\n".join(lines) + "\n")

        whl_name = f"{pkg_name}-{version}-{tag}.whl"
        whl_path = os.path.join(dest_dir, whl_name)
        with zipfile.ZipFile(whl_path, "w") as zf:
            for root, _dirs, files in os.walk(tmpdir):
                for fname in files:
                    full = os.path.join(root, fname)
                    arcname = os.path.relpath(full, tmpdir)
                    zf.write(full, arcname)
        return whl_path


def _read_wheel_field(whl_path, meta_file_suffix, field_prefix):
    """Read a field from a metadata file inside a wheel."""
    with zipfile.ZipFile(whl_path) as z:
        for name in z.namelist():
            if name.endswith(meta_file_suffix):
                data = z.read(name).decode()
                for line in data.splitlines():
                    if line.startswith(field_prefix):
                        return line.split(":", 1)[1].strip()
    return None


def _read_metadata_version(whl_path):
    return _read_wheel_field(whl_path, ".dist-info/METADATA", "Version:")


def _read_wheel_tag(whl_path):
    return _read_wheel_field(whl_path, ".dist-info/WHEEL", "Tag:")


def _get_distinfo_names(whl_path):
    names = set()
    with zipfile.ZipFile(whl_path) as z:
        for name in z.namelist():
            if ".dist-info/" in name:
                names.add(name.split("/")[0])
    return names


def _setup_cuda(version):
    """Create a fake /usr/local/cuda-<version> directory."""
    _teardown_cuda()
    os.makedirs(f"/usr/local/cuda-{version}", exist_ok=True)


def _teardown_cuda():
    """Remove all fake CUDA directories."""
    for d in _CUDA_DIRS_TO_MANAGE:
        shutil.rmtree(d, ignore_errors=True)


def _run_script_in_workdir(pkg_name, version, platform, cuda_version=None):
    """Create a mock wheel, run rename_wheels.sh, return path to output wheel."""
    workdir = tempfile.mkdtemp()
    dist_dir = os.path.join(workdir, "dist")
    os.makedirs(dist_dir)

    _create_mock_wheel(pkg_name, version, platform, dist_dir)

    if cuda_version:
        _setup_cuda(cuda_version)
    else:
        _teardown_cuda()

    shutil.copy2(SCRIPT, os.path.join(workdir, "rename_wheels.sh"))
    os.chmod(os.path.join(workdir, "rename_wheels.sh"), 0o755)

    r = subprocess.run(
        ["bash", "rename_wheels.sh"],
        cwd=workdir,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"rename_wheels.sh failed (exit {r.returncode}):\n"
        f"{r.stdout.decode()}\n{r.stderr.decode()}"
    )

    whls = sorted(Path(dist_dir).glob("*.whl"))
    assert whls, f"No output wheel found in {dist_dir}"
    return str(whls[0]), workdir


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """rename_wheels.sh must be valid bash."""
    r = subprocess.run(
        ["bash", "-n", SCRIPT], capture_output=True, timeout=10
    )
    assert r.returncode == 0, (
        f"Bash syntax error in {SCRIPT}:\n{r.stderr.decode()}"
    )


# [repo_tests] pass_to_pass — shellcheck linting
def test_shellcheck_rename_wheels():
    """Repo's shellcheck on rename_wheels.sh passes (pass_to_pass)."""
    # Install shellcheck if not available
    try:
        subprocess.run(["shellcheck", "--version"], capture_output=True, timeout=5)
    except FileNotFoundError:
        subprocess.run(
            ["apt-get", "update", "-qq"],
            capture_output=True, timeout=30
        )
        subprocess.run(
            ["apt-get", "install", "-y", "-qq", "shellcheck"],
            capture_output=True, timeout=60
        )
    r = subprocess.run(
        ["shellcheck", "--severity=error", SCRIPT],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Shellcheck errors:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — script is executable
def test_rename_wheels_executable():
    """rename_wheels.sh must be executable (pass_to_pass)."""
    assert os.access(SCRIPT, os.X_OK), f"{SCRIPT} is not executable"


# [repo_tests] pass_to_pass — build.sh syntax check
def test_build_sh_syntax():
    """build.sh must have valid bash syntax (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-n", f"{REPO}/sgl-kernel/build.sh"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"build.sh has syntax errors:\n{r.stderr}"


# [repo_tests] pass_to_pass — kernel-runner-setup.sh syntax check
def test_kernel_runner_setup_sh_syntax():
    """kernel-runner-setup.sh must have valid bash syntax (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-n", f"{REPO}/sgl-kernel/kernel-runner-setup.sh"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"kernel-runner-setup.sh has syntax errors:\n{r.stderr}"


# [repo_tests] pass_to_pass — wheel module available
def test_wheel_module_installed():
    """wheel Python module must be installed (required by rename_wheels.sh) (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "import wheel; print(wheel.__version__)"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"wheel module not installed or import failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_metadata_version_includes_cuda_suffix():
    """Internal METADATA Version must include +cu suffix after script run."""
    out_whl, workdir = _run_script_in_workdir(
        "sgl_kernel", "0.4.5", "linux_x86_64", cuda_version="12.4"
    )
    try:
        version = _read_metadata_version(out_whl)
        assert version is not None, "Could not read Version from METADATA"
        assert "+cu124" in version, (
            f"METADATA Version missing +cu124 suffix, got: {version}"
        )
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
        _teardown_cuda()


# [pr_diff] fail_to_pass
def test_metadata_version_cu128():
    """METADATA Version must include +cu128 suffix for CUDA 12.8."""
    out_whl, workdir = _run_script_in_workdir(
        "sgl_kernel", "1.0.0", "linux_x86_64", cuda_version="12.8"
    )
    try:
        version = _read_metadata_version(out_whl)
        assert version is not None, "Could not read Version from METADATA"
        assert "+cu128" in version, (
            f"METADATA Version missing +cu128 suffix, got: {version}"
        )
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
        _teardown_cuda()


# [pr_diff] fail_to_pass
def test_distinfo_dir_includes_cuda_suffix():
    """dist-info directory name inside the wheel must include +cu suffix."""
    out_whl, workdir = _run_script_in_workdir(
        "sgl_kernel", "0.4.5", "linux_x86_64", cuda_version="12.4"
    )
    try:
        di_names = _get_distinfo_names(out_whl)
        assert any("+cu" in n for n in di_names), (
            f"dist-info directory missing +cu suffix, got: {di_names}"
        )
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
        _teardown_cuda()


# [pr_diff] fail_to_pass
def test_wheel_platform_tags_manylinux():
    """WHEEL Tag must say manylinux2014, not linux."""
    out_whl, workdir = _run_script_in_workdir(
        "sgl_kernel", "0.4.5", "linux_x86_64", cuda_version="12.4"
    )
    try:
        tag = _read_wheel_tag(out_whl)
        assert tag is not None, "Could not read Tag from WHEEL"
        assert "manylinux2014" in tag, (
            f"WHEEL Tag not updated to manylinux2014, got: {tag}"
        )
        assert tag.count("linux") == 1 or "manylinux2014" in tag, (
            f"WHEEL Tag still contains bare 'linux': {tag}"
        )
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
        _teardown_cuda()


# [pr_diff] fail_to_pass
def test_idempotent_no_double_suffix():
    """Running the script twice must not double the +cu suffix."""
    workdir = tempfile.mkdtemp()
    dist_dir = os.path.join(workdir, "dist")
    os.makedirs(dist_dir)
    _create_mock_wheel("sgl_kernel", "0.4.5", "linux_x86_64", dist_dir)
    _setup_cuda("12.4")

    shutil.copy2(SCRIPT, os.path.join(workdir, "rename_wheels.sh"))
    os.chmod(os.path.join(workdir, "rename_wheels.sh"), 0o755)

    try:
        for _ in range(2):
            r = subprocess.run(
                ["bash", "rename_wheels.sh"],
                cwd=workdir,
                capture_output=True,
                timeout=30,
            )
            assert r.returncode == 0, f"Script failed:\n{r.stderr.decode()}"

        whls = sorted(Path(dist_dir).glob("*.whl"))
        assert whls, "No output wheel found after second run"
        version = _read_metadata_version(str(whls[0]))
        cu_count = version.count("+cu")
        assert cu_count == 1, (
            f"Version has {cu_count} +cu occurrences (expected 1): {version}"
        )
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
        _teardown_cuda()


# [pr_diff] fail_to_pass
def test_filename_metadata_consistency():
    """Wheel filename version must match internal METADATA version."""
    out_whl, workdir = _run_script_in_workdir(
        "sgl_kernel", "0.4.5", "linux_x86_64", cuda_version="12.4"
    )
    try:
        fname = os.path.basename(out_whl)
        # Extract version from filename: pkg-VERSION-tag.whl
        fname_version = fname.split("-")[1]
        meta_version = _read_metadata_version(out_whl)

        assert "+cu" in fname_version, (
            f"Filename version missing +cu: {fname_version}"
        )
        assert "+cu" in meta_version, (
            f"METADATA version missing +cu: {meta_version}"
        )
        assert fname_version == meta_version, (
            f"Filename version ({fname_version}) != METADATA version ({meta_version})"
        )
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
        _teardown_cuda()


# [pr_diff] fail_to_pass
def test_platform_tag_no_corruption():
    """Already-manylinux wheel must not get corrupted by double substitution."""
    out_whl, workdir = _run_script_in_workdir(
        "sgl_kernel", "0.4.5", "manylinux2014_x86_64", cuda_version="12.4"
    )
    try:
        fname = os.path.basename(out_whl)
        assert "manylinux20142014" not in fname, (
            f"Platform tag corrupted by double substitution: {fname}"
        )
        assert "manymanylinux" not in fname, (
            f"Platform tag corrupted: {fname}"
        )
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
        _teardown_cuda()


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_no_cuda_wheel_unchanged():
    """Without CUDA detected, wheel should pass through with version unchanged."""
    out_whl, workdir = _run_script_in_workdir(
        "sgl_kernel", "0.4.5", "manylinux2014_x86_64", cuda_version=None
    )
    try:
        version = _read_metadata_version(out_whl)
        assert version == "0.4.5", (
            f"Version changed without CUDA present: {version}"
        )
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
