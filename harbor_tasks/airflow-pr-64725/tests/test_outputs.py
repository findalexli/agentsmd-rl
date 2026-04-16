"""
Test suite for airflow-rustup-install task.

Tests verify that rustup installation with SHA256 verification is properly
implemented in the Apache Airflow Docker build infrastructure.
"""

import os
import re

REPO = "/workspace/airflow"

# Official SHA256 checksums for rustup-init 1.29.0
# These can be verified at: https://static.rust-lang.org/rustup/archive/1.29.0/{target}/rustup-init.sha256
OFFICIAL_CHECKSUMS = {
    "amd64": "4acc9acc76d5079515b46346a485974457b5a79893cfb01112423c89aeb5aa10",
    "arm64": "9732d6c5e2a098d3521fca8145d826ae0aaa067ef2385ead08e6feac88fa5792",
}

# Official target mappings for rustup
OFFICIAL_TARGETS = {
    "amd64": "x86_64-unknown-linux-gnu",
    "arm64": "aarch64-unknown-linux-gnu",
}


def read_file(path: str) -> str:
    """Read file contents from the repo."""
    full_path = os.path.join(REPO, path)
    with open(full_path, "r") as f:
        return f.read()


# =============================================================================
# Fail-to-pass tests: These must FAIL on base commit and PASS after fix
# =============================================================================


def test_dockerfile_has_install_rustup_function():
    """Dockerfile defines install_rustup function (fail_to_pass)."""
    content = read_file("Dockerfile")
    # Must have the function definition
    assert "function install_rustup()" in content, (
        "Dockerfile must define install_rustup() function for secure Rust installation"
    )
    # Function must include SHA256 verification
    assert "sha256sum --check" in content, (
        "install_rustup must verify SHA256 checksum before execution"
    )


def test_dockerfile_ci_has_install_rustup_function():
    """Dockerfile.ci defines install_rustup function (fail_to_pass)."""
    content = read_file("Dockerfile.ci")
    assert "function install_rustup()" in content, (
        "Dockerfile.ci must define install_rustup() function"
    )
    assert "sha256sum --check" in content, (
        "install_rustup must verify SHA256 checksum"
    )


def test_install_script_has_install_rustup_function():
    """install_os_dependencies.sh defines install_rustup function (fail_to_pass)."""
    content = read_file("scripts/docker/install_os_dependencies.sh")
    assert "function install_rustup()" in content, (
        "install_os_dependencies.sh must define install_rustup() function"
    )
    assert "sha256sum --check" in content, (
        "install_rustup must verify SHA256 checksum"
    )


def test_dockerfile_sha256_checksums_correct():
    """Dockerfile has correct SHA256 checksums for rustup-init 1.29.0 (fail_to_pass)."""
    content = read_file("Dockerfile")

    for arch, expected_checksum in OFFICIAL_CHECKSUMS.items():
        # Look for the checksum in the file
        assert expected_checksum in content, (
            f"Dockerfile missing correct SHA256 checksum for {arch}: {expected_checksum}"
        )


def test_dockerfile_ci_sha256_checksums_correct():
    """Dockerfile.ci has correct SHA256 checksums for rustup-init 1.29.0 (fail_to_pass)."""
    content = read_file("Dockerfile.ci")

    for arch, expected_checksum in OFFICIAL_CHECKSUMS.items():
        assert expected_checksum in content, (
            f"Dockerfile.ci missing correct SHA256 checksum for {arch}: {expected_checksum}"
        )


def test_install_script_sha256_checksums_correct():
    """install_os_dependencies.sh has correct SHA256 checksums (fail_to_pass)."""
    content = read_file("scripts/docker/install_os_dependencies.sh")

    for arch, expected_checksum in OFFICIAL_CHECKSUMS.items():
        assert expected_checksum in content, (
            f"install_os_dependencies.sh missing correct SHA256 for {arch}: {expected_checksum}"
        )


def test_dockerfile_architecture_mapping():
    """Dockerfile has correct architecture to target mapping (fail_to_pass)."""
    content = read_file("Dockerfile")

    for arch, target in OFFICIAL_TARGETS.items():
        # Check that the mapping exists
        # Format: [amd64]="x86_64-unknown-linux-gnu"
        pattern = rf'\[{arch}\]="?{re.escape(target)}"?'
        assert re.search(pattern, content), (
            f"Dockerfile missing architecture mapping: {arch} -> {target}"
        )


def test_dockerfile_calls_install_rustup():
    """Dockerfile calls install_rustup in dev installation flow (fail_to_pass)."""
    content = read_file("Dockerfile")

    # install_rustup should be called (not just defined)
    # Look for the call after install_additional_dev_dependencies
    assert re.search(r"install_additional_dev_dependencies\s*\n\s*install_rustup", content), (
        "Dockerfile must call install_rustup after install_additional_dev_dependencies"
    )


