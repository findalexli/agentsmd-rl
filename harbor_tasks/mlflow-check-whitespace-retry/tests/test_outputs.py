"""Behavior tests for the retry logic added to dev/check_whitespace_only.py.

Strategy: load the script as a Python module, mock urllib.request.urlopen
and time.sleep, then assert behavior of get_pr_diff() and github_api_request()
under transient and permanent failures.
"""

import importlib.util
import subprocess
import sys
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO = Path("/workspace/mlflow")
SCRIPT = REPO / "dev" / "check_whitespace_only.py"
MODNAME = "_cwo_under_test"


def _load_fresh():
    """Re-load the script as a module from disk for test isolation."""
    sys.modules.pop(MODNAME, None)
    spec = importlib.util.spec_from_file_location(MODNAME, str(SCRIPT))
    module = importlib.util.module_from_spec(spec)
    sys.modules[MODNAME] = module
    spec.loader.exec_module(module)
    return module


def _resp_cm(body: str):
    """A context-manager mock that mimics urlopen()'s return value."""
    resp = MagicMock()
    resp.read.return_value = body.encode("utf-8")
    cm = MagicMock()
    cm.__enter__.return_value = resp
    cm.__exit__.return_value = False
    return cm


def _http_err(status: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        url="http://example.com",
        code=status,
        msg=f"{status}",
        hdrs={},  # type: ignore[arg-type]
        fp=None,
    )


def _url_err():
    return urllib.error.URLError("connection refused")


# ---------------------------------------------------------------------------
# Fail-to-pass tests (behavior added by the PR)
# ---------------------------------------------------------------------------


def test_get_pr_diff_retries_on_5xx_then_succeeds():
    """A transient 5xx should be retried; the eventual success body is returned."""
    mod = _load_fresh()
    fake = MagicMock(side_effect=[_http_err(503), _resp_cm("THE_DIFF")])
    with patch.object(mod.urllib.request, "urlopen", fake), \
         patch("time.sleep"):
        result = mod.get_pr_diff("o", "r", 1)
    assert result == "THE_DIFF"
    assert fake.call_count == 2


def test_github_api_request_retries_on_5xx_then_succeeds():
    """github_api_request must retry transient 5xx errors too."""
    mod = _load_fresh()
    fake = MagicMock(side_effect=[_http_err(502), _resp_cm("API_BODY")])
    with patch.object(mod.urllib.request, "urlopen", fake), \
         patch("time.sleep"):
        result = mod.github_api_request("http://example.com", "application/json")
    assert result == "API_BODY"
    assert fake.call_count == 2


def test_get_pr_diff_does_not_retry_on_4xx():
    """A 4xx error is permanent and must be raised immediately, no retries."""
    mod = _load_fresh()
    fake = MagicMock(side_effect=[_http_err(404), _resp_cm("SHOULD_NOT_BE_USED")])
    with patch.object(mod.urllib.request, "urlopen", fake), \
         patch("time.sleep") as sleep_mock:
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            mod.get_pr_diff("o", "r", 1)
    assert exc_info.value.code == 404
    assert fake.call_count == 1
    assert sleep_mock.call_count == 0


def test_github_api_request_does_not_retry_on_403():
    """github_api_request must propagate 4xx (e.g., 403) without retry."""
    mod = _load_fresh()
    fake = MagicMock(side_effect=[_http_err(403)])
    with patch.object(mod.urllib.request, "urlopen", fake), \
         patch("time.sleep") as sleep_mock:
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            mod.github_api_request("http://example.com", "application/json")
    assert exc_info.value.code == 403
    assert fake.call_count == 1
    assert sleep_mock.call_count == 0


def test_retries_on_urlerror():
    """A non-HTTP URLError (e.g., DNS / connection refused) is also retryable."""
    mod = _load_fresh()
    fake = MagicMock(side_effect=[_url_err(), _resp_cm("RECOVERED")])
    with patch.object(mod.urllib.request, "urlopen", fake), \
         patch("time.sleep"):
        result = mod.get_pr_diff("o", "r", 1)
    assert result == "RECOVERED"
    assert fake.call_count == 2


