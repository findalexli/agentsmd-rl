#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dbt-bouncer

# Idempotency guard
if grep -qF "This generates fixtures for dbt 1.10 and 1.11 in `tests/fixtures/dbt_1X/target/`" ".claude/skills/build-artifacts/SKILL.md" && grep -qF "| `make build-artifacts` | Regenerate test fixtures (dbt 1.10, 1.11) |" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/build-artifacts/SKILL.md b/.claude/skills/build-artifacts/SKILL.md
@@ -21,7 +21,7 @@ Regenerate test fixture files after making changes to the dbt project in `dbt_pr
 make build-artifacts
 ```
 
-This generates fixtures for dbt 1.9, 1.10, and 1.11 in `tests/fixtures/dbt_1X/target/` (manifest.json, catalog.json, run_results.json).
+This generates fixtures for dbt 1.10 and 1.11 in `tests/fixtures/dbt_1X/target/` (manifest.json, catalog.json, run_results.json). Note: dbt 1.9 fixtures are frozen and not regenerated.
 
 **Note:** The Makefile uses specific dbt-duckdb version pins. Do not modify the version pins in the Makefile without understanding the compatibility matrix.
 
@@ -30,7 +30,6 @@ This generates fixtures for dbt 1.9, 1.10, and 1.11 in `tests/fixtures/dbt_1X/ta
 Check that the generated files exist and are non-empty:
 
 ```bash
-ls -la tests/fixtures/dbt_19/target/
 ls -la tests/fixtures/dbt_110/target/
 ls -la tests/fixtures/dbt_111/target/
 ```
diff --git a/AGENTS.md b/AGENTS.md
@@ -21,7 +21,7 @@ make install
 | `make test-integration` | Run integration tests only |
 | `prek run --all-files` | Run pre-commit hooks (**not** `pre-commit run`) |
 | `make build-and-run-dbt-bouncer` | End-to-end validation |
-| `make build-artifacts` | Regenerate test fixtures (dbt 1.9, 1.10, 1.11) |
+| `make build-artifacts` | Regenerate test fixtures (dbt 1.10, 1.11) |
 | `make generate-schema` | Regenerate `schema.json` from Pydantic models |
 | `make test-perf` | Performance benchmarks (bencher + hyperfine) |
 
PATCH

echo "Gold patch applied."
