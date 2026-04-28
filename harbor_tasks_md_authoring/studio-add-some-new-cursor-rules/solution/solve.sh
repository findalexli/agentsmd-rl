#!/usr/bin/env bash
set -euo pipefail

cd /workspace/studio

# Idempotency guard
if grep -qF "**Prefer Drizzle ORM for all new code.** We're gradually migrating away from Sup" ".cursor/rules/api-development.mdc" && grep -qF "Tool groups automatically become virtual integrations accessible via `i:{group-n" ".cursor/rules/data-flow.mdc" && grep -qF "This guide covers the complete pattern for adding new native applications to dec" ".cursor/rules/native-apps-and-views.mdc" && grep -qF "For features that manipulate CSS or DOM directly (like theme editors, live previ" ".cursor/rules/react-ts.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/api-development.mdc b/.cursor/rules/api-development.mdc
@@ -79,7 +79,103 @@ const createTool = createToolGroup("Feature", {
 });
 ```
 
-### 1.2 Tool Implementation Pattern
+### 1.2 Return Type Requirements
+
+**CRITICAL**: MCP tools MUST return objects, not nullable primitives:
+
+```typescript
+// ❌ BAD - TypeScript error: null not assignable to object
+export const getFeature = createTool({
+  name: "FEATURE_GET",
+  handler: async ({ id }, c) => {
+    const feature = await fetchFeature(id);
+    return feature || null;  // ERROR: Type 'Feature | null' not assignable
+  },
+});
+
+// ✅ GOOD - Wrap in object
+export const getFeature = createTool({
+  name: "FEATURE_GET",
+  outputSchema: z.object({ 
+    feature: FeatureSchema.nullable() 
+  }),
+  handler: async ({ id }, c) => {
+    const feature = await fetchFeature(id);
+    return { feature: feature || null };  // ✅ Always returns object
+  },
+});
+```
+
+### 1.3 Organization Context Handling
+
+For org-level operations, auto-resolve context and use slug-based authorization:
+
+```typescript
+import { getOrgIdFromContext } from "../projects/util.ts";
+
+export const updateOrgFeature = createTool({
+  name: "FEATURE_UPDATE_ORG",
+  inputSchema: z.object({
+    // Do NOT include orgId in input - always resolve from context
+    featureData: FeatureSchema,
+  }),
+  handler: async (props, c) => {
+    // 1. Auto-resolve org ID from context
+    const orgId = await getOrgIdFromContext(c);
+    
+    if (!orgId) {
+      throw new Error("No organization context available");
+    }
+
+    // 2. Use org SLUG for authorization (not ID!)
+    const orgSlug = c.locator?.org;
+    if (!orgSlug) {
+      throw new Error("No organization slug in context");
+    }
+    
+    // ✅ CORRECT - Use slug from locator
+    await assertTeamResourceAccess("TEAMS_UPDATE", orgSlug, c);
+
+    // 3. Use Drizzle for database operations
+    const result = await c.drizzle
+      .update(organizations)
+      .set({ feature: props.featureData })
+      .where(eq(organizations.id, orgId))
+      .returning();
+
+    return { feature: result[0].feature };
+  },
+});
+```
+
+**Key Points**:
+- Do NOT accept `orgId` from input - always auto-resolve from context
+- Auto-resolve using `getOrgIdFromContext(c)`
+- Always use **org slug** for `assertTeamResourceAccess`, never numeric ID
+- Use `c.drizzle` for Drizzle ORM
+
+### 1.4 Database Operations
+
+**Prefer Drizzle ORM for all new code.** We're gradually migrating away from Supabase queries:
+
+```typescript
+// ✅ PREFERRED - Use c.drizzle for Drizzle ORM
+const result = await c.drizzle
+  .select()
+  .from(organizations)
+  .where(eq(organizations.id, orgId));
+
+// ⚠️ LEGACY - c.db (Supabase client) for existing queries only
+// Avoid using for new features
+const { data, error } = await c.db
+  .from(DECO_CHAT_FEATURE_TABLE)
+  .select(SELECT_FEATURE_QUERY)
+  .eq("workspace", workspace);
+
+if (error) throw error;  // Supabase pattern
+```
+
+### 1.5 Tool Implementation Pattern
 
 ```typescript
 export const listFeatures = createTool({
diff --git a/.cursor/rules/data-flow.mdc b/.cursor/rules/data-flow.mdc
@@ -308,22 +308,44 @@ const result = await db.from("agents").insert(agent);
 React Query updates cache and triggers re-renders
 ```
 
-## 6. Best Practices
+## 6. Virtual Integrations
+
+### Tool Groups as Integrations
+Tool groups automatically become virtual integrations accessible via `i:{group-name}`:
+
+```typescript
+// Tool group definition
+export const createTool = createToolGroup("Theme", {
+  name: "Theme Management",
+  description: "Manage organization-level themes.",
+  icon: "https://assets.decocache.com/mcp/.../theme.png",
+});
+
+// Becomes virtual integration: i:theme-management
+// Accessible in frontend via:
+const { data: tools } = useTools(integration.connection);
+```
+
+## 7. Best Practices
 
 ### Tool Development
 - Always use Zod schemas for input/output validation
 - Call `context.resourceAccess.grant()` after authorization checks
 - Use descriptive tool names following the pattern `{RESOURCE}_{ACTION}`
 - Group related tools by functionality
+- Return objects, not nullable primitives (MCP requirement)
+- Use slug-based authorization for team resources
 
 ### Frontend Integration
 - Use consistent query keys from `KEYS` object
 - Implement optimistic updates for better UX
 - Handle loading and error states appropriately
 - Use `useSuspenseQuery` for critical data
+- Include `locator` in all scoped API calls
 
 ### Authorization
 - Always check workspace/team access before operations
+- Use **org slugs** for team resource access, not IDs
 - Use least-privilege principle for API keys
 - Implement proper error handling for forbidden operations
 - Log authorization failures for debugging
diff --git a/.cursor/rules/native-apps-and-views.mdc b/.cursor/rules/native-apps-and-views.mdc
@@ -0,0 +1,682 @@
+---
+description: How to add new native apps with views, MCP tools, and AI chat integration
+globs: 
+alwaysApply: false
+---
+# Adding Native Apps & Views with MCP Tool Integration
+
+This guide covers the complete pattern for adding new native applications to deco CMS, from MCP tools to frontend views with AI chat integration.
+
+## Overview
+
+Native apps are first-class features in deco CMS that:
+- Expose MCP tools for programmatic access
+- Provide dedicated UI views for user interaction
+- Integrate with AI chat for conversational interfaces
+- Appear in sidebar navigation automatically
+- Support organization and project-level scoping
+
+## Step 1: Create MCP Tools
+
+### 1.1 Define Tool Group
+
+Create a new tool group that will become a virtual integration:
+
+```typescript
+// packages/sdk/src/mcp/{feature}/api.ts
+import { createToolGroup } from "../context.ts";
+
+export const createTool = createToolGroup("{Feature}", {
+  name: "{Feature} Management",
+  description: "Manage {feature} settings and configuration.",
+  icon: "https://assets.decocache.com/mcp/{uuid}/{feature}.png",
+  // workspace: true  // Only if this is project-scoped, omit for org-level
+});
+```
+
+**Important**: The group name becomes the integration ID as `i:{name-in-kebab-case}`.
+
+### 1.2 Implement Tools with Proper Return Types
+
+MCP tools must return **objects**, not nullable primitives:
+
+```typescript
+// ❌ BAD - Returns nullable primitive
+export const getTheme = createTool({
+  name: "THEME_GET",
+  handler: async (props, c) => {
+    return theme || null;  // Type error: null not assignable to object
+  },
+});
+
+// ✅ GOOD - Returns object wrapper
+export const getTheme = createTool({
+  name: "THEME_GET",
+  outputSchema: z.object({
+    theme: themeSchema.nullable(),
+  }),
+  handler: async (props, c) => {
+    return { theme: theme || null };
+  },
+});
+```
+
+### 1.3 Handle Organization Context
+
+For org-level features, auto-resolve org ID from context:
+
+```typescript
+import { getOrgIdFromContext } from "../projects/util.ts";
+
+export const updateOrgSetting = createTool({
+  name: "SETTING_UPDATE_ORG",
+  inputSchema: z.object({
+    // Do NOT include orgId in input - always resolve from context
+    setting: settingSchema,
+  }),
+  handler: async (props, c) => {
+    // Auto-resolve from context
+    const orgId = await getOrgIdFromContext(c);
+    
+    if (!orgId) {
+      throw new Error("No organization context available");
+    }
+
+    // Use org slug for authorization (not ID!)
+    const orgSlug = c.locator?.org;
+    await assertTeamResourceAccess("TEAMS_UPDATE", orgSlug, c);
+
+    // Use drizzle for database operations
+    const result = await c.drizzle
+      .update(organizations)
+      .set({ setting: props.setting })
+      .where(eq(organizations.id, orgId))
+      .returning();
+
+    return { setting: result[0].setting };
+  },
+});
+```
+
+**Key Points**:
+- Do NOT accept `orgId` from input - always auto-resolve from context
+- Use `assertTeamResourceAccess` with **org slug**, not org ID
+- Authorization system expects slugs for team resources
+
+### 1.4 Register Tools
+
+Add to appropriate tool collection:
+
+```typescript
+// packages/sdk/src/mcp/index.ts
+
+// Project-scoped tools
+export const PROJECT_TOOLS = [
+  // ... existing tools
+  
+  // Project-scoped features
+  featureAPI.getSetting,
+  featureAPI.updateSetting,
+  
+  // Org-level features that need project context
+  featureAPI.getOrgSetting,
+  featureAPI.updateOrgSetting,
+] as const;
+
+// OR for org-level tools (if they don't need project context)
+export const ORG_TOOLS = [
+  // ... existing tools
+  featureAPI.getOrgSetting,
+  featureAPI.updateOrgSetting,
+] as const;
+```
+
+## Step 2: Create CRUD Layer
+
+### 2.1 Define Typed Operations
+
+```typescript
+// packages/sdk/src/crud/{feature}.ts
+import { MCPClient } from "../fetcher.ts";
+import type { ProjectLocator } from "../locator.ts";
+
+export interface GetOrgSettingInput {
+  locator: ProjectLocator;  // Always include for scoped clients
+  orgId: number;
+}
+
+export const getOrgSetting = async (
+  input: GetOrgSettingInput,
+  init?: RequestInit,
+): Promise<Setting | null> => {
+  const result = await MCPClient.forLocator(input.locator).SETTING_GET_ORG(
+    { orgId: input.orgId },
+    init,
+  );
+  return (result as { setting: Setting | null }).setting;
+};
+```
+
+**Key Pattern**: Always unwrap MCP tool responses that return object wrappers.
+
+### 2.2 Create React Query Hooks
+
+```typescript
+// packages/sdk/src/hooks/{feature}.ts
+import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
+import { useSDK } from "./store.tsx";
+
+export function useOrgSetting(orgId?: number) {
+  const { locator } = useSDK();
+
+  return useQuery({
+    queryKey: ["org-setting", orgId],
+    queryFn: () => orgId && locator ? getOrgSetting({ locator, orgId }) : null,
+    enabled: !!orgId && !!locator,
+  });
+}
+
+export function useUpdateOrgSetting() {
+  const client = useQueryClient();
+  const { locator } = useSDK();
+
+  return useMutation({
+    mutationFn: (input: Omit<UpdateOrgSettingInput, 'locator'>) => {
+      if (!locator) throw new Error('No locator available');
+      return updateOrgSetting({ ...input, locator });
+    },
+    onSuccess: (_, variables) => {
+      client.invalidateQueries({ queryKey: ["org-setting", variables.orgId] });
+      
+      // Invalidate related caches
+      if (locator) {
+        const { org } = Locator.parse(locator);
+        client.invalidateQueries({ queryKey: KEYS.TEAM_THEME(org) });
+      }
+    },
+  });
+}
+```
+
+## Step 3: Register Native App
+
+### 3.1 Add to Native Apps List
+
+```typescript
+// apps/web/src/components/integrations/apps.ts
+
+export const NATIVE_APPS: GroupedApp[] = [
+  // ...
+  {
+    id: "native:::feature-editor",
+    name: "Feature Editor",
+    icon: "icon://settings",
+    description: "Configure feature settings",
+    instances: 1,
+    provider: "native",
+    usedBy: [],
+    isNative: true,
+  },
+];
+
+export const NATIVE_APP_NAME_MAP: Record<string, string> = {
+  // ...
+  "native:::feature-editor": "Feature Editor",
+};
+```
+
+### 3.2 Add Default View
+
+```typescript
+// packages/sdk/src/views.ts
+
+export const DEFAULT_VIEWS: View[] = [
+  // ...
+  {
+    id: "feature-editor",
+    title: "Feature Editor",
+    icon: "settings",
+    type: "default",
+    metadata: {
+      path: "/feature-editor",
+    },
+  },
+];
+```
+
+### 3.3 Update Sidebar Navigation
+
+Add to well-known items and ordering:
+
+```typescript
+// apps/web/src/components/sidebar/index.tsx
+
+const wellKnownItems = [
+  "Tools",
+  "Views",
+  "Workflows",
+  "Documents",
+  "Agents",
+  "Feature Editor",  // Add here
+];
+
+const resourceTypeOrder = [
+  "Documents",
+  "Agents",
+  "Workflows",
+  "Tools",
+  "Views",
+  "Files",
+  "Feature Editor",  // Add here
+];
+```
+
+## Step 4: Create Frontend View
+
+### 4.1 Resource List Component
+
+```typescript
+// apps/web/src/components/feature-editor/feature-editor-resource-list.tsx
+import { useMemo } from "react";
+import { useParams } from "react-router";
+import { useTrackNativeViewVisit, useSDK, type View } from "@deco/sdk";
+import { useCurrentTeam } from "../sidebar/team-selector.tsx";
+import { FeatureEditorView } from "./feature-editor-view.tsx";
+
+export function FeatureEditorResourceList() {
+  const { locator } = useSDK();
+  const team = useCurrentTeam();
+
+  const projectKey = typeof locator === "string" ? locator : undefined;
+  const featureViewId = useMemo(() => {
+    const views = (team?.views ?? []) as View[];
+    const view = views.find((v) => v.title === "Feature Editor");
+    return view?.id;
+  }, [team?.views]);
+
+  // Track visit for recents/pinning
+  useTrackNativeViewVisit({
+    viewId: featureViewId || "feature-editor-fallback",
+    viewTitle: "Feature Editor",
+    viewIcon: "settings",
+    viewPath: `/${projectKey}/feature-editor`,
+    projectKey,
+  });
+
+  return <FeatureEditorView />;
+}
+```
+
+### 4.2 Main View Component with AI Chat Integration
+
+```typescript
+// apps/web/src/components/feature-editor/feature-editor-view.tsx
+import { useMemo } from "react";
+import { useForm } from "react-hook-form";
+import { useSetThreadContextEffect } from "../decopilot/thread-context-provider.tsx";
+
+export function FeatureEditorView() {
+  const team = useCurrentTeam();
+  const orgId = typeof team?.id === "number" ? team.id : undefined;
+  
+  // Load data
+  const { data: setting, isLoading } = useOrgSetting(orgId);
+  const updateMutation = useUpdateOrgSetting();
+
+  // AI Chat Context Integration
+  const threadContextItems = useMemo<Array<
+    { id: string; type: "rule"; text: string } | 
+    { id: string; type: "toolset"; integrationId: string; enabledTools: string[] }
+  >>(() => {
+    const rules = [
+      `You are helping configure feature settings for the organization.`,
+      `Use SETTING_UPDATE_ORG to update settings. Do NOT pass orgId - it will be auto-determined from context.`,
+      `Available settings: {list settings and their purposes}`,
+    ];
+
+    const contextItems: Array<
+      { id: string; type: "rule"; text: string } | 
+      { id: string; type: "toolset"; integrationId: string; enabledTools: string[] }
+    > = rules.map((text) => ({
+      id: crypto.randomUUID(),
+      type: "rule" as const,
+      text,
+    }));
+
+    // Add feature management toolset
+    contextItems.push({
+      id: crypto.randomUUID(),
+      type: "toolset" as const,
+      integrationId: "i:feature-management",  // Matches tool group name
+      enabledTools: ["SETTING_GET_ORG", "SETTING_UPDATE_ORG"],
+    });
+
+    // Add HTTP fetch for external data
+    contextItems.push({
+      id: crypto.randomUUID(),
+      type: "toolset" as const,
+      integrationId: "i:http",
+      enabledTools: ["HTTP_FETCH"],
+    });
+
+    return contextItems;
+  }, []);
+
+  // Inject context into AI thread
+  useSetThreadContextEffect(threadContextItems);
+
+  // Form and UI implementation...
+  return (
+    <div>
+      {/* Feature editor UI */}
+    </div>
+  );
+}
+```
+
+**Key Pattern**: Use explicit union type for `threadContextItems` to satisfy TypeScript:
+```typescript
+Array<
+  { id: string; type: "rule"; text: string } | 
+  { id: string; type: "toolset"; integrationId: string; enabledTools: string[] }
+>
+```
+
+### 4.3 Add Route
+
+```typescript
+// apps/web/src/main.tsx
+
+// In org-level routes
+{
+  path: "feature-editor",
+  element: <FeatureEditorResourceList />,
+},
+
+// Or in project-level routes
+{
+  path: ":project/feature-editor",
+  element: <FeatureEditorResourceList />,
+},
+```
+
+## Step 5: Chat Integration Patterns
+
+### 5.1 Auto-Reload on AI Updates
+
+For features that update visual state, trigger reloads when AI updates:
+
+```typescript
+// apps/web/src/components/chat/provider.tsx
+
+const chat = useChat({
+  // ...
+  onToolCall: ({ toolCall }) => {
+    // Handle feature updates
+    if (toolCall.toolName === "SETTING_UPDATE_ORG") {
+      const { org } = Locator.parse(locator);
+      
+      // Invalidate queries
+      queryClient.invalidateQueries({ 
+        queryKey: ["org-setting", org] 
+      });
+      
+      // Force refetch immediately
+      queryClient.refetchQueries({ 
+        queryKey: ["org-setting", org] 
+      });
+      
+      // Dispatch custom event for UI updates
+      window.dispatchEvent(new CustomEvent("setting-updated"));
+    }
+  },
+});
+```
+
+### 5.2 Listen for Manual Updates
+
+```typescript
+// In your view component
+useEffect(() => {
+  const handleUpdate = () => {
+    // Clear caches, trigger reloads, etc.
+  };
+
+  window.addEventListener("setting-updated", handleUpdate);
+  return () => {
+    window.removeEventListener("setting-updated", handleUpdate);
+  };
+}, []);
+```
+
+## Step 6: Organization Layout Integration
+
+### 6.1 Add Context Providers
+
+For org-level features that need AI chat:
+
+```typescript
+// apps/web/src/components/layout/org.tsx
+
+export function OrgsLayout() {
+  return (
+    <WithWorkspaceTheme>
+      <ThreadManagerProvider>
+        <ThreadContextProvider>
+          <DecopilotThreadProvider>
+            {/* Your org layout content */}
+          </DecopilotThreadProvider>
+        </ThreadContextProvider>
+      </ThreadManagerProvider>
+    </WithWorkspaceTheme>
+  );
+}
+```
+
+### 6.2 Conditional Chat Panel
+
+Show AI chat panel only for specific routes where it makes sense:
+
+```typescript
+import { useLocation } from "react-router";
+
+const location = useLocation();
+
+// Example: Only show chat on theme-editor and settings pages
+const showChatPanel = 
+  location.pathname.endsWith('/theme-editor') ||
+  location.pathname.endsWith('/settings');
+
+return (
+  <ResizablePanelGroup direction="horizontal">
+    <ResizablePanel className="bg-background">
+      <Outlet />
+    </ResizablePanel>
+    {decopilotOpen && showChatPanel && (
+      <>
+        <ResizableHandle withHandle />
+        <ResizablePanel defaultSize={30}>
+          <DecopilotChat />
+        </ResizablePanel>
+      </>
+    )}
+  </ResizablePanelGroup>
+);
+```
+
+## Common Patterns & Best Practices
+
+### Real-Time UI Updates
+
+For features that manipulate CSS or DOM:
+
+```typescript
+export function SettingsEditor() {
+  const form = useForm();
+  const debounceTimerRef = useRef<number>();
+  const previousValueRef = useRef<string>();
+
+  // Clean up debounce timer on unmount
+  useEffect(() => {
+    return () => {
+      if (debounceTimerRef.current) {
+        clearTimeout(debounceTimerRef.current);
+      }
+    };
+  }, []);
+
+  const handleChange = (key: string, newValue: string) => {
+    // Store current value before changing
+    const currentValue = form.getValues(key);
+    previousValueRef.current = currentValue;
+
+    // Apply immediately to DOM
+    document.documentElement.style.setProperty("--custom-var", newValue);
+
+    // Debounce form update
+    if (debounceTimerRef.current) {
+      clearTimeout(debounceTimerRef.current);
+    }
+    debounceTimerRef.current = window.setTimeout(() => {
+      form.setValue(key, newValue, { shouldDirty: true });
+    }, 100);
+  };
+
+  return <Input onChange={(e) => handleChange("setting", e.target.value)} />;
+}
+```
+
+### Undo Functionality
+
+**CRITICAL**: Undo should revert to the **saved state**, not the -1 change:
+
+```typescript
+export function ThemeEditor() {
+  const { data: currentData } = useTheme();
+  const form = useForm();
+  const debounceTimerRef = useRef<number>();
+  const previousValuesRef = useRef<Record<string, string>>({});
+
+  // Reset previous values when saved data changes
+  useEffect(() => {
+    form.reset({ variables: currentData?.variables ?? {} });
+    previousValuesRef.current = {};
+  }, [currentData, form]);
+
+  // Clean up debounce timer on unmount
+  useEffect(() => {
+    return () => {
+      if (debounceTimerRef.current) {
+        clearTimeout(debounceTimerRef.current);
+      }
+    };
+  }, []);
+
+  const handleChange = (key: string, value: string) => {
+    // Store the ORIGINAL saved value only once
+    // This way undo always reverts to the saved state, not the -1 change
+    if (!(key in previousValuesRef.current)) {
+      const savedValue = currentData?.variables?.[key];
+      if (savedValue) {
+        previousValuesRef.current[key] = savedValue;
+      }
+    }
+    
+    // Apply immediately to DOM
+    document.documentElement.style.setProperty(key, value);
+    
+    // Debounce form update
+    if (debounceTimerRef.current) {
+      clearTimeout(debounceTimerRef.current);
+    }
+    debounceTimerRef.current = window.setTimeout(() => {
+      form.setValue(key, value, { shouldDirty: true });
+    }, 100);
+  };
+
+  const handleUndo = (key: string) => {
+    const savedValue = previousValuesRef.current[key];
+    if (savedValue) {
+      // Revert to the saved value from database
+      document.documentElement.style.setProperty(key, savedValue);
+      form.setValue(key, savedValue);
+      delete previousValuesRef.current[key];
+    }
+  };
+
+  return (
+    <ColorPicker
+      value={form.watch(key)}
+      onChange={(val) => handleChange(key, val)}
+      onUndo={() => handleUndo(key)}
+    />
+  );
+}
+
+// ❌ BAD: This only undoes the last change, not all changes since last save
+export function BadUndo() {
+  const previousValuesRef = useRef<Record<string, string>>({});
+  
+  const handleChangeBad = (key: string, value: string) => {
+    previousValuesRef.current[key] = form.getValues(key); // Overwrites on every change!
+    form.setValue(key, value);
+  };
+}
+```
+
+### Permission Checks
+
+Always use team/org slugs for authorization:
+
+```typescript
+// ❌ BAD - Using numeric ID
+await assertTeamResourceAccess("TEAMS_UPDATE", orgId, c);
+
+// ✅ GOOD - Using slug
+const orgSlug = c.locator?.org;
+await assertTeamResourceAccess("TEAMS_UPDATE", orgSlug, c);
+```
+
+### Tool Discovery in UI
+
+The `IntegrationToolsetDisplay` component automatically discovers and displays tools:
+
+```typescript
+// In context-resources.tsx
+const { data: toolsData } = useTools(integration.connection);
+const tools = toolsData?.tools || [];
+
+// Tools are automatically fetched and displayed
+{tools.map((tool) => (
+  <ToolItem key={tool.name} tool={tool} />
+))}
+```
+
+## Checklist for New Native Apps
+
+- [ ] Create MCP tool group with descriptive name
+- [ ] Implement tools with object return types
+- [ ] Handle org context with auto-resolution
+- [ ] Use slug-based authorization
+- [ ] Add to NATIVE_APPS and DEFAULT_VIEWS
+- [ ] Update sidebar wellKnownItems and resourceTypeOrder
+- [ ] Create resource list component with visit tracking
+- [ ] Create main view component with AI context
+- [ ] Add route to main.tsx
+- [ ] Implement chat reload on AI updates
+- [ ] Add environment variables if needed
+- [ ] Test tool discovery in chat UI
+- [ ] Verify permissions with different roles
+- [ ] Test real-time updates
+- [ ] Add undo functionality if appropriate
+
+## Example: Theme Editor
+
+See the complete theme editor implementation for reference:
+- MCP Tools: `packages/sdk/src/mcp/theme/api.ts`
+- CRUD: `packages/sdk/src/crud/theme.ts`
+- Hooks: `packages/sdk/src/hooks/theme.ts`
+- View: `apps/web/src/components/theme-editor/`
+- Integration: Search for "Theme" across the codebase
+
+This follows all patterns and demonstrates real-world usage of native apps with full AI chat integration.
diff --git a/.cursor/rules/react-ts.mdc b/.cursor/rules/react-ts.mdc
@@ -364,6 +364,270 @@ export function AgentList() {
 }
 ```
 
+### Real-Time State Management
+
+**Immediate DOM Updates with Debounced State:**
+
+For features that manipulate CSS or DOM directly (like theme editors, live previews):
+
+```tsx
+// ✅ Good - Immediate visual feedback with debounced persistence
+export function ThemeEditor() {
+  const form = useForm();
+  const debounceTimerRef = useRef<number>();
+  const previousValuesRef = useRef<Record<string, string>>({});
+
+  // Clean up debounce timer on unmount
+  useEffect(() => {
+    return () => {
+      if (debounceTimerRef.current) {
+        clearTimeout(debounceTimerRef.current);
+      }
+    };
+  }, []);
+
+  const handleChange = (key: string, value: string) => {
+    // 1. Store previous value for undo functionality
+    const current = form.getValues(key);
+    if (current) {
+      previousValuesRef.current[key] = current;
+    }
+
+    // 2. Apply immediately to DOM for instant visual feedback
+    document.documentElement.style.setProperty(key, value);
+
+    // 3. Debounce form state update to reduce re-renders
+    if (debounceTimerRef.current) {
+      clearTimeout(debounceTimerRef.current);
+    }
+    
+    debounceTimerRef.current = window.setTimeout(() => {
+      form.setValue(key, value, { shouldDirty: true });
+    }, 100);
+  };
+
+  const handleUndo = (key: string) => {
+    const previousValue = previousValuesRef.current[key];
+    if (previousValue) {
+      document.documentElement.style.setProperty(key, previousValue);
+      form.setValue(key, previousValue);
+      delete previousValuesRef.current[key];
+    }
+  };
+
+  return (
+    <div>
+      <Input onChange={(e) => handleChange("--primary", e.target.value)} />
+      <Button onClick={() => handleUndo("--primary")}>Undo</Button>
+    </div>
+  );
+}
+
+// ❌ Bad - Every keystroke triggers full re-render
+export function BadThemeEditor() {
+  const [value, setValue] = useState("");
+  
+  return (
+    <Input 
+      value={value}
+      onChange={(e) => {
+        setValue(e.target.value);  // Triggers re-render
+        document.documentElement.style.setProperty("--primary", e.target.value);
+      }}
+    />
+  );
+}
+```
+
+**Cross-Component Communication:**
+
+Use custom events for coordinating updates across unrelated components:
+
+```tsx
+// Component A - Dispatch after mutation
+export function SettingsForm() {
+  const updateMutation = useUpdateSettings();
+
+  const handleSave = async () => {
+    await updateMutation.mutateAsync(data);
+    
+    // Notify other components of the update
+    window.dispatchEvent(new CustomEvent("settings-updated"));
+  };
+
+  return <button onClick={handleSave}>Save</button>;
+}
+
+// Component B - Listen and react
+export function SettingsPreview() {
+  const queryClient = useQueryClient();
+
+  useEffect(() => {
+    const handleUpdate = () => {
+      // Invalidate and refetch
+      queryClient.invalidateQueries({ queryKey: ["settings"] });
+      
+      // Or force immediate refetch
+      queryClient.refetchQueries({ queryKey: ["settings"] });
+    };
+    
+    window.addEventListener("settings-updated", handleUpdate);
+    return () => {
+      window.removeEventListener("settings-updated", handleUpdate);
+    };
+  }, [queryClient]);
+
+  return <div>Preview updates automatically</div>;
+}
+```
+
+**Undo/Redo Pattern:**
+
+Implement single-level undo that reverts to the **saved state**, not the -1 change:
+
+```tsx
+export function ThemeEditor() {
+  const { data: currentTheme } = useTheme();
+  const form = useForm();
+  const debounceTimerRef = useRef<number>();
+  const previousValuesRef = useRef<Record<string, string>>({});
+
+  // Reset previous values when saved theme changes
+  useEffect(() => {
+    form.reset({ themeVariables: currentTheme?.variables ?? {} });
+    previousValuesRef.current = {};
+  }, [currentTheme, form]);
+
+  // Clean up debounce timer on unmount
+  useEffect(() => {
+    return () => {
+      if (debounceTimerRef.current) {
+        clearTimeout(debounceTimerRef.current);
+      }
+    };
+  }, []);
+
+  const handleChange = (key: string, newValue: string) => {
+    // Store the ORIGINAL saved value only once
+    // This way undo always reverts to the saved state, not the -1 change
+    if (!(key in previousValuesRef.current)) {
+      const savedValue = currentTheme?.variables?.[key];
+      if (savedValue) {
+        previousValuesRef.current[key] = savedValue;
+      }
+    }
+
+    // Apply immediately to DOM
+    document.documentElement.style.setProperty(key, newValue);
+    
+    // Debounce form update
+    if (debounceTimerRef.current) {
+      clearTimeout(debounceTimerRef.current);
+    }
+    debounceTimerRef.current = window.setTimeout(() => {
+      form.setValue(key, newValue, { shouldDirty: true });
+    }, 100);
+  };
+
+  const handleUndo = (key: string) => {
+    const savedValue = previousValuesRef.current[key];
+    if (savedValue) {
+      // Revert to the saved theme value
+      document.documentElement.style.setProperty(key, savedValue);
+      form.setValue(key, savedValue);
+      delete previousValuesRef.current[key];
+    }
+  };
+
+  return (
+    <div>
+      <ColorPicker
+        value={form.watch(key)}
+        onChange={(val) => handleChange(key, val)}
+        onUndo={() => handleUndo(key)}
+        hasPreviousValue={!!(key in previousValuesRef.current)}
+      />
+    </div>
+  );
+}
+
+// ❌ Bad - Undo only goes back one step, not to saved state
+export function BadUndo({ value, onChange }: Props) {
+  const previousValueRef = useRef<string>();
+
+  const handleChange = (newValue: string) => {
+    previousValueRef.current = value; // Overwrites on every change!
+    onChange(newValue);
+  };
+
+  // This only undoes the last change, not all changes since last save
+}
+```
+
+### AI Chat Context Integration
+
+**Injecting Context into AI Threads:**
+
+Use `useSetThreadContextEffect` to provide rules and tools to AI chat:
+
+```tsx
+import { useSetThreadContextEffect } from "../decopilot/thread-context-provider.tsx";
+
+export function FeatureEditor() {
+  // ✅ Good - Explicit union type for TypeScript
+  const threadContextItems = useMemo<Array<
+    { id: string; type: "rule"; text: string } | 
+    { id: string; type: "toolset"; integrationId: string; enabledTools: string[] }
+  >>(() => {
+    const rules = [
+      `You are helping configure feature settings.`,
+      `Use FEATURE_UPDATE to modify settings.`,
+      `Do NOT pass orgId - it will be auto-determined from context.`,
+    ];
+
+    const contextItems: Array<
+      { id: string; type: "rule"; text: string } | 
+      { id: string; type: "toolset"; integrationId: string; enabledTools: string[] }
+    > = rules.map((text) => ({
+      id: crypto.randomUUID(),
+      type: "rule" as const,
+      text,
+    }));
+
+    // Add feature management toolset
+    contextItems.push({
+      id: crypto.randomUUID(),
+      type: "toolset" as const,
+      integrationId: "i:feature-management",  // Virtual integration ID
+      enabledTools: ["FEATURE_GET", "FEATURE_UPDATE"],
+    });
+
+    // Add HTTP fetch for external data
+    contextItems.push({
+      id: crypto.randomUUID(),
+      type: "toolset" as const,
+      integrationId: "i:http",
+      enabledTools: ["HTTP_FETCH"],
+    });
+
+    return contextItems;
+  }, []);
+
+  // Inject into current thread
+  useSetThreadContextEffect(threadContextItems);
+
+  return <div>Feature editor UI</div>;
+}
+
+// ❌ Bad - TypeScript can't infer the union type correctly
+const items = useMemo(() => {
+  const rules = [/* ... */].map(text => ({ type: "rule", text }));
+  rules.push({ type: "toolset", integrationId: "i:...", enabledTools: [] });
+  // Type error: string[] not assignable to expected type
+  return rules;
+}, []);
+```
+
 **Extract Logic into Components Instead of Inline Functions:**
 ```tsx
 // ❌ Bad - Using immediately invoked function expressions (IIFEs) in JSX
PATCH

echo "Gold patch applied."
