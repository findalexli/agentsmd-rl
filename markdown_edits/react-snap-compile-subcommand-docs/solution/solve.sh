#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'BABEL_PLUGIN_ROOT' compiler/packages/snap/src/constants.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/compiler/.claude/agents/investigate-error.md b/compiler/.claude/agents/investigate-error.md
index b3673c596f74..ef32227cb6a4 100644
--- a/compiler/.claude/agents/investigate-error.md
+++ b/compiler/.claude/agents/investigate-error.md
@@ -13,7 +13,7 @@ You are an expert React Compiler debugging specialist with deep knowledge of com
 Create a new fixture file at `packages/babel-plugin-react-compiler/src/__tests__/fixtures/compiler/<fixture-name>.js` containing the problematic code. Use a descriptive name that reflects the issue (e.g., `bug-optional-chain-in-effect.js`).

 ### Step 2: Run Debug Compilation
-Execute `yarn snap -d -p <fixture-name>` to compile the fixture with full debug output. This shows the state of the program after each compilation pass.
+Execute `yarn snap -d -p <fixture-name>` to compile the fixture with full debug output. This shows the state of the program after each compilation pass. You can also use `yarn snap compile -d <path-to-fixture>`.

 ### Step 3: Analyze Compilation Results

diff --git a/compiler/CLAUDE.md b/compiler/CLAUDE.md
index 8de9c88fcf77..94a7d4b5d6d9 100644
--- a/compiler/CLAUDE.md
+++ b/compiler/CLAUDE.md
@@ -35,6 +35,31 @@ yarn snap -p <file-basename> -d
 yarn snap -u
 ```

+## Compiling Arbitrary Files
+
+Use `yarn snap compile` to compile any file (not just fixtures) with the React Compiler:
+
+```bash
+# Compile a file and see the output
+yarn snap compile <path>
+
+# Compile with debug logging to see the state after each compiler pass
+# This is an alternative to `yarn snap -d -p <pattern>` when you don't have a fixture file yet
+yarn snap compile --debug <path>
+```
+
+## Minimizing Test Cases
+
+Use `yarn snap minimize` to automatically reduce a failing test case to its minimal reproduction:
+
+```bash
+# Minimize a file that causes a compiler error
+yarn snap minimize <path>
+
+# Minimize and update the file in-place with the minimized version
+yarn snap minimize --update <path>
+```
+
 ## Version Control

 This repository uses Sapling (`sl`) for version control. Sapling is similar to Mercurial: there is not staging area, but new/deleted files must be explicitlyu added/removed.
diff --git a/compiler/docs/DEVELOPMENT_GUIDE.md b/compiler/docs/DEVELOPMENT_GUIDE.md
index af3973fada86..a38d8436e68e 100644
--- a/compiler/docs/DEVELOPMENT_GUIDE.md
+++ b/compiler/docs/DEVELOPMENT_GUIDE.md
@@ -17,7 +17,32 @@ yarn snap:build
 yarn snap --watch
 ```

-`snap` is our custom test runner, which creates "golden" test files that have the expected output for each input fixture, as well as the results of executing a specific input (or sequence of inputs) in both the uncompiled and compiler versions of the input.
+`snap` is our custom test runner, which creates "golden" test files that have the expected output for each input fixture, as well as the results of executing a specific input (or sequence of inputs) in both the uncompiled and compiler versions of the input.
+
+### Compiling Arbitrary Files
+
+You can compile any file (not just fixtures) using:
+
+```sh
+# Compile a file and see the output
+yarn snap compile <path>
+
+# Compile with debug output to see the state after each compiler pass
+# This is an alternative to `yarn snap -d -p <pattern>` when you don't have a fixture file yet
+yarn snap compile --debug <path>
+```
+
+### Minimizing Test Cases
+
+To reduce a failing test case to its minimal reproduction:
+
+```sh
+# Minimize a file that causes a compiler error
+yarn snap minimize <path>
+
+# Minimize and update the file in-place
+yarn snap minimize --update <path>
+```

 When contributing changes, we prefer to:
 * Add one or more fixtures that demonstrate the current compiled output for a particular combination of input and configuration. Send this as a first PR.
diff --git a/compiler/packages/babel-plugin-react-compiler/docs/passes/README.md b/compiler/packages/babel-plugin-react-compiler/docs/passes/README.md
index cafee2287ca7..bc9e17ac5238 100644
--- a/compiler/packages/babel-plugin-react-compiler/docs/passes/README.md
+++ b/compiler/packages/babel-plugin-react-compiler/docs/passes/README.md
@@ -294,6 +294,15 @@ yarn snap -p <fixture-name>
 # Run with debug output (shows all passes)
 yarn snap -p <fixture-name> -d

