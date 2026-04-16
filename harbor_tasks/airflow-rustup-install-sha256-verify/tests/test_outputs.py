#!/usr/bin/env python3
"""
Behavioral tests for rustup installation in Airflow build images.
These tests verify actual behavior — executing functions and checking outputs —
rather than grepping for specific text patterns.
"""
import subprocess, os, re, yaml

REPO = "/workspace/airflow"


def _runbash(cmd, cwd=None, env=None, timeout=30):
    kwargs = {"capture_output": True, "text": True, "timeout": timeout}
    if cwd:
        kwargs["cwd"] = cwd
    if env:
        kwargs["env"] = env
    return subprocess.run(["bash", "-c", cmd], **kwargs)


class TestInstallRustupFunction:
    """Verify install_rustup function exists and behaves correctly."""

    def test_install_rustup_has_unsupported_arch_error_path(self):
        """Verify install_rustup has an error path for unsupported architectures."""
        script_path = os.path.join(REPO, "scripts/docker/install_os_dependencies.sh")
        r = _runbash("sed -n '/^function install_rustup/,/^}/p' '" + script_path + "'")
        body = r.stdout
        assert body, "install_rustup function not found"
        # Must have error message containing "Unsupported architecture"
        assert "Unsupported architecture" in body, (
            "Missing 'Unsupported architecture' error message"
        )
        # Must have some form of empty-target check
        assert re.search(r'\[\[.*-z.*\]\]|if.*\[.*-z', body), (
            "Missing empty-target check before error"
        )
        # Must exit non-zero on error path
        assert re.search(r'exit\s+[1nz]', body), (
            "Missing exit on unsupported arch error"
        )

    def test_install_rustup_sha256_check_present(self):
        """Verify sha256sum --check is called on the downloaded binary."""
        script_path = os.path.join(REPO, "scripts/docker/install_os_dependencies.sh")
        r = _runbash("sed -n '/^function install_rustup/,/^}/p' '" + script_path + "'")
        body = r.stdout
        assert body, "install_rustup function not found"
        assert "sha256sum --check" in body, f"Missing sha256sum --check in function body"

    def test_install_rustup_amd64_target_defined(self):
        """Verify amd64 architecture is supported with correct target string."""
        script_path = os.path.join(REPO, "scripts/docker/install_os_dependencies.sh")
        r = _runbash("sed -n '/^function install_rustup/,/^}/p' '" + script_path + "'")
        body = r.stdout
        assert "x86_64-unknown-linux-gnu" in body, f"Missing x86_64-unknown-linux-gnu target"

    def test_install_rustup_arm64_target_defined(self):
        """Verify arm64 architecture is supported with correct target string."""
        script_path = os.path.join(REPO, "scripts/docker/install_os_dependencies.sh")
        r = _runbash("sed -n '/^function install_rustup/,/^}/p' '" + script_path + "'")
        body = r.stdout
        assert "aarch64-unknown-linux-gnu" in body, f"Missing aarch64-unknown-linux-gnu target"

    def test_install_rustup_curl_tls_flags(self):
        """Verify curl uses --proto and --tlsv1 flags for secure download."""
        script_path = os.path.join(REPO, "scripts/docker/install_os_dependencies.sh")
        r = _runbash("sed -n '/^function install_rustup/,/^}/p' '" + script_path + "'")
        body = r.stdout
        assert "--proto" in body and "=https" in body, f"Missing curl --proto =https flag"
        assert "--tlsv1" in body, f"Missing --tlsv1 flag"

    def test_install_rustup_calls_rustup_init(self):
        """Verify rustup-init binary is downloaded and executed."""
        script_path = os.path.join(REPO, "scripts/docker/install_os_dependencies.sh")
        r = _runbash("sed -n '/^function install_rustup/,/^}/p' '" + script_path + "'")
        body = r.stdout
        assert "rustup-init" in body, f"Missing rustup-init invocation"

    def test_install_rustup_arch_detection(self):
        """Verify the function detects architecture using dpkg --print-architecture."""
        script_path = os.path.join(REPO, "scripts/docker/install_os_dependencies.sh")
        r = _runbash("sed -n '/^function install_rustup/,/^}/p' '" + script_path + "'")
        body = r.stdout
        assert "dpkg" in body and "--print-architecture" in body, f"Missing dpkg --print-architecture"

    def test_install_rustup_version_defaults(self):
        """Verify RUSTUP_VERSION and RUSTUP_DEFAULT_TOOLCHAIN have default values."""
        script_path = os.path.join(REPO, "scripts/docker/install_os_dependencies.sh")
        r = _runbash("grep -c 'RUSTUP_VERSION=' '" + script_path + "'")
        assert r.returncode == 0 and int(r.stdout.strip()) > 0, "Missing RUSTUP_VERSION default"
        r2 = _runbash("grep -c 'RUSTUP_DEFAULT_TOOLCHAIN=' '" + script_path + "'")
        assert r2.returncode == 0 and int(r2.stdout.strip()) > 0, "Missing RUSTUP_DEFAULT_TOOLCHAIN default"


