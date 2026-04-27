#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ai-setup

# Idempotency guard
if grep -qF "1. **Choose or create a check file** in `src/scoring/checks/` matching the categ" ".agents/skills/scoring-checks/SKILL.md" && grep -qF "Choose the right file in `src/scoring/checks/` based on category (`existence.ts`" ".cursor/skills/scoring-checks/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/scoring-checks/SKILL.md b/.agents/skills/scoring-checks/SKILL.md
@@ -6,109 +6,102 @@ description: Add a new deterministic scoring check in src/scoring/checks/. Retur
 
 ## Critical
 
-1. **Check must return `Check[]`** — Never return a single check or a Promise. Return an empty array `[]` if the condition fails.
-2. **Use constants from `src/scoring/constants.ts`** — All weights, thresholds, and names must reference constants, never hardcoded values.
-3. **Deterministic only** — No LLM calls. Scoring checks inspect existing files, fingerprint data, and git history. Use `src/fingerprint/` data exclusively.
-4. **File structure**: Create one file per check in `src/scoring/checks/`. Export a default function with signature `(ctx: ScoringContext) => Check[]`.
-5. **Integration point**: Add the check function to the `checks` array in `src/scoring/index.ts` — this is the ONLY place checks are orchestrated.
+1. **Check must return `Check[]`** — Never return a single check or a Promise. Return an empty array `[]` only if there are genuinely zero checks; always push at least one check object.
+2. **Use constants from `src/scoring/constants.ts`** — All `maxPoints` and `earnedPoints` values must reference `POINTS_*` constants; never hardcode numbers.
+3. **Deterministic only** — No LLM calls, no network. Scoring checks use `fs`, `path`, and `execSync` for git commands only.
+4. **File structure**: Add checks to existing category files in `src/scoring/checks/`. Export a **named function** with signature `check{Category}(dir: string): Check[]`.
+5. **Integration point**: Spread the result into `allChecks` in `computeLocalScore()` inside `src/scoring/index.ts`.
 
 ## Instructions
 
-1. **Create the check file** at `src/scoring/checks/{check-name}.ts`.
-   - Import `Check` type from `../types.js`.
+1. **Choose or create a check file** in `src/scoring/checks/` matching the category (`existence.ts`, `quality.ts`, `grounding.ts`, `accuracy.ts`, `freshness.ts`, `bonus.ts`, `sources.ts`).
+   - Import `type { Check }` from `../index.js`.
    - Import constants from `../constants.js`.
-   - Export default function: `export default function {checkName}(ctx: ScoringContext): Check[] { }`
+   - Add a new `export function check{Category}(dir: string): Check[]` function (or add to the existing one).
    - Verify file compiles: `npx tsc --noEmit`.
 
-2. **Inspect the ScoringContext** to access fingerprint data.
-   - Available: `ctx.fingerprint`, `ctx.manifest` (existing config), `ctx.git` (history).
-   - Example: `ctx.fingerprint.sources` (detected sources), `ctx.fingerprint.files` (file tree).
-   - Verify using `src/scoring/__tests__/` test setup to mock context.
+2. **Inspect the filesystem** using the `dir` parameter.
+   - Use `fs.existsSync(join(dir, 'path'))`, `fs.readFileSync(join(dir, 'file'), 'utf-8')`, etc.
+   - For git-based checks: `execSync('git log ...', { cwd: dir })`.
+   - No external APIs, no LLM calls.
 
 3. **Build the Check object**.
-   - `id`: Unique string, lowercase-kebab (e.g., `'existence'`, `'freshness-days-old'`).
-   - `name`: Human-readable display name (e.g., `'CLAUDE.md exists'`).
-   - `points`: Number (0–100). Must reference constant from `src/scoring/constants.ts`.
-   - `reasons`: String array explaining why the check passed/failed (max 1–2 sentences each).
-   - `passed`: Boolean.
-   - Return `[check]` if passed, `[]` if failed.
+   - `id`: Unique kebab-case string (e.g., `'claude_md_exists'`, `'skills_count'`).
+   - `name`: Human-readable display name.
+   - `category`: One of `'existence' | 'quality' | 'grounding' | 'accuracy' | 'freshness' | 'bonus'`.
+   - `maxPoints` / `earnedPoints`: Must reference `POINTS_*` constants.
+   - `passed`: `earnedPoints >= Math.ceil(maxPoints * 0.6)` (or custom logic).
+   - `detail`: Human-friendly message explaining the result.
+   - Optional: `suggestion` (if not passed) and `fix` object with `action`, `data`, `instruction`.
 
 4. **Reference constants for all numeric values**.
