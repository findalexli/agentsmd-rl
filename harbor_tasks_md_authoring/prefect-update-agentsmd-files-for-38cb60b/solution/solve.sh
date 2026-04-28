#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "- **Task-run submission schemas must be eagerly rebuilt.** Schemas instantiated " "src/prefect/client/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/prefect/client/AGENTS.md b/src/prefect/client/AGENTS.md
@@ -9,6 +9,7 @@ HTTP client for communicating with Prefect server and Prefect Cloud.
 - **Methods should accept simple kwargs** (`str`, `int`, `UUID`, etc.) and return Pydantic models. Avoid accepting complex objects as parameters.
 - **Client schemas are separate from server schemas.** This module has its own `schemas/` to avoid tangling with `server/schemas/`. Keep the boundary clean.
 - **Do not import server-only modules** (`server/database`, `server/models`, etc.) from anything in this directory — it would break the `prefect-client` package build.
+- **Task-run submission schemas must be eagerly rebuilt.** Schemas instantiated on the concurrent submission path (`Task.create_local_run()`) are rebuilt at import time via `model_rebuild()` at the bottom of `schemas/objects.py`. Pydantic defers schema construction to first use; under threadpool contention, multiple workers race to build the same schema simultaneously. If you add a new schema used in this hot path, add a corresponding `model_rebuild()` call there.
 
 ## Structure
 
PATCH

echo "Gold patch applied."
