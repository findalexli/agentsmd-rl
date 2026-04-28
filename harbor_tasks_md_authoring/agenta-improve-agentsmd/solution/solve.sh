#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agenta

# Idempotency guard
if grep -qF "For data fetching, use `atomWithQuery` from `jotai-tanstack-query`. This combine" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -68,6 +68,133 @@ Our folder structure follows a module-based architecture that prioritizes mainta
     - Use Context for complex state with multiple consumers
     - Local component state for UI-only concerns
 
+4. **Avoiding Prop Drilling**
+    - **When state is only meaningful within a component tree**: Use Jotai atoms instead of prop drilling
+    - Prop drilling (passing props through multiple levels) makes code brittle and hard to maintain
+    - Atoms allow any component in the tree to access state without intermediate components knowing about it
+
+**Example - Avoid prop drilling:**
+
+❌ **Don't do this:**
+```typescript
+function Parent() {
+    const [selectedId, setSelectedId] = useState(null)
+    return <Child1 selectedId={selectedId} setSelectedId={setSelectedId} />
+}
+
+function Child1({selectedId, setSelectedId}) {
+    // Child1 doesn't use these props, just passes them down
+    return <Child2 selectedId={selectedId} setSelectedId={setSelectedId} />
+}
+
+function Child2({selectedId, setSelectedId}) {
+    return <GrandChild selectedId={selectedId} setSelectedId={setSelectedId} />
+}
+
+function GrandChild({selectedId, setSelectedId}) {
+    // Finally uses them here
+    return <div onClick={() => setSelectedId(123)}>{selectedId}</div>
+}
+```
+
+✅ **Use atoms instead:**
+```typescript
+// In module store or appropriate location
+export const selectedIdAtom = atom<string | null>(null)
+
+function Parent() {
+    return <Child1 />
+}
+
+function Child1() {
+    // No props needed
+    return <Child2 />
+}
+
+function Child2() {
+    return <GrandChild />
+}
+
+function GrandChild() {
+    // Direct access to state
+    const [selectedId, setSelectedId] = useAtom(selectedIdAtom)
+    return <div onClick={() => setSelectedId(123)}>{selectedId}</div>
+}
+```
+
+**When to use atoms vs props:**
+- Use **props** when: Parent component owns/controls the state, single level passing, or props are configuration/callbacks
+- Use **atoms** when: State needs to be shared across non-parent-child components, multiple levels of drilling, or state is module/feature-scoped
+
+5. **Persisted State with LocalStorage**
+
+For state that needs to persist across browser sessions, use `atomWithStorage` from `jotai/utils`:
+
+```typescript
+import {atomWithStorage} from "jotai/utils"
+
+// Simple usage - automatically syncs with localStorage
+export const rowHeightAtom = atomWithStorage<"small" | "medium" | "large">(
+    "agenta:table:row-height", // localStorage key
+    "medium", // default value
+)
+
+// Usage in components - same as regular atoms
+const [rowHeight, setRowHeight] = useAtom(rowHeightAtom)
+```
+
+**For storing app/module-scoped data:**
+```typescript
+// Storage atom holds all app-specific data
+const selectedVariantsByAppAtom = atomWithStorage<Record<string, string[]>>(
+    "agenta_selected_revisions_v2",
+    {},
+)
+
+// Derived atom provides scoped access per app
+export const selectedVariantsAtom = atom(
+    (get) => {
+        const appId = get(routerAppIdAtom) || "__global__"
+        const all = get(selectedVariantsByAppAtom)
+        return all[appId] || []
+    },
+    (get, set, next: string[]) => {
+        const appId = get(routerAppIdAtom) || "__global__"
+        const all = get(selectedVariantsByAppAtom)
+        set(selectedVariantsByAppAtom, {...all, [appId]: next})
+    },
+)
+```
+
+**For nullable strings, use custom stringStorage:**
+```typescript
+import {stringStorage} from "@/oss/state/utils/stringStorage"
+
+export const recentAppIdAtom = atomWithStorage<string | null>(
+    "agenta:recent-app",
+    null,
+    stringStorage, // Handles null values properly
+)
+```
+
+**When to use `atomWithStorage`:**
+- User preferences (theme, row height, view mode)
+- Recently used items (recent app, recent filter)
+- UI state that should persist (sidebar open/closed, panel sizes)
+- Form drafts or temporary data
+
+**Best practices:**
+- Prefix keys with `agenta:` for consistency (e.g., `"agenta:table:row-height"`)
+- Use TypeScript types for type safety
+- Provide sensible defaults
+- For complex objects, `atomWithStorage` handles JSON serialization automatically
+- For nullable strings, use `stringStorage` helper
+
+**Examples in codebase:**
+- `web/oss/src/components/EvalRunDetails2/state/rowHeight.ts` - User preference
+- `web/oss/src/state/app/atoms/fetcher.ts` - Recent app tracking
+- `web/oss/src/components/Playground/state/atoms/core.ts` - App-scoped selections
+
 #### Implementation Strategy
 
 -   **Current Approach**: Gradual adoption during regular development
