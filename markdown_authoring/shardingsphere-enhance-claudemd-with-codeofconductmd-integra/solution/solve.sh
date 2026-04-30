#!/usr/bin/env bash
set -euo pipefail

cd /workspace/shardingsphere

# Idempotency guard
if grep -qF "1. Follow CODE_OF_CONDUCT.md (clean code principles, naming conventions, formatt" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -35,54 +35,20 @@ Maven build commands:
 
 ## Code Standards
 
-1. Follow CODE_OF_CONDUCT.md
-2. Generate minimal essential code only
-3. Prioritize readability & scalability, avoid over-engineering
-
-## Quality Assurance Standards
-
-### Code Quality Requirements
-
-1. **Minimal Essential Code**: Write only the code needed to fulfill requirements
-   - Eliminate redundant variables, methods, and logic
-   - Remove dead code and unused imports
-   - Prefer concise expressions over verbose implementations
-
-2. **Readability First**: Code must be self-documenting and immediately understandable
-   - Use clear, descriptive variable and method names
-   - Write code that reads like natural language
-   - Add comments only when business logic is complex or non-obvious
-   - Structure code to minimize cognitive load
-
-3. **Performance Considerations**: Consider execution efficiency in all implementations
-   - Optimize algorithms for optimal time/space complexity
-   - Consider execution frequency and critical path optimization
-   - Minimize resource consumption (memory, CPU, I/O)
-   - Avoid unnecessary object creation and method calls in hot paths
-   - Use appropriate data structures for the use case
-   - Consider lazy evaluation where beneficial
-
-### Testing Standards
-
-1. **Coverage Requirements**:
-   - 100% line coverage for all new code
-   - 100% branch coverage where logically possible
-   - Test all edge cases and error conditions
-   - Validate both positive and negative scenarios
-
-2. **Test Case Principles**:
-   - Each test must validate unique behavior - no redundant tests
-   - Use clear, descriptive test names that indicate what is being tested
-   - Follow Arrange-Act-Assert pattern consistently
-   - Mock external dependencies appropriately
-   - Keep tests fast, independent, and deterministic
-
-3. **Test Quality**:
-   - Tests should fail for the right reasons and be easy to debug
-   - Maintain test readability and maintainability
-   - Use parameterized tests for multiple similar scenarios
-   - Focus on behavior testing rather than implementation details
-   - Ensure tests provide meaningful failure messages
+1. Follow CODE_OF_CONDUCT.md (clean code principles, naming conventions, formatting)
+2. **AI-Specific Requirements**:
+   - Generate minimal essential code only
+   - Prioritize readability as highest priority
+   - Consider extreme performance optimization
+3. Prioritize scalability, avoid over-engineering
+
+## Testing Standards
+
+1. Follow CODE_OF_CONDUCT.md (AIR principle, BCDE design, naming conventions)
+2. **AI-Specific Requirements**:
+   - 100% line and branch coverage for all new code
+   - No redundant test cases - each test validates unique behavior
+   - Focus on behavior testing over implementation details
 
 ## Absolute Prohibitions (Zero-Tolerance)
 
PATCH

echo "Gold patch applied."
