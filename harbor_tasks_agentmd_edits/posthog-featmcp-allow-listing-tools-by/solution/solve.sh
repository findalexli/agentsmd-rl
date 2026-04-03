#!/usr/bin/env bash
set -euo pipefail

cd /workspace/posthog

# Idempotent: skip if already applied
if grep -q "const toolsParam = url.searchParams.get('tools')" services/mcp/src/index.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/services/mcp/README.md b/services/mcp/README.md
index 256d1f5fbbbf..f04407e95cd8 100644
--- a/services/mcp/README.md
+++ b/services/mcp/README.md
@@ -302,6 +302,22 @@ Available features:

 To view which tools are available per feature, see our [documentation](https://posthog.com/docs/model-context-protocol) or check `schema/tool-definitions-all.json`.

+### Tool filtering
+
+For finer-grained control you can allowlist specific tools by name using the `tools` query parameter. Only the exact tool names listed will be exposed, regardless of their feature category.
+
+```text
+https://mcp.posthog.com/mcp?tools=dashboard-get,feature-flag-get-all,execute-sql
+```
+
+When `features` and `tools` are both provided they are combined as a **union** — a tool is included if it matches a feature category **or** is in the tools list. This lets you select a feature group and add a handful of individual tools on top:
+
+```text
+https://mcp.posthog.com/mcp?features=flags&tools=dashboard-get
+```
+
+The example above exposes all flag tools plus `dashboard-get`.
+
 ### Data processing

 The MCP server is hosted on a Cloudflare worker which can be located outside of the EU / US, for this reason the MCP server does not store any sensitive data outside of your cloud region.
diff --git a/services/mcp/src/index.ts b/services/mcp/src/index.ts
index fa674bcffa2e..4846bae6544a 100644
--- a/services/mcp/src/index.ts
+++ b/services/mcp/src/index.ts
@@ -236,6 +236,9 @@ const handleRequest = async (
     const featuresParam = url.searchParams.get('features')
     const features = featuresParam ? featuresParam.split(',').filter(Boolean) : undefined

+    const toolsParam = url.searchParams.get('tools')
+    const tools = toolsParam ? toolsParam.split(',').filter(Boolean) : undefined
+
     // Region param is used to route API calls to the correct PostHog instance (US or EU).
     // This is set by the wizard based on user's cloud region selection during MCP setup.
     const regionParam = url.searchParams.get('region') || undefined
@@ -245,7 +248,7 @@ const handleRequest = async (
     const readOnlyRaw = request.headers.get('x-posthog-readonly') || url.searchParams.get('readonly')
     const readOnly = readOnlyRaw === 'true' || readOnlyRaw === '1' || undefined

-    const extraContextProps = { features, region: regionParam, version, readOnly }
+    const extraContextProps = { features, tools, region: regionParam, version, readOnly }
     Object.assign(ctx.props, extraContextProps)
     log.extend(extraContextProps)

diff --git a/services/mcp/src/mcp.ts b/services/mcp/src/mcp.ts
index 872a7b143472..97c24ad0bf7c 100644
--- a/services/mcp/src/mcp.ts
+++ b/services/mcp/src/mcp.ts
@@ -37,6 +37,7 @@ export type RequestProperties = {
     apiToken: string
     sessionId?: string
     features?: string[]
+    tools?: string[]
     region?: string
     version?: number
     organizationId?: string
@@ -416,7 +417,7 @@ export class MCP extends McpAgent<Env> {
     }

     async init(): Promise<void> {
-        const { features, version: clientVersion, organizationId, projectId, readOnly } = this.requestProperties
+        const { features, tools, version: clientVersion, organizationId, projectId, readOnly } = this.requestProperties

         // Pre-seed cache, fetch group types, and evaluate feature flag in parallel
         const groupTypesPromise = projectId ? this.getOrFetchGroupTypes(projectId) : Promise.resolve(undefined)
@@ -456,6 +457,7 @@ export class MCP extends McpAgent<Env> {
         const { getToolsFromContext } = await import('@/tools')
         const allTools = await getToolsFromContext(context, {
             features,
+            tools,
             version,
             excludeTools,
             readOnly,
diff --git a/services/mcp/src/tools/toolDefinitions.ts b/services/mcp/src/tools/toolDefinitions.ts
index aeab129c33df..d8f833e561e5 100644
--- a/services/mcp/src/tools/toolDefinitions.ts
+++ b/services/mcp/src/tools/toolDefinitions.ts
@@ -70,6 +70,7 @@ export function getToolDefinition(toolName: string, version?: number): ToolDefin

 export interface ToolFilterOptions {
     features?: string[] | undefined
+    tools?: string[] | undefined
     version?: number | undefined
     excludeTools?: string[] | undefined
     readOnly?: boolean | undefined
@@ -81,7 +82,7 @@ function normalizeFeatureName(name: string): string {
 }

 export function getToolsForFeatures(options?: ToolFilterOptions): string[] {
-    const { features, version, readOnly, aiConsentGiven } = options || {}
+    const { features, tools, version, readOnly, aiConsentGiven } = options || {}
     const toolDefinitions = getToolDefinitions(version)

     let entries = Object.entries(toolDefinitions)
@@ -91,13 +92,22 @@ export function getToolsForFeatures(options?: ToolFilterOptions): string[] {
         entries = entries.filter(([_, definition]) => definition.new_mcp !== false)
     }

-    // Filter by features if provided. Normalize hyphens to underscores so that
-    // both "error-tracking" and "error_tracking" match regardless of convention.
-    if (features && features.length > 0) {
-        const normalizedFeatures = new Set(features.map(normalizeFeatureName))
-        entries = entries.filter(
-            ([_, definition]) => definition.feature && normalizedFeatures.has(normalizeFeatureName(definition.feature))
-        )
+    // Filter by features and/or tools allowlist (OR union).
+    // When both are provided, a tool is included if it matches a feature category OR is in the tools list.
+    // Normalize hyphens to underscores so that both "error-tracking" and "error_tracking" match.
+    const hasFeatures = features && features.length > 0
+    const hasTools = tools && tools.length > 0
+    if (hasFeatures || hasTools) {
+        const normalizedFeatures = hasFeatures ? new Set(features.map(normalizeFeatureName)) : null
+        const allowedTools = hasTools ? new Set(tools) : null
+
+        entries = entries.filter(([toolName, definition]) => {
+            const matchesFeature = normalizedFeatures
+                ? definition.feature && normalizedFeatures.has(normalizeFeatureName(definition.feature))
+                : false
+            const matchesTool = allowedTools ? allowedTools.has(toolName) : false
+            return matchesFeature || matchesTool
+        })
     }

     // In read-only mode, only expose tools annotated as read-only
diff --git a/services/mcp/tests/unit/tool-filtering.test.ts b/services/mcp/tests/unit/tool-filtering.test.ts
index bce3f29c42a4..7d4abf2fb43a 100644
--- a/services/mcp/tests/unit/tool-filtering.test.ts
+++ b/services/mcp/tests/unit/tool-filtering.test.ts
@@ -107,6 +107,84 @@ describe('Tool Filtering - Features', () => {
     })
 })

+describe('Tool Filtering - Tools Allowlist', () => {
+    describe('getToolsForFeatures with tools', () => {
+        it('should return all tools when tools is undefined', () => {
+            const allTools = getToolsForFeatures({})
+            const withUndefinedTools = getToolsForFeatures({ tools: undefined })
+            expect(withUndefinedTools).toEqual(allTools)
+        })
+
+        it('should return all tools when tools is empty array', () => {
+            const allTools = getToolsForFeatures({})
+            const withEmptyTools = getToolsForFeatures({ tools: [] })
+            expect(withEmptyTools).toEqual(allTools)
+        })
+
+        it('should return only specified tools', () => {
+            const tools = getToolsForFeatures({ tools: ['dashboard-get', 'dashboard-create'] })
+            expect(tools).toContain('dashboard-get')
+            expect(tools).toContain('dashboard-create')
+            expect(tools).toHaveLength(2)
+        })
+
+        it('should return empty array for nonexistent tool names', () => {
+            const tools = getToolsForFeatures({ tools: ['nonexistent-tool'] })
+            expect(tools).toEqual([])
+        })
+
+        it('should union with features (OR) when both are provided', () => {
+            const tools = getToolsForFeatures({ features: ['flags'], tools: ['dashboard-get'] })
+
+            // Should include flag tools from features
+            expect(tools).toContain('feature-flag-get-definition')
+            expect(tools).toContain('feature-flag-get-all')
+
+            // Should also include the explicitly named tool
+            expect(tools).toContain('dashboard-get')
+
+            // Should not include unrelated tools
+            expect(tools).not.toContain('insights-get-all')
+        })
+
+        it('should still apply readOnly on top of tools filter', () => {
+            const tools = getToolsForFeatures({ tools: ['dashboard-get', 'dashboard-create'], readOnly: true })
+
+            expect(tools).toContain('dashboard-get')
+            expect(tools).not.toContain('dashboard-create')
+        })
+
+        it('should still apply aiConsentGiven on top of tools filter', () => {
+            const withoutConsent = getToolsForFeatures({
+                tools: ['dashboard-get', 'query-generate-hogql-from-question'],
+                aiConsentGiven: false,
+            })
+            expect(withoutConsent).toContain('dashboard-get')
+            expect(withoutConsent).not.toContain('query-generate-hogql-from-question')
+
+            const withConsent = getToolsForFeatures({
+                tools: ['dashboard-get', 'query-generate-hogql-from-question'],
+                aiConsentGiven: true,
+            })
+            expect(withConsent).toContain('dashboard-get')
+            expect(withConsent).toContain('query-generate-hogql-from-question')
+        })
+    })
+
+    it('should combine tools with excludeTools via getToolsFromContext', async () => {
+        const context = createMockContext(['*'])
+        const tools = await getToolsFromContext(context, {
+            tools: ['dashboard-get', 'dashboard-create', 'dashboard-delete'],
+            excludeTools: ['dashboard-delete'],
+        })
+        const toolNames = tools.map((t) => t.name)
+
+        expect(toolNames).toContain('dashboard-get')
+        expect(toolNames).toContain('dashboard-create')
+        expect(toolNames).not.toContain('dashboard-delete')
+    })
+})
+
 const createMockContext = (scopes: string[]): Context => ({
     api: {} as any,
     cache: {} as any,

PATCH

echo "Patch applied successfully."
