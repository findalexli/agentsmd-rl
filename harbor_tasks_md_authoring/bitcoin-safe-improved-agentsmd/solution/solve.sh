#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bitcoin-safe

# Idempotency guard
if grep -qF "- take every change you do as an opportunity to improve architecture: think abou" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -6,6 +6,9 @@
 - avoid keyword-only `*` in method/function signatures unless explicitly requested.
 - Before you commit, run pre-commit ruff format. commit and push the changes (use a dedicated branch for each session). If the pre-commit returns errors, fix them. For the pre-commit to work you have to cd into the current project and activate the environment.
 - Ensure git hooks can resolve `python`: run commit/pre-commit commands with the project venv first on `PATH`, e.g. `PATH="$(poetry env info -p)/bin:$PATH" poetry run pre-commit run ruff-format --files <files>` and `PATH="$(poetry env info -p)/bin:$PATH" git commit -m "<message>"`.
+- do not use someenum(str, Enum),  but instead use someenum(Enum), then (de)serailization works type safe via BaseSaveableClass
+- do not use Callable arguments if possible
+- take every change you do as an opportunity to improve architecture: think about if the change does introduce or remove coupling and what architecture improvements this could be used for 
 
 ## App run + GUI interaction notes
 - Launch the app with `DISPLAY=desktop:0 poetry run python -m bitcoin_safe`.
PATCH

echo "Gold patch applied."
