#!/usr/bin/env bash
set -euo pipefail

cd /workspace/radzionkit

# Idempotency guard
if grep -qF ".cursor/rules/add-library.mdc" ".cursor/rules/add-library.mdc" && grep -qF "description: Use shouldBePresent() instead of optional chaining or default value" ".cursor/rules/assert.mdc" && grep -qF "description: USE attempt utility WHEN handling errors is necessary FOR user feed" ".cursor/rules/attempt-over-try-catch.mdc" && grep -qF ".cursor/rules/cusor-rules.mdc" ".cursor/rules/cusor-rules.mdc" && grep -qF "When creating Cursor rules for this TypeScript codebase, default to using file-s" ".cursor/rules/default-rule-scoping.mdc" && grep -qF "description: Use ESLint autofix (yarn) only for issues that ESLint can automatic" ".cursor/rules/eslint-autofix.mdc" && grep -qF "1. **Two obvious arguments**: When the function has exactly two parameters that " ".cursor/rules/functions.mdc" && grep -qF "description: Import path guidelines for monorepo packages - use relative paths w" ".cursor/rules/imports.mdc" && grep -qF "globs: *.ts,*.tsx" ".cursor/rules/package-manager.mdc" && grep -qF "description: Prefer writing self-documenting, readable code over adding explanat" ".cursor/rules/readable-code-over-comments.mdc" && grep -qF "description: Resolver pattern \u2013 how to design, name, type, and route resolvers (" ".cursor/rules/resolver-pattern.mdc" && grep -qF "description: Trust TS-defined values \u2013 avoid optional chaining and fallbacks whe" ".cursor/rules/trust-types-no-fallbacks.mdc" && grep -qF "Type checking takes time, so it should only be used when there's a reasonable li" ".cursor/rules/typecheck-guidance.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/add-library.mdc b/.cursor/rules/add-library.mdc
@@ -1,53 +0,0 @@
----
-description: USE package-specific installation WHEN adding dependencies in monorepo TO prevent root package bloat
-globs:
-alwaysApply: true
----
-
-# Monorepo Dependency Management
-
-## Context
-
-- When adding new dependencies to a monorepo project
-- Applies to all package installations using the project's package manager
-- Ensures dependencies are properly scoped to the packages that use them
-- Prevents dependency bloat in the root package.json
-
-## Requirements
-
-- Install dependencies in the specific package that will use them, not in the root package.json
-- Only add dependencies to the root package.json when they are genuinely needed across the entire codebase (rare)
-- Use the package manager commands with the appropriate path to the package's directory
-- When using workspaces, use the workspace-specific commands to add dependencies to individual packages
-
-## Examples
-
-<example>
-# Good: Adding a dependency to a specific package
-cd packages/my-package
-yarn add lodash
-
-# Or using workspace command (if using Yarn workspaces)
-
-yarn workspace my-package add lodash
-</example>
-
-<example type="invalid">
-# Bad: Adding a package-specific dependency to the root
-yarn add lodash
-</example>
-
-<example>
-# Good: Adding a development dependency to a specific package
-yarn workspace my-package add -D jest
-</example>
-
-<example type="invalid">
-# Bad: Adding a package-specific dev dependency to the root
-yarn add -D jest
-</example>
-
-<example>
-# Good: Adding a dependency that is genuinely used across the entire codebase to the root
-yarn add -W typescript
-</example>
diff --git a/.cursor/rules/assert.mdc b/.cursor/rules/assert.mdc
@@ -1,66 +1,46 @@
 ---
-description: Use assertions instead of optional chaining or default values when values should exist
+description: Use shouldBePresent() instead of optional chaining or default values for required values
 globs: *.ts,*.tsx
 alwaysApply: false
 ---
 
-# TypeScript Assertion Standards
-
-## Context
-- Use when working with values that should always be present
-- Applied in TypeScript and React files
-- Particularly important when dealing with configuration, API responses, and required object properties
+# Assertion Standards
 
 ## Requirements
