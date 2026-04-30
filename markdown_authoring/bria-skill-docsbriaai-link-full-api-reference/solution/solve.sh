#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bria-skill

# Idempotency guard
if grep -qF "If you are stuck on request shapes, parameters, or endpoints not covered here, *" "skills/bria-ai/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/bria-ai/SKILL.md b/skills/bria-ai/SKILL.md
@@ -15,6 +15,8 @@ metadata:
 
 Commercially safe, royalty-free image generation and editing through 20+ API endpoints. Generate from text, edit with natural language, remove backgrounds, create product shots, and build automated image pipelines.
 
+If you are stuck on request shapes, parameters, or endpoints not covered here, **fetch the full agent-oriented API reference** at [docs.bria.ai/llms.txt](https://docs.bria.ai/llms.txt) — it is the canonical LLM-ready documentation and the right place to look before guessing.
+
 ## When to Use This Skill
 
 Use this skill when the user wants to:
@@ -266,7 +268,9 @@ def get_result(status_url, api_key):
 
 ## API Reference
 
-See `references/api-endpoints.md` for complete endpoint documentation with request/response formats for all 20+ endpoints.
+For the **complete** Bria API (all endpoints, fields, and behaviors), use **[docs.bria.ai/llms.txt](https://docs.bria.ai/llms.txt)** — agent-ready docs meant for assistants implementing the API. Reach for it whenever this skill’s summary is not enough.
+
+See `references/api-endpoints.md` for complete endpoint documentation with request/response formats for all 20+ endpoints (in-repo companion to the quick reference above).
 
 ### Authentication
 
@@ -281,6 +285,7 @@ User-Agent: BriaSkills/1.2.7
 
 ## Additional Resources
 
+- **[Agent-ready API reference — llms.txt](https://docs.bria.ai/llms.txt)** — Full Bria API documentation for assistants; use when stuck on implementation details
 - **[API Endpoints Reference](references/api-endpoints.md)** — Complete endpoint documentation with request/response formats
 - **[Workflows & Pipelines](references/workflows.md)** — Batch generation, parallel pipelines, integration examples
 - **[Python Client](references/code-examples/bria_client.py)** — Full-featured async Python client
PATCH

echo "Gold patch applied."
