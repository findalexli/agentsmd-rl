#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cloudbase-mcp

# Idempotency guard
if grep -qF "- If the product requirement says \"create when missing\", implement that as an ex" "config/source/skills/cloud-functions/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/config/source/skills/cloud-functions/SKILL.md b/config/source/skills/cloud-functions/SKILL.md
@@ -50,6 +50,7 @@ Keep local `references/...` paths for files that ship with the current skill dir
 - Confusing official CloudBase API client work with building your own HTTP function.
 - Mixing Event Function code shape (`exports.main(event, context)`) with HTTP Function code shape (`req` / `res` on port `9000`).
 - Treating HTTP Access as the implementation model for HTTP Functions. HTTP Access is a gateway configuration for Event Functions, not the HTTP Function runtime model.
+- Assuming `db.collection("name").add(...)` will create a missing document-database collection automatically. Collection creation is a separate management step.
 - Forgetting that runtime cannot be changed after creation.
 - Using cloud functions as the first answer for Web login.
 - Forgetting that HTTP Functions must ship `scf_bootstrap`, listen on port `9000`, and include dependencies.
@@ -111,6 +112,12 @@ Use this skill when developing, deploying, and operating CloudBase cloud functio
    - HTTP Function details -> `./references/http-functions.md`
    - Logs, gateway, env vars, and legacy mappings -> `./references/operations-and-config.md`
 
+## Database write reminder
+
+- If a function will write to CloudBase document database, create the target collection first through console or management tooling.
+- `db.collection("feedback").add(...)` only inserts into an existing collection; it does not auto-create `feedback` when absent.
+- If the product requirement says "create when missing", implement that as an explicit collection-management step before the first write instead of assuming the runtime write call will provision it.
+
 ## Function types comparison
 
 | Feature | Event Function | HTTP Function |
PATCH

echo "Gold patch applied."
