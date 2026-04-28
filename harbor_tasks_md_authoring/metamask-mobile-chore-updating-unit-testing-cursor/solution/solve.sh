#!/usr/bin/env bash
set -euo pipefail

cd /workspace/metamask-mobile

# Idempotency guard
if grep -qF "**ALL `@metamask/design-system-react-native` and `app/component-library` compone" ".cursor/rules/unit-testing-guidelines.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/unit-testing-guidelines.mdc b/.cursor/rules/unit-testing-guidelines.mdc
@@ -49,6 +49,7 @@ it('returns false for email without domain', () => {
 ```
 
 **Helper Functions**:
+
 ```ts
 const createTestEvent = (overrides = {}) => ({
   type: EventType.TrackEvent,
@@ -58,8 +59,175 @@ const createTestEvent = (overrides = {}) => ({
 });
 ```
 
+## Element Selection - PREFER DATA TEST IDs
+
+- **ALWAYS prefer `testID` props** for selecting elements in tests
+- **Use `getByTestId`** as the primary query method for reliable element selection
+- **Add `testID` props** to components when writing new code or updating existing code
+- **Avoid selecting by text** when the text might change (i18n, copy updates)
+
+```tsx
+// ✅ CORRECT - Use testID for reliable selection
+<Button testID="submit-button" onPress={handleSubmit}>
+  {t('common.submit')}
+</Button>;
+
+// In test:
+const submitButton = screen.getByTestId('submit-button');
+expect(submitButton).toBeOnTheScreen();
+
+// ✅ ALSO GOOD - Locale keys (safe from content updates)
+const button = screen.getByText(strings('common.submit'));
+
+// ❌ AVOID - Selecting by hardcoded text content
+const button = screen.getByText('Submit'); // Breaks when text changes
+const input = screen.getByPlaceholderText('Enter email'); // Fragile
+```
+
+### CHILD PROP OBJECTS - ALL COMPONENTS SUPPORT THIS
+
+**ALL `@metamask/design-system-react-native` and `app/component-library` components support child prop objects for passing testIDs to internal elements.** This is a universal design pattern - prefer not to mock these components just to inject testIDs.
+
+Common child prop object patterns:
+
+- `closeButtonProps` - for close/dismiss buttons
+- `backButtonProps` - for back navigation buttons
+- `startAccessoryProps` / `endAccessoryProps` - for accessory elements
+- `iconProps` - for icon elements
+- `labelProps` - for label text elements
+- `inputProps` - for input elements within compound components
+- `*Props` - any prop ending in `Props` is likely a child prop object
+
+```tsx
+// ❌ WRONG - Mocking to add testID (141 lines of unnecessary code!)
+// The testID capability ALREADY EXISTS via child prop objects!
+jest.mock('BottomSheetHeader', () => {
+  return ({ onClose }) => (
+    <TouchableOpacity testID="close-button" onPress={onClose}>Close</TouchableOpacity>
+  );
+});
+
+// ✅ CORRECT - Use the component's child prop object API
+<HeaderCenter
+  title="Select a region"
+  onClose={handleClose}
+  closeButtonProps={{ testID: 'region-selector-close-button' }}
+/>
+
+// ✅ CORRECT - BottomSheetHeader supports child prop objects
+<BottomSheetHeader
+  onClose={handleClose}
+  closeButtonProps={{ testID: 'modal-close-button' }}
+  onBack={handleBack}
+  backButtonProps={{ testID: 'modal-back-button' }}
+>
+  {title}
+</BottomSheetHeader>
+
+// In test - no mocking needed!
+const closeButton = screen.getByTestId('region-selector-close-button');
+fireEvent.press(closeButton);
+```
+
+### This Is Universal - No Exceptions
+
+| Library                                | testID Support                                                 |
+| -------------------------------------- | -------------------------------------------------------------- |
+| `@metamask/design-system-react-native` | ✅ All components support `testID` prop AND child prop objects |
+| `app/component-library/*`              | ✅ All components support `testID` prop AND child prop objects |
+
+**If you need to add a testID to one of these components, check for child prop objects first.** Most components support this functionality. If not available, suggest adjusting the component to support it in another change set.
+
+### How to Find Child Prop Objects
+
+1. **Check TypeScript types** - Look at the component's props interface for props ending in `Props`
+2. **Check component source** - Search for `Props` suffix patterns
+3. **Check Storybook** - Component stories demonstrate these props
+
+```tsx
+// Example: BottomSheetHeader TypeScript interface shows:
+// - closeButtonProps?: ButtonIconProps
+// - backButtonProps?: ButtonIconProps
+
+// Example: Design system Button with icon
+<Button
+  testID="submit-button"
+  iconProps={{ testID: 'submit-icon' }}
+  labelProps={{ testID: 'submit-label' }}
+>
+  Submit
+</Button>
+```
+
+### TestID Naming Conventions
+
+```tsx
+// Use kebab-case for testIDs
+testID="settings-screen"
+testID="submit-button"
+testID="error-message"
+testID="token-list-item"
+
+// Include context for list items
+testID={`token-item-${token.symbol}`}
+testID={`network-option-${network.chainId}`}
+```
+
+## Assertions - PREFER toBeOnTheScreen
+
+- **ALWAYS use `toBeOnTheScreen()`** to assert element presence - NOT `toBeTruthy()` or `toBeDefined()`
+- **Use specific matchers** that communicate intent clearly
+- **Avoid weak matchers** that don't actually verify the expected behavior
+
+```tsx
+// ✅ CORRECT - Clear, specific assertions
+expect(screen.getByTestId('submit-button')).toBeOnTheScreen();
+expect(screen.queryByTestId('error-message')).not.toBeOnTheScreen();
+expect(screen.getByTestId('balance-text')).toHaveTextContent('100 ETH');
+
+// ❌ WRONG - Weak matchers that don't verify presence properly
+expect(screen.getByTestId('submit-button')).toBeTruthy(); // Misleading
+expect(screen.getByTestId('submit-button')).toBeDefined(); // Doesn't verify render
+expect(element).not.toBeNull(); // Use toBeOnTheScreen() instead
+```
+
+### Recommended Matchers
+
+| Instead of                           | Use                                                       |
+| ------------------------------------ | --------------------------------------------------------- |
+| `toBeTruthy()` for elements          | `toBeOnTheScreen()`                                       |
+| `toBeDefined()` for elements         | `toBeOnTheScreen()`                                       |
+| `not.toBeNull()`                     | `not.toBeOnTheScreen()` or `queryByTestId` returning null |
+| `toHaveLength(1)` for single element | `toBeOnTheScreen()`                                       |
+
 ## Mocking Rules - CRITICAL
 
+### Exception: UI Components and TestIDs
+
+**Prefer not to mock `@metamask/design-system-react-native` or `app/component-library` components just to inject testIDs.** All these components support testIDs via:
+
+- Direct `testID` prop on the component
+- Child prop objects (`closeButtonProps`, `iconProps`, etc.) for internal elements
+
+```tsx
+// ❌ WRONG: Mocking to inject testID
+jest.mock('BottomSheetHeader', () => ({ onClose }) => (
+  <TouchableOpacity testID="close-button" onPress={onClose}>
+    Close
+  </TouchableOpacity>
+));
+
+// ✅ RIGHT: Use child prop objects
+<BottomSheetHeader
+  onClose={handleClose}
+  closeButtonProps={{ testID: 'modal-close-button' }}
+/>;
+```
+
+See [PR #25548](https://github.com/MetaMask/metamask-mobile/pull/25548) for refactoring example.
+
+### General Mocking Rules
+
 - **EVERYTHING not under test MUST be mocked** - no exceptions
 - **NO** use of `require` - use ES6 imports only
 - **NO** use of `any` type - use proper TypeScript types
@@ -80,7 +248,7 @@ interface MockEvent {
 
 // ❌ WRONG
 const mockApi = require('../services/api'); // ❌ no require
-const mockApi: any = jest.fn();             // ❌ no any type
+const mockApi: any = jest.fn(); // ❌ no any type
 ```
 
 ## Test Isolation and Focus - MANDATORY
@@ -122,6 +290,7 @@ describe('MetaMetricsCustomTimestampPlugin', () => {
 ## Test Coverage (MANDATORY)
 
 **EVERY component MUST test:**
+
 - ✅ **Happy path** - normal expected behavior
 - ✅ **Edge cases** - null, undefined, empty values, boundary conditions
 - ✅ **Error conditions** - invalid inputs, failure scenarios
@@ -192,13 +361,15 @@ jest.setSystemTime(new Date('2024-01-01'));
 ### When to Use act()
 
 Use `act()` when you:
+
 - Call async functions via component props (e.g., `onRefresh`, `onPress` with async handlers)
 - Invoke functions that perform state updates asynchronously
 - Test pull-to-refresh or other async interactions
 
 ### Symptoms of Missing act()
 
 Tests fail intermittently with:
+
 - `TypeError: terminated`
 - `SocketError: other side closed`
 - Warnings about state updates not being wrapped in act()
@@ -261,23 +432,27 @@ await act(async () => {
 ### Why This Matters
 
 Without `act()`:
+
 1. Async function starts executing
 2. Test continues and waits only for specific assertion
 3. Jest cleanup/termination happens while promises are still pending
 4. Results in "terminated" or "other side closed" errors
 
 With `act()`:
+
 1. React Testing Library waits for all state updates
 2. All promises resolve before test proceeds
 3. Clean, deterministic test execution
 
 # Reviewer Responsibilities
 
 - Validate that tests fail when the code is broken (test the test).
+
 ```ts
 // Break the SuT and make sure this test fails
 expect(result).toBe(false);
 ```
+
 - Ensure tests use proper matchers (`toBeOnTheScreen` vs `toBeDefined`).
 - Do not approve PRs without reviewing snapshot diffs, it can reveal errors.
 - Reject tests with complex names combining multiple logical conditions (AND/OR).
@@ -291,36 +466,37 @@ expect(result).toBe(false);
 # Quality Checklist - MANDATORY
 
 Before submitting any test file, verify:
+
+- [ ] **No mocking to inject testIDs** - Use component's built-in testID support
+- [ ] **testIDs via child prop objects** - Use `closeButtonProps={{ testID }}` not mocks
 - [ ] **No "should" in any test name**
 - [ ] **All tests follow AAA pattern**
 - [ ] **Each test has one clear purpose**
 - [ ] **All code paths are tested**
 - [ ] **Edge cases are covered**
 - [ ] **Test data is realistic**
 - [ ] **Tests are independent**
+- [ ] **Assertions use `toBeOnTheScreen()`** - NOT `toBeTruthy()` or `toBeDefined()`
 - [ ] **Assertions are specific**
+- [ ] **Elements selected by `testID`** - NOT fragile text queries
 - [ ] **Test names are descriptive**
 - [ ] **No test duplication**
 - [ ] **Async operations wrapped in act()** when they trigger state updates
 
 # Common Mistakes to AVOID - CRITICAL
 
-- ❌ **Using "should" in test names** - This is the #1 mistake
+- ❌ **Mocking to inject testIDs** - Components already support testID (see guidelines above)
+- ❌ **Using "should" in test names** - This is the #1 mistake, use action-oriented descriptions
 - ❌ **Testing multiple behaviors in one test** - One test, one behavior
 - ❌ **Sharing state between tests** - Each test must be independent
 - ❌ **Not testing error conditions** - Test both success and failure paths
 - ❌ **Using unrealistic test data** - Use data that reflects real usage
 - ❌ **Not following AAA pattern** - Always Arrange, Act, Assert
 - ❌ **Not testing edge cases** - Test null, undefined, empty values
-- ❌ **Using weak matchers** - Use specific assertions like `toBe()`, `toEqual()`
+- ❌ **Using weak matchers** - Use `toBeOnTheScreen()` instead of `toBeTruthy()`/`toBeDefined()`
+- ❌ **Selecting elements by text** - Use `testID` props for reliable selection
 - ❌ **Not wrapping async state updates in act()** - Causes flaky "terminated" errors
 
-# Anti-patterns to Avoid
-
-- ❌ Do not consider snapshot coverage as functional coverage.
-- ❌ Do not rely on code coverage percentage without real assertions.
-- ❌ Do not use weak matchers like `toBeDefined` or `toBeTruthy` to assert element presence. Use `toBeOnTheScreen()`.
-
 # Unit tests developement workflow
 
 - Always run unit tests after making code changes.
@@ -329,6 +505,7 @@ Before submitting any test file, verify:
 ## Testing Commands
 
 ### Single File Testing
+
 ```shell
 # Use this command for testing a specific file
 yarn jest <filename>
@@ -342,20 +519,22 @@ yarn jest utils/helpers.test.ts
 ```
 
 ### Coverage Reports
+
 ```shell
 # Use this command for coverage reports
 yarn test:unit:coverage
 ```
 
-
 ## Workflow Requirements
+
 - Confirm all tests are passing before commit.
 - When a snapshot update is detected, confirm the changes are expected.
 - Do not blindly update snapshots without understanding the differences.
 
 # Reference Code Examples
 
 **Proper AAA**:
+
 ```ts
 it('indicates expired milk when past due date', () => {
   const today = new Date('2025-06-01');
@@ -368,6 +547,7 @@ it('indicates expired milk when past due date', () => {
 ```
 
 ## ❌ Brittle Snapshot
+
 ```ts
 it('renders the button', () => {
   const { container } = render(<MyButton />);
@@ -376,6 +556,7 @@ it('renders the button', () => {
 ```
 
 ## ✅ Robust UI Assertion
+
 ```ts
 it('displays error message when API fails', async () => {
   mockApi.failOnce();
@@ -386,12 +567,13 @@ it('displays error message when API fails', async () => {
 ```
 
 **Test the Test**:
+
 ```ts
 it('hides selector when disabled', () => {
   const { queryByTestId } = render(<Selector enabled={false} />);
 
   expect(queryByTestId('IPFS_GATEWAY_SELECTED')).toBeNull();
-  
+
   // Break test: change enabled={false} to enabled={true} and verify test fails
 });
 ```
@@ -402,10 +584,10 @@ Validate tests fail when code breaks • Ensure proper matchers • Review snaps
 
 ```ts
 // OK
-it('renders button when enabled')
+it('renders button when enabled');
 
 // NOT OK
-it('renders and disables button when input is empty or missing required field')
+it('renders and disables button when input is empty or missing required field');
 ```
 
 ## Workflow
PATCH

echo "Gold patch applied."
