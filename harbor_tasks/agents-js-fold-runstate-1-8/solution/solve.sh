#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agents-js

# Idempotency: if the patch has already been applied, exit early.
if grep -q "tool search item variants, batched computer actions, and GA computer tool" packages/agents-core/src/runState.ts; then
  echo "Patch already applied; skipping."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/implementation-strategy/SKILL.md b/.agents/skills/implementation-strategy/SKILL.md
index 965fc90a5..af6d21472 100644
--- a/.agents/skills/implementation-strategy/SKILL.md
+++ b/.agents/skills/implementation-strategy/SKILL.md
@@ -7,7 +7,7 @@ description: Decide how to implement runtime and API changes in openai-agents-js

 ## Overview

-Use this skill before editing code when the task changes runtime behavior or anything that might look like a compatibility concern. The goal is to keep implementations simple while protecting real released contracts.
+Use this skill before editing code when the task changes runtime behavior or anything that might look like a compatibility concern. The goal is to keep implementations simple while protecting real released contracts and genuinely supported external state.

 ## Quick start

@@ -18,14 +18,14 @@ Use this skill before editing code when the task changes runtime behavior or any
    ```
 3. Judge breaking-change risk against that latest release tag, not against unreleased branch churn or post-tag changes already on `main`.
 4. Prefer the simplest implementation that satisfies the current task. Update callers, tests, docs, and examples directly instead of preserving superseded unreleased interfaces.
-5. Add a compatibility layer only when there is a concrete released consumer or durable external state that requires it, or when the user explicitly asks for a migration path.
+5. Add a compatibility layer only when there is a concrete released consumer, an otherwise supported durable external state that requires it, or when the user explicitly asks for a migration path.

 ## Compatibility boundary rules

 - Released public API or documented external behavior: preserve compatibility or provide an explicit migration path.
-- Persisted schema, serialized state, wire protocol, CLI flags, environment variables, and externally consumed config: treat as compatibility-sensitive even if the implementation is local.
+- Persisted schema, serialized state, wire protocol, CLI flags, environment variables, and externally consumed config: treat as compatibility-sensitive once they are released or otherwise have a supported external consumer. Unreleased post-tag formats that only exist on the current branch can still be rewritten directly.
 - Interface changes introduced only on the current branch: not a compatibility target. Rewrite them directly.
-- Interface changes present on `main` but added after the latest release tag: not a semver breaking change by themselves. Rewrite them directly unless they already define durable external state.
+- Interface changes present on `main` but added after the latest release tag: not a semver breaking change by themselves. Rewrite them directly unless they already back a released or otherwise supported durable format.
 - Internal helpers, private types, same-branch tests, fixtures, and examples: update them directly instead of adding adapters.

 ## Default implementation stance
@@ -38,7 +38,7 @@ Use this skill before editing code when the task changes runtime behavior or any
 ## When to stop and confirm

 - The change would alter behavior shipped in the latest release tag.
-- The change would modify durable external data or protocol formats.
+- The change would modify durable external data or protocol formats that are already released or otherwise supported.
 - The user explicitly asked for backward compatibility, deprecation, or migration support.

 ## Output expectations
@@ -46,4 +46,5 @@ Use this skill before editing code when the task changes runtime behavior or any
 When this skill materially affects the implementation approach, state the decision briefly in your reasoning or handoff, for example:

 - `Compatibility boundary: latest release tag v0.x.y; branch-local interface rewrite, no shim needed.`
+- `Compatibility boundary: latest release tag v0.x.y; unreleased RunState snapshot rewrite, no shim needed.`
 - `Compatibility boundary: released RunState schema; preserve compatibility and add migration coverage.`
diff --git a/.changeset/fold-runstate-schema-1-8.md b/.changeset/fold-runstate-schema-1-8.md
new file mode 100644
index 000000000..59755e05b
--- /dev/null
+++ b/.changeset/fold-runstate-schema-1-8.md
@@ -0,0 +1,5 @@
+---
+'@openai/agents-core': patch
+---
+
+fix: fold unreleased run state schema changes into 1.8
diff --git a/AGENTS.md b/AGENTS.md
index 1d9a7ef26..74cff09d7 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -35,11 +35,11 @@ When working on OpenAI API or OpenAI platform integrations in this repo (Respons

 #### `$implementation-strategy`

-Before changing runtime code, exported APIs, external configuration, persisted schemas, wire protocols, or other user-facing behavior, use `$implementation-strategy` to decide the compatibility boundary and implementation shape. Judge breaking changes against the latest release tag, not unreleased branch-local churn. Interfaces introduced or changed after the latest release tag may be rewritten without compatibility shims unless they define durable external state or the user explicitly asks for a migration path.
+Before changing runtime code, exported APIs, external configuration, persisted schemas, wire protocols, or other user-facing behavior, use `$implementation-strategy` to decide the compatibility boundary and implementation shape. Judge breaking changes against the latest release tag, not unreleased branch-local churn. Interfaces introduced or changed after the latest release tag may be rewritten without compatibility shims unless they already have a released or otherwise supported durable-state consumer, or the user explicitly asks for a migration path.

 ### ExecPlans

-When writing complex features or significant refactors, use an ExecPlan (as described in PLANS.md) from design to implementation. Store each ExecPlan file in the repository root (top level) with a descriptive name. Call out compatibility risk only when the plan changes behavior shipped in the latest release tag or durable external state. Do not treat branch-local interface churn or unreleased post-tag changes on `main` as breaking by default; prefer direct replacement over compatibility layers in those cases. Confirm the approach when changes could impact package consumers or durable external data.
+When writing complex features or significant refactors, use an ExecPlan (as described in PLANS.md) from design to implementation. Store each ExecPlan file in the repository root (top level) with a descriptive name. Call out compatibility risk only when the plan changes behavior shipped in the latest release tag or a released/otherwise supported durable format. Do not treat branch-local interface churn or unreleased post-tag changes on `main` as breaking by default; prefer direct replacement over compatibility layers in those cases. Confirm the approach when changes could impact package consumers or durable external data that is already supported outside the current branch.

 ## Project Structure Guide

@@ -83,7 +83,7 @@ The OpenAI Agents JS repository is a pnpm-managed monorepo that provides:
 - Input guardrails run only on the first turn; interruption resumes should not increment the turn counter.
 - When `conversationId`/`previousResponseId` is provided, only deltas are sent; `callModelInputFilter` must return an input array and keep session persistence in sync.
 - Adding new tool/output/approval item types requires coordinated updates across model output processing, tool execution, turn resolution, streaming events, run item extraction, and RunState serialization.
-- If serialized RunState shape changes, bump the schema version and update serialization/deserialization.
+- If serialized RunState shape changes in a released or otherwise supported snapshot format, bump the schema version and update serialization/deserialization. Unreleased post-tag RunState changes on `main` may fold into the same next schema version when no supported snapshot consumer exists yet.

 ## Operation Guide

diff --git a/packages/agents-core/src/runState.ts b/packages/agents-core/src/runState.ts
index c87557ef8..54ed08cdb 100644
--- a/packages/agents-core/src/runState.ts
+++ b/packages/agents-core/src/runState.ts
@@ -75,10 +75,10 @@ import {
  * - 1.5: Adds optional reasoningItemIdPolicy to preserve reasoning input policy across resume.
  * - 1.6: Adds optional requestId to serialized model responses.
  * - 1.7: Adds optional approval rejection messages.
- * - 1.8: Adds tool search item variants to serialized run state payloads.
- * - 1.9: Adds batched computer actions and GA computer tool aliasing.
+ * - 1.8: Adds tool search item variants, batched computer actions, and GA computer tool
+ *   aliasing to serialized run state payloads.
  */
-export const CURRENT_SCHEMA_VERSION = '1.9' as const;
+export const CURRENT_SCHEMA_VERSION = '1.8' as const;
 const SUPPORTED_SCHEMA_VERSIONS = [
   '1.0',
   '1.1',
@@ -88,7 +88,6 @@ const SUPPORTED_SCHEMA_VERSIONS = [
   '1.5',
   '1.6',
   '1.7',
-  '1.8',
   CURRENT_SCHEMA_VERSION,
 ] as const;
 type SupportedSchemaVersion = (typeof SUPPORTED_SCHEMA_VERSIONS)[number];
@@ -975,7 +974,7 @@ function assertSchemaVersionSupportsToolSearch(
   schemaVersion: SupportedSchemaVersion,
   stateJson: z.infer<typeof SerializedRunState>,
 ): void {
-  if (schemaVersion === '1.8' || schemaVersion === '1.9') {
+  if (schemaVersion === '1.8') {
     return;
   }

PATCH

# Rebuild agents-core so dist reflects the patched source.
pnpm -F @openai/agents-core build

echo "solve.sh applied patch and rebuilt."
