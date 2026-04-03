#!/usr/bin/env bash
set -euo pipefail

cd /workspace/zulip

# Idempotent: skip if already applied
if grep -q 'Zulip Chat Links' .claude/CLAUDE.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.claude/CLAUDE.md b/.claude/CLAUDE.md
index 32482a2857dd3..23be88655b15b 100644
--- a/.claude/CLAUDE.md
+++ b/.claude/CLAUDE.md
@@ -375,6 +375,13 @@ tools/            # Development and testing scripts
 docs/             # ReadTheDocs documentation source
 ```

+## Zulip Chat Links
+
+When you encounter a Zulip narrow URL (e.g., from `chat.zulip.org` in a
+GitHub issue, PR, or user message), use the `/fetch-zulip-messages` skill
+to read the conversation. Do not use `WebFetch` — it cannot access Zulip
+message content.
+
 ## Common Commands

 ```bash
diff --git a/.claude/skills/fetch-zulip-messages/fetch-zulip-web-public-messages b/.claude/skills/fetch-zulip-messages/fetch-zulip-web-public-messages
index 720ee445140f1..d4d1abc920b7a 100755
--- a/.claude/skills/fetch-zulip-messages/fetch-zulip-web-public-messages
+++ b/.claude/skills/fetch-zulip-messages/fetch-zulip-web-public-messages
@@ -40,15 +40,15 @@ def parse_zulip_url(url: str) -> tuple[str, int, str, str | None]:
     server_url = f"{parsed.scheme}://{parsed.netloc}"
     fragment = parsed.fragment

-    # Parse the narrow fragment: narrow/channel/ID-slug/topic/encoded-topic[/with/ID]
+    # Parse the narrow fragment: narrow/channel/ID-slug/topic/encoded-topic[/with|near/ID]
     match = re.match(
-        r"^narrow/(?:channel|stream)/(\d+)-([^/]*)/topic/([^/]+)(?:/with/(\d+))?$",
+        r"^narrow/(?:channel|stream)/(\d+)-([^/]*)/topic/([^/]+)(?:/(?:with|near)/(\d+))?$",
         fragment,
     )
     if not match:
         print(f"Error: Could not parse Zulip narrow URL: {url}", file=sys.stderr)
         print(
-            "Expected format: https://HOSTNAME/#narrow/channel/ID-name/topic/TOPIC[/with/MSG_ID]",
+            "Expected format: https://HOSTNAME/#narrow/channel/ID-name/topic/TOPIC[/with|near/MSG_ID]",
             file=sys.stderr,
         )
         sys.exit(1)

PATCH

echo "Patch applied successfully."
