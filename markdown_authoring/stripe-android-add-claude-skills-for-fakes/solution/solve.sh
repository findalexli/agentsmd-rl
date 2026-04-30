#!/usr/bin/env bash
set -euo pipefail

cd /workspace/stripe-android

# Idempotency guard
if grep -qF "This skill describes how to create fake implementations for testing in the Strip" ".claude/skills/create-fake/SKILL.md" && grep -qF "This skill describes how to structure tests in the Stripe Android SDK using fake" ".claude/skills/write-tests/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/create-fake/SKILL.md b/.claude/skills/create-fake/SKILL.md
@@ -0,0 +1,189 @@
+---
+name: create-fake
+description: Explains how to create a fake following stripe-android's coding standards
+---
+
+# Creating Fakes for Testing
+
+This skill describes how to create fake implementations for testing in the Stripe Android SDK. The codebase **strongly prefers fakes over mocks** for better test reliability and clarity.
+
+## Core Principles
+
+1. **Prefer fakes over mocks** - Create `FakeClassName` implementations that provide controllable, inspectable behavior
+2. **Use Turbine for call tracking** - Track method invocations with Turbine channels for verification
+3. **Provide default parameters** - Make fakes easy to instantiate with sensible defaults
+4. **Enable validation** - Implement `ensureAllEventsConsumed()` validation method when using Turbines
+
+## Basic Fake Structure
+
+### File Naming and Location
+- Place fakes in the test source directory: `src/test/java/com/stripe/android/.../FakeClassName.kt`
+- Name pattern: `Fake` + interface/class name (e.g., `FakeEventReporter`, `FakeCustomerRepository`)
+- Mark as `internal` to scope to the test module
+
+### Constructor Pattern
+Always use **default parameters** to make instantiation easy:
+
+```kotlin
+internal class FakeCustomerRepository(
+    private val paymentMethods: List<PaymentMethod> = emptyList(),
+    private val customer: Customer? = null
+) : CustomerRepository {
+    // Implementation
+}
+```
+
+For complex setup, provide a **companion object factory method**:
+
+```kotlin
+internal class FakePaymentMethodVerticalLayoutInteractor(
+    initialState: PaymentMethodVerticalLayoutInteractor.State,
+    initialShowsWalletsHeader: Boolean = false,
+    private val viewActionRecorder: ViewActionRecorder<PaymentMethodVerticalLayoutInteractor.ViewAction>
+) : PaymentMethodVerticalLayoutInteractor {
+
+    companion object {
+        fun create(
+            paymentMethodMetadata: PaymentMethodMetadata = PaymentMethodMetadataFactory.create(),
+            initialShowsWalletsHeader: Boolean = true,
+            viewActionRecorder: ViewActionRecorder<PaymentMethodVerticalLayoutInteractor.ViewAction> = ViewActionRecorder()
+        ): FakePaymentMethodVerticalLayoutInteractor {
+            // Complex initialization logic
+            val initialState = /* construct complex state */
+            return FakePaymentMethodVerticalLayoutInteractor(
+                initialState = initialState,
+                initialShowsWalletsHeader = initialShowsWalletsHeader,
+                viewActionRecorder = viewActionRecorder
+            )
+        }
+    }
+}
+```
+
+## Tracking Method Calls with Turbine
+
+### Basic Turbine Pattern
+
+Directly expose Turbines for test verification:
+
+```kotlin
+internal class FakeEventReporter : EventReporter {
+    val paymentFailureCalls = Turbine<PaymentFailureCall>()
+    val paymentSuccessCalls = Turbine<PaymentSuccessCall>()
+
+    override fun onPaymentFailure(error: Throwable, source: PaymentEventSource) {
+        paymentFailureCalls.add(PaymentFailureCall(error, source))
+    }
+
+    override fun onPaymentSuccess(paymentMethod: PaymentMethod) {
+        paymentSuccessCalls.add(PaymentSuccessCall(paymentMethod))
+    }
+}
+```
+
+### Data Classes for Call Capture
+
+Define **data classes** to capture method call parameters:
+
+```kotlin
+data class PaymentFailureCall(val error: Throwable, val source: PaymentEventSource)
+data class PaymentSuccessCall(val paymentMethod: PaymentMethod)
+data class DetachRequest(val paymentMethodId: String, val customerId: String)
+```
+
+### Validation with ensureAllEventsConsumed
+
+Implement a **validation method** that ensures all turbine events were consumed:
+
+```kotlin
+fun ensureAllEventsConsumed() {
+    paymentFailureCalls.ensureAllEventsConsumed()
+    paymentSuccessCalls.ensureAllEventsConsumed()
+    detachRequests.ensureAllEventsConsumed()
+    updateRequests.ensureAllEventsConsumed()
+    // ... validate all turbines
+}
+```
+
+Tests should call this method after verification:
+
+```kotlin
+@Test
+fun `test payment flow`() = runTest {
+    val fake = FakeEventReporter()
+
+    // Perform operations
+    fake.onPaymentSuccess(paymentMethod)
+
+    // Verify calls
+    assertThat(fake.paymentSuccessCalls.awaitItem()).isEqualTo(
+        PaymentSuccessCall(paymentMethod)
+    )
+
+    // Validate all events consumed
+    fake.ensureAllEventsConsumed()
+}
+```
+
+## ViewActionRecorder Pattern
+
+For classes that handle view actions, use **ViewActionRecorder**:
+
+```kotlin
+internal class FakePaymentMethodVerticalLayoutInteractor(
+    initialState: PaymentMethodVerticalLayoutInteractor.State,
+    private val viewActionRecorder: ViewActionRecorder<PaymentMethodVerticalLayoutInteractor.ViewAction>
+) : PaymentMethodVerticalLayoutInteractor {
+
+    override fun handleViewAction(viewAction: PaymentMethodVerticalLayoutInteractor.ViewAction) {
+        viewActionRecorder.record(viewAction)
+        // Optional: implement state changes based on action
+    }
+}
+```
+
+**Include ViewActionRecorder in factory with default**:
+
+```kotlin
+companion object {
+    fun create(
+        paymentMethodMetadata: PaymentMethodMetadata = PaymentMethodMetadataFactory.create(),
+        viewActionRecorder: ViewActionRecorder<PaymentMethodVerticalLayoutInteractor.ViewAction> = ViewActionRecorder()
+    ): FakePaymentMethodVerticalLayoutInteractor {
+        return FakePaymentMethodVerticalLayoutInteractor(
+            initialState = /* ... */,
+            viewActionRecorder = viewActionRecorder
+        )
+    }
+}
+```
+
+## Excellent Real-World Examples
+
+Reference these fakes from the codebase as gold standards:
+
+### **FakeEventReporter**
+`paymentsheet/src/test/java/com/stripe/android/paymentsheet/analytics/FakeEventReporter.kt`
+- 16 different Turbine channels for comprehensive event tracking
+- Clean `validate()` method checking all turbines
+- Data classes for each event type
+- Gold standard for Turbine usage
+
+### **FakeCustomerRepository**
+`paymentsheet/src/test/java/com/stripe/android/utils/FakeCustomerRepository.kt`
+- Excellent use of default parameters
+- Multiple Turbines for tracking different operations (detach, update, setDefault)
+- Data classes for request tracking
+
+### **FakePaymentMethodVerticalLayoutInteractor**
+`paymentsheet/src/test/java/com/stripe/android/paymentsheet/verticalmode/FakePaymentMethodVerticalLayoutInteractor.kt`
+- ViewActionRecorder integration
+- Companion object factory method with sophisticated defaults
+
+## Quick Reference
+
+- **Need to track method calls?** → Use Turbine with data classes
+- **Tracking view actions?** → Use ViewActionRecorder
+- **Need to verify all events consumed?** → Implement `ensureAllEventsConsumed()` that calls it on all Turbines
+- **Complex initialization?** → Add companion object `create()` factory method
+- **Always** → Provide default parameters for easy instantiation
diff --git a/.claude/skills/write-tests/SKILL.md b/.claude/skills/write-tests/SKILL.md
@@ -0,0 +1,113 @@
+---
+name: write-test
+description: Explains how to write tests and structure test classes following stripe-android's coding standards
+---
+# Setting Up Tests
+
+This skill describes how to structure tests in the Stripe Android SDK using fakes, scenarios, and proper verification patterns.
+
+## Core Principles
+
+1. **Use fakes over mocks** - Leverage fake implementations for dependencies (see `create-fake.md`)
+2. **Create test scenarios** - Use Scenario classes with `runScenario` functions to organize test setup
+3. **Verify all events consumed** - Call `validate()` or `ensureAllEventsConsumed()` on fakes after test block
+4. **Use Turbine for Flow testing** - Test Flow emissions with Turbine's `.test { }` syntax
+
+## Basic Test Structure
+
+Every test should follow this pattern:
+
+```kotlin
+@Test
+fun `test description`() = runScenario(
+    // Test-specific parameters
+    config = testConfig
+) {
+    // 1. Configure: Set up fake behaviors (optional)
+    fakeService.result = expectedResult
+
+    // 2. Execute: Call the code under test
+    val result = systemUnderTest.doSomething()
+
+    // 3. Verify: Assert results and check fake calls
+    assertThat(result).isEqualTo(expected)
+    assertThat(fakeService.calls.awaitItem()).isEqualTo(expectedCall)
+}
+// 4. Validation: ensureAllEventsConsumed called automatically by runScenario
+```
+
+## Scenario Pattern with runScenario
+
+### Basic Structure
+
+Create a `runScenario` function and a `Scenario` class at the bottom of your test file:
+
+```kotlin
+class MyFeatureTest {
+    @Test
+    fun `test case`() = runScenario {
+        // Test code using scenario fields
+        assertThat(systemUnderTest.getValue()).isEqualTo(expectedValue)
+    }
+
+    private fun runScenario(
+        config: Config = defaultConfig,
+        block: suspend Scenario.() -> Unit,
+    ) = runTest {
+        // Setup fakes
+        val fakeRepository = FakeRepository()
+        val fakeAnalytics = FakeAnalytics()
+
+        // Create system under test
+        val systemUnderTest = MyFeature(
+            repository = fakeRepository,
+            analytics = fakeAnalytics,
+            config = config
+        )
+
+        // Run test block with scenario context
+        block(
+            Scenario(
+                systemUnderTest = systemUnderTest,
+                fakeRepository = fakeRepository,
+                fakeAnalytics = fakeAnalytics,
+            )
+        )
+
+        // Validate all fakes
+        fakeRepository.ensureAllEventsConsumed()
+        fakeAnalytics.ensureAllEventsConsumed()
+    }
+
+    private class Scenario(
+        val systemUnderTest: MyFeature,
+        val fakeRepository: FakeRepository,
+        val fakeAnalytics: FakeAnalytics,
+    )
+}
+```
+
+**Key Features:**
+- `runScenario` replaces `runTest` as the test entry point
+- Default parameters for all configuration make tests concise
+- Trailing lambda provides DSL-like syntax with scenario fields
+- `ensureAllEventsConsumed()` called automatically after test block
+- Scenario class holds system under test and all fakes
+
+### Using runScenario in Tests
+
+```kotlin
+@Test
+fun `fetching data returns success when repository succeeds`() = runScenario {
+    // Configure fake behavior
+    fakeRepository.dataResult = Result.success(testData)
+
+    // Execute
+    val result = systemUnderTest.fetchData()
+
+    // Verify
+    assertThat(result.isSuccess).isTrue()
+    assertThat(fakeRepository.fetchCalls.awaitItem()).isEqualTo(FetchCall(userId = "123"))
+}
+// ensureAllEventsConsumed called automatically
+```
PATCH

echo "Gold patch applied."
