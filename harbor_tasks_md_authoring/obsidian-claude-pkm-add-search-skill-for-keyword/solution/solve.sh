#!/usr/bin/env bash
set -euo pipefail

cd /workspace/obsidian-claude-pkm

# Idempotency guard
if grep -qF "description: Search vault content by keyword using Grep. Zero dependencies \u2014 wor" "vault-template/.claude/skills/search/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/vault-template/.claude/skills/search/SKILL.md b/vault-template/.claude/skills/search/SKILL.md
@@ -0,0 +1,104 @@
+---
+name: search
+description: Search vault content by keyword using Grep. Zero dependencies — works in any vault without indexes or plugins. Groups results by directory for easy scanning.
+allowed-tools: Grep, Glob, Read
+user-invocable: true
+---
+
+# Search Skill
+
+Fast keyword search across all vault markdown files using the Grep tool. No indexes, no plugins, no setup — just structured search with directory grouping.
+
+## Usage
+
+```
+/search <term>
+```
+
+Examples:
+- `/search project planning`
+- `/search weekly review`
+- `/search TODO`
+
+## How to Execute
+
+When the user invokes `/search <term>`:
+
+### Step 1: Search for the term
+
+Use the **Grep** tool to search all `.md` files for the term:
+
+```
+Grep:
+  pattern: <search term>
+  glob: "*.md"
+  output_mode: content
+  -n: true
+  -C: 1
+```
+
+Exclude hidden directories (`.claude/`, `.obsidian/`) and templates:
+
+```
+Grep:
+  pattern: <search term>
+  glob: "*.md"
+  path: .
+  output_mode: content
+  -n: true
+  -C: 1
+```
+
+Filter out results from `.claude/`, `.obsidian/`, and `Templates/` directories.
+
+### Step 2: Group results by directory
+
+Organise matches into sections by their parent directory:
+
+- **Daily Notes/** — journal entries
+- **Goals/** — goal and vision documents
+- **Projects/** — project notes
+- **Archives/** — archived content
+- **Inbox/** — unprocessed items
+- **(root)** — top-level notes
+
+### Step 3: Present results
+
+Format output as:
+
+```markdown
+## Search: "<term>"
+
+### Daily Notes/
+- **2024-01-15.md** (line 23): ...matching context...
+- **2024-01-14.md** (line 8): ...matching context...
+
+### Projects/
+- **Project Alpha.md** (line 45): ...matching context...
+
+### Goals/
+- **2024 Goals.md** (line 12): ...matching context...
+
+**Found X matches across Y files**
+```
+
+### Step 4: Suggest related content
+
+After showing results, check if any matched files contain `[[wiki-links]]` to other notes. If so, briefly mention:
+
+```
+💡 Related notes mentioned in results: [[Note A]], [[Note B]]
+```
+
+## No Results
+
+If no matches are found:
+1. Suggest alternative search terms (synonyms, related words)
+2. Offer to search with case-insensitive matching if the original search was case-sensitive
+3. Suggest checking `Archives/` if not already included
+
+## Tips
+
+- Search is case-sensitive by default. Add `-i: true` to the Grep call for case-insensitive search
+- Use regex patterns for advanced searches: `task.*complete`, `#tag-name`
+- Combine with `/daily` to quickly find when something was mentioned
PATCH

echo "Gold patch applied."
