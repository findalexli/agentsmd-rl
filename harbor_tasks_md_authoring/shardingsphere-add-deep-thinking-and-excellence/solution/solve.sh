#!/usr/bin/env bash
set -euo pipefail

cd /workspace/shardingsphere

# Idempotency guard
if grep -qF "- `Pluggable:` Leveraging micro kernel and 3 layers pluggable mode, features and" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -5,7 +5,108 @@ Apache ShardingSphere: Distributed SQL engine for sharding, scaling, encryption.
 Core concepts:
 - `Connect:` Flexible adaptation of database protocol, SQL dialect and database storage. It can quickly connect applications and heterogeneous databases.
 - `Enhance:` Capture database access entry to provide additional features transparently, such as: redirect (sharding, readwrite-splitting and shadow), transform (data encrypt and mask), authentication (security, audit and authority), governance (circuit breaker and access limitation and analyze, QoS and observability).
-- `Pluggable:` Leveraging the micro kernel and 3 layers pluggable mode, features and database ecosystem can be embedded flexibly. Developers can customize their ShardingSphere just like building with LEGO blocks.
+- `Pluggable:` Leveraging micro kernel and 3 layers pluggable mode, features and database ecosystem can be embedded flexibly. Developers can customize their ShardingSphere just like building with LEGO blocks.
+
+## Rule Hierarchy (Priority Order)
+
+1. **Quick Reference** (First check - Daily usage)
+2. **Core Prohibitions** (Critical - Absolute restrictions)
+3. **AI-Enhanced Standards** (Quality - Excellence requirements)
+4. **Detailed Procedures** (Reference - Implementation details)
+
+## Quick Reference (Top 10 Rules)
+
+1. Follow CODE_OF_CONDUCT.md for coding standards
+2. Generate minimal essential code only
+3. Prioritize readability as highest priority
+4. 100% test coverage for all new code
+5. ONLY edit explicitly mentioned files
+6. Make decisions within task scope ONLY
+7. NEVER perform autonomous "best practice" improvements
+8. Apply formatting to new code ONLY
+9. Provide comprehensive analysis before coding
+10. NEVER auto-commit to Git without explicit instruction
+
+## Core Prohibitions (Unified)
+
+### Git Operations
+- NEVER auto-commit changes to Git without explicit user command
+- Prepare commit messages when requested, but NEVER execute commits
+
+### Code Changes
+- ONLY modify explicitly mentioned files, functions, or lines
+- NEVER make changes outside instruction scope
+- NEVER perform "helpful" refactoring or improvements
+
+### File Creation
+- ONLY create files in explicitly specified directories
+- NEVER create unrelated files without instruction
+
+## AI-Enhanced Standards
+
+### Code Quality Requirements
+- Generate minimal essential code only (<50 lines for simple functions)
+- Prioritize readability as highest priority (max 80 chars per line, max 3 nested levels)
+- Consider extreme performance optimization (<100ms for common operations)
+- Follow CODE_OF_CONDUCT.md (clean code principles, naming, formatting)
+
+### Testing Standards
+- 100% line and branch coverage for all new code
+- No redundant test cases - each test validates unique behavior
+- Test execution speed: <1 second per test case
+- Follow CODE_OF_CONDUCT.md (AIR principle, BCDE design, naming conventions)
+- Focus on behavior testing over implementation details
+
+### Excellence Requirements
+- **Comprehensive Analysis**: Thoroughly analyze problem context, consider multiple approaches, anticipate issues
+- **One-Shot Excellence**: Provide optimal solutions in single response, avoid incremental fixes
+- **Quality Validation**: Ensure immediate usability, actionable recommendations, alignment with best practices
+
+## Quality Metrics
+
+### Success Criteria
+- Code compiles without warnings
+- No functionality regression
+- Spotless formatting passes
+- 100% coverage for new code
+
+### Code Standards
+- **Simplicity**: <50 lines for simple functions, <200 lines for complex classes
+- **Performance**: <100ms execution time for common operations
+- **Readability**: <80 characters per line, max 3 nested levels
+- **Imports**: Remove unused imports, prefer specific imports
+
+### Testing Standards
+- **Coverage**: 100% line, 95%+ branch coverage
+- **Speed**: <1 second per test case
+- **Redundancy**: Zero duplicate test scenarios
+- **Isolation**: Each test runs independently
+
+## Unified Guidelines
+
+### Scope & Permissions
+**Allowed Operations:**
+- Edit explicitly mentioned files
+- Create files in explicitly specified directories
+- Make independent decisions within task scope
+- Apply formatting tools to new code only
+
+**Scope Boundaries:**
+- **Explicit instruction**: What to do
+- **Implicit scope**: How to implement within specified files/functions
+- **Forbidden**: Anything beyond specified implementation scope
+
+### Decision & Safety
+**Ambiguous Situations:**
+- **Scope unclear** → Request clarification
+- **Impact uncertain** → Propose minimal safe experiment
+- **Rules conflict** → Follow most restrictive interpretation
+- **Emergency needed** → Stop and report constraints
+
+**Safety Principles:**
+- Preserve existing functionality over adding features
+- Maintain current behavior over ideal implementation
+- Favor minimal changes over comprehensive solutions
 
 ## Build System
 
