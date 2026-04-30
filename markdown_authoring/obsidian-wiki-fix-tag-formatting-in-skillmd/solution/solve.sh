#!/usr/bin/env bash
set -euo pipefail

cd /workspace/obsidian-wiki

# Idempotency guard
if grep -qF "- [[transformer-architecture]] \u2014 The dominant architecture for sequence modeling" ".skills/llm-wiki/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.skills/llm-wiki/SKILL.md b/.skills/llm-wiki/SKILL.md
@@ -117,12 +117,15 @@ A content-oriented catalog organized by category. Each entry has a one-line summ
 # Wiki Index
 
 ## Concepts
-- [[transformer-architecture]] — The dominant architecture for sequence modeling (#ml #architecture)
-- [[attention-mechanism]] — Core building block of transformers (#ml #fundamentals)
+- [[transformer-architecture]] — The dominant architecture for sequence modeling ( #ml #architecture)
+- [[attention-mechanism]] — Core building block of transformers ( #ml #fundamentals)
 
 ## Entities
-- [[andrej-karpathy]] — AI researcher, educator, former Tesla AI director (#person #ml)
+- [[andrej-karpathy]] — AI researcher, educator, former Tesla AI director ( #person #ml)
 ```
+**Format rule**: Add a space after the opening `(` and tags.
+❌ Don't: `description (#tag)` — breaks tag parsing
+✅ Do: `description ( #tag)` — proper spacing and tag parsing
 
 ### `log.md`
 Chronological append-only record tracking every operation. Each entry is parseable:
PATCH

echo "Gold patch applied."
