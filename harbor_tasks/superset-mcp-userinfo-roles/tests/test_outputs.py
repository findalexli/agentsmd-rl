# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""Behavioral tests for the UserInfo role-serialization fix.

The Superset MCP service serializes Chart, Dashboard, and Dataset objects
to Pydantic schemas. Each serializer constructs a `UserInfo` for every
owner. UserInfo declares `roles: List[str]`, but the SQLAlchemy ORM exposes
each user's roles as a list of `Role` objects (objects with a `.name`
attribute), not strings. The fix must convert each Role's `.name` into a
string before validation.

These tests run against the real on-disk source under
`/workspace/superset/superset/mcp_service/`. To avoid pulling in the full
Superset/Flask/SQLAlchemy stack, we stub the heavy upstream modules that
the schemas import (`superset.constants`, `superset.daos.base`,
`superset.utils.json`, and the mcp_service utility helpers). The schema
modules under test are loaded from disk normally.
"""

from __future__ import annotations

import json as _stdjson
import subprocess
import sys
import types
from enum import Enum

from pydantic import BaseModel

REPO = "/workspace/superset"


def _install_stubs() -> None:
    """Pre-populate sys.modules with lightweight stubs so the schema modules
    can be imported without Flask, SQLAlchemy, or superset-core installed.

    We deliberately do NOT execute superset/__init__.py — instead, sys.modules
    is seeded with bare-bones package objects whose __path__ points at the real
    source tree. Python's import machinery then finds the real submodules
    (e.g., superset.mcp_service.system.schemas) under that path.
    """

    def _pkg(name: str, path: str | None = None) -> types.ModuleType:
        mod = types.ModuleType(name)
        if path:
            mod.__path__ = [path]
        sys.modules[name] = mod
        return mod

    _pkg("superset", path=f"{REPO}/superset")

    constants = types.ModuleType("superset.constants")

    class TimeGrain(str, Enum):
        SECOND = "PT1S"
        MINUTE = "PT1M"
        HOUR = "PT1H"
        DAY = "P1D"
        WEEK = "P1W"
        MONTH = "P1M"
        QUARTER = "P3M"
        YEAR = "P1Y"

    constants.TimeGrain = TimeGrain
    sys.modules["superset.constants"] = constants

    _pkg("superset.daos", path=f"{REPO}/superset/daos")
    daos_base = types.ModuleType("superset.daos.base")

    class ColumnOperatorEnum(str, Enum):
        EQ = "eq"
        NEQ = "neq"
        GT = "gt"
        LT = "lt"
        IN = "in_"
        NIN = "nin"
        LIKE = "like"
        ILIKE = "ilike"
        IS_NULL = "is_null"
        IS_NOT_NULL = "is_not_null"

    class ColumnOperator(BaseModel):
        col: str = ""
        opr: str = ""
        value: object = None

    daos_base.ColumnOperatorEnum = ColumnOperatorEnum
    daos_base.ColumnOperator = ColumnOperator
    sys.modules["superset.daos.base"] = daos_base

    _pkg("superset.utils", path=f"{REPO}/superset/utils")
    utils_json = types.ModuleType("superset.utils.json")
    utils_json.dumps = _stdjson.dumps
    utils_json.loads = _stdjson.loads
    sys.modules["superset.utils.json"] = utils_json

    _pkg("superset.mcp_service", path=f"{REPO}/superset/mcp_service")
    _pkg("superset.mcp_service.utils", path=f"{REPO}/superset/mcp_service/utils")

    sanit = types.ModuleType("superset.mcp_service.utils.sanitization")
    sanit.sanitize_filter_value = lambda v, max_length=1000: v
    sanit.sanitize_user_input = lambda v, *a, **k: v
    sys.modules["superset.mcp_service.utils.sanitization"] = sanit

    url_utils = types.ModuleType("superset.mcp_service.utils.url_utils")
    url_utils.get_superset_base_url = lambda: "http://test.local"
    sys.modules["superset.mcp_service.utils.url_utils"] = url_utils

    if REPO not in sys.path:
        sys.path.insert(0, REPO)


_install_stubs()

# Now pull in the actual schema modules from disk.
from superset.mcp_service.chart.schemas import (  # noqa: E402
    serialize_chart_object,
)
from superset.mcp_service.dashboard.schemas import (  # noqa: E402
    dashboard_serializer,
)
from superset.mcp_service.dataset.schemas import (  # noqa: E402
    serialize_dataset_object,
)
from superset.mcp_service.system.schemas import UserInfo  # noqa: E402


# ---------------------------------------------------------------------------
# Lightweight stand-ins for SQLAlchemy ORM objects
# ---------------------------------------------------------------------------


class Role:
    """Mimics flask_appbuilder's Role ORM class — has a .name string."""

    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return self.name