-   - Open `src/scoring/constants.ts` and use existing constants or add new ones.
-   - Example: `const POINTS_EXISTENCE = 10` in constants, then use `points: POINTS_EXISTENCE` in check.
-   - Verify constant is exported: `export const POINTS_EXISTENCE = 10`.
+   - Add new constants to `src/scoring/constants.ts` if needed.
+   - Example: `export const POINTS_YOUR_CHECK = 4;` then use `maxPoints: POINTS_YOUR_CHECK`.
 
-5. **Add the check to the orchestrator** in `src/scoring/index.ts`.
-   - Import: `import {checkName} from './checks/{check-name}.js'`.
-   - Add to `checks` array: `{checkName}(ctx),`.
-   - Verify tests pass: `npm test -- src/scoring/__tests__/index.test.ts`.
+5. **Register in src/scoring/index.ts**.
+   - The existing category functions (`checkExistence`, `checkQuality`, etc.) are already called in `computeLocalScore()`.
+   - If adding a new function: import it and spread into `allChecks`.
+   - Verify tests pass: `npm test -- src/scoring/__tests__/`.
 
-6. **Write a test** in `src/scoring/checks/__tests__/{check-name}.test.ts`.
-   - Mock `ScoringContext` with fingerprint data using `memfs` or fixtures from existing tests.
-   - Test both pass and fail cases.
-   - Verify test runs: `npx vitest run src/scoring/checks/__tests__/{check-name}.test.ts`.
+6. **Write a test** in `src/scoring/checks/__tests__/{category}.test.ts`.
+   - Use `mkdtempSync` to create a temp directory; write files to simulate conditions.
+   - Test both passing and failing cases.
+   - Verify: `npx vitest run src/scoring/checks/__tests__/{category}.test.ts`.
 
 ## Examples
 
 **User says**: "Add a scoring check that verifies CLAUDE.md exists and is not empty."
 
 **Actions**:
-1. Create `src/scoring/checks/existence.ts`:
+1. In `src/scoring/checks/existence.ts`, add to the `checkExistence(dir: string): Check[]` function:
 ```typescript
-import type { Check, ScoringContext } from '../types.js';
-import { POINTS_EXISTENCE } from '../constants.js';
-
-export default function existence(ctx: ScoringContext): Check[] {
-  const claudeMd = ctx.manifest.claude;
-  const passed = claudeMd && claudeMd.trim().length > 0;
-
-  if (!passed) {
-    return [];
-  }
-
-  return [{
-    id: 'existence',
+import type { Check } from '../index.js';
+import { POINTS_CLAUDE_MD_EXISTS } from '../constants.js';
+import { existsSync, readFileSync } from 'fs';
+import { join } from 'path';
+
+export function checkExistence(dir: string): Check[] {
+  const checks: Check[] = [];
+  const claudeMdPath = join(dir, 'CLAUDE.md');
+  const exists = existsSync(claudeMdPath);
+  const nonEmpty = exists && readFileSync(claudeMdPath, 'utf-8').trim().length > 0;
+  const earned = nonEmpty ? POINTS_CLAUDE_MD_EXISTS : 0;
+  checks.push({
+    id: 'claude_md_exists',
     name: 'CLAUDE.md exists and is not empty',
-    points: POINTS_EXISTENCE,
-    reasons: ['CLAUDE.md is present and contains configuration.'],
-    passed: true,
-  }];
+    category: 'existence',
+    maxPoints: POINTS_CLAUDE_MD_EXISTS,
+    earnedPoints: earned,
+    passed: earned > 0,
+    detail: exists ? (nonEmpty ? 'CLAUDE.md present and non-empty' : 'CLAUDE.md is empty') : 'CLAUDE.md missing',
+  });
+  return checks;
 }
 ```
 
-2. Add to `src/scoring/constants.ts`: `export const POINTS_EXISTENCE = 10`.
+2. Add to `src/scoring/constants.ts`: `export const POINTS_CLAUDE_MD_EXISTS = 10;`
 
-3. Update `src/scoring/index.ts`:
-```typescript
-import existence from './checks/existence.js';
-// ...
-const checks = [
-  existence(ctx),
-  // other checks
-];
-```
+3. `checkExistence` is already called in `computeLocalScore()` in `src/scoring/index.ts` — no changes needed there.
 
-4. Test with `npm test`.
+4. Test with `npm test -- src/scoring/`.
 
