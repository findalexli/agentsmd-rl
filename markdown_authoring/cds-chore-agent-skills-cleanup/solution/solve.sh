#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cds

# Idempotency guard
if grep -qF "- Use the `git.repo-manager` skill (`.claude/skills/git.repo-manager/SKILL.md`) " ".claude/agents/design-system-researcher.md" && grep -qF ".claude/skills/code-review/SKILL.md" ".claude/skills/code-review/SKILL.md" && grep -qF "description: Use this skill whenever working on CDS React components in any pack" ".claude/skills/components.best-practices/SKILL.md" && grep -qF "**Usage:** `/components.styles <ComponentName> [additional context]`" ".claude/skills/components.styles/README.md" && grep -qF "description: Guidelines writing styles API (styles, classNames, and static class" ".claude/skills/components.styles/SKILL.md" && grep -qF "- `/component-docs LineChart add examples for real-time data updates`" ".claude/skills/components.write-docs/README.md" && grep -qF "description: Guidelines for creating or updating documentation for a CDS compone" ".claude/skills/components.write-docs/SKILL.md" && grep -qF "name: dev.cds-mobile" ".claude/skills/dev.cds-mobile/SKILL.md" && grep -qF "name: dev.cds-web" ".claude/skills/dev.cds-web/SKILL.md" && grep -qF ".claude/skills/feature-planner/SKILL.md" ".claude/skills/feature-planner/SKILL.md" && grep -qF "- **ALWAYS** reference the guidelines for writing code connect mappings in the `" ".claude/skills/figma.audit-connect/SKILL.md" && grep -qF "description: Guidelines for writing Figma Code Connect property mappings. Use th" ".claude/skills/figma.connect-best-practices/SKILL.md" && grep -qF "- ALWAYS reference the guidelines for writing code connect mappings in the `figm" ".claude/skills/figma.create-connect/SKILL.md" && grep -qF "description: Analyzes the previous N commits for breaking changes across the CDS" ".claude/skills/git.detect-breaking-changes/SKILL.md" && grep -qF "name: git.repo-manager" ".claude/skills/git.repo-manager/SKILL.md" && grep -qF "name: research.component-libs" ".claude/skills/research.component-libs/SKILL.md" && grep -qF "If you are researching a single deprecation, find it in this monorepo's source c" ".claude/skills/research.deprecation-usage/SKILL.md" && grep -qF ".claude/skills/summarize-commits/SKILL.md" ".claude/skills/summarize-commits/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/agents/design-system-researcher.md b/.claude/agents/design-system-researcher.md
@@ -99,7 +99,7 @@ Follow this systematic approach:
    - If the theme of the research goal cannot be found within the project source code, abandon the research task
 
 2. **Environment Preparation**
-   - Use the `github-repo-manager` skill (`.claude/skills/github-repo-manager/SKILL.md`) to ensure the project's repository is cloned and up to date in `temp/repo-cache/`.
+   - Use the `git.repo-manager` skill (`.claude/skills/git.repo-manager/SKILL.md`) to ensure the project's repository is cloned and up to date in `temp/repo-cache/`.
    - Only manage the single repository you are researching.
 
 3. **Deep Technical Analysis**
diff --git a/.claude/skills/code-review/SKILL.md b/.claude/skills/code-review/SKILL.md
@@ -1,15 +0,0 @@
----
-name: code-review
-description: Use these rules to review CDS React component code
-disable-model-invocation: true
----
-
-# CDS React Component Code Reviews
-
-Check for the following:
-
-- Structure: does the component's file follow the correct structure of imports, styles, types, and component?
-- Type safety: were any changes made backwards compatible? Were there any breaking changes? Are props clearly typed and following best practices? Are there any props that are unused / missing?
-- Styling: does the component rely on css variables and theme tokens where possible? Are there any missing className or styles props?
-- Accessibility: does the component follow best practices for accessibility for the platform?
-- Tests & stories: is the component used in a meaningful way by Jest tests and have story examples?
diff --git a/.claude/skills/components.best-practices/SKILL.md b/.claude/skills/components.best-practices/SKILL.md
@@ -1,6 +1,6 @@
 ---
-name: development-react-components
-description: USE THIS whenever you are working on CDS React components
+name: components.best-practices
+description: Use this skill whenever working on CDS React components in any package.
 user-invocable: false
 ---
 
