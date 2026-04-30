#!/usr/bin/env bash
set -euo pipefail

cd /workspace/posthog

# Idempotent: skip if already applied
if grep -q 'TOOL_NAME_PATTERN' services/mcp/scripts/yaml-config-schema.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.agents/skills/implementing-mcp-tools/SKILL.md b/.agents/skills/implementing-mcp-tools/SKILL.md
index 6ab42f1bdb84..22362ff00535 100644
--- a/.agents/skills/implementing-mcp-tools/SKILL.md
+++ b/.agents/skills/implementing-mcp-tools/SKILL.md
@@ -67,6 +67,42 @@ Agents compose these primitives into higher-level workflows.
 Good: "List feature flags", "Get experiment by ID", "Create a survey".
 Bad: "Search for session recordings of an experiment" — bundles multiple concerns.

+## Tool naming constraints
+
+Tool names and feature identifiers are validated at build time and in CI.
+Violations fail the build.
+
+### Tool names
+
+- **Format**: lowercase kebab-case — only `[a-z0-9-]`, no leading/trailing hyphens
+- **Length**: 52 characters or fewer
+- **Convention**: `domain-action`, e.g. `cohorts-create`, `dashboard-get`, `feature-flags-list`
+
+### Feature identifiers
+
+- **Format**: lowercase snake*case — only `[a-z0-9*]`, must start with a letter
+- **Convention**: should match the product folder name, e.g. `error_tracking`, `feature_flags`
+
+### Why 52 characters?
+
+MCP clients enforce different limits on tool names. The 52-char limit is the safe zone
+that works across all known clients:
+
+| Client           | Limit                          | Notes                                                            |
+| ---------------- | ------------------------------ | ---------------------------------------------------------------- |
+| MCP spec (draft) | 1–128 chars, `[A-Za-z0-9_\-.]` | Official recommendation, not enforced                            |
+| Claude Code      | 64 chars                       | Hard limit; prefixes tool names with `mcp____`                   |
+| Cursor           | 60 chars combined              | `server_name + tool_name`; tools over this are silently filtered |
+| OpenAI API       | `^[a-zA-Z0-9_-]+$`, 64 chars   | No dots allowed                                                  |
+
+With the server name "posthog" (7 chars) plus a separator, tool names must stay at
+or below 52 characters to fit within Cursor's 60-char combined limit.
+
+### CI enforcement
+
+- `pnpm --filter=@posthog/mcp lint-tool-names` — validates length and pattern for YAML and JSON definitions
+- A vitest test validates all runtime `TOOL_MAP` and `GENERATED_TOOL_MAP` entries
+
 ## YAML definitions

 YAML files configure which operations are exposed as MCP tools.
