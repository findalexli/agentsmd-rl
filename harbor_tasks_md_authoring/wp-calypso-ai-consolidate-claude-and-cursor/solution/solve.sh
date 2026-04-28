#!/usr/bin/env bash
set -euo pipefail

cd /workspace/wp-calypso

# Idempotency guard
if grep -qF ".claude/rules/e2e-testing.md" ".claude/rules/e2e-testing.md" && grep -qF ".cursor/rules/a4a.mdc" ".cursor/rules/a4a.mdc" && grep -qF ".cursor/rules/calypso-client.mdc" ".cursor/rules/calypso-client.mdc" && grep -qF ".cursor/rules/dashboard.mdc" ".cursor/rules/dashboard.mdc" && grep -qF "CLAUDE.md" "CLAUDE.md" && grep -qF "client/AGENTS.md" "client/AGENTS.md" && grep -qF "client/CLAUDE.md" "client/CLAUDE.md" && grep -qF "client/a8c-for-agencies/AGENTS.md" "client/a8c-for-agencies/AGENTS.md" && grep -qF "client/a8c-for-agencies/CLAUDE.md" "client/a8c-for-agencies/CLAUDE.md" && grep -qF "- **Purpose**: Ensures proper environment configuration (dev vs production hostn" "client/dashboard/AGENTS.md" && grep -qF "client/dashboard/CLAUDE.md" "client/dashboard/CLAUDE.md" && grep -qF "- docs-new/ - New Playwright Test framework documentation" "test/e2e/AGENTS.md" && grep -qF "test/e2e/CLAUDE.md" "test/e2e/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/rules/e2e-testing.md b/.claude/rules/e2e-testing.md
@@ -1,192 +0,0 @@
----
-paths:
-  - "test/e2e/**"
----
-# E2E Test Framework Instructions
-
-## Documentation
-
-Full documentation is available in:
-- @test/e2e/docs/ - Legacy framework documentation
-- @test/e2e/docs-new/ - New Playwright Test framework documentation
-
-Key docs to reference:
-- [Overview](test/e2e/docs-new/overview.md)
-- [Setup](test/e2e/docs-new/setup.md)
-- [Running and Debugging Tests](test/e2e/docs-new/running_debugging_tests.md)
-- [Creating Reliable Tests](test/e2e/docs-new/creating_reliable_tests.md)
-- [New Style Guide](test/e2e/docs-new/new_style_guide.md)
-- [Custom Fixtures](test/e2e/docs-new/custom_fixtures.md)
-
-## Framework Migration Status
-
-We are migrating from the legacy framework to Playwright Test:
-
-**Legacy Framework (Playwright + Jest runner)**
-- Test files: `test/e2e/specs/**/*.ts` (without `.spec.` in filename)
-- Examples: @test/e2e/specs/blocks/blocks__core.ts, @test/e2e/specs/published-content/likes__post.ts
-- Documentation: @test/e2e/docs/
-- Status: Being phased out, do not write new tests in this format
-
-**New Framework (Playwright Test)**
-- Test files: `test/e2e/specs/**/*.spec.ts` (with `.spec.` in filename)
-- Examples: @test/e2e/specs/tools/import__sites-squarespace.spec.ts, @test/e2e/specs/tools/marketing__seo.spec.ts
-- Documentation: @test/e2e/docs-new/
-- Status: Target framework for all new and migrated tests
-
-## Guidelines
-
-- Always write new tests using Playwright Test (`.spec.ts` files)
-- When modifying existing tests, consider migrating them to the new framework
-- Follow the patterns and style guide in @test/e2e/docs-new/
-- Reference legacy docs only for understanding existing code
-
-## Running Tests
-
-When running Playwright Test specs (`.spec.ts` files):
-
-**IMPORTANT**: Always use `--reporter=list` to prevent the HTML report from opening automatically on failure. Without this flag, the test process will hang waiting for the HTML report browser window to close.
-
-```bash
-# Good - process exits immediately after test completion
-yarn playwright test specs/path/to/test.spec.ts --reporter=list
-
-# Bad - hangs on failure waiting for HTML report to close
-yarn playwright test specs/path/to/test.spec.ts
-```
-
-For legacy tests (`*.ts` without `.spec.`), use the Jest runner:
-```bash
-yarn test specs/path/to/test.ts
-```
-
-## Migration Quick Reference
-
-### File Structure Changes
-
-**Legacy**: `specs/feature/test-name.ts`
-**New**: `specs/feature/test-name.spec.ts`
-
-### Import Changes
-
-```typescript
-// Legacy
-import { DataHelper, LoginPage, TestAccount } from '@automattic/calypso-e2e';
-import { Page, Browser } from 'playwright';
-declare const browser: Browser;
-
-// New
-import { tags, test, expect } from '../../lib/pw-base';
-```
-
-### Test Structure Changes
-
-```typescript
-// Legacy
-describe( DataHelper.createSuiteTitle( 'Test Suite' ), function () {
-  let page: Page;
-
-  beforeAll( async () => {
-    page = await browser.newPage();
-  } );
-
-  it( 'Step 1', async function () {
-    // test code
-  } );
-
-  afterAll( async () => {
-    await page.close();
-  } );
-} );
-
-// New
-test.describe( 'Test Suite', { tag: [ tags.TAG_NAME ] }, () => {
-  test( 'As a user, I can do something', async ( { page } ) => {
-    await test.step( 'Given precondition', async function () {
-      // test code
-    } );
-  } );
-} );
-```
-
-### Authentication Changes
-
-```typescript
-// Legacy
-const testAccount = new TestAccount( 'accountName' );
-await testAccount.authenticate( page );
-
-// New - use fixtures
-test( 'Test', async ( { accountDefaultUser, page } ) => {
-  await test.step( 'Given I am authenticated', async function () {
-    await accountDefaultUser.authenticate( page );
-  } );
-} );
-```
-
-### Page Objects & Components
-
-```typescript
-// Legacy
-const loginPage = new LoginPage( page );
-const sidebar = new SidebarComponent( page );
-
-// New - use fixtures
-test( 'Test', async ( { pageLogin, componentSidebar } ) => {
-  await pageLogin.visit();
-  await componentSidebar.navigate( 'Menu', 'Item' );
-} );
-```
-
-### Available Fixtures
-
-**Accounts**: `accountDefaultUser`, `accountGivenByEnvironment`, `accountAtomic`, `accountGutenbergSimple`, `accounti18n`, `accountPreRelease`, `accountSimpleSiteFreePlan`, `accountSMS`
-
-**Pages/Components**: Follow naming conventions:
-- `page*` - Pages (e.g., `pageLogin`, `pageEditor`, `pagePeople`)
-- `component*` - Components (e.g., `componentSidebar`, `componentGutenberg`)
-- `flow*` - Flows (e.g., `flowStartWriting`)
-
-**Clients**: `clientEmail`, `clientRestAPI`
-
-**Other**: `secrets`, `environment`, `pageIncognito`, `sitePublic`
-
-### Given/When/Then Pattern
-
-Use `test.step()` with descriptive names:
-- **Given**: Preconditions
-- **When**: Actions
-- **Then**: Assertions
-- **And**: Continuation
-
-```typescript
-await test.step( 'Given I am on the login page', async function () {} );
-await test.step( 'When I enter credentials', async function () {} );
-await test.step( 'Then I am logged in', async function () {} );
-```
-
-### Skip Conditions
-
-```typescript
-// Legacy
-skipDescribeIf( condition )( 'Suite', function () {} );
-
-// New
-test( 'Test', async ( { environment } ) => {
-  test.skip( environment.TEST_ON_ATOMIC, 'Reason' );
-} );
-```
-
-### Multiple Contexts
-
-```typescript
-// Legacy
-const newContext = await browser.newContext();
-const newPage = await newContext.newPage();
-
-// New
-test( 'Test', async ( { page, pageIncognito } ) => {
-  // page = authenticated context
-  // pageIncognito = unauthenticated context
-} );
-```
diff --git a/.cursor/rules/a4a.mdc b/.cursor/rules/a4a.mdc
@@ -1,21 +0,0 @@
----
-description: Rules that applies for Automattic for Agencies related development
-globs: client/a8c-for-agencies/**/*.*
----
-Use this rules on top of [calypso-client-rules.mdc](mdc:.cursor/rules/calypso-client-rules.mdc)
-
-## Code Style and Structure
-
-### Code Standards
-
-- When creating forms, use `calypso/a8c-for-agencies/components/form` and `calypso/components/forms/` components where possible.
-
-### Style Conventions
-
-- Use [style.scss](mdc:client/a8c-for-agencies/style.scss) as an example.
-- Don't use `&--` & `&__` selectors and write full name when defining styles.
-- Avoid using `--studio*` colors and instead use `--color*`. Example, instead of `var(--studio-gray-50)` use `var(--color-neutral-50)`.
-
-### Color and Typography Conventions
-
-#### Typography
diff --git a/.cursor/rules/calypso-client.mdc b/.cursor/rules/calypso-client.mdc
@@ -1,66 +0,0 @@
----
-description: Rules that applies for all Clients within repository
-globs: client/**
-alwaysApply: false
----
-
-You are an expert React + TypeScript programming assistant focused on producing clear, readable, and production-quality code.
-
-## Core Principles
-
-- Provide concise, technical answers with accurate TypeScript examples.
-- Use functional, declarative React (no classes).
-- Prefer composition and modularization over duplication.
-- Prioritize accessibility, performance, and scalability.
-- Read linked documentation files to have wider context.
-- Research existing patterns and conventions in the codebase before coming up with new solutions.
-
-## Code Style
-
-- Use TypeScript strictly; no `any` unless justified.
-- Keep components small and focused.
-- Use `import clsx from 'clsx'` instead of `classnames`.
-- There should be 1 empty line between `import './style.scss'` and other imports.
-- Follow ESLint-compatible patterns. Run `yarn eslint --fix` on that specific file individually for large changes.
-
-## Naming
-
-- Descriptive names with auxiliary verbs (e.g., `isLoading`, `hasError`).
-- kebab-case directories (e.g., `components/auth-wizard`).
-
-## Styling
-
-- Avoid BEM shortcuts (`&--`, `&__`).
-- Use logical properties (e.g., `margin-inline-start`).
-- Prefer scalable, accessible layouts.
-
-## WordPress UI Components
-
-- When building UI, prefer existing components from `@wordpress/components` instead of creating custom implementations.
-- Do NOT recreate common primitives such as:
-  - Button
-  - Modal
-  - Card
-  - Panel
-  - Notice
-  - Tooltip
-  - Spinner
-  - TextControl / SelectControl / ToggleControl / CheckboxControl
-  - Flex / VStack / HStack / Grid
-  - Popover / Dropdown
-  - Form controls and layout primitives
-- Only build custom components if no suitable WordPress component exists.
-- Avoid `__experimental*` components unless explicitly requested or there are already existing examples.
-
-## Documentation
-
-- Follow JSDoc.
-- Explain intent and reasoning, not obvious behavior.
-- Wrap comments at 100 columns.
-
-## Testing
-
-- To run tests for individual files, use the command `yarn test-client <filename>`.
-- Use React Testing Library.
-- Prefer `userEvent` over `fireEvent`.
-- Use `toBeVisible` for user-visible assertions instead of `toBeInTheDocument`.
diff --git a/.cursor/rules/dashboard.mdc b/.cursor/rules/dashboard.mdc
@@ -1,100 +0,0 @@
----
-description: Rules for development in the dashboard subdirectory
-globs: client/dashboard/**
-alwaysApply: false
----
-
-You are an expert AI programming assistant specializing in the WordPress.com Dashboard. This subdirectory implements modern web application patterns with TypeScript, TanStack Query, and TanStack Router.
-
-Use these rules on top of [calypso-client-rules.mdc](mdc:./rules/calypso-client-rules.mdc).
-
-## Documentation
-
-For detailed implementation guidance, refer to:
-- [Data Library](mdc:client/dashboard/docs/data-library.md) - TanStack Query usage, loaders, caching
-- [UI Components](mdc:client/dashboard/docs/ui-components.md) - WordPress components, placeholders, DataViews
-- [Router](mdc:client/dashboard/docs/router.md) - TanStack Router patterns, lazy loading
-- [Internationalization](mdc:client/dashboard/docs/i18n.md) - Translation patterns, CSS logical properties
-- [Typography and Copy](mdc:client/dashboard/docs/typography-and-copy.md) - Capitalization, snackbar messages
-- [Testing](mdc:client/dashboard/docs/testing.md) - Testing strategies
-
-## Code Review Guidelines
-
-When reviewing dashboard code, watch for these specific patterns and potential issues:
-
-### External Link Handling
-
-- All URLs linking to old WordPress.com/Calypso MUST use `wpcomLink()` function
-	- **Import**: Use `import { wpcomLink } from '@automattic/dashboard/utils/link'`
-	- **Purpose**: Ensures proper environment configuration (dev vs production hostnames)
-- Every link to `/checkout` must have `redirect_to` and `cancel_to` query param
-	- **Purpose**: Ensures correct behaviour when exiting the checkout screen
-- Every link to `/setup/plan-upgrade` must have a `cancel_to` query param
-	- **Purpose**: Ensures correct behaviour when exiting the upgrade screen
-
-```typescript
-// ✅ Correct - wrapped with wpcomLink()
-<a href={ wpcomLink( '/me/security' ) }>Security Settings</a>
-
-// ❌ Incorrect - hardcoded WordPress.com URL
-<a href="https://wordpress.com/me/security">Security Settings</a>
-
-// ❌ Incorrect - relative URL to old dashboard
-<a href="/me/security">Security Settings</a>
-```
-
-### Mutation Callback Handling
-
-- **Component-specific Callbacks**: Attach `onSuccess`/`onError` to the `mutate()` call, not `useMutation()`
-- **Query Options**: Don't override callbacks defined in api-queries mutation options
-- **Cache Updates**: Query option callbacks handle cache invalidation and updates
-
-```typescript
-// ✅ Correct - callback on mutate call
-const { mutate: saveSetting } = useMutation( saveSettingMutation() );
-
-const handleSave = () => {
-  saveSetting( newValue, {
-    onSuccess: () => {
-      // Component-specific success handling
-      setShowSuccessMessage( true );
-    },
-    onError: ( error ) => {
-      // Component-specific error handling
-      setError( error.message );
-    },
-  } );
-};
-
-// ❌ Incorrect - overrides query option callbacks
-const { mutate: saveSetting } = useMutation( {
-  ...saveSettingMutation(),
-  onSuccess: () => setShowSuccessMessage( true ), // Breaks cache updates!
-  onError: ( error ) => setError( error.message ),
-} );
-```
-
-### Typography and Copy Compliance
-
-- **Sentence Case**: Verify buttons, labels, and headings use sentence case (not title case)
-- **Periods**: Check sentences end with periods; buttons and labels do not
-- **Curly Quotes**: Ensure proper curly quotes (“like this”) and apostrophes (it’s) are used
-- **Product Names**: "Hosting Dashboard" should be capitalized as proper noun
-- **Snackbar Patterns**: Follow established patterns for success/error messages
-
-```typescript
-// ✅ Correct copy patterns
-<Button>Save changes</Button>  // No period, sentence case
-<p>Your settings have been saved.</p>  // Period, curly quotes if needed
-
-// Snackbar messages
-`SSH access enabled.`
-`Failed to save PHP version.`
-
-// ❌ Incorrect patterns  
-<Button>Save Changes.</Button>  // Has period, title case
-<p>Your settings have been saved</p>  // Missing period
-`SSH Access Enabled`  // Title case, missing period
-```
-
-Remember: This dashboard represents modern React patterns. Prioritize performance, accessibility, and maintainability while leveraging the WordPress ecosystem.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,27 +1,4 @@
-# CLAUDE.md
-
-## Repository layout
-
-- client/ — main application clients, deployed as single-page React apps.
-- packages/ — shared libraries across clients.
-- apps/ — standalone mini-apps, deployed separately.
-
-## Clients
-
-- **Calypso** — the classic WordPress.com hosting dashboard, sharing data using Redux and split via Webpack section chunks.
-  - client/my-sites — per-site management; deprecated in favor of the Dashboard client
-  - client/landing/stepper — onboarding/signup flows (site creation, domain purchase, migration wizards)
-  - client/reader — WordPress.com Reader: feed streams, discover, conversations, likes, lists, following management
-  - Shared infra: client/components, client/state, client/lib, client/layout
-- **Jetpack Cloud** (client/jetpack-cloud) — reuses Calypso shared infra (client/state, client/components).
-- **A8C for Agencies** (client/a8c-for-agencies) — reuses Calypso shared infra.
-- **Dashboard** (client/dashboard) — the new multi-site dashboard. Self-contained: does not reuse Calypso client code. Has its own components, data fetching (TanStack Query), and routing (TanStack Router).
-
-## Development
-
-- `yarn install`
-- `yarn start` to start the dev server.
-- `yarn start-dashboard` to start the dev server for the Dashboard client only.
+@AGENTS.md
 
 ## Creating PRs
 
diff --git a/client/AGENTS.md b/client/AGENTS.md
@@ -1,8 +1,3 @@
----
-paths:
-  - "client/**"
----
-
 You are an expert React + TypeScript programming assistant focused on producing clear, readable, and production-quality code.
 
 ## Core Principles
diff --git a/client/CLAUDE.md b/client/CLAUDE.md
@@ -0,0 +1 @@
+@AGENTS.md
diff --git a/client/a8c-for-agencies/AGENTS.md b/client/a8c-for-agencies/AGENTS.md
@@ -1,9 +1,3 @@
----
-paths:
-  - client/a8c-for-agencies/**
----
-Use this rules on top of @.claude/rules/calypso-client.md.
-
 ## Code Style and Structure
 
 ### Code Standards
diff --git a/client/a8c-for-agencies/CLAUDE.md b/client/a8c-for-agencies/CLAUDE.md
@@ -0,0 +1 @@
+@AGENTS.md
diff --git a/client/dashboard/AGENTS.md b/client/dashboard/AGENTS.md
@@ -1,21 +1,15 @@
----
-paths:
-  - "client/dashboard/**"
----
-
 You are an expert AI programming assistant specializing in the WordPress.com Dashboard. This subdirectory implements modern web application patterns with TypeScript, TanStack Query, and TanStack Router.
 
-IMPORTANT: Use these rules on top of [calypso-client.mdc](mdc:./calypso-client.mdc).
-
 ## Documentation
 
 For detailed implementation guidance, refer to:
-- [Data Library](mdc:client/dashboard/docs/data-library.md) - TanStack Query usage, loaders, caching
-- [UI Components](mdc:client/dashboard/docs/ui-components.md) - WordPress components, placeholders, DataViews
-- [Router](mdc:client/dashboard/docs/router.md) - TanStack Router patterns, lazy loading
-- [Internationalization](mdc:client/dashboard/docs/i18n.md) - Translation patterns, CSS logical properties
-- [Typography and Copy](mdc:client/dashboard/docs/typography-and-copy.md) - Capitalization, snackbar messages
-- [Testing](mdc:client/dashboard/docs/testing.md) - Testing strategies
+
+- docs/data-library.md - TanStack Query usage, loaders, caching
+- docs/ui-components.md - WordPress components, placeholders, DataViews
+- docs/router.md - TanStack Router patterns, lazy loading
+- docs/i18n.md - Translation patterns, CSS logical properties
+- docs/typography-and-copy.md - Capitalization, snackbar messages
+- docs/testing.md - Testing strategies
 
 ## Code Review Guidelines
 
@@ -24,12 +18,12 @@ When reviewing dashboard code, watch for these specific patterns and potential i
 ### External Link Handling
 
 - All URLs linking to old WordPress.com/Calypso MUST use `wpcomLink()` function
-	- **Import**: Use `import { wpcomLink } from '@automattic/dashboard/utils/link'`
-	- **Purpose**: Ensures proper environment configuration (dev vs production hostnames)
+    - **Import**: Use `import { wpcomLink } from '@automattic/dashboard/utils/link'`
+    - **Purpose**: Ensures proper environment configuration (dev vs production hostnames)
 - Every link to `/checkout` must have `redirect_to` and `cancel_to` query param
-	- **Purpose**: Ensures correct behaviour when exiting the checkout screen
+    - **Purpose**: Ensures correct behaviour when exiting the checkout screen
 - Every link to `/setup/plan-upgrade` must have a `cancel_to` query param
-	- **Purpose**: Ensures correct behaviour when exiting the upgrade screen
+    - **Purpose**: Ensures correct behaviour when exiting the upgrade screen
 
 ```typescript
 // ✅ Correct - wrapped with wpcomLink()
diff --git a/client/dashboard/CLAUDE.md b/client/dashboard/CLAUDE.md
@@ -0,0 +1 @@
+@AGENTS.md
diff --git a/test/e2e/AGENTS.md b/test/e2e/AGENTS.md
@@ -1,43 +1,44 @@
----
-description: Rules that applies for e2e testing
----
 # E2E Test Framework Instructions
 
 ## Documentation
 
 Full documentation is available in:
-- `test/e2e/docs/` - Legacy framework documentation
-- `test/e2e/docs-new/` - New Playwright Test framework documentation
+
+- docs/ - Legacy framework documentation
+- docs-new/ - New Playwright Test framework documentation
 
 Key docs to reference:
-- [Overview](test/e2e/docs-new/overview.md)
-- [Setup](test/e2e/docs-new/setup.md)
-- [Running and Debugging Tests](test/e2e/docs-new/running_debugging_tests.md)
-- [Creating Reliable Tests](test/e2e/docs-new/creating_reliable_tests.md)
-- [New Style Guide](test/e2e/docs-new/new_style_guide.md)
-- [Custom Fixtures](test/e2e/docs-new/custom_fixtures.md)
+
+- docs-new/overview.md
+- docs-new/setup.md
+- docs-new/running_debugging_tests.md
+- docs-new/creating_reliable_tests.md
+- docs-new/new_style_guide.md
+- docs-new/custom_fixtures.md
 
 ## Framework Migration Status
 
 We are migrating from the legacy framework to Playwright Test:
 
-**Legacy Framework (Playwright + Jest runner)**
+### Legacy Framework (Playwright + Jest runner)
+
 - Test files: `test/e2e/specs/**/*.ts` (without `.spec.` in filename)
 - Examples: `specs/blocks/blocks__core.ts`, `specs/published-content/likes__post.ts`
-- Documentation: `test/e2e/docs/`
+- Documentation: docs/
 - Status: Being phased out, do not write new tests in this format
 
-**New Framework (Playwright Test)**
+### New Framework (Playwright Test)
+
 - Test files: `test/e2e/specs/**/*.spec.ts` (with `.spec.` in filename)
 - Examples: `specs/tools/import__sites-squarespace.spec.ts`, `specs/tools/marketing__seo.spec.ts`
-- Documentation: `test/e2e/docs-new/`
+- Documentation: docs-new/
 - Status: Target framework for all new and migrated tests
 
 ## Guidelines
 
 - Always write new tests using Playwright Test (`.spec.ts` files)
 - When modifying existing tests, consider migrating them to the new framework
-- Follow the patterns and style guide in `test/e2e/docs-new/`
+- Follow the patterns and style guide in docs-new/
 - Reference legacy docs only for understanding existing code
 
 ## Running Tests
@@ -55,6 +56,7 @@ yarn playwright test specs/path/to/test.spec.ts
 ```
 
 For legacy tests (`*.ts` without `.spec.`), use the Jest runner:
+
 ```bash
 yarn test specs/path/to/test.ts
 ```
@@ -142,6 +144,7 @@ test( 'Test', async ( { pageLogin, componentSidebar } ) => {
 **Accounts**: `accountDefaultUser`, `accountGivenByEnvironment`, `accountAtomic`, `accountGutenbergSimple`, `accounti18n`, `accountPreRelease`, `accountSimpleSiteFreePlan`, `accountSMS`
 
 **Pages/Components**: Follow naming conventions:
+
 - `page*` - Pages (e.g., `pageLogin`, `pageEditor`, `pagePeople`)
 - `component*` - Components (e.g., `componentSidebar`, `componentGutenberg`)
 - `flow*` - Flows (e.g., `flowStartWriting`)
@@ -153,6 +156,7 @@ test( 'Test', async ( { pageLogin, componentSidebar } ) => {
 ### Given/When/Then Pattern
 
 Use `test.step()` with descriptive names:
+
 - **Given**: Preconditions
 - **When**: Actions
 - **Then**: Assertions
diff --git a/test/e2e/CLAUDE.md b/test/e2e/CLAUDE.md
@@ -0,0 +1 @@
+@AGENTS.md
PATCH

echo "Gold patch applied."