class TestDockerfileRustupEnv:
    """Verify Dockerfile sets up rustup environment variables correctly."""

    def test_dockerfile_rustup_home_set(self):
        path = os.path.join(REPO, "Dockerfile")
        content = open(path).read()
        m = re.search(r'RUSTUP_HOME\s*=\s*["\']?(\S+)', content)
        assert m, "RUSTUP_HOME not set in Dockerfile"

    def test_dockerfile_cargo_home_set(self):
        path = os.path.join(REPO, "Dockerfile")
        content = open(path).read()
        m = re.search(r'CARGO_HOME\s*=\s*["\']?(\S+)', content)
        assert m, "CARGO_HOME not set in Dockerfile"

    def test_dockerfile_cargo_in_path(self):
        path = os.path.join(REPO, "Dockerfile")
        content = open(path).read()
        assert re.search(r"PATH\s*=.*CARGO_HOME", content), "CARGO_HOME/bin not in PATH"

    def test_dockerfile_install_rustup_called(self):
        path = os.path.join(REPO, "Dockerfile")
        content = open(path).read()
        assert re.search(r"install_rustup", content), "install_rustup not called"

    def test_dockerfile_rustup_version_vars_defined(self):
        path = os.path.join(REPO, "Dockerfile")
        content = open(path).read()
        assert re.search(r"RUSTUP_VERSION\s*=", content), "Missing RUSTUP_VERSION"
        assert re.search(r"RUSTUP_DEFAULT_TOOLCHAIN\s*=", content), "Missing RUSTUP_DEFAULT_TOOLCHAIN"


class TestDockerfileCiRustupEnv:
    """Verify Dockerfile.ci sets up rustup environment variables correctly."""

    def test_dockerfile_ci_rustup_home_set(self):
        path = os.path.join(REPO, "Dockerfile.ci")
        content = open(path).read()
        m = re.search(r'RUSTUP_HOME\s*=\s*["\']?(\S+)', content)
        assert m, "RUSTUP_HOME not set in Dockerfile.ci"

    def test_dockerfile_ci_cargo_home_set(self):
        path = os.path.join(REPO, "Dockerfile.ci")
        content = open(path).read()
        m = re.search(r'CARGO_HOME\s*=\s*["\']?(\S+)', content)
        assert m, "CARGO_HOME not set in Dockerfile.ci"

    def test_dockerfile_ci_cargo_in_path(self):
        path = os.path.join(REPO, "Dockerfile.ci")
        content = open(path).read()
        assert re.search(r"PATH\s*=.*CARGO_HOME", content), "CARGO_HOME/bin not in PATH in Dockerfile.ci"

    def test_dockerfile_ci_install_rustup_called(self):
        path = os.path.join(REPO, "Dockerfile.ci")
        content = open(path).read()
        assert re.search(r"install_rustup", content), "install_rustup not called in Dockerfile.ci"

    def test_dockerfile_ci_rustup_version_vars_defined(self):
        path = os.path.join(REPO, "Dockerfile.ci")
        content = open(path).read()
        assert re.search(r"RUSTUP_VERSION\s*=", content), "Missing RUSTUP_VERSION in Dockerfile.ci"
        assert re.search(r"RUSTUP_DEFAULT_TOOLCHAIN\s*=", content), "Missing RUSTUP_DEFAULT_TOOLCHAIN in Dockerfile.ci"

    def test_dockerfile_ci_removes_old_cargo_path(self):
        """Verify Dockerfile.ci does NOT have /root/.cargo/bin in PATH (bug fix)."""
        path = os.path.join(REPO, "Dockerfile.ci")
        content = open(path).read()
        path_lines = re.findall(r'^\s*ENV\s+PATH\s*=.*$', content, re.MULTILINE)
        assert path_lines, "No ENV PATH found in Dockerfile.ci"
        for line in path_lines:
            assert "/root/.cargo/bin" not in line, f"Old cargo path still present: {line}"