def test_dockerfile_ci_calls_install_rustup():
    """Dockerfile.ci calls install_rustup in dev installation flow (fail_to_pass)."""
    content = read_file("Dockerfile.ci")

    assert re.search(r"install_additional_dev_dependencies\s*\n\s*install_rustup", content), (
        "Dockerfile.ci must call install_rustup after install_additional_dev_dependencies"
    )


def test_install_script_calls_install_rustup():
    """install_os_dependencies.sh calls install_rustup (fail_to_pass)."""
    content = read_file("scripts/docker/install_os_dependencies.sh")

    assert re.search(r"install_additional_dev_dependencies\s*\n\s*install_rustup", content), (
        "install_os_dependencies.sh must call install_rustup"
    )


def test_dockerfile_sets_rustup_env_vars():
    """Dockerfile sets RUSTUP_HOME and CARGO_HOME environment variables (fail_to_pass)."""
    content = read_file("Dockerfile")

    assert 'RUSTUP_HOME="/usr/local/rustup"' in content, (
        "Dockerfile must set RUSTUP_HOME=/usr/local/rustup"
    )
    assert 'CARGO_HOME="/usr/local/cargo"' in content, (
        "Dockerfile must set CARGO_HOME=/usr/local/cargo"
    )


def test_dockerfile_ci_sets_rustup_env_vars():
    """Dockerfile.ci sets RUSTUP_HOME and CARGO_HOME environment variables (fail_to_pass)."""
    content = read_file("Dockerfile.ci")

    assert 'RUSTUP_HOME="/usr/local/rustup"' in content, (
        "Dockerfile.ci must set RUSTUP_HOME=/usr/local/rustup"
    )
    assert 'CARGO_HOME="/usr/local/cargo"' in content, (
        "Dockerfile.ci must set CARGO_HOME=/usr/local/cargo"
    )


def test_dockerfile_version_pinned():
    """Dockerfile pins RUSTUP_VERSION to 1.29.0 (fail_to_pass)."""
    content = read_file("Dockerfile")

    assert "RUSTUP_VERSION=${RUSTUP_VERSION:-1.29.0}" in content or \
           "RUSTUP_VERSION=1.29.0" in content, (
        "Dockerfile must pin RUSTUP_VERSION to 1.29.0"
    )


def test_dockerfile_ci_version_pinned():
    """Dockerfile.ci pins RUSTUP_VERSION to 1.29.0 (fail_to_pass)."""
    content = read_file("Dockerfile.ci")

    assert "RUSTUP_VERSION=${RUSTUP_VERSION:-1.29.0}" in content or \
           "RUSTUP_VERSION=1.29.0" in content, (
        "Dockerfile.ci must pin RUSTUP_VERSION to 1.29.0"
    )


def test_dockerfile_uses_https_tlsv12():
    """Dockerfile downloads rustup-init using secure HTTPS with TLS 1.2+ (fail_to_pass)."""
    content = read_file("Dockerfile")

    # Check for secure download pattern
    assert "--proto '=https'" in content or '--proto "=https"' in content, (
        "install_rustup must use --proto '=https' for secure download"
    )
    assert "--tlsv1.2" in content, (
        "install_rustup must use --tlsv1.2 to enforce TLS 1.2 or higher"
    )


def test_ci_workflow_timeout_updated():
    """CI workflow timeout increased for rustup installation (fail_to_pass)."""
    content = read_file(".github/workflows/additional-ci-image-checks.yml")

    # The timeout-minutes should be 25 (increased from 17)
    assert "timeout-minutes: 25" in content, (
        "check-that-image-builds-quickly job must have timeout-minutes: 25"
    )

    # The max-time should be 1320 (increased from 900)
    assert "--max-time 1320" in content, (
        "breeze shell command must use --max-time 1320"
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


def test_dockerfile_has_install_golang():
    """Dockerfile has install_golang function (existing functionality) (pass_to_pass)."""
    content = read_file("Dockerfile")
    assert "function install_golang()" in content, (
        "Dockerfile should have install_golang function (existing)"
    )


def test_dockerfile_ci_has_golang_version():
    """Dockerfile.ci has GOLANG_MAJOR_MINOR_VERSION defined (pass_to_pass)."""
    content = read_file("Dockerfile.ci")
    assert "GOLANG_MAJOR_MINOR_VERSION" in content, (
        "Dockerfile.ci should have GOLANG_MAJOR_MINOR_VERSION"
    )


# =============================================================================
# Pass-to-pass tests: Real CI commands from the repo
# =============================================================================

import subprocess


def test_repo_shellcheck_install_script():
    """Repo's shellcheck passes on install_os_dependencies.sh (pass_to_pass).

    This runs the same shellcheck check that the repo's pre-commit hooks run.
    """
    # First install shellcheck if not present
    install_result = subprocess.run(
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
        ["pip", "install", "-q", "yamllint"],
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
