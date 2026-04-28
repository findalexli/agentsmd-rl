#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-skills

# Idempotency guard
if grep -qF "| Field         | Required | Constraints                                        " "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -29,43 +29,142 @@ npm run validate -- {skill-name} # Validate specific skill
 npm run check                    # Format and lint (auto-fix)
 ```
 
-**Before completing any task**, run `npm run check` and `npm run build` to ensure CI passes.
+**Before completing any task**, run `npm run check` and `npm run build` to
+ensure CI passes.
 
 ## Creating a New Skill
 
 Skills follow the [Agent Skills Open Standard](https://agentskills.io/).
 
 1. Create directory: `mkdir -p skills/{skill-name}/references`
-2. Create `SKILL.md` with required frontmatter:
-   ```yaml
-   ---
-   name: skill-name
-   description: What this skill does and when to use it.
-   license: MIT
-   metadata:
-     author: your-org
-     version: "1.0.0"
-   ---
-   ```
+2. Create `SKILL.md` following the format below
 3. Add `references/_sections.md` defining sections
 4. Add reference files: `{prefix}-{reference-name}.md`
 5. Run `npm run build`
 
-## SKILL.md Format (Agent Skills Spec)
+---
+
+## Writing SKILL.md Files
+
+SKILL.md is the core of every skill. It consists of **YAML frontmatter**
+followed by **Markdown instructions**.
+
+### Frontmatter (Required)
 
 ```yaml
 ---
-name: skill-name                    # Required: must match directory name
-description: Description of skill.  # Required: what it does and when to use
-license: MIT                        # Optional: license
-metadata:                           # Optional: arbitrary key-value pairs
-  author: your-org
-  version: "1.0.0"
+name: skill-name
+description: What this skill does and when to use it.
 ---
 ```
 
+| Field         | Required | Constraints                                                                     |
+| ------------- | -------- | ------------------------------------------------------------------------------- |
+| `name`        | Yes      | 1-64 chars. Lowercase alphanumeric and hyphens only. Must match directory name. |
+| `description` | Yes      | 1-1024 chars. Describe what the skill does AND when to use it.                  |
+| `license`     | No       | License name or reference to bundled license file.                              |
+| `metadata`    | No       | Arbitrary key-value pairs (e.g., `author`, `version`).                          |
+
+### Name Field Rules
+
+- Lowercase letters, numbers, and hyphens only (`a-z`, `0-9`, `-`)
+- Must not start or end with `-`
+- Must not contain consecutive hyphens (`--`)
+- Must match the parent directory name
+
+```yaml
+# Valid
+name: pdf-processing
+name: data-analysis
+
+# Invalid
+name: PDF-Processing # uppercase not allowed
+name: -pdf # cannot start with hyphen
+name: pdf--processing # consecutive hyphens not allowed
+```
+
+### Description Field (Critical)
+
+The description is the **primary trigger mechanism**. Claude uses it to decide
+when to activate the skill.
+
+**Include both:**
+
+1. What the skill does
+2. Specific triggers/contexts for when to use it
+
+```yaml
+# Good - comprehensive and trigger-rich
+description: >
+  Supabase database best practices for schema design, RLS policies,
+  indexing, and query optimization. Use when working with Supabase
+  projects, writing PostgreSQL migrations, configuring Row Level Security,
+  or optimizing database performance.
+
+# Bad - too vague
+description: Helps with databases.
+```
+
+**Do not put "when to use" in the body.** The body loads only after triggering,
+so trigger context must be in the description.
+
+### Body Content
+
+The Markdown body contains instructions for using the skill. Write
+concisely—Claude is already capable. Only add context Claude doesn't already
+have.
+
+**Guidelines:**
+
+- Use imperative form ("Create the table", not "You should create the table")
+- Keep under 500 lines; move detailed content to `references/`
+- Prefer concise examples over verbose explanations
+- Challenge each paragraph: "Does this justify its token cost?"
+
+**Recommended structure:**
+
+1. Quick start or core workflow
+2. Key patterns with examples
+3. Links to reference files for advanced topics
+
+```markdown
+## Quick Start
+
+Create a table with RLS:
+
+[concise code example]
+
+## Common Patterns
+
+### Authentication
+
+[pattern with example]
+
+## Advanced Topics
+
+- **Complex policies**: See
+  [references/rls-patterns.md](references/rls-patterns.md)
+- **Performance tuning**: See
+  [references/optimization.md](references/optimization.md)
+```
+
+### Progressive Disclosure
+
+Skills use three loading levels:
+
+1. **Metadata** (~100 tokens) - Always loaded for all skills
+2. **Body** (<5k tokens recommended) - Loaded when skill triggers
+3. **References** (as needed) - Loaded on demand by Claude
+
+Keep SKILL.md lean. Move detailed reference material to separate files and link
+to them.
+
+---
+
 ## Reference File Format
 
+Reference files in `references/` extend skills with detailed documentation.
+
 ```markdown
 ---
 title: Action-Oriented Title
@@ -78,24 +177,18 @@ tags: keywords
 
 1-2 sentence explanation.
 
-**Incorrect:**
-\`\`\`sql
--- bad example
-\`\`\`
+**Incorrect:** \`\`\`sql -- bad example \`\`\`
 
-**Correct:**
-\`\`\`sql
--- good example
-\`\`\`
+**Correct:** \`\`\`sql -- good example \`\`\`
 ```
 
-## Impact Levels
+## What NOT to Include
+
+Skills should only contain essential files. Do NOT create:
+
+- README.md
+- INSTALLATION_GUIDE.md
+- QUICK_REFERENCE.md
+- CHANGELOG.md
 
-| Level       | Improvement                   | Use For                                                    |
-| ----------- | ----------------------------- | ---------------------------------------------------------- |
-| CRITICAL    | 10-100x or prevents failure   | Security vulnerabilities, data loss, breaking changes      |
-| HIGH        | 5-20x or major quality gain   | Architecture decisions, core functionality, scalability    |
-| MEDIUM-HIGH | 2-5x or significant benefit   | Design patterns, common anti-patterns, reliability         |
-| MEDIUM      | 1.5-3x or noticeable gain     | Optimization, best practices, maintainability              |
-| LOW-MEDIUM  | 1.2-2x or minor benefit       | Configuration, tooling, code organization                  |
-| LOW         | Incremental or edge cases     | Advanced techniques, rare scenarios, polish                |
+The skill should contain only what an AI agent needs to do the job.
PATCH

echo "Gold patch applied."
