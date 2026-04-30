#!/usr/bin/env bash
set -euo pipefail

cd /workspace/aztec-packages

# Idempotency guard
if grep -qF "description: Guidelines for writing module READMEs that explain how a module wor" "yarn-project/.claude/skills/readme-writer/SKILL.md" && grep -qF "description: Best practices for implementing unit tests in this TypeScript monor" "yarn-project/.claude/skills/unit-test-implementation/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/yarn-project/.claude/skills/readme-writer/SKILL.md b/yarn-project/.claude/skills/readme-writer/SKILL.md
@@ -0,0 +1,231 @@
+---
+name: readme-writer
+description: Guidelines for writing module READMEs that explain how a module works to developers who need to use it or understand its internals. Use when documenting a module, package, or subsystem.
+---
+
+# Module README Writing Guide
+
+## File Placement
+
+Place the README in the same folder as the module it explains, not at the package root.
+
+```
+# Good: README next to the module it documents
+sequencer-client/src/sequencer/README.md
+archiver/src/archiver/l1/README.md
+
+# Also good: Package-level README for small packages
+slasher/README.md
+```
+
+Use package-level READMEs when the package is small or you want to explain the package as a whole.
+
+## Structure
+
+### 1. Overview
+
+Start with 2-4 sentences explaining what the module does and where it fits in the system.
+
+```markdown
+# L1 Transaction Utils
+
+This module handles sending L1 txs, including simulating txs, choosing gas prices,
+estimating gas limits, monitoring sent txs, speeding them up, and cancelling them.
+Each instance of `L1TxUtils` is stateful, corresponds to a given publisher EOA,
+and tracks its in-flight txs.
+```
+
+### 2. Usage Context
+
+Explain when and how this module is used. Who calls it? Under what conditions?
+
+```markdown
+## Usage
+
+The slasher is integrated into the Aztec node and activates when:
+1. The node is configured as a validator
+2. The validator is selected as proposer for a slot
+3. Slashable offenses have been detected
+```
+
+### 3. Code Examples
+
+For utility-like modules, include a code snippet showing typical usage:
+
+```typescript
+const versionManager = new version.VersionManager(DB_VERSION, rollupAddress, {
+  dataDir: '/path/to/data',
+  serviceName: 'my-database',
+});
+
+await versionManager.checkVersionAndHandle(
+  async () => await initializeFreshDatabase(),
+  async (oldVersion, newVersion) => await migrate(oldVersion, newVersion),
+);
+```
+
+### 4. Core Concepts
+
+Define domain-specific terms and objects (blocks, checkpoints, slots, proposals, offenses, etc.). Explain relationships between them.
+
+```markdown
+### Slot vs Block vs Checkpoint
+
+- **Slot**: A fixed time window (e.g., 72 seconds) during which a proposer can build blocks
+- **Block**: A single batch of transactions, executed and validated
+- **Checkpoint**: The collection of all blocks built in a slot, attested by validators
+```
+
+### 5. Main API
+
+List main methods without exhaustive parameter/return documentation. Focus on what each does:
+
+```markdown
+## API
+
+- `sendTransaction`: Sends an L1 tx and returns the tx hash. Consumes a nonce.
+- `monitorTransaction`: Monitors a sent tx and speeds up or cancels it.
+- `sendAndMonitorTransaction`: Combines sending and monitoring in a single call.
+```
+
+### 6. State Lifecycle
+
+Use tables to document object states and transitions:
+
+```markdown
+| From | To | Condition | Effect |
+|-|-|-|-|
+| `idle` | `sent` | `send_tx` | A new tx is sent and nonce is consumed |
+| `sent` | `speed-up` | `stall_time exceeded` | Tx replaced with higher gas |
+| `sent` | `mined` | `get_nonce(latest) > tx_nonce` | Tx confirmed |
+```
+
+### 7. Timing and Sequence
+
+Use ASCII diagrams or tables for temporal flows:
+
+```markdown
+T=0s    Slot begins
+T=0-2s  SYNCHRONIZING, PROPOSER_CHECK
+T=2s    Start building Block 1
+T=10s   Block 1 deadline, start Block 2
+...
+T=72s   Slot ends
+```
+
+For parallel operations, use multi-column timelines:
+
+```markdown
+Time | Proposer              | Validators
+-----|----------------------|------------------
+10s  | Finish Block 1       | (idle)
+12s  |                      | Receive Block 1
+18s  | Finish Block 2       | Re-executing Block 1
+```
+
+### 8. Dependencies
+
+Explain what other modules this connects to:
+
+```markdown
+## Integration Flow
+
+1. **Offense Detection**: Watchers emit `WANT_TO_SLASH_EVENT` when they detect violations
+2. **Offense Collection**: SlashOffensesCollector stores offenses in SlasherOffensesStore
+3. **Action Execution**: SequencerPublisher executes actions on L1
+```
+
+### 9. Error Handling
+
+Dedicate a section to unhappy paths and how deviations are handled:
+
+```markdown
+## Handling Timing Variations
+
+### Slow Initialization
+
+If initialization completes at 3s instead of 2s:
+- Block 1 has 1s less time (7s instead of 8s)
+- Sub-slot deadlines remain fixed
+- Still enough time to build, just with fewer transactions
+```
+
+### 10. Configuration
+
+Document configuration options with their purpose and constraints:
+
+```markdown
+## Configuration
+
+| Parameter | Default | Purpose |
+|-----------|---------|---------|
+| `slotDuration` | 72s | Total time for checkpoint |
+| `blockDuration` | 8s | Duration of each sub-slot |
+```
+
+Include considerations for how values relate to each other:
+
+```markdown
+The `slashingOffsetInRounds` needs to be strictly greater than the proof
+submission window to be able to slash for epoch prunes or data withholding.
+```
+
+### 11. Security
+
+Include when the module has security implications:
+
+```markdown
+## Vetoing
+
+The slashing system includes a veto mechanism that allows designated vetoers
+to block slash payloads during the execution delay period. This provides a
+safety valve for incorrectly proposed slashes.
+```
+
+## Writing Style
+
+### Explain Rationale
+
+Don't just document what happens—explain why:
+
+```markdown
+# Bad
+The last sub-slot is reserved for validator re-execution.
+
+# Good
+The last sub-slot is reserved for validator re-execution. Validators execute
+blocks sequentially with a ~2s propagation delay. For the last block, there's
+no next block to build while validators re-execute, so we must wait for them
+to finish before collecting attestations.
+```
+
+### Avoid Subjective Qualifiers
+
+```markdown
+# Bad
+This is a key aspect of the design with critical security implications.
+
+# Good
+This provides a safety valve for incorrectly proposed slashes.
+```
+
+### Be Succinct
+
+```markdown
+# Bad
+It is important to note that the configuration values must satisfy certain
+constraints which will be explained in detail in the following section.
+
+# Good
+These values must satisfy certain constraints (explained below).
+```
+
+### Include Only Relevant Sections
+
+Not every module needs every section. Skip sections that don't apply:
+- Small utilities don't need architecture sections
+- Stateless modules don't need lifecycle tables
+- Internal modules don't need usage examples
+- Not everything has security implications
+
+Ask yourself: "Does this section help someone understand or use this module?" If not, skip it.
diff --git a/yarn-project/.claude/skills/unit-test-implementation/SKILL.md b/yarn-project/.claude/skills/unit-test-implementation/SKILL.md
@@ -0,0 +1,426 @@
+---
+name: unit-test-implementation
+description: Best practices for implementing unit tests in this TypeScript monorepo. Use when writing new tests, refactoring existing tests, or fixing failing tests. Covers mocking strategies, test organization, helper functions, and assertion patterns.
+---
+
+# Unit Test Implementation Guide
+
+## Mocking Dependencies
+
+### Use jest-mock-extended for External Dependencies
+
+Use `jest-mock-extended` for dependencies that are external to the unit under test:
+
+```typescript
+import { mock, mockDeep, mockFn, type MockProxy } from "jest-mock-extended";
+
+let httpClient: MockProxy<HttpClient>;
+let database: MockProxy<Database>;
+
+beforeEach(() => {
+  httpClient = mock<HttpClient>();
+  database = mockDeep<Database>(); // Use mockDeep when mocking nested properties
+});
+```
+
+### When to Use Real Instances vs Mocks
+
+**Mock external dependencies** that are:
+
+- Difficult to set up and not to relevant to the behavior being tested
+- External services or APIs
+
+**Use real instances** for dependencies that are:
+
+- Tightly coupled to the subject (e.g., a config object, a small utility class)
+- Pure functions or simple data transformers
+- Part of the same module and tested together
+
+**When in doubt, ask the user** which dependencies should be mocked and which should use real instances. The decision depends on what behavior you're trying to test.
+
+### Prefer mockReturnValueOnce Over Complex mockImplementation
+
+```typescript
+// ❌ Bad: Counter-based implementation
+let callCount = 0;
+mock.fetch.mockImplementation(() => {
+  callCount++;
+  return callCount === 1 ? responseA : responseB;
+});
+
+// ✅ Good: Clear sequence of return values
+mock.fetch
+  .mockReturnValueOnce(responseA)
+  .mockReturnValueOnce(responseB)
+  .mockReturnValue(defaultResponse);
+```
+
+### When Mock Behavior Becomes Too Complex, Create a Mock Class
+
+If mocking requires complex state management (tracking multiple calls, conditional responses based on arguments, etc.), create a proper fake implementation instead:
+
+```typescript
+/**
+ * A fake implementation for testing. Does NOT use jest mocks internally.
+ * Implements the same interface as the real class.
+ */
+export class MockCache {
+  private store = new Map<string, Item>();
+
+  // Track calls for assertions
+  public getCalls: string[] = [];
+  public setCalls: Array<{ key: string; value: Item }> = [];
+
+  async get(key: string): Promise<Item | undefined> {
+    this.getCalls.push(key);
+    return this.store.get(key);
+  }
+
+  async set(key: string, value: Item): Promise<void> {
+    this.setCalls.push({ key, value });
+    this.store.set(key, value);
+  }
+
+  /** Seed data for testing */
+  seed(entries: Array<[string, Item]>): this {
+    entries.forEach(([k, v]) => this.store.set(k, v));
+    return this;
+  }
+
+  /** Reset for reuse */
+  reset(): void {
+    this.store.clear();
+    this.getCalls = [];
+    this.setCalls = [];
+  }
+}
+```
+
+## Avoiding Type Casts
+
+### Never Use `as any`
+
+Type casts like `as any` hide type errors and make tests brittle. They indicate either:
+
+1. The test data doesn't match the expected type (fix the test data)
+2. The types are wrong (fix the types)
+3. The test is accessing internals incorrectly (use proper test patterns)
+
+```typescript
+// ❌ Bad: Hiding type mismatches
+const result = someFn() as any;
+mockFn.mockReturnValue({ partial: "data" } as any);
+
+// ✅ Good: Proper typing
+const result: ExpectedType = someFn();
+mockFn.mockReturnValue(createValidMockData());
+```
+
+### Minimize Type Assertions
+
+If you must use type assertions, prefer the most specific type possible:
+
+```typescript
+// ❌ Bad
+const config = {} as any;
+
+// ⚠️ Acceptable when truly needed
+const config = { knownField: "value" } as Partial<Config>;
+
+// ✅ Best: Use factory functions
+const config = createTestConfig({ knownField: "value" });
+```
+
+## Exposing Internals for Testing
+
+### Use a Derived Test Class
+
+When you need to access or modify internal state, create a test subclass that exposes protected members:
+
+**Base class (production code):**
+
+```typescript
+class MyService {
+  protected config: Config;
+
+  constructor(config: Config) {
+    this.config = config;
+  }
+
+  protected async waitUntilReady(): Promise<void> {
+    await sleep(1000);
+  }
+
+  async execute(): Promise<Result> {
+    await this.waitUntilReady();
+    // ... implementation
+  }
+}
+```
+
+**Test class (test file):**
+
+```typescript
+class TestMyService extends MyService {
+  /** Override to skip delays in tests */
+  protected override async waitUntilReady(): Promise<void> {
+    return Promise.resolve();
+  }
+
+  /** Expose config for modification */
+  public updateConfig(partial: Partial<Config>): void {
+    this.config = { ...this.config, ...partial };
+  }
+
+  /** Expose config for assertions */
+  public getConfig(): Config {
+    return this.config;
+  }
+}
+```
+
+**Note:** This requires the base class to use `protected` (not `private`) for members you need to access. Feel free to modify the base class for this when writing its unit tests.
+
+## Test Organization
+
+### Move Setup Logic to beforeEach
+
+```typescript
+describe("MyFeature", () => {
+  let subject: TestMyService;
+  let dependency: MockProxy<Dependency>;
+
+  beforeEach(() => {
+    dependency = mock<Dependency>();
+    subject = new TestMyService(dependency);
+  });
+
+  // Tests modify subject via update methods, not direct mutation
+});
+```
+
+### Use Nested beforeEach for Variations
+
+```typescript
+describe("with caching enabled", () => {
+  beforeEach(() => {
+    subject.updateConfig({ cacheEnabled: true });
+  });
+
+  it("returns cached results", async () => {
+    /* ... */
+  });
+});
+
+describe("with caching disabled", () => {
+  beforeEach(() => {
+    subject.updateConfig({ cacheEnabled: false });
+  });
+
+  it("always fetches fresh data", async () => {
+    /* ... */
+  });
+});
+```
+
+### Avoid Direct Object Mutation
+
+```typescript
+// ❌ Bad: Direct mutation
+config.maxRetries = 5;
+
+// ✅ Good: Use update methods
+subject.updateConfig({ maxRetries: 5 });
+```
+
+## Helper Functions for Readability
+
+### Extract Repeated Setup Patterns
+
+When you find yourself repeating the same 3-4 setup calls across multiple tests, extract them:
+
+```typescript
+// ❌ Bad: Repeated in every test
+it("test 1", async () => {
+  const items = await Promise.all([createItem(1), createItem(2)]);
+  mockSource.getItems.mockResolvedValue(items);
+  mockValidator.validate.mockResolvedValue(true);
+  // ... actual test
+});
+
+it("test 2", async () => {
+  const items = await Promise.all([createItem(1), createItem(2)]);
+  mockSource.getItems.mockResolvedValue(items);
+  mockValidator.validate.mockResolvedValue(true);
+  // ... actual test
+});
+
+// ✅ Good: Extracted helper
+async function setupValidItems(count: number) {
+  const items = await Promise.all(times(count, (i) => createItem(i)));
+  mockSource.getItems.mockResolvedValue(items);
+  mockValidator.validate.mockResolvedValue(true);
+  return items;
+}
+
+it("test 1", async () => {
+  const items = await setupValidItems(2);
+  // ... actual test
+});
+```
+
+### Extract Repeated Assertion Patterns
+
+When the same assertion sequence appears in multiple tests:
+
+```typescript
+// ❌ Bad: Repeated in every test
+it("test 1", async () => {
+  await subject.publish();
+
+  expect(publisher.enqueue).toHaveBeenCalledTimes(1);
+  expect(publisher.enqueue).toHaveBeenCalledWith(
+    expect.objectContaining({ type: "proposal" }),
+    expect.any(Date)
+  );
+  expect(publisher.send).toHaveBeenCalled();
+});
+
+// ✅ Good: Extracted helper
+const expectPublished = () => {
+  expect(publisher.enqueue).toHaveBeenCalledTimes(1);
+  expect(publisher.enqueue).toHaveBeenCalledWith(
+    expect.objectContaining({ type: "proposal" }),
+    expect.any(Date)
+  );
+  expect(publisher.send).toHaveBeenCalled();
+};
+
+it("test 1", async () => {
+  await subject.publish();
+  expectPublished();
+});
+```
+
+**Note:** Only extract when the pattern repeats across multiple tests. A single complex assertion block doesn't need extraction.
+
+### Helper Location
+
+- **Suite-specific helpers:** Define inside the describe block
+- **Package-shared helpers:** Move to `src/test/utils.ts`
+- **Cross-package helpers:** Consider if they belong in a shared testing package
+
+## Assertions
+
+### Be Specific
+
+```typescript
+// ❌ Too generic - doesn't verify actual behavior
+expect(mock.save).toHaveBeenCalledWith(expect.anything());
+
+// ✅ Specific - verifies the important parts
+expect(mock.save).toHaveBeenCalledWith(
+  expect.objectContaining({
+    id: expectedId,
+    status: "active",
+  })
+);
+```
+
+### Use Mock Class Properties for Assertions
+
+When using custom mock classes, assert on tracked properties:
+
+```typescript
+expect(mockCache.getCalls).toEqual(["key1", "key2"]);
+expect(mockCache.setCalls).toHaveLength(1);
+expect(mockCache.setCalls[0]).toEqual({ key: "key1", value: expectedValue });
+```
+
+## Reusable Test Suites
+
+For testing multiple implementations of the same interface (e.g., in-memory vs persistent storage), create a shared test suite:
+
+```typescript
+// cache_test_suite.ts
+export function describeCacheImplementation(
+  name: string,
+  createCache: () => Cache
+) {
+  describe(name, () => {
+    let cache: Cache;
+
+    beforeEach(() => {
+      cache = createCache();
+    });
+
+    it("stores and retrieves values", async () => {
+      await cache.set("key", "value");
+      expect(await cache.get("key")).toBe("value");
+    });
+
+    it("returns undefined for missing keys", async () => {
+      expect(await cache.get("missing")).toBeUndefined();
+    });
+  });
+}
+
+// memory_cache.test.ts
+describeCacheImplementation("MemoryCache", () => new MemoryCache());
+
+// redis_cache.test.ts
+describeCacheImplementation("RedisCache", () => new RedisCache(mockClient));
+```
+
+## Testing Async Operations
+
+### Use Promise.allSettled for Multiple Outcomes
+
+```typescript
+it("handles mixed success and failure", async () => {
+  const results = await Promise.allSettled([
+    subject.processValid(),
+    subject.processInvalid(),
+  ]);
+
+  expect(results).toEqual([
+    { status: "fulfilled", value: expectedValue },
+    {
+      status: "rejected",
+      reason: expect.objectContaining({ message: "Invalid" }),
+    },
+  ]);
+});
+```
+
+### Control Time in Tests
+
+```typescript
+beforeEach(() => {
+  jest.useFakeTimers();
+});
+
+afterEach(() => {
+  jest.useRealTimers();
+});
+
+it("retries after delay", async () => {
+  mock.fetch.mockRejectedValueOnce(new Error("fail")).mockResolvedValue(data);
+
+  const promise = subject.fetchWithRetry();
+
+  await jest.advanceTimersByTimeAsync(1000);
+
+  await expect(promise).resolves.toEqual(data);
+});
+```
+
+## Running Tests
+
+```bash
+cd <package-name>
+yarn tsc -b                                    # Always compile first
+yarn test my-class.test.ts                     # Run specific test file
+yarn test my-class.test.ts -t 'test name'      # Run specific test
+env LOG_LEVEL=verbose yarn test my-class.test.ts  # With debug logging
+```
PATCH

echo "Gold patch applied."
