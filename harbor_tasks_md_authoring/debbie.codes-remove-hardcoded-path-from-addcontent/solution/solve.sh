#!/usr/bin/env bash
set -euo pipefail

cd /workspace/debbie.codes

# Idempotency guard
if grep -qF "export NVM_DIR=\"$HOME/.nvm\" && [ -s \"$NVM_DIR/nvm.sh\" ] && \\. \"$NVM_DIR/nvm.sh\" " ".agents/skills/add-content/references/environment.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/add-content/references/environment.md b/.agents/skills/add-content/references/environment.md
@@ -68,11 +68,11 @@ git push origin add-<type>/<kebab-case-short-title>
 ### Install dependencies and start
 
 ```bash
-export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && cd /Users/debbieobrien/workspace/debbie.codes && npm install 2>&1 | tail -5
+export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && npm install 2>&1 | tail -5
 ```
 
 ```bash
-export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && cd /Users/debbieobrien/workspace/debbie.codes && npm run dev > /tmp/nuxt-dev.log 2>&1 &
+export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && npm run dev > /tmp/nuxt-dev.log 2>&1 &
 ```
 
 Wait for ready:
PATCH

echo "Gold patch applied."