class User:
    def __init__(self, roles: object = (), **overrides: object) -> None:
        self.id = 7
        self.username = "alice"
        self.first_name = "Alice"
        self.last_name = "Liddell"
        self.email = "alice@example.com"
        self.active = True
        self.roles = roles
        for k, v in overrides.items():
            setattr(self, k, v)


class _Chart:
    def __init__(self, owners: list) -> None:
        self.id = 100
        self.slice_name = "MyChart"
        self.viz_type = "table"
        self.datasource_name = "ds"
        self.datasource_type = "table"
        self.description = "desc"
        self.cache_timeout = 0
        self.changed_by_name = None
        self.changed_by = None
        self.changed_on = None
        self.changed_on_humanized = None
        self.created_by_name = None
        self.created_by = None
        self.created_on = None
        self.created_on_humanized = None
        self.uuid = None
        self.tags = []
        self.owners = owners


class _Dashboard:
    def __init__(self, owners: list) -> None:
        self.id = 200
        self.dashboard_title = "MyDash"
        self.slug = "my-dash"
        self.description = "d"
        self.css = ""
        self.certified_by = None
        self.certification_details = None
        self.json_metadata = "{}"
        self.position_json = "{}"
        self.published = False
        self.is_managed_externally = False
        self.external_url = None
        self.created_on = None
        self.changed_on = None
        self.created_by = None
        self.changed_by = None
        self.uuid = None
        self.url = ""
        self.created_on_humanized = None
        self.changed_on_humanized = None
        self.slices = []
        self.owners = owners
        self.tags = []
        self.roles = []


class _Dataset:
    def __init__(self, owners: list) -> None:
        self.id = 300
        self.table_name = "tbl"
        self.schema = None
        self.database = None
        self.description = None
        self.changed_by_name = None
        self.changed_by = None
        self.changed_on = None
        self.changed_on_humanized = None
        self.created_by_name = None
        self.created_by = None
        self.created_on = None
        self.created_on_humanized = None
        self.uuid = None
        self.is_virtual = False
        self.database_id = None
        self.schema_perm = None
        self.url = None
        self.sql = None
        self.main_dttm_col = None
        self.offset = 0
        self.cache_timeout = 0
        self.params = None
        self.template_params = None
        self.extra = None
        self.columns = []
        self.metrics = []
        self.tags = []
        self.owners = owners


# ---------------------------------------------------------------------------
# fail-to-pass tests
# ---------------------------------------------------------------------------


def test_chart_serializer_extracts_role_names_from_role_objects():
    """Bug repro: serialize_chart_object must accept owners whose .roles
    are non-string ORM Role objects and emit string role names."""
    user = User(roles=[Role("Admin"), Role("Alpha")])
    result = serialize_chart_object(_Chart(owners=[user]))

    assert result is not None
    assert len(result.owners) == 1
    out_roles = result.owners[0].roles
    assert out_roles == ["Admin", "Alpha"], f"got {out_roles!r}"
    assert all(isinstance(r, str) for r in out_roles), (
        f"role values must be strings, got {[type(r).__name__ for r in out_roles]}"
    )


def test_dashboard_serializer_extracts_role_names_from_role_objects():
    user = User(roles=[Role("Gamma")])
    result = dashboard_serializer(_Dashboard(owners=[user]))

    assert result is not None
    assert len(result.owners) == 1
    out_roles = result.owners[0].roles
    assert out_roles == ["Gamma"], f"got {out_roles!r}"
    assert all(isinstance(r, str) for r in out_roles)


