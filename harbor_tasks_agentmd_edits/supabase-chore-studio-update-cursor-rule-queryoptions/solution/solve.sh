#!/usr/bin/env bash
set -euo pipefail

cd /workspace/supabase

# Idempotent: skip if already applied
if grep -q 'thirdPartyAuthIntegrationsQueryOptions' apps/studio/data/third-party-auth/integrations-query.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.cursor/rules/studio/queries/RULE.md b/.cursor/rules/studio/queries/RULE.md
index 0e394b01d28ae..a68bd2b8d9128 100644
--- a/.cursor/rules/studio/queries/RULE.md
+++ b/.cursor/rules/studio/queries/RULE.md
@@ -9,12 +9,12 @@ alwaysApply: false

 # Studio queries & mutations (React Query)

-Follow the `apps/studio/data/` patterns used by edge functions:
+Follow the `apps/studio/data/` patterns:

-- Query hook: `apps/studio/data/edge-functions/edge-functions-query.ts`
+- Query options: `apps/studio/data/table-editor/table-editor-query.ts`
 - Mutation hook: `apps/studio/data/edge-functions/edge-functions-update-mutation.ts`
 - Keys: `apps/studio/data/edge-functions/keys.ts`
-- Page usage: `apps/studio/pages/project/[ref]/functions/index.tsx`
+- Page usage: `apps/studio/pages/project/[ref]/database/tables/[id].tsx`

 ## Organize query keys

@@ -31,23 +31,41 @@ export const edgeFunctionsKeys = {
 }
 ```

-## Write a query hook
+## Write query options (preferred pattern)

-- Export `Variables`, `Data`, and `Error` types from the file.
-- Implement a `getX(variables, signal?)` function that:
+Use `queryOptions` from `@tanstack/react-query` to define reusable query configurations. This pattern:
+
+- Provides type safety for query keys and data
+- Can be used with `useQuery()` in components
+- Can be used with `queryClient.fetchQuery()` for imperative fetching
+
+Guidelines:
+
+- Export `XVariables`, `XData`, and `XError` types from the file (prefixed with the domain name).
+- Implement a private `getX(variables, signal?)` function that:
   - throws if required variables are missing
   - passes the `signal` through to the fetcher for cancellation
-  - calls `handleError(error)` and returns `data`
-- Wrap it in `useXQuery()` using `useQuery`, `UseCustomQueryOptions`, and a domain key helper.
-- Gate with `enabled` so the query doesn't run until required variables exist (and platform-only queries should include `IS_PLATFORM`).
+  - calls `handleError(error)` on failure (which throws) — the function returns `data` on success
+  - this function should NOT be exported. For imperative fetching, use `queryClient.fetchQuery(xQueryOptions(...))`
+- Export `xQueryOptions()` using `queryOptions` from `@tanstack/react-query`.
+- Gate with `enabled` so the query doesn't run until required variables exist (and platform-only queries should include `IS_PLATFORM` from `lib/constants`).
+- When migrating away from exporting `useQuery`, move all options into the `xQueryOptions` as default values.
+- No extra options should be added as params, if the user wants to overwrite the options, they can do by destructuring the query options. For example, `{ ...xQueryOptions(vars), enabled: true }`.

 Template:

 ```ts
+import { queryOptions } from '@tanstack/react-query'
+
+import { xKeys } from './keys'
+import { get, handleError } from '@/data/fetchers'
+import { IS_PLATFORM } from '@/lib/constants'
+import { ResponseError } from '@/types'
+
 export type XVariables = { projectRef?: string }
 export type XError = ResponseError

