#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ai-setup

# Idempotency guard
if grep -qF "- **\"ENOENT: no such file or directory\"** \u2014 Ensure `fs.mkdirSync(parentDir, { re" ".agents/skills/writers-pattern/SKILL.md" && grep -qF "2. Implement `export function writeGithubCopilotConfig(config: GithubCopilotConf" ".cursor/skills/writers-pattern/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/writers-pattern/SKILL.md b/.agents/skills/writers-pattern/SKILL.md
@@ -6,12 +6,11 @@ description: Adds a new platform writer in src/writers/ following existing patte
 
 ## Critical
 
-- Each writer MUST export a default function matching the signature: `(config: WriterConfig, skillLines: SkillLine[]) => Promise<string[]>`
-- Writer MUST return full file paths written, not relative paths
-- All writers MUST be exported in `src/writers/index.ts` as named exports
-- Writer files live in `src/writers/{platform}/index.ts` with sibling `__tests__/index.test.ts`
-- Configuration object (`WriterConfig`) is shared across all writers — inspect `src/writers/claude/index.ts` for the exact shape
-- Never hardcode file paths or extension detection — use the `config` object and `skillLines` array passed in
+- Each writer MUST export a **named synchronous** function: `export function write{Platform}Config(config: {PlatformConfig}): string[]`
+- Writer MUST return `string[]` of written file paths (NOT `Promise<string[]>`) — all file I/O uses synchronous `fs` APIs
+- Writers are called from `writeSetup()` in `src/writers/index.ts`; they must be synchronous to compose correctly
+- Writer files live in `src/writers/{platform}/index.ts` with a platform-specific config interface defined in the same file
+- Never use default exports — `src/writers/index.ts` imports all writers by their named export
 
 ## Instructions
 
@@ -21,56 +20,54 @@ description: Adds a new platform writer in src/writers/ following existing patte
    - Verify directory does not already exist: `ls -la src/writers/{platform}/` should return error
 
 2. **Implement writer function signature**
-   - Import `WriterConfig` and `SkillLine` from `src/writers/index.ts`
-   - Export default async function: `export default async function write{Platform}(config: WriterConfig, skillLines: SkillLine[]): Promise<string[]>`
-   - Function receives `config` with properties: `cwd`, `platform`, `agent`, `token` (optional), `quiet` (boolean)
-   - Function receives `skillLines` array of objects with `name`, `description`, `path`, `markdown` properties
-   - Return array of absolute file paths written (e.g., `['/path/to/file1', '/path/to/file2']`)
+   - Define a platform-specific config interface at the top of the file (see `src/writers/claude/index.ts` for shape)
+   - Export named synchronous function: `export function write{Platform}Config(config: {PlatformConfig}): string[]`
+   - Initialize `const written: string[] = []` to track all written paths
+   - Use synchronous `fs.writeFileSync` and `fs.mkdirSync` — no async/await
+   - Return the `written` array at the end
 
 3. **Implement core write logic**
-   - Determine target directory from `config.cwd` (entry point for all writes)
-   - For each skill in `skillLines`, generate platform-specific file(s)
-   - Match file structure of existing writer: inspect `src/writers/claude/index.ts` lines 1–50 for pattern (typically generates SKILL.md or equivalent)
-   - Use `await fs.promises.writeFile()` or Caliber's `writeFile()` helper if available
-   - Catch and handle write errors — log to stderr if `config.quiet` is false
-   - Use `path.resolve()` and `path.join()` for all path operations
+   - For the main config file: use content-wrapping helpers from `src/writers/pre-commit-block.ts` (e.g., `appendPreCommitBlock`, `appendLearningsBlock`)
+   - For rules: create `<platform>/rules/` directory, write each rule, push paths to `written`
+   - For skills: create `<platform>/skills/<name>/` directory, write `SKILL.md` with YAML frontmatter, push paths to `written`
+   - For MCP servers: read existing JSON (if any), merge with spread operator, write back
+   - All writes use `fs.writeFileSync`; all directory creation uses `fs.mkdirSync(dir, { recursive: true })`
 
 4. **Add test file**
