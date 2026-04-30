#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lobehub

# Idempotency guard
if grep -qF "description: 'Common recurring mistakes in LobeHub code review \u2014 console leftove" ".agents/skills/review-checklist/SKILL.md" && grep -qF "Before reviewing a PR / diff / branch change, read the **review-checklist** skil" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/review-checklist/SKILL.md b/.agents/skills/review-checklist/SKILL.md
@@ -1,58 +1,51 @@
 ---
-name: code-review
-description: 'Code review checklist for LobeHub. Use when reviewing PRs, diffs, or code changes. Covers correctness, security, quality, and project-specific patterns.'
+name: review-checklist
+description: 'Common recurring mistakes in LobeHub code review — console leftovers, missing return await, hardcoded secrets, hardcoded i18n strings, desktop router pair drift, antd vs @lobehub/ui, non-idempotent migrations, cloud impact red flags. Use as a quick checklist when reviewing PRs, diffs, or branch changes.'
 ---
 
-# Code Review Guide
+# Review Checklist
 
-## Before You Start
-
-1. Read `/typescript` and `/testing` skills for code style and test conventions
-2. Get the diff (skip if already in context, e.g., injected by GitHub review app): `git diff` or `git diff origin/canary..HEAD`
-
-## Checklist
-
-### Correctness
+## Correctness
 
 - Leftover `console.log` / `console.debug` — should use `debug` package or remove
 - Missing `return await` in try/catch — see <https://typescript-eslint.io/rules/return-await/> (not in our ESLint config yet, requires type info)
 - Can the fix/implementation be more concise, efficient, or have better compatibility?
 
-### Security
+## Security
 
 - No sensitive data (API keys, tokens, credentials) in `console.*` or `debug()` output
 - No base64 output to terminal — extremely long, freezes output
 - No hardcoded secrets — use environment variables
 
-### Testing
+## Testing
 
 - Bug fixes must include tests covering the fixed scenario
 - New logic (services, store actions, utilities) should have test coverage
 - Existing tests still cover the changed behavior?
 - Prefer `vi.spyOn` over `vi.mock` (see `/testing` skill)
 
-### i18n
+## i18n
 
 - New user-facing strings use i18n keys, not hardcoded text
 - Keys added to `src/locales/default/{namespace}.ts` with `{feature}.{context}.{action|status}` naming
 - For PRs: `locales/` translations for all languages updated (`pnpm i18n`)
 
-### SPA / routing
+## SPA / routing
 
 - **`desktopRouter` pair:** If the diff touches `src/spa/router/desktopRouter.config.tsx`, does it also update `src/spa/router/desktopRouter.config.desktop.tsx` with the same route paths and nesting? Single-file edits often cause drift and blank screens.
 
-### Reuse
+## Reuse
 
 - Newly written code duplicates existing utilities in `packages/utils` or shared modules?
 - Copy-pasted blocks with slight variation — extract into shared function
 - `antd` imports replaceable with `@lobehub/ui` wrapped components (`Input`, `Button`, `Modal`, `Avatar`, etc.)
 - Use `antd-style` token system, not hardcoded colors; prefer `createStaticStyles` + `cssVar.*` over `createStyles` + `token` unless runtime computation is required
 
-### Database
+## Database
 
 - Migration scripts must be idempotent (`IF NOT EXISTS`, `IF EXISTS` guards)
 
-### Cloud Impact
+## Cloud Impact
 
 A downstream cloud deployment depends on this repo. Flag changes that may require cloud-side updates:
 
@@ -61,13 +54,3 @@ A downstream cloud deployment depends on this repo. Flag changes that may requir
 - **Dependency versions bumped** — e.g., upgrading `next` or `drizzle-orm` in `package.json`
 - **`@lobechat/business-*` exports changed** — e.g., renaming a function in `src/business/` or changing type signatures in `packages/business/`
 - `src/business/` and `packages/business/` must not expose cloud commercial logic in comments or code
-
-## Output Format
-
-For local CLI review only (GitHub review app posts inline PR comments instead):
-
-- Number all findings sequentially
-- Indicate priority: `[high]` / `[medium]` / `[low]`
-- Include file path and line number for each finding
-- Only list problems — no summary, no praise
-- Re-read full source for each finding to verify it's real, then output "All findings verified."
diff --git a/AGENTS.md b/AGENTS.md
@@ -121,4 +121,8 @@ cd packages/database && bunx vitest run --silent='passed-only' '[file]'
 
 - Add keys to a namespace file under `src/locales/default/` (e.g. `agent.ts`, `auth.ts`)
 - For dev preview: translate `locales/zh-CN/` and `locales/en-US/`
-- Don't run `pnpm i18n` - CI handles it
+- `pnpm i18n` is slow; run it manually when locale keys need updating (e.g. before opening a PR).
+
+### Code Review
+
+Before reviewing a PR / diff / branch change, read the **review-checklist** skill (`.agents/skills/review-checklist/SKILL.md`) — it lists the recurring mistakes specific to this codebase.
PATCH

echo "Gold patch applied."
