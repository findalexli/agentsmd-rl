#!/usr/bin/env bash
set -euo pipefail

cd /workspace/better-auth

# Idempotency guard
if grep -qF "[Next.js](https://nextjs.org/docs/llms.txt) + [Fumadocs](https://www.fumadocs.de" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,12 +1,12 @@
 # CLAUDE.md
 
-This file provides guidance to Claude Code (claude.ai/code) when working
-with code in this repository.
+This file provides guidance to AI assistants (Claude Code, Cursor, etc.)
+when working with code in this repository.
 
 ## Project Overview
 
-Better Auth is a comprehensive, framework-agnostic authentication library
-for TypeScript.
+Better Auth is a comprehensive, framework-agnostic authentication
+framework for TypeScript.
 
 ## Development Commands
 
@@ -45,21 +45,25 @@ run specific tests.
 
 ## Code Style
 
-* Avoid classes; prefer functions
-* Do not use runtime-specific feature like `Buffer` in codebase except test,
-  use `Uint8Array` instead.
+* Formatter: Biome (tabs for code, 2-space for JSON)
+* Avoid unsafe typecasts or types like `any`
+* Avoid classes, use functions and objects
+* Do not use runtime-specific feature like `Buffer` in codebase except
+  test, use `Uint8Array` instead
 
 ## Testing
 
 * Most of the tests use Vitest
 * Some tests under `e2e` directory use playwright
 * Adapter tests require Docker containers running (`docker compose up -d`)
+* Consider using test helpers like `getTestInstance()` from
+  `better-auth/test` first
 
 ## Documentation
 
 * Please update the documentation when you make changes to the public API
 * Documentation is located in the `docs/` directory, built with
-  [Next.js](https://nextjs.org/) + [Fumadocs](https://fumadocs.dev/)
+  [Next.js](https://nextjs.org/docs/llms.txt) + [Fumadocs](https://www.fumadocs.dev/llms.txt)
 
 ## Git Workflow
 
PATCH

echo "Gold patch applied."
