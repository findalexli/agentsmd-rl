# Agent Config Files for nextjs-cna-skip-prompts-with-flags

Repo: vercel/next.js
Commit: e6bf5f69a23e6b8681dbc9cb59e7c1cdbe3b9b3c
Files found: 15


---
## .agents/skills/authoring-skills/SKILL.md

```
   1 | ---
   2 | name: authoring-skills
   3 | description: >
   4 |   How to create and maintain agent skills in .agents/skills/. Use when
   5 |   creating a new SKILL.md, writing skill descriptions, choosing frontmatter
   6 |   fields, or deciding what content belongs in a skill vs AGENTS.md.
   7 |   Covers the supported spec fields, description writing, naming conventions,
   8 |   and the relationship between always-loaded AGENTS.md and on-demand skills.
   9 | user-invocable: false
  10 | ---
  11 | 
  12 | # Authoring Skills
  13 | 
  14 | Use this skill when creating or modifying agent skills in `.agents/skills/`.
  15 | 
  16 | ## When to Create a Skill
  17 | 
  18 | Create a skill when content is:
  19 | 
  20 | - Too detailed for AGENTS.md (code templates, multi-step workflows, diagnostic procedures)
  21 | - Only relevant for specific tasks (not needed every session)
  22 | - Self-contained enough to load independently
  23 | 
  24 | Keep in AGENTS.md instead when:
  25 | 
  26 | - It's a one-liner rule or guardrail every session needs
  27 | - It's a general-purpose gotcha any agent could hit
  28 | 
  29 | ## File Structure
  30 | 
  31 | ```
  32 | .agents/skills/
  33 | └── my-skill/
  34 |     ├── SKILL.md          # Required: frontmatter + content
  35 |     ├── workflow.md        # Optional: supplementary detail
  36 |     └── examples.md        # Optional: referenced from SKILL.md
  37 | ```
  38 | 
  39 | ## Supported Frontmatter Fields
  40 | 
  41 | ```yaml
  42 | ---
  43 | name: my-skill # Required. Used for $name references and /name commands.
  44 | description: > # Required. How Claude decides to auto-load the skill.
  45 |   What this covers and when to use it. Include file names and keywords.
  46 | argument-hint: '<pr-number>' # Optional. Hint for expected arguments.
  47 | user-invocable: false # Optional. Set false to hide from / menu.
  48 | disable-model-invocation: true # Optional. Set true to prevent auto-triggering.
  49 | allowed-tools: [Bash, Read] # Optional. Tools allowed without permission.
  50 | model: opus # Optional. Model override.
  51 | context: fork # Optional. Isolated subagent execution.
  52 | agent: Explore # Optional. Subagent type (with context: fork).
  53 | ---
  54 | ```
  55 | 
  56 | Only use fields from this list. Unknown fields are silently ignored.
  57 | 
  58 | ## Writing Descriptions
  59 | 
  60 | The `description` is the primary matching surface for auto-activation. Include:
  61 | 
  62 | 1. **What the skill covers** (topic)
  63 | 2. **When to use it** (trigger scenario)
  64 | 3. **Key file names** the skill references (e.g. `config-shared.ts`)
  65 | 4. **Keywords** a user or agent might mention (e.g. "feature flag", "DCE")
  66 | 
  67 | ```yaml
  68 | # Too vague - won't auto-trigger reliably
  69 | description: Helps with flags.
  70 | 
  71 | # Good - specific files and concepts for matching
  72 | description: >
  73 |   How to add or modify Next.js experimental feature flags end-to-end.
  74 |   Use when editing config-shared.ts, config-schema.ts, define-env-plugin.ts.
  75 | ```
  76 | 
  77 | ## Content Conventions
  78 | 
  79 | ### Structure for Action
  80 | 
  81 | Skills should tell the agent what to **do**, not just what to **know**:
  82 | 
  83 | - Lead with "Use this skill when..."
  84 | - Include step-by-step procedures
  85 | - Add code templates ready to adapt
  86 | - End with verification commands
  87 | - Cross-reference related skills in a "Related Skills" section
  88 | 
  89 | ### Relationship to AGENTS.md
  90 | 
  91 | | AGENTS.md (always loaded)               | Skills (on demand)                                                     |
  92 | | --------------------------------------- | ---------------------------------------------------------------------- |
  93 | | One-liner guardrails                    | Step-by-step workflows                                                 |
  94 | | "Keep require() behind if/else for DCE" | Full DCE pattern with code examples, verification commands, edge cases |
  95 | | Points to skills via `$name`            | Expands on AGENTS.md rules                                             |
  96 | 
  97 | When adding a skill, also add a one-liner summary to the relevant AGENTS.md section with a `$skill-name` reference.
  98 | 
  99 | ### Naming
 100 | 
 101 | - Short, descriptive, topic-scoped: `flags`, `dce-edge`, `react-vendoring`
 102 | - No repo prefix (already scoped by `.agents/skills/`)
 103 | - Hyphens for multi-word names
 104 | 
 105 | ### Supplementary Files
 106 | 
 107 | For complex skills, use a hub + detail pattern:
 108 | 
 109 | ```
 110 | pr-status-triage/
 111 | ├── SKILL.md         # Overview, quick commands, links to details
 112 | ├── workflow.md      # Prioritization and patterns
 113 | └── local-repro.md   # CI env matching
 114 | ```
```


---
## .agents/skills/dce-edge/SKILL.md

```
   1 | ---
   2 | name: dce-edge
   3 | description: >
   4 |   DCE-safe require() patterns and edge runtime constraints. Use when writing
   5 |   conditional require() calls, guarding Node-only imports (node:stream etc.),
   6 |   or editing define-env-plugin.ts / app-render / stream-utils for edge builds.
   7 |   Covers if/else branching for webpack DCE, TypeScript definite assignment,
   8 |   the NEXT_RUNTIME vs real feature flag distinction, and forcing flags false
   9 |   for edge in define-env.ts.
  10 | ---
  11 | 
  12 | # DCE + Edge
  13 | 
  14 | Use this skill when changing conditional `require()` paths, Node-only imports, or edge/runtime branching.
  15 | 
  16 | ## DCE-Safe `require()` Pattern
  17 | 
  18 | Webpack only DCEs a `require()` when it sits inside the dead branch of an `if/else` whose condition DefinePlugin can evaluate at compile time.
  19 | 
  20 | ```ts
  21 | // CORRECT - webpack can eliminate the dead branch
  22 | if (process.env.__NEXT_USE_NODE_STREAMS) {
  23 |   require('node:stream')
  24 | } else {
  25 |   // web path
  26 | }
  27 | ```
  28 | 
  29 | What does NOT work:
  30 | 
  31 | - **Early-return/throw guards**: webpack doesn't do control-flow analysis for throws/returns, so the `require()` is still traced.
  32 | - **Bare `if` without `else`**: works for inline `node:*` specifiers but NOT for `require('./some-module')` that pulls a new file into the module graph.
  33 | 
  34 | Always test edge changes with `pnpm test-start-webpack` on `test/e2e/app-dir/app/standalone.test.ts` (has edge routes), not with `NEXT_SKIP_ISOLATE=1` which skips the full webpack compilation.
  35 | 
  36 | ## TypeScript + DCE Interaction
  37 | 
  38 | Use `if/else` (not two independent `if` blocks) when assigning a variable conditionally on `process.env.X`. TypeScript cannot prove exhaustiveness across `if (flag) { x = a }; if (!flag) { x = b }` and will error with "variable used before being assigned". The `if/else` pattern satisfies both TypeScript (definite assignment) and webpack DCE.
  39 | 
  40 | ## Compile-Time Switcher Pattern
  41 | 
  42 | Platform-specific code (node vs web) can use a single `.ts` switcher module that conditionally `require()`s either `.node.ts` or `.web.ts` into a typed variable, then re-exports the shared runtime API as named exports. Keep the branch as `if/else` so DefinePlugin can dead-code-eliminate the unused `require()`. Keep shared types canonical in `.node.ts`, with `.web.ts` importing them via `import type` and the switcher re-exporting types as needed. Examples: `stream-ops.ts` and `debug-channel-server.ts`.
  43 | 
  44 | ## `NEXT_RUNTIME` Is Not a Feature Flag
  45 | 
  46 | In user-project webpack server compilers, `process.env.NEXT_RUNTIME` is inlined to `'nodejs'`. Guarding Node-only `require('node:*')` paths with `NEXT_RUNTIME === 'nodejs'` does **not** prune anything. For feature-gated codepaths, guard on the real feature define (e.g. `process.env.__NEXT_USE_NODE_STREAMS`).
  47 | 
  48 | ## Edge Runtime Constraints
  49 | 
  50 | Edge routes do NOT use pre-compiled runtime bundles. They are compiled by the user's webpack/Turbopack, so `define-env.ts` controls DCE. Feature flags that gate `node:*` imports must be forced to `false` for edge builds in `define-env.ts` (`isEdgeServer ? false : flagValue`), otherwise webpack will try to resolve `node:stream` etc. and fail.
  51 | 
  52 | ## `app-page.ts` Template Gotchas
  53 | 
  54 | - `app-page.ts` is a build template compiled by the user's bundler. Any `require()` in this file is traced by webpack/turbopack at `next build` time. You cannot require internal modules with relative paths because they won't be resolvable from the user's project. Instead, export new helpers from `entry-base.ts` and access them via `entryBase.*` in the template.
  55 | - Template helpers should stay out of `RenderResult`. If `app-page.ts` needs a Node-stream-only utility, prefer a small dedicated helper module in `server/stream-utils/` (with DCE-safe `if/else` + `require()`).
  56 | 
  57 | ## Verification
  58 | 
  59 | - Validate edge bundling regressions with `pnpm test-start-webpack test/e2e/app-dir/app/standalone.test.ts`
  60 | - For module-resolution/build-graph fixes, verify without `NEXT_SKIP_ISOLATE=1`
  61 | 
  62 | ## Related Skills
  63 | 
  64 | - `$flags` - flag wiring (config/schema/define-env/runtime env)
  65 | - `$react-vendoring` - entry-base boundaries and vendored React
  66 | - `$runtime-debug` - reproduction and verification workflow
```


---
## .agents/skills/flags/SKILL.md

```
   1 | ---
   2 | name: flags
   3 | description: >
   4 |   How to add or modify Next.js experimental feature flags end-to-end.
   5 |   Use when editing config-shared.ts, config-schema.ts, define-env-plugin.ts,
   6 |   next-server.ts, export/worker.ts, or module.compiled.js. Covers type
   7 |   declaration, zod schema, build-time injection, runtime env plumbing,
   8 |   and the decision between runtime env-var branching vs separate bundle variants.
   9 | ---
  10 | 
  11 | # Feature Flags
  12 | 
  13 | Use this skill when adding or changing framework feature flags in Next.js internals.
  14 | 
  15 | ## Required Wiring
  16 | 
  17 | All flags need: `config-shared.ts` (type) → `config-schema.ts` (zod). If the flag is consumed in user-bundled code (client components, edge routes, `app-page.ts` template), also add it to `define-env.ts` for build-time injection. Runtime-only flags consumed exclusively in pre-compiled bundles can skip `define-env.ts`.
  18 | 
  19 | ## Where the Flag Is Consumed
  20 | 
  21 | **Client/bundled code only** (e.g. `__NEXT_PPR` in client components): `define-env.ts` is sufficient. Webpack/Turbopack replaces `process.env.X` at the user's build time.
  22 | 
  23 | **Pre-compiled runtime bundles** (e.g. code in `app-render.tsx`): The flag must also be set as a real `process.env` var at runtime, because `app-render.tsx` runs from pre-compiled bundles where `define-env.ts` doesn't reach. Two approaches:
  24 | 
  25 | - **Runtime env var**: Set in `next-server.ts` + `export/worker.ts`. Both code paths stay in one bundle. Simple but increases bundle size.
  26 | - **Separate bundle variant**: Add DefinePlugin entry in `next-runtime.webpack-config.js` (scoped to `bundleType === 'app'`), new taskfile tasks, update `module.compiled.js` selector, and still set env var in `next-server.ts` + `export/worker.ts` for bundle selection. Eliminates dead code but adds build complexity.
  27 | 
  28 | For runtime flags, also add the field to the `NextConfigRuntime` Pick type in `config-shared.ts`.
  29 | 
  30 | ## Runtime-Bundle Model
  31 | 
  32 | - Runtime bundles are built by `next-runtime.webpack-config.js` (rspack) via `taskfile.js` bundle tasks.
  33 | - Bundle selection occurs at runtime in `src/server/route-modules/app-page/module.compiled.js` based on `process.env` vars.
  34 | - Variants: `{turbo/webpack} × {experimental/stable/nodestreams/experimental-nodestreams} × {dev/prod}` = up to 16 bundles per route type.
  35 | - `define-env.ts` affects user bundling, not pre-compiled runtime internals.
  36 | - `process.env.X` checks in `app-render.tsx` are either replaced by DefinePlugin at runtime-bundle-build time, or read as actual env vars at server startup. They are NOT affected by the user's defines from `define-env.ts`.
  37 | - **Gotcha**: DefinePlugin entries in `next-runtime.webpack-config.js` must be scoped to the correct `bundleType` (e.g. `app` only, not `server`) to avoid replacing assignment targets in `next-server.ts`.
  38 | 
  39 | ## Related Skills
  40 | 
  41 | - `$dce-edge` - DCE-safe require patterns and edge constraints
  42 | - `$react-vendoring` - entry-base boundaries and vendored React
  43 | - `$runtime-debug` - reproduction and verification workflow
```


---
## .agents/skills/pr-status-triage/SKILL.md

```
   1 | ---
   2 | name: pr-status-triage
   3 | description: >
   4 |   Triage CI failures and PR review comments using scripts/pr-status.js.
   5 |   Use when investigating failing CI jobs, flaky tests, or PR review feedback.
   6 |   Covers blocker-first prioritization (build > lint > types > tests),
   7 |   CI env var matching for local reproduction, and the Known Flaky Tests
   8 |   distinction.
   9 | ---
  10 | 
  11 | # PR Status Triage
  12 | 
  13 | Use this skill when the user asks about PR status, CI failures, or review comments in the Next.js monorepo.
  14 | 
  15 | ## Workflow
  16 | 
  17 | 1. Run `node scripts/pr-status.js --wait` in the background (timeout 1 min), then read `scripts/pr-status/index.md`.
  18 | 2. Analyze each `job-{id}.md` and `thread-{N}.md` file for failures and review feedback.
  19 | 3. Prioritize blocking jobs first: build, lint, types, then test jobs.
  20 | 4. Treat failures as real until disproven; check the "Known Flaky Tests" section before calling anything flaky.
  21 | 5. Reproduce locally with the same mode and env vars as CI.
  22 | 6. After addressing review comments, reply to the thread describing what was done, then resolve it. See `thread-N.md` files for ready-to-use commands.
  23 | 7. When the only remaining failures are known flaky tests and no code changes are needed, retrigger the failing CI jobs with `gh run rerun <run-id> --failed`. Then wait 5 minutes and go back to step 1. Repeat this loop up to 5 times.
  24 | 
  25 | ## Quick Commands
  26 | 
  27 | ```bash
  28 | node scripts/pr-status.js                  # current branch PR
  29 | node scripts/pr-status.js <number>         # specific PR
  30 | node scripts/pr-status.js [PR] --wait      # background mode, waits for CI to finish
  31 | node scripts/pr-status.js --skip-flaky-check  # skip flaky test detection
  32 | ```
  33 | 
  34 | ## References
  35 | 
  36 | - [workflow.md](./workflow.md) — prioritization, common failure patterns, resolving review threads
  37 | - [local-repro.md](./local-repro.md) — mode/env matching and isolation guidance
```


---
## .agents/skills/react-vendoring/SKILL.md

