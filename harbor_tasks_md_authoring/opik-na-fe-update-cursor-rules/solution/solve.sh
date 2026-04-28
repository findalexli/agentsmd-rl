#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opik

# Idempotency guard
if grep -qF "expect(screen.getByRole(\"alert\")).toHaveTextContent(\"Email is required\");" "apps/opik-frontend/.cursor/rules/accessibility-testing.mdc" && grep -qF "queryFn: ({ pageParam = 1 }) => fetchEntities({ page: pageParam })," "apps/opik-frontend/.cursor/rules/api-data-fetching.mdc" && grep -qF "When you like the emulation of some functionality, try to isolate it in a way th" "apps/opik-frontend/.cursor/rules/code-quality.mdc" && grep -qF "setCurrentStep((prev) => Math.min(prev + 1, steps.length - 1));" "apps/opik-frontend/.cursor/rules/forms.mdc" && grep -qF "- Simple object/array literals that don't impact child components" "apps/opik-frontend/.cursor/rules/performance.mdc" && grep -qF "export const useEntityFilters = () => useEntityStore((state) => state.filters);" "apps/opik-frontend/.cursor/rules/state-management.mdc" && grep -qF "alwaysApply: true" "apps/opik-frontend/.cursor/rules/tech-stack.mdc" && grep -qF "const UserCard: React.FC<{ user: User; onEdit: (user: User) => void }> = ({ user" "apps/opik-frontend/.cursor/rules/ui-components.mdc" && grep -qF "When in doubt, write the test. Complex functions should have comprehensive test " "apps/opik-frontend/.cursor/rules/unit-testing.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/apps/opik-frontend/.cursor/rules/accessibility-testing.mdc b/apps/opik-frontend/.cursor/rules/accessibility-testing.mdc
@@ -1,14 +1,15 @@
 ---
 description: Frontend accessibility guidelines and testing patterns
 globs: "**/*"
-alwaysApply: false
+alwaysApply: true
 ---
 
 # Accessibility & Testing Guidelines
 
 ## Accessibility Guidelines
 
 ### Semantic HTML
+
 ```typescript
 // ✅ Use semantic HTML elements
 <header className="comet-header">
@@ -38,6 +39,7 @@ alwaysApply: false
 ```
 
 ### ARIA Labels and Descriptions
+
 ```typescript
 // ✅ Always provide aria-label for icon buttons
 <Button variant="ghost" size="icon" aria-label="Delete item">
@@ -61,7 +63,7 @@ alwaysApply: false
 </div>
 
 // ✅ Use aria-expanded for collapsible content
-<Button 
+<Button
   aria-expanded={isOpen}
   aria-controls="dropdown-menu"
   onClick={() => setIsOpen(!isOpen)}
@@ -74,6 +76,7 @@ alwaysApply: false
 ```
 
 ### Keyboard Navigation
+
 ```typescript
 // ✅ Ensure keyboard navigation works
 const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
@@ -98,6 +101,7 @@ const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
 ```
 
 ### Focus Management
+
 ```typescript
 // ✅ Provide visible focus indicators
 .focus-visible:focus {
@@ -122,23 +126,24 @@ import { FocusTrap } from '@radix-ui/react-focus-trap';
 ```
 
 ### Heading Hierarchy
+
 ```typescript
 // ✅ Use proper heading hierarchy
 <div className="page">
   <h1>Dashboard</h1>
-  
+
   <section>
     <h2>Recent Projects</h2>
-    
+
     <article>
       <h3>Project Name</h3>
       <p>Project description...</p>
     </article>
   </section>
-  
+
   <section>
     <h2>System Status</h2>
-    
+
     <div>
       <h3>Database</h3>
       <p>Status: Online</p>
@@ -152,6 +157,7 @@ import { FocusTrap } from '@radix-ui/react-focus-trap';
 ```
 
 ### Loading States and Error Messages
+
 ```typescript
 // ✅ Include accessible loading states
 {isLoading && (
@@ -177,6 +183,7 @@ import { FocusTrap } from '@radix-ui/react-focus-trap';
 ## Testing Patterns
 
 ### Component Testing with React Testing Library
+
 ```typescript
 import { render, screen, fireEvent, waitFor } from '@testing-library/react';
 import userEvent from '@testing-library/user-event';
