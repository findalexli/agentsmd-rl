#!/usr/bin/env bash
set -euo pipefail

cd /workspace/docling-java

# Idempotency guard
if grep -qF "- All commits must include DCO sign-off (`git commit -s`)" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -61,5 +61,6 @@ This is a multi-module Gradle project (Kotlin DSL) with group `ai.docling`. Vers
 ## Conventions
 
 - Commits must follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
+- All commits must include DCO sign-off (`git commit -s`)
 - `spotless` uses `ratchetFrom("origin/main")` — only files changed relative to `origin/main` are checked
 - Line endings: LF; no trailing whitespace; files must end with a newline (`.editorconfig`)
PATCH

echo "Gold patch applied."
