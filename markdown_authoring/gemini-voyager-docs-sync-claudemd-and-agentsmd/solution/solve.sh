#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gemini-voyager

# Idempotency guard
if grep -qF "The bump script automatically updates `package.json`, `manifest.json`, and `mani" "AGENTS.md" && grep -qF "> **Note**: This file is mirrored in `AGENTS.md`. Keep both files in sync." "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -4,9 +4,10 @@ trigger: always_on
 
 # AGENTS.md - AI Assistant Guide for Gemini Voyager
 
-> **Last Updated**: 2026-03-05
-> **Version**: 1.3.1
+> **Last Updated**: 2026-03-11
+> **Version**: 1.3.4
 > **Purpose**: Comprehensive guide for AI assistants working with the Gemini Voyager codebase
+> **Note**: This file is mirrored in `CLAUDE.md`. Keep both files in sync.
 
 ---
 
@@ -163,7 +164,8 @@ beforeEach(() => {
 ```bash
 bun run test                # Run all tests
 bun run test <filename>     # Run specific test file
-bun run test:watch          # Interactive mode
+bun run test:watch          # Interactive watch mode
+bun run test:ui             # Visual UI test runner
 bun run test:coverage       # Check coverage
 ```
 
@@ -217,6 +219,20 @@ Examples:
 - `refactor(copy): introduce temml to convert tex2mathml`
 - `chore: update sponsors.svg`
 
+### Version Bump & Release
+
+```bash
+bun run bump              # Bumps patch version (e.g., 1.3.2 → 1.3.3)
+```
+
+After bumping, follow this workflow:
+
+1. Commit the version bump: `chore: bump to v{VERSION}`
+2. Create a git tag: `git tag v{VERSION}`
+3. Push with tags: `git push && git push --tags`
+
+The bump script automatically updates `package.json`, `manifest.json`, and `manifest.dev.json`, then runs `bun run format`.
+
 ### Definition of Done (DoD)
 
 Before claiming a task is complete, verify:
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,8 +1,9 @@
 # CLAUDE.md - AI Assistant Guide for Gemini Voyager
 
-> **Last Updated**: 2026-03-09
-> **Version**: 1.3.3
+> **Last Updated**: 2026-03-11
+> **Version**: 1.3.4
 > **Purpose**: Comprehensive guide for AI assistants working with the Gemini Voyager codebase
+> **Note**: This file is mirrored in `AGENTS.md`. Keep both files in sync.
 
 ---
 
@@ -159,7 +160,8 @@ beforeEach(() => {
 ```bash
 bun run test                # Run all tests
 bun run test <filename>     # Run specific test file
-bun run test:watch          # Interactive mode
+bun run test:watch          # Interactive watch mode
+bun run test:ui             # Visual UI test runner
 bun run test:coverage       # Check coverage
 ```
 
PATCH

echo "Gold patch applied."
