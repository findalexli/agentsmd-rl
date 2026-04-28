#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mlflow

# Idempotency guard
if grep -qF "(cd mlflow/server/js && yarn prettier:check)" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -82,7 +82,7 @@ uv run --with transformers pytest tests/transformers
 uv run --extra gateway pytest tests/gateway
 
 # Run JavaScript tests
-yarn --cwd mlflow/server/js test
+(cd mlflow/server/js && yarn test)
 ```
 
 **IMPORTANT**: `uv` may fail initially because the environment has not been set up yet. Follow the instructions to set up the environment and then rerun `uv` as needed.
@@ -101,15 +101,15 @@ uv run --only-group lint clint .                    # Run MLflow custom linter
 uv run --only-group lint bash dev/mlflow-typo.sh .
 
 # JavaScript linting and formatting
-yarn --cwd mlflow/server/js lint
-yarn --cwd mlflow/server/js prettier:check
-yarn --cwd mlflow/server/js prettier:fix
+(cd mlflow/server/js && yarn lint)
+(cd mlflow/server/js && yarn prettier:check)
+(cd mlflow/server/js && yarn prettier:fix)
 
 # Type checking
-yarn --cwd mlflow/server/js type-check
+(cd mlflow/server/js && yarn type-check)
 
 # Run all checks
-yarn --cwd mlflow/server/js check-all
+(cd mlflow/server/js && yarn check-all)
 ```
 
 ### Special Testing
@@ -190,7 +190,7 @@ Commits without DCO sign-off will be rejected by CI.
 **Frontend Changes**: If your PR touches any code in `mlflow/server/js/`, you MUST run `yarn check-all` before committing:
 
 ```bash
-yarn --cwd mlflow/server/js check-all
+(cd mlflow/server/js && yarn check-all)
 ```
 
 ### Creating Pull Requests
PATCH

echo "Gold patch applied."