```
   1 | ---
   2 | name: react-vendoring
   3 | description: >
   4 |   React vendoring and react-server layer boundaries. Use when editing
   5 |   entry-base.ts, $$compiled.internal.d.ts, compiled/react* packages,
   6 |   or taskfile.js copy_vendor_react. Covers the entry-base.ts boundary
   7 |   (all react-server-dom-webpack/* imports must go through it), vendored
   8 |   React channels, type declarations, Turbopack remap to
   9 |   react-server-dom-turbopack, ComponentMod access patterns, and ESLint
  10 |   suppression for guarded requires.
  11 | ---
  12 | 
  13 | # React Vendoring
  14 | 
  15 | Use this skill for changes touching vendored React, `react-server-dom-webpack/*`, or react-server layer boundaries.
  16 | 
  17 | ## App Router Vendoring
  18 | 
  19 | React is NOT resolved from `node_modules` for App Router. It's vendored into `packages/next/src/compiled/` during `pnpm build` (task: `copy_vendor_react()` in `taskfile.js`). Pages Router resolves React from `node_modules` normally.
  20 | 
  21 | - **Two channels**: stable (`compiled/react/`) and experimental (`compiled/react-experimental/`). The runtime bundle webpack config aliases to the correct channel via `makeAppAliases({ experimental })`.
  22 | 
  23 | ## `entry-base.ts` Boundary
  24 | 
  25 | Only `entry-base.ts` is compiled in rspack's `(react-server)` layer. ALL imports from `react-server-dom-webpack/*` (Flight server/static APIs) must go through `entry-base.ts`. Other files like `stream-ops.node.ts` or `app-render.tsx` must access Flight APIs via the `ComponentMod` parameter (which is the `entry-base.ts` module exposed through the `app-page.ts` build template).
  26 | 
  27 | Direct imports from `react-server-dom-webpack/server.node` or `react-server-dom-webpack/static` in files outside `entry-base.ts` will fail at runtime with "The react-server condition must be enabled". Dev mode may mask this error, but production workers fail immediately.
  28 | 
  29 | ## Type Declarations
  30 | 
  31 | `packages/next/types/$$compiled.internal.d.ts` contains `declare module` blocks for vendored React packages. When adding new APIs (e.g. `renderToPipeableStream`, `prerenderToNodeStream`), you must add type declarations here. The bare specifier types (e.g. `declare module 'react-server-dom-webpack/server'`) are what source code in `src/` imports against.
  32 | 
  33 | ## Adding Node.js-Only React APIs
  34 | 
  35 | These exist in `.node` builds but not in the type definitions. Steps:
  36 | 
  37 | 1. Add type declarations to `$$compiled.internal.d.ts`.
  38 | 2. Export the API from `entry-base.ts` behind a `process.env` guard.
  39 | 3. Access it via `ComponentMod` in other files.
  40 | 
  41 | ```typescript
  42 | // In entry-base.ts (react-server layer) only:
  43 | /* eslint-disable import/no-extraneous-dependencies */
  44 | export let renderToPipeableStream: ... | undefined
  45 | if (process.env.__NEXT_USE_NODE_STREAMS) {
  46 |   renderToPipeableStream = (
  47 |     require('react-server-dom-webpack/server.node') as typeof import('react-server-dom-webpack/server.node')
  48 |   ).renderToPipeableStream
  49 | } else {
  50 |   renderToPipeableStream = undefined
  51 | }
  52 | /* eslint-enable import/no-extraneous-dependencies */
  53 | 
  54 | // In other files, access via ComponentMod:
  55 | ComponentMod.renderToPipeableStream!(payload, clientModules, opts)
  56 | ```
  57 | 
  58 | ## ESLint Practical Rule
  59 | 
  60 | For guarded runtime `require()` blocks that need `import/no-extraneous-dependencies` suppression, prefer scoped block disable/enable. If using `eslint-disable-next-line`, the comment must be on the line immediately before the `require()` call, NOT before the `const` declaration. When the `const` and `require()` are on different lines, this is error-prone.
  61 | 
  62 | ## Turbopack Remap
  63 | 
  64 | `react-server-dom-webpack/*` is silently remapped to `react-server-dom-turbopack/*` by Turbopack's import map. Code says "webpack" everywhere, but Turbopack gets its own bindings at runtime. This affects debugging: stack traces and error messages will reference the turbopack variant.
  65 | 
  66 | ## Related Skills
  67 | 
  68 | - `$flags` - flag wiring (config/schema/define-env/runtime env)
  69 | - `$dce-edge` - DCE-safe require patterns and edge constraints
  70 | - `$runtime-debug` - reproduction and verification workflow
```


---
## .agents/skills/router-act/SKILL.md

```
   1 | ---
   2 | name: router-act
   3 | description: >
   4 |   How to write end-to-end tests using createRouterAct and LinkAccordion.
   5 |   Use when writing or modifying tests that need to control the timing of
   6 |   internal Next.js requests (like prefetches) or assert on their responses.
   7 |   Covers the act API, fixture patterns, prefetch control via LinkAccordion,
   8 |   fake clocks, and avoiding flaky testing patterns.
   9 | user-invocable: false
  10 | ---
  11 | 
  12 | # Router Act Testing
  13 | 
  14 | Use this skill when writing or modifying tests that involve prefetch requests, client router navigations, or the segment cache. The `createRouterAct` utility from `test/lib/router-act.ts` lets you assert on prefetch and navigation responses in an end-to-end way without coupling to the exact number of requests or the protocol details. This is why most client router-related tests use this pattern.
  15 | 
  16 | ## When NOT to Use `act`
  17 | 
  18 | Don't bother with `act` if you don't need to instrument the network responses — either to control their timing or to assert on what's included in them. If all you're doing is waiting for some part of the UI to appear after a navigation, regular Playwright helpers like `browser.elementById()`, `browser.elementByCss()`, and `browser.waitForElementByCss()` are sufficient.
  19 | 
  20 | ## Core Principles
  21 | 
  22 | 1. **Use `LinkAccordion` to control when prefetches happen.** Never let links be visible outside an `act` scope.
  23 | 2. **Prefer `'no-requests'`** whenever the data should be served from cache. This is the strongest assertion — it proves the cache is working.
  24 | 3. **Avoid retry/polling timers.** The `act` utility exists specifically to replace inherently flaky patterns like `retry()` loops or `setTimeout` waits for network activity. If you find yourself wanting to poll, you're probably not using `act` correctly.
  25 | 4. **Avoid the `block` feature.** It's prone to false negatives. Prefer `includes` and `'no-requests'` assertions instead.
  26 | 
  27 | ## Act API
  28 | 
  29 | ### Config Options
  30 | 
  31 | ```typescript
  32 | // Assert NO router requests are made (data served from cache).
  33 | // Prefer this whenever possible — it's the strongest assertion.
  34 | await act(async () => { ... }, 'no-requests')
  35 | 
  36 | // Expect at least one response containing this substring
  37 | await act(async () => { ... }, { includes: 'Page content' })
  38 | 
  39 | // Expect multiple responses (checked in order)
  40 | await act(async () => { ... }, [
  41 |   { includes: 'First response' },
  42 |   { includes: 'Second response' },
  43 | ])
  44 | 
  45 | // Assert the same content appears in two separate responses
  46 | await act(async () => { ... }, [
  47 |   { includes: 'Repeated content' },
  48 |   { includes: 'Repeated content' },
  49 | ])
  50 | 
  51 | // Expect at least one request, don't assert on content
  52 | await act(async () => { ... })
  53 | ```
  54 | 
  55 | ### How `includes` Matching Works
  56 | 
  57 | - The `includes` substring is matched against the HTTP response body. Use text content that appears literally in the rendered output (e.g. `'Dynamic content (stale time 60s)'`).
  58 | - Extra responses that don't match any `includes` assertion are silently ignored — you only need to assert on the responses you care about. This keeps tests decoupled from the exact number of requests the router makes.
  59 | - Each `includes` expectation claims exactly one response. If the same substring appears in N separate responses, provide N separate `{ includes: '...' }` entries.
  60 | 
  61 | ### What `act` Does Internally
  62 | 
  63 | `act` intercepts all router requests — prefetches, navigations, and Server Actions — made during the scope:
  64 | 
  65 | 1. Installs a Playwright route handler to intercept router requests
  66 | 2. Runs your scope function
  67 | 3. Waits for a `requestIdleCallback` (captures IntersectionObserver-triggered prefetches)
  68 | 4. Fulfills buffered responses to the browser
  69 | 5. Repeats steps 3-4 until no more requests arrive
  70 | 6. Asserts on the responses based on the config
  71 | 
  72 | Responses are buffered and only forwarded to the browser after the scope function returns. This means you cannot navigate to a new page and wait for it to render within the same scope — that would deadlock. Trigger the navigation (click the link) and let `act` handle the rest. Read destination page content _after_ `act` returns:
  73 | 
  74 | ```typescript
  75 | await act(
  76 |   async () => {
  77 |     /* toggle accordion, click link */
  78 |   },
  79 |   { includes: 'Page content' }
  80 | )
  81 | 
  82 | // Read content after act returns, not inside the scope
  83 | expect(await browser.elementById('my-content').text()).toBe('Page content')
  84 | ```
  85 | 
  86 | ## LinkAccordion Pattern
  87 | 
  88 | ### Why LinkAccordion Exists
  89 | 
  90 | `LinkAccordion` controls when `<Link>` components enter the DOM. A Next.js `<Link>` triggers a prefetch when it enters the viewport (via IntersectionObserver). By hiding the Link behind a checkbox toggle, you control exactly when prefetches happen — only when you explicitly toggle the accordion inside an `act` scope.
  91 | 
  92 | ```tsx
  93 | // components/link-accordion.tsx
  94 | 'use client'
  95 | import Link from 'next/link'
  96 | import { useState } from 'react'
  97 | 
  98 | export function LinkAccordion({ href, children, prefetch }) {
  99 |   const [isVisible, setIsVisible] = useState(false)
 100 |   return (
 101 |     <>
 102 |       <input
 103 |         type="checkbox"
 104 |         checked={isVisible}
 105 |         onChange={() => setIsVisible(!isVisible)}
 106 |         data-link-accordion={href}
 107 |       />
 108 |       {isVisible ? (
 109 |         <Link href={href} prefetch={prefetch}>
 110 |           {children}
 111 |         </Link>
 112 |       ) : (
 113 |         `${children} (link is hidden)`
 114 |       )}
 115 |     </>
 116 |   )
 117 | }
 118 | ```
 119 | 
 120 | ### Standard Navigation Pattern
 121 | 
 122 | Always toggle the accordion and click the link inside the same `act` scope:
 123 | 
 124 | ```typescript
 125 | await act(
 126 |   async () => {
 127 |     // 1. Toggle accordion — Link enters DOM, triggers prefetch
 128 |     const toggle = await browser.elementByCss(
 129 |       'input[data-link-accordion="/target-page"]'
 130 |     )
 131 |     await toggle.click()
 132 | 
 133 |     // 2. Click the now-visible link — triggers navigation
 134 |     const link = await browser.elementByCss('a[href="/target-page"]')
 135 |     await link.click()
 136 |   },
 137 |   { includes: 'Expected page content' }
 138 | )
 139 | ```
 140 | 
 141 | ## Common Sources of Flakiness
 142 | 
 143 | ### Using `browser.back()` with open accordions
 144 | 
 145 | Do not use `browser.back()` to return to a page where accordions were previously opened. BFCache restores the full React state including `useState` values, so previously-opened Links are immediately visible. This triggers IntersectionObserver callbacks outside any `act` scope — if the cached data is stale, uncontrolled re-prefetches fire and break subsequent `no-requests` assertions.
 146 | 
 147 | The only safe use of `browser.back()`/`browser.forward()` is when testing BFCache behavior specifically.
 148 | 
 149 | **Fix:** navigate forward to a fresh hub page instead. See [Hub Pages](#hub-pages).
 150 | 
 151 | ### Using visible `<Link>` components outside `act` scopes
 152 | 
 153 | Any `<Link>` visible in the viewport can trigger a prefetch at any time via IntersectionObserver. If this happens outside an `act` scope, the request is uncontrolled and can interfere with subsequent assertions. Always hide links behind `LinkAccordion` and only toggle them inside `act`.
 154 | 
 155 | ### Using retry/polling timers to wait for network activity
 156 | 
 157 | `retry()`, `setTimeout`, or any polling pattern to wait for prefetches or navigations to settle is inherently flaky. `act` deterministically waits for all router requests to complete before returning.
 158 | 
 159 | ### Navigating and waiting for render in the same `act` scope
 160 | 
 161 | Responses are buffered until the scope exits. Clicking a link then reading destination content in the same scope deadlocks. Read page content after `act` returns instead.
 162 | 
 163 | ## Hub Pages
 164 | 
 165 | When you need to navigate away from a page and come back to test staleness, use "hub" pages instead of `browser.back()`. Each hub is a fresh page with its own `LinkAccordion` components that start closed.
 166 | 
 167 | Hub pages use `connection()` to ensure they are dynamically rendered. This guarantees that navigating to a hub always produces a router request, which lets `act` properly manage the navigation and wait for the page to fully render before continuing.
 168 | 
 169 | **Hub page pattern:**
 170 | 
 171 | ```tsx
 172 | // app/my-test/hub-a/page.tsx
 173 | import { Suspense } from 'react'
 174 | import { connection } from 'next/server'
 175 | import { LinkAccordion } from '../../components/link-accordion'
 176 | 
 177 | async function Content() {
 178 |   await connection()
 179 |   return <div id="hub-a-content">Hub a</div>
 180 | }
 181 | 
 182 | export default function Page() {
 183 |   return (
 184 |     <>
 185 |       <Suspense fallback="Loading...">
 186 |         <Content />
 187 |       </Suspense>
 188 |       <ul>
 189 |         <li>
 190 |           <LinkAccordion href="/my-test/target-page">Target page</LinkAccordion>
 191 |         </li>
 192 |       </ul>
 193 |     </>
 194 |   )
 195 | }
 196 | ```
 197 | 
 198 | **Target pages link to hubs via LinkAccordion too:**
 199 | 
 200 | ```tsx
 201 | // On target pages, add LinkAccordion links to hub pages
 202 | <LinkAccordion href="/my-test/hub-a">Hub A</LinkAccordion>
 203 | ```
 204 | 
 205 | **Test flow:**
 206 | 
 207 | ```typescript
 208 | // 1. Navigate to target (first visit)
 209 | await act(
 210 |   async () => {
 211 |     /* toggle accordion, click link */
 212 |   },
 213 |   { includes: 'Target content' }
 214 | )
 215 | 
 216 | // 2. Navigate to hub-a (fresh page, all accordions closed)
 217 | await act(
 218 |   async () => {
 219 |     const toggle = await browser.elementByCss(
 220 |       'input[data-link-accordion="/my-test/hub-a"]'
 221 |     )
 222 |     await toggle.click()
 223 |     const link = await browser.elementByCss('a[href="/my-test/hub-a"]')
 224 |     await link.click()
 225 |   },
 226 |   { includes: 'Hub a' }
 227 | )
 228 | 
 229 | // 3. Advance time
 230 | await page.clock.setFixedTime(startDate + 60 * 1000)
 231 | 
 232 | // 4. Navigate back to target from hub (controlled prefetch)
 233 | await act(async () => {
 234 |   const toggle = await browser.elementByCss(
 235 |     'input[data-link-accordion="/my-test/target-page"]'
 236 |   )
 237 |   await toggle.click()
 238 |   const link = await browser.elementByCss('a[href="/my-test/target-page"]')
 239 |   await link.click()
 240 | }, 'no-requests') // or { includes: '...' } if data is stale
 241 | ```
 242 | 
 243 | ## Fake Clock Setup
 244 | 
 245 | Segment cache staleness tests use Playwright's clock API to control `Date.now()`:
 246 | 
 247 | ```typescript
 248 | async function startBrowserWithFakeClock(url: string) {
 249 |   let page!: Playwright.Page
 250 |   const startDate = Date.now()
 251 | 
 252 |   const browser = await next.browser(url, {
 253 |     async beforePageLoad(p: Playwright.Page) {
 254 |       page = p
 255 |       await page.clock.install()
 256 |       await page.clock.setFixedTime(startDate)
 257 |     },
 258 |   })
 259 | 
 260 |   const act = createRouterAct(page)
 261 |   return { browser, page, act, startDate }
 262 | }
 263 | ```
 264 | 
 265 | - `setFixedTime` changes `Date.now()` return value but timers still run in real time
 266 | - The segment cache uses `Date.now()` for staleness checks
 267 | - Advancing the clock doesn't trigger IntersectionObserver — only viewport changes do
 268 | - `setFixedTime` does NOT fire pending `setTimeout`/`setInterval` callbacks
 269 | 
 270 | ## Reference
 271 | 
 272 | - `createRouterAct`: `test/lib/router-act.ts`
 273 | - `LinkAccordion`: `test/e2e/app-dir/segment-cache/staleness/components/link-accordion.tsx`
 274 | - Example tests: `test/e2e/app-dir/segment-cache/staleness/`
```


---
## .agents/skills/runtime-debug/SKILL.md

```
   1 | ---
   2 | name: runtime-debug
   3 | description: >
   4 |   Debug and verification workflow for runtime-bundle and module-resolution
   5 |   regressions. Use when diagnosing unexpected module inclusions, bundle
   6 |   size regressions, or CI failures related to NEXT_SKIP_ISOLATE, nft.json
   7 |   traces, or runtime bundle selection (module.compiled.js). Covers CI env
   8 |   mirroring, full stack traces via __NEXT_SHOW_IGNORE_LISTED, route trace
   9 |   inspection, and webpack stats diffing.
  10 | ---
  11 | 
  12 | # Runtime Debug
  13 | 
  14 | Use this skill when reproducing runtime-bundle, module-resolution, or user-bundle inclusion regressions.
  15 | 
  16 | ## Local Repro Discipline
  17 | 
  18 | - Mirror CI env vars when reproducing CI failures.
  19 | - Key variables: `IS_WEBPACK_TEST=1` forces webpack (turbopack is default), `NEXT_SKIP_ISOLATE=1` skips packing next.js.
  20 | - For module-resolution validation, always rerun without `NEXT_SKIP_ISOLATE=1`.
  21 | 
  22 | ## Stack Trace Visibility
  23 | 
  24 | Set `__NEXT_SHOW_IGNORE_LISTED=true` to disable the ignore-list filtering in dev server error output. By default, Next.js collapses internal frames to `at ignore-listed frames`, which hides useful context when debugging framework internals. Defined in `packages/next/src/server/patch-error-inspect.ts`.
  25 | 
  26 | ## User-Bundle Regression Guardrail
  27 | 
  28 | When user `next build` starts bundling internal Node-only helpers unexpectedly:
  29 | 
  30 | 1. Inspect route trace artifacts (`.next/server/.../page.js.nft.json`).
  31 | 2. Inspect traced server chunks for forbidden internals (e.g. `next/dist/server/stream-utils/node-stream-helpers.js`, `node:stream/promises`).
  32 | 3. Add a `test-start-webpack` assertion that reads the route trace and traced server chunks, and fails on forbidden internals. This validates user-project bundling (not publish-time runtime bundling).
  33 | 
  34 | ## Bundle Tracing / Inclusion Proof
  35 | 
  36 | To prove what user bundling includes, emit webpack stats from the app's `next.config.js`:
  37 | 
  38 | ```js
  39 | // next.config.js
  40 | module.exports = {
  41 |   webpack(config) {
  42 |     config.profile = true
  43 |     return config
  44 |   },
  45 | }
  46 | ```
  47 | 
  48 | Then use `stats.toJson({ modules: true, chunks: true, reasons: true })` and diff `webpack-stats-server.json` between modes. This gives concrete inclusion reasons (e.g. which module required `node:stream/promises`) and is more reliable than analyzer HTML alone.
  49 | 
  50 | ## Related Skills
  51 | 
  52 | - `$flags` - flag wiring (config/schema/define-env/runtime env)
  53 | - `$dce-edge` - DCE-safe require patterns and edge constraints
  54 | - `$react-vendoring` - entry-base boundaries and vendored React
```


---
## .agents/skills/update-docs/SKILL.md