def test_max_three_attempts_then_raises():
    """If all three attempts fail with 5xx, the final HTTPError is raised."""
    mod = _load_fresh()
    fake = MagicMock(side_effect=[_http_err(503), _http_err(503), _http_err(503)])
    with patch.object(mod.urllib.request, "urlopen", fake), \
         patch("time.sleep") as sleep_mock:
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            mod.get_pr_diff("o", "r", 1)
    assert exc_info.value.code == 503
    assert fake.call_count == 3
    # Sleeps happen *between* attempts: 3 attempts -> 2 sleeps.
    assert sleep_mock.call_count == 2


def test_exponential_backoff_delays():
    """Backoff doubles: first sleep is 1 second, second is 2 seconds."""
    mod = _load_fresh()
    fake = MagicMock(
        side_effect=[_http_err(503), _http_err(503), _resp_cm("OK")]
    )
    with patch.object(mod.urllib.request, "urlopen", fake), \
         patch("time.sleep") as sleep_mock:
        result = mod.get_pr_diff("o", "r", 1)
    assert result == "OK"
    delays = [c.args[0] for c in sleep_mock.call_args_list]
    assert delays == [1, 2], f"expected [1, 2], got {delays}"


def test_non_retryable_exception_propagates_immediately():
    """An exception type that is not URLError/HTTPError must not trigger retry."""
    mod = _load_fresh()
    fake = MagicMock(side_effect=[ValueError("boom")])
    with patch.object(mod.urllib.request, "urlopen", fake), \
         patch("time.sleep") as sleep_mock:
        with pytest.raises(ValueError):
            mod.get_pr_diff("o", "r", 1)
    assert fake.call_count == 1
    assert sleep_mock.call_count == 0


# ---------------------------------------------------------------------------
# Pass-to-pass tests (behavior that should remain unchanged)
# ---------------------------------------------------------------------------


def test_parse_diff_detects_whitespace_only_file():
    """parse_diff still flags a file whose only diff lines are blank."""
    mod = _load_fresh()
    diff = (
        "diff --git a/foo.py b/foo.py\n"
        "--- a/foo.py\n"
        "+++ b/foo.py\n"
        "@@ -1,3 +1,2 @@\n"
        " def foo():\n"
        "-\n"
        " pass\n"
    )
    assert mod.parse_diff(diff) == ["foo.py"]


def test_parse_diff_ignores_real_changes():
    """parse_diff returns no files when changes are non-whitespace."""
    mod = _load_fresh()
    diff = (
        "diff --git a/foo.py b/foo.py\n"
        "--- a/foo.py\n"
        "+++ b/foo.py\n"
        "@@ -1,2 +1,2 @@\n"
        "-def foo():\n"
        "+def bar():\n"
        " pass\n"
    )
    assert mod.parse_diff(diff) == []