def test_dataset_serializer_extracts_role_names_from_role_objects():
    user = User(roles=[Role("Admin"), Role("Public")])
    result = serialize_dataset_object(_Dataset(owners=[user]))

    assert result is not None
    assert len(result.owners) == 1
    out_roles = result.owners[0].roles
    assert out_roles == ["Admin", "Public"], f"got {out_roles!r}"
    assert all(isinstance(r, str) for r in out_roles)


def test_chart_serializer_with_single_role():
    """Vary input: single role rather than two."""
    user = User(roles=[Role("Viewer")])
    result = serialize_chart_object(_Chart(owners=[user]))
    assert result.owners[0].roles == ["Viewer"]


def test_chart_serializer_handles_none_roles():
    """Owner.roles == None must not crash; produces empty list."""
    user = User(roles=None)
    result = serialize_chart_object(_Chart(owners=[user]))
    assert result is not None
    assert result.owners[0].roles == []


def test_dashboard_serializer_handles_none_roles():
    user = User(roles=None)
    result = dashboard_serializer(_Dashboard(owners=[user]))
    assert result is not None
    assert result.owners[0].roles == []


def test_dataset_serializer_handles_non_iterable_roles():
    """Owner.roles set to a non-iterable scalar must not crash."""
    user = User(roles=42)
    result = serialize_dataset_object(_Dataset(owners=[user]))
    assert result is not None
    assert result.owners[0].roles == []


def test_chart_serializer_multiple_owners_preserves_per_user_roles():
    """Each owner's roles are extracted independently."""
    u1 = User(roles=[Role("Admin")])
    u2 = User(roles=[Role("Alpha"), Role("Gamma")])
    u2.id = 8
    u2.username = "bob"
    result = serialize_chart_object(_Chart(owners=[u1, u2]))

    assert result is not None
    assert len(result.owners) == 2
    assert result.owners[0].roles == ["Admin"]
    assert result.owners[1].roles == ["Alpha", "Gamma"]


def test_chart_owners_serialize_basic_user_fields_alongside_roles():
    """Confirm the role fix doesn't drop other UserInfo fields."""
    user = User(roles=[Role("Admin")])
    result = serialize_chart_object(_Chart(owners=[user]))
    owner = result.owners[0]

    assert owner.username == "alice"
    assert owner.first_name == "Alice"
    assert owner.last_name == "Liddell"
    assert owner.email == "alice@example.com"
    assert owner.active is True
    assert owner.roles == ["Admin"]


# ---------------------------------------------------------------------------
# pass-to-pass tests (unchanged on both base and gold)
# ---------------------------------------------------------------------------


def test_userinfo_default_roles_is_empty_list():
    """UserInfo() defaults `roles` to an empty list (added in #38407)."""
    info = UserInfo()
    assert info.roles == []


def test_userinfo_accepts_list_of_string_roles():
    """UserInfo declares roles as List[str]."""
    info = UserInfo(roles=["Admin", "Alpha"])
    assert info.roles == ["Admin", "Alpha"]
    assert all(isinstance(r, str) for r in info.roles)


def test_userinfo_schema_has_roles_field_typed_as_list_of_strings():
    """Schema introspection: the roles field is typed as a list of strings."""
    schema = UserInfo.model_json_schema()
    assert "roles" in schema["properties"]
    roles_prop = schema["properties"]["roles"]
    assert roles_prop.get("type") == "array"
    assert roles_prop.get("items", {}).get("type") == "string"


# ---------------------------------------------------------------------------
# Repo-CI sanity check (pass-to-pass): the source files compile with python.
# ---------------------------------------------------------------------------


def test_modified_schema_files_compile_cleanly():
    """Static syntax check across every schema file the fix touches.

    Catches accidental syntax breakage from a bad edit. Uses python -m py_compile
    so we exercise the agent's actual on-disk source, not our cached imports.
    """
    targets = [
        f"{REPO}/superset/mcp_service/system/schemas.py",
        f"{REPO}/superset/mcp_service/chart/schemas.py",
        f"{REPO}/superset/mcp_service/dashboard/schemas.py",
        f"{REPO}/superset/mcp_service/dataset/schemas.py",
    ]
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", *targets],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr}"
