#!/usr/bin/env bash
set -euo pipefail

cd /workspace/obsidian-claude-pkm

# Idempotency guard
if grep -qF "Finds broken `[[wiki-links]]` across your vault by extracting link targets and v" "vault-template/.claude/skills/check-links/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/vault-template/.claude/skills/check-links/SKILL.md b/vault-template/.claude/skills/check-links/SKILL.md
@@ -0,0 +1,108 @@
+---
+name: check-links
+description: Find broken wiki-links in the vault. Read-only analysis — scans for [[links]] and verifies target files exist. No writes, no dependencies.
+allowed-tools: Grep, Glob, Read
+user-invocable: true
+---
+
+# Check Links Skill
+
+Finds broken `[[wiki-links]]` across your vault by extracting link targets and verifying that each target file exists. Read-only — never modifies files.
+
+## Usage
+
+```
+/check-links
+```
+
+Or ask:
+- "Check for broken links in my vault"
+- "Find dead wiki-links"
+- "Are there any broken links?"
+
+## How to Execute
+
+### Step 1: Extract all wiki-links
+
+Use **Grep** to find all `[[...]]` patterns in markdown files:
+
+```
+Grep:
+  pattern: "\\[\\[([^\\]|]+)"
+  glob: "*.md"
+  output_mode: content
+  -n: true
+```
+
+This captures the link target (before any `|` alias). Exclude `.claude/` and `.obsidian/` directories from results.
+
+### Step 2: Build unique target list
+
+From the grep results, extract the unique link targets. For each match like `[[My Note]]` or `[[My Note|display text]]`, the target is `My Note`.
+
+Strip:
+- Heading anchors: `[[Note#heading]]` → target is `Note`
+- Block references: `[[Note^block-id]]` → target is `Note`
+- Aliases: `[[Note|alias]]` → target is `Note`
+
+### Step 3: Verify each target exists
+
+For each unique target, use **Glob** to check if a matching file exists:
+
+```
+Glob:
+  pattern: "**/<target>.md"
+```
+
+A link is **broken** if no file matches. A link is **valid** if at least one file matches.
+
+### Step 4: Report results
+
+Group broken links by source file:
+
+```markdown
+## Broken Links Report
+
+### Daily Notes/2024-01-15.md
+- [[Projet Alpha]] — no matching file found
+- [[Old Goal]] — no matching file found
+
+### Projects/Project Beta.md
+- [[Meeting Notes Jan]] — no matching file found
+
+---
+
+**Summary:** 3 broken links across 2 files (out of 45 total links checked)
+```
+
+### Step 5: Suggest fixes
+
+For each broken link, try to find a close match:
+
+1. Use **Glob** with a partial pattern: `**/*<partial-target>*.md`
+2. If a similar filename exists, suggest it:
+   ```
+   - [[Projet Alpha]] — Did you mean [[Project Alpha]]?
+   ```
+3. If no close match, just report "no matching file found"
+
+## Edge Cases
+
+- **Embedded images** (`![[image.png]]`) — skip these, they reference attachments
+- **External links** (`[text](https://...)`) — skip these, they are not wiki-links
+- **Template placeholders** (`[[{{date}}]]`) — skip anything with `{{` in the target
+- **Empty links** (`[[]]`) — report as malformed, not broken
+
+## No Broken Links
+
+If all links are valid:
+
+```
+✅ All wiki-links verified — no broken links found across X files (Y links checked)
+```
+
+## Tips
+
+- Run `/check-links` periodically to catch link rot
+- After renaming files, run this to find links that need updating
+- Combine with `/search` to find notes that reference deleted content
PATCH

echo "Gold patch applied."
