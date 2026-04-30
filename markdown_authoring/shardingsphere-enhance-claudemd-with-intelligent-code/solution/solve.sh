#!/usr/bin/env bash
set -euo pipefail

cd /workspace/shardingsphere

# Idempotency guard
if grep -qF "- **Comprehensive Analysis**: Thoroughly analyze problem context, consider multi" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -3,34 +3,27 @@
 Apache ShardingSphere: Distributed SQL engine for sharding, scaling, encryption. Database Plus concept - unified service layer over existing databases.
 
 Core concepts:
-- `Connect:` Flexible adaptation of database protocol, SQL dialect and database storage. It can quickly connect applications and heterogeneous databases.
-- `Enhance:` Capture database access entry to provide additional features transparently, such as: redirect (sharding, readwrite-splitting and shadow), transform (data encrypt and mask), authentication (security, audit and authority), governance (circuit breaker and access limitation and analyze, QoS and observability).
-- `Pluggable:` Leveraging micro kernel and 3 layers pluggable mode, features and database ecosystem can be embedded flexibly. Developers can customize their ShardingSphere just like building with LEGO blocks.
-
-## Rule Hierarchy (Priority Order)
-
-1. **Quick Reference** (First check - Daily usage)
-2. **Core Prohibitions** (Critical - Absolute restrictions)
-3. **AI-Enhanced Standards** (Quality - Excellence requirements)
-4. **Detailed Procedures** (Reference - Implementation details)
+- `Connect:` Flexible adaptation of database protocol, SQL dialect and database storage
+- `Enhance:` Transparent features: sharding, encryption, security, governance
+- `Pluggable:` Micro-kernel + 3-layer pluggable architecture
 
 ## Quick Reference (Top 10 Rules)
 
 1. Follow CODE_OF_CONDUCT.md for coding standards
 2. Generate minimal essential code only
 3. Prioritize readability as highest priority
 4. 100% test coverage for all new code
-5. ONLY edit explicitly mentioned files
-6. Make decisions within task scope ONLY
-7. NEVER perform autonomous "best practice" improvements
-8. Apply formatting to new code ONLY
-9. Provide comprehensive analysis before coding
-10. NEVER auto-commit to Git without explicit instruction
+5. NEVER auto-commit to Git without explicit instruction
+6. ONLY edit explicitly mentioned files
+7. Make decisions within task scope ONLY
+8. NEVER perform autonomous "best practice" improvements
+9. Apply formatting to new code ONLY
+10. Provide comprehensive analysis before coding
 
 ## Core Prohibitions (Unified)
 
 ### Git Operations
-- NEVER auto-commit changes to Git without explicit user command
+- NEVER auto-commit changes without explicit user command
 - Prepare commit messages when requested, but NEVER execute commits
 
 ### Code Changes
@@ -57,15 +50,36 @@ Core concepts:
 - Follow CODE_OF_CONDUCT.md (AIR principle, BCDE design, naming conventions)
 - Focus on behavior testing over implementation details
 
+### Intelligent Code Standards
+
+#### Contextual Intelligence
+- **Pattern Recognition**: Identify and apply existing architectural patterns
+- **Style Adaptation**: Seamlessly match current codebase conventions
+- **Architectural Harmony**: Ensure new code fits existing design philosophy
+- **Self-Documenting Design**: Code should explain its purpose through structure
+
+#### Clean Code Intelligence
+- **Single Responsibility**: Each function/class has one clear purpose
+- **DRY Principle**: Detect and eliminate duplication automatically
+- **Effortless Reading**: Code reads like well-written prose
+- **Optimal Abstraction**: Create right level of abstraction for problem domain
+
+#### Evolutionary Code Design
+- **Open-Closed Principle**: Code open for extension, closed for modification
+- **Fail-Fast Design**: Detect errors early and exit cleanly
+- **Graceful Degradation**: Implement automatic recovery when possible
+- **Future-Proofing**: Anticipate likely future requirements
+
 ### Excellence Requirements
