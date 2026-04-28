#!/usr/bin/env bash
set -euo pipefail

cd /workspace/peloton-to-garmin

# Idempotency guard
if grep -qF "description: Starts work on an existing GitHub issue by fetching its details, cr" ".claude/skills/working-issue/SKILL.md" && grep -qF ".cursor/rules/api-development-patterns.mdc" ".cursor/rules/api-development-patterns.mdc" && grep -qF ".cursor/rules/configuration-patterns.mdc" ".cursor/rules/configuration-patterns.mdc" && grep -qF ".cursor/rules/development-workflow.mdc" ".cursor/rules/development-workflow.mdc" && grep -qF ".cursor/rules/documentation-guide.mdc" ".cursor/rules/documentation-guide.mdc" && grep -qF ".cursor/rules/knowledge-base-maintenance.mdc" ".cursor/rules/knowledge-base-maintenance.mdc" && grep -qF ".cursor/rules/knowledge-base-reference.mdc" ".cursor/rules/knowledge-base-reference.mdc" && grep -qF ".cursor/rules/project-overview.mdc" ".cursor/rules/project-overview.mdc" && grep -qF ".cursor/rules/sync-service-patterns.mdc" ".cursor/rules/sync-service-patterns.mdc" && grep -qF ".cursor/rules/testing-requirements.mdc" ".cursor/rules/testing-requirements.mdc" && grep -qF ".cursor/rules/ui-development.mdc" ".cursor/rules/ui-development.mdc" && grep -qF "Refer to `.ai/knowledge-base/03-development-setup.md` for setup instructions and" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/working-issue/SKILL.md b/.claude/skills/working-issue/SKILL.md
@@ -0,0 +1,184 @@
+---
+name: working-issue
+description: Starts work on an existing GitHub issue by fetching its details, creating the correct branch, writing the spec file, committing, and pushing — leaving the project in a ready-to-implement state. Use this skill whenever the user says "work on issue", "start issue", "pick up issue", "implement issue", or provides an issue number and implies they want to begin working on it. Always use this skill when the intent is to begin development on a tracked GitHub issue.
+---
+
+# Working a GitHub Issue
+
+When the user wants to start work on an issue, execute the full setup sequence before writing any implementation code.
+
+## Step 1: Fetch the issue
+
+```bash
+gh issue view <number> --json number,title,body,labels
+```
+
+Read the issue fully — understand the problem statement, acceptance criteria, and any blocking relationships. If the issue is marked as blocked by another open issue, flag this to the user before continuing.
+
+## Step 2: Create and push the branch
+
+```bash
+git checkout master
+git pull origin master
+git checkout -b issue<number>-<short-description>
+git push -u origin issue<number>-<short-description>
+```
+
+Derive the short description from the issue title — lowercase, hyphen-separated, 3–5 words.
+
+## Step 3 (optional): Agent-team mode — spawn spec-agent
+
+If the issue is complex (multiple subsystems, long spec, or the user has requested agent-team mode), delegate spec writing to `spec-agent` rather than writing it inline:
+
+```
+Use the spec-agent to write the spec for issue #<number>.
+```
+
+`spec-agent` will:
+1. Fetch the issue and read the codebase
+2. Write the spec file to `docs/specs/`
+3. Return a structured summary of ACs for your review
+
+Review the returned ACs. Once approved, commit the spec file and continue to Step 4. If agent-team mode is not needed, skip this step and write the spec inline below.
+
+---
+
+## Step 3: Write or update the spec file
+
+Specs live in `docs/specs/` and are **per feature or capability**, not per issue. A single spec may cover multiple issues as the feature evolves over time.
+
+**Before creating a new file**, scan `docs/specs/` for an existing spec that covers the same feature area. If one exists, add a new `## Capability: <short title>` section to it rather than creating a new file.
+
+If no suitable spec exists, create `docs/specs/<feature-area>.md` — named after the capability, not the issue number:
+
+```markdown
+# Spec: <Feature / Capability Name>
+
+**Status:** In Progress
+
+## Overview
+<Brief description of the feature area and its purpose>
+
+---
+
+## Capability: <Short Title>
+
+**Issue:** #<number> | **Status:** Draft
+
+### Problem
+<Extract or summarise from the issue's Problem Statement / Motivation>
+
+### Acceptance Criteria
+<Convert each AC from the issue checklist into a testable checkbox here>
+- [ ]
+
+### Notes
+<Any relevant context, constraints, or open questions from the issue body>
+```
+
+When adding a capability section to an existing spec, use the same `## Capability:` structure. Mark completed capabilities with `**Status:** Implemented` and check off their ACs.
+
+Populate from the issue content — do not leave sections empty.
+
+## Step 4: Commit and push the spec
+
+```bash
+git add docs/specs/<spec-file>.md
+git commit -m "[<number>] write spec"
+git push
+```
+
+## Step 5: Write the implementation plan
+
+Create `tmp/plan.md` with:
+- What needs to be built or changed
+- Key files or packages involved
+- Order of operations
+- Any decisions or trade-offs worth noting upfront
+
+```bash
+git add tmp/plan.md
+git commit -m "[<number>] implementation plan"
+git push
+```
+
+## Step 6: Validate before every commit
+
+Before committing any code changes (not docs-only commits), always run:
+
+```bash
+dotnet workload restore
+dotnet restore
+dotnet build --no-restore --configuration Debug
+dotnet test
+```
+
+All steps must pass cleanly. Fix any failures before committing — do not rely on CI to catch these.
+
+## Step 7: Implement the change
+
+The project is now ready for implementation. After implementing, open a PR.
+
+---
+
+## Opening the PR
+
+When the user asks to open the PR:
+
+1. (Optional agent-team mode) Run `reviewer-agent` as a pre-PR quality gate before opening:
+   ```
+   Use reviewer-agent to review the branch against the spec before I open the PR.
+   ```
+   Address any **must fix** items before proceeding. Suggestions are optional.
+
+2. Delete `tmp/` and commit:
+   ```bash
+   git rm -r tmp/
+   git commit -m "[<number>] remove tmp/ before merge"
+   git push
+   ```
+
+3. Open the PR:
+   ```bash
+   gh pr create --title "[<number>] <short description>" --body-file tmp/pr-body.md
+   ```
+   - PR title format: `[<number>] <short description>` matching the project's commit style
+   - Body should include a summary, list of changes, test plan, and `Closes #<number>`
+   - Write the body to a temp file, then clean it up after the `gh pr create` call
+
+---
+
+## After the PR is Open
+
+### Step 1: Monitor CI
+
+```bash
+gh pr checks <pr-number> --watch
+```
+
+If any check fails, investigate and fix:
+```bash
+gh run view <run-id> --log-failed
+```
+
+Push fixes and re-verify until all checks pass.
+
+### Step 2: Wait for code review
+
+Once CI passes, wait for any automated or human review to complete before proceeding.
+
+```bash
+gh pr view <pr-number> --comments
+```
+
+### Step 3: Address review feedback
+
+Read the review carefully. For each piece of feedback:
+- If the concern is valid: make the fix, commit, and push
+- If the concern is a false positive or intentional: leave a reply explaining why no change was made
+
+After addressing feedback, re-check that CI still passes.
+
+### Step 4: Mark ready
+
+Once CI is green and all review feedback is addressed, tell the user the PR is ready to merge.
diff --git a/.cursor/rules/api-development-patterns.mdc b/.cursor/rules/api-development-patterns.mdc
@@ -1,63 +0,0 @@
----
-description: When working with API controllers
-alwaysApply: false
----
-# API Development Patterns
-
-## REST API Development Guidelines
-
-When working with API controllers, follow the established patterns documented in the knowledge base:
-
-### API Structure (from [.ai/knowledge-base/02-api-reference.md](mdc:.ai/knowledge-base/02-api-reference.md)):
-- **Base URL**: `http://localhost:8080` (configurable via `Api.HostUrl`)
-- **Content-Type**: `application/json`
-- **No Authentication**: Currently for local deployment only
-
-### Existing Controllers:
-- **SyncController** (`/api/sync`) - Workout synchronization operations
-- **SettingsController** (`/api/settings`) - Application configuration
-- **SystemInfoController** (`/api/systeminfo`) - System information
-- **GarminAuthenticationController** (`/api/garmin/auth`) - Garmin authentication
-- **PelotonWorkoutsController** (`/api/peloton/workouts`) - Peloton workout data
-- **PelotonAnnualChallengeController** (`/api/peloton/challenges`) - Challenge data
-
-### Response Patterns:
-```csharp
-// Success response
-return Ok(new { isSuccess = true, data = result });
-
-// Error response
-return BadRequest(new { 
-    error = new { 
-        code = "VALIDATION_ERROR", 
-        message = "Error description",
-        details = new[] { "Specific error details" }
-    }
-});
-```
-
-### HTTP Status Code Usage:
-- **200 OK** - Successful operation
-- **400 Bad Request** - Invalid request parameters
-- **401 Unauthorized** - Authentication required
-- **404 Not Found** - Resource not found
-- **500 Internal Server Error** - Server error
-
-### Validation Patterns:
-- Use model validation attributes
-- Return specific error messages
-- Validate business rules in service layer
-- Use `ServiceResult<T>` pattern for service responses
-
-### Dependency Injection:
-- Inject services through constructor
-- Use interfaces for testability
-- Follow established service registration patterns in [src/ConsoleClient/Program.cs](mdc:src/ConsoleClient/Program.cs)
-
-### Testing Considerations:
-- Create integration tests for new endpoints
-- Mock external dependencies
-- Test error scenarios and edge cases
-- Verify response schemas match documentation
-
-Ensure API changes are documented in [.ai/knowledge-base/02-api-reference.md](mdc:.ai/knowledge-base/02-api-reference.md).
\ No newline at end of file
diff --git a/.cursor/rules/configuration-patterns.mdc b/.cursor/rules/configuration-patterns.mdc
@@ -1,77 +0,0 @@
----
-description: When working with configuration and settings
-alwaysApply: false
----
-# Configuration Management Patterns
-
-## Configuration System Guidelines
-
-Follow the configuration patterns established in the knowledge base when working with settings:
-
-### Configuration Files:
-- **Example**: [configuration.example.json](mdc:configuration.example.json) - Template configuration
-- **Local**: `configuration.local.json` - Local development settings (gitignored)
-- **Loading Logic**: [src/Common/Configuration.cs](mdc:src/Common/Configuration.cs)
-
-### Configuration Hierarchy (Priority Order):
-1. **Command line arguments** - Highest priority
-2. **Environment variables** (prefix: `P2G_`) - Override config file
-3. **Configuration files** (`configuration.local.json`) - File-based settings
-4. **Default values** - Fallback values
-
-### Environment Variable Format:
-```bash
-# Correct format (double underscore for nested properties)
-P2G_Peloton__Email=user@example.com
-P2G_Peloton__Password=password123
-P2G_Garmin__Upload=true
-
-# Incorrect format
-P2G_PELOTON_EMAIL=user@example.com  # Wrong separator
-```
-
-### Configuration Sections:
-- **App**: Application behavior settings
-- **Format**: Output format preferences (FIT, TCX, JSON)
-- **Peloton**: Peloton API credentials and settings
-- **Garmin**: Garmin Connect credentials and settings
-- **Observability**: Logging, metrics, and tracing
-
-### Security Considerations:
-- **Never commit credentials** to version control
-- **Use environment variables** for sensitive data in production
-- **Encrypt stored credentials** using platform-specific secure storage
-- **Validate configuration** on application startup
-
-### Settings Service Pattern:
-```csharp
-// Inject settings service
-public class MyService
-{
-    private readonly ISettingsService _settingsService;
-    
-    public MyService(ISettingsService settingsService)
-    {
-        _settingsService = settingsService;
-    }
-    
-    public async Task DoWorkAsync()
-    {
-        var settings = await _settingsService.GetSettingsAsync();
-        // Use settings...
-    }
-}
-```
-
-### Configuration Validation:
-- Validate required settings on startup
-- Provide clear error messages for missing configuration
-- Use data annotations for validation where appropriate
-- Test configuration loading in unit tests
-
-### Development vs Production:
-- **Development**: Use `configuration.local.json` with test accounts
-- **Production**: Use environment variables or secure configuration providers
-- **Docker**: Mount configuration files or use environment variables
-
-Refer to [.ai/knowledge-base/03-development-setup.md](mdc:.ai/knowledge-base/03-development-setup.md) for setup instructions and [.ai/knowledge-base/04-troubleshooting-guide.md](mdc:.ai/knowledge-base/04-troubleshooting-guide.md) for configuration issues.
\ No newline at end of file
diff --git a/.cursor/rules/development-workflow.mdc b/.cursor/rules/development-workflow.mdc
@@ -1,36 +0,0 @@
----
-alwaysApply: true
----
-
-You are a Senior .NET Software Arhitect who follows a specific workflow and guiding principles.
-
-**Workflow:**
-1. Research your [knowledge base](mdc:./cursor/rules/knowledge-base-reference.mdc) for relevant information.
-2. Plan your changes
-    1. Document a clear and concise step by step plan to accomplish your goal
-3. Follow Test Driven Development to Implement your changes
-    1. First establish any needed interface changes, create tests to assert behavior against those interfaces, then modify the implementations until the assertions are met. 
-4. Verify the code compiles and all tests pass
-    1. dotnet workload restore
-    2. dotnet restore
-    3. dotnet build --no-restore --configuration Debug
-    4. dotnet test
-5. Update user documentation in [mkdocs/](mdc:mkdocs/)
-6. Update your personal [knowledge base](mdc:./cursor/rules/knowledge-base-maintenance.mdc) 
-7. Update [vNextReleaseNotes.md](mdc:vNextReleaseNotes.md) and [Constant.cs](mdc:src/Common/Constants.cs) Version information if needed
-
-**Testing**:
-Follow the guidelines in [testing-requirements.mdc](mdc:./cursor/testing-requirements.mdc)
-
-**Guiding Principles:**
-1. Follow Test Driven Development
-2. Follow software design best practices
-3. Follow SOLID, DRY, and KISS
-4. Changes should always be backwards compatible
-5. Keep your changes focused, and isolated.
-6. Minimize unnecessary additions and refactors.
-
-**Don'ts**
-- ❌ Don't ignore compile errors
-- ❌ Don't ignore test failures
-- ❌ Don't ignore flakey tests
\ No newline at end of file
diff --git a/.cursor/rules/documentation-guide.mdc b/.cursor/rules/documentation-guide.mdc
@@ -1,41 +0,0 @@
----
-description: When you need to make updates to documentation to reflect changes to the application.
-alwaysApply: false
----
-# Documentation Guide
-
-## Documentation Structure:
-- **MkDocs Site**: [mkdocs/mkdocs.yml](mdc:mkdocs/mkdocs.yml) - Main documentation configuration
-- **Homepage**: [mkdocs/docs/index.md](mdc:mkdocs/docs/index.md) - Project overview and quick start
-- **Features**: [mkdocs/docs/features.md](mdc:mkdocs/docs/features.md) - Detailed feature descriptions
-- **Installation**: [mkdocs/docs/install/](mdc:mkdocs/docs/install/) - Various installation methods
-- **Configuration**: [mkdocs/docs/configuration/](mdc:mkdocs/docs/configuration/) - Settings and options
-- **Help**: [mkdocs/docs/help.md](mdc:mkdocs/docs/help.md) - Troubleshooting and support
-
-## Key Documentation Sections:
-- **Installation Options**: Docker, Windows App, Source, GitHub Actions
-- **Configuration**: App settings, format options, Peloton/Garmin credentials
-- **Migration Guides**: Version upgrade instructions
-- **FAQ**: Common questions and solutions
-- **Contributing**: Development guidelines and setup
-
-## Documentation Features:
-- **Material Theme**: Modern, responsive design
-- **Version Management**: Using Mike for versioned docs
-- **Search**: Full-text search across all pages
-- **Navigation**: Tabbed navigation and breadcrumbs
-- **Code Annotations**: Syntax highlighting and copy functionality
-
-## Contributing to Docs:
-- Use Markdown format with MkDocs extensions
-- Include screenshots and examples
-- Keep installation steps clear and sequential
-- Update configuration examples when adding new features
-- Test documentation changes locally with `mkdocs serve`
-
-## Documentation Workflow:
-1. Edit markdown files in [mkdocs/docs/](mdc:mkdocs/docs/)
-2. Test locally with `mkdocs serve`
-3. Build with `mkdocs build`
-
-IMPORTANT: NEVER DEPLOY DOCUMENTATION!
diff --git a/.cursor/rules/knowledge-base-maintenance.mdc b/.cursor/rules/knowledge-base-maintenance.mdc
@@ -1,55 +0,0 @@
----
-alwaysApply: true
----
-
-# Knowledge Base Maintenance Rule
-
-## Update Knowledge Base After Code Changes
-
-After making ANY changes to the P2G codebase, you MUST verify and update the knowledge base for accuracy.
-
-### Check These Documents for Impact:
-
-#### For Architecture Changes:
-- Update [.ai/knowledge-base/01-system-architecture.md](mdc:.ai/knowledge-base/01-system-architecture.md)
-- Verify component interactions and data flow diagrams
-- Update deployment model information if needed
-
-#### For API Changes:
-- Update [.ai/knowledge-base/02-api-reference.md](mdc:.ai/knowledge-base/02-api-reference.md)
-- Add new endpoints or modify existing ones
-- Update request/response schemas and examples
-
-#### For Configuration Changes:
-- Update [.ai/knowledge-base/03-development-setup.md](mdc:.ai/knowledge-base/03-development-setup.md)
-- Verify setup instructions remain accurate
-- Update configuration examples
-
-#### For New Issues/Solutions:
-- Update [.ai/knowledge-base/04-troubleshooting-guide.md](mdc:.ai/knowledge-base/04-troubleshooting-guide.md)
-- Add new troubleshooting scenarios
-- Update diagnostic procedures
-
-#### For External API Changes:
-- Update [.ai/knowledge-base/05-external-api-integration.md](mdc:.ai/knowledge-base/05-external-api-integration.md)
-- Modify authentication flows or endpoint documentation
-- Update rate limiting or error handling information
-
-#### For Testing Changes:
-- Update [.ai/knowledge-base/06-testing-strategy.md](mdc:.ai/knowledge-base/06-testing-strategy.md)
-- Add new testing patterns or frameworks
-- Update test data management strategies
-
-### Maintenance Checklist:
-1. **Identify Impact**: Determine which knowledge base sections are affected
-2. **Update Content**: Modify relevant documentation sections
-3. **Verify Examples**: Ensure code examples still work
-4. **Check Cross-References**: Update links between documents
-5. **Update Overview**: Modify [.ai/knowledge-base/README.md](mdc:.ai/knowledge-base/README.md) if structure changes
-
-### Common Update Scenarios:
-- **New Features**: Document in architecture and API reference
-- **Bug Fixes**: Add to troubleshooting guide
-- **Dependencies**: Update development setup
-- **Performance**: Update optimization guides
-- **Security**: Update security considerations
diff --git a/.cursor/rules/knowledge-base-reference.mdc b/.cursor/rules/knowledge-base-reference.mdc
@@ -1,31 +0,0 @@
----
-alwaysApply: true
----
-
-# Knowledge Base Reference Rule
-
-## Always Consult Knowledge Base Before Making Changes
-
-Before implementing any changes to the P2G codebase, you MUST reference the comprehensive knowledge base located in [.ai/knowledge-base/README.md](mdc:.ai/knowledge-base/README.md).
-
-### Knowledge Base Structure:
-- **System Architecture**: [.ai/knowledge-base/01-system-architecture.md](mdc:.ai/knowledge-base/01-system-architecture.md)
-- **API Reference**: [.ai/knowledge-base/02-api-reference.md](mdc:.ai/knowledge-base/02-api-reference.md)
-- **Development Setup**: [.ai/knowledge-base/03-development-setup.md](mdc:.ai/knowledge-base/03-development-setup.md)
-- **Troubleshooting**: [.ai/knowledge-base/04-troubleshooting-guide.md](mdc:.ai/knowledge-base/04-troubleshooting-guide.md)
-- **External APIs**: [.ai/knowledge-base/05-external-api-integration.md](mdc:.ai/knowledge-base/05-external-api-integration.md)
-- **Testing Strategy**: [.ai/knowledge-base/06-testing-strategy.md](mdc:.ai/knowledge-base/06-testing-strategy.md)
-
-### When Planning Changes:
-1. **Check Architecture**: Review system architecture to understand component interactions
-2. **Verify API Impact**: Check if changes affect REST API endpoints or external API integrations
-3. **Follow Patterns**: Use established development patterns and conventions
-4. **Consider Testing**: Plan appropriate test coverage using the testing strategy
-5. **Check Dependencies**: Understand how changes might affect other components
-
-### Key Project Context:
-- **.NET 9.0** application with multiple deployment models
-- **External APIs**: Peloton API and Garmin Connect integration
-- **Core Components**: ConsoleClient, WebUI, API, ClientUI, Sync Service
-- **File Formats**: FIT, TCX, JSON conversion capabilities
-- **Authentication**: Complex OAuth flows for both Peloton and Garmin
\ No newline at end of file
diff --git a/.cursor/rules/project-overview.mdc b/.cursor/rules/project-overview.mdc
@@ -1,33 +0,0 @@
----
-alwaysApply: true
----
-
-# Peloton to Garmin (P2G) Project Overview
-
-This is a .NET 9.0 application that syncs Peloton workout data to Garmin Connect. The project converts Peloton workouts to FIT/TCX/JSON formats and uploads them to Garmin Connect.
-
-## Key Components:
-- **API** (`src/Api/`): REST API for programmatic access
-- **WebUI** (`src/WebUI/`): Blazor-based web interface  
-- **ClientUI** (`src/ClientUI/`): MAUI-based desktop application
-- **ConsoleClient** (`src/ConsoleClient/`): Headless console application
-- **Sync Service** (`src/Sync/`): Core synchronization logic
-- **Conversion** (`src/Conversion/`): Format converters (FIT, TCX, JSON)
-- **Peloton Integration** (`src/Peloton/`): Peloton API client
-- **Garmin Integration** (`src/Garmin/`): Garmin Connect uploader
-- **Common** (`src/Common/`): Shared utilities and DTOs
-
-## Main Entry Points:
-- [src/ConsoleClient/Program.cs](mdc:src/ConsoleClient/Program.cs) - Console application entry
-- [src/WebUI/Program.cs](mdc:src/WebUI/Program.cs) - Web UI entry
-- [src/Api/Program.cs](mdc:src/Api/Program.cs) - API entry
-- [src/ClientUI/MauiProgram.cs](mdc:src/ClientUI/MauiProgram.cs) - MAUI app entry
-
-## Configuration:
-- [configuration.example.json](mdc:configuration.example.json) - Example configuration
-- [src/Common/Configuration.cs](mdc:src/Common/Configuration.cs) - Configuration loading logic
-
-## Core Sync Logic:
-- [src/Sync/SyncService.cs](mdc:src/Sync/SyncService.cs) - Main synchronization service
-- [src/Conversion/IConverter.cs](mdc:src/Conversion/IConverter.cs) - Format conversion interface
-# Peloton to Garmin (P2G) Project Overview
diff --git a/.cursor/rules/sync-service-patterns.mdc b/.cursor/rules/sync-service-patterns.mdc
@@ -1,47 +0,0 @@
----
-description: When modifying sync-related components
-alwaysApply: false
----
-# Sync Service Development Patterns
-
-## Core Sync Components
-
-When modifying sync-related components, follow these established patterns from the knowledge base:
-
-### Key Files and Patterns:
-- **Main Sync Logic**: [src/Sync/SyncService.cs](mdc:src/Sync/SyncService.cs)
-- **Peloton Integration**: [src/Peloton/ApiClient.cs](mdc:src/Peloton/ApiClient.cs)
-- **Garmin Integration**: [src/Garmin/ApiClient.cs](mdc:src/Garmin/ApiClient.cs)
-
-### Sync Workflow (from [.ai/knowledge-base/01-system-architecture.md](mdc:.ai/knowledge-base/01-system-architecture.md)):
-1. **Authentication** - Both Peloton and Garmin APIs
-2. **Fetch Workouts** - From Peloton API
-3. **Filter Workouts** - Apply user-configured filters
-4. **Stack Workouts** - Combine back-to-back workouts if enabled
-5. **Convert Formats** - To FIT, TCX, or JSON
-6. **Upload to Garmin** - Upload converted files
-
-### Error Handling Patterns:
-- Use `ServiceResult<T>` for operation results
-- Return `ConvertStatus` for conversion operations
-- Handle authentication errors separately (Peloton/Garmin)
-- Log exceptions with context using Serilog
-
-### Authentication Considerations:
-- **Peloton**: Session-based authentication with automatic renewal
-- **Garmin**: OAuth 1.0a + OAuth 2.0 hybrid flow with MFA support
-- Store credentials encrypted using platform-specific secure storage
-
-### Testing Requirements:
-- Mock external API dependencies
-- Test authentication failure scenarios
-- Verify workout filtering and stacking logic
-- Test conversion error handling
-
-### Performance Considerations:
-- Implement rate limiting for API calls
-- Use exponential backoff for transient failures
-- Process workouts in batches when possible
-- Clean up temporary files after processing
-
-Refer to [.ai/knowledge-base/05-external-api-integration.md](mdc:.ai/knowledge-base/05-external-api-integration.md) for detailed API integration patterns.
diff --git a/.cursor/rules/testing-requirements.mdc b/.cursor/rules/testing-requirements.mdc
@@ -1,65 +0,0 @@
----
-description: When adding, modifying, or planning tests
-alwaysApply: false
----
-# Testing Requirements
-
-Follow these testing guidelines when adding or modifying tests.
-
-**Location**: `src/UnitTests/`
-
-## Testing Framework Stack:
-- **NUnit** - Primary testing framework
-- **Moq** - Mocking framework
-- **FluentAssertions** - Assertion library
-- **Bogus** - Test Data generator
-
-## Example Tests
-
-- Using AutoMock to mock dependencies: [SyncServiceTests.cs](mdc:src\UnitTests\Sync\SyncServiceTests.cs)
-- Using Bogus to setup test data: [StackedWorkoutsCalculatorTests.cs](mdc:src\UnitTests\Sync\StackedWorkoutsCalculatorTests.cs)
-
-### Mocking Guidelines:
-- Mock external dependencies (Peloton/Garmin APIs)
-- Use interfaces for testability
-- Verify mock interactions
-- Test both success and failure scenarios
-
-### Running Tests:
-```bash
-# Run all tests
-dotnet test
-
-# Run specific test class
-dotnet test --filter "FullyQualifiedName~SyncServiceTests"
-
-# With Coverage
-dotnet test --collect:"XPlat Code Coverage"
-```
-
-## Test Maintenance
-
-### Regular Tasks
-1. **Update Test Data**: Keep sample data current
-2. **Review Coverage**: Maintain >80% code coverage
-3. **Remove Obsolete Tests**: Clean up unused tests
-4. **Update Dependencies**: Keep test frameworks updated
-
-
-## Best Practices
-
-### Do's
-- ✅ Write tests before fixing bugs
-- ✅ Test edge cases and error conditions
-- ✅ Use descriptive test names
-- ✅ Keep tests independent and isolated
-- ✅ Mock external dependencies
-- ✅ Use test data builders for complex objects
-
-### Don'ts
-- ❌ Don't test implementation details
-- ❌ Don't write tests that depend on external services
-- ❌ Don't ignore flaky tests
-- ❌ Don't test multiple concerns in one test
-- ❌ Don't use production data in tests
-- ❌ Don't skip tests without good reason
\ No newline at end of file
diff --git a/.cursor/rules/ui-development.mdc b/.cursor/rules/ui-development.mdc
@@ -1,36 +0,0 @@
----
-description: When making changes to the UI or UX
-alwaysApply: false
----
-# UI Development Patterns for P2G
-
-## Blazor WebUI:
-- **Entry**: [src/WebUI/Program.cs](mdc:src/WebUI/Program.cs)
-- **Shared Components**: [src/SharedUI/](mdc:src/SharedUI/) - Reusable Blazor components
-- **Pages**: [src/SharedUI/Pages/](mdc:src/SharedUI/Pages/) - Main application pages
-- **API Client**: [src/WebUI/ApiClient.cs](mdc:src/WebUI/ApiClient.cs) - Communicates with API
-
-## MAUI ClientUI:
-- **Entry**: [src/ClientUI/MauiProgram.cs](mdc:src/ClientUI/MauiProgram.cs)
-- **Main App**: [src/ClientUI/Main.razor](mdc:src/ClientUI/Main.razor) - Uses shared Blazor components
-- **Platforms**: Android, iOS, macOS, Windows, Tizen
-- **Service Client**: [src/ClientUI/Platforms/](mdc:src/ClientUI/Platforms/) - Platform-specific implementations
-
-## Shared UI Components:
-- **Layout**: [src/SharedUI/Shared/MainLayout.razor](mdc:src/SharedUI/Shared/MainLayout.razor)
-- **Forms**: [src/SharedUI/Shared/AppSettingsForm.razor](mdc:src/SharedUI/Shared/AppSettingsForm.razor)
-- **Logs**: [src/SharedUI/Shared/ApiLogs.razor](mdc:src/SharedUI/Shared/ApiLogs.razor)
-
-## UI Patterns:
-- Use dependency injection for services
-- Shared components between WebUI and ClientUI
-- Bootstrap for styling and responsive design
-- Real-time updates via API polling
-- Error handling with user-friendly messages
-
-## Key Features:
-- Configuration management
-- Real-time sync status
-- Log viewing and filtering
-- Workout progress tracking
-- Annual challenge progress display
\ No newline at end of file
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,424 @@
+# Peloton to Garmin (P2G) — Claude Code Instructions
+
+## Project Overview
+
+.NET 9.0 application that syncs Peloton workout data to Garmin Connect, converting workouts to FIT/TCX/JSON formats.
+
+### Key Components
+- **API** (`src/Api/`) — REST API for programmatic access
+- **WebUI** (`src/WebUI/`) — Blazor-based web interface
+- **ClientUI** (`src/ClientUI/`) — MAUI-based desktop application
+- **ConsoleClient** (`src/ConsoleClient/`) — Headless console application
+- **Sync Service** (`src/Sync/`) — Core synchronization logic
+- **Conversion** (`src/Conversion/`) — Format converters (FIT, TCX, JSON)
+- **Peloton Integration** (`src/Peloton/`) — Peloton API client
+- **Garmin Integration** (`src/Garmin/`) — Garmin Connect uploader
+- **Common** (`src/Common/`) — Shared utilities and DTOs
+
+### Main Entry Points
+- `src/ConsoleClient/Program.cs` — Console application
+- `src/WebUI/Program.cs` — Web UI
+- `src/Api/Program.cs` — API
+- `src/ClientUI/MauiProgram.cs` — MAUI app
+
+### Configuration Files
+- `configuration.example.json` — Template configuration
+- `src/Common/Configuration.cs` — Configuration loading logic
+
+### Core Sync Logic
+- `src/Sync/SyncService.cs` — Main synchronization service
+- `src/Conversion/IConverter.cs` — Format conversion interface
+
+---
+
+## Development Workflow
+
+When working a GitHub issue end-to-end (branch → spec → implement → PR), use the `/working-issue` skill.
+
+For all changes:
+
+1. **Research** — Consult the knowledge base in `.ai/knowledge-base/` for relevant context
+2. **Plan** — Document a clear, concise step-by-step plan before writing code
+3. **TDD** — First establish interface changes, write tests asserting behavior, then implement until tests pass
+4. **Verify** — Build and all tests must pass before committing (see `/working-issue` for the full validation sequence)
+5. **Docs** — Update user documentation in `mkdocs/`
+6. **Knowledge Base** — Update `.ai/knowledge-base/` to reflect changes
+7. **Release Notes** — Update `vNextReleaseNotes.md` and version in `src/Common/Constants.cs` if needed
+
+### Guiding Principles
+- Follow Test Driven Development
+- Follow SOLID, DRY, and KISS
+- Changes must be backwards compatible
+- Keep changes focused and isolated
+- Minimize unnecessary additions and refactors
+
+### Don'ts
+- Never ignore compile errors
+- Never ignore test failures
+- Never ignore flaky tests
+
+---
+
+## Knowledge Base
+
+### Before Making Changes
+Always consult the knowledge base before implementing changes:
+
+- **System Architecture**: `.ai/knowledge-base/01-system-architecture.md`
+- **API Reference**: `.ai/knowledge-base/02-api-reference.md`
+- **Development Setup**: `.ai/knowledge-base/03-development-setup.md`
+- **Troubleshooting**: `.ai/knowledge-base/04-troubleshooting-guide.md`
+- **External APIs**: `.ai/knowledge-base/05-external-api-integration.md`
+- **Testing Strategy**: `.ai/knowledge-base/06-testing-strategy.md`
+
+### When Planning Changes
+1. **Check Architecture** — Review system architecture to understand component interactions
+2. **Verify API Impact** — Check if changes affect REST API endpoints or external API integrations
+3. **Follow Patterns** — Use established development patterns and conventions
+4. **Consider Testing** — Plan appropriate test coverage using the testing strategy
+5. **Check Dependencies** — Understand how changes might affect other components
+
+### Key Project Context
+- **.NET 9.0** application with multiple deployment models (Docker, Windows app, console, GitHub Actions)
+- **External APIs**: Peloton API and Garmin Connect integration
+- **Core Components**: ConsoleClient, WebUI, API, ClientUI, Sync Service
+- **File Formats**: FIT, TCX, JSON conversion capabilities
+- **Authentication**: Complex OAuth flows for both Peloton and Garmin
+
+### After Making Changes
+Update the relevant knowledge base documents after any code change:
+
+| Change Type | Update |
+|---|---|
+| Architecture | `01-system-architecture.md` — verify component interactions and data flow diagrams |
+| API endpoints | `02-api-reference.md` — add/modify endpoints, update request/response schemas |
+| Config/setup | `03-development-setup.md` — verify setup instructions, update configuration examples |
+| New issues/solutions | `04-troubleshooting-guide.md` — add troubleshooting scenarios, update diagnostic procedures |
+| External API flows | `05-external-api-integration.md` — update auth flows, rate limiting, error handling |
+| Test patterns | `06-testing-strategy.md` — add new patterns, update test data management strategies |
+
+### Maintenance Checklist
+1. **Identify Impact** — Determine which knowledge base sections are affected
+2. **Update Content** — Modify relevant documentation sections
+3. **Verify Examples** — Ensure code examples still work
+4. **Check Cross-References** — Update links between documents
+5. **Update Overview** — Modify `.ai/knowledge-base/README.md` if structure changes
+
+### Common Update Scenarios
+- **New Features** — Document in architecture and API reference
+- **Bug Fixes** — Add to troubleshooting guide
+- **Dependencies** — Update development setup
+- **Performance** — Update optimization guides
+- **Security** — Update security considerations
+
+---
+
+## Testing
+
+_Apply when adding, modifying, or planning tests._
+
+**Location**: `src/UnitTests/`
+
+### Framework Stack
+- **NUnit** — Primary testing framework
+- **Moq** — Mocking framework
+- **FluentAssertions** — Assertion library
+- **Bogus** — Test data generator
+
+### Example Tests
+- AutoMock usage: `src/UnitTests/Sync/SyncServiceTests.cs`
+- Bogus test data: `src/UnitTests/Sync/StackedWorkoutsCalculatorTests.cs`
+
+### Mocking Guidelines
+- Mock external dependencies (Peloton/Garmin APIs)
+- Use interfaces for testability
+- Verify mock interactions
+- Test both success and failure scenarios
+
+### Running Tests
+```bash
+# Run all tests
+dotnet test
+
+# Run specific test class
+dotnet test --filter "FullyQualifiedName~SyncServiceTests"
+
+# With coverage
+dotnet test --collect:"XPlat Code Coverage"
+```
+
+### Test Maintenance
+- Keep sample data current
+- Maintain >80% code coverage
+- Remove obsolete tests
+- Keep test frameworks updated
+
+### Do's
+- Write tests before fixing bugs
+- Test edge cases and error conditions
+- Use descriptive test names
+- Keep tests independent and isolated
+- Mock external dependencies
+- Use test data builders for complex objects
+
+### Don'ts
+- Don't test implementation details
+- Don't write tests that depend on external services
+- Don't ignore flaky tests
+- Don't test multiple concerns in one test
+- Don't use production data in tests
+- Don't skip tests without good reason
+
+---
+
+## API Development
+
+_Apply when working with API controllers._
+
+- **Base URL**: `http://localhost:8080` (configurable via `Api.HostUrl`)
+- **Content-Type**: `application/json`
+- **No Authentication**: Local deployment only
+
+### Existing Controllers
+- `SyncController` (`/api/sync`) — Workout synchronization operations
+- `SettingsController` (`/api/settings`) — Application configuration
+- `SystemInfoController` (`/api/systeminfo`) — System information
+- `GarminAuthenticationController` (`/api/garmin/auth`) — Garmin authentication
+- `PelotonWorkoutsController` (`/api/peloton/workouts`) — Peloton workout data
+- `PelotonAnnualChallengeController` (`/api/peloton/challenges`) — Challenge data
+
+### Response Patterns
+```csharp
+// Success
+return Ok(new { isSuccess = true, data = result });
+
+// Error
+return BadRequest(new { 
+    error = new { 
+        code = "VALIDATION_ERROR", 
+        message = "Error description",
+        details = new[] { "Specific error details" }
+    }
+});
+```
+
+### HTTP Status Codes
+- **200** — Successful operation
+- **400** — Invalid request parameters
+- **401** — Authentication required
+- **404** — Resource not found
+- **500** — Server error
+
+### Validation Patterns
+- Use model validation attributes
+- Return specific error messages
+- Validate business rules in the service layer
+- Use `ServiceResult<T>` pattern for service responses
+
+### Dependency Injection
+- Inject services through constructor
+- Use interfaces for testability
+- Follow established service registration patterns in `src/ConsoleClient/Program.cs`
+
+### Testing Considerations
+- Create integration tests for new endpoints
+- Mock external dependencies
+- Test error scenarios and edge cases
+- Verify response schemas match documentation
+
+Ensure API changes are documented in `.ai/knowledge-base/02-api-reference.md`.
+
+---
+
+## Configuration
+
+_Apply when working with configuration and settings._
+
+- **Example**: `configuration.example.json`
+- **Local**: `configuration.local.json` (gitignored)
+- **Loading Logic**: `src/Common/Configuration.cs`
+
+### Priority Order (highest to lowest)
+1. Command line arguments
+2. Environment variables (prefix: `P2G_`, double underscore for nesting)
+3. `configuration.local.json`
+4. Default values
+
+### Environment Variable Format
+```bash
+# Correct — double underscore for nested properties
+P2G_Peloton__Email=user@example.com
+P2G_Peloton__Password=password123
+P2G_Garmin__Upload=true
+
+# Incorrect — wrong separator
+P2G_PELOTON_EMAIL=user@example.com
+```
+
+### Configuration Sections
+- **App** — Application behavior
+- **Format** — Output format preferences (FIT, TCX, JSON)
+- **Peloton** — Peloton API credentials and settings
+- **Garmin** — Garmin Connect credentials and settings
+- **Observability** — Logging, metrics, and tracing
+
+### Settings Service Pattern
+```csharp
+public class MyService
+{
+    private readonly ISettingsService _settingsService;
+
+    public MyService(ISettingsService settingsService)
+    {
+        _settingsService = settingsService;
+    }
+
+    public async Task DoWorkAsync()
+    {
+        var settings = await _settingsService.GetSettingsAsync();
+        // Use settings...
+    }
+}
+```
+
+### Configuration Validation
+- Validate required settings on startup
+- Provide clear error messages for missing configuration
+- Use data annotations for validation where appropriate
+- Test configuration loading in unit tests
+
+### Security
+- Never commit credentials to version control
+- Use environment variables for sensitive data in production
+- Encrypt stored credentials using platform-specific secure storage
+- Validate configuration on application startup
+
+### Development vs Production
+- **Development**: Use `configuration.local.json` with test accounts
+- **Production**: Use environment variables or secure configuration providers
+- **Docker**: Mount configuration files or use environment variables
+
+Refer to `.ai/knowledge-base/03-development-setup.md` for setup instructions and `.ai/knowledge-base/04-troubleshooting-guide.md` for configuration issues.
+
+---
+
+## Sync Service
+
+_Apply when modifying sync-related components._
+
+### Key Files
+- `src/Sync/SyncService.cs` — Main sync logic
+- `src/Peloton/ApiClient.cs` — Peloton integration
+- `src/Garmin/ApiClient.cs` — Garmin integration
+
+### Sync Workflow
+1. Authentication (Peloton + Garmin)
+2. Fetch workouts from Peloton API
+3. Filter workouts per user config
+4. Stack back-to-back workouts (if enabled)
+5. Convert to FIT/TCX/JSON
+6. Upload to Garmin Connect
+
+### Error Handling
+- Use `ServiceResult<T>` for operation results
+- Use `ConvertStatus` for conversion operations
+- Handle Peloton/Garmin auth errors separately
+- Log exceptions with context using Serilog
+
+### Authentication
+- **Peloton**: Session-based with automatic renewal
+- **Garmin**: OAuth 1.0a + OAuth 2.0 hybrid with MFA support
+- Store credentials encrypted using platform-specific secure storage
+
+### Testing Requirements
+- Mock external API dependencies
+- Test authentication failure scenarios
+- Verify workout filtering and stacking logic
+- Test conversion error handling
+
+### Performance
+- Implement rate limiting for API calls
+- Use exponential backoff for transient failures
+- Process workouts in batches when possible
+- Clean up temporary files after processing
+
+Refer to `.ai/knowledge-base/05-external-api-integration.md` for detailed API integration patterns.
+
+---
+
+## UI Development
+
+_Apply when making changes to the UI or UX._
+
+### Blazor WebUI
+- Entry: `src/WebUI/Program.cs`
+- Shared components: `src/SharedUI/`
+- Pages: `src/SharedUI/Pages/`
+- API client: `src/WebUI/ApiClient.cs`
+
+### MAUI ClientUI
+- Entry: `src/ClientUI/MauiProgram.cs`
+- Main app: `src/ClientUI/Main.razor`
+- Platforms: Android, iOS, macOS, Windows, Tizen
+- Platform-specific implementations: `src/ClientUI/Platforms/`
+
+### Shared UI Components
+- Layout: `src/SharedUI/Shared/MainLayout.razor`
+- Forms: `src/SharedUI/Shared/AppSettingsForm.razor`
+- Logs: `src/SharedUI/Shared/ApiLogs.razor`
+
+### Patterns
+- Use dependency injection for services
+- Shared components between WebUI and ClientUI
+- Bootstrap for styling and responsive design
+- Real-time updates via API polling
+- Error handling with user-friendly messages
+
+### Key Features
+- Configuration management
+- Real-time sync status
+- Log viewing and filtering
+- Workout progress tracking
+- Annual challenge progress display
+
+---
+
+## Documentation
+
+_Apply when updating documentation to reflect application changes._
+
+### Structure
+- **MkDocs config**: `mkdocs/mkdocs.yml`
+- **Homepage**: `mkdocs/docs/index.md` — Project overview and quick start
+- **Features**: `mkdocs/docs/features.md` — Detailed feature descriptions
+- **Installation**: `mkdocs/docs/install/` — Docker, Windows App, Source, GitHub Actions
+- **Configuration**: `mkdocs/docs/configuration/` — Settings and options
+- **Help**: `mkdocs/docs/help.md` — Troubleshooting and support
+
+### Key Sections
+- **Installation Options**: Docker, Windows App, Source, GitHub Actions
+- **Configuration**: App settings, format options, Peloton/Garmin credentials
+- **Migration Guides**: Version upgrade instructions
+- **FAQ**: Common questions and solutions
+- **Contributing**: Development guidelines and setup
+
+### Features
+- Material Theme — modern, responsive design
+- Version management via Mike
+- Full-text search
+- Tabbed navigation and breadcrumbs
+- Syntax highlighting and code copy
+
+### Contributing to Docs
+- Use Markdown format with MkDocs extensions
+- Include screenshots and examples where helpful
+- Keep installation steps clear and sequential
+- Update configuration examples when adding new features
+- Test changes locally with `mkdocs serve`
+
+### Workflow
+1. Edit markdown files in `mkdocs/docs/`
+2. Test locally with `mkdocs serve`
+3. Build with `mkdocs build`
+
+**NEVER deploy documentation.**
PATCH

echo "Gold patch applied."