+# Compile any file (not just fixtures) and see output
+yarn snap compile <path>
+
+# Compile any file with debug output (alternative to yarn snap -d -p when you don't have a fixture)
+yarn snap compile --debug <path>
+
+# Minimize a failing test case to its minimal reproduction
+yarn snap minimize <path>
+
 # Update expected outputs
 yarn snap -u
 ```
diff --git a/compiler/packages/snap/src/constants.ts b/compiler/packages/snap/src/constants.ts
index 066b6b950a2b..788a2a6865da 100644
--- a/compiler/packages/snap/src/constants.ts
+++ b/compiler/packages/snap/src/constants.ts
@@ -7,19 +7,21 @@

 import path from 'path';

+export const PROJECT_ROOT = path.join(process.cwd(), '..', '..');
+
 // We assume this is run from `babel-plugin-react-compiler`
-export const PROJECT_ROOT = path.normalize(
-  path.join(process.cwd(), '..', 'babel-plugin-react-compiler'),
+export const BABEL_PLUGIN_ROOT = path.normalize(
+  path.join(PROJECT_ROOT, 'packages', 'babel-plugin-react-compiler'),
 );

-export const PROJECT_SRC = path.normalize(
-  path.join(PROJECT_ROOT, 'dist', 'index.js'),
+export const BABEL_PLUGIN_SRC = path.normalize(
+  path.join(BABEL_PLUGIN_ROOT, 'dist', 'index.js'),
 );
 export const PRINT_HIR_IMPORT = 'printFunctionWithOutlined';
 export const PRINT_REACTIVE_IR_IMPORT = 'printReactiveFunction';
 export const PARSE_CONFIG_PRAGMA_IMPORT = 'parseConfigPragmaForTests';
 export const FIXTURES_PATH = path.join(
-  PROJECT_ROOT,
+  BABEL_PLUGIN_ROOT,
   'src',
   '__tests__',
   'fixtures',
diff --git a/compiler/packages/snap/src/minimize.ts b/compiler/packages/snap/src/minimize.ts
index 1560cf0d2a13..0cce5ce1bdee 100644
--- a/compiler/packages/snap/src/minimize.ts
+++ b/compiler/packages/snap/src/minimize.ts
@@ -12,7 +12,7 @@ import traverse from '@babel/traverse';
 import * as t from '@babel/types';
 import type {parseConfigPragmaForTests as ParseConfigPragma} from 'babel-plugin-react-compiler/src/Utils/TestUtils';
 import {parseInput} from './compiler.js';
-import {PARSE_CONFIG_PRAGMA_IMPORT, PROJECT_SRC} from './constants.js';
+import {PARSE_CONFIG_PRAGMA_IMPORT, BABEL_PLUGIN_SRC} from './constants.js';

 type CompileSuccess = {kind: 'success'};
 type CompileParseError = {kind: 'parse_error'; message: string};
@@ -1919,7 +1919,7 @@ export function minimize(
   sourceType: 'module' | 'script',
 ): MinimizeResult {
   // Load the compiler plugin
-  const importedCompilerPlugin = require(PROJECT_SRC) as Record<
+  const importedCompilerPlugin = require(BABEL_PLUGIN_SRC) as Record<
     string,
     unknown
   >;
diff --git a/compiler/packages/snap/src/runner-watch.ts b/compiler/packages/snap/src/runner-watch.ts
index c29a29851531..dcec52689471 100644
--- a/compiler/packages/snap/src/runner-watch.ts
+++ b/compiler/packages/snap/src/runner-watch.ts
@@ -8,7 +8,7 @@
 import watcher from '@parcel/watcher';
 import path from 'path';
 import ts from 'typescript';
-import {FIXTURES_PATH, PROJECT_ROOT} from './constants';
+import {FIXTURES_PATH, BABEL_PLUGIN_ROOT} from './constants';
 import {TestFilter, getFixtures} from './fixture-utils';
 import {execSync} from 'child_process';

@@ -17,7 +17,7 @@ export function watchSrc(
   onComplete: (isSuccess: boolean) => void,
 ): ts.WatchOfConfigFile<ts.SemanticDiagnosticsBuilderProgram> {
   const configPath = ts.findConfigFile(
-    /*searchPath*/ PROJECT_ROOT,
+    /*searchPath*/ BABEL_PLUGIN_ROOT,
     ts.sys.fileExists,
     'tsconfig.json',
   );
@@ -166,7 +166,7 @@ function subscribeTsc(
       let isCompilerBuildValid = false;
       if (isTypecheckSuccess) {
         try {
-          execSync('yarn build', {cwd: PROJECT_ROOT});
+          execSync('yarn build', {cwd: BABEL_PLUGIN_ROOT});
           console.log('Built compiler successfully with tsup');
           isCompilerBuildValid = true;
         } catch (e) {
diff --git a/compiler/packages/snap/src/runner-worker.ts b/compiler/packages/snap/src/runner-worker.ts
index 554348534e30..fe76f6ccd3aa 100644
--- a/compiler/packages/snap/src/runner-worker.ts
+++ b/compiler/packages/snap/src/runner-worker.ts
@@ -5,7 +5,6 @@
  * LICENSE file in the root directory of this source tree.
  */

-import {codeFrameColumns} from '@babel/code-frame';
 import type {PluginObj} from '@babel/core';
 import type {parseConfigPragmaForTests as ParseConfigPragma} from 'babel-plugin-react-compiler/src/Utils/TestUtils';
 import type {printFunctionWithOutlined as PrintFunctionWithOutlined} from 'babel-plugin-react-compiler/src/HIR/PrintHIR';
@@ -15,7 +14,7 @@ import {
   PARSE_CONFIG_PRAGMA_IMPORT,
   PRINT_HIR_IMPORT,
   PRINT_REACTIVE_IR_IMPORT,
-  PROJECT_SRC,
+  BABEL_PLUGIN_SRC,
 } from './constants';
 import {TestFixture, getBasename, isExpectError} from './fixture-utils';
 import {TestResult, writeOutputToString} from './reporter';
@@ -65,7 +64,7 @@ async function compile(
   let compileResult: TransformResult | null = null;
   let error: string | null = null;
   try {
-    const importedCompilerPlugin = require(PROJECT_SRC) as Record<
+    const importedCompilerPlugin = require(BABEL_PLUGIN_SRC) as Record<
       string,
       unknown
     >;
diff --git a/compiler/packages/snap/src/runner.ts b/compiler/packages/snap/src/runner.ts
index c5443eaddecd..3d6e5b4fc156 100644
--- a/compiler/packages/snap/src/runner.ts
+++ b/compiler/packages/snap/src/runner.ts
@@ -12,7 +12,7 @@ import * as readline from 'readline';
 import ts from 'typescript';
 import yargs from 'yargs';
 import {hideBin} from 'yargs/helpers';
-import {PROJECT_ROOT} from './constants';
+import {BABEL_PLUGIN_ROOT, PROJECT_ROOT} from './constants';
 import {TestFilter, getFixtures} from './fixture-utils';
 import {TestResult, TestResults, report, update} from './reporter';
 import {
@@ -26,7 +26,14 @@ import {execSync} from 'child_process';
 import fs from 'fs';
 import path from 'path';
 import {minimize} from './minimize';
-import {parseLanguage, parseSourceType} from './compiler';
+import {parseInput, parseLanguage, parseSourceType} from './compiler';
+import {
+  PARSE_CONFIG_PRAGMA_IMPORT,
+  PRINT_HIR_IMPORT,
+  PRINT_REACTIVE_IR_IMPORT,
+  BABEL_PLUGIN_SRC,
+} from './constants';
+import chalk from 'chalk';

 const WORKER_PATH = require.resolve('./runner-worker.js');
 const NUM_WORKERS = cpus().length - 1;
@@ -48,6 +55,11 @@ type MinimizeOptions = {
   update: boolean;
 };

+type CompileOptions = {
+  path: string;
+  debug: boolean;
+};
+
 async function runTestCommand(opts: TestOptions): Promise<void> {
   const worker: Worker & typeof runnerWorker = new Worker(WORKER_PATH, {
     enableWorkerThreads: opts.workerThreads,
@@ -106,7 +118,7 @@ async function runTestCommand(opts: TestOptions): Promise<void> {
             );
           } else {
             try {
-              execSync('yarn build', {cwd: PROJECT_ROOT});
+              execSync('yarn build', {cwd: BABEL_PLUGIN_ROOT});
               console.log('Built compiler successfully with tsup');

               // Determine which filter to use
@@ -147,7 +159,7 @@ async function runMinimizeCommand(opts: MinimizeOptions): Promise<void> {
   // Resolve the input path
   const inputPath = path.isAbsolute(opts.path)
     ? opts.path
-    : path.resolve(process.cwd(), opts.path);
+    : path.resolve(PROJECT_ROOT, opts.path);

   // Check if file exists
   if (!fs.existsSync(inputPath)) {
@@ -196,6 +208,128 @@ async function runMinimizeCommand(opts: MinimizeOptions): Promise<void> {
   }
 }

+async function runCompileCommand(opts: CompileOptions): Promise<void> {
+  // Resolve the input path
+  const inputPath = path.isAbsolute(opts.path)
+    ? opts.path
+    : path.resolve(PROJECT_ROOT, opts.path);
+
+  // Check if file exists
+  if (!fs.existsSync(inputPath)) {
+    console.error(`Error: File not found: ${inputPath}`);
+    process.exit(1);
+  }
+
+  // Read the input file
+  const input = fs.readFileSync(inputPath, 'utf-8');
+  const filename = path.basename(inputPath);
+  const firstLine = input.substring(0, input.indexOf('\n'));
+  const language = parseLanguage(firstLine);
+  const sourceType = parseSourceType(firstLine);
+
+  // Import the compiler
+  const importedCompilerPlugin = require(BABEL_PLUGIN_SRC) as Record<
+    string,
+    any
+  >;
+  const BabelPluginReactCompiler = importedCompilerPlugin['default'];
+  const parseConfigPragmaForTests =
+    importedCompilerPlugin[PARSE_CONFIG_PRAGMA_IMPORT];
+  const printFunctionWithOutlined = importedCompilerPlugin[PRINT_HIR_IMPORT];
+  const printReactiveFunctionWithOutlined =
+    importedCompilerPlugin[PRINT_REACTIVE_IR_IMPORT];
+  const EffectEnum = importedCompilerPlugin['Effect'];
+  const ValueKindEnum = importedCompilerPlugin['ValueKind'];
+  const ValueReasonEnum = importedCompilerPlugin['ValueReason'];
+
+  // Setup debug logger
+  let lastLogged: string | null = null;
+  const debugIRLogger = opts.debug
+    ? (value: any) => {
+        let printed: string;
+        switch (value.kind) {
+          case 'hir':
+            printed = printFunctionWithOutlined(value.value);
+            break;
+          case 'reactive':
+            printed = printReactiveFunctionWithOutlined(value.value);
+            break;
+          case 'debug':
+            printed = value.value;
+            break;
+          case 'ast':
+            printed = '(ast)';
+            break;
+          default:
+            printed = String(value);
+        }
+
+        if (printed !== lastLogged) {
+          lastLogged = printed;
+          console.log(`${chalk.green(value.name)}:\n${printed}\n`);
+        } else {
+          console.log(`${chalk.blue(value.name)}: (no change)\n`);
+        }
+      }
+    : () => {};
+
+  // Parse the input
+  let ast;
+  try {
+    ast = parseInput(input, filename, language, sourceType);
+  } catch (e: any) {
+    console.error(`Parse error: ${e.message}`);
+    process.exit(1);
+  }
+
+  // Build plugin options
+  const config = parseConfigPragmaForTests(firstLine, {compilationMode: 'all'});
+  const options = {
+    ...config,
+    environment: {
+      ...config.environment,
+    },
+    logger: {
+      logEvent: () => {},
+      debugLogIRs: debugIRLogger,
+    },
+    enableReanimatedCheck: false,
+  };
+
+  // Compile
+  const {transformFromAstSync} = require('@babel/core');
+  try {
+    const result = transformFromAstSync(ast, input, {
+      filename: '/' + filename,
+      highlightCode: false,
+      retainLines: true,
+      compact: true,
+      plugins: [[BabelPluginReactCompiler, options]],
+      sourceType: 'module',
+      ast: false,
+      cloneInputAst: true,
+      configFile: false,
+      babelrc: false,
+    });
+
+    if (result?.code != null) {
+      // Format the output
+      const prettier = require('prettier');
+      const formatted = await prettier.format(result.code, {
+        semi: true,
+        parser: language === 'typescript' ? 'babel-ts' : 'flow',
+      });
+      console.log(formatted);
+    } else {
+      console.error('Error: No code emitted from compiler');
+      process.exit(1);
+    }
+  } catch (e: any) {
+    console.error(e.message);
+    process.exit(1);
+  }
+}
+
 yargs(hideBin(process.argv))
   .command(
     ['test', '$0'],
@@ -245,14 +379,15 @@ yargs(hideBin(process.argv))
     },
   )
   .command(
-    'minimize',
+    'minimize <path>',
     'Minimize a test case to reproduce a compiler error',
     yargs => {
       return yargs
-        .string('path')
-        .alias('p', 'path')
-        .describe('path', 'Path to the file to minimize')
-        .demandOption('path')
+        .positional('path', {
+          describe: 'Path to the file to minimize',
+          type: 'string',
+          demandOption: true,
+        })
         .boolean('update')
         .alias('u', 'update')
         .describe(
@@ -265,6 +400,25 @@ yargs(hideBin(process.argv))
       await runMinimizeCommand(argv as unknown as MinimizeOptions);
     },
   )
+  .command(
+    'compile <path>',
+    'Compile a file with the React Compiler',
+    yargs => {
+      return yargs
+        .positional('path', {
+          describe: 'Path to the file to compile',
+          type: 'string',
+          demandOption: true,
+        })
+        .boolean('debug')
+        .alias('d', 'debug')
+        .describe('debug', 'Enable debug logging to print HIR for each pass')
+        .default('debug', false);
+    },
+    async argv => {
+      await runCompileCommand(argv as unknown as CompileOptions);
+    },
+  )
   .help('help')
   .strict()
   .demandCommand()

PATCH

echo "Patch applied successfully."
