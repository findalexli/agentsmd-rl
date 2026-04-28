#!/usr/bin/env bash
set -euo pipefail

cd /workspace/handsontable

# Idempotency guard
if grep -qF "Behavioral guidelines to reduce common LLM coding mistakes. These complement - n" "AGENTS.md" && grep -qF "docs/AGENTS.md" "docs/AGENTS.md" && grep -qF "- **Control flow**: Use `@for`, `@if`, `@switch` (Angular 17+ built-in control f" "docs/AGENTS.md" && grep -qF "docs/CLAUDE.md" "docs/CLAUDE.md" && grep -qF "docs/CLAUDE.md" "docs/CLAUDE.md" && grep -qF "For server-backed grids (`dataProvider` with `fetchRows` and CRUD callbacks), en" "handsontable/AGENTS.md" && grep -qF "handsontable/CLAUDE.md" "handsontable/CLAUDE.md" && grep -qF "handsontable/CLAUDE.md" "handsontable/CLAUDE.md" && grep -qF "Self-contained rendering engine for viewport calculation, DOM rendering, scroll " "handsontable/src/3rdparty/walkontable/AGENTS.md" && grep -qF "handsontable/src/3rdparty/walkontable/CLAUDE.md" "handsontable/src/3rdparty/walkontable/CLAUDE.md" && grep -qF "handsontable/src/3rdparty/walkontable/CLAUDE.md" "handsontable/src/3rdparty/walkontable/CLAUDE.md" && grep -qF "- Custom `tablePage` fixture from `src/test-runner.ts` (auto-navigates to demo, " "visual-tests/AGENTS.md" && grep -qF "visual-tests/CLAUDE.md" "visual-tests/CLAUDE.md" && grep -qF "visual-tests/CLAUDE.md" "visual-tests/CLAUDE.md" && grep -qF "| Using `standalone: false` or `AppModule` | All Angular docs examples use `stan" "wrappers/angular-wrapper/AGENTS.md" && grep -qF "wrappers/angular-wrapper/CLAUDE.md" "wrappers/angular-wrapper/CLAUDE.md" && grep -qF "wrappers/angular-wrapper/CLAUDE.md" "wrappers/angular-wrapper/CLAUDE.md" && grep -qF "- **No business logic** in wrappers - data transformation, validation, cell mani" "wrappers/react-wrapper/AGENTS.md" && grep -qF "wrappers/react-wrapper/CLAUDE.md" "wrappers/react-wrapper/CLAUDE.md" && grep -qF "wrappers/react-wrapper/CLAUDE.md" "wrappers/react-wrapper/CLAUDE.md" && grep -qF "| `arr.push(...largeArray)` with large arrays | Causes stack overflow with 10k+ " "wrappers/vue3/AGENTS.md" && grep -qF "wrappers/vue3/CLAUDE.md" "wrappers/vue3/CLAUDE.md" && grep -qF "wrappers/vue3/CLAUDE.md" "wrappers/vue3/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -23,6 +23,38 @@ For task-specific workflow guidance, see `.claude/skills/` (Claude Code) or `.cu
 
 ---
 
+## Skill discovery - check before acting
+
+**Before starting any of the tasks below, invoke the matching skill.** Do not rely on memory - skills evolve. Invoking the wrong skill is better than skipping the check.
+
+| Task | Skill to invoke |
+|---|---|
+| Create or update a PR | `pr-creation` |
+| Build a demo / test page / repro | `handsontable-demo-page` |
+| Write or modify E2E tests (`*.spec.js`) | `handsontable-e2e-testing` |
+| Write or modify unit tests (`*.unit.js`) | `handsontable-unit-testing` |
+| Create or modify a plugin | `handsontable-plugin-dev` |
+| Create or modify an editor | `handsontable-editor-dev` |
+| Create or modify a renderer | `handsontable-renderer-dev` |
+| Create or modify a cell type | `handsontable-celltype-dev` |
+| Work on CSS, themes, or tokens | `handsontable-css-dev` |
+| Add or change user-visible text / i18n | `i18n-translations` |
+| Write a changelog entry | `changelog-creation` |
+| Work on React wrapper | `react-wrapper-dev` |
+| Work on Angular wrapper | `angular-wrapper-dev` |
+| Work on Vue 3 wrapper | `vue-wrapper-dev` |
+| Work on Walkontable engine | `walkontable-dev` |
+| Work on performance tests | `performance-testing` |
+| Add or fix linting violations | `linting` |
+| Row/column index translation | `coordinate-systems` |
+| Refactoring | `refactoring` |
+| Architecture review | `architecture-review` |
+| `.mjs` scripts or build utilities | `node-scripts-dev` |
+| Visual regression tests | `visual-testing` |
+| Documentation pages | `writing-docs-pages` |
+
+---
+
 ## Self-improvement rules
 
 When an AI agent discovers that information in this file, `.ai/`, skills, or CLAUDE.md files is **incorrect, outdated, or missing**, it must update the correct file immediately as part of the current task. Do not leave known inaccuracies for a future session.
@@ -34,43 +66,23 @@ When an AI agent discovers that information in this file, `.ai/`, skills, or CLA
 | Architecture or design change | `.ai/ARCHITECTURE.md` + relevant skill |
 | New tech debt or known issue | `.ai/CONCERNS.md` |
 | Testing infrastructure change | `.ai/TESTING.md` + relevant testing skill |
-| Package-specific rule | Subdirectory `CLAUDE.md` (e.g., `handsontable/CLAUDE.md`) |
+| Package-specific rule | Subdirectory `AGENTS.md` (e.g., `handsontable/AGENTS.md`) |
 
 After updating, run `node scripts/sync-skills-to-cursor.mjs` to keep Cursor rules in sync with Claude skills.
 
 **Single source of truth hierarchy:**
-1. `.claude/skills/` -- detailed workflow guides (synced to `.cursor/rules/`)
-2. `.ai/` -- deep reference material
-3. This file (AGENTS.md) -- concise overview and quick reference
-4. Subdirectory `CLAUDE.md` -- package-specific cheat sheets
+1. `.claude/skills/` - detailed workflow guides (synced to `.cursor/rules/`)
+2. `.ai/` - deep reference material
+3. This file (AGENTS.md) - concise overview and quick reference
+4. Subdirectory `AGENTS.md` - package-specific cheat sheets
 
 Never duplicate detailed content across multiple sources. Reference the authoritative source instead.
 
 ---
 
 ## Common pitfalls
 
