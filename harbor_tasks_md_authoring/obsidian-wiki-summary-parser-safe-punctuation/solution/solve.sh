#!/usr/bin/env bash
set -euo pipefail

cd /workspace/obsidian-wiki

# Idempotency guard
if grep -qF "**Write a `summary:` frontmatter field** on every new/updated page (1\u20132 sentence" ".skills/wiki-update/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.skills/wiki-update/SKILL.md b/.skills/wiki-update/SKILL.md
@@ -104,7 +104,8 @@ title: Page Title
 category: concepts
 tags: [tag1, tag2]
 sources: [projects/<project-name>]
-summary: One or two sentences (≤200 chars) describing what this page covers.
+summary: >-
+    One or two sentences (≤200 chars) describing what this page covers.
 provenance:
   extracted: 0.6
   inferred: 0.35
@@ -113,6 +114,9 @@ created: TIMESTAMP
 updated: TIMESTAMP
 ---
 
+Use folded scalar syntax (summary: >-) for summary to keep frontmatter parser-safe across punctuation (:, #, quotes) without escaping rules.
+Keep the summary content indented by two spaces under summary: >-.
+
 # Page Title
 
 - A fact the codebase or a doc actually states.
@@ -121,7 +125,7 @@ updated: TIMESTAMP
 Use [[wikilinks]] to connect to other pages.
 ```
 
-**Write a `summary:` frontmatter field** on every new/updated page (1–2 sentences, ≤200 chars). For project sync, a good summary answers "what does this page tell me about the project I wouldn't guess from its title?" This field powers cheap retrieval by `wiki-query`.
+**Write a `summary:` frontmatter field** on every new/updated page (1–2 sentences, ≤200 chars), using `>-` folded style. For project sync, a good summary answers "what does this page tell me about the project I wouldn't guess from its title?" This field powers cheap retrieval by `wiki-query`.
 
 **Apply provenance markers** per `llm-wiki` (Provenance Markers section). For project sync specifically:
 
PATCH

echo "Gold patch applied."