-**Result**: Check is integrated and appears in score output.
+**Result**: Check appears in score output under the existence category.
 
 ## Common Issues
 
 **"Check is not appearing in score output"**
-- Verify check is added to `checks` array in `src/scoring/index.ts`.
-- Verify it returns `Check[]` (not a single object or Promise).
+- Verify the check ID is not in a `*_ONLY_CHECKS` set that excludes your target agent.
+- Verify the function is called (or its result is spread) in `computeLocalScore()` in `src/scoring/index.ts`.
 - Run `npm run build && npm test` to ensure no import errors.
 
-**"Type error: ScoringContext has no property X"**
-- Check `src/scoring/types.ts` for available context properties.
-- Use `ctx.fingerprint`, `ctx.manifest`, `ctx.git` — not custom properties.
-- Verify fingerprint data exists in test fixture: `console.log(ctx)` in test.
+**"Points are hardcoded but should use constants"**
+- Replace all literal numbers like `earnedPoints: 5` with `earnedPoints: POINTS_YOUR_CHECK`.
+- Constants are in `src/scoring/constants.ts` — add new ones if needed.
 
-**"Constant is undefined"**
-- Open `src/scoring/constants.ts` and confirm constant is exported.
-- Use `npm run build` to catch missing exports.
-- Add new constants if needed and commit to constants.ts first.
+**"Platform-specific check appears for wrong agent"**
+- Add check ID to the appropriate `*_ONLY_CHECKS` set in `src/scoring/constants.ts`.
+- Verify `filterChecksForTarget()` in `src/scoring/index.ts` handles your platform set.
 
-**"Test fails with 'memfs is not found'"**
-- Import from test setup: `import { vol } from 'memfs'`.
-- See existing tests in `src/scoring/checks/__tests__/` for memfs usage patterns.
\ No newline at end of file
+**"Test fails with file not found"**
+- Use `mkdtempSync` to create a real temp directory; write files with `writeFileSync`.
+- Always clean up in a `finally` block: `rmSync(dir, { recursive: true })`.
\ No newline at end of file
diff --git a/.cursor/skills/scoring-checks/SKILL.md b/.cursor/skills/scoring-checks/SKILL.md
@@ -6,135 +6,132 @@ description: Adds a new deterministic scoring check in src/scoring/checks/. Foll
 
 ## Critical
 
-- **All checks must be deterministic**: No randomness, no timestamps. Same input → same output.
-- **Return type is always `Check[]`**: Each check has `id`, `name`, `weight`, `maxScore`, `score`, `reasons`.
-- **Weights must sum to 100** across all checks in `src/scoring/index.ts`. Verify: `existenceWeight + qualityWeight + groundingWeight + accuracyWeight + freshnessWeight + bonusWeight + sourcesWeight === 100`.
-- **Only import from `src/scoring/constants.ts`** for weight/threshold values. Never hardcode thresholds.
-- **Check logic is synchronous**. No async/await in check functions.
+- **All checks must be deterministic**: No randomness, no external APIs. Same filesystem state → same result.
+- **Return type is always `Check[]`**: Each check has `id`, `name`, `category`, `maxPoints`, `earnedPoints`, `passed`, `detail`.
+- **Function signature**: `export function check{Category}(dir: string): Check[]` — takes a directory path, not a fingerprint or config object.
+- **Only import from `src/scoring/constants.ts`** for `POINTS_*` values. Never hardcode numbers.
+- **Check logic is synchronous**. No async/await. Use `fs`, `path`, and `execSync` for git commands.
 
 ## Instructions
 
-### Step 1: Define the check function in a new file
+### Step 1: Add check to the appropriate category file
 