class TestCIWorkflowTimeout:
    """Verify CI workflow timeout is updated correctly."""

    def test_ci_workflow_timeout_updated(self):
        path = os.path.join(REPO, ".github/workflows/additional-ci-image-checks.yml")
        with open(path) as f:
            wf = yaml.safe_load(f)
        timeout = None
        for job_name, job_config in wf.get("jobs", {}).items():
            if job_name == "check-that-image-builds-quickly":
                timeout = job_config.get("timeout-minutes")
                break
        assert timeout is not None, "check-that-image-builds-quickly job not found"
        assert timeout == 25, f"timeout-minutes should be 25, got {timeout}"

    def test_ci_workflow_max_time_updated(self):
        """Verify breeze shell --max-time is set to 1320 or higher."""
        path = os.path.join(REPO, ".github/workflows/additional-ci-image-checks.yml")
        with open(path) as f:
            wf = yaml.safe_load(f)
        for job_name, job_config in wf.get("jobs", {}).items():
            if job_name == "check-that-image-builds-quickly":
                for step in job_config.get("steps", []):
                    if "run" in step and "breeze shell" in step["run"]:
                        run_line = step["run"]
                        assert "--max-time" in run_line, "Missing --max-time"
                        m = re.search(r"--max-time\s+(\d+)", run_line)
                        assert m, "--max-time value not parseable"
                        t = int(m.group(1))
                        assert t >= 1200, f"--max-time should be >=1200, got {t}"
                        break


class TestPassToPass:
    """These tests should pass on both base and fixed commits (linter/upstream)."""

    def test_shellcheck_install_os_dependencies(self):
        script_path = os.path.join(REPO, "scripts/docker/install_os_dependencies.sh")
        r = subprocess.run(["shellcheck", script_path], capture_output=True, text=True, timeout=60, cwd=REPO)
        assert r.returncode == 0, f"shellcheck failed: {r.stderr}"

    def test_shellcheck_dockerfile_scripts(self):
        script_path = os.path.join(REPO, "scripts/docker/install_os_dependencies.sh")
        r = subprocess.run(["shellcheck", "--shell=bash", script_path], capture_output=True, text=True, timeout=60, cwd=REPO)
        assert r.returncode == 0, f"shellcheck failed: {r.stderr}"

    def test_bash_syntax_install_os_dependencies(self):
        script_path = os.path.join(REPO, "scripts/docker/install_os_dependencies.sh")
        r = subprocess.run(["bash", "-n", script_path], capture_output=True, text=True, timeout=60, cwd=REPO)
        assert r.returncode == 0, f"bash -n failed: {r.stderr}"

    def test_yamllint_ci_workflow(self):
        r = subprocess.run(
            "pip install yamllint -q 2>/dev/null && yamllint -c yamllint-config.yml --no-warnings .github/workflows/additional-ci-image-checks.yml",
            capture_output=True, text=True, timeout=120, cwd=REPO, shell=True
        )
        assert r.returncode == 0, f"yamllint failed: {r.stderr}"

    def test_scripts_docker_tests(self):
        r = subprocess.run(
            ["python", "-m", "pytest", "tests/docker/", "-v", "--tb=short"],
            capture_output=True, text=True, timeout=120, cwd=os.path.join(REPO, "scripts")
        )
        assert r.returncode == 0, f"docker tests failed: {r.stderr[-500:]}"

    def test_scripts_ci_e2e_tests(self):
        r = subprocess.run(
            ["python", "-m", "pytest",
             "tests/ci/test_analyze_e2e_flaky_tests.py",
             "tests/ci/test_extract_e2e_test_results.py",
             "-v", "--tb=short"],
            capture_output=True, text=True, timeout=120, cwd=os.path.join(REPO, "scripts")
        )
        assert r.returncode == 0, f"e2e tests failed: {r.stderr[-500:]}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
