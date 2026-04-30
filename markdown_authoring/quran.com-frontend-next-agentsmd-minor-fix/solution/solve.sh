#!/usr/bin/env bash
set -euo pipefail

cd /workspace/quran.com-frontend-next

# Idempotency guard
if grep -qF "- Run lint and typecheck after changes: `yarn lint && yarn build`" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -38,6 +38,4 @@ Follow all Cursor rules in `.cursor/rules/` including:
 - Follow Next.js Pages Router patterns (not App Router)
 - Implement proper i18n with next-translate
 - Use SCSS modules for component styling
-- Run lint and typecheck after changes: `yarn lint && yarn build`</content> </xai:function_call/>
-  </xai:function_call name="read">
-  <parameter name="filePath">/Users/ahmed/Projects/QuranFoundation/quran.com-frontend-next/AGENTS.md
+- Run lint and typecheck after changes: `yarn lint && yarn build`
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -98,7 +98,6 @@ repository.
 
 ### Build & Deployment
 
-- **Vercel** deployment with environment-based configurations
 - **Sentry** for error tracking and performance monitoring
 - **PWA** support with service workers
 - Bundle analysis and optimization
PATCH

echo "Gold patch applied."
