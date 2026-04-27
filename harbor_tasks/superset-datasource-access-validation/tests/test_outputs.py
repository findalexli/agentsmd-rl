"""Behavioural tests for the legacy /datasource access-validation alignment.

The PR being benchmarked aligns resource-level access checks across the
legacy `/datasource` endpoints in :mod:`superset.views.datasource.views`.
These tests exercise the unwrapped view methods using mocks; we do not
need a database, but we DO need a Superset app context so that the
`superset.connectors.sqla.models` module (which the view module pulls in
transitively) can finish loading.

The session-scoped ``_app_context`` fixture below mirrors the one in the
upstream `tests/unit_tests/conftest.py` so this file can run in
isolation outside the repo's pytest tree.
"""

from __future__ import annotations

import importlib
import inspect
import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO = Path("/workspace/superset")
os.environ.setdefault("SUPERSET_TESTENV", "true")
os.environ.setdefault("SUPERSET_SECRET_KEY", "not-a-secret")

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


@pytest.fixture(scope="session", autouse=True)
def _app_context() -> Iterator[None]:
    """Build a SupersetApp once and push an app context for the whole session."""
    from superset.app import SupersetApp
    from superset.extensions import appbuilder
    from superset.initialization import SupersetAppInitializer

    app = SupersetApp(__name__)
    app.config.from_object("superset.config")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["PREVENT_UNSAFE_DB_CONNECTIONS"] = False
    app.config["TESTING"] = True
    app.config["RATELIMIT_ENABLED"] = False
    app.config["CACHE_CONFIG"] = {}
    app.config["DATA_CACHE_CONFIG"] = {}
    app.config["SERVER_NAME"] = "example.com"
    app.config["APPLICATION_ROOT"] = "/"

    appbuilder.baseviews = []
    SupersetAppInitializer(app).init_app()

    with app.app_context():
        import superset.views.base  # noqa: F401

        importlib.reload(superset.views.base)
        yield


# ---------------------------------------------------------------------------
# Helpers (lazy imports so app context is up before they touch superset)
# ---------------------------------------------------------------------------


def _security_exception():
    from superset.errors import ErrorLevel, SupersetError, SupersetErrorType
    from superset.exceptions import SupersetSecurityException

    return SupersetSecurityException(
        SupersetError(
            message="Access denied",
            error_type=SupersetErrorType.DATASOURCE_SECURITY_ACCESS_ERROR,
            level=ErrorLevel.WARNING,
        )
    )


def _unwrap(name: str):
    from superset.views.datasource.views import Datasource

    return inspect.unwrap(getattr(Datasource, name))


def _view_self() -> MagicMock:
    self = MagicMock()
    self.json_response = MagicMock(return_value="ok")
    return self


# ---------------------------------------------------------------------------
# Datasource.get must enforce raise_for_access
# ---------------------------------------------------------------------------


@patch("superset.views.datasource.views.security_manager", new_callable=MagicMock)
@patch("superset.views.datasource.views.DatasourceDAO.get_datasource")
def test_get_denies_unauthorised_user(
    mock_get_datasource: MagicMock,
    mock_security_manager: MagicMock,
) -> None:
    """Calling Datasource.get for a forbidden datasource must raise."""
    from superset.exceptions import SupersetSecurityException

    ds = MagicMock()
    mock_get_datasource.return_value = ds
    mock_security_manager.raise_for_access.side_effect = _security_exception()

    raw_get = _unwrap("get")
    with pytest.raises(SupersetSecurityException):
        raw_get(_view_self(), "table", 1)

    mock_security_manager.raise_for_access.assert_called_once_with(datasource=ds)


@patch("superset.views.datasource.views.sanitize_datasource_data")
@patch("superset.views.datasource.views.security_manager", new_callable=MagicMock)
@patch("superset.views.datasource.views.DatasourceDAO.get_datasource")
def test_get_invokes_raise_for_access_for_authorised_user(
    mock_get_datasource: MagicMock,
    mock_security_manager: MagicMock,
    mock_sanitize: MagicMock,
) -> None:
    """raise_for_access must be invoked on every authorised get call."""
    ds = MagicMock()
    ds.data = {"id": 7}
    mock_get_datasource.return_value = ds
    mock_security_manager.raise_for_access.return_value = None
    mock_sanitize.return_value = {"id": 7}

    view = _view_self()
    raw_get = _unwrap("get")
    raw_get(view, "table", 7)

    mock_security_manager.raise_for_access.assert_called_once_with(datasource=ds)
    view.json_response.assert_called_once_with({"id": 7})


# ---------------------------------------------------------------------------
# Datasource.external_metadata must enforce raise_for_access
# ---------------------------------------------------------------------------


