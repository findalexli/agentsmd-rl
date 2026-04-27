"""Tests for the SAML login support PR (apache/superset#38606).

These tests verify three behaviors of `superset.views.base.cached_common_bootstrap_data`:

1. When AUTH_TYPE == AUTH_SAML, the SAML providers are injected into the
   bootstrap payload as AUTH_PROVIDERS.
2. When a SAML provider entry has no `icon`, a default ("fa-sign-in") is used.
3. When AUTH_TYPE is OAUTH or SAML, recaptcha is excluded from the payload
   even if AUTH_USER_REGISTRATION is True.

Plus checks for the CSRF exempt list and frontend enum/render changes.
"""

import os
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO = Path("/workspace/superset")

# A test file that exercises cached_common_bootstrap_data using the same
# `app_context` fixture as the rest of superset's unit tests. We drop this
# into the repo at module import time so pytest can collect it under the
# existing tests/unit_tests/views package (which inherits from conftest.py).
PYTEST_FILE = REPO / "tests" / "unit_tests" / "views" / "test_saml_bootstrap.py"

PYTEST_FILE_CONTENT = textwrap.dedent('''\
    # Drop-in test invoked via subprocess from /tests/test_outputs.py.
    from typing import Any
    from unittest.mock import MagicMock, patch

    import pytest
    from flask import g
    from flask_appbuilder.const import (
        AUTH_DB,
        AUTH_LDAP,
        AUTH_OAUTH,
        AUTH_SAML,
    )

    from superset.views.base import cached_common_bootstrap_data


    @pytest.fixture(autouse=True)
    def mock_user() -> None:
        g.user = MagicMock()


    @pytest.fixture(autouse=True)
    def _clear_bootstrap_cache():
        # cached_common_bootstrap_data is @cache.memoize'd so we need a fresh
        # entry per test - clearing the cache is the safest option.
        from superset.extensions import cache_manager
        cache_manager.cache.delete_memoized(cached_common_bootstrap_data)
        yield
        cache_manager.cache.delete_memoized(cached_common_bootstrap_data)


    _user_id_seq = [1000]


    def _get_bootstrap() -> dict[str, Any]:
        # Vary user_id per call to defeat any residual memoization keying.
        _user_id_seq[0] += 1
        with patch("superset.views.base.menu_data", return_value={}):
            return cached_common_bootstrap_data(user_id=_user_id_seq[0], locale=None)


    def test_bootstrap_saml_providers(app_context: None) -> None:
        from flask import current_app

        current_app.config["AUTH_TYPE"] = AUTH_SAML
        current_app.config["AUTH_USER_REGISTRATION"] = False
        current_app.config["SAML_PROVIDERS"] = [
            {"name": "okta", "icon": "fa-okta"},
            {"name": "entra_id", "icon": "fa-microsoft"},
        ]

        payload = _get_bootstrap()

        assert payload["conf"]["AUTH_TYPE"] == AUTH_SAML
        providers = payload["conf"]["AUTH_PROVIDERS"]
        assert len(providers) == 2
        assert providers[0] == {"name": "okta", "icon": "fa-okta"}
        assert providers[1] == {"name": "entra_id", "icon": "fa-microsoft"}


    def test_bootstrap_saml_provider_default_icon(app_context: None) -> None:
        from flask import current_app

        current_app.config["AUTH_TYPE"] = AUTH_SAML
        current_app.config["AUTH_USER_REGISTRATION"] = False
        current_app.config["SAML_PROVIDERS"] = [{"name": "onelogin"}]

        payload = _get_bootstrap()
        providers = payload["conf"]["AUTH_PROVIDERS"]
        assert providers[0] == {"name": "onelogin", "icon": "fa-sign-in"}


    def test_bootstrap_oauth_providers_still_work(app_context: None) -> None:
        from flask import current_app

        current_app.config["AUTH_TYPE"] = AUTH_OAUTH
        current_app.config["AUTH_USER_REGISTRATION"] = False
        current_app.config["OAUTH_PROVIDERS"] = [
            {"name": "github", "icon": "fa-github"},
        ]

        payload = _get_bootstrap()

        assert payload["conf"]["AUTH_TYPE"] == AUTH_OAUTH
        providers = payload["conf"]["AUTH_PROVIDERS"]
        assert len(providers) == 1
        assert providers[0] == {"name": "github", "icon": "fa-github"}


    @pytest.mark.parametrize(
        "auth_type",
        [AUTH_OAUTH, AUTH_SAML],
        ids=["AUTH_OAUTH", "AUTH_SAML"],
    )
    def test_recaptcha_excluded_for_federated(
        app_context: None, auth_type: int
    ) -> None:
        from flask import current_app

        current_app.config["AUTH_TYPE"] = auth_type
        current_app.config["AUTH_USER_REGISTRATION"] = True
        current_app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        current_app.config.pop("RECAPTCHA_PUBLIC_KEY", None)
        # Provide empty provider lists so the bootstrap branches succeed;
        # the rendering of providers isn't what we're checking here.
        current_app.config["OAUTH_PROVIDERS"] = []
        current_app.config["SAML_PROVIDERS"] = []

        payload = _get_bootstrap()

        assert "RECAPTCHA_PUBLIC_KEY" not in payload["conf"]


    @pytest.mark.parametrize(
        "auth_type",
        [AUTH_DB, AUTH_LDAP],
        ids=["AUTH_DB", "AUTH_LDAP"],
    )
    def test_recaptcha_shown_for_db_ldap(
        app_context: None, auth_type: int
    ) -> None:
        from flask import current_app

        current_app.config["AUTH_TYPE"] = auth_type
        current_app.config["AUTH_USER_REGISTRATION"] = True
        current_app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"
        current_app.config["RECAPTCHA_PUBLIC_KEY"] = "test-key"

        payload = _get_bootstrap()
        assert payload["conf"]["RECAPTCHA_PUBLIC_KEY"] == "test-key"
''')