-export async function getX({ projectRef }: XVariables, signal?: AbortSignal) {
+async function getX({ projectRef }: XVariables, signal?: AbortSignal) {
   if (!projectRef) throw new Error('projectRef is required')
   const { data, error } = await get('/v1/projects/{ref}/x', {
     params: { path: { ref: projectRef } },
@@ -59,16 +77,58 @@ export async function getX({ projectRef }: XVariables, signal?: AbortSignal) {

 export type XData = Awaited<ReturnType<typeof getX>>

-export const useXQuery = <TData = XData>(
-  { projectRef }: XVariables,
-  { enabled = true, ...options }: UseCustomQueryOptions<XData, XError, TData> = {}
-) =>
-  useQuery<XData, XError, TData>({
+export const xQueryOptions = ({ projectRef }: XVariables) => {
+  return queryOptions({
     queryKey: xKeys.list(projectRef),
     queryFn: ({ signal }) => getX({ projectRef }, signal),
-    enabled: IS_PLATFORM && enabled && typeof projectRef !== 'undefined',
-    ...options,
+    enabled: IS_PLATFORM && typeof projectRef !== 'undefined',
   })
+}
+```
+
+## Using query options in components
+
+Use `useQuery` directly with the query options:
+
+```ts
+import { useQuery } from '@tanstack/react-query'
+
+import { xQueryOptions } from '@/data/x/x-query'
+
+// In component:
+const { data, isPending, isError } = useQuery(
+  xQueryOptions({
+    projectRef: project?.ref,
+    connectionString: project?.connectionString,
+  })
+)
+```
+
+## Imperative fetching (outside React or in callbacks)
+
+Use `queryClient.fetchQuery()` with the query options:
+
+```ts
+import { useQueryClient } from '@tanstack/react-query'
+
+import { xQueryOptions } from '@/data/x/x-query'
+
+// In component:
+const queryClient = useQueryClient()
+
+const handleClick = useCallback(
+  async (id: number) => {
+    const data = await queryClient.fetchQuery(
+      xQueryOptions({
+        id,
+        projectRef,
+        connectionString: project?.connectionString,
+      })
+    )
+    // use data...
+  },
+  [project?.connectionString, projectRef, queryClient]
+)
 ```

 ## Write a mutation hook
@@ -78,12 +138,24 @@ export const useXQuery = <TData = XData>(
 - Prefer a `useXMutation()` wrapper that:
   - accepts `UseCustomMutationOptions` (omit `mutationFn`)
   - invalidates the relevant `list()` + `detail()` keys in `onSuccess` and `await`s them via `Promise.all`
-  - defaults to a `toast.error(...)` when `onError` isn't provided
+  - defaults to a `toast.error(...)` when `onError` isn't provided

 Template:

 ```ts
-export const useXUpdateMutation = ({ onSuccess, onError, ...options } = {}) => {
+import { useMutation, UseMutationOptions, useQueryClient } from '@tanstack/react-query'
+import toast from 'react-hot-toast'
+
+import { xKeys } from './keys'
+import type { UseCustomMutationOptions } from '@/data/custom-mutation'
+
+type XUpdateVariables = { projectRef: string; slug: string; payload: XPayload }
+
+export const useXUpdateMutation = ({
+  onSuccess,
+  onError,
+  ...options
+}: UseMutationOptions<XData, XError, XUpdateVariables> = {}) => {
   const queryClient = useQueryClient()
   return useMutation({
     mutationFn: updateX,
@@ -107,7 +179,7 @@ export const useXUpdateMutation = ({ onSuccess, onError, ...options } = {}) => {

 ## Component usage

-- Prefer React Query's v5 flags:
+- Prefer React Query's v5 flags:
   - `isPending` for initial load (often aliased to `isLoading`)
   - `isFetching` for background refetches
-- Render states explicitly (pending → error → success), like `apps/studio/pages/project/[ref]/functions/index.tsx`.
+- Render states explicitly (pending → error → success), like `apps/studio/pages/project/[ref]/database/tables/[id].tsx`.
diff --git a/apps/studio/components/interfaces/Auth/ThirdPartyAuthForm/index.tsx b/apps/studio/components/interfaces/Auth/ThirdPartyAuthForm/index.tsx
index 082ee52c7179e..a6d7c82e42a05 100644
--- a/apps/studio/components/interfaces/Auth/ThirdPartyAuthForm/index.tsx
+++ b/apps/studio/components/interfaces/Auth/ThirdPartyAuthForm/index.tsx
@@ -1,22 +1,12 @@
 import { PermissionAction } from '@supabase/shared-types/out/constants'
+import { useQuery } from '@tanstack/react-query'
+import { useParams } from 'common'
 import { Loader2 } from 'lucide-react'
 import { useState } from 'react'
 import { toast } from 'sonner'
-
-import { useParams } from 'common'
-import AlertError from 'components/ui/AlertError'
-import { DocsButton } from 'components/ui/DocsButton'
-import { InlineLink } from 'components/ui/InlineLink'
-import { useDeleteThirdPartyAuthIntegrationMutation } from 'data/third-party-auth/integration-delete-mutation'
-import {
-  ThirdPartyAuthIntegration,
-  useThirdPartyAuthIntegrationsQuery,
-} from 'data/third-party-auth/integrations-query'
-import { useAsyncCheckPermissions } from 'hooks/misc/useCheckPermissions'
-import { DOCS_URL } from 'lib/constants'
 import { cn } from 'ui'
-import { EmptyStatePresentational } from 'ui-patterns'
 import ConfirmationModal from 'ui-patterns/Dialogs/ConfirmationModal'
+import { EmptyStatePresentational } from 'ui-patterns/EmptyStatePresentational'
 import {
   PageSection,
   PageSectionAside,
@@ -26,6 +16,7 @@ import {
   PageSectionSummary,
   PageSectionTitle,
 } from 'ui-patterns/PageSection'
+
 import { AddIntegrationDropdown } from './AddIntegrationDropdown'
 import { CreateAuth0IntegrationDialog } from './CreateAuth0Dialog'
 import { CreateAwsCognitoAuthIntegrationDialog } from './CreateAwsCognitoAuthDialog'
@@ -38,6 +29,16 @@ import {
   getIntegrationTypeLabel,
   INTEGRATION_TYPES,
 } from './ThirdPartyAuthForm.utils'
+import AlertError from '@/components/ui/AlertError'
+import { DocsButton } from '@/components/ui/DocsButton'
+import { InlineLink } from '@/components/ui/InlineLink'
+import { useDeleteThirdPartyAuthIntegrationMutation } from '@/data/third-party-auth/integration-delete-mutation'
+import {
+  ThirdPartyAuthIntegration,
+  thirdPartyAuthIntegrationsQueryOptions,
+} from '@/data/third-party-auth/integrations-query'
+import { useAsyncCheckPermissions } from '@/hooks/misc/useCheckPermissions'
+import { DOCS_URL } from '@/lib/constants'

 export const ThirdPartyAuthForm = () => {
   const { ref: projectRef } = useParams()
@@ -47,7 +48,7 @@ export const ThirdPartyAuthForm = () => {
     isError,
     isSuccess,
     error,
-  } = useThirdPartyAuthIntegrationsQuery({ projectRef })
+  } = useQuery(thirdPartyAuthIntegrationsQueryOptions({ projectRef }))
   const integrations = integrationsData || []

   const [selectedIntegration, setSelectedIntegration] = useState<INTEGRATION_TYPES>()
diff --git a/apps/studio/data/third-party-auth/integrations-query.ts b/apps/studio/data/third-party-auth/integrations-query.ts
index 20975a8fa66e4..feb8e9b9f50e3 100644
--- a/apps/studio/data/third-party-auth/integrations-query.ts
+++ b/apps/studio/data/third-party-auth/integrations-query.ts
@@ -1,17 +1,20 @@
-import { useQuery } from '@tanstack/react-query'
+import { queryOptions } from '@tanstack/react-query'
 import { components } from 'api-types'
-import { get, handleError } from 'data/fetchers'
-import type { ResponseError, UseCustomQueryOptions } from 'types'
+
 import { keys } from './keys'
+import { get, handleError } from '@/data/fetchers'
+import type { ResponseError } from '@/types'

-export type GetThirdPartyAuthIntegrationsVariables = {
+export type ThirdPartyAuthIntegrationsVariables = {
   projectRef?: string
 }

+export type ThirdPartyAuthIntegrationsError = ResponseError
+
 export type ThirdPartyAuthIntegration = components['schemas']['ThirdPartyAuth']

-export async function getThirdPartyAuthIntegrations(
-  { projectRef }: GetThirdPartyAuthIntegrationsVariables,
+async function getThirdPartyAuthIntegrations(
+  { projectRef }: ThirdPartyAuthIntegrationsVariables,
   signal?: AbortSignal
 ) {
   if (!projectRef) throw new Error('projectRef is required')
@@ -29,16 +32,13 @@ export type ThirdPartyAuthIntegrationsData = Awaited<
   ReturnType<typeof getThirdPartyAuthIntegrations>
 >

-export const useThirdPartyAuthIntegrationsQuery = <TData = ThirdPartyAuthIntegrationsData>(
-  { projectRef }: GetThirdPartyAuthIntegrationsVariables,
-  {
-    enabled = true,
-    ...options
-  }: UseCustomQueryOptions<ThirdPartyAuthIntegrationsData, ResponseError, TData> = {}
-) =>
-  useQuery<ThirdPartyAuthIntegrationsData, ResponseError, TData>({
+export const thirdPartyAuthIntegrationsQueryOptions = (
+  { projectRef }: ThirdPartyAuthIntegrationsVariables,
+  { enabled = true }: { enabled?: boolean } = { enabled: true }
+) => {
+  return queryOptions({
     queryKey: keys.integrations(projectRef),
     queryFn: ({ signal }) => getThirdPartyAuthIntegrations({ projectRef }, signal),
     enabled: enabled && typeof projectRef !== 'undefined',
-    ...options,
   })
+}
diff --git a/apps/studio/types/react-query.ts b/apps/studio/types/react-query.ts
index c6a2f622ea857..fbb8048193f6e 100644
--- a/apps/studio/types/react-query.ts
+++ b/apps/studio/types/react-query.ts
@@ -13,6 +13,7 @@ export type UseCustomQueryOptions<
   TQueryKey extends QueryKey = QueryKey,
 > = Omit<UseQueryOptions<TQueryFnData, TError, TData, TQueryKey>, 'queryKey'>

+// @deprecated Just use UseMutationOptions directly
 export type UseCustomMutationOptions<
   TData = unknown,
   TError = unknown,

PATCH

echo "Patch applied successfully."