-   - Create `src/writers/{platform}/__tests__/index.test.ts` with vitest imports
-   - Test the writer function with mock `WriterConfig` and `SkillLine[]` inputs
-   - Assert that returned `string[]` contains expected file paths
-   - Mock file I/O if needed using memfs or spy on `fs.promises.writeFile`
-   - Verify at least one skill is written per test case
+   - Create `src/writers/__tests__/{platform}.test.ts` following the vitest pattern in `src/writers/__tests__/codex.test.ts`
+   - Mock `fs` module: `vi.mock('fs')`
+   - Test that main config file is written to correct path and returned in the array
+   - Test skill frontmatter format is correct
+   - Verify test runs: `npm test -- src/writers/__tests__/{platform}.test.ts`
 
-5. **Export writer in src/writers/index.ts**
-   - Open `src/writers/index.ts`
-   - Add import: `import write{Platform} from './{platform}/index.js'`
-   - Export as named export in the module exports object (inspect existing claude, cursor, codex exports)
-   - Verify import uses `.js` extension (ESM convention in this project)
+5. **Register in src/writers/index.ts**
+   - Add import: `import { write{Platform}Config } from './{platform}/index.js'`
+   - Add platform to `AgentSetup.targetAgent` tuple
+   - Add `{platform}?: Parameters<typeof write{Platform}Config>[0]` to `AgentSetup`
+   - Add conditional write block in `writeSetup()` and `getFilesToWrite()`
 
 6. **Verify integration**
    - Run `npm run build` — must compile without errors
-   - Run `npm run test -- src/writers/{platform}/__tests__/` — all tests pass
-   - Run `npm run lint` — no linting errors in new writer code
-   - Inspect `src/writers/index.ts` to confirm new writer is exported and callable
+   - Run `npm run test` — all tests pass
+   - Run `npx tsc --noEmit` — no type errors
 
 ## Examples
 
 **User says**: "Add support for a new agent platform called Jetbrains"
 
 **Actions**:
-1. Create `src/writers/jetbrains/index.ts`
-2. Implement `export default async function writeJetbrains(config: WriterConfig, skillLines: SkillLine[]): Promise<string[]>` — reads `config.cwd`, iterates `skillLines`, writes files to `.jetbrains/rules/` (or platform-specific dir)
-3. Create `src/writers/jetbrains/__tests__/index.test.ts` with tests
-4. Add to `src/writers/index.ts`: `import writeJetbrains from './jetbrains/index.js'` and export
-5. Run build + tests + lint — all pass
+1. Create `src/writers/jetbrains/index.ts` with a `JetbrainsConfig` interface
+2. Implement `export function writeJetbrainsConfig(config: JetbrainsConfig): string[]` — synchronous, uses `fs.writeFileSync`, returns `written` array
+3. Create `src/writers/__tests__/jetbrains.test.ts` using `vi.mock('fs')` pattern from `codex.test.ts`
+4. Add to `src/writers/index.ts`: import `{ writeJetbrainsConfig }`, add to `AgentSetup`, call in `writeSetup()`
+5. Run `npm run build && npm run test` — all pass
 
-**Result**: New writer available via `writeSetup()` orchestration; each skill generates a file in the platform-specific directory and returns full paths written.
+**Result**: New writer available via `writeSetup()` orchestration; files are written synchronously and paths are returned.
 
 ## Common Issues
 