@@ -85,125 +212,316 @@ This structure supports:
 
 ### Data Fetching Best Practices
 
-We recommend using SWR with Axios for data fetching instead of useEffect patterns. This helps achieve cleaner code while,
+**Primary Pattern: Jotai Atoms with TanStack Query**
+
+For data fetching, use `atomWithQuery` from `jotai-tanstack-query`. This combines Jotai's reactive state with TanStack Query's caching and synchronization.
+
+**When to use `atomWithQuery`:**
+- Fetching data from APIs
+- When query depends on other atoms (e.g., `projectIdAtom`, `appIdAtom`)
+- Sharing data across multiple components
+- Need caching, loading states, and automatic refetching
+
+**Basic Pattern:**
+
+```typescript
+import {atomWithQuery} from "jotai-tanstack-query"
+
+export const dataQueryAtom = atomWithQuery((get) => {
+    const projectId = get(projectIdAtom) // Read dependencies
+    
+    return {
+        queryKey: ["data", projectId], // Include all dependencies
+        queryFn: () => fetchData(projectId),
+        staleTime: 60_000,
+        refetchOnWindowFocus: false,
+        enabled: !!projectId, // Conditional fetching
+    }
+})
+
+// Usage in components
+const query = useAtomValue(dataQueryAtom)
+const data = query.data
+const isLoading = query.isPending
+```
 
--   simplifying management of fetch states.
--   handling cache better
--   having a more interactive UI by revalidating in background
--   utilizing optimistic mutations.
+**For parameterized queries, use `atomFamily`:**
 
-#### Example: Converting useEffect Data Fetching to SWR with Axios
+```typescript
+export const itemQueryAtomFamily = atomFamily((itemId: string) =>
+    atomWithQuery((get) => {
+        const projectId = get(projectIdAtom)
+        return {
+            queryKey: ["item", itemId, projectId],
+            queryFn: () => fetchItem(itemId),
+            enabled: !!itemId && !!projectId,
+        }
+    })
+)
 
-❌ **Avoid this pattern:**
+// Usage
+const itemQuery = useAtomValue(itemQueryAtomFamily(itemId))
+```
+
+**Derived atoms for data transformation:**
+
+```typescript
+export const dataAtom = selectAtom(
+    dataQueryAtom,
+    (res) => res.data ?? [],
+    deepEqual
+)
+```
+
+**Mutations and invalidation:**
+
+```typescript
+export const createItemAtom = atom(
+    null,
+    async (_get, _set, payload) => {
+        const res = await createItem(payload)
+        await queryClient.invalidateQueries({queryKey: ["items"]})
+        return res
+    }
+)
+```
+
+**Key Principles:**
+1. Include all reactive dependencies in `queryKey`
+2. Use `enabled` for conditional queries
+3. Use `selectAtom` for derived data
+4. Invalidate queries after mutations
+5. Set appropriate `staleTime` for caching
+
+**Examples in codebase:**
+- `web/oss/src/state/profile/selectors/user.ts` - Simple query
+- `web/oss/src/state/environment/atoms/fetcher.ts` - Multi-dependency query
+- `web/oss/src/state/queries/atoms/fetcher.ts` - Atom family with parameters
+- `web/oss/src/state/testset/hooks/useTestset.ts` - Hook wrapper pattern
+
+---
+
+**Legacy: SWR Pattern (avoid for new code)**
+
+We previously used SWR with Axios for data fetching. This pattern is still present in older code but should not be used for new features.
+
+#### ❌ Avoid: useEffect for Data Fetching
+
+Don't use `useEffect` with manual state management for data fetching:
 
 ```javascript
+// DON'T DO THIS
 useEffect(() => {
-    fetchData1()
-        .then((data1) => {
-            setData1(data1)
-        })
-        .catch((error) => {
-            setError1(error)
-        })
-
-    fetchData2()
-        .then((data2) => {
-            setData2(data2)
-        })
-        .catch((error) => {
-            setError2(error)
-        })
+    fetchData().then(setData).catch(setError)
 }, [])
 ```
 
