"""Verifier for OpenHands PR #14013: hide All toggle in SaaS LLM settings."""
import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/OpenHands")
FRONTEND = REPO / "frontend"


def _run(cmd, cwd=FRONTEND, timeout=900, env_extra=None):
    env = os.environ.copy()
    env.setdefault("CI", "1")
    env.setdefault("NODE_OPTIONS", "--max-old-space-size=4096")
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True,
        timeout=timeout, env=env,
    )


# ---------- f2p (fail-to-pass): the PR's new behaviour tests ----------

def test_f2p_force_advanced_toggle_for_critical_only_schema():
    """Vitest: 'shows the advanced toggle when it is forced for a critical-only schema'.

    Fails on base because SdkSectionPage does not accept the forcing prop.
    """
    r = _run([
        "npx", "vitest", "run",
        "__tests__/components/features/settings/sdk-settings/sdk-section-page.test.tsx",
        "-t", "shows the advanced toggle when it is forced for a critical-only schema",
    ], timeout=900)
    assert r.returncode == 0, (
        f"vitest failed (rc={r.returncode}).\n"
        f"STDOUT (tail):\n{r.stdout[-2000:]}\n"
        f"STDERR (tail):\n{r.stderr[-1000:]}"
    )


def test_f2p_oss_shows_advanced_and_all_toggles():
    """Vitest: 'shows Advanced and All toggles in OSS mode for the default LLM route schema'."""
    r = _run([
        "npx", "vitest", "run",
        "__tests__/routes/llm-settings.test.tsx",
        "-t", "shows Advanced and All toggles in OSS mode for the default LLM route schema",
    ], timeout=900)
    assert r.returncode == 0, (
        f"vitest failed (rc={r.returncode}).\n"
        f"STDOUT (tail):\n{r.stdout[-2000:]}\n"
        f"STDERR (tail):\n{r.stderr[-1000:]}"
    )


def test_f2p_saas_keeps_advanced_hides_all():
    """Vitest: 'keeps Advanced visible but hides All in SaaS mode for the default LLM route schema'."""
    r = _run([
        "npx", "vitest", "run",
        "__tests__/routes/llm-settings.test.tsx",
        "-t", "keeps Advanced visible but hides All in SaaS mode for the default LLM route schema",
    ], timeout=900)
    assert r.returncode == 0, (
        f"vitest failed (rc={r.returncode}).\n"
        f"STDOUT (tail):\n{r.stdout[-2000:]}\n"
        f"STDERR (tail):\n{r.stderr[-1000:]}"
    )


# ---------- f2p: whole test files must pass (new tests pass + no regressions) ----------

def test_f2p_full_llm_settings_test_file():
    """Whole llm-settings.test.tsx passes (repo's existing route tests must not regress)."""
    r = _run([
        "npx", "vitest", "run",
        "__tests__/routes/llm-settings.test.tsx",
    ], timeout=900)
    assert r.returncode == 0, (
        f"llm-settings test file failed (rc={r.returncode}).\n"
        f"STDOUT (tail):\n{r.stdout[-3000:]}\n"
        f"STDERR (tail):\n{r.stderr[-1500:]}"
    )


def test_f2p_full_sdk_section_page_test_file():
    """Whole sdk-section-page.test.tsx passes (repo's existing component tests must not regress)."""
    r = _run([
        "npx", "vitest", "run",
        "__tests__/components/features/settings/sdk-settings/sdk-section-page.test.tsx",
    ], timeout=900)
    assert r.returncode == 0, (
        f"sdk-section-page test file failed (rc={r.returncode}).\n"
        f"STDOUT (tail):\n{r.stdout[-3000:]}\n"
        f"STDERR (tail):\n{r.stderr[-1500:]}"
    )


# ---------- p2p (pass-to-pass): regression guard ----------

def test_p2p_build():
    """The repo's frontend build (`npm run build`) succeeds — required by AGENTS.md."""
    r = _run(["npm", "run", "build"], timeout=900)
    assert r.returncode == 0, (
        f"build failed (rc={r.returncode}).\n"
        f"STDOUT (tail):\n{r.stdout[-3000:]}\n"
        f"STDERR (tail):\n{r.stderr[-1500:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
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

def test_ci_fe_e2e_tests_run_playwright_tests():
    """pass_to_pass | CI job 'FE E2E Tests' → step 'Run Playwright tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'npx playwright test --project=chromium'], cwd=os.path.join(REPO, './frontend'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Playwright tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_openhands_ui_build_package():
    """pass_to_pass | CI job 'Build openhands-ui' → step 'Build package'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run build'], cwd=os.path.join(REPO, './openhands-ui'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build package' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_package_versions_check_for_any_rev_fields_in_pyproject_to():
    # pass_to_pass | CI job 'check-package-versions' → step "Check for any 'rev' fields in pyproject.toml
    r = subprocess.run(
        ["bash", "-lc", "python - <<'PY'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check for any 'rev' fields in pyproject.toml' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_frontend_lint_typescript_compilation_and_translat():
    """pass_to_pass | CI job 'Lint frontend' → step 'Lint, TypeScript compilation, and translation checks'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run lint && npm run make-i18n && npx tsc && npm run check-translation-completeness'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint, TypeScript compilation, and translation checks' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_enterprise_python_unit_tests_run_unit_tests():
    """pass_to_pass | CI job 'Enterprise Python Unit Tests' → step 'Run Unit Tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'PYTHONPATH=".:$PYTHONPATH" poetry run --project=enterprise pytest --forked -n auto -s -p no:ddtrace -p no:ddtrace.pytest_bdd -p no:ddtrace.pytest_benchmark ./enterprise/tests/unit --cov=enterprise --cov-branch'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Unit Tests' failed (returncode={r.returncode}):\n"
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