@@ -191,27 +198,27 @@ describe('UserProfile', () => {
 
   it('renders user information correctly', () => {
     render(<UserProfile user={mockUser} />);
-    
+
     expect(screen.getByText('John Doe')).toBeInTheDocument();
     expect(screen.getByText('john@example.com')).toBeInTheDocument();
   });
 
   it('allows editing user name', async () => {
     const user = userEvent.setup();
     const onSave = jest.fn();
-    
+
     render(<UserProfile user={mockUser} onSave={onSave} />);
-    
+
     const editButton = screen.getByRole('button', { name: /edit/i });
     await user.click(editButton);
-    
+
     const nameInput = screen.getByLabelText(/name/i);
     await user.clear(nameInput);
     await user.type(nameInput, 'Jane Doe');
-    
+
     const saveButton = screen.getByRole('button', { name: /save/i });
     await user.click(saveButton);
-    
+
     await waitFor(() => {
       expect(onSave).toHaveBeenCalledWith({
         ...mockUser,
@@ -223,58 +230,60 @@ describe('UserProfile', () => {
 ```
 
 ### Custom Hook Testing
+
 ```typescript
-import { renderHook, act } from '@testing-library/react';
-import { useEntityList } from './useEntityList';
+import { renderHook, act } from "@testing-library/react";
+import { useEntityList } from "./useEntityList";
 
-describe('useEntityList', () => {
-  it('fetches entities successfully', async () => {
+describe("useEntityList", () => {
+  it("fetches entities successfully", async () => {
     const mockData = {
-      content: [{ id: '1', name: 'Entity 1' }],
+      content: [{ id: "1", name: "Entity 1" }],
       total: 1,
     };
-    
+
     // Mock API call
     jest.mocked(api.get).mockResolvedValue({ data: mockData });
-    
+
     const { result } = renderHook(() =>
-      useEntityList({ workspaceName: 'test', page: 1, size: 10 })
+      useEntityList({ workspaceName: "test", page: 1, size: 10 }),
     );
-    
+
     await waitFor(() => {
       expect(result.current.isSuccess).toBe(true);
     });
-    
+
     expect(result.current.data).toEqual(mockData);
   });
 });
 ```
 
 ### API Mocking with MSW
+
 ```typescript
 // src/mocks/handlers.ts
-import { rest } from 'msw';
+import { rest } from "msw";
 
 export const handlers = [
-  rest.get('/api/v1/entities', (req, res, ctx) => {
+  rest.get("/api/v1/entities", (req, res, ctx) => {
     return res(
       ctx.json({
         content: [
-          { id: '1', name: 'Entity 1' },
-          { id: '2', name: 'Entity 2' },
+          { id: "1", name: "Entity 1" },
+          { id: "2", name: "Entity 2" },
         ],
         total: 2,
-      })
+      }),
     );
   }),
-  
-  rest.delete('/api/v1/entities/:id', (req, res, ctx) => {
+
+  rest.delete("/api/v1/entities/:id", (req, res, ctx) => {
     return res(ctx.status(204));
   }),
 ];
 
 // In test files
-import { server } from '../mocks/server';
+import { server } from "../mocks/server";
 
 beforeEach(() => {
   server.listen();
@@ -290,6 +299,7 @@ afterAll(() => {
 ```
 
 ### Integration Testing
+
 ```typescript
 import { render, screen, waitFor } from '@testing-library/react';
 import userEvent from '@testing-library/user-event';
@@ -303,7 +313,7 @@ const createWrapper = () => {
       mutations: { retry: false },
     },
   });
-  
+
   return ({ children }: { children: React.ReactNode }) => (
     <QueryClientProvider client={queryClient}>
       {children}
@@ -314,33 +324,33 @@ const createWrapper = () => {
 describe('EntityListPage Integration', () => {
   it('loads and displays entities', async () => {
     render(<EntityListPage />, { wrapper: createWrapper() });
-    
+
     // Wait for loading to complete
     await waitFor(() => {
       expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
     });
-    
+
     // Check if entities are displayed
     expect(screen.getByText('Entity 1')).toBeInTheDocument();
     expect(screen.getByText('Entity 2')).toBeInTheDocument();
   });
-  
+
   it('handles entity deletion flow', async () => {
     const user = userEvent.setup();
     render(<EntityListPage />, { wrapper: createWrapper() });
-    
+
     await waitFor(() => {
       expect(screen.getByText('Entity 1')).toBeInTheDocument();
     });
-    
+
     // Find and click delete button
     const deleteButton = screen.getByRole('button', { name: /delete entity 1/i });
     await user.click(deleteButton);
-    
+
     // Confirm deletion
     const confirmButton = screen.getByRole('button', { name: /confirm/i });
     await user.click(confirmButton);
-    
+
     // Check if entity is removed
     await waitFor(() => {
       expect(screen.queryByText('Entity 1')).not.toBeInTheDocument();
@@ -360,7 +370,7 @@ describe('EntityListPage Integration', () => {
 
 ```typescript
 // ✅ Good: Testing behavior
-expect(screen.getByRole('button', { name: /save/i })).toBeEnabled();
+expect(screen.getByRole("button", { name: /save/i })).toBeEnabled();
 
 // ❌ Avoid: Testing implementation
 expect(component.state.isSaving).toBe(false);
@@ -370,5 +380,5 @@ expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
 
 // ✅ Good: Testing error states
 await user.click(submitButton);
-expect(screen.getByRole('alert')).toHaveTextContent('Email is required');
-```
\ No newline at end of file
+expect(screen.getByRole("alert")).toHaveTextContent("Email is required");
+```
diff --git a/apps/opik-frontend/.cursor/rules/api-data-fetching.mdc b/apps/opik-frontend/.cursor/rules/api-data-fetching.mdc
@@ -1,14 +1,15 @@
 ---
 description: Frontend API and data fetching patterns using React Query
 globs: "**/*"
-alwaysApply: false
+alwaysApply: true
 ---
 
 # API & Data Fetching Patterns
 
 ## React Query Hook Structure
 
 ### Query Hook Template
+
 ```typescript
 // File: src/api/entity/useEntityList.ts
 import { useQuery } from "@tanstack/react-query";
@@ -52,30 +53,35 @@ export default function useEntityList(
 ```
 
 ### Query Key Patterns
+
 - Use descriptive keys: `[ENTITIES_KEY, params]`
 - Include all parameters that affect the query
 - Use constants for query keys defined in `api.ts`
 
 ### Data Processing
+
 ```typescript
 // Simple fallbacks (no useMemo needed)
 const entities = data?.content ?? [];
 const totalItems = data?.total ?? 0;
 
 // Complex transformations (use useMemo)
 const processedEntities = useMemo(() => {
-  return data?.content
-    ?.filter(entity => entity.status === 'active')
-    ?.map(entity => ({
-      ...entity,
-      displayName: formatEntityName(entity),
-    })) ?? [];
+  return (
+    data?.content
+      ?.filter((entity) => entity.status === "active")
+      ?.map((entity) => ({
+        ...entity,
+        displayName: formatEntityName(entity),
+      })) ?? []
+  );
 }, [data?.content]);
 ```
 
 ## Mutation Patterns
 
 ### Basic Mutation
+
 ```typescript
 const mutation = useMutation({
   mutationFn: deleteEntity,
@@ -90,24 +96,26 @@ const mutation = useMutation({
 ```
 
 ### Optimistic Updates
+
 ```typescript
 const updateMutation = useMutation({
   mutationFn: updateEntity,
   onMutate: async (newEntity) => {
     // Cancel outgoing refetches
     await queryClient.cancelQueries({ queryKey: [ENTITIES_KEY] });
-    
+
     // Snapshot previous value
     const previousEntities = queryClient.getQueryData([ENTITIES_KEY]);
-    
+
     // Optimistically update
     queryClient.setQueryData([ENTITIES_KEY], (old) => ({
       ...old,
-      content: old?.content?.map(entity => 
-        entity.id === newEntity.id ? { ...entity, ...newEntity } : entity
-      ) ?? []
+      content:
+        old?.content?.map((entity) =>
+          entity.id === newEntity.id ? { ...entity, ...newEntity } : entity,
+        ) ?? [],
     }));
-    
+
     return { previousEntities };
   },
   onError: (err, newEntity, context) => {
@@ -124,6 +132,7 @@ const updateMutation = useMutation({
 ## Loading and Error States
 
 ### Loading Patterns
+
 ```typescript
 // Query loading
 if (isLoading) return <Loader />;
@@ -140,6 +149,7 @@ if (error) return <div>Error: {error.message}</div>;
 ```
 
 ### Toast Notifications
+
 ```typescript
 import { useToast } from "@/components/ui/use-toast";
 
@@ -148,16 +158,17 @@ const { toast } = useToast();
 // Success toast
 toast({ description: "Operation completed successfully" });
 
-// Error toast  
-toast({ 
-  description: "Operation failed", 
-  variant: "destructive" 
+// Error toast
+toast({
+  description: "Operation failed",
+  variant: "destructive",
 });
 ```
 
 ## API Response Handling
 
 ### Error Boundaries
+
 ```typescript
 // Use React Query's built-in error handling
 const { data, error, isLoading, isError } = useQuery({
@@ -178,17 +189,14 @@ if (isError) {
 ```
 
 ### Pagination Handling
+
 ```typescript
-const {
-  data,
-  fetchNextPage,
-  hasNextPage,
-  isFetchingNextPage,
-} = useInfiniteQuery({
-  queryKey: ['entities'],
-  queryFn: ({ pageParam = 1 }) => fetchEntities({ page: pageParam }),
-  getNextPageParam: (lastPage) => {
-    return lastPage.hasMore ? lastPage.page + 1 : undefined;
-  },
-});
-```
\ No newline at end of file
+const { data, fetchNextPage, hasNextPage, isFetchingNextPage } =
+  useInfiniteQuery({
+    queryKey: ["entities"],
+    queryFn: ({ pageParam = 1 }) => fetchEntities({ page: pageParam }),
+    getNextPageParam: (lastPage) => {
+      return lastPage.hasMore ? lastPage.page + 1 : undefined;
+    },
+  });
+```
diff --git a/apps/opik-frontend/.cursor/rules/code-quality.mdc b/apps/opik-frontend/.cursor/rules/code-quality.mdc
@@ -1,14 +1,15 @@
 ---
 description: Frontend code quality standards, TypeScript patterns, and naming conventions
 globs: "**/*"
-alwaysApply: false
+alwaysApply: true
 ---
 
 # Frontend Code Quality Standards
 
 ## TypeScript Patterns
 
 ### Component Type Definitions
+
 ```typescript
 // ✅ Always define explicit prop interfaces
 interface ComponentProps {
@@ -35,6 +36,7 @@ const Component = ({ title, description, onAction, children }: any) => {
 ```
 
 ### API Response Types
+
 ```typescript
 // ✅ Use strict type checking for API responses
 interface ApiResponse<T> {
@@ -58,45 +60,51 @@ const fetchUser = async (id: string): Promise<ApiResponse<UserData>> => {
 ```
 
 ### Union Types vs Enums
+
 ```typescript
 // ✅ Prefer type unions for simple cases
-type ButtonVariant = 'default' | 'outline' | 'ghost' | 'destructive';
-type Size = 'sm' | 'md' | 'lg';
+type ButtonVariant = "default" | "outline" | "ghost" | "destructive";
+type Size = "sm" | "md" | "lg";
 
 // ✅ Use enums for complex cases with methods
 enum UserRole {
-  ADMIN = 'admin',
-  USER = 'user',
-  GUEST = 'guest',
+  ADMIN = "admin",
+  USER = "user",
+  GUEST = "guest",
 }
 
 // ✅ Const assertions for readonly arrays
-const VALID_STATUSES = ['pending', 'approved', 'rejected'] as const;
-type Status = typeof VALID_STATUSES[number];
+const VALID_STATUSES = ["pending", "approved", "rejected"] as const;
+type Status = (typeof VALID_STATUSES)[number];
 ```
 
 ### Complex Function Types
+
 ```typescript
 // ✅ Always provide return types for complex functions
 const processUserData = (
   users: UserData[],
-  filters: FilterOptions
+  filters: FilterOptions,
 ): ProcessedUserData[] => {
   return users
-    .filter(user => applyFilters(user, filters))
-    .map(user => transformUser(user));
+    .filter((user) => applyFilters(user, filters))
+    .map((user) => transformUser(user));
 };
 
 // ✅ Type event handlers properly
-const handleUserSelect = useCallback((user: UserData, event: React.MouseEvent) => {
-  event.preventDefault();
-  onUserSelect(user.id);
-}, [onUserSelect]);
+const handleUserSelect = useCallback(
+  (user: UserData, event: React.MouseEvent) => {
+    event.preventDefault();
+    onUserSelect(user.id);
+  },
+  [onUserSelect],
+);
 ```
 
 ## Import Organization
 
 ### Import Grouping
+
 ```typescript
 // 1. React and external libraries
 import React, { useState, useCallback, useMemo } from "react";
@@ -117,12 +125,20 @@ import { cn } from "@/lib/utils";
 import { formatDate } from "@/lib/date-utils";
 import useEntityStore from "@/store/EntityStore";
 
-// 5. Types and constants
+// 5. Lodash utilities (grouped together)
+import isString from "lodash/isString";
+import isArray from "lodash/isArray";
+import isEmpty from "lodash/isEmpty";
+import pick from "lodash/pick";
+import groupBy from "lodash/groupBy";
+
+// 6. Types and constants
 import { COLUMN_TYPE, ROW_HEIGHT } from "@/types/shared";
 import { UserData, ApiResponse } from "@/types/api";
 ```
 
 ### Import Best Practices
+
 ```typescript
 // ✅ Use named imports when possible
 import { Button, Input, Select } from "@/components/ui";
@@ -140,40 +156,42 @@ import Button, { ButtonProps } from "@/components/ui/button"; // Confusing
 ## Naming Conventions
 
 ### File and Component Names
+
 ```typescript
 // ✅ Components: PascalCase
-DataTable.tsx
-UserProfile.tsx
-SettingsDialog.tsx
+DataTable.tsx;
+UserProfile.tsx;
+SettingsDialog.tsx;
 
 // ✅ Utilities: camelCase
-dateUtils.ts
-stringHelpers.ts
-apiClient.ts
+dateUtils.ts;
+stringHelpers.ts;
+apiClient.ts;
 
 // ✅ Hooks: camelCase starting with 'use'
-useEntityList.ts
-useUserPermissions.ts
-useDebounce.ts
+useEntityList.ts;
+useUserPermissions.ts;
+useDebounce.ts;
 
 // ✅ Types: PascalCase
-UserData.ts
-ApiResponse.ts
-ComponentProps.ts
+UserData.ts;
+ApiResponse.ts;
+ComponentProps.ts;
 ```
 
 ### Variable and Function Names
+
 ```typescript
 // ✅ Constants: SCREAMING_SNAKE_CASE
 const COLUMN_TYPE = {
-  STRING: 'string',
-  NUMBER: 'number',
-  DATE: 'date',
+  STRING: "string",
+  NUMBER: "number",
+  DATE: "date",
 } as const;
 
 const API_ENDPOINTS = {
-  USERS: '/api/v1/users',
-  PROJECTS: '/api/v1/projects',
+  USERS: "/api/v1/users",
+  PROJECTS: "/api/v1/projects",
 } as const;
 
 // ✅ Event handlers: Descriptive names
@@ -183,25 +201,27 @@ const onModalClose = useCallback(() => {}, []);
 
 // ❌ Avoid: Generic names
 const handleClick = () => {}; // Too vague
-const onSubmit = () => {};    // What is being submitted?
+const onSubmit = () => {}; // What is being submitted?
 ```
 
 ### CSS Classes
+
 ```typescript
 // ✅ Use 'comet-' prefix for custom classes
-className="comet-table-row-active"
-className="comet-sidebar-collapsed"
-className="comet-header-height"
+className = "comet-table-row-active";
+className = "comet-sidebar-collapsed";
+className = "comet-header-height";
 
 // ✅ Use semantic Tailwind classes
-className="flex items-center gap-2"
-className="rounded-lg border bg-card p-6"
-className="text-sm text-muted-foreground"
+className = "flex items-center gap-2";
+className = "rounded-lg border bg-card p-6";
+className = "text-sm text-muted-foreground";
 ```
 
 ## Component Composition
 
 ### Favor Composition over Prop Drilling
+
 ```typescript
 // ✅ Good: Using composition
 interface DialogProps {
@@ -238,12 +258,13 @@ const Dialog: React.FC<{
 ```
 
 ### Custom Hooks for Logic Extraction
+
 ```typescript
 // ✅ Extract common logic into custom hooks
 const useEntityActions = (entityId: string) => {
   const [isDeleting, setIsDeleting] = useState(false);
   const { toast } = useToast();
-  
+
   const deleteEntity = useCallback(async () => {
     setIsDeleting(true);
     try {
@@ -255,20 +276,20 @@ const useEntityActions = (entityId: string) => {
       setIsDeleting(false);
     }
   }, [entityId, toast]);
-  
+
   return { deleteEntity, isDeleting };
 };
 
 // Usage in component
 const EntityCard: React.FC<{ entity: Entity }> = ({ entity }) => {
   const { deleteEntity, isDeleting } = useEntityActions(entity.id);
-  
+
   return (
     <Card>
       <CardContent>{entity.name}</CardContent>
       <CardActions>
-        <Button 
-          variant="destructive" 
+        <Button
+          variant="destructive"
           onClick={deleteEntity}
           disabled={isDeleting}
         >
@@ -280,9 +301,145 @@ const EntityCard: React.FC<{ entity: Entity }> = ({ entity }) => {
 };
 ```
 
+## Utility Libraries
+
+### Lodash Usage Guidelines
+
+Use Lodash for complex operations, but **always import methods individually** for optimal tree-shaking and bundle size:
+
+```typescript
+// ✅ Good: Individual imports for tree-shaking
+import pick from "lodash/pick";
+import merge from "lodash/merge";
+import cloneDeep from "lodash/cloneDeep";
+import uniqBy from "lodash/uniqBy";
+import groupBy from "lodash/groupBy";
+import orderBy from "lodash/orderBy";
+import isNil from "lodash/isNil";
+import isEmpty from "lodash/isEmpty";
+import isEqual from "lodash/isEqual";
+import camelCase from "lodash/camelCase";
+import capitalize from "lodash/capitalize";
+
+// ✅ Object operations
+const user = pick(rawUser, ["id", "name", "email"]);
+const merged = merge({}, defaultConfig, userConfig);
+const deepCloned = cloneDeep(complexObject);
+
+// ✅ Array operations
+const uniqueItems = uniqBy(items, "id");
+const grouped = groupBy(users, "role");
+const sorted = orderBy(data, ["date", "name"], ["desc", "asc"]);
+
+// ✅ Type checking - Use Lodash methods instead of built-in type checks
+import isString from "lodash/isString";
+import isNumber from "lodash/isNumber";
+import isBoolean from "lodash/isBoolean";
+import isObject from "lodash/isObject";
+import isArray from "lodash/isArray";
+import isFunction from "lodash/isFunction";
+import isDate from "lodash/isDate";
+import isRegExp from "lodash/isRegExp";
+import isNull from "lodash/isNull";
+
+// ✅ Prefer Lodash type determination over built-in methods
+if (isString(value)) {
+  /* handle string */
+}
+if (isNumber(value)) {
+  /* handle number */
+}
+if (isBoolean(value)) {
+  /* handle boolean */
+}
+if (isObject(value)) {
+  /* handle object */
+}
+if (isArray(value)) {
+  /* handle array */
+}
+
+// ❌ Avoid: Default import (includes entire library)
+import _ from "lodash"; // Bad for bundle size
+const user = _.pick(rawUser, ["id", "name", "email"]);
+
+// ❌ Avoid: Named imports from main module (still includes more than needed)
+import { pick, merge, cloneDeep } from "lodash"; // Less efficient than individual imports
+
+// ❌ Avoid: Lodash only for very specific simple operations where built-in is clearer
+import has from "lodash/has";
+const hasProperty = has(obj, "prop"); // Use: 'prop' in obj or obj.hasOwnProperty('prop')
+```
+
+## Functionality Isolation Patterns
+
+### Isolating for Future Replacement
+
+When you like the emulation of some functionality, try to isolate it in a way that makes it easy to replace in the future:
+
+```typescript
+// ✅ Good: Isolated date formatting service
+// lib/dateService.ts
+export interface DateService {
+  format(date: Date, format: string): string;
+  parse(dateString: string): Date;
+  isValid(date: any): boolean;
+}
+
+class MomentDateService implements DateService {
+  format(date: Date, format: string): string {
+    return moment(date).format(format);
+  }
+
+  parse(dateString: string): Date {
+    return moment(dateString).toDate();
+  }
+
+  isValid(date: any): boolean {
+    return moment(date).isValid();
+  }
+}
+
+// Export single instance
+export const dateService: DateService = new MomentDateService();
+
+// Usage in components
+import { dateService } from "@/lib/dateService";
+
+const formattedDate = dateService.format(new Date(), "YYYY-MM-DD");
+
+// ✅ Easy to replace later with different implementation:
+// class DayJsDateService implements DateService { ... }
+// export const dateService: DateService = new DayJsDateService();
+```
+
+```typescript
+// ✅ Good: Isolated chart service
+// lib/chartService.ts
+export interface ChartService {
+  createLineChart(data: ChartData[], container: HTMLElement): ChartInstance;
+  updateChart(chart: ChartInstance, data: ChartData[]): void;
+  destroyChart(chart: ChartInstance): void;
+}
+
+class RechartsService implements ChartService {
+  createLineChart(data: ChartData[], container: HTMLElement): ChartInstance {
+    // Recharts implementation
+    return new RechartsInstance(data, container);
+  }
+
+  // ... other methods
+}
+
+export const chartService: ChartService = new RechartsService();
+
+// Easy to replace with D3, Chart.js, etc.
+```
+
 ## Code Formatting
 
 ### Prettier Configuration
+
 ```typescript
 // ✅ Use trailing commas in multiline structures
 const config = {
@@ -293,7 +450,7 @@ const config = {
 
 const items = [
   "item1",
-  "item2", 
+  "item2",
   "item3", // <- trailing comma
 ];
 
@@ -302,47 +459,48 @@ const message = "Hello, world!";
 const template = `User ${userName} has logged in`;
 
 // ✅ Use meaningful variable names
-const filteredActiveUsers = users.filter(user => user.isActive);
+const filteredActiveUsers = users.filter((user) => user.isActive);
 const formattedCreationDate = formatDate(user.createdAt);
 ```
 
 ### Code Organization
+
 ```typescript
 // ✅ Group related functionality
 const UserManagement: React.FC = () => {
   // 1. State declarations
   const [selectedUser, setSelectedUser] = useState<UserData | null>(null);
   const [isDialogOpen, setIsDialogOpen] = useState(false);
-  
+
   // 2. Queries and mutations
   const { data: users, isLoading } = useUserList();
   const deleteMutation = useDeleteUser();
-  
+
   // 3. Memoized values (only when needed)
-  const activeUsers = useMemo(() => 
-    users?.filter(user => user.isActive) ?? [], 
+  const activeUsers = useMemo(() =>
+    users?.filter(user => user.isActive) ?? [],
     [users]
   );
-  
+
   // 4. Event handlers
   const handleUserSelect = useCallback((user: UserData) => {
     setSelectedUser(user);
     setIsDialogOpen(true);
   }, []);
-  
+
   const handleDeleteUser = useCallback(async (userId: string) => {
     await deleteMutation.mutateAsync(userId);
     setIsDialogOpen(false);
   }, [deleteMutation]);
-  
+
   // 5. Early returns
   if (isLoading) return <LoadingSpinner />;
-  
+
   // 6. Main render
   return (
     <div className="space-y-4">
       {/* Component JSX */}
     </div>
   );
 };
-```
\ No newline at end of file
+```
diff --git a/apps/opik-frontend/.cursor/rules/forms.mdc b/apps/opik-frontend/.cursor/rules/forms.mdc
@@ -1,14 +1,15 @@
 ---
 description: Frontend form handling patterns using React Hook Form and Zod
 globs: "**/*"
-alwaysApply: false
+alwaysApply: true
 ---
 
 # Form Handling Patterns
 
 ## React Hook Form + Zod Pattern
 
 ### Basic Form Setup
+
 ```typescript
 import { useForm } from "react-hook-form";
 import { zodResolver } from "@hookform/resolvers/zod";
@@ -40,6 +41,7 @@ const onSubmit = useCallback((data: FormData) => {
 ```
 
 ### Form JSX Structure
+
 ```typescript
 <Form {...form}>
   <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
@@ -56,7 +58,7 @@ const onSubmit = useCallback((data: FormData) => {
         </FormItem>
       )}
     />
-    
+
     <FormField
       control={form.control}
       name="email"
@@ -70,7 +72,7 @@ const onSubmit = useCallback((data: FormData) => {
         </FormItem>
       )}
     />
-    
+
     <Button type="submit" disabled={form.formState.isSubmitting}>
       {form.formState.isSubmitting && <Spinner className="mr-2" />}
       Submit
@@ -82,6 +84,7 @@ const onSubmit = useCallback((data: FormData) => {
 ## Advanced Form Patterns
 
 ### Dynamic Form Fields
+
 ```typescript
 const formSchema = z.object({
   items: z.array(z.object({
@@ -110,43 +113,53 @@ const { fields, append, remove } = useFieldArray({
         </FormItem>
       )}
     />
-    
-    <Button 
-      type="button" 
-      variant="outline" 
+
+    <Button
+      type="button"
+      variant="outline"
       onClick={() => remove(index)}
     >
       Remove
     </Button>
   </div>
 ))}
 
-<Button 
-  type="button" 
+<Button
+  type="button"
   onClick={() => append({ name: "", value: "" })}
 >
   Add Item
 </Button>
 ```
 
 ### Conditional Validation
+
 ```typescript
-const formSchema = z.object({
-  type: z.enum(["user", "admin"]),
-  permissions: z.array(z.string()).optional(),
-}).refine((data) => {
-  // Conditional validation: admin must have permissions
-  if (data.type === "admin" && (!data.permissions || data.permissions.length === 0)) {
-    return false;
-  }
-  return true;
-}, {
-  message: "Admin users must have at least one permission",
-  path: ["permissions"],
-});
+const formSchema = z
+  .object({
+    type: z.enum(["user", "admin"]),
+    permissions: z.array(z.string()).optional(),
+  })
+  .refine(
+    (data) => {
+      // Conditional validation: admin must have permissions
+      if (
+        data.type === "admin" &&
+        (!data.permissions || data.permissions.length === 0)
+      ) {
+        return false;
+      }
+      return true;
+    },
+    {
+      message: "Admin users must have at least one permission",
+      path: ["permissions"],
+    },
+  );
 ```
 
 ### Custom Field Components
+
 ```typescript
 // Custom field wrapper
 interface CustomFieldProps {
@@ -165,7 +178,7 @@ const CustomField: React.FC<CustomFieldProps> = ({
   children,
 }) => {
   const form = useFormContext();
-  
+
   return (
     <FormField
       control={form.control}
@@ -202,23 +215,24 @@ const CustomField: React.FC<CustomFieldProps> = ({
 ## Form State Management
 
 ### Loading and Error States
+
 ```typescript
 const [isSubmitting, setIsSubmitting] = useState(false);
 const [submitError, setSubmitError] = useState<string | null>(null);
 
 const onSubmit = useCallback(async (data: FormData) => {
   setIsSubmitting(true);
   setSubmitError(null);
-  
+
   try {
     await submitForm(data);
     toast({ description: "Form submitted successfully!" });
     form.reset();
   } catch (error) {
     setSubmitError(error.message);
-    toast({ 
-      description: "Failed to submit form", 
-      variant: "destructive" 
+    toast({
+      description: "Failed to submit form",
+      variant: "destructive"
     });
   } finally {
     setIsSubmitting(false);
@@ -239,16 +253,20 @@ const onSubmit = useCallback(async (data: FormData) => {
 ```
 
 ### Form Reset and Default Values
+
 ```typescript
 // Reset form to default values
 const handleReset = useCallback(() => {
   form.reset();
 }, [form]);
 
 // Reset with new default values
-const handleResetWithData = useCallback((newData: Partial<FormData>) => {
-  form.reset(newData);
-}, [form]);
+const handleResetWithData = useCallback(
+  (newData: Partial<FormData>) => {
+    form.reset(newData);
+  },
+  [form],
+);
 
 // Watch for changes
 const watchedValues = form.watch();
@@ -263,24 +281,35 @@ useEffect(() => {
 ## Validation Patterns
 
 ### Custom Validators
+
 ```typescript
-const phoneSchema = z.string().refine((val) => {
-  const phoneRegex = /^\+?[1-9]\d{1,14}$/;
-  return phoneRegex.test(val);
-}, {
-  message: "Invalid phone number format",
-});
+const phoneSchema = z.string().refine(
+  (val) => {
+    const phoneRegex = /^\+?[1-9]\d{1,14}$/;
+    return phoneRegex.test(val);
+  },
+  {
+    message: "Invalid phone number format",
+  },
+);
 
 // Async validation
-const emailSchema = z.string().email().refine(async (email) => {
-  const isAvailable = await checkEmailAvailability(email);
-  return isAvailable;
-}, {
-  message: "Email is already taken",
-});
+const emailSchema = z
+  .string()
+  .email()
+  .refine(
+    async (email) => {
+      const isAvailable = await checkEmailAvailability(email);
+      return isAvailable;
+    },
+    {
+      message: "Email is already taken",
+    },
+  );
 ```
 
 ### Multi-step Forms
+
 ```typescript
 const steps = [
   { name: "Personal Info", schema: personalInfoSchema },
@@ -299,11 +328,11 @@ const form = useForm({
 const handleNext = useCallback(async () => {
   const isValid = await form.trigger();
   if (isValid) {
-    setCurrentStep(prev => Math.min(prev + 1, steps.length - 1));
+    setCurrentStep((prev) => Math.min(prev + 1, steps.length - 1));
   }
 }, [form]);
 
 const handlePrevious = useCallback(() => {
-  setCurrentStep(prev => Math.max(prev - 1, 0));
+  setCurrentStep((prev) => Math.max(prev - 1, 0));
 }, []);
-```
\ No newline at end of file
+```
diff --git a/apps/opik-frontend/.cursor/rules/performance.mdc b/apps/opik-frontend/.cursor/rules/performance.mdc
@@ -1,14 +1,15 @@
 ---
 description: Frontend performance optimization rules for React hooks and data processing
 globs: "**/*"
-alwaysApply: false
+alwaysApply: true
 ---
 
 # Frontend Performance Guidelines
 
 ## Selective useMemo Usage
 
 **Use useMemo ONLY for:**
+
 - Complex computations that are expensive to recalculate
 - Data transformations with multiple operations or iterations
 - Large array filtering/sorting operations
@@ -18,9 +19,9 @@ alwaysApply: false
 // ✅ Good: Complex computation
 const expensiveValue = useMemo(() => {
   return largeDataSet
-    .filter(item => item.category === selectedCategory)
+    .filter((item) => item.category === selectedCategory)
     .sort((a, b) => a.date.localeCompare(b.date))
-    .map(item => transformItem(item));
+    .map((item) => transformItem(item));
 }, [largeDataSet, selectedCategory]);
 
 // ✅ Good: API data transformation for child components
@@ -36,17 +37,21 @@ const isVisible = useMemo(() => showModal, [showModal]); // Unnecessary
 ## Selective useCallback Usage
 
 **Use useCallback ONLY for:**
+
 - Functions passed as props to child components
 - Functions used in useEffect dependencies
 - Event handlers in frequently re-rendering components
 - Functions that have complex logic or closures
 
 ```typescript
 // ✅ Good: Function passed to child component
-const handleItemSelect = useCallback((id: string) => {
-  setSelectedItem(id);
-  onSelectionChange?.(id);
-}, [onSelectionChange]);
+const handleItemSelect = useCallback(
+  (id: string) => {
+    setSelectedItem(id);
+    onSelectionChange?.(id);
+  },
+  [onSelectionChange],
+);
 
 // ✅ Good: Function used in effect dependency
 const fetchData = useCallback(async () => {
@@ -68,16 +73,19 @@ const processValue = useCallback((value) => value.toUpperCase(), []); // Unneces
 ## Data Processing Patterns
 
 ### API Response Handling
+
 ```typescript
 // ✅ For complex transformations
 const processedItems = useMemo(() => {
-  return data?.content
-    ?.filter(item => item.status === 'active')
-    ?.map(item => ({
-      ...item,
-      displayName: `${item.firstName} ${item.lastName}`,
-      formattedDate: formatDate(item.createdAt)
-    })) ?? [];
+  return (
+    data?.content
+      ?.filter((item) => item.status === "active")
+      ?.map((item) => ({
+        ...item,
+        displayName: `${item.firstName} ${item.lastName}`,
+        formattedDate: formatDate(item.createdAt),
+      })) ?? []
+  );
 }, [data?.content]);
 
 // ✅ For simple fallbacks
@@ -86,6 +94,7 @@ const totalCount = data?.total ?? 0; // No useMemo needed
 ```
 
 ### Column Definitions
+
 ```typescript
 // ✅ Memoize complex column definitions
 const columns: ColumnDef<DataType>[] = useMemo(() => [
@@ -131,4 +140,4 @@ const handleAction = useCallback(() => doSomething(), []);
 - Simple primitive values or direct property access
 - Functions that are only called locally within the component
 - Values that change on every render anyway
-- Simple object/array literals that don't impact child components
\ No newline at end of file
+- Simple object/array literals that don't impact child components
diff --git a/apps/opik-frontend/.cursor/rules/state-management.mdc b/apps/opik-frontend/.cursor/rules/state-management.mdc
@@ -1,14 +1,15 @@
 ---
 description: Frontend state management patterns using Zustand and local storage
 globs: "**/*"
-alwaysApply: false
+alwaysApply: true
 ---
 
 # State Management Patterns
 
 ## Zustand Store Pattern
 
 ### Store Structure
+
 ```typescript
 // File: src/store/EntityStore.ts
 import { create } from "zustand";
@@ -30,19 +31,18 @@ const useEntityStore = create<EntityStore>((set) => ({
   // State
   selectedEntity: null,
   filters: defaultFilters,
-  
+
   // Actions
   setSelectedEntity: (entity) => set({ selectedEntity: entity }),
-  updateFilters: (newFilters) => 
+  updateFilters: (newFilters) =>
     set((state) => ({ filters: { ...state.filters, ...newFilters } })),
   resetFilters: () => set({ filters: defaultFilters }),
 }));
 
 // Exported selectors
-export const useSelectedEntity = () => 
+export const useSelectedEntity = () =>
   useEntityStore((state) => state.selectedEntity);
-export const useEntityFilters = () => 
-  useEntityStore((state) => state.filters);
+export const useEntityFilters = () => useEntityStore((state) => state.filters);
 
 export default useEntityStore;
 ```
@@ -66,6 +66,7 @@ const { selectedEntity, filters } = useEntityStore();
 ## Local Storage Integration
 
 ### Using use-local-storage-state
+
 ```typescript
 // Use use-local-storage-state for persistence
 import useLocalStorageState from "use-local-storage-state";
@@ -79,16 +80,20 @@ const [preferences, setPreferences] = useLocalStorageState("userPreferences", {
 });
 
 // Update specific preference
-const updatePreference = useCallback((key: string, value: any) => {
-  setPreferences(prev => ({ ...prev, [key]: value }));
-}, [setPreferences]);
+const updatePreference = useCallback(
+  (key: string, value: any) => {
+    setPreferences((prev) => ({ ...prev, [key]: value }));
+  },
+  [setPreferences],
+);
 ```
 
 ### Local Storage Patterns
+
 ```typescript
 // ✅ Good: Type-safe local storage
 interface UserPreferences {
-  theme: 'light' | 'dark';
+  theme: "light" | "dark";
   sidebarCollapsed: boolean;
   tablePageSize: number;
 }
@@ -101,7 +106,7 @@ const [preferences, setPreferences] = useLocalStorageState<UserPreferences>(
       sidebarCollapsed: false,
       tablePageSize: 10,
     },
-  }
+  },
 );
 
 // ❌ Avoid: Untyped local storage
@@ -113,6 +118,7 @@ const [prefs, setPrefs] = useLocalStorageState("prefs", {
 ## State Composition Patterns
 
 ### Combining Multiple Stores
+
 ```typescript
 // Use multiple focused stores instead of one large store
 const useUIStore = create<UIState>((set) => ({
@@ -131,12 +137,13 @@ const useDataStore = create<DataState>((set) => ({
 const Component = () => {
   const sidebarOpen = useUIStore((state) => state.sidebarOpen);
   const entities = useDataStore((state) => state.entities);
-  
+
   return <div>{/* Component JSX */}</div>;
 };
 ```
 
 ### Context for Component Trees
+
 ```typescript
 // Use context sparingly, prefer prop passing
 interface ComponentContextValue {
@@ -166,34 +173,36 @@ const useComponentContext = () => {
 ## State Synchronization
 
 ### Syncing with URL State
+
 ```typescript
 import { useNavigate, useSearch } from "@tanstack/react-router";
 
 const EntityListPage = () => {
   const navigate = useNavigate();
   const { page, search, sortBy } = useSearch({ strict: false });
-  
+
   const updateUrl = useCallback((updates: Partial<SearchParams>) => {
     navigate({
       search: (prev) => ({ ...prev, ...updates }),
     });
   }, [navigate]);
-  
+
   const handlePageChange = useCallback((newPage: number) => {
     updateUrl({ page: newPage });
   }, [updateUrl]);
-  
+
   return <div>{/* Component JSX */}</div>;
 };
 ```
 
 ### Syncing Stores with Server State
+
 ```typescript
 // Sync Zustand store with React Query data
 const useEntitySync = () => {
   const setEntities = useEntityStore((state) => state.setEntities);
   const { data } = useEntityList();
-  
+
   useEffect(() => {
     if (data?.content) {
       setEntities(data.content);
@@ -210,16 +219,19 @@ const useEntitySync = () => {
 
 ```typescript
 // ✅ Good: Shallow comparison for objects
-import { shallow } from 'zustand/shallow';
+import { shallow } from "zustand/shallow";
 
 const { filters, selectedEntity } = useEntityStore(
   (state) => ({ filters: state.filters, selectedEntity: state.selectedEntity }),
-  shallow
+  shallow,
 );
 
 // ✅ Good: Memoized actions
-const actions = useMemo(() => ({
-  updateFilters: useEntityStore.getState().updateFilters,
-  resetFilters: useEntityStore.getState().resetFilters,
-}), []);
-```
\ No newline at end of file
+const actions = useMemo(
+  () => ({
+    updateFilters: useEntityStore.getState().updateFilters,
+    resetFilters: useEntityStore.getState().resetFilters,
+  }),
+  [],
+);
+```
diff --git a/apps/opik-frontend/.cursor/rules/tech-stack.mdc b/apps/opik-frontend/.cursor/rules/tech-stack.mdc
@@ -1,12 +1,13 @@
 ---
 description: Frontend technology stack and project structure guidelines
 globs: "**/*"
-alwaysApply: false
+alwaysApply: true
 ---
 
 # Frontend Technology Stack & Architecture
 
 ## Core Technologies
+
 - **React 18** with **TypeScript**
 - **Vite** as build tool and dev server
 - **TanStack Router** for routing
@@ -20,6 +21,7 @@ alwaysApply: false
 - **Lodash** for utility functions
 
 ## Project Structure
+
 ```
 src/
 ├── api/                    # API layer with React Query hooks
@@ -38,6 +40,7 @@ src/
 ```
 
 ## Component Structure Pattern
+
 ```typescript
 // Standard component structure
 import React, { useMemo, useCallback } from "react";
@@ -56,7 +59,7 @@ const Component: React.FunctionComponent<ComponentProps> = ({
   // 2. useMemo for expensive computations (only when needed)
   // 3. useCallback for event handlers (only when passed to children)
   // 4. Other hooks
-  
+
   return (
     <div className="component-container">
       {/* JSX */}
@@ -65,4 +68,4 @@ const Component: React.FunctionComponent<ComponentProps> = ({
 };
 
 export default Component;
-```
\ No newline at end of file
+```
diff --git a/apps/opik-frontend/.cursor/rules/ui-components.mdc b/apps/opik-frontend/.cursor/rules/ui-components.mdc
@@ -1,21 +1,23 @@
 ---
 description: Frontend UI component patterns and design system guidelines
 globs: "**/*"
-alwaysApply: false
+alwaysApply: true
 ---
 
 # UI Components & Design System
 
 ## Button Component Patterns
 
 ### Button Variants
+
 Use the established button variant system:
+
 ```typescript
 // Primary actions
 <Button variant="default">Save</Button>
 <Button variant="special">Special Action</Button>
 
-// Secondary actions  
+// Secondary actions
 <Button variant="secondary">Cancel</Button>
 <Button variant="outline">Edit</Button>
 
@@ -32,15 +34,17 @@ Use the established button variant system:
 ```
 
 ### Size Variants
+
 ```typescript
 // Button sizes
-size="3xs" | "2xs" | "sm" | "default" | "lg"
-size="icon-3xs" | "icon-2xs" | "icon-xs" | "icon-sm" | "icon" | "icon-lg"
+size = "3xs" | "2xs" | "sm" | "default" | "lg";
+size = "icon-3xs" | "icon-2xs" | "icon-xs" | "icon-sm" | "icon" | "icon-lg";
 ```
 
 ## Data Table Patterns
 
 ### DataTable Component Usage
+
 ```typescript
 const columns: ColumnDef<DataType>[] = useMemo(() => [
   {
@@ -58,7 +62,7 @@ const columns: ColumnDef<DataType>[] = useMemo(() => [
 const rows = data?.content ?? []; // Simple fallback, no useMemo needed
 
 // Always use DataTable wrapper
-<DataTable 
+<DataTable
   columns={columns}
   data={rows}
   rowHeight={ROW_HEIGHT.medium}
@@ -67,7 +71,9 @@ const rows = data?.content ?? []; // Simple fallback, no useMemo needed
 ```
 
 ### Column Types
+
 Use predefined column types:
+
 - `COLUMN_TYPE.string` - Text data
 - `COLUMN_TYPE.number` - Numeric data
 - `COLUMN_TYPE.time` - Date/time data
@@ -79,7 +85,9 @@ Use predefined column types:
 - `COLUMN_TYPE.category` - Category/tag data
 
 ## Color System
+
 Always use CSS custom properties:
+
 ```css
 /* Primary colors */
 bg-primary text-primary-foreground
@@ -101,7 +109,9 @@ bg-background bg-primary-foreground bg-popover
 ```
 
 ## Typography Classes
+
 Use custom typography classes:
+
 ```css
 /* Titles */
 .comet-title-xl    /* 3xl font-medium */
@@ -123,6 +133,7 @@ Use custom typography classes:
 ```
 
 ## Layout Classes
+
 ```css
 .comet-header-height      /* 64px header */
 .comet-sidebar-width      /* sidebar width */
@@ -132,11 +143,12 @@ Use custom typography classes:
 ```
 
 ## Container Patterns
+
 ```typescript
 // Page containers
 <div className="size-full overflow-auto p-6">
 
-// Card containers  
+// Card containers
 <div className="rounded-lg border bg-card p-6">
 
 // Form containers
@@ -150,6 +162,7 @@ Use custom typography classes:
 ```
 
 ## State Classes
+
 ```typescript
 // Loading states
 <Skeleton className="h-4 w-full" />
@@ -164,8 +177,135 @@ className={cn("border", { "border-destructive": hasError })}
 "disabled:opacity-50 disabled:pointer-events-none"
 ```
 
+## Component Reusability and Organization
+
+### UI Logic Separation
+
+Try not to write complex UI logic inside components. Follow these principles:
+
+```typescript
+// ✅ Good: Extract reusable logic into separate component
+// components/shared/UserCard/UserCard.tsx
+const UserCard: React.FC<{ user: User; onEdit: (user: User) => void }> = ({ user, onEdit }) => {
+  return (
+    <Card className="p-4">
+      <div className="flex items-center gap-3">
+        <Avatar src={user.avatar} />
+        <div>
+          <h3 className="comet-title-s">{user.name}</h3>
+          <p className="comet-body-s text-muted-foreground">{user.email}</p>
+        </div>
+      </div>
+      <Button variant="outline" onClick={() => onEdit(user)}>
+        Edit
+      </Button>
+    </Card>
+  );
+};
+
+// ❌ Avoid: Complex inline UI logic
+const UserList: React.FC = () => {
+  return (
+    <div>
+      {users.map(user => (
+        <div key={user.id} className="p-4 border rounded">
+          <div className="flex items-center gap-3">
+            <img src={user.avatar} className="w-10 h-10 rounded-full" />
+            <div>
+              <h3>{user.name}</h3>
+              <p>{user.email}</p>
+            </div>
+          </div>
+          <button onClick={() => /* complex edit logic */}>Edit</button>
+        </div>
+      ))}
+    </div>
+  );
+};
+```
+
+### Component Placement Rules
+
+- **Reusable components**: Place in `components/shared/` folder
+- **Non-reusable components**: Place in the same folder as the parent component
+
+Check these folders when adding new components:
+
+- `apps/opik-frontend/src/components/ui` for low-level components
+- `apps/opik-frontend/src/components/shared` for high-level components
+
+```
+components/
+├── ui/                     # Low-level base components (Button, Input, etc.)
+├── shared/
+│   ├── UserCard/          # Reusable across multiple pages
+│   ├── DataTable/         # Reusable table component
+│   └── LoadingSpinner/    # Reusable loading component
+└── pages/
+    └── UserManagement/
+        ├── UserManagement.tsx
+        ├── UserFilters.tsx    # Only used in UserManagement
+        └── UserActions.tsx    # Only used in UserManagement
+```
+
+## Dark Theme Support
+
+### Theme-Aware Components
+
+When adding a new UI component, remember it should support both light and dark themes:
+
+```typescript
+// ✅ Good: Use theme-aware classes
+const MyComponent: React.FC = () => (
+  <div className="bg-card text-card-foreground border border-border">
+    <h2 className="text-primary">Title</h2>
+    <p className="text-muted-foreground">Description</p>
+    <Button className="bg-primary text-primary-foreground hover:bg-primary-hover">
+      Action
+    </Button>
+  </div>
+);
+
+// ❌ Avoid: Hard-coded colors
+const MyComponent: React.FC = () => (
+  <div className="bg-white text-black border-gray-200">
+    <h2 className="text-blue-600">Title</h2>
+    <p className="text-gray-500">Description</p>
+  </div>
+);
+```
+
+### Color Management
+
+Add all new colors to the `main.css` file, along with their alternatives for the dark theme:
+
+```css
+/* main.css */
+:root {
+  /* Light theme colors */
+  --my-custom-color: 210 100% 50%;
+  --my-custom-color-foreground: 0 0% 100%;
+}
+
+.dark {
+  /* Dark theme alternatives */
+  --my-custom-color: 220 100% 60%;
+  --my-custom-color-foreground: 0 0% 0%;
+}
+```
+
+Then use in components:
+
+```typescript
+// ✅ Good: Using CSS custom properties
+<div className="bg-my-custom-color text-my-custom-color-foreground">
+  Content
+</div>
+```
+
 ## Spacing Guidelines
+
 - Use consistent spacing: `gap-2`, `gap-4`, `gap-6`, `gap-8`
 - Use consistent padding: `p-2`, `p-4`, `p-6`, `px-4`, `py-2`
 - Use consistent margins: `mb-4`, `mt-6`, `mx-2`
-- Border radius: `rounded-md` (default), `rounded-lg`, `rounded-xl`
\ No newline at end of file
+- Border radius: `rounded-md` (default), `rounded-lg`, `rounded-xl`
diff --git a/apps/opik-frontend/.cursor/rules/unit-testing.mdc b/apps/opik-frontend/.cursor/rules/unit-testing.mdc
@@ -1,20 +1,22 @@
 ---
 description: Unit testing guidelines and patterns for complex cases using Vitest
 globs: "**/*"
-alwaysApply: false
+alwaysApply: true
 ---
 
 # Unit Testing Guidelines
 
 ## Testing Framework Setup
 
 ### Core Technologies
+
 - **Vitest** - Testing framework (fast, ESM-first)
 - **@testing-library/react** - React component testing
 - **@testing-library/jest-dom** - Additional DOM matchers
 - **happy-dom** - Lightweight DOM environment
 
 ### Test File Organization
+
 ```
 src/
 ├── lib/
@@ -34,19 +36,22 @@ src/
 ## When to Write Unit Tests
 
 ### **ALWAYS** Test Complex Cases:
+
 1. **Utility Functions** with multiple scenarios
-2. **Data Processing Logic** with edge cases  
+2. **Data Processing Logic** with edge cases
 3. **Parsing/Transformation Functions** with various inputs
 4. **Filter/Search Logic** with complex conditions
 5. **Business Logic** with multiple branches
 
 ### **Consider** Testing:
+
 - Custom hooks with complex state logic
 - Components with significant conditional rendering
 - API response transformations
 - Validation functions
 
 ### **Don't** Test:
+
 - Simple UI components without logic
 - Third-party library integrations
 - Trivial getters/setters
@@ -113,8 +118,12 @@ function hello() {
   describe("false positives", () => {
     it("should not identify regular text as markdown", () => {
       expect(isStringMarkdown("This is just regular text.")).toBe(false);
-      expect(isStringMarkdown("This contains an asterisk * but is not markdown.")).toBe(false);
-      expect(isStringMarkdown("This contains a hash # but is not markdown.")).toBe(false);
+      expect(
+        isStringMarkdown("This contains an asterisk * but is not markdown."),
+      ).toBe(false);
+      expect(
+        isStringMarkdown("This contains a hash # but is not markdown."),
+      ).toBe(false);
     });
   });
 });
@@ -140,7 +149,7 @@ describe("parsePythonMethodParameters", () => {
       expect(result).toEqual([
         { name: "a", type: "any", optional: false },
         { name: "b", type: "any", optional: false },
-        { name: "c", type: "any", optional: false }
+        { name: "c", type: "any", optional: false },
       ]);
     });
   });
@@ -151,15 +160,15 @@ describe("parsePythonMethodParameters", () => {
       const result = parsePythonMethodParameters(code, "typed_method");
       expect(result).toEqual([
         { name: "a", type: "int", optional: false },
-        { name: "b", type: "str", optional: false }
+        { name: "b", type: "str", optional: false },
       ]);
     });
 
     it("should handle complex types", () => {
       const code = "def complex_method(data: Dict[str, List[int]]):";
       const result = parsePythonMethodParameters(code, "complex_method");
       expect(result).toEqual([
-        { name: "data", type: "Dict[str, List[int]]", optional: false }
+        { name: "data", type: "Dict[str, List[int]]", optional: false },
       ]);
     });
   });
@@ -170,7 +179,7 @@ describe("parsePythonMethodParameters", () => {
       const result = parsePythonMethodParameters(code, "method");
       expect(result).toEqual([
         { name: "input", type: "str", optional: false },
-        { name: "count", type: "int", optional: true }
+        { name: "count", type: "int", optional: true },
       ]);
     });
   });
@@ -179,15 +188,14 @@ describe("parsePythonMethodParameters", () => {
     it("should ignore self parameter", () => {
       const code = "def score(self, input: str):";
       const result = parsePythonMethodParameters(code, "score");
-      expect(result).toEqual([
-        { name: "input", type: "str", optional: false }
-      ]);
+      expect(result).toEqual([{ name: "input", type: "str", optional: false }]);
     });
 
     it("should throw when method not found", () => {
       const code = "def other_method():";
-      expect(() => parsePythonMethodParameters(code, "missing_method"))
-        .toThrowError("Method missing_method not found");
+      expect(() =>
+        parsePythonMethodParameters(code, "missing_method"),
+      ).toThrowError("Method missing_method not found");
     });
   });
 });
@@ -207,70 +215,82 @@ describe("filterFunction", () => {
     type: "llm",
     createdAt: "2024-01-01T00:00:00Z",
     tags: ["tag1", "tag2"],
-    metrics: { cost: 0.05, tokens: 100 }
+    metrics: { cost: 0.05, tokens: 100 },
   };
 
   describe("string column filtering", () => {
     it("should filter with equals operator", () => {
-      const filter = [{
-        field: "name",
-        operator: "=",
-        value: "Test Item",
-        type: COLUMN_TYPE.string
-      }];
+      const filter = [
+        {
+          field: "name",
+          operator: "=",
+          value: "Test Item",
+          type: COLUMN_TYPE.string,
+        },
+      ];
 
       expect(filterFunction(mockData, filter)).toBe(true);
     });
 
     it("should filter with contains operator", () => {
-      const filter = [{
-        field: "name", 
-        operator: "contains",
-        value: "Test",
-        type: COLUMN_TYPE.string
-      }];
+      const filter = [
+        {
+          field: "name",
+          operator: "contains",
+          value: "Test",
+          type: COLUMN_TYPE.string,
+        },
+      ];
 
       expect(filterFunction(mockData, filter)).toBe(true);
     });
 
     it("should handle case sensitivity", () => {
-      const filter = [{
-        field: "name",
-        operator: "contains", 
-        value: "test",
-        type: COLUMN_TYPE.string
-      }];
+      const filter = [
+        {
+          field: "name",
+          operator: "contains",
+          value: "test",
+          type: COLUMN_TYPE.string,
+        },
+      ];
 
       expect(filterFunction(mockData, filter)).toBe(true); // Case insensitive
     });
   });
 
   describe("category column filtering", () => {
     it("should filter categories with equals", () => {
-      const filter = [{
-        field: "type",
-        operator: "=",
-        value: "llm", 
-        type: COLUMN_TYPE.category
-      }];
+      const filter = [
+        {
+          field: "type",
+          operator: "=",
+          value: "llm",
+          type: COLUMN_TYPE.category,
+        },
+      ];
 
       expect(filterFunction(mockData, filter)).toBe(true);
     });
 
     it("should handle empty/not empty operators", () => {
-      const isEmptyFilter = [{
-        field: "type",
-        operator: "is_empty",
-        value: "",
-        type: COLUMN_TYPE.category
-      }];
-
-      const isNotEmptyFilter = [{
-        field: "type", 
-        operator: "is_not_empty",
-        value: "",
-        type: COLUMN_TYPE.category
-      }];
+      const isEmptyFilter = [
+        {
+          field: "type",
+          operator: "is_empty",
+          value: "",
+          type: COLUMN_TYPE.category,
+        },
+      ];
+
+      const isNotEmptyFilter = [
+        {
+          field: "type",
+          operator: "is_not_empty",
+          value: "",
+          type: COLUMN_TYPE.category,
+        },
+      ];
 
       expect(filterFunction(mockData, isEmptyFilter)).toBe(false);
       expect(filterFunction(mockData, isNotEmptyFilter)).toBe(true);
@@ -284,14 +304,14 @@ describe("filterFunction", () => {
           field: "name",
           operator: "contains",
           value: "Test",
-          type: COLUMN_TYPE.string
+          type: COLUMN_TYPE.string,
         },
         {
           field: "type",
-          operator: "=", 
+          operator: "=",
           value: "llm",
-          type: COLUMN_TYPE.category
-        }
+          type: COLUMN_TYPE.category,
+        },
       ];
 
       expect(filterFunction(mockData, filters)).toBe(true);
@@ -303,14 +323,14 @@ describe("filterFunction", () => {
           field: "name",
           operator: "=",
           value: "Test Item",
-          type: COLUMN_TYPE.string
+          type: COLUMN_TYPE.string,
         },
         {
           field: "type",
           operator: "=",
           value: "embedding", // Wrong type
-          type: COLUMN_TYPE.category
-        }
+          type: COLUMN_TYPE.category,
+        },
       ];
 
       expect(filterFunction(mockData, filters)).toBe(false);
@@ -322,13 +342,16 @@ describe("filterFunction", () => {
 ## Testing Best Practices
 
 ### Test Structure (AAA Pattern)
+
 ```typescript
 describe("ComponentName", () => {
   describe("feature group", () => {
     it("should do something when condition", () => {
       // Arrange - Set up test data
       const input = createTestData();
-      const expectedOutput = { /* expected result */ };
+      const expectedOutput = {
+        /* expected result */
+      };
 
       // Act - Execute the function
       const result = functionUnderTest(input);
@@ -341,12 +364,15 @@ describe("ComponentName", () => {
 ```
 
 ### Test Naming Conventions
+
 - **Describe blocks**: Use feature names or function names
 - **Test names**: Use "should [behavior] when [condition]" or just "[behavior]" for simple cases
 - **Be descriptive**: Names should clearly indicate what's being tested
 
 ### Edge Case Testing
+
 Always test these scenarios for complex functions:
+
 ```typescript
 describe("edge cases", () => {
   it("should handle empty input", () => {
@@ -359,7 +385,9 @@ describe("edge cases", () => {
   });
 
   it("should handle large datasets", () => {
-    const largeArray = Array(1000).fill().map((_, i) => ({ id: i }));
+    const largeArray = Array(1000)
+      .fill()
+      .map((_, i) => ({ id: i }));
     const result = processData(largeArray);
     expect(result).toHaveLength(1000);
   });
@@ -372,6 +400,7 @@ describe("edge cases", () => {
 ```
 
 ### Mock Data Generation
+
 ```typescript
 // Create realistic test data
 const createMockUser = (overrides = {}) => ({
@@ -380,7 +409,7 @@ const createMockUser = (overrides = {}) => ({
   email: "john@example.com",
   role: "admin",
   createdAt: "2024-01-01T00:00:00Z",
-  ...overrides
+  ...overrides,
 });
 
 // Use in tests
@@ -392,12 +421,13 @@ it("should process user data", () => {
 ```
 
 ### Testing Utilities and Helpers
+
 For utilities in `src/lib/`, always include comprehensive tests:
 
 ```typescript
 // Test all public functions
 // Test all code paths
-// Test error conditions 
+// Test error conditions
 // Test performance for large inputs
 // Document complex test cases with comments
 ```
@@ -426,4 +456,4 @@ npm test -- --coverage
 4. **Group related tests** - Use describe blocks for organization
 5. **Clean up after tests** - Reset mocks, clear state
 
-When in doubt, write the test. Complex functions should have comprehensive test coverage to prevent regressions and ensure reliability.
\ No newline at end of file
+When in doubt, write the test. Complex functions should have comprehensive test coverage to prevent regressions and ensure reliability.
PATCH

echo "Gold patch applied."
