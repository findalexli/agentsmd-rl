"""Behavioral tests for resolve_provider_llm_base_url.

The function must apply a deployment-specific LLM proxy URL override when the
model uses the ``openhands/`` or ``litellm_proxy/`` prefix and the stored
``base_url`` is the SDK default. The function must live in
``openhands/app_server/config.py``.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

REPO = Path("/workspace/openhands")

# These literals are copied from the PR description; agents must match them.
SDK_DEFAULT = "https://llm-proxy.app.all-hands.dev/"
STAGING_URL = "https://llm-proxy.staging.all-hands.dev/"
CUSTOM_URL = "https://my-own-proxy.example.com/v1"


def _run(code: str, env: dict[str, str] | None = None, timeout: int = 60) -> str:
    """Execute *code* inside the repo's Python env. Print captured stdout.

    Each test runs in its own subprocess so an environment-variable test cannot
    leak state into a sibling test.
    """
    full_env = os.environ.copy()
    full_env["PYTHONPATH"] = str(REPO)
    # Strip the proxy env vars by default; tests opt into setting them.
    full_env.pop("OPENHANDS_PROVIDER_BASE_URL", None)
    full_env.pop("LLM_BASE_URL", None)
    if env:
        full_env.update(env)
    r = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(code)],
        cwd=str(REPO),
        env=full_env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if r.returncode != 0:
        raise AssertionError(
            "Subprocess failed:\n"
            f"STDOUT:\n{r.stdout}\n"
            f"STDERR:\n{r.stderr[-2000:]}"
        )
    return r.stdout


# ───────────────────────── Existence / contract ─────────────────────────


def test_function_exists_and_is_callable():
    """The module exposes a callable resolve_provider_llm_base_url."""
    out = _run(
        """
        from openhands.app_server.config import resolve_provider_llm_base_url
        print(callable(resolve_provider_llm_base_url))
        """
    )
    assert "True" in out, out


def test_sdk_default_constant_exposed():
    """The module exposes the SDK default proxy URL as _SDK_DEFAULT_PROXY."""
    out = _run(
        """
        from openhands.app_server.config import _SDK_DEFAULT_PROXY
        print(_SDK_DEFAULT_PROXY)
        """
    )
    assert SDK_DEFAULT in out, f"Expected {SDK_DEFAULT!r} in output, got: {out!r}"


# ───────────────────────── openhands/ prefix ─────────────────────────


def test_openhands_prefix_replaces_sdk_default_with_provider():
    out = _run(
        f"""
        from openhands.app_server.config import resolve_provider_llm_base_url
        r = resolve_provider_llm_base_url(
            model='openhands/gpt-4',
            base_url={SDK_DEFAULT!r},
            provider_base_url={STAGING_URL!r},
        )
        print(repr(r))
        """
    )
    assert STAGING_URL in out, out


def test_openhands_prefix_custom_url_preserved():
    out = _run(
        f"""
        from openhands.app_server.config import resolve_provider_llm_base_url
        r = resolve_provider_llm_base_url(
            model='openhands/claude-3',
            base_url={CUSTOM_URL!r},
            provider_base_url={STAGING_URL!r},
        )
        print(repr(r))
        """
    )
    assert CUSTOM_URL in out, out


def test_openhands_prefix_no_provider_returns_sdk_default():
    out = _run(
        f"""
        from openhands.app_server.config import resolve_provider_llm_base_url
        r = resolve_provider_llm_base_url(
            model='openhands/gpt-4',
            base_url={SDK_DEFAULT!r},
            provider_base_url='',
        )
        print(repr(r))
        """
    )
    assert SDK_DEFAULT in out, out


def test_openhands_prefix_trailing_slash_normalized():
    """Trailing-slash variants of the SDK default must both be detected."""
    out = _run(
        f"""
        from openhands.app_server.config import resolve_provider_llm_base_url
        # base_url WITHOUT trailing slash should still trigger replacement.
        r = resolve_provider_llm_base_url(
            model='openhands/gpt-4',
            base_url={SDK_DEFAULT.rstrip('/')!r},
            provider_base_url={STAGING_URL!r},
        )
        print(repr(r))
        """
    )
    assert STAGING_URL in out, out


# ───────────────────────── litellm_proxy/ prefix ─────────────────────────


def test_litellm_proxy_prefix_replaces_sdk_default():
    out = _run(
        f"""
        from openhands.app_server.config import resolve_provider_llm_base_url
        r = resolve_provider_llm_base_url(
            model='litellm_proxy/gpt-4',
            base_url={SDK_DEFAULT!r},
            provider_base_url={STAGING_URL!r},
        )
        print(repr(r))
        """
    )
    assert STAGING_URL in out, out


def test_litellm_proxy_prefix_custom_url_preserved():
    out = _run(
        f"""
        from openhands.app_server.config import resolve_provider_llm_base_url
        r = resolve_provider_llm_base_url(
            model='litellm_proxy/llama-3',
            base_url={CUSTOM_URL!r},
            provider_base_url={STAGING_URL!r},
        )
        print(repr(r))
        """
    )
    assert CUSTOM_URL in out, out


# ───────────────────────── Non-matching prefixes ─────────────────────────


def test_plain_model_returns_base_url_unchanged():
    """Models without openhands/ or litellm_proxy/ must keep their base_url."""
    out = _run(
        f"""
        from openhands.app_server.config import resolve_provider_llm_base_url
        r = resolve_provider_llm_base_url(
            model='gpt-4',
            base_url='https://api.openai.com/v1',
            provider_base_url={STAGING_URL!r},
        )
        print(repr(r))
        """
    )
    assert "https://api.openai.com/v1" in out, out


def test_anthropic_model_returns_base_url_unchanged():
    out = _run(
        f"""
        from openhands.app_server.config import resolve_provider_llm_base_url
        r = resolve_provider_llm_base_url(
            model='anthropic/claude-3-opus',
            base_url='https://api.anthropic.com',
            provider_base_url={STAGING_URL!r},
        )
        print(repr(r))
        """
    )
    assert "https://api.anthropic.com" in out and "staging" not in out, out


def test_none_model_returns_base_url_unchanged():
    out = _run(
        f"""
        from openhands.app_server.config import resolve_provider_llm_base_url
        r = resolve_provider_llm_base_url(
            model=None,
            base_url={SDK_DEFAULT!r},
            provider_base_url={STAGING_URL!r},
        )
        print(repr(r))
        """
    )
    # SDK default kept because the function does not match a non-prefixed model.
    assert SDK_DEFAULT in out and "staging" not in out, out


def test_empty_model_returns_base_url_unchanged():
    out = _run(
        f"""
        from openhands.app_server.config import resolve_provider_llm_base_url
        r = resolve_provider_llm_base_url(
            model='',
            base_url={SDK_DEFAULT!r},
            provider_base_url={STAGING_URL!r},
        )
        print(repr(r))
        """
    )
    assert SDK_DEFAULT in out and "staging" not in out, out


# ───────────────────────── None base_url ─────────────────────────


def test_none_base_url_with_openhands_prefix_uses_provider():
    out = _run(
        f"""
        from openhands.app_server.config import resolve_provider_llm_base_url
        r = resolve_provider_llm_base_url(
            model='openhands/gpt-4',
            base_url=None,
            provider_base_url={STAGING_URL!r},
        )
        print(repr(r))
        """
    )
    assert STAGING_URL in out, out


def test_none_base_url_no_provider_returns_none():
    out = _run(
        """
        from openhands.app_server.config import resolve_provider_llm_base_url
        r = resolve_provider_llm_base_url(
            model='openhands/gpt-4',
            base_url=None,
        )
        print(repr(r))
        """
    )
    assert "None" in out, out


# ───────────────────────── Env-var fallback ─────────────────────────


def test_env_fallback_openhands_provider_base_url():
    """When provider_base_url is None, fall back to OPENHANDS_PROVIDER_BASE_URL."""
    out = _run(
        f"""
        from openhands.app_server.config import resolve_provider_llm_base_url
        r = resolve_provider_llm_base_url(
            model='openhands/gpt-4',
            base_url={SDK_DEFAULT!r},
        )
        print(repr(r))
        """,
        env={"OPENHANDS_PROVIDER_BASE_URL": STAGING_URL},
    )
    assert STAGING_URL in out, out


def test_env_fallback_llm_base_url():
    """When provider_base_url is None and OPENHANDS_PROVIDER_BASE_URL is unset,
    fall back to LLM_BASE_URL."""
    out = _run(
        f"""
        from openhands.app_server.config import resolve_provider_llm_base_url
        r = resolve_provider_llm_base_url(
            model='openhands/gpt-4',
            base_url={SDK_DEFAULT!r},
        )
        print(repr(r))
        """,
        env={"LLM_BASE_URL": STAGING_URL},
    )
    assert STAGING_URL in out, out


# ───────────────────────── Refactor of v1 conversation path ─────────────────────────


def test_live_status_service_imports_resolve_function():
    """The v1 conversation service should import resolve_provider_llm_base_url
    from the config module (refactor required by the PR description)."""
    out = _run(
        """
        import openhands.app_server.app_conversation.live_status_app_conversation_service as m
        print('has_resolve:', hasattr(m, 'resolve_provider_llm_base_url'))
        """
    )
    assert "has_resolve: True" in out, out


# ───────────────────────── pass-to-pass: existing repo tests ─────────────────────────


def test_p2p_app_conversation_service_base():
    """Pre-existing app_conversation_service_base unit test must keep passing."""
    r = subprocess.run(
        ["python", "-m", "pytest", "-x", "-q",
         "tests/unit/app_server/test_app_conversation_service_base.py"],
        cwd=str(REPO), capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"P2P test failed:\nSTDOUT:\n{r.stdout[-1500:]}\n"
        f"STDERR:\n{r.stderr[-1000:]}"
    )


def test_p2p_jwt_service():
    """Pre-existing JWT service test must keep passing."""
    r = subprocess.run(
        ["python", "-m", "pytest", "-x", "-q",
         "tests/unit/app_server/test_jwt_service.py"],
        cwd=str(REPO), capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"P2P test failed:\nSTDOUT:\n{r.stdout[-1500:]}\n"
        f"STDERR:\n{r.stderr[-1000:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_lint_frontend_lint_typescript_compilation_and_translat():
    """pass_to_pass | CI job 'Lint frontend' → step 'Lint, TypeScript compilation, and translation checks'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run lint && npm run make-i18n && npx tsc && npm run check-translation-completeness'], cwd=REPO,
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