diff --git a/.claude/skills/components.styles/README.md b/.claude/skills/components.styles/README.md
@@ -0,0 +1,12 @@
+# components.styles agent skill
+
+This skill may be invoked by the user following the examples below.
+
+**Usage:** `/components.styles <ComponentName> [additional context]`
+
+Examples:
+
+- `/components.styles SlideButton`
+- `/components.styles Button add static classnames for sub elements`
+- `/components.styles Select add styles documentation`
+- `/components.styles Avatar mobile only`
diff --git a/.claude/skills/components.styles/SKILL.md b/.claude/skills/components.styles/SKILL.md
@@ -1,22 +1,10 @@
 ---
-name: component-styles
-description: Guidelines writing styles API (styles, classNames, and static classNames) for a CDS component.
-model: claude-sonnet-4-6
-disable-model-invocation: true
+name: components.styles
+description: Guidelines writing styles API (styles, classNames, and static classNames) for a CDS component. Use this skill when adding customization options to a React component via `styles` or `classNames` props or when needing to update the docsite with component styles documentation.
+argument-hint: <ComponentName> [additional context] (e.g., "Button", "LineChart add real-time examples")
 ---
 
-# Component Styles
-
-Add styles API (styles, classNames, and static classNames) to a CDS component.
-
-**Usage:** `/component-styles <ComponentName> [additional context]`
-
-Examples:
-
-- `/component-styles SlideButton`
-- `/component-styles Button add static classnames for sub elements`
-- `/component-styles Select add styles documentation`
-- `/component-styles Avatar mobile only`
+Goal: Add styles API (styles, classNames, and static classNames) to a CDS component and/or update the component documentation with styles documentation.
 
 If no component name is provided, ask the user which component they want to add styles to.
 
