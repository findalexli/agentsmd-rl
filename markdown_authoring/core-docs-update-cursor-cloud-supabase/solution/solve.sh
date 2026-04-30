#!/usr/bin/env bash
set -euo pipefail

cd /workspace/core

# Idempotency guard
if grep -qF "7. **Note**: Migration `20260226113000_authz_memberships_foundation.sql` has an " "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -387,13 +387,16 @@ Note: unit tests are currently run repo-wide with `bun run test:unit`.
 
 Docker and Supabase CLI must be installed and running before starting local Supabase. After Docker is running (`sudo dockerd &`), run `supabase start` from the repo root.
 
-**Known issue**: Migration `20260214090000_foundation_1_schema.sql` uses `LOCK TABLE` outside a transaction block, which fails with the Supabase CLI. Workaround:
+**Known issue**: Migration `20260214090000_foundation_1_schema.sql` uses `LOCK TABLE` outside a transaction block, which fails with the Supabase CLI. Later migrations also have dependency chains that require the foundation schema. Workaround:
 
-1. Temporarily move `supabase/migrations/20260214090000_foundation_1_schema.sql`, `20260216153000_demo_readonly_rls.sql`, and `supabase/seed.sql` to `/tmp/`
-2. Run `supabase start` (applies only the init migration)
-3. Restore the moved files
-4. Apply the remaining migration manually: `docker exec -i supabase_db_asymmetrical-platform psql -U postgres -d postgres --single-transaction < supabase/migrations/20260214090000_foundation_1_schema.sql`
-5. Apply seed: `docker exec -i supabase_db_asymmetrical-platform psql -U postgres -d postgres --single-transaction < supabase/seed.sql`
+1. Move **all** `2026*` migrations and `seed.sql` out: `mkdir -p /tmp/supabase_mig_staging && for f in supabase/migrations/2026*.sql; do mv "$f" /tmp/supabase_mig_staging/; done && mv supabase/seed.sql /tmp/`
+2. Run `supabase start` (applies only the init migration `20250101000000`)
+3. Restore all moved files back: `mv /tmp/supabase_mig_staging/*.sql supabase/migrations/ && mv /tmp/seed.sql supabase/seed.sql`
+4. Apply foundation migration: `docker exec -i supabase_db_asymmetrical-platform psql -U postgres -d postgres --single-transaction < supabase/migrations/20260214090000_foundation_1_schema.sql`
+5. Record it in the migration table: `docker exec -i supabase_db_asymmetrical-platform psql -U postgres -d postgres -c "INSERT INTO supabase_migrations.schema_migrations (version) VALUES ('20260214090000');"`
+6. Apply remaining migrations in order (without `--single-transaction` for those with explicit `BEGIN`/`COMMIT`); record each version in `supabase_migrations.schema_migrations`
+7. **Note**: Migration `20260226113000_authz_memberships_foundation.sql` has an index expression (`COALESCE(staff_role::text, '')`) that Postgres rejects as non-IMMUTABLE. Create the `authz` schema, types, table, and functions manually (see the migration SQL for definitions), skipping the problematic index expression. If that migration file changes, re-derive these manual steps from the file so local state does not silently drift.
+8. Apply seed: `docker exec -i supabase_db_asymmetrical-platform psql -U postgres -d postgres < supabase/seed.sql` (use without `--single-transaction` since the seed contains its own `BEGIN`/`COMMIT`)
 
 ### Environment variables
 
@@ -412,6 +415,10 @@ Minimum required env vars for local dev (from `supabase status -o env`):
 - `NEXT_PUBLIC_SUPABASE_URL=http://127.0.0.1:54321`
 - `NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon key from supabase status>`
 
+Optional (local dev and Cursor Cloud sandboxes only; do **not** rely on this in production or shared previews unless you deliberately accept weaker startup checks):
+
+- `SKIP_ENV_VALIDATION=1` — bypasses strict env schema validation when optional keys like Stripe/Sentry are not set (see `packages/env/src/schema.ts`).
+
 ### Checks
 
 Standard commands documented in `AGENTS.md` monorepo rules section:
PATCH

echo "Gold patch applied."