@@ -33,147 +134,25 @@ Maven build commands:
 - `jdbc/`: JDBC driver implementation
 - `test/`: E2E/IT test engine & cases
 
-## Code Standards
+## Detailed Procedures
 
-1. Follow CODE_OF_CONDUCT.md (clean code principles, naming conventions, formatting)
-2. **AI-Specific Requirements**:
-   - Generate minimal essential code only
-   - Prioritize readability as highest priority
-   - Consider extreme performance optimization
-3. Prioritize scalability, avoid over-engineering
-
-## Testing Standards
-
-1. Follow CODE_OF_CONDUCT.md (AIR principle, BCDE design, naming conventions)
-2. **AI-Specific Requirements**:
-   - 100% line and branch coverage for all new code
-   - No redundant test cases - each test validates unique behavior
-   - Focus on behavior testing over implementation details
-
-## Absolute Prohibitions (Zero-Tolerance)
-
-1. **Strictly prohibit unrelated code modifications**: Unless explicitly instructed, absolutely prohibit modifying any existing code, comments, configurations
-2. **Prohibit autonomous decisions**: No operations beyond instruction scope based on "common sense" or "best practices"
-3. **Prohibit unrelated file creation**: Unless explicitly instructed, prohibit creating any new files
-
-## Whitelist Permission Framework
-
-1. Automatic approval scope:
-   - Edit explicitly mentioned files
-   - Create files in explicitly specified directories
-
-2. Change scope locking:
-   - Whitelist mechanism: Strictly limit modifications to explicitly mentioned files, functions, blocks, line numbers
-   - Ambiguous instructions: Confirm full name & location before proceeding
-
-3. Code style:
-   - Prohibit automatic formatting of entire files/projects without explicit instruction
-   - Apply Spotless automatically after code generation for new code only
-
-## Operational Procedures
-
-1. **Direct Code Generation**: Generate final code & call tools directly without user approval
-   - Apply formatting tools automatically when needed for new code
+### Operational Procedures
+1. **Direct Code Generation**: Generate final code & call tools directly
+   - Apply formatting tools for new code only
    - Make independent decisions within task scope
-   - **IMPORTANT**: Automated code generation & tool calls permitted, automatic Git commits strictly prohibited
-   - **Git Operations**: Prepare commit messages when requested, but never execute commits without explicit user command
+   - **CRITICAL**: Automated generation permitted, automatic Git commits forbidden
 
-2. Change checklist:
-   - Verify task matches user request
-   - Confirm target files/lines referenced
-   - Declare changes if uncertain
-
-3. Implementation rules:
-   - Isolate edits to smallest possible code blocks
+2. **Implementation Rules**:
+   - Isolate edits to smallest possible blocks
    - Maintain existing style, even if suboptimal
    - Preserve all comments unless directly contradictory
