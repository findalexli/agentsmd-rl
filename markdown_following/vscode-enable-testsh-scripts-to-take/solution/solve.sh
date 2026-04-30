#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vscode

# Idempotent: skip if already applied
if grep -q 'bareFiles' test/unit/electron/index.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.github/skills/unit-tests/SKILL.md b/.github/skills/unit-tests/SKILL.md
index 18f0290877c12..5f2ebfc304ddc 100644
--- a/.github/skills/unit-tests/SKILL.md
+++ b/.github/skills/unit-tests/SKILL.md
@@ -26,7 +26,25 @@ These scripts download Electron if needed and launch the Mocha test runner.

 ### Commonly used options

-#### `--run <file>` - Run tests from a specific file
+#### Bare file paths - Run tests from specific files
+
+Pass source file paths directly as positional arguments. The test runner automatically treats bare `.ts`/`.js` positional arguments as `--run` values.
+
+```bash
+./scripts/test.sh src/vs/editor/test/common/model.test.ts
+```
+
+```bat
+.\scripts\test.bat src\vs\editor\test\common\model.test.ts
+```
+
+Multiple files:
+
+```bash
+./scripts/test.sh src/vs/editor/test/common/model.test.ts src/vs/editor/test/common/range.test.ts
+```
+
+#### `--run <file>` - Run tests from a specific file (explicit form)

 Accepts a **source file path** (starting with `src/`). The runner strips the `src/` prefix and the `.ts`/`.js` extension automatically to resolve the compiled module.

@@ -80,7 +98,7 @@ Override the default Mocha timeout for long-running tests.

 ### Integration tests

-Integration tests (files ending in `.integrationTest.ts` or located in `extensions/`) are **not run** by `scripts/test.sh`. Use `scripts/test-integration.sh` (or `scripts/test-integration.bat`) instead. See the `integration-tests` skill for details on filtering and running specific integration test files.
+Integration tests (files ending in `.integrationTest.ts` or located in `extensions/`) are **not run** by `scripts/test.sh`. Use `scripts/test-integration.sh` (or `scripts/test-integration.bat`) instead. See the `integration-tests` skill for details.

 ### Compilation requirement

diff --git a/test/unit/electron/index.js b/test/unit/electron/index.js
index 842feb80e9056..16863fcc22817 100644
--- a/test/unit/electron/index.js
+++ b/test/unit/electron/index.js
@@ -27,8 +27,9 @@ const minimist = require('minimist');

 /**
  * @type {{
+ * _: string[];
  * grep: string;
- * run: string;
+ * run: string | string[];
  * runGlob: string;
  * testSplit: string;
  * dev: boolean;
@@ -62,7 +63,10 @@ const args = minimist(process.argv.slice(2), {
 });

 if (args.help) {
-	console.log(`Usage: node ${process.argv[1]} [options]
+	console.log(`Usage: node ${process.argv[1]} [options] [file...]
+
+Bare .ts/.js file paths passed as positional arguments are treated as
+--run arguments.

 Options:
 --grep, -g, -f <pattern>      only run tests matching <pattern>
@@ -83,6 +87,14 @@ Options:
 	process.exit(0);
 }

+// Treat bare .ts/.js positional arguments as --run values
+const bareFiles = (args._ || []).filter(a => typeof a === 'string' && (a.endsWith('.ts') || a.endsWith('.js')));
+if (bareFiles.length > 0) {
+	const existing = !args.run ? [] : Array.isArray(args.run) ? args.run : [args.run];
+	args.run = [...existing, ...bareFiles];
+	args._ = (args._ || []).filter(a => !bareFiles.includes(a));
+}
+
 let crashReporterDirectory = args['crash-reporter-directory'];
 if (crashReporterDirectory) {
 	crashReporterDirectory = path.normalize(crashReporterDirectory);

PATCH

echo "Patch applied successfully."
