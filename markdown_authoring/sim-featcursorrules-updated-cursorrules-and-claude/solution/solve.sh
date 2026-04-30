#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sim

# Idempotency guard
if grep -qF "return <Primitive className={cn('style-classes', className)} {...props} />" ".cursor/rules/emcn-components.mdc" && grep -qF "Import `createLogger` from `sim/logger`. Use `logger.info`, `logger.warn`, `logg" ".cursor/rules/global.mdc" && grep -qF "- **Location**: `lib/` (app-wide) \u2192 `feature/utils/` (feature-scoped) \u2192 inline (" ".cursor/rules/sim-architecture.mdc" && grep -qF "**Extract when:** 50+ lines, used in 2+ files, or has own state/logic" ".cursor/rules/sim-components.mdc" && grep -qF "// 4. Operations (useCallback with empty deps when using refs)" ".cursor/rules/sim-hooks.mdc" && grep -qF "Use barrel exports (`index.ts`) when a folder has 3+ exports. Import from barrel" ".cursor/rules/sim-imports.mdc" && grep -qF "**SubBlock Types:** `short-input`, `long-input`, `dropdown`, `code`, `switch`, `" ".cursor/rules/sim-integrations.mdc" && grep -qF "For optimistic mutations syncing with Zustand, use `createOptimisticMutationHand" ".cursor/rules/sim-queries.mdc" && grep -qF "const initialState = { items: [] as Item[], activeId: null as string | null }" ".cursor/rules/sim-stores.mdc" && grep -qF "2. **No duplicate dark classes** - Skip `dark:` when value matches light mode" ".cursor/rules/sim-styling.mdc" && grep -qF "Use Vitest. Test files live next to source: `feature.ts` \u2192 `feature.test.ts`" ".cursor/rules/sim-testing.mdc" && grep -qF "3. **Const assertions** - `as const` for constant objects/arrays" ".cursor/rules/sim-typescript.mdc" && grep -qF "Extract when: 50+ lines, used in 2+ files, or has own state/logic. Keep inline w" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/emcn-components.mdc b/.cursor/rules/emcn-components.mdc
@@ -1,45 +1,35 @@
 ---
-description: EMCN component library patterns with CVA
+description: EMCN component library patterns
 globs: ["apps/sim/components/emcn/**"]
 ---
 
-# EMCN Component Guidelines
+# EMCN Components
 
-## When to Use CVA vs Direct Styles
+Import from `@/components/emcn`, never from subpaths (except CSS files).
 
-**Use CVA (class-variance-authority) when:**
-- 2+ visual variants (primary, secondary, outline)
-- Multiple sizes or state variations
-- Example: Button with variants
+## CVA vs Direct Styles
 
-**Use direct className when:**
-- Single consistent style
-- No variations needed
-- Example: Label with one style
+**Use CVA when:** 2+ variants (primary/secondary, sm/md/lg)
 
-## Patterns
-
-**With CVA:**
 ```tsx
 const buttonVariants = cva('base-classes', {
-  variants: { 
-    variant: { default: '...', primary: '...' },
-    size: { sm: '...', md: '...' }
-  }
+  variants: { variant: { default: '...', primary: '...' } }
 })
 export { Button, buttonVariants }
 ```
 
-**Without CVA:**
+**Use direct className when:** Single consistent style, no variations
+
 ```tsx
 function Label({ className, ...props }) {
-  return <Primitive className={cn('single-style-classes', className)} {...props} />
+  return <Primitive className={cn('style-classes', className)} {...props} />
 }
 ```
 
 ## Rules
+
 - Use Radix UI primitives for accessibility
 - Export component and variants (if using CVA)
 - TSDoc with usage examples
 - Consistent tokens: `font-medium`, `text-[12px]`, `rounded-[4px]`
-- Always use `transition-colors` for hover states
+- `transition-colors` for hover states
diff --git a/.cursor/rules/global.mdc b/.cursor/rules/global.mdc
@@ -8,7 +8,7 @@ alwaysApply: true
 You are a professional software engineer. All code must follow best practices: accurate, readable, clean, and efficient.
 
 ## Logging
-Use `logger.info`, `logger.warn`, `logger.error` instead of `console.log`.
+Import `createLogger` from `sim/logger`. Use `logger.info`, `logger.warn`, `logger.error` instead of `console.log`.
 
 ## Comments
 Use TSDoc for documentation. No `====` separators. No non-TSDoc comments.
diff --git a/.cursor/rules/sim-architecture.mdc b/.cursor/rules/sim-architecture.mdc
@@ -10,58 +10,47 @@ globs: ["apps/sim/**"]
 2. **Composition Over Complexity**: Break down complex logic into smaller pieces
 3. **Type Safety First**: TypeScript interfaces for all props, state, return types
 4. **Predictable State**: Zustand for global state, useState for UI-only concerns
-5. **Performance by Default**: useMemo, useCallback, refs appropriately
 