-- Use `shouldBePresent()` when you expect a value to exist instead of default values
-- Use `assertField()` when checking object properties instead of optional chaining
+
+- Use `shouldBePresent()` for values that should always exist
 - Throw early and explicitly with clear error messages
-- Avoid propagating invalid states that can cause subtle runtime errors
-- Don't use assertions for truly optional values or external data you don't control
+- Avoid optional chaining and default values for required data
 
 ## Examples
 
 <example>
-// Asserting required configuration
+// Required configuration
 const config = {
   apiKey: shouldBePresent(process.env.API_KEY, 'API_KEY'),
   baseUrl: shouldBePresent(process.env.BASE_URL, 'BASE_URL')
 }
 </example>
 
 <example type="invalid">
-// Using default values for required data
+// Don't use defaults for required values
 const config = {
   apiKey: process.env.API_KEY || '',
   baseUrl: process.env.BASE_URL ?? 'http://localhost'
 }
 </example>
 
 <example>
-// Asserting required values
+// Nested required values
 const getUserName = (user: User) => {
   const profile = shouldBePresent(user.profile, 'user.profile')
   return shouldBePresent(profile.name, 'user.profile.name')
 }
 </example>
 
 <example type="invalid">
-// Optional chaining when value should exist
+// Don't use optional chaining for required values
 const getUserName = (user: User) => {
   return user?.profile?.name || 'Anonymous'
 }
 </example>
-
-<example>
-// Asserting required field
-const getBalance = (account: Account) => {
-  return assertField(account, 'balance')
-}
-</example>
-
-<example type="invalid">
-// Using default for required field
-const getBalance = (account: Account) => {
-  return account.balance ?? 0
-}
-</example>
\ No newline at end of file
diff --git a/.cursor/rules/attempt-over-try-catch.mdc b/.cursor/rules/attempt-over-try-catch.mdc
@@ -1,100 +1,52 @@
 ---
-description: USE attempt utility WHEN handling errors INSTEAD OF try-catch blocks TO ensure consistent error handling
+description: USE attempt utility WHEN handling errors is necessary FOR user feedback or alternative logic, NOT for logging
 globs: *.ts,*.tsx
 alwaysApply: false
 ---
+
 # Use attempt Utility Instead of try-catch
 
-## Context
-- Applies when handling errors in asynchronous or synchronous operations
-- The codebase provides a utility function [attempt.ts](mdc:lib/utils/attempt.ts) from `@lib/utils/attempt`
-- This utility provides a consistent way to handle errors with Result types
-- Eliminates the need for try-catch blocks and provides type-safe error handling
+## Core Rule
 
-## Requirements
-- NEVER use try-catch blocks for error handling
-- ALWAYS use the `attempt` utility from `@lib/utils/attempt`
-- Use pattern matching with 'data' in result or 'error' in result for type-safe error handling
-- Use `withFallback` when a default value is needed in case of error
-- Only use try-finally when resource cleanup is needed (e.g., closing connections)
+- **NEVER use try-catch blocks** for error handling
+- **ONLY use `attempt`** from `@lib/utils/attempt` when you need to:
+  - Show errors to users
+  - Execute alternative logic on failure
+  - Provide fallback values
+- **Let errors bubble up naturally** - don't wrap functions just to log errors
 
-## Examples
+## When to Use attempt
 
 <example>
-// Good: Using attempt for error handling
-import { attempt } from '@lib/utils/attempt'
-
-// For synchronous functions
-const result = await attempt<Data, Error>(async () => {
-  return await fetchData()
-})
-
+// ✅ Show error to user
+const result = await attempt(() => saveUserData(data))
 if ('data' in result) {
-  // Handle success case
-  processData(result.data)
+  showSuccessMessage()
 } else {
-  // Handle error case
-  logError(result.error)
+  showErrorToUser(result.error.message)
 }
 
-// Using withFallback for default values
-const data = withFallback(
-  attempt(() => parseJSON(data)),
-  defaultValue
-)
+// ✅ Alternative logic on failure
+const primaryResult = await attempt(() => fetchPrimary())
+const data = 'data' in primaryResult ? primaryResult.data : await fetchBackup()
 
