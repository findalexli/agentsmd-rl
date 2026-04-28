#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sentry-cocoa

# Idempotency guard
if grep -qF ".cursor/rules/file-filters.mdc" ".cursor/rules/file-filters.mdc" && grep -qF ".cursor/rules/github-workflow.mdc" ".cursor/rules/github-workflow.mdc" && grep -qF "- **Context Management**: When using compaction (which reduces context by summar" "AGENTS.md" && grep -qF "**ALWAYS adhere to AGENTS.md at all times.** This file contains comprehensive de" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/file-filters.mdc b/.cursor/rules/file-filters.mdc
@@ -1,214 +0,0 @@
----
-description: |
-  Apply this rule when making changes to the project's file hierarchy or structure, including:
-  - Creating new directories (e.g., new test directories, sample projects, utility folders)
-  - Renaming or moving existing directories
-  - Restructuring code organization (e.g., splitting modules, reorganizing tests)
-  - Adding new top-level folders or reorganizing subdirectories
-  - Reviewing PRs that involve file/folder creation, deletion, or reorganization
-  
-  This rule ensures that .github/file-filters.yml stays synchronized with the project structure
-  so that GitHub Actions workflows are properly triggered by relevant file changes. Missing
-  patterns can cause CI workflows to not run when they should, leading to undetected issues.
-alwaysApply: false
----
-
-# File Filters Configuration Rules
-
-## Core Principles
-
-### 1. Complete Coverage
-Every directory that contains code, tests, or configuration affecting CI should be included in at least one filter pattern.
-
-### 2. Logical Grouping
-Files should be grouped with workflows they logically affect:
-- **Source changes** → Build and test workflows
-- **Test changes** → Test workflows
-- **Configuration changes** → Relevant validation workflows
-- **Script changes** → Workflows using those scripts
-
-### 3. Hierarchy Awareness
-Use glob patterns (`**`) to capture all subdirectories and their contents recursively.
-
-## Verification Checklist
-
-Before submitting a PR that affects project structure:
-
-- [ ] List all new or renamed directories
-- [ ] Check if each directory appears in `.github/file-filters.yml`
-- [ ] Add missing patterns to appropriate filter groups
-- [ ] Verify glob patterns match intended files
-- [ ] Test locally using the `dorny/paths-filter` action logic
-
-## Pattern Best Practices
-
-### Use Glob Patterns for Depth
-✅ **Good:**
-```yaml
-- "Sources/**"           # Matches all files under Sources/
-- "Tests/**"             # Matches all files under Tests/
-- "SentryTestUtils/**"   # Matches all files under SentryTestUtils/
-```
-
-❌ **Bad:**
-```yaml
-- "Sources/*"            # Only matches one level deep
-- "Tests/"               # Doesn't match files, only directory
-```
-
-### Be Specific When Needed
-✅ **Good:**
-```yaml
-- "Samples/iOS-Cocoapods-*/**"   # Matches multiple specific samples
-- "**/*.xctestplan"              # Matches test plans anywhere
-- "scripts/ci-*.sh"              # Matches CI scripts specifically
-```
-
-❌ **Bad:**
-```yaml
-- "Samples/**"                   # Too broad, includes unrelated samples
-- "**/*"                         # Matches everything (defeats the purpose)
-```
-
-### Include Related Configuration
-Always include configuration files that affect the workflow:
-
-```yaml
-run_unit_tests_for_prs: &run_unit_tests_for_prs
-  - "Sources/**"
-  - "Tests/**"
-  
-  # GH Actions - Changes to these workflows should trigger tests
-  - ".github/workflows/test.yml"
-  - ".github/file-filters.yml"
-  
-  # Project files - Changes to project structure should trigger tests
-  - "Sentry.xcodeproj/**"
-  - "Sentry.xcworkspace/**"
-```
-
-## Common Patterns by Workflow Type
-
-These are complete, production-ready filter patterns for common workflow types. Use these as templates when adding new workflows or ensuring proper coverage.
-
-### Unit Test Workflows
-**Required coverage:** All test-related directories (Tests, SentryTestUtils, SentryTestUtilsDynamic, SentryTestUtilsTests) must be included to ensure changes to test infrastructure trigger test runs.
-```yaml
-run_unit_tests_for_prs: &run_unit_tests_for_prs
-  - "Sources/**"                    # Source code changes
-  - "Tests/**"                      # Test changes
-  - "SentryTestUtils/**"            # Test utility changes
-  - "SentryTestUtilsDynamic/**"     # Dynamic test utilities
-  - "SentryTestUtilsTests/**"       # Test utility tests
-  - ".github/workflows/test.yml"    # Workflow definition
-  - ".github/file-filters.yml"      # Filter changes
-  - "scripts/ci-*.sh"               # CI scripts
-  - "test-server/**"                # Test infrastructure
-  - "**/*.xctestplan"               # Test plans
-  - "Plans/**"                      # Test plan directory
-  - "Sentry.xcodeproj/**"           # Project structure
-```
-
-### Lint Workflows
-```yaml
-run_lint_swift_formatting_for_prs: &run_lint_swift_formatting_for_prs
-  - "**/*.swift"                    # All Swift files
-  - ".github/workflows/lint-swift-formatting.yml"
-  - ".github/file-filters.yml"
-  - ".swiftlint.yml"                # Linter config
-  - "scripts/.swiftlint-version"    # Version config
-```
-
-### Build Workflows
-```yaml
-run_build_for_prs: &run_build_for_prs
-  - "Sources/**"                    # Source code
-  - "Samples/**"                    # Sample projects
-  - ".github/workflows/build.yml"
-  - ".github/file-filters.yml"
-  - "Sentry.xcodeproj/**"           # Project files
-  - "Package*.swift"                # SPM config
-  - "scripts/sentry-xcodebuild.sh"  # Build script
-```
-
-## Troubleshooting
-
-### PR Not Triggering Expected Workflows
-
-1. **Check the paths-filter configuration** in the workflow:
-   ```yaml
-   - uses: dorny/paths-filter@v3
-     id: changes
-     with:
-       filters: .github/file-filters.yml
-   ```
-
-2. **Verify the filter name** matches between `file-filters.yml` and workflow:
-   ```yaml
-   # In file-filters.yml
-   run_unit_tests_for_prs: &run_unit_tests_for_prs
-   
-   # In workflow
-   if: steps.changes.outputs.run_unit_tests_for_prs == 'true'
-   ```
-
-3. **Test the pattern locally** using glob matching tools
-
-### Pattern Not Matching Expected Files
-
-Common issues:
-- Missing `**` for recursive matching
-- Using `*` instead of `**` for deep directories
-- Forgetting to include file extensions
-- Pattern too broad or too narrow
-
-## Maintenance Guidelines
-
-### Regular Audits
-Periodically review file-filters.yml to:
-- Remove patterns for deleted directories
-- Update patterns for renamed directories  
-- Ensure new directories are covered
-- Verify patterns match current structure
-
-### Documentation
-Each filter group should have comments explaining:
-- What the filter is for
-- Which workflow uses it
-- Special considerations
-
-### Testing Changes
-When updating file-filters.yml:
-1. Create a test PR with changes in the new pattern
-2. Verify the expected workflow triggers
-3. Check that unrelated workflows don't trigger
-4. Review the GitHub Actions logs for filter results
-
-## Error Prevention
-
-### Pre-Merge Checklist for Structural Changes
-
-When reviewing PRs that add/move/rename directories:
-
-1. **Identify all affected directories**
-   ```bash
-   gh pr view --json files --jq '.files[].path' | cut -d'/' -f1-2 | sort | uniq
-   ```
-
-2. **Check each directory against file-filters.yml**
-   ```bash
-   grep -r "DirectoryName" .github/file-filters.yml
-   ```
-
-3. **Add missing patterns** to appropriate filter groups
-
-4. **Verify the changes** trigger correct workflows
-
-### Automated Detection (Future Enhancement)
-
-Consider adding a script that:
-- Detects new top-level directories
-- Checks if they appear in file-filters.yml
-- Warns in PR if missing coverage
-
-Example location: `.github/workflows/check-file-filters.yml`
diff --git a/.cursor/rules/github-workflow.mdc b/.cursor/rules/github-workflow.mdc
@@ -1,292 +0,0 @@
----
-globs: .github/workflows/*
-alwaysApply: false
----
-
-# Cursor Rules for Sentry Cocoa Repository
-
-## GitHub Workflow Naming Convention
-
-### Workflow Names (Top-level `name:` field)
-
-Use concise, action-oriented names that describe the workflow's primary purpose:
-
-**Format:** `[Action] [Subject]`
-
-**Examples:**
-- ✅ `Release` (not "Release a new version")
-- ✅ `UI Tests` (not "Sentry Cocoa UI Tests")
-- ✅ `Benchmarking` (not "Run benchmarking tests")
-- ✅ `Lint SwiftLint` (not "Lint Swiftlint Formatting")
-- ✅ `Test CocoaPods` (not "CocoaPods Integration Test")
-
-### Job Names (Job-level `name:` field)
-
-Use clear, concise descriptions that avoid redundancy with the workflow name:
-
-**Principles:**
-1. **Remove redundant prefixes** - Don't repeat the workflow name
-2. **Use action verbs** - Start with what the job does
-3. **Avoid version-specific naming** - Don't include Xcode versions, tool versions, etc.
-4. **Keep it concise** - Maximum 3-4 words when possible
-
-**Patterns:**
-
-#### Build Jobs
-- ✅ `Build XCFramework Slice` (not "Build XCFramework Variant Slice")
-- ✅ `Assemble XCFramework Variant` (not "Assemble XCFramework" - be specific about variants)
-- ✅ `Build App and Test Runner`
-- ✅ `${{matrix.sdk}}` for platform-specific builds (e.g., "iphoneos", "macosx")
-- ✅ `${{inputs.name}}${{inputs.suffix}}` for variant assembly (e.g., "Sentry-Dynamic")
-
-#### Test Jobs
-- ✅ `Test ${{matrix.name}} V3 # Up the version with every change to keep track of flaky tests`
-- ✅ `Unit ${{matrix.name}}` (for unit test matrices)
-- ✅ `Run Benchmarks ${{matrix.suite}}` (for benchmarking matrices)
-- ✅ `Test SwiftUI V4 # Up the version with every change to keep track of flaky tests`
-- ✅ `Test Sentry Duplication V4 # Up the version with every change to keep track of flaky tests`
-
-**Note:** 
-- Version numbers (V1, V2, etc.) are included in test job names for flaky test tracking, with explanatory comments retained.
-- For matrix-based jobs, use clean variable names that produce readable job names (e.g., `${{matrix.sdk}}`, `${{matrix.name}}`, `${{inputs.name}}${{inputs.suffix}}`).
-- When matrix includes multiple iOS versions, add a descriptive `name` field to each matrix entry (e.g., "iOS 16 Swift", "iOS 17 Swift") for clear job identification.
-
-#### Validation Jobs
-- ✅ `Validate XCFramework` (not "Validate XCFramework - Static")
-- ✅ `Validate SPM Static` (not "Validate Swift Package Manager - Static")
-- ✅ `Check API Stability` (not "API Stability Check")
-
-#### Lint Jobs
-- ✅ `Lint` (job name when workflow already specifies the tool, e.g., "Lint SwiftLint")
-- ❌ `SwiftLint` (redundant with workflow name "Lint SwiftLint")
-- ❌ `Clang Format` (redundant with workflow name "Lint Clang")
-
-#### Utility Jobs
-- ✅ `Collect App Metrics` (not "Collect app metrics")
-- ✅ `Detect File Changes` (not "Detect Changed Files")
-- ✅ `Release New Version` (not "Release a new version")
-
-### Version Tracking for Flaky Test Management
-
-For UI test jobs that need version tracking for flaky test management, include the version number in BOTH the job name AND a comment:
-
-**Format:** `[Job Name] V{number} # Up the version with every change to keep track of flaky tests`
-
-**Example:**
-```yaml
-name: Test iOS Swift V5 # Up the version with every change to keep track of flaky tests
-```
-
-**Rationale:** 
-- Version numbers must be in the job name because failure rate monitoring captures job names and ignores comments
-- Comments are kept to provide context and instructions for developers
-
-### Matrix Variables in Names
-
-When using matrix variables, prefer descriptive names over technical details:
-
-**Examples:**
-- ✅ `Test ${{matrix.name}}` where name = "iOS Objective-C", "tvOS Swift"
-- ✅ `Test ${{matrix.name}}` where name = "iOS 16 Swift", "iOS 17 Swift", "iOS 18 Swift"
-- ✅ `Unit ${{matrix.name}}` where name = "iOS 16 Sentry", "macOS 15 Sentry", "tvOS 18 Sentry"
-- ✅ `Run Benchmarks ${{matrix.suite}}` where suite = "High-end device", "Low-end device"
-- ✅ `Check API Stability (${{ matrix.version }})` where version = "default", "v9"
-- ❌ `Test iOS Swift Xcode ${{matrix.xcode}}` (version-specific)
-
-### Reusable Workflow Names
-
-For reusable workflows (workflow_call), use descriptive names that indicate their purpose:
-
-**Examples:**
-- ✅ `Build XCFramework Slice`
-- ✅ `Assemble XCFramework Variant`
-- ✅ `UI Tests Common`
-
-### Benefits of This Convention
-
-1. **Status Check Stability** - Names won't break when tool versions change
-2. **Cleaner GitHub UI** - Shorter, more readable names in PR checks
-3. **Better Organization** - Consistent patterns make workflows easier to understand
-4. **Future-Proof** - Version-agnostic naming reduces maintenance overhead
-5. **Branch Protection Compatibility** - Stable names work well with GitHub's branch protection rules
-
-### Anti-Patterns to Avoid
-
-❌ **Don't include:**
-- Tool versions (Xcode 15.4, Swift 5.9, etc.) unless they are relevant to the job
-- Redundant workflow prefixes ("Release /", "UI Tests /")
-- Overly verbose descriptions
-- Technical implementation details in user-facing names
-- Lowercase inconsistency
-
-❌ **Examples of what NOT to do:**
-- "Release / Build XCFramework Variant Slice (Sentry, mh_dylib, -Dynamic, sentry-dynamic) / Build XCFramework Slice"
-- "UI Tests / UI Tests for iOS-Swift Xcode 15.4 - V5"
-- "Lint Swiftlint Formatting / SwiftLint" (redundant job name)
-- "Build Sentry Cocoa XCFramework Variant Slice"
-
-### Implementation Notes
-
-- Always include version numbers in test job names AND keep explanatory comments for flaky test management
-- Keep matrix variable usage minimal and descriptive
-- Ensure names remain meaningful when viewed in GitHub's status check UI
-- Test names in the GitHub PR interface before committing changes
-- For lint workflows, use simple "Lint" job name since the tool is already specified in the workflow name
-
----
-
-## GitHub Actions Concurrency Strategy
-
-### Overview
-
-This document outlines the concurrency configuration strategy for all GitHub Actions workflows in the Sentry Cocoa repository. The strategy optimizes CI resource usage while ensuring critical runs (like main branch pushes) are never interrupted.
-
-### Core Principles
-
-#### 1. Resource Optimization
-- **Cancel outdated PR runs** - When new commits are pushed to a PR, cancel the previous workflow run since only the latest commit matters for merge decisions
-- **Protect critical runs** - Never cancel workflows running on main branch, release branches, or scheduled runs as these are essential for maintaining baseline quality and release integrity
-- **Per-branch grouping** - Use `github.ref` for consistent concurrency grouping across all branch types
-
-#### 2. Consistent Patterns
-All workflows follow standardized concurrency patterns based on their trigger types and criticality.
-
-### Concurrency Patterns
-
-#### Pattern 1: Conditional Cancellation (Most Common)
-**Used by:** Most workflows that run on both main/release branches AND pull requests
-
-```yaml
-concurrency:
-  group: ${{ github.workflow }}-${{ github.ref }}
-  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
-```
-
-**Behavior:**
-- ✅ Cancels in-progress runs when new commits are pushed to PRs
-- ✅ Never cancels runs on main branch pushes
-- ✅ Never cancels runs on release branch pushes  
-- ✅ Never cancels scheduled runs
-- ✅ Never cancels manual workflow_dispatch runs
-
-**Examples:** `test.yml`, `build.yml`, `benchmarking.yml`, `ui-tests.yml`, all lint workflows
-
-#### Pattern 2: Always Cancel (PR-Only Workflows)
-**Used by:** Workflows that ONLY run on pull requests
-
-```yaml
-concurrency:
-  group: ${{ github.workflow }}-${{ github.ref }}
-  cancel-in-progress: true
-```
-
-**Behavior:**
-- ✅ Always cancels in-progress runs (safe since they only run on PRs)
-- ✅ Provides immediate feedback on latest changes
-
-**Examples:** `danger.yml`, `api-stability.yml`, `changes-in-high-risk-code.yml`
-
-#### Pattern 3: Fixed Group Name (Special Cases)
-**Used by:** Utility workflows with specific requirements
-
-```yaml
-concurrency:
-  group: "auto-update-tools"
-  cancel-in-progress: true
-```
-
-**Example:** `auto-update-tools.yml` (uses fixed group name for global coordination)
-
-### Implementation Details
-
-#### Group Naming Convention
-- **Standard:** `${{ github.workflow }}-${{ github.ref }}`
-- **Benefits:**
-  - Unique per workflow and branch/PR
-  - Consistent across all workflow types
-  - Works with main, release, and feature branches
-  - Handles PRs and direct pushes uniformly
-
-#### Why `github.ref` Instead of `github.head_ref || github.run_id`?
-- **Simpler logic** - No conditional expressions needed
-- **Consistent behavior** - Same pattern works for all trigger types
-- **Per-branch grouping** - Natural grouping by branch without special cases
-- **Better maintainability** - Single pattern to understand and maintain
-
-#### Cancellation Logic Evolution
-**Before:**
-```yaml
-cancel-in-progress: ${{ !(github.event_name == 'push' && github.ref == 'refs/heads/main') && github.event_name != 'schedule' }}
-```
-
-**After:**
-```yaml
-cancel-in-progress: ${{ github.event_name == 'pull_request' }}
-```
-
-**Why simplified:**
-- ✅ Much more readable and maintainable
-- ✅ Functionally identical behavior
-- ✅ Clear intent: "only cancel on pull requests"
-- ✅ Less prone to errors
-
-### Workflow-Specific Configurations
-
-#### High-Resource Workflows
-**Examples:** `benchmarking.yml`, `ui-tests.yml`
-- Use conditional cancellation to protect expensive main branch runs
-- Include detailed comments explaining resource considerations
-- May include special cleanup steps (e.g., SauceLabs job cancellation)
-
-#### Fast Validation Workflows  
-**Examples:** All lint workflows, `danger.yml`
-- Use appropriate cancellation strategy based on trigger scope
-- Focus on providing quick feedback on latest changes
-
-#### Critical Infrastructure Workflows
-**Examples:** `test.yml`, `build.yml`, `release.yml`
-- Never cancel on main/release branches to maintain quality gates
-- Ensure complete validation of production-bound code
-
-### Documentation Requirements
-
-Each workflow's concurrency block must include comments explaining:
-
-1. **Purpose** - Why concurrency control is needed for this workflow
-2. **Resource considerations** - Any expensive operations (SauceLabs, device time, etc.)
-3. **Branch protection logic** - Why main/release branches need complete runs
-4. **User experience** - How the configuration improves feedback timing
-
-#### Example Documentation:
-```yaml
-# Concurrency configuration:
-# - We use workflow-specific concurrency groups to prevent multiple benchmark runs on the same code,
-#   as benchmarks are extremely resource-intensive and require dedicated device time on SauceLabs.
-# - For pull requests, we cancel in-progress runs when new commits are pushed to avoid wasting
-#   expensive external testing resources and provide timely performance feedback.
-# - For main branch pushes, we never cancel benchmarks to ensure we have complete performance
-#   baselines for every main branch commit, which are critical for performance regression detection.
-concurrency:
-  group: ${{ github.workflow }}-${{ github.ref }}
-  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
-```
-
-### Maintenance Guidelines
-
-#### When Adding New Workflows
-1. **Identify trigger scope** - Does it run on main/release branches?
-2. **Choose appropriate pattern** - Conditional vs always cancel
-3. **Add documentation** - Explain the resource and timing considerations
-4. **Follow naming convention** - Use standard group naming pattern
-
-#### When Modifying Existing Workflows
-1. **Preserve protection** - Don't break main/release branch safeguards
-2. **Update documentation** - Keep comments accurate and helpful
-3. **Test edge cases** - Verify behavior with scheduled/manual triggers
-4. **Consider resource impact** - Evaluate cost of additional runs
-
-#### Red Flags to Avoid
-- ❌ Never use `cancel-in-progress: true` on workflows that run on main/release branches
-- ❌ Don't create complex conditional logic when simple patterns work
-- ❌ Avoid custom group names unless absolutely necessary
-- ❌ Don't skip documentation - future maintainers need context
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,657 @@
+# AGENTS.md
+
+This file provides comprehensive guidance for AI coding agents working with the Sentry Cocoa SDK repository.
+
+## Agent Responsibilities
+
+- **Continuous Learning**: Whenever an agent performs a task and discovers new patterns, conventions, or best practices that aren't documented here, it should add these learnings to AGENTS.md. This ensures the documentation stays current and helps future agents work more effectively.
+- **Context Management**: When using compaction (which reduces context by summarizing older messages), the agent must re-read AGENTS.md afterwards to ensure it's always fully available in context. This guarantees that all guidelines, conventions, and best practices remain accessible throughout the entire session.
+
+## Best Practices
+
+### Compilation & Testing
+
+- Before forming a commit, ensure compilation succeeds for all platforms: iOS, macOS, tvOS, watchOS and visionOS. This should hold for:
+  - the SDK framework targets
+  - the sample apps
+  - the test targets for the SDK framework and sample apps
+- Before submitting a branch for a PR, ensure there are no new issues being introduced for:
+  - static analysis
+  - runtime analysis, using thread, address and undefined behavior sanitizers
+  - cross platform dependencies:
+    - React Native
+    - Flutter
+    - .Net
+    - Unity
+- While preparing changes, ensure that relevant documentation is added/updated in:
+  - headerdocs and inline comments
+  - readmes and maintainer markdown docs
+  - our docs repo and web app onboarding
+  - our cli and integration wizard
+
+### Testing Instructions
+
+- Find the CI plan in the .github/workflows folder.
+- Run unit tests: `make run-test-server && make test`
+- Run important UI tests: `make test-ui-critical`
+- Fix any test or type errors until the whole suite is green.
+- Add or update tests for the code you change, even if nobody asked.
+
+### Commit Guidelines
+
+- **Pre-commit Hooks**: This repository uses pre-commit hooks. If a commit fails because files were changed during the commit process (e.g., by formatting hooks), automatically retry the commit. Pre-commit hooks may modify files (like formatting), and the commit should be retried with the updated files.
+
+#### Conventional Commits
+
+This project uses [Conventional Commits 1.0.0](https://www.conventionalcommits.org/) for all commit messages.
+
+**Commit Message Structure:**
+
+```
+<type>[optional scope]: <description>
+
+[optional body]
+
+[optional footer(s)]
+```
+
+**Required Types:**
+
+- `feat:` - A new feature (correlates with MINOR in SemVer)
+- `fix:` - A bug fix (correlates with PATCH in SemVer)
+
+**Other Allowed Types:**
+
+- `build:` - Changes to build system or dependencies
+- `chore:` - Routine tasks, maintenance
+- `ci:` - Changes to CI configuration
+- `docs:` - Documentation changes
+- `style:` - Code style changes (formatting, missing semi-colons, etc.)
+- `refactor:` - Code refactoring without changing functionality
+- `perf:` - Performance improvements
+- `test:` - Adding or updating tests
+
+**Breaking Changes:**
+
+- Add `!` after type/scope: `feat!:` or `feat(api)!:`
+- Or use footer: `BREAKING CHANGE: description`
+
+**Examples:**
+
+```
+feat: add new session replay feature
+fix: resolve memory leak in session storage
+docs: update installation guide
+refactor: simplify event serialization
+feat!: change API response format
+
+BREAKING CHANGE: API now returns JSON instead of XML
+```
+
+#### No AI References
+
+**NEVER mention AI assistant names (like Claude, ChatGPT, Cursor, etc.) in commit messages or PR descriptions.**
+
+Keep commit messages focused on the technical changes made and their purpose.
+
+**What to avoid:**
+
+- ❌ "Add feature X with Claude's help"
+- ❌ "Co-Authored-By: Claude <noreply@anthropic.com>"
+- ❌ "Co-Authored-By: Cursor <noreply@cursor.com>"
+- ❌ "Generated with Claude Code"
+- ❌ "Generated by Cursor"
+- ❌ "🤖 Generated with [Claude Code](https://claude.com/claude-code)"
+
+**Good examples:**
+
+- ✅ "feat: add user authentication system"
+- ✅ "fix: resolve connection pool exhaustion"
+- ✅ "refactor: simplify error handling logic"
+
+## Helpful Commands
+
+- format code: `make format`
+- run static analysis: `make analyze`
+- run unit tests: `make run-test-server && make test`
+- run important UI tests: `make test-ui-critical`
+- build the XCFramework deliverables: `make build-xcframework`
+- lint pod deliverable: `make pod-lint`
+
+## Resources & Documentation
+
+- **Main Documentation**: [docs.sentry.io/platforms/apple](https://docs.sentry.io/platforms/apple/)
+  - **Docs Repo**: [sentry-docs](https://github.com/getsentry/sentry-docs)
+- **SDK Developer Documentation**: [develop.sentry.dev/sdk/](https://develop.sentry.dev/sdk/)
+
+### `sentry-cocoa` Maintainer Documentation
+
+- **README**: @README.md
+- **Contributing**: @CONTRIBUTING.md
+- **Developer README**: @develop-docs/README.md
+- **Sample App collection README**: @Samples/README.md
+
+## Related Code & Repositories
+
+- [sentry-cli](https://github.com/getsentry/sentry-cli): uploading dSYMs for symbolicating stack traces gathered via the SDK
+- [sentry-wizard](https://github.com/getsentry/sentry-wizard): automatically injecting SDK initialization code
+- [sentry-cocoa onboarding](https://github.com/getsentry/sentry/blob/master/static/app/utils/gettingStartedDocs/apple.tsx): the web app's onboarding instructions for `sentry-cocoa`
+- [sentry-unity](https://github.com/getsentry/sentry-unity): the Sentry Unity SDK, which depends on sentry-cocoa
+- [sentry-dart](https://github.com/getsentry/sentry-dart): the Sentry Dart SDK, which depends on sentry-cocoa
+- [sentry-react-native](https://github.com/getsentry/sentry-react-native): the Sentry React Native SDK, which depends on sentry-cocoa
+- [sentry-dotnet](https://github.com/getsentry/sentry-dotnet): the Sentry .NET SDK, which depends on sentry-cocoa
+
+## GitHub Workflow Guidelines
+
+### Workflow Naming Convention
+
+#### Workflow Names (Top-level `name:` field)
+
+Use concise, action-oriented names that describe the workflow's primary purpose:
+
+**Format:** `[Action] [Subject]`
+
+**Examples:**
+
+- ✅ `Release` (not "Release a new version")
+- ✅ `UI Tests` (not "Sentry Cocoa UI Tests")
+- ✅ `Benchmarking` (not "Run benchmarking tests")
+- ✅ `Lint SwiftLint` (not "Lint Swiftlint Formatting")
+- ✅ `Test CocoaPods` (not "CocoaPods Integration Test")
+
+#### Job Names (Job-level `name:` field)
+
+Use clear, concise descriptions that avoid redundancy with the workflow name:
+
+**Principles:**
+
+1. **Remove redundant prefixes** - Don't repeat the workflow name
+2. **Use action verbs** - Start with what the job does
+3. **Avoid version-specific naming** - Don't include Xcode versions, tool versions, etc.
+4. **Keep it concise** - Maximum 3-4 words when possible
+
+**Patterns:**
+
+##### Build Jobs
+
+- ✅ `Build XCFramework Slice` (not "Build XCFramework Variant Slice")
+- ✅ `Assemble XCFramework Variant` (not "Assemble XCFramework" - be specific about variants)
+- ✅ `Build App and Test Runner`
+- ✅ `${{matrix.sdk}}` for platform-specific builds (e.g., "iphoneos", "macosx")
+- ✅ `${{inputs.name}}${{inputs.suffix}}` for variant assembly (e.g., "Sentry-Dynamic")
+
+##### Test Jobs
+
+- ✅ `Test ${{matrix.name}} V3 # Up the version with every change to keep track of flaky tests`
+- ✅ `Unit ${{matrix.name}}` (for unit test matrices)
+- ✅ `Run Benchmarks ${{matrix.suite}}` (for benchmarking matrices)
+- ✅ `Test SwiftUI V4 # Up the version with every change to keep track of flaky tests`
+- ✅ `Test Sentry Duplication V4 # Up the version with every change to keep track of flaky tests`
+
+**Note:**
+
+- Version numbers (V1, V2, etc.) are included in test job names for flaky test tracking, with explanatory comments retained.
+- For matrix-based jobs, use clean variable names that produce readable job names (e.g., `${{matrix.sdk}}`, `${{matrix.name}}`, `${{inputs.name}}${{inputs.suffix}}`).
+- When matrix includes multiple iOS versions, add a descriptive `name` field to each matrix entry (e.g., "iOS 16 Swift", "iOS 17 Swift") for clear job identification.
+
+##### Validation Jobs
+
+- ✅ `Validate XCFramework` (not "Validate XCFramework - Static")
+- ✅ `Validate SPM Static` (not "Validate Swift Package Manager - Static")
+- ✅ `Check API Stability` (not "API Stability Check")
+
+##### Lint Jobs
+
+- ✅ `Lint` (job name when workflow already specifies the tool, e.g., "Lint SwiftLint")
+- ❌ `SwiftLint` (redundant with workflow name "Lint SwiftLint")
+- ❌ `Clang Format` (redundant with workflow name "Lint Clang")
+
+##### Utility Jobs
+
+- ✅ `Collect App Metrics` (not "Collect app metrics")
+- ✅ `Detect File Changes` (not "Detect Changed Files")
+- ✅ `Release New Version` (not "Release a new version")
+
+#### Version Tracking for Flaky Test Management
+
+For UI test jobs that need version tracking for flaky test management, include the version number in BOTH the job name AND a comment:
+
+**Format:** `[Job Name] V{number} # Up the version with every change to keep track of flaky tests`
+
+**Example:**
+
+```yaml
+name: Test iOS Swift V5 # Up the version with every change to keep track of flaky tests
+```
+
+**Rationale:**
+
+- Version numbers must be in the job name because failure rate monitoring captures job names and ignores comments
+- Comments are kept to provide context and instructions for developers
+
+#### Matrix Variables in Names
+
+When using matrix variables, prefer descriptive names over technical details:
+
+**Examples:**
+
+- ✅ `Test ${{matrix.name}}` where name = "iOS Objective-C", "tvOS Swift"
+- ✅ `Test ${{matrix.name}}` where name = "iOS 16 Swift", "iOS 17 Swift", "iOS 18 Swift"
+- ✅ `Unit ${{matrix.name}}` where name = "iOS 16 Sentry", "macOS 15 Sentry", "tvOS 18 Sentry"
+- ✅ `Run Benchmarks ${{matrix.suite}}` where suite = "High-end device", "Low-end device"
+- ✅ `Check API Stability (${{ matrix.version }})` where version = "default", "v9"
+- ❌ `Test iOS Swift Xcode ${{matrix.xcode}}` (version-specific)
+
+#### Reusable Workflow Names
+
+For reusable workflows (workflow_call), use descriptive names that indicate their purpose:
+
+**Examples:**
+
+- ✅ `Build XCFramework Slice`
+- ✅ `Assemble XCFramework Variant`
+- ✅ `UI Tests Common`
+
+#### Benefits of This Convention
+
+1. **Status Check Stability** - Names won't break when tool versions change
+2. **Cleaner GitHub UI** - Shorter, more readable names in PR checks
+3. **Better Organization** - Consistent patterns make workflows easier to understand
+4. **Future-Proof** - Version-agnostic naming reduces maintenance overhead
+5. **Branch Protection Compatibility** - Stable names work well with GitHub's branch protection rules
+
+#### Anti-Patterns to Avoid
+
+❌ **Don't include:**
+
+- Tool versions (Xcode 15.4, Swift 5.9, etc.) unless they are relevant to the job
+- Redundant workflow prefixes ("Release /", "UI Tests /")
+- Overly verbose descriptions
+- Technical implementation details in user-facing names
+- Lowercase inconsistency
+
+❌ **Examples of what NOT to do:**
+
+- "Release / Build XCFramework Variant Slice (Sentry, mh_dylib, -Dynamic, sentry-dynamic) / Build XCFramework Slice"
+- "UI Tests / UI Tests for iOS-Swift Xcode 15.4 - V5"
+- "Lint Swiftlint Formatting / SwiftLint" (redundant job name)
+- "Build Sentry Cocoa XCFramework Variant Slice"
+
+### GitHub Actions Concurrency Strategy
+
+#### Overview
+
+This document outlines the concurrency configuration strategy for all GitHub Actions workflows in the Sentry Cocoa repository. The strategy optimizes CI resource usage while ensuring critical runs (like main branch pushes) are never interrupted.
+
+#### Core Principles
+
+##### 1. Resource Optimization
+
+- **Cancel outdated PR runs** - When new commits are pushed to a PR, cancel the previous workflow run since only the latest commit matters for merge decisions
+- **Protect critical runs** - Never cancel workflows running on main branch, release branches, or scheduled runs as these are essential for maintaining baseline quality and release integrity
+- **Per-branch grouping** - Use `github.ref` for consistent concurrency grouping across all branch types
+
+##### 2. Consistent Patterns
+
+All workflows follow standardized concurrency patterns based on their trigger types and criticality.
+
+#### Concurrency Patterns
+
+##### Pattern 1: Conditional Cancellation (Most Common)
+
+**Used by:** Most workflows that run on both main/release branches AND pull requests
+
+```yaml
+concurrency:
+  group: ${{ github.workflow }}-${{ github.ref }}
+  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
+```
+
+**Behavior:**
+
+- ✅ Cancels in-progress runs when new commits are pushed to PRs
+- ✅ Never cancels runs on main branch pushes
+- ✅ Never cancels runs on release branch pushes
+- ✅ Never cancels runs on scheduled runs
+- ✅ Never cancels manual workflow_dispatch runs
+
+**Examples:** `test.yml`, `build.yml`, `benchmarking.yml`, `ui-tests.yml`, all lint workflows
+
+##### Pattern 2: Always Cancel (PR-Only Workflows)
+
+**Used by:** Workflows that ONLY run on pull requests
+
+```yaml
+concurrency:
+  group: ${{ github.workflow }}-${{ github.ref }}
+  cancel-in-progress: true
+```
+
+**Behavior:**
+
+- ✅ Always cancels in-progress runs (safe since they only run on PRs)
+- ✅ Provides immediate feedback on latest changes
+
+**Examples:** `danger.yml`, `api-stability.yml`, `changes-in-high-risk-code.yml`
+
+##### Pattern 3: Fixed Group Name (Special Cases)
+
+**Used by:** Utility workflows with specific requirements
+
+```yaml
+concurrency:
+  group: "auto-update-tools"
+  cancel-in-progress: true
+```
+
+**Example:** `auto-update-tools.yml` (uses fixed group name for global coordination)
+
+#### Implementation Details
+
+##### Group Naming Convention
+
+- **Standard:** `${{ github.workflow }}-${{ github.ref }}`
+- **Benefits:**
+  - Unique per workflow and branch/PR
+  - Consistent across all workflow types
+  - Works with main, release, and feature branches
+  - Handles PRs and direct pushes uniformly
+
+##### Why `github.ref` Instead of `github.head_ref || github.run_id`?
+
+- **Simpler logic** - No conditional expressions needed
+- **Consistent behavior** - Same pattern works for all trigger types
+- **Per-branch grouping** - Natural grouping by branch without special cases
+- **Better maintainability** - Single pattern to understand and maintain
+
+##### Cancellation Logic Evolution
+
+**Before:**
+
+```yaml
+cancel-in-progress: ${{ !(github.event_name == 'push' && github.ref == 'refs/heads/main') && github.event_name != 'schedule' }}
+```
+
+**After:**
+
+```yaml
+cancel-in-progress: ${{ github.event_name == 'pull_request' }}
+```
+
+**Why simplified:**
+
+- ✅ Much more readable and maintainable
+- ✅ Functionally identical behavior
+- ✅ Clear intent: "only cancel on pull requests"
+- ✅ Less prone to errors
+
+#### Workflow-Specific Configurations
+
+##### High-Resource Workflows
+
+**Examples:** `benchmarking.yml`, `ui-tests.yml`
+
+- Use conditional cancellation to protect expensive main branch runs
+- Include detailed comments explaining resource considerations
+- May include special cleanup steps (e.g., SauceLabs job cancellation)
+
+##### Fast Validation Workflows
+
+**Examples:** All lint workflows, `danger.yml`
+
+- Use appropriate cancellation strategy based on trigger scope
+- Focus on providing quick feedback on latest changes
+
+##### Critical Infrastructure Workflows
+
+**Examples:** `test.yml`, `build.yml`, `release.yml`
+
+- Never cancel on main/release branches to maintain quality gates
+- Ensure complete validation of production-bound code
+
+#### Documentation Requirements
+
+Each workflow's concurrency block must include comments explaining:
+
+1. **Purpose** - Why concurrency control is needed for this workflow
+2. **Resource considerations** - Any expensive operations (SauceLabs, device time, etc.)
+3. **Branch protection logic** - Why main/release branches need complete runs
+4. **User experience** - How the configuration improves feedback timing
+
+#### Example Documentation:
+
+```yaml
+# Concurrency configuration:
+# - We use workflow-specific concurrency groups to prevent multiple benchmark runs on the same code,
+#   as benchmarks are extremely resource-intensive and require dedicated device time on SauceLabs.
+# - For pull requests, we cancel in-progress runs when new commits are pushed to avoid wasting
+#   expensive external testing resources and provide timely performance feedback.
+# - For main branch pushes, we never cancel benchmarks to ensure we have complete performance
+#   baselines for every main branch commit, which are critical for performance regression detection.
+concurrency:
+  group: ${{ github.workflow }}-${{ github.ref }}
+  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
+```
+
+## File Filters Configuration Rules
+
+### Core Principles
+
+#### 1. Complete Coverage
+
+Every directory that contains code, tests, or configuration affecting CI should be included in at least one filter pattern.
+
+#### 2. Logical Grouping
+
+Files should be grouped with workflows they logically affect:
+
+- **Source changes** → Build and test workflows
+- **Test changes** → Test workflows
+- **Configuration changes** → Relevant validation workflows
+- **Script changes** → Workflows using those scripts
+
+#### 3. Hierarchy Awareness
+
+Use glob patterns (`**`) to capture all subdirectories and their contents recursively.
+
+### Verification Checklist
+
+Before submitting a PR that affects project structure:
+
+- [ ] List all new or renamed directories
+- [ ] Check if each directory appears in `.github/file-filters.yml`
+- [ ] Add missing patterns to appropriate filter groups
+- [ ] Verify glob patterns match intended files
+- [ ] Test locally using the `dorny/paths-filter` action logic
+
+### Pattern Best Practices
+
+#### Use Glob Patterns for Depth
+
+✅ **Good:**
+
+```yaml
+- "Sources/**" # Matches all files under Sources/
+- "Tests/**" # Matches all files under Tests/
+- "SentryTestUtils/**" # Matches all files under SentryTestUtils/
+```
+
+❌ **Bad:**
+
+```yaml
+- "Sources/*" # Only matches one level deep
+- "Tests/" # Doesn't match files, only directory
+```
+
+#### Be Specific When Needed
+
+✅ **Good:**
+
+```yaml
+- "Samples/iOS-Cocoapods-*/**" # Matches multiple specific samples
+- "**/*.xctestplan" # Matches test plans anywhere
+- "scripts/ci-*.sh" # Matches CI scripts specifically
+```
+
+❌ **Bad:**
+
+```yaml
+- "Samples/**" # Too broad, includes unrelated samples
+- "**/*" # Matches everything (defeats the purpose)
+```
+
+#### Include Related Configuration
+
+Always include configuration files that affect the workflow:
+
+```yaml
+run_unit_tests_for_prs: &run_unit_tests_for_prs
+  - "Sources/**"
+  - "Tests/**"
+
+  # GH Actions - Changes to these workflows should trigger tests
+  - ".github/workflows/test.yml"
+  - ".github/file-filters.yml"
+
+  # Project files - Changes to project structure should trigger tests
+  - "Sentry.xcodeproj/**"
+  - "Sentry.xcworkspace/**"
+```
+
+### Common Patterns by Workflow Type
+
+These are complete, production-ready filter patterns for common workflow types. Use these as templates when adding new workflows or ensuring proper coverage.
+
+#### Unit Test Workflows
+
+**Required coverage:** All test-related directories (Tests, SentryTestUtils, SentryTestUtilsDynamic, SentryTestUtilsTests) must be included to ensure changes to test infrastructure trigger test runs.
+
+```yaml
+run_unit_tests_for_prs: &run_unit_tests_for_prs
+  - "Sources/**" # Source code changes
+  - "Tests/**" # Test changes
+  - "SentryTestUtils/**" # Test utility changes
+  - "SentryTestUtilsDynamic/**" # Dynamic test utilities
+  - "SentryTestUtilsTests/**" # Test utility tests
+  - ".github/workflows/test.yml" # Workflow definition
+  - ".github/file-filters.yml" # Filter changes
+  - "scripts/ci-*.sh" # CI scripts
+  - "test-server/**" # Test infrastructure
+  - "**/*.xctestplan" # Test plans
+  - "Plans/**" # Test plan directory
+  - "Sentry.xcodeproj/**" # Project structure
+```
+
+#### Lint Workflows
+
+```yaml
+run_lint_swift_formatting_for_prs: &run_lint_swift_formatting_for_prs
+  - "**/*.swift" # All Swift files
+  - ".github/workflows/lint-swift-formatting.yml"
+  - ".github/file-filters.yml"
+  - ".swiftlint.yml" # Linter config
+  - "scripts/.swiftlint-version" # Version config
+```
+
+#### Build Workflows
+
+```yaml
+run_build_for_prs: &run_build_for_prs
+  - "Sources/**" # Source code
+  - "Samples/**" # Sample projects
+  - ".github/workflows/build.yml"
+  - ".github/file-filters.yml"
+  - "Sentry.xcodeproj/**" # Project files
+  - "Package*.swift" # SPM config
+  - "scripts/sentry-xcodebuild.sh" # Build script
+```
+
+### Troubleshooting
+
+#### PR Not Triggering Expected Workflows
+
+1. **Check the paths-filter configuration** in the workflow:
+   ```yaml
+   - uses: dorny/paths-filter@v3
+     id: changes
+     with:
+       filters: .github/file-filters.yml
+   ```
+
+2. **Verify the filter name** matches between `file-filters.yml` and workflow:
+   ```yaml
+   # In file-filters.yml
+   run_unit_tests_for_prs: &run_unit_tests_for_prs
+
+   # In workflow
+   if: steps.changes.outputs.run_unit_tests_for_prs == 'true'
+   ```
+
+3. **Test the pattern locally** using glob matching tools
+
+#### Pattern Not Matching Expected Files
+
+Common issues:
+
+- Missing `**` for recursive matching
+- Using `*` instead of `**` for deep directories
+- Forgetting to include file extensions
+- Pattern too broad or too narrow
+
+### Maintenance Guidelines
+
+#### Regular Audits
+
+Periodically review file-filters.yml to:
+
+- Remove patterns for deleted directories
+- Update patterns for renamed directories
+- Ensure new directories are covered
+- Verify patterns match current structure
+
+#### Documentation
+
+Each filter group should have comments explaining:
+
+- What the filter is for
+- Which workflow uses it
+- Special considerations
+
+#### Testing Changes
+
+When updating file-filters.yml:
+
+1. Create a test PR with changes in the new pattern
+2. Verify the expected workflow triggers
+3. Check that unrelated workflows don't trigger
+4. Review the GitHub Actions logs for filter results
+
+### Error Prevention
+
+#### Pre-Merge Checklist for Structural Changes
+
+When reviewing PRs that add/move/rename directories:
+
+1. **Identify all affected directories**
+   ```bash
+   gh pr view --json files --jq '.files[].path' | cut -d'/' -f1-2 | sort | uniq
+   ```
+
+2. **Check each directory against file-filters.yml**
+   ```bash
+   grep -r "DirectoryName" .github/file-filters.yml
+   ```
+
+3. **Add missing patterns** to appropriate filter groups
+
+4. **Verify the changes** trigger correct workflows
+
+#### Automated Detection (Future Enhancement)
+
+Consider adding a script that:
+
+- Detects new top-level directories
+- Checks if they appear in file-filters.yml
+- Warns in PR if missing coverage
+
+Example location: `.github/workflows/check-file-filters.yml`
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -2,54 +2,36 @@
 
 This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
 
-## Best Practices
-
-- Before forming a commit, ensure compilation succeeds for all platforms: iOS, macOS, tvOS, watchOS and visionOS. This should hold for:
-  - the SDK framework targets
-  - the sample apps
-  - the test targets for the SDK framework and sample apps
-- Before submitting a branch for a PR, ensure there are no new issues being introduced for:
-  - static analysis
-  - runtime analysis, using thread, address and undefined behavior sanitizers
-  - cross platform dependencies:
-    - React Native
-    - Flutter
-    - .Net
-    - Unity
-- While preparing changes, ensure that relevant documentation is added/updated in:
-  - headerdocs and inline comments
-  - readmes and maintainer markdown docs
-  - our docs repo and web app onboarding
-  - our cli and integration wizard
-
-## Helpful Commands
-
-- format code: `make format`
-- run static analysis: `make analyze`
-- run unit tests: `make run-test-server && make test`
-- run important UI tests: `make test-ui-critical`
-- build the XCFramework deliverables: `make build-xcframework`
-- lint pod deliverable: make `pod-lint`
-
-## Resources & Documentation
-
-- **Main Documentation**: [docs.sentry.io/platforms/apple](https://docs.sentry.io/platforms/apple/)
-  - **Docs Repo**: [sentry-docs](https://github.com/getsentry/sentry-docs)
-- **SDK Developer Documentation**: [develop.sentry.dev/sdk/](https://develop.sentry.dev/sdk/)
-
-### `sentry-cocoa` Maintainer Documentation
-
-- **README**: @README.md
-- **Contributing**: @CONTRIBUTING.md
-- **Developer README**: @develop-docs/README.md
-- **Sample App collection README**: @Samples/README.md
-
-## Related Code & Repositories
-
-- [sentry-cli](https://github.com/getsentry/sentry-cli): uploading dSYMs for symbolicating stack traces gathered via the SDK
-- [sentry-wizard](https://github.com/getsentry/sentry-wizard): automatically injecting SDK initialization code
-- [sentry-cocoa onboarding](https://github.com/getsentry/sentry/blob/master/static/app/utils/gettingStartedDocs/apple.tsx): the web app's onboarding instructions for `sentry-cocoa`
-- [sentry-unity](https://github.com/getsentry/sentry-unity): the Sentry Unity SDK, which depends on sentry-cocoa
-- [sentry-dart](https://github.com/getsentry/sentry-dart): the Sentry Dart SDK, which depends on sentry-cocoa
-- [sentry-react-native](https://github.com/getsentry/sentry-react-native): the Sentry React Native SDK, which depends on sentry-cocoa
-- [sentry-dotnet](https://github.com/getsentry/sentry-dotnet): the Sentry .NET SDK, which depends on sentry-cocoa
+## Project Guidelines
+
+**ALWAYS adhere to AGENTS.md at all times.** This file contains comprehensive development patterns, conventions, and best practices for the Sentry Cocoa SDK project.
+
+## Critical Rules
+
+1. **Read AGENTS.md**: Familiarize yourself with all guidelines before making changes
+2. **No AI References**: NEVER mention AI assistant names (Claude, ChatGPT, Cursor, etc.) in:
+   - Git commit messages
+   - Pull request titles or descriptions
+   - Code comments (unless technically relevant)
+   - Co-authored-by tags
+   - Generated-with footers
+
+3. **Follow Conventions**: All code, commits, and PRs must follow the patterns documented in AGENTS.md:
+   - Compilation requirements for all platforms (iOS, macOS, tvOS, watchOS, visionOS)
+   - Testing requirements before commits and PRs
+   - Documentation standards
+   - GitHub workflow naming conventions
+   - File filter configuration patterns
+   - Concurrency strategies for CI workflows
+
+## Quick Reference
+
+- Use `make help` to discover available commands
+- Format code: `make format`
+- Run static analysis: `make analyze`
+- Run unit tests: `make run-test-server && make test`
+- Run important UI tests: `make test-ui-critical`
+- Build XCFramework deliverables: `make build-xcframework`
+- Lint pod deliverable: `make pod-lint`
+- Follow file structure and naming conventions in AGENTS.md
+- Create focused, atomic commits with clear messages
PATCH

echo "Gold patch applied."