-- **Type error: 'WriterConfig' not found** — Ensure import is `import type { WriterConfig, SkillLine } from '../index.js'` (use `type` keyword for type imports)
-- **Function returns relative paths instead of absolute** — Use `path.resolve(config.cwd, relativePath)` to construct full paths; all returned paths must be absolute
-- **Writer not callable in index.ts exports** — Verify default export function in `{platform}/index.ts` is async and returns `Promise<string[]>`, then check `index.ts` import uses `.js` extension
-- **Tests fail with 'Cannot find module'** — Confirm `__tests__/index.test.ts` imports writer as `import write{Platform} from '../index.js'` (relative path, ESM)
+- **"TypeError: write{Platform}Config is not a function"** — Verify the function is exported: `export function write{Platform}Config(...)`. Missing `export` is a common mistake.
+- **"ENOENT: no such file or directory"** — Ensure `fs.mkdirSync(parentDir, { recursive: true })` is called BEFORE `fs.writeFileSync(filePath, ...)`. See `src/writers/claude/index.ts` for correct order.
+- **"Skill file has no frontmatter"** — Frontmatter format must be `---\nname: ...\ndescription: ...\n---\n<content>` (no extra blank lines). Compare with `src/writers/claude/index.ts` lines 40–48.
+- **"written array is empty but files were created"** — Every `fs.writeFileSync()` call must be followed by `written.push(filePath)`. Check every file operation.
 - **Build fails: 'platform' already exists** — Check if `src/writers/{platform}/` dir exists from prior attempt; remove or use different platform name
\ No newline at end of file
diff --git a/.cursor/skills/writers-pattern/SKILL.md b/.cursor/skills/writers-pattern/SKILL.md
@@ -6,12 +6,11 @@ description: Adds a new platform writer in src/writers/ following existing patte
 
 ## Critical
 
-- Writers MUST return `string[]` (array of file paths written)
-- Each writer lives in `src/writers/{platform}/index.ts` with a named export `writeSetup(setup: WriteSetup): Promise<string[]>`
-- Writers are registered in `src/writers/index.ts` in the `writers` Map and exported from `getWriters()`
-- All writers follow the exact signature: `(setup: WriteSetup) => Promise<string[]>`
-- Test files go in `src/writers/{platform}/__tests__/` matching vitest conventions
-- Writers are async and must handle file I/O via fs promises (not sync)
+- Writers MUST return `string[]` (array of file paths written) — **synchronously**, not `Promise<string[]>`
+- Each writer lives in `src/writers/{platform}/index.ts` with a named export `write{Platform}Config(config: {PlatformConfig}): string[]`
+- Writers are registered in `src/writers/index.ts` within the `writeSetup()` function (not a Map)
+- All file I/O uses synchronous `fs` APIs (`fs.writeFileSync`, `fs.mkdirSync`)
+- Test files go in `src/writers/__tests__/{platform}.test.ts` (not nested under the writer directory)
 
 ## Instructions
 
@@ -25,82 +24,87 @@ Read `src/writers/claude/index.ts`, `src/writers/cursor/index.ts`, and `src/writ
 Verify the `WriteSetup` type includes: `claudeMd`, `rules`, `agents`, `hooks`, `skills`, `manifest`.
 
 **Step 2: Create platform directory**
-Create `src/writers/{platform}/` with `index.ts` and `__tests__/` subdirectory.
+Create `src/writers/{platform}/` with `index.ts`.
 
 Example structure for `openai-gpt` platform:
 ```
 src/writers/openai-gpt/
-├── index.ts
-└── __tests__/
-    └── openai-gpt.test.ts
+└── index.ts
 ```
 
-**Step 3: Implement writeSetup() export**
-Write the function signature matching claude/cursor/codex. Follow this template:
+**Step 3: Implement write{Platform}Config() export**
+Write the function matching the claude/cursor/codex pattern. Follow this template:
 ```typescript
-import { WriteSetup } from '../types.js';
-import { ensureStaged, writeFile } from '../staging.js';
+import fs from 'fs';
+import path from 'path';
+import { appendPreCommitBlock, appendLearningsBlock } from '../pre-commit-block.js';
+
+interface OpenaiGptConfig {
+  instructions: string;
+  rules?: Array<{ filename: string; content: string }>;
+  skills?: Array<{ name: string; description: string; content: string }>;
+}
 
