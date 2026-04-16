#!/bin/bash
set -e

cd /workspace/ClickHouse

# Apply the fix for refreshable materialized views DROP handling
patch -p1 <<'PATCH'
diff --git a/src/Interpreters/InterpreterDropQuery.cpp b/src/Interpreters/InterpreterDropQuery.cpp
index 1234567..abcdefg 100644
--- a/src/Interpreters/InterpreterDropQuery.cpp
+++ b/src/Interpreters/InterpreterDropQuery.cpp
@@ -199,7 +199,15 @@ BlockIO InterpreterDropQuery::executeToTableImpl(const ContextPtr & context_, AS
                 table_id.getNameForLogs());

         bool secondary_query = getContext()->getClientInfo().query_kind == ClientInfo::QueryKind::SECONDARY_QUERY;
-        if (!secondary_query && settings[Setting::ignore_drop_queries_probability] != 0 && ast_drop_query.kind == ASTDropQuery::Kind::Drop
+
+        /// Don't ignore DROP for refreshable materialized views: TRUNCATE doesn't stop
+        /// the periodic refresh task, so the orphaned view would keep refreshing indefinitely,
+        /// consuming background pool threads and potentially overwhelming the server.
+        auto * materialized_view = dynamic_cast<StorageMaterializedView *>(table.get());
+        bool is_refreshable_view = materialized_view && materialized_view->isRefreshable();
+
+        if (!secondary_query && !is_refreshable_view
+            && settings[Setting::ignore_drop_queries_probability] != 0 && ast_drop_query.kind == ASTDropQuery::Kind::Drop
             && std::uniform_real_distribution<>(0.0, 1.0)(thread_local_rng) <= settings[Setting::ignore_drop_queries_probability])
         {
             ast_drop_query.sync = false;
PATCH

echo "Patch applied successfully"
