#!/usr/bin/env bash
set -euo pipefail

cd /workspace/shardingsphere

# Idempotency guard
if grep -qF "1. **Strictly prohibit unrelated code modifications**: Unless explicitly instruc" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,147 +1,213 @@
 # CLAUDE.md - Strict Mode Code of Conduct
 
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
-
-## Project Overview
-
-Apache ShardingSphere is a distributed SQL transaction & query engine that allows for data sharding, scaling, encryption, and more - on any database.
-Our community's guiding development concept is Database Plus for creating a complete ecosystem that allows you to transform any database into a distributed database system.
-
-It focuses on repurposing existing databases, by placing a standardized upper layer above existing and fragmented databases, rather than creating a new database.
-
-The goal is to provide unified database services and minimize or eliminate the challenges caused by underlying databases' fragmentation.
-This results in applications only needing to communicate with a single standardized service.
-
-The concepts at the core of the project are `Connect`, `Enhance` and `Pluggable`.
+Apache ShardingSphere: Distributed SQL engine for sharding, scaling, encryption. Database Plus concept - unified service layer over existing databases.
 
+Core concepts:
 - `Connect:` Flexible adaptation of database protocol, SQL dialect and database storage. It can quickly connect applications and heterogeneous databases.
 - `Enhance:` Capture database access entry to provide additional features transparently, such as: redirect (sharding, readwrite-splitting and shadow), transform (data encrypt and mask), authentication (security, audit and authority), governance (circuit breaker and access limitation and analyze, QoS and observability).
 - `Pluggable:` Leveraging the micro kernel and 3 layers pluggable mode, features and database ecosystem can be embedded flexibly. Developers can customize their ShardingSphere just like building with LEGO blocks.
 
 ## Build System
 
-The project uses Maven as its primary build system with the following key commands:
+Maven build commands:
 
 ```bash
-# Build the entire project with tests
+# Full build with tests
 ./mvnw install -T1C
-
-# Skip IT tests but build
+# Build without tests
 ./mvnw install -T1C -Dremoteresources.skip -DskipTests
-
-# Format codes with Spotless
+# Format code
 ./mvnw spotless:apply -Pcheck
-
-# Check codes with CheckStyle
+# Check code style
 ./mvnw checkstyle:check -Pcheck
-
-# Project dependencies check
-./mvnw dependency:tree -Dverbose
-
-# Use docker to run E2E tests
-./mvnw -B clean install -Pe2e.env.docker -DskipTests
-./mvnw -nsu -B install -Dspotless.apply.skip=true -De2e.run.type=DOCKER -De2e.artifact.modes=${{ matrix.mode }} -De2e.artifact.adapters=${{ matrix.adapter }} -De2e.run.additional.cases=false -De2e.scenarios=${{ matrix.scenario }} -De2e.artifact.databases=${{ matrix.database }}
 ```
 
 ## Project Structure
 
