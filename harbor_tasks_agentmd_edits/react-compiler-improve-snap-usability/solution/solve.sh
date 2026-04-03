#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if [ -f compiler/CLAUDE.md ] && grep -q "inputMode:" compiler/packages/snap/src/runner-watch.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/compiler/.claude/settings.local.json b/compiler/.claude/settings.json
similarity index 69%
rename from compiler/.claude/settings.local.json
rename to compiler/.claude/settings.json
index 9bbd18802e47..9b961f1c17e0 100644
--- a/compiler/.claude/settings.local.json
+++ b/compiler/.claude/settings.json
@@ -1,6 +1,8 @@
 {
   "permissions": {
     "allow": [
+      "Bash(yarn snap:*)",
+      "Bash(yarn snap:build)",
       "Bash(node scripts/enable-feature-flag.js:*)"
     ],
     "deny": [],
diff --git a/compiler/.gitignore b/compiler/.gitignore
index 77e4c01bef70..70622d250d00 100644
--- a/compiler/.gitignore
+++ b/compiler/.gitignore
@@ -8,7 +8,9 @@ dist
 .vscode
 !packages/playground/.vscode
 testfilter.txt
+.claude/settings.local.json
 
 # forgive
 *.vsix
 .vscode-test
+
diff --git a/compiler/CLAUDE.md b/compiler/CLAUDE.md
new file mode 100644
index 000000000000..c8e909bf2148
--- /dev/null
+++ b/compiler/CLAUDE.md
@@ -0,0 +1,221 @@
+# React Compiler Knowledge Base
+
+This document contains knowledge about the React Compiler gathered during development sessions. It serves as a reference for understanding the codebase architecture and key concepts.
+
+## Project Structure
+
+- `packages/babel-plugin-react-compiler/` - Main compiler package
+  - `src/HIR/` - High-level Intermediate Representation types and utilities
+  - `src/Inference/` - Effect inference passes (aliasing, mutation, etc.)
+  - `src/Validation/` - Validation passes that check for errors
+  - `src/Entrypoint/Pipeline.ts` - Main compilation pipeline with pass ordering
+  - `src/__tests__/fixtures/compiler/` - Test fixtures
+    - `error.todo-*.js` - Unsupported feature, correctly throws Todo error (graceful bailout)
+    - `error.bug-*.js` - Known bug, throws wrong error type or incorrect behavior
+    - `*.expect.md` - Expected output for each fixture
+
+## Running Tests
+
+```bash
+# Run all tests
+yarn snap
+
+# Run tests matching a pattern
+# Example: yarn snap -p 'error.*'
+yarn snap -p <pattern>
+
+# Run a single fixture in debug mode. Use the path relative to the __tests__/fixtures/compiler directory
+# For each step of compilation, outputs the step name and state of the compiled program
+# Example: yarn snap -p simple.js -d
+yarn snap -p <file-basename> -d
+
+# Update fixture outputs (also works with -p)
+yarn snap -u
+```
+
+## Version Control
+
+This repository uses Sapling (`sl`) for version control. Sapling is similar to Mercurial: there is not staging area, but new/deleted files must be explicitlyu added/removed.
+
+```bash
+# Check status
+sl status
+
+# Add new files, remove deleted files
+sl addremove
+
+# Commit all changes
+sl commit -m "Your commit message"
+
+# Commit with multi-line message using heredoc
+sl commit -m "$(cat <<'EOF'
+Summary line
+
+Detailed description here
+EOF
+)"
+```
+
+## Key Concepts
+
+### HIR (High-level Intermediate Representation)
+
+The compiler converts source code to HIR for analysis. Key types in `src/HIR/HIR.ts`:
+
+- **HIRFunction** - A function being compiled
+  - `body.blocks` - Map of BasicBlocks
+  - `context` - Captured variables from outer scope
+  - `params` - Function parameters
+  - `returns` - The function's return place
+  - `aliasingEffects` - Effects that describe the function's behavior when called
+
+- **Instruction** - A single operation
+  - `lvalue` - The place being assigned to
+  - `value` - The instruction kind (CallExpression, FunctionExpression, LoadLocal, etc.)
+  - `effects` - Array of AliasingEffects for this instruction
+
+- **Terminal** - Block terminators (return, branch, etc.)
+  - `effects` - Array of AliasingEffects
+
+- **Place** - A reference to a value
+  - `identifier.id` - Unique IdentifierId
+
+- **Phi nodes** - Join points for values from different control flow paths
+  - Located at `block.phis`
+  - `phi.place` - The result place
+  - `phi.operands` - Map of predecessor block to source place
+
+### AliasingEffects System
+
+Effects describe data flow and operations. Defined in `src/Inference/AliasingEffects.ts`:
+
+**Data Flow Effects:**
+- `Impure` - Marks a place as containing an impure value (e.g., Date.now() result, ref.current)
+- `Capture a -> b` - Value from `a` is captured into `b` (mutable capture)
+- `Alias a -> b` - `b` aliases `a`
+- `ImmutableCapture a -> b` - Immutable capture (like Capture but read-only)
+- `Assign a -> b` - Direct assignment
+- `MaybeAlias a -> b` - Possible aliasing
+- `CreateFrom a -> b` - Created from source
+
+**Mutation Effects:**
+- `Mutate value` - Value is mutated
+- `MutateTransitive value` - Value and transitive captures are mutated
+- `MutateConditionally value` - May mutate
+- `MutateTransitiveConditionally value` - May mutate transitively
+
+**Other Effects:**
+- `Render place` - Place is used in render context (JSX props, component return)
+- `Freeze place` - Place is frozen (made immutable)
+- `Create place` - New value created
+- `CreateFunction` - Function expression created, includes `captures` array
+- `Apply` - Function application with receiver, function, args, and result
+
+### Hook Aliasing Signatures
+
+Located in `src/HIR/Globals.ts`, hooks can define custom aliasing signatures to control how data flows through them.
+
+**Structure:**
+```typescript
+aliasing: {
+  receiver: '@receiver',    // The hook function itself
+  params: ['@param0'],      // Named positional parameters
+  rest: '@rest',            // Rest parameters (or null)
+  returns: '@returns',      // Return value
+  temporaries: [],          // Temporary values during execution
+  effects: [                // Array of effects to apply when hook is called
+    {kind: 'Freeze', value: '@param0', reason: ValueReason.HookCaptured},
+    {kind: 'Assign', from: '@param0', into: '@returns'},
+  ],
+}
+```
+
+**Common patterns:**
+
+1. **RenderHookAliasing** (useState, useContext, useMemo, useCallback):
+   - Freezes arguments (`Freeze @rest`)
+   - Marks arguments as render-time (`Render @rest`)
+   - Creates frozen return value
+   - Aliases arguments to return
+
+2. **EffectHookAliasing** (useEffect, useLayoutEffect, useInsertionEffect):
+   - Freezes function and deps
+   - Creates internal effect object
+   - Captures function and deps into effect
+   - Returns undefined
+
+3. **Event handler hooks** (useEffectEvent):
+   - Freezes callback (`Freeze @fn`)
+   - Aliases input to return (`Assign @fn -> @returns`)
+   - NO Render effect (callback not called during render)
+
+**Example: useEffectEvent**
+```typescript
+const UseEffectEventHook = addHook(
+  DEFAULT_SHAPES,
+  {
+    positionalParams: [Effect.Freeze],  // Takes one positional param
+    restParam: null,
+    returnType: {kind: 'Function', ...},
+    calleeEffect: Effect.Read,
+    hookKind: 'useEffectEvent',
+    returnValueKind: ValueKind.Frozen,
+    aliasing: {
+      receiver: '@receiver',
+      params: ['@fn'],              // Name for the callback parameter
+      rest: null,
+      returns: '@returns',
+      temporaries: [],
+      effects: [
+        {kind: 'Freeze', value: '@fn', reason: ValueReason.HookCaptured},
+        {kind: 'Assign', from: '@fn', into: '@returns'},
+        // Note: NO Render effect - callback is not called during render
+      ],
+    },
+  },
+  BuiltInUseEffectEventId,
+);
+
+// Add as both names for compatibility
+['useEffectEvent', UseEffectEventHook],
+['experimental_useEffectEvent', UseEffectEventHook],
+```
+
+**Key insight:** If a hook is missing an `aliasing` config, it falls back to `DefaultNonmutatingHook` which includes a `Render` effect on all arguments. This can cause false positives for hooks like `useEffectEvent` whose callbacks are not called during render.
+
+## Feature Flags
+
+Feature flags are configured in `src/HIR/Environment.ts`, for example `enableJsxOutlining`. Test fixtures can override the active feature flags used for that fixture via a comment pragma on the first line of the fixture input, for example:
+
+```javascript
+// enableJsxOutlining @enableChangeVariableCodegen:false
+
+...code...
+```
+
+Would enable the `enableJsxOutlining` feature and disable the `enableChangeVariableCodegen` feature.
+
+## Debugging Tips
+
+1. Run `yarn snap -p <fixture>` to see full HIR output with effects
+2. Look for `@aliasingEffects=` on FunctionExpressions
+3. Look for `Impure`, `Render`, `Capture` effects on instructions
+4. Check the pass ordering in Pipeline.ts to understand when effects are populated vs validated
+
+## Error Handling for Unsupported Features
+
+When the compiler encounters an unsupported but known pattern, use `CompilerError.throwTodo()` instead of `CompilerError.invariant()`. Todo errors cause graceful bailouts in production; Invariant errors are hard failures indicating unexpected/invalid states.
+
+```typescript
+// Unsupported but expected pattern - graceful bailout
+CompilerError.throwTodo({
+  reason: `Support [description of unsupported feature]`,
+  loc: terminal.loc,
+});
+
+// Invariant is for truly unexpected/invalid states - hard failure
+CompilerError.invariant(false, {
+  reason: `Unexpected [thing]`,
+  loc: terminal.loc,
+});
+```
diff --git a/compiler/packages/snap/src/constants.ts b/compiler/packages/snap/src/constants.ts
index d1ede2a2f2aa..066b6b950a2b 100644
--- a/compiler/packages/snap/src/constants.ts
+++ b/compiler/packages/snap/src/constants.ts
@@ -26,5 +26,3 @@ export const FIXTURES_PATH = path.join(
   'compiler',
 );
 export const SNAPSHOT_EXTENSION = '.expect.md';
-export const FILTER_FILENAME = 'testfilter.txt';
-export const FILTER_PATH = path.join(PROJECT_ROOT, FILTER_FILENAME);
diff --git a/compiler/packages/snap/src/fixture-utils.ts b/compiler/packages/snap/src/fixture-utils.ts
index fae6afef1519..29f7d4ddfbb9 100644
--- a/compiler/packages/snap/src/fixture-utils.ts
+++ b/compiler/packages/snap/src/fixture-utils.ts
@@ -8,7 +8,7 @@
 import fs from 'fs/promises';
 import * as glob from 'glob';
 import path from 'path';
-import {FILTER_PATH, FIXTURES_PATH, SNAPSHOT_EXTENSION} from './constants';
+import {FIXTURES_PATH, SNAPSHOT_EXTENSION} from './constants';
 
 const INPUT_EXTENSIONS = [
   '.js',
@@ -22,19 +22,9 @@ const INPUT_EXTENSIONS = [
 ];
 
 export type TestFilter = {
-  debug: boolean;
   paths: Array<string>;
 };
 
-async function exists(file: string): Promise<boolean> {
-  try {
-    await fs.access(file);
-    return true;
-  } catch {
-    return false;
-  }
-}
-
 function stripExtension(filename: string, extensions: Array<string>): string {
   for (const ext of extensions) {
     if (filename.endsWith(ext)) {
@@ -44,37 +34,6 @@ function stripExtension(filename: string, extensions: Array<string>): string {
   return filename;
 }
 
-export async function readTestFilter(): Promise<TestFilter | null> {
-  if (!(await exists(FILTER_PATH))) {
-    throw new Error(`testfilter file not found at \`${FILTER_PATH}\``);
-  }
-
-  const input = await fs.readFile(FILTER_PATH, 'utf8');
-  const lines = input.trim().split('\n');
-
-  let debug: boolean = false;
-  const line0 = lines[0];
-  if (line0 != null) {
-    // Try to parse pragmas
-    let consumedLine0 = false;
-    if (line0.indexOf('@only') !== -1) {
-      consumedLine0 = true;
-    }
-    if (line0.indexOf('@debug') !== -1) {
-      debug = true;
-      consumedLine0 = true;
-    }
-
-    if (consumedLine0) {
-      lines.shift();
-    }
-  }
-  return {
-    debug,
-    paths: lines.filter(line => !line.trimStart().startsWith('//')),
-  };
-}
-
 export function getBasename(fixture: TestFixture): string {
   return stripExtension(path.basename(fixture.inputPath), INPUT_EXTENSIONS);
 }
diff --git a/compiler/packages/snap/src/runner-watch.ts b/compiler/packages/snap/src/runner-watch.ts
index 6073fd30f921..06ae99846681 100644
--- a/compiler/packages/snap/src/runner-watch.ts
+++ b/compiler/packages/snap/src/runner-watch.ts
@@ -8,8 +8,8 @@
 import watcher from '@parcel/watcher';
 import path from 'path';
 import ts from 'typescript';
-import {FILTER_FILENAME, FIXTURES_PATH, PROJECT_ROOT} from './constants';
-import {TestFilter, readTestFilter} from './fixture-utils';
+import {FIXTURES_PATH, PROJECT_ROOT} from './constants';
+import {TestFilter} from './fixture-utils';
 import {execSync} from 'child_process';
 
 export function watchSrc(
@@ -117,6 +117,10 @@ export type RunnerState = {
   lastUpdate: number;
   mode: RunnerMode;
   filter: TestFilter | null;
+  debug: boolean;
+  // Input mode for interactive pattern entry
+  inputMode: 'none' | 'pattern';
+  inputBuffer: string;
 };
 
 function subscribeFixtures(
@@ -142,26 +146,6 @@ function subscribeFixtures(
   });
 }
 
-function subscribeFilterFile(
-  state: RunnerState,
-  onChange: (state: RunnerState) => void,
-) {
-  watcher.subscribe(PROJECT_ROOT, async (err, events) => {
-    if (err) {
-      console.error(err);
-      process.exit(1);
-    } else if (
-      events.findIndex(event => event.path.includes(FILTER_FILENAME)) !== -1
-    ) {
-      if (state.mode.filter) {
-        state.filter = await readTestFilter();
-        state.mode.action = RunnerAction.Test;
-        onChange(state);
-      }
-    }
-  });
-}
-
 function subscribeTsc(
   state: RunnerState,
   onChange: (state: RunnerState) => void,
@@ -200,15 +184,67 @@ function subscribeKeyEvents(
   onChange: (state: RunnerState) => void,
 ) {
   process.stdin.on('keypress', async (str, key) => {
+    // Handle input mode (pattern entry)
+    if (state.inputMode !== 'none') {
+      if (key.name === 'return') {
+        // Enter pressed - process input
+        const pattern = state.inputBuffer.trim();
+        state.inputMode = 'none';
+        state.inputBuffer = '';
+        process.stdout.write('\n');
+
+        if (pattern !== '') {
+          // Set the pattern as filter
+          state.filter = {paths: [pattern]};
+          state.mode.filter = true;
+          state.mode.action = RunnerAction.Test;
+          onChange(state);
+        }
+        // If empty, just exit input mode without changes
+        return;
+      } else if (key.name === 'escape') {
+        // Cancel input mode
+        state.inputMode = 'none';
+        state.inputBuffer = '';
+        process.stdout.write(' (cancelled)\n');
+        return;
+      } else if (key.name === 'backspace') {
+        if (state.inputBuffer.length > 0) {
+          state.inputBuffer = state.inputBuffer.slice(0, -1);
+          // Erase character: backspace, space, backspace
+          process.stdout.write('\b \b');
+        }
+        return;
+      } else if (str && !key.ctrl && !key.meta) {
+        // Regular character - accumulate and echo
+        state.inputBuffer += str;
+        process.stdout.write(str);
+        return;
+      }
+      return; // Ignore other keys in input mode
+    }
+
+    // Normal mode keypress handling
     if (key.name === 'u') {
       // u => update fixtures
       state.mode.action = RunnerAction.Update;
     } else if (key.name === 'q') {
       process.exit(0);
-    } else if (key.name === 'f') {
-      state.mode.filter = !state.mode.filter;
-      state.filter = state.mode.filter ? await readTestFilter() : null;
+    } else if (key.name === 'a') {
+      // a => exit filter mode and run all tests
+      state.mode.filter = false;
+      state.filter = null;
+      state.mode.action = RunnerAction.Test;
+    } else if (key.name === 'd') {
+      // d => toggle debug logging
+      state.debug = !state.debug;
       state.mode.action = RunnerAction.Test;
+    } else if (key.name === 'p') {
+      // p => enter pattern input mode
+      state.inputMode = 'pattern';
+      state.inputBuffer = '';
+      process.stdout.write('Pattern: ');
+      return; // Don't trigger onChange yet
     } else {
       // any other key re-runs tests
       state.mode.action = RunnerAction.Test;
@@ -219,21 +255,33 @@ function subscribeKeyEvents(
 
 export async function makeWatchRunner(
   onChange: (state: RunnerState) => void,
-  filterMode: boolean,
+  debugMode: boolean,
+  initialPattern?: string,
 ): Promise<void> {
-  const state = {
+  // Determine initial filter state
+  let filter: TestFilter | null = null;
+  let filterEnabled = false;
+
+  if (initialPattern) {
+    filter = {paths: [initialPattern]};
+    filterEnabled = true;
+  }
+
+  const state: RunnerState = {
     compilerVersion: 0,
     isCompilerBuildValid: false,
     lastUpdate: -1,
     mode: {
       action: RunnerAction.Test,
-      filter: filterMode,
+      filter: filterEnabled,
     },
-    filter: filterMode ? await readTestFilter() : null,
+    filter,
+    debug: debugMode,
+    inputMode: 'none',
+    inputBuffer: '',
   };
 
   subscribeTsc(state, onChange);
   subscribeFixtures(state, onChange);
   subscribeKeyEvents(state, onChange);
-  subscribeFilterFile(state, onChange);
 }
diff --git a/compiler/packages/snap/src/runner.ts b/compiler/packages/snap/src/runner.ts
index 478a32d426cd..04724532b641 100644
--- a/compiler/packages/snap/src/runner.ts
+++ b/compiler/packages/snap/src/runner.ts
@@ -12,8 +12,8 @@ import * as readline from 'readline';
 import ts from 'typescript';
 import yargs from 'yargs';
 import {hideBin} from 'yargs/helpers';
-import {FILTER_PATH, PROJECT_ROOT} from './constants';
-import {TestFilter, getFixtures, readTestFilter} from './fixture-utils';
+import {PROJECT_ROOT} from './constants';
+import {TestFilter, getFixtures} from './fixture-utils';
 import {TestResult, TestResults, report, update} from './reporter';
 import {
   RunnerAction,
@@ -33,9 +33,9 @@ type RunnerOptions = {
   sync: boolean;
   workerThreads: boolean;
   watch: boolean;
-  filter: boolean;
   update: boolean;
   pattern?: string;
+  debug: boolean;
 };
 
 const opts: RunnerOptions = yargs
@@ -59,18 +59,16 @@ const opts: RunnerOptions = yargs
   .alias('u', 'update')
   .describe('update', 'Update fixtures')
   .default('update', false)
-  .boolean('filter')
-  .describe(
-    'filter',
-    'Only run fixtures which match the contents of testfilter.txt',
-  )
-  .default('filter', false)
   .string('pattern')
   .alias('p', 'pattern')
   .describe(
     'pattern',
     'Optional glob pattern to filter fixtures (e.g., "error.*", "use-memo")',
   )
+  .boolean('debug')
+  .alias('d', 'debug')
+  .describe('debug', 'Enable debug logging to print HIR for each pass')
+  .default('debug', false)
   .help('help')
   .strict()
   .parseSync(hideBin(process.argv)) as RunnerOptions;
@@ -82,12 +80,15 @@ async function runFixtures(
   worker: Worker & typeof runnerWorker,
   filter: TestFilter | null,
   compilerVersion: number,
+  debug: boolean,
+  requireSingleFixture: boolean,
 ): Promise<TestResults> {
   // We could in theory be fancy about tracking the contents of the fixtures
   // directory via our file subscription, but it's simpler to just re-read
   // the directory each time.
   const fixtures = await getFixtures(filter);
   const isOnlyFixture = filter !== null && fixtures.size === 1;
+  const shouldLog = debug && (!requireSingleFixture || isOnlyFixture);
 
   let entries: Array<[string, TestResult]>;
   if (!opts.sync) {
@@ -96,12 +97,7 @@ async function runFixtures(
     for (const [fixtureName, fixture] of fixtures) {
       work.push(
         worker
-          .transformFixture(
-            fixture,
-            compilerVersion,
-            (filter?.debug ?? false) && isOnlyFixture,
-            true,
-          )
+          .transformFixture(fixture, compilerVersion, shouldLog, true)
           .then(result => [fixtureName, result]),
       );
     }
@@ -113,7 +109,7 @@ async function runFixtures(
       let output = await runnerWorker.transformFixture(
         fixture,
         compilerVersion,
-        (filter?.debug ?? false) && isOnlyFixture,
+        shouldLog,
         true,
       );
       entries.push([fixtureName, output]);
@@ -128,7 +124,7 @@ async function onChange(
   worker: Worker & typeof runnerWorker,
   state: RunnerState,
 ) {
-  const {compilerVersion, isCompilerBuildValid, mode, filter} = state;
+  const {compilerVersion, isCompilerBuildValid, mode, filter, debug} = state;
   if (isCompilerBuildValid) {
     const start = performance.now();
 
@@ -142,6 +138,8 @@ async function onChange(
       worker,
       mode.filter ? filter : null,
       compilerVersion,
+      debug,
+      true, // requireSingleFixture in watch mode
     );
     const end = performance.now();
     if (mode.action === RunnerAction.Update) {
@@ -159,11 +157,13 @@ async function onChange(
   console.log(
     '\n' +
       (mode.filter
-        ? `Current mode = FILTER, filter test fixtures by "${FILTER_PATH}".`
+        ? `Current mode = FILTER, pattern = "${filter?.paths[0] ?? ''}".`
         : 'Current mode = NORMAL, run all test fixtures.') +
       '\nWaiting for input or file changes...\n' +
       'u     - update all fixtures\n' +
-      `f     - toggle (turn ${mode.filter ? 'off' : 'on'}) filter mode\n` +
+      `d     - toggle (turn ${debug ? 'off' : 'on'}) debug logging\n` +
+      'p     - enter pattern to filter fixtures\n' +
+      (mode.filter ? 'a     - run all tests (exit filter mode)\n' : '') +
       'q     - quit\n' +
       '[any] - rerun tests\n',
   );
@@ -180,15 +180,12 @@ export async function main(opts: RunnerOptions): Promise<void> {
   worker.getStderr().pipe(process.stderr);
   worker.getStdout().pipe(process.stdout);
 
-  // If pattern is provided, force watch mode off and use pattern filter
-  const shouldWatch = opts.watch && opts.pattern == null;
-  if (opts.watch && opts.pattern != null) {
-    console.warn('NOTE: --watch is ignored when a --pattern is supplied');
-  }
+  // Check if watch mode should be enabled
+  const shouldWatch = opts.watch;
 
   if (shouldWatch) {
-    makeWatchRunner(state => onChange(worker, state), opts.filter);
-    if (opts.filter) {
+    makeWatchRunner(state => onChange(worker, state), opts.debug, opts.pattern);
+    if (opts.pattern) {
       /**
        * Warm up wormers when in watch mode. Loading the Forget babel plugin
        * and all of its transitive dependencies takes 1-3s (per worker) on a M1.
@@ -236,14 +233,17 @@ export async function main(opts: RunnerOptions): Promise<void> {
               let testFilter: TestFilter | null = null;
               if (opts.pattern) {
                 testFilter = {
-                  debug: true,
                   paths: [opts.pattern],
                 };
-              } else if (opts.filter) {
-                testFilter = await readTestFilter();
               }
 
-              const results = await runFixtures(worker, testFilter, 0);
+              const results = await runFixtures(
+                worker,
+                testFilter,
+                0,
+                opts.debug,
+                false, // no requireSingleFixture in non-watch mode
+              );
               if (opts.update) {
                 update(results);
                 isSuccess = true;

PATCH

echo "Patch applied successfully."
