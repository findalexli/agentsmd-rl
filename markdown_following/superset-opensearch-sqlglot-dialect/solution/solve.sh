#!/bin/bash
# Reference solution: applies the gold patch from PR #39538.
# Patch is inlined as a HEREDOC — never fetched over the network.
set -euo pipefail

cd /workspace/superset

# Idempotency: if the OpenSearch dialect file is already present and the
# parse.py registration line exists, the patch was already applied.
if [ -f superset/sql/dialects/opensearch.py ] && \
   grep -q '"odelasticsearch": OpenSearch,' superset/sql/parse.py; then
    echo "Patch already applied; nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/superset/sql/dialects/__init__.py b/superset/sql/dialects/__init__.py
index 71c8958a80ff..0334efb5f111 100644
--- a/superset/sql/dialects/__init__.py
+++ b/superset/sql/dialects/__init__.py
@@ -18,6 +18,7 @@
 from .db2 import DB2
 from .dremio import Dremio
 from .firebolt import Firebolt, FireboltOld
+from .opensearch import OpenSearch
 from .pinot import Pinot

-__all__ = ["DB2", "Dremio", "Firebolt", "FireboltOld", "Pinot"]
+__all__ = ["DB2", "Dremio", "Firebolt", "FireboltOld", "OpenSearch", "Pinot"]
diff --git a/superset/sql/dialects/opensearch.py b/superset/sql/dialects/opensearch.py
new file mode 100644
index 000000000000..5cde7469b685
--- /dev/null
+++ b/superset/sql/dialects/opensearch.py
@@ -0,0 +1,34 @@
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
+
+"""
+OpenSearch SQL dialect.
+
+OpenSearch SQL is syntactically close to MySQL but accepts both backticks and
+double-quotes as identifier delimiters. Treating ``"`` as an identifier (rather
+than a string delimiter, as MySQL does) is what keeps mixed-case column names
+from being emitted as string literals after a SQLGlot round-trip.
+"""
+
+from __future__ import annotations
+
+from sqlglot.dialects.mysql import MySQL
+
+
+class OpenSearch(MySQL):
+    class Tokenizer(MySQL.Tokenizer):
+        IDENTIFIERS = ['"', "`"]
diff --git a/superset/sql/parse.py b/superset/sql/parse.py
index 20fe7f2b0c8d..6f07c15c1640 100644
--- a/superset/sql/parse.py
+++ b/superset/sql/parse.py
@@ -45,7 +45,7 @@
 )

 from superset.exceptions import QueryClauseValidationException, SupersetParseError
-from superset.sql.dialects import DB2, Dremio, Firebolt, Pinot
+from superset.sql.dialects import DB2, Dremio, Firebolt, OpenSearch, Pinot

 if TYPE_CHECKING:
     from superset.models.core import Database
@@ -93,7 +93,7 @@
     "netezza": Dialects.POSTGRES,
     "oceanbase": Dialects.MYSQL,
     # "ocient": ???
-    # "odelasticsearch": ???
+    "odelasticsearch": OpenSearch,
     "oracle": Dialects.ORACLE,
     "parseable": Dialects.POSTGRES,
     "pinot": Pinot,
PATCH

echo "Gold patch applied."