-These are the most frequent mistakes. Read this section first.
-
-| Pitfall | What to do instead |
-|---|---|
-| `throw new Error('...')` | Use `throwWithCause('...', cause)` from `src/helpers/errors.js`. Enforced by ESLint. |
-| Using `window`, `document`, `console` as globals | Use `this.hot.rootWindow`, `this.hot.rootDocument`, and helpers from `src/helpers/console.js`. Enforced by ESLint. |
-| Importing from barrel index files (`plugins/index`, `editors/index`, `renderers/index`, `validators/index`, `cellTypes/index`, `i18n/index`) | Import from the specific submodule path (e.g., `import { HiddenColumns } from '../plugins/hiddenColumns/hiddenColumns'`). Only exception: `src/registry.js`. |
-| Writing `it('should ...', () => { ... })` in spec files | All `it()` callbacks in `*.spec.js` that call HOT rendering APIs **must** be `async` and the API calls must be `await`-ed. |
-| `arr.push(...largeArray)` with large arrays | Causes stack overflow with 10k+ elements. Use `forEach` loop instead. |
-| Confusing physical, visual, and renderable coordinates | See skill `coordinate-systems` or `.ai/ARCHITECTURE.md`. |
-| Creating `.ts` files in `handsontable/src/` | Core is JavaScript. TypeScript definitions live in `handsontable/types/` as `.d.ts` files. |
-| Forgetting `super.enablePlugin()` / `super.disablePlugin()` in plugins | See skill `handsontable-plugin-dev`. |
-| Hardcoding user-visible text in source code | Add language constants in `src/i18n/constants.js` and update all language files in `src/i18n/languages/`. |
-| Using `.bind(this)` for hook/event callbacks | Use arrow-function class fields (`#onAfterX = () => { ... }`) instead. |
-| Direct cross-plugin imports | Use hooks for inter-plugin communication or `hot.getPlugin('{Name}')` if API access is required. |
-| Confusing the context menu with the column (dropdown) menu | These are two separate plugins. See [Context menu vs column menu](#context-menu-vs-column-menu). |
-| Using `standalone: false` or `AppModule` in Angular examples | All Angular docs examples use `standalone: true` with `imports: [HotTableModule]` and `app.config.ts`. See skill `angular-wrapper-dev`. |
-| Adding `licenseKey` to individual `<hot-table>` in Angular examples | Set it globally via `HOT_GLOBAL_CONFIG` in `app.config.ts`. Never put it on each component. |
-| Using `*ngIf` / `*ngFor` in Angular templates | Use Angular 17+ built-in control flow: `@if (cond) { }` and `@for (x of list; track x.id) { }`. |
-| Typing Angular row data as `any[]` | Use `RowObject[]` imported from `handsontable/common`. |
-| Expecting built-in DataProvider error UI from `dialog: true` alone | Enable `notification: true` (or a `notification` config object). DataProvider uses the Notification plugin for fetch/CRUD failures. Dialog stays for blocking modals (for example Loading plugin, ExportFile binary export overlay, custom `show` content). |
+Cross-package pitfalls only. When adding a new entry: if it applies to one package only, add it to that package's CLAUDE.md instead (`handsontable/`, `wrappers/angular-wrapper/`, `wrappers/react-wrapper/`, `wrappers/vue3/`, `visual-tests/`, `docs/`).
 
 ---
 
@@ -100,24 +112,12 @@ These are the most frequent mistakes. Read this section first.
 All commands use `npm run` with `--prefix` to target the right package from the workspace root:
 
 - **Build core**: `npm run build --prefix handsontable` (must be done before wrapper tests)
-- **Lint core**: `npm run eslint --prefix handsontable` and `npm run stylelint --prefix handsontable`
-- **Unit tests (core)**: `npm run test:unit --prefix handsontable` (Jest, ~2200 tests)
-- **E2E tests (core)**: `npm run test:e2e --prefix handsontable` (Puppeteer/Jasmine, headless Chrome)
-- **Targeted unit test**: `npm run test:unit --testPathPattern=<regex> --prefix handsontable` (regex matched against file paths, e.g. `filters`, `ghostTable.unit`, `metaManager`)
-- **Targeted e2e test**: `npm run test:e2e --testPathPattern=<regex> --prefix handsontable` (e.g. `collapsibleColumns`, `textEditor`, `nestedHeaders/__tests__/hidingColumns`)
-- **E2E with theme**: `npm run test:e2e --testPathPattern=<regex> --theme=horizon --prefix handsontable` (themes: `classic`, `main`, `horizon`; default: `main`)
-- **Walkontable tests**: `npm run test:walkontable --prefix handsontable` (separate pipeline)
+- **Lint core**: `npm run lint --prefix handsontable`
+- **Unit tests (core)**: `npm run test:unit --prefix handsontable`
+- **E2E tests (core)**: `npm run test:e2e --prefix handsontable`
 - **Wrapper tests**: `npm run test --prefix wrappers/react-wrapper`, `npm run test --prefix wrappers/vue3`, `npm run test --prefix wrappers/angular-wrapper`
 
-### Build outputs
-
-| Output | Path |
-|---|---|
-| UMD / minified bundles | `handsontable/dist/` |
-| ES and CJS modules (used by wrappers) | `handsontable/tmp/` |
-| Compiled CSS | `handsontable/styles/` |
-
-Two build variants: `handsontable.js` (base, external deps) and `handsontable.full.js` (includes HyperFormula). The E2E runner loads `dist/handsontable.js` -- rebuild after changing `src/`.
+For targeted tests (`--testPathPattern`, `--theme`), Walkontable, and build outputs see `handsontable/AGENTS.md`.
 
 ---
 
@@ -148,8 +148,8 @@ Changes to JavaScript APIs that are **not listed in the public API reference** (
 
 Every code change **must** satisfy all of the following:
 
-1. **Use red-green TDD -- tests come first, always.** Write the failing test(s) before touching any production code. Confirm they fail, implement the fix/feature, then confirm they pass. **Never write or modify source code before the corresponding tests exist.**
-2. **Tests are required.** Include both **unit tests** (`*.unit.js`) and/or **E2E tests** (`*.spec.js`). Favor E2E tests -- if a unit test requires mocking a module, write an E2E test instead.
+1. **Use red-green TDD - tests come first, always.** Write the failing test(s) before touching any production code. Confirm they fail, implement the fix/feature, then confirm they pass. **Never write or modify source code before the corresponding tests exist.**
+2. **Tests are required.** Include both **unit tests** (`*.unit.js`) and/or **E2E tests** (`*.spec.js`). Favor E2E tests - if a unit test requires mocking a module, write an E2E test instead.
 3. **Documentation must be updated.** If a change affects public API, hooks, behavior, or UX, update JSDoc/Typedoc comments and guides.
 4. **Update AGENTS.md and skills.** If a change introduces new conventions, constraints, or gotchas, update this file and the relevant skill in `.claude/skills/`. Run `node scripts/sync-skills-to-cursor.mjs` to sync Cursor rules.
 
@@ -175,7 +175,7 @@ Every code change **must** satisfy all of the following:
 1. Short sentences. Active voice. American English spelling.
 2. Use "you" not "we". Oxford comma.
 3. No evaluative adjectives ("easy", "simple", "obvious").
-4. Use hyphens (`-`) or double hyphens (`--`) to separate clauses. Do not use typographic en dashes or em dashes. Use straight quotes (`"` and `'`) only -- no curly/smart quotes or smart apostrophes. Stick to standard ASCII characters.
+4. Use hyphens (`-`) to separate clauses. Do not use typographic en dashes or em dashes. Use straight quotes (`"` and `'`) only - no curly/smart quotes or smart apostrophes. Stick to standard ASCII characters.
 5. Consistent naming: `Node.js`, `Rspack`, `SWC`, `TypeScript`.
 
 ---
@@ -197,79 +197,39 @@ Every code change **must** satisfy all of the following:
 
 - Every PR must be connected to a GitHub issue.
 - Every PR that changes **library source code** (`handsontable/` or `wrappers/` packages) must include a changelog entry (`.changelogs/*.json`). See skill `changelog-creation`.
-- Use `[skip changelog]` in the **PR body** for all other changes -- docs (`docs/`), config, CI, scripts, AGENTS.md. "Source code" here means library packages, not the docs site or tooling. This line must appear in the PR body, not in the commit message.
+- Use `[skip changelog]` in the **PR body** for all other changes - docs (`docs/`), config, CI, scripts, AGENTS.md. "Source code" here means library packages, not the docs site or tooling. This line must appear in the PR body, not in the commit message.
 - PRs are merged using **"Squash and merge"**. Commit messages: descriptive, max 80 characters.
 - If a task spans multiple days, create a draft PR and commit daily.
 - See skill `pr-creation` for the full workflow.
 
 ---
 
-## Context menu vs column menu
-
-| | Context menu | Column menu (dropdown menu) |
-|---|---|---|
-| **Plugin class / key** | `ContextMenu` / `'contextMenu'` | `DropdownMenu` / `'dropdownMenu'` |
-| **Trigger** | Right-click (or `Ctrl+Shift+\` / `Shift+F10`) | Column header button (or `Shift+Alt+ArrowDown`) |
-| **Scope** | Cells and headers across rows and columns | Column-specific operations only |
-| **Hook prefix** | `beforeContextMenu*`, `afterContextMenu*` | `beforeDropdownMenu*`, `afterDropdownMenu*` |
-
-`DropdownMenu` is built on the shared `Menu` class from `contextMenu` but configured and triggered independently.
-
----
-
 ## Key file locations
 
 | Area | Path |
 |---|---|
-| Core class | `handsontable/src/core.js` |
-| Entry points | `handsontable/src/index.js` (full), `handsontable/src/base.js` (tree-shakeable) |
-| Plugin base class | `handsontable/src/plugins/base/base.js` |
-| Meta schema (defaults) | `handsontable/src/dataMap/metaManager/metaSchema.js` |
-| Index translations | `handsontable/src/translations/` |
-| Walkontable engine | `handsontable/src/3rdparty/walkontable/src/` |
-| Hooks system | `handsontable/src/core/hooks/` |
-| DataProvider plugin (server-backed data) | `handsontable/src/plugins/dataProvider/dataProvider.js` |
-| Error helpers | `handsontable/src/helpers/errors.js` |
-| i18n | `handsontable/src/i18n/constants.js`, `src/i18n/languages/` |
-| TypeScript definitions | `handsontable/types/` |
-| Browser targets | `browser-targets.js` (root) |
+| Browser targets | `browser-targets.js` |
 | ESLint config | `.eslintrc.js` (root), `handsontable/.eslintrc.js` |
 
+For handsontable core key file locations (core.js, plugins, hooks, i18n, types, etc.) see `handsontable/AGENTS.md`.
+
 ---
 
 ## Gotchas
 
 - **Cross-platform `npm` scripts**: All `scripts` entries in wrapper `package.json` files must work on Linux, macOS, and Windows. Use Node.js `.mjs` helpers, not bash constructs. See skill `node-scripts-dev`.
 - Wrappers consume `handsontable/tmp/` (not `dist/`). Build core before running wrapper tests.
-- Two builds: `handsontable.js` (base) and `handsontable.full.js` (includes HyperFormula). Test both.
-- Angular wrapper tests use `NODE_OPTIONS=--openssl-legacy-provider` (already in the `test` script).
-- The docs site (`docs/`) uses Node 20 and is not needed for core development.
-- **Docs guide pages** (`docs/content/guides/`): do not put an H1 in the Markdown body; `title` in frontmatter is the only page heading (Starlight shows it once). See skill `writing-docs-pages`.
-- Walkontable has its **own test runner** -- do not mix with main E2E tests.
-- **Merged cells -- read from meta, not DOM**: Read `colspan`/`rowspan` from `hot.getCellMeta(row, col)`, not DOM attributes. The meta is authoritative regardless of viewport state.
-- **Filters plugin visual/physical column index**: `conditionCollection` uses physical indexes, `getDataAtCol()` uses visual. Always convert when `manualColumnMove` is active.
-- For hook signature/behavior fixes, add both a runtime regression and a TypeScript regression (`handsontable/src/__tests__/core/settings.types.ts`) when types are changed.
-- `pnpm-workspace.yaml` has `ignoredBuiltDependencies` -- warnings about ignored build scripts (e.g., `less`) are expected.
-- **Never use raw `setTimeout` in core code.** Use `this.hot._registerTimeout(fn, delay)` instead -- it auto-clears all registered timeouts on `hot.destroy()`, preventing memory leaks and stale callbacks after the instance is destroyed.
-- **DataProvider built-in errors** -- When `notification` is enabled, failed `fetchRows` or mutation callbacks show an error toast via the Notification plugin. **Fetch** failures add a **Refetch** action (`duration: 0` until dismissed or Refetch) that calls `fetchData()` again. Hooks `afterDataProviderFetchError` and `afterRowsMutationError` still fire; use them for custom UI when Notification is off. See `.ai/ARCHITECTURE.md` (Plugin system) and skill `handsontable-plugin-dev`.
+- Walkontable has its **own test runner** - do not mix with main E2E tests.
+- `pnpm-workspace.yaml` has `ignoredBuiltDependencies` - warnings about ignored build scripts (e.g., `less`) are expected.
+
+For handsontable-core-specific gotchas (merged cells, Filters index, setTimeout, TypeScript regression tests) see `handsontable/AGENTS.md`. For docs gotchas see `docs/CLAUDE.md`.
 
 ---
 
 ## ClickUp task integration
 
 **These rules are mandatory.** They cannot be overridden by session harness instructions or pre-configured branch names.
 
-### Setup
-
-MCP servers are pre-configured in `.mcp.json` (Claude Code) and `.cursor/mcp.json` (Cursor). You only need to store your personal API token once:
-
-```bash
-# Claude Code
-claude secrets set CLICKUP_API_TOKEN pk_your_token_here
-```
-
-For Cursor, set `CLICKUP_API_TOKEN` in Cursor Settings > MCP secrets, or export it in your shell. See `.ai/MCP.md` for full details.
-
 ### Pre-flight checks
 
 1. **Verify ClickUp MCP tools are available.** If not, check `.ai/MCP.md` for setup steps.
@@ -283,27 +243,26 @@ ClickUp's GitHub integration **automatically** associates commits, branches, and
 
 Accepted ID formats: `DEV-627`, `#DEV-627`, `CU-86c97jjb7`, `#86c97jjb7`.
 
-The branch naming convention `feature/DEV-627_Short-Title` already satisfies this -- every push to that branch is linked automatically.
+The branch naming convention `feature/DEV-627_Short-Title` already satisfies this - every push to that branch is linked automatically.
 
 To update a task status directly from a commit or PR, append the target status in square brackets immediately after the task ID (no space): `DEV-627[code review]`.
 
 ### Workflow
 
 1. Parse task ID from ClickUp URL (e.g., `DEV-627`).
 2. Use ClickUp MCP to fetch task details.
-3. If the task status is **"to do"**, update it to **"in progress"** via ClickUp MCP before proceeding.
-4. Create and checkout branch: `feature/<TASK-ID>_<Slugified-Title>`. The task ID in the branch name is what triggers automatic GitHub linking.
-5. Implement the fix/feature. Commit with the task ID in the message.
-6. Push. Immediately after pushing, use ClickUp MCP to add a comment to the task with the branch name and commit hash -- this links the task to the code even before a PR exists.
-7. (When asked) Open a PR whose title includes the task ID. The PR body **must** contain the ClickUp task URL on its own line (e.g., `ClickUp task: https://app.clickup.com/t/9015210959/DEV-627`). This is what attaches the PR to the ClickUp task.
-8. Apply changelog policy: put `[skip changelog]` in the **PR body** if the change does not touch library source code (`handsontable/` or `wrappers/`).
-9. After PR is created, use ClickUp MCP to update task status to **"code review"**.
+3. Create and checkout branch: `feature/<TASK-ID>_<Slugified-Title>`. The task ID in the branch name is what triggers automatic GitHub linking.
+4. Implement the fix/feature. Commit with the task ID in the message.
+5. Push. Immediately after pushing, use ClickUp MCP to add a comment to the task with the branch name and commit hash - this links the task to the code even before a PR exists.
+6. (When asked) Open a PR whose title includes the task ID. The PR body **must** contain the ClickUp task URL on its own line (e.g., `ClickUp task: https://app.clickup.com/t/9015210959/DEV-627`). This is what attaches the PR to the ClickUp task.
+7. Apply changelog policy: put `[skip changelog]` in the **PR body** if the change does not touch library source code (`handsontable/` or `wrappers/`).
+8. After PR is created, use ClickUp MCP to update task status to **"code review"**.
 
 **Authentication**: Use the ClickUp MCP tools for all ClickUp API interactions. Do not call the ClickUp REST API directly.
 
 ## Coding discipline
 
-Behavioral guidelines to reduce common LLM coding mistakes. These complement -- not replace -- the [Mandatory checklist for every change](#mandatory-checklist-for-every-change) and [Architecture constraints](#architecture-constraints). They bias toward caution over speed; for small, low-risk tasks, use judgment.
+Behavioral guidelines to reduce common LLM coding mistakes. These complement - not replace - the [Mandatory checklist for every change](#mandatory-checklist-for-every-change) and [Architecture constraints](#architecture-constraints). They bias toward caution over speed; for small, low-risk tasks, use judgment.
 
 ### Think before coding
 
@@ -312,7 +271,7 @@ Do not assume. Do not hide confusion. Surface tradeoffs.
 Before implementing:
 
 - State your assumptions explicitly. If uncertain, ask.
-- If multiple interpretations exist, present them -- do not pick silently.
+- If multiple interpretations exist, present them - do not pick silently.
 - If a shorter approach exists, say so. Push back when warranted.
 - If something is unclear, stop. Name what is confusing. Ask.
 
@@ -337,7 +296,7 @@ When editing existing code:
 - Do not "improve" adjacent code, comments, or formatting.
 - Do not refactor things that are not broken.
 - Match existing style, even if you would do it differently.
-- If you notice unrelated dead code, mention it -- do not delete it.
+- If you notice unrelated dead code, mention it - do not delete it.
 
 When your changes create orphans:
 
@@ -391,13 +350,13 @@ A Tree-sitter knowledge graph (28k+ nodes, 419k+ edges) pre-built over the full
 |------|--------------|
 | Methods in one file | `children_of` standard = ~2,845 tokens; grep = ~473 tokens (6x cheaper) |
 | Recent change review | `detect_changes` requires the graph to be on the same branch |
-| Test coverage lookup | `tests_for` returns 0 incorrectly for files with known tests -- not reliable |
+| Test coverage lookup | `tests_for` returns 0 incorrectly for files with known tests - not reliable |
 | Natural-language search | No embeddings built; `semantic_search_nodes` falls back to keyword matching |
-| Architecture overview | `get_architecture_overview` returns 3.9M characters -- do not call it |
+| Architecture overview | `get_architecture_overview` returns 3.9M characters - do not call it |
 
 ### Mandatory rules
 
-1. **Always pass `detail_level: "minimal"`** -- standard mode repeats the full absolute path per node and inflates token cost 6x.
+1. **Always pass `detail_level: "minimal"`** - standard mode repeats the full absolute path per node and inflates token cost 6x.
 2. **Use fully qualified names**: `path/to/file.js::ClassName.methodName`. Bare names return an "ambiguous" error.
 3. **Rebuild on branch switch**: `pipx run code-review-graph==2.3.2 build`. A stale graph causes `detect_changes` to report function names from unrelated files.
 
diff --git a/docs/AGENTS.md b/docs/AGENTS.md
@@ -1 +0,0 @@
-CLAUDE.md
\ No newline at end of file
diff --git a/docs/AGENTS.md b/docs/AGENTS.md
@@ -0,0 +1,476 @@
+# Documentation Standards
+
+This document is written for both human authors and AI agents. All rules are stated explicitly so both roles can apply them without ambiguity.
+
+Astro Starlight-based documentation site. **Requires Node 20** (separate from core's Node 22).
+
+For detailed authoring guidance, use skills `writing-docs-pages` and `creating-docs-examples`.
+
+---
+
+## 2.1 Documentation Architecture (Diátaxis)
+
+Every page belongs to exactly one of four content types from the [Diátaxis framework](https://diataxis.fr/). Mixing types on a single page creates confusion. When content doesn't fit one type, split it into two pages.
+
+### The four content types
+
+| Type | Serves | User's question | Handsontable example |
+|---|---|---|---|
+| **Tutorial** | Learning | "Teach me to do X" | "Build a sortable data grid from scratch" |
+| **How-to guide** | Goals | "How do I accomplish X?" | "How to freeze the first two columns" |
+| **Reference** | Information | "What are the options for X?" | "Column filter configuration options" |
+| **Explanation** | Understanding | "Why does X work this way?" | "Understanding the plugin system" |
+
+### Decision tree
+
+Use this to pick the right type for a new page:
+
+1. Is the reader a beginner who needs guided instruction? → **Tutorial**
+2. Does the reader already know the basics and needs to accomplish a specific task? → **How-to guide**
+3. Is the reader looking up a specific fact, option, or API signature? → **Reference**
+4. Is the page answering "why?" or explaining a concept, design, or trade-off? → **Explanation**
+5. Does the content fit two or more types? → Split into separate pages.
+
+### Folder-to-type mapping
+
+| Folder | Expected type |
+|---|---|
+| `guides/getting-started/` | How-to (task-oriented setup steps) |
+| `guides/*/` (feature guides) | How-to or mixed (lean toward splitting) |
+| `guides/upgrade-and-migration/migrating-from-*/` | How-to |
+| `guides/upgrade-and-migration/changelog-*/` | Reference |
+| `guides/upgrade-and-migration/versioning-policy/` | Explanation |
+| `guides/upgrade-and-migration/deprecation-policy/` | Explanation |
+| `api/` | Reference |
+| `recipes/` | Tutorial |
+
+### Required frontmatter field
+
+Every page **must** declare its Diátaxis type in frontmatter:
+
+```yaml
+type: tutorial | how-to | reference | explanation
+```
+
+This field is in addition to the existing required frontmatter fields (see [Section 2.6](#26-frontmatter-schema)).
+
+---
+
+## 2.2 Voice and Style
+
+### Person, tense, and voice
+
+- **Second person**: "you", not "we" or "the user".
+- **Present tense**: "the plugin renders", not "the plugin will render".
+- **Active voice**: "Click **Save**", not "The Save button should be clicked".
+- **Direct imperative for instructions**: "Click **Save**" not "You should click **Save**".
+
+### Words to avoid
+
+| Avoid | Use instead |
+|---|---|
+| simply, just, easy, straightforward | (omit — state the fact directly) |
+| note that, please | (omit — restructure as a callout or sentence) |
+| allows you to | "lets you" or rephrase actively |
+| in order to | "to" |
+| utilize | "use" |
+
+### Sentence length
+
+- Instructions: max ~25 words per sentence.
+- One idea per sentence.
+- Separate compound sentences at conjunctions.
+
+### Technical terms
+
+- Define on first use in the page: "The `ColumnSorting` plugin -- which sorts rows by column values -- is disabled by default."
+- On subsequent uses, link to the reference page once per page section.
+- Use code formatting for all API names, option keys, file paths, and code values.
+
+### Formatting conventions
+
+- Hyphens (`-`) or double hyphens (`--`) to separate clauses. No en dashes or em dashes.
+- Straight quotes (`"` and `'`) only. No curly/smart quotes.
+- Bold for UI elements: **Save**, **Add column**.
+- Inline code for API names: `columnSorting`, `readOnly`.
+- Oxford comma in lists of three or more items.
+- American English spelling.
+
+---
+
+## 2.3 Page Structure Templates
+
+Use the appropriate template for each Diátaxis type. Do not omit required sections.
+
+### Tutorial template
+
+```markdown
+---
+type: tutorial
+id: <8-char alphanum>
+title: <Verb phrase — Build/Create/Set up X>
+metaTitle: <title> - JavaScript Data Grid | Handsontable
+description: <1-2 sentences summarizing outcome and who benefits>
+permalink: /<slug>
+tags: [keyword1, keyword2]
+searchCategory: Guides
+category: <nav category>
+---
+
+In this tutorial, you will [concrete outcome]. You will learn [skill or concept].
+
+## Before you begin
+
+- [prerequisite 1]
+- [prerequisite 2]
+
+## Step 1 — [Action phrase]
+
+[Instruction text. Keep to ~3-5 sentences. Show one code block.]
+
+## Step 2 — [Action phrase]
+
+...
+
+## What you learned
+
+- [learning point 1]
+- [learning point 2]
+
+## Next steps
+
+- [link to related how-to or reference]
+- [link to deeper topic]
+```
+
+### How-to guide template
+
+```markdown
+---
+type: how-to
+id: <8-char alphanum>
+title: How to [specific goal]
+metaTitle: How to [specific goal] - JavaScript Data Grid | Handsontable
+description: <1-2 sentences: what this achieves and when to use it>
+permalink: /<slug>
+tags: [keyword1, keyword2]
+searchCategory: Guides
+category: <nav category>
+---
+
+[One sentence: what this accomplishes and when to use it.]
+
+## Prerequisites
+
+- [prerequisite 1]
+
+## Steps
+
+1. [First action]
+
+   [Explanation and code block]
+
+2. [Second action]
+
+   [Explanation and code block]
+
+## Result
+
+[Describe what the reader now has. One or two sentences.]
+
+## Related
+
+- [link to related reference]
+- [link to related how-to]
+```
+
+### Reference template
+
+```markdown
+---
+type: reference
+id: <8-char alphanum>
+title: [Component/API/option name]
+metaTitle: [Component/API name] - JavaScript Data Grid | Handsontable
+description: <1-2 sentences describing what this is>
+permalink: /<slug>
+tags: [keyword1, keyword2]
+searchCategory: Guides
+category: <nav category>
+---
+
+[One sentence describing what this is and what it does.]
+
+## Syntax / Signature
+
+```javascript
+// function/option signature
+```
+
+## Parameters / Options
+
+| Name | Type | Default | Description |
+|---|---|---|---|
+| `name` | `string` | `'value'` | What this controls. |
+
+## Returns
+
+[Return type and description, if applicable.]
+
+## Examples
+
+[Minimal, runnable code example with language tag.]
+
+## Related
+
+- [link to how-to for this feature]
+- [link to related reference]
+```
+
+### Explanation template
+
+```markdown
+---
+type: explanation
+id: <8-char alphanum>
+title: Understanding [concept]
+metaTitle: Understanding [concept] - JavaScript Data Grid | Handsontable
+description: <1-2 sentences: why this concept matters and who should read this>
+permalink: /<slug>
+tags: [keyword1, keyword2]
+searchCategory: Guides
+category: <nav category>
+---
+
+[Why this concept matters and when it is relevant. 2-3 sentences.]
+
+## Background
+
+[Historical or architectural context.]
+
+## How it works
+
+[Mechanism, flow, or design explanation.]
+
+## Trade-offs
+
+[What you gain and what you give up. When to choose differently.]
+
+## Related
+
+- [link to how-to that applies this concept]
+- [link to reference for this feature]
+```
+
+---
+
+## 2.4 Example Data Standards
+
+### Never use
+
+The following placeholder values are banned from all published documentation:
+
+`A1`, `A2`, `A3`, `foo`, `bar`, `baz`, `test`, `Column1`, `Column2`, `Item1`, `value1`, `xxx`, `sample`, `dummy`, `placeholder`, `name1`, `name2`, `data1`, `data2`
+
+### Always use domain-realistic data
+
+Each example must use data from a coherent, plausible real-world domain. Pick one domain per example and stay consistent throughout.
+
+**Approved example domains:**
+
+| Domain | Example data |
+|---|---|
+| **Financial** | Company names (Acme Corp, Vertex Industries), revenue ($4.2M, $18.7M), fiscal quarters (Q1 2025), currencies (USD, EUR) |
+| **HR / workforce** | Employee names (diverse: Ana García, James Okafor, Li Wei), job titles (Senior Engineer, Product Manager), departments (Engineering, Marketing), hire dates (2022-03-14) |
+| **Inventory** | Product SKUs (SKU-4821, SKU-0093), supplier names (Harbor Goods, Alpine Supply Co.), stock quantities (142, 0, 67), categories (Electronics, Apparel) |
+| **Analytics** | Campaign names (Spring Sale 2025, Brand Awareness Q3), conversion rates (3.4%, 8.1%), channels (Email, Paid Search, Organic) |
+| **Project management** | Task names (Update API docs, Deploy hotfix), assignees, due dates (2025-06-30), statuses (In progress, Blocked) |
+
+### Data coherence rules
+
+- All rows in an example use the same domain.
+- Values must be plausible: no negative ages, no revenue of $1, no dates in 1900.
+- The dataset should make the demonstrated feature meaningful. A sorting example must use data where sorting is useful. A filtering example must use data where filtering makes sense.
+- Use at least five rows in table examples so the feature behavior is visible.
+
+---
+
+## 2.5 Code Example Standards
+
+### Language tags
+
+All code blocks **must** include a language tag:
+
+````markdown
+```javascript
+```typescript
+```html
+```css
+```shell
+```json
+```yaml
+````
+
+Untagged code blocks (```` ``` ````) are not allowed.
+
+### Example quality rules
+
+- Examples must be self-contained and runnable (or clearly labeled as a snippet).
+- Use `const` and `let`. Never use `var`.
+- Always include `licenseKey: 'non-commercial-and-evaluation'` in `new Handsontable(...)` calls.
+- No inline `// TODO` or `// ...` comments in published examples.
+- Keep examples between 25 and 60 lines. If longer, link to the live sandbox instead.
+- TypeScript is the primary language for new examples. Generate the JavaScript variant: `npm run docs:code-examples:generate-js <path>`.
+
+### Example embedding
+
+```markdown
+::: example #example1 --js 1 --ts 2
+@[code](@/content/guides/category/feature/javascript/example1.js)
+@[code](@/content/guides/category/feature/javascript/example1.ts)
+:::
+```
+
+### Framework-specific content
+
+```markdown
+::: only-for javascript
+Content for vanilla JS only.
+:::
+
+::: only-for react
+Content for React only.
+:::
+```
+
+### Angular component rules (standalone pattern)
+
+All Angular docs examples use `standalone: true` bootstrapped via `bootstrapApplication`. The Angular JIT compiler runs in the browser and **cannot resolve file-based resources at runtime**. Violating these rules causes the component to silently fail to render.
+
+**Never do this:**
+```typescript
+@Component({
+  standalone: true,
+  styleUrls: ['./example1.css'],  // ❌ JIT cannot fetch files at runtime
+  templateUrl: './example1.html', // ❌ JIT cannot fetch files at runtime
+})
+```
+
+**Always do this instead:**
+
+- **CSS**: Put styles in the `--css` slot of the example directive (the example-runner injects them as a global `<style>` tag). Do **not** reference them in `styleUrls`. If the CSS must live in the component, use inline `styles: ['...']` with `ViewEncapsulation.None`.
+- **Template**: Always use an inline `template: \`...\`` in the `@Component` decorator. The `angular/example1.html` file is the **outer wrapper** (contains the selector tag) loaded by the example-runner, not the component's internal template.
+- **Constructor DI**: Never inject services via the constructor. Use the `inject()` function instead -- constructors are not processed by Angular JIT without TypeScript decorator metadata.
+- **Lifecycle hooks**: Put `afterInit`, `afterChange`, and other Handsontable hook functions inside `gridSettings`, not as template event bindings (e.g., `(afterInit)="..."` fails in JIT mode).
+- **`@ViewChild`**: Safe to use. It is populated after the component view is initialized.
+- **Control flow**: Use `@for`, `@if`, `@switch` (Angular 17+ built-in control flow). Do **not** use `*ngFor`, `*ngIf`, or `*ngSwitch` with structural directives — they require importing `NgFor`, `NgIf`, etc. from `@angular/common`, which is error-prone. The built-in control flow syntax requires no imports.
+- **Imports**: Only import symbols you actually use. Unused imports (e.g., `RowObject`, `ViewChild`, `NgFor`) can cause module resolution errors.
+
+Correct standalone component skeleton:
+```typescript
+@Component({
+  standalone: true,
+  imports: [HotTableModule],
+  selector: 'example1-feature-name',
+  template: `
+    <div>
+      <hot-table [data]="data" [settings]="gridSettings"></hot-table>
+    </div>
+  `,
+  // No styleUrls, no templateUrl
+})
+export class AppComponent {
+  readonly data = [...];
+  readonly gridSettings: GridSettings = { ... };
+}
+```
+
+---
+
+## 2.6 Frontmatter Schema
+
+Required fields for all pages:
+
+```yaml
+---
+type: tutorial | how-to | reference | explanation   # Diátaxis type (required)
+id: abc12345              # 8 random alphanumeric chars — NEVER change existing IDs
+title: Feature Name       # Matches H1; do NOT add H1 in body (Starlight renders title once)
+metaTitle: Feature Name - JavaScript Data Grid | Handsontable
+description: Short SEO description (1-2 sentences)
+permalink: /feature-name
+tags: [keyword1, keyword2]  # Optional; kebab-case
+react:
+  id: def67890            # Different ID per framework variant
+  metaTitle: Feature Name - React Data Grid | Handsontable
+searchCategory: Guides
+category: Cell features
+---
+```
+
+**Rules:**
+- Never change an existing `id` value. IDs are permanent.
+- `title` is the only H1. Do not add `# Title` in the Markdown body.
+- `description` is used in SEO meta and link previews -- make it specific and accurate.
+- `tags` must be lowercase kebab-case.
+
+---
+
+## 2.7 Links and Paths
+
+Use the `@` prefix with `.md` extension for all internal links:
+
+```markdown
+[text](@/path/to/file.md#anchor)
+```
+
+Do not use relative paths (`../`) for internal links.
+
+---
+
+## 2.8 Trademark Notices
+
+- Pages mentioning "Excel" must include the Microsoft trademark disclaimer.
+- Pages also mentioning "Google Sheets" use the expanded disclaimer.
+- Add the disclaimer in a callout or footnote at the bottom of the page.
+
+---
+
+## 2.9 Sidebar Registration
+
+Register new pages in `content/guides/sidebar.js`. A page not registered there will not appear in navigation.
+
+---
+
+## 2.10 Checklist Before Submitting a Docs PR
+
+Copy and complete this checklist in your PR description:
+
+```markdown
+## Docs PR checklist
+
+- [ ] `type:` field added to frontmatter (tutorial | how-to | reference | explanation)
+- [ ] Page uses the correct Diátaxis template for its type
+- [ ] Title matches Diátaxis naming convention for its type
+  - Tutorial: verb phrase ("Build X", "Create X")
+  - How-to: starts with "How to ..."
+  - Reference: component or API name
+  - Explanation: starts with "Understanding ..."
+- [ ] Intro paragraph states: what, for whom, and what outcome the reader gains
+- [ ] No banned placeholder data (foo, bar, A1, Column1, etc.)
+- [ ] All example data is domain-realistic and internally consistent
+- [ ] All code blocks have language tags (```javascript, ```typescript, etc.)
+- [ ] No `var` in code examples; uses `const` / `let`
+- [ ] All examples include `licenseKey: 'non-commercial-and-evaluation'`
+- [ ] Heading hierarchy is correct (no skipped levels, e.g., H2 → H4)
+- [ ] Active voice and second person ("you") used throughout
+- [ ] No banned words: simply, just, easy, straightforward, note that, please
+- [ ] Tutorials and how-tos have a Prerequisites section
+- [ ] Tutorials have "What you learned" and "Next steps" sections
+- [ ] How-tos have a "Result" section
+- [ ] New page registered in `content/guides/sidebar.js`
+- [ ] `id` field uses 8 random alphanumeric chars (existing IDs are unchanged)
+- [ ] Microsoft trademark disclaimer added where "Excel" is mentioned
+- [ ] TypeScript example exists; JS generated via `npm run docs:code-examples:generate-js`
+- [ ] `[skip changelog]` in PR body (docs changes don't need changelog entries)
+```
diff --git a/docs/CLAUDE.md b/docs/CLAUDE.md
@@ -1,476 +0,0 @@
-# Documentation Standards
-
-This document is written for both human authors and AI agents. All rules are stated explicitly so both roles can apply them without ambiguity.
-
-Astro Starlight-based documentation site. **Requires Node 20** (separate from core's Node 22).
-
-For detailed authoring guidance, use skills `writing-docs-pages` and `creating-docs-examples`.
-
----
-
-## 2.1 Documentation Architecture (Diátaxis)
-
-Every page belongs to exactly one of four content types from the [Diátaxis framework](https://diataxis.fr/). Mixing types on a single page creates confusion. When content doesn't fit one type, split it into two pages.
-
-### The four content types
-
-| Type | Serves | User's question | Handsontable example |
-|---|---|---|---|
-| **Tutorial** | Learning | "Teach me to do X" | "Build a sortable data grid from scratch" |
-| **How-to guide** | Goals | "How do I accomplish X?" | "How to freeze the first two columns" |
-| **Reference** | Information | "What are the options for X?" | "Column filter configuration options" |
-| **Explanation** | Understanding | "Why does X work this way?" | "Understanding the plugin system" |
-
-### Decision tree
-
-Use this to pick the right type for a new page:
-
-1. Is the reader a beginner who needs guided instruction? → **Tutorial**
-2. Does the reader already know the basics and needs to accomplish a specific task? → **How-to guide**
-3. Is the reader looking up a specific fact, option, or API signature? → **Reference**
-4. Is the page answering "why?" or explaining a concept, design, or trade-off? → **Explanation**
-5. Does the content fit two or more types? → Split into separate pages.
-
-### Folder-to-type mapping
-
-| Folder | Expected type |
-|---|---|
-| `guides/getting-started/` | How-to (task-oriented setup steps) |
-| `guides/*/` (feature guides) | How-to or mixed (lean toward splitting) |
-| `guides/upgrade-and-migration/migrating-from-*/` | How-to |
-| `guides/upgrade-and-migration/changelog-*/` | Reference |
-| `guides/upgrade-and-migration/versioning-policy/` | Explanation |
-| `guides/upgrade-and-migration/deprecation-policy/` | Explanation |
-| `api/` | Reference |
-| `recipes/` | Tutorial |
-
-### Required frontmatter field
-
-Every page **must** declare its Diátaxis type in frontmatter:
-
-```yaml
-type: tutorial | how-to | reference | explanation
-```
-
-This field is in addition to the existing required frontmatter fields (see [Section 2.6](#26-frontmatter-schema)).
-
----
-
-## 2.2 Voice and Style
-
-### Person, tense, and voice
-
-- **Second person**: "you", not "we" or "the user".
-- **Present tense**: "the plugin renders", not "the plugin will render".
-- **Active voice**: "Click **Save**", not "The Save button should be clicked".
-- **Direct imperative for instructions**: "Click **Save**" not "You should click **Save**".
-
-### Words to avoid
-
-| Avoid | Use instead |
-|---|---|
-| simply, just, easy, straightforward | (omit — state the fact directly) |
-| note that, please | (omit — restructure as a callout or sentence) |
-| allows you to | "lets you" or rephrase actively |
-| in order to | "to" |
-| utilize | "use" |
-
-### Sentence length
-
-- Instructions: max ~25 words per sentence.
-- One idea per sentence.
-- Separate compound sentences at conjunctions.
-
-### Technical terms
-
-- Define on first use in the page: "The `ColumnSorting` plugin -- which sorts rows by column values -- is disabled by default."
-- On subsequent uses, link to the reference page once per page section.
-- Use code formatting for all API names, option keys, file paths, and code values.
-
-### Formatting conventions
-
-- Hyphens (`-`) or double hyphens (`--`) to separate clauses. No en dashes or em dashes.
-- Straight quotes (`"` and `'`) only. No curly/smart quotes.
-- Bold for UI elements: **Save**, **Add column**.
-- Inline code for API names: `columnSorting`, `readOnly`.
-- Oxford comma in lists of three or more items.
-- American English spelling.
-
----
-
-## 2.3 Page Structure Templates
-
-Use the appropriate template for each Diátaxis type. Do not omit required sections.
-
-### Tutorial template
-
-```markdown
----
-type: tutorial
-id: <8-char alphanum>
-title: <Verb phrase — Build/Create/Set up X>
-metaTitle: <title> - JavaScript Data Grid | Handsontable
-description: <1-2 sentences summarizing outcome and who benefits>
-permalink: /<slug>
-tags: [keyword1, keyword2]
-searchCategory: Guides
-category: <nav category>
----
-
-In this tutorial, you will [concrete outcome]. You will learn [skill or concept].
-
-## Before you begin
-
-- [prerequisite 1]
-- [prerequisite 2]
-
-## Step 1 — [Action phrase]
-
-[Instruction text. Keep to ~3-5 sentences. Show one code block.]
-
-## Step 2 — [Action phrase]
-
-...
-
-## What you learned
-
-- [learning point 1]
-- [learning point 2]
-
-## Next steps
-
-- [link to related how-to or reference]
-- [link to deeper topic]
-```
-
-### How-to guide template
-
-```markdown
----
-type: how-to
-id: <8-char alphanum>
-title: How to [specific goal]
-metaTitle: How to [specific goal] - JavaScript Data Grid | Handsontable
-description: <1-2 sentences: what this achieves and when to use it>
-permalink: /<slug>
-tags: [keyword1, keyword2]
-searchCategory: Guides
-category: <nav category>
----
-
-[One sentence: what this accomplishes and when to use it.]
-
-## Prerequisites
-
-- [prerequisite 1]
-
-## Steps
-
-1. [First action]
-
-   [Explanation and code block]
-
-2. [Second action]
-
-   [Explanation and code block]
-
-## Result
-
-[Describe what the reader now has. One or two sentences.]
-
-## Related
-
-- [link to related reference]
-- [link to related how-to]
-```
-
-### Reference template
-
-```markdown
----
-type: reference
-id: <8-char alphanum>
-title: [Component/API/option name]
-metaTitle: [Component/API name] - JavaScript Data Grid | Handsontable
-description: <1-2 sentences describing what this is>
-permalink: /<slug>
-tags: [keyword1, keyword2]
-searchCategory: Guides
-category: <nav category>
----
-
-[One sentence describing what this is and what it does.]
-
-## Syntax / Signature
-
-```javascript
-// function/option signature
-```
-
-## Parameters / Options
-
-| Name | Type | Default | Description |
-|---|---|---|---|
-| `name` | `string` | `'value'` | What this controls. |
-
-## Returns
-
-[Return type and description, if applicable.]
-
-## Examples
-
-[Minimal, runnable code example with language tag.]
-
-## Related
-
-- [link to how-to for this feature]
-- [link to related reference]
-```
-
-### Explanation template
-
-```markdown
----
-type: explanation
-id: <8-char alphanum>
-title: Understanding [concept]
-metaTitle: Understanding [concept] - JavaScript Data Grid | Handsontable
-description: <1-2 sentences: why this concept matters and who should read this>
-permalink: /<slug>
-tags: [keyword1, keyword2]
-searchCategory: Guides
-category: <nav category>
----
-
-[Why this concept matters and when it is relevant. 2-3 sentences.]
-
-## Background
-
-[Historical or architectural context.]
-
-## How it works
-
-[Mechanism, flow, or design explanation.]
-
-## Trade-offs
-
-[What you gain and what you give up. When to choose differently.]
-
-## Related
-
-- [link to how-to that applies this concept]
-- [link to reference for this feature]
-```
-
----
-
-## 2.4 Example Data Standards
-
-### Never use
-
-The following placeholder values are banned from all published documentation:
-
-`A1`, `A2`, `A3`, `foo`, `bar`, `baz`, `test`, `Column1`, `Column2`, `Item1`, `value1`, `xxx`, `sample`, `dummy`, `placeholder`, `name1`, `name2`, `data1`, `data2`
-
-### Always use domain-realistic data
-
-Each example must use data from a coherent, plausible real-world domain. Pick one domain per example and stay consistent throughout.
-
-**Approved example domains:**
-
-| Domain | Example data |
-|---|---|
-| **Financial** | Company names (Acme Corp, Vertex Industries), revenue ($4.2M, $18.7M), fiscal quarters (Q1 2025), currencies (USD, EUR) |
-| **HR / workforce** | Employee names (diverse: Ana García, James Okafor, Li Wei), job titles (Senior Engineer, Product Manager), departments (Engineering, Marketing), hire dates (2022-03-14) |
-| **Inventory** | Product SKUs (SKU-4821, SKU-0093), supplier names (Harbor Goods, Alpine Supply Co.), stock quantities (142, 0, 67), categories (Electronics, Apparel) |
-| **Analytics** | Campaign names (Spring Sale 2025, Brand Awareness Q3), conversion rates (3.4%, 8.1%), channels (Email, Paid Search, Organic) |
-| **Project management** | Task names (Update API docs, Deploy hotfix), assignees, due dates (2025-06-30), statuses (In progress, Blocked) |
-
-### Data coherence rules
-
-- All rows in an example use the same domain.
-- Values must be plausible: no negative ages, no revenue of $1, no dates in 1900.
-- The dataset should make the demonstrated feature meaningful. A sorting example must use data where sorting is useful. A filtering example must use data where filtering makes sense.
-- Use at least five rows in table examples so the feature behavior is visible.
-
----
-
-## 2.5 Code Example Standards
-
-### Language tags
-
-All code blocks **must** include a language tag:
-
-````markdown
-```javascript
-```typescript
-```html
-```css
-```shell
-```json
-```yaml
-````
-
-Untagged code blocks (```` ``` ````) are not allowed.
-
-### Example quality rules
-
-- Examples must be self-contained and runnable (or clearly labeled as a snippet).
-- Use `const` and `let`. Never use `var`.
-- Always include `licenseKey: 'non-commercial-and-evaluation'` in `new Handsontable(...)` calls.
-- No inline `// TODO` or `// ...` comments in published examples.
-- Keep examples between 25 and 60 lines. If longer, link to the live sandbox instead.
-- TypeScript is the primary language for new examples. Generate the JavaScript variant: `npm run docs:code-examples:generate-js <path>`.
-
-### Example embedding
-
-```markdown
-::: example #example1 --js 1 --ts 2
-@[code](@/content/guides/category/feature/javascript/example1.js)
-@[code](@/content/guides/category/feature/javascript/example1.ts)
-:::
-```
-
-### Framework-specific content
-
-```markdown
-::: only-for javascript
-Content for vanilla JS only.
-:::
-
-::: only-for react
-Content for React only.
-:::
-```
-
-### Angular component rules (standalone pattern)
-
-All Angular docs examples use `standalone: true` bootstrapped via `bootstrapApplication`. The Angular JIT compiler runs in the browser and **cannot resolve file-based resources at runtime**. Violating these rules causes the component to silently fail to render.
-
-**Never do this:**
-```typescript
-@Component({
-  standalone: true,
-  styleUrls: ['./example1.css'],  // ❌ JIT cannot fetch files at runtime
-  templateUrl: './example1.html', // ❌ JIT cannot fetch files at runtime
-})
-```
-
-**Always do this instead:**
-
-- **CSS**: Put styles in the `--css` slot of the example directive (the example-runner injects them as a global `<style>` tag). Do **not** reference them in `styleUrls`. If the CSS must live in the component, use inline `styles: ['...']` with `ViewEncapsulation.None`.
-- **Template**: Always use an inline `template: \`...\`` in the `@Component` decorator. The `angular/example1.html` file is the **outer wrapper** (contains the selector tag) loaded by the example-runner, not the component's internal template.
-- **Constructor DI**: Never inject services via the constructor. Use the `inject()` function instead -- constructors are not processed by Angular JIT without TypeScript decorator metadata.
-- **Lifecycle hooks**: Put `afterInit`, `afterChange`, and other Handsontable hook functions inside `gridSettings`, not as template event bindings (e.g., `(afterInit)="..."` fails in JIT mode).
-- **`@ViewChild`**: Safe to use. It is populated after the component view is initialized.
-- **Control flow**: Use `@for`, `@if`, `@switch` (Angular 17+ built-in control flow). Do **not** use `*ngFor`, `*ngIf`, or `*ngSwitch` with structural directives — they require importing `NgFor`, `NgIf`, etc. from `@angular/common`, which is error-prone. The built-in control flow syntax requires no imports.
-- **Imports**: Only import symbols you actually use. Unused imports (e.g., `RowObject`, `ViewChild`, `NgFor`) can cause module resolution errors.
-
-Correct standalone component skeleton:
-```typescript
-@Component({
-  standalone: true,
-  imports: [HotTableModule],
-  selector: 'example1-feature-name',
-  template: `
-    <div>
-      <hot-table [data]="data" [settings]="gridSettings"></hot-table>
-    </div>
-  `,
-  // No styleUrls, no templateUrl
-})
-export class AppComponent {
-  readonly data = [...];
-  readonly gridSettings: GridSettings = { ... };
-}
-```
-
----
-
-## 2.6 Frontmatter Schema
-
-Required fields for all pages:
-
-```yaml
----
-type: tutorial | how-to | reference | explanation   # Diátaxis type (required)
-id: abc12345              # 8 random alphanumeric chars — NEVER change existing IDs
-title: Feature Name       # Matches H1; do NOT add H1 in body (Starlight renders title once)
-metaTitle: Feature Name - JavaScript Data Grid | Handsontable
-description: Short SEO description (1-2 sentences)
-permalink: /feature-name
-tags: [keyword1, keyword2]  # Optional; kebab-case
-react:
-  id: def67890            # Different ID per framework variant
-  metaTitle: Feature Name - React Data Grid | Handsontable
-searchCategory: Guides
-category: Cell features
----
-```
-
-**Rules:**
-- Never change an existing `id` value. IDs are permanent.
-- `title` is the only H1. Do not add `# Title` in the Markdown body.
-- `description` is used in SEO meta and link previews -- make it specific and accurate.
-- `tags` must be lowercase kebab-case.
-
----
-
-## 2.7 Links and Paths
-
-Use the `@` prefix with `.md` extension for all internal links:
-
-```markdown
-[text](@/path/to/file.md#anchor)
-```
-
-Do not use relative paths (`../`) for internal links.
-
----
-
-## 2.8 Trademark Notices
-
-- Pages mentioning "Excel" must include the Microsoft trademark disclaimer.
-- Pages also mentioning "Google Sheets" use the expanded disclaimer.
-- Add the disclaimer in a callout or footnote at the bottom of the page.
-
----
-
-## 2.9 Sidebar Registration
-
-Register new pages in `content/guides/sidebar.js`. A page not registered there will not appear in navigation.
-
----
-
-## 2.10 Checklist Before Submitting a Docs PR
-
-Copy and complete this checklist in your PR description:
-
-```markdown
-## Docs PR checklist
-
-- [ ] `type:` field added to frontmatter (tutorial | how-to | reference | explanation)
-- [ ] Page uses the correct Diátaxis template for its type
-- [ ] Title matches Diátaxis naming convention for its type
-  - Tutorial: verb phrase ("Build X", "Create X")
-  - How-to: starts with "How to ..."
-  - Reference: component or API name
-  - Explanation: starts with "Understanding ..."
-- [ ] Intro paragraph states: what, for whom, and what outcome the reader gains
-- [ ] No banned placeholder data (foo, bar, A1, Column1, etc.)
-- [ ] All example data is domain-realistic and internally consistent
-- [ ] All code blocks have language tags (```javascript, ```typescript, etc.)
-- [ ] No `var` in code examples; uses `const` / `let`
-- [ ] All examples include `licenseKey: 'non-commercial-and-evaluation'`
-- [ ] Heading hierarchy is correct (no skipped levels, e.g., H2 → H4)
-- [ ] Active voice and second person ("you") used throughout
-- [ ] No banned words: simply, just, easy, straightforward, note that, please
-- [ ] Tutorials and how-tos have a Prerequisites section
-- [ ] Tutorials have "What you learned" and "Next steps" sections
-- [ ] How-tos have a "Result" section
-- [ ] New page registered in `content/guides/sidebar.js`
-- [ ] `id` field uses 8 random alphanumeric chars (existing IDs are unchanged)
-- [ ] Microsoft trademark disclaimer added where "Excel" is mentioned
-- [ ] TypeScript example exists; JS generated via `npm run docs:code-examples:generate-js`
-- [ ] `[skip changelog]` in PR body (docs changes don't need changelog entries)
-```
diff --git a/docs/CLAUDE.md b/docs/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
diff --git a/handsontable/AGENTS.md b/handsontable/AGENTS.md
@@ -0,0 +1,122 @@
+# Handsontable Core Package
+
+This is the core data grid package. **JavaScript only** - no TypeScript files in `src/`. Type definitions are hand-authored `.d.ts` files in `types/`.
+
+## Critical Rules
+
+- Use `throwWithCause()` from `src/helpers/errors.js`, never `throw new Error()`
+- No barrel imports from `plugins/index`, `editors/index`, `renderers/index`, `validators/index`, `cellTypes/index`, `i18n/index` - import from specific submodule paths. Only exception: `src/registry.js`
+- No global `window`, `document`, `console` - use `this.hot.rootWindow`, `this.hot.rootDocument`, and helpers from `src/helpers/console.js`
+- Private fields use `#` prefix, not `@private` JSDoc
+- Arrow function class fields for callbacks: `#onAfterX = () => { ... }` (not `.bind(this)`)
+- Cognitive complexity: keep each function at 15 or below
+- Optional chaining `?.` only when value is genuinely optional by design
+- No hardcoded user-visible strings in source - add constants to `src/i18n/constants.js` and update all language files in `src/i18n/languages/`
+- No direct cross-plugin imports - use hooks for inter-plugin communication, or `hot.getPlugin('Name')` if API access is required
+- Never use raw `setTimeout` - use `this.hot._registerTimeout(fn, delay)` instead; it auto-clears on `hot.destroy()`, preventing memory leaks
+
+## Plugin Lifecycle
+
+```
+isEnabled()      → return !!this.hot.getSettings()[PLUGIN_KEY]
+enablePlugin()   → init state, create IndexMaps, register hooks. super.enablePlugin() AT END.
+updatePlugin()   → this.disablePlugin(); this.enablePlugin(); super.updatePlugin();
+disablePlugin()  → super.disablePlugin() FIRST. Then clean up.
+destroy()        → null out fields. super.destroy() AT END.
+```
+
+Gold standard: `src/plugins/pagination/pagination.js`
+
+## Three Coordinate Systems
+
+| Type | Description | Use for |
+|------|-------------|---------|
+| Physical | Position in source data array | Data access, persistence |
+| Visual | Position after trimming (DataMap) | User-facing display logic |
+| Renderable | Position after hiding (DOM) | DOM operations |
+
+Translate with `hot.rowIndexMapper` / `hot.columnIndexMapper`.
+Gotcha: Filters `conditionCollection` uses physical indexes, `getDataAtCol()` uses visual.
+
+## DataProvider and Notification
+
+For server-backed grids (`dataProvider` with `fetchRows` and CRUD callbacks), enable **`notification`** if you want built-in error toasts on failed fetches or mutations. **`dialog: true` alone does not** show those errors. Failed **fetch** toasts include a **Refetch** button that calls `fetchData()` again (`duration: 0` until dismissed or Refetch). Use **`afterDataProviderFetchError`** and **`afterRowsMutationError`** for custom UI when Notification is disabled. See `src/plugins/dataProvider/dataProvider.js` and AGENTS.md Gotchas.
+
+## Testing
+
+| Type | Pattern | Framework | Run |
+|------|---------|-----------|-----|
+| Unit | `*.unit.js` | Jest (jsdom) | `npm run test:unit` |
+| E2E | `*.spec.js` | Jasmine (Puppeteer) | `npm run test:e2e` |
+
+- ALL `it()` callbacks in spec files MUST be `async`
+- HOT API calls MUST be `await`-ed
+- E2E helpers are globals (no imports): `handsontable()`, `selectCell()`, `getDataAtCell()`, `createSpreadsheetData()`
+- Targeted unit: `npm run test:unit --testPathPattern=<regex>` (regex matched against file paths, e.g. `filters`, `ghostTable.unit`)
+- Targeted e2e: `npm run test:e2e --testPathPattern=<regex>` (e.g. `collapsibleColumns`, `textEditor`, `nestedHeaders/__tests__/hidingColumns`)
+- E2E with theme: `npm run test:e2e --testPathPattern=<regex> --theme=horizon` (themes: `classic`, `main`, `horizon`; default: `main`)
+- **Rebuild before E2E:** E2E runner loads `dist/handsontable.js` - rebuild after changing `src/`
+
+## Common Pitfalls
+
+- **`arr.push(...largeArray)`**: Causes stack overflow with 10k+ elements. Use `forEach` loop instead.
+- **Merged cells**: Read `colspan`/`rowspan` from `hot.getCellMeta(row, col)`, NOT from DOM element attributes. The meta is authoritative regardless of viewport state.
+- **Filters visual/physical index**: `conditionCollection` uses physical indexes, `getDataAtCol()` uses visual. Always convert when `manualColumnMove` is active.
+- **Hook signature / TypeScript fixes**: When changing hook signatures, add both a runtime regression test and a TypeScript regression (`src/__tests__/core/settings.types.ts`).
+- **Two builds to test**: `handsontable.js` (base, no HyperFormula) and `handsontable.full.js` (includes HyperFormula). Test both when changing build-time behavior.
+
+## Key File Locations
+
+| Area | Path (relative to `handsontable/`) |
+|---|---|
+| Core class | `src/core.js` |
+| Entry points | `src/index.js` (full), `src/base.js` (tree-shakeable) |
+| Plugin base class | `src/plugins/base/base.js` |
+| Meta schema (defaults) | `src/dataMap/metaManager/metaSchema.js` |
+| Index translations | `src/translations/` |
+| Walkontable engine | `src/3rdparty/walkontable/src/` |
+| Hooks system | `src/core/hooks/` |
+| DataProvider plugin | `src/plugins/dataProvider/dataProvider.js` |
+| Error helpers | `src/helpers/errors.js` |
+| i18n constants | `src/i18n/constants.js` |
+| i18n language files | `src/i18n/languages/` |
+| TypeScript definitions | `types/` |
+
+## Context Menu vs Column Menu
+
+| | Context menu | Column menu (dropdown menu) |
+|---|---|---|
+| **Plugin class / key** | `ContextMenu` / `'contextMenu'` | `DropdownMenu` / `'dropdownMenu'` |
+| **Trigger** | Right-click (or `Ctrl+Shift+\` / `Shift+F10`) | Column header button (or `Shift+Alt+ArrowDown`) |
+| **Scope** | Cells and headers across rows and columns | Column-specific operations only |
+| **Hook prefix** | `beforeContextMenu*`, `afterContextMenu*` | `beforeDropdownMenu*`, `afterDropdownMenu*` |
+
+`DropdownMenu` is built on the shared `Menu` class from `contextMenu` but configured and triggered independently.
+
+## Lint
+
+```
+npm run lint
+```
+
+## Build
+
+`npm run build`
+
+| Output | Path |
+|---|---|
+| UMD / minified bundles | `dist/` |
+| ES and CJS modules (used by wrappers) | `tmp/` |
+| Compiled CSS | `styles/` |
+
+Two build variants: `handsontable.js` (base, external deps) and `handsontable.full.js` (includes HyperFormula). The E2E runner loads `dist/handsontable.js` - rebuild after changing `src/`.
+
+## For Deeper Guidance
+
+Use these skills for detailed workflow instructions:
+- Plugin development: `handsontable-plugin-dev`
+- Editors/renderers/validators/cellTypes: `handsontable-editor-dev`, `handsontable-renderer-dev`, `handsontable-validator-dev`, `handsontable-celltype-dev`
+- Testing: `handsontable-unit-testing`, `handsontable-e2e-testing`
+- Coordinate systems: `coordinate-systems`
+- Linting: `linting`
+- i18n: `i18n-translations`
diff --git a/handsontable/CLAUDE.md b/handsontable/CLAUDE.md
@@ -1,75 +0,0 @@
-# Handsontable Core Package
-
-This is the core data grid package. **JavaScript only** - no TypeScript files in `src/`. Type definitions are hand-authored `.d.ts` files in `types/`.
-
-## Critical Rules
-
-- Use `throwWithCause()` from `src/helpers/errors.js`, never `throw new Error()`
-- No barrel imports from `plugins/index`, `editors/index`, `renderers/index`, `validators/index`, `cellTypes/index`, `i18n/index` - import from specific submodule paths. Only exception: `src/registry.js`
-- No global `window`, `document`, `console` - use `this.hot.rootWindow`, `this.hot.rootDocument`, and helpers from `src/helpers/console.js`
-- Private fields use `#` prefix, not `@private` JSDoc
-- Arrow function class fields for callbacks: `#onAfterX = () => { ... }` (not `.bind(this)`)
-- Cognitive complexity: keep each function at 15 or below
-- Optional chaining `?.` only when value is genuinely optional by design
-
-## Plugin Lifecycle
-
-```
-isEnabled()      → return !!this.hot.getSettings()[PLUGIN_KEY]
-enablePlugin()   → init state, create IndexMaps, register hooks. super.enablePlugin() AT END.
-updatePlugin()   → this.disablePlugin(); this.enablePlugin(); super.updatePlugin();
-disablePlugin()  → super.disablePlugin() FIRST. Then clean up.
-destroy()        → null out fields. super.destroy() AT END.
-```
-
-Gold standard: `src/plugins/pagination/pagination.js`
-
-## Three Coordinate Systems
-
-| Type | Description | Use for |
-|------|-------------|---------|
-| Physical | Position in source data array | Data access, persistence |
-| Visual | Position after trimming (DataMap) | User-facing display logic |
-| Renderable | Position after hiding (DOM) | DOM operations |
-
-Translate with `hot.rowIndexMapper` / `hot.columnIndexMapper`.
-Gotcha: Filters `conditionCollection` uses physical indexes, `getDataAtCol()` uses visual.
-
-## DataProvider and Notification
-
-For server-backed grids (`dataProvider` with `fetchRows` and CRUD callbacks), enable **`notification`** if you want built-in error toasts on failed fetches or mutations. **`dialog: true` alone does not** show those errors. Failed **fetch** toasts include a **Refetch** button that calls `fetchData()` again (`duration: 0` until dismissed or Refetch). Use **`afterDataProviderFetchError`** and **`afterRowsMutationError`** for custom UI when Notification is disabled. See `src/plugins/dataProvider/dataProvider.js` and AGENTS.md Gotchas.
-
-## Testing
-
-| Type | Pattern | Framework | Run |
-|------|---------|-----------|-----|
-| Unit | `*.unit.js` | Jest (jsdom) | `npm run test:unit` |
-| E2E | `*.spec.js` | Jasmine (Puppeteer) | `npm run test:e2e` |
-
-- ALL `it()` callbacks in spec files MUST be `async`
-- HOT API calls MUST be `await`-ed
-- E2E helpers are globals (no imports): `handsontable()`, `selectCell()`, `getDataAtCell()`, `createSpreadsheetData()`
-- Targeted unit: `npm run test:unit --testPathPattern=<regex>` (regex matched against file paths, e.g. `filters`, `ghostTable.unit`)
-- Targeted e2e: `npm run test:e2e --testPathPattern=<regex>` (e.g. `collapsibleColumns`, `textEditor`, `nestedHeaders/__tests__/hidingColumns`)
-- E2E with theme: `npm run test:e2e --testPathPattern=<regex> --theme=horizon` (themes: `classic`, `main`, `horizon`; default: `main`)
-- **Rebuild before E2E:** E2E runner loads `dist/handsontable.js` - rebuild after changing `src/`
-
-## Merged Cells Gotcha
-
-Read `colspan`/`rowspan` from `hot.getCellMeta(row, col)`, NOT from DOM element attributes. The meta (set by MergeCells via `afterGetCellMeta`) is authoritative and always available regardless of viewport state.
-
-## Build
-
-`npm run build`
-
-Outputs: `dist/` (UMD), `tmp/` (ES/CJS, used by wrappers), `styles/` (CSS)
-
-## For Deeper Guidance
-
-Use these skills for detailed workflow instructions:
-- Plugin development: `handsontable-plugin-dev`
-- Editors/renderers/validators/cellTypes: `handsontable-editor-dev`, `handsontable-renderer-dev`, `handsontable-validator-dev`, `handsontable-celltype-dev`
-- Testing: `handsontable-unit-testing`, `handsontable-e2e-testing`
-- Coordinate systems: `coordinate-systems`
-- Linting: `linting`
-- i18n: `i18n-translations`
diff --git a/handsontable/CLAUDE.md b/handsontable/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
diff --git a/handsontable/src/3rdparty/walkontable/AGENTS.md b/handsontable/src/3rdparty/walkontable/AGENTS.md
@@ -0,0 +1,38 @@
+# Walkontable Rendering Engine
+
+Self-contained rendering engine for viewport calculation, DOM rendering, scroll synchronization, and the overlay system.
+
+## Architecture Boundary
+
+- Walkontable lives in `src/3rdparty/walkontable/src/`
+- The bridge to core Handsontable is `src/tableView.js` (TableView class)
+- Plugins must NEVER access Walkontable internals directly - always go through TableView
+- Do not import core Handsontable modules from Walkontable code
+
+## Key Subsystems
+
+- **Overlay system** (6 types): Frozen rows/columns and scroll sync. Fragile - proceed with caution.
+- **Viewport calculation**: Determines visible rows/columns based on scroll position
+- **Renderer**: DOM element management, cell reuse
+- **Scroll handling**: requestAnimationFrame batching required
+
+## Known Tech Debt
+
+- DAO layer uses Data Access Objects instead of DI (20+ TODO comments)
+- Filter objects are recreated instead of updated
+- See `.ai/CONCERNS.md` for full list
+
+## Performance
+
+- Batch scroll events with requestAnimationFrame
+- Never `arr.push(...largeArray)` with 10k+ elements
+- Reuse DOM elements, minimize layout thrashing
+
+## Testing
+
+Separate test runner - do NOT mix with main E2E tests:
+`pnpm --filter handsontable run test:walkontable`
+
+Tests in: `src/3rdparty/walkontable/test/`
+
+For detailed guidance: use skills `walkontable-dev`, `walkontable-testing`
diff --git a/handsontable/src/3rdparty/walkontable/CLAUDE.md b/handsontable/src/3rdparty/walkontable/CLAUDE.md
@@ -1,38 +0,0 @@
-# Walkontable Rendering Engine
-
-Self-contained rendering engine for viewport calculation, DOM rendering, scroll synchronization, and the overlay system.
-
-## Architecture Boundary
-
-- Walkontable lives in `src/3rdparty/walkontable/src/`
-- The bridge to core Handsontable is `src/tableView.js` (TableView class)
-- Plugins must NEVER access Walkontable internals directly - always go through TableView
-- Do not import core Handsontable modules from Walkontable code
-
-## Key Subsystems
-
-- **Overlay system** (6 types): Frozen rows/columns and scroll sync. Fragile - proceed with caution.
-- **Viewport calculation**: Determines visible rows/columns based on scroll position
-- **Renderer**: DOM element management, cell reuse
-- **Scroll handling**: requestAnimationFrame batching required
-
-## Known Tech Debt
-
-- DAO layer uses Data Access Objects instead of DI (20+ TODO comments)
-- Filter objects are recreated instead of updated
-- See `.ai/CONCERNS.md` for full list
-
-## Performance
-
-- Batch scroll events with requestAnimationFrame
-- Never `arr.push(...largeArray)` with 10k+ elements
-- Reuse DOM elements, minimize layout thrashing
-
-## Testing
-
-Separate test runner - do NOT mix with main E2E tests:
-`pnpm --filter handsontable run test:walkontable`
-
-Tests in: `src/3rdparty/walkontable/test/`
-
-For detailed guidance: use skills `walkontable-dev`, `walkontable-testing`
diff --git a/handsontable/src/3rdparty/walkontable/CLAUDE.md b/handsontable/src/3rdparty/walkontable/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
diff --git a/visual-tests/AGENTS.md b/visual-tests/AGENTS.md
@@ -0,0 +1,47 @@
+# Visual Regression Tests
+
+Playwright-based visual regression testing with Argos CI for screenshot comparison.
+
+## Framework
+
+- Playwright with TypeScript
+- Custom `tablePage` fixture from `src/test-runner.ts` (auto-navigates to demo, disables animations, waits for table)
+- Config: `playwright.config.ts`, `playwright-cross-browser.config.ts`
+
+## Test Pattern
+
+```typescript
+import { test } from '../../../src/test-runner';
+import { helpers } from '../../../src/helpers';
+
+test(__filename, async({ tablePage }) => {
+  // Setup
+  const cell = await tablePage.locator('.ht_master td').first();
+  await cell.click();
+
+  // Capture state
+  await tablePage.screenshot({ path: helpers.screenshotPath() });
+
+  // Action + another screenshot
+  await tablePage.keyboard.press('Escape');
+  await tablePage.screenshot({ path: helpers.screenshotPath() });
+});
+```
+
+## Key Rules
+
+- Test naming: `__filename` auto-generates title from file path
+- Screenshots: Always use `helpers.screenshotPath()` for consistent naming
+- Organization: `tests/js-only/`, `tests/multi-frameworks/`, `tests/cross-browser/`
+- Examples for testing live in `examples/next/docs/`
+
+## Helpers
+
+- `src/helpers.ts`: screenshotPath, DOM selectors, platform detection
+- `src/page-helpers.ts`: selectCell, menu navigation, high-level interactions
+
+## Run
+
+See `package.json` scripts for build, test, and upload commands.
+
+For detailed guidance: use skills `visual-testing`, `creating-visual-test-examples`
diff --git a/visual-tests/CLAUDE.md b/visual-tests/CLAUDE.md
@@ -1,47 +0,0 @@
-# Visual Regression Tests
-
-Playwright-based visual regression testing with Argos CI for screenshot comparison.
-
-## Framework
-
-- Playwright with TypeScript
-- Custom `tablePage` fixture from `src/test-runner.ts` (auto-navigates to demo, disables animations, waits for table)
-- Config: `playwright.config.ts`, `playwright-cross-browser.config.ts`
-
-## Test Pattern
-
-```typescript
-import { test } from '../../../src/test-runner';
-import { helpers } from '../../../src/helpers';
-
-test(__filename, async({ tablePage }) => {
-  // Setup
-  const cell = await tablePage.locator('.ht_master td').first();
-  await cell.click();
-
-  // Capture state
-  await tablePage.screenshot({ path: helpers.screenshotPath() });
-
-  // Action + another screenshot
-  await tablePage.keyboard.press('Escape');
-  await tablePage.screenshot({ path: helpers.screenshotPath() });
-});
-```
-
-## Key Rules
-
-- Test naming: `__filename` auto-generates title from file path
-- Screenshots: Always use `helpers.screenshotPath()` for consistent naming
-- Organization: `tests/js-only/`, `tests/multi-frameworks/`, `tests/cross-browser/`
-- Examples for testing live in `examples/next/docs/`
-
-## Helpers
-
-- `src/helpers.ts`: screenshotPath, DOM selectors, platform detection
-- `src/page-helpers.ts`: selectCell, menu navigation, high-level interactions
-
-## Run
-
-See `package.json` scripts for build, test, and upload commands.
-
-For detailed guidance: use skills `visual-testing`, `creating-visual-test-examples`
diff --git a/visual-tests/CLAUDE.md b/visual-tests/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
diff --git a/wrappers/angular-wrapper/AGENTS.md b/wrappers/angular-wrapper/AGENTS.md
@@ -0,0 +1,41 @@
+# Angular Wrapper (@handsontable/angular-wrapper)
+
+## Critical Rules
+
+- **No business logic** in wrappers - belongs in `handsontable/src/`
+- **Feature parity**: Angular wrapper must expose identical Handsontable functionality
+- **Build core first**: `npm run build --prefix handsontable` - wrappers consume `handsontable/tmp/` not `dist/`
+- Cross-platform scripts: Use Node.js `.mjs` helpers, never bash constructs
+
+## Architecture
+
+- Library source: `projects/hot-table/src/lib/`
+- `@Component` with `@Input()` decorators for each Handsontable option
+- Lifecycle: `AfterViewInit` (create), `OnChanges` (update), `OnDestroy` (cleanup)
+- `@ViewChild('container')` for DOM access
+- `NgZone.runOutsideAngular()` for performance (runs HOT outside Angular change detection)
+- Services: `HotSettingsResolver`, `HotGlobalConfig`
+- `HotTableModule` for Angular module system
+
+## Key Files
+
+- `projects/hot-table/src/lib/hot-table.component.ts`
+- `projects/hot-table/src/lib/services/`
+
+## Build & Test
+
+- Build: ng-packagr 16
+- Test: `npm run test --prefix wrappers/angular-wrapper` (Jest + jest-preset-angular)
+- Gotcha: Tests use `NODE_OPTIONS=--openssl-legacy-provider`
+
+## Common Pitfalls
+
+| Pitfall | What to do instead |
+|---|---|
+| `arr.push(...largeArray)` with large arrays | Causes stack overflow with 10k+ elements. Use `forEach` loop instead. |
+| Using `standalone: false` or `AppModule` | All Angular docs examples use `standalone: true` with `imports: [HotTableModule]` and `app.config.ts`. |
+| Adding `licenseKey` to individual `<hot-table>` | Set it globally via `HOT_GLOBAL_CONFIG` in `app.config.ts`. Never put it on each component. |
+| Using `*ngIf` / `*ngFor` in templates | Use Angular 17+ built-in control flow: `@if (cond) { }` and `@for (x of list; track x.id) { }`. |
+| Typing Angular row data as `any[]` | Use `RowObject[]` imported from `handsontable/common`. |
+
+For detailed guidance: use skill `angular-wrapper-dev`
diff --git a/wrappers/angular-wrapper/CLAUDE.md b/wrappers/angular-wrapper/CLAUDE.md
@@ -1,30 +0,0 @@
-# Angular Wrapper (@handsontable/angular-wrapper)
-
-## Critical Rules
-
-- **No business logic** in wrappers - belongs in `handsontable/src/`
-- **Build core first**: `pnpm --filter handsontable run build` - wrappers consume `handsontable/tmp/`
-- Cross-platform scripts: Use Node.js `.mjs` helpers, never bash constructs
-
-## Architecture
-
-- Library source: `projects/hot-table/src/lib/`
-- `@Component` with `@Input()` decorators for each Handsontable option
-- Lifecycle: `AfterViewInit` (create), `OnChanges` (update), `OnDestroy` (cleanup)
-- `@ViewChild('container')` for DOM access
-- `NgZone.runOutsideAngular()` for performance (runs HOT outside Angular change detection)
-- Services: `HotSettingsResolver`, `HotGlobalConfig`
-- `HotTableModule` for Angular module system
-
-## Key Files
-
-- `projects/hot-table/src/lib/hot-table.component.ts`
-- `projects/hot-table/src/lib/services/`
-
-## Build & Test
-
-- Build: ng-packagr 16
-- Test: `pnpm --filter @handsontable/angular-wrapper run test` (Jest + jest-preset-angular)
-- Gotcha: Tests use `NODE_OPTIONS=--openssl-legacy-provider`
-
-For detailed guidance: use skill `angular-wrapper-dev`
diff --git a/wrappers/angular-wrapper/CLAUDE.md b/wrappers/angular-wrapper/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
diff --git a/wrappers/react-wrapper/AGENTS.md b/wrappers/react-wrapper/AGENTS.md
@@ -0,0 +1,35 @@
+# React Wrapper (@handsontable/react-wrapper)
+
+## Critical Rules
+
+- **No business logic** in wrappers - data transformation, validation, cell manipulation belongs in `handsontable/src/`
+- **Feature parity**: React wrapper must expose identical Handsontable functionality
+- **Build core first**: `npm run build --prefix handsontable` - wrappers consume `handsontable/tmp/` not `dist/`
+- **Preserve selection** during updateSettings: use `selection.exportSelection()` / `selection.importSelection()`
+- Cross-platform scripts: Use Node.js `.mjs` helpers, never bash-only constructs
+
+## Architecture
+
+- `HotTable` (public) -> `HotTableInner` (forwardRef) -> Handsontable instance via `useRef()`
+- `SettingsMapper.getSettings()` converts React props -> Handsontable settings
+- `useImperativeHandle` exposes the instance
+- React portals and context for component-based renderers/editors
+- `useHotEditor()` hook for custom editors
+
+## Key Files
+
+- `src/hotTable.tsx`, `src/hotTableInner.tsx`, `src/settingsMapper.ts`
+- `src/hotColumn.tsx`, `src/hotEditor.tsx`
+
+## Build & Test
+
+- Build: Rollup 4 (CommonJS, ES, UMD, minified)
+- Test: `npm run test --prefix wrappers/react-wrapper` (Jest + React Testing Library)
+
+## Common Pitfalls
+
+| Pitfall | What to do instead |
+|---|---|
+| `arr.push(...largeArray)` with large arrays | Causes stack overflow with 10k+ elements. Use `forEach` loop instead. |
+
+For detailed guidance: use skill `react-wrapper-dev`
diff --git a/wrappers/react-wrapper/CLAUDE.md b/wrappers/react-wrapper/CLAUDE.md
@@ -1,28 +0,0 @@
-# React Wrapper (@handsontable/react-wrapper)
-
-## Critical Rules
-
-- **No business logic** in wrappers - data transformation, validation, cell manipulation belongs in `handsontable/src/`
-- **Build core first**: `pnpm --filter handsontable run build` - wrappers consume `handsontable/tmp/` not `dist/`
-- **Preserve selection** during updateSettings: use `selection.exportSelection()` / `selection.importSelection()`
-- Cross-platform scripts: Use Node.js `.mjs` helpers, never bash-only constructs
-
-## Architecture
-
-- `HotTable` (public) -> `HotTableInner` (forwardRef) -> Handsontable instance via `useRef()`
-- `SettingsMapper.getSettings()` converts React props -> Handsontable settings
-- `useImperativeHandle` exposes the instance
-- React portals and context for component-based renderers/editors
-- `useHotEditor()` hook for custom editors
-
-## Key Files
-
-- `src/hotTable.tsx`, `src/hotTableInner.tsx`, `src/settingsMapper.ts`
-- `src/hotColumn.tsx`, `src/hotEditor.tsx`
-
-## Build & Test
-
-- Build: Rollup 4 (CommonJS, ES, UMD, minified)
-- Test: `pnpm --filter @handsontable/react-wrapper run test` (Jest + React Testing Library)
-
-For detailed guidance: use skill `react-wrapper-dev`
diff --git a/wrappers/react-wrapper/CLAUDE.md b/wrappers/react-wrapper/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
diff --git a/wrappers/vue3/AGENTS.md b/wrappers/vue3/AGENTS.md
@@ -0,0 +1,34 @@
+# Vue 3 Wrapper (@handsontable/vue3)
+
+## Critical Rules
+
+- **No business logic** in wrappers - belongs in `handsontable/src/`
+- **Feature parity**: Vue 3 wrapper must expose identical Handsontable functionality
+- **Build core first**: `npm run build --prefix handsontable` - wrappers consume `handsontable/tmp/` not `dist/`
+- Cross-platform scripts: Use Node.js `.mjs` helpers
+
+## Architecture
+
+- SFC components: `HotTable.vue`, `HotColumn.vue`
+- `defineComponent` with `propFactory('HotTable')`
+- Deep watchers (`watch` with `deep: true`) detect prop changes -> `updateSettings()`
+- `prepareSettings()` transforms Vue props -> Handsontable settings
+- `provide()` exposes settings to HotColumn children
+- Data syncs by reference (no deep copying)
+
+## Key Files
+
+- `src/HotTable.vue`, `src/HotColumn.vue`, `src/helpers.ts`, `src/types.ts`
+
+## Build & Test
+
+- Build: Rollup 4
+- Test: `npm run test --prefix wrappers/vue3` (Jest + @vue/test-utils)
+
+## Common Pitfalls
+
+| Pitfall | What to do instead |
+|---|---|
+| `arr.push(...largeArray)` with large arrays | Causes stack overflow with 10k+ elements. Use `forEach` loop instead. |
+
+For detailed guidance: use skill `vue-wrapper-dev`
diff --git a/wrappers/vue3/CLAUDE.md b/wrappers/vue3/CLAUDE.md
@@ -1,27 +0,0 @@
-# Vue 3 Wrapper (@handsontable/vue3)
-
-## Critical Rules
-
-- **No business logic** in wrappers - belongs in `handsontable/src/`
-- **Build core first**: `pnpm --filter handsontable run build` - wrappers consume `handsontable/tmp/`
-- Cross-platform scripts: Use Node.js `.mjs` helpers
-
-## Architecture
-
-- SFC components: `HotTable.vue`, `HotColumn.vue`
-- `defineComponent` with `propFactory('HotTable')`
-- Deep watchers (`watch` with `deep: true`) detect prop changes -> `updateSettings()`
-- `prepareSettings()` transforms Vue props -> Handsontable settings
-- `provide()` exposes settings to HotColumn children
-- Data syncs by reference (no deep copying)
-
-## Key Files
-
-- `src/HotTable.vue`, `src/HotColumn.vue`, `src/helpers.ts`, `src/types.ts`
-
-## Build & Test
-
-- Build: Rollup 4
-- Test: `pnpm --filter @handsontable/vue3 run test` (Jest + @vue/test-utils)
-
-For detailed guidance: use skill `vue-wrapper-dev`
diff --git a/wrappers/vue3/CLAUDE.md b/wrappers/vue3/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
