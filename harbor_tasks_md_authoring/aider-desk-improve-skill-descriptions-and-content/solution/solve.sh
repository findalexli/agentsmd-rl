#!/usr/bin/env bash
set -euo pipefail

cd /workspace/aider-desk

# Idempotency guard
if grep -qF "description: Create and configure AiderDesk agent profiles by defining tool grou" ".aider-desk/skills/agent-creator/SKILL.md" && grep -qF "description: Create AiderDesk Agent Skills by writing SKILL.md files, defining f" ".aider-desk/skills/skill-creator/SKILL.md" && grep -qF "description: Create new AiderDesk UI themes by defining SCSS color variables, re" ".aider-desk/skills/theme-factory/SKILL.md" && grep -qF "description: Write unit tests, component tests, and integration tests for AiderD" ".aider-desk/skills/writing-tests/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.aider-desk/skills/agent-creator/SKILL.md b/.aider-desk/skills/agent-creator/SKILL.md
@@ -1,19 +1,15 @@
 ---
 name: agent-creator
-description: Create AiderDesk agent profiles via interactive Q&A.
+description: Create and configure AiderDesk agent profiles by defining tool groups, approval rules, subagent settings, and provider/model selection. Use when setting up a new agent, creating a profile, or configuring agent tools and permissions.
 ---
 
 # Agent Profile Creator
 
 Create agent profiles stored as `config.json` in `~/.aider-desk/agents/{name}/` (global) or `{project}/.aider-desk/agents/{name}/` (project-level).
 
-**READ REFERENCES** before proposing to ensure accuracy:
-- Tool groups & schema: `references/agent-profile-schema.md`
-- Tool approvals: `references/tool-approval-guide.md` + `references/agent-profile-schema.md`
-- Subagent config: `references/subagent-guide.md`
-- Examples: `references/profile-examples.md`
+Read all reference files before proposing a profile to ensure accuracy.
 
-## Simplified Q&A Process
+## Q&A Process
 
 ### Step 1: Understand Purpose
 
@@ -27,8 +23,6 @@ Based on their response, **internally propose** all properties:
 - Subagent config (always enabled, contextMemory: "off" by default)
 - Tool approvals (based on needs)
 
-**READ all reference files** before proposing.
-
 ### Step 2: Provider/Model
 
 Ask: "Which provider/model? (format: provider/model, e.g., anthropic/claude-sonnet-4-5-20250929)"
@@ -68,23 +62,7 @@ Show:
 
 ### Step 6: Create
 
-On user confirmation, generate the profile.
-
-**READ `references/profile-examples.md`** to verify structure before creating files.
-
-## Tool Group Reference
-
-- **Power Tools**: File system, shell, search (for agents that read/write files)
-- **Aider Tools**: AI code generation via Aider (NOT default - see note below)
-- **Power Search**: Advanced code search (for analysis/docs)
-- **Todo Tools**: Task list management (for agents that track work)
-- **Memory Tools**: Persistent information storage (for learning agents)
-- **Skills Tools**: Access to project-specific skills (for agents using custom skills)
-- **Subagents**: Task delegation to specialized subagents (for agents that can call others)
-
-**Aider Tools Note**: Specialized for AI code generation. Do NOT enable by default.
-- If user wants coding: explain Aider (advanced refactoring) vs Power Tools (direct editing)
-- Ask preference before enabling
+On user confirmation, generate the profile. Verify structure against `references/profile-examples.md` before creating files.
 
 ## Tool Approval Strategy
 
@@ -94,15 +72,11 @@ On user confirmation, generate the profile.
 - **"never"**: Tools completely irrelevant (e.g., `power---bash` for read-only agents)
 - **"always"**: Safe, essential tools (e.g., read operations for reviewers)
 
-**READ `references/tool-approval-guide.md`** to see all available tools and their purposes.
-
-Only include tools that exist in reference docs.
+Only include tools that exist in `references/tool-approval-guide.md`.
 
 ## Subagent Configuration
 
-**Every agent is a subagent (enabled: true)**
-
-**READ `references/subagent-guide.md`** for detailed guidance on context memory modes and configuration:
+**Every agent is a subagent (enabled: true)**. See `references/subagent-guide.md` for detailed guidance.
 
 - `contextMemory`: **Default is `"off"`** (fresh each time)
   - Use `"full-context"` only for specialized analysis agents (code review, security audit)
@@ -112,11 +86,24 @@ Only include tools that exist in reference docs.
 - `color`: Relevant color (e.g., red=security, blue=power tools)
 - `description`: Clear description for auto-invocation
 