-✅ **Use this pattern:**
+Use `atomWithQuery` instead (see above).
 
-We configure SWR globally with our pre-configured Axios instance:
+### Styling Best Practices
 
-```javascript
-// src/utils/swrConfig.js
-import axios from "@/oss/lib/helpers/axios"
-import useSWR from "swr"
+#### Use Tailwind CSS (Preferred)
 
-const fetcher = (url) => axios.get(url).then((res) => res.data)
+**Always prefer Tailwind utility classes over CSS-in-JS or separate CSS files** for styling whenever possible.
 
-export const swrConfig = {
-    fetcher,
-}
+✅ **Preferred: Tailwind classes**
+```typescript
+// Good - Uses Tailwind utilities
+<main className="flex flex-col grow h-full overflow-hidden items-center justify-center">
+    <Card className="max-w-[520px] w-[90%] text-center">
+        <Typography.Title level={3} className="!mb-2">
+            Unable to establish connection
+        </Typography.Title>
+    </Card>
+</main>
 ```
 
-To ensure SWR configuration is applied globally, wrap your application with SWRConfig in `_app.tsx`:
+❌ **Avoid: CSS-in-JS (react-jss, styled-components)**
+```typescript
+// Avoid - Creates extra overhead and complexity
+const useStyles = createUseStyles((theme: JSSTheme) => ({
+    collapseContainer: {
+        "& .ant-collapse-header": {
+            backgroundColor: `#FAFAFB !important`,
+        },
+    },
+}))
 
-```javascript
-// src/pages/_app.tsx
-import {SWRConfig} from "swr"
-import {swrConfig} from "../utils/swrConfig"
-
-function MyApp({Component, pageProps}) {
-    return (
-        <SWRConfig value={swrConfig}>
-            <Component {...pageProps} />
-        </SWRConfig>
-    )
+function Component() {
+    const classes = useStyles()
+    return <div className={classes.collapseContainer}>...</div>
 }
+```
 
-export default MyApp
+❌ **Avoid: Inline styles**
+```typescript
+// Avoid - Not themeable, harder to maintain
+<div style={{maxWidth: "520px", width: "90%", textAlign: "center"}}>
 ```
 
-and data can be then be fetched in a way that fits react mental model inside the component:
+**When CSS-in-JS is acceptable:**
+- Complex Ant Design component overrides that can't be done with Tailwind
+- Dynamic theme-dependent styles that require JS calculations
+- Legacy components (refactor to Tailwind when touching the code)
 
-```javascript
-import useSWR from "swr"
+**Tailwind benefits:**
+- No style bloat or unused CSS
+- Consistent design system
+- Better performance (no runtime style injection)
+- Easier to read and maintain
+- Works seamlessly with Ant Design
 
-function Component() {
-    const {data: data1, error: error1, loading: loadingData1} = useSWR("/api/data1")
-    const {data: data2, error: error2, loading: loadingData2} = useSWR("/api/data2")
-
-    if (error1 || error2) return <div>Error loading data</div>
-    if (!data1 || !data2) return <div>Loading...</div>
-
-    return (
-        <div>
-            <div>Data 1: {data1}</div>
-            <div>Data 2: {data2}</div>
-        </div>
-    )
-}
+**Examples in codebase:**
+- `web/oss/src/components/CustomWorkflowBanner/index.tsx` - Good Tailwind usage
+- `web/oss/src/components/ChatInputs/ChatInputs.tsx` - Mixed (being migrated)
+
+---
+
+### React Best Practices
+
+#### Component Reusability
+
+**Before implementing similar functionality in multiple places, consider reusability:**
+
+When you notice patterns that could be extracted:
+1. **Don't immediately refactor** - Jumping straight to abstraction can over-engineer
+2. **Ask the developer** with context about the potential for reuse
+3. **Provide analysis**: Show where similar code exists and potential benefits/costs of refactoring
+
+**Example prompt when detecting reusability:**
 ```
+I notice this table cell rendering logic is similar to:
+- components/EvalRunDetails2/TableCells/MetricCell.tsx
+- components/Evaluators/cells/MetricDisplayCell.tsx
 
-Mutations can be triggered via Swr in the following way
+Before implementing, would you like me to:
+A) Create a reusable component (requires refactoring both existing usages)
+B) Proceed with current implementation (can consolidate later if pattern repeats)
 
-```javascript
-import useSWRMutation from 'swr/mutation'
+The trade-off: (A) takes more time now but improves maintainability; (B) is faster but may create tech debt.
+```
 
