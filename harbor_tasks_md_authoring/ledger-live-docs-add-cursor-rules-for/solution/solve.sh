#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ledger-live

# Idempotency guard
if grep -qF "export const selectStatus = (state: RootState) => state.myFeature.status;" ".cursor/rules/redux-slice.mdc" && grep -qF "import { createApi, fetchBaseQuery } from \"@reduxjs/toolkit/query/react\";" ".cursor/rules/rtk-query-api.mdc" && grep -qF "Define types in `state-manager/types.ts` using Zod schemas for runtime validatio" ".cursor/rules/zod-schemas.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/redux-slice.mdc b/.cursor/rules/redux-slice.mdc
@@ -0,0 +1,102 @@
+---
+description: Redux Toolkit createSlice best practices
+alwaysApply: true
+---
+
+# Redux Toolkit - createSlice
+
+## Structure
+
+- Use descriptive `name` for action type prefixes
+- Define typed `initialState` with `satisfies`
+- Export actions and reducer separately
+
+```typescript
+// ✅ GOOD
+import { createSlice, PayloadAction } from "@reduxjs/toolkit";
+
+interface MyState {
+  value: number;
+  status: "idle" | "loading" | "error";
+}
+
+const initialState: MyState = {
+  value: 0,
+  status: "idle",
+};
+
+const mySlice = createSlice({
+  name: "myFeature",
+  initialState,
+  reducers: {
+    setValue: (state, action: PayloadAction<number>) => {
+      state.value = action.payload;
+    },
+    setStatus: (state, action: PayloadAction<MyState["status"]>) => {
+      state.status = action.payload;
+    },
+  },
+});
+
+export const { setValue, setStatus } = mySlice.actions;
+export default mySlice.reducer;
+```
+
+## Registration
+
+Add the slice to `reducers/index.ts`:
+
+```typescript
+// 1. Import the reducer and state type
+import myFeature, { MyFeatureState } from "./myFeature";
+
+// 2. Add to State type
+export type State = {
+  // ...existing
+  myFeature: MyFeatureState;
+};
+
+// 3. Add to combineReducers
+const appReducer = combineReducers({
+  // ...existing
+  myFeature,
+});
+```
+
+## Reducers
+
+- Use Immer's mutable syntax safely
+- Type `PayloadAction<T>` for actions with payloads
+- Keep reducers focused on single state changes
+
+## Selectors
+
+- Define selectors with the slice
+- Use `createSelector` for derived data
+
+```typescript
+// Colocate selectors with slice
+export const selectValue = (state: RootState) => state.myFeature.value;
+export const selectStatus = (state: RootState) => state.myFeature.status;
+```
+
+## extraReducers
+
+- Use builder callback for external actions
+- Handle async thunk states (pending/fulfilled/rejected)
+
+```typescript
+extraReducers: (builder) => {
+  builder
+    .addCase(fetchData.pending, (state) => {
+      state.status = "loading";
+    })
+    .addCase(fetchData.fulfilled, (state, action) => {
+      state.status = "idle";
+      state.data = action.payload;
+    })
+    .addCase(fetchData.rejected, (state) => {
+      state.status = "error";
+    });
+},
+```
diff --git a/.cursor/rules/rtk-query-api.mdc b/.cursor/rules/rtk-query-api.mdc
@@ -0,0 +1,108 @@
+---
+description: RTK Query createApi best practices
+alwaysApply: true
+---
+
+# RTK Query - createApi
+
+## Structure
+
+- One API slice per base URL / data source
+- Define API slices in `state-manager/api.ts` files
+- Export generated hooks alongside the API
+
+```typescript
+// ✅ GOOD - state-manager/api.ts
+import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
+import { EntityTags } from "./types";
+
+export const myApi = createApi({
+  reducerPath: "myApi",
+  baseQuery: fetchBaseQuery({ baseUrl: "/api" }),
+  tagTypes: [EntityTags.Entity, EntityTags.Entities],
+  endpoints: (build) => ({
+    getEntity: build.query<Entity, string>({
+      query: (id) => `entities/${id}`,
+      providesTags: [EntityTags.Entity],
+    }),
+  }),
+});
+
+export const { useGetEntityQuery } = myApi;
+```
+
+Define tags as enums in `state-manager/types.ts`:
+
+```typescript
+export enum EntityTags {
+  Entity = "Entity",
+  Entities = "Entities",
+}
+```
+
+## Endpoints
+
+- Use `build.query` for GET requests
+- Use `build.mutation` for POST/PUT/DELETE
+- Type both response and argument: `build.query<ResponseType, ArgType>`
+- Use `void` for no arguments: `build.query<Data[], void>`
+
+## Caching & Tags
+
+- Define tags as **enums** in `types.ts`
+- Use `providesTags` on queries for cache invalidation
+- Use `invalidatesTags` on mutations to trigger refetch
+- Use `keepUnusedDataFor` for custom cache duration
+
+```typescript
+endpoints: (build) => ({
+  getItems: build.query<Item[], void>({
+    query: () => "items",
+    providesTags: [ItemTags.Items],
+    keepUnusedDataFor: 60, // seconds
+  }),
+  addItem: build.mutation<Item, Partial<Item>>({
+    query: (body) => ({ url: "items", method: "POST", body }),
+    invalidatesTags: [ItemTags.Items],
+  }),
+}),
+```
+
+## Transform Responses
+
+- Use `transformResponse` to reshape API data
+- Use `transformErrorResponse` for custom error handling
+
+```typescript
+getItems: build.query<Item[], void>({
+  query: () => "items",
+  transformResponse: (response: ApiResponse) => response.data.items,
+}),
+```
+
+## Error Handling
+
+- Always catch errors in custom `baseQuery` or `queryFn`
+- Return `{ data }` on success, `{ error }` on failure
+
+```typescript
+// ✅ GOOD - errors are caught and returned
+queryFn: async (arg) => {
+  try {
+    const data = await fetchData(arg);
+    return { data };
+  } catch (error) {
+    return { error: { status: "CUSTOM_ERROR", data: error } };
+  }
+},
+```
+
+## Registration
+
+Register APIs in `reducers/rtkQueryApi.ts`:
+
+```typescript
+const APIs = {
+  [myApi.reducerPath]: myApi,
+};
+```
diff --git a/.cursor/rules/zod-schemas.mdc b/.cursor/rules/zod-schemas.mdc
@@ -0,0 +1,90 @@
+---
+description: Zod schema validation patterns for API types
+alwaysApply: true
+---
+
+# Zod Schema Validation
+
+Define types in `state-manager/types.ts` using Zod schemas for runtime validation.
+
+## Structure
+
+- Define Zod schemas first, then infer TypeScript types
+- Use enums for tag types
+- Export both schemas and inferred types
+
+```typescript
+// ✅ GOOD - state-manager/types.ts
+import { z } from "zod";
+
+// 1. Define tag types as enum
+export enum MyDataTags {
+  Items = "Items",
+  Item = "Item",
+}
+
+// 2. Define Zod schemas with validation rules
+const ItemSchema = z.object({
+  id: z.string().uuid(),
+  name: z.string().min(1),
+  value: z.number().min(0),
+  status: z.enum(["active", "inactive"]),
+  createdAt: z.string().datetime(),
+});
+
+const ItemResponseSchema = z.object({
+  data: ItemSchema,
+  meta: z.object({
+    timestamp: z.string(),
+    version: z.string(),
+  }),
+});
+
+const ItemListResponseSchema = z.object({
+  items: z.array(ItemSchema),
+  pagination: z.object({
+    nextCursor: z.string().optional(),
+    total: z.number(),
+  }),
+});
+
+// 3. Infer TypeScript types from schemas
+export type Item = z.infer<typeof ItemSchema>;
+export type ItemResponse = z.infer<typeof ItemResponseSchema>;
+export type ItemListResponse = z.infer<typeof ItemListResponseSchema>;
+
+// 4. Define query params as interfaces
+export interface GetItemsParams {
+  search?: string;
+  limit?: number;
+  cursor?: string;
+}
+
+// 5. Export schemas for runtime validation
+export { ItemSchema, ItemResponseSchema, ItemListResponseSchema };
+```
+
+## Using Schemas in API
+
+```typescript
+// state-manager/api.ts
+import { ItemListResponseSchema, type ItemListResponse } from "./types";
+
+endpoints: (build) => ({
+  getItems: build.query<ItemListResponse, GetItemsParams>({
+    query: (params) => ({ url: "items", params }),
+    transformResponse: (response: unknown) => {
+      // Runtime validation
+      return ItemListResponseSchema.parse(response);
+    },
+  }),
+}),
+```
+
+## Best Practices
+
+- Use `.min()`, `.max()`, `.uuid()`, `.email()` for field validation
+- Use `z.enum()` for fixed string values
+- Use `z.union()` for multiple possible types
+- Use `.optional()` for nullable fields
+- Always infer types with `z.infer<typeof Schema>`
PATCH

echo "Gold patch applied."
