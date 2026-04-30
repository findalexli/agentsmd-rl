#!/usr/bin/env bash
set -euo pipefail

cd /workspace/growthbook

# Idempotency guard
if grep -qF "- If creating a new controller and router, use the pattern of putting the router" ".cursor/rules/backend/api-patterns.md" && grep -qF "Note: Permission checks, migrations, etc. are all done automatically within the " ".cursor/rules/backend/model-patterns.md" && grep -qF "- Only declare types/interfaces from scratch when there is no Zod schema. When t" ".cursor/rules/development-guidelines.md" && grep -qF "GrowthBook uses SWR for data fetching with a custom `useApi()` hook, and `apiCal" ".cursor/rules/frontend/data-fetching.md" && grep -qF "Available design system components: Avatar, Badge, Button, Callout, Checkbox, Co" ".cursor/rules/frontend/react-patterns.md" && grep -qF "- Affected components: Avatar, Badge, Button, Callout, Checkbox, DataList, Dropd" ".cursor/rules/package-boundaries.md" && grep -qF "GrowthBook uses a three-tier permission system with Global, Project-scoped, and " ".cursor/rules/permissions.md" && grep -qF "1. **Internal API** - Used by the GrowthBook front-end application (controllers," ".cursor/rules/project-overview.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/backend/api-patterns.md b/.cursor/rules/backend/api-patterns.md
@@ -0,0 +1,163 @@
+---
+description: "Backend API patterns for both internal and external APIs"
+globs: ["packages/back-end/src/**/*.ts"]
+alwaysApply: false
+---
+
+# Backend API Patterns
+
+The back-end serves **two distinct types of APIs** with different patterns and purposes:
+
+1. **Internal API** - Used by the GrowthBook front-end application
+2. **External REST API** - Public API for customers to integrate with GrowthBook
+
+## Internal API (Front-end Application)
+
+The internal API powers the GrowthBook web application and uses a traditional controller/router pattern.
+
+### Location & Structure
+
+- Controllers: `packages/back-end/src/controllers/`
+- Routers: `packages/back-end/src/routers/`
+- Mounted in: `packages/back-end/src/app.ts`
+
+### Controller Pattern
+
+- Controllers export named functions that are HTTP handlers
+- Wrap controllers with `wrapController()` for automatic error handling
+- Controllers handle authentication via session cookies
+- Return data directly in responses
+
+**Example:**
+
+```typescript
+// In controllers/myController.ts
+export const getMyResource = async (req: AuthRequest, res: Response) => {
+  const { org } = getContextFromReq(req);
+  const data = await getResourceData(org.id);
+  res.status(200).json({ data });
+};
+
+// In app.ts or a router
+import * as myControllerRaw from "./controllers/myController";
+const myController = wrapController(myControllerRaw);
+
+app.get("/api/my-resource", myController.getMyResource);
+```
+
+### Router Pattern (Internal)
+
+- Routers in `src/routers/` organize related endpoints
+- Use Express Router
+- Handle session-based authentication
+- Example: `src/routers/users/users.router.ts`, `src/routers/organizations/organizations.router.ts`
+
+### Additional Rules
+
+- If creating a new controller and router, use the pattern of putting the router in the `src/routers/` directory, and not using the `back-end/src/app.ts` file - that is the old way of doing things.
+- If building a new model, the model should not be exported from the model file - only the functions and methods should be exported.
+
+## External REST API (Customer Integration)
+
+The external REST API is for customers to integrate with GrowthBook programmatically.
+
+### Location & Structure
+
+- All external API routes: `packages/back-end/src/api/`
+- Each resource has its own directory with a `*.router.ts` file
+- Mounted at: `/api/v1/` prefix
+- Documented in OpenAPI spec at `src/api/openapi/`
+
+**Example structure:**
+
+```
+src/api/
+  features/
+    features.router.ts
+    getFeature.ts
+    postFeature.ts
+    putFeature.ts
+    deleteFeature.ts
+  experiments/
+    experiments.router.ts
+    getExperiments.ts
+    ...
+```
+
+### API Model Pattern
+
+- Use the `ApiModel` pattern for CRUD operations
+- Automatically generates standard REST endpoints (GET, POST, PUT, DELETE)
+- Define models in `packages/back-end/src/api/*/models.ts`
+- Uses `createApiRequestHandler` for consistent request handling
+
+**Example:**
+
+```typescript
+// In api/myresource/models.ts
+export const MyResourceApiModel = {
+  modelKey: "myResource",
+  crudActions: ["list", "get", "create", "update", "delete"],
+  // ... configuration
+};
+
+// Router automatically generated with:
+// GET /api/v1/myresources
+// GET /api/v1/myresources/:id
+// POST /api/v1/myresources
+// PUT /api/v1/myresources/:id
+// DELETE /api/v1/myresources/:id
+```
+
+### Custom Handlers (External API)
+
+For endpoints that don't fit CRUD patterns, define custom handlers:
+
+```typescript
+// In api/myresource/myresource.router.ts
+import { createApiRequestHandler } from "../utils";
+
+const myCustomHandler = createApiRequestHandler(validator)(async (req) => {
+  // Custom logic here
+  return { data: result };
+});
+
+router.post("/my-custom-endpoint", myCustomHandler);
+```
+
+### Authentication (External API)
+
+- Uses API key authentication via `authenticateApiRequestMiddleware`
+- API keys passed in `Authorization: Bearer <key>` header
+- Context available at `req.context.org`, `req.context.permissions`
+
+## Common Patterns (Both APIs)
+
+### Request Validation
+
+- Use Zod for all request validation
+- Validators in `packages/back-end/src/validators/` (back-end only)
+- Validators in `packages/shared/src/validators/` (shared with front-end)
+
+### Permissions
+
+- Use `permissionsUtil` class and its helpers when checking permissions
+- Check permissions before sensitive operations
+- Available at `req.context.permissions`
+
+### Models
+
+- **Leverage the BaseModel** - When adding a new model, default to using the BaseModel except for rare cases
+- Models are in `packages/back-end/src/models/`
+- BaseModel provides standard CRUD operations, validation, and hooks
+
+## Key Differences Summary
+
+| Aspect             | Internal API                       | External REST API                  |
+| ------------------ | ---------------------------------- | ---------------------------------- |
+| **Location**       | `src/controllers/`, `src/routers/` | `src/api/`                         |
+| **Authentication** | Session cookies                    | API keys (Bearer token)            |
+| **Pattern**        | Controllers + wrapController       | ApiModel + createApiRequestHandler |
+| **Audience**       | GrowthBook web app                 | Customer integrations              |
+| **Documentation**  | Internal only                      | OpenAPI spec                       |
+| **URL Prefix**     | `/api/*`                           | `/api/v1/*`                        |
diff --git a/.cursor/rules/backend/model-patterns.md b/.cursor/rules/backend/model-patterns.md
@@ -0,0 +1,349 @@
+---
+description: "Backend data model patterns using BaseModel/MakeModelClass"
+globs: ["packages/back-end/src/models/**/*.ts"]
+alwaysApply: false
+---
+
+# Backend Model Patterns
+
+## Overview
+
+GrowthBook uses a `BaseModel` pattern built on MongoDB. New models should use `MakeModelClass()` to create a base class, then extend it with permission logic and customize further if needed.
+
+**Location:** `packages/back-end/src/models/`
+
+## Creating a New Model
+
+### Step 1: Create the Base Class
+
+```typescript
+// In packages/back-end/src/models/MyResourceModel.ts
+import { MakeModelClass } from "./BaseModel";
+import { myResourceValidator } from "shared/validators";
+
+const BaseClass = MakeModelClass({
+  schema: myResourceValidator, // Zod schema from shared
+  collectionName: "myresources", // MongoDB collection name
+  idPrefix: "res_", // ID prefix for generation
+  auditLog: {
+    // Audit logging config (optional)
+    entity: "myResource",
+    createEvent: "myResource.create",
+    updateEvent: "myResource.update",
+    deleteEvent: "myResource.delete",
+  },
+  globallyUniqueIds: true, // IDs unique across all orgs
+  defaultValues: {
+    // Default field values
+    description: "",
+    settings: {},
+  },
+});
+```
+
+### Step 2: Extend with Permission Logic
+
+```typescript
+export class MyResourceModel extends BaseClass {
+  // Required: Check if user can read this document
+  protected canRead(doc: MyResourceInterface) {
+    return this.context.permissions.canReadSingleProjectResource(doc.project);
+  }
+
+  // Required: Check if user can create documents
+  protected canCreate() {
+    return this.context.permissions.canCreateMyResource();
+  }
+
+  // Required: Check if user can update this document
+  protected canUpdate(doc: MyResourceInterface) {
+    return this.context.permissions.canUpdateMyResource(doc);
+  }
+
+  // Required: Check if user can delete this document
+  protected canDelete(doc: MyResourceInterface) {
+    return this.context.permissions.canDeleteMyResource(doc);
+  }
+}
+```
+
+### Step 3: Add to the RequestContext so it can be used from anywhere
+
+Add the model to `back-end/src/services/context.ts`. That way it can be referenced from anywhere. Use the plural version of the model name here. For example:
+
+```ts
+const resource = req.context.myResources.getById("abc123");
+```
+
+## Configuration Options
+
+### MakeModelClass Config
+
+| Option                  | Type       | Required | Description                                                |
+| ----------------------- | ---------- | -------- | ---------------------------------------------------------- |
+| `schema`                | Zod schema | Yes      | Validator from `shared/validators`                         |
+| `collectionName`        | string     | Yes      | MongoDB collection name                                    |
+| `idPrefix`              | string     | No       | Prefix for auto-generated IDs (e.g., "prj\_")              |
+| `auditLog`              | object     | No       | Audit event configuration                                  |
+| `globallyUniqueIds`     | boolean    | No       | Create unique index on `id` only (not `id + organization`) |
+| `defaultValues`         | object     | No       | Default values applied on creation                         |
+| `readonlyFields`        | string[]   | No       | Fields that cannot be updated after creation               |
+| `skipDateUpdatedFields` | string[]   | No       | Fields that don't trigger `dateUpdated` when changed       |
+| `additionalIndexes`     | array      | No       | Extra MongoDB indexes to create                            |
+
+### Audit Log Config
+
+```typescript
+auditLog: {
+  entity: "project",              // Entity type for audit system
+  createEvent: "project.create",  // Event name for creates
+  updateEvent: "project.update",  // Event name for updates
+  deleteEvent: "project.delete",  // Event name for deletes
+}
+```
+
+## ID Prefix Conventions
+
+Use consistent prefixes for entity IDs:
+
+| Entity       | Prefix   | Example        |
+| ------------ | -------- | -------------- |
+| Project      | `prj_`   | `prj_abc123`   |
+| Experiment   | `exp_`   | `exp_xyz789`   |
+| Feature      | `feat_`  | `feat_def456`  |
+| Saved Group  | `grp_`   | `grp_ghi012`   |
+| Segment      | `seg_`   | `seg_jkl345`   |
+| Metric       | `met_`   | `met_mno678`   |
+| Webhook      | `wh_`    | `wh_pqr901`    |
+| API Key      | `key_`   | `key_stu234`   |
+| Custom Field | `cfd_`   | `cfd_vwx567`   |
+| Safe Rollout | `sr_`    | `sr_yza890`    |
+| Holdout      | `hld_`   | `hld_bcd123`   |
+| Fact Table   | `fact__` | `fact__efg456` |
+| URL Redirect | `url_`   | `url_hij789`   |
+
+## Lifecycle Hooks
+
+Override these methods to add custom logic:
+
+### Validation Hook
+
+```typescript
+protected async customValidation(doc: MyResourceInterface) {
+  if (doc.name.length < 3) {
+    throw new Error("Name must be at least 3 characters");
+  }
+}
+```
+
+### Create Hooks
+
+```typescript
+protected async beforeCreate(doc: MyResourceInterface) {
+  // Called before document is inserted
+  doc.computedField = calculateValue(doc);
+}
+
+protected async afterCreate(doc: MyResourceInterface) {
+  // Called after document is inserted
+  await notifyExternalService(doc);
+}
+```
+
+### Update Hooks
+
+```typescript
+protected async beforeUpdate(
+  existing: MyResourceInterface,
+  updates: Partial<MyResourceInterface>,
+  newDoc: MyResourceInterface
+) {
+  // Called before update is applied
+}
+
+protected async afterUpdate(
+  existing: MyResourceInterface,
+  updates: Partial<MyResourceInterface>,
+  newDoc: MyResourceInterface
+) {
+  // Called after update - useful for cache invalidation
+  if (updates.rules || updates.settings) {
+    await invalidateSDKCache(this.context);
+  }
+}
+```
+
+### Delete Hooks
+
+```typescript
+protected async beforeDelete(doc: MyResourceInterface) {
+  // Check for dependencies before allowing delete
+  const dependents = await findDependents(doc.id);
+  if (dependents.length > 0) {
+    throw new Error("Cannot delete: has dependent resources");
+  }
+}
+
+protected async afterDelete(doc: MyResourceInterface) {
+  // Cleanup after delete
+  await cleanupRelatedData(doc.id);
+}
+```
+
+## Data Migration
+
+Handle legacy document formats with the `migrate()` method:
+
+```typescript
+protected migrate(legacyDoc: LegacyMyResourceInterface): MyResourceInterface {
+  const { oldField, deprecatedProperty, ...rest } = legacyDoc;
+
+  return {
+    ...rest,
+    // Map old field to new structure
+    newField: oldField ?? "default",
+    // Remove deprecated properties by not including them
+  };
+}
+```
+
+Migration runs automatically when documents are read, transforming legacy data to the current schema.
+
+## Built-in CRUD Methods
+
+### Read Operations
+
+```typescript
+const model = new MyResourceModel(context);
+
+// Get by ID
+const doc = await model.getById("res_abc123");
+
+// Get multiple by IDs
+const docs = await model.getByIds(["res_abc123", "res_def456"]);
+
+// Get all (with optional filter)
+const allDocs = await model.getAll();
+const filtered = await model.getAll({ status: "active" });
+```
+
+### Write Operations
+
+```typescript
+const model = new MyResourceModel(context);
+
+// Create
+const newDoc = await model.create({
+  name: "My Resource",
+  settings: { enabled: true },
+});
+
+// Update by document
+const updated = await model.update(existingDoc, { name: "New Name" });
+
+// Update by ID
+const updated = await model.updateById("res_abc123", { name: "New Name" });
+
+// Delete
+await model.delete(existingDoc);
+await model.deleteById("res_abc123");
+```
+
+### Bypass Permission (Use Sparingly)
+
+For system operations that shouldn't check user permissions:
+
+```typescript
+// Only use when truly necessary (e.g., system migrations, webhooks)
+await model.dangerousCreateBypassPermission(data);
+await model.dangerousUpdateByIdBypassPermission(id, updates);
+```
+
+## Adding Custom Methods
+
+You can add more tailored data fetching methods as needed by referencing the `_findOne` and `_find` methods. There are similar protected methods for write operations, although those are rarely needed.
+
+Here's an example:
+
+```ts
+export class FooDataModel extends BaseClass {
+  // ...
+
+  public getByNames(names: string[]) {
+    return this._find({ name: { $in: names } });
+  }
+}
+```
+
+Note: Permission checks, migrations, etc. are all done automatically within the `_find` method, so you don't need to repeat any of that in your custom methods. Also, the `organization` field is automatically added to every query, so it will always be multi-tenant safe.
+
+## Complete Example
+
+```typescript
+// packages/back-end/src/models/WidgetModel.ts
+import { MakeModelClass } from "./BaseModel";
+import { widgetValidator, WidgetInterface } from "shared/validators";
+import { ReqContext } from "../types";
+
+const BaseClass = MakeModelClass({
+  schema: widgetValidator,
+  collectionName: "widgets",
+  idPrefix: "wgt_",
+  auditLog: {
+    entity: "widget",
+    createEvent: "widget.create",
+    updateEvent: "widget.update",
+    deleteEvent: "widget.delete",
+  },
+  globallyUniqueIds: true,
+  defaultValues: {
+    description: "",
+    enabled: false,
+  },
+  readonlyFields: ["organization"],
+});
+
+export class WidgetModel extends BaseClass {
+  protected canRead(doc: WidgetInterface) {
+    return this.context.permissions.canReadSingleProjectResource(doc.project);
+  }
+
+  protected canCreate() {
+    return this.context.permissions.canCreateWidget();
+  }
+
+  protected canUpdate(doc: WidgetInterface) {
+    return this.context.permissions.canUpdateWidget(doc);
+  }
+
+  protected canDelete(doc: WidgetInterface) {
+    return this.context.permissions.canDeleteWidget(doc);
+  }
+
+  protected async afterUpdate(
+    existing: WidgetInterface,
+    updates: Partial<WidgetInterface>,
+  ) {
+    if (updates.enabled !== undefined) {
+      await this.context.logger.info("Widget enabled state changed", {
+        widgetId: existing.id,
+        enabled: updates.enabled,
+      });
+    }
+  }
+
+  // Custom method
+  async getEnabledByProject(projectId: string): Promise<WidgetInterface[]> {
+    return this._find({ project: projectId, enabled: true });
+  }
+}
+```
+
+## Key Points
+
+1. **Always use MakeModelClass** for new models (unless there's a specific reason not to)
+2. **Implement all four permission methods** - canRead, canCreate, canUpdate, canDelete
+3. **Use hooks for side effects** - afterUpdate for cache invalidation, beforeDelete for dependency checks
+4. **Use migrate() for schema evolution** - handles legacy documents gracefully
+5. **Choose appropriate ID prefix** - follow existing conventions
+6. **Enable audit logging** - for user-facing entities that need tracking
diff --git a/.cursor/rules/development-guidelines.md b/.cursor/rules/development-guidelines.md
@@ -0,0 +1,70 @@
+---
+description: "General development guidelines, code quality standards, and common patterns"
+alwaysApply: true
+---
+
+# Development Guidelines
+
+## General Rules
+
+- DO NOT write tests for front-end components or back-end routers/controllers/models. DO write tests for critical utility/helper functions
+- Follow existing patterns in the codebase
+- When in doubt, search for similar existing code and follow that pattern
+- Use existing ESLint rules - they're comprehensive and enforced in CI
+- Do not use `//eslint-disable-next-line` comments to fix type issues
+
+## Code Quality
+
+- TypeScript: Use strict types. Never use `any`. If you don't know the type, use `unknown`.
+- If data is coming from an untrusted source (like the request body or JSON.parse), it should start out as `unknown` until you validate it (usually with zod).
+- Avoid unused variables whenever possible. If you absolutely must use them, prefix with `_`.
+- Console logging: Avoid `console.log` in production code (ESLint warns). On the back-end, you can import from `util/logger` instead.
+
+## Common Patterns
+
+### Zod Validation
+
+```typescript
+import { z } from "zod";
+
+const mySchema = z.object({
+  name: z.string(),
+  count: z.number().int().positive(),
+});
+
+type MyType = z.infer<typeof mySchema>;
+```
+
+### Type Definitions
+
+- Shared types go in `packages/shared/types/*.d.ts`
+- Use `.d.ts` files for type-only definitions
+- Export types with `export type` or `export interface`
+- Only declare types/interfaces from scratch when there is no Zod schema. When there is a corresponding Zod schema, use that as the source of truth and infer the type.
+
+### Environment Variables
+
+- Back-end: Define in `packages/back-end/src/util/secrets.ts`
+- Front-end: Define in `packages/front-end/pages/api/init.ts` and `packages/front-end/services/env.ts`
+- Use environment-specific `.env.local` files for local overrides
+- DO NOT reference `process.env` directly outside of the files above.
+
+## Code Quality Commands
+
+- **Lint**: `pnpm lint` (auto-fixes issues)
+- **Type check**: `pnpm type-check` (all packages)
+- **Format**: `pnpm pretty` (Prettier formatting)
+
+## Key Principles
+
+1. **Respect package boundaries** - front-end, back-end, and shared have strict import restrictions
+2. **Use design system components** - don't import Radix UI directly in front-end
+3. **Follow existing patterns** - search the codebase for similar code
+4. **Use pnpm** - this is a pnpm workspace
+5. **TypeScript strict mode** - use proper types, avoid `any`
+6. **Check commercial features** - use `hasCommercialFeature()` for premium functionality
+7. **Router pattern for APIs** - organize by resource with dedicated router files
+8. **Leverage the BaseModel** - when adding a new model, default to using the BaseModel except for rare cases
+9. **Use permissionsUtil** - when checking permissions, leverage the permissionsUtil class and it's included helpers
+
+These rules ensure consistency and maintainability across the GrowthBook codebase.
diff --git a/.cursor/rules/frontend/data-fetching.md b/.cursor/rules/frontend/data-fetching.md
@@ -0,0 +1,310 @@
+---
+description: "Data fetching and mutation patterns for the front-end application"
+globs: ["packages/front-end/**/*.tsx", "packages/front-end/**/*.ts"]
+alwaysApply: false
+---
+
+# Frontend Data Fetching Patterns
+
+## Overview
+
+GrowthBook uses SWR for data fetching with a custom `useApi()` hook, and `apiCall()` for mutations. All requests are automatically scoped to the current organization.
+
+## Fetching Data - useApi()
+
+The `useApi()` hook is the primary way to fetch data. It's built on SWR and provides caching, revalidation, and organization scoping.
+
+**Location:** `packages/front-end/hooks/useApi.ts`
+
+### Basic Usage
+
+```typescript
+import useApi from "@/hooks/useApi";
+
+// Simple fetch
+const { data, error, mutate } = useApi<{ items: ItemInterface[] }>("/items");
+
+// With query parameters
+const { data, error, mutate } = useApi<{ experiments: ExperimentInterface[] }>(
+  `/experiments?project=${project || ""}&includeArchived=${includeArchived ? "1" : ""}`,
+);
+```
+
+### Return Values
+
+- `data` - The response data (undefined while loading)
+- `error` - Error object if request failed
+- `mutate` - Function to revalidate/update the cache
+- `isLoading` - Boolean indicating loading state (from SWR)
+
+### Options
+
+```typescript
+useApi<Response>(path, {
+  shouldRun?: () => boolean,    // Conditional execution
+  autoRevalidate?: boolean,     // Default: true - revalidate on focus/reconnect
+  orgScoped?: boolean,          // Default: true - scope cache to organization
+});
+```
+
+### Conditional Fetching
+
+Use `shouldRun` to conditionally fetch data:
+
+```typescript
+// Only fetch when user is authenticated
+const { data } = useApi<UserResponse>(`/user`, {
+  shouldRun: () => isAuthenticated,
+  orgScoped: false,
+});
+
+// Only fetch when we have an ID
+const { data } = useApi<FeatureResponse>(`/feature/${featureId}`, {
+  shouldRun: () => !!featureId,
+});
+```
+
+### Disable Auto-Revalidation
+
+For data that shouldn't refresh automatically (e.g., form editing):
+
+```typescript
+const { data, mutate } = useApi<DataResponse>("/endpoint", {
+  autoRevalidate: false,
+});
+```
+
+## Mutations - apiCall()
+
+For POST, PUT, PATCH, DELETE operations, use `apiCall()` from the auth context.
+
+### Basic Usage
+
+```typescript
+import { useAuth } from "@/services/auth";
+
+function MyComponent() {
+  const { apiCall } = useAuth();
+
+  const handleCreate = async () => {
+    await apiCall("/items", {
+      method: "POST",
+      body: JSON.stringify({ name: "New Item" }),
+    });
+  };
+
+  const handleUpdate = async (id: string) => {
+    await apiCall(`/items/${id}`, {
+      method: "PUT",
+      body: JSON.stringify({ name: "Updated Name" }),
+    });
+  };
+
+  const handleDelete = async (id: string) => {
+    await apiCall(`/items/${id}`, {
+      method: "DELETE",
+    });
+  };
+}
+```
+
+### With Cache Revalidation
+
+After mutations, call `mutate()` to refresh the cached data:
+
+```typescript
+function MyComponent() {
+  const { apiCall } = useAuth();
+  const { data, mutate } = useApi<{ items: ItemInterface[] }>("/items");
+
+  const handleCreate = async (formData: CreateItemData) => {
+    try {
+      await apiCall("/items", {
+        method: "POST",
+        body: JSON.stringify(formData),
+      });
+      // Revalidate the list after creation
+      await mutate();
+    } catch (e) {
+      // Handle error
+      console.error(e);
+    }
+  };
+}
+```
+
+### Typed Responses
+
+```typescript
+const response = await apiCall<{ item: ItemInterface; message?: string }>(
+  "/items",
+  {
+    method: "POST",
+    body: JSON.stringify(data),
+  },
+);
+
+// Access typed response
+console.log(response.item.id);
+```
+
+## Error Handling Patterns
+
+### Pattern 1: Try-Catch with State
+
+```typescript
+const [error, setError] = useState<string | null>(null);
+
+const handleSubmit = async (data: FormData) => {
+  setError(null);
+  try {
+    const response = await apiCall<{ error?: string }>("/endpoint", {
+      method: "POST",
+      body: JSON.stringify(data),
+    });
+
+    if (response.error) {
+      setError(response.error);
+      return;
+    }
+
+    mutate(); // Refresh data on success
+  } catch (e) {
+    setError(e.message || "An error occurred");
+  }
+};
+```
+
+### Pattern 2: Modal Error Handling
+
+When using the `Modal` component, errors thrown in `submit` are automatically displayed:
+
+```typescript
+<Modal
+  header="Create Item"
+  submit={async () => {
+    await apiCall("/items", {
+      method: "POST",
+      body: JSON.stringify(formData),
+    });
+    mutate();
+  }}
+>
+  {/* Form fields */}
+</Modal>
+```
+
+### Pattern 3: Check Error in useApi
+
+```typescript
+const { data, error } = useApi<DataResponse>("/endpoint");
+
+if (error) {
+  return <div className="alert alert-danger">{error.message}</div>;
+}
+
+if (!data) {
+  return <LoadingSpinner />;
+}
+
+return <MyContent data={data} />;
+```
+
+## Common Patterns
+
+### Fetch with Loading State
+
+```typescript
+const { data, error } = useApi<{ features: FeatureInterface[] }>("/features");
+
+if (error) return <ErrorDisplay error={error} />;
+if (!data) return <LoadingOverlay />;
+
+return <FeatureList features={data.features} />;
+```
+
+### Optimistic Updates
+
+Update the cache immediately, then revalidate:
+
+```typescript
+const { data, mutate } = useApi<{ items: ItemInterface[] }>("/items");
+
+const handleToggle = async (id: string, enabled: boolean) => {
+  // Optimistically update UI
+  mutate(
+    {
+      items: data.items.map((item) =>
+        item.id === id ? { ...item, enabled } : item,
+      ),
+    },
+    false, // Don't revalidate yet
+  );
+
+  try {
+    await apiCall(`/items/${id}`, {
+      method: "PUT",
+      body: JSON.stringify({ enabled }),
+    });
+    // Revalidate to confirm
+    await mutate();
+  } catch (e) {
+    // Revert on error
+    await mutate();
+  }
+};
+```
+
+### Refresh Multiple Caches
+
+```typescript
+const { mutate: mutateFeatures } = useApi<FeaturesResponse>("/features");
+const { mutate: mutateExperiments } =
+  useApi<ExperimentsResponse>("/experiments");
+
+const handleBulkAction = async () => {
+  await apiCall("/bulk-action", { method: "POST", body: JSON.stringify(data) });
+  // Refresh both caches
+  await Promise.all([mutateFeatures(), mutateExperiments()]);
+};
+```
+
+### Using mutateDefinitions for Global State
+
+For data that affects the global definitions context (metrics, features, segments):
+
+```typescript
+import { useDefinitions } from "@/services/DefinitionsContext";
+
+function MyComponent() {
+  const { mutateDefinitions } = useDefinitions();
+
+  const handleCreateMetric = async () => {
+    await apiCall("/metrics", {
+      method: "POST",
+      body: JSON.stringify(metricData),
+    });
+    // Refresh the global definitions cache
+    mutateDefinitions();
+  };
+}
+```
+
+## Organization Context
+
+All API requests automatically include:
+
+- `Authorization: Bearer <token>` header
+- `X-Organization: <orgId>` header
+- Cache keys are prefixed with `orgId::` for organization scoping
+
+This means switching organizations automatically invalidates all cached data.
+
+## Key Hooks Summary
+
+| Hook               | Purpose                                    | Location                        |
+| ------------------ | ------------------------------------------ | ------------------------------- |
+| `useApi()`         | SWR-based data fetching                    | `@/hooks/useApi`                |
+| `useAuth()`        | Access `apiCall()` for mutations           | `@/services/auth`               |
+| `useDefinitions()` | Global definitions + `mutateDefinitions()` | `@/services/DefinitionsContext` |
+| `useUser()`        | User context with `refreshOrganization()`  | `@/services/UserContext`        |
diff --git a/.cursor/rules/frontend/react-patterns.md b/.cursor/rules/frontend/react-patterns.md
@@ -0,0 +1,181 @@
+---
+description: "TypeScript and React conventions for front-end development"
+globs: ["packages/front-end/**/*.tsx", "packages/front-end/**/*.ts"]
+alwaysApply: false
+---
+
+# Frontend React & TypeScript Patterns
+
+## Component Structure
+
+- Use **functional components** with TypeScript
+- Define props interfaces inline or as separate types
+- Use explicit return types for complex functions
+
+### Example Component Structure
+
+```typescript
+import { ReactNode } from "react";
+import { useUser } from "@/services/UserContext";
+
+export default function MyComponent({
+  value,
+  onChange,
+  disabled = false,
+}: {
+  value: string;
+  onChange: (value: string) => void;
+  disabled?: boolean;
+}) {
+  const { organization, hasCommercialFeature } = useUser();
+  const hasFeature = hasCommercialFeature("feature-name");
+
+  // Component logic here
+
+  return (
+    <div>
+      {hasFeature && <span>Premium content</span>}
+      <input value={value} onChange={(e) => onChange(e.target.value)} disabled={disabled} />
+    </div>
+  );
+}
+```
+
+## Commercial Features
+
+- Check feature availability with `hasCommercialFeature("feature-name")`
+- Wrap premium features with `<PremiumTooltip commercialFeature="feature-name">`
+- Feature flags are defined in `packages/shared/src/enterprise/license-consts.ts`
+
+## Common Hooks
+
+- `useUser()` - Access user context, organization, permissions
+- `useEnvironments()` - Get available environments
+- `useDefinitions()` - Access metrics, features, segments
+- `useAuth()` - Authentication state
+
+Context providers are in `packages/front-end/services/`
+
+## UI Component Hierarchy
+
+When building UI, follow this priority order for component selection:
+
+### 1. Design System Components (`@/ui/`) - PREFERRED
+
+Always check the design system first. These components are purpose-built for GrowthBook and provide consistent styling and behavior:
+
+```typescript
+// ✅ Preferred - use design system components
+import { Button } from "@/ui/Button";
+import { Badge } from "@/ui/Badge";
+import { Checkbox } from "@/ui/Checkbox";
+import { Select } from "@/ui/Select";
+import { Tabs } from "@/ui/Tabs";
+import { Table } from "@/ui/Table";
+import { Callout } from "@/ui/Callout";
+import { Link } from "@/ui/Link";
+import { Switch } from "@/ui/Switch";
+import { RadioGroup } from "@/ui/RadioGroup";
+import { RadioCards } from "@/ui/RadioCards";
+import { DropdownMenu } from "@/ui/DropdownMenu";
+import { Avatar } from "@/ui/Avatar";
+import { DataList } from "@/ui/DataList";
+import { Popover } from "@/ui/Popover";
+import { HelperText } from "@/ui/HelperText";
+import { Tooltip } from "@/ui/Tooltip";
+```
+
+Available design system components: Avatar, Badge, Button, Callout, Checkbox, ConfirmDialog, DataList, DropdownMenu, ErrorDisplay, Frame, HelperText, Link, LinkButton, Metadata, Pagination, Popover, PremiumCallout, RadioCards, RadioGroup, Select, SplitButton, Switch, Table, Tabs, Tooltip
+
+### 2. Radix Themes - SECONDARY
+
+If a component doesn't exist in `@/ui/`, check Radix Themes. Use for layout primitives and components not yet wrapped in our design system:
+
+```typescript
+// ✅ OK when no @/ui/ equivalent exists
+import { Flex, Box, Grid, Text, Heading } from "@radix-ui/themes";
+```
+
+### 3. Existing GrowthBook Components - TERTIARY
+
+Check `packages/front-end/components/` for domain-specific components that may already exist.
+
+### 4. Build New Components - LAST RESORT
+
+If none of the above work, build a new component.
+
+**Before building inline or one-off components, ask yourself:** Could this be useful elsewhere in the codebase? If the component is generic and reusable (not domain-specific), propose adding it to `@/ui/` instead of building it inline.
+
+**When to suggest a new `@/ui/` component:**
+
+- The pattern is generic (not tied to a specific feature/domain)
+- Similar UI patterns exist elsewhere in the codebase
+- The component wraps a Radix primitive with GrowthBook-specific styling
+- You're about to duplicate similar markup/logic in multiple places
+
+**Ask the user before creating:** "This looks like a reusable pattern. Should I create a new `@/ui/ComponentName` component that can be used across the codebase?"
+
+New `@/ui/` components should:
+
+- Live in `packages/front-end/ui/`
+- Include a `.stories.tsx` file for Storybook documentation
+- Follow existing component patterns in that folder
+
+## Avoid Bootstrap
+
+**Bootstrap classes are legacy and should NOT be used in new code.** The codebase is migrating away from Bootstrap toward our design system.
+
+### ❌ DON'T - Bootstrap Classes
+
+```tsx
+// ❌ Bad - Bootstrap utility classes
+<div className="d-flex justify-content-between align-items-center">
+<div className="mb-3 mt-2">
+<div className="btn btn-primary">
+<span className="badge bg-success">
+<div className="container-fluid">
+<div className="row">
+<div className="col-md-6">
+```
+
+### ✅ DO - Design System & Radix Themes
+
+```tsx
+// ✅ Good - Radix Themes layout primitives
+<Flex justify="between" align="center">
+<Box mb="3" mt="2">
+
+// ✅ Good - Design system components
+<Button variant="solid">Click me</Button>
+<Badge color="green">Active</Badge>
+
+// ✅ Good - CSS Modules or inline styles when needed
+<div className={styles.container}>
+<div style={{ display: "flex", gap: "8px" }}>
+```
+
+### Common Bootstrap → Design System Migrations
+
+| Bootstrap Class              | Replacement                               |
+| ---------------------------- | ----------------------------------------- |
+| `btn btn-primary`            | `<Button>` from `@/ui/Button`             |
+| `btn btn-outline-*`          | `<Button variant="outline">`              |
+| `badge bg-*`                 | `<Badge>` from `@/ui/Badge`               |
+| `form-check` / `form-switch` | `<Checkbox>` or `<Switch>` from `@/ui/`   |
+| `nav nav-tabs`               | `<Tabs>` from `@/ui/Tabs`                 |
+| `table`                      | `<Table>` from `@/ui/Table`               |
+| `alert alert-*`              | `<Callout>` from `@/ui/Callout`           |
+| `dropdown`                   | `<DropdownMenu>` from `@/ui/DropdownMenu` |
+| `d-flex`                     | `<Flex>` from `@radix-ui/themes`          |
+| `d-none` / `d-block`         | Conditional rendering or CSS              |
+| `mb-*` / `mt-*` / `mx-*`     | `<Box mb="3">` or style props             |
+| `row` / `col-*`              | `<Grid>` from `@radix-ui/themes`          |
+| `text-center` / `text-end`   | `<Text align="center">` or CSS            |
+
+### When You Encounter Bootstrap
+
+If you're modifying code that uses Bootstrap:
+
+1. **Small changes**: OK to leave existing Bootstrap, but don't add more
+2. **New features**: Use design system components exclusively
+3. **Refactoring**: Migrate Bootstrap to design system when touching that code
diff --git a/.cursor/rules/package-boundaries.md b/.cursor/rules/package-boundaries.md
@@ -0,0 +1,40 @@
+---
+description: "Critical package import restrictions enforced by ESLint - must be strictly followed"
+alwaysApply: true
+---
+
+# Package Import Boundaries
+
+These restrictions are enforced by ESLint and must be strictly followed.
+
+## Front-end Package
+
+- ✅ CAN import from: `shared` package, itself, `sdk-js`, and `sdk-react`
+- ❌ CANNOT import from: `back-end`
+- ❌ DO NOT import Radix UI components directly - use design system wrappers from `@/ui/` instead
+  - Bad: `import { Button } from "@radix-ui/themes"`
+  - Good: `import { Button } from "@/ui/Button"`
+  - Affected components: Avatar, Badge, Button, Callout, Checkbox, DataList, DropdownMenu, Link, RadioCards, RadioGroup, Select, Switch, Table, Tabs
+- ❌ DO NOT use `window.history.pushState` or `window.history.replaceState` directly
+  - Use `router.push(url, undefined, { shallow: true })` from `next/router` instead
+
+## Back-end Package
+
+- ✅ CAN import from: `shared` package, itself, `sdk-js`
+- ❌ CANNOT import from: `front-end`, `sdk-react`
+- ❌ DO NOT import `node-fetch` directly
+  - Use `import { fetch } from "back-end/src/util/http.util"` instead
+
+## Shared Package
+
+- ✅ CAN import from: itself, `sdk-js`
+- ❌ CANNOT import from: `back-end`, `front-end`, `sdk-react`
+- ❌ DO NOT use `.default()` on Zod schemas in `packages/shared/src/validators/*`
+  - Use the `defaultValues` option in the BaseModel config instead
+
+## SDK Packages
+
+- ✅ CAN import from: themselves only (React can import from JS, but not the other way around)
+- ❌ CANNOT import from: `back-end`, `front-end`, `shared`, or any internal package
+- ❌ CANNOT use any 3rd party npm libraries. Must have zero dependencies and be self-contained.
+- Must remain fully isolated for npm distribution
diff --git a/.cursor/rules/permissions.md b/.cursor/rules/permissions.md
@@ -0,0 +1,413 @@
+---
+description: "Permission system for access control across front-end and back-end"
+alwaysApply: true
+---
+
+# Permission System
+
+## Overview
+
+GrowthBook uses a three-tier permission system with Global, Project-scoped, and Environment-scoped permissions. Permissions work alongside commercial features - both gates must pass for access.
+
+## Permission Scopes
+
+### Global Permissions
+
+Apply organization-wide, not restricted to projects or environments:
+
+- `manageTeam`, `manageBilling`, `manageApiKeys`
+- `organizationSettings`, `viewAuditLog`
+- `createPresentations`, `createDimensions`, `manageNamespaces`
+- `manageCustomRoles`, `manageCustomFields`, `manageDecisionCriteria`
+
+### Project-Scoped Permissions
+
+Can be granted for all projects or specific projects:
+
+- `readData`, `addComments`, `canReview`
+- `manageFeatures`, `manageFeatureDrafts`
+- `createMetrics`, `createAnalyses`, `createSegments`
+- `manageFactTables`, `manageFactMetrics`
+- `manageSavedGroups`, `manageTargetingAttributes`
+- `createDatasources`, `editDatasourceSettings`, `runQueries`
+
+### Environment-Scoped Permissions
+
+Further restricted to specific environments within projects:
+
+- `publishFeatures` - Publish feature changes to environments
+- `runExperiments` - Start/stop experiments
+- `manageEnvironments` - Create/edit environments
+- `manageSDKConnections` - Manage SDK connections
+- `manageSDKWebhooks` - Manage SDK webhooks
+
+## Frontend Permission Checking
+
+### Using usePermissionsUtil()
+
+The primary hook for checking permissions:
+
+```typescript
+import usePermissionsUtil from "@/hooks/usePermissionsUtils";
+
+function MyComponent() {
+  const permissionsUtil = usePermissionsUtil();
+
+  // Global permission check
+  if (!permissionsUtil.canManageTeam()) {
+    return <NoAccess />;
+  }
+
+  // Project-scoped check
+  if (!permissionsUtil.canCreateFeature({ project: "prj_123" })) {
+    return <NoAccess />;
+  }
+
+  // Environment-scoped check
+  if (!permissionsUtil.canPublishFeature(feature, ["production"])) {
+    return <NoAccess />;
+  }
+
+  return <MyContent />;
+}
+```
+
+### Common Permission Check Methods
+
+```typescript
+const permissionsUtil = usePermissionsUtil();
+
+// Feature permissions
+permissionsUtil.canCreateFeature({ project });
+permissionsUtil.canUpdateFeature(existingFeature, updatedFeature);
+permissionsUtil.canDeleteFeature(feature);
+permissionsUtil.canPublishFeature(feature, environments);
+
+// Experiment permissions
+permissionsUtil.canCreateExperiment({ project });
+permissionsUtil.canUpdateExperiment(existingExp, updatedExp);
+permissionsUtil.canRunExperiment(experiment, environments);
+
+// Metric permissions
+permissionsUtil.canCreateMetric({ projects });
+permissionsUtil.canUpdateMetric(existingMetric, updatedMetric);
+permissionsUtil.canDeleteMetric(metric);
+
+// Project permissions
+permissionsUtil.canReadSingleProjectResource(projectId);
+permissionsUtil.canReadMultiProjectResource(projectIds);
+permissionsUtil.canManageSomeProjects();
+
+// General checks
+permissionsUtil.canViewFeatureModal(project);
+permissionsUtil.canViewExperimentModal(project);
+```
+
+### Using Raw Permissions
+
+For simple global permission checks:
+
+```typescript
+import usePermissions from "@/hooks/usePermissions";
+
+function MyComponent() {
+  const permissions = usePermissions();
+
+  if (permissions.manageTeam) {
+    // Show team management UI
+  }
+
+  if (permissions.viewAuditLog) {
+    // Show audit log link
+  }
+}
+```
+
+### Conditional Rendering Pattern
+
+```typescript
+function FeatureActions({ feature }: { feature: FeatureInterface }) {
+  const permissionsUtil = usePermissionsUtil();
+
+  return (
+    <div>
+      {permissionsUtil.canUpdateFeature(feature, feature) && (
+        <Button onClick={handleEdit}>Edit</Button>
+      )}
+
+      {permissionsUtil.canDeleteFeature(feature) && (
+        <Button variant="danger" onClick={handleDelete}>Delete</Button>
+      )}
+
+      {permissionsUtil.canPublishFeature(feature, ["production"]) && (
+        <Button onClick={handlePublish}>Publish to Production</Button>
+      )}
+    </div>
+  );
+}
+```
+
+## Backend Permission Checking
+
+### In Controllers/Routers
+
+Access permissions through the request context:
+
+```typescript
+import { getContextFromReq } from "back-end/src/services/organizations";
+
+export async function updateFeature(req: AuthRequest, res: Response) {
+  const context = getContextFromReq(req);
+  const { id } = req.params;
+  const updates = req.body;
+
+  // Get existing document
+  const feature = await getFeatureById(context, id);
+  if (!feature) {
+    return res.status(404).json({ error: "Feature not found" });
+  }
+
+  // Check permission
+  if (
+    !context.permissions.canUpdateFeature(feature, { ...feature, ...updates })
+  ) {
+    context.permissions.throwPermissionError();
+  }
+
+  // Proceed with update
+  const updated = await updateFeature(context, id, updates);
+  res.json({ feature: updated });
+}
+```
+
+### Permission Methods in Context
+
+```typescript
+const context = getContextFromReq(req);
+
+// Global permissions
+context.permissions.canManageTeam();
+context.permissions.canManageOrgSettings();
+context.permissions.canViewAuditLogs();
+context.permissions.canManageBilling();
+
+// Project-scoped permissions
+context.permissions.canCreateFeature({ project });
+context.permissions.canUpdateFeature(existing, updated);
+context.permissions.canDeleteFeature(feature);
+
+// Environment-scoped permissions
+context.permissions.canPublishFeature(feature, environments);
+context.permissions.canRunExperiment(experiment, environments);
+
+// Throw error if permission denied
+context.permissions.throwPermissionError();
+context.permissions.throwPermissionError("Custom error message");
+```
+
+### In Models
+
+Models use permission methods internally:
+
+```typescript
+class MyResourceModel extends BaseClass {
+  protected canRead(doc: MyResourceInterface) {
+    return this.context.permissions.canReadSingleProjectResource(doc.project);
+  }
+
+  protected canCreate() {
+    return this.context.permissions.canCreateMyResource();
+  }
+
+  protected canUpdate(doc: MyResourceInterface) {
+    return this.context.permissions.canUpdateMyResource(doc);
+  }
+
+  protected canDelete(doc: MyResourceInterface) {
+    return this.context.permissions.canDeleteMyResource(doc);
+  }
+}
+```
+
+## Commercial Features
+
+Commercial features are a separate gate from permissions. A user might have permission but the organization's plan might not include the feature.
+
+### Frontend - Check Feature Availability
+
+```typescript
+import { useUser } from "@/services/UserContext";
+
+function MyComponent() {
+  const { hasCommercialFeature } = useUser();
+
+  if (!hasCommercialFeature("advanced-permissions")) {
+    return <UpgradePrompt />;
+  }
+
+  return <AdvancedPermissionsUI />;
+}
+```
+
+### Frontend - PremiumTooltip Wrapper
+
+Wrap premium features to show upgrade prompts:
+
+```typescript
+import PremiumTooltip from "@/components/Marketing/PremiumTooltip";
+
+function MyComponent() {
+  return (
+    <PremiumTooltip commercialFeature="advanced-permissions">
+      <Button disabled={!hasFeature} onClick={handleClick}>
+        Advanced Settings
+      </Button>
+    </PremiumTooltip>
+  );
+}
+```
+
+### Backend - Check Feature Availability
+
+```typescript
+import { orgHasPremiumFeature } from "back-end/src/enterprise/licenseUtil";
+
+export async function createArchetype(req: AuthRequest, res: Response) {
+  const context = getContextFromReq(req);
+
+  // Check permission first
+  if (!context.permissions.canCreateArchetype(req.body)) {
+    context.permissions.throwPermissionError();
+  }
+
+  // Then check commercial feature
+  if (!orgHasPremiumFeature(context.org, "archetypes")) {
+    throw new PlanDoesNotAllowError("Archetypes require a Pro plan or higher");
+  }
+
+  // Proceed with creation
+  const archetype = await createArchetype(context, req.body);
+  res.json({ archetype });
+}
+```
+
+### Common Commercial Features
+
+- `advanced-permissions` - Custom roles and project-level permissions
+- `teams` - Team management
+- `audit-logging` - Audit log access
+- `archetypes` - User archetypes
+- `templates` - Experiment templates
+- `sso` - Single sign-on
+- `encrypt-features-endpoint` - SDK endpoint encryption
+- `ai-suggestions` - AI-powered suggestions
+
+## Roles and Policies
+
+### Default Roles
+
+| Role           | Description                   |
+| -------------- | ----------------------------- |
+| `noaccess`     | No permissions                |
+| `readonly`     | Read-only access              |
+| `collaborator` | Read + comments + ideas       |
+| `visualEditor` | Visual editor access          |
+| `engineer`     | Features + SDK + environments |
+| `analyst`      | Analytics + metrics + SQL     |
+| `experimenter` | Engineer + analyst combined   |
+| `admin`        | Full access                   |
+
+### How Permissions Resolve
+
+1. User has a global role (organization-wide)
+2. User can have project-specific role overrides
+3. User can be on teams with their own roles
+4. Permissions merge using OR logic (union)
+5. Environment limits apply only to environment-scoped permissions
+
+## Best Practices
+
+### 1. Check Permissions Early
+
+```typescript
+// Good - check at start of handler
+if (!context.permissions.canUpdateFeature(feature, updates)) {
+  context.permissions.throwPermissionError();
+}
+
+// Bad - check after doing work
+const result = await expensiveOperation();
+if (!context.permissions.canUpdateFeature(feature, updates)) {
+  throw new Error("No permission");
+}
+```
+
+### 2. Use Specific Permission Methods
+
+```typescript
+// Good - use the specific method
+if (!permissionsUtil.canUpdateFeature(existing, updated)) {
+  return <NoAccess />;
+}
+
+// Bad - check raw permission without context
+if (!permissions.manageFeatures) {
+  return <NoAccess />;
+}
+```
+
+### 3. Pass Complete Objects for Update Checks
+
+```typescript
+// Good - pass both existing and updated states (merged object)
+const canUpdate = permissionsUtil.canUpdateFeature(existingFeature, {
+  ...existingFeature,
+  ...updates,
+});
+
+// Bad - passing partial updates without merging with existing state
+const canUpdate = permissionsUtil.canUpdateFeature(existingFeature, {
+  name: "new name", // Missing other fields from existingFeature
+});
+```
+
+### 4. Handle Both Permission and Feature Gates
+
+```typescript
+// Frontend
+const { hasCommercialFeature } = useUser();
+const permissionsUtil = usePermissionsUtil();
+
+const canAccess =
+  hasCommercialFeature("feature-name") && permissionsUtil.canDoSomething();
+
+// Backend
+if (!context.permissions.canDoSomething()) {
+  context.permissions.throwPermissionError();
+}
+if (!orgHasPremiumFeature(context.org, "feature-name")) {
+  throw new PlanDoesNotAllowError("Feature not available");
+}
+```
+
+### 5. Don't Hardcode Permission Logic
+
+```typescript
+// Good - use permission utilities
+if (!permissionsUtil.canManageSomeProjects()) {
+  return null;
+}
+
+// Bad - hardcode role checks
+if (user.role !== "admin" && user.role !== "engineer") {
+  return null;
+}
+```
+
+## Permission Definitions Location
+
+- Permission constants: `packages/shared/src/permissions/permissions.constants.ts`
+- Permission utilities: `packages/shared/src/permissions/permissions.utils.ts`
+- Permissions class: `packages/shared/src/permissions/permissionsClass.ts`
+- Frontend hooks: `packages/front-end/hooks/usePermissions.ts`, `usePermissionsUtils.ts`
+- Backend resolution: `packages/back-end/src/util/organization.util.ts`
diff --git a/.cursor/rules/project-overview.md b/.cursor/rules/project-overview.md
@@ -0,0 +1,62 @@
+---
+description: "GrowthBook project architecture, monorepo structure, and package organization"
+alwaysApply: true
+---
+
+# GrowthBook Project Overview
+
+You are working on GrowthBook, an open-source feature flagging and A/B testing platform.
+
+## Monorepo Structure
+
+- This is a monorepo managed by **pnpm workspaces**
+- Use `pnpm` for all package management operations (never npm or yarn)
+- Packages are located in the `packages/` directory
+
+## Package Organization
+
+### packages/front-end - Next.js application (UI)
+
+- Next.js app serving the full GrowthBook UI
+- Runs on http://localhost:3000 in development
+- TypeScript with React functional components
+- Uses path alias `@/` for imports (e.g., `@/components`, `@/services`, `@/ui`)
+
+### packages/back-end - Express API server
+
+- Runs on http://localhost:3100 in development
+- MongoDB as primary data store
+- Uses `back-end/` prefix for internal imports
+- Serves two distinct APIs:
+  1. **Internal API** - Used by the GrowthBook front-end application (controllers, routers in `src/controllers/`, `src/routers/`)
+  2. **External REST API** - Public API for customers to integrate with GrowthBook (located in `src/api/` directory)
+
+### packages/shared - Shared TypeScript code
+
+- Common types, utilities, validators, and constants
+- Shared between front-end and back-end
+- No UI components or server-specific code
+
+### packages/stats - Python statistics engine
+
+- Python 3.9+ package called `gbstats`
+- Managed by Poetry for dependencies
+- Statistical computations for A/B testing
+- Uses pandas, numpy, scipy
+
+### packages/sdk-js - JavaScript SDK
+
+- Published as `@growthbook/growthbook` on npm
+- Fully isolated from internal packages
+
+### packages/sdk-react - React SDK
+
+- Published as `@growthbook/growthbook-react` on npm
+- Fully isolated from internal packages
+
+## Enterprise Code
+
+- `packages/front-end/enterprise/` - Non-open source front-end features
+- `packages/back-end/src/enterprise/` - Non-open source back-end features
+- `packages/shared/src/enterprise/` - Non-open source shared code
+- Do NOT typically accept outside contributions to enterprise directories
PATCH

echo "Gold patch applied."
