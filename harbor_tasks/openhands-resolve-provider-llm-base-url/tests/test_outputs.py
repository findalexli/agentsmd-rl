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
