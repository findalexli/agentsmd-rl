#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sentry-javascript

# Idempotency guard
if grep -qF "description: Add a new AI provider integration to the Sentry JavaScript SDK. Use" ".agents/skills/add-ai-integration/SKILL.md" && grep -qF "5. Update `CHANGELOG.md` \u2014 add the new version entry with the changelog output. " ".agents/skills/release/SKILL.md" && grep -qF "Do **not** upgrade the major version of a dependency in `dev-packages/e2e-tests/" ".agents/skills/upgrade-dep/SKILL.md" && grep -qF "2. **All `@opentelemetry/instrumentation-*` packages.** Check each changelog: `h" ".agents/skills/upgrade-otel/SKILL.md" && grep -qF ".cursor/rules/adding-a-new-ai-integration.mdc" ".cursor/rules/adding-a-new-ai-integration.mdc" && grep -qF ".cursor/rules/fetch-docs/attributes.mdc" ".cursor/rules/fetch-docs/attributes.mdc" && grep -qF ".cursor/rules/fetch-docs/scopes.mdc" ".cursor/rules/fetch-docs/scopes.mdc" && grep -qF ".cursor/rules/publishing_release.mdc" ".cursor/rules/publishing_release.mdc" && grep -qF ".cursor/rules/sdk_dependency_upgrades.mdc" ".cursor/rules/sdk_dependency_upgrades.mdc" && grep -qF ".cursor/rules/upgrade_opentelemetry_instrumentations.mdc" ".cursor/rules/upgrade_opentelemetry_instrumentations.mdc" && grep -qF "- [Scopes (global, isolation, current)](https://develop.sentry.dev/sdk/telemetry" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/add-ai-integration/SKILL.md b/.agents/skills/add-ai-integration/SKILL.md
@@ -0,0 +1,121 @@
+---
+name: add-ai-integration
+description: Add a new AI provider integration to the Sentry JavaScript SDK. Use when contributing a new AI instrumentation (OpenAI, Anthropic, Vercel AI, LangChain, etc.) or modifying an existing one.
+argument-hint: <provider-name>
+---
+
+# Adding a New AI Integration
+
+## Decision Tree
+
+```
+Does the AI SDK have native OpenTelemetry support?
+|- YES -> Does it emit OTel spans automatically?
+|   |- YES (like Vercel AI) -> Pattern 1: OTel Span Processors
+|   +- NO -> Pattern 2: OTel Instrumentation (wrap client)
++- NO -> Does the SDK provide hooks/callbacks?
+    |- YES (like LangChain) -> Pattern 3: Callback/Hook Based
+    +- NO -> Pattern 4: Client Wrapping
+```
+
+## Runtime-Specific Placement
+
+If an AI SDK only works in one runtime, code lives exclusively in that runtime's package. Do NOT add it to `packages/core/`.
+
+- **Node.js-only** -> `packages/node/src/integrations/tracing/{provider}/`
+- **Cloudflare-only** -> `packages/cloudflare/src/integrations/tracing/{provider}.ts`
+- **Browser-only** -> `packages/browser/src/integrations/tracing/{provider}/`
+- **Multi-runtime** -> shared core in `packages/core/src/tracing/{provider}/` with runtime-specific wrappers
+
+## Span Hierarchy
+
+- `gen_ai.invoke_agent` — parent/pipeline spans (chains, agents, orchestration)
+- `gen_ai.chat`, `gen_ai.generate_text`, etc. — child spans (actual LLM calls)
+
+## Shared Utilities (`packages/core/src/tracing/ai/`)
+
+- `gen-ai-attributes.ts` — OTel Semantic Convention attribute constants. **Always use these, never hardcode.**
+- `utils.ts` — `setTokenUsageAttributes()`, `getTruncatedJsonString()`, `truncateGenAiMessages()`, `buildMethodPath()`
+- Only use attributes from [Sentry Gen AI Conventions](https://getsentry.github.io/sentry-conventions/attributes/gen_ai/).
+
+## Streaming
+
+- **Non-streaming:** `startSpan()`, set attributes from response
+- **Streaming:** `startSpanManual()`, accumulate state via async generator or event listeners, set `GEN_AI_RESPONSE_STREAMING_ATTRIBUTE: true`, call `span.end()` in finally block
+- Detect via `params.stream === true`
+- References: `openai/streaming.ts` (async generator), `anthropic-ai/streaming.ts` (event listeners)
+
+## Token Accumulation
+
+- **Child spans:** Set tokens directly from API response via `setTokenUsageAttributes()`
+- **Parent spans (`invoke_agent`):** Accumulate from children using event processor (see `vercel-ai/`)
+
+## Pattern 1: OTel Span Processors
+
+**Use when:** SDK emits OTel spans automatically (Vercel AI)
+
+1. **Core:** Create `add{Provider}Processors()` in `packages/core/src/tracing/{provider}/index.ts` — registers `spanStart` listener + event processor
+2. **Node.js:** Add `callWhenPatched()` optimization in `packages/node/src/integrations/tracing/{provider}/index.ts` — defers registration until package is imported
+3. **Edge:** Direct registration in `packages/cloudflare/src/integrations/tracing/{provider}.ts` — no OTel, call processors immediately
+
+Reference: `packages/node/src/integrations/tracing/vercelai/`
+
+## Pattern 2: OTel Instrumentation (Client Wrapping)
+
+**Use when:** SDK has no native OTel support (OpenAI, Anthropic, Google GenAI)
+
+1. **Core:** Create `instrument{Provider}Client()` in `packages/core/src/tracing/{provider}/index.ts` — Proxy to wrap client methods, create spans manually
+2. **Node.js `instrumentation.ts`:** Patch module exports, wrap client constructor. Check `_INTERNAL_shouldSkipAiProviderWrapping()` for LangChain compatibility.
+3. **Node.js `index.ts`:** Export integration function using `generateInstrumentOnce()` helper
+
+Reference: `packages/node/src/integrations/tracing/openai/`
+
+## Pattern 3: Callback/Hook Based
+
+**Use when:** SDK provides lifecycle hooks (LangChain, LangGraph)
+
+1. **Core:** Create `create{Provider}CallbackHandler()` — implement SDK's callback interface, create spans in callbacks
+2. **Node.js `instrumentation.ts`:** Auto-inject callbacks by patching runnable methods. Disable underlying AI provider wrapping.
+
+Reference: `packages/node/src/integrations/tracing/langchain/`
+
+## Auto-Instrumentation (Node.js)
+
+**Mandatory** for Node.js AI integrations. OTel only patches when the package is imported (zero cost if unused).
+
+### Steps
+
+1. **Add to `getAutoPerformanceIntegrations()`** in `packages/node/src/integrations/tracing/index.ts` — LangChain MUST come first
+2. **Add to `getOpenTelemetryInstrumentationToPreload()`** for OTel-based integrations
+3. **Export from `packages/node/src/index.ts`**: integration function + options type
+4. **Add E2E tests:**
+   - Node.js: `dev-packages/node-integration-tests/suites/tracing/{provider}/`
+   - Cloudflare: `dev-packages/cloudflare-integration-tests/suites/tracing/{provider}/`
+   - Browser: `dev-packages/browser-integration-tests/suites/tracing/ai-providers/{provider}/`
+
+## Key Rules
+
+1. Respect `sendDefaultPii` for `recordInputs`/`recordOutputs`
+2. Set `SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN = 'auto.ai.{provider}'` (alphanumerics, `_`, `.` only)
+3. Truncate large data with helper functions from `utils.ts`
+4. `gen_ai.invoke_agent` for parent ops, `gen_ai.chat` for child ops
+
+## Checklist
+
+- [ ] Runtime-specific code placed only in that runtime's package
+- [ ] Added to `getAutoPerformanceIntegrations()` in correct order (Node.js)
+- [ ] Added to `getOpenTelemetryInstrumentationToPreload()` (Node.js with OTel)
+- [ ] Exported from appropriate package index
+- [ ] E2E tests added and verifying auto-instrumentation
+- [ ] Only used attributes from [Sentry Gen AI Conventions](https://getsentry.github.io/sentry-conventions/attributes/gen_ai/)
+- [ ] JSDoc says "enabled by default" or "not enabled by default"
+- [ ] Documented how to disable (if auto-enabled)
+- [ ] Verified OTel only patches when package imported (Node.js)
+
+## Reference Implementations
+
+- **Pattern 1 (Span Processors):** `packages/node/src/integrations/tracing/vercelai/`
+- **Pattern 2 (Client Wrapping):** `packages/node/src/integrations/tracing/openai/`
+- **Pattern 3 (Callback/Hooks):** `packages/node/src/integrations/tracing/langchain/`
+
+**When in doubt, follow the pattern of the most similar existing integration.**
diff --git a/.agents/skills/release/SKILL.md b/.agents/skills/release/SKILL.md
@@ -0,0 +1,31 @@
+---
+name: release
+description: Publish a new Sentry JavaScript SDK release. Use when preparing a release, updating the changelog, or creating a release branch.
+argument-hint: [VERSION]
+---
+
+# Release Process
+
+See `docs/publishing-a-release.md` for full details.
+
+## Steps
+
+1. Ensure you're on `develop` with latest changes. Stash any unsaved work with `git stash -u` if needed.
+2. Run `yarn changelog` (use `yarn changelog | pbcopy` to copy output).
+3. Decide on a version per [semver](https://semver.org). Check the top of `CHANGELOG.md` for the current version.
+4. Create branch `prepare-release/VERSION` off `develop`.
+5. Update `CHANGELOG.md` — add the new version entry with the changelog output. See the "Updating the Changelog" section in `docs/publishing-a-release.md` for formatting details. Do not remove existing entries.
+6. Commit: `meta(changelog): Update changelog for VERSION`
+7. Push the branch and remind the user to open a PR targeting `master`.
+8. If you were on a different branch, checkout back and `git stash pop` if needed.
+
+## First-time SDK releases
+
+Follow `docs/new-sdk-release-checklist.md`. If anything doesn't match the checklist, remind the user.
+
+## Key commands
+
+- `yarn changelog` — generate changelog entries
+- `yarn lint` — verify code quality
+- `yarn test` — run test suite
+- `yarn build:dev` — verify build
diff --git a/.agents/skills/upgrade-dep/SKILL.md b/.agents/skills/upgrade-dep/SKILL.md
@@ -0,0 +1,59 @@
+---
+name: upgrade-dep
+description: Upgrade a dependency in the Sentry JavaScript SDK. Use when upgrading packages, bumping versions, or fixing security vulnerabilities via dependency updates.
+argument-hint: <package-name>
+---
+
+# Dependency Upgrade
+
+**Only upgrade one package at a time.**
+
+## Upgrade command
+
+```bash
+npx yarn-update-dependency@latest [package-name]
+```
+
+If the dependency is not defined in any `package.json`, run the upgrade from the root workspace (the `yarn.lock` lives there).
+
+Avoid upgrading top-level dependencies (especially test dependencies) without asking the user first.
+
+Ensure updated `package.json` files end with a newline.
+
+## OpenTelemetry constraint
+
+**STOP** if upgrading any `opentelemetry` package would introduce forbidden versions:
+
+- `2.x.x` (e.g., `2.0.0`)
+- `0.2xx.x` (e.g., `0.200.0`, `0.201.0`)
+
+Verify before upgrading:
+
+```bash
+yarn info <package-name>@<version> dependencies
+```
+
+## E2E test dependencies
+
+Do **not** upgrade the major version of a dependency in `dev-packages/e2e-tests/test-applications/*` if the test directory name pins a version (e.g., `nestjs-8` must stay on NestJS 8).
+
+## Post-upgrade verification
+
+```bash
+yarn install
+yarn build:dev
+yarn dedupe-deps:fix
+yarn fix
+yarn circularDepCheck
+```
+
+## Useful commands
+
+```bash
+yarn list --depth=0          # Check dependency tree
+yarn why [package-name]      # Find why a package is installed
+yarn info <pkg> dependencies # Inspect package dependencies
+yarn info <pkg> versions     # Check available versions
+yarn outdated                # Check outdated dependencies
+yarn audit                   # Check for security vulnerabilities
+```
diff --git a/.agents/skills/upgrade-otel/SKILL.md b/.agents/skills/upgrade-otel/SKILL.md
@@ -0,0 +1,32 @@
+---
+name: upgrade-otel
+description: Upgrade OpenTelemetry instrumentations across the Sentry JavaScript SDK. Use when bumping OTel instrumentation packages to their latest versions.
+argument-hint: ''
+---
+
+# Upgrading OpenTelemetry Instrumentations
+
+**All upgrades must be free of breaking changes.** Read each changelog before proceeding.
+
+## 1. `packages/**`
+
+Upgrade in this order:
+
+1. **`@opentelemetry/instrumentation`** to latest. Check changelog: `https://github.com/open-telemetry/opentelemetry-js/blob/main/experimental/CHANGELOG.md`
+2. **All `@opentelemetry/instrumentation-*` packages.** Check each changelog: `https://github.com/open-telemetry/opentelemetry-js-contrib/blob/main/packages/instrumentation-{name}/CHANGELOG.md`
+3. **Third-party instrumentations** (currently `@prisma/instrumentation`). Check their changelogs.
+
+**STOP** if any upgrade introduces breaking changes — fail with the reason.
+
+## 2. `dev-packages/**`
+
+- If an app depends on `@opentelemetry/instrumentation` >= `0.200.x`, upgrade to latest.
+- If an app depends on `@opentelemetry/instrumentation-http` >= `0.200.x`, upgrade to latest.
+
+Same rule: no breaking changes allowed.
+
+## 3. Regenerate lock file
+
+```bash
+yarn install
+```
diff --git a/.cursor/rules/adding-a-new-ai-integration.mdc b/.cursor/rules/adding-a-new-ai-integration.mdc
@@ -1,403 +0,0 @@
----
-description: Guidelines for contributing a new Sentry JavaScript SDK AI integration.
-alwaysApply: true
----
-
-# Adding a New AI Integration
-
-Use these guidelines when contributing a new Sentry JavaScript SDK AI integration.
-
-## Quick Decision Tree
-
-**CRITICAL**
-
-```
-Does the AI SDK have native OpenTelemetry support?
-├─ YES → Does it emit OTel spans automatically?
-│   ├─ YES (like Vercel AI) → Pattern 1: OTEL Span Processors
-│   └─ NO → Pattern 2: OTEL Instrumentation (wrap client)
-└─ NO → Does the SDK provide hooks/callbacks?
-    ├─ YES (like LangChain) → Pattern 3: Callback/Hook Based
-    └─ NO → Pattern 4: Client Wrapping
-
-Multi-runtime considerations:
-- Node.js: Use OpenTelemetry instrumentation
-- Edge (Cloudflare/Vercel): No OTel, processors only or manual wrapping
-```
-
-**IMPORTANT - Runtime-Specific Placement:**
-
-If an AI SDK only works in a specific runtime, the integration code should live exclusively in that runtime's package. Do NOT add it to `packages/core/` or attempt to make it work in other runtimes where it cannot function.
-
-**Runtime-specific integration structures:**
-
-**Node.js-only SDKs** → `packages/node/`
-
-- Core logic: `packages/node/src/integrations/tracing/{provider}/index.ts`
-- OTel instrumentation: `packages/node/src/integrations/tracing/{provider}/instrumentation.ts`
-- Use when SDK only work with Node.js-specific APIs
-
-**Cloudflare Workers-only SDKs** → `packages/cloudflare/`
-
-- Single file: `packages/cloudflare/src/integrations/tracing/{provider}.ts`
-- Use when SDK only works with Cloudflare Workers APIs or Cloudflare AI
-
-**Browser-only SDKs** → `packages/browser/`
-
-- Core logic: `packages/browser/src/integrations/tracing/{provider}/index.ts`
-- Use when SDK requires browser-specific APIs (DOM, WebAPIs, etc.)
-
-**For all runtime-specific SDKs:** DO NOT create `packages/core/src/tracing/{provider}/` - keep everything in the runtime package.
-
-**Multi-runtime SDKs:** If the SDK works across multiple runtimes (Node.js, browser, edge), follow the standard pattern with shared core logic in `packages/core/` and runtime-specific wrappers/instrumentation in each package where needed.
-
----
-
-## Span Hierarchy
-
-**Two span types:**
-
-- `gen_ai.invoke_agent` - Parent/pipeline spans (chains, agents, orchestration)
-- `gen_ai.chat`, `gen_ai.generate_text`, etc. - Child spans (actual LLM calls)
-
-**Hierarchy example:**
-
-```
-gen_ai.invoke_agent (ai.generateText)
-  └── gen_ai.generate_text (ai.generateText.doGenerate)
-```
-
-**References:**
-
-- Vercel AI: `packages/core/src/tracing/vercel-ai/constants.ts`
-- LangChain: `onChainStart` callback in `packages/core/src/tracing/langchain/index.ts`
-
----
-
-## Streaming vs Non-Streaming
-
-**Non-streaming:** Use `startSpan()`, set attributes immediately from response
-
-**Streaming:** Use `startSpanManual()` and prefer event listeners/hooks when available (like Anthropic's `stream.on()`). If not available, use async generator pattern:
-
-```typescript
-interface StreamingState {
-  responseTexts: string[];  // Accumulate fragments
-  promptTokens: number | undefined;
-  completionTokens: number | undefined;
-  // ...
-}
-
-async function* instrumentStream(stream, span, recordOutputs) {
-  const state: StreamingState = { responseTexts: [], ... };
-  try {
-    for await (const event of stream) {
-      processEvent(event, state, recordOutputs);  // Accumulate data
-      yield event;  // Pass through
-    }
-  } finally {
-    setTokenUsageAttributes(span, state.promptTokens, state.completionTokens);
-    span.setAttributes({ [GEN_AI_RESPONSE_STREAMING_ATTRIBUTE]: true });
-    span.end();  // MUST call manually
-  }
-}
-```
-
-**Key rules:**
-
-- Accumulate with arrays/strings, don't overwrite
-- Set `GEN_AI_RESPONSE_STREAMING_ATTRIBUTE: true`
-- Call `span.end()` in finally block
-
-**Detection:** Check request parameters for `stream: true` to determine if response will be streamed.
-
-**References:**
-
-- OpenAI async generator: `instrumentStream` in `packages/core/src/tracing/openai/streaming.ts`
-- Anthropic event listeners: `instrumentMessageStream` in `packages/core/src/tracing/anthropic-ai/streaming.ts`
-- Detection logic: Check `params.stream === true` in `packages/core/src/tracing/openai/index.ts`
-
----
-
-## Token Accumulation
-
-**Child spans (LLM calls):** Set tokens directly from API response
-
-```typescript
-setTokenUsageAttributes(span, inputTokens, outputTokens, totalTokens);
-```
-
-**Parent spans (invoke_agent):** Accumulate from children using event processor
-
-```typescript
-// First pass: accumulate from children
-for (const span of event.spans) {
-  if (span.parent_span_id && isGenAiOperationSpan(span)) {
-    accumulateTokensForParent(span, tokenAccumulator);
-  }
-}
-
-// Second pass: apply to invoke_agent parents
-for (const span of event.spans) {
-  if (span.op === 'gen_ai.invoke_agent') {
-    applyAccumulatedTokens(span, tokenAccumulator);
-  }
-}
-```
-
-**Reference:** `vercelAiEventProcessor` and `accumulateTokensForParent` in `packages/core/src/tracing/vercel-ai/`
-
----
-
-## Shared Utilities
-
-Location: `packages/core/src/tracing/ai/`
-
-### `gen-ai-attributes.ts`
-
-OpenTelemetry Semantic Convention attribute names. **Always use these constants!**
-
-- `GEN_AI_SYSTEM_ATTRIBUTE` - 'openai', 'anthropic', etc.
-- `GEN_AI_REQUEST_MODEL_ATTRIBUTE` - Model from request
-- `GEN_AI_RESPONSE_MODEL_ATTRIBUTE` - Model from response
-- `GEN_AI_INPUT_MESSAGES_ATTRIBUTE` - Input (requires recordInputs)
-- `GEN_AI_RESPONSE_TEXT_ATTRIBUTE` - Output (requires recordOutputs)
-- `GEN_AI_USAGE_INPUT_TOKENS_ATTRIBUTE` - Token counts
-- `GEN_AI_OPERATION_NAME_ATTRIBUTE` - 'chat', 'embeddings', etc.
-
-**CRITICAL - Attribute Usage:**
-
-Only use attributes explicitly listed in the [Sentry Gen AI Conventions](https://getsentry.github.io/sentry-conventions/attributes/gen_ai/). Do NOT create custom attributes or use undocumented ones. If you need a new attribute, it MUST be documented in the conventions first before implementation.
-
-### `utils.ts`
-
-- `setTokenUsageAttributes()` - Set token usage on span
-- `getTruncatedJsonString()` - Truncate for attributes
-- `truncateGenAiMessages()` - Truncate message arrays
-- `buildMethodPath()` - Build method path from traversal
-
----
-
-## Pattern 1: OTEL Span Processors
-
-**Use when:** SDK emits OTel spans automatically (Vercel AI)
-
-### Key Steps
-
-1. **Core:** Create `add{Provider}Processors()` in `packages/core/src/tracing/{provider}/index.ts`
-   - Registers `spanStart` listener + event processor
-   - Post-processes spans to match semantic conventions
-
-2. **Node.js:** Add performance optimization in `packages/node/src/integrations/tracing/{provider}/index.ts`
-   - Use `callWhenPatched()` to defer processor registration
-   - Only register when package is actually imported (see `vercelAIIntegration` function)
-
-3. **Edge:** Direct registration in `packages/cloudflare/src/integrations/tracing/{provider}.ts`
-   - No OTel patching available
-   - Just call `add{Provider}Processors()` immediately
-
-**Reference:** `packages/node/src/integrations/tracing/vercelai/`
-
----
-
-## Pattern 2: OTEL Instrumentation (Client Wrapping)
-
-**Use when:** SDK has NO native OTel support (OpenAI, Anthropic, Google GenAI)
-
-### Key Steps
-
-1. **Core:** Create `instrument{Provider}Client()` in `packages/core/src/tracing/{provider}/index.ts`
-   - Use Proxy to wrap client methods recursively
-   - Create spans manually with `startSpan()` or `startSpanManual()`
-
-2. **Node.js Instrumentation:** Patch module exports in `instrumentation.ts`
-   - Wrap client constructor
-   - Check `_INTERNAL_shouldSkipAiProviderWrapping()` (for LangChain)
-   - See `instrumentOpenAi` in `packages/node/src/integrations/tracing/openai/instrumentation.ts`
-
-3. **Node.js Integration:** Export instrumentation function
-   - Use `generateInstrumentOnce()` helper
-   - See `openAIIntegration` in `packages/node/src/integrations/tracing/openai/index.ts`
-
-**Reference:** `packages/node/src/integrations/tracing/openai/`
-
----
-
-## Pattern 3: Callback/Hook Based
-
-**Use when:** SDK provides lifecycle hooks (LangChain, LangGraph)
-
-### Key Steps
-
-1. **Core:** Create `create{Provider}CallbackHandler()` in `packages/core/src/tracing/{provider}/index.ts`
-   - Implement SDK's callback interface
-   - Create spans in callback methods
-
-2. **Node.js Instrumentation:** Auto-inject callbacks
-   - Patch runnable methods to add handler automatically
-   - **Important:** Disable underlying AI provider wrapping (see `instrumentLangchain` in `packages/node/src/integrations/tracing/langchain/instrumentation.ts`)
-
-**Reference:** `packages/node/src/integrations/tracing/langchain/`
-
----
-
-## Auto-Instrumentation (Out-of-the-Box Support)
-
-**MANDATORY**
-
-**RULE:** AI SDKs should be auto-enabled in Node.js runtime if possible.
-
-✅ **Auto-enable if:**
-
-- SDK works in Node.js runtime
-- OTel only patches when package imported (zero cost if unused)
-
-❌ **Don't auto-enable if:**
-
-- SDK is niche/experimental
-- Integration has significant limitations
-
-### Steps to Auto-Enable
-
-**1. Add to auto performance integrations**
-
-Location: `packages/node/src/integrations/tracing/index.ts`
-
-```typescript
-export function getAutoPerformanceIntegrations(): Integration[] {
-  return [
-    // AI providers - IMPORTANT: LangChain MUST come first!
-    langChainIntegration(),      // Disables underlying providers
-    langGraphIntegration(),
-    vercelAIIntegration(),
-    openAIIntegration(),
-    anthropicAIIntegration(),
-    googleGenAIIntegration(),
-    {provider}Integration(),     // <-- Add here
-  ];
-}
-```
-
-**2. Add to preload instrumentation**
-
-```typescript
-export function getOpenTelemetryInstrumentationToPreload() {
-  return [
-    instrumentOpenAi,
-    instrumentAnthropicAi,
-    instrument{Provider},  // <-- Add here
-  ];
-}
-```
-
-**3. Export from package index**
-
-```typescript
-// packages/node/src/index.ts
-export { {provider}Integration } from './integrations/tracing/{provider}';
-export type { {Provider}Options } from './integrations/tracing/{provider}';
-
-// If browser-compatible: packages/browser/src/index.ts
-export { {provider}Integration } from './integrations/tracing/{provider}';
-```
-
-**4. Add E2E tests**
-
-For Node.js integrations, add tests in `dev-packages/node-integration-tests/suites/tracing/{provider}/`:
-
-- Verify spans created automatically (no manual setup)
-- Test `recordInputs` and `recordOutputs` options
-- Test integration can be disabled
-
-For Cloudflare Workers integrations, add tests in `dev-packages/cloudflare-integration-tests/suites/tracing/{provider}`:
-
-- Create a new worker test app with the AI SDK
-- Verify manual instrumentation creates spans correctly
-- Test in actual Cloudflare Workers runtime (use `wrangler dev` or `miniflare`)
-
-For Browser integrations, add tests in `dev-packages/browser-integration-tests/suites/tracing/ai-providers/{provider}/`:
-
-- Create a new test suite with Playwright
-- Verify manual instrumentation creates spans correctly in the browser
-- Test with actual browser runtime
-
----
-
-## Directory Structure
-
-```
-packages/
-├── core/src/tracing/
-│   ├── ai/                          # Shared utilities
-│   │   ├── gen-ai-attributes.ts
-│   │   ├── utils.ts
-│   │   └── messageTruncation.ts
-│   └── {provider}/                  # Provider-specific
-│       ├── index.ts                 # Main logic
-│       ├── types.ts
-│       ├── constants.ts
-│       └── streaming.ts
-│
-├── node/src/integrations/tracing/{provider}/
-│   ├── index.ts                     # Integration definition
-│   └── instrumentation.ts           # OTel instrumentation
-│
-├── cloudflare/src/integrations/tracing/
-│   └── {provider}.ts                # Single file
-│
-└── vercel-edge/src/integrations/tracing/
-    └── {provider}.ts                # Single file
-```
-
----
-
-## Key Best Practices
-
-1. **Auto-instrumentation is mandatory** - All integrations MUST auto-detect and instrument automatically in Node.js runtime
-2. **Runtime-specific placement** - If SDK only works in one runtime, code lives only in that package
-3. **Respect `sendDefaultPii`** for recordInputs/recordOutputs
-4. **Use semantic attributes** from `gen-ai-attributes.ts` (never hardcode) - Only use attributes from [Sentry Gen AI Conventions](https://getsentry.github.io/sentry-conventions/attributes/gen_ai/)
-5. **Set Sentry origin**: `SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN = 'auto.ai.openai'` (use provider name: `openai`, `anthropic`, `vercelai`, etc. - only alphanumerics, `_`, and `.` allowed)
-6. **Truncate large data**: Use helper functions from `utils.ts`
-7. **Correct span operations**: `gen_ai.invoke_agent` for parent, `gen_ai.chat` for children
-8. **Streaming**: Use `startSpanManual()`, accumulate state, call `span.end()`
-9. **Token accumulation**: Direct on child spans, accumulate on parent from children
-10. **Performance**: Use `callWhenPatched()` for Pattern 1
-11. **LangChain**: Check `_INTERNAL_shouldSkipAiProviderWrapping()` in Pattern 2
-
----
-
-## Reference Implementations
-
-- **Pattern 1 (Span Processors):** `packages/node/src/integrations/tracing/vercelai/`
-- **Pattern 2 (Client Wrapping):** `packages/node/src/integrations/tracing/openai/`
-- **Pattern 3 (Callback/Hooks):** `packages/node/src/integrations/tracing/langchain/`
-
----
-
-## Auto-Instrumentation Checklist
-
-- [ ] If runtime-specific, placed code only in that runtime's package
-- [ ] Added to `getAutoPerformanceIntegrations()` in correct order (Node.js)
-- [ ] Added to `getOpenTelemetryInstrumentationToPreload()` (Node.js with OTel)
-- [ ] Exported from appropriate package index (`packages/node/src/index.ts`, `packages/cloudflare/src/index.ts`, etc.)
-- [ ] Added E2E tests:
-  - [ ] Node.js: `dev-packages/node-integration-tests/suites/tracing/{provider}/`
-  - [ ] Cloudflare: `dev-packages/cloudflare-integration-tests/suites/tracing/{provider}/`
-  - [ ] Browser: `dev-packages/browser-integration-tests/suites/tracing/ai-providers/{provider}/`
-- [ ] E2E test verifies auto-instrumentation (no manual setup required)
-- [ ] Only used attributes from [Sentry Gen AI Conventions](https://getsentry.github.io/sentry-conventions/attributes/gen_ai/)
-- [ ] JSDoc says "enabled by default" or "not enabled by default"
-- [ ] Documented how to disable (if auto-enabled)
-- [ ] Documented limitations clearly
-- [ ] Verified OTel only patches when package imported (Node.js)
-
----
-
-## Questions?
-
-1. Look at reference implementations above
-2. Check shared utilities in `packages/core/src/tracing/ai/`
-3. Review OpenTelemetry Semantic Conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
-
-**When in doubt, follow the pattern of the most similar existing integration!**
diff --git a/.cursor/rules/fetch-docs/attributes.mdc b/.cursor/rules/fetch-docs/attributes.mdc
@@ -1,6 +0,0 @@
----
-description: Use this rule if you need developer documentation about Span Attributes within the Sentry SDKs
-alwaysApply: false
----
-
-Find the SDK developer documentation here: https://develop.sentry.dev/sdk/telemetry/attributes.md
diff --git a/.cursor/rules/fetch-docs/scopes.mdc b/.cursor/rules/fetch-docs/scopes.mdc
@@ -1,6 +0,0 @@
----
-description: Use this rule if you need developer documentation about the concept of Scopes (global, isolation, current) within the Sentry SDKs
-alwaysApply: false
----
-
-Find the SDK developer documentation here: https://develop.sentry.dev/sdk/telemetry/scopes.md
diff --git a/.cursor/rules/publishing_release.mdc b/.cursor/rules/publishing_release.mdc
@@ -1,38 +0,0 @@
----
-description: Use this rule if you are looking to publish a release for the Sentry JavaScript SDKs
-globs:
-alwaysApply: false
----
-
-# Publishing a Release
-
-Use these guidelines when publishing a new Sentry JavaScript SDK release.
-
-## Standard Release Process (from develop to master)
-
-The release process is outlined in [publishing-a-release.md](mdc:docs/publishing-a-release.md).
-
-1. Ensure you're on the `develop` branch with the latest changes:
-   - If you have unsaved changes, stash them with `git stash -u`.
-   - If you're on a different branch than `develop`, check out the develop branch using `git checkout develop`.
-   - Pull the latest updates from the remote repository by running `git pull origin develop`.
-
-2. Run `yarn changelog` on the `develop` branch and copy the output. You can use `yarn changelog | pbcopy` to copy the output of `yarn changelog` into your clipboard.
-3. Decide on a version for the release based on [semver](mdc:https://semver.org). The version should be decided based on what is in included in the release. For example, if the release includes a new feature, we should increment the minor version. If it includes only bug fixes, we should increment the patch version. You can find the latest version in [CHANGELOG.md](mdc:CHANGELOG.md) at the very top.
-4. Create a branch `prepare-release/VERSION`, eg. `prepare-release/8.1.0`, off `develop`.
-5. Update [CHANGELOG.md](mdc:CHANGELOG.md) to add an entry for the next release number and a list of changes since the last release from the output of `yarn changelog`. See the `Updating the Changelog` section in [publishing-a-release.md](mdc:docs/publishing-a-release.md) for more details. Do not remove any changelog entries.
-6. Commit the changes to [CHANGELOG.md](mdc:CHANGELOG.md) with `meta(changelog): Update changelog for VERSION` where `VERSION` is the version of the release, e.g. `meta(changelog): Update changelog for 8.1.0`
-7. Push the `prepare-release/VERSION` branch to origin and remind the user that the release PR needs to be opened from the `master` branch.
-8. In case you were working on a different branch, you can checkout back to the branch you were working on and continue your work by unstashing the changes you stashed earlier with the command `git stash pop` (only if you stashed changes).
-
-## Key Commands
-
-- `yarn changelog` - Generate changelog entries
-- `yarn lint` - Ensure code quality
-- `yarn test` - Run test suite
-- `yarn build:dev` - Verify build
-
-## Important Notes
-
-- This repository uses **Git Flow** - target `develop` for feature PRs, not `master`. See [gitflow.md](mdc:docs/gitflow.md) for more details.
-- For first-time SDK releases, follow the New SDK Release Checklist [new-sdk-release-checklist.md](mdc:docs/new-sdk-release-checklist.md). If you notice there is something not following the new SDK release checklist, please remind the user.
diff --git a/.cursor/rules/sdk_dependency_upgrades.mdc b/.cursor/rules/sdk_dependency_upgrades.mdc
@@ -1,167 +0,0 @@
----
-description: Use this rule if you are looking to upgrade a dependency in the Sentry JavaScript SDKs
-globs:
-alwaysApply: false
----
-
-# Yarn v1 Dependency Upgrades
-
-## Upgrade Process
-
-### Dependency Analysis
-
-```bash
-# Check dependency tree
-yarn list --depth=0
-
-# Find why package is installed
-yarn why [package-name]
-```
-
-### Root Workspace vs. Package Dependencies
-
-**CRITICAL**: Understand the difference between dependency types:
-
-- **Root Workspace dependencies**: Shared dev tools, build tools, testing frameworks
-- **Package dependencies**: Package-specific runtime and dev dependencies
-- Always check if dependency should be in root workspace or package level
-
-### Upgrade Dependencies
-
-**MANDATORY**: Only ever upgrade a single package at a time.
-
-**CRITICAL RULE**: If a dependency is not defined in `package.json` anywhere, the upgrade must be run in the root workspace as the `yarn.lock` file is contained there.
-
-```bash
-# Upgrade specific package to latest compatible version
-npx yarn-update-dependency@latest [package-name]
-```
-
-Avoid upgrading top-level dependencies (defined in `package.json`), especially if they are used for tests. If you are going to upgrade them, ask the user before proceeding.
-
-**REQUIREMENT**: If a `package.json` file is updated, make sure it has a new line at the end.
-
-#### CRITICAL: OpenTelemetry Dependency Constraint
-
-**STOP UPGRADE IMMEDIATELY** if upgrading any dependency with `opentelemetry` in the name and the new version or any of its dependencies uses forbidden OpenTelemetry versions.
-
-**FORBIDDEN VERSION PATTERNS:**
-
-- `2.x.x` versions (e.g., `2.0.0`, `2.1.0`)
-- `0.2xx.x` versions (e.g., `0.200.0`, `0.201.0`)
-
-When upgrading OpenTelemetry dependencies:
-
-1. Check the dependency's `package.json` after upgrade
-2. Verify the package itself doesn't use forbidden version patterns
-3. Verify none of its dependencies use `@opentelemetry/*` packages with forbidden version patterns
-4. **Example**: `@opentelemetry/instrumentation-pg@0.52.0` is forbidden because it bumped to core `2.0.0` and instrumentation `0.200.0`
-5. If forbidden OpenTelemetry versions are detected, **ABORT the upgrade** and notify the user that this upgrade cannot proceed due to OpenTelemetry v2+ compatibility constraints
-
-#### CRITICAL: E2E Test Dependencies
-
-**DO NOT UPGRADE** the major version of dependencies in test applications where the test name explicitly mentions a dependency version.
-
-**RULE**: For `dev-packages/e2e-tests/test-applications/*`, if the test directory name mentions a specific version (e.g., `nestjs-8`), do not upgrade that dependency beyond the mentioned major version.
-
-**Example**: Do not upgrade the nestjs version of `dev-packages/e2e-tests/test-applications/nestjs-8` to nestjs 9 or above because the test name mentions nestjs 8.
-
-## Safety Protocols
-
-### Pre-Upgrade Checklist
-
-**COMPLETE ALL STEPS** before proceeding with any upgrade:
-
-1. **Backup**: Ensure clean git state or create backup branch
-2. **CI Status**: Verify all tests are passing
-3. **Lockfile works**: Confirm `yarn.lock` is in a good state (no merge conflicts)
-4. **OpenTelemetry Check**: For OpenTelemetry dependencies, verify no forbidden version patterns (`2.x.x` or `0.2xx.x`) will be introduced
-
-### Post-Upgrade Verification
-
-```bash
-# rebuild everything
-yarn install
-
-# Build the project
-yarn build:dev
-
-# Make sure dependencies are deduplicated
-yarn dedupe-deps:fix
-
-# Fix any linting issues
-yarn fix
-
-# Check circular dependencies
-yarn circularDepCheck
-```
-
-## Version Management
-
-### Pinning Strategies
-
-- **Exact versions** (`1.2.3`): Use for critical dependencies
-- **Caret versions** (`^1.2.3`): Allow minor updates only
-- **Latest tag**: Avoid as much as possible other than in certain testing and development scenarios
-
-## Troubleshooting
-
-- **Yarn Version**: Run `yarn --version` - must be yarn v1 (not v2/v3/v4)
-- **Lockfile Issues**: Verify yarn.lock exists and is properly maintained. Fix merge conflicts by running `yarn install`
-
-## Best Practices
-
-### Security Audits
-
-```bash
-# Check for security vulnerabilities
-yarn audit
-
-# Fix automatically fixable vulnerabilities
-yarn audit fix
-
-# Install security patches only
-yarn upgrade --security-only
-```
-
-### Check for Outdated Dependencies
-
-```bash
-# Check all outdated dependencies
-yarn outdated
-
-# Check specific package
-yarn outdated [package-name]
-
-# Check dependencies in specific workspace
-yarn workspace [workspace-name] outdated
-```
-
-### Using yarn info for Dependency Inspection
-
-Use `yarn info` to inspect package dependencies before and after upgrades:
-
-```bash
-# Check current version and dependencies
-yarn info <package-name>
-
-# Check specific version dependencies
-yarn info <package-name>@<version>
-
-# Check dependencies field specifically
-yarn info <package-name>@<version> dependencies
-
-# Check all available versions
-yarn info <package-name> versions
-```
-
-The `yarn info` command provides detailed dependency information without requiring installation, making it particularly useful for:
-
-- Verifying OpenTelemetry packages don't introduce forbidden version patterns (`2.x.x` or `0.2xx.x`)
-- Checking what dependencies a package will bring in before upgrading
-- Understanding package version history and compatibility
-
-### Documentation
-
-- Update README or code comments if dependency change affects usage of the SDK or its integrations
-- Notify team of significant changes
diff --git a/.cursor/rules/upgrade_opentelemetry_instrumentations.mdc b/.cursor/rules/upgrade_opentelemetry_instrumentations.mdc
@@ -1,33 +0,0 @@
----
-description: Use this rule if you are looking to grade OpenTelemetry instrumentations for the Sentry JavaScript SDKs
-globs: *
-alwaysApply: false
----
-
-# Upgrading OpenTelemetry instrumentations
-
-1. For every package in packages/\*\*:
-   - When upgrading dependencies for OpenTelemetry instrumentations we need to first upgrade `@opentelemetry/instrumentation` to the latest version.
-     **CRITICAL**: `@opentelemetry/instrumentation` MUST NOT include any breaking changes.
-     Read through the changelog of `@opentelemetry/instrumentation` to figure out if breaking changes are included and fail with the reason if it does include breaking changes.
-     You can find the changelog at `https://github.com/open-telemetry/opentelemetry-js/blob/main/experimental/CHANGELOG.md`
-
-   - After successfully upgrading `@opentelemetry/instrumentation` upgrade all `@opentelemetry/instrumentation-{instrumentation}` packages, e.g. `@opentelemetry/instrumentation-pg`
-     **CRITICAL**: `@opentelemetry/instrumentation-{instrumentation}` MUST NOT include any breaking changes.
-     Read through the changelog of `@opentelemetry/instrumentation-{instrumentation}` to figure out if breaking changes are included and fail with the reason if it does including breaking changes.
-     You can find the changelogs at `https://github.com/open-telemetry/opentelemetry-js-contrib/blob/main/packages/instrumentation-{instrumentation}/CHANGELOG.md`.
-
-   - Finally, upgrade third party instrumentations to their latest versions, these are currently:
-     - @prisma/instrumentation
-
-     **CRITICAL**: Upgrades to third party instrumentations MUST NOT include breaking changes.
-     Read through the changelog of each third party instrumentation to figure out if breaking changes are included and fail with the reason if it does include breaking changes.
-
-2. For packages and apps in dev-packages/\*\*:
-   - If an app depends on `@opentelemetry/instrumentation` >= 0.200.x upgrade it to the latest version.
-     **CRITICAL**: `@opentelemetry/instrumentation` MUST NOT include any breaking changes.
-
-   - If an app depends on `@opentelemetry/instrumentation-http` >= 0.200.x upgrade it to the latest version.
-     **CRITICAL**: `@opentelemetry/instrumentation-http` MUST NOT include any breaking changes.
-
-3. Generate a new yarn lock file.
diff --git a/AGENTS.md b/AGENTS.md
@@ -76,7 +76,7 @@ Uses **Git Flow** (see `docs/gitflow.md`).
 - `packages/core/src/tracing/{provider}/` — Core instrumentation
 - `packages/node/src/integrations/tracing/{provider}/` — Node.js integration + OTel
 - `packages/cloudflare/src/integrations/tracing/{provider}.ts` — Edge runtime
-- See `.cursor/rules/adding-a-new-ai-integration.mdc` for implementation guide
+- Use `/add-ai-integration` skill when adding or modifying integrations
 
 ### User Experience
 
@@ -98,6 +98,11 @@ Uses **Git Flow** (see `docs/gitflow.md`).
 - Never expose secrets or keys
 - When modifying files, cover all occurrences (including `src/` and `test/`)
 
+## Reference Documentation
+
+- [Span Attributes](https://develop.sentry.dev/sdk/telemetry/attributes.md)
+- [Scopes (global, isolation, current)](https://develop.sentry.dev/sdk/telemetry/scopes.md)
+
 ## Skills
 
 ### E2E Testing
@@ -115,3 +120,19 @@ Use `/triage-issue` skill. See `.claude/skills/triage-issue/SKILL.md`
 ### CDN Bundles
 
 Use `/add-cdn-bundle` skill. See `.claude/skills/add-cdn-bundle/SKILL.md`
+
+### Publishing a Release
+
+Use `/release` skill. See `.claude/skills/release/SKILL.md`
+
+### Dependency Upgrades
+
+Use `/upgrade-dep` skill. See `.claude/skills/upgrade-dep/SKILL.md`
+
+### OpenTelemetry Instrumentation Upgrades
+
+Use `/upgrade-otel` skill. See `.claude/skills/upgrade-otel/SKILL.md`
+
+### AI Integration
+
+Use `/add-ai-integration` skill. See `.claude/skills/add-ai-integration/SKILL.md`
PATCH

echo "Gold patch applied."
