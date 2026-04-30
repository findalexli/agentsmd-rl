#!/usr/bin/env bash
set -euo pipefail

cd /workspace/obsidian-wiki

# Idempotency guard
if grep -qF "`visibility/` is a reserved tag group with special rules. These tags are **not**" ".skills/tag-taxonomy/SKILL.md" && grep -qF "Glob all `.md` files in the vault (excluding `_archives/`, `_raw/`, `.obsidian/`" ".skills/wiki-export/SKILL.md" && grep -qF "`visibility/` tags are system tags and do **not** count toward the 5-tag limit. " ".skills/wiki-ingest/SKILL.md" && grep -qF "If the user's query includes phrases like **\"public only\"**, **\"user-facing\"**, " ".skills/wiki-query/SKILL.md" && grep -qF "Pages can carry a `visibility/` tag to mark their intended reach. **This is enti" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.skills/tag-taxonomy/SKILL.md b/.skills/tag-taxonomy/SKILL.md
@@ -30,6 +30,25 @@ The canonical tag vocabulary lives at `$OBSIDIAN_VAULT_PATH/_meta/taxonomy.md`.
 
 **Always read this file before tagging.** It's the source of truth.
 
+## Reserved System Tags
+
+`visibility/` is a reserved tag group with special rules. These tags are **not** domain or type tags and are managed separately from the taxonomy vocabulary:
+
+| Tag | Purpose |
+|---|---|
+| `visibility/public` | Explicitly public — shown in all modes (same as no tag) |
+| `visibility/internal` | Team-only — excluded in filtered query/export mode |
+| `visibility/pii` | Sensitive data — excluded in filtered query/export mode |
+
+**Rules for `visibility/` tags:**
+- They do **not** count toward the 5-tag limit
+- Only one `visibility/` tag per page
+- Omit entirely when content is clearly public — no tag needed
+- Never add `visibility/internal` just because content is technical; use it only for genuinely team-restricted knowledge
+- When running a tag audit, report `visibility/` tag usage separately — do not flag them as unknown or non-canonical
+
+When normalizing tags, leave `visibility/` tags untouched — they are not subject to alias mapping.
+
 ## Mode 1: Tag Audit
 
 When the user wants to see the current state of tags:
diff --git a/.skills/wiki-export/SKILL.md b/.skills/wiki-export/SKILL.md
@@ -17,9 +17,22 @@ You are exporting the wiki's wikilink graph to structured formats so it can be u
 1. Read `.env` to get `OBSIDIAN_VAULT_PATH`
 2. Confirm the vault has pages to export — if fewer than 5 pages exist, warn the user and stop
 
+## Visibility Filter (optional)
+
+By default, **all pages are exported** regardless of visibility tags. This preserves existing behavior.
+
+If the user requests a filtered export — phrases like **"public export"**, **"user-facing export"**, **"exclude internal"**, **"no internal pages"** — activate **filtered mode**:
+
+- Build a **blocked tag set**: `{visibility/internal, visibility/pii}`
+- Skip any page whose frontmatter tags contain a blocked tag when building the node list
+- Skip any edge where either endpoint was excluded
+- Note the filter in the summary: `(filtered: visibility/internal, visibility/pii excluded)`
+
+Pages with no `visibility/` tag, or tagged `visibility/public`, are always included.
+
 ## Step 1: Build the Node and Edge Lists
 
-Glob all `.md` files in the vault (excluding `_archives/`, `_raw/`, `.obsidian/`, `index.md`, `log.md`, `_insights.md`).
+Glob all `.md` files in the vault (excluding `_archives/`, `_raw/`, `.obsidian/`, `index.md`, `log.md`, `_insights.md`). In filtered mode, also skip pages whose tags contain `visibility/internal` or `visibility/pii`.
 
 For each page, extract from frontmatter:
 - `id` — relative path from vault root, without `.md` extension (e.g. `concepts/transformers`)
diff --git a/.skills/wiki-ingest/SKILL.md b/.skills/wiki-ingest/SKILL.md
@@ -173,6 +173,13 @@ For each page in your plan:
 
 **Write a `summary:` frontmatter field** on every new page (1–2 sentences, ≤200 characters) answering "what is this page about?" for a reader who hasn't opened it. When updating an existing page whose meaning has shifted, rewrite the summary to match the new content. This field is what `wiki-query`'s cheap retrieval path reads — a missing or stale summary forces expensive full-page reads.
 