-## File Organization
+## Root-Level Structure
+
+```
+apps/sim/
+├── app/                 # Next.js app router (pages, API routes)
+├── blocks/              # Block definitions and registry
+├── components/          # Shared UI (emcn/, ui/)
+├── executor/            # Workflow execution engine
+├── hooks/               # Shared hooks (queries/, selectors/)
+├── lib/                 # App-wide utilities
+├── providers/           # LLM provider integrations
+├── stores/              # Zustand stores
+├── tools/               # Tool definitions
+└── triggers/            # Trigger definitions
+```
+
+## Feature Organization
+
+Features live under `app/workspace/[workspaceId]/`:
 
 ```
 feature/
-├── components/        # Feature components
-│   └── sub-feature/   # Sub-feature with own components
-├── hooks/             # Custom hooks
-└── feature.tsx        # Main component
+├── components/          # Feature components
+├── hooks/               # Feature-scoped hooks
+├── utils/               # Feature-scoped utilities (2+ consumers)
+├── feature.tsx          # Main component
+└── page.tsx             # Next.js page entry
 ```
 
 ## Naming Conventions
-- **Components**: PascalCase (`WorkflowList`, `TriggerPanel`)
-- **Hooks**: camelCase with `use` prefix (`useWorkflowOperations`)
-- **Files**: kebab-case matching export (`workflow-list.tsx`)
-- **Stores**: kebab-case in stores/ (`sidebar/store.ts`)
+- **Components**: PascalCase (`WorkflowList`)
+- **Hooks**: `use` prefix (`useWorkflowOperations`)
+- **Files**: kebab-case (`workflow-list.tsx`)
+- **Stores**: `stores/feature/store.ts`
 - **Constants**: SCREAMING_SNAKE_CASE
 - **Interfaces**: PascalCase with suffix (`WorkflowListProps`)
 
-## State Management
-
-**useState**: UI-only concerns (dropdown open, hover, form inputs)
-**Zustand**: Shared state, persistence, global app state
-**useRef**: DOM refs, avoiding dependency issues, mutable non-reactive values
-
-## Component Extraction
-
-**Extract to separate file when:**
-- Complex (50+ lines)
-- Used across 2+ files
-- Has own state/logic
-
-**Keep inline when:**
-- Simple (< 10 lines)
-- Used in only 1 file
-- Purely presentational
-
-**Never import utilities from another component file.** Extract shared helpers to `lib/` or `utils/`.
-
-## Utils Files
-
-**Never create a `utils.ts` file for a single consumer.** Inline the logic directly in the consuming component.
-
-**Create `utils.ts` when:**
-- 2+ files import the same helper
-
-**Prefer existing sources of truth:**
-- Before duplicating logic, check if a centralized helper already exists (e.g., `lib/logs/get-trigger-options.ts`)
-- Import from the source of truth rather than creating wrapper functions
+## Utils Rules
 
-**Location hierarchy:**
-- `lib/` — App-wide utilities (auth, billing, core)
-- `feature/utils.ts` — Feature-scoped utilities (used by 2+ components in the feature)
-- Inline — Single-use helpers (define directly in the component)
+- **Never create `utils.ts` for single consumer** - inline it
+- **Create `utils.ts` when** 2+ files need the same helper
+- **Check existing sources** before duplicating (`lib/` has many utilities)
+- **Location**: `lib/` (app-wide) → `feature/utils/` (feature-scoped) → inline (single-use)
diff --git a/.cursor/rules/sim-components.mdc b/.cursor/rules/sim-components.mdc
@@ -6,59 +6,43 @@ globs: ["apps/sim/**/*.tsx"]
 # Component Patterns
 
 ## Structure Order
+
 ```typescript
 'use client' // Only if using hooks
 
-// 1. Imports (external → internal → relative)
-// 2. Constants at module level
+// Imports (external → internal)
+// Constants at module level
 const CONFIG = { SPACING: 8 } as const
 
-// 3. Props interface with TSDoc
+// Props interface
 interface ComponentProps {
-  /** Description */
   requiredProp: string
   optionalProp?: boolean
 }
 
-// 4. Component with TSDoc
 export function Component({ requiredProp, optionalProp = false }: ComponentProps) {
   // a. Refs
   // b. External hooks (useParams, useRouter)
   // c. Store hooks
   // d. Custom hooks
   // e. Local state
-  // f. useMemo computations
-  // g. useCallback handlers
+  // f. useMemo
+  // g. useCallback
   // h. useEffect
   // i. Return JSX
 }
 ```
 
 ## Rules
-1. Add `'use client'` when using React hooks
-2. Always define props interface
-3. TSDoc on component: description, @param, @returns
-4. Extract constants with `as const`
-5. Use Tailwind only, no inline styles
-6. Semantic HTML (`aside`, `nav`, `article`)
-7. Include ARIA attributes where appropriate
-8. Optional chain callbacks: `onAction?.(id)`
 
-## Factory Pattern with Caching
+1. `'use client'` only when using React hooks
+2. Always define props interface
+3. Extract constants with `as const`
+4. Semantic HTML (`aside`, `nav`, `article`)
+5. Optional chain callbacks: `onAction?.(id)`
 
-When generating components for a specific signature (e.g., icons):
+## Component Extraction
 
-```typescript
-const cache = new Map<string, React.ComponentType<{ className?: string }>>()
+**Extract when:** 50+ lines, used in 2+ files, or has own state/logic
 
-function getColorIcon(color: string) {
-  if (cache.has(color)) return cache.get(color)!
-  
-  const Icon = ({ className }: { className?: string }) => (
-    <div className={cn(className, 'rounded-[3px]')} style={{ backgroundColor: color, width: 10, height: 10 }} />
-  )
-  Icon.displayName = `ColorIcon(${color})`
-  cache.set(color, Icon)
-  return Icon
-}
-```
+**Keep inline when:** < 10 lines, single use, purely presentational
diff --git a/.cursor/rules/sim-hooks.mdc b/.cursor/rules/sim-hooks.mdc
@@ -6,21 +6,13 @@ globs: ["apps/sim/**/use-*.ts", "apps/sim/**/hooks/**/*.ts"]
 # Hook Patterns
 
 ## Structure