```
   1 | ---
   2 | name: update-docs
   3 | description: This skill should be used when the user asks to "update documentation for my changes", "check docs for this PR", "what docs need updating", "sync docs with code", "scaffold docs for this feature", "document this feature", "review docs completeness", "add docs for this change", "what documentation is affected", "docs impact", or mentions "docs/", "docs/01-app", "docs/02-pages", "MDX", "documentation update", "API reference", ".mdx files". Provides guided workflow for updating Next.js documentation based on code changes.
   4 | ---
   5 | 
   6 | # Next.js Documentation Updater
   7 | 
   8 | Guides you through updating Next.js documentation based on code changes on the active branch. Designed for maintainers reviewing PRs for documentation completeness.
   9 | 
  10 | ## Quick Start
  11 | 
  12 | 1. **Analyze changes**: Run `git diff canary...HEAD --stat` to see what files changed
  13 | 2. **Identify affected docs**: Map changed source files to documentation paths
  14 | 3. **Review each doc**: Walk through updates with user confirmation
  15 | 4. **Validate**: Run `pnpm lint` to check formatting
  16 | 5. **Commit**: Stage documentation changes
  17 | 
  18 | ## Workflow: Analyze Code Changes
  19 | 
  20 | ### Step 1: Get the diff
  21 | 
  22 | ```bash
  23 | # See all changed files on this branch
  24 | git diff canary...HEAD --stat
  25 | 
  26 | # See changes in specific areas
  27 | git diff canary...HEAD -- packages/next/src/
  28 | ```
  29 | 
  30 | ### Step 2: Identify documentation-relevant changes
  31 | 
  32 | Look for changes in these areas:
  33 | 
  34 | | Source Path                            | Likely Doc Impact           |
  35 | | -------------------------------------- | --------------------------- |
  36 | | `packages/next/src/client/components/` | Component API reference     |
  37 | | `packages/next/src/server/`            | Function API reference      |
  38 | | `packages/next/src/shared/lib/`        | Varies by export            |
  39 | | `packages/next/src/build/`             | Configuration or build docs |
  40 | | `packages/next/src/lib/`               | Various features            |
  41 | 
  42 | ### Step 3: Map to documentation files
  43 | 
  44 | Use the code-to-docs mapping in `references/CODE-TO-DOCS-MAPPING.md` to find corresponding documentation files.
  45 | 
  46 | Example mappings:
  47 | 
  48 | - `src/client/components/image.tsx` → `docs/01-app/03-api-reference/02-components/image.mdx`
  49 | - `src/server/config-shared.ts` → `docs/01-app/03-api-reference/05-config/`
  50 | 
  51 | ## Workflow: Update Existing Documentation
  52 | 
  53 | ### Step 1: Read the current documentation
  54 | 
  55 | Before making changes, read the existing doc to understand:
  56 | 
  57 | - Current structure and sections
  58 | - Frontmatter fields in use
  59 | - Whether it uses `<AppOnly>` / `<PagesOnly>` for router-specific content
  60 | 
  61 | ### Step 2: Identify what needs updating
  62 | 
  63 | Common updates include:
  64 | 
  65 | - **New props/options**: Add to the props table and create a section explaining usage
  66 | - **Changed behavior**: Update descriptions and examples
  67 | - **Deprecated features**: Add deprecation notices and migration guidance
  68 | - **New examples**: Add code blocks following conventions
  69 | 
  70 | ### Step 3: Apply updates with confirmation
  71 | 
  72 | For each change:
  73 | 
  74 | 1. Show the user what you plan to change
  75 | 2. Wait for confirmation before editing
  76 | 3. Apply the edit
  77 | 4. Move to the next change
  78 | 
  79 | ### Step 4: Check for shared content
  80 | 
  81 | If the doc uses the `source` field pattern (common for Pages Router docs), the source file is the one to edit. Example:
  82 | 
  83 | ```yaml
  84 | # docs/02-pages/... file with shared content
  85 | ---
  86 | source: app/building-your-application/optimizing/images
  87 | ---
  88 | ```
  89 | 
  90 | Edit the App Router source, not the Pages Router file.
  91 | 
  92 | ### Step 5: Validate changes
  93 | 
  94 | ```bash
  95 | pnpm lint          # Check formatting
  96 | pnpm prettier-fix  # Auto-fix formatting issues
  97 | ```
  98 | 
  99 | ## Workflow: Scaffold New Feature Documentation
 100 | 
 101 | Use this when adding documentation for entirely new features.
 102 | 
 103 | ### Step 1: Determine the doc type
 104 | 
 105 | | Feature Type        | Doc Location                                        | Template         |
 106 | | ------------------- | --------------------------------------------------- | ---------------- |
 107 | | New component       | `docs/01-app/03-api-reference/02-components/`       | API Reference    |
 108 | | New function        | `docs/01-app/03-api-reference/04-functions/`        | API Reference    |
 109 | | New config option   | `docs/01-app/03-api-reference/05-config/`           | Config Reference |
 110 | | New concept/guide   | `docs/01-app/02-guides/`                            | Guide            |
 111 | | New file convention | `docs/01-app/03-api-reference/03-file-conventions/` | File Convention  |
 112 | 
 113 | ### Step 2: Create the file with proper naming
 114 | 
 115 | - Use kebab-case: `my-new-feature.mdx`
 116 | - Add numeric prefix if ordering matters: `05-my-new-feature.mdx`
 117 | - Place in the correct directory based on feature type
 118 | 
 119 | ### Step 3: Use the appropriate template
 120 | 
 121 | **API Reference Template:**
 122 | 
 123 | ```mdx
 124 | ---
 125 | title: Feature Name
 126 | description: Brief description of what this feature does.
 127 | ---
 128 | 
 129 | {/* The content of this doc is shared between the app and pages router. You can use the `<PagesOnly>Content</PagesOnly>` component to add content that is specific to the Pages Router. Any shared content should not be wrapped in a component. */}
 130 | 
 131 | Brief introduction to the feature.
 132 | 
 133 | ## Reference
 134 | 
 135 | ### Props
 136 | 
 137 | <div style={{ overflowX: 'auto', width: '100%' }}>
 138 | 
 139 | | Prop                    | Example            | Type   | Status   |
 140 | | ----------------------- | ------------------ | ------ | -------- |
 141 | | [`propName`](#propname) | `propName="value"` | String | Required |
 142 | 
 143 | </div>
 144 | 
 145 | #### `propName`
 146 | 
 147 | Description of the prop.
 148 | 
 149 | \`\`\`tsx filename="app/example.tsx" switcher
 150 | // TypeScript example
 151 | \`\`\`
 152 | 
 153 | \`\`\`jsx filename="app/example.js" switcher
 154 | // JavaScript example
 155 | \`\`\`
 156 | ```
 157 | 
 158 | **Guide Template:**
 159 | 
 160 | ```mdx
 161 | ---
 162 | title: How to do X in Next.js
 163 | nav_title: X
 164 | description: Learn how to implement X in your Next.js application.
 165 | ---
 166 | 
 167 | Introduction explaining why this guide is useful.
 168 | 
 169 | ## Prerequisites
 170 | 
 171 | What the reader needs to know before starting.
 172 | 
 173 | ## Step 1: First Step
 174 | 
 175 | Explanation and code example.
 176 | 
 177 | \`\`\`tsx filename="app/example.tsx" switcher
 178 | // Code example
 179 | \`\`\`
 180 | 
 181 | ## Step 2: Second Step
 182 | 
 183 | Continue with more steps...
 184 | 
 185 | ## Next Steps
 186 | 
 187 | Related topics to explore.
 188 | ```
 189 | 
 190 | ### Step 4: Add related links
 191 | 
 192 | Update frontmatter with related documentation:
 193 | 
 194 | ```yaml
 195 | related:
 196 |   title: Next Steps
 197 |   description: Learn more about related features.
 198 |   links:
 199 |     - app/api-reference/functions/related-function
 200 |     - app/guides/related-guide
 201 | ```
 202 | 
 203 | ## Documentation Conventions
 204 | 
 205 | See `references/DOC-CONVENTIONS.md` for complete formatting rules.
 206 | 
 207 | ### Quick Reference
 208 | 
 209 | **Frontmatter (required):**
 210 | 
 211 | ```yaml
 212 | ---
 213 | title: Page Title (2-3 words)
 214 | description: One or two sentences describing the page.
 215 | ---
 216 | ```
 217 | 
 218 | **Code blocks:**
 219 | 
 220 | ```
 221 | \`\`\`tsx filename="app/page.tsx" switcher
 222 | // TypeScript first
 223 | \`\`\`
 224 | 
 225 | \`\`\`jsx filename="app/page.js" switcher
 226 | // JavaScript second
 227 | \`\`\`
 228 | ```
 229 | 
 230 | **Router-specific content:**
 231 | 
 232 | ```mdx
 233 | <AppOnly>Content only for App Router docs.</AppOnly>
 234 | 
 235 | <PagesOnly>Content only for Pages Router docs.</PagesOnly>
 236 | ```
 237 | 
 238 | **Notes:**
 239 | 
 240 | ```mdx
 241 | > **Good to know**: Single line note.
 242 | 
 243 | > **Good to know**:
 244 | >
 245 | > - Multi-line note point 1
 246 | > - Multi-line note point 2
 247 | ```
 248 | 
 249 | ## Validation Checklist
 250 | 
 251 | Before committing documentation changes:
 252 | 
 253 | - [ ] Frontmatter has `title` and `description`
 254 | - [ ] Code blocks have `filename` attribute
 255 | - [ ] TypeScript examples use `switcher` with JS variant
 256 | - [ ] Props tables are properly formatted
 257 | - [ ] Related links point to valid paths
 258 | - [ ] `pnpm lint` passes
 259 | - [ ] Changes render correctly (if preview available)
 260 | 
 261 | ## References
 262 | 
 263 | - `references/DOC-CONVENTIONS.md` - Complete frontmatter and formatting rules
 264 | - `references/CODE-TO-DOCS-MAPPING.md` - Source code to documentation mapping
```


---
## .agents/skills/v8-jit/SKILL.md

```
   1 | ---
   2 | name: v8-jit
   3 | description: >
   4 |   V8 JIT optimization patterns for writing high-performance JavaScript in
   5 |   Next.js server internals. Use when writing or reviewing hot-path code in
   6 |   app-render, stream-utils, routing, caching, or any per-request code path.
   7 |   Covers hidden classes / shapes, monomorphic call sites, inline caches,
   8 |   megamorphic deopt, closure allocation, array packing, and profiling with
   9 |   --trace-opt / --trace-deopt.
  10 | user-invocable: false
  11 | ---
  12 | 
  13 | # V8 JIT Optimization
  14 | 
  15 | Use this skill when writing or optimizing performance-critical code paths in
  16 | Next.js server internals — especially per-request hot paths like rendering,
  17 | streaming, routing, and caching.
  18 | 
  19 | ## Background: V8's Tiered Compilation
  20 | 
  21 | V8 compiles JavaScript through multiple tiers:
  22 | 
  23 | 1. **Ignition** (interpreter) — executes bytecode immediately.
  24 | 2. **Sparkplug** — fast baseline compiler (no optimization).
  25 | 3. **Maglev** — mid-tier optimizing compiler.
  26 | 4. **Turbofan** — full optimizing compiler (speculative, type-feedback-driven).
  27 | 
  28 | Code starts in Ignition and is promoted to higher tiers based on execution
  29 | frequency and collected type feedback. Turbofan produces the fastest machine
  30 | code but **bails out (deopts)** when assumptions are violated at runtime.
  31 | 
  32 | The key principle: **help V8 make correct speculative assumptions by keeping
  33 | types, shapes, and control flow predictable.**
  34 | 
  35 | ## Hidden Classes (Shapes / Maps)
  36 | 
  37 | Every JavaScript object has an internal "hidden class" (V8 calls it a _Map_,
  38 | the spec calls it a _Shape_). Objects that share the same property names, added
  39 | in the same order, share the same hidden class. This enables fast property
  40 | access via inline caches.
  41 | 
  42 | ### Initialize All Properties in Constructors
  43 | 
  44 | ```ts
  45 | // GOOD — consistent shape, single hidden class transition chain
  46 | class RequestContext {
  47 |   url: string
  48 |   method: string
  49 |   headers: Record<string, string>
  50 |   startTime: number
  51 |   cached: boolean
  52 | 
  53 |   constructor(url: string, method: string, headers: Record<string, string>) {
  54 |     this.url = url
  55 |     this.method = method
  56 |     this.headers = headers
  57 |     this.startTime = performance.now()
  58 |     this.cached = false // always initialize, even defaults
  59 |   }
  60 | }
  61 | ```
  62 | 
  63 | ```ts
  64 | // BAD — conditional property addition creates multiple hidden classes
  65 | class RequestContext {
  66 |   constructor(url, method, headers, options) {
  67 |     this.url = url
  68 |     this.method = method
  69 |     if (options.timing) {
  70 |       this.startTime = performance.now() // shape fork!
  71 |     }
  72 |     if (options.cache) {
  73 |       this.cached = false // another shape fork!
  74 |     }
  75 |     this.headers = headers
  76 |   }
  77 | }
  78 | ```
  79 | 
  80 | **Rules:**
  81 | 
  82 | - Assign every property in the constructor, in the same order, for every
  83 |   instance. Use `null` / `undefined` / `false` as default values rather than
  84 |   omitting the property.
  85 | - Prefer factory functions when constructing hot-path objects. A single factory
  86 |   makes it harder to accidentally fork shapes in different call sites.
  87 | - Never `delete` a property on a hot object — it forces a transition to
  88 |   dictionary mode (slow properties).
  89 | - Avoid adding properties after construction (`obj.newProp = x`) on objects
  90 |   used in hot paths.
  91 | - Object literals that flow into the same function should have keys in the
  92 |   same order:
  93 | - Use tuples for very small fixed-size records when names are not needed.
  94 |   Tuples avoid key-order pitfalls entirely.
  95 | 
  96 | ```ts
  97 | // GOOD — same key order, shares hidden class
  98 | const a = { type: 'static', value: 1 }
  99 | const b = { type: 'dynamic', value: 2 }
 100 | 
 101 | // BAD — different key order, different hidden classes
 102 | const a = { type: 'static', value: 1 }
 103 | const b = { value: 2, type: 'dynamic' }
 104 | ```
 105 | 
 106 | ### Real Codebase Example
 107 | 
 108 | `Span` in `src/trace/trace.ts` initializes all fields in the constructor in a
 109 | fixed order — `name`, `parentId`, `attrs`, `status`, `id`, `_start`, `now`.
 110 | This ensures all `Span` instances share one hidden class.
 111 | 
 112 | ## Monomorphic vs Polymorphic vs Megamorphic
 113 | 
 114 | V8's inline caches (ICs) track the types/shapes seen at each call site or
 115 | property access:
 116 | 
 117 | | IC State        | Shapes Seen | Speed                                 |
 118 | | --------------- | ----------- | ------------------------------------- |
 119 | | **Monomorphic** | 1           | Fastest — single direct check         |
 120 | | **Polymorphic** | 2–4         | Fast — linear search through cases    |
 121 | | **Megamorphic** | 5+          | Slow — hash-table lookup, no inlining |
 122 | 
 123 | Once an IC goes megamorphic it does NOT recover (until the function is
 124 | re-compiled). Megamorphic ICs also **prevent Turbofan from inlining** the
 125 | function.
 126 | 
 127 | ### Keep Hot Call Sites Monomorphic
 128 | 
 129 | ```ts
 130 | // GOOD — always called with the same argument shape
 131 | function processChunk(chunk: Uint8Array): void {
 132 |   // chunk is always Uint8Array → monomorphic
 133 | }
 134 | 
 135 | // BAD — called with different types at the same call site
 136 | function processChunk(chunk: Uint8Array | Buffer | string): void {
 137 |   // IC becomes polymorphic/megamorphic
 138 | }
 139 | ```
 140 | 
 141 | **Practical strategies:**
 142 | 
 143 | - Normalize inputs at the boundary (e.g. convert `Buffer` → `Uint8Array`
 144 |   once) and keep internal functions monomorphic.
 145 | - Avoid passing both `null` and `undefined` for the same parameter — pick one
 146 |   sentinel value.
 147 | - When a function must handle multiple types, split into separate specialized
 148 |   functions and dispatch once at the entry point:
 149 | 
 150 | ```ts
 151 | // Entry point dispatches once
 152 | function handleStream(stream: ReadableStream | Readable) {
 153 |   if (stream instanceof ReadableStream) {
 154 |     return handleWebStream(stream) // monomorphic call
 155 |   }
 156 |   return handleNodeStream(stream) // monomorphic call
 157 | }
 158 | ```
 159 | 
 160 | This is the pattern used in `stream-ops.ts` and throughout the stream-utils
 161 | code (Node.js vs Web stream split via compile-time switcher).
 162 | 
 163 | ## Closure and Allocation Pressure
 164 | 
 165 | Every closure captures its enclosing scope. Creating closures in hot loops
 166 | or per-request paths generates GC pressure and can prevent escape analysis.
 167 | 
 168 | ### Hoist Closures Out of Hot Paths
 169 | 
 170 | ```ts
 171 | // BAD — closure allocated for every request
 172 | function handleRequest(req) {
 173 |   stream.on('data', (chunk) => processChunk(chunk, req.id))
 174 | }
 175 | 
 176 | // GOOD — shared listener, request context looked up by stream
 177 | const requestIdByStream = new WeakMap()
 178 | function onData(chunk) {
 179 |   const id = requestIdByStream.get(this)
 180 |   if (id !== undefined) processChunk(chunk, id)
 181 | }
 182 | 
 183 | function processChunk(chunk, id) {
 184 |   /* ... */
 185 | }
 186 | 
 187 | function handleRequest(req) {
 188 |   requestIdByStream.set(stream, req.id)
 189 |   stream.on('data', onData)
 190 | }
 191 | ```
 192 | 
 193 | ```ts
 194 | // BEST — pre-allocate the callback as a method on a context object
 195 | class StreamProcessor {
 196 |   id: string
 197 |   constructor(id: string) {
 198 |     this.id = id
 199 |   }
 200 |   handleChunk(chunk: Uint8Array) {
 201 |     processChunk(chunk, this.id)
 202 |   }
 203 | }
 204 | ```
 205 | 
 206 | ### Avoid Allocations in Tight Loops
 207 | 
 208 | ```ts
 209 | // BAD — allocates a new object per iteration
 210 | for (const item of items) {
 211 |   doSomething({ key: item.key, value: item.value })
 212 | }
 213 | 
 214 | // GOOD — reuse a mutable scratch object
 215 | const scratch = { key: '', value: '' }
 216 | for (const item of items) {
 217 |   scratch.key = item.key
 218 |   scratch.value = item.value
 219 |   doSomething(scratch)
 220 | }
 221 | ```
 222 | 
 223 | ### Real Codebase Example
 224 | 
 225 | `node-stream-helpers.ts` hoists `encoder`, `BUFFER_TAGS`, and tag constants to
 226 | module scope to avoid re-creating them on every request. The `bufferIndexOf`
 227 | helper uses `Buffer.indexOf` (C++ native) instead of a per-call JS loop,
 228 | eliminating per-chunk allocation.
 229 | 
 230 | ## Array Optimizations
 231 | 
 232 | V8 tracks array "element kinds" — an internal type tag that determines how
 233 | elements are stored in memory:
 234 | 
 235 | | Element Kind      | Description                   | Speed                       |
 236 | | ----------------- | ----------------------------- | --------------------------- |
 237 | | `PACKED_SMI`      | Small integers only, no holes | Fastest                     |
 238 | | `PACKED_DOUBLE`   | Numbers only, no holes        | Fast                        |
 239 | | `PACKED_ELEMENTS` | Mixed/objects, no holes       | Moderate                    |
 240 | | `HOLEY_*`         | Any of above with holes       | Slower (extra bounds check) |
 241 | 
 242 | **Transitions are one-way** — once an array becomes `HOLEY` or `PACKED_ELEMENTS`,
 243 | it never goes back.
 244 | 
 245 | ### Rules
 246 | 
 247 | - Pre-allocate arrays with known size: `new Array(n)` creates a holey array.
 248 |   Prefer `[]` and `push()`, or use `Array.from({ length: n }, initFn)`.
 249 | - Don't create holes: `arr[100] = x` on an empty array creates 100 holes.
 250 | - Don't mix types: `[1, 'two', {}]` immediately becomes `PACKED_ELEMENTS`.
 251 | - Prefer typed arrays only when you need binary interop/contiguous memory or
 252 |   have profiling evidence that they help. For small/short-lived collections,
 253 |   normal arrays can be faster and allocate less.
 254 | 
 255 | ```ts
 256 | // GOOD — packed SMI array
 257 | const indices: number[] = []
 258 | for (let i = 0; i < n; i++) {
 259 |   indices.push(i)
 260 | }
 261 | 
 262 | // BAD — holey from the start
 263 | const indices = new Array(n)
 264 | for (let i = 0; i < n; i++) {
 265 |   indices[i] = i
 266 | }
 267 | ```
 268 | 
 269 | ### Real Codebase Example
 270 | 
 271 | `accumulateStreamChunks` in `app-render.tsx` uses `const staticChunks: Array<Uint8Array> = []` with `push()` — keeping a packed array of a single type
 272 | throughout its lifetime.
 273 | 
 274 | ## Function Optimization and Deopts
 275 | 
 276 | ### Hot-Path Deopt Footguns
 277 | 
 278 | - **`arguments` object**: using `arguments` in non-trivial ways (e.g.
 279 |   `arguments[i]` with variable `i`, leaking `arguments`). Use rest params
 280 |   instead.
 281 | - **Type instability at one call site**: same operation sees both numbers and
 282 |   strings (or many object shapes) and becomes polymorphic/megamorphic.
 283 | - **`eval` / `with`**: prevents optimization entirely.
 284 | - **Highly dynamic object iteration**: avoid `for...in` on hot objects; prefer
 285 |   `Object.keys()` / `Object.entries()` when possible.
 286 | 
 287 | ### Favor Predictable Control Flow
 288 | 
 289 | ```ts
 290 | // GOOD — predictable: always returns same type
 291 | function getStatus(code: number): string {
 292 |   if (code === 200) return 'ok'
 293 |   if (code === 404) return 'not found'
 294 |   return 'error'
 295 | }
 296 | 
 297 | // BAD — returns different types
 298 | function getStatus(code: number): string | null | undefined {
 299 |   if (code === 200) return 'ok'
 300 |   if (code === 404) return null
 301 |   // implicitly returns undefined
 302 | }
 303 | ```
 304 | 
 305 | ### Watch Shape Diversity in `switch` Dispatch
 306 | 
 307 | ```ts
 308 | // WATCH OUT — `node.type` IC can go megamorphic if many shapes hit one site
 309 | function render(node) {
 310 |   switch (node.type) {
 311 |     case 'div':
 312 |       return { tag: 'div', children: node.children }
 313 |     case 'span':
 314 |       return { tag: 'span', text: node.text }
 315 |     case 'img':
 316 |       return { src: node.src, alt: node.alt }
 317 |     // Many distinct node layouts can make this dispatch site polymorphic
 318 |   }
 319 | }
 320 | ```
 321 | 
 322 | This pattern is not always bad. Often the main pressure is at the shared
 323 | dispatch site (`node.type`), while properties used only in one branch stay
 324 | monomorphic within that branch. Reach for normalization/splitting only when
 325 | profiles show this site is hot and polymorphic.
 326 | 
 327 | ## String Operations
 328 | 
 329 | - **String concatenation in loops is usually fine in modern V8** (ropes make
 330 |   many concatenations cheap). For binary data, use `Buffer.concat()`.
 331 | - **Template literals vs concatenation**: equivalent performance in modern V8,
 332 |   but template literals are clearer.
 333 | - **`string.indexOf()` > regex** for simple substring checks.
 334 | - **Reuse RegExp objects**: don't create a `new RegExp()` inside a hot
 335 |   function — hoist it to module scope.
 336 | 
 337 | ```ts
 338 | // GOOD — regex hoisted to module scope
 339 | const ROUTE_PATTERN = /^\/api\//
 340 | 
 341 | function isApiRoute(path: string): boolean {
 342 |   return ROUTE_PATTERN.test(path)
 343 | }
 344 | 
 345 | // BAD — regex recreated on every call
 346 | function isApiRoute(path: string): boolean {
 347 |   return /^\/api\//.test(path) // V8 may or may not cache this
 348 | }
 349 | ```
 350 | 
 351 | ## `Map` and `Set` vs Plain Objects
 352 | 
 353 | - **`Map`** is faster than plain objects for frequent additions/deletions
 354 |   (avoids hidden class transitions and dictionary mode).
 355 | - **`Set`** is faster than `obj[key] = true` for membership checks with
 356 |   dynamic keys.
 357 | - For **static lookups** (known keys at module load), plain objects or
 358 |   `Object.freeze({...})` are fine — V8 optimizes them as constant.
 359 | - Never use an object as a map if keys come from user input (prototype
 360 |   pollution risk + megamorphic shapes).
 361 | 
 362 | ## Profiling and Verification
 363 | 
 364 | ### V8 Flags for Diagnosing JIT Issues
 365 | 
 366 | ```bash
 367 | # Trace which functions get optimized
 368 | node --trace-opt server.js 2>&1 | grep "my-function-name"
 369 | 
 370 | # Trace deoptimizations (critical for finding perf regressions)
 371 | node --trace-deopt server.js 2>&1 | grep "my-function-name"
 372 | 
 373 | # Combined: see the full opt/deopt lifecycle
 374 | node --trace-opt --trace-deopt server.js 2>&1 | tee /tmp/v8-trace.log
 375 | 
 376 | # Show IC state transitions (verbose)
 377 | node --trace-ic server.js 2>&1 | tee /tmp/ic-trace.log
 378 | 
 379 | # Print optimized code (advanced)
 380 | node --print-opt-code --code-comments server.js
 381 | ```
 382 | 
 383 | ### Targeted Profiling in Next.js
 384 | 
 385 | ```bash
 386 | # Profile a production build
 387 | node --cpu-prof --cpu-prof-dir=/tmp/profiles \
 388 |   node_modules/.bin/next build
 389 | 
 390 | # Profile the server during a benchmark
 391 | node --cpu-prof --cpu-prof-dir=/tmp/profiles \
 392 |   node_modules/.bin/next start &
 393 | # ... run benchmark ...
 394 | # Analyze in Chrome DevTools: chrome://inspect → Open dedicated DevTools
 395 | 
 396 | # Quick trace-deopt check on a specific test
 397 | node --trace-deopt $(which jest) --runInBand test/path/to/test.ts \
 398 |   2>&1 | grep -i "deopt" | head -50
 399 | ```
 400 | 
 401 | ### Using `%` Natives (Development/Testing Only)
 402 | 
 403 | With `--allow-natives-syntax`:
 404 | 
 405 | ```js
 406 | function hotFunction(x) {
 407 |   return x + 1
 408 | }
 409 | 
 410 | // Force optimization
 411 | %PrepareFunctionForOptimization(hotFunction)
 412 | hotFunction(1)
 413 | hotFunction(2) % OptimizeFunctionOnNextCall(hotFunction)
 414 | hotFunction(3)
 415 | 
 416 | // Check optimization status
 417 | // 1 = optimized, 2 = not optimized, 3 = always optimized, 6 = maglev
 418 | console.log(%GetOptimizationStatus(hotFunction))
 419 | ```
 420 | 
 421 | ## Checklist for Hot Path Code Reviews
 422 | 
 423 | - [ ] All object properties initialized in constructor/literal, same order
 424 | - [ ] No `delete` on hot objects
 425 | - [ ] No post-construction property additions on hot objects
 426 | - [ ] Functions receive consistent types (monomorphic call sites)
 427 | - [ ] Type dispatch happens at boundaries, not deep in hot loops
 428 | - [ ] No closures allocated inside tight loops
 429 | - [ ] Module-scope constants for regex, encoders, tag buffers
 430 | - [ ] Arrays are packed (no holes, no mixed types)
 431 | - [ ] `Map`/`Set` used for dynamic key collections
 432 | - [ ] No `arguments` object — use rest params
 433 | - [ ] `try/catch` at function boundary, not inside tight loops
 434 | - [ ] String building via array + `join()` or `Buffer.concat()`
 435 | - [ ] Return types are consistent (no `string | null | undefined` mixes)
 436 | 
 437 | ## Related Skills
 438 | 
 439 | - `$dce-edge` — DCE-safe require patterns (compile-time dead code)
 440 | - `$runtime-debug` — runtime bundle debugging and profiling workflow
```


---
## .agents/skills/write-api-reference/SKILL.md

```
   1 | ---
   2 | name: write-api-reference
   3 | description: |
   4 |   Produces API reference documentation for Next.js APIs: functions, components, file conventions, directives, and config options.
   5 | 
   6 |   **Auto-activation:** User asks to write, create, or draft an API reference page. Also triggers on paths like `docs/01-app/03-api-reference/`, or keywords like "API reference", "props", "parameters", "returns", "signature".
   7 | 
   8 |   **Input sources:** Next.js source code, existing API reference pages, or user-provided specifications.
   9 | 
  10 |   **Output type:** A markdown (.mdx) API reference page with YAML frontmatter, usage example, reference section, behavior notes, and examples.
  11 | agent: Plan
  12 | context: fork
  13 | ---
  14 | 
  15 | # Writing API Reference Pages
  16 | 
  17 | ## Goal
  18 | 
  19 | Produce an API reference page that documents a single API surface (function, component, file convention, directive, or config option). The page should be concise, scannable, and example-driven.
  20 | 
  21 | Each page documents **one API**. If the API has sub-methods (like `cookies.set()`), document them on the same page. If two APIs are independent, they get separate pages.
  22 | 
  23 | ## Structure
  24 | 
  25 | Identify which category the API belongs to, then follow the corresponding template.
  26 | 
  27 | ### Categories
  28 | 
  29 | 1. **Function** (`cookies`, `fetch`, `generateStaticParams`): signature, params/returns, methods table, examples
  30 | 2. **Component** (`Link`, `Image`, `Script`): props summary table, individual prop docs, examples
  31 | 3. **File convention** (`page`, `layout`, `route`): definition, code showing the convention, props, behavior, examples
  32 | 4. **Directive** (`use client`, `use cache`): definition, usage, serialization/boundary rules, reference
  33 | 5. **Config option** (`basePath`, `images`, etc.): definition, config code, behavioral sections
  34 | 
  35 | ### Template
  36 | 
  37 | ````markdown
  38 | ---
  39 | title: {API name}
  40 | description: {API Reference for the {API name} {function|component|file convention|directive|config option}.}
  41 | ---
  42 | 
  43 | {One sentence defining what it does and where it's used.}
  44 | 
  45 | ```tsx filename="path/to/file.tsx" switcher
  46 | // Minimal working usage
  47 | ```
  48 | 
  49 | ```jsx filename="path/to/file.js" switcher
  50 | // Same example in JS
  51 | ```
  52 | 
  53 | ## Reference
  54 | 
  55 | {For functions: methods/params table, return type.}
  56 | {For components: props summary table, then `#### propName` subsections.}
  57 | {For file conventions: `### Props` with `#### propName` subsections.}
  58 | {For directives: usage rules and serialization constraints.}
  59 | {For config: options table or individual option docs.}
  60 | 
  61 | ### {Subsection name}
  62 | 
  63 | {Description + code example + table of values where applicable.}
  64 | 
  65 | ## Good to know
  66 | 
  67 | - {Default behavior or implicit effects.}
  68 | - {Caveats, limitations, or version-specific notes.}
  69 | - {Edge cases the developer should be aware of.}
  70 | 
  71 | ## Examples
  72 | 
  73 | ### {Example name}
  74 | 
  75 | {Brief context, 1-2 sentences.}
  76 | 
  77 | ```tsx filename="path/to/file.tsx" switcher
  78 | // Complete working example
  79 | ```
  80 | 
  81 | ```jsx filename="path/to/file.js" switcher
  82 | // Same example in JS
  83 | ```
  84 | 
  85 | ## Version History
  86 | 
  87 | | Version  | Changes         |
  88 | | -------- | --------------- |
  89 | | `vX.Y.Z` | {What changed.} |
  90 | ````
  91 | 
  92 | **Category-specific notes:**
  93 | 
  94 | - **Functions**: Lead with the function signature and `await` if async. Document methods in a table if the return value has methods (like `cookies`). Document options in a separate table if applicable.
  95 | - **Components**: Start with a props summary table (`| Prop | Example | Type | Required |`). Then document each prop under `#### propName` with description, code example, and value table where useful.
  96 | - **File conventions**: Show the default export signature with TypeScript types. Document each prop (`params`, `searchParams`, etc.) under `#### propName` with a route/URL/value example table.
  97 | - **Directives**: No `## Reference` section. Use `## Usage` instead, showing correct placement. Document serialization constraints and boundary rules.
  98 | - **Config options**: Show the `next.config.ts` snippet. Use subsections for each behavioral aspect.
  99 | 
 100 | ## Rules
 101 | 
 102 | 1. **Lead with what it does.** First sentence defines the API. No preamble.
 103 | 2. **Show working code immediately.** A minimal usage example appears right after the opening sentence, before `## Reference`.
 104 | 3. **Use `switcher` for tsx/jsx pairs.** Always include both. Always include `filename="path/to/file.ext"`.
 105 | 4. **Use `highlight={n}` for key lines.** Highlight the line that demonstrates the API being documented.
 106 | 5. **Tables for simple APIs, subsections for complex ones.** If a prop/param needs only a type and one-line description, use a table row. If it needs a code example or multiple values, use a `####` subsection.
 107 | 6. **Behavior section uses `> **Good to know**:`or`## Good to know`.** Use the blockquote format for brief notes (1-3 bullets). Use the heading format for longer sections. Not "Note:" or "Warning:".
 108 | 7. **Examples section uses `### Example Name` subsections.** Each example solves one specific use case.
 109 | 8. **Version History table at the end.** Include when the API has changed across versions. Omit for new APIs.
 110 | 9. **No em dashes.** Use periods, commas, or parentheses instead.
 111 | 10. **Mechanical, observable language.** Describe what happens, not how it feels. "Returns an object" not "gives you an object".
 112 | 11. **Link to related docs with relative paths.** Use `/docs/app/...` format.
 113 | 12. **No selling or justifying.** No "powerful", "easily", "simply". State what the API does.
 114 | 
 115 | | Don't                                                   | Do                                                                                          |
 116 | | ------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
 117 | | "This powerful function lets you easily manage cookies" | "`cookies` is an async function that reads HTTP request cookies in Server Components"       |
 118 | | "You can conveniently access..."                        | "Returns an object containing..."                                                           |
 119 | | "The best way to handle navigation"                     | "`<Link>` extends the HTML `<a>` element to provide prefetching and client-side navigation" |
 120 | 
 121 | ## Workflow
 122 | 
 123 | 1. **Ask for reference material.** Ask the user if they have any RFCs, PRs, design docs, or other context that should inform the doc.
 124 | 2. **Identify the API category** (function, component, file convention, directive, config).
 125 | 3. **Research the implementation.** Read the source code to understand params, return types, edge cases, and defaults.
 126 | 4. **Check e2e tests.** Search `test/` for tests exercising the API to find real usage patterns, edge cases, and expected behavior.
 127 | 5. **Check existing related docs** for linking opportunities and to avoid duplication.
 128 | 6. **Write using the appropriate category template.** Follow the rules above.
 129 | 7. **Review against the rules.** Verify: one sentence opener, immediate code example, correct `switcher`/`filename` usage, tables vs subsections, "Good to know" format, no em dashes, mechanical language.
 130 | 
 131 | ## References
 132 | 
 133 | Read these pages in `docs/01-app/03-api-reference/` before writing. They demonstrate the patterns above.
 134 | 
 135 | - `04-functions/cookies.mdx` - Function with methods table, options table, and behavior notes
 136 | - `03-file-conventions/page.mdx` - File convention with props subsections and route/URL/value tables
 137 | - `02-components/link.mdx` - Component with props summary table and detailed per-prop docs
 138 | - `01-directives/use-client.mdx` - Directive with usage section and serialization rules
 139 | - `04-functions/fetch.mdx` - Function with troubleshooting section and version history
```


---
## .agents/skills/write-guide/SKILL.md

```
   1 | ---
   2 | name: write-guide
   3 | description: |
   4 |   Generates technical guides that teach real-world use cases through progressive examples.
   5 | 
   6 |   **Auto-activation:** User asks to write, create, or draft a guide or tutorial. Also use when converting feature documentation, API references, or skill knowledge into step-by-step learning content.
   7 | 
   8 |   **Input sources:** Feature skills, API documentation, existing code examples, or user-provided specifications.
   9 | 
  10 |   **Output type:** A markdown guide with YAML frontmatter, introduction, 2-4 progressive steps, and next steps section.
  11 | agent: Plan
  12 | context: fork
  13 | ---
  14 | 
  15 | # Writing Guides
  16 | 
  17 | ## Goal
  18 | 
  19 | Produce a technical guide that teaches a real-world use case through progressive examples. Concepts are introduced only when the reader needs them.
  20 | 
  21 | Each guide solves **one specific problem**. Not a category of problems. If the outline has 5+ steps or covers multiple approaches, split it.
  22 | 
  23 | ## Structure
  24 | 
  25 | Every guide follows this arc: introduction, example setup, 2-5 progressive steps, next steps.
  26 | 
  27 | Each step follows this loop: working code → new requirement → friction → explanation → resolution → observable proof.
  28 | 
  29 | Sections: introduction (no heading, 2 paragraphs max), `## Example` (what we're building + source link), `### Step N` (action-oriented titles, 2-4 steps), `## Next steps` (summary + related links).
  30 | 
  31 | Headings should tell a story on their own. If readers only saw the headings, they'd understand the guide's takeaway.
  32 | 
  33 | ### Template
  34 | 
  35 | ````markdown
  36 | ---
  37 | title: {Action-oriented, e.g., "Building X" or "How to Y"}
  38 | description: {One sentence}
  39 | nav_title: {Short title for navigation}
  40 | ---
  41 | 
  42 | {What the reader will accomplish and why it matters. The friction and how this approach resolves it. 2 paragraphs max.}
  43 | 
  44 | ## Example
  45 | 
  46 | As an example, we'll build {what we're building}.
  47 | 
  48 | We'll start with {step 1}, then {step 2}, and {step 3}.
  49 | 
  50 | {Source code link.}
  51 | 
  52 | ### Step 1: {Action-oriented title}
  53 | 
  54 | {Brief context, 1-2 sentences.}
  55 | 
  56 | ```tsx filename="path/to/file.tsx"
  57 | // Minimal working code
  58 | ```
  59 | 
  60 | {Explain what happens.}
  61 | 
  62 | {Introduce friction: warning, limitation, or constraint.}
  63 | 
  64 | {Resolution: explain the choice, apply the fix.}
  65 | 
  66 | {Verify the fix with observable proof.}
  67 | 
  68 | ### Step 2: {Action-oriented title}
  69 | 
  70 | {Same pattern: context → code → explain → friction → resolution → proof.}
  71 | 
  72 | ### Step 3: {Action-oriented title}
  73 | 
  74 | {Same pattern.}
  75 | 
  76 | ## Next steps
  77 | 
  78 | You now know how to {summary}.
  79 | 
  80 | Next, learn how to:
  81 | 
  82 | - [Related guide 1]()
  83 | - [Related guide 2]()
  84 | ````
  85 | 
  86 | ### Workflow
  87 | 
  88 | 1. **Research**: Check available skills for relevant features. Read existing docs for context and linking opportunities.
  89 | 2. **Plan**: Outline sections. Verify scope (one problem, 2-4 steps). Each step needs a friction point and resolution.
  90 | 3. **Write**: Follow the template above. Apply the rules below.
  91 | 4. **Review**: Re-read the rules, verify, then present.
  92 | 
  93 | ## Rules
  94 | 
  95 | 1. **Progressive disclosure.** Start with the smallest working example. Introduce complexity only when the example breaks. Name concepts at the moment of resolution, after the reader has felt the problem. Full loop: working → new requirement → something breaks → explain why → name the fix → apply → verify with proof → move on.
  96 | 2. **Show problems visually.** Console errors, terminal output, build warnings, slow-loading pages. "If we refresh the page, we can see the component blocks the response."
  97 | 3. **Verify resolutions with observable proof.** Before/after comparisons, browser reloads, terminal output. "If we refresh the page again, we can see it loads instantly."
  98 | 4. **One friction point per step.** If a step has multiple friction points, split it.
  99 | 5. **Minimal code blocks.** Only the code needed for the current step. Collapse unchanged functions with `function Header() {}`.
 100 | 6. **No em dashes.** Use periods, commas, or parentheses instead.
 101 | 7. **Mechanical, observable language.** Describe what happens, not how it feels.
 102 | 8. **No selling, justifying, or comparing.** No "the best way," no historical context, no framework comparisons.
 103 | 
 104 | | Don't                                                | Do                                                       |
 105 | | ---------------------------------------------------- | -------------------------------------------------------- |
 106 | | "creates friction in the pipeline"                   | "blocks the response"                                    |
 107 | | "needs dynamic information"                          | "depends on request-time data"                           |
 108 | | "requires dynamic processing"                        | "output can't be known ahead of time"                    |
 109 | | "The component blocks the response — causing delays" | "The component blocks the response. This causes delays." |
 110 | 
 111 | ## References
 112 | 
 113 | Read these guides in `docs/01-app/02-guides/` before writing. They demonstrate the patterns above.
 114 | 
 115 | - `public-static-pages.mdx` — intro → example → 3 progressive steps → next steps. Concepts named at point of resolution. Problems shown with build output.
 116 | - `forms.mdx` — progressive feature building without explicit "Step" labels. Each section adds one capability.
```


---
## .claude-plugin/plugins/cache-components/skills/cache-components/SKILL.md

```
   1 | ---
   2 | name: cache-components
   3 | description: |
   4 |   Expert guidance for Next.js Cache Components and Partial Prerendering (PPR).
   5 | 
   6 |   **PROACTIVE ACTIVATION**: Use this skill automatically when working in Next.js projects that have `cacheComponents: true` in their next.config.ts/next.config.js. When this config is detected, proactively apply Cache Components patterns and best practices to all React Server Component implementations.
   7 | 
   8 |   **DETECTION**: At the start of a session in a Next.js project, check for `cacheComponents: true` in next.config. If enabled, this skill's patterns should guide all component authoring, data fetching, and caching decisions.
   9 | 
  10 |   **USE CASES**: Implementing 'use cache' directive, configuring cache lifetimes with cacheLife(), tagging cached data with cacheTag(), invalidating caches with updateTag()/revalidateTag(), optimizing static vs dynamic content boundaries, debugging cache issues, and reviewing Cache Component implementations.
  11 | ---
  12 | 
  13 | # Next.js Cache Components
  14 | 
  15 | > **Auto-activation**: This skill activates automatically in projects with `cacheComponents: true` in next.config.
  16 | 
  17 | ## Project Detection
  18 | 
  19 | When starting work in a Next.js project, check if Cache Components are enabled:
  20 | 
  21 | ```bash
  22 | # Check next.config.ts or next.config.js for cacheComponents
  23 | grep -r "cacheComponents" next.config.* 2>/dev/null
  24 | ```
  25 | 
  26 | If `cacheComponents: true` is found, apply this skill's patterns proactively when:
  27 | 
  28 | - Writing React Server Components
  29 | - Implementing data fetching
  30 | - Creating Server Actions with mutations
  31 | - Optimizing page performance
  32 | - Reviewing existing component code
  33 | 
  34 | Cache Components enable **Partial Prerendering (PPR)** - mixing static HTML shells with dynamic streaming content for optimal performance.
  35 | 
  36 | ## Philosophy: Code Over Configuration
  37 | 
  38 | Cache Components represents a shift from **segment configuration** to **compositional code**:
  39 | 
  40 | | Before (Deprecated)                     | After (Cache Components)                  |
  41 | | --------------------------------------- | ----------------------------------------- |
  42 | | `export const revalidate = 3600`        | `cacheLife('hours')` inside `'use cache'` |
  43 | | `export const dynamic = 'force-static'` | Use `'use cache'` and Suspense boundaries |
  44 | | All-or-nothing static/dynamic           | Granular: static shell + cached + dynamic |
  45 | 
  46 | **Key Principle**: Components co-locate their caching, not just their data. Next.js provides build-time feedback to guide you toward optimal patterns.
  47 | 
  48 | ## Core Concept
  49 | 
  50 | ```
  51 | ┌─────────────────────────────────────────────────────┐
  52 | │                   Static Shell                       │
  53 | │  (Sent immediately to browser)                       │
  54 | │                                                      │
  55 | │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
  56 | │  │   Header    │  │  Cached     │  │  Suspense   │  │
  57 | │  │  (static)   │  │  Content    │  │  Fallback   │  │
  58 | │  └─────────────┘  └─────────────┘  └──────┬──────┘  │
  59 | │                                           │         │
  60 | │                                    ┌──────▼──────┐  │
  61 | │                                    │  Dynamic    │  │
  62 | │                                    │  (streams)  │  │
  63 | │                                    └─────────────┘  │
  64 | └─────────────────────────────────────────────────────┘
  65 | ```
  66 | 
  67 | ## Mental Model: The Caching Decision Tree
  68 | 
  69 | When writing a React Server Component, ask these questions in order:
  70 | 
  71 | ```
  72 | ┌─────────────────────────────────────────────────────────┐
  73 | │ Does this component fetch data or perform I/O?          │
  74 | └─────────────────────┬───────────────────────────────────┘
  75 |                       │
  76 |            ┌──────────▼──────────┐
  77 |            │   YES               │ NO → Pure component, no action needed
  78 |            └──────────┬──────────┘
  79 |                       │
  80 |     ┌─────────────────▼─────────────────┐
  81 |     │ Does it depend on request context? │
  82 |     │ (cookies, headers, searchParams)   │
  83 |     └─────────────────┬─────────────────┘
  84 |                       │
  85 |          ┌────────────┴────────────┐
  86 |          │                         │
  87 |     ┌────▼────┐              ┌─────▼─────┐
  88 |     │   YES   │              │    NO     │
  89 |     └────┬────┘              └─────┬─────┘
  90 |          │                         │
  91 |          │                   ┌─────▼─────────────────┐
  92 |          │                   │ Can this be cached?   │
  93 |          │                   │ (same for all users?) │
  94 |          │                   └─────┬─────────────────┘
  95 |          │                         │
  96 |          │              ┌──────────┴──────────┐
  97 |          │              │                     │
  98 |          │         ┌────▼────┐          ┌─────▼─────┐
  99 |          │         │   YES   │          │    NO     │
 100 |          │         └────┬────┘          └─────┬─────┘
 101 |          │              │                     │
 102 |          │              ▼                     │
 103 |          │         'use cache'                │
 104 |          │         + cacheTag()               │
 105 |          │         + cacheLife()              │
 106 |          │                                    │
 107 |          └──────────────┬─────────────────────┘
 108 |                         │
 109 |                         ▼
 110 |               Wrap in <Suspense>
 111 |               (dynamic streaming)
 112 | ```
 113 | 
 114 | **Key insight**: The `'use cache'` directive is for data that's the _same across users_. User-specific data stays dynamic with Suspense.
 115 | 
 116 | ## Quick Start
 117 | 
 118 | ### Enable Cache Components
 119 | 
 120 | ```typescript
 121 | // next.config.ts
 122 | import type { NextConfig } from 'next'
 123 | 
 124 | const nextConfig: NextConfig = {
 125 |   cacheComponents: true,
 126 | }
 127 | 
 128 | export default nextConfig
 129 | ```
 130 | 
 131 | ### Basic Usage
 132 | 
 133 | ```tsx
 134 | // Cached component - output included in static shell
 135 | async function CachedPosts() {
 136 |   'use cache'
 137 |   const posts = await db.posts.findMany()
 138 |   return <PostList posts={posts} />
 139 | }
 140 | 
 141 | // Page with static + cached + dynamic content
 142 | export default async function BlogPage() {
 143 |   return (
 144 |     <>
 145 |       <Header /> {/* Static */}
 146 |       <CachedPosts /> {/* Cached */}
 147 |       <Suspense fallback={<Skeleton />}>
 148 |         <DynamicComments /> {/* Dynamic - streams */}
 149 |       </Suspense>
 150 |     </>
 151 |   )
 152 | }
 153 | ```
 154 | 
 155 | ## Core APIs
 156 | 
 157 | ### 1. `'use cache'` Directive
 158 | 
 159 | Marks code as cacheable. Can be applied at three levels:
 160 | 
 161 | ```tsx
 162 | // File-level: All exports are cached
 163 | 'use cache'
 164 | export async function getData() {
 165 |   /* ... */
 166 | }
 167 | export async function Component() {
 168 |   /* ... */
 169 | }
 170 | 
 171 | // Component-level
 172 | async function UserCard({ id }: { id: string }) {
 173 |   'use cache'
 174 |   const user = await fetchUser(id)
 175 |   return <Card>{user.name}</Card>
 176 | }
 177 | 
 178 | // Function-level
 179 | async function fetchWithCache(url: string) {
 180 |   'use cache'
 181 |   return fetch(url).then((r) => r.json())
 182 | }
 183 | ```
 184 | 
 185 | **Important**: All cached functions must be `async`.
 186 | 
 187 | ### 2. `cacheLife()` - Control Cache Duration
 188 | 
 189 | ```tsx
 190 | import { cacheLife } from 'next/cache'
 191 | 
 192 | async function Posts() {
 193 |   'use cache'
 194 |   cacheLife('hours') // Use a predefined profile
 195 | 
 196 |   // Or custom configuration:
 197 |   cacheLife({
 198 |     stale: 60, // 1 min - client cache validity
 199 |     revalidate: 3600, // 1 hr - start background refresh
 200 |     expire: 86400, // 1 day - absolute expiration
 201 |   })
 202 | 
 203 |   return await db.posts.findMany()
 204 | }
 205 | ```
 206 | 
 207 | **Predefined profiles**: `'default'`, `'seconds'`, `'minutes'`, `'hours'`, `'days'`, `'weeks'`, `'max'`
 208 | 
 209 | ### 3. `cacheTag()` - Tag for Invalidation
 210 | 
 211 | ```tsx
 212 | import { cacheTag } from 'next/cache'
 213 | 
 214 | async function BlogPosts() {
 215 |   'use cache'
 216 |   cacheTag('posts')
 217 |   cacheLife('days')
 218 | 
 219 |   return await db.posts.findMany()
 220 | }
 221 | 
 222 | async function UserProfile({ userId }: { userId: string }) {
 223 |   'use cache'
 224 |   cacheTag('users', `user-${userId}`) // Multiple tags
 225 | 
 226 |   return await db.users.findUnique({ where: { id: userId } })
 227 | }
 228 | ```
 229 | 
 230 | ### 4. `updateTag()` - Immediate Invalidation
 231 | 
 232 | For **read-your-own-writes** semantics:
 233 | 
 234 | ```tsx
 235 | 'use server'
 236 | import { updateTag } from 'next/cache'
 237 | 
 238 | export async function createPost(formData: FormData) {
 239 |   await db.posts.create({ data: formData })
 240 | 
 241 |   updateTag('posts') // Client immediately sees fresh data
 242 | }
 243 | ```
 244 | 
 245 | ### 5. `revalidateTag()` - Background Revalidation
 246 | 
 247 | For stale-while-revalidate pattern:
 248 | 
 249 | ```tsx
 250 | 'use server'
 251 | import { revalidateTag } from 'next/cache'
 252 | 
 253 | export async function updatePost(id: string, data: FormData) {
 254 |   await db.posts.update({ where: { id }, data })
 255 | 
 256 |   revalidateTag('posts', 'max') // Serve stale, refresh in background
 257 | }
 258 | ```
 259 | 
 260 | ## When to Use Each Pattern
 261 | 
 262 | | Content Type | API                 | Behavior                              |
 263 | | ------------ | ------------------- | ------------------------------------- |
 264 | | **Static**   | No directive        | Rendered at build time                |
 265 | | **Cached**   | `'use cache'`       | Included in static shell, revalidates |
 266 | | **Dynamic**  | Inside `<Suspense>` | Streams at request time               |
 267 | 
 268 | ## Parameter Permutations & Subshells
 269 | 
 270 | **Critical Concept**: With Cache Components, Next.js renders ALL permutations of provided parameters to create reusable subshells.
 271 | 
 272 | ```tsx
 273 | // app/products/[category]/[slug]/page.tsx
 274 | export async function generateStaticParams() {
 275 |   return [
 276 |     { category: 'jackets', slug: 'classic-bomber' },
 277 |     { category: 'jackets', slug: 'essential-windbreaker' },
 278 |     { category: 'accessories', slug: 'thermal-fleece-gloves' },
 279 |   ]
 280 | }
 281 | ```
 282 | 
 283 | Next.js renders these routes:
 284 | 
 285 | ```
 286 | /products/jackets/classic-bomber        ← Full params (complete page)
 287 | /products/jackets/essential-windbreaker ← Full params (complete page)
 288 | /products/accessories/thermal-fleece-gloves ← Full params (complete page)
 289 | /products/jackets/[slug]                ← Partial params (category subshell)
 290 | /products/accessories/[slug]            ← Partial params (category subshell)
 291 | /products/[category]/[slug]             ← No params (fallback shell)
 292 | ```
 293 | 
 294 | **Why this matters**: The category subshell (`/products/jackets/[slug]`) can be reused for ANY jacket product, even ones not in `generateStaticParams`. Users navigating to an unlisted jacket get the cached category shell immediately, with product details streaming in.
 295 | 
 296 | ### `generateStaticParams` Requirements
 297 | 
 298 | With Cache Components enabled:
 299 | 
 300 | 1. **Must provide at least one parameter** - Empty arrays now cause build errors (prevents silent production failures)
 301 | 2. **Params prove static safety** - Providing params lets Next.js verify no dynamic APIs are called
 302 | 3. **Partial params create subshells** - Each unique permutation generates a reusable shell
 303 | 
 304 | ```tsx
 305 | // ❌ ERROR with Cache Components
 306 | export function generateStaticParams() {
 307 |   return [] // Build error: must provide at least one param
 308 | }
 309 | 
 310 | // ✅ CORRECT: Provide real params
 311 | export async function generateStaticParams() {
 312 |   const products = await getPopularProducts()
 313 |   return products.map(({ category, slug }) => ({ category, slug }))
 314 | }
 315 | ```
 316 | 
 317 | ## Cache Key = Arguments
 318 | 
 319 | Arguments become part of the cache key:
 320 | 
 321 | ```tsx
 322 | // Different userId = different cache entry
 323 | async function UserData({ userId }: { userId: string }) {
 324 |   'use cache'
 325 |   cacheTag(`user-${userId}`)
 326 | 
 327 |   return await fetchUser(userId)
 328 | }
 329 | ```
 330 | 
 331 | ## Build-Time Feedback
 332 | 
 333 | Cache Components provides early feedback during development. These build errors **guide you toward optimal patterns**:
 334 | 
 335 | ### Error: Dynamic data outside Suspense
 336 | 
 337 | ```
 338 | Error: Accessing cookies/headers/searchParams outside a Suspense boundary
 339 | ```
 340 | 
 341 | **Solution**: Wrap dynamic components in `<Suspense>`:
 342 | 
 343 | ```tsx
 344 | <Suspense fallback={<Skeleton />}>
 345 |   <ComponentThatUsesCookies />
 346 | </Suspense>
 347 | ```
 348 | 
 349 | ### Error: Uncached data outside Suspense
 350 | 
 351 | ```
 352 | Error: Accessing uncached data outside Suspense
 353 | ```
 354 | 
 355 | **Solution**: Either cache the data or wrap in Suspense:
 356 | 
 357 | ```tsx
 358 | // Option 1: Cache it
 359 | async function ProductData({ id }: { id: string }) {
 360 |   'use cache'
 361 |   return await db.products.findUnique({ where: { id } })
 362 | }
 363 | 
 364 | // Option 2: Make it dynamic with Suspense
 365 | ;<Suspense fallback={<Loading />}>
 366 |   <DynamicProductData id={id} />
 367 | </Suspense>
 368 | ```
 369 | 
 370 | ### Error: Request data inside cache
 371 | 
 372 | ```
 373 | Error: Cannot access cookies/headers inside 'use cache'
 374 | ```
 375 | 
 376 | **Solution**: Extract runtime data outside cache boundary (see "Handling Runtime Data" above).
 377 | 
 378 | ## Additional Resources
 379 | 
 380 | - For complete API reference, see [REFERENCE.md](REFERENCE.md)
 381 | - For common patterns and recipes, see [PATTERNS.md](PATTERNS.md)
 382 | - For debugging and troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
 383 | 
 384 | ## Code Generation Guidelines
 385 | 
 386 | When generating Cache Component code:
 387 | 
 388 | 1. **Always use `async`** - All cached functions must be async
 389 | 2. **Place `'use cache'` first** - Must be first statement in function body
 390 | 3. **Call `cacheLife()` early** - Should follow `'use cache'` directive
 391 | 4. **Tag meaningfully** - Use semantic tags that match your invalidation needs
 392 | 5. **Extract runtime data** - Move `cookies()`/`headers()` outside cached scope
 393 | 6. **Wrap dynamic content** - Use `<Suspense>` for non-cached async components
 394 | 
 395 | ---
 396 | 
 397 | ## Proactive Application (When Cache Components Enabled)
 398 | 
 399 | When `cacheComponents: true` is detected in the project, **automatically apply these patterns**:
 400 | 
 401 | ### When Writing Data Fetching Components
 402 | 
 403 | Ask yourself: "Can this data be cached?" If yes, add `'use cache'`:
 404 | 
 405 | ```tsx
 406 | // Before: Uncached fetch
 407 | async function ProductList() {
 408 |   const products = await db.products.findMany()
 409 |   return <Grid products={products} />
 410 | }
 411 | 
 412 | // After: With caching
 413 | async function ProductList() {
 414 |   'use cache'
 415 |   cacheTag('products')
 416 |   cacheLife('hours')
 417 | 
 418 |   const products = await db.products.findMany()
 419 |   return <Grid products={products} />
 420 | }
 421 | ```
 422 | 
 423 | ### When Writing Server Actions
 424 | 
 425 | Always invalidate relevant caches after mutations:
 426 | 
 427 | ```tsx
 428 | 'use server'
 429 | import { updateTag } from 'next/cache'
 430 | 
 431 | export async function createProduct(data: FormData) {
 432 |   await db.products.create({ data })
 433 |   updateTag('products') // Don't forget!
 434 | }
 435 | ```
 436 | 
 437 | ### When Composing Pages
 438 | 
 439 | Structure with static shell + cached content + dynamic streaming:
 440 | 
 441 | ```tsx
 442 | export default async function Page() {
 443 |   return (
 444 |     <>
 445 |       <StaticHeader /> {/* No cache needed */}
 446 |       <CachedContent /> {/* 'use cache' */}
 447 |       <Suspense fallback={<Skeleton />}>
 448 |         <DynamicUserContent /> {/* Streams at runtime */}
 449 |       </Suspense>
 450 |     </>
 451 |   )
 452 | }
 453 | ```
 454 | 
 455 | ### When Reviewing Code
 456 | 
 457 | Flag these issues in Cache Components projects:
 458 | 
 459 | - [ ] Data fetching without `'use cache'` where caching would benefit
 460 | - [ ] Missing `cacheTag()` calls (makes invalidation impossible)
 461 | - [ ] Missing `cacheLife()` (relies on defaults which may not be appropriate)
 462 | - [ ] Server Actions without `updateTag()`/`revalidateTag()` after mutations
 463 | - [ ] `cookies()`/`headers()` called inside `'use cache'` scope
 464 | - [ ] Dynamic components without `<Suspense>` boundaries
 465 | - [ ] **DEPRECATED**: `export const revalidate` - replace with `cacheLife()` in `'use cache'`
 466 | - [ ] **DEPRECATED**: `export const dynamic` - replace with Suspense + cache boundaries
 467 | - [ ] Empty `generateStaticParams()` return - must provide at least one param
```


---
## AGENTS.md

```
   1 | # Next.js Development Guide
   2 | 
   3 | > **Note:** `CLAUDE.md` is a symlink to `AGENTS.md`. They are the same file.
   4 | 
   5 | ## Codebase structure
   6 | 
   7 | ### Monorepo Overview
   8 | 
   9 | This is a pnpm monorepo containing the Next.js framework and related packages.
  10 | 
  11 | ```
  12 | next.js/
  13 | ├── packages/           # Published npm packages
  14 | ├── turbopack/          # Turbopack bundler (Rust) - git subtree
  15 | ├── crates/             # Rust crates for Next.js SWC bindings
  16 | ├── test/               # All test suites
  17 | ├── examples/           # Example Next.js applications
  18 | ├── docs/               # Documentation
  19 | └── scripts/            # Build and maintenance scripts
  20 | ```
  21 | 
  22 | ### Core Package: `packages/next`
  23 | 
  24 | The main Next.js framework lives in `packages/next/`. This is what gets published as the `next` npm package.
  25 | 
  26 | **Source code** is in `packages/next/src/`.
  27 | 
  28 | **Key entry points:**
  29 | 
  30 | - Dev server: `src/cli/next-dev.ts` → `src/server/dev/next-dev-server.ts`
  31 | - Production server: `src/cli/next-start.ts` → `src/server/next-server.ts`
  32 | - Build: `src/cli/next-build.ts` → `src/build/index.ts`
  33 | 
  34 | **Compiled output** goes to `packages/next/dist/` (mirrors src/ structure).
  35 | 
  36 | ### Other Important Packages
  37 | 
  38 | - `packages/create-next-app/` - The `create-next-app` CLI tool
  39 | - `packages/next-swc/` - Native Rust bindings (SWC transforms)
  40 | - `packages/eslint-plugin-next/` - ESLint rules for Next.js
  41 | - `packages/font/` - `next/font` implementation
  42 | - `packages/third-parties/` - Third-party script integrations
  43 | 
  44 | ### README files
  45 | 
  46 | Before editing or creating files in any subdirectory (e.g., `packages/*`, `crates/*`), read all `README.md` files in the directory path from the repo root up to and including the target file's directory. This helps identify any local patterns, conventions, and documentation.
  47 | 
  48 | **Example:** Before editing `turbopack/crates/turbopack-ecmascript-runtime/js/src/nodejs/runtime/runtime-base.ts`, read:
  49 | 
  50 | - `turbopack/README.md` (if exists)
  51 | - `turbopack/crates/README.md` (if exists)
  52 | - `turbopack/crates/turbopack-ecmascript-runtime/README.md` (if exists)
  53 | - `turbopack/crates/turbopack-ecmascript-runtime/js/README.md` (if exists - closest to target file)
  54 | 
  55 | ## Build Commands
  56 | 
  57 | ```bash
  58 | # Build the Next.js package
  59 | pnpm --filter=next build
  60 | 
  61 | # Build all JS code
  62 | pnpm build
  63 | 
  64 | # Build all JS and Rust code
  65 | pnpm build-all
  66 | 
  67 | # Run specific task
  68 | pnpm --filter=next exec taskr <task>
  69 | ```
  70 | 
  71 | ## Fast Local Development
  72 | 
  73 | For iterative development, default to watch mode + skip-isolate for the inner loop (not full builds), with exceptions noted below.
  74 | 
  75 | **Default agent rule:** If you are changing Next.js source or integration tests, start `pnpm --filter=next dev` in a separate terminal session before making edits (unless it is already running). If you skip this, explicitly state why (for example: docs-only, read-only investigation, or CI-only analysis).
  76 | 
  77 | **1. Start watch build in background:**
  78 | 
  79 | ```bash
  80 | # Auto-rebuilds on file changes (~1-2s per change vs ~60s full build)
  81 | # Keep this running while you iterate on code
  82 | pnpm --filter=next dev
  83 | ```
  84 | 
  85 | **2. Run tests fast (no isolation, no packing):**
  86 | 
  87 | ```bash
  88 | # NEXT_SKIP_ISOLATE=1 - skip packing Next.js for each test (~100s faster)
  89 | # NEXT_TEST_MODE=<mode> - run dev or start based on the context provided
  90 | # testheadless - runs headless with --runInBand (no worker isolation overhead)
  91 | NEXT_SKIP_ISOLATE=1 NEXT_TEST_MODE=<dev|start> pnpm testheadless test/path/to/test.ts
  92 | ```
  93 | 
  94 | **3. When done, kill the background watch process (if you started it).**
  95 | 
  96 | **For type errors only:** Use `pnpm --filter=next types` (~10s) instead of `pnpm --filter=next build` (~60s).
  97 | 
  98 | After the workspace is bootstrapped, prefer `pnpm --filter=next build` when edits are limited to core Next.js files. Use full `pnpm build-all` for branch switches/bootstrap, before CI push, or when changes span multiple packages.
  99 | 
 100 | **Always run a full bootstrap build after switching branches:**
 101 | 
 102 | ```bash
 103 | git checkout <branch>
 104 | pnpm build-all   # Sets up outputs for dependent packages (Turborepo dedupes if unchanged)
 105 | ```
 106 | 
 107 | **When NOT to use NEXT_SKIP_ISOLATE:** Drop it when testing module resolution changes (new require() paths, new exports from entry-base.ts, edge route imports). Without isolation, the test uses local dist/ directly, hiding resolution failures that occur when Next.js is packed as a real npm package.
 108 | 
 109 | ## Bundler Selection
 110 | 
 111 | Turbopack is the default bundler for both `next dev` and `next build`. To force webpack:
 112 | 
 113 | ```bash
 114 | next build --webpack        # Production build with webpack
 115 | next dev --webpack          # Dev server with webpack
 116 | ```
 117 | 
 118 | There is no `--no-turbopack` flag.
 119 | 
 120 | ## Testing
 121 | 
 122 | ```bash
 123 | # Run specific test file (development mode with Turbopack)
 124 | pnpm test-dev-turbo test/path/to/test.test.ts
 125 | 
 126 | # Run tests matching pattern
 127 | pnpm test-dev-turbo -t "pattern"
 128 | 
 129 | # Run development tests
 130 | pnpm test-dev-turbo test/development/
 131 | ```
 132 | 
 133 | **Test commands by mode:**
 134 | 
 135 | - `pnpm test-dev-turbo` - Development mode with Turbopack (default)
 136 | - `pnpm test-dev-webpack` - Development mode with Webpack
 137 | - `pnpm test-start-turbo` - Production build+start with Turbopack
 138 | - `pnpm test-start-webpack` - Production build+start with Webpack
 139 | 
 140 | **Other test commands:**
 141 | 
 142 | - `pnpm test-unit` - Run unit tests only (fast, no browser)
 143 | - `pnpm testheadless <path>` - Run tests headless without rebuilding (faster iteration when build artifacts are already up to date)
 144 | - `pnpm new-test` - Generate a new test file from template (interactive)
 145 | 
 146 | **Generate tests non-interactively (for AI agents):**
 147 | 
 148 | Generating tests using `pnpm new-test` is mandatory.
 149 | 
 150 | ```bash
 151 | # Use --args for non-interactive mode (forward args to the script using `--`)
 152 | # Format: pnpm new-test -- --args <appDir> <name> <type>
 153 | # appDir: true/false (is this for app directory?)
 154 | # name: test name (e.g. "my-feature")
 155 | # type: e2e | production | development | unit
 156 | 
 157 | pnpm new-test -- --args true my-feature e2e
 158 | ```
 159 | 
 160 | **Analyzing test output efficiently:**
 161 | 
 162 | Never re-run the same test suite with different grep filters. Capture output once to a file, then read from it:
 163 | 
 164 | ```bash
 165 | # Run once, save everything
 166 | HEADLESS=true pnpm test-dev-turbo test/path/to/test.ts > /tmp/test-output.log 2>&1
 167 | 
 168 | # Then analyze without re-running
 169 | grep "●" /tmp/test-output.log            # Failed test names
 170 | grep -A5 "Error:" /tmp/test-output.log   # Error details
 171 | tail -5 /tmp/test-output.log             # Summary
 172 | ```
 173 | 
 174 | ## Writing Tests
 175 | 
 176 | **Test writing expectations:**
 177 | 
 178 | - **Use `pnpm new-test` to generate new test suites** - it creates proper structure with fixture files
 179 | 
 180 | - **Use `retry()` from `next-test-utils` instead of `setTimeout` for waiting**
 181 | 
 182 |   ```typescript
 183 |   // Good - use retry() for polling/waiting
 184 |   import { retry } from 'next-test-utils'
 185 |   await retry(async () => {
 186 |     const text = await browser.elementByCss('p').text()
 187 |     expect(text).toBe('expected value')
 188 |   })
 189 | 
 190 |   // Bad - don't use setTimeout for waiting
 191 |   await new Promise((resolve) => setTimeout(resolve, 1000))
 192 |   ```
 193 | 
 194 | - **Do NOT use `check()` - it is deprecated. Use `retry()` + `expect()` instead**
 195 | 
 196 |   ```typescript
 197 |   // Deprecated - don't use check()
 198 |   await check(() => browser.elementByCss('p').text(), /expected/)
 199 | 
 200 |   // Good - use retry() with expect()
 201 |   await retry(async () => {
 202 |     const text = await browser.elementByCss('p').text()
 203 |     expect(text).toMatch(/expected/)
 204 |   })
 205 |   ```
 206 | 
 207 | - **Prefer real fixture directories over inline `files` objects**
 208 | 
 209 |   ```typescript
 210 |   // Good - use a real directory with fixture files
 211 |   const { next } = nextTestSetup({
 212 |     files: __dirname, // points to directory containing test fixtures
 213 |   })
 214 | 
 215 |   // Avoid - inline file definitions are harder to maintain
 216 |   const { next } = nextTestSetup({
 217 |     files: {
 218 |       'app/page.tsx': `export default function Page() { ... }`,
 219 |     },
 220 |   })
 221 |   ```
 222 | 
 223 | ## Linting and Types
 224 | 
 225 | ```bash
 226 | pnpm lint              # Full lint (types, prettier, eslint, ast-grep)
 227 | pnpm lint-fix          # Auto-fix lint issues
 228 | pnpm prettier-fix      # Fix formatting only
 229 | pnpm types             # TypeScript type checking
 230 | ```
 231 | 
 232 | ## PR Status (CI Failures and Reviews)
 233 | 
 234 | When the user asks about CI failures, PR reviews, or the status of a PR, run the pr-status script:
 235 | 
 236 | ```bash
 237 | node scripts/pr-status.js           # Auto-detects PR from current branch
 238 | node scripts/pr-status.js <number>  # Analyze specific PR by number
 239 | ```
 240 | 
 241 | This generates analysis files in `scripts/pr-status/`.
 242 | 
 243 | General triage rules (always apply; `$pr-status-triage` skill expands on these):
 244 | 
 245 | - Prioritize blocking failures first: build, lint, types, then tests.
 246 | - Assume failures are real until disproven; use "Known Flaky Tests" as context, not auto-dismissal.
 247 | - Reproduce with the same CI mode/env vars (especially `IS_WEBPACK_TEST=1` when present).
 248 | - For module-resolution/build-graph fixes, verify without `NEXT_SKIP_ISOLATE=1`.
 249 | 
 250 | For full triage workflow (failure prioritization, mode selection, CI env reproduction, and common failure patterns), use the `$pr-status-triage` skill:
 251 | 
 252 | - Skill file: `.agents/skills/pr-status-triage/SKILL.md`
 253 | 
 254 | **Use `$pr-status-triage` for automated analysis** - see `.agents/skills/pr-status-triage/SKILL.md` for the full step-by-step workflow.
 255 | 
 256 | **CI Analysis Tips:**
 257 | 
 258 | - Prioritize CI failures over review comments
 259 | - Prioritize blocking jobs first: build, lint, types, then test jobs
 260 | - Common fast checks:
 261 |   - `rust check / build` → Run `cargo fmt -- --check`, then `cargo fmt`
 262 |   - `lint / build` → Run `pnpm prettier --write <file>` for prettier errors
 263 |   - test failures → Run the specific failing test path locally
 264 | 
 265 | **Run tests in the right mode:**
 266 | 
 267 | ```bash
 268 | # Dev mode (Turbopack)
 269 | pnpm test-dev-turbo test/path/to/test.ts
 270 | 
 271 | # Prod mode
 272 | pnpm test-start-turbo test/path/to/test.ts
 273 | ```
 274 | 
 275 | ## Key Directories (Quick Reference)
 276 | 
 277 | See [Codebase structure](#codebase-structure) above for detailed explanations.
 278 | 
 279 | - `packages/next/src/` - Main Next.js source code
 280 | - `packages/next/src/server/` - Server runtime (most changes happen here)
 281 | - `packages/next/src/client/` - Client-side runtime
 282 | - `packages/next/src/build/` - Build tooling
 283 | - `test/e2e/` - End-to-end tests
 284 | - `test/development/` - Dev server tests
 285 | - `test/production/` - Production build tests
 286 | - `test/unit/` - Unit tests (fast, no browser)
 287 | 
 288 | ## Development Tips
 289 | 
 290 | - The dev server entry point is `packages/next/src/cli/next-dev.ts`
 291 | - Router server: `packages/next/src/server/lib/router-server.ts`
 292 | - Use `DEBUG=next:*` for debug logging
 293 | - Use `NEXT_TELEMETRY_DISABLED=1` when testing locally
 294 | 
 295 | ### `NODE_ENV` vs `__NEXT_DEV_SERVER`
 296 | 
 297 | Both `next dev` and `next build --debug-prerender` produce bundles with `NODE_ENV=development`. Use `process.env.__NEXT_DEV_SERVER` to distinguish between them:
 298 | 
 299 | - `process.env.NODE_ENV !== 'production'` — code that should exist in dev bundles but be eliminated from prod bundles. This is a build-time check.
 300 | - `process.env.__NEXT_DEV_SERVER` — code that should only run with the dev server (`next dev`), not during `next build --debug-prerender` or `next start`.
 301 | 
 302 | ## Secrets and Env Safety
 303 | 
 304 | Always treat environment variable values as sensitive unless they are known test-mode flags.
 305 | 
 306 | - Never print or paste secret values (tokens, API keys, cookies) in chat responses, commits, or shared logs.
 307 | - Mirror CI env **names and modes** exactly, but do not inline literal secret values in commands.
 308 | - If a required secret is missing locally, stop and ask the user rather than inventing placeholder credentials.
 309 | - Never commit local secret files; if documenting env setup, use placeholder-only examples.
 310 | - When sharing command output, summarize and redact sensitive-looking values.
 311 | 
 312 | ## Specialized Skills
 313 | 
 314 | Use skills for conditional, deep workflows. Keep baseline iteration/build/test policy in this file.
 315 | 
 316 | - `$pr-status-triage` - CI failure and PR review triage with `scripts/pr-status.js`
 317 | - `$flags` - feature-flag wiring across config/schema/define-env/runtime env
 318 | - `$dce-edge` - DCE-safe `require()` patterns and edge/runtime constraints
 319 | - `$react-vendoring` - `entry-base.ts` boundaries and vendored React type/runtime rules
 320 | - `$runtime-debug` - runtime-bundle/module-resolution regression reproduction and verification
 321 | - `$authoring-skills` - how to create and maintain skills in `.agents/skills/`
 322 | 
 323 | ## Context-Efficient Workflows
 324 | 
 325 | **Reading large files** (>500 lines, e.g. `app-render.tsx`):
 326 | 
 327 | - Grep first to find relevant line numbers, then read targeted ranges with `offset`/`limit`
 328 | - Never re-read the same section of a file without code changes in between
 329 | - For generated files (`dist/`, `node_modules/`, `.next/`): search only, don't read
 330 | 
 331 | **Build & test output:**
 332 | 
 333 | - Capture to file once, then analyze: e.g. `pnpm build 2>&1 | tee /tmp/build.log`
 334 | - Don't re-run the same test command without code changes; re-analyze saved output instead
 335 | 
 336 | **Batch edits before building:**
 337 | 
 338 | - Group related edits across files, then run one build, not build-per-edit
 339 | - Use `pnpm --filter=next types` (~10s) to check type errors without full rebuild
 340 | 
 341 | **External API calls (gh, curl):**
 342 | 
 343 | - Save response to variable or file: `JOBS=$(gh api ...) && echo "$JOBS" | jq '...'`
 344 | - Don't re-fetch the same API data to analyze from different angles
 345 | 
 346 | ## Commit and PR Style
 347 | 
 348 | - Do NOT add "Generated with Claude Code" or co-author footers to commits or PRs
 349 | - Keep commit messages concise and descriptive
 350 | - PR descriptions should focus on what changed and why
 351 | - Do NOT mark PRs as "ready for review" (`gh pr ready`) - leave PRs in draft mode and let the user decide when to mark them ready
 352 | 
 353 | ## Task Decomposition and Verification
 354 | 
 355 | - **Split work into smaller, individually verifiable tasks.** Before starting, break the overall goal into incremental steps where each step produces a result that can be checked independently.
 356 | - **Verify each task before moving on to the next.** After completing a step, confirm it works correctly (e.g., run relevant tests, check types, build, or manually inspect output). Do not proceed to the next task until the current one is verified.
 357 | - **Choose the right verification method for each change.** This may include running unit tests, integration tests, type checking, linting, building the project, or inspecting runtime behavior depending on what was changed.
 358 | - **When unclear how to verify a change, ask the user.** If there is no obvious test or verification method for a particular change, ask the user how they would like it verified before moving on.
 359 | 
 360 | **Pre-validate before committing** to avoid slow lint-staged failures (~2 min each):
 361 | 
 362 | ```bash
 363 | # Run exactly what the pre-commit hook runs on your changed files:
 364 | pnpm prettier --with-node-modules --ignore-path .prettierignore --write <files>
 365 | npx eslint --config eslint.config.mjs --fix <files>
 366 | ```
 367 | 
 368 | ## Rebuilding Before Running Tests
 369 | 
 370 | When running Next.js integration tests, you must rebuild if source files have changed:
 371 | 
 372 | - **First run after branch switch/bootstrap (or if unsure)?** → `pnpm build-all`
 373 | - **Edited only core Next.js files (`packages/next/**`) after bootstrap?** → `pnpm --filter=next build`
 374 | - **Edited Next.js code or Turbopack (Rust)?** → `pnpm build-all`
 375 | 
 376 | ## Development Anti-Patterns
 377 | 
 378 | For runtime internals, use focused skills:
 379 | 
 380 | - Feature-flag plumbing and runtime bundle wiring: `$flags` (`.agents/skills/flags/SKILL.md`)
 381 | - DCE and edge/runtime constraints: `$dce-edge` (`.agents/skills/dce-edge/SKILL.md`)
 382 | - React vendoring and `entry-base.ts` boundaries: `$react-vendoring` (`.agents/skills/react-vendoring/SKILL.md`)
 383 | - Debugging and verification workflow: `$runtime-debug` (`.agents/skills/runtime-debug/SKILL.md`)
 384 | 
 385 | Keep these high-frequency guardrails in mind:
 386 | 
 387 | - Reproduce module resolution and bundling issues without `NEXT_SKIP_ISOLATE=1`
 388 | - Validate edge bundling regressions with `pnpm test-start-webpack test/e2e/app-dir/app/standalone.test.ts`
 389 | - Use `__NEXT_SHOW_IGNORE_LISTED=true` when you need full internal stack traces
 390 | 
 391 | Core runtime/bundling rules (always apply; skills above expand on these with verification steps and examples):
 392 | 
 393 | - New flags: add type in `config-shared.ts`, schema in `config-schema.ts`, and `define-env.ts` when used in user-bundled code.
 394 | - If a flag is consumed in pre-compiled runtime internals, also wire runtime env values (`next-server.ts`/`export/worker.ts` as needed).
 395 | - `define-env.ts` affects user bundling; it does not control pre-compiled runtime bundle internals.
 396 | - Keep `require()` behind compile-time `if/else` branches for DCE (avoid early-return/throw patterns).
 397 | - In edge builds, force feature flags that gate Node-only imports to `false` in `define-env.ts`.
 398 | - `react-server-dom-webpack/*` imports must stay in `entry-base.ts`; consume via component module exports elsewhere.
 399 | 
 400 | ### Test Gotchas
 401 | 
 402 | - **Cache components enables PPR by default**: When `__NEXT_CACHE_COMPONENTS=true`, most app-dir pages use PPR implicitly. Dedicated `ppr-full/` and `ppr/` test suites are mostly `describe.skip` (migrating to cache components). To test PPR codepaths, run normal app-dir e2e tests with `__NEXT_CACHE_COMPONENTS=true` rather than looking for explicit PPR test suites.
 403 |   -- **Quick smoke testing with toy apps**: For fast feedback, generate a minimal test fixture with `pnpm new-test -- --args true <name> e2e`, then run the dev server directly with `node packages/next/dist/bin/next dev --port <port>` and `curl --max-time 10`. This avoids the overhead of the full test harness and gives immediate feedback on hangs/crashes.
 404 | - Mode-specific tests need `skipStart: true` + manual `next.start()` in `beforeAll` after mode check
 405 | - Don't rely on exact log messages - filter by content patterns, find sequences not positions
 406 | - **Snapshot tests vary by env flags**: Tests with inline snapshots can produce different output depending on env flags. When updating snapshots, always run the test with the exact env flags the CI job uses (check `.github/workflows/build_and_test.yml` `afterBuild:` sections). Turbopack resolves `react-dom/server.edge` (no Node APIs like `renderToPipeableStream`), while webpack resolves the `.node` build (has them).
 407 | - **`app-page.ts` is a build template compiled by the user's bundler**: Any `require()` in this file is traced by webpack/turbopack at `next build` time. You cannot require internal modules with relative paths because they won't be resolvable from the user's project. Instead, export new helpers from `entry-base.ts` and access them via `entryBase.*` in the template.
 408 | - **Reproducing CI failures locally**: Always match the exact CI env vars (check `pr-status` output for "Job Environment Variables"). Key differences: `IS_WEBPACK_TEST=1` forces webpack (turbopack is default), `NEXT_SKIP_ISOLATE=1` skips packing next.js (hides module resolution failures). Always run without `NEXT_SKIP_ISOLATE` when verifying module resolution fixes.
 409 | - **Showing full stack traces**: Set `__NEXT_SHOW_IGNORE_LISTED=true` to disable the ignore-list filtering in dev server error output. By default, Next.js collapses internal frames to `at ignore-listed frames`, which hides useful context when debugging framework internals. Defined in `packages/next/src/server/patch-error-inspect.ts`.
 410 | - **Router act tests must use LinkAccordion to control prefetches**: Always use `LinkAccordion` to control when prefetches happen inside `act` scopes. Never use `browser.back()` to return to a page where accordion links are already visible — BFCache restores state and triggers uncontrolled re-prefetches. See `$router-act` for full patterns.
 411 | 
 412 | ### Rust/Cargo
 413 | 
 414 | - cargo fmt uses ASCII order (uppercase before lowercase) - just run `cargo fmt`
 415 | - **Internal compiler error (ICE)?** Delete incremental compilation artifacts and retry. Remove `*/incremental` directories from your cargo target directory (default `target/`, or check `CARGO_TARGET_DIR` env var)
 416 | 
 417 | ### Node.js Source Maps
 418 | 
 419 | - `findSourceMap()` needs `--enable-source-maps` flag or returns undefined
 420 | - Source map paths vary (webpack: `./src/`, tsc: `src/`) - try multiple formats
 421 | - `process.cwd()` in stack trace formatting produces different paths in tests vs production
 422 | 
 423 | ### Stale Native Binary
 424 | 
 425 | If Turbopack produces unexpected errors after switching branches or pulling, check if `packages/next-swc/native/*.node` is stale. Delete it and run `pnpm install` to get the npm-published binary instead of a locally-built one.
 426 | 
 427 | ### Documentation Code Blocks
 428 | 
 429 | - When adding `highlight={...}` attributes to code blocks, carefully count the actual line numbers within the code block
 430 | - Account for empty lines, import statements, and type imports that shift line numbers
 431 | - Highlights should point to the actual relevant code, not unrelated lines like `return (` or framework boilerplate
 432 | - Double-check highlights by counting lines from 1 within each code block
```


---
## CLAUDE.md

```
   1 | # Next.js Development Guide
   2 | 
   3 | > **Note:** `CLAUDE.md` is a symlink to `AGENTS.md`. They are the same file.
   4 | 
   5 | ## Codebase structure
   6 | 
   7 | ### Monorepo Overview
   8 | 
   9 | This is a pnpm monorepo containing the Next.js framework and related packages.
  10 | 
  11 | ```
  12 | next.js/
  13 | ├── packages/           # Published npm packages
  14 | ├── turbopack/          # Turbopack bundler (Rust) - git subtree
  15 | ├── crates/             # Rust crates for Next.js SWC bindings
  16 | ├── test/               # All test suites
  17 | ├── examples/           # Example Next.js applications
  18 | ├── docs/               # Documentation
  19 | └── scripts/            # Build and maintenance scripts
  20 | ```
  21 | 
  22 | ### Core Package: `packages/next`
  23 | 
  24 | The main Next.js framework lives in `packages/next/`. This is what gets published as the `next` npm package.
  25 | 
  26 | **Source code** is in `packages/next/src/`.
  27 | 
  28 | **Key entry points:**
  29 | 
  30 | - Dev server: `src/cli/next-dev.ts` → `src/server/dev/next-dev-server.ts`
  31 | - Production server: `src/cli/next-start.ts` → `src/server/next-server.ts`
  32 | - Build: `src/cli/next-build.ts` → `src/build/index.ts`
  33 | 
  34 | **Compiled output** goes to `packages/next/dist/` (mirrors src/ structure).
  35 | 
  36 | ### Other Important Packages
  37 | 
  38 | - `packages/create-next-app/` - The `create-next-app` CLI tool
  39 | - `packages/next-swc/` - Native Rust bindings (SWC transforms)
  40 | - `packages/eslint-plugin-next/` - ESLint rules for Next.js
  41 | - `packages/font/` - `next/font` implementation
  42 | - `packages/third-parties/` - Third-party script integrations
  43 | 
  44 | ### README files
  45 | 
  46 | Before editing or creating files in any subdirectory (e.g., `packages/*`, `crates/*`), read all `README.md` files in the directory path from the repo root up to and including the target file's directory. This helps identify any local patterns, conventions, and documentation.
  47 | 
  48 | **Example:** Before editing `turbopack/crates/turbopack-ecmascript-runtime/js/src/nodejs/runtime/runtime-base.ts`, read:
  49 | 
  50 | - `turbopack/README.md` (if exists)
  51 | - `turbopack/crates/README.md` (if exists)
  52 | - `turbopack/crates/turbopack-ecmascript-runtime/README.md` (if exists)
  53 | - `turbopack/crates/turbopack-ecmascript-runtime/js/README.md` (if exists - closest to target file)
  54 | 
  55 | ## Build Commands
  56 | 
  57 | ```bash
  58 | # Build the Next.js package
  59 | pnpm --filter=next build
  60 | 
  61 | # Build all JS code
  62 | pnpm build
  63 | 
  64 | # Build all JS and Rust code
  65 | pnpm build-all
  66 | 
  67 | # Run specific task
  68 | pnpm --filter=next exec taskr <task>
  69 | ```
  70 | 
  71 | ## Fast Local Development
  72 | 
  73 | For iterative development, default to watch mode + skip-isolate for the inner loop (not full builds), with exceptions noted below.
  74 | 
  75 | **Default agent rule:** If you are changing Next.js source or integration tests, start `pnpm --filter=next dev` in a separate terminal session before making edits (unless it is already running). If you skip this, explicitly state why (for example: docs-only, read-only investigation, or CI-only analysis).
  76 | 
  77 | **1. Start watch build in background:**
  78 | 
  79 | ```bash
  80 | # Auto-rebuilds on file changes (~1-2s per change vs ~60s full build)
  81 | # Keep this running while you iterate on code
  82 | pnpm --filter=next dev
  83 | ```
  84 | 
  85 | **2. Run tests fast (no isolation, no packing):**
  86 | 
  87 | ```bash
  88 | # NEXT_SKIP_ISOLATE=1 - skip packing Next.js for each test (~100s faster)
  89 | # NEXT_TEST_MODE=<mode> - run dev or start based on the context provided
  90 | # testheadless - runs headless with --runInBand (no worker isolation overhead)
  91 | NEXT_SKIP_ISOLATE=1 NEXT_TEST_MODE=<dev|start> pnpm testheadless test/path/to/test.ts
  92 | ```
  93 | 
  94 | **3. When done, kill the background watch process (if you started it).**
  95 | 
  96 | **For type errors only:** Use `pnpm --filter=next types` (~10s) instead of `pnpm --filter=next build` (~60s).
  97 | 
  98 | After the workspace is bootstrapped, prefer `pnpm --filter=next build` when edits are limited to core Next.js files. Use full `pnpm build-all` for branch switches/bootstrap, before CI push, or when changes span multiple packages.
  99 | 
 100 | **Always run a full bootstrap build after switching branches:**
 101 | 
 102 | ```bash
 103 | git checkout <branch>
 104 | pnpm build-all   # Sets up outputs for dependent packages (Turborepo dedupes if unchanged)
 105 | ```
 106 | 
 107 | **When NOT to use NEXT_SKIP_ISOLATE:** Drop it when testing module resolution changes (new require() paths, new exports from entry-base.ts, edge route imports). Without isolation, the test uses local dist/ directly, hiding resolution failures that occur when Next.js is packed as a real npm package.
 108 | 
 109 | ## Bundler Selection
 110 | 
 111 | Turbopack is the default bundler for both `next dev` and `next build`. To force webpack:
 112 | 
 113 | ```bash
 114 | next build --webpack        # Production build with webpack
 115 | next dev --webpack          # Dev server with webpack
 116 | ```
 117 | 
 118 | There is no `--no-turbopack` flag.
 119 | 
 120 | ## Testing
 121 | 
 122 | ```bash
 123 | # Run specific test file (development mode with Turbopack)
 124 | pnpm test-dev-turbo test/path/to/test.test.ts
 125 | 
 126 | # Run tests matching pattern
 127 | pnpm test-dev-turbo -t "pattern"
 128 | 
 129 | # Run development tests
 130 | pnpm test-dev-turbo test/development/
 131 | ```
 132 | 
 133 | **Test commands by mode:**
 134 | 
 135 | - `pnpm test-dev-turbo` - Development mode with Turbopack (default)
 136 | - `pnpm test-dev-webpack` - Development mode with Webpack
 137 | - `pnpm test-start-turbo` - Production build+start with Turbopack
 138 | - `pnpm test-start-webpack` - Production build+start with Webpack
 139 | 
 140 | **Other test commands:**
 141 | 
 142 | - `pnpm test-unit` - Run unit tests only (fast, no browser)
 143 | - `pnpm testheadless <path>` - Run tests headless without rebuilding (faster iteration when build artifacts are already up to date)
 144 | - `pnpm new-test` - Generate a new test file from template (interactive)
 145 | 
 146 | **Generate tests non-interactively (for AI agents):**
 147 | 
 148 | Generating tests using `pnpm new-test` is mandatory.
 149 | 
 150 | ```bash
 151 | # Use --args for non-interactive mode (forward args to the script using `--`)
 152 | # Format: pnpm new-test -- --args <appDir> <name> <type>
 153 | # appDir: true/false (is this for app directory?)
 154 | # name: test name (e.g. "my-feature")
 155 | # type: e2e | production | development | unit
 156 | 
 157 | pnpm new-test -- --args true my-feature e2e
 158 | ```
 159 | 
 160 | **Analyzing test output efficiently:**
 161 | 
 162 | Never re-run the same test suite with different grep filters. Capture output once to a file, then read from it:
 163 | 
 164 | ```bash
 165 | # Run once, save everything
 166 | HEADLESS=true pnpm test-dev-turbo test/path/to/test.ts > /tmp/test-output.log 2>&1
 167 | 
 168 | # Then analyze without re-running
 169 | grep "●" /tmp/test-output.log            # Failed test names
 170 | grep -A5 "Error:" /tmp/test-output.log   # Error details
 171 | tail -5 /tmp/test-output.log             # Summary
 172 | ```
 173 | 
 174 | ## Writing Tests
 175 | 
 176 | **Test writing expectations:**
 177 | 
 178 | - **Use `pnpm new-test` to generate new test suites** - it creates proper structure with fixture files
 179 | 
 180 | - **Use `retry()` from `next-test-utils` instead of `setTimeout` for waiting**
 181 | 
 182 |   ```typescript
 183 |   // Good - use retry() for polling/waiting
 184 |   import { retry } from 'next-test-utils'
 185 |   await retry(async () => {
 186 |     const text = await browser.elementByCss('p').text()
 187 |     expect(text).toBe('expected value')
 188 |   })
 189 | 
 190 |   // Bad - don't use setTimeout for waiting
 191 |   await new Promise((resolve) => setTimeout(resolve, 1000))
 192 |   ```
 193 | 
 194 | - **Do NOT use `check()` - it is deprecated. Use `retry()` + `expect()` instead**
 195 | 
 196 |   ```typescript
 197 |   // Deprecated - don't use check()
 198 |   await check(() => browser.elementByCss('p').text(), /expected/)
 199 | 
 200 |   // Good - use retry() with expect()
 201 |   await retry(async () => {
 202 |     const text = await browser.elementByCss('p').text()
 203 |     expect(text).toMatch(/expected/)
 204 |   })
 205 |   ```
 206 | 
 207 | - **Prefer real fixture directories over inline `files` objects**
 208 | 
 209 |   ```typescript
 210 |   // Good - use a real directory with fixture files
 211 |   const { next } = nextTestSetup({
 212 |     files: __dirname, // points to directory containing test fixtures
 213 |   })
 214 | 
 215 |   // Avoid - inline file definitions are harder to maintain
 216 |   const { next } = nextTestSetup({
 217 |     files: {
 218 |       'app/page.tsx': `export default function Page() { ... }`,
 219 |     },
 220 |   })
 221 |   ```
 222 | 
 223 | ## Linting and Types
 224 | 
 225 | ```bash
 226 | pnpm lint              # Full lint (types, prettier, eslint, ast-grep)
 227 | pnpm lint-fix          # Auto-fix lint issues
 228 | pnpm prettier-fix      # Fix formatting only
 229 | pnpm types             # TypeScript type checking
 230 | ```
 231 | 
 232 | ## PR Status (CI Failures and Reviews)
 233 | 
 234 | When the user asks about CI failures, PR reviews, or the status of a PR, run the pr-status script:
 235 | 
 236 | ```bash
 237 | node scripts/pr-status.js           # Auto-detects PR from current branch
 238 | node scripts/pr-status.js <number>  # Analyze specific PR by number
 239 | ```
 240 | 
 241 | This generates analysis files in `scripts/pr-status/`.
 242 | 
 243 | General triage rules (always apply; `$pr-status-triage` skill expands on these):
 244 | 
 245 | - Prioritize blocking failures first: build, lint, types, then tests.
 246 | - Assume failures are real until disproven; use "Known Flaky Tests" as context, not auto-dismissal.
 247 | - Reproduce with the same CI mode/env vars (especially `IS_WEBPACK_TEST=1` when present).
 248 | - For module-resolution/build-graph fixes, verify without `NEXT_SKIP_ISOLATE=1`.
 249 | 
 250 | For full triage workflow (failure prioritization, mode selection, CI env reproduction, and common failure patterns), use the `$pr-status-triage` skill:
 251 | 
 252 | - Skill file: `.agents/skills/pr-status-triage/SKILL.md`
 253 | 
 254 | **Use `$pr-status-triage` for automated analysis** - see `.agents/skills/pr-status-triage/SKILL.md` for the full step-by-step workflow.
 255 | 
 256 | **CI Analysis Tips:**
 257 | 
 258 | - Prioritize CI failures over review comments
 259 | - Prioritize blocking jobs first: build, lint, types, then test jobs
 260 | - Common fast checks:
 261 |   - `rust check / build` → Run `cargo fmt -- --check`, then `cargo fmt`
 262 |   - `lint / build` → Run `pnpm prettier --write <file>` for prettier errors
 263 |   - test failures → Run the specific failing test path locally
 264 | 
 265 | **Run tests in the right mode:**
 266 | 
 267 | ```bash
 268 | # Dev mode (Turbopack)
 269 | pnpm test-dev-turbo test/path/to/test.ts
 270 | 
 271 | # Prod mode
 272 | pnpm test-start-turbo test/path/to/test.ts
 273 | ```
 274 | 
 275 | ## Key Directories (Quick Reference)
 276 | 
 277 | See [Codebase structure](#codebase-structure) above for detailed explanations.
 278 | 
 279 | - `packages/next/src/` - Main Next.js source code
 280 | - `packages/next/src/server/` - Server runtime (most changes happen here)
 281 | - `packages/next/src/client/` - Client-side runtime
 282 | - `packages/next/src/build/` - Build tooling
 283 | - `test/e2e/` - End-to-end tests
 284 | - `test/development/` - Dev server tests
 285 | - `test/production/` - Production build tests
 286 | - `test/unit/` - Unit tests (fast, no browser)
 287 | 
 288 | ## Development Tips
 289 | 
 290 | - The dev server entry point is `packages/next/src/cli/next-dev.ts`
 291 | - Router server: `packages/next/src/server/lib/router-server.ts`
 292 | - Use `DEBUG=next:*` for debug logging
 293 | - Use `NEXT_TELEMETRY_DISABLED=1` when testing locally
 294 | 
 295 | ### `NODE_ENV` vs `__NEXT_DEV_SERVER`
 296 | 
 297 | Both `next dev` and `next build --debug-prerender` produce bundles with `NODE_ENV=development`. Use `process.env.__NEXT_DEV_SERVER` to distinguish between them:
 298 | 
 299 | - `process.env.NODE_ENV !== 'production'` — code that should exist in dev bundles but be eliminated from prod bundles. This is a build-time check.
 300 | - `process.env.__NEXT_DEV_SERVER` — code that should only run with the dev server (`next dev`), not during `next build --debug-prerender` or `next start`.
 301 | 
 302 | ## Secrets and Env Safety
 303 | 
 304 | Always treat environment variable values as sensitive unless they are known test-mode flags.
 305 | 
 306 | - Never print or paste secret values (tokens, API keys, cookies) in chat responses, commits, or shared logs.
 307 | - Mirror CI env **names and modes** exactly, but do not inline literal secret values in commands.
 308 | - If a required secret is missing locally, stop and ask the user rather than inventing placeholder credentials.
 309 | - Never commit local secret files; if documenting env setup, use placeholder-only examples.
 310 | - When sharing command output, summarize and redact sensitive-looking values.
 311 | 
 312 | ## Specialized Skills
 313 | 
 314 | Use skills for conditional, deep workflows. Keep baseline iteration/build/test policy in this file.
 315 | 
 316 | - `$pr-status-triage` - CI failure and PR review triage with `scripts/pr-status.js`
 317 | - `$flags` - feature-flag wiring across config/schema/define-env/runtime env
 318 | - `$dce-edge` - DCE-safe `require()` patterns and edge/runtime constraints
 319 | - `$react-vendoring` - `entry-base.ts` boundaries and vendored React type/runtime rules
 320 | - `$runtime-debug` - runtime-bundle/module-resolution regression reproduction and verification
 321 | - `$authoring-skills` - how to create and maintain skills in `.agents/skills/`
 322 | 
 323 | ## Context-Efficient Workflows
 324 | 
 325 | **Reading large files** (>500 lines, e.g. `app-render.tsx`):
 326 | 
 327 | - Grep first to find relevant line numbers, then read targeted ranges with `offset`/`limit`
 328 | - Never re-read the same section of a file without code changes in between
 329 | - For generated files (`dist/`, `node_modules/`, `.next/`): search only, don't read
 330 | 
 331 | **Build & test output:**
 332 | 
 333 | - Capture to file once, then analyze: e.g. `pnpm build 2>&1 | tee /tmp/build.log`
 334 | - Don't re-run the same test command without code changes; re-analyze saved output instead
 335 | 
 336 | **Batch edits before building:**
 337 | 
 338 | - Group related edits across files, then run one build, not build-per-edit
 339 | - Use `pnpm --filter=next types` (~10s) to check type errors without full rebuild
 340 | 
 341 | **External API calls (gh, curl):**
 342 | 
 343 | - Save response to variable or file: `JOBS=$(gh api ...) && echo "$JOBS" | jq '...'`
 344 | - Don't re-fetch the same API data to analyze from different angles
 345 | 
 346 | ## Commit and PR Style
 347 | 
 348 | - Do NOT add "Generated with Claude Code" or co-author footers to commits or PRs
 349 | - Keep commit messages concise and descriptive
 350 | - PR descriptions should focus on what changed and why
 351 | - Do NOT mark PRs as "ready for review" (`gh pr ready`) - leave PRs in draft mode and let the user decide when to mark them ready
 352 | 
 353 | ## Task Decomposition and Verification
 354 | 
 355 | - **Split work into smaller, individually verifiable tasks.** Before starting, break the overall goal into incremental steps where each step produces a result that can be checked independently.
 356 | - **Verify each task before moving on to the next.** After completing a step, confirm it works correctly (e.g., run relevant tests, check types, build, or manually inspect output). Do not proceed to the next task until the current one is verified.
 357 | - **Choose the right verification method for each change.** This may include running unit tests, integration tests, type checking, linting, building the project, or inspecting runtime behavior depending on what was changed.
 358 | - **When unclear how to verify a change, ask the user.** If there is no obvious test or verification method for a particular change, ask the user how they would like it verified before moving on.
 359 | 
 360 | **Pre-validate before committing** to avoid slow lint-staged failures (~2 min each):
 361 | 
 362 | ```bash
 363 | # Run exactly what the pre-commit hook runs on your changed files:
 364 | pnpm prettier --with-node-modules --ignore-path .prettierignore --write <files>
 365 | npx eslint --config eslint.config.mjs --fix <files>
 366 | ```
 367 | 
 368 | ## Rebuilding Before Running Tests
 369 | 
 370 | When running Next.js integration tests, you must rebuild if source files have changed:
 371 | 
 372 | - **First run after branch switch/bootstrap (or if unsure)?** → `pnpm build-all`
 373 | - **Edited only core Next.js files (`packages/next/**`) after bootstrap?** → `pnpm --filter=next build`
 374 | - **Edited Next.js code or Turbopack (Rust)?** → `pnpm build-all`
 375 | 
 376 | ## Development Anti-Patterns
 377 | 
 378 | For runtime internals, use focused skills:
 379 | 
 380 | - Feature-flag plumbing and runtime bundle wiring: `$flags` (`.agents/skills/flags/SKILL.md`)
 381 | - DCE and edge/runtime constraints: `$dce-edge` (`.agents/skills/dce-edge/SKILL.md`)
 382 | - React vendoring and `entry-base.ts` boundaries: `$react-vendoring` (`.agents/skills/react-vendoring/SKILL.md`)
 383 | - Debugging and verification workflow: `$runtime-debug` (`.agents/skills/runtime-debug/SKILL.md`)
 384 | 
 385 | Keep these high-frequency guardrails in mind:
 386 | 
 387 | - Reproduce module resolution and bundling issues without `NEXT_SKIP_ISOLATE=1`
 388 | - Validate edge bundling regressions with `pnpm test-start-webpack test/e2e/app-dir/app/standalone.test.ts`
 389 | - Use `__NEXT_SHOW_IGNORE_LISTED=true` when you need full internal stack traces
 390 | 
 391 | Core runtime/bundling rules (always apply; skills above expand on these with verification steps and examples):
 392 | 
 393 | - New flags: add type in `config-shared.ts`, schema in `config-schema.ts`, and `define-env.ts` when used in user-bundled code.
 394 | - If a flag is consumed in pre-compiled runtime internals, also wire runtime env values (`next-server.ts`/`export/worker.ts` as needed).
 395 | - `define-env.ts` affects user bundling; it does not control pre-compiled runtime bundle internals.
 396 | - Keep `require()` behind compile-time `if/else` branches for DCE (avoid early-return/throw patterns).
 397 | - In edge builds, force feature flags that gate Node-only imports to `false` in `define-env.ts`.
 398 | - `react-server-dom-webpack/*` imports must stay in `entry-base.ts`; consume via component module exports elsewhere.
 399 | 
 400 | ### Test Gotchas
 401 | 
 402 | - **Cache components enables PPR by default**: When `__NEXT_CACHE_COMPONENTS=true`, most app-dir pages use PPR implicitly. Dedicated `ppr-full/` and `ppr/` test suites are mostly `describe.skip` (migrating to cache components). To test PPR codepaths, run normal app-dir e2e tests with `__NEXT_CACHE_COMPONENTS=true` rather than looking for explicit PPR test suites.
 403 |   -- **Quick smoke testing with toy apps**: For fast feedback, generate a minimal test fixture with `pnpm new-test -- --args true <name> e2e`, then run the dev server directly with `node packages/next/dist/bin/next dev --port <port>` and `curl --max-time 10`. This avoids the overhead of the full test harness and gives immediate feedback on hangs/crashes.
 404 | - Mode-specific tests need `skipStart: true` + manual `next.start()` in `beforeAll` after mode check
 405 | - Don't rely on exact log messages - filter by content patterns, find sequences not positions
 406 | - **Snapshot tests vary by env flags**: Tests with inline snapshots can produce different output depending on env flags. When updating snapshots, always run the test with the exact env flags the CI job uses (check `.github/workflows/build_and_test.yml` `afterBuild:` sections). Turbopack resolves `react-dom/server.edge` (no Node APIs like `renderToPipeableStream`), while webpack resolves the `.node` build (has them).
 407 | - **`app-page.ts` is a build template compiled by the user's bundler**: Any `require()` in this file is traced by webpack/turbopack at `next build` time. You cannot require internal modules with relative paths because they won't be resolvable from the user's project. Instead, export new helpers from `entry-base.ts` and access them via `entryBase.*` in the template.
 408 | - **Reproducing CI failures locally**: Always match the exact CI env vars (check `pr-status` output for "Job Environment Variables"). Key differences: `IS_WEBPACK_TEST=1` forces webpack (turbopack is default), `NEXT_SKIP_ISOLATE=1` skips packing next.js (hides module resolution failures). Always run without `NEXT_SKIP_ISOLATE` when verifying module resolution fixes.
 409 | - **Showing full stack traces**: Set `__NEXT_SHOW_IGNORE_LISTED=true` to disable the ignore-list filtering in dev server error output. By default, Next.js collapses internal frames to `at ignore-listed frames`, which hides useful context when debugging framework internals. Defined in `packages/next/src/server/patch-error-inspect.ts`.
 410 | - **Router act tests must use LinkAccordion to control prefetches**: Always use `LinkAccordion` to control when prefetches happen inside `act` scopes. Never use `browser.back()` to return to a page where accordion links are already visible — BFCache restores state and triggers uncontrolled re-prefetches. See `$router-act` for full patterns.
 411 | 
 412 | ### Rust/Cargo
 413 | 
 414 | - cargo fmt uses ASCII order (uppercase before lowercase) - just run `cargo fmt`
 415 | - **Internal compiler error (ICE)?** Delete incremental compilation artifacts and retry. Remove `*/incremental` directories from your cargo target directory (default `target/`, or check `CARGO_TARGET_DIR` env var)
 416 | 
 417 | ### Node.js Source Maps
 418 | 
 419 | - `findSourceMap()` needs `--enable-source-maps` flag or returns undefined
 420 | - Source map paths vary (webpack: `./src/`, tsc: `src/`) - try multiple formats
 421 | - `process.cwd()` in stack trace formatting produces different paths in tests vs production
 422 | 
 423 | ### Stale Native Binary
 424 | 
 425 | If Turbopack produces unexpected errors after switching branches or pulling, check if `packages/next-swc/native/*.node` is stale. Delete it and run `pnpm install` to get the npm-published binary instead of a locally-built one.
 426 | 
 427 | ### Documentation Code Blocks
 428 | 
 429 | - When adding `highlight={...}` attributes to code blocks, carefully count the actual line numbers within the code block
 430 | - Account for empty lines, import statements, and type imports that shift line numbers
 431 | - Highlights should point to the actual relevant code, not unrelated lines like `return (` or framework boilerplate
 432 | - Double-check highlights by counting lines from 1 within each code block
```


---
## packages/create-next-app/README.md

```
   1 | # Create Next App
   2 | 
   3 | The easiest way to get started with Next.js is by using `create-next-app`. This CLI tool enables you to quickly start building a new Next.js application, with everything set up for you. You can create a new app using the default Next.js template, or by using one of the [official Next.js examples](https://github.com/vercel/next.js/tree/canary/examples). To get started, use the following command:
   4 | 
   5 | ### Interactive
   6 | 
   7 | You can create a new project interactively by running:
   8 | 
   9 | ```bash
  10 | npx create-next-app@latest
  11 | # or
  12 | yarn create next-app
  13 | # or
  14 | pnpm create next-app
  15 | # or
  16 | bunx create-next-app
  17 | ```
  18 | 
  19 | You will be asked for the name of your project, and then whether you want to
  20 | create a TypeScript project:
  21 | 
  22 | ```bash
  23 | ✔ Would you like to use TypeScript? … No / Yes
  24 | ```
  25 | 
  26 | Select **Yes** to install the necessary types/dependencies and create a new TS project.
  27 | 
  28 | ### Non-interactive
  29 | 
  30 | You can also pass command line arguments to set up a new project
  31 | non-interactively. See `create-next-app --help`:
  32 | 
  33 | ```bash
  34 | Usage: create-next-app [project-directory] [options]
  35 | 
  36 | Options:
  37 |   -V, --version                        output the version number
  38 |   --ts, --typescript
  39 | 
  40 |     Initialize as a TypeScript project. (default)
  41 | 
  42 |   --js, --javascript
  43 | 
  44 |     Initialize as a JavaScript project.
  45 | 
  46 |   --tailwind
  47 | 
  48 |     Initialize with Tailwind CSS config. (default)
  49 | 
  50 |   --eslint
  51 | 
  52 |     Initialize with ESLint config.
  53 | 
  54 |   --app
  55 | 
  56 |     Initialize as an App Router project.
  57 | 
  58 |   --src-dir
  59 | 
  60 |     Initialize inside a `src/` directory.
  61 | 
  62 |   --import-alias <alias-to-configure>
  63 | 
  64 |     Specify import alias to use (default "@/*").
  65 | 
  66 |   --empty
  67 | 
  68 |     Initialize an empty project.
  69 | 
  70 |   --use-npm
  71 | 
  72 |     Explicitly tell the CLI to bootstrap the application using npm
  73 | 
  74 |   --use-pnpm
  75 | 
  76 |     Explicitly tell the CLI to bootstrap the application using pnpm
  77 | 
  78 |   --use-yarn
  79 | 
  80 |     Explicitly tell the CLI to bootstrap the application using Yarn
  81 | 
  82 |   --use-bun
  83 | 
  84 |     Explicitly tell the CLI to bootstrap the application using Bun
  85 | 
  86 |   -e, --example [name]|[github-url]
  87 | 
  88 |     An example to bootstrap the app with. You can use an example name
  89 |     from the official Next.js repo or a GitHub URL. The URL can use
  90 |     any branch and/or subdirectory
  91 | 
  92 |   --example-path <path-to-example>
  93 | 
  94 |     In a rare case, your GitHub URL might contain a branch name with
  95 |     a slash (e.g. bug/fix-1) and the path to the example (e.g. foo/bar).
  96 |     In this case, you must specify the path to the example separately:
  97 |     --example-path foo/bar
  98 | 
  99 |   --reset-preferences
 100 | 
 101 |     Explicitly tell the CLI to reset any stored preferences
 102 | 
 103 |   --skip-install
 104 | 
 105 |     Explicitly tell the CLI to skip installing packages
 106 | 
 107 |   --disable-git
 108 | 
 109 |     Explicitly tell the CLI to skip initializing a git repository.
 110 | 
 111 |   --yes
 112 | 
 113 |     Use previous preferences or defaults for all options that were not
 114 |     explicitly specified, without prompting.
 115 | 
 116 |   -h, --help                           display help for command
 117 | ```
 118 | 
 119 | ### Why use Create Next App?
 120 | 
 121 | `create-next-app` allows you to create a new Next.js app within seconds. It is officially maintained by the creators of Next.js, and includes a number of benefits:
 122 | 
 123 | - **Interactive Experience**: Running `npx create-next-app@latest` (with no arguments) launches an interactive experience that guides you through setting up a project.
 124 | - **Zero Dependencies**: Initializing a project is as quick as one second. Create Next App has zero dependencies.
 125 | - **Offline Support**: Create Next App will automatically detect if you're offline and bootstrap your project using your local package cache.
 126 | - **Support for Examples**: Create Next App can bootstrap your application using an example from the Next.js examples collection (e.g. `npx create-next-app --example route-handlers`).
 127 | - **Tested**: The package is part of the Next.js monorepo and tested using the same integration test suite as Next.js itself, ensuring it works as expected with every release.
```
