#!/usr/bin/env bash
set -euo pipefail

cd /workspace/screenpipe

# Idempotency guard
if grep -qF "- always use progressive disclosure when designing agentic systems" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -43,10 +43,6 @@ Use `#` for Python, `//` for Rust/TS/JS/Swift. Keep it as the first comment in t
 ## git usage
 - make sure to understand there is always bunch of other agents working on the same codebase in parallel, never delete local code or use git reset or such
 
-## A/B test learnings (Mar-Apr 2026)
-- "automations" converts better than "pipes" for checkout (+32-95% lift)
-- shorter landing page (no search/chat/privacy sections) converts better (+78% lift)
-- hero headline "agents that watch you" vs "your computer finally works" — no difference
-- showing price in hero CTA ("$99/mo") slightly hurts vs plain "DOWNLOAD" (-18%)
-- prominent guarantee banner above pricing — no effect
-- annual plan shown first doubles annual uptake (36% vs 18%), similar total checkout rate
+## context
+
+- always use progressive disclosure when designing agentic systems
PATCH

echo "Gold patch applied."