-## File Structure
-
-```
-{profile-name}/
-└── config.json
+## Minimal config.json Structure
+
+```json
+{
+  "name": "my-agent",
+  "provider": "anthropic",
+  "model": "claude-sonnet-4-5-20250929",
+  "maxIterations": 250,
+  "toolGroups": ["power", "todo"],
+  "toolApprovals": {
+    "power---bash": "ask",
+    "power---read": "always"
+  },
+  "subagent": {
+    "enabled": true,
+    "contextMemory": "off"
+  }
+}
 ```
 
 ## Validation
diff --git a/.aider-desk/skills/skill-creator/SKILL.md b/.aider-desk/skills/skill-creator/SKILL.md
@@ -1,7 +1,7 @@
 ---
 name: skill-creator
 # prettier-ignore
-description: Design and create Agent Skills using progressive disclosure principles. Use when building new skills, planning skill architecture, or writing skill content.
+description: Create AiderDesk Agent Skills by writing SKILL.md files, defining frontmatter metadata, structuring references, and organizing skill directories. Use when building a new skill, creating a SKILL.md, planning skill architecture, or writing skill content.
 ---
 
 # Skill Creator
@@ -27,6 +27,45 @@ Skills load in 3 levels:
 
 **Key**: Keep Levels 1 & 2 lean. Move details to Level 3.
 
+## Quick Workflow
+
+1. Create skill directory: `.aider-desk/skills/my-skill/`
+2. Write `SKILL.md` with YAML frontmatter (`name`, `description`) and body instructions
+3. Add detailed docs to `references/` as needed
+4. Verify: mention a trigger keyword — skill should appear in active skills sidebar
+
+**If skill doesn't load**: check YAML syntax is valid, `name` is lowercase-hyphenated, and `description` contains the trigger terms users would say
+
+### SKILL.md Example
+
+```yaml
+---
+name: deploy-helper
+description: Deploy AiderDesk builds to staging and production environments. Use when deploying, releasing, or publishing builds.
+---
+```
+
+```markdown
+# Deploy Helper
+
+Build and deploy AiderDesk to target environments.
+
+## Steps
+
+1. Run `npm run build` to generate production artifacts
+2. Verify build output exists in `dist/`
+3. Deploy to staging: `./scripts/deploy.sh staging`
+4. Verify deployment: check health endpoint returns 200
+
+## Troubleshooting
+
+- Build fails: check `tsconfig.json` paths and run `npm run typecheck`
+
+## References
+
+- [environments.md](references/environments.md) - Environment configs
+```
+
 ## Structure
 
 ```
diff --git a/.aider-desk/skills/theme-factory/SKILL.md b/.aider-desk/skills/theme-factory/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: theme-factory
-description: Step-by-step guide to add a new UI theme to AiderDesk (SCSS + CSS variables + types + i18n).
+description: Create new AiderDesk UI themes by defining SCSS color variables, registering theme types, and adding i18n display names. Use when adding a theme, creating a color scheme, customizing appearance, or implementing dark mode and light mode variants.
 ---
 
 # Theme Factory
diff --git a/.aider-desk/skills/writing-tests/SKILL.md b/.aider-desk/skills/writing-tests/SKILL.md
@@ -1,6 +1,6 @@
 ---
-name: Writing Tests
-description: Comprehensive guide for writing unit tests, integration tests, and component tests in AiderDesk using Vitest. Use when creating new tests, configuring mocks, or organizing test files.
+name: writing-tests
+description: Write unit tests, component tests, and integration tests for AiderDesk using Vitest and React Testing Library. Use when creating new tests, adding test coverage, configuring mocks, setting up test files, or debugging failing tests.
 ---
 
 # Writing Tests
@@ -38,6 +38,14 @@ Test React components in `src/renderer`. Focus on user interactions and props.
 Use centralized mock factories for consistent testing across components and contexts.
 - [references/mocking-guide.md](references/mocking-guide.md) - Mock factories and API patterns
 
+## Debugging Failing Tests
+
+1. Read the error output and identify the failing assertion
+2. Check mock setup — verify `vi.mock()` paths and return values match expectations
+3. For component tests, inspect rendered output with `screen.debug()`
+4. Run a single test in isolation: `npm run test:node -- --no-color -t "test name"`
+5. Verify coverage: `npm run test:coverage` to confirm new code is tested
+
 ## Advanced Usage
 
 For detailed information:
PATCH

echo "Gold patch applied."
