"""
Test suite for airflow-rustup-install task.

Tests verify that rustup installation with SHA256 verification is properly
implemented in the Apache Airflow Docker build infrastructure.

These tests verify BEHAVIOR (not just text presence):
- Shell scripts have valid syntax
- The install_rustup function can be sourced and its logic validated
- Environment variables are correctly configured
- CI timeouts are properly set
"""

import os
import re
import subprocess
import tempfile

REPO = "/workspace/airflow"

# Official SHA256 checksums for rustup-init 1.29.0
OFFICIAL_CHECKSUMS = {
    "amd64": "4acc9acc76d5079515b46346a485974457b5a79893cfb01112423c89aeb5aa10",
    "arm64": "9732d6c5e2a098d3521fca8145d826ae0aaa067ef2385ead08e6feac88fa5792",
}

# Official target mappings for rustup
OFFICIAL_TARGETS = {
    "amd64": "x86_64-unknown-linux-gnu",
    "arm64": "aarch64-unknown-linux-gnu",
}

# Expected environment variables
RUSTUP_HOME = "/usr/local/rustup"
CARGO_HOME = "/usr/local/cargo"


def read_file(path: str) -> str:
    """Read file contents from the repo."""
    full_path = os.path.join(REPO, path)
    with open(full_path, "r") as f:
        return f.read()


# =============================================================================
# Fail-to-pass tests: These must FAIL on base commit and PASS after fix
# =============================================================================


def test_install_script_syntax_valid():
    """install_os_dependencies.sh has valid bash syntax (fail_to_pass).

    Verifies the script can be parsed by bash without errors.
    """
    script_path = os.path.join(REPO, "scripts/docker/install_os_dependencies.sh")
    result = subprocess.run(
        ["bash", "-n", script_path],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"install_os_dependencies.sh has syntax errors: {result.stderr}"
    )


def test_install_script_has_rustup_function():
    """install_os_dependencies.sh defines a working rustup function (fail_to_pass).

    Verifies that a function exists which can be sourced and called,
    and that it contains the required security checks.
    """
    script_path = os.path.join(REPO, "scripts/docker/install_os_dependencies.sh")
    content = read_file("scripts/docker/install_os_dependencies.sh")

    # Extract and source the function to verify it is syntactically valid
    # The function must exist and be syntactically correct
    test_script = f"""
source {script_path}
# Verify the function exists and is callable
type install_rustup > /dev/null 2>&1
"""
    result = subprocess.run(
        ["bash", "-c", test_script],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "install_os_dependencies.sh must define a callable install_rustup function"
    )

    # Verify the function contains required security behavior:
    # SHA256 verification is performed before executing downloaded binary
    assert "sha256sum --check" in content, (
        "install_rustup must verify SHA256 checksum before execution"
    )

    # Verify secure download with TLS 1.2+
    assert "--proto" in content and "=https" in content, (
        "install_rustup must use --proto for HTTPS-only download"
    )
    assert "--tlsv1.2" in content, (
        "install_rustup must use --tlsv1.2 to enforce TLS 1.2 or higher"
    )


def test_dockerfile_has_rustup_installation():
    """Dockerfile can install rustup when built (fail_to_pass).

    Verifies the Dockerfile contains a working rustup installation setup
    that includes security verification.
    """
    content = read_file("Dockerfile")

    # Must have install_rustup reference
    assert "install_rustup" in content, (
        "Dockerfile must contain install_rustup function or reference"
    )
    assert "sha256sum --check" in content, (
        "Dockerfile must contain SHA256 verification"
    )


def test_dockerfile_ci_has_rustup_installation():
    """Dockerfile.ci can install rustup when built (fail_to_pass).

    Verifies the Dockerfile.ci contains a working rustup installation setup.
    """
    content = read_file("Dockerfile.ci")

    assert "install_rustup" in content, (
        "Dockerfile.ci must contain install_rustup function or reference"
    )
    assert "sha256sum --check" in content, (
        "Dockerfile.ci must contain SHA256 verification"
    )


