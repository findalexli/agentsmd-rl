#!/usr/bin/env bash
set -euo pipefail

cd /workspace/copilot-collections

# Idempotency guard
if grep -qF "| **Database support** | `CONCURRENTLY` is PostgreSQL-specific. Other engines ha" ".github/skills/sql-and-database/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/sql-and-database/SKILL.md b/.github/skills/sql-and-database/SKILL.md
@@ -361,6 +361,36 @@ WHERE idx_scan = 0
 ORDER BY pg_relation_size(indexrelid) DESC;
 ```
 
+### Non-Blocking Index Operations (CONCURRENTLY)
+
+Standard `CREATE INDEX` and `DROP INDEX` acquire locks that **block writes** on the table for the duration of the operation. On large or heavily-used tables this can cause downtime.
+
+**Always use `CONCURRENTLY`** when creating or dropping indexes on tables that serve live traffic:
+
+```sql
+-- Creating an index without blocking writes
+CREATE INDEX CONCURRENTLY idx_orders_customer_id ON orders(customer_id);
+
+-- Dropping an index without blocking writes
+DROP INDEX CONCURRENTLY idx_orders_customer_id;
+```
+
+**Key constraints and caveats:**
+
+| Aspect | Detail |
+|---|---|
+| **Database support** | `CONCURRENTLY` is PostgreSQL-specific. Other engines have their own online indexing alternatives: MySQL/MariaDB use `ALGORITHM=INPLACE, LOCK=NONE`; SQL Server uses `WITH (ONLINE = ON)`; Oracle uses `ONLINE` keyword. Consult engine-specific docs for constraints and limitations |
+| **Transaction blocks** | `CREATE INDEX CONCURRENTLY` and `DROP INDEX CONCURRENTLY` **cannot run inside a transaction block** — avoid wrapping them in `BEGIN`/`COMMIT` |
+| **Migration frameworks** | Most migration tools wrap statements in a transaction by default. Disable this for concurrent index operations (e.g., `disable_ddl_transaction!` in Rails, `atomic = False` in Django, separate migration step in Flyway) |
+| **Failed builds** | If `CREATE INDEX CONCURRENTLY` fails, it leaves behind an **invalid index**. Check with `\d table_name` and drop the invalid index before retrying |
+| **Unique indexes** | `CREATE UNIQUE INDEX CONCURRENTLY` performs an extra table scan — takes longer but still avoids blocking writes |
+| **Build time** | Concurrent builds are slower than regular ones because they require multiple table passes |
+
+**When to skip `CONCURRENTLY`:**
+- Initial schema setup or empty tables (no live traffic to block)
+- During a maintenance window with no active connections
+- Test/development environments
+
 ---
 
 ## 5. Writing Performant SQL Queries
PATCH

echo "Gold patch applied."