-```typescript
-import { createLogger } from '@/lib/logs/console/logger'
-
-const logger = createLogger('useFeatureName')
 
+```typescript
 interface UseFeatureProps {
   id: string
   onSuccess?: (result: Result) => void
 }
 
-/**
- * Hook description.
- * @param props - Configuration
- * @returns State and operations
- */
 export function useFeature({ id, onSuccess }: UseFeatureProps) {
   // 1. Refs for stable dependencies
   const idRef = useRef(id)
@@ -29,40 +21,34 @@ export function useFeature({ id, onSuccess }: UseFeatureProps) {
   // 2. State
   const [data, setData] = useState<Data | null>(null)
   const [isLoading, setIsLoading] = useState(false)
-  const [error, setError] = useState<Error | null>(null)
 
   // 3. Sync refs
   useEffect(() => {
     idRef.current = id
     onSuccessRef.current = onSuccess
   }, [id, onSuccess])
 
-  // 4. Operations with useCallback
+  // 4. Operations (useCallback with empty deps when using refs)
   const fetchData = useCallback(async () => {
     setIsLoading(true)
     try {
       const result = await fetch(`/api/${idRef.current}`).then(r => r.json())
       setData(result)
       onSuccessRef.current?.(result)
-    } catch (err) {
-      setError(err as Error)
-      logger.error('Failed', { error: err })
     } finally {
       setIsLoading(false)
     }
-  }, []) // Empty deps - using refs
+  }, [])
 
-  // 5. Return grouped by state/operations
-  return { data, isLoading, error, fetchData }
+  return { data, isLoading, fetchData }
 }
 ```
 
 ## Rules
+
 1. Single responsibility per hook
 2. Props interface required
-3. TSDoc required
-4. Use logger, not console.log
-5. Refs for stable callback dependencies
-6. Wrap returned functions in useCallback
-7. Always try/catch async operations
-8. Track loading/error states
+3. Refs for stable callback dependencies
+4. Wrap returned functions in useCallback
+5. Always try/catch async operations
+6. Track loading/error states
diff --git a/.cursor/rules/sim-imports.mdc b/.cursor/rules/sim-imports.mdc
@@ -5,33 +5,45 @@ globs: ["apps/sim/**/*.ts", "apps/sim/**/*.tsx"]
 
 # Import Patterns
 
-## EMCN Components
-Import from `@/components/emcn`, never from subpaths like `@/components/emcn/components/modal/modal`.
+## Absolute Imports
 
-**Exception**: CSS imports use actual file paths: `import '@/components/emcn/components/code/code.css'`
+**Always use absolute imports.** Never use relative imports.
 
-## Feature Components
-Import from central folder indexes, not specific subfolders:
 ```typescript
-// ✅ Correct
-import { Dashboard, Sidebar } from '@/app/workspace/[workspaceId]/logs/components'
+// ✓ Good
+import { useWorkflowStore } from '@/stores/workflows/store'
+import { Button } from '@/components/ui/button'
 