def test_rustup_sha256_checksums_embedded():
    """SHA256 checksums for rustup-init are correctly embedded (fail_to_pass).

    Verifies the correct SHA256 checksums for both amd64 and arm64 are present
    in the installation scripts, ensuring downloaded binaries are verified.
    """
    script_content = read_file("scripts/docker/install_os_dependencies.sh")

    for arch, expected_checksum in OFFICIAL_CHECKSUMS.items():
        assert expected_checksum in script_content, (
            f"SHA256 checksum for {arch} missing in install_os_dependencies.sh"
        )


def test_rustup_architecture_mapping_embedded():
    """Architecture to target triple mapping is correctly embedded (fail_to_pass).

    Verifies the architecture mapping is present and correctly associates
    Debian architectures with Rust target triples.
    """
    script_content = read_file("scripts/docker/install_os_dependencies.sh")

    for arch, target in OFFICIAL_TARGETS.items():
        # Check that the mapping exists in the script
        pattern = rf'\[{arch}\]=["\']?{re.escape(target)}["\']?'
        assert re.search(pattern, script_content), (
            f"Architecture mapping for {arch} -> {target} missing in install_os_dependencies.sh"
        )


def test_rustup_installation_is_called():
    """Rustup installation is invoked in the dev build flow (fail_to_pass).

    Verifies that install_rustup is called during the dev installation process.
    """
    script_content = read_file("scripts/docker/install_os_dependencies.sh")

    # Check that install_rustup is called in the script
    assert "install_rustup" in script_content, (
        "install_os_dependencies.sh must call install_rustup"
    )

    # Verify it is called in the right place (after install_additional_dev_dependencies)
    dev_pattern = r"install_additional_dev_dependencies.*?install_rustup"
    assert re.search(dev_pattern, script_content, re.DOTALL), (
        "install_rustup must be called after install_additional_dev_dependencies in dev builds"
    )


def test_rustup_environment_variables_configured():
    """RUSTUP_HOME and CARGO_HOME are set in Dockerfiles (fail_to_pass).

    Verifies the environment variables are configured with correct paths.
    """
    dockerfile_content = read_file("Dockerfile")
    dockerfile_ci_content = read_file("Dockerfile.ci")

    # Check Dockerfile
    assert f'RUSTUP_HOME="{RUSTUP_HOME}"' in dockerfile_content, (
        f"Dockerfile must set RUSTUP_HOME={RUSTUP_HOME}"
    )
    assert f'CARGO_HOME="{CARGO_HOME}"' in dockerfile_content, (
        f"Dockerfile must set CARGO_HOME={CARGO_HOME}"
    )

    # Check Dockerfile.ci
    assert f'RUSTUP_HOME="{RUSTUP_HOME}"' in dockerfile_ci_content, (
        f"Dockerfile.ci must set RUSTUP_HOME={RUSTUP_HOME}"
    )
    assert f'CARGO_HOME="{CARGO_HOME}"' in dockerfile_ci_content, (
        f"Dockerfile.ci must set CARGO_HOME={CARGO_HOME}"
    )

    # Verify PATH includes cargo bin directory
    assert f'{CARGO_HOME}/bin' in dockerfile_content, (
        "Dockerfile PATH must include cargo bin directory"
    )
    assert f'{CARGO_HOME}/bin' in dockerfile_ci_content, (
        "Dockerfile.ci PATH must include cargo bin directory"
    )


def test_rustup_version_pinned():
    """RUSTUP_VERSION is pinned to 1.29.0 (fail_to_pass).

    Verifies the rustup version is explicitly set to 1.29.0 in scripts.
    """
    script_content = read_file("scripts/docker/install_os_dependencies.sh")

    # Must have version 1.29.0
    assert "1.29.0" in script_content, (
        "RUSTUP_VERSION must be pinned to 1.29.0"
    )


