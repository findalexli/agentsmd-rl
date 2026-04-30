#!/usr/bin/env bash
# Oracle: applies the gold patch from PR apache/superset#38647 to /workspace/superset.
# The patch is inlined as a HEREDOC; no network fetches are performed.
set -euo pipefail

cd /workspace/superset

if grep -q "raise_for_access(datasource=datasource)" superset/views/datasource/views.py 2>/dev/null \
   && [ -f tests/unit_tests/views/datasource/views_test.py ]; then
  echo "Solution already applied; skipping patch."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/superset/views/datasource/views.py b/superset/views/datasource/views.py
index d0a4b6851c53..6796fd4cdc5e 100644
--- a/superset/views/datasource/views.py
+++ b/superset/views/datasource/views.py
@@ -90,8 +90,7 @@ def save(self) -> FlaskResponse:
         )
         orm_datasource.database_id = database_id

-        if "owners" in datasource_dict and orm_datasource.owner_class is not None:
-            # Check ownership
+        if orm_datasource.owner_class is not None:
             try:
                 security_manager.raise_for_ownership(orm_datasource)
             except SupersetSecurityException as ex:
@@ -131,6 +130,7 @@ def get(self, datasource_type: str, datasource_id: int) -> FlaskResponse:
         datasource = DatasourceDAO.get_datasource(
             DatasourceType(datasource_type), datasource_id
         )
+        security_manager.raise_for_access(datasource=datasource)
         return self.json_response(sanitize_datasource_data(datasource.data))

     @expose("/external_metadata/<datasource_type>/<datasource_id>/")
@@ -145,6 +145,7 @@ def external_metadata(
             DatasourceType(datasource_type),
             datasource_id,
         )
+        security_manager.raise_for_access(datasource=datasource)
         try:
             external_metadata = datasource.external_metadata()
         except SupersetException as ex:
@@ -174,6 +175,7 @@ def external_metadata_by_name(self, **kwargs: Any) -> FlaskResponse:
         try:
             if datasource is not None:
                 # Get columns from Superset metadata
+                security_manager.raise_for_access(datasource=datasource)
                 external_metadata = datasource.external_metadata()
             else:
                 # Use the SQLAlchemy inspector to get columns
@@ -182,9 +184,18 @@ def external_metadata_by_name(self, **kwargs: Any) -> FlaskResponse:
                     .filter_by(database_name=params["database_name"])
                     .one()
                 )
+                table = Table(
+                    params["table_name"],
+                    params["schema_name"],
+                    params.get("catalog_name"),
+                )
+                security_manager.raise_for_access(
+                    database=database,
+                    table=table,
+                )
                 external_metadata = get_physical_table_metadata(
                     database=database,
-                    table=Table(params["table_name"], params["schema_name"]),
+                    table=table,
                     normalize_columns=params.get("normalize_columns") or False,
                 )
         except (NoResultFound, NoSuchTableError) as ex:
