#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "Only read files whose content is needed to write the six sections with concrete," "plugins/compound-engineering/skills/onboarding/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/onboarding/SKILL.md b/plugins/compound-engineering/skills/onboarding/SKILL.md
@@ -15,7 +15,7 @@ This skill always regenerates the document from scratch. It does not read or dif
 
 1. **Write for humans first** -- Clear prose that a new developer can read and understand. Agent utility is a side effect of good human writing, not a separate goal.
 2. **Show, don't just tell** -- Use ASCII diagrams for architecture and flow, markdown tables for structured information, and backtick formatting for all file paths, commands, and code references.
-3. **Six sections, each earning its place** -- Every section answers a question a new contributor will ask in their first hour. No speculative sections.
+3. **Six sections, each earning its place** -- Every section answers a question a new contributor will ask in their first hour. No speculative sections. Section 2 may be skipped for pure infrastructure with no consuming audience, producing five sections.
 4. **State what you can observe, not what you must infer** -- Do not fabricate design rationale or assess fragility. If the code doesn't reveal why a decision was made, don't guess.
 5. **Never include secrets** -- The onboarding document is committed to the repository. Never include API keys, tokens, passwords, connection strings with credentials, or any other secret values. Reference environment variable *names* (`STRIPE_SECRET_KEY`), never their *values*. If a `.env` file contains actual secrets, extract only the variable names.
 6. **Link, don't duplicate** -- When existing documentation covers a topic well, link to it inline rather than re-explaining.
@@ -50,7 +50,7 @@ Guided by the inventory, read files that are essential for understanding the cod
 
 Read files in parallel batches where there are no dependencies between them. For example, batch README.md, entry points, and AGENTS.md/CLAUDE.md together in a single turn since none depend on each other's content.
 
-Only read files whose content is needed to write the five sections with concrete, specific detail. The inventory already provides structure, languages, frameworks, scripts, and entry point paths -- don't re-read files just to confirm what the inventory already says. Different repos need different amounts of reading; a small CLI tool might need 4 files, a complex monorepo might need 20. Let the sections drive what you read, not an arbitrary count.
+Only read files whose content is needed to write the six sections with concrete, specific detail. The inventory already provides structure, languages, frameworks, scripts, and entry point paths -- don't re-read files just to confirm what the inventory already says. Different repos need different amounts of reading; a small CLI tool might need 4 files, a complex monorepo might need 20. Let the sections drive what you read, not an arbitrary count.
 
 **Priority order:**
 
@@ -65,7 +65,7 @@ Do not read files speculatively. Every file read should be justified by the inve
 
 ### Phase 3: Write ONBOARDING.md
 
-Synthesize the inventory data and key file contents into a document with exactly six sections. Write the file to the repo root.
+Synthesize the inventory data and key file contents into the sections defined below. Write the file to the repo root.
 
 **Title**: Use `# {Project Name} Onboarding Guide` as the document heading. Derive the project name from the inventory. Do not use the filename as a heading.
 
@@ -92,7 +92,7 @@ What to avoid:
 
 **Formatting requirements -- apply consistently throughout:**
 - Use backticks for all file names (`package.json`), paths (`src/routes/`), commands (`bun test`), function/class names, environment variables, and technical terms
-- Use markdown headers (`##`) for the five sections
+- Use markdown headers (`##`) for each section
 - Use ASCII diagrams and markdown tables where specified below
 - Use bold for emphasis sparingly
 - Keep paragraphs short -- 2-4 sentences
PATCH

echo "Gold patch applied."