-async function sendRequest(url, { arg }: { arg: { username: string }}) {
-  return fetch(url, {
-    method: 'POST',
-    body: JSON.stringify(arg)
-  }).then(res => res.json())
+**When to extract components:**
+- Used in 3+ places with similar logic
+- Complex logic that benefits from isolation
+- Clear, stable interface that won't change often
+
+**When NOT to extract:**
+- Only used twice (wait for third usage to confirm pattern)
+- Requirements are still evolving
+- Small, simple components (< 20 lines)
+
+---
+
+#### Performance Considerations
+
+**Critical for evaluations and observability features** - these handle large datasets:
+
+1. **Minimize Re-renders**
+   - Use `useMemo` for expensive computations
+   - Use `React.memo` for components that receive stable props
+   - Avoid inline functions/objects in render (especially in lists)
+
+```typescript
+// ❌ Bad - Creates new function every render
+{items.map(item => <Row key={item.id} onClick={() => handleClick(item)} />)}
+
+// ✅ Good - Stable callback
+const handleRowClick = useCallback((item) => handleClick(item), [])
+{items.map(item => <Row key={item.id} onClick={handleRowClick} item={item} />)}
+```
+
+2. **Optimize Query Updates**
+   - Be mindful of `queryKey` dependencies - don't include frequently changing values unnecessarily
+   - Use `select` option in queries to extract only needed data
+   - Consider `staleTime` for data that doesn't change often
+
+```typescript
+// ❌ Bad - Refetches on every UI update
+atomWithQuery((get) => ({
+    queryKey: ["data", get(currentTimeAtom)], // currentTimeAtom updates every second!
+    queryFn: fetchData
+}))
+
+// ✅ Good - Only refetches when meaningful dependencies change
+atomWithQuery((get) => ({
+    queryKey: ["data", get(projectIdAtom), get(filterAtom)],
+    queryFn: fetchData,
+    staleTime: 60_000 // Cache for 1 minute
+}))
+```
+
+3. **Virtualization for Large Lists**
+   - Use virtual scrolling for lists with 100+ items
+   - Reference: `InfiniteVirtualTable` component
+
+4. **Debounce/Throttle User Input**
+   - Debounce search inputs, filters
+   - Throttle scroll handlers, resize handlers
+
+---
+
+#### Modular Component Design
+
+**Keep components focused and decoupled:**
+
+✅ **Good: Component owns its internal concerns**
+```typescript
+// Component only needs IDs, fetches its own data
+function UserCard({userId}: {userId: string}) {
+    const user = useAtomValue(userQueryAtomFamily(userId))
+    return <Card>{user.name}</Card>
 }
 
-function App() {
-  const { trigger, isMutating } = useSWRMutation('/api/user', sendRequest, /* options */)
-
-  return (
-    <button
-      disabled={isMutating}
-      onClick={async () => {
-        try {
-          const result = await trigger({ username: 'johndoe' }, /* options */)
-        } catch (e) {
-          // error handling
-        }
-      }}
-    >
-      Create User
-    </button>
-  )
+// Parent doesn't need to know about user data structure
+function UserList({userIds}: {userIds: string[]}) {
+    return userIds.map(id => <UserCard key={id} userId={id} />)
 }
 ```
 
-### React Best Practices
+❌ **Bad: Parent must know too much**
+```typescript
+// Parent must fetch and pass everything
+function UserCard({
+    userName,
+    userEmail,
+    userAvatar,
+    userRole,
+    userDepartment
+}: {/* many props */}) {
+    return <Card>...</Card>
+}
+
+// Parent is tightly coupled to UserCard's needs
+function UserList({userIds}: {userIds: string[]}) {
+    const users = useAtomValue(usersQueryAtom) // Must fetch all data
+    return users.map(user => (
+        <UserCard
+            key={user.id}
+            userName={user.name}
+            userEmail={user.email}
+            userAvatar={user.avatar}
+            userRole={user.role}
+            userDepartment={user.department}
+        />
+    ))
+}
+```
+
+**Principles:**
+- **High cohesion**: Component contains related logic together
+- **Low coupling**: Minimal dependencies on parent/sibling components
+- **Props should be minimal**: Pass IDs/keys, not entire data structures when possible
+- **Components fetch their own data**: Use atoms with queries for data needs
+- **Single Responsibility**: Each component does one thing well
+
+**Benefits:**
+- Easier to test in isolation
+- Can reuse without bringing unnecessary dependencies
+- Changes to one component don't cascade to others
+- Clear interfaces and responsibilities
+
+---
 
 #### Avoiding Inline Array Props
 
PATCH

echo "Gold patch applied."