-Create `src/scoring/checks/<checkName>.ts`.
+Choose the right file in `src/scoring/checks/` based on category (`existence.ts`, `quality.ts`, `grounding.ts`, `accuracy.ts`, `freshness.ts`, `bonus.ts`, `sources.ts`). Add your logic to that file's exported function.
 
 Use this template:
 
 ```typescript
-import { Check } from '../types.js';
-import { <CONSTANT_NAME> } from '../constants.js';
-
-export function <checkName>(
-  fingerprint: Fingerprint,
-  config: ParsedConfig,
-): Check[] {
-  const checkId = '<checkName>';
-  let score = 0;
-  const reasons: string[] = [];
-
-  // Logic here: inspect fingerprint/config, calculate score 0–maxScore
-  // Add reason strings for each deduction
-
-  return [
-    {
-      id: checkId,
-      name: 'Check Display Name',
-      weight: <WEIGHT_CONSTANT>,
-      maxScore: 100,
-      score,
-      reasons,
-    },
-  ];
+import type { Check } from '../index.js';
+import { POINTS_YOUR_CHECK, YOUR_THRESHOLD_ARRAY } from '../constants.js';
+import { existsSync, readFileSync } from 'fs';
+import { join } from 'path';
+
+export function checkYourCategory(dir: string): Check[] {
+  const checks: Check[] = [];
+
+  // Inspect the filesystem using `dir`
+  const metric = /* e.g., count files, parse content */;
+  const threshold = YOUR_THRESHOLD_ARRAY.find(t => metric >= t.minValue);
+  const earned = threshold?.points ?? 0;
+
+  checks.push({
+    id: 'your_unique_check_id',
+    name: 'Human-readable check name',
+    category: 'quality', // matches the category file
+    maxPoints: POINTS_YOUR_CHECK,
+    earnedPoints: earned,
+    passed: earned >= Math.ceil(POINTS_YOUR_CHECK * 0.6),
+    detail: `${earned}/${POINTS_YOUR_CHECK} points — ${metric} items found`,
+    suggestion: earned >= POINTS_YOUR_CHECK ? undefined : 'Action to improve',
+  });
+
+  return checks;
 }
 ```
 
-Verify the function returns exactly one `Check` object (or multiple if logically grouped). Verify `score` is between 0 and `maxScore`.
+Verify the function signature is `check{Category}(dir: string): Check[]` — NOT `(fingerprint, config)` or `(ctx: ScoringContext)`.
 
-### Step 2: Export from `src/scoring/checks/index.ts`
-
-Add the import and export:
-
-```typescript
-export { <checkName> } from './<checkName>.js';
-```
-
-Verify file is listed in the barrel export.
-
-### Step 3: Call the check in `src/scoring/index.ts`
-
-In the `score()` function, add a line:
+### Step 2: Add point constants in `src/scoring/constants.ts`
 
 ```typescript
-const <checkName>Results = <checkName>(fingerprint, config);
-allChecks.push(...<checkName>Results);
+export const POINTS_YOUR_CHECK = 4; // fits within category budget
 ```
 
-Verify placement is before the weight-sum validation at the end of `score()`.
+Check the `CATEGORY_MAX` object to ensure your check fits within its category's point budget.
 
-### Step 4: Update weight constants in `src/scoring/constants.ts`
+### Step 3: Register new function in `src/scoring/index.ts` (if adding a new function)
 
-If adding a new check type (not modifying an existing one), add the weight constant:
+If you created a new function (rather than adding to an existing one):
 
 ```typescript
-export const <CHECK_NAME>_WEIGHT = <number>;
+import { checkYourCategory } from './checks/your-file.js';
+// In computeLocalScore():
+const allChecks: Check[] = [
+  ...checkExistence(dir),
+  ...checkQuality(dir),
+  ...checkYourCategory(dir), // ← ADD IN ORDER
+  ...checkFreshness(dir),
+  ...checkBonus(dir),
+];
 ```
 
-Then update all other weight constants so the sum remains 100. Verify the weights comment block lists all active checks.
-
-Verify: Run `npm run test -- src/scoring/__tests__/index.test.ts` to ensure weight validation passes.
+### Step 4: Handle platform-specific filtering (if applicable)
 
-### Step 5: Write or update the test
+If the check only applies to certain platforms, add its ID to a `*_ONLY_CHECKS` set in `src/scoring/constants.ts`.
 
-In `src/scoring/__tests__/`, create or update `<checkName>.test.ts`. Test both pass and fail cases:
+### Step 5: Write a test
 
 ```typescript
-it('returns maxScore when condition is met', () => {
-  const result = <checkName>({ /* fingerprint */ }, { /* config */ });
-  expect(result[0].score).toBe(100);
-});
-
-it('returns 0 when condition is not met', () => {
-  const result = <checkName>({ /* fingerprint */ }, { /* config */ });
-  expect(result[0].score).toBe(0);
-  expect(result[0].reasons.length).toBeGreaterThan(0);
+import { mkdtempSync, writeFileSync, rmSync } from 'fs';
+import { join } from 'path';
+import { checkYourCategory } from '../your-file.js';
+
+it('awards full points when condition passes', () => {
+  const dir = mkdtempSync('test-scoring-');
+  try {
+    writeFileSync(join(dir, 'SOME_FILE.md'), 'content');
+    const checks = checkYourCategory(dir);
+    const check = checks.find(c => c.id === 'your_unique_check_id');
+    expect(check?.passed).toBe(true);
+    expect(check?.earnedPoints).toBe(POINTS_YOUR_CHECK);
+  } finally {
+    rmSync(dir, { recursive: true });
+  }
 });
 ```
 