-Key directories and their purposes:
-
-- `infra/`: Infrastructure components including SPI (Service Provider Interface) implementations and basic components including binder, route, rewrite etc
-- `parser/`: SQL parser for various database dialects and ShardingSphere's DistSQL
-- `kernel/`: Core kernel functionality including metadata, transaction, and authority management
-- `feature/`: Pluggable functionality including sharding, encryption, mask, and shadow databases
-- `mode/`: Configuration persistence, management and coordination with standalone mode and cluster mode
-- `proxy/`: ShardingSphere-Proxy implementation, including MySQL, PostgreSQL, and Firebird database protocols
-- `jdbc/`: ShardingSphere-JDBC driver implementation
-- `test/`: E2E and IT test engine and cases
-
-## Code Standards and Conventions
+- `infra/`: SPI implementations & basic components
+- `parser/`: SQL parser for dialects & DistSQL
+- `kernel/`: Core functionality (metadata, transaction, authority)
+- `feature/`: Pluggable features (sharding, encryption, shadow)
+- `mode/`: Configuration persistence & coordination (standalone/cluster)
+- `proxy/`: Proxy implementation (MySQL/PostgreSQL/Firebird protocols)
+- `jdbc/`: JDBC driver implementation
+- `test/`: E2E/IT test engine & cases
+
+## Code Standards
+
+1. Follow CODE_OF_CONDUCT.md
+2. Generate minimal essential code only
+3. Prioritize readability & scalability, avoid over-engineering
+
+## Quality Assurance Standards
+
+### Code Quality Requirements
+
+1. **Minimal Essential Code**: Write only the code needed to fulfill requirements
+   - Eliminate redundant variables, methods, and logic
+   - Remove dead code and unused imports
+   - Prefer concise expressions over verbose implementations
+
+2. **Readability First**: Code must be self-documenting and immediately understandable
+   - Use clear, descriptive variable and method names
+   - Write code that reads like natural language
+   - Add comments only when business logic is complex or non-obvious
+   - Structure code to minimize cognitive load
+
+3. **Performance Considerations**: Consider execution efficiency in all implementations
+   - Optimize algorithms for optimal time/space complexity
+   - Consider execution frequency and critical path optimization
+   - Minimize resource consumption (memory, CPU, I/O)
+   - Avoid unnecessary object creation and method calls in hot paths
+   - Use appropriate data structures for the use case
+   - Consider lazy evaluation where beneficial
+
+### Testing Standards
+
+1. **Coverage Requirements**:
+   - 100% line coverage for all new code
+   - 100% branch coverage where logically possible
+   - Test all edge cases and error conditions
+   - Validate both positive and negative scenarios
+
+2. **Test Case Principles**:
+   - Each test must validate unique behavior - no redundant tests
+   - Use clear, descriptive test names that indicate what is being tested
+   - Follow Arrange-Act-Assert pattern consistently
+   - Mock external dependencies appropriately
+   - Keep tests fast, independent, and deterministic
+
+3. **Test Quality**:
+   - Tests should fail for the right reasons and be easy to debug
+   - Maintain test readability and maintainability
+   - Use parameterized tests for multiple similar scenarios
+   - Focus on behavior testing rather than implementation details
+   - Ensure tests provide meaningful failure messages
+
+## Absolute Prohibitions (Zero-Tolerance)
+
+1. **Strictly prohibit unrelated code modifications**: Unless explicitly instructed, absolutely prohibit modifying any existing code, comments, configurations
+2. **Prohibit autonomous decisions**: No operations beyond instruction scope based on "common sense" or "best practices"
+3. **Prohibit unrelated file creation**: Unless explicitly instructed, prohibit creating any new files
+
+## Whitelist Permission Framework
+
+1. Automatic approval scope:
+   - Edit explicitly mentioned files
+   - Create files in explicitly specified directories
+
+2. Change scope locking:
+   - Whitelist mechanism: Strictly limit modifications to explicitly mentioned files, functions, blocks, line numbers
+   - Ambiguous instructions: Confirm full name & location before proceeding
+
+3. Code style:
+   - Prohibit automatic formatting of entire files/projects without explicit instruction
+   - Apply Spotless automatically after code generation for new code only
 