-// Good: Using try-finally for resource cleanup
-let resource = null
-try {
-  resource = await createResource()
-  return await attempt(() => useResource(resource))
-} finally {
-  if (resource) {
-    await resource.close()
-  }
-}
+// ✅ Fallback values
+const prefs = withFallback(attempt(() => parsePrefs()), DEFAULT_PREFS)
 </example>
 
-<example type="invalid">
-// Bad: Using try-catch for error handling
-try {
-  const data = await fetchData()
-  processData(data)
-} catch (error) {
-  logError(error)
-}
+## When NOT to Use attempt
 
-// Bad: Using try-catch with type casting
-try {
-  const data = await fetchData()
-  processData(data)
-} catch (error: unknown) {
-  if (error instanceof Error) {
-    logError(error.message)
-  }
-}
+<example type="invalid">
+// ❌ Don't wrap just to log
+await trackAnalytics(event) // Let it throw naturally
 
-// Bad: Using try-catch-finally when only cleanup is needed
+// ❌ Never use try-catch
 try {
-  await doSomething()
+await fetchData()
 } catch (error) {
-  console.error(error)
-} finally {
-  cleanup()
+console.error(error) // Just logging - let it throw
 }
 
-// Instead, use:
-const result = await attempt(() => doSomething())
-cleanup()
-if ('error' in result) {
-  console.error(result.error)
-}
+// ❌ Don't wrap internal utilities
+await internalUtility() // Should throw on failure
 </example>