-- **Comprehensive Analysis**: Thoroughly analyze problem context, consider multiple approaches, anticipate issues
-- **One-Shot Excellence**: Provide optimal solutions in single response, avoid incremental fixes
-- **Quality Validation**: Ensure immediate usability, actionable recommendations, alignment with best practices
+- **Comprehensive Analysis**: Thoroughly analyze problem context, consider multiple approaches
+- **One-Shot Excellence**: Provide optimal solutions in single response
+- **Quality Validation**: Ensure immediate usability, actionable recommendations
 
 ## Quality Metrics
 
 ### Success Criteria
 - Code compiles without warnings
+- All tests pass in <5 minutes
 - No functionality regression
 - Spotless formatting passes
 - 100% coverage for new code
@@ -74,13 +88,7 @@ Core concepts:
 - **Simplicity**: <50 lines for simple functions, <200 lines for complex classes
 - **Performance**: <100ms execution time for common operations
 - **Readability**: <80 characters per line, max 3 nested levels
-- **Imports**: Remove unused imports, prefer specific imports
-
-### Testing Standards
-- **Coverage**: 100% line, 95%+ branch coverage
-- **Speed**: <1 second per test case
-- **Redundancy**: Zero duplicate test scenarios
-- **Isolation**: Each test runs independently
+- **Intelligence**: Patterns recognized, architecture harmonized, future-proof
 
 ## Unified Guidelines
 
@@ -108,6 +116,43 @@ Core concepts:
 - Maintain current behavior over ideal implementation
 - Favor minimal changes over comprehensive solutions
 
+## Practical Examples
+
+### Example 1: Intelligent Bug Fix
+Before (potential null pointer):
+public void processConnection(DatabaseConnection conn) {
+    conn.execute(sql);
+}
+
+After (context-aware, self-documenting):
+public void processConnection(DatabaseConnection validConnection) {
+    if (validConnection.isValid()) {
+        validConnection.execute(sql);
+    }
+}
+
+### Example 2: Pattern-Based New Feature
+Following Repository pattern for consistency:
+public class MySQLConnectionValidator implements DatabaseValidator {
+    private static final int TIMEOUT_MS = 5000;
+
+    public ValidationResult validate(ConnectionConfig config) {
+        return timeoutAwareValidation(config);
+    }
+}
+
+### Example 3: Evolutionary Design
+Open-closed principle implementation:
+public abstract class AbstractDatabaseConnector {
+    protected abstract Connection createConnection(Config config);
+
+    public final ValidationResult validate(Config config) {
+        return preValidation(config);
+    // Implementation in child classes
+    return createConnection(config);
+    }
+}
+
 ## Build System
 
 Maven build commands:
@@ -139,20 +184,21 @@ Maven build commands:
 ### Operational Procedures
 1. **Direct Code Generation**: Generate final code & call tools directly
    - Apply formatting tools for new code only
-   - Make independent decisions within task scope
+   - Make intelligent decisions within task scope
    - **CRITICAL**: Automated generation permitted, automatic Git commits forbidden
 
 2. **Implementation Rules**:
    - Isolate edits to smallest possible blocks
-   - Maintain existing style, even if suboptimal
-   - Preserve all comments unless directly contradictory
+   - Maintain existing architectural patterns
+   - Preserve existing style and design philosophy
+   - Apply context-aware design principles
 
 ### Verification Process
-1. **Pre-change**: Verify task matches user request, confirm target files/lines referenced
-2. **Post-change**: Run relevant tests, verify no regression, confirm scope matches request
+1. **Pre-change**: Verify task matches user request, analyze existing patterns
+2. **Post-change**: Run relevant tests, verify no regression, confirm architectural harmony
 3. **Continuous**: Re-read protocol before tasks, verify compliance, report violations
 
 ### Emergency Procedures
 - **Immediate termination** if code deletion exceeds 10 lines without instruction
 - **Stop immediately** if tests fail after changes
-- **Report deviations** as soon as detected
\ No newline at end of file
+- **Report deviations** as soon as detected
PATCH

echo "Gold patch applied."
