#!/usr/bin/env bash
set -euo pipefail

cd /workspace/byterover-cli

# Idempotency guard
if grep -qF "**Overview:** Store knowledge in the best available external memory provider. By" "src/server/templates/skill/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/server/templates/skill/SKILL.md b/src/server/templates/skill/SKILL.md
@@ -310,6 +310,169 @@ brv vc push -u origin main       # push and set upstream tracking
 brv vc clone https://byterover.dev/<team>/<space>.git
 ```
 
+### 8. Swarm Query
+**Overview:** Search across all active memory providers simultaneously — ByteRover context tree, Obsidian vault, Local Markdown folders, GBrain, and Memory Wiki. Results are fused via Reciprocal Rank Fusion (RRF) and ranked by provider weight and relevance. No LLM call — pure algorithmic search.
+
+**Use this skill when:**
+- You need to search across multiple knowledge sources at once
+- The user has configured multiple memory providers (check with `brv swarm status`)
+- You want results from Obsidian notes, GBrain entities, or wiki pages alongside ByteRover context
+
+**Do NOT use this skill when:**
+- The user only has ByteRover configured — use `brv query` instead (it synthesizes via LLM)
+- You need an LLM-synthesized answer — `brv swarm query` returns raw search results, not synthesized text
+
+```bash
+brv swarm query "How does JWT refresh work?"
+```
+
+Output:
+```
+Swarm Query: "How does JWT refresh work?"
+Type: factual | Providers: 4 queried | Latency: 398ms
+──────────────────────────────────────────────────
+1. [memory-wiki] sources/jwt-token-lifecycle.md    score: 0.0150  [keyword]
+   # JWT Token Lifecycle ...
+2. [obsidian] SwarmTestData/Authentication System.md    score: 0.0142  [keyword]
+   # Authentication System ...
+3. [gbrain] alex-chen    score: 0.0117  [semantic]
+   # Alex Chen — Senior Backend Engineer ...
+```
+
+**With explain mode** (shows classification, provider selection, enrichment):
+```bash
+brv swarm query "authentication patterns" --explain
+```
+
+Output:
+```
+Classification: factual
+Provider selection: 4 of 4 available
+  ✓ byterover    (healthy, selected, 0 results, 14ms)
+  ✓ obsidian    (healthy, selected, 5 results, 91ms)
+  ✓ memory-wiki    (healthy, selected, 2 results, 15ms)
+  ✓ gbrain    (healthy, selected, 1 results, 260ms)
+Enrichment:
+  byterover → obsidian
+  byterover → memory-wiki
+Results: 8 raw → 7 after RRF fusion + precision filtering
+```
+
+**JSON output:**
+```bash
+brv swarm query "rate limiting" --format json
+```
+
+Output:
+```json
+{
+  "meta": {
+    "queryType": "factual",
+    "totalLatencyMs": 340,
+    "providers": {
+      "byterover": { "selected": true, "resultCount": 0 },
+      "obsidian": { "selected": true, "resultCount": 5 },
+      "gbrain": { "selected": true, "resultCount": 1 },
+      "memory-wiki": { "selected": true, "resultCount": 1 }
+    }
+  },
+  "results": [
+    { "provider": "memory-wiki", "providerType": "memory-wiki", "score": 0.015, "content": "# Rate Limiting ..." }
+  ]
+}
+```
+
+**Limit results:**
+```bash
+brv swarm query "testing strategy" -n 5
+```
+
+**Flags:** `--explain` (show routing details), `--format json` (structured output), `-n <value>` (max results).
+
+### 9. Swarm Curate
+**Overview:** Store knowledge in the best available external memory provider. ByteRover automatically classifies the content type and routes accordingly: entities (people, orgs) go to GBrain, notes (meeting notes, TODOs) go to Local Markdown, general content goes to the first writable provider. Falls back to ByteRover context tree if no external providers are available.
+
+**Use this skill when:**
+- You want to store knowledge in an external provider (GBrain, Local Markdown, Memory Wiki)
+- The user has configured writable swarm providers
+
+**Do NOT use this skill when:**
+- You want to store in ByteRover's context tree specifically — use `brv curate` instead
+- No swarm providers are configured — use `brv curate` instead
+
+```bash
+brv swarm curate "Jane Smith is the CTO of TechCorp"
+```
+
+Output:
+```
+Stored to gbrain as concept/jane-smith-cto
+```
+
+**Target a specific provider:**
+```bash
+brv swarm curate "meeting notes: decided on JWT" --provider local-markdown:notes
+```
+
+Output:
+```
+Stored to local-markdown:notes as note-1776052527043.md
+```
+
+```bash
+brv swarm curate "Architecture uses event sourcing" --provider gbrain
+```
+
+Output:
+```
+Stored to gbrain as concept/event-sourcing-architecture
+```
+
+**JSON output:**
+```bash
+brv swarm curate "Test content" --format json
+```
+
+Output:
+```json
+{
+  "id": "note-1776052594462.md",
+  "provider": "local-markdown:project-docs",
+  "success": true,
+  "latencyMs": 1
+}
+```
+
+**Flags:** `--provider <id>` (target specific provider), `--format json` (structured output).
+
+### 10. Swarm Status
+**Overview:** Check provider health and write targets before running swarm query or curate. Use this to verify which providers are available and operational.
+
+**Use this skill when:**
+- Before running `brv swarm query` or `brv swarm curate` to check available providers
+- Diagnosing why swarm results are missing from a specific provider
+
+```bash
+brv swarm status
+```
+
+Output:
+```
+Memory Swarm Health Check
+════════════════════════════════════════
+  ✓ ByteRover       context-tree (always on)
+  ✓ Obsidian        /Users/you/Documents/MyObsidian
+  ✓ Local .md       1 folder(s)
+  ✓ GBrain          /Users/you/workspaces/gbrain
+  ✓ Memory Wiki     /Users/you/.openclaw/wiki/main
+
+Write Targets:
+  gbrain (entity, general)
+  local-markdown:project-docs (note, general)
+
+Swarm is operational (5/5 providers configured).
+```
+
 ## Data Handling
 
 **Storage**: All knowledge is stored as Markdown files in `.brv/context-tree/` within the project directory. Files are human-readable and version-controllable.
PATCH

echo "Gold patch applied."