-// ❌ Wrong
-import { Dashboard } from '@/app/workspace/[workspaceId]/logs/components/dashboard'
+// ✗ Bad
+import { useWorkflowStore } from '../../../stores/workflows/store'
 ```
 
-## Internal vs External
-- **Cross-feature**: Absolute paths through central index
-- **Within feature**: Relative paths (`./components/...`, `../utils`)
+## Barrel Exports
+
+Use barrel exports (`index.ts`) when a folder has 3+ exports. Import from barrel, not individual files.
+
+```typescript
+// ✓ Good
+import { Dashboard, Sidebar } from '@/app/workspace/[workspaceId]/logs/components'
+
+// ✗ Bad
+import { Dashboard } from '@/app/workspace/[workspaceId]/logs/components/dashboard/dashboard'
+```
 
 ## Import Order
+
 1. React/core libraries
 2. External libraries
 3. UI components (`@/components/emcn`, `@/components/ui`)
 4. Utilities (`@/lib/...`)
-5. Feature imports from indexes
-6. Relative imports
+5. Stores (`@/stores/...`)
+6. Feature imports
 7. CSS imports
 
-## Types
-Use `type` keyword: `import type { WorkflowLog } from '...'`
+## Type Imports
+
+Use `type` keyword for type-only imports:
+
+```typescript
+import type { WorkflowLog } from '@/stores/logs/types'
+```
diff --git a/.cursor/rules/sim-integrations.mdc b/.cursor/rules/sim-integrations.mdc
@@ -0,0 +1,207 @@
+---
+description: Adding new integrations (tools, blocks, triggers)
+globs: ["apps/sim/tools/**", "apps/sim/blocks/**", "apps/sim/triggers/**"]
+---
+
+# Adding Integrations
+
+## Overview
+
+Adding a new integration typically requires:
+1. **Tools** - API operations (`tools/{service}/`)
+2. **Block** - UI component (`blocks/blocks/{service}.ts`)
+3. **Icon** - SVG icon (`components/icons.tsx`)
+4. **Trigger** (optional) - Webhooks/polling (`triggers/{service}/`)
+
+Always look up the service's API docs first.
+
+## 1. Tools (`tools/{service}/`)
+
+```
+tools/{service}/
+├── index.ts           # Export all tools
+├── types.ts           # Params/response types
+├── {action}.ts        # Individual tool (e.g., send_message.ts)
+└── ...
+```
+
+**Tool file structure:**
+
+```typescript
+// tools/{service}/{action}.ts
+import type { {Service}Params, {Service}Response } from '@/tools/{service}/types'
+import type { ToolConfig } from '@/tools/types'
+
+export const {service}{Action}Tool: ToolConfig<{Service}Params, {Service}Response> = {
+  id: '{service}_{action}',
+  name: '{Service} {Action}',
+  description: 'What this tool does',
+  version: '1.0.0',
+  oauth: { required: true, provider: '{service}' }, // if OAuth
+  params: { /* param definitions */ },
+  request: {
+    url: '/api/tools/{service}/{action}',
+    method: 'POST',
+    headers: () => ({ 'Content-Type': 'application/json' }),
+    body: (params) => ({ ...params }),
+  },
+  transformResponse: async (response) => {
+    const data = await response.json()
+    if (!data.success) throw new Error(data.error)
+    return { success: true, output: data.output }
+  },
+  outputs: { /* output definitions */ },
+}
+```
+
+**Register in `tools/registry.ts`:**
+
+```typescript
+import { {service}{Action}Tool } from '@/tools/{service}'
+// Add to registry object
+{service}_{action}: {service}{Action}Tool,
+```
+
+## 2. Block (`blocks/blocks/{service}.ts`)
+
+```typescript
+import { {Service}Icon } from '@/components/icons'
+import type { BlockConfig } from '@/blocks/types'
+import type { {Service}Response } from '@/tools/{service}/types'
+
+export const {Service}Block: BlockConfig<{Service}Response> = {
+  type: '{service}',
+  name: '{Service}',
+  description: 'Short description',
+  longDescription: 'Detailed description',
+  category: 'tools',
+  bgColor: '#hexcolor',
+  icon: {Service}Icon,
+  subBlocks: [ /* see SubBlock Properties below */ ],
+  tools: {
+    access: ['{service}_{action}', ...],
+    config: {
+      tool: (params) => `{service}_${params.operation}`,
+      params: (params) => ({ ...params }),
+    },
+  },
+  inputs: { /* input definitions */ },
+  outputs: { /* output definitions */ },
+}
+```
+
+### SubBlock Properties
+
+```typescript
+{
+  id: 'fieldName',           // Unique identifier
+  title: 'Field Label',      // UI label
+  type: 'short-input',       // See SubBlock Types below
+  placeholder: 'Hint text',
+  required: true,            // See Required below
+  condition: { ... },        // See Condition below
+  dependsOn: ['otherField'], // See DependsOn below
+  mode: 'basic',             // 'basic' | 'advanced' | 'both' | 'trigger'
+}
+```
+
+**SubBlock Types:** `short-input`, `long-input`, `dropdown`, `code`, `switch`, `slider`, `oauth-input`, `channel-selector`, `user-selector`, `file-upload`, etc.
+
+### `condition` - Show/hide based on another field
+
+```typescript
+// Show when operation === 'send'
+condition: { field: 'operation', value: 'send' }
+
+// Show when operation is 'send' OR 'read'
+condition: { field: 'operation', value: ['send', 'read'] }
+
+// Show when operation !== 'send'
+condition: { field: 'operation', value: 'send', not: true }
+
+// Complex: NOT in list AND another condition
+condition: {
+  field: 'operation',
+  value: ['list_channels', 'list_users'],
+  not: true,
+  and: { field: 'destinationType', value: 'dm', not: true }
+}
+```
+
+### `required` - Field validation
+
+```typescript
+// Always required
+required: true
+
+// Conditionally required (same syntax as condition)
+required: { field: 'operation', value: 'send' }
+```
+
+### `dependsOn` - Clear field when dependencies change
+
+```typescript
+// Clear when credential changes
+dependsOn: ['credential']
+
+// Clear when authMethod changes AND (credential OR botToken) changes
+dependsOn: { all: ['authMethod'], any: ['credential', 'botToken'] }
+```
+
+### `mode` - When to show field
+
+- `'basic'` - Only in basic mode (default UI)
+- `'advanced'` - Only in advanced mode (manual input)
+- `'both'` - Show in both modes (default)
+- `'trigger'` - Only when block is used as trigger
+
+**Register in `blocks/registry.ts`:**
+
+```typescript
+import { {Service}Block } from '@/blocks/blocks/{service}'
+// Add to registry object (alphabetically)
+{service}: {Service}Block,
+```
+
+## 3. Icon (`components/icons.tsx`)
+
+```typescript
+export function {Service}Icon(props: SVGProps<SVGSVGElement>) {
+  return (
+    <svg {...props} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
+      {/* SVG path from service's brand assets */}
+    </svg>
+  )
+}
+```
+
+## 4. Trigger (`triggers/{service}/`) - Optional
+
+```
+triggers/{service}/
+├── index.ts           # Export all triggers
+├── webhook.ts         # Webhook handler
+├── utils.ts           # Shared utilities
+└── {event}.ts         # Specific event handlers
+```
+
+**Register in `triggers/registry.ts`:**
+
+```typescript
+import { {service}WebhookTrigger } from '@/triggers/{service}'
+// Add to TRIGGER_REGISTRY
+{service}_webhook: {service}WebhookTrigger,
+```
+
+## Checklist
+
+- [ ] Look up API docs for the service
+- [ ] Create `tools/{service}/types.ts` with proper types
+- [ ] Create tool files for each operation
+- [ ] Create `tools/{service}/index.ts` barrel export
+- [ ] Register tools in `tools/registry.ts`
+- [ ] Add icon to `components/icons.tsx`
+- [ ] Create block in `blocks/blocks/{service}.ts`
+- [ ] Register block in `blocks/registry.ts`
+- [ ] (Optional) Create triggers in `triggers/{service}/`
+- [ ] (Optional) Register triggers in `triggers/registry.ts`
diff --git a/.cursor/rules/sim-queries.mdc b/.cursor/rules/sim-queries.mdc
@@ -0,0 +1,66 @@
+---
+description: React Query patterns for the Sim application
+globs: ["apps/sim/hooks/queries/**/*.ts"]
+---
+
+# React Query Patterns
+
+All React Query hooks live in `hooks/queries/`.
+
+## Query Key Factory
+
+Every query file defines a keys factory:
+
+```typescript
+export const entityKeys = {
+  all: ['entity'] as const,
+  list: (workspaceId?: string) => [...entityKeys.all, 'list', workspaceId ?? ''] as const,
+  detail: (id?: string) => [...entityKeys.all, 'detail', id ?? ''] as const,
+}
+```
+
+## File Structure
+
+```typescript
+// 1. Query keys factory
+// 2. Types (if needed)
+// 3. Private fetch functions
+// 4. Exported hooks
+```
+
+## Query Hook
+
+```typescript
+export function useEntityList(workspaceId?: string, options?: { enabled?: boolean }) {
+  return useQuery({
+    queryKey: entityKeys.list(workspaceId),
+    queryFn: () => fetchEntities(workspaceId as string),
+    enabled: Boolean(workspaceId) && (options?.enabled ?? true),
+    staleTime: 60 * 1000,
+    placeholderData: keepPreviousData,
+  })
+}
+```
+
+## Mutation Hook
+
+```typescript
+export function useCreateEntity() {
+  const queryClient = useQueryClient()
+  return useMutation({
+    mutationFn: async (variables) => { /* fetch POST */ },
+    onSuccess: () => queryClient.invalidateQueries({ queryKey: entityKeys.all }),
+  })
+}
+```
+
+## Optimistic Updates
+
+For optimistic mutations syncing with Zustand, use `createOptimisticMutationHandlers` from `@/hooks/queries/utils/optimistic-mutation`.
+
+## Naming
+
+- **Keys**: `entityKeys`
+- **Query hooks**: `useEntity`, `useEntityList`
+- **Mutation hooks**: `useCreateEntity`, `useUpdateEntity`
+- **Fetch functions**: `fetchEntity` (private)
diff --git a/.cursor/rules/sim-stores.mdc b/.cursor/rules/sim-stores.mdc
@@ -5,53 +5,66 @@ globs: ["apps/sim/**/store.ts", "apps/sim/**/stores/**/*.ts"]
 
 # Zustand Store Patterns
 
-## Structure
+Stores live in `stores/`. Complex stores split into `store.ts` + `types.ts`.
+
+## Basic Store
+
 ```typescript
 import { create } from 'zustand'