@patch("superset.views.datasource.views.security_manager", new_callable=MagicMock)
@patch("superset.views.datasource.views.DatasourceDAO.get_datasource")
def test_external_metadata_denies_unauthorised_user(
    mock_get_datasource: MagicMock,
    mock_security_manager: MagicMock,
) -> None:
    from superset.exceptions import SupersetSecurityException

    ds = MagicMock()
    mock_get_datasource.return_value = ds
    mock_security_manager.raise_for_access.side_effect = _security_exception()

    raw_fn = _unwrap("external_metadata")
    with pytest.raises(SupersetSecurityException):
        raw_fn(_view_self(), "table", 42)

    mock_security_manager.raise_for_access.assert_called_once_with(datasource=ds)


@patch("superset.views.datasource.views.security_manager", new_callable=MagicMock)
@patch("superset.views.datasource.views.DatasourceDAO.get_datasource")
def test_external_metadata_invokes_raise_for_access(
    mock_get_datasource: MagicMock,
    mock_security_manager: MagicMock,
) -> None:
    ds = MagicMock()
    ds.external_metadata.return_value = [{"name": "col1"}]
    mock_get_datasource.return_value = ds
    mock_security_manager.raise_for_access.return_value = None

    view = _view_self()
    raw_fn = _unwrap("external_metadata")
    raw_fn(view, "table", 13)

    mock_security_manager.raise_for_access.assert_called_once_with(datasource=ds)


# ---------------------------------------------------------------------------
# Datasource.external_metadata_by_name — both branches enforce access
# ---------------------------------------------------------------------------


@patch("superset.views.datasource.views.security_manager", new_callable=MagicMock)
@patch("superset.views.datasource.views.SqlaTable.get_datasource_by_name")
@patch("superset.views.datasource.views.ExternalMetadataSchema")
def test_external_metadata_by_name_known_datasource_denied(
    mock_schema_cls: MagicMock,
    mock_get_by_name: MagicMock,
    mock_security_manager: MagicMock,
) -> None:
    """When the datasource is known, raise_for_access(datasource=...) must run."""
    from superset.exceptions import SupersetSecurityException

    params = {
        "database_name": "warehouse",
        "schema_name": "private",
        "table_name": "secrets",
    }
    mock_schema_cls.return_value.load.return_value = params

    ds = MagicMock()
    mock_get_by_name.return_value = ds
    mock_security_manager.raise_for_access.side_effect = _security_exception()

    raw_fn = _unwrap("external_metadata_by_name")
    with pytest.raises(SupersetSecurityException):
        raw_fn(_view_self(), rison=params)

    mock_security_manager.raise_for_access.assert_called_once_with(datasource=ds)


@patch("superset.views.datasource.views.security_manager", new_callable=MagicMock)
@patch("superset.views.datasource.views.SqlaTable.get_datasource_by_name")
@patch("superset.views.datasource.views.ExternalMetadataSchema")
@patch("superset.views.datasource.views.db")
def test_external_metadata_by_name_unknown_datasource_denied(
    mock_db: MagicMock,
    mock_schema_cls: MagicMock,
    mock_get_by_name: MagicMock,
    mock_security_manager: MagicMock,
) -> None:
    """When the datasource is unknown, raise_for_access(database=, table=) must run."""
    from superset.exceptions import SupersetSecurityException

    params = {
        "database_name": "warehouse",
        "schema_name": "private",
        "table_name": "candidate_table",
    }
    mock_schema_cls.return_value.load.return_value = params
    mock_get_by_name.return_value = None

    database = MagicMock()
    mock_db.session.query.return_value.filter_by.return_value.one.return_value = (
        database
    )
    mock_security_manager.raise_for_access.side_effect = _security_exception()

    raw_fn = _unwrap("external_metadata_by_name")
    with pytest.raises(SupersetSecurityException):
        raw_fn(_view_self(), rison=params)

    mock_security_manager.raise_for_access.assert_called_once()
    call_kwargs = mock_security_manager.raise_for_access.call_args.kwargs
    assert call_kwargs["database"] is database
    assert call_kwargs["table"].table == "candidate_table"
    assert call_kwargs["table"].schema == "private"


# ---------------------------------------------------------------------------
# Datasource.save — ownership check must run regardless of "owners" field
# ---------------------------------------------------------------------------


@patch("superset.views.datasource.views.security_manager", new_callable=MagicMock)
@patch("superset.views.datasource.views.DatasourceDAO.get_datasource")
def test_save_checks_ownership_when_owners_omitted(
    mock_get_datasource: MagicMock,
    mock_security_manager: MagicMock,
) -> None:
    """Save must run raise_for_ownership even when 'owners' is missing."""
    from flask import Flask

    from superset.commands.dataset.exceptions import DatasetForbiddenError
    from superset.errors import ErrorLevel, SupersetError, SupersetErrorType
    from superset.exceptions import SupersetSecurityException
    from superset.utils import json as superset_json

    orm = MagicMock()
    orm.owner_class = MagicMock()
    mock_get_datasource.return_value = orm
    mock_security_manager.raise_for_ownership.side_effect = SupersetSecurityException(
        SupersetError(
            message="Not an owner",
            error_type=SupersetErrorType.DATASOURCE_SECURITY_ACCESS_ERROR,
            level=ErrorLevel.WARNING,
        )
    )

    raw_save = _unwrap("save")
    payload = {
        "id": 1,
        "type": "table",
        "database": {"id": 1},
        "columns": [],
    }
    app = Flask(__name__)
    with app.test_request_context(
        "/datasource/save/",
        method="POST",
        data={"data": superset_json.dumps(payload)},
    ):
        with pytest.raises(DatasetForbiddenError):
            raw_save(_view_self())

    mock_security_manager.raise_for_ownership.assert_called_once_with(orm)


