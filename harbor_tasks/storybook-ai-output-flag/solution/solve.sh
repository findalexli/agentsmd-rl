#!/usr/bin/env bash
set -euo pipefail

cd /workspace/storybook

# Idempotent: skip if already applied
if grep -q 'const outputPath = resolve(output)' code/lib/cli-storybook/src/ai/index.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/code/lib/cli-storybook/src/ai/index.ts b/code/lib/cli-storybook/src/ai/index.ts
index 2c78f3382b95..c86ec58a76c7 100644
--- a/code/lib/cli-storybook/src/ai/index.ts
+++ b/code/lib/cli-storybook/src/ai/index.ts
@@ -1,3 +1,6 @@
+import { writeFile } from 'node:fs/promises';
+import { resolve } from 'node:path';
+
 import type { PackageManagerName } from 'storybook/internal/common';
 import { logger } from 'storybook/internal/node-logger';

@@ -6,7 +9,7 @@ import { generateMarkdownOutput } from './prompt';
 import type { ProjectInfo, AiPrepareOptions } from './types';

 export async function aiPrepare(options: AiPrepareOptions): Promise<void> {
-  const { configDir: userConfigDir, packageManager: packageManagerName } = options;
+  const { configDir: userConfigDir, packageManager: packageManagerName, output } = options;

   let projectInfo: ProjectInfo;

@@ -54,7 +57,15 @@ export async function aiPrepare(options: AiPrepareOptions): Promise<void> {
     return;
   }

-  logger.log(generateMarkdownOutput(projectInfo));
+  const markdownOutput = generateMarkdownOutput(projectInfo);
+
+  if (output) {
+    const outputPath = resolve(output);
+    await writeFile(outputPath, markdownOutput, 'utf-8');
+    logger.log(`Prompt written to ${outputPath}`);
+  } else {
+    logger.log(markdownOutput);
+  }
 }

 function parseMajorVersion(version: string): number | undefined {
diff --git a/code/lib/cli-storybook/src/ai/types.ts b/code/lib/cli-storybook/src/ai/types.ts
index 8ae2f5dea9c1..252e28e51534 100644
--- a/code/lib/cli-storybook/src/ai/types.ts
+++ b/code/lib/cli-storybook/src/ai/types.ts
@@ -1,6 +1,7 @@
 export interface AiPrepareOptions {
   configDir?: string;
   packageManager?: string;
+  output?: string;
 }

 export interface ProjectInfo {
diff --git a/code/lib/cli-storybook/src/bin/run.ts b/code/lib/cli-storybook/src/bin/run.ts
index a54790e05060..064e5c3bb6d3 100644
--- a/code/lib/cli-storybook/src/bin/run.ts
+++ b/code/lib/cli-storybook/src/bin/run.ts
@@ -304,7 +304,12 @@ command('doctor')
     }).catch(handleCommandFailure(options.logfile));
   });

-const aiCommand = command('ai').description('AI agent helpers for Storybook');
+const aiCommand = command('ai')
+  .description('AI agent helpers for Storybook')
+  .option(
+    '-o, --output <path>',
+    'Write the prompt output to a file instead of printing it to stdout'
+  );

 aiCommand
   .command('prepare')
@@ -315,10 +320,12 @@ aiCommand
     )
   )
   .option('-c, --config-dir <dir-name>', 'Directory of Storybook configuration')
-  .action(async (options) => {
-    await withTelemetry('ai-prepare', { cliOptions: options }, async () => {
-      await aiPrepare(options);
-    }).catch(handleCommandFailure(options.logfile));
+  .action(async (options, cmd) => {
+    const parentOptions = cmd.parent?.opts() ?? {};
+    const mergedOptions = { ...parentOptions, ...options };
+    await withTelemetry('ai-prepare', { cliOptions: mergedOptions }, async () => {
+      await aiPrepare(mergedOptions);
+    }).catch(handleCommandFailure(mergedOptions.logfile));
   });

 // Show available subcommands when `storybook ai` is run without arguments

PATCH

echo "Patch applied successfully."