-export async function writeSetup(setup: WriteSetup): Promise<string[]> {
+export function writeOpenaiGptConfig(config: OpenaiGptConfig): string[] {
   const written: string[] = [];
-  
-  // 1. Write platform-specific config file(s)
-  // Example: .openai/gpt-rules.json or similar
-  if (setup.rules.length > 0) {
-    const filePath = '.openai/gpt-rules.json';
-    await writeFile(filePath, JSON.stringify(setup.rules, null, 2));
-    written.push(filePath);
-  }
-  
-  // 2. Integrate hooks if platform supports them
-  if (setup.hooks && setup.hooks.length > 0) {
-    // Write hooks in platform-specific location
-  }
-  
-  // 3. Stage files if setup.manifest exists
-  if (setup.manifest) {
-    await ensureStaged(written, setup.manifest);
+
+  // 1. Write main config file
+  fs.writeFileSync('.openai/instructions.md', appendLearningsBlock(appendPreCommitBlock(config.instructions, 'openai-gpt')));
+  written.push('.openai/instructions.md');
+
+  // 2. Write rules (if any)
+  if (config.rules?.length) {
+    const rulesDir = path.join('.openai', 'rules');
+    fs.mkdirSync(rulesDir, { recursive: true });
+    for (const rule of config.rules) {
+      const rulePath = path.join(rulesDir, rule.filename);
+      fs.writeFileSync(rulePath, rule.content);
+      written.push(rulePath);
+    }
   }
-  
+
   return written;
 }
 ```
 
-Verify each write operation appends to `written[]` BEFORE returning.
+Verify: function is synchronous; every `fs.writeFileSync` is preceded by `fs.mkdirSync`; every written path is in the returned array.
 
-**Step 4: Register writer in src/writers/index.ts**
-Add to the `writers` Map:
+**Step 4: Register in src/writers/index.ts**
 ```typescript
-writers.set('openai-gpt', () => import('./openai-gpt/index.js').then(m => m.writeSetup));
+import { writeOpenaiGptConfig } from './openai-gpt/index.js';
 ```
 
-Verify export from `getWriters()` function includes the new platform.
+Add to `AgentSetup`:
+- Add `'openai-gpt'` to the `targetAgent` tuple
+- Add `'openaiGpt'?: Parameters<typeof writeOpenaiGptConfig>[0]`
 
-**Step 5: Write tests in __tests__/index.test.ts**
-Follow vitest patterns from existing tests:
-- Mock `WriteSetup` with realistic rules/hooks/agents
-- Test file path generation (verify `written[]` matches expected files)
-- Test error handling (e.g., writeFile failures)
-- Test integration with `ensureStaged()` if applicable
+Add to `writeSetup()` and `getFilesToWrite()`:
+```typescript
+if (setup.targetAgent.includes('openai-gpt') && setup.openaiGpt) {
+  written.push(...writeOpenaiGptConfig(setup.openaiGpt));
+}
+```
 
-Example:
+**Step 5: Write tests in src/writers/__tests__/{platform}.test.ts**
+Follow the pattern from `src/writers/__tests__/codex.test.ts`:
 ```typescript
-import { describe, it, expect, vi } from 'vitest';
-import { writeSetup } from '../index.js';
-
-describe('openai-gpt writer', () => {
-  it('writes rules to .openai/gpt-rules.json', async () => {
-    const setup = { rules: ['rule1'], manifest: undefined };
-    const written = await writeSetup(setup as any);
-    expect(written).toContain('.openai/gpt-rules.json');
+import { describe, it, expect, vi, beforeEach } from 'vitest';
+import fs from 'fs';
+vi.mock('fs');
+import { writeOpenaiGptConfig } from '../openai-gpt/index.js';
+
+describe('writeOpenaiGptConfig', () => {
+  beforeEach(() => { vi.clearAllMocks(); vi.mocked(fs.existsSync).mockReturnValue(false); });
+  it('writes instructions.md', () => {
+    const written = writeOpenaiGptConfig({ instructions: '# Config' });
+    expect(written).toContain('.openai/instructions.md');
   });
 });
 ```
 
 **Step 6: Run tests and type check**
-Execute:
 ```bash
-npm test -- src/writers/{platform}/__tests__/
+npm test -- src/writers/__tests__/{platform}.test.ts
 npx tsc --noEmit
 ```
 
@@ -111,36 +115,32 @@ Verify no type errors and all tests pass.
 **User says:** "Add support for GitHub Copilot (new platform)"
 
 **Actions:**
-1. Create `src/writers/github-copilot/index.ts` (already exists, so this is example-only)
-2. Implement `writeSetup()` that writes `.copilot/rules.md` from `setup.rules`
-3. Add to `src/writers/index.ts`: `writers.set('github-copilot', ...)`
-4. Write tests verifying rules are written to correct path
-5. Verify `npm test` passes and no TypeScript errors
+1. Create `src/writers/github-copilot/index.ts` with `GithubCopilotConfig` interface
+2. Implement `export function writeGithubCopilotConfig(config: GithubCopilotConfig): string[]` — synchronous, writes `.github/copilot-instructions.md` and `.github/instructions/` files
+3. Add to `src/writers/index.ts`: import `{ writeGithubCopilotConfig }`, add to `AgentSetup`, call in `writeSetup()`
+4. Create `src/writers/__tests__/github-copilot.test.ts` with `vi.mock('fs')` tests
+5. Verify `npm run build && npm test` passes
 
-**Result:** New writer integrated; `getWriters()` now includes `github-copilot`; can be used by `refresh` and `regenerate` commands.
+**Result:** New writer integrated; `writeSetup()` calls `writeGithubCopilotConfig()` when `'github-copilot'` is in `targetAgent`.
 
 ## Common Issues
 
-**"Cannot find module src/writers/{platform}"**
-- Verify directory exists and `index.ts` is in it
-- Check import path uses `.js` extension per ESM convention
-- Run `npm run build` to compile TypeScript
+**"TypeError: write{Platform}Config is not a function"**
+- Verify function is exported with `export function write{Platform}Config(...)` — no `default`, no `async`
+- Check import in `src/writers/index.ts` uses `{ write{Platform}Config }` (named import, `.js` extension)
 
-**"writeSetup is not a named export"**
-- Ensure function is exported as `export async function writeSetup(...)`
-- Do NOT use default export; writers are imported by name in `src/writers/index.ts`
+**"ENOENT: no such file or directory"**
+- `fs.mkdirSync(parentDir, { recursive: true })` must be called BEFORE `fs.writeFileSync`
+- See `src/writers/claude/index.ts` for the correct order
 
 **"written array is empty but files were created"**
-- Every `writeFile()` call must append to `written[]` before returning
-- Do NOT forget to push file paths to array
-- Example: `written.push(filePath)` after each file operation
-
-**"Tests fail with 'ensureStaged not defined'"**
-- Verify import: `import { ensureStaged } from '../staging.js'`
-- Check staging.ts exports the function
-- Mock `fs` if testing file I/O (see vitest setup in `src/test/setup.ts`)
-
-**"Type 'WriteSetup' does not match signature"**
-- Verify `WriteSetup` is imported from `../types.js`
-- Ensure function signature is exactly: `(setup: WriteSetup) => Promise<string[]>`
-- Do NOT add optional parameters or change return type
\ No newline at end of file
+- Every `fs.writeFileSync()` call must be followed by `written.push(filePath)`
+- Check every file operation in the writer for a missing push
+
+**"Tests fail with mock not working"**
+- `vi.mock('fs')` must be at the top of the test file (before imports)
+- Follow pattern from `src/writers/__tests__/codex.test.ts`
+
+**"Type error on AgentSetup"**
+- Add platform to `targetAgent` tuple AND add the platform property to `AgentSetup` in `src/writers/index.ts`
+- Both must be updated together — missing either causes a type error
\ No newline at end of file
PATCH

echo "Gold patch applied."
