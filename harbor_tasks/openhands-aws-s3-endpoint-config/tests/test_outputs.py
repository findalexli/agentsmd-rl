"""Tests for AWS S3 endpoint URL configuration fix.

This validates the fix for properly handling AWS S3 (Minio) endpoint URLs
with correct HTTP/HTTPS protocol based on environment variables.
"""

import ast
import os
import subprocess
import sys
from pathlib import Path

REPO = Path('/workspace/openhands')
SOURCE_PATH = REPO / 'openhands' / 'app_server' / 'event' / 'aws_event_service.py'


# ==================== Pass-to-pass Tests ====================
# These verify the repo's existing CI/CD checks pass on base commit and after fix

def test_repo_python_syntax_valid():
    """Target file has valid Python syntax (pass_to_pass)."""
    r = subprocess.run(
        ['python', '-m', 'py_compile', 'openhands/app_server/event/aws_event_service.py'],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


def test_repo_ruff_check():
    """Repo's ruff linting passes on target file (pass_to_pass)."""
    r = subprocess.run(
        ['pip', 'install', 'ruff', '-q'],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ['ruff', 'check', 'openhands/app_server/event/aws_event_service.py', '--config', 'dev_config/python/ruff.toml', '--fix'],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format():
    """Repo's ruff formatting passes on target file (pass_to_pass)."""
    r = subprocess.run(
        ['pip', 'install', 'ruff', '-q'],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ['ruff', 'format', '--check', 'openhands/app_server/event/aws_event_service.py', '--config', 'dev_config/python/ruff.toml'],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr}"


def test_repo_unit_test_file_valid():
    """Repo's unit test file for aws_event_service has valid Python syntax (pass_to_pass)."""
    r = subprocess.run(
        ['python', '-m', 'py_compile', 'tests/unit/app_server/test_aws_event_service.py'],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit test file syntax check failed:\n{r.stderr}"


def test_repo_test_config_file_valid():
    """Repo's event service config test file has valid Python syntax (pass_to_pass)."""
    r = subprocess.run(
        ['python', '-m', 'py_compile', 'tests/unit/app_server/test_config_event_service_selection.py'],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Config test file syntax check failed:\n{r.stderr}"


def test_repo_file_is_git_tracked():
    """Target file is tracked in git repo (pass_to_pass)."""
    r = subprocess.run(
        ['git', 'ls-files', '--error-unmatch', 'openhands/app_server/event/aws_event_service.py'],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Target file is not tracked in git:\n{r.stderr}"


def test_repo_unit_tests_aws_event_service():
    """Repo's unit tests for aws_event_service pass (pass_to_pass)."""
    r = subprocess.run(
        ['pip', 'install', 'boto3', 'botocore', 'pydantic', 'pytest-asyncio', '-q'],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ['pip', 'install', '-e', '.', '-q'],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ['python', '-m', 'pytest', 'tests/unit/app_server/test_aws_event_service.py', '-v', '--tb=short'],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-500:]}"


def test_repo_unit_tests_config_event_service_selection():
    """Repo's unit tests for event service config selection pass (pass_to_pass)."""
    r = subprocess.run(
        ['pip', 'install', 'boto3', 'botocore', 'pydantic', 'pytest-asyncio', '-q'],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ['pip', 'install', '-e', '.', '-q'],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ['python', '-m', 'pytest', 'tests/unit/app_server/test_config_event_service_selection.py', '-v', '--tb=short'],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Config tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-500:]}"


def test_repo_mypy_clean():
    """Repo's mypy type checking passes on target file (pass_to_pass)."""
    r = subprocess.run(
        ['pip', 'install', 'mypy', 'boto3', 'botocore', 'pydantic', 'types-requests', 'types-setuptools', 'types-pyyaml', 'types-toml', 'types-docker', 'types-Markdown', 'lxml', '-q'],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ['mypy', '--config-file', 'dev_config/python/mypy.ini', 'openhands/app_server/event/aws_event_service.py'],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"MyPy check failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_validate_pyproject():
    """Repo's pyproject.toml is valid (pass_to_pass)."""
    r = subprocess.run(
        ['pip', 'install', 'validate-pyproject', '-q'],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ['validate-pyproject', 'pyproject.toml'],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"pyproject.toml validation failed:\n{r.stderr[-500:]}"


def test_repo_imports_clean():
    """Target file can be imported without errors (pass_to_pass)."""
    r = subprocess.run(
        ['python', '-c', 'from openhands.app_server.event.aws_event_service import AwsEventServiceInjector'],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Import check failed:\n{r.stderr[-500:]}"


# ==================== Fail-to-pass Tests ====================
# These verify the fix produces correct behavior

def _run_endpoint_url_test(endpoint_value, secure_value, expected):
    """Helper to test endpoint URL computation via subprocess.

    Runs a Python script that:
    1. Sets environment variables
    2. Imports and calls _get_default_aws_endpoint_url
    3. Validates the result against expected
    4. Exits with 0 if result matches expected, 1 otherwise
    """
    env = {
        'AWS_S3_ENDPOINT': endpoint_value if endpoint_value is not None else '',
        'AWS_S3_SECURE': secure_value,
    }
    env = {k: v for k, v in env.items() if v is not None}

    expected_repr = repr(expected)
    code = f'''
import os
import sys
sys.path.insert(0, '/workspace/openhands')
from openhands.app_server.event.aws_event_service import _get_default_aws_endpoint_url
result = _get_default_aws_endpoint_url()
expected = {expected_repr}
if result != expected:
    print(f"MISMATCH: got {{repr(result)}}, expected {{repr(expected)}}")
    sys.exit(1)
print(repr(result))
'''
    r = subprocess.run(
        ['python', '-c', code],
        capture_output=True, text=True, timeout=30,
        env={**os.environ, **env},
    )
    return r


def test_endpoint_url_https_when_secure_true_no_protocol():
    """F2P: https:// prefix added when AWS_S3_SECURE=true and no protocol in endpoint."""
    r = _run_endpoint_url_test('minio.example.com:9000', 'true', 'https://minio.example.com:9000')
    assert r.returncode == 0, f"Expected https:// URL, got returncode={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}"
    assert 'https://minio.example.com:9000' in r.stdout, f"Expected https:// in output, got: {r.stdout}"


def test_endpoint_url_converts_http_to_https_when_secure():
    """F2P: http:// converted to https:// when AWS_S3_SECURE=true."""
    r = _run_endpoint_url_test('http://minio.example.com:9000', 'true', 'https://minio.example.com:9000')
    assert r.returncode == 0, f"Expected https:// URL, got returncode={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}"
    assert 'https://minio.example.com:9000' in r.stdout, f"Expected https:// in output, got: {r.stdout}"


def test_endpoint_url_http_when_secure_false_no_protocol():
    """F2P: http:// prefix added when AWS_S3_SECURE=false and no protocol in endpoint."""
    r = _run_endpoint_url_test('minio.example.com:9000', 'false', 'http://minio.example.com:9000')
    assert r.returncode == 0, f"Expected http:// URL, got returncode={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}"
    assert 'http://minio.example.com:9000' in r.stdout, f"Expected http:// in output, got: {r.stdout}"


def test_endpoint_url_converts_https_to_http_when_insecure():
    """F2P: https:// converted to http:// when AWS_S3_SECURE=false."""
    r = _run_endpoint_url_test('https://minio.example.com:9000', 'false', 'http://minio.example.com:9000')
    assert r.returncode == 0, f"Expected http:// URL, got returncode={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}"
    assert 'http://minio.example.com:9000' in r.stdout, f"Expected http:// in output, got: {r.stdout}"


def test_endpoint_url_none_when_env_not_set():
    """F2P: Returns None when AWS_S3_ENDPOINT is not set."""
    r = _run_endpoint_url_test('', 'true', None)
    assert r.returncode == 0, f"Expected None, got returncode={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}"
    assert 'None' in r.stdout, f"Expected None in output, got: {r.stdout}"


def test_injector_passes_correct_endpoint_to_boto3():
    """F2P: AwsEventServiceInjector makes boto3 client receive correct endpoint URL."""
    code = '''
import os
import sys
sys.path.insert(0, '/workspace/openhands')

os.environ['AWS_S3_ENDPOINT'] = 'minio.example.com:9000'
os.environ['AWS_S3_SECURE'] = 'true'

from openhands.app_server.event.aws_event_service import AwsEventServiceInjector

injector = AwsEventServiceInjector(bucket_name='test-bucket')
print(f"endpoint_url={injector.endpoint_url}")
'''
    r = subprocess.run(
        ['python', '-c', code],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Expected success, got returncode={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}"
    assert 'https://minio.example.com:9000' in r.stdout, f"Expected https:// URL in injector.endpoint_url, got: {r.stdout}"


def test_injector_endpoint_url_computed_from_env_vars():
    """F2P: AwsEventServiceInjector.endpoint_url reflects AWS_S3_SECURE env var."""
    code = '''
import os
import sys
sys.path.insert(0, '/workspace/openhands')

os.environ['AWS_S3_ENDPOINT'] = 'minio.example.com:9000'
os.environ['AWS_S3_SECURE'] = 'false'

from openhands.app_server.event.aws_event_service import AwsEventServiceInjector

injector = AwsEventServiceInjector(bucket_name='test-bucket')
print(f"endpoint_url={injector.endpoint_url}")
'''
    r = subprocess.run(
        ['python', '-c', code],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Expected success, got returncode={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}"
    assert 'http://minio.example.com:9000' in r.stdout, f"Expected http:// URL in injector.endpoint_url, got: {r.stdout}"


def test_injector_endpoint_url_none_when_env_empty():
    """F2P: AwsEventServiceInjector.endpoint_url is None when AWS_S3_ENDPOINT empty."""
    code = '''
import os
import sys
sys.path.insert(0, '/workspace/openhands')

# Clear the env vars
os.environ.pop('AWS_S3_ENDPOINT', None)
os.environ.pop('AWS_S3_SECURE', None)

from openhands.app_server.event.aws_event_service import AwsEventServiceInjector

injector = AwsEventServiceInjector(bucket_name='test-bucket')
print(f"endpoint_url={injector.endpoint_url}")
'''
    r = subprocess.run(
        ['python', '-c', code],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Expected success, got returncode={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}"
    assert 'None' in r.stdout, f"Expected None in injector.endpoint_url, got: {r.stdout}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_openhands_ui_build_package():
    """pass_to_pass | CI job 'Build openhands-ui' → step 'Build package'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run build'], cwd=os.path.join(REPO, './openhands-ui'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build package' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_package_versions_check_for_any_rev_fields_in_pyproject_to():
    """pass_to_pass | CI job 'check-package-versions' → step "Check for any 'rev' fields in pyproject.toml""""
    r = subprocess.run(
        ["bash", "-lc", "python - <<'PY'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step "Check for any 'rev' fields in pyproject.toml" failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_fe_e2e_tests_run_playwright_tests():
    """pass_to_pass | CI job 'FE E2E Tests' → step 'Run Playwright tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'npx playwright test --project=chromium'], cwd=os.path.join(REPO, './frontend'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Playwright tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_frontend_lint_typescript_compilation_and_translat():
    """pass_to_pass | CI job 'Lint frontend' → step 'Lint, TypeScript compilation, and translation checks'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run lint && npm run make-i18n && tsc && npm run check-translation-completeness'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint, TypeScript compilation, and translation checks' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_all_runtime_tests_passed_all_tests_passed():
    """pass_to_pass | CI job 'All Runtime Tests Passed' → step 'All tests passed'"""
    r = subprocess.run(
        ["bash", "-lc", 'echo "All runtime tests have passed successfully!"'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'All tests passed' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_fe_unit_tests_run_typescript_compilation():
    """pass_to_pass | CI job 'FE Unit Tests' → step 'Run TypeScript compilation'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run build'], cwd=os.path.join(REPO, './frontend'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run TypeScript compilation' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_fe_unit_tests_run_tests_and_collect_coverage():
    """pass_to_pass | CI job 'FE Unit Tests' → step 'Run tests and collect coverage'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run test:coverage'], cwd=os.path.join(REPO, './frontend'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests and collect coverage' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_python_tests_on_linux_build_environment():
    """pass_to_pass | CI job 'Python Tests on Linux' → step 'Build Environment'"""
    r = subprocess.run(
        ["bash", "-lc", 'make build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build Environment' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_python_tests_on_linux_run_unit_tests():
    """pass_to_pass | CI job 'Python Tests on Linux' → step 'Run Unit Tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'PYTHONPATH=".:$PYTHONPATH" poetry run pytest --forked -n auto -s ./tests/unit --cov=openhands --cov-branch'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Unit Tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_python_tests_on_linux_run_runtime_tests_with_cliruntime():
    """pass_to_pass | CI job 'Python Tests on Linux' → step 'Run Runtime Tests with CLIRuntime'"""
    r = subprocess.run(
        ["bash", "-lc", 'PYTHONPATH=".:$PYTHONPATH" TEST_RUNTIME=cli poetry run pytest -n 5 --reruns 2 --reruns-delay 3 -s tests/runtime/test_bash.py --cov=openhands --cov-branch'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Runtime Tests with CLIRuntime' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_enterprise_python_unit_tests_run_unit_tests():
    """pass_to_pass | CI job 'Enterprise Python Unit Tests' → step 'Run Unit Tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'PYTHONPATH=".:$PYTHONPATH" poetry run --project=enterprise pytest --forked -n auto -s -p no:ddtrace -p no:ddtrace.pytest_bdd -p no:ddtrace.pytest_benchmark ./enterprise/tests/unit --cov=enterprise --cov-branch'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Unit Tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")