-import { persist } from 'zustand/middleware'
+import { devtools } from 'zustand/middleware'
+import type { FeatureState } from '@/stores/feature/types'
 
-interface FeatureState {
-  // State
-  items: Item[]
-  activeId: string | null
-  
-  // Actions
-  setItems: (items: Item[]) => void
-  addItem: (item: Item) => void
-  clearState: () => void
-}
-
-const createInitialState = () => ({
-  items: [],
-  activeId: null,
-})
+const initialState = { items: [] as Item[], activeId: null as string | null }
 
 export const useFeatureStore = create<FeatureState>()(
-  persist(
-    (set) => ({
-      ...createInitialState(),
-
+  devtools(
+    (set, get) => ({
+      ...initialState,
       setItems: (items) => set({ items }),
+      addItem: (item) => set((state) => ({ items: [...state.items, item] })),
+      reset: () => set(initialState),
+    }),
+    { name: 'feature-store' }
+  )
+)
+```
+
+## Persisted Store
 
-      addItem: (item) => set((state) => ({
-        items: [...state.items, item],
-      })),
+```typescript
+import { create } from 'zustand'
+import { persist } from 'zustand/middleware'
 
-      clearState: () => set(createInitialState()),
+export const useFeatureStore = create<FeatureState>()(
+  persist(
+    (set) => ({
+      width: 300,
+      setWidth: (width) => set({ width }),
+      _hasHydrated: false,
+      setHasHydrated: (v) => set({ _hasHydrated: v }),
     }),
     {
       name: 'feature-state',
-      partialize: (state) => ({ items: state.items }),
+      partialize: (state) => ({ width: state.width }),
+      onRehydrateStorage: () => (state) => state?.setHasHydrated(true),
     }
   )
 )
 ```
 
 ## Rules
-1. Interface includes state and actions
-2. Extract config to module constants
-3. TSDoc on store
-4. Only persist what's needed
-5. Immutable updates only - never mutate
-6. Use `set((state) => ...)` when depending on previous state
-7. Provide clear/reset actions
+
+1. Use `devtools` middleware (named stores)
+2. Use `persist` only when data should survive reload
+3. `partialize` to persist only necessary state
+4. `_hasHydrated` pattern for persisted stores needing hydration tracking
+5. Immutable updates only
+6. `set((state) => ...)` when depending on previous state
+7. Provide `reset()` action
+
+## Outside React
+
+```typescript
+const items = useFeatureStore.getState().items
+useFeatureStore.setState({ items: newItems })
+```
diff --git a/.cursor/rules/sim-styling.mdc b/.cursor/rules/sim-styling.mdc
@@ -6,13 +6,14 @@ globs: ["apps/sim/**/*.tsx", "apps/sim/**/*.css"]
 # Styling Rules
 
 ## Tailwind
-1. **No inline styles** - Use Tailwind classes exclusively
-2. **No duplicate dark classes** - Don't add `dark:` when value matches light mode
-3. **Exact values** - Use design system values (`text-[14px]`, `h-[25px]`)
-4. **Prefer px** - Use `px-[4px]` over `px-1`
-5. **Transitions** - Add `transition-colors` for interactive states
+
+1. **No inline styles** - Use Tailwind classes
+2. **No duplicate dark classes** - Skip `dark:` when value matches light mode
+3. **Exact values** - `text-[14px]`, `h-[25px]`
+4. **Transitions** - `transition-colors` for interactive states
 
 ## Conditional Classes
+
 ```typescript
 import { cn } from '@/lib/utils'
 
@@ -23,25 +24,17 @@ import { cn } from '@/lib/utils'
 )} />
 ```
 
-## CSS Variables for Dynamic Styles
+## CSS Variables
+
+For dynamic values (widths, heights) synced with stores:
+
 ```typescript
-// In store setter
-setSidebarWidth: (width) => {
-  set({ sidebarWidth: width })
+// In store
+setWidth: (width) => {
+  set({ width })
   document.documentElement.style.setProperty('--sidebar-width', `${width}px`)
 }
 
 // In component
 <aside style={{ width: 'var(--sidebar-width)' }} />
 ```
-
-## Anti-Patterns
-```typescript
-// ❌ Bad
-<div style={{ width: 200 }}>
-<div className='text-[var(--text-primary)] dark:text-[var(--text-primary)]'>
-
-// ✅ Good
-<div className='w-[200px]'>
-<div className='text-[var(--text-primary)]'>
-```
diff --git a/.cursor/rules/sim-testing.mdc b/.cursor/rules/sim-testing.mdc
@@ -0,0 +1,60 @@
+---
+description: Testing patterns with Vitest
+globs: ["apps/sim/**/*.test.ts", "apps/sim/**/*.test.tsx"]
+---
+
+# Testing Patterns
+
+Use Vitest. Test files live next to source: `feature.ts` → `feature.test.ts`
+
+## Structure
+
+```typescript
+/**
+ * Tests for [feature name]
+ *
+ * @vitest-environment node
+ */
+
+// 1. Mocks BEFORE imports
+vi.mock('@sim/db', () => ({ db: { select: vi.fn() } }))
+vi.mock('@sim/logger', () => loggerMock)
+
+// 2. Imports AFTER mocks
+import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
+import { createSession, loggerMock } from '@sim/testing'
+import { myFunction } from '@/lib/feature'
+
+describe('myFunction', () => {
+  beforeEach(() => vi.clearAllMocks())
+
+  it('should do something', () => {
+    expect(myFunction()).toBe(expected)
+  })
+
+  it.concurrent('runs in parallel', () => { ... })
+})
+```
+
+## @sim/testing Package
+
+```typescript
+// Factories - create test data
+import { createBlock, createWorkflow, createSession } from '@sim/testing'
+
+// Mocks - pre-configured mocks
+import { loggerMock, databaseMock, fetchMock } from '@sim/testing'
+
+// Builders - fluent API for complex objects
+import { ExecutionBuilder, WorkflowBuilder } from '@sim/testing'
+```
+
+## Rules
+
+1. `@vitest-environment node` directive at file top
+2. **Mocks before imports** - `vi.mock()` calls must come first
+3. Use `@sim/testing` factories over manual test data
+4. `it.concurrent` for independent tests (faster)
+5. `beforeEach(() => vi.clearAllMocks())` to reset state
+6. Group related tests with nested `describe` blocks
+7. Test file naming: `*.test.ts` (not `*.spec.ts`)
diff --git a/.cursor/rules/sim-typescript.mdc b/.cursor/rules/sim-typescript.mdc
@@ -6,19 +6,15 @@ globs: ["apps/sim/**/*.ts", "apps/sim/**/*.tsx"]
 # TypeScript Rules
 
 1. **No `any`** - Use proper types or `unknown` with type guards
-2. **Props interface** - Always define, even for simple components
-3. **Callback types** - Full signature with params and return type
-4. **Generics** - Use for reusable components/hooks
-5. **Const assertions** - `as const` for constant objects/arrays
-6. **Ref types** - Explicit: `useRef<HTMLDivElement>(null)`
+2. **Props interface** - Always define for components
+3. **Const assertions** - `as const` for constant objects/arrays
+4. **Ref types** - Explicit: `useRef<HTMLDivElement>(null)`
+5. **Type imports** - `import type { X }` for type-only imports
 
-## Anti-Patterns
 ```typescript
-// ❌ Bad
+// ✗ Bad
 const handleClick = (e: any) => {}
-useEffect(() => { doSomething(prop) }, []) // Missing dep
 
-// ✅ Good  
+// ✓ Good
 const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {}
-useEffect(() => { doSomething(prop) }, [prop])
 ```
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,47 +1,295 @@
-# Expert Programming Standards
+# Sim Studio Development Guidelines
 
-**You are tasked with implementing solutions that follow best practices. You MUST be accurate, elegant, and efficient as an expert programmer.**
+You are a professional software engineer. All code must follow best practices: accurate, readable, clean, and efficient.
 
----
+## Global Standards
 
-# Role
+- **Logging**: Import `createLogger` from `@sim/logger`. Use `logger.info`, `logger.warn`, `logger.error` instead of `console.log`
+- **Comments**: Use TSDoc for documentation. No `====` separators. No non-TSDoc comments
+- **Styling**: Never update global styles. Keep all styling local to components
+- **Package Manager**: Use `bun` and `bunx`, not `npm` and `npx`
 
-You are a professional software engineer. All code you write MUST follow best practices, ensuring accuracy, quality, readability, and cleanliness. You MUST make FOCUSED EDITS that are EFFICIENT and ELEGANT.
+## Architecture
 
-## Logs
+### Core Principles
+1. Single Responsibility: Each component, hook, store has one clear purpose
+2. Composition Over Complexity: Break down complex logic into smaller pieces
+3. Type Safety First: TypeScript interfaces for all props, state, return types
+4. Predictable State: Zustand for global state, useState for UI-only concerns
 
-ENSURE that you use the logger.info and logger.warn and logger.error instead of the console.log whenever you want to display logs.
+### Root Structure
+```
+apps/sim/
+├── app/           # Next.js app router (pages, API routes)
+├── blocks/        # Block definitions and registry
+├── components/    # Shared UI (emcn/, ui/)
+├── executor/      # Workflow execution engine
+├── hooks/         # Shared hooks (queries/, selectors/)
+├── lib/           # App-wide utilities
+├── providers/     # LLM provider integrations
+├── stores/        # Zustand stores
+├── tools/         # Tool definitions
+└── triggers/      # Trigger definitions
+```
 
-## Comments
+### Naming Conventions
+- Components: PascalCase (`WorkflowList`)
+- Hooks: `use` prefix (`useWorkflowOperations`)
+- Files: kebab-case (`workflow-list.tsx`)
+- Stores: `stores/feature/store.ts`
+- Constants: SCREAMING_SNAKE_CASE
+- Interfaces: PascalCase with suffix (`WorkflowListProps`)
 
-You must use TSDOC for comments. Do not use ==== for comments to separate sections. Do not leave any comments that are not TSDOC.
+## Imports
 
-## Global Styles
+**Always use absolute imports.** Never use relative imports.
 
-You should not update the global styles unless it is absolutely necessary. Keep all styling local to components and files.
+```typescript
+// ✓ Good
+import { useWorkflowStore } from '@/stores/workflows/store'
 
-## Bun
+// ✗ Bad
+import { useWorkflowStore } from '../../../stores/workflows/store'
+```
 
-Use bun and bunx not npm and npx.
+Use barrel exports (`index.ts`) when a folder has 3+ exports.
 
-## Code Quality
+### Import Order
+1. React/core libraries
+2. External libraries
+3. UI components (`@/components/emcn`, `@/components/ui`)
+4. Utilities (`@/lib/...`)
+5. Stores (`@/stores/...`)
+6. Feature imports
+7. CSS imports
 
-- Write clean, maintainable code that follows the project's existing patterns
-- Prefer composition over inheritance
-- Keep functions small and focused on a single responsibility
-- Use meaningful variable and function names
-- Handle errors gracefully and provide useful error messages
-- Write type-safe code with proper TypeScript types
+Use `import type { X }` for type-only imports.
+
+## TypeScript
+
+1. No `any` - Use proper types or `unknown` with type guards
+2. Always define props interface for components
+3. `as const` for constant objects/arrays
+4. Explicit ref types: `useRef<HTMLDivElement>(null)`
+
+## Components
+
+```typescript
+'use client' // Only if using hooks
+
+const CONFIG = { SPACING: 8 } as const
+
+interface ComponentProps {
+  requiredProp: string
+  optionalProp?: boolean
+}
+
+export function Component({ requiredProp, optionalProp = false }: ComponentProps) {
+  // Order: refs → external hooks → store hooks → custom hooks → state → useMemo → useCallback → useEffect → return
+}
+```
+
+Extract when: 50+ lines, used in 2+ files, or has own state/logic. Keep inline when: < 10 lines, single use, purely presentational.
+
+## Hooks
+
+```typescript
+interface UseFeatureProps { id: string }
+
+export function useFeature({ id }: UseFeatureProps) {
+  const idRef = useRef(id)
+  const [data, setData] = useState<Data | null>(null)
+  
+  useEffect(() => { idRef.current = id }, [id])
+  
+  const fetchData = useCallback(async () => { ... }, []) // Empty deps when using refs
+  
+  return { data, fetchData }
+}
+```
+
+## Zustand Stores
+
+Stores live in `stores/`. Complex stores split into `store.ts` + `types.ts`.
+
+```typescript
+import { create } from 'zustand'
+import { devtools } from 'zustand/middleware'
+
+const initialState = { items: [] as Item[] }
+
+export const useFeatureStore = create<FeatureState>()(
+  devtools(
+    (set, get) => ({
+      ...initialState,
+      setItems: (items) => set({ items }),
+      reset: () => set(initialState),
+    }),
+    { name: 'feature-store' }
+  )
+)
+```
+
+Use `devtools` middleware. Use `persist` only when data should survive reload with `partialize` to persist only necessary state.
+
+## React Query
+
+All React Query hooks live in `hooks/queries/`.
+
+```typescript
+export const entityKeys = {
+  all: ['entity'] as const,
+  list: (workspaceId?: string) => [...entityKeys.all, 'list', workspaceId ?? ''] as const,
+}
+
+export function useEntityList(workspaceId?: string) {
+  return useQuery({
+    queryKey: entityKeys.list(workspaceId),
+    queryFn: () => fetchEntities(workspaceId as string),
+    enabled: Boolean(workspaceId),
+    staleTime: 60 * 1000,
+    placeholderData: keepPreviousData,
+  })
+}
+```
+
+## Styling
+
+Use Tailwind only, no inline styles. Use `cn()` from `@/lib/utils` for conditional classes.
+
+```typescript
+<div className={cn('base-classes', isActive && 'active-classes')} />
+```
+
+## EMCN Components
+
+Import from `@/components/emcn`, never from subpaths (except CSS files). Use CVA when 2+ variants exist.
 
 ## Testing
 
-- Write tests for new functionality when appropriate
-- Ensure existing tests pass before completing work
-- Follow the project's testing conventions
+Use Vitest. Test files: `feature.ts` → `feature.test.ts`
+
+```typescript
+/**
+ * @vitest-environment node
+ */
+
+// Mocks BEFORE imports
+vi.mock('@sim/db', () => ({ db: { select: vi.fn() } }))
+
+// Imports AFTER mocks
+import { describe, expect, it, vi } from 'vitest'
+import { createSession, loggerMock } from '@sim/testing'
+
+describe('feature', () => {
+  beforeEach(() => vi.clearAllMocks())
+  it.concurrent('runs in parallel', () => { ... })
+})
+```
+
+Use `@sim/testing` factories over manual test data.
+
+## Utils Rules
+
+- Never create `utils.ts` for single consumer - inline it
+- Create `utils.ts` when 2+ files need the same helper
+- Check existing sources in `lib/` before duplicating
+
+## Adding Integrations
+
+New integrations require: **Tools** → **Block** → **Icon** → (optional) **Trigger**
+
+Always look up the service's API docs first.
+
+### 1. Tools (`tools/{service}/`)
+
+```
+tools/{service}/
+├── index.ts      # Barrel export
+├── types.ts      # Params/response types
+└── {action}.ts   # Tool implementation
+```
+
+**Tool structure:**
+```typescript
+export const serviceTool: ToolConfig<Params, Response> = {
+  id: 'service_action',
+  name: 'Service Action',
+  description: '...',
+  version: '1.0.0',
+  oauth: { required: true, provider: 'service' },
+  params: { /* ... */ },
+  request: { url: '/api/tools/service/action', method: 'POST', ... },
+  transformResponse: async (response) => { /* ... */ },
+  outputs: { /* ... */ },
+}
+```
+
+Register in `tools/registry.ts`.
+
+### 2. Block (`blocks/blocks/{service}.ts`)
+
+```typescript
+export const ServiceBlock: BlockConfig = {
+  type: 'service',
+  name: 'Service',
+  description: '...',
+  category: 'tools',
+  bgColor: '#hexcolor',
+  icon: ServiceIcon,
+  subBlocks: [ /* see SubBlock Properties */ ],
+  tools: { access: ['service_action'], config: { tool: (p) => `service_${p.operation}` } },
+  inputs: { /* ... */ },
+  outputs: { /* ... */ },
+}
+```
+
+Register in `blocks/registry.ts` (alphabetically).
+
+**SubBlock Properties:**
+```typescript
+{
+  id: 'field', title: 'Label', type: 'short-input', placeholder: '...',
+  required: true,                    // or condition object
+  condition: { field: 'op', value: 'send' },  // show/hide
+  dependsOn: ['credential'],         // clear when dep changes
+  mode: 'basic',                     // 'basic' | 'advanced' | 'both' | 'trigger'
+}
+```
+
+**condition examples:**
+- `{ field: 'op', value: 'send' }` - show when op === 'send'
+- `{ field: 'op', value: ['a','b'] }` - show when op is 'a' OR 'b'
+- `{ field: 'op', value: 'x', not: true }` - show when op !== 'x'
+- `{ field: 'op', value: 'x', not: true, and: { field: 'type', value: 'dm', not: true } }` - complex
+
+**dependsOn:** `['field']` or `{ all: ['a'], any: ['b', 'c'] }`
+
+### 3. Icon (`components/icons.tsx`)
+
+```typescript
+export function ServiceIcon(props: SVGProps<SVGSVGElement>) {
+  return <svg {...props}>/* SVG from brand assets */</svg>
+}
+```
+
+### 4. Trigger (`triggers/{service}/`) - Optional
+
+```
+triggers/{service}/
+├── index.ts      # Barrel export
+├── webhook.ts    # Webhook handler
+└── {event}.ts    # Event-specific handlers
+```
+
+Register in `triggers/registry.ts`.
 
-## Performance
+### Integration Checklist
 
-- Consider performance implications of your code
-- Avoid unnecessary re-renders in React components
-- Use appropriate data structures and algorithms
-- Profile and optimize when necessary
+- [ ] Look up API docs
+- [ ] Create `tools/{service}/` with types and tools
+- [ ] Register tools in `tools/registry.ts`
+- [ ] Add icon to `components/icons.tsx`
+- [ ] Create block in `blocks/blocks/{service}.ts`
+- [ ] Register block in `blocks/registry.ts`
+- [ ] (Optional) Create and register triggers
PATCH

echo "Gold patch applied."
