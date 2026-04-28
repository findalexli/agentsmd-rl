#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opik

# Idempotency guard
if grep -qF "**Rule**: When you have repeated string prefixes or patterns, define them as con" "apps/opik-backend/.cursor/rules/code_quality.mdc" && grep -qF "**Rule**: Remove commented-out constants and unused field declarations instead o" "apps/opik-backend/.cursor/rules/code_style.mdc" && grep -qF "Use PODAM for generating test data. See the comprehensive [Test Data Generation " "apps/opik-backend/.cursor/rules/general.mdc" && grep -qF "**Why This Is Wrong**: This test extracts actual values from the API response, s" "apps/opik-backend/.cursor/rules/test_assertions.mdc" && grep -qF "**Background**: Awaitility should only be used when dealing with truly asynchron" "apps/opik-backend/.cursor/rules/test_async_patterns.mdc" && grep -qF "**Note**: For test data generation in parameterized tests, follow the [PODAM gui" "apps/opik-backend/.cursor/rules/testing.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/apps/opik-backend/.cursor/rules/code_quality.mdc b/apps/opik-backend/.cursor/rules/code_quality.mdc
@@ -249,6 +249,71 @@ public void createUser(UserCreateRequest request) {
 }
 ```
 
+### **String Constants and Templates**
+
+**Rule**: When you have repeated string prefixes or patterns, define them as constants with string formatting templates.
+
+```java
+// ❌ BAD: Hardcoded Repeated String Patterns
+private static final Map<AutomationRuleEvaluatorField, String> FIELD_MAP = new EnumMap<>(
+    ImmutableMap.<AutomationRuleEvaluatorField, String>builder()
+        .put(AutomationRuleEvaluatorField.ID, "rule." + ID_DB)
+        .put(AutomationRuleEvaluatorField.NAME, "rule." + NAME_DB)
+        .put(AutomationRuleEvaluatorField.TYPE, "evaluator." + TYPE_DB)
+        .put(AutomationRuleEvaluatorField.ENABLED, "evaluator." + ENABLED_DB)
+        .put(AutomationRuleEvaluatorField.PROJECT_ID, "evaluator." + PROJECT_ID_DB)
+        .build());
+
+// ✅ GOOD: String Template Constants
+// Define templates at the top of the class
+private static final String RULE_PREFIX = "rule.%s";
+private static final String EVALUATOR_PREFIX = "evaluator.%s";
+
+private static final Map<AutomationRuleEvaluatorField, String> FIELD_MAP = new EnumMap<>(
+    ImmutableMap.<AutomationRuleEvaluatorField, String>builder()
+        .put(AutomationRuleEvaluatorField.ID, RULE_PREFIX.formatted(ID_DB))
+        .put(AutomationRuleEvaluatorField.NAME, RULE_PREFIX.formatted(NAME_DB))
+        .put(AutomationRuleEvaluatorField.TYPE, EVALUATOR_PREFIX.formatted(TYPE_DB))
+        .put(AutomationRuleEvaluatorField.ENABLED, EVALUATOR_PREFIX.formatted(ENABLED_DB))
+        .put(AutomationRuleEvaluatorField.PROJECT_ID, EVALUATOR_PREFIX.formatted(PROJECT_ID_DB))
+        .build());
+```
+
+**Benefits**:
+- Single source of truth for prefixes
+- Easier to refactor if prefix changes
+- More maintainable and readable
+- Less error-prone when adding new mappings
+
+### **Constants Organization**
+
+Group related constants by category with clear comments:
+
+```java
+public class FilterQueryBuilder {
+    
+    // Database column names - base fields
+    private static final String ID_DB = "id";
+    private static final String NAME_DB = "name";
+    private static final String TYPE_DB = "type";
+    
+    // Database column names - timestamps
+    private static final String CREATED_AT_DB = "created_at";
+    private static final String LAST_UPDATED_AT_DB = "last_updated_at";
+    
+    // Database column names - audit fields
+    private static final String CREATED_BY_DB = "created_by";
+    private static final String LAST_UPDATED_BY_DB = "last_updated_by";
+    
+    // Table prefixes
+    private static final String RULE_PREFIX = "rule.%s";
+    private static final String EVALUATOR_PREFIX = "evaluator.%s";
+    
+    // Sensitive fields (DO NOT expose in API)
+    // private static final String WEBHOOK_SECRET_TOKEN_DB = "webhook_secret_token"; // REMOVED
+}
+```
+
 ### **Configuration Management**
 
 - Use Dropwizard configuration classes
diff --git a/apps/opik-backend/.cursor/rules/code_style.mdc b/apps/opik-backend/.cursor/rules/code_style.mdc
@@ -0,0 +1,69 @@
+---
+description: Code Style guidelines
+globs: apps/opik-backend/**/*
+alwaysApply: false
+---
+# Backend Java Code Style Guidelines
+
+## Comment Hygiene
+
+### Clean Up Unused Code
+
+**Rule**: Remove commented-out constants and unused field declarations instead of leaving them in the codebase.
+
+```java
+// ❌ BAD: Leaving commented-out sensitive field
+private static final String WEBHOOK_URL_DB = "webhook_url";
+// private static final String WEBHOOK_SECRET_TOKEN_DB = "webhook_secret_token"; // Don't expose
+
+// ✅ GOOD: Just remove it completely
+private static final String WEBHOOK_URL_DB = "webhook_url";
+// Webhook secret token is intentionally not included for security reasons
+```
+
+**When to keep comments**:
+- Explaining WHY something was removed (in PR description)
+- Documenting business decisions
+- Clarifying non-obvious security constraints
+
+## Method Parameter Formatting
+
+### Consistent Parameter Alignment
+
+For methods with multiple parameters, use consistent line breaks:
+
+```java
+// ✅ GOOD: Each parameter on its own line when breaking
+public Response find(
+        @QueryParam("project_id") UUID projectId,
+        @QueryParam("id") 
+        @Schema(description = "Filter by rule ID (partial match)") 
+        String id,
+        @QueryParam("filters") String filters,
+        @QueryParam("sorting") String sorting,
+        @QueryParam("page") @DefaultValue("1") int page,
+        @QueryParam("size") @DefaultValue("10") int size) {
+    // method body
+}
+```
+
+## Enum and Map Initialization
+
+### ImmutableMap Patterns
+
+Use consistent formatting for map initialization:
+
+```java
+// ✅ GOOD: Consistent formatting with clear structure
+private static final Map<Field, String> FIELD_MAP = new EnumMap<>(
+    ImmutableMap.<Field, String>builder()
+        .put(Field.ID, RULE_PREFIX.formatted(ID_DB))
+        .put(Field.NAME, RULE_PREFIX.formatted(NAME_DB))
+        .put(Field.TYPE, EVALUATOR_PREFIX.formatted(TYPE_DB))
+        .build());
+```
+
+## Related Rules
+
+- [Code Quality Guidelines](mdc:apps/opik-backend/.cursor/rules/code_quality.mdc)
+- [General Guidelines](mdc:apps/opik-backend/.cursor/rules/general.mdc)
diff --git a/apps/opik-backend/.cursor/rules/general.mdc b/apps/opik-backend/.cursor/rules/general.mdc
@@ -197,24 +197,7 @@ void shouldThrowBadRequestException_whenInvalidInput() {
 
 ### **Test Data Generation**
 
-Use PODAM for generating test data:
-
-```java
-@Autowired
-private PodamFactory podamFactory;
-
-@Test
-void shouldCreateEntity_whenValidRequest() {
-    // Given
-    var request = podamFactory.manufacturePojo(EntityCreateRequest.class);
-    
-    // When
-    var result = entityService.createEntity(request);
-    
-    // Then
-    assertThat(result).isNotNull();
-}
-```
+Use PODAM for generating test data. See the comprehensive [Test Data Generation guidelines](mdc:apps/opik-backend/.cursor/rules/testing.mdc#test-data-generation) in the testing documentation.
 
 ## Common Patterns
 
diff --git a/apps/opik-backend/.cursor/rules/test_assertions.mdc b/apps/opik-backend/.cursor/rules/test_assertions.mdc
@@ -0,0 +1,229 @@
+---
+description: Tests Assertions
+globs: apps/opik-backend/**/*
+alwaysApply: false
+---
+# Backend Test Assertion Patterns
+
+## Testing Sorting Logic
+
+### Test Actual Sorting, Not Self-Fulfilling Prophecy
+
+**Critical Issue**: Tests must verify that the API actually sorts data correctly, not just verify that sorting the same list twice produces the same result.
+
+### ❌ BAD: Self-Fulfilling Test (Does Not Test Sorting)
+
+```java
+@Test
+void testSorting() {
+    // Create test data
+    createTestData();
+    
+    // Fetch from API with sorting
+    var page = api.findSorted("name", "ASC");
+    
+    // ❌ BAD: Extract actual values, then sort them, then compare
+    var actualValues = page.content().stream()
+        .map(Entity::getName)
+        .toList();
+    
+    var expectedValues = new ArrayList<>(actualValues);
+    expectedValues.sort(Comparator.naturalOrder()); // Sorting the actual results!
+    
+    assertThat(actualValues).isEqualTo(expectedValues);
+    // This test will ALWAYS pass, even if API sorting is broken!
+}
+```
+
+**Why This Is Wrong**: This test extracts actual values from the API response, sorts those same values, and then compares them. This will always pass regardless of whether the API actually sorted correctly.
+
+### ✅ GOOD: Test Against Known Data Order
+
+```java
+@Test
+void testSorting() {
+    // Create test data with KNOWN values in KNOWN order
+    var entity1 = createEntity("Alice", 100);
+    var entity2 = createEntity("Bob", 200);
+    var entity3 = createEntity("Charlie", 300);
+    
+    // Fetch from API with sorting by name ASC
+    var page = api.findSorted("name", "ASC");
+    
+    // ✅ GOOD: Verify actual API order matches expected order
+    assertThat(page.content())
+        .extracting(Entity::getName)
+        .containsExactly("Alice", "Bob", "Charlie");
+    
+    // Verify with DESC
+    var pageDesc = api.findSorted("name", "DESC");
+    assertThat(pageDesc.content())
+        .extracting(Entity::getName)
+        .containsExactly("Charlie", "Bob", "Alice");
+}
+```
+
+### ✅ ALTERNATIVE: Use AssertJ Sorting Assertions
+
+```java
+@Test
+void testSorting() {
+    // Create test data
+    createRandomTestData(10);
+    
+    // Fetch with sorting
+    var page = api.findSorted("name", "ASC");
+    
+    // ✅ GOOD: Use AssertJ to verify list is sorted
+    assertThat(page.content())
+        .extracting(Entity::getName)
+        .isSorted(); // This checks actual sorting
+    
+    // For DESC
+    var pageDesc = api.findSorted("name", "DESC");
+    assertThat(pageDesc.content())
+        .extracting(Entity::getName)
+        .isSortedAccordingTo(Comparator.reverseOrder());
+}
+```
+
+### ✅ BEST: Compare Against Pre-Sorted Data
+
+```java
+@ParameterizedTest
+@MethodSource("sortingTestCases")
+void testSorting(String field, String direction, Comparator<Entity> comparator) {
+    // Create test data
+    var entities = IntStream.range(0, 5)
+        .mapToObj(i -> factory.manufacturePojo(Entity.class))
+        .toList();
+    
+    entities.forEach(e -> api.create(e));
+    
+    // Sort the ORIGINAL test data using the expected comparator
+    var expectedOrder = entities.stream()
+        .sorted(direction.equals("ASC") ? comparator : comparator.reversed())
+        .map(Entity::getId)
+        .toList();
+    
+    // Fetch from API with sorting
+    var page = api.findSorted(field, direction);
+    
+    // ✅ BEST: Compare API result against independently sorted original data
+    var actualOrder = page.content().stream()
+        .map(Entity::getId)
+        .toList();
+    
+    assertThat(actualOrder).isEqualTo(expectedOrder);
+}
+```
+
+## Why The Bad Pattern Fails
+
+The problematic pattern:
+```java
+var actualValues = getFromApi();
+var expectedValues = new ArrayList<>(actualValues);
+expectedValues.sort(...);
+assertThat(actualValues).isEqualTo(expectedValues);
+```
+
+This is a **tautology** - it will always pass because:
+1. You're comparing a list against a sorted version of itself
+2. Even if the API returned completely random order, this test would pass
+3. The test doesn't verify the API did any sorting
+
+**This pattern doesn't test anything meaningful!**
+
+## Proper Sorting Test Structure
+
+### Three Valid Approaches:
+
+1. **Known Values**: Create entities with specific values, verify exact order
+2. **Sorting Assertions**: Use AssertJ's `.isSorted()` or `.isSortedAccordingTo()`
+3. **Pre-Sorted Comparison**: Sort original data independently, compare with API results
+
+### Complete Example
+
+```java
+@Nested
+@DisplayName("Sorting Tests")
+class SortingTests {
+    
+    @ParameterizedTest(name = "Sort by {0} {1}")
+    @MethodSource("sortingTestCases")
+    void testEntitySorting(String field, String direction, 
+                          Comparator<Entity> comparator) {
+        // Arrange: Create 10 entities with random data
+        var originalEntities = IntStream.range(0, 10)
+            .mapToObj(i -> factory.manufacturePojo(Entity.class))
+            .toList();
+        
+        // Save to database
+        originalEntities.forEach(entity -> repository.save(entity));
+        
+        // Act: Query with sorting
+        var result = service.findAll(field, direction);
+        
+        // Assert: Verify sorting
+        // Method 1: Check if sorted using AssertJ
+        var actualValues = result.stream()
+            .map(getFieldExtractor(field))
+            .toList();
+        
+        if (direction.equals("ASC")) {
+            assertThat(actualValues).isSorted();
+        } else {
+            assertThat(actualValues).isSortedAccordingTo(Comparator.reverseOrder());
+        }
+        
+        // Method 2: Compare with independently sorted original data
+        var expectedOrder = originalEntities.stream()
+            .sorted(direction.equals("ASC") ? comparator : comparator.reversed())
+            .map(Entity::getId)
+            .toList();
+        
+        var actualOrder = result.stream()
+            .map(Entity::getId)
+            .toList();
+        
+        assertThat(actualOrder).isEqualTo(expectedOrder);
+    }
+    
+    static Stream<Arguments> sortingTestCases() {
+        return Stream.of(
+            Arguments.of("name", "ASC", Comparator.comparing(Entity::getName)),
+            Arguments.of("name", "DESC", Comparator.comparing(Entity::getName)),
+            Arguments.of("createdAt", "ASC", Comparator.comparing(Entity::getCreatedAt)),
+            Arguments.of("createdAt", "DESC", Comparator.comparing(Entity::getCreatedAt))
+        );
+    }
+}
+```
+
+## Testing Filtering Logic
+
+Similar principles apply to filtering tests - verify against known data:
+
+```java
+@Test
+void testFiltering() {
+    // Create entities with known values
+    var entity1 = createEntity("test-123");
+    var entity2 = createEntity("test-456");
+    var entity3 = createEntity("other-789");
+    
+    // Apply filter
+    var results = api.findByName("test");
+    
+    // ✅ GOOD: Verify against known matching entities
+    assertThat(results)
+        .extracting(Entity::getId)
+        .containsExactlyInAnyOrder(entity1.getId(), entity2.getId())
+        .doesNotContain(entity3.getId());
+}
+```
+
+## Related Rules
+
+- [Testing Guidelines](mdc:apps/opik-backend/.cursor/rules/testing.mdc)
diff --git a/apps/opik-backend/.cursor/rules/test_async_patterns.mdc b/apps/opik-backend/.cursor/rules/test_async_patterns.mdc
@@ -0,0 +1,192 @@
+---
+description: Test Async Patterns
+globs: apps/opik-backend/**/*
+alwaysApply: false
+---
+# Backend Test Async and Timing Patterns
+
+## Avoid Awaitility in Synchronous Tests
+
+### Rule: Don't Use Awaitility for MySQL Synchronous Operations
+
+**Background**: Awaitility should only be used when dealing with truly asynchronous operations. MySQL operations in Opik backend tests are synchronous and transactional.
+
+### ❌ BAD: Using Awaitility for Synchronous Operations
+
+```java
+// When testing MySQL-based CRUD operations that are synchronous
+evaluatorsResourceClient.createEvaluator(evaluator, WORKSPACE_NAME, API_KEY);
+
+// ❌ BAD: Unnecessary Awaitility for synchronous data
+Awaitility.await().pollInterval(500, TimeUnit.MILLISECONDS).untilAsserted(() -> {
+    var page = evaluatorsResourceClient.findEvaluatorPage(
+        projectId, null, null, sorting, 1, 10, WORKSPACE_NAME, API_KEY);
+    
+    assertThat(page.content()).hasSizeGreaterThanOrEqualTo(5);
+    // assertions...
+});
+```
+
+### ✅ GOOD: Direct Assertions for Synchronous Operations
+
+```java
+// Create data synchronously
+evaluatorsResourceClient.createEvaluator(evaluator, WORKSPACE_NAME, API_KEY);
+
+// Direct query - no waiting needed
+var page = evaluatorsResourceClient.findEvaluatorPage(
+    projectId, null, null, sorting, 1, 10, WORKSPACE_NAME, API_KEY);
+
+// Direct assertions
+assertThat(page.content()).hasSize(5);
+assertThat(page.content()).isSortedAccordingTo(comparator);
+```
+
+## When to Use Awaitility
+
+### Use Awaitility Only For:
+
+1. **Asynchronous Message Processing**: Kafka consumers, message queues
+2. **Background Jobs**: Scheduled tasks, async processors
+3. **External Service Polling**: Waiting for external system state changes
+4. **Event-Driven Systems**: Waiting for event propagation
+
+### Example: Valid Awaitility Usage
+
+```java
+// ✅ GOOD: Waiting for async Kafka message processing
+kafkaProducer.send(message);
+
+Awaitility.await()
+    .atMost(5, TimeUnit.SECONDS)
+    .pollInterval(100, TimeUnit.MILLISECONDS)
+    .untilAsserted(() -> {
+        var processed = repository.findProcessedMessage(message.getId());
+        assertThat(processed).isNotNull();
+    });
+```
+
+## Alternative to Thread.sleep()
+
+### Avoid Thread.sleep() in Tests
+
+**Rule**: Instead of using `Thread.sleep()` to create time gaps, use timestamp manipulation or Instant-based approaches.
+
+### ❌ BAD: Using Thread.sleep()
+
+```java
+// Create first entity
+var entity1 = client.create(data1);
+
+var timestamp = Instant.now();
+Thread.sleep(1000); // ❌ Slows down tests
+
+// Create second entity
+var entity2 = client.create(data2);
+
+// Filter by timestamp
+var results = client.findAfter(timestamp);
+```
+
+### ✅ GOOD: Use Timestamp Manipulation or Controlled Data
+
+```java
+// Option 1: Use explicit timestamps in test data
+var timestamp1 = Instant.now().minusSeconds(10);
+var timestamp2 = Instant.now();
+
+var entity1 = Entity.builder()
+    .createdAt(timestamp1)
+    .build();
+var entity2 = Entity.builder()
+    .createdAt(timestamp2)
+    .build();
+
+// Option 2: Accept small time differences and use millis precision
+var timestampBefore = Instant.now();
+var entity1 = client.create(data1);
+var entity2 = client.create(data2);
+
+// Most database timestamps have enough precision
+var results = client.findAfter(timestampBefore);
+assertThat(results).contains(entity1, entity2);
+```
+
+## Troubleshooting Test Timing Issues
+
+### If Tests Pass Locally But Fail in CI
+
+**Symptoms**: Tests pass on local machine but fail in GitHub Actions or CI environment.
+
+**Common Causes**:
+1. **Race conditions**: Test assumes synchronous behavior but operation is async
+2. **Database replication lag**: Using read replicas with replication delay
+3. **Resource contention**: CI has slower CPU/memory causing timing issues
+
+**Solutions**:
+
+```java
+// ❌ BAD: Assuming instant database consistency in replicated setup
+entity.create();
+var result = entity.find(); // May fail if replica is lagging
+
+// ✅ GOOD: If replication exists, add appropriate wait with timeout
+entity.create();
+
+if (hasReplication()) {
+    Awaitility.await()
+        .atMost(2, TimeUnit.SECONDS)
+        .untilAsserted(() -> {
+            var result = entity.find();
+            assertThat(result).isNotNull();
+        });
+} else {
+    var result = entity.find();
+    assertThat(result).isNotNull();
+}
+```
+
+### Investigation Checklist
+
+When tests fail inconsistently in CI:
+
+- [ ] Check if database has replication configured
+- [ ] Verify database connection is not using eventual consistency
+- [ ] Review if caching layer could cause stale reads
+- [ ] Examine if test uses fire-and-forget async patterns
+- [ ] Look for race conditions in concurrent test execution
+
+## Test Performance Considerations
+
+### Keep Tests Fast
+
+- **Avoid Awaitility** unless absolutely necessary (adds minimum 100-500ms per poll)
+- **No Thread.sleep()** - wastes time and makes tests slower
+- **Use Transactional Tests** - rollback after each test for isolation
+- **Parallel Execution** - ensure tests can run in parallel safely
+
+### Example: Fast Test Pattern
+
+```java
+@Test
+void testSorting() {
+    // Arrange: Create test data (synchronous, fast)
+    var entities = IntStream.range(0, 5)
+        .mapToObj(i -> factory.manufacturePojo(Entity.class))
+        .toList();
+    entities.forEach(client::create);
+    
+    // Act: Execute query (synchronous, returns immediately)
+    var page = client.findSorted("name", "ASC");
+    
+    // Assert: Verify results (no waiting needed)
+    assertThat(page.content())
+        .extracting(Entity::getName)
+        .isSorted();
+}
+```
+
+## Related Rules
+
+- [Testing Guidelines](mdc:apps/opik-backend/.cursor/rules/testing.mdc)
+- [MySQL Transaction Patterns](mdc:apps/opik-backend/.cursor/rules/mysql.mdc)
diff --git a/apps/opik-backend/.cursor/rules/testing.mdc b/apps/opik-backend/.cursor/rules/testing.mdc
@@ -156,6 +156,30 @@ void createUsers() {
 }
 ```
 