-
-## Benefits
-1. Type-safe error handling with discriminated unions
-2. Consistent error handling patterns across the codebase
-3. No need for type casting of errors
-4. Better error propagation
-5. Easier to test and maintain
-6. Eliminates common try-catch pitfalls
\ No newline at end of file
diff --git a/.cursor/rules/cusor-rules.mdc b/.cursor/rules/cusor-rules.mdc
@@ -1,95 +0,0 @@
----
-description: Use ALWAYS when asked to CREATE A RULE or UPDATE A RULE or taught a lesson from the user that should be retained as a new rule for Cursor
-globs: .cursor/rules/*.mdc
-alwaysApply: false
----
-# Cursor Rules Format
-## Core Structure
-
-```mdc
----
-description: ACTION when TRIGGER to OUTCOME
-globs: *.mdc
-alwaysApply: false
----
-
-# Rule Title
-
-## Context
-- When to apply this rule
-- Prerequisites or conditions
-
-## Requirements
-- Concise, actionable items
-- Each requirement must be testable
-
-## Examples
-<example>
-Good concise example with explanation
-</example>
-
-<example type="invalid">
-Invalid concise example with explanation
-</example>
-```
-
-## File Organization
-
-### Location
-- Path: `.cursor/rules/`
-- Extension: `.mdc`
-
-### Glob Pattern Examples
-Common glob patterns for different rule types:
-- Most often pattern would be `*.ts,*.tsx` as it's a typescript monorepo.
-
-## Required Fields
-
-### Frontmatter
-- description: ACTION TRIGGER OUTCOME format
-- globs: `glob pattern for files and folders`
-- alwaysApply: `true` or `false`
-
-### Body
-- context: Usage conditions
-- requirements: Actionable items
-- examples: Both valid and invalid
-
-## Formatting Guidelines
-
-- Use Concise Markdown primarily
-- XML tags limited to:
-  - <example>
-  - <danger>
-  - <required>
-  - <rules>
-  - <rule>
-  - <critical>
-- Always indent content within XML or nested XML tags by 2 spaces
-- Keep rules as short as possbile
-- Use Mermaid syntax if it will be shorter or clearer than describing a complex rule
-- Use Emojis where appropriate to convey meaning that will improve rule understanding by the AI Agent
-- Keep examples as short as possible to clearly convey the positive or negative example
-
-## AI Optimization Tips
-
-1. Use precise, deterministic ACTION TRIGGER OUTCOME format in descriptions
-2. Provide concise positive and negative example of rule application in practice
-3. Optimize for AI context window efficiency
-4. Remove any non-essential or redundant information
-5. Use standard glob patterns without quotes (e.g., *.js, src/**/*.ts)
-
-## AI Context Efficiency
-
-1. Keep frontmatter description under 120 characters (or less) while maintaining clear intent for rule selection by AI AGent
-2. Limit examples to essential patterns only
-3. Use hierarchical structure for quick parsing
-4. Remove redundant information across sections
-5. Maintain high information density with minimal tokens
-6. Focus on machine-actionable instructions over human explanations
-
-<critical>
-  - NEVER include verbose explanations or redundant context that increases AI token overhead
-  - Keep file as short and to the point as possible BUT NEVER at the expense of sacrificing rule impact and usefulness for the AI Agent.
-  - the front matter can ONLY have the fields description and globs.
-</critical>
diff --git a/.cursor/rules/default-rule-scoping.mdc b/.cursor/rules/default-rule-scoping.mdc
@@ -0,0 +1,50 @@
+---
+globs: *.mdc
+---
+
+# Default Rule Scoping Strategy
+
+## TypeScript Codebase Rule Targeting
+
+When creating Cursor rules for this TypeScript codebase, default to using file-specific targeting rather than descriptions or always-apply rules.
+
+## Default Approach
+
+- Use `globs: *.ts,*.tsx` for most coding standards and practices
+- Use `globs: *.tsx` for React-specific rules
+- Use `globs: *.ts` for non-React TypeScript rules
+- Use `alwaysApply: true` only for project-wide architectural guidance
+- Use `description:` for rules that need manual activation
+
+## Examples
+
+<example>
+```
+---
+globs: *.ts,*.tsx
+---
+# TypeScript coding standard that applies to all TS files
+```
+</example>
+
+<example>
+```
+---
+globs: *.tsx
+---
+# React component specific rule
+```
+</example>
+
+<example type="invalid">
+```
+---
+description: Some coding standard
+---
+# Should use globs instead for better targeting
+```
+</example>
+
+## Rationale
+
+File-specific targeting ensures rules are contextually relevant and reduces noise for the AI agent when working on specific file types.
diff --git a/.cursor/rules/eslint-autofix.mdc b/.cursor/rules/eslint-autofix.mdc
@@ -0,0 +1,26 @@
+---
+alwaysApply: true
+description: Use ESLint autofix (yarn) only for issues that ESLint can automatically fix, like import sorting; never sort imports manually.
+---
+
+# ESLint Autofix Workflow
+
+- **Use ESLint auto-fix only for issues that ESLint can automatically resolve**, such as import sorting. Do not sort imports manually.
+- **Check lint errors first** - only run autofix when ESLint indicates the issues are auto-fixable.
+- For issues that require manual fixes, address them directly in the code rather than relying on autofix.
+
+## Single file fixes
+
+Run from the repository root:
+
+```bash
+yarn eslint <path-to-file> --fix
+```
+
+## Multiple files
+
+If your changes affect multiple files, run from the repository root:
+
+```bash
+yarn lint:fix
+```
diff --git a/.cursor/rules/functions.mdc b/.cursor/rules/functions.mdc
@@ -7,17 +7,38 @@ alwaysApply: false
 # TypeScript Function Rules
 
 ## Context
+
 - Apply when writing TypeScript functions with multiple parameters
 - Applies to both function declarations and arrow function expressions
 - Aims to improve code maintainability and readability
 
 ## Requirements
-- Functions with more than 1 parameter must use an object parameter pattern
+
+- Functions with more than 1 parameter should generally use an object parameter pattern
 - Name input types with the pattern: `{FunctionName}Input`
 - For single parameters, direct arguments are acceptable
 - Object parameters should use destructuring in the function signature
 
+## Exceptions
+
+Direct multiple arguments are acceptable in these cases:
+
+1. **Two obvious arguments**: When the function has exactly two parameters that are very clear from context and it's unlikely a third parameter will be added
+2. **Required + optional props**: When the first argument is required and the second is optional configuration/props
+3. **Well-established patterns**: Functions following established API patterns (like DOM APIs, standard library functions)
+
+## When to Use Object Parameters
+
+Use object parameters when:
+
+- Function has 3+ parameters
+- Parameters are related configuration options
+- Function signature is likely to evolve with more parameters
+- Parameters have similar types that could be confused
+- The function is part of a public API
+
 ## Examples