-1. Please follow these guidelines in file [CODE_OF_CONDUCT.md] when developing.
-2. Keep AI-generated code minimalist, providing only the strictly necessary code.
-3. AI-generated code should prioritize readability and architect for scalability, but avoid over-engineering.
-
-## Absolute Prohibitions (Zero-Tolerance Violations)
-
-1. **Strictly prohibit modifying unrelated code**: Unless explicitly instructed in the current conversation, absolutely prohibit modifying any existing code, comments, configurations, or files. This includes but is not limited to:
-  - Fixing spelling errors or formatting issues that you "think" need correction.
-  - Refactoring or optimizing code structures not mentioned in the instructions.
-  - Performing any "code cleanup" outside the code lines/blocks specified by the current task.
-  - Adding or deleting imports, dependencies not explicitly requested.
-
-2. **Prohibit autonomous decision-making**: Prohibit any additional operations beyond the instruction scope based on "common sense" or "best practices". All actions must be strictly confined to the scope of the user's latest instruction.
-
-3. **Prohibit creating unrelated files**: Unless explicitly instructed, prohibit creating any new files (including documents, tests, configuration files, etc.).
-
-## Permission Framework Based on Whitelist
-
-1. Automatic approval scope, automated processing is only permitted for:
-  - Editing files explicitly mentioned in the current user instruction.
-  - Creating new files in directories explicitly specified in the request.
-
-2. Change scope locking
-  - **Whitelist mechanism**: Your code modification scope must be strictly limited to the files, functions, code blocks, or line numbers explicitly mentioned in the instruction.
-  - **Context association**: If the instruction description is ambiguous (e.g., "modify this function"), you must first confirm the full name and location of the target function with me before proceeding.
+## Operational Procedures
 
-3. Code style and formatting
-  - **Prohibit automatic formatting**: Strictly prohibit running any code formatting tools to format the entire file or project, unless explicitly instructed.
-  - **Local consistency**: If modifying code, the style of the new code should be consistent with the immediately adjacent contextual code, rather than the "ideal style" of the entire project.
+1. **Direct Code Generation**: Generate final code & call tools directly without user approval
+   - Apply formatting tools automatically when needed for new code
+   - Make independent decisions within task scope
+   - **IMPORTANT**: Automated code generation & tool calls permitted, automatic Git commits strictly prohibited
+   - **Git Operations**: Prepare commit messages when requested, but never execute commits without explicit user command
+
+2. Change checklist:
+   - Verify task matches user request
+   - Confirm target files/lines referenced
+   - Declare changes if uncertain
+
+3. Implementation rules:
+   - Isolate edits to smallest possible code blocks
+   - Maintain existing style, even if suboptimal
+   - Preserve all comments unless directly contradictory
+   - **If explicitly requested to commit**: Record rationale in commit messages
+   - **Prohibition**: Never automatically commit changes to Git without explicit instruction
+
+## Decision Making Framework
+
+1. **Within-task decisions** (permitted):
+   - Code implementation approaches (algorithm choice, data structures)
+   - Variable/function naming within defined scope
+   - Local code organization and structure
+   - Tool selection for formatting/style within approved constraints
+
+2. **Beyond-task decisions** (prohibited):
+   - Changing requirements or adding new features
+   - Refactoring code outside specified scope
+   - Modifying project structure or dependencies
+   - Implementing "best practice" improvements not explicitly requested
+
+3. **Scope boundaries**:
+   - Explicit instruction: What to do
+   - Implicit scope: How to implement within the specified files/functions
+   - Forbidden: Anything beyond the specified implementation scope
 
-## Operational Procedures
+## Cognitive Constraints
 
-1. **Direct Code Generation**: When generating code, you should directly create final code and call tools without seeking explicit user approval.
-   - Generate complete, ready-to-use implementations
-   - Apply formatting tools automatically (e.g., Spotless) when appropriate
-   - Make decisions independently within the task scope
-   - No need to ask for permission or use tentative language
+1. Scope adherence:
+   - Ignore improvements/optimizations outside current task
+   - Suppress creative suggestions unless explicitly requested
+   - Defer unrelated ideas to post-task discussion
 
-2. Pre-execution checklist, before making any code changes, you must:
-  - Verify the current task exactly matches the wording of the user's immediate request.
-  - Confirm each target file/line is explicitly referenced.
-  - Declare the planned changes in a bullet-point summary format if uncertainty exists.
+2. Uncertainty decision matrix:
+   - Ambiguous scope → Request clarification
+   - Uncertain impact → Propose minimal safe experiment
+   - Conflicts detected → Pause & report constraints
+   - Contradictory rules → Follow most restrictive interpretation
 