@patch("superset.views.datasource.views.security_manager", new_callable=MagicMock)
@patch("superset.views.datasource.views.DatasourceDAO.get_datasource")
def test_save_checks_ownership_when_owners_supplied(
    mock_get_datasource: MagicMock,
    mock_security_manager: MagicMock,
) -> None:
    """A non-owner cannot bypass the check by supplying an attacker-chosen owners list."""
    from flask import Flask

    from superset.commands.dataset.exceptions import DatasetForbiddenError
    from superset.errors import ErrorLevel, SupersetError, SupersetErrorType
    from superset.exceptions import SupersetSecurityException
    from superset.utils import json as superset_json

    orm = MagicMock()
    orm.owner_class = MagicMock()
    mock_get_datasource.return_value = orm
    mock_security_manager.raise_for_ownership.side_effect = SupersetSecurityException(
        SupersetError(
            message="Not an owner",
            error_type=SupersetErrorType.DATASOURCE_SECURITY_ACCESS_ERROR,
            level=ErrorLevel.WARNING,
        )
    )

    raw_save = _unwrap("save")
    payload = {
        "id": 1,
        "type": "table",
        "database": {"id": 1},
        "columns": [],
        "owners": [99],
    }
    app = Flask(__name__)
    with app.test_request_context(
        "/datasource/save/",
        method="POST",
        data={"data": superset_json.dumps(payload)},
    ):
        with pytest.raises(DatasetForbiddenError):
            raw_save(_view_self())

    mock_security_manager.raise_for_ownership.assert_called_once_with(orm)


# ---------------------------------------------------------------------------
# pass_to_pass: agent-config compliance & repo CI sanity checks
# ---------------------------------------------------------------------------


def test_new_test_file_has_apache_license_header() -> None:
    """AGENTS.md / CLAUDE.md require ASF license headers on new code files."""
    path = REPO / "tests" / "unit_tests" / "views" / "datasource" / "views_test.py"
    if not path.exists():
        pytest.skip("New test file not present — gold patch not applied")
    text = path.read_text(encoding="utf-8")
    assert "Licensed to the Apache Software Foundation" in text, (
        "New test file is missing the ASF license header required by AGENTS.md"
    )
    assert "Apache License, Version 2.0" in text


def test_new_test_file_uses_type_hints() -> None:
    """AGENTS.md / CLAUDE.md require type hints on new Python code."""
    import ast

    path = REPO / "tests" / "unit_tests" / "views" / "datasource" / "views_test.py"
    if not path.exists():
        pytest.skip("New test file not present — gold patch not applied")
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    typed_defs = 0
    untyped_defs = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("_") and not node.name.startswith("__"):
                continue
            has_return_anno = node.returns is not None
            params = [a for a in node.args.args if a.arg != "self"]
            params_typed = (
                all(a.annotation is not None for a in params) if params else True
            )
            if has_return_anno and params_typed:
                typed_defs += 1
            else:
                untyped_defs += 1
    assert typed_defs > 0, "no annotated public functions found"
    assert untyped_defs == 0, (
        f"{untyped_defs} function(s) in new test file lack required type annotations"
    )


def test_repo_unit_test_collection_succeeds() -> None:
    """The repo's pytest collection must succeed for the new test directory."""
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--collect-only",
            "-q",
            "tests/unit_tests/views/datasource/",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"pytest collection failed:\nSTDOUT:\n{r.stdout[-1500:]}\n"
        f"STDERR:\n{r.stderr[-1500:]}"
    )


def test_views_module_importable_via_subprocess() -> None:
    """Smoke check: the patched views module imports cleanly under an app context."""
    snippet = (
        "from superset.app import SupersetApp;"
        "from superset.initialization import SupersetAppInitializer;"
        "from superset.extensions import appbuilder;"
        "appbuilder.baseviews = [];"
        "app = SupersetApp(__name__);"
        "app.config.from_object('superset.config');"
        "app.config['SQLALCHEMY_DATABASE_URI']='sqlite://';"
        "SupersetAppInitializer(app).init_app();"
        "ctx = app.app_context(); ctx.push();"
        "import superset.views.datasource.views as v;"
        "print('ok')"
    )
    r = subprocess.run(
        [sys.executable, "-c", snippet],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=180,
        env={
            **os.environ,
            "SUPERSET_TESTENV": "true",
            "SUPERSET_SECRET_KEY": "not-a-secret",
        },
    )
    assert r.returncode == 0 and "ok" in r.stdout, (
        f"import failed:\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
    )
