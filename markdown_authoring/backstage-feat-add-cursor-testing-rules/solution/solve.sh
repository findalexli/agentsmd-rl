#!/usr/bin/env bash
set -euo pipefail

cd /workspace/backstage

# Idempotency guard
if grep -qF "**CRITICAL**: When writing tests for Backstage backend code, you MUST use utilit" ".cursor/rules/tests/backend-test-utils.mdc" && grep -qF "**CRITICAL**: When writing tests for Backstage frontend code, plugins, or React " ".cursor/rules/tests/test-utils.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/tests/backend-test-utils.mdc b/.cursor/rules/tests/backend-test-utils.mdc
@@ -0,0 +1,91 @@
+---
+description: Enforce usage of @backstage/backend-test-utils in backend tests
+globs: ['**/*.test.*', '**/*.spec.*']
+alwaysApply: false
+---
+# Backstage Backend Testing Rules
+
+**CRITICAL**: When writing tests for Backstage backend code, you MUST use utilities from `@backstage/backend-test-utils` wherever possible. Do NOT create custom mocks, test databases, caches, or service implementations when equivalent utilities exist in backend-test-utils.
+
+## Required Usage
+
+1. **Service Mocking**: Always use `mockServices` from `@backstage/backend-test-utils` instead of creating custom service mocks. This includes:
+   - `mockServices.auth()` - For authentication service mocking
+   - `mockServices.httpAuth()` - For HTTP authentication service mocking
+   - `mockServices.database()` - For database service mocking
+   - `mockServices.cache()` - For cache service mocking
+   - `mockServices.logger()` - For logger service mocking
+   - `mockServices.permissions()` - For permissions service mocking
+   - `mockServices.scheduler()` - For scheduler service mocking
+   - `mockServices.userInfo()` - For user info service mocking
+   - `mockServices.events()` - For events service mocking
+   - `mockServices.urlReader()` - For URL reader service mocking
+   - `mockServices.rootConfig()` - For root config service mocking
+   - `mockServices.rootLogger()` - For root logger service mocking
+   - `mockServices.rootHealth()` - For root health service mocking
+   - `mockServices.rootLifecycle()` - For root lifecycle service mocking
+   - `mockServices.httpRouter()` - For HTTP router service mocking
+   - `mockServices.lifecycle()` - For lifecycle service mocking
+   - `mockServices.auditor()` - For auditor service mocking
+   - `mockServices.permissionsRegistry()` - For permissions registry service mocking
+
+2. **Credentials**: Always use `mockCredentials` from `@backstage/backend-test-utils` for creating test credentials instead of manually constructing credential objects.
+
+3. **Test Backend**: Always use `startTestBackend` and `TestBackend` from `@backstage/backend-test-utils` when testing backend features, plugins, or modules. This provides a fully configured test backend with all necessary services.
+
+4. **Service Factory Testing**: Use `ServiceFactoryTester` from `@backstage/backend-test-utils` when testing individual service factories in isolation.
+
+5. **Database Testing**: Always use `TestDatabases` from `@backstage/backend-test-utils` for database testing. This supports multiple database engines (PostgreSQL, MySQL, SQLite) and handles ephemeral test database creation and cleanup automatically.
+
+6. **Cache Testing**: Always use `TestCaches` from `@backstage/backend-test-utils` for cache testing. This supports multiple cache backends (Redis, Valkey, Memcache) and handles ephemeral test cache creation and cleanup automatically.
+
+7. **Filesystem Testing**: Use `createMockDirectory` from `@backstage/backend-test-utils` when testing code that interacts with the filesystem. This provides a safe, isolated temporary directory for tests.
+
+8. **MSW Integration**: Use `registerMswTestHooks` from `@backstage/backend-test-utils` when setting up Mock Service Worker for HTTP request mocking in tests.
+
+9. **Error Handler**: Use `mockErrorHandler` from `@backstage/backend-test-utils` when testing Express routers that need error handling middleware.
+
+10. **Alpha Services**: For alpha/experimental services, use the utilities from `@backstage/backend-test-utils/alpha` (e.g., `actionsRegistryServiceMock`, `actionsServiceMock`).
+
+## Import Patterns
+
+Always import from the main package:
+
+```typescript
+import {
+  mockServices,
+  mockCredentials,
+  startTestBackend,
+  TestDatabases,
+  TestCaches,
+  createMockDirectory,
+  registerMswTestHooks,
+  mockErrorHandler,
+  ServiceFactoryTester
+} from '@backstage/backend-test-utils';
+```
+
+For alpha services:
+
+```typescript
+import {
+  actionsRegistryServiceMock,
+  actionsServiceMock
+} from '@backstage/backend-test-utils/alpha';
+```
+
+## When to Use
+
+- **Always** use these utilities when writing backend tests
+- **Never** create custom mocks for services that have equivalents in backend-test-utils
+- **Never** manually set up test databases or caches when TestDatabases/TestCaches are available
+- **Never** create custom test backends when startTestBackend is available
+
+## Benefits
+
+Using backend-test-utils ensures:
+- Consistent test setup across the codebase
+- Proper cleanup and resource management
+- Support for multiple database/cache backends
+- Well-tested and maintained utilities
+- Reduced boilerplate in test code
diff --git a/.cursor/rules/tests/test-utils.mdc b/.cursor/rules/tests/test-utils.mdc
@@ -0,0 +1,100 @@
+---
+description: Enforce usage of @backstage/test-utils in frontend tests
+globs: ['**/*.test.*', '**/*.spec.*']
+alwaysApply: false
+---
+# Backstage Frontend/Plugin Testing Rules
+
+**CRITICAL**: When writing tests for Backstage frontend code, plugins, or React components, you MUST use utilities from `@backstage/test-utils` wherever possible. Do NOT create custom mocks, test wrappers, or API implementations when equivalent utilities exist in test-utils.
+
+## Required Usage
+
+1. **API Mocking**: Always use `mockApis` from `@backstage/test-utils` instead of creating custom API mocks. This includes:
+   - `mockApis.analytics()` - For AnalyticsApi mocking
+   - `mockApis.config()` - For ConfigApi mocking with optional configuration data
+   - `mockApis.discovery()` - For DiscoveryApi mocking
+   - `mockApis.identity()` - For IdentityApi mocking with user entity ref, token, profile info
+   - `mockApis.permission()` - For PermissionApi mocking with authorization control
+   - `mockApis.storage()` - For StorageApi mocking with in-memory storage
+   - `mockApis.translation()` - For TranslationApi mocking (from alpha)
+   - Each API also provides `.mock()` for jest mocks and `.factory()` for API factories
+
+2. **Test App Wrappers**: Always use `wrapInTestApp` or `renderInTestApp` from `@backstage/test-utils` when testing React components that need Backstage app context (routing, theme, APIs). Use `createTestAppWrapper` for custom wrapper creation.
+
+3. **Test API Provider**: Always use `TestApiProvider` or `TestApiRegistry` from `@backstage/test-utils` when testing components that depend on Backstage APIs. This allows you to provide only the APIs needed for your test.
+
+4. **Async Component Rendering**: Use `renderWithEffects` from `@backstage/test-utils` when testing components that perform asynchronous operations (e.g., useEffect with fetch). This properly handles async rendering with React's act.
+
+5. **Log Collection**: Use `withLogCollector` from `@backstage/test-utils` when you need to capture and assert on console logs, warnings, or errors during tests.
+
+6. **MSW Integration**: Use `registerMswTestHooks` from `@backstage/test-utils` when setting up Mock Service Worker for HTTP request mocking in frontend tests.
+
+7. **Text Content Matcher**: Use `textContentMatcher` from `@backstage/test-utils` as a custom matcher for testing-library queries when matching text content.
+
+8. **Mock Breakpoint**: Use `mockBreakpoint` from `@backstage/test-utils` when testing components that use Material-UI's `useMediaQuery` hook (though this is deprecated in favor of core-components/testUtils).
+
+9. **Individual API Mocks**: Use individual mock APIs when you need more control:
+   - `MockAnalyticsApi` - Analytics API mock
+   - `MockConfigApi` - Config API mock
+   - `MockErrorApi` - Error API mock
+   - `MockFetchApi` - Fetch API mock
+   - `MockPermissionApi` - Permission API mock
+   - `MockStorageApi` - Storage API mock
+   - `MockTranslationApi` - Translation API mock (from alpha)
+
+10. **Alpha APIs**: For alpha/experimental APIs, use the utilities from `@backstage/test-utils/alpha` (e.g., `MockTranslationApi`).
+
+## Import Patterns
+
+Always import from the main package:
+
+```typescript
+import {
+  mockApis,
+  wrapInTestApp,
+  renderInTestApp,
+  createTestAppWrapper,
+  TestApiProvider,
+  TestApiRegistry,
+  renderWithEffects,
+  withLogCollector,
+  registerMswTestHooks,
+  textContentMatcher,
+  mockBreakpoint,
+  MockAnalyticsApi,
+  MockConfigApi,
+  MockErrorApi,
+  MockFetchApi,
+  MockPermissionApi,
+  MockStorageApi
+} from '@backstage/test-utils';
+```
+
+For alpha APIs:
+
+```typescript
+import {
+  MockTranslationApi
+} from '@backstage/test-utils/alpha';
+```
+
+## When to Use
+
+- **Always** use these utilities when writing frontend/plugin tests
+- **Always** use `renderInTestApp` or `wrapInTestApp` for components that need Backstage context
+- **Always** use `TestApiProvider` or `TestApiRegistry` when components depend on Backstage APIs
+- **Always** use `mockApis` instead of creating custom API implementations
+- **Never** manually set up React Router, theme providers, or API contexts when test wrappers are available
+- **Never** create custom API mocks when mockApis provides equivalents
+- **Never** use raw `render` from testing-library when `renderWithEffects` is needed for async components
+
+## Benefits
+
+Using test-utils ensures:
+- Consistent test setup across frontend codebase
+- Proper Backstage app context (routing, theme, APIs)
+- Simplified API mocking with realistic implementations
+- Proper async rendering handling
+- Well-tested and maintained utilities
+- Reduced boilerplate in test code
+- Better integration with Backstage's plugin architecture
PATCH

echo "Gold patch applied."