+
 <example>
 // Good: Using object parameter for multiple parameters
 type UpdateNameInput = {
@@ -26,10 +47,10 @@ type UpdateNameInput = {
 }
 
 const updateName = ({
-  id,
-  newName
+id,
+newName
 }: UpdateNameInput) => {
-  // ...
+// ...
 }
 </example>
 
@@ -41,8 +62,30 @@ const getUser = (id: string) => {
 </example>
 
 <example type="invalid">
-// Bad: Multiple direct parameters
+// Bad: Multiple direct parameters (when object parameters would be better)
 const updateName = (id: string, newName: string) => {
   // ...
 }
-</example>
\ No newline at end of file
+</example>
+
+<example>
+// Acceptable: Two obvious arguments with clear context
+const setTimeout = (callback: () => void, delay: number) => {
+  // Very clear what callback and delay are, unlikely to add more params
+}
+
+const arrayIndexOf = (array: any[], item: any) => {
+// Clear relationship between array and item, unlikely to change
+}
+</example>
+
+<example>
+// Acceptable: Required argument + optional configuration
+const createElement = (tagName: string, options?: { className?: string; id?: string }) => {
+  // First arg required, second is optional configuration object
+}
+
+const fetchData = (url: string, config?: RequestInit) => {
+// URL is required, config is optional standard pattern
+}
+</example>
diff --git a/.cursor/rules/imports.mdc b/.cursor/rules/imports.mdc
@@ -1,33 +1,44 @@
 ---
-description: 
+description: Import path guidelines for monorepo packages - use relative paths within packages, absolute paths for cross-package imports
 globs: *.tsx,*.ts
 alwaysApply: false
 ---
+
 # Monorepo Package Imports
 
 ## Context
+
 - When importing files from other packages in the monorepo
 - Applies to all TypeScript and TypeScript React files in the project
 - This is a monorepo with packages
 
 ## Requirements
-- Always use proper package paths (not relative paths) when importing from the state directory
-- Use package-based imports from package.json names
-- Do not use relative path imports like '../../../../state/isInitiatingDevice'
+
+- Use relative paths when importing within the same package
+- Always use absolute package paths (not relative paths) when importing from a different package
+- Use package-based imports from package.json names for cross-package imports
+- Do not use relative path imports like '../../../../state/isInitiatingDevice' for cross-package imports
 - Maintain consistency with monorepo package structure
 
 ## Examples
+
 <example>
-// Good: Using package path
+// Good: Relative import within same package
+import { Button } from '../components/Button'
+import { useState } from './hooks/useState'
+</example>
+
+<example>
+// Good: Absolute package import for cross-package imports
 import { useIsInitiatingDevice } from '@your-org/ui/state/isInitiatingDevice'
 </example>
 
 <example type="invalid">
-// Bad: Using relative path
+// Bad: Relative path for cross-package import
 import { useIsInitiatingDevice } from '../../../../state/isInitiatingDevice'
 </example>
 
 <example>
-// Good: Using proper package import
+// Good: Using proper package import for cross-package dependencies
 import { useIsInitiatingDevice } from '@your-package/ui/state/isInitiatingDevice'
-</example> 
\ No newline at end of file
+</example>
diff --git a/.cursor/rules/package-manager.mdc b/.cursor/rules/package-manager.mdc
@@ -1,39 +1,46 @@
 ---
 description: USE specified package manager WHEN managing dependencies TO ensure consistent dependency resolution
-globs: 
+globs: *.ts,*.tsx
 alwaysApply: true
 ---
 
 # Package Manager Selection Rules
 
 ## Context
+
 - Applies when installing, updating, or removing dependencies
 - Applies when running package scripts
 - Based on the project's packageManager field in package.json
 - Currently, this project uses yarn@4.7.0 as specified in package.json
 - Consistent package manager usage prevents lock file conflicts and ensures reliable dependency resolution
 
 ## Requirements
+
 - Always use the package manager specified in the root package.json's packageManager field
 - Do not use other package managers unless the packageManager field is updated
 - Use the correct command equivalents based on the specified package manager
 
 ## Examples
+
 <example>
 # If package.json specifies yarn (current configuration)
 # Installing a package
 yarn add react
 
 # Installing a dev dependency
+
 yarn add -D eslint
 
 # Removing a package
+
 yarn remove lodash
 
 # Installing all dependencies
+
 yarn
 
 # Running a script
+
 yarn build
 </example>
 
@@ -46,9 +53,10 @@ npm install
 npm run build
 
 # Using pnpm when package.json specifies yarn
+
 pnpm add react
 pnpm add -D eslint
 pnpm remove lodash
 pnpm install
 pnpm run build
-</example>
\ No newline at end of file
+</example>
diff --git a/.cursor/rules/readable-code-over-comments.mdc b/.cursor/rules/readable-code-over-comments.mdc
@@ -0,0 +1,68 @@
+---
+description: Prefer writing self-documenting, readable code over adding explanatory comments. Add comments only when absolutely necessary for complex business logic or non-obvious decisions.
+globs: *.tsx,*.ts
+alwaysApply: false
+---
+
+# Readable Code Over Comments
+
+## Principle
+
+Write self-documenting, readable code instead of adding explanatory comments. Add comments only when absolutely necessary.
+
+## When Comments Are Necessary
+
+- Complex business logic that isn't obvious from the code
+- Non-obvious algorithmic decisions or optimizations
+- Public API documentation
+- Temporary workarounds or TODOs with context
+- Legal notices or license headers
+
+## When Comments Are Unnecessary
+
+- Explaining what the code does (code should be self-explanatory)
+- Restating variable or function names
+- Obvious operations or standard patterns
+- Redundant information already clear from types
+
+## Examples
+
+<example>
+```typescript
+// Good: Self-documenting code
+const isActiveUser = user.status === 'active'
+const userEmail = user.contactInfo.email
+const processedData = transformUserData(user, options)
+```
+</example>
+
+<example type="invalid">
+```typescript
+// Bad: Useless comments
+// Check if user is active
+const isActiveUser = user.status === 'active'
+// Get user's email address
+const userEmail = user.contactInfo.email
+// Process the user data
+const processedData = transformUserData(user, options)
+```
+</example>
+
+<example>
+```typescript
+// Good: Comment for non-obvious business logic
+// Use base64 encoding for data transmission to ensure compatibility with legacy systems
+// that don't support binary data in JSON payloads
+return {
+  encoding: 'base64',
+  data: encodeToBase64(processedData)
+}
+```
+</example>
+
+## Guidelines
+
+- Use descriptive variable and function names
+- Extract complex logic into well-named functions
+- Prefer clear code structure over explanatory comments
+- Use TypeScript types to document interfaces and contracts
diff --git a/.cursor/rules/resolver-pattern.mdc b/.cursor/rules/resolver-pattern.mdc
@@ -0,0 +1,195 @@
+---
+globs: *.ts,*.tsx
+description: Resolver pattern – how to design, name, type, and route resolvers (index.ts/resolver.ts/resolvers/*) with discriminants. Aligns with assert, pattern-matching, functions, attempt-over-try-catch, and type-definitions rules.
+---
+
+## Resolver Pattern Guide
+
+Build logic as small, composable resolvers and a single router instead of switch/case. Each resolver set handles one responsibility.
+
+### When to use
+
+- Routing work by a discriminant (a property that determines which logic to execute):
+  - Environment type (development, staging, production)
+  - Platform type (web, mobile, desktop)
+  - Service provider (AWS, GCP, Azure)
+  - API version or format
+  - Feature flags or configuration variants
+- A single operation that varies by the chosen discriminant
+
+### Files and layout
+
+- index.ts: Main exported function. Extract discriminant, select resolver, delegate.
+- resolver.ts: Exports the resolver type(s) and input/output types using `type` per type-definitions.
+- resolvers/: One file per routing value. Each exports a single, fully named resolver function.
+- supported.ts (optional): Lists supported discriminant values for this operation.
+
+Folder example:
+
+```
+<feature>/
+  index.ts
+  resolver.ts
+  resolvers/
+    development.ts
+    staging.ts
+    production.ts
+    ...
+  [supported.ts]
+```
+
+### Naming conventions
+
+- Resolver file names match the routing value (e.g., `development.ts`, `web.ts`, `aws.ts`).
+- Resolver function names include the full operation name and routing value for clarity, e.g., `getDevelopmentConfig`, `processWebRequest`, `deployAwsService`.
+- For API-style modules without a natural routing key, resolver files should use a full, descriptive name.
+
+### Router implementation patterns
+
+1. Route by discriminant
+
+```ts
+import { getDiscriminantValue } from './utils'
+
+import { SomeResolver } from './resolver'
+import { getDevelopmentX } from './resolvers/development'
+import { getStagingX } from './resolvers/staging'
+import { getProductionX } from './resolvers/production'
+
+const resolvers: Record<EnvironmentType, SomeResolver<any>> = {
+  development: getDevelopmentX,
+  staging: getStagingX,
+  production: getProductionX,
+}
+
+export const doX: SomeResolver = async (input) =>
+  resolvers[getDiscriminantValue(input)](input)
+```
+
+2. Route a supported subset and validate
+
+```ts
+import { getDiscriminantValue } from './utils'
+
+import { SupportedType, supportedTypes } from './supported'
+import { SomeResolver } from './resolver'
+import { getWebX } from './resolvers/web'
+import { getMobileX } from './resolvers/mobile'
+
+const resolvers: Record<SupportedType, SomeResolver<any>> = {
+  web: getWebX,
+  mobile: getMobileX,
+}
+
+export const doX: SomeResolver = async (input) => {
+  const discriminant = getDiscriminantValue(input)
+  if (!supportedTypes.includes(discriminant)) {
+    throw new Error(
+      `Unsupported doX type: ${discriminant}, should be one of ${supportedTypes.join(', ')}`,
+    )
+  }
+  return resolvers[discriminant](input)
+}
+```
+
+### Resolver typing (resolver.ts)
+
+- Use `type` for object types and generics.
+- Follow functions rule: use object params when there is more than one parameter.
+
+```ts
+// Generic resolver type - replace with your actual resolver utility
+export type Resolver<TInput, TOutput> = (input: TInput) => TOutput
+
+export type DoXInput<T extends DiscriminantType = DiscriminantType> = {
+  discriminant: T
+  // other fields...
+}
+
+export type DoXResolver<T extends DiscriminantType = DiscriminantType> =
+  Resolver<DoXInput<T>, Promise<OutputType>>
+```
+
+### Implementation guidelines
+
+- Assertions: Use assertion utilities (like `shouldBePresent()`, `assertField()`) over optional chaining when values must exist (assert rule).
+- Pattern matching: Prefer pattern matching utilities and record lookups over switch/case (pattern-matching rule).
+- Error handling: Use error handling utilities only when you must show errors to users or pursue alternative logic (attempt-over-try-catch rule).
+- Function params: If you need more than one parameter, use an object parameter with a `{FunctionName}Input` type (functions rule).
+- Imports: Use consistent import paths according to your project's conventions.
+- Types: Use `type` for object types and unions (type-definitions rule).
+
+### Common use cases
+
+- Environment-based routing: Different logic for development, staging, production
+- Platform-based routing: Different implementations for web, mobile, desktop
+- Provider-based routing: Different services for AWS, GCP, Azure
+- Version-based routing: Different behavior for API v1, v2, v3
+- Feature flag routing: Different logic when features are enabled/disabled
+
+### Template – scaffold a new resolver set
+
+1. Create `resolver.ts` with typed input/output:
+
+```ts
+// resolver.ts
+export type Resolver<TInput, TOutput> = (input: TInput) => TOutput
+
+export type ProcessDataInput<T extends Environment = Environment> = {
+  environment: T
+  data: string
+  // other fields...
+}
+
+export type ProcessDataResolver<T extends Environment = Environment> = Resolver<
+  ProcessDataInput<T>,
+  Promise<ProcessedData>
+>
+```
+
+2. Add resolvers under `resolvers/` named by routing value, with fully named functions:
+
+```ts
+// resolvers/development.ts
+import { ProcessDataResolver } from '../resolver'
+
+export const processDevelopmentData: ProcessDataResolver<
+  'development'
+> = async (input) => {
+  // Development-specific logic
+  return processData(input)
+}
+```
+
+3. Implement `index.ts` router:
+
+```ts
+// index.ts
+import { ProcessDataResolver } from './resolver'
+import { processDevelopmentData } from './resolvers/development'
+import { processStagingData } from './resolvers/staging'
+import { processProductionData } from './resolvers/production'
+
+const resolvers: Record<Environment, ProcessDataResolver<any>> = {
+  development: processDevelopmentData,
+  staging: processStagingData,
+  production: processProductionData,
+}
+
+export const processData: ProcessDataResolver = async (input) => {
+  return resolvers[input.environment](input)
+}
+```
+
+4. If operation supports only a subset, add validation in the router.
+
+### Checklist
+
+- Single responsibility: One operation per resolver set.
+- Strong types in `resolver.ts` with `type`, not `interface`.
+- Router uses a typed `Record` map; no `switch`.
+- Enforce supported discriminants with validation when necessary.
+- Use assertion utilities for required values.
+- Use error handling utilities only when alternative logic or user-facing errors are needed.
+- Use object parameters for multi-arg functions.
+- Use consistent import paths according to your project's conventions.
diff --git a/.cursor/rules/trust-types-no-fallbacks.mdc b/.cursor/rules/trust-types-no-fallbacks.mdc
@@ -0,0 +1,27 @@
+---
+globs: *.ts,*.tsx
+description: Trust TS-defined values – avoid optional chaining and fallbacks when types guarantee presence
+---
+
+## Trust TypeScript – No Fallbacks for Defined Values
+
+When a value's type is non-optional, use it directly. Do not add optional chaining or fallback values.
+
+Do:
+
+```ts
+const { requestOrigin } = usePopupContext()
+useIt(requestOrigin)
+```
+
+Don't:
+
+```ts
+const ctx = usePopupContext()
+useIt(ctx?.requestOrigin || '')
+```
+
+Notes:
+
+- If a value may be missing, validate earlier and fail fast (e.g., assertions in @rules).
+- Do not silence type guarantees with `?.`, `||`, or `??` when the type is non-optional.
diff --git a/.cursor/rules/typecheck-guidance.mdc b/.cursor/rules/typecheck-guidance.mdc
@@ -0,0 +1,41 @@
+---
+globs: *.tsx,*.ts
+alwaysApply: false
+---
+
+# TypeScript Type Checking Guidance
+
+## When to Run Type Checking
+
+Only run `yarn typecheck` from the root of the codebase when making changes that are **likely to affect other parts of the codebase**.
+
+### High-Risk Changes (Run typecheck)
+
+- Modifying shared types, interfaces, or utility functions
+- Adding new dependencies or changing import/export structures
+- Refactoring that spans multiple files
+- Changes to core infrastructure or shared components
+- Modifying function signatures or return types that are used elsewhere
+- Changes to public APIs or contracts between modules
+
+### Low-Risk Changes (Skip typecheck)
+
+- Simple translation updates or i18n changes
+- Styling or CSS-only modifications
+- Single-file component updates that don't change interfaces
+- Adding new isolated components
+- Minor bug fixes within a single file
+- Documentation updates
+- Configuration changes that don't affect types
+
+## Command
+
+When type checking is needed, run from the repository root:
+
+```bash
+yarn typecheck
+```
+
+## Rationale
+
+Type checking takes time, so it should only be used when there's a reasonable likelihood that changes could introduce type errors in other parts of the codebase. For isolated changes, the time investment is not justified.
PATCH

echo "Gold patch applied."
