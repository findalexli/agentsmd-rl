#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotency: check if the key fix line is already present
if grep -q 'Using defaults for unprovided options' packages/create-next-app/index.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/create-next-app/index.ts b/packages/create-next-app/index.ts
index 313086c76d906..6cdc2977103ba 100644
--- a/packages/create-next-app/index.ts
+++ b/packages/create-next-app/index.ts
@@ -251,19 +251,45 @@ async function run(): Promise<void> {
     type DisplayConfigItem = {
       key: keyof typeof defaults
       values?: Record<string, string>
+      flags?: Record<string, string>
     }

     const displayConfig: DisplayConfigItem[] = [
       {
         key: 'typescript',
         values: { true: 'TypeScript', false: 'JavaScript' },
+        flags: { true: '--ts', false: '--js' },
+      },
+      {
+        key: 'linter',
+        values: { eslint: 'ESLint', biome: 'Biome', none: 'None' },
+        flags: { eslint: '--eslint', biome: '--biome', none: '--no-eslint' },
+      },
+      {
+        key: 'reactCompiler',
+        values: { true: 'React Compiler', false: 'No React Compiler' },
+        flags: { true: '--react-compiler', false: '--no-react-compiler' },
+      },
+      {
+        key: 'tailwind',
+        values: { true: 'Tailwind CSS', false: 'No Tailwind CSS' },
+        flags: { true: '--tailwind', false: '--no-tailwind' },
+      },
+      {
+        key: 'srcDir',
+        values: { true: 'src/ directory', false: 'No src/ directory' },
+        flags: { true: '--src-dir', false: '--no-src-dir' },
+      },
+      {
+        key: 'app',
+        values: { true: 'App Router', false: 'Pages Router' },
+        flags: { true: '--app', false: '--no-app' },
+      },
+      {
+        key: 'agentsMd',
+        values: { true: 'AGENTS.md', false: 'No AGENTS.md' },
+        flags: { true: '--agents-md', false: '--no-agents-md' },
       },
-      { key: 'linter', values: { eslint: 'ESLint', biome: 'Biome' } },
-      { key: 'reactCompiler', values: { true: 'React Compiler' } },
-      { key: 'tailwind', values: { true: 'Tailwind CSS' } },
-      { key: 'srcDir', values: { true: 'src/ dir' } },
-      { key: 'app', values: { true: 'App Router', false: 'Pages Router' } },
-      { key: 'agentsMd', values: { true: 'AGENTS.md' } },
     ]

     // Helper to format settings for display based on displayConfig
@@ -291,10 +317,17 @@ async function run(): Promise<void> {
     const hasSavedPreferences = Object.keys(preferences).length > 0

     // Check if user provided any configuration flags
-    // If they did, skip the "recommended defaults" prompt and go straight to
-    // individual prompts for any missing options
+    // If they did, skip all prompts and use recommended defaults for unspecified
+    // options. This is critical for AI agents, which pass flags like
+    // --typescript --tailwind --app and expect the rest to use sensible defaults
+    // without entering interactive mode.
     const hasProvidedOptions = process.argv.some((arg) => arg.startsWith('--'))

+    if (!skipPrompt && hasProvidedOptions) {
+      skipPrompt = true
+      useRecommendedDefaults = true
+    }
+
     // Only show the "recommended defaults" prompt if:
     // - Not in CI and not using --yes flag
     // - User hasn't provided any custom options
@@ -620,6 +653,56 @@ async function run(): Promise<void> {
         preferences.agentsMd = Boolean(agentsMd)
       }
     }
+
+    // When prompts were skipped because flags were provided, print the
+    // defaults that were assumed so agents and users know what to override.
+    if (hasProvidedOptions && useRecommendedDefaults) {
+      const lines: string[] = []
+
+      for (const config of displayConfig) {
+        if (!config.flags || !config.values) continue
+
+        // Skip options the user already specified explicitly
+        const wasExplicit = process.argv.some((arg) =>
+          Object.values(config.flags!).includes(arg)
+        )
+        if (wasExplicit) continue
+
+        const value = String(defaults[config.key])
+        const flag = config.flags[value]
+        const label = config.values[value]
+        if (!flag || !label) continue
+
+        // Show alternatives the user could pass instead
+        const alts: string[] = []
+        for (const [k, f] of Object.entries(config.flags)) {
+          if (k !== value && config.values[k]) {
+            alts.push(`${f} for ${config.values[k]}`)
+          }
+        }
+
+        const altText = alts.length > 0 ? ` (use ${alts.join(', ')})` : ''
+        lines.push(`  ${flag.padEnd(24)}${label}${altText}`)
+      }
+
+      // Import alias is not a boolean toggle, handle separately
+      const hasImportAlias = process.argv.some(
+        (arg) =>
+          arg.startsWith('--import-alias') ||
+          arg.startsWith('--no-import-alias')
+      )
+      if (!hasImportAlias) {
+        lines.push(`  ${'--import-alias'.padEnd(24)}"${defaults.importAlias}"`)
+      }
+
+      if (lines.length > 0) {
+        console.log(
+          '\nUsing defaults for unprovided options:\n\n' +
+            lines.join('\n') +
+            '\n'
+        )
+      }
+    }
   }

   const bundler: Bundler = opts.rspack ? Bundler.Rspack : Bundler.Turbopack

PATCH

echo "Patch applied successfully."
