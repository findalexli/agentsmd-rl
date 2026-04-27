#!/usr/bin/env bash
set -euo pipefail

cd /workspace/airflow

# Idempotency: if patch already applied, skip
if grep -q "_strip_userinfo" providers/opensearch/src/airflow/providers/opensearch/log/os_task_handler.py 2>/dev/null; then
    echo "Patch already applied; skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/providers/elasticsearch/AGENTS.md b/providers/elasticsearch/AGENTS.md
new file mode 100644
index 0000000000000..6c749efd1d728
--- /dev/null
+++ b/providers/elasticsearch/AGENTS.md
@@ -0,0 +1,28 @@
+<!-- SPDX-License-Identifier: Apache-2.0
+     https://www.apache.org/licenses/LICENSE-2.0 -->
+
+# Elasticsearch Provider — Agent Instructions
+
+## Keep in sync with `providers/opensearch`
+
+OpenSearch was forked from Elasticsearch and the two providers share most of
+their task-log handler code and surface. File layouts mirror each other:
+
+| Elasticsearch                                   | OpenSearch                              |
+| ----------------------------------------------- | --------------------------------------- |
+| `log/es_task_handler.py`                        | `log/os_task_handler.py`                |
+| `log/es_response.py`                            | `log/os_response.py`                    |
+| `log/es_json_formatter.py`                      | `log/os_json_formatter.py`              |
+| `ElasticsearchTaskHandler`                      | `OpensearchTaskHandler`                 |
+| `ElasticsearchRemoteLogIO`                      | `OpensearchRemoteLogIO`                 |
+
+**When fixing a bug or changing behaviour here, check whether the equivalent
+change is needed in `providers/opensearch` (and vice-versa).** This applies
+especially to: task-log handler logic, log grouping / formatting, connection
+handling, URL/credential treatment, and response parsing. The two packages
+ship on independent release cadences, so the fix should usually land as two
+separate PRs on the same day.
+
+Legitimate reasons to diverge: upstream client API differences (`elasticsearch`
+vs `opensearchpy`), provider-specific features that only one side has, or
+changes gated on config that only exists in one provider.
diff --git a/providers/opensearch/AGENTS.md b/providers/opensearch/AGENTS.md
new file mode 100644
index 0000000000000..5ad60da33fa59
--- /dev/null
+++ b/providers/opensearch/AGENTS.md
@@ -0,0 +1,28 @@
+<!-- SPDX-License-Identifier: Apache-2.0
+     https://www.apache.org/licenses/LICENSE-2.0 -->
+
+# OpenSearch Provider — Agent Instructions
+
+## Keep in sync with `providers/elasticsearch`
+
+OpenSearch was forked from Elasticsearch and the two providers share most of
+their task-log handler code and surface. File layouts mirror each other:
+
+| OpenSearch                              | Elasticsearch                                   |
+| --------------------------------------- | ----------------------------------------------- |
+| `log/os_task_handler.py`                | `log/es_task_handler.py`                        |
+| `log/os_response.py`                    | `log/es_response.py`                            |
+| `log/os_json_formatter.py`              | `log/es_json_formatter.py`                      |
+| `OpensearchTaskHandler`                 | `ElasticsearchTaskHandler`                      |
+| `OpensearchRemoteLogIO`                 | `ElasticsearchRemoteLogIO`                      |
+
+**When fixing a bug or changing behaviour here, check whether the equivalent
+change is needed in `providers/elasticsearch` (and vice-versa).** This applies
+especially to: task-log handler logic, log grouping / formatting, connection
+handling, URL/credential treatment, and response parsing. The two packages
+ship on independent release cadences, so the fix should usually land as two
+separate PRs on the same day.
+
+Legitimate reasons to diverge: upstream client API differences (`opensearchpy`
+vs `elasticsearch`), provider-specific features that only one side has (e.g.
+`write_to_os`), or changes gated on config that only exists in one provider.
diff --git a/providers/opensearch/docs/changelog.rst b/providers/opensearch/docs/changelog.rst
index 76560826118af..4c31d750825f9 100644
--- a/providers/opensearch/docs/changelog.rst
+++ b/providers/opensearch/docs/changelog.rst
@@ -27,6 +27,14 @@
 Changelog
 ---------

+When the ``[opensearch] host`` config embeds credentials
+(``https://user:password@opensearch.example.com:9200``), the log-source
+label shown in task logs is now the host URL with the ``user:password@``
+portion stripped. Previously the full URL (including credentials) could
+appear as a dictionary key in the task-log output when log-hits did not
+carry a ``host`` field. The OpenSearch client is still connected using
+the full URL, so authentication is unaffected.
+
 1.9.0
 .....

diff --git a/providers/opensearch/src/airflow/providers/opensearch/log/os_task_handler.py b/providers/opensearch/src/airflow/providers/opensearch/log/os_task_handler.py
index f3b921b78b2ab..bb63d341355c4 100644
--- a/providers/opensearch/src/airflow/providers/opensearch/log/os_task_handler.py
+++ b/providers/opensearch/src/airflow/providers/opensearch/log/os_task_handler.py
@@ -197,6 +197,28 @@ def _create_opensearch_client(
     )


+def _strip_userinfo(url: str) -> str:
+    """
+    Return ``url`` with any ``user:password@`` userinfo removed.
+
+    The OpenSearch ``[opensearch] host`` config commonly embeds
+    credentials (``https://user:password@opensearch.example.com:9200``).
+    This value is reused as a display label for log-source grouping, so
+    the credentials would otherwise end up in task logs. Anything that
+    is not a valid URL is returned unchanged.
+    """
+    try:
+        parsed = urlparse(url)
+    except (TypeError, ValueError):
+        return url
+    if not parsed.hostname or (not parsed.username and not parsed.password):
+        return url
+    netloc = parsed.hostname
+    if parsed.port is not None:
+        netloc = f"{netloc}:{parsed.port}"
+    return parsed._replace(netloc=netloc).geturl()
+
+
 def _render_log_id(
     log_id_template: str, ti: TaskInstance | TaskInstanceKey | RuntimeTI, try_number: int
 ) -> str:
@@ -713,8 +735,9 @@ def _get_result(self, hit: dict[Any, Any], parent_class=None) -> Hit:

     def _group_logs_by_host(self, response: OpensearchResponse) -> dict[str, list[Hit]]:
         grouped_logs = defaultdict(list)
+        host_fallback = _strip_userinfo(self.host)
         for hit in response:
-            key = getattr_nested(hit, self.host_field, None) or self.host
+            key = getattr_nested(hit, self.host_field, None) or host_fallback
             grouped_logs[key].append(hit)
         return grouped_logs

@@ -937,8 +960,9 @@ def _get_index_patterns(self, ti: RuntimeTI | None) -> str:

     def _group_logs_by_host(self, response: OpensearchResponse) -> dict[str, list[Hit]]:
         grouped_logs = defaultdict(list)
+        host_fallback = _strip_userinfo(self.host)
         for hit in response:
-            key = getattr_nested(hit, self.host_field, None) or self.host
+            key = getattr_nested(hit, self.host_field, None) or host_fallback
             grouped_logs[key].append(hit)
         return grouped_logs

PATCH

echo "Patch applied successfully."