+### **Leverage Random Generation**
+
+**Rule**: Use `factory.manufacturePojo()` to generate random test data instead of manually setting values, unless specific values are required for the test case.
+
+```java
+// ❌ BAD: Manually setting values that don't need to be specific
+var builder = factory.manufacturePojo(AutomationRuleEvaluatorLlmAsJudge.class).toBuilder()
+    .projectId(projectId);
+
+if (field.equals("name")) {
+    builder.name("name-" + (char) ('a' + i) + "-" + RandomStringUtils.randomAlphanumeric(5));
+} else if (field.equals("sampling_rate")) {
+    builder.samplingRate((float) (i + 1) / 10);
+}
+
+// ✅ GOOD: Let factory generate random values, only override when necessary
+var evaluator = factory.manufacturePojo(AutomationRuleEvaluatorLlmAsJudge.class).toBuilder()
+    .projectId(projectId)
+    .build();
+
+// Factory generates sufficiently random values for testing sorting
+// If values collide, use secondary sort by id (which is time-based)
+```
+
 ## Assertion Best Practices
 
 ### **Object Equality vs Field-by-Field Assertions**
@@ -239,7 +263,51 @@ void createUserWhenInvalidInputThrowsBadRequestException() {
 
 ## Parameterized Testing
 
-### **Using @ParameterizedTest**
+### **Use Parameterized Tests to Reduce Duplication**
+
+**Rule**: When testing multiple values/scenarios of the same behavior, use `@ParameterizedTest` with `@MethodSource` instead of writing separate test methods.
+
+```java
+// ❌ BAD: Duplicate Test Methods
+@Test
+void testSortByNameAsc() {
+    // Test logic for name ASC
+}
+
+@Test
+void testSortByNameDesc() {
+    // Same logic for name DESC
+}
+
+@Test
+void testSortByTypeAsc() {
+    // Same logic for type ASC
+}
+
+@Test
+void testSortByTypeDesc() {
+    // Same logic for type DESC
+}
+
+// ✅ GOOD: Single Parameterized Test
+@ParameterizedTest(name = "Sort by {0} {1}")
+@MethodSource("sortingTestCases")
+@DisplayName("Sort evaluators by various fields with ASC/DESC")
+void sortEvaluators(String field, String direction, Comparator<Entity> comparator) {
+    // Single test method handles all sorting scenarios
+}
+
+static Stream<Arguments> sortingTestCases() {
+    return Stream.of(
+        Arguments.of("name", "ASC", Comparator.comparing(Entity::getName)),
+        Arguments.of("name", "DESC", Comparator.comparing(Entity::getName).reversed()),
+        Arguments.of("type", "ASC", Comparator.comparing(e -> e.getType().name())),
+        Arguments.of("type", "DESC", Comparator.comparing(e -> e.getType().name()).reversed())
+    );
+}
+```
+
+### **Basic Parameterized Tests**
 
 ```java
 // In test class
@@ -291,6 +359,143 @@ void createUserWhenEmailFormatIsValidated(String email, boolean expectedValid) {
 }
 ```
 
+### **Test Coverage Requirements**
+
+**Critical**: When testing sorting/filtering functionality, ensure ALL fields from the corresponding factory class are included in parameterized tests at least once.
+
+```java
+// Reference: AutomationRuleEvaluatorSortingFactory has fields: 
+// id, name, type, enabled, sampling_rate, project_id, project_name, 
+// created_at, last_updated_at, created_by, last_updated_by
+
+// ✅ GOOD: All factory fields covered in test parameters
+static Stream<Arguments> sortingTestCases() {
+    return Stream.of(
+        Arguments.of("id", "ASC", Comparator.comparing(Entity::getId)),
+        Arguments.of("name", "ASC", Comparator.comparing(Entity::getName)),
+        Arguments.of("type", "ASC", Comparator.comparing(e -> e.getType().name())),
+        Arguments.of("enabled", "ASC", Comparator.comparing(Entity::isEnabled)),
+        Arguments.of("sampling_rate", "ASC", Comparator.comparing(Entity::getSamplingRate)),
+        Arguments.of("project_id", "ASC", Comparator.comparing(Entity::getProjectId)),
+        Arguments.of("project_name", "ASC", Comparator.comparing(Entity::getProjectName)),
+        Arguments.of("created_at", "ASC", Comparator.comparing(Entity::getCreatedAt)),
+        Arguments.of("last_updated_at", "ASC", Comparator.comparing(Entity::getLastUpdatedAt)),
+        Arguments.of("created_by", "ASC", Comparator.comparing(Entity::getCreatedBy)),
+        Arguments.of("last_updated_by", "ASC", Comparator.comparing(Entity::getLastUpdatedBy))
+        // Include DESC variants as needed
+    );
+}
+```
+
+### **Test Method Parameters**
+
+**Pattern**: For sorting tests, use `Comparator<T>` as the parameter type instead of `Function<T, Comparable<?>>`.
+
+```java
+// ❌ BAD: Using Function with wildcards (harder to work with)
+void sortEvaluators(String field, String direction,
+        java.util.function.Function<AutomationRuleEvaluator<?>, Comparable> extractor)
+
+// ✅ GOOD: Using Comparator (cleaner and more flexible)
+void sortEvaluators(String field, String direction,
+        Comparator<AutomationRuleEvaluator<?>> comparator)
+```
+
+### **Proper Imports for Parameterized Tests**
+
+**Always use imports** instead of fully qualified class names in test signatures:
+
+```java
+// ❌ BAD: Fully qualified class names
+static Stream<org.junit.jupiter.params.provider.Arguments> sortingTestCases() {
+    return Stream.of(
+        org.junit.jupiter.params.provider.Arguments.of(...)
+    );
+}
+
+// ✅ GOOD: Proper imports
+import org.junit.jupiter.params.provider.Arguments;
+
+static Stream<Arguments> sortingTestCases() {
+    return Stream.of(
+        Arguments.of(...)
+    );
+}
+```
+
+**Note**: For test data generation in parameterized tests, follow the [PODAM guidelines](#podam-configuration) above. Let the factory generate random values and only override when necessary for the specific test scenario.
+
+### **Pagination Testing**
+
+Use single parameterized test for pagination scenarios:
+
+```java
+// ❌ BAD: Three separate pagination test methods
+@Test
+void paginationPage1() { /* ... */ }
+
+@Test
+void paginationPage2() { /* ... */ }
+
+@Test
+void paginationLastPage() { /* ... */ }
+
+// ✅ GOOD: One parameterized test
+@ParameterizedTest(name = "Fetch page {0} with size {1}")
+@MethodSource("paginationTestCases")
+void testPagination(int pageNumber, int pageSize, int expectedSize, int totalRecords) {
+    // Single test handles all pagination scenarios
+}
+
+static Stream<Arguments> paginationTestCases() {
+    return Stream.of(
+        Arguments.of(1, 10, 10, 25), // First page
+        Arguments.of(2, 10, 10, 25), // Middle page
+        Arguments.of(3, 10, 5, 25)   // Last page with fewer items
+    );
+}
+```
+
+### **Test Organization for Parameterized Tests**
+
+Group related tests in single nested class:
+
+```java
+// ❌ BAD: Multiple nested classes for similar functionality
+@Nested
+class SortingFunctionality { }
+
+@Nested
+class ListFilteringFunctionality { }
+
+@Nested
+class PaginationFunctionality { }
+
+@Nested
+class ProjectIdFilteringFunctionality { }
+
+// ✅ GOOD: Combine related tests into logical groups
+@Nested
+@DisplayName("Search, Filter, and Sort Functionality")
+class SearchFilterSortFunctionality {
+    
+    @ParameterizedTest
+    void testSorting(...) { }
+    
+    @ParameterizedTest
+    void testFiltering(...) { }
+    
+    @ParameterizedTest
+    void testPagination(...) { }
+}
+```
+
+### **Reference Examples**
+
+For well-structured parameterized tests, refer to:
+- [AnnotationQueuesResourceTest.java](mdc:apps/opik-backend/src/test/java/com/comet/opik/api/resources/v1/priv/AnnotationQueuesResourceTest.java)
+- [AlertResourceTest.java](mdc:apps/opik-backend/src/test/java/com/comet/opik/api/resources/v1/priv/AlertResourceTest.java)
+
 ## Mocking and Stubbing
 
 ### **Mocking Dependencies**
PATCH

echo "Gold patch applied."