-Verify: Run `npm run test -- src/scoring/__tests__/<checkName>.test.ts`.
+Verify: `npm run test -- src/scoring/checks/__tests__/{category}.test.ts`.
 
 ## Examples
 
 **User says**: "Add a scoring check that penalizes repos without a CLAUDE.md file."
 
 **Actions**:
-1. Create `src/scoring/checks/existence.ts` (or modify if exists).
-2. Check if `config.claudeMdPath` exists and is non-empty: if yes, `score = 100`; if no, `score = 0` with reason "CLAUDE.md not found".
-3. Add export to `src/scoring/checks/index.ts`.
-4. Call `existenceResults = existence(fingerprint, config)` in `src/scoring/index.ts` and push to `allChecks`.
-5. Ensure weight is defined in `constants.ts` (e.g., `EXISTENCE_WEIGHT = 20`).
-6. Test: `npm run test -- src/scoring/__tests__/existence.test.ts`.
+1. In `src/scoring/checks/existence.ts`, add to the `checkExistence(dir: string): Check[]` function:
+   - `const exists = existsSync(join(dir, 'CLAUDE.md'));`
+   - Push a check with `id: 'claude_md_exists'`, `maxPoints: POINTS_CLAUDE_MD_EXISTS`, `earnedPoints: exists ? POINTS_CLAUDE_MD_EXISTS : 0`.
+2. Add `export const POINTS_CLAUDE_MD_EXISTS = 10;` to `src/scoring/constants.ts`.
+3. `checkExistence` is already called in `computeLocalScore()` — no `src/scoring/index.ts` changes needed.
+4. Test: create temp dir with/without `CLAUDE.md`, call `checkExistence(dir)`, verify `passed` and `earnedPoints`.
 
-## Common Issues
+**Result**: Check appears in score output under the existence category.
 
-**Error: "Weights do not sum to 100"**
-- Check `src/scoring/index.ts` at the end of `score()`: find the validation that sums all weights.
-- List all active checks and their weights from `constants.ts`.
-- Adjust the weight constant so the sum equals 100. Example: if adding a new check with weight 15, reduce an existing check's weight by 15.
+## Common Issues
 
-**Error: "Check returned undefined score"**
-- Ensure the check function always initializes `score` to a number before any logic.
-- Verify no conditional path leaves `score` unset.
-- Check must always return a `Check` object with `score` field.
+**"My check doesn't appear in the score report"**
+- Verify the check ID is not in a `*_ONLY_CHECKS` set that excludes your target agent.
+- Verify the category function is called and its result is spread into `allChecks` in `computeLocalScore()`.
+- Run `npm run build && npm test` to catch import errors.
 
-**Error: "Test fails with 'score out of bounds'"**
-- Verify `score` is >= 0 and <= `maxScore` (usually 100).
-- Check logic should cap: `Math.max(0, Math.min(maxScore, score))`.
-- Verify no negative deductions drop score below 0.
+**"Points are hardcoded"**
+- Replace literal numbers with `POINTS_*` constants from `src/scoring/constants.ts`.
+- Add a new constant if one doesn't exist for your check.
 
-**Error: "Check is called twice or results are duplicated in allChecks"**
-- Ensure `<checkName>()` is called exactly once in `src/scoring/index.ts`.
-- Verify you push the result array with spread: `allChecks.push(...result)` not `allChecks.push(result)`.
+**"Type error: Property X does not exist on Check"**
+- The `Check` interface in `src/scoring/index.ts` requires: `id`, `name`, `category`, `maxPoints`, `earnedPoints`, `passed`, `detail`.
+- Optional fields: `suggestion`, `fix` (object with `action`, `data`, `instruction`).
+- Do NOT use `score`, `weight`, `reasons` — those are from a different shape.
 
-**Error: "Fingerprint/config types are unknown"**
-- Import `Fingerprint` from `src/fingerprint/types.js` and `ParsedConfig` from `src/commands/types.js` (or check existing check files for the correct imports).
-- Match the type signature of an existing check function.
\ No newline at end of file
+**"Test fails — can't create real files"**
+- Use `mkdtempSync` to create a temp dir; write files with `writeFileSync`; clean up with `rmSync(dir, { recursive: true })` in a `finally` block.
+- See `src/scoring/checks/__tests__/` for existing patterns.
\ No newline at end of file
PATCH

echo "Gold patch applied."
