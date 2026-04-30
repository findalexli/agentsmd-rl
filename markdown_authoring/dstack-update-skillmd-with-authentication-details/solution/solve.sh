#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dstack

# Idempotency guard
if grep -qF "- OpenAI-compatible models: Use `service.url` from `dstack run get <run-name> --" "skills/dstack/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/dstack/SKILL.md b/skills/dstack/SKILL.md
@@ -219,7 +219,14 @@ resources:
 **Service endpoints:**
 - Without gateway: `<dstack server URL>/proxy/services/<project name>/<run name>/`
 - With gateway: `https://<run name>.<gateway domain>/`
-- For OpenAI-compatible models, use the `/v1/...` paths under the service URL and pass the dstack token in the `Authorization` header.
+- Authentication: Unless `auth` is `false`, include `Authorization: Bearer <DSTACK_TOKEN>` on all service requests.
+- OpenAI-compatible models: Use `service.url` from `dstack run get <run-name> --json` and append `/v1` as the base URL; do **not** use deprecated `service.model.base_url` for requests.
+- Example (with gateway):
+  ```bash
+  curl -sS -X POST "https://<run name>.<gateway domain>/v1/chat/completions" \
+    -H "Authorization: Bearer <dstack token>" \
+    -H "Content-Type: application/json" \
+    -d '{"model":"<model name>","messages":[{"role":"user","content":"Hello"}],"max_tokens":64}'
 
 [Concept documentation](https://dstack.ai/docs/concepts/services.md) | [Configuration reference](https://dstack.ai/docs/reference/dstack.yml/service.md)
 
@@ -235,7 +242,7 @@ resources:
   gpu: 24GB..
   disk: 200GB
 
-spot_policy: auto
+spot_policy: auto # other values: spot, on-demand
 idle_duration: 5m
 ```
 
PATCH

echo "Gold patch applied."