diff --git a/docs/published/handbook/engineering/ai/implementing-mcp-tools.md b/docs/published/handbook/engineering/ai/implementing-mcp-tools.md
index 16ea14758ee1..e2217a910407 100644
--- a/docs/published/handbook/engineering/ai/implementing-mcp-tools.md
+++ b/docs/published/handbook/engineering/ai/implementing-mcp-tools.md
@@ -188,14 +188,26 @@ Product teams own their definitions and control which operations are exposed as
 2. **Configure** the YAML – enable tools, add scopes, annotations, and descriptions.
    Each YAML file has a top-level structure validated by Zod ([`scripts/yaml-config-schema.ts`](https://github.com/PostHog/posthog/blob/master/services/mcp/scripts/yaml-config-schema.ts)):

-   Tool names follow a **`domain-action`** convention in kebab-case,
+   **Tool names** follow a **`domain-action`** convention in lowercase kebab-case (`[a-z0-9-]`),
    e.g. `feature-flags-list`, `experiments-create`, `surveys-delete`.
    The domain groups related tools together and the action describes the operation.
+   Names must not start or end with a hyphen.

-   **Tool name length limit:** Some MCP clients (notably Cursor) enforce a 60-character
-   combined limit on `server_name:tool_name`. Since our server name is `posthog` (7 chars),
-   tool names must be **52 characters or fewer**.
-   CI runs `pnpm --filter=@posthog/mcp lint-tool-names` to enforce this.
+   **Feature identifiers** must be lowercase snake*case (`[a-z0-9*]`), e.g. `error_tracking`,
+`feature_flags`. They should match the product folder name.
+
+   **Tool name length limit:** tool names must be **52 characters or fewer**.
+   This limit exists because MCP clients enforce different combined limits on server+tool name:
+
+   | Client           | Limit                          | Notes                                                                 |
+   | ---------------- | ------------------------------ | --------------------------------------------------------------------- |
+   | MCP spec (draft) | 1–128 chars, `[A-Za-z0-9_\-.]` | Recommendation, not hard-enforced                                     |
+   | Claude Code      | 64 chars                       | Prefixes tool names with `mcp____`                                    |
+   | Cursor           | 60 chars combined              | `server_name + tool_name`; tools exceeding this are silently filtered |
+   | OpenAI API       | `^[a-zA-Z0-9_-]+$`, 64 chars   | No dots allowed                                                       |
+
+   With the server name "posthog" (7 chars) plus a separator, 52 characters is the safe zone.
+   CI runs `pnpm --filter=@posthog/mcp lint-tool-names` to enforce both length and pattern.
    If you hit the limit, shorten the domain prefix or use a more concise action name.

    ```yaml
diff --git a/services/mcp/scripts/lint-tool-names.ts b/services/mcp/scripts/lint-tool-names.ts
index 740afbd483ae..26ae2bfcc9fe 100644
--- a/services/mcp/scripts/lint-tool-names.ts
+++ b/services/mcp/scripts/lint-tool-names.ts
@@ -1,10 +1,17 @@
 #!/usr/bin/env tsx
 /**
- * Lint check: ensures MCP tool names don't exceed the length limit.
+ * Lint check: ensures all MCP tool names satisfy length and pattern constraints.
  *
- * Some MCP clients (notably Cursor) enforce a 60-character combined limit on
- * server_name + tool_name. With server name "posthog" (7 chars), tool names
- * must be <= 52 chars.
+ * Validates tool names from three sources:
+ *   1. YAML definitions (products and services/mcp/definitions)
+ *   2. Handwritten JSON definitions (tool-definitions.json, tool-definitions-v2.json)
+ *   3. Generated JSON definitions (generated-tool-definitions.json)
+ *
+ * Length: tool names must be <= 52 chars because some MCP clients (notably Cursor)
+ * enforce a 60-char combined server_name + tool_name limit ("posthog" is 7 chars).
+ *
+ * Pattern: tool names must be lowercase kebab-case ([a-z0-9-], no leading/trailing
+ * hyphens) for cross-client compatibility.
  *
  * Usage:
  *   pnpm --filter=@posthog/mcp lint-tool-names
@@ -14,19 +21,34 @@ import * as path from 'node:path'
 import { parse as parseYaml } from 'yaml'

 import { discoverDefinitions } from './lib/definitions.mjs'
-import { CategoryConfigSchema, MAX_TOOL_NAME_LENGTH } from './yaml-config-schema'
+import { CategoryConfigSchema, MAX_TOOL_NAME_LENGTH, TOOL_NAME_PATTERN } from './yaml-config-schema'

 const MCP_ROOT = path.resolve(__dirname, '..')
 const REPO_ROOT = path.resolve(MCP_ROOT, '../..')
 const DEFINITIONS_DIR = path.resolve(MCP_ROOT, 'definitions')
 const PRODUCTS_DIR = path.resolve(REPO_ROOT, 'products')
+const SCHEMA_DIR = path.resolve(MCP_ROOT, 'schema')

-/** Pre-existing tools that exceed the limit. Remove entries as they get renamed. */
-const PREEXISTING_EXCEPTIONS: Set<string> = new Set(['warehouse-saved-queries-revert-materialization-create'])
+/** Pre-existing tools that exceed the length limit. Remove entries as they get renamed. */
+const PREEXISTING_LENGTH_EXCEPTIONS: Set<string> = new Set(['warehouse-saved-queries-revert-materialization-create'])

-function main(): void {
+type Violation = { source: string; tool: string; reason: string }
+
+function validateToolName(name: string, source: string, violations: Violation[]): void {
+    if (name.length > MAX_TOOL_NAME_LENGTH && !PREEXISTING_LENGTH_EXCEPTIONS.has(name)) {
+        violations.push({ source, tool: name, reason: `${name.length} chars (max ${MAX_TOOL_NAME_LENGTH})` })
+    }
+    if (!TOOL_NAME_PATTERN.test(name)) {
+        violations.push({
+            source,
+            tool: name,
+            reason: `invalid pattern (must be lowercase kebab-case: ${TOOL_NAME_PATTERN})`,
+        })
+    }
+}
+
+function validateYamlDefinitions(violations: Violation[]): boolean {
     const definitions = discoverDefinitions({ definitionsDir: DEFINITIONS_DIR, productsDir: PRODUCTS_DIR })
-    const violations: { file: string; tool: string; length: number }[] = []
     let hasErrors = false

     for (const def of definitions) {
@@ -44,27 +66,51 @@ function main(): void {
             if (!config.enabled) {
                 continue
             }
-            if (name.length > MAX_TOOL_NAME_LENGTH && !PREEXISTING_EXCEPTIONS.has(name)) {
-                violations.push({ file: label, tool: name, length: name.length })
-            }
+            validateToolName(name, label, violations)
         }
     }

+    return hasErrors
+}
+
+function validateJsonDefinitions(fileName: string, violations: Violation[]): boolean {
+    const filePath = path.resolve(SCHEMA_DIR, fileName)
+    if (!fs.existsSync(filePath)) {
+        return false
+    }
+    const label = path.relative(REPO_ROOT, filePath)
+    const content = JSON.parse(fs.readFileSync(filePath, 'utf-8')) as Record<string, unknown>
+
+    for (const name of Object.keys(content)) {
+        validateToolName(name, label, violations)
+    }
+    return false
+}
+
+function main(): void {
+    const violations: Violation[] = []
+    let hasErrors = false
+
+    hasErrors = validateYamlDefinitions(violations) || hasErrors
+
+    for (const jsonFile of ['tool-definitions.json', 'tool-definitions-v2.json', 'generated-tool-definitions.json']) {
+        hasErrors = validateJsonDefinitions(jsonFile, violations) || hasErrors
+    }
+
     if (violations.length === 0) {
         if (!hasErrors) {
-            process.stdout.write(`All enabled tool names are within the ${MAX_TOOL_NAME_LENGTH}-char limit.\n`)
+            process.stdout.write(
+                `All tool names pass validation (max ${MAX_TOOL_NAME_LENGTH} chars, pattern ${TOOL_NAME_PATTERN}).\n`
+            )
         }
         return
     }

-    process.stderr.write(
-        `Found ${violations.length} tool name(s) exceeding ${MAX_TOOL_NAME_LENGTH}-char limit ` +
-            `(Cursor enforces a 60-char combined server+tool name limit, "posthog" is 7 chars):\n\n`
-    )
+    process.stderr.write(`Found ${violations.length} tool name violation(s):\n\n`)
     for (const v of violations) {
-        process.stderr.write(`  ${v.tool} (${v.length} chars) in ${v.file}\n`)
+        process.stderr.write(`  ${v.tool}: ${v.reason} (${v.source})\n`)
     }
-    process.stderr.write(`\nTo fix: shorten the tool name in the YAML config.\n`)
+    process.stderr.write(`\nTo fix: shorten or rename the tool name in the config.\n`)
     process.exitCode = 1
 }

diff --git a/services/mcp/scripts/yaml-config-schema.ts b/services/mcp/scripts/yaml-config-schema.ts
index 5c71d926f8c6..d44462d030ec 100644
--- a/services/mcp/scripts/yaml-config-schema.ts
+++ b/services/mcp/scripts/yaml-config-schema.ts
@@ -84,17 +84,31 @@ export type EnabledToolConfig = Omit<ToolConfig, 'scopes' | 'annotations'> & {
  * server_name + tool_name. With server name "posthog" (7 chars), tool names
  * must be <= 52 chars to stay under that limit.
  *
- * Enforced by lint-tool-names.ts rather than here so pre-existing tools
- * that already exceed the limit don't break schema validation.
+ * Length is enforced by lint-tool-names.ts rather than here so pre-existing
+ * tools that already exceed the limit don't break schema validation.
  */
 export const MAX_TOOL_NAME_LENGTH = 52

+/** Tool names must be lowercase kebab-case: letters, digits, hyphens. No leading/trailing hyphens. */
+export const TOOL_NAME_PATTERN = /^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/
+
+/** Feature identifiers must be lowercase snake_case: letters, digits, underscores. */
+export const FEATURE_NAME_PATTERN = /^[a-z][a-z0-9_]*$/
+
 export const CategoryConfigSchema = z
     .object({
         category: z.string(),
-        feature: z.string(),
+        feature: z.string().regex(FEATURE_NAME_PATTERN, 'Feature must be lowercase snake_case: [a-z0-9_]'),
         url_prefix: z.string(),
-        tools: z.record(z.string(), ToolConfigSchema),
+        tools: z.record(
+            z
+                .string()
+                .regex(
+                    TOOL_NAME_PATTERN,
+                    'Tool name must be lowercase kebab-case: [a-z0-9-], no leading/trailing hyphens'
+                ),
+            ToolConfigSchema
+        ),
     })
     .strict()

diff --git a/services/mcp/tests/unit/tool-name-validation.test.ts b/services/mcp/tests/unit/tool-name-validation.test.ts
new file mode 100644
index 000000000000..b97d64463851
--- /dev/null
+++ b/services/mcp/tests/unit/tool-name-validation.test.ts
@@ -0,0 +1,25 @@
+import { describe, expect, it } from 'vitest'
+
+import { TOOL_MAP } from '@/tools'
+import { GENERATED_TOOL_MAP } from '@/tools/generated'
+
+import { MAX_TOOL_NAME_LENGTH, TOOL_NAME_PATTERN } from '../../scripts/yaml-config-schema'
+
+/** Pre-existing tools that exceed the length limit. Remove entries as they get renamed. */
+const PREEXISTING_LENGTH_EXCEPTIONS: Set<string> = new Set(['warehouse-saved-queries-revert-materialization-create'])
+
+describe('Tool name validation', () => {
+    const allTools = { ...TOOL_MAP, ...GENERATED_TOOL_MAP }
+
+    it.each(Object.keys(allTools))('%s — name matches map key, length, and pattern', (mapKey) => {
+        const factory = allTools[mapKey]!
+        const tool = factory()
+
+        expect(tool.name).toBe(mapKey)
+        expect(tool.name).toMatch(TOOL_NAME_PATTERN)
+
+        if (!PREEXISTING_LENGTH_EXCEPTIONS.has(tool.name)) {
+            expect(tool.name.length).toBeLessThanOrEqual(MAX_TOOL_NAME_LENGTH)
+        }
+    })
+})

PATCH

echo "Patch applied successfully."