+**Apply a `visibility/` tag** if the content clearly warrants one (optional):
+- `visibility/internal` — architecture internals, system credentials patterns, team-only context
+- `visibility/pii` — content that references personal data, user records, or sensitive identifiers
+- No tag (default) — anything that's safe to surface in user-facing answers
+
+`visibility/` tags are system tags and do **not** count toward the 5-tag limit. When in doubt, omit — untagged pages are treated as public. Never add a visibility tag just because a topic sounds technical.
+
 **Apply provenance markers** per the convention in `llm-wiki` (Provenance Markers section):
 - Inferred claims get a trailing `^[inferred]`
 - Ambiguous/contested claims get a trailing `^[ambiguous]`
diff --git a/.skills/wiki-query/SKILL.md b/.skills/wiki-query/SKILL.md
@@ -18,6 +18,21 @@ You are answering questions against a compiled Obsidian wiki, not raw source doc
 1. Read `~/.obsidian-wiki/config` to get `OBSIDIAN_VAULT_PATH` (works from any project). Fall back to `.env` if you're inside the obsidian-wiki repo.
 2. Read `$OBSIDIAN_VAULT_PATH/index.md` to understand the wiki's scope and structure
 
+## Visibility Filter (optional)
+
+By default, **all pages are returned** regardless of visibility tags. This preserves existing behavior — nothing changes unless the user asks for it.
+
+If the user's query includes phrases like **"public only"**, **"user-facing"**, **"no internal content"**, **"as a user would see it"**, or **"exclude internal"**, activate **filtered mode**:
+
+- Build a **blocked tag set**: `{visibility/internal, visibility/pii}`
+- In the Index Pass (Step 2), skip any candidate whose frontmatter tags contain a blocked tag
+- In Section/Full Read passes (Steps 3–4), do not read or cite any blocked page
+- Synthesize the answer **only from allowed pages** — do not mention that excluded pages exist
+
+Pages with no `visibility/` tag, or tagged `visibility/public`, are always included.
+
+In filtered mode, note the filter in the Step 6 log entry: `mode=filtered`.
+
 ## Retrieval Protocol
 
 **Follow the Retrieval Primitives table in `llm-wiki/SKILL.md`.** Reading is the dominant cost of this skill — use the cheapest primitive that answers the question and escalate only when it can't. Never jump straight to full-page reads.
@@ -103,7 +118,7 @@ Compose your answer from wiki content:
 
 Append to `log.md`:
 ```
-- [TIMESTAMP] QUERY query="the user's question" result_pages=N mode=normal|index_only escalated=true|false
+- [TIMESTAMP] QUERY query="the user's question" result_pages=N mode=normal|index_only|filtered escalated=true|false
 ```
 
 ## Answer Format
diff --git a/AGENTS.md b/AGENTS.md
@@ -78,12 +78,30 @@ On repeat runs, it checks `last_commit_synced` in `.manifest.json` and only proc
 3. Only open page bodies when the index pass can't answer
 4. Return a synthesized answer with `[[wikilink]]` citations
 
+## Visibility Tags (optional)
+
+Pages can carry a `visibility/` tag to mark their intended reach. **This is entirely optional** — untagged pages behave exactly as they always have (visible everywhere). The system stays single-vault, single source of truth.
+
+| Tag | Meaning |
+|---|---|
+| *(no tag)* | Same as `visibility/public` — visible in all modes |
+| `visibility/public` | Explicitly public — visible in all modes |
+| `visibility/internal` | Team-only — excluded when querying in filtered mode |
+| `visibility/pii` | Sensitive data — excluded when querying in filtered mode |
+
+**Filtered mode** is opt-in, triggered by phrases like "public only", "user-facing answer", "no internal content", or "as a user would see it" in a query. Default mode shows everything.
+
+`visibility/` tags are **system tags** — they don't count toward the 5-tag limit and are listed separately from domain/type tags in the taxonomy.
+
+See `wiki-query` and `wiki-export` skills for how the filter is applied.
+
 ## Core Principles
 
 - **Compile, don't retrieve.** The wiki is pre-compiled knowledge. Update existing pages — don't append or duplicate.
 - **Track everything.** Update `.manifest.json` after ingesting, `index.md` and `log.md` after any operation.
 - **Connect with `[[wikilinks]]`.** Every page should link to related pages. This is what makes it a knowledge graph, not a folder of files.
 - **Frontmatter is required.** Every wiki page needs: `title`, `category`, `tags`, `sources`, `created`, `updated`.
+- **Single source of truth.** Visibility tags shape how content is surfaced — they don't duplicate or separate it.
 
 ## Architecture Reference
 
PATCH

echo "Gold patch applied."