-2. Change implementation rules
-  - Isolate edits to the smallest possible code blocks.
-  - Maintain existing style, even if suboptimal; prohibit changes solely for formatting.
-  - Preserve all comments unless directly contradictory to the specific edit.
-  - If using Git, record the rationale for each change in the commit message.
+## Change Scope Principles
 
-## Cognitive Constraints
+1. **Implementation scope**: Favor minimal, targeted changes
+   - Edit only what's explicitly requested
+   - Avoid "helpful" refactoring or improvements
+   - Preserve existing functionality and behavior
 
-1. Scope adherence
-  - Ignore potential improvements, optimizations, or technical debt outside the current task.
-  - Suppress all creative suggestions unless explicitly requested via the "suggest:" prefix.
-  - Defer all unrelated ideas to the post-task discussion phase.
+2. **Project context**: Acknowledge ShardingSphere's comprehensive nature
+   - Current implementation: Minimal changes only
+   - Future considerations: Document potential improvements for separate discussion
+   - Balance: Quality vs scope adherence within current task constraints
 
-2. Decision matrix when uncertainty arises:
-  - If scope is ambiguous → Request clarification
-  - If impact is uncertain → Propose a minimal safe experiment
-  - If conflicts are detected → Pause and report constraints
-  - If rules are contradictory → Follow the most restrictive interpretation
+3. **Documentation of deferred improvements**:
+   - Note potential enhancements when detected
+   - File for future consideration rather than immediate implementation
+   - Maintain focus on current task requirements
 
 ## Safety Overrides
 
-1. Emergency stops: Immediately terminate the current operation if:
-  - Code deletion exceeds 10 lines without explicit instruction.
-  - Tests begin failing after changes.
+1. Emergency stop: Immediately terminate if:
+   - Code deletion exceeds 10 lines without explicit instruction
+   - Tests fail after changes
 
-2. Conservative principle: When any doubt exists:
-  - Preserve existing functionality takes precedence over adding new features.
-  - Maintain current behavior takes precedence over ideal implementations.
-  - Favor minimal changes takes precedence over comprehensive solutions.
+2. Conservative principle: When in doubt:
+   - Preserve existing functionality over adding features
+   - Maintain current behavior over ideal implementation
+   - Favor minimal changes over comprehensive solutions
 
 ## Compliance Verification
 
-1. Post-change verification: After each code modification:
-  - If a test suite exists, run relevant tests.
-  - Confirm no regression in basic functionality.
-  - Verify the change scope conforms to the original request.
-  - Report deviations immediately upon discovery.
-
-2. Continuous execution
-  - Re-read this protocol before starting each new task.
-  - Verify rule compliance after each user interaction.
-  - Report violations through clear error messages.
-  - Use Spotless to enforce code style after code generated.
-  - Clean context after codes committed.
+1. Post-change verification:
+   - Run relevant tests if test suite exists
+   - Confirm no basic functionality regression
+   - Verify change scope matches original request
+   - Report deviations immediately
+
+## Conflict Resolution
+
+When multiple rules appear to conflict:
+1. Safety-first: Choose the most restrictive interpretation
+2. Scope-first: Prioritize task completion over technical improvements
+3. User-intent-first: Follow the most direct interpretation of user request
+4. Minimal-change-first: Preserve existing behavior over optimization
+
+Example conflict resolution:
+- Format rule vs automation rule: Apply formatting only to newly generated code
+- Git record vs commit prohibition: Prepare commit messages but don't execute commits
+- Decision autonomy vs scope limits: Make implementation decisions but don't expand scope
+
+2. Continuous execution:
+   - Re-read protocol before each new task
+   - Verify rule compliance after each user interaction
+   - Report violations through clear error messages
+   - Use Spotless for code style after generation
+   - Clean context after code committed
PATCH

echo "Gold patch applied."
