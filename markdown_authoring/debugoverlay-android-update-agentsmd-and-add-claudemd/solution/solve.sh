#!/usr/bin/env bash
set -euo pipefail

cd /workspace/debugoverlay-android

# Idempotency guard
if grep -qF "Document all executed commands in the hand-off message. If a test is skipped, st" "AGENTS.md" && grep -qF "This repository already contains `AGENTS.md`. Claude should use that document as" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -18,8 +18,8 @@ Welcome! This guide defines how automation and human agents should collaborate i
 ## 2. Code & Build Standards
 
 - **Gradle & AGP**
-    - Project uses Gradle 8.13 and AGP 8.13.0. Any wrapper or plugin changes must remain compatible (JDK 17+).
-    - When upgrading dependencies, confirm repository definitions live in `settings.gradle`. Avoid reintroducing deprecated repositories (e.g., JCenter).
+    - Project tracks tool versions via `gradle/wrapper/gradle-wrapper.properties` (Gradle) and `gradle/libs.versions.toml` (AGP, plugins, dependencies). Keep those files as the single sources of truth; any wrapper or plugin change must remain compatible with JDK 17+.
+    - When upgrading dependencies or plugins, update the catalog (`gradle/libs.versions.toml`) and keep repository definitions centralised in `settings.gradle.kts`. Avoid reintroducing deprecated repositories (e.g., JCenter).
 
 - **Module Conventions**
     - Library modules stick to `namespace` declarations and Java 17 compatibility (`compileOptions`).
@@ -46,13 +46,13 @@ Welcome! This guide defines how automation and human agents should collaborate i
 
 | Change Type | Mandatory Checks |
 |-------------|------------------|
-| Gradle/build logic | `./gradlew help` or a representative assemble task |
+| Gradle/build logic | `./gradlew help`; run the smallest assemble task that exercises your change when artifact wiring is affected |
 | Library runtime code | `./gradlew :debugoverlay:check` (or targeted tests) |
 | Extension modules | `./gradlew :debugoverlay-ext-timber:check` or `./gradlew :debugoverlay-ext-netstats:check` |
 | Sample app UX/UI | `./gradlew :sample:assembleDebug` plus manual sanity if feasible |
 | Documentation only | No build, but ensure links and code snippets compile conceptually |
 
-Document all executed commands in the hand-off message. If a test is skipped, state why and note the risk.
+Document all executed commands in the hand-off message. If a test is skipped, state why and note the risk. For script/config changes (Gradle `.kts`, `libs.versions.toml`, wrapper updates), run a lightweight task such as `./gradlew help` to ensure the configuration still loads.
 
 ---
 
@@ -133,4 +133,4 @@ Use the following structured analysis process when performing code reviews:
 
 ---
 