diff --git a/tests/unit_tests/views/datasource/views_test.py b/tests/unit_tests/views/datasource/views_test.py
new file mode 100644
index 000000000000..3a54932d80c3
--- /dev/null
+++ b/tests/unit_tests/views/datasource/views_test.py
@@ -0,0 +1,314 @@
+# Licensed to the Apache Software Foundation (ASF) under one
+# or more contributor license agreements.  See the NOTICE file
+# distributed with this work for additional information
+# regarding copyright ownership.  The ASF licenses this file
+# to you under the Apache License, Version 2.0 (the
+# "License"); you may not use this file except in compliance
+# with the License.  You may obtain a copy of the License at
+#
+#   http://www.apache.org/licenses/LICENSE-2.0
+#
+# Unless required by applicable law or agreed to in writing,
+# software distributed under the License is distributed on an
+# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
+# KIND, either express or implied.  See the License for the
+# specific language governing permissions and limitations
+# under the License.
+"""Unit tests for resource-level authorization in superset/views/datasource/views.py.
+
+Tests use ``inspect.unwrap`` to call the underlying view logic directly,
+bypassing the Flask-AppBuilder permission decorator machinery.
+"""
+
+import inspect
+from unittest.mock import MagicMock, patch
+
+import pytest
+
+from superset.errors import ErrorLevel, SupersetError, SupersetErrorType
+from superset.exceptions import SupersetSecurityException
+from superset.utils import json as superset_json
+
+
+def _security_exception() -> SupersetSecurityException:
+    return SupersetSecurityException(
+        SupersetError(
+            message="Access denied",
+            error_type=SupersetErrorType.DATASOURCE_SECURITY_ACCESS_ERROR,
+            level=ErrorLevel.WARNING,
+        )
+    )
+
+
+def _get_view_func(name: str):
+    """Return the unwrapped body of a Datasource view method."""
+    from superset.views.datasource.views import Datasource
+
+    return inspect.unwrap(getattr(Datasource, name))
+
+
+def _view_self() -> MagicMock:
+    """Create a minimal stand-in for a Datasource view instance."""
+    self = MagicMock()
+    self.json_response = MagicMock(return_value="ok")
+    return self
+
+
+# ---------------------------------------------------------------------------
+# Datasource.get
+# ---------------------------------------------------------------------------
+
+
+@patch("superset.views.datasource.views.security_manager", new_callable=MagicMock)
+@patch("superset.views.datasource.views.DatasourceDAO.get_datasource")
+def test_get_raises_when_access_denied(
+    mock_get_datasource: MagicMock,
+    mock_security_manager: MagicMock,
+) -> None:
+    """raise_for_access is called and propagates for unauthorised callers."""
+    mock_datasource = MagicMock()
+    mock_get_datasource.return_value = mock_datasource
+    mock_security_manager.raise_for_access.side_effect = _security_exception()
+
+    raw_get = _get_view_func("get")
+    with pytest.raises(SupersetSecurityException):
+        raw_get(_view_self(), "table", 1)
+
+    mock_security_manager.raise_for_access.assert_called_once_with(
+        datasource=mock_datasource
+    )
+
+
+@patch("superset.views.datasource.views.sanitize_datasource_data")
+@patch("superset.views.datasource.views.security_manager", new_callable=MagicMock)
+@patch("superset.views.datasource.views.DatasourceDAO.get_datasource")
+def test_get_succeeds_for_authorised_user(
+    mock_get_datasource: MagicMock,
+    mock_security_manager: MagicMock,
+    mock_sanitize: MagicMock,
+) -> None:
+    """raise_for_access is called without raising; sanitized data is returned."""
+    mock_datasource = MagicMock()
+    mock_datasource.data = {"id": 1}
+    mock_get_datasource.return_value = mock_datasource
+    mock_security_manager.raise_for_access.return_value = None
+    mock_sanitize.return_value = {"id": 1}
+
+    view = _view_self()
+    raw_get = _get_view_func("get")
+    raw_get(view, "table", 1)
+
+    mock_security_manager.raise_for_access.assert_called_once_with(
+        datasource=mock_datasource
+    )
+    view.json_response.assert_called_once_with({"id": 1})
+
+
+# ---------------------------------------------------------------------------
+# Datasource.external_metadata
+# ---------------------------------------------------------------------------
+
+
+@patch("superset.views.datasource.views.security_manager", new_callable=MagicMock)
+@patch("superset.views.datasource.views.DatasourceDAO.get_datasource")
+def test_external_metadata_raises_when_access_denied(
+    mock_get_datasource: MagicMock,
+    mock_security_manager: MagicMock,
+) -> None:
+    mock_datasource = MagicMock()
+    mock_get_datasource.return_value = mock_datasource
+    mock_security_manager.raise_for_access.side_effect = _security_exception()
+
+    raw_fn = _get_view_func("external_metadata")
+    with pytest.raises(SupersetSecurityException):
+        raw_fn(_view_self(), "table", 1)
+
+    mock_security_manager.raise_for_access.assert_called_once_with(
+        datasource=mock_datasource
+    )
+
+
+@patch("superset.views.datasource.views.security_manager", new_callable=MagicMock)
+@patch("superset.views.datasource.views.DatasourceDAO.get_datasource")
+def test_external_metadata_succeeds_for_authorised_user(
+    mock_get_datasource: MagicMock,
+    mock_security_manager: MagicMock,
+) -> None:
+    mock_datasource = MagicMock()
+    mock_datasource.external_metadata.return_value = [{"name": "col1"}]
+    mock_get_datasource.return_value = mock_datasource
+    mock_security_manager.raise_for_access.return_value = None
+
+    view = _view_self()
+    raw_fn = _get_view_func("external_metadata")
+    raw_fn(view, "table", 1)
+
+    mock_security_manager.raise_for_access.assert_called_once_with(
+        datasource=mock_datasource
+    )
+    view.json_response.assert_called_once_with([{"name": "col1"}])
+
+
+# ---------------------------------------------------------------------------
+# Datasource.external_metadata_by_name
+# ---------------------------------------------------------------------------
+
+
+@patch("superset.views.datasource.views.security_manager", new_callable=MagicMock)
+@patch("superset.views.datasource.views.SqlaTable.get_datasource_by_name")
+@patch("superset.views.datasource.views.ExternalMetadataSchema")
+def test_external_metadata_by_name_known_datasource_raises_when_access_denied(
+    mock_schema_cls: MagicMock,
+    mock_get_by_name: MagicMock,
+    mock_security_manager: MagicMock,
+) -> None:
+    """When a datasource exists, raise_for_access(datasource=...) is enforced."""
+    params = {
+        "database_name": "mydb",
+        "schema_name": "public",
+        "table_name": "private_table",
+    }
+    mock_schema_cls.return_value.load.return_value = params
+
+    mock_datasource = MagicMock()
+    mock_get_by_name.return_value = mock_datasource
+    mock_security_manager.raise_for_access.side_effect = _security_exception()
+
+    raw_fn = _get_view_func("external_metadata_by_name")
+    with pytest.raises(SupersetSecurityException):
+        raw_fn(_view_self(), rison=params)
+
+    mock_security_manager.raise_for_access.assert_called_once_with(
+        datasource=mock_datasource
+    )
+
+
+@patch("superset.views.datasource.views.security_manager", new_callable=MagicMock)
+@patch("superset.views.datasource.views.SqlaTable.get_datasource_by_name")
+@patch("superset.views.datasource.views.ExternalMetadataSchema")
+@patch("superset.views.datasource.views.db")
+def test_external_metadata_by_name_no_datasource_raises_when_access_denied(
+    mock_db: MagicMock,
+    mock_schema_cls: MagicMock,
+    mock_get_by_name: MagicMock,
+    mock_security_manager: MagicMock,
+) -> None:
+    """When no datasource exists, raise_for_access(database=..., table=...) runs."""
+    params = {
+        "database_name": "mydb",
+        "schema_name": "public",
+        "table_name": "new_table",
+    }
+    mock_schema_cls.return_value.load.return_value = params
+    mock_get_by_name.return_value = None
+
+    mock_database = MagicMock()
+    mock_db.session.query.return_value.filter_by.return_value.one.return_value = (
+        mock_database
+    )
+    mock_security_manager.raise_for_access.side_effect = _security_exception()
+
+    raw_fn = _get_view_func("external_metadata_by_name")
+    with pytest.raises(SupersetSecurityException):
+        raw_fn(_view_self(), rison=params)
+
+    mock_security_manager.raise_for_access.assert_called_once()
+    call_kwargs = mock_security_manager.raise_for_access.call_args.kwargs
+    assert call_kwargs["database"] is mock_database
+    assert call_kwargs["table"].table == "new_table"
+    assert call_kwargs["table"].schema == "public"
+
+
+# ---------------------------------------------------------------------------
+# Datasource.save — ownership bypass prevention
+# ---------------------------------------------------------------------------
+
+
+@patch("superset.views.datasource.views.security_manager", new_callable=MagicMock)
+@patch("superset.views.datasource.views.DatasourceDAO.get_datasource")
+def test_save_always_checks_ownership_even_without_owners_field(
+    mock_get_datasource: MagicMock,
+    mock_security_manager: MagicMock,
+) -> None:
+    """Ownership check runs even when 'owners' is absent from the payload."""
+    mock_orm = MagicMock()
+    mock_orm.owner_class = MagicMock()  # not None — model supports ownership
+    mock_get_datasource.return_value = mock_orm
+    mock_security_manager.raise_for_ownership.side_effect = SupersetSecurityException(
+        SupersetError(
+            message="Not an owner",
+            error_type=SupersetErrorType.DATASOURCE_SECURITY_ACCESS_ERROR,
+            level=ErrorLevel.WARNING,
+        )
+    )
+
+    from flask import Flask
+
+    from superset.commands.dataset.exceptions import DatasetForbiddenError
+
+    raw_save = _get_view_func("save")
+    app = Flask(__name__)
+    with app.test_request_context(
+        "/datasource/save/",
+        method="POST",
+        data={
+            "data": superset_json.dumps(
+                {
+                    "id": 1,
+                    "type": "table",
+                    "database": {"id": 1},
+                    "columns": [],
+                    # 'owners' intentionally omitted
+                }
+            )
+        },
+    ):
+        with pytest.raises(DatasetForbiddenError):
+            raw_save(_view_self())
+
+    mock_security_manager.raise_for_ownership.assert_called_once_with(mock_orm)
+
+
+@patch("superset.views.datasource.views.security_manager", new_callable=MagicMock)
+@patch("superset.views.datasource.views.DatasourceDAO.get_datasource")
+def test_save_non_owner_with_owners_field_is_rejected(
+    mock_get_datasource: MagicMock,
+    mock_security_manager: MagicMock,
+) -> None:
+    """A non-owner cannot use the save endpoint even when supplying an owners list."""
+    mock_orm = MagicMock()
+    mock_orm.owner_class = MagicMock()
+    mock_get_datasource.return_value = mock_orm
+    mock_security_manager.raise_for_ownership.side_effect = SupersetSecurityException(
+        SupersetError(
+            message="Not an owner",
+            error_type=SupersetErrorType.DATASOURCE_SECURITY_ACCESS_ERROR,
+            level=ErrorLevel.WARNING,
+        )
+    )
+
+    from flask import Flask
+
+    from superset.commands.dataset.exceptions import DatasetForbiddenError
+
+    raw_save = _get_view_func("save")
+    app = Flask(__name__)
+    with app.test_request_context(
+        "/datasource/save/",
+        method="POST",
+        data={
+            "data": superset_json.dumps(
+                {
+                    "id": 1,
+                    "type": "table",
+                    "database": {"id": 1},
+                    "columns": [],
+                    "owners": [99],  # attacker-supplied owners list
+                }
+            )
+        },
+    ):
+        with pytest.raises(DatasetForbiddenError):
+            raw_save(_view_self())
+
+    mock_security_manager.raise_for_ownership.assert_called_once_with(mock_orm)
PATCH

echo "Patch applied successfully."
