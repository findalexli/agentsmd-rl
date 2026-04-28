#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vibesos

# Idempotency guard
if grep -qF "-H \"Authorization: Bearer $(cat ~/.vibes/auth.json | python3 -c \"import sys,json" "skills/factory/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/factory/SKILL.md b/skills/factory/SKILL.md
@@ -101,7 +101,7 @@ VIBES_ROOT="${CLAUDE_PLUGIN_ROOT:-$(dirname "$(dirname "${CLAUDE_SKILL_DIR}")")}
 APP_NAME="${1:-}"
 if [ -n "$APP_NAME" ]; then
   curl -s "https://factory.vibesos.com/connect/status/$APP_NAME" \
-    -H "Authorization: Bearer $(cat ~/.vibes/auth.json | grep -o '"token":"[^"]*"' | cut -d'"' -f4)" 2>/dev/null
+    -H "Authorization: Bearer $(cat ~/.vibes/auth.json | python3 -c "import sys,json; print(json.load(sys.stdin)['accessToken'])")" 2>/dev/null
 fi
 ```
 
@@ -223,7 +223,7 @@ Description: |
 
 **Get the auth token:**
 ```bash
-TOKEN=$(cat ~/.vibes/auth.json | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])" 2>/dev/null || echo "")
+TOKEN=$(cat ~/.vibes/auth.json | python3 -c "import sys,json; print(json.load(sys.stdin)['accessToken'])" 2>/dev/null || echo "")
 ```
 
 **Create Stripe Connect account:**
PATCH

echo "Gold patch applied."