-Keep this guide visible during sessions. Deviations must be justified in the task notes. Happy debugging!
\ No newline at end of file
+Keep this guide visible during sessions. Deviations must be justified in the task notes. Happy debugging!
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,89 @@
+# DebugOverlay Guide for Claude
+
+This repository already contains `AGENTS.md`. Claude should use that document as the canonical reference and treat this file as a Claude-specific companion that highlights preferred behaviours and common pitfalls. Follow every directive below unless a higher-priority instruction (system > developer > user) explicitly overrides it.
+
+---
+
+## 1. Core Principles
+
+1. **Pause and align** – read the full request, open tasks, and any referenced files before taking action. When requirements are ambiguous or contradictory, ask for clarification instead of guessing.
+2. **Follow instruction priority** – system > developer > user > repo docs (`AGENTS.md`, `CLAUDE.md`) > task context. Resolve conflicts in that order and call them out when they appear.
+3. **Stay conservative** – prefer the minimal change that satisfies the request and avoid speculative edits.
+
+---
+
+## 2. Workflow Checklist
+
+1. `git status -sb` to understand the current branch and pending work.
+2. Review `AGENTS.md` for baseline policies (testing expectations, coding standards, communication style).
+3. Form a short plan (2–5 steps) for any non-trivial task. Update or restate the plan after completing each major step.
+4. Execute changes incrementally. After each significant edit, re-run `git status` to confirm only intended files changed.
+5. Keep notes about commands run, decisions taken, and any blockers—these will feed into the final hand-off.
+
+Use tools deliberately:
+- Prefer `rg`/`fd`/`ls` for discovery.
+- Use `apply_patch` for manual edits; avoid auto-format commands that could produce large style-only diffs unless requested.
+
+---
+
+## 3. Code & Build Expectations (Quick Reference)
+
+- Gradle & AGP versions are defined in `gradle/wrapper/gradle-wrapper.properties` and `gradle/libs.versions.toml`. Update both when tool upgrades are required.
+- All modules now use Kotlin DSL (`*.gradle.kts`) and the central version catalog. When modifying dependencies or plugins:
+  - Add or update aliases in `gradle/libs.versions.toml`.
+  - Reference them via `libs.*` or `libs.plugins.*` in module build scripts.
+- Java/Kotlin toolchains default to Java 17; keep `java { toolchain { languageVersion = JavaLanguageVersion.of(17) } }` unless the user requests a change.
+- Preserve resource prefixes (`resourcePrefix 'debugoverlay_'`) and do not remove default resource directories when adding extra paths (use `res.srcDir(...)` instead of overwriting `srcDirs`).
+- Honour the module list in `AGENTS.md` and avoid creating new modules without approval.
+
+---
+
+## 4. Testing Guidance
+
+| Scenario | Minimum Verification |
+|----------|----------------------|
+| Gradle/build logic or catalog edits | `./gradlew help`; add the smallest assemble task that exercises the affected wiring if artifacts could be impacted |
+| Library runtime changes | `./gradlew :debugoverlay:check` (or narrower unit/integration tasks if only part of the module is touched) |
+| Extension modules | `./gradlew :debugoverlay-ext-timber:check` / `:debugoverlay-ext-netstats:check` as appropriate |
+| Sample app UI/UX | `./gradlew :sample:assembleDebug`, plus manual interaction notes if feasible |
+| Documentation-only edits | No build required, but confirm code snippets compile conceptually |
+
+Always document executed commands and outcomes in the final response. When a test cannot be run (e.g., tooling restriction), explain why and call out the residual risk.
+
+---
+
+## 5. Communication Defaults
+
+- Keep updates short, friendly, and actionable.
+- Reference files using clickable paths with line numbers when possible (e.g., ``debugoverlay/build.gradle.kts:42`` or ``gradle/libs.versions.toml``).
+- Present options as numbered lists when offering alternatives.
+- If blocked (permissions, sandbox limits, missing context), report the issue, propose workarounds, and wait for guidance.
+
+---
+
+## 6. Review Mindset (When Asked to Review)
+
+1. Identify issues first, ordered by severity (critical → major → minor), citing file paths and line numbers.
+2. Focus on functionality, security/privacy, reliability/performance, maintainability, testing coverage, and consistency with project patterns.
+3. Provide concrete remediation suggestions or questions. Mention residual risks or testing gaps even when approving.
+
+---
+
+## 7. Safety & Incident Handling
+
+- Never run destructive Git commands (`git reset --hard`, `git clean -fd`) unless explicitly instructed by the user.
+- If unexpected file changes appear (e.g., unrelated modifications, generated files), stop, describe the observation, and request direction.
+- Preserve secrets: do not print or store contents of `local.properties`, keystores, or other sensitive files.
+
+---
+
+## 8. Final Response Template
+
+Unless the user specifies otherwise, final messages should include:
+1. **Outcome summary** – what was changed, fixed, or investigated.
+2. **Validation** – list commands/tests run, including failures or skipped checks with reasons.
+3. **Follow-ups/Risks** – mention remaining issues, suggested next steps, or verification the user should perform.
+
+---
+
+Keep both `AGENTS.md` and this guide open during sessions. If new conventions emerge (e.g., tool upgrades, testing matrix changes), update both documents in a coordinated PR. Happy collaborating, Claude!
PATCH

echo "Gold patch applied."
