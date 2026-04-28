#!/usr/bin/env bash
set -euo pipefail

cd /workspace/js-recall

# Idempotency guard
if grep -qF "- **Method Complexity:** If a service method has 3+ distinct steps (especially i" ".cursor/rules/api-specific-config.mdc" && grep -qF "- **Extract Helper Methods:** When a function exceeds ~30-40 lines or has distin" ".cursor/rules/org-general-practices.mdc" && grep -qF "- Avoid `.filter().length === 0` or `.filter().length > 0` when `.some()` or `.e" ".cursor/rules/org-typescript-standards.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/api-specific-config.mdc b/.cursor/rules/api-specific-config.mdc
@@ -78,6 +78,19 @@ alwaysApply: false
 - Keep manager methods focused on single responsibilities
 - Always handle errors gracefully and return consistent result objects
 
+### Service Method Design Patterns
+- **Method Complexity:** If a service method has 3+ distinct steps (especially if labeled as "Step 1", "Step 2", etc.), consider extracting each step into a private helper method
+- **Retry Logic Separation:** Extract retry logic with exponential backoff into dedicated helper methods rather than inline in business logic
+- **Batch Operation Helpers:** Create reusable helpers for batch operations (batch fetching, batch processing) that can be shared across methods
+- **Clear Method Contracts:** Helper methods should clearly indicate what they assume about their inputs:
+  - Use descriptive names like `processWithValidatedData` vs just `processData`
+  - Document preconditions in method comments
+  - Consider using TypeScript branded types or type predicates for validated data
+- **Fail-Fast in Service Methods:** 
+  - Validate inputs and check preconditions at the start of public methods
+  - Return early on invalid conditions rather than nesting the entire method body
+  - Let helper methods assume valid inputs (since the public method already validated)
+
 ### Code Reuse & Method Implementation
 - **Before implementing any new method**: Always search the codebase for similar existing functionality using semantic search or grep
 - **If a similar method exists but is not adequate**: You must explicitly explain why the existing method cannot be used or extended, including:
diff --git a/.cursor/rules/org-general-practices.mdc b/.cursor/rules/org-general-practices.mdc
@@ -16,6 +16,19 @@ alwaysApply: true
 - **Function Size:** Avoid overly long functions.  Break up large functions using helper functions that encapsulate related functionality into smaller and more focused pieces.
 – **Script Usage:** Avoid writing one-off scripts if a more integrated solution is feasible.
 
+## Function Design & Complexity Management
+- **Extract Helper Methods:** When a function exceeds ~30-40 lines or has distinct logical sections (e.g., validation, processing, output), extract helper methods. If you have numbered steps in comments (Step 1, Step 2, etc.), consider if each step should be its own function.
+- **Single Responsibility:** Each function should do ONE thing well. A function should either answer one question OR perform one action, not both.
+- **Fail-Fast Pattern:** Check error conditions early and return/throw immediately. Don't carry invalid state through the entire function. This makes the happy path clearer and reduces nesting.
+- **Avoid Redundant Checking:** Don't check the same condition multiple times across different functions. Check once at the boundary, then pass validated data to inner functions.
+- **Clear Method Contracts:** Helper methods should clearly indicate via their name and signature what they assume (e.g., `calculateValueWithValidPrices` assumes prices are already validated).
+
+## Efficient Code Patterns
+- **Don't Compute What You Don't Need:** Avoid building intermediate data structures (arrays, objects) just to check a property. For example, don't build an array just to check if it's empty - use a boolean check directly.
+- **Choose Appropriate Loops:** Use `for` loops when iteration count is known upfront, `while` for conditional iteration. Modern `for` loops are often cleaner than `while` with manual increment.
+- **Early Exit Strategies:** Prefer methods that can exit early (`.some()`, `.every()`, `.find()`) over methods that process everything (`.filter().length`, `.map()`) when you just need a boolean or single result.
+- **Separation of Concerns:** Separate "what failed" (detailed logging) from "should we continue" (control flow) logic. Log details where the failure is detected, make decisions based on simple booleans.
+
 ## Data Handling
 – **Mocking:** Mock data *only* for automated tests. Never use mocked or stubbed data in development or production environments.
 – **Secrets:** Ensure secrets, API keys, or passwords are *never* committed to the repository. Use environment variables or secure secret management solutions.
diff --git a/.cursor/rules/org-typescript-standards.mdc b/.cursor/rules/org-typescript-standards.mdc
@@ -52,6 +52,39 @@ alwaysApply: true
 - **Caching:** Implement appropriate caching strategies (client-side and server-side).
 - **Asset Optimization:** Optimize images, fonts, and other static assets.
 
+## Code Efficiency Patterns
+- **Array Method Selection:**
+  - Use `.some()` to check if ANY element matches (stops on first match)
+  - Use `.every()` to check if ALL elements match (stops on first non-match)  
+  - Use `.find()` to get the first matching element (stops on first match)
+  - Avoid `.filter().length === 0` or `.filter().length > 0` when `.some()` or `.every()` would suffice
+  - Don't build arrays just to check emptiness or count - use boolean checks where possible
+
+- **Type Narrowing with Early Returns:**
+  - Use early returns to narrow types and reduce nesting
+  - After null/undefined checks with early returns, TypeScript knows the value is defined
+  - Prefer guard clauses at the start of functions over deeply nested if-else blocks
+  - Example:
+    ```typescript
+    // Good: Fail fast with type narrowing
+    if (!data) {
+      logger.error('No data provided');
+      return;
+    }
+    // TypeScript now knows data is defined for rest of function
+    
+    // Avoid: Carrying uncertainty through the function
+    if (data) {
+      // entire function body nested here
+    }
+    ```
+
+- **Helper Function Extraction:**
+  - Extract complex type transformations into well-typed helper functions
+  - Use generics in helpers to maintain type safety across different use cases
+  - Return discriminated unions or Result types from helpers to make error handling explicit
+  - Keep helper functions pure when possible (no side effects, deterministic output)
+
 ## Documentation Standards
 - **API Changes:** Document changes to public APIs clearly (e.g., in changelogs or PR descriptions).
 - **Usage Examples:** Update usage examples when APIs change or new features are added.
PATCH

echo "Gold patch applied."