def _write_pytest_file() -> None:
    PYTEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    PYTEST_FILE.write_text(PYTEST_FILE_CONTENT)


def _run_one(test_id: str) -> subprocess.CompletedProcess:
    """Run a single test from the dropped pytest file, return the result."""
    _write_pytest_file()
    cmd = [
        "python",
        "-m",
        "pytest",
        f"tests/unit_tests/views/test_saml_bootstrap.py::{test_id}",
        "-v",
        "--tb=short",
        "-p",
        "no:cacheprovider",
    ]
    return subprocess.run(
        cmd,
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=300,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass tests — must FAIL on base commit, PASS after the agent's fix.
# ---------------------------------------------------------------------------


def test_bootstrap_saml_providers_populated():
    """SAML providers from config land in AUTH_PROVIDERS for AUTH_SAML."""
    r = _run_one("test_bootstrap_saml_providers")
    assert r.returncode == 0, (
        f"Pytest failed:\nSTDOUT:\n{r.stdout[-3000:]}\nSTDERR:\n{r.stderr[-1000:]}"
    )


def test_bootstrap_saml_default_icon_applied():
    """SAML providers without an icon get the default 'fa-sign-in'."""
    r = _run_one("test_bootstrap_saml_provider_default_icon")
    assert r.returncode == 0, (
        f"Pytest failed:\nSTDOUT:\n{r.stdout[-3000:]}\nSTDERR:\n{r.stderr[-1000:]}"
    )


@pytest.mark.parametrize("federated", ["AUTH_OAUTH", "AUTH_SAML"])
def test_recaptcha_excluded_for_federated_auth(federated):
    """Recaptcha is excluded from the bootstrap payload for OAuth + SAML."""
    test_id = f"test_recaptcha_excluded_for_federated[{federated}]"
    r = _run_one(test_id)
    assert r.returncode == 0, (
        f"Pytest failed for {federated}:\n"
        f"STDOUT:\n{r.stdout[-3000:]}\nSTDERR:\n{r.stderr[-1000:]}"
    )


def test_csrf_exempt_includes_saml_acs():
    """The SAML ACS endpoint is in WTF_CSRF_EXEMPT_LIST in superset/config.py."""
    cfg = (REPO / "superset" / "config.py").read_text()
    # find the WTF_CSRF_EXEMPT_LIST literal block
    start = cfg.find("WTF_CSRF_EXEMPT_LIST")
    assert start >= 0, "WTF_CSRF_EXEMPT_LIST not found in superset/config.py"
    end = cfg.find("]", start)
    assert end > start
    block = cfg[start:end]
    assert "flask_appbuilder.security.views.acs" in block, (
        "SAML ACS endpoint must be added to WTF_CSRF_EXEMPT_LIST so "
        "that cross-site SAML response POSTs from the IdP succeed"
    )


def test_frontend_login_handles_saml_auth_type():
    """The Login React component renders provider buttons for AUTH_SAML."""
    src = (
        REPO / "superset-frontend" / "src" / "pages" / "Login" / "index.tsx"
    ).read_text()

    # The AuthType enum must include a SAML entry with value 5.
    # We don't pin the exact identifier name — just that 5 is mapped.
    import re

    enum_match = re.search(r"enum\s+AuthType\s*\{([^}]*)\}", src, re.DOTALL)
    assert enum_match, "AuthType enum not found"
    enum_body = enum_match.group(1)
    assert "= 5" in enum_body, (
        "AuthType enum must include an entry mapped to value 5 (AUTH_SAML)"
    )

    # The OAuth render branch must also fire for SAML — i.e. some condition
    # mentions both OAuth and SAML auth types together.
    assert "AuthOauth" in src and "5" in src, (
        "Login component must reference both OAuth and SAML auth modes"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass tests — must PASS on base commit AND after fix.
# These exercise existing repo CI-style checks.
# ---------------------------------------------------------------------------


def test_oauth_branch_unchanged():
    """OAuth provider bootstrap behavior is preserved — must pass on base."""
    r = _run_one("test_bootstrap_oauth_providers_still_work")
    assert r.returncode == 0, (
        f"OAuth p2p failed:\nSTDOUT:\n{r.stdout[-3000:]}\nSTDERR:\n{r.stderr[-1000:]}"
    )


@pytest.mark.parametrize("non_federated", ["AUTH_DB", "AUTH_LDAP"])
def test_recaptcha_shown_for_non_federated(non_federated):
    """Recaptcha is still shown for DB and LDAP — must pass on base."""
    test_id = f"test_recaptcha_shown_for_db_ldap[{non_federated}]"
    r = _run_one(test_id)
    assert r.returncode == 0, (
        f"Recaptcha p2p failed for {non_federated}:\n"
        f"STDOUT:\n{r.stdout[-3000:]}\nSTDERR:\n{r.stderr[-1000:]}"
    )


