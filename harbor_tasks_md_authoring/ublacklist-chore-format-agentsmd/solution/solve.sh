#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ublacklist

# Idempotency guard
if grep -qF "AGENTS.md" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -44,21 +44,25 @@ pnpm generate:message-names     # Generate message name constants
 ### Key Subsystems
 
 **Ruleset Engine** (`src/scripts/ruleset/`):
+
 - Uses Lezer parser generated from `ruleset.grammar`
 - Supports match patterns (`*://*.example.com/*`) and expressions with regex, variables, string matchers
 - Parser output is `parser.generated.ts` - regenerate with `pnpm generate:ruleset-parser`
 
 **SERP Info System** (`src/scripts/serpinfo/`):
+
 - Declarative system for defining how to find/filter results on different search engines
 - `filter.ts` - Core filtering logic using MutationObserver
 - `schemas.ts` - Zod schemas for SERP configuration
 - User-defined configurations stored via `storage-store.ts`
 
 **Cloud Sync** (`src/scripts/clouds/`):
+
 - `google-drive.ts`, `dropbox.ts`, `webdav.ts`, `browser-sync.ts` - Provider implementations
 - `helpers.ts` - OAuth flow helpers with browser-specific handling
 
 **Storage** (`src/scripts/background/`):
+
 - `raw-storage.ts` - Low-level browser storage access
 - `local-storage.ts` - Application state management
 - `sync.ts` - Cloud synchronization logic
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1 +1 @@
-AGENTS.md
\ No newline at end of file
+AGENTS.md
PATCH

echo "Gold patch applied."