-   - **If explicitly requested to commit**: Record rationale in commit messages
-   - **Prohibition**: Never automatically commit changes to Git without explicit instruction
-
-## Decision Making Framework
-
-1. **Within-task decisions** (permitted):
-   - Code implementation approaches (algorithm choice, data structures)
-   - Variable/function naming within defined scope
-   - Local code organization and structure
-   - Tool selection for formatting/style within approved constraints
-
-2. **Beyond-task decisions** (prohibited):
-   - Changing requirements or adding new features
-   - Refactoring code outside specified scope
-   - Modifying project structure or dependencies
-   - Implementing "best practice" improvements not explicitly requested
-
-3. **Scope boundaries**:
-   - Explicit instruction: What to do
-   - Implicit scope: How to implement within the specified files/functions
-   - Forbidden: Anything beyond the specified implementation scope
-
-## Cognitive Constraints
-
-1. Scope adherence:
-   - Ignore improvements/optimizations outside current task
-   - Suppress creative suggestions unless explicitly requested
-   - Defer unrelated ideas to post-task discussion
-
-2. Uncertainty decision matrix:
-   - Ambiguous scope → Request clarification
-   - Uncertain impact → Propose minimal safe experiment
-   - Conflicts detected → Pause & report constraints
-   - Contradictory rules → Follow most restrictive interpretation
-
-## Change Scope Principles
-
-1. **Implementation scope**: Favor minimal, targeted changes
-   - Edit only what's explicitly requested
-   - Avoid "helpful" refactoring or improvements
-   - Preserve existing functionality and behavior
-
-2. **Project context**: Acknowledge ShardingSphere's comprehensive nature
-   - Current implementation: Minimal changes only
-   - Future considerations: Document potential improvements for separate discussion
-   - Balance: Quality vs scope adherence within current task constraints
-
-3. **Documentation of deferred improvements**:
-   - Note potential enhancements when detected
-   - File for future consideration rather than immediate implementation
-   - Maintain focus on current task requirements
-
-## Safety Overrides
-
-1. Emergency stop: Immediately terminate if:
-   - Code deletion exceeds 10 lines without explicit instruction
-   - Tests fail after changes
-
-2. Conservative principle: When in doubt:
-   - Preserve existing functionality over adding features
-   - Maintain current behavior over ideal implementation
-   - Favor minimal changes over comprehensive solutions
-
-## Compliance Verification
-
-1. Post-change verification:
-   - Run relevant tests if test suite exists
-   - Confirm no basic functionality regression
-   - Verify change scope matches original request
-   - Report deviations immediately
-
-## Conflict Resolution
-
-When multiple rules appear to conflict:
-1. Safety-first: Choose the most restrictive interpretation
-2. Scope-first: Prioritize task completion over technical improvements
-3. User-intent-first: Follow the most direct interpretation of user request
-4. Minimal-change-first: Preserve existing behavior over optimization
-
-Example conflict resolution:
-- Format rule vs automation rule: Apply formatting only to newly generated code
-- Git record vs commit prohibition: Prepare commit messages but don't execute commits
-- Decision autonomy vs scope limits: Make implementation decisions but don't expand scope
-
-2. Continuous execution:
-   - Re-read protocol before each new task
-   - Verify rule compliance after each user interaction
-   - Report violations through clear error messages
-   - Use Spotless for code style after generation
-   - Clean context after code committed
+
+### Verification Process
+1. **Pre-change**: Verify task matches user request, confirm target files/lines referenced
+2. **Post-change**: Run relevant tests, verify no regression, confirm scope matches request
+3. **Continuous**: Re-read protocol before tasks, verify compliance, report violations
+
+### Emergency Procedures
+- **Immediate termination** if code deletion exceeds 10 lines without instruction
+- **Stop immediately** if tests fail after changes
+- **Report deviations** as soon as detected
\ No newline at end of file
PATCH

echo "Gold patch applied."