@@ -349,13 +337,11 @@ After adding the styles API to the component, update the documentation:
    yarn nx run docs:docgen
    ```
 
-2. **Create or update the styles documentation** following the `/component-docs` command guidelines:
+2. **Create or update the styles documentation** use the `components.write-docs` SKILL for general knowledge on how to write component documentation:
    - Create `_webStyles.mdx` with ComponentStylesTable and StylesExplorer
    - Create `_mobileStyles.mdx` with ComponentStylesTable (if mobile)
    - Update `index.mdx` to import and render the styles tables
 
-See `.cursor/commands/component-docs.md` for detailed documentation templates.
-
 ## Final Checklist
 
 Before completing, verify:
@@ -370,5 +356,5 @@ Before completing, verify:
 - [ ] Special rendering conditions documented in JSDoc
 - [ ] Tests added for static classNames (web only) - see Step 4.4
 - [ ] Ran `yarn nx run docs:docgen` to regenerate styles data
-- [ ] Documentation updated (see `/component-docs` command)
+- [ ] Documentation updated to include new component styles information
 - [ ] Updated this file's "Approved Selector Names" table if new selectors were added
diff --git a/.claude/skills/components.write-docs/README.md b/.claude/skills/components.write-docs/README.md
@@ -0,0 +1,11 @@
+# components.write-docs agent skill
+
+This skill may be invoked by the user following the examples below.
+
+**Usage:** `/component-docs <ComponentName> [additional context]`
+
+Examples:
+
+- `/component-docs Button`
+- `/component-docs LineChart add examples for real-time data updates`
+- `/component-docs Avatar needs accessibility improvements`
diff --git a/.claude/skills/components.write-docs/SKILL.md b/.claude/skills/components.write-docs/SKILL.md
@@ -1,22 +1,11 @@
 ---
-name: component-docs
-description: Guidelines for creating or updating documentation for a CDS component on the docsite (apps/docs/).
+name: components.write-docs
+description: Guidelines for creating or updating documentation for a CDS component on the docsite (apps/docs/). Use this skill after creating or making updates to a CDS React component to write high quality documentaiton in the CDS docsite.
 argument-hint: <ComponentName> [additional context] (e.g., "Button", "LineChart add real-time examples")
 model: claude-sonnet-4-6
-disable-model-invocation: true
 ---
 
-# Component Documentation
-
-Create or update documentation for a CDS component on the docsite (apps/docs/).
-
-**Usage:** `/component-docs <ComponentName> [additional context]`
-
-Examples:
-
-- `/component-docs Button`
-- `/component-docs LineChart add examples for real-time data updates`
-- `/component-docs Avatar needs accessibility improvements`
+Goal: Create or update documentation for a CDS component on the docsite (apps/docs/).
 
 If no component name is provided, ask the user which component they want to document.
 
@@ -49,7 +38,7 @@ Review these before writing to ensure consistency in style, structure, and depth
 When writing examples, reference these files for valid values:
 
 - **Icon names** (`packages/icons/src/IconName.ts`) - All valid icon names (e.g., `'checkmark'`, `'close'`, `'warning'`)
-- **Design tokens** - Follow `.cursor/rules/react-component-development.mdc` for valid CDS design token values (Color, Space, BorderRadius, Font, etc.)
+- **Design tokens** - Use the `components.best-practices` SKILL for knowledge on valid CDS design token values (Color, Space, BorderRadius, Font, etc.)
 
 ## Step 2: Research Phase (for new docs or major updates)
 
@@ -686,7 +675,7 @@ Before completing, verify:
 - [ ] All imports use correct source categories
 - [ ] Component description is clear and helpful
 - [ ] Added storybook/figma links if story files exist or links are provided
-- [ ] Design token values are valid (reference `.cursor/rules/react-component-development.mdc`)
+- [ ] Design token values are valid (followed `components.best-practices` SKILL)
 
 ## Additional Notes
 
diff --git a/.claude/skills/dev.cds-mobile/SKILL.md b/.claude/skills/dev.cds-mobile/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: development-cds-mobile
+name: dev.cds-mobile
 description: USE THIS when asked to work on a new or existing (MOBILE) CDS React component in packages/mobile
 ---
 
diff --git a/.claude/skills/dev.cds-web/SKILL.md b/.claude/skills/dev.cds-web/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: development-cds-web
+name: dev.cds-web
 description: USE THIS when asked to work on a new or existing (WEB) CDS React component in packages/web
 ---
 
diff --git a/.claude/skills/feature-planner/SKILL.md b/.claude/skills/feature-planner/SKILL.md
@@ -92,7 +92,6 @@ The plan should include:
   - **Existing patterns to follow** — Reference specific existing files the engineer should model their work after (e.g., "follow the pattern in `Switch.tsx` for controlled/uncontrolled behavior"). Note which existing utilities, hooks, or base components to reuse.
 - **Suggested implementation steps** — A numbered list of steps an engineer would follow, in order. Each step should be concrete and actionable.
 - **Test strategy** — Key test cases the engineer should cover, organized by category (unit tests, accessibility, integration). Reference existing test files as patterns to follow.
-- **Relevant skills** — List any CDS skills the engineer should invoke when implementing (e.g., `/development-cds-web` for a new web component).
 - **Open questions for the engineer** — Anything that requires a technical decision the designer can't make (e.g., "should this use framer-motion or CSS transitions?"). Keep this section focused — only include genuine technical trade-offs, not things you could reasonably decide yourself.
 - **What's NOT in scope** — Explicitly call out visual design details (exact colors, spacing, typography) as something to be finalized in a follow-up session between the engineer and designer. This avoids premature decisions. Note: this section is about deferring _visual_ decisions — it should NOT be used to skip technical depth. The plan should be as technically detailed as possible while keeping visual design open.
 
diff --git a/.claude/skills/figma.audit-connect/SKILL.md b/.claude/skills/figma.audit-connect/SKILL.md
@@ -36,7 +36,7 @@ Within the current mapping file:
 
 2. **Identify Property Types Correctly**
    Before analyzing mappings, study the Figma metadata you found:
-   - **ALWAYS** reference the guidelines for writing code connect mappings here: .cursor/rules/code-connect.mdc
+   - **ALWAYS** reference the guidelines for writing code connect mappings in the `figma.connect-best-practices` SKILL
    - **Component Properties**: Boolean toggles, dropdowns/enums in the properties panel
    - **Property Values**: Options within enum properties (e.g., "disabled" is a value of "state")
    - **Text Layers**: Named text layers that need `figma.textContent()`
diff --git a/.claude/skills/figma.connect-best-practices/SKILL.md b/.claude/skills/figma.connect-best-practices/SKILL.md
@@ -1,6 +1,6 @@
 ---
-name: code-connect-best-practice
-description: Guidelines for writing Figma Code Connect property mappings. Use when working on Figma Code Connect files, which typically end in .figma.tsx.
+name: figma.connect-best-practices
+description: Guidelines for writing Figma Code Connect property mappings. Use this skill when working on Figma Code Connect files, which typically end in .figma.tsx.
 ---
 
 # Guidelines for writing Figma Code Connect mappings
diff --git a/.claude/skills/figma.create-connect/SKILL.md b/.claude/skills/figma.create-connect/SKILL.md
@@ -36,7 +36,7 @@ If you do not have either, MUST NEVER proceed with the task.
    - Study the React props for the component(s)
 
 3. **Generate Code Connect Mapping File**
-   - ALWAYS reference the guidelines for writing code connect mappings here: .cursor/rules/code-connect.mdc
+   - ALWAYS reference the guidelines for writing code connect mappings in the `figma.connect-best-practices` SKILL
    - Create the mapping file for the component
    - Provide a brief description of the mappings you created when you are done.
    - ALWAYS check to make sure there are no EsLint errors or warnings in your new mapping file.
diff --git a/.claude/skills/git.detect-breaking-changes/SKILL.md b/.claude/skills/git.detect-breaking-changes/SKILL.md
@@ -1,6 +1,6 @@
 ---
-name: detect-breaking-changes
-description: Analyzes the previous N commits for breaking changes across the CDS public API surface
+name: git.detect-breaking-changes
+description: Analyzes the previous N commits for breaking changes across the CDS public API surface. Use this skill when you need to check if any recent changes will cause breaking changes in the CDS public API surface.
 allowed-tools: Bash(git log:*), Bash(git show:*), Bash(git diff:*), Bash(git rev-parse:*), Read, Glob, Grep
 argument-hint: [Number of commits to review]
 model: opus
diff --git a/.claude/skills/git.repo-manager/SKILL.md b/.claude/skills/git.repo-manager/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: github-repo-manager
+name: git.repo-manager
 description: Instructions to manage a local cache of GitHub repositories. This would typically done in cases where the user want to perform research/analysis on a repository. Invoke whenever you need to clone a repo that isn't present locally, bring an existing clone up to date, or remove a repo from the cache. This skill handles only the mechanical filesystem/git operations — not research, analysis, or anything about the repo's contents.
 allowed-tools: Bash(git clone *), Bash(git pull *), Bash(rm -rf temp/repo-cache/*), Bash(test -d temp/repo-cache/*)
 user-invocable: false
diff --git a/.claude/skills/research.component-libs/SKILL.md b/.claude/skills/research.component-libs/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: competitor-research
+name: research.component-libs
 description: Orchestrates a comprehensive research effort across multiple design systems/component libraries
 argument-hint: [research goal (e.g. "theming architecture", "progress bar component API", "styling solutions")]
 model: claude-sonnet-4-6
diff --git a/.claude/skills/research.deprecation-usage/SKILL.md b/.claude/skills/research.deprecation-usage/SKILL.md
@@ -0,0 +1,90 @@
+---
+name: research.deprecation-usage
+description: |
+  Audits how often deprecated CDS exports are actively used in customer codebases using Sourcegraph MCP search tools.
+  Use this skill whenever asked to assess removal readiness for deprecated CDS APIs, investigate the
+  blast radius of removing a deprecated component or hook, check Sourcegraph for customer usage of
+  deprecated exports, or help the team decide which deprecated APIs are safe to remove in the next
+  major version. Always invoke when asked to "audit deprecated APIs", "check Sourcegraph for deprecated
+  usage", "find usages of deprecated exports", "analyze deprecation impact", or any similar request
+  involving CDS deprecations and customer adoption.
+---
+
+## Objective
+
+Your objective is to provide information to user about the extent to which deprecated members of CDS are used in customer repositories. This information should be as accurate as possible as it will be used to inform decisions on whether or not it is safe to drop certain exports in a release or hold them for the next major version.
+
+Follow the
+
+## 1 - Determining Research Scope
+
+You may be asked to investigate a single, specific deprecation or all CDS deprecations in general.
+
+If you need to perform a comprehensive audit, there is one additional preparation step:
+
+```bash
+yarn node scripts/findDeprecations.mjs --json
+```
+
+This script extracts the deprecations with metadata from all CDS packages in JSON format.
+
+### 2 - Determining the Type of Deprecation
+
+There are two common categories of deprecations in CDS packages:
+
+1. A single prop of a React component
+2. A whole React component, function or constant
+
+If you are researching a single deprecation, find it in this monorepo's source code (DO NOT USE SOURCEGRAPH). It will be marked with the jsdoc `@deprecated` annotation. Inspect the code around the deprecation to determine which of the two categories it falls into. If the deprecation is found in multiple CDS packages you may ask the user to clarify which package is of interest to them.
+
+If you are performing a comprehensive audit for all CDS deprecations, the output of the script you ran in Step 1 will have already classified the deprecaations for you.
+
+## 3 - Using Sourcegraph
+
+For every deprecation you must research, perform a search on Sourcegraph to find evidence of usage.
+
+**IMPORTANT:** Only attempt to search for one deprecation at a time.
+
+**IMPORTANT:** Do not attempt to search if you do not have the information to
+
+You must perform a `keyword search` using the Sourcegraph MCP server. For the `query` parameter you must use the EXACT queries I share below, substituing in the name(s) of the deprecation you are investigating.
+
+### Components, Functions, Constants
+
+Replace `NAME_HERE` with the name of the deprecated component/function/constant
+
+```
+NOT repo:frontend/cds(-(internal|public|next))?$ file:..(t|j)sx?$ /import[^;'"]*?\bNAME_HERE\b[^;'"]*?from\s+['"][^'"]*(?:cds-web|cds-mobile)[^'"]*['"]/
+```
+
+### React prop
+
+Replace `NAME_HERE` with the name of the React component and `PROP_HERE` with the name of the deprecated prop.
+
+```
+NOT repo:frontend/cds(-(internal|public|next))?$ file:..(t|j)sx?$ /<\\s*NAME_HERE\\b[^>]*?\\s+PROP_HERE[\\s=\/>]/
+```
+
+## 4 - Structured Output
+
+Your output will depend on the number of deprecations you needed to audit:
+
+### Single Deprecation Output
+
+State the total number of usages found and output a markdown table with columns: Repo, Hits, Search Link — where each link uses a full Sourcegraph URL that will take the user directly to the relevant regex search for the deprecation, filtered by the repo represented in the row of the table.
+
+### How to build per-repo Sourcegraph search
+
+For the following sourcegraph search:
+
+```
+/<\\s*CellMedia\\b[^>]*\\stitle[\\s=\\/>]/ NOT repo:frontend/cds(-(internal|public|next))?$ file:\\.(t|j)sx?$
+```
+
+Here is an example for repo coinbase.ghe.com/payments/onramp-widget:
+
+`https://sourcegraph.cbhq.net/search?q=NOT+repo%3Afrontend%2Fcds%28-%28internal%7Cpublic%7Cnext%29%29%3F%24+file%3A..%28t%7Cj%29sx%3F%24+%3C%5Cs*CellMedia%5Cb%5B%5E%3E%5D*%3F%5Cs%2Btitle%5B%5Cs%3D%2F%3E%5D&patternType=regexp&sm=0&__cc=1&df=%5B%22repo%22%2C%22coinbase.ghe.com%2Fpayments%2Fonramp-widget%22%2C%22repo%3A%5Ecoinbase%5C%5C.ghe%5C%5C.com%2Fpayments%2Fonramp-widget%24%22%5D`
+
+### Multiple Deprecations Output
+
+When you have analyzed more than one deprecation, simply list out every deprecation and the total number of matches that came back from its sourcegraph query.
diff --git a/.claude/skills/summarize-commits/SKILL.md b/.claude/skills/summarize-commits/SKILL.md
@@ -1,10 +0,0 @@
----
-name: summarize-commits
-description: Reviews a git log to summarize the recent N changes
-allowed-tools: Bash(git log:*), Bash(git status:*), Bash(git show:*), Bash(echo:*)
-argument-hint: [Number of commits to review]
----
-
-## Your task
-
-Review the last $1 git commits and provide a summary of the changes. In addition to `git log`, use `git show` to obtain detailed information about the changesets before making any conclusions.
PATCH

echo "Gold patch applied."
