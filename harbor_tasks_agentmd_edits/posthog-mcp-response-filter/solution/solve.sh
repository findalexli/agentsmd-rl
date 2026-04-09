#!/usr/bin/env bash
set -euo pipefail

cd /workspace/posthog

# Idempotent: skip if already applied
if grep -q 'pickResponseFields' services/mcp/src/tools/tool-utils.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.agents/skills/implementing-mcp-tools/SKILL.md b/.agents/skills/implementing-mcp-tools/SKILL.md
index 22362ff005..f5ab8461f8 100644
--- a/.agents/skills/implementing-mcp-tools/SKILL.md
+++ b/.agents/skills/implementing-mcp-tools/SKILL.md
@@ -139,6 +139,10 @@ tools:
     param_overrides:
       name:
         description: Custom description for the LLM
+    response: # filter response fields (applied per-item on list endpoints)
+      include: [id, key, name] # keep only these fields (dot-path wildcards supported)
+      exclude: [filters.groups.*.properties] # remove these fields
+      # include and exclude are mutually exclusive
 ```

 Unknown keys are rejected at build time (Zod `.strict()`).
diff --git a/docs/published/handbook/engineering/ai/implementing-mcp-tools.md b/docs/published/handbook/engineering/ai/implementing-mcp-tools.md
index e2217a9104..18102a8584 100644
--- a/docs/published/handbook/engineering/ai/implementing-mcp-tools.md
+++ b/docs/published/handbook/engineering/ai/implementing-mcp-tools.md
@@ -234,6 +234,10 @@ Product teams own their definitions and control which operations are exposed as
        enrich_url: '{id}' # appended to url_prefix for result URLs
        exclude_params: [field] # hide params from tool input
        include_params: [field] # whitelist params (excludes all others)
+       response: # filter response fields (applied per-item on list endpoints)
+         include: [id, key, name] # keep only these fields (dot-path wildcards supported)
+         exclude: [filters.groups.*.properties] # remove these fields
+         # include and exclude are mutually exclusive
        input_schema: ActionCreateSchema # use a hand-crafted schema from tool-inputs (optional)
        param_overrides: # override Orval-generated param descriptions or schemas
          name:
diff --git a/products/feature_flags/mcp/tools.yaml b/products/feature_flags/mcp/tools.yaml
index 7d09f24fef..10ab5e8837 100644
--- a/products/feature_flags/mcp/tools.yaml
+++ b/products/feature_flags/mcp/tools.yaml
@@ -38,6 +38,14 @@ tools:
                 description:
                     Search by feature flag key or name (case-insensitive). Use this to find the flag ID for get/update/delete
                     tools.
+        response:
+            include:
+                - id
+                - key
+                - name
+                - updated_at
+                - status
+                - tags
     feature-flag-get-definition:
         operation: feature_flags_retrieve_2
         enabled: true
diff --git a/services/mcp/definitions/README.md b/services/mcp/definitions/README.md
index e40c44a403..4b83018723 100644
--- a/services/mcp/definitions/README.md
+++ b/services/mcp/definitions/README.md
@@ -110,6 +110,10 @@ tools:
     enrich_url: '{id}' # appended to url_prefix for result URLs
     exclude_params: [field] # hide params from tool input
     include_params: [field] # whitelist params (excludes all others)
+    response: # filter response fields (applied per-item on list endpoints)
+      include: [id, key, name] # keep only these fields (dot-path wildcards supported)
+      exclude: [filters.groups.*.properties] # remove these fields
+      # include and exclude are mutually exclusive
     requires_ai_consent: true # gate behind org AI data processing consent
     param_overrides: # override individual param descriptions or schemas
       name:
diff --git a/services/mcp/scripts/generate-tools.ts b/services/mcp/scripts/generate-tools.ts
index 10e4e35277..50676896f8 100644
--- a/services/mcp/scripts/generate-tools.ts
+++ b/services/mcp/scripts/generate-tools.ts
@@ -462,35 +462,72 @@ function buildPathExpr(urlPath: string, pathParamNames: string[], paramAccessPre
     return pathExpr
 }

+// ------------------------------------------------------------------
+// Response filtering templates
+// ------------------------------------------------------------------
+
+function buildResponseFilter(config: ToolConfig): {
+    code: string
+    helperImport: 'pickResponseFields' | 'omitResponseFields' | null
+} {
+    if (config.response?.include?.length) {
+        const paths = config.response?.include.map((f) => `'${f}'`).join(', ')
+        if (config.list) {
+            return {
+                code: `        const filtered = { ...result, results: result.results.map((item: any) => pickResponseFields(item, [${paths}])) } as typeof result\n`,
+                helperImport: 'pickResponseFields',
+            }
+        }
+        return {
+            code: `        const filtered = pickResponseFields(result, [${paths}]) as typeof result\n`,
+            helperImport: 'pickResponseFields',
+        }
+    }
+    if (config.response?.exclude?.length) {
+        const paths = config.response?.exclude.map((f) => `'${f}'`).join(', ')
+        if (config.list) {
+            return {
+                code: `        const filtered = { ...result, results: result.results.map((item: any) => omitResponseFields(item, [${paths}])) } as typeof result\n`,
+                helperImport: 'omitResponseFields',
+            }
+        }
+        return {
+            code: `        const filtered = omitResponseFields(result, [${paths}]) as typeof result\n`,
+            helperImport: 'omitResponseFields',
+        }
+    }
+    return { code: '', helperImport: null }
+}
+
 // ------------------------------------------------------------------
 // Response enrichment templates
 // ------------------------------------------------------------------

-function buildEnrichment(config: ToolConfig, category: CategoryConfig): string {
+function buildEnrichment(config: ToolConfig, category: CategoryConfig, resultVar = 'result'): string {
     const baseUrl = category.url_prefix

     if (config.list && config.enrich_url) {
         const { prefix, field } = parseEnrichUrl(config.enrich_url)
         return [
             `        return await withPostHogUrl(context, {`,
-            `            ...result,`,
-            `            results: await Promise.all(result.results.map((item) => withPostHogUrl(context, item, \`${baseUrl}/${prefix}\${item.${field}}\`))),`,
+            `            ...${resultVar},`,
+            `            results: await Promise.all(${resultVar}.results.map((item) => withPostHogUrl(context, item, \`${baseUrl}/${prefix}\${item.${field}}\`))),`,
             `        }, '${baseUrl}')`,
             ``,
         ].join('\n')
     }

     if (config.list) {
-        return `        return await withPostHogUrl(context, result, '${baseUrl}')\n`
+        return `        return await withPostHogUrl(context, ${resultVar}, '${baseUrl}')\n`
     }

     if (config.enrich_url) {
         const { prefix, field } = parseEnrichUrl(config.enrich_url)

-        return `        return await withPostHogUrl(context, result, \`${baseUrl}/${prefix}\${result.${field}}\`)\n`
+        return `        return await withPostHogUrl(context, ${resultVar}, \`${baseUrl}/${prefix}\${${resultVar}.${field}}\`)\n`
     }

-    return `        return result\n`
+    return `        return ${resultVar}\n`
 }

 // ------------------------------------------------------------------
@@ -511,6 +548,7 @@ function generateToolCode(
     responseType: string | undefined
     needsWithPostHogUrl: boolean
     hasEnrichment: boolean
+    responseFilterImport: 'pickResponseFields' | 'omitResponseFields' | null
 } {
     const schemaName = `${toPascalCase(toolName)}Schema`
     const factoryName = toCamelCase(toolName)
@@ -585,8 +623,27 @@ function generateToolCode(
     }
     handlerBody += `        })\n`

+    // Response filtering — pick/omit fields before enrichment
+    const responseFilter = buildResponseFilter(config)
+    if (responseFilter.code) {
+        // Warn if filtering might break enrich_url
+        if (config.enrich_url) {
+            const { field } = parseEnrichUrl(config.enrich_url)
+            if (config.response?.exclude?.includes(field)) {
+                console.warn(`Warning: tool "${toolName}" excludes response field "${field}" used by enrich_url`)
+            }
+            if (config.response?.include?.length && !config.response?.include.includes(field)) {
+                console.warn(
+                    `Warning: tool "${toolName}" uses response_include without "${field}" needed by enrich_url`
+                )
+            }
+        }
+    }
+    handlerBody += responseFilter.code
+
     // Response enrichment — adds _posthogUrl for "View in PostHog" links
-    handlerBody += buildEnrichment(config, category)
+    const enrichmentVar = responseFilter.code ? 'filtered' : 'result'
+    handlerBody += buildEnrichment(config, category, enrichmentVar)

     // Compute the result type for the ToolBase generic parameter
     let resultType: string
@@ -632,6 +689,7 @@ const ${factoryName} = (): ToolBase<typeof ${schemaName}, ${resultType}> => ${fa
         responseType,
         needsWithPostHogUrl,
         hasEnrichment,
+        responseFilterImport: responseFilter.helperImport,
     }
 }

@@ -650,6 +708,7 @@ function generateCustomSchemaToolCode(
     responseType: string | undefined
     needsWithPostHogUrl: boolean
     hasEnrichment: boolean
+    responseFilterImport: 'pickResponseFields' | 'omitResponseFields' | null
 } {
     const pathParamNames = extractPathParams(resolved.path)

@@ -694,7 +753,12 @@ function generateCustomSchemaToolCode(
     }
     handlerBody += `        })\n`

-    handlerBody += buildEnrichment(config, category)
+    // Response filtering — pick/omit fields before enrichment
+    const responseFilter = buildResponseFilter(config)
+    handlerBody += responseFilter.code
+
+    const enrichmentVar = responseFilter.code ? 'filtered' : 'result'
+    handlerBody += buildEnrichment(config, category, enrichmentVar)

     const code = `
 const ${schemaName} = ${config.input_schema}
@@ -714,6 +778,7 @@ ${handlerBody}    },
         responseType,
         needsWithPostHogUrl: false,
         hasEnrichment: false,
+        responseFilterImport: responseFilter.helperImport,
     }
 }

@@ -791,6 +856,8 @@ function generateCategoryFile(

     let hasEnrichment = false

+    const responseFilterImports = new Set<string>()
+
     for (const [name, config, resolved] of enabledTools) {
         const result = generateToolCode(name, config, resolved, category, spec, knownTypes)
         toolCodes.push(result.code)
@@ -809,6 +876,9 @@ function generateCategoryFile(
         if (result.hasEnrichment) {
             hasEnrichment = true
         }
+        if (result.responseFilterImport) {
+            responseFilterImports.add(result.responseFilterImport)
+        }
     }

     // Generate query wrapper Zod schemas and registrations if wrappers are present
@@ -923,6 +993,9 @@ function generateCategoryFile(
     if (hasEnrichment) {
         toolUtilsValueImports.push('withPostHogUrl')
     }
+    for (const imp of responseFilterImports) {
+        toolUtilsValueImports.push(imp)
+    }
     let toolUtilsImportLine = ''
     if (toolUtilsValueImports.length > 0 && toolUtilsTypeImports.length > 0) {
         toolUtilsImportLine = `import { ${toolUtilsValueImports.join(', ')}, type ${toolUtilsTypeImports.join(', type ')} } from '@/tools/tool-utils'\n`
@@ -1327,6 +1400,7 @@ ${spreads}

 // Export for testing
 export {
+    buildResponseFilter,
     composeToolSchema,
     extractPathParams,
     generateCategoryFile,
diff --git a/services/mcp/scripts/yaml-config-schema.ts b/services/mcp/scripts/yaml-config-schema.ts
index 91794e40a4..ebdd4fddf3 100644
--- a/services/mcp/scripts/yaml-config-schema.ts
+++ b/services/mcp/scripts/yaml-config-schema.ts
@@ -62,6 +62,22 @@ export const ToolConfigSchema = z
          * the request body still sends the original field name.
          */
         rename_params: z.record(z.string(), z.string()).optional(),
+        /**
+         * Response field filtering. Supports dot-path patterns with wildcards (e.g. 'filters.groups.*.key').
+         * For list endpoints, applied to each item in `results`. `include` and `exclude` are mutually exclusive.
+         */
+        response: z
+            .object({
+                /** Dot-path patterns of response fields to keep. Only matched fields are preserved. */
+                include: z.array(z.string()).optional(),
+                /** Dot-path patterns of response fields to remove. */
+                exclude: z.array(z.string()).optional(),
+            })
+            .strict()
+            .refine((data) => !(data.include?.length && data.exclude?.length), {
+                message: 'response.include and response.exclude are mutually exclusive',
+            })
+            .optional(),
     })
     .strict()
     .refine(
diff --git a/services/mcp/src/tools/tool-utils.ts b/services/mcp/src/tools/tool-utils.ts
index 2548f017ba..19885b38f7 100644
--- a/services/mcp/src/tools/tool-utils.ts
+++ b/services/mcp/src/tools/tool-utils.ts
@@ -12,3 +12,107 @@ export async function withPostHogUrl<T>(context: Context, result: T, path: strin

     return { ...result, _posthogUrl: fullUrl } as WithPostHogUrl<T>
 }
+
+/**
+ * Pick only fields matching the given dot-path patterns.
+ * Supports wildcards: `'groups.*.key'` iterates all array items / object keys.
+ */
+export function pickResponseFields<T>(obj: T, paths: string[]): Partial<T> {
+    const result: Record<string, unknown> = {}
+    for (const p of paths) {
+        copyAtPath(obj, result, p.split('.'))
+    }
+    return result as Partial<T>
+}
+
+function copyAtPath(source: unknown, target: Record<string, unknown>, segments: string[]): void {
+    if (source === null || source === undefined || typeof source !== 'object') {
+        return
+    }
+    const [head, ...rest] = segments
+    if (!head) {
+        return
+    }
+    if (head === '*') {
+        const src = source as Record<string, unknown>
+        if (Array.isArray(source)) {
+            const arr = target as unknown as unknown[]
+            for (let i = 0; i < source.length; i++) {
+                if (arr[i] === undefined) {
+                    arr[i] = {}
+                }
+                if (rest.length === 0) {
+                    arr[i] = structuredClone(source[i])
+                } else {
+                    copyAtPath(source[i], arr[i] as Record<string, unknown>, rest)
+                }
+            }
+        } else {
+            for (const key of Object.keys(src)) {
+                if (target[key] === undefined) {
+                    target[key] = {}
+                }
+                if (rest.length === 0) {
+                    target[key] = structuredClone(src[key])
+                } else {
+                    copyAtPath(src[key], target[key] as Record<string, unknown>, rest)
+                }
+            }
+        }
+        return
+    }
+    const src = (source as Record<string, unknown>)[head]
+    if (src === undefined) {
+        return
+    }
+    if (rest.length === 0) {
+        target[head] = structuredClone(src)
+    } else {
+        if (src === null || typeof src !== 'object') {
+            return
+        }
+        if (target[head] === undefined) {
+            target[head] = Array.isArray(src) ? [] : {}
+        }
+        copyAtPath(src, target[head] as Record<string, unknown>, rest)
+    }
+}
+
+/**
+ * Remove fields matching the given dot-path patterns.
+ * Supports wildcards: `'groups.*.properties'` iterates all array items / object keys.
+ */
+export function omitResponseFields<T>(obj: T, paths: string[]): Partial<T> {
+    const result = structuredClone(obj)
+    for (const p of paths) {
+        removeAtPath(result, p.split('.'))
+    }
+    return result as Partial<T>
+}
+
+function removeAtPath(obj: unknown, segments: string[]): void {
+    if (obj === null || obj === undefined || typeof obj !== 'object') {
+        return
+    }
+    const [head, ...rest] = segments
+    if (!head) {
+        return
+    }
+    if (head === '*') {
+        const items = Array.isArray(obj) ? obj : Object.values(obj)
+        for (const item of items) {
+            if (rest.length === 0) {
+                // Wildcard at leaf makes no sense for omit — skip
+            } else {
+                removeAtPath(item, rest)
+            }
+        }
+        return
+    }
+    const record = obj as Record<string, unknown>
+    if (rest.length === 0) {
+        delete record[head]
+    } else {
+        removeAtPath(record[head], rest)
+    }
+}

PATCH

echo "Patch applied successfully."
