#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ship

# Idempotency guard
if grep -qF "Shared Prettier config in [packages/prettier-config/index.js](mdc:packages/prett" "template/.cursor/rules/code-quality.mdc" && grep -qF "description: Guidelines for pnpm workspace management, installing packages and w" "template/.cursor/rules/package-management.mdc" && grep -qF "**Important**: Always import from `types`, not `app-types`. The API application " "template/.cursor/rules/shared-packages.mdc" && grep -qF "Validation-related constants in [packages/app-constants/src/validation.constants" "template/.cursor/rules/validation-schemas.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/template/.cursor/rules/code-quality.mdc b/template/.cursor/rules/code-quality.mdc
@@ -0,0 +1,147 @@
+---
+alwaysApply: true
+---
+
+# Code Quality and Style Guidelines
+
+## Linting and Formatting
+
+### ESLint
+
+Shared ESLint configuration in [packages/eslint-config/](mdc:packages/eslint-config/):
+- `node.js` - For API and Node.js packages
+- `next.js` - For Next.js web application
+
+Run ESLint:
+```bash
+# Per workspace, fix issues automatically
+pnpm --filter api eslint
+pnpm --filter web eslint
+```
+
+### Prettier
+
+Shared Prettier config in [packages/prettier-config/index.js](mdc:packages/prettier-config/index.js)
+
+Run Prettier:
+```bash
+pnpm --filter api prettier
+pnpm --filter web prettier
+```
+
+## Pre-commit Hooks
+
+Husky + lint-staged configured at root:
+- Run script: `pnpm prepare` (runs automatically after install)
+
+Each workspace has lint-staged configuration in their package.json
+
+Run precommit manually:
+```bash
+pnpm --filter api precommit
+pnpm --filter web precommit
+```
+
+## Code Organization
+
+### Import Sorting
+
+After implementing a feature, run ESLint to automatically sort and organize imports:
+```bash
+pnpm --filter api eslint
+pnpm --filter web eslint
+```
+
+ESLint is configured to automatically organize imports in the following order:
+1. External dependencies (React, Next.js, third-party packages)
+2. Internal packages (app-constants, app-types, schemas, etc.)
+3. Local imports (relative paths)
+
+The import sorting happens automatically during:
+- Pre-commit hooks (via lint-staged)
+- Running `eslint . --fix` manually
+- IDE auto-fix on save (if configured)
+
+### File Naming
+
+- **API**: Use kebab-case for files (e.g., `user.service.ts`, `auth.middleware.ts`)
+- **Web**: Use kebab-case for files (e.g., `index.page.tsx`, `user.api.ts`)
+- **Components**: PascalCase for directories and files (e.g., `Button/index.tsx`)
+- **Types/Interfaces**: PascalCase with descriptive names
+- **Constants**: SCREAMING_SNAKE_CASE
+
+### Export Patterns
+
+Prefer named exports over default exports, except for:
+- Next.js pages (require default export)
+- React components (can use either, but be consistent)
+
+Use barrel exports (index.ts) for cleaner imports:
+```typescript
+// components/index.ts
+export { Button } from './Button';
+export { Input } from './Input';
+
+// Usage
+import { Button, Input } from 'components';
+```
+
+## Error Handling
+
+### API
+
+- Throw descriptive errors that will be caught by error middleware
+- Use appropriate HTTP status codes
+- Include error context
+
+### Web
+
+- Use try-catch with the error handler utility
+- Show user-friendly messages via notifications
+- Log errors to analytics if needed
+
+## Comments and Documentation
+
+- Write self-documenting code with clear variable and function names
+- Add comments for complex business logic
+- Document non-obvious behavior
+- Use JSDoc for public APIs and complex functions
+
+## Performance Best Practices
+
+### API
+- Use MongoDB indexes for frequently queried fields
+- Cache expensive operations in Redis
+- Use pagination for list endpoints
+- Avoid N+1 queries
+
+### Web
+- Use React.memo for expensive components
+- Implement code splitting with dynamic imports
+- Optimize images (use Next.js Image component)
+- Use React Query's caching effectively
+- Memoize expensive calculations with useMemo/useCallback
+
+## Security Best Practices
+
+### API
+- Validate all input with Zod schemas
+- Use rate limiting middleware when applicable
+- Sanitize user input
+- Use secure password hashing (argon2)
+- Implement CORS properly
+- Don't include sensitive data in response
+
+
+### Web
+- Sanitize HTML with DOMPurify before rendering
+- Don't expose sensitive data in client code
+- Implement CSRF protection for forms
+- Don't store sensitive data in localStorage
+
+## Typescript
+- Always use TypeScript strict mode (enabled in all tsconfig.json files)
+- Prefer explicit types over `any`
+- Use type inference where appropriate to reduce verbosity
+- Export types and interfaces from shared packages when used across apps
+
diff --git a/template/.cursor/rules/package-management.mdc b/template/.cursor/rules/package-management.mdc
@@ -0,0 +1,44 @@
+---
+description: Guidelines for pnpm workspace management, installing packages and workspace dependencies
+alwaysApply: false
+---
+# Package Management Rules
+
+## Package Manager: pnpm
+
+This project uses **pnpm** as the package manager. Never use npm or yarn.
+
+### Installing Packages
+
+**Always use the workspace filter flag when adding packages to specific apps or packages.**
+
+Examples:
+```bash
+# Add a package to the api app
+pnpm add stripe --filter api
+
+# Add a dev dependency to the web app
+pnpm add -D @types/lodash --filter web
+
+# Add a package to a shared package
+pnpm add lodash --filter app-constants
+
+# Add a package to all workspaces
+pnpm add -w zod
+
+# Add a package to the root workspace
+pnpm add -w -D husky
+```
+
+### Workspace Dependencies
+
+When referencing internal packages, use the `workspace:*` protocol in package.json:
+```json
+{
+  "dependencies": {
+    "app-constants": "workspace:*",
+    "app-types": "workspace:*",
+    "schemas": "workspace:*"
+  }
+}
+```
diff --git a/template/.cursor/rules/shared-packages.mdc b/template/.cursor/rules/shared-packages.mdc
@@ -0,0 +1,274 @@
+---
+description: Guidelines for working with shared packages
+alwaysApply: false
+---
+# Shared Packages Guidelines
+
+The `packages/` directory contains reusable code shared between `api` and `web` applications.
+
+## Available Packages
+
+### app-constants
+[packages/app-constants/src/](mdc:packages/app-constants/src/)
+
+Shared constants used across applications.
+
+Usage:
+```typescript
+import { API_ROUTES, COOKIES, FILE } from 'app-constants';
+```
+
+### app-types
+[packages/app-types/src/](mdc:packages/app-types/src/)
+
+Shared TypeScript type definitions and enums (re-exported to prevent dependency cycles).
+
+**Important**: Always import from `types`, not `app-types`. The API application has a local `types.ts` file that stores API-specific types which cannot be used by the Web application. Using `types` as the import path prevents conflicts.
+
+Usage:
+```typescript
+// ✅ Correct - import from 'types'
+import { User, Account, ListParams, TokenType } from 'types';
+
+// ❌ Incorrect - don't use 'app-types'
+import { User } from 'app-types';
+```
+
+### enums
+[packages/enums/src/](mdc:packages/enums/src/)
+
+Shared enumerations:
+- `token.enum.ts` - Token types enum
+
+**Important**: To prevent dependency cycle issues, import enums from the `types` package instead of `enums`. The `app-types` package re-exports all enums to break circular dependencies.
+
+Usage:
+```typescript
+// ✅ Correct - import from 'types'
+import { TokenType } from 'types';
+
+// ❌ Incorrect - don't import directly from 'enums'
+import { TokenType } from 'enums';
+```
+
+### schemas
+[packages/schemas/src/](mdc:packages/schemas/src/)
+
+Zod validation schemas shared between API and web for type-safe validation:
+- `common.schema.ts` - Reusable schema components
+- `db.schema.ts` - Database-specific schemas (contains base database entity schema)
+
+**Important**: When creating a new database resource schema, always extend from `dbSchema` to include common database fields (`_id`, `createdOn`, `updatedOn`, etc.):
+
+```typescript
+import { z } from 'zod';
+
+import { dbSchema } from './db.schema';
+
+export const userSchema = dbSchema.extends({
+  name: z.string().min(1),
+  email: z.string().email(),
+});
+```
+
+See [validation-schemas.mdc](mdc:.cursor/rules/validation-schemas.mdc) for detailed usage.
+
+### mailer
+[packages/mailer/](mdc:packages/mailer/)
+
+Email templates built with React Email:
+- `emails/` - React email components
+- `src/template.ts` - Template registry (enum, component mapping, props types)
+- `src/utils.tsx` - Email utilities
+
+Email templates:
+- `sign-up-welcome.tsx` - Welcome email
+- `verify-email.tsx` - Email verification
+- `reset-password.tsx` - Password reset
+
+#### Adding a New Email Template
+
+**Step 1**: Create email template in [packages/mailer/emails/](mdc:packages/mailer/emails/) folder
+```tsx
+// packages/mailer/emails/my-template.tsx
+export interface MyTemplateProps {
+  firstName: string;
+  actionUrl: string;
+}
+
+export const MyTemplate = ({ firstName, actionUrl }: MyTemplateProps) => (
+  <Layout previewText="Greeting">
+    <Text>Hello, {firstName}!</Text>
+    <Button href={actionUrl}>Take Action</Button>
+  </Layout>
+);
+```
+
+**Step 2**: Register template in [packages/mailer/src/template.ts](mdc:packages/mailer/src/template.ts)
+```typescript
+// Add to Template enum
+export enum Template {
+  MY_TEMPLATE = 'MY_TEMPLATE',
+  // ... other templates
+}
+
+// Add to EmailComponent mapping
+export const EmailComponent = {
+  [Template.MY_TEMPLATE]: MyTemplate,
+  // ... other templates
+};
+
+// Add to TemplateProps interface
+export interface TemplateProps {
+  [Template.MY_TEMPLATE]: MyTemplateProps;
+  // ... other templates
+}
+```
+
+**Step 3**: Use in API with emailService
+```typescript
+import { emailService } from 'services';
+import { Template } from 'mailer';
+
+await emailService.sendTemplate<Template.MY_TEMPLATE>({
+  to: user.email,
+  subject: 'Action Required',
+  template: Template.MY_TEMPLATE,
+  params: {
+    firstName: user.firstName,
+    actionUrl: resetUrl.toString(),
+  },
+});
+```
+
+### eslint-config
+[packages/eslint-config/](mdc:packages/eslint-config/)
+
+Shared ESLint configurations:
+- `node.js` - For Node.js/API code
+- `next.js` - For Next.js/React code
+
+Usage in app's `eslint.config.js`:
+```javascript
+import config from 'eslint-config/node.js';
+// or
+import config from 'eslint-config/next.js';
+
+export default config;
+```
+
+### prettier-config
+[packages/prettier-config/](mdc:packages/prettier-config/)
+
+Shared Prettier configuration.
+
+Usage in app's `.prettierrc.json`:
+```json
+"prettier-config"
+```
+
+### tsconfig
+[packages/tsconfig/](mdc:packages/tsconfig/)
+
+Shared TypeScript configurations:
+- `base.json` - Base config
+- `nodejs.json` - Node.js specific settings
+- `nextjs.json` - Next.js specific settings
+
+Usage in app's `tsconfig.json`:
+```json
+{
+  "extends": "tsconfig/nodejs.json"
+}
+```
+
+## Package Development Guidelines
+
+### Exports
+- Always export through an `index.ts` barrel file
+- Use named exports for better tree-shaking
+- Export types separately when possible
+
+### Dependencies
+- Minimize dependencies in shared packages
+- Use peer dependencies for framework-specific packages
+- Common dependencies should use the catalog version
+
+### TypeScript
+- Extend from `tsconfig/base.json`
+- Enable strict mode
+- Export types alongside runtime code
+
+### Versioning
+- Keep versions in sync (use same version across packages)
+- Update version when making breaking changes
+- Document changes if creating a changelog
+
+## Common Patterns
+
+### Constants Package
+```typescript
+// 1. Define in packages/app-constants/src/feature.constants.ts
+export const FEATURE = {
+  MAX_ITEMS: 100,
+  DEFAULT_TIMEOUT: 5000,
+} as const;
+
+// 2. Export from packages/app-constants/src/index.ts
+export * from './feature.constants';
+
+// 3. Consume
+import { FEATURE } from 'app-constants';
+```
+
+### Types Package
+```typescript
+// 1. Define in packages/app-types/src/feature.types.ts
+export interface Feature {
+  id: string;
+  name: string;
+}
+
+export type FeatureList = Feature[];
+
+// 2. Export from packages/app-types/src/index.ts
+export * from './feature.types';
+
+// 3. Consume - always use 'types' not 'app-types'
+import { Feature } from 'types';
+```
+
+### Enums Pattern
+```typescript
+// 1. Define in packages/enums/src/feature.enum.ts
+export enum FeatureType {
+  TypeA = 'type-a',
+  TypeB = 'type-b',
+}
+
+// 2. Export from packages/enums/src/index.ts
+export * from './feature.enum';
+
+// 3. Consume from 'types' (already re-exported in app-types)
+import { FeatureType } from 'types';
+```
+
+**Note**: All enums are automatically re-exported from the `app-types` package, so you don't need to manually add re-exports there.
+
+### Schemas Package
+```typescript
+// 1. Define in packages/schemas/src/feature.schema.ts
+import { z } from 'zod';
+
+export const featureSchema = {
+  create: z.object({
+    name: z.string().min(1),
+  }),
+};
+
+// 2. Export from packages/schemas/src/index.ts
+export * from './feature.schema';
+
+// 3. Consume
+import { featureSchema } from 'schemas';
+```
diff --git a/template/.cursor/rules/validation-schemas.mdc b/template/.cursor/rules/validation-schemas.mdc
@@ -0,0 +1,139 @@
+---
+description: "Guidelines for using and creating Zod validation schemas"
+---
+
+# Validation and Schema Guidelines
+
+## Zod Schemas Package
+
+All validation schemas are centralized in the `schemas` package: [packages/schemas/src/](mdc:packages/schemas/src/)
+
+This ensures type-safe validation shared between API and web applications.
+
+## Using Schemas
+
+Import schemas from the `schemas` package:
+```typescript
+import { userSchema, accountSchema, commonSchema } from 'schemas';
+```
+## API Validation
+
+Use the validate middleware in the API:
+```typescript
+import { validateMiddleware } from 'middlewares';
+
+import { createUserSchema } from 'schemas';
+
+router.post('/users',
+  validateMiddleware(createUserSchema),
+  handler
+);
+```
+
+The middleware validates:
+- `ctx.request.body` - Request body
+- `ctx.request.files` - Uploaded formidable files
+- `ctx.query` - Query parameters
+- `ctx.params` - URL parameters  
+
+## Web/Frontend Validation
+
+### With React Hook Form
+
+```typescript
+import { useForm } from 'react-hook-form';
+import { zodResolver } from '@hookform/resolvers/zod';
+
+import { createUserSchema } from 'schemas';
+import { CreateUserSchema } from 'types';
+
+const form = useForm<CreateUserSchema>({
+  resolver: zodResolver(createUserSchema),
+});
+```
+
+### Manual Validation
+
+```typescript
+import { createUserSchema } from 'schemas';
+
+const result = createUserSchema.safeParse(data);
+
+if (!result.success) {
+  console.error(result.error.errors);
+}
+```
+
+## Creating New Schemas
+
+When adding new schemas:
+
+1. Add to the appropriate file in `packages/schemas/src/`
+2. Export from [packages/schemas/src/index.ts](mdc:packages/schemas/src/index.ts)
+3. Use Zod's built-in validators and composability
+
+Example structure:
+```typescript
+import { z } from 'zod';
+
+import { dbSchema } from './db.schema';
+
+export const userSchema = dbSchema.extend({
+  firstName: z.string(),
+  lastName: z.string(),
+  email: z.string().email(),
+  passwordHash: z.string().optional(),
+});
+
+// Compose schemas (mostly based on entity schema)
+export const createUserSchema = userSchema.pick({
+  firstName: true,
+  lastName: true,
+  email: true,
+});
+
+export const updateUserSchema = userSchema
+  .pick({ firstName: true, lastName: true })
+  .extend({
+    password: userSchema.shape.passwordHash.optional(),
+  })
+  .partial();
+```
+
+## Enums in Schemas
+
+Enums are centralized in [packages/enums/src/](mdc:packages/enums/src/). Use `z.nativeEnum()` for validation:
+
+```typescript
+import { TokenType } from 'enums';
+
+export const tokenSchema = dbSchema.extend({
+  type: z.nativeEnum(TokenType),
+});
+```
+
+When creating new enums, add to `packages/enums/src/*.enum.ts` and export from index:
+```typescript
+export enum TokenType {
+  ACCESS = 'access',
+  RESET_PASSWORD = 'reset-password',
+}
+```
+
+## Type Inference
+
+Extract TypeScript types from Zod schemas:
+```typescript
+import { z } from 'zod';
+
+import { createUserSchema, updateUserSchema } from 'schemas';
+
+type CreateUser = z.infer<typeof createUserSchema>;
+type UpdateUser = z.infer<typeof updateUserSchema>;
+```
+
+For API types, consider adding to [packages/app-types/](mdc:packages/app-types/) if used across applications.
+
+## Constants
+
+Validation-related constants in [packages/app-constants/src/validation.constants.ts](mdc:packages/app-constants/src/validation.constants.ts)
PATCH

echo "Gold patch applied."
