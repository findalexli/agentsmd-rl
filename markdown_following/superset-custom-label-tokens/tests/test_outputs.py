"""
Tests verify that the agent has implemented custom label theme tokens
(labelPublished*, labelDraft*, labelDatasetPhysical*, labelDatasetVirtual*).

Strategy: copy gold test fixtures into the repo at the right paths, then run
jest on those files. The new test files exercise the new theme-token behavior;
they fail at base because the source doesn't reference the tokens, and pass
when the agent's implementation matches the gold patch.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

REPO = "/workspace/superset"
FRONTEND = f"{REPO}/superset-frontend"
LABEL_DIR = f"{FRONTEND}/packages/superset-ui-core/src/components/Label/reusable"
THEME_UTILS_DIR = f"{FRONTEND}/src/theme/utils"
GOLD_DIR = "/tests/gold_tests"

JEST_BIN = f"{FRONTEND}/node_modules/.bin/jest"


def _stage_gold_tests():
    """Copy gold test fixtures into the repo; idempotent."""
    shutil.copy(f"{GOLD_DIR}/DatasetTypeLabel.test.tsx",
                f"{LABEL_DIR}/DatasetTypeLabel.test.tsx")
    shutil.copy(f"{GOLD_DIR}/PublishedLabel.test.tsx",
                f"{LABEL_DIR}/PublishedLabel.test.tsx")
    shutil.copy(f"{GOLD_DIR}/testUtils.tsx",
                f"{LABEL_DIR}/testUtils.tsx")
    shutil.copy(f"{GOLD_DIR}/antdTokenNames_extra.test.ts",
                f"{THEME_UTILS_DIR}/antdTokenNames_extra.test.ts")


def _run_jest(test_path: str, timeout: int = 600) -> subprocess.CompletedProcess:
    """Run jest on a specific test file from the frontend root."""
    env = os.environ.copy()
    env["NODE_ENV"] = "test"
    env["NODE_OPTIONS"] = "--max-old-space-size=8192"
    env["TZ"] = "America/New_York"
    rel = os.path.relpath(test_path, FRONTEND)
    return subprocess.run(
        [JEST_BIN, "--silent", "--no-coverage", "--runInBand", rel],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def _stage_and_run(test_path: str, timeout: int = 600):
    _stage_gold_tests()
    r = _run_jest(test_path, timeout=timeout)
    return r


# ---------------- f2p tests ----------------

def test_published_label_tokens():
    """PublishedLabel uses labelPublished* / labelDraft* tokens (fail_to_pass)."""
    r = _stage_and_run(f"{LABEL_DIR}/PublishedLabel.test.tsx", timeout=600)
    assert r.returncode == 0, (
        f"PublishedLabel.test.tsx failed.\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-2000:]}"
    )


def test_dataset_type_label_tokens():
    """DatasetTypeLabel uses labelDatasetPhysical*/Virtual* tokens (fail_to_pass)."""
    r = _stage_and_run(f"{LABEL_DIR}/DatasetTypeLabel.test.tsx", timeout=600)
    assert r.returncode == 0, (
        f"DatasetTypeLabel.test.tsx failed.\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-2000:]}"
    )


def test_antd_token_names_recognize_label_tokens():
    """antdTokenNames recognizes the 16 new label tokens (fail_to_pass)."""
    r = _stage_and_run(
        f"{THEME_UTILS_DIR}/antdTokenNames_extra.test.ts", timeout=300
    )
    assert r.returncode == 0, (
        f"antdTokenNames_extra.test.ts failed.\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-2000:]}"
    )


def test_repo_antd_token_names_existing(  ):
    """Existing antdTokenNames.test.ts continues to pass (pass_to_pass).

    The PR adds new tokens to SUPERSET_CUSTOM_TOKENS but should not break
    the existing token-validation tests that were already in the repo.
    """
    test_path = f"{THEME_UTILS_DIR}/antdTokenNames.test.ts"
    r = _run_jest(test_path, timeout=300)
    assert r.returncode == 0, (
        f"Existing antdTokenNames.test.ts regressed.\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-2000:]}"
    )


def test_types_ts_declares_label_tokens():
    """SupersetSpecificTokens interface declares the 16 new label tokens (fail_to_pass).

    This is a TypeScript declaration check: the agent must add these optional
    fields to the SupersetSpecificTokens interface for the tests to type-check.
    """
    types_path = Path(f"{FRONTEND}/packages/superset-core/src/theme/types.ts")
    content = types_path.read_text()
    expected_tokens = [
        "labelPublishedColor", "labelPublishedBg",
        "labelPublishedBorderColor", "labelPublishedIconColor",
        "labelDraftColor", "labelDraftBg",
        "labelDraftBorderColor", "labelDraftIconColor",
        "labelDatasetPhysicalColor", "labelDatasetPhysicalBg",
        "labelDatasetPhysicalBorderColor", "labelDatasetPhysicalIconColor",
        "labelDatasetVirtualColor", "labelDatasetVirtualBg",
        "labelDatasetVirtualBorderColor", "labelDatasetVirtualIconColor",
    ]
    # Check declarations appear within the SupersetSpecificTokens interface
    iface_idx = content.find("interface SupersetSpecificTokens")
    assert iface_idx >= 0, "SupersetSpecificTokens interface not found"
    iface_block = content[iface_idx:iface_idx + 5000]
    for t in expected_tokens:
        assert f"{t}?" in iface_block or f"{t}:" in iface_block, (
            f"Token {t} not declared in SupersetSpecificTokens interface"
        )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_load_examples_superset_init():
    """pass_to_pass | CI job 'test-load-examples' → step 'superset init'"""
    r = subprocess.run(
        ["bash", "-lc", 'pip install -e .'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'superset init' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_npm():
    """pass_to_pass | CI job 'build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_npm_2():
    """pass_to_pass | CI job 'build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run ci:release'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_frontend_check_translations_lint():
    """pass_to_pass | CI job 'frontend-check-translations' → step 'lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run build-translation'], cwd=os.path.join(REPO, './superset-frontend'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_python_deps_run_uv():
    """pass_to_pass | CI job 'check-python-deps' → step 'Run uv'"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/uv-pip-compile.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run uv' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_python_deps_check_for_uncommitted_changes():
    """pass_to_pass | CI job 'check-python-deps' → step 'Check for uncommitted changes'"""
    r = subprocess.run(
        ["bash", "-lc", 'echo "Full diff (for logging/debugging):"\ngit diff\n\necho "Filtered diff (excluding comments and whitespace):"\nfiltered_diff=$(git diff -U0 | grep \'^[-+]\' | grep -vE \'^[-+]{3}\' | grep -vE \'^[-+][[:space:]]*#\' | grep -vE \'^[-+][[:space:]]*$\' || true)\necho "$filtered_diff"\n\nif [[ -n "$filtered_diff" ]]; then\n  echo\n  echo "ERROR: The pinned dependencies are not up-to-date."\n  echo "Please run \'./scripts/uv-pip-compile.sh\' and commit the changes."\n  echo "More info: https://github.com/apache/superset/tree/master/requirements"\n  exit 1\nelse\n  echo "Pinned dependencies are up-to-date."\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check for uncommitted changes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_postgres_presto_python_unit_tests_postgresql():
    """pass_to_pass | CI job 'test-postgres-presto' → step 'Python unit tests (PostgreSQL)'"""
    r = subprocess.run(
        ["bash", "-lc", "./scripts/python_tests.sh -m 'chart_data_flow or sql_json_flow'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python unit tests (PostgreSQL)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_postgres_hive_python_unit_tests_postgresql():
    """pass_to_pass | CI job 'test-postgres-hive' → step 'Python unit tests (PostgreSQL)'"""
    r = subprocess.run(
        ["bash", "-lc", "pip install -e .[hive] && ./scripts/python_tests.sh -m 'chart_data_flow or sql_json_flow'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python unit tests (PostgreSQL)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_tests_python_unit_tests():
    """pass_to_pass | CI job 'unit-tests' → step 'Python unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pytest --durations-min=0.5 --cov-report= --cov=superset ./tests/common ./tests/unit_tests --cache-clear --maxfail=50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_tests_python_100_coverage_unit_tests():
    """pass_to_pass | CI job 'unit-tests' → step 'Python 100% coverage unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pytest --durations-min=0.5 --cov=superset/sql/ ./tests/unit_tests/sql/ --cache-clear --cov-fail-under=100'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python 100% coverage unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")