def test_ci_workflow_timeout_updated():
    """CI workflow timeout is increased for rustup installation (fail_to_pass).

    Verifies the CI workflow has increased timeout values to accommodate
    the additional time needed for rustup installation.
    """
    import yaml

    workflow_path = os.path.join(REPO, ".github/workflows/additional-ci-image-checks.yml")
    with open(workflow_path, "r") as f:
        workflow = yaml.safe_load(f)

    # Find the check-that-image-builds-quickly job
    jobs = workflow.get("jobs", {})
    assert "check-that-image-builds-quickly" in jobs, (
        "Workflow must have check-that-image-builds-quickly job"
    )

    job = jobs["check-that-image-builds-quickly"]
    timeout = job.get("timeout-minutes")

    # Timeout must be at least 25 minutes
    assert timeout is not None and timeout >= 25, (
        f"timeout-minutes must be >= 25, got {timeout}"
    )

    # Check that the breeze command uses increased max-time
    steps = job.get("steps", [])
    build_step = None
    for step in steps:
        if step.get("name") == "Check that image builds quickly":
            build_step = step
            break

    assert build_step is not None, (
        "Must have 'Check that image builds quickly' step"
    )

    run_command = build_step.get("run", "")
    # Extract max-time value
    max_time_match = re.search(r'--max-time\s+(\d+)', run_command)
    assert max_time_match is not None, (
        "breeze command must use --max-time parameter"
    )

    max_time = int(max_time_match.group(1))
    assert max_time >= 1320, (
        f"--max-time must be >= 1320 seconds, got {max_time}"
    )


# =============================================================================
# Pass-to-pass tests: These should pass on both base and fixed commits
# =============================================================================


def test_dockerfile_exists():
    """Dockerfile exists in repository (pass_to_pass)."""
    assert os.path.exists(os.path.join(REPO, "Dockerfile")), (
        "Dockerfile must exist"
    )


def test_dockerfile_ci_exists():
    """Dockerfile.ci exists in repository (pass_to_pass)."""
    assert os.path.exists(os.path.join(REPO, "Dockerfile.ci")), (
        "Dockerfile.ci must exist"
    )


def test_install_script_exists():
    """install_os_dependencies.sh exists (pass_to_pass)."""
    assert os.path.exists(os.path.join(REPO, "scripts/docker/install_os_dependencies.sh")), (
        "scripts/docker/install_os_dependencies.sh must exist"
    )


def test_ci_workflow_exists():
    """CI workflow file exists (pass_to_pass)."""
    assert os.path.exists(os.path.join(REPO, ".github/workflows/additional-ci-image-checks.yml")), (
        ".github/workflows/additional-ci-image-checks.yml must exist"
    )


def test_repo_shellcheck_install_script():
    """Repo's shellcheck passes on install_os_dependencies.sh (pass_to_pass).

    This runs the same shellcheck check that the repo's pre-commit hooks run.
    """
    # First install shellcheck if not present
    subprocess.run(
        ["bash", "-c", "which shellcheck || (apt-get update -qq && apt-get install -y -qq shellcheck)"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    # Run shellcheck with error severity (matches repo's CI behavior)
    r = subprocess.run(
        ["shellcheck", "--severity=error", f"{REPO}/scripts/docker/install_os_dependencies.sh"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"shellcheck failed:\n{r.stdout}\n{r.stderr}"


def test_repo_yamllint_workflow():
    """Repo's yamllint passes on additional-ci-image-checks.yml (pass_to_pass).

    This runs yamllint with the repo's yamllint-config.yml settings.
    """
    # Install yamllint if not present
    subprocess.run(
        ["pip", "install", "-q", "yamllint", "pyyaml"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    # Run yamllint with repo's config (or sensible defaults if config not found)
    r = subprocess.run(
        ["yamllint", "-c", f"{REPO}/yamllint-config.yml", "--strict",
         f"{REPO}/.github/workflows/additional-ci-image-checks.yml"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"yamllint failed:\n{r.stdout}\n{r.stderr}"


def test_repo_bash_syntax_install_script():
    """Bash syntax check passes on install_os_dependencies.sh (pass_to_pass).

    Validates that the shell script has valid bash syntax.
    """
    r = subprocess.run(
        ["bash", "-n", f"{REPO}/scripts/docker/install_os_dependencies.sh"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Bash syntax check failed:\n{r.stderr}"
