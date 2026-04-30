#!/usr/bin/env bash
set -euo pipefail

cd /workspace/console

# Idempotency guard
if grep -qF "description: \"Write tests for the akash-network/console monorepo following estab" ".claude/skills/console-tests/SKILL.md" && grep -qF "Functional tests use **whitebox seeding** and **blackbox testing**: seed data at" ".claude/skills/console-tests/references/api-patterns.md" && grep -qF "This is the canonical pattern for testing React components without `vi.mock()`. " ".claude/skills/console-tests/references/frontend-patterns.md" && grep -qF ".cursor/rules/no-jest-mock.mdc" ".cursor/rules/no-jest-mock.mdc" && grep -qF ".cursor/rules/query-by-in-tests.mdc" ".cursor/rules/query-by-in-tests.mdc" && grep -qF ".cursor/rules/setup-instead-of-before-each.mdc" ".cursor/rules/setup-instead-of-before-each.mdc" && grep -qF ".cursor/rules/test-descriptions.mdc" ".cursor/rules/test-descriptions.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/console-tests/SKILL.md b/.claude/skills/console-tests/SKILL.md
@@ -0,0 +1,251 @@
+---
+name: console-tests
+description: "Write tests for the akash-network/console monorepo following established team patterns and reviewer expectations. Use this skill whenever you need to write, fix, review, or refactor tests in the console project — including unit tests, functional tests, integration tests, or E2E tests for both frontend (deploy-web) and backend (api, notifications, indexer, provider-proxy). Also trigger when the user mentions 'write tests', 'add tests', 'fix tests', 'test this', 'spec file', or asks about testing patterns in the console codebase. When in doubt about whether to use this skill for a testing task in this repo, USE IT."
+---
+
+# Console Test Writing Guide
+
+This skill encodes the testing conventions and patterns for the akash-network/console monorepo.
+
+Before writing any test, read the source file you're testing thoroughly. Understand what it does, what dependencies it has, and what level of testing is appropriate.
+
+## Deciding What Type of Test to Write
+
+Choose the lowest-effective test level. Writing E2E tests for logic that can be unit tested wastes everyone's time and creates brittle, slow suites.
+
+**Unit tests** (99% of cases):
+- Components, hooks, pure logic services, utilities
+- All dependencies mocked via DI (never module-level mocking)
+- Run at PR level, must be fast
+
+**Integration tests** (service + database):
+- Services that rely heavily on database logic or Repository patterns
+- Use real database fixtures, not mocks
+- Mock only 3rd-party service calls if needed
+- Good for verifying queries, transactions, and data integrity
+
+**Functional / API tests** (black-box HTTP):
+- Test the service as a black box through its HTTP endpoints
+- External network calls MUST be mocked with `nock` (v14+ supports native `fetch` in addition to `http`/`https`)
+- Do NOT mock internal application services — they're implementation details at this level
+- Should only fail when functional requirements change, not from refactoring
+- Don't write functional tests for simple routes — test the service layer directly instead
+
+**E2E tests** (post-deployment verification):
+- Only for verifying deployed services in target environments (beta/prod)
+- No mocks at all
+- Happy path only
+- Use Playwright with semantic locators
+
+## Universal Rules (All Test Types)
+
+### The `setup` Function Pattern
+
+This is the most important convention. Never use `beforeEach` with shared mutable variables.
+
+- Define a `setup()` function at the **bottom** of the root `describe` block
+- It constructs the unit under test and returns it along with all mocked dependencies
+- It accepts a **single parameter** with an **inline type definition**
+- Do **not** specify the return type — let TypeScript infer it
+- Each test calls `setup()` independently — no shared mutable state across tests
+
+```typescript
+describe(BalancesService.name, () => {
+  it("returns balances for a given address", async () => {
+    const { service, balanceRepository } = setup();
+    balanceRepository.findByAddress.mockResolvedValue([{ denom: "uakt", amount: "1000" }]);
+
+    const result = await service.getBalances("akash1abc...");
+
+    expect(result).toEqual([{ denom: "uakt", amount: "1000" }]);
+  });
+
+  it("returns empty array when no balances found", async () => {
+    const { service, balanceRepository } = setup();
+    balanceRepository.findByAddress.mockResolvedValue([]);
+
+    const result = await service.getBalances("akash1xyz...");
+
+    expect(result).toEqual([]);
+  });
+
+  function setup(input?: { customConfig?: Partial<BalancesConfig> }) {
+    const balanceRepository = mock<BalanceRepository>();
+    const config = mockConfigService<BalancesConfig>({ ...input?.customConfig });
+    const service = new BalancesService(balanceRepository, config);
+    return { service, balanceRepository, config };
+  }
+});
+```
+
+Skip `setup` only if creating the object under test is trivially simple (e.g., testing a pure function with no dependencies).
+
+### Test Description Conventions
+
+**Root `describe`**: Use `SubjectUnderTest.name` (the actual reference, not a string). This enables IDE refactoring and reference-finding.
+
+```typescript
+// Good
+describe(StripeWebhookService.name, () => { ... });
+
+// Bad
+describe("StripeWebhookService", () => { ... });
+```
+
+**Nested `describe`**: Use either a method name or a `"when ..."` condition.
+
+```typescript
+describe(StripeWebhookService.name, () => {
+  describe("handleChargeRefunded", () => { ... });
+  describe("when payment method is missing", () => { ... });
+});
+```
+
+**`it` blocks**: Use present simple, 3rd person singular. Do NOT prepend with "should".
+
+```typescript
+// Good
+it("returns early when customer ID is missing", async () => { ... });
+it("updates both limits and isTrialing when endTrial is true", async () => { ... });
+
+// Bad
+it("should return early when customer ID is missing", async () => { ... });
+```
+
+### Mocking: `mock<T>()` from `vitest-mock-extended`
+
+Always use `mock<T>()` for typed mocks. Never use `jest.mock()` or `vi.mock()` for module-level mocking — it causes OOM with heavy component trees and couples tests to implementation details.
+
+```typescript
+import { mock } from "vitest-mock-extended";
+
+const userRepository = mock<UserRepository>();
+const stripeService = mock<StripeService>();
+const logger = mock<LoggerService>();
+```
+
+For config services, use `mockConfigService<T>()` (in `apps/api/test/mocks/config-service.mock.ts`):
+
+```typescript
+const billingConfig = mockConfigService<BillingConfigService>({
+  DEPLOYMENT_GRANT_DENOM: "uakt",
+  TRIAL_ALLOWANCE_EXPIRATION_DAYS: 14
+});
+```
+
+### Vitest Imports
+
+Always explicitly import from `vitest`:
+
+```typescript
+import { describe, expect, it, vi } from "vitest";
+```
+
+Explicit imports make dependencies visible and simplify TypeScript types.
+
+### No `if` Statements in Assertions
+
+Never use conditional logic in test expectations. If you need to narrow a type, use `as` assertions. Otherwise, skipped assertions silently pass when they shouldn't.
+
+```typescript
+// Good
+const result = await service.validate(cert) as CertValidationResultError;
+expect(result.ok).toBe(false);
+expect(result.code).toBe("unknownCertificate");
+
+// Bad
+const result = await service.validate(cert);
+if (!result.ok) {
+  expect(result.code).toBe("unknownCertificate");
+}
+```
+
+### Arrange-Act-Assert (AAA)
+
+Follow the AAA pattern. Setup prepares state; the test validates it. Don't mix concerns.
+
+```typescript
+it("creates a deployment grant", async () => {
+  // Arrange
+  const { service, grantService } = setup();
+  grantService.create.mockResolvedValue(mockGrant);
+
+  // Act
+  const result = await service.createGrant("akash1abc...");
+
+  // Assert
+  expect(result).toEqual(mockGrant);
+  expect(grantService.create).toHaveBeenCalledWith("akash1abc...");
+});
+```
+
+### Comments Answer WHY, Not WHAT
+
+Remove obvious comments. If a comment just restates the method name or assertion, delete it.
+
+### Test Error Handling Thoughtfully
+
+When testing error paths, focus on errors the code explicitly handles — but don't skip error coverage just because the happy path works. If a service catches and transforms errors, test those paths. If important error scenarios aren't handled in production code, that may be a gap worth flagging rather than ignoring.
+
+## Frontend Tests (deploy-web)
+
+Read @references/frontend-patterns.md for the full set of frontend-specific patterns including the DEPENDENCIES pattern, hook testing, query testing, and container testing.
+
+Key points:
+- Use `getBy*` for presence assertions (`toBeInTheDocument()`), and `queryBy*` for absence assertions (`not.toBeInTheDocument()`)
+- Use the `DEPENDENCIES` export + `dependencies` prop for component DI (never `vi.mock`) — this covers components, hooks, and any other heavy imports
+- Use `MockComponents()` helper to auto-mock dependencies
+- Services are injected via `useServices` hook, not via `DEPENDENCIES` prop
+- Use `setupQuery()` utility for React Query hook tests
+- Use `renderHook` from `@testing-library/react` for hook tests
+
+## API Unit Tests
+
+Read @references/api-patterns.md for the full set of API-specific patterns including service testing, config mocking, and seeder patterns.
+
+Key points:
+- Construct services manually with `mock<T>()` dependencies
+- Use seeders for test data (`apps/api/test/seeders/`)
+- Use function-based seeders (not class-based)
+- Use `@faker-js/faker` for randomized data in seeders
+- Seeder accepts `Partial<T>` overrides with sensible defaults
+
+## API Functional Tests
+
+Read @references/api-patterns.md for functional test setup details.
+
+Key points:
+- **Whitebox seeding, blackbox testing**: Seed data at the DB/repository level, but interact only through HTTP
+- Each spec file gets its own database via `TestDatabaseService` (auto-created, migrated, dropped)
+- Don't resolve controllers/services from the DI container — don't call application services or other endpoints to set up state
+- Mock external HTTP calls with `nock`, not internal services
+- Use a plain HTTP client (`fetch()`-based helpers) for Hono apps, `supertest` for NestJS — avoid framework-internal methods like `app.request()`
+- Each test verifies a single endpoint's behavior in isolation
+- Use function-based seeders to create test fixtures in the real database
+- Write race condition tests for upsert operations
+
+## Notifications Tests (NestJS)
+
+- Use `@nestjs/testing` `Test.createTestingModule()` for DI
+- Use `MockProvider()` helper to create NestJS providers with `vitest-mock-extended` mocks
+- Functional tests use `supertest` with a real NestJS app and per-file test databases
+
+## E2E / Playwright Tests
+
+- Use semantic locators: `getByRole`, `getByLabel`, `getByPlaceholder` — never CSS selectors or `data-testid`
+- `getByRole('button', { name: /Submit/ })` — don't add redundant `aria-label` to buttons that already have text
+- Page Objects abstract UI interactions but must NOT contain assertions
+- Use `waitFor(...)` instead of `setTimeout` — timeouts cause flakiness
+- No `console.log` or manual screenshots — use Playwright's built-in traces (`npx playwright --ui`)
+- No randomness in test data — it causes flaky failures
+- Use `Promise.all` with `context.waitForEvent("page")` for navigation patterns
+
+## Test File Organization
+
+- Test files are co-located with source: `my-service.ts` → `my-service.spec.ts`
+- Frontend: `*.spec.tsx` for components, `*.spec.ts` for logic
+- API unit: `src/**/*.spec.ts`
+- API integration: `src/**/*.integration.ts`
+- API functional: `test/functional/**/*.spec.ts`
+- API e2e: `test/e2e/**/*.spec.ts`
+- Seeders: `test/seeders/` in each app
diff --git a/.claude/skills/console-tests/references/api-patterns.md b/.claude/skills/console-tests/references/api-patterns.md
@@ -0,0 +1,345 @@
+# API Testing Patterns (apps/api, apps/notifications)
+
+## Table of Contents
+1. [Unit Test Pattern](#unit-test-pattern)
+2. [Config Service Mocking](#config-service-mocking)
+3. [Logger Mocking](#logger-mocking)
+4. [Seeders](#seeders)
+5. [Functional Test Setup](#functional-test-setup)
+6. [Functional Test Pattern](#functional-test-pattern)
+7. [Integration Test Pattern](#integration-test-pattern)
+8. [NestJS Tests (Notifications)](#nestjs-tests-notifications)
+9. [Assertion Patterns](#assertion-patterns)
+
+## Unit Test Pattern
+
+Construct the service under test manually, passing `vitest-mock-extended` mocks for all dependencies. Always use the `setup()` function at the bottom of the root `describe`.
+
+```typescript
+import { mock } from "vitest-mock-extended";
+
+describe(TopUpManagedDeploymentsService.name, () => {
+  it("tops up wallets below threshold", async () => {
+    const { service, drainingDeploymentService } = setup();
+    drainingDeploymentService.findAll.mockResolvedValue([mockDeployment]);
+
+    await service.topUp();
+
+    expect(drainingDeploymentService.findAll).toHaveBeenCalled();
+  });
+
+  function setup(input?: { grantDenom?: string }) {
+    const managedSignerService = mock<ManagedSignerService>();
+    const billingConfig = mockConfigService<BillingConfigService>({
+      DEPLOYMENT_GRANT_DENOM: input?.grantDenom ?? "uakt"
+    });
+    const drainingDeploymentService = mock<DrainingDeploymentService>();
+    const logger = mock<LoggerService>();
+
+    const service = new TopUpManagedDeploymentsService(
+      managedSignerService,
+      billingConfig,
+      drainingDeploymentService,
+      logger
+    );
+
+    return { service, managedSignerService, billingConfig, drainingDeploymentService, logger };
+  }
+});
+```
+
+The setup function returns ALL mocked dependencies so tests can configure them individually.
+
+## Config Service Mocking
+
+Use `mockConfigService<T>()` from `apps/api/test/mocks/config-service.mock.ts`. It creates a typed mock where `get(key)` returns provided values or throws for unmocked keys.
+
+```typescript
+import { mockConfigService } from "@test/mocks/config-service.mock";
+
+const billingConfig = mockConfigService<BillingConfigService>({
+  DEPLOYMENT_GRANT_DENOM: "uakt",
+  TRIAL_ALLOWANCE_EXPIRATION_DAYS: 14
+});
+```
+
+## Logger Mocking
+
+Use `mock<LoggerService>()` for unit tests:
+
+```typescript
+const logger = mock<LoggerService>();
+```
+
+When verifying log calls, check for structured event objects:
+
+```typescript
+expect(logger.info).toHaveBeenCalledWith(
+  expect.objectContaining({
+    event: "POD_DISCOVERY_COMPLETED",
+    namespace: "test-ns",
+    totalPods: 5
+  })
+);
+```
+
+## Seeders
+
+Seeders generate test data with sensible defaults and `Partial<T>` overrides. Use function-based seeders.
+
+```typescript
+import { faker } from "@faker-js/faker";
+
+export function createUserWallet(overrides: Partial<UserWalletOutput> = {}): UserWalletOutput {
+  return {
+    id: faker.number.int({ min: 0, max: 1000 }),
+    userId: faker.string.uuid(),
+    address: createAkashAddress(),
+    creditAmount: faker.number.int({ min: 0, max: 100000000 }),
+    isTrialing: false,
+    deploymentAllowance: faker.number.int({ min: 0, max: 100000000 }),
+    feeAllowance: faker.number.int({ min: 0, max: 100000000 }),
+    ...overrides
+  };
+}
+```
+
+For batch creation, add a companion function:
+
+```typescript
+export function createManyUserWallets(count: number, overrides: Partial<UserWalletOutput> = {}): UserWalletOutput[] {
+  return Array.from({ length: count }, () => createUserWallet(overrides));
+}
+```
+
+### Seeder rules
+- Seeders live in `test/seeders/` within each app
+- Share seeders across unit and functional tests
+- Use `@faker-js/faker` for randomized defaults
+- Don't use conditional defaults that silently ignore `null`/`undefined` values
+- When you need a seeder, check if one already exists before creating a new one
+
+## Functional Test Setup
+
+Functional tests use a shared setup that creates per-file test databases.
+
+### How it works (`apps/api/test/setup-functional-tests.ts`)
+
+1. **Before all**: Creates a dedicated test database (unique name per spec file via UUID), runs Drizzle migrations
+2. **Between tests**: Clears cache
+3. **After all**: Drops the test database
+
+The setup registers `RAW_APP_CONFIG` in the `tsyringe` container and provides custom matchers (`toBeTypeOrNull`, `dateTimeZ`).
+
+### `TestDatabaseService` (`apps/api/test/services/test-database.service.ts`)
+
+- Generates unique DB names: `test_<uuid>_<filename>`
+- Creates both a user DB and an indexer DB
+- Runs Drizzle ORM migrations
+- Drops both databases on teardown
+
+## Functional Test Pattern
+
+Functional tests use **whitebox seeding** and **blackbox testing**: seed data at the DB/repository level, but interact with the service only through HTTP. Don't resolve controllers or services from the DI container — that couples tests to internal implementation and makes them break on refactoring.
+
+**Seeding rules:**
+- Use DB-level seeders and real DB inserts (repository level)
+- Don't call application services or other endpoints to set up test state
+- Each test should verify a single endpoint's behavior in isolation
+
+**Testing rules:**
+- Use a plain HTTP client (not framework-internal methods like Hono's `app.request()`) — tests should survive framework changes
+- Mock only external 3rd-party network calls (blockchain nodes, Stripe, Auth0)
+- Don't mock internal application services — they're implementation details at this level
+
+```typescript
+import nock from "nock";
+
+describe("Wallets Refill", () => {
+  it("refills wallets below threshold", async () => {
+    // Whitebox seeding: insert directly into DB
+    await db.insert(userWalletsTable).values({
+      userId: user.id,
+      address: createAkashAddress(),
+      creditAmount: 100
+    }).returning();
+
+    // Mock external blockchain calls
+    nock(config.REST_API_NODE_URL)
+      .get(/\/cosmos\/feegrant\//)
+      .reply(200, FeeAllowanceResponseSeeder.create());
+
+    // Blackbox testing: interact only through HTTP
+    const response = await request("/v1/wallets/refill", { method: "POST" });
+
+    // Assert
+    expect(response.status).toBe(200);
+  });
+});
+```
+
+The database handle (`db`) is available from the shared functional test setup — it's the only internal you should access directly (for seeding and verifying data).
+
+### Key functional test rules
+
+- **Use a plain HTTP client**: Use `fetch()`-based helpers (see "Making HTTP requests" below), not framework internals
+- **Minimal mocking**: Only mock external 3rd-party services (blockchain nodes, Stripe, Auth0)
+- **Mock via request interception**: Use `nock` (v14+ supports both `http`/`https` and native `fetch`), or mock at the SDK level (`ManagementClient`) when appropriate
+- **Whitebox seeding only**: Use seeders and real DB inserts at the repository level — don't call application services or other endpoints to set up state
+- **One endpoint per test**: Each test should verify a single endpoint's behavior; don't chain endpoint calls
+- **Don't duplicate setup**: Use `setup-functional-tests.ts` — don't recreate DB setup per file
+- **Race condition tests**: Write them for upsert operations — concurrent requests hitting the same row is common
+
+### Making HTTP requests
+
+Use a plain HTTP client that makes real requests over the network. This decouples tests from the HTTP framework — if the app migrates from Hono to another framework, the tests survive unchanged.
+
+The recommended pattern (see `apps/provider-proxy/test/setup/proxyServer.ts`):
+
+```typescript
+// Start the server on a random port, then use fetch()
+const host = await startServer(config);
+
+const response = await fetch(host + "/v1/blocks");
+expect(response.status).toBe(200);
+const body = await response.json();
+```
+
+For NestJS apps (notifications), use `supertest`:
+
+```typescript
+const res = await request(app.getHttpServer()).get("/v1/alerts");
+expect(res.status).toBe(200);
+```
+
+## Integration Test Pattern
+
+Integration tests verify service behavior with real database fixtures. They sit between unit tests (all mocked) and functional tests (HTTP endpoints).
+
+```typescript
+// File: src/user/services/user.service.integration.ts
+describe(UserService.name, () => {
+  it("cleans up stale anonymous users", async () => {
+    // Seed real data
+    await db.insert(usersTable).values([
+      { id: "user-1", createdAt: daysBefore(30), type: "anonymous" },
+      { id: "user-2", createdAt: daysBefore(5), type: "anonymous" }
+    ]);
+
+    const service = container.resolve(UserService);
+    await service.cleanupStaleAnonymousUsers();
+
+    // Verify against real DB
+    const remaining = await db.select().from(usersTable);
+    expect(remaining).toHaveLength(1);
+    expect(remaining[0].id).toBe("user-2");
+  });
+});
+```
+
+Use integration tests when:
+- Testing services that heavily rely on database logic
+- Testing Repository patterns (unit testing pure delegation adds little value)
+- Verifying complex queries, transactions, or cascading operations
+
+## NestJS Tests (Notifications)
+
+### Unit tests with `@nestjs/testing`
+
+```typescript
+import { Test, TestingModule } from "@nestjs/testing";
+import { MockProvider } from "@test/mocks/provider.mock";
+
+describe(ChainAlertService.name, () => {
+  it("evaluates conditions against alert", async () => {
+    const { service, alertRepository } = await setup();
+    alertRepository.findById.mockResolvedValue(mockAlert);
+
+    await service.evaluate("alert-1");
+
+    expect(alertRepository.findById).toHaveBeenCalledWith("alert-1");
+  });
+
+  async function setup() {
+    const module: TestingModule = await Test.createTestingModule({
+      providers: [
+        ChainAlertService,
+        TemplateService,
+        MockProvider(AlertRepository),
+        MockProvider(ConditionsMatcherService),
+        MockProvider(LoggerService)
+      ]
+    }).compile();
+
+    return {
+      service: module.get<ChainAlertService>(ChainAlertService),
+      alertRepository: module.get<MockProxy<AlertRepository>>(AlertRepository)
+    };
+  }
+});
+```
+
+### `MockProvider` utility (`apps/notifications/test/mocks/provider.mock.ts`)
+
+```typescript
+import { mock } from "vitest-mock-extended";
+
+export const MockProvider = <T>(token: InjectionToken<T>, override?: Partial<T>): Provider => {
+  return { provide: token, useValue: mock<T>(override) };
+};
+```
+
+### Functional tests with `supertest`
+
+```typescript
+import request from "supertest";
+
+const res = await request(app.getHttpServer())
+  .post("/v1/alerts")
+  .set("x-user-id", userId)
+  .send({ data: input });
+
+expect(res.status).toBe(201);
+```
+
+## Assertion Patterns
+
+### Use `expect.objectContaining` for partial matching
+
+```typescript
+expect(callback).toHaveBeenCalledWith(
+  expect.objectContaining({ podName: "pod-2" }),
+  expect.any(AbortSignal)
+);
+```
+
+### Use `expect.arrayContaining` instead of `.every()` loops
+
+```typescript
+// Good
+expect(actualIds).toEqual(expect.arrayContaining(expectedIds));
+
+// Bad
+expectedIds.every(id => expect(actualIds).toContain(id));
+```
+
+### Verify idempotency with "not called" expectations
+
+```typescript
+it("handles duplicate webhook delivery idempotently", async () => {
+  // ... setup already-processed state
+
+  await service.handleChargeRefunded(event);
+
+  expect(repository.updateById).not.toHaveBeenCalled();
+  expect(refillService.reduceWalletBalance).not.toHaveBeenCalled();
+});
+```
+
+### Generate sensitive test data explicitly
+
+Don't hardcode mnemonics or secrets in config — generate them in tests:
+
+```typescript
+const mnemonic = generateMnemonic();
+```
diff --git a/.claude/skills/console-tests/references/frontend-patterns.md b/.claude/skills/console-tests/references/frontend-patterns.md
@@ -0,0 +1,231 @@
+# Frontend Testing Patterns (deploy-web)
+
+## Table of Contents
+1. [DEPENDENCIES Pattern](#dependencies-pattern)
+2. [MockComponents Utility](#mockcomponents-utility)
+3. [Hook Testing](#hook-testing)
+4. [Query Hook Testing](#query-hook-testing)
+5. [Container Component Testing](#container-component-testing)
+6. [Service Testing](#service-testing)
+7. [queryBy vs getBy](#queryby-vs-getby)
+8. [Snapshot Testing](#snapshot-testing)
+
+## DEPENDENCIES Pattern
+
+This is the canonical pattern for testing React components without `vi.mock()`. Components export their heavy dependencies (child components, hooks, and any other heavy imports) and accept them as a prop for test injection.
+
+Use a single `DEPENDENCIES` export that covers everything — components, hooks, and other imports. There's no need for a separate `COMPONENTS` export.
+
+### Source-side
+
+```typescript
+// MyComponent.tsx
+import { useRouter } from "next/navigation";
+import { CustomTooltip } from "../CustomTooltip";
+import { LabelValue } from "../LabelValue";
+import { useSettings } from "@src/hooks/useSettings";
+
+export const DEPENDENCIES = { useRouter, useSettings, CustomTooltip, LabelValue };
+
+interface Props {
+  title: string;
+  dependencies?: typeof DEPENDENCIES;
+}
+
+export function MyComponent({ title, dependencies = DEPENDENCIES }: Props) {
+  const { CustomTooltip, LabelValue, useRouter, useSettings } = dependencies;
+  // ... use them normally
+}
+```
+
+### Test-side
+
+```typescript
+import { DEPENDENCIES, MyComponent } from "./MyComponent";
+import { MockComponents } from "@tests/unit/mocks";
+
+// Note: .name only works for named function declarations (function MyComponent() {}).
+// Arrow function components (const MyComponent = () => ...) return an empty string for .name.
+// In that case, use a string literal: describe("MyComponent", () => { ... })
+describe(MyComponent.name, () => {
+  it("renders title", () => {
+    setup({ title: "Hello" });
+    expect(screen.getByText("Hello")).toBeInTheDocument();
+  });
+
+  it("uses custom tooltip", () => {
+    const CustomTooltip = vi.fn(() => <div>tooltip</div>);
+    setup({ title: "Test", dependencies: { CustomTooltip } });
+    expect(CustomTooltip).toHaveBeenCalled();
+  });
+
+  function setup(input: { title: string; dependencies?: Partial<typeof DEPENDENCIES> }) {
+    return render(
+      <MyComponent
+        title={input.title}
+        dependencies={MockComponents(DEPENDENCIES, input.dependencies)}
+      />
+    );
+  }
+});
+```
+
+**Important distinction**: Services should be injected via `useServices` hook (DI container), NOT via the `DEPENDENCIES` prop. The `DEPENDENCIES` prop is for components and hooks only.
+
+## MockComponents Utility
+
+Located at `apps/deploy-web/tests/unit/mocks.tsx`:
+
+```typescript
+export function MockComponents<T extends Record<string, any>>(
+  components: T,
+  overrides?: Partial<T>
+): Mocked<T> {
+  return Object.keys(components).reduce((all, name: keyof T) => {
+    all[name] = overrides?.[name] ||
+      (vi.fn(typeof name === "string" && name.startsWith("use")
+        ? undefined
+        : ComponentMock) as T[keyof T]);
+    return all;
+  }, {} as T);
+}
+```
+
+This auto-mocks:
+- Components as pass-through `<>{children}</>` renderers
+- Hooks (names starting with `use`) as `vi.fn()` returning `undefined`
+- Overrides replace specific dependencies
+
+There's also a `ComponentMock` helper for simpler cases.
+
+## Hook Testing
+
+Use `renderHook` from `@testing-library/react`. Inject dependencies directly.
+
+```typescript
+import { renderHook } from "@testing-library/react";
+
+describe(useDeployButtonFlow.name, () => {
+  it("returns deploy action when template param exists", () => {
+    const { result } = setup({ templateId: "abc123" });
+    expect(result.current.action).toBe("deploy");
+  });
+
+  function setup(searchParams: Record<string, string | null>) {
+    const params = createSearchParams(searchParams);
+    const useSearchParams = () => params as ReadonlyURLSearchParams;
+    return renderHook(() =>
+      useDeployButtonFlow({
+        dependencies: { useSearchParams, window: mockWindow }
+      })
+    );
+  }
+});
+```
+
+Simple hooks without dependencies:
+
+```typescript
+const { result } = renderHook(() => useCurrencyFormatter());
+expect(result.current(1234.56)).toBe("$1,234.56");
+```
+
+## Query Hook Testing
+
+Use the `setupQuery` utility from `apps/deploy-web/tests/unit/query-client.tsx`. It wraps `renderHook` with `TestContainerProvider` containing a `QueryClient` and mock services.
+
+```typescript
+import { setupQuery } from "@tests/unit/query-client";
+import { mock } from "vitest-mock-extended";
+
+describe(usePaymentMethodsQuery.name, () => {
+  it("returns payment methods on success", async () => {
+    const stripeService = mock<StripeService>({
+      getPaymentMethods: vi.fn().mockResolvedValue(mockMethods)
+    });
+
+    const { result } = setupQuery(
+      () => usePaymentMethodsQuery(),
+      { services: { stripe: () => stripeService } }
+    );
+
+    await vi.waitFor(() => {
+      expect(result.current.isSuccess).toBe(true);
+    });
+    expect(result.current.data).toEqual(mockMethods);
+  });
+});
+```
+
+## Container Component Testing
+
+For render-prop / children-as-function containers, use `createContainerTestingChildCapturer` from `apps/deploy-web/tests/unit/container-testing-child-capturer.tsx`.
+
+```typescript
+import { createContainerTestingChildCapturer } from "@tests/unit/container-testing-child-capturer";
+
+describe(BillingContainer.name, () => {
+  it("passes transaction data to children", async () => {
+    const childCapturer = createContainerTestingChildCapturer<ChildrenProps>();
+
+    render(
+      <BillingContainer dependencies={dependencies}>
+        {props => childCapturer.renderChild({ ...props })}
+      </BillingContainer>
+    );
+
+    const child = await childCapturer.awaitChild(() => true);
+    expect(child.data).toEqual(expectedTransactions);
+  });
+});
+```
+
+## Service Testing
+
+Frontend services are tested by constructing them directly with mocked dependencies:
+
+```typescript
+describe(FeatureFlagService.name, () => {
+  it("returns all flags enabled when enableAll is true", async () => {
+    const { service } = setup({ enableAll: true });
+    const flags = await service.getFlags();
+    expect(flags.every(f => f.enabled)).toBe(true);
+  });
+
+  function setup(options?: { enableAll?: boolean }) {
+    const unleash = mock<typeof unleashModule>();
+    const config = { NEXT_PUBLIC_UNLEASH_ENABLE_ALL: options?.enableAll ?? false } as ServerEnvConfig;
+    const service = new FeatureFlagService(unleash, config);
+    return { service, unleash };
+  }
+});
+```
+
+## queryBy vs getBy
+
+In frontend test expectations:
+- Use `getBy*` for presence assertions
+- Use `queryBy*` for absence assertions
+
+- `getBy*` throws if missing and prints useful DOM context (better for debugging presence failures)
+- `queryBy*` returns `null`, which is ideal for absence checks
+
+```typescript
+// Good
+expect(screen.getByText("John Doe")).toBeInTheDocument();
+expect(screen.queryByText("Admin")).not.toBeInTheDocument();
+
+// Bad
+expect(screen.queryByText("John Doe")).toBeInTheDocument();
+```
+
+## Snapshot Testing
+
+Use snapshot testing only for pure presentational (View-only) components with no logic. This is rare — most components have some behavior worth testing explicitly.
+
+```typescript
+it("matches snapshot", () => {
+  const { container } = setup({ variant: "primary" });
+  expect(container).toMatchSnapshot();
+});
+```
diff --git a/.cursor/rules/no-jest-mock.mdc b/.cursor/rules/no-jest-mock.mdc
@@ -1,48 +0,0 @@
----
-description: "Disallow use of jest.mock() in test files"
-globs: **/*.spec.ts,**/*.spec.tsx
-alwaysApply: false
----
-# Don't use jest.mock
-
-## Description
-
-Don't use `jest.mock()` to mock dependencies. Instead, use `jest-mock-extended` to create mocks and pass mocks as dependencies to the service under test.
-
-## Why
-
-- Avoid implicit dependencies: `jest.mock` mocks internal implementation details
-- Improve maintainability: explicit mocks make tests easier to understand and refactor
-- Better type safety: with jest-mock-extended, you get autocompletion and type checking for mocks.
-- No shared state state between tests: `jest.mock` introduce shared state which can lead to flaky and unreliable tests
-
-## Examples
-
-### Do this
-```ts
-import { mock } from "jest-mock-extended";
-
-describe("UserService", () => {
-  it("creates user", async () => {
-    const userRepository = mock<UserRepository>();
-    const userService = new UserService(userRepository);
-
-    userRepository.create.mockResolvedValue({ id: 1 });
-
-    await expect(userService.create()).resolves.toEqual({ id: 1 });
-  });
-});
-```
-
-### Don't do this
-
-```ts
-jest.mock("./user.repository");
-
-describe("UserService", () => {
-  it("creates user", async () => {
-    const userService = new UserService();
-    await expect(userService.create()).resolves.toEqual({ id: 1 });
-  });
-});
-```
diff --git a/.cursor/rules/query-by-in-tests.mdc b/.cursor/rules/query-by-in-tests.mdc
@@ -1,37 +0,0 @@
----
-description:
-globs: apps/deploy-web/**/*.spec.tsx,apps/provider-console/**/*.spec.tsx
-alwaysApply: false
----
-# Use queryBy instead of getBy in test expectations
-
-## Description
-- Use `queryBy` methods instead of `getBy` methods in test expectations
-- `queryBy` methods return `null` if element is not found, making it safer for testing both presence and absence of elements
-- `getBy` methods throw an error if element is not found, which can make tests harder to debug
-
-## File Pattern
-`*.spec.tsx`
-
-## Examples
-
-### Good
-```typescript
-// Testing presence of element
-expect(screen.queryByText("John Doe")).toBeInTheDocument();
-
-// Testing absence of element
-expect(screen.queryByText("John Doe")).not.toBeInTheDocument();
-```
-
-### Bad
-```typescript
-// Using getBy for presence check
-expect(screen.getByText("John Doe")).toBeInTheDocument();
-
-// Using getBy for absence check (will throw error)
-expect(screen.getByText("John Doe")).not.toBeInTheDocument();
-```
-
-## References
-- [DeploymentName.spec.tsx](mdc:apps/deploy-web/src/components/deployments/DeploymentName/DeploymentName.spec.tsx)
diff --git a/.cursor/rules/setup-instead-of-before-each.mdc b/.cursor/rules/setup-instead-of-before-each.mdc
@@ -1,51 +0,0 @@
----
-description:
-globs: **/*.spec.tsx,**/*.spec.ts
-alwaysApply: false
----
-# Use setup function instead of beforeEach
-
-## Description
-- Use `setup` function instead of `beforeEach`
-- `setup` function must be at the bottom of the root `describe` block
-- `setup` function creates an object under test and returns it
-- `setup` function should accept a single parameter with inline type definition
-- Don't use shared state in `setup` function
-- Don't specify return type of `setup` function
-
-## Examples
-
-### Good
-```typescript
-describe("UserProfile", () => {
-  it("renders user name when provided", () => {
-    setup({ name: "John Doe" });
-    expect(screen.queryByText("John Doe")).toBeInTheDocument();
-  });
-
-  function setup(input: { name?: string; email?: string; isLoading?: boolean; error?: string }) {
-    render(<UserProfile {...input} />);
-    return input;
-  }
-});
-```
-
-### Bad
-```typescript
-describe("UserProfile", () => {
-  let props: UserProfileProps;
-
-  beforeEach(() => {
-    props = { name: "John Doe" };
-    render(<UserProfile {...props} />);
-  });
-
-  it("renders user name when provided", () => {
-    expect(screen.getByText("John Doe")).toBeInTheDocument();
-  });
-});
-```
-
-## References
-- [DeploymentName.spec.tsx](mdc:apps/deploy-web/src/components/deployments/DeploymentName/DeploymentName.spec.tsx)
-- https://github.com/akash-network/console/discussions/910
diff --git a/.cursor/rules/test-descriptions.mdc b/.cursor/rules/test-descriptions.mdc
@@ -1,91 +0,0 @@
----
-description:
-globs: **/*.spec.tsx,**/*.spec.ts
-alwaysApply: false
----
-
-## Root Suite Description
-
-Whenever possible, use `<Subject under test>.name` in the root description. This helps to rename the subject and find all references of the subject using automated refactoring tools in your IDE. For example:
-
-### Good
-
-```ts
-import { ProviderProxyService } from './provider-proxy.service'
-
-describe(ProviderProxyService.name, () => {
-  // other tests
-})
-```
-
-### Bad
-
-Don't use the service name as a string in the root suite description because then we can't find service references in this location using automated refactoring tools
-
-```ts
-describe('ProviderProxyService', () => {
-  // other tests
-})
-```
-
-## Nested Suite Description
-
-For nested suite descriptions, use either a condition that starts with "when" or a single word representing the specific service method being tested:
-
-### Good
-
-```ts
-import { ProviderProxyService } from './provider-proxy.service'
-
-describe(ProviderProxyService.name, () => {
-  describe('sendManifestToProvider', () => {
-    // tests for sendManifestToProvider method
-  });
-
-  describe('when provider is down', () => {
-    // tests which validates behavior when provider is down, could do few retries for example
-  })
-})
-```
-
-### Bad
-
-```ts
-describe('ProviderProxyService', () => {
-  describe('sends manifest to provider', () => { // Better to use the method name here
-    // tests for sendManifestToProvider method
-  });
-
-  describe('provider is down', () => { // Missing "when" prefix for conditional descriptions
-    // tests which validate behavior when provider is down, could do few retries for example
-  })
-})
-```
-
-## Test Description
-
-Use present simple, 3rd person singular for test descriptions:
-
-### Good
-
-```ts
-import { ProviderProxyService } from './provider-proxy.service';
-
-describe(ProviderProxyService.name, () => {
-  it('is defined', () => {
-    // test implementation
-  })
-})
-```
-
-### Bad
-
-Do not prepend every test with "should" - it's redundant and makes descriptions noisy
-
-```ts
-describe('ProviderProxyService', () => {
-  it('should be defined', () => {
-    // test implementation
-  })
-})
-```
PATCH

echo "Gold patch applied."
