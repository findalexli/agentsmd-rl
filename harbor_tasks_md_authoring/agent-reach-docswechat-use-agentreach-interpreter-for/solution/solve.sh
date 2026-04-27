#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-reach

# Idempotency guard
if grep -qF "AGENT_REACH_PYTHON=$(python3 -c \"import agent_reach, sys; print(sys.executable)\"" "agent_reach/skill/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/agent_reach/skill/SKILL.md b/agent_reach/skill/SKILL.md
@@ -108,13 +108,16 @@ mcporter call 'douyin.get_douyin_download_link(share_link: "https://v.douyin.com
 ## 微信公众号 / WeChat Articles
 
 **Search** (miku_ai):
-```python
-python3 -c "
+```bash
+# miku_ai is installed inside the agent-reach Python environment.
+# Use the same interpreter that runs agent-reach (handles pipx / venv installs):
+AGENT_REACH_PYTHON=$(python3 -c "import agent_reach, sys; print(sys.executable)" 2>/dev/null || echo python3)
+$AGENT_REACH_PYTHON -c "
 import asyncio
 from miku_ai import get_wexin_article
 async def s():
-    for a in await get_wexin_article('query', 5):
-        print(f'{a[\"title\"]} | {a[\"url\"]}')
+    for a in await get_wexin_article(\'query\', 5):
+        print(f\'{a[\"title\"]} | {a[\"url\"]}\')
 asyncio.run(s())
 "
 ```
PATCH

echo "Gold patch applied."