def test_cli_help_runs():
    """The --help interface remains intact and exits 0."""
    r = subprocess.run(
        [sys.executable, "dev/check_whitespace_only.py", "--help"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, r.stderr
    assert "--repo" in r.stdout
    assert "--pr" in r.stdout


def test_ruff_check_passes_on_target_file():
    """The target file lints cleanly under the repo's ruff config."""
    r = subprocess.run(
        ["ruff", "check", "--no-cache", "dev/check_whitespace_only.py"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"ruff failures:\n{r.stdout}\n{r.stderr}"


def test_ruff_format_check_passes_on_target_file():
    """The target file is formatted per the repo's ruff format rules."""
    r = subprocess.run(
        ["ruff", "format", "--check", "--no-cache", "dev/check_whitespace_only.py"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"ruff format diff:\n{r.stdout}\n{r.stderr}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_lint_run_pre_commit():
    """pass_to_pass | CI job 'lint' → step 'Run pre-commit'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --no-sync pre-commit run --all-files'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run pre-commit' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_test_clint():
    """pass_to_pass | CI job 'lint' → step 'Test clint'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --no-sync pytest dev/clint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test clint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_check_function_signatures():
    """pass_to_pass | CI job 'lint' → step 'Check function signatures'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --no-project dev/check_function_signatures.py'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check function signatures' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_check_whitespace_only_changes():
    """pass_to_pass | CI job 'lint' → step 'Check whitespace-only changes'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --no-project dev/check_whitespace_only.py \\\n  --repo $REPO \\\n  --pr $PR_NUMBER'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check whitespace-only changes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_check_uv_lock_changes():
    """pass_to_pass | CI job 'lint' → step 'Check uv.lock changes'"""
    r = subprocess.run(
        ["bash", "-lc", 'files=$(gh pr view "${PR_NUMBER}" --repo "${REPO}" --json files --jq \'.files[].path\')\nif echo "$files" | grep -q \'^uv.lock$\' && echo "$files" | grep -q \'^pyproject.toml$\'; then\n  echo \'::warning file=pyproject.toml,line=1,col=1::[Non-blocking]\' \\\n       \'Run `uv lock --upgrade-package <package>` if this PR should update package versions.\' \\\n       \'`uv lock` alone won\'"\'"\'t bump them.\'\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check uv.lock changes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_check_unused_media():
    """pass_to_pass | CI job 'lint' → step 'Check unused media'"""
    r = subprocess.run(
        ["bash", "-lc", 'dev/find-unused-media.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check unused media' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_build_ui():
    """pass_to_pass | CI job 'build' → step 'Build UI'"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn install --immutable && yarn build'], cwd=os.path.join(REPO, 'mlflow/server/js'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build UI' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_build_distribution_files():
    """pass_to_pass | CI job 'build' → step 'Build distribution files'"""
    r = subprocess.run(
        ["bash", "-lc", '# if workflow_dispatch is triggered, use the specified ref\nif [ "$EVENT_NAME" == "workflow_dispatch" ]; then\n  SHA_OPT="--sha $(git rev-parse HEAD)"\nelse\n  SHA_OPT=""\nfi\n\npython dev/build.py --package-type "$MATRIX_TYPE" $SHA_OPT\n\n# List distribution files and check their file sizes\nls -lh dist\n\n# Set step outputs\nsdist_path=$(find dist -type f -name "*.tar.gz")\nwheel_path=$(find dist -type f -name "*.whl")\nwheel_name=$(basename $wheel_path)\nwheel_size=$(stat -c %s $wheel_path)\necho "sdist-path=${sdist_path}" >> $GITHUB_OUTPUT\necho "wheel-path=${wheel_path}" >> $GITHUB_OUTPUT\necho "wheel-name=${wheel_name}" >> $GITHUB_OUTPUT\necho "wheel-size=${wheel_size}" >> $GITHUB_OUTPUT'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build distribution files' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_run_twine_check():
    """pass_to_pass | CI job 'build' → step 'Run twine check'"""
    r = subprocess.run(
        ["bash", "-lc", 'twine check --strict $WHEEL_PATH'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run twine check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_test_installation_from_tarball():
    """pass_to_pass | CI job 'build' → step 'Test installation from tarball'"""
    r = subprocess.run(
        ["bash", "-lc", 'python -c "import mlflow; print(mlflow.__version__)" && python -c "from mlflow import *"'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test installation from tarball' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_test_installation_from_github():
    """pass_to_pass | CI job 'build' → step 'Test installation from GitHub'"""
    r = subprocess.run(
        ["bash", "-lc", 'if [ "$MATRIX_TYPE" == "skinny" ]; then\n  URL="git+https://github.com/${REPO}.git@${REF}#subdirectory=libs/skinny"\nelif [ "$MATRIX_TYPE" == "tracing" ]; then\n  URL="git+https://github.com/${REPO}.git@${REF}#subdirectory=libs/tracing"\nelse\n  URL="git+https://github.com/${REPO}.git@${REF}"\nfi\n\nuv run --isolated --no-project --with $URL python -I -c \'import mlflow; print(mlflow.__version__)\''], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test installation from GitHub' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_test_dev_install_skinny_sh():
    """pass_to_pass | CI job 'build' → step 'Test dev/install-skinny.sh'"""
    r = subprocess.run(
        ["bash", "-lc", 'dev/install-skinny.sh pull/$PR_NUMBER/merge'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test dev/install-skinny.sh' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")