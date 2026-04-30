#!/usr/bin/env bash
set -euo pipefail

cd /workspace/appsmith

# Idempotency guard
if grep -qF "- **No Trigger Happy**: Don't start write actions and long plans without confirm" ".cursor/rules/agent-behavior.mdc" && grep -qF "`controllers/`, `services/`, `domains/`, `repositories/`, `dtos/`, `configuratio" ".cursor/rules/backend.mdc" && grep -qF "PR titles must follow [Conventional Commits](https://www.conventionalcommits.org" ".cursor/rules/commit/semantic-pr-validator.mdc" && grep -qF ".cursor/rules/commit/semantic-pr.md" ".cursor/rules/commit/semantic-pr.md" && grep -qF "`pages/`, `widgets/`, `sagas/`, `reducers/`, `actions/`, `selectors/`, `componen" ".cursor/rules/frontend.mdc" && grep -qF ".cursor/rules/index.md" ".cursor/rules/index.md" && grep -qF "Enterprise and community edition code coexist in the same repo. Look for `ce/` a" ".cursor/rules/index.mdc" && grep -qF "Key scripts: `deploy_preview.sh`, `build_dp_from_branch.sh`, `cleanup_dp.sh`, `h" ".cursor/rules/infra.mdc" && grep -qF "- Minimize expensive properties in frequently repainted elements (box-shadow, bo" ".cursor/rules/quality/performance-optimizer.mdc" && grep -qF ".cursor/rules/quality/pre-commit-checks.mdc" ".cursor/rules/quality/pre-commit-checks.mdc" && grep -qF ".cursor/rules/task-list.mdc" ".cursor/rules/task-list.mdc" && grep -qF "description: Test conventions and examples for frontend (Jest/Cypress) and backe" ".cursor/rules/testing/test-generator.mdc" && grep -qF "description: Bug fix quality checklist \u2014 reproduction, root cause analysis, test" ".cursor/rules/verification/bug-fix-verifier.mdc" && grep -qF ".cursor/rules/verification/feature-implementation-validator.mdc" ".cursor/rules/verification/feature-implementation-validator.mdc" && grep -qF "description: Feature implementation checklist \u2014 requirements, code quality, test" ".cursor/rules/verification/feature-verifier.mdc" && grep -qF "- Using deprecated action versions (prefer `@v4` for checkout, setup-node, etc.)" ".cursor/rules/verification/workflow-validator.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/agent-behavior.mdc b/.cursor/rules/agent-behavior.mdc
@@ -0,0 +1,53 @@
+---
+description: Agent workflow orchestration, task management, and core principles for all interactions
+globs: 
+alwaysApply: true
+---
+
+# Agent Behavior
+
+## Workflow Orchestration
+### 1. Plan Node Default
+- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
+- If something goes sideways, STOP and re-plan immediately - don't keep pushing
+- Use plan mode for verification steps, not just building
+- Use subagents to build in plan mode when tasks are independent
+- Write detailed specs upfront to reduce ambiguity
+### 2. Subagent Strategy
+- Use subagents liberally to keep main context window clean
+- Offload research, exploration, and parallel analysis to subagents
+- For complex problems, throw more compute at it via subagents
+- One tack per subagent for focused execution
+### 3. Self-Improvement Loop
+- After ANY correction from the user: update `.cursor/lessons.md` with the pattern
+- Add the learning in `.claude/lessons.md` incrementally
+- Write rules for yourself that prevent the same mistake
+- Ruthlessly iterate on these lessons until mistake rate drops
+- Review lessons at session start for relevant project
+### 4. Verification Before Done
+- Never mark a task complete without proving it works
+- Diff behavior between main and your changes when relevant
+- Ask yourself: "Would a staff engineer approve this?"
+- Run tests, check logs, demonstrate correctness
+### 5. Demand Elegance (Balanced)
+- For non-trivial changes: pause and ask "is there a more elegant way?"
+- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
+- Skip this for simple, obvious fixes - don't over-engineer
+- Challenge your own work before presenting it
+### 6. Autonomous Bug Fixing
+- When given a bug report: just fix it. Don't ask for hand-holding
+- Point at logs, errors, failing tests - then resolve them
+- Zero context switching required from the user
+- Go fix failing CI tests without being told how
+## Task Management
+1. **Plan First**: Write plan to `.cursor/todo.md` with checkable items
+2. **Verify Plan**: Check in before starting implementation
+3. **Track Progress**: Mark items complete as you go
+4. **Explain Changes**: High-level summary at each step
+5. **Document Results**: Add review section to `.cursor/todo.md`
+6. **Capture Lessons**: Update `.cursor/lessons.md` after corrections
+## Core Principles
+- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
+- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
+- **No Trigger Happy**: Don't start write actions and long plans without confirming intent from user explicitly
+- **Minimat Impact**: Changes should only touch what's necessary. Avoid introducing bugs.
\ No newline at end of file
diff --git a/.cursor/rules/backend.mdc b/.cursor/rules/backend.mdc
@@ -0,0 +1,36 @@
+---
+description: Java backend — Spring Boot server, Maven modules, key packages, entry points, and build commands
+globs:
+alwaysApply: false
+---
+# Backend — `app/server/`
+
+- **Stack:** Java 17, Spring Boot 3.x (Reactive WebFlux), MongoDB
+- **Build:** Maven (`pom.xml`) — run with `mvn` or `./mvnw`
+- **Entry point:** `appsmith-server/src/main/java/com/appsmith/server/ServerApplication.java`
+
+## Maven Modules
+
+| Module | Purpose |
+|---|---|
+| `appsmith-server` | Core app — controllers, services, domains, repositories, migrations, Git, exports/imports |
+| `appsmith-interfaces` | Shared DTOs, models, constants, plugin interfaces (contract layer) |
+| `appsmith-plugins` | ~28 datasource plugins (Postgres, Mongo, MySQL, REST API, GraphQL, S3, Snowflake, Redis, Oracle, Google Sheets, OpenAI, Anthropic, etc.) |
+| `appsmith-git` | Git integration — file handlers, converters, services for app version control |
+| `appsmith-ai` | AI features module |
+| `reactive-caching` | Custom reactive caching library |
+
+## Key Packages
+
+`controllers/`, `services/`, `domains/`, `repositories/`, `dtos/`, `configurations/`, `git/`, `authentication/`, `exports/`, `imports/`, `workflows/`, `modules/`, `migrations/`
+
+## EE Pattern
+
+Community and enterprise code coexist. Look for `ce/` and `ee/` sub-packages within each module. Enterprise logic extends or overrides CE implementations.
+
+## Testing
+
+- **Framework:** JUnit
+- **Unit tests:** `**/*Test.java`
+- **Integration tests:** `**/*IntegrationTest.java`
+- **Style check:** Spotless (`./mvnw spotlessCheck`)
diff --git a/.cursor/rules/commit/semantic-pr-validator.mdc b/.cursor/rules/commit/semantic-pr-validator.mdc
@@ -1,174 +1,117 @@
 ---
-description: 
+description: Conventional Commits format for PR titles and structured PR descriptions
 globs: 
-alwaysApply: true
+alwaysApply: false
 ---
-# Semantic PR Validator
-
-```yaml
-name: Semantic PR Validator
-description: Validates that PR titles follow the Conventional Commits specification
-author: Cursor AI
-version: 1.0.0
-tags:
-  - git
-  - pull-request
-  - semantic
-  - conventional-commits
-activation:
-  always: true
-  event:
-    - pull_request
-    - pull_request_title_edit
-    - command
-triggers:
-  - pull_request.created
-  - pull_request.edited
-  - command: "validate_pr_title"
-```
+# Semantic PR Guidelines
+
+## Part 1: PR Title
+
+PR titles must follow [Conventional Commits](https://www.conventionalcommits.org/). Enforced by the `semantic-prs` GitHub app (config: `.github/semantic.yml`, `titleOnly: true` — only the PR title is validated, not individual commits).
+
+### Format
 
-## Rule Definition
-
-This rule ensures that pull request titles follow the [Conventional Commits](mdc:https:/www.conventionalcommits.org) specification.
-
-## Validation Logic
-
-```javascript
-// Function to validate PR titles against Conventional Commits spec
-function validatePRTitle(title) {
-  // Regular expression for conventional commits format
-  const conventionalCommitRegex = /^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9-_]+\))?(!)?: [a-z0-9].+$/i;
-  
-  if (!conventionalCommitRegex.test(title)) {
-    return {
-      valid: false,
-      errors: [
-        "PR title doesn't follow the Conventional Commits format: type(scope): description",
-        "Example valid titles:",
-        "- feat(widget): add new table component",
-        "- fix: resolve login issue",
-        "- docs(readme): update installation instructions"
-      ]
-    };
-  }
-  
-  // Check for empty scope in parentheses
-  if (title.includes('()')) {
-    return {
-      valid: false,
-      errors: [
-        "Empty scope provided. Either include a scope value or remove the parentheses."
-      ]
-    };
-  }
-  
-  // Extract parts
-  const match = title.match(/^([a-z]+)(?:\(([a-z0-9-_]+)\))?(!)?:/i);
-  
-  if (!match || !match[1]) {
-    return {
-      valid: false,
-      errors: [
-        "Failed to parse PR title format. Please follow the pattern: type(scope): description"
-      ]
-    };
-  }
-  
-  const type = match[1].toLowerCase();
-  
-  // Validate type
-  const validTypes = ["feat", "fix", "docs", "style", "refactor", 
-                      "perf", "test", "build", "ci", "chore", "revert"];
-  
-  if (!validTypes.includes(type)) {
-    return {
-      valid: false,
-      errors: [
-        `Invalid type "${type}". Valid types are: ${validTypes.join(', ')}`
-      ]
-    };
-  }
-  
-  return { valid: true };
-}
-
-// Triggered when a PR is created or the title is changed
-function onPRTitleChange(prTitle) {
-  const validation = validatePRTitle(prTitle);
-  
-  if (!validation.valid) {
-    return {
-      status: "failure",
-      message: "PR title doesn't follow Conventional Commits format",
-      details: validation.errors.join('\n'),
-      suggestions: [
-        {
-          label: "Fix PR title format",
-          description: "Update title to follow type(scope): description format"
-        }
-      ]
-    };
-  }
-  
-  return {
-    status: "success",
-    message: "PR title follows Conventional Commits format"
-  };
-}
-
-// Run on activation
-function activate(context) {
-  // Register event handlers
-  context.on('pull_request.created', (event) => {
-    const prTitle = event.pull_request.title;
-    return onPRTitleChange(prTitle);
-  });
-  
-  context.on('pull_request.edited', (event) => {
-    const prTitle = event.pull_request.title;
-    return onPRTitleChange(prTitle);
-  });
-  
-  context.registerCommand('validate_pr_title', (args) => {
-    const prTitle = args.title || context.currentPR?.title;
-    if (!prTitle) {
-      return {
-        status: "error",
-        message: "No PR title provided"
-      };
-    }
-    return onPRTitleChange(prTitle);
-  });
-}
-
-// Export the functions
-module.exports = {
-  activate,
-  onPRTitleChange,
-  validatePRTitle
-};
 ```
+type(scope): description
+```
+
+### Valid Types
 
-## When It Runs
+- `feat` — new feature
+- `fix` — bug fix
+- `docs` — documentation only
+- `style` — formatting, no logic change
+- `refactor` — neither fix nor feature
+- `perf` — performance improvement
+- `test` — adding or fixing tests
+- `build` — build process or dependencies
+- `ci` — CI configuration
+- `chore` — other non-source changes
+- `revert` — reverts a previous commit
 
-This rule automatically runs in the following scenarios:
-- When a new pull request is created
-- When a pull request title is edited
-- When a developer asks for validation via Cursor command: `validate_pr_title`
+### Scope
 
-## Usage Example
+Optional. Represents the area affected: `client`, `server`, `widgets`, `plugins`, `git`, `auth`, `api`, etc.
 
-To validate a PR title before submitting:
+### Title Description
 
-1. Create a branch and make your changes
-2. Prepare to create a PR
-3. Use the command: `validate_pr_title` in Cursor
-4. Cursor will check your title and suggest corrections if needed
+- Imperative mood: "add" not "added" or "adds"
+- Lowercase first letter
+- No trailing period
 
-## Examples of Valid PR Titles
+### Title Examples
 
+Valid:
 - `feat(widgets): add new table widget capabilities`
 - `fix(auth): resolve login redirect issue`
-- `docs: update README with setup instructions`
+- `docs: update README with new setup instructions`
 - `refactor(api): simplify error handling logic`
-- `chore: update dependencies to latest versions` 
\ No newline at end of file
+- `chore: update dependencies to latest versions`
+
+Invalid:
+- `Added new feature` — missing type
+- `fix - login bug` — wrong format
+- `feat(client): Added new component.` — capital letter, trailing period, past tense
+
+---
+
+## Part 2: PR Description Body
+
+The PR description follows the template in `.github/pull_request_template.md`. When generating a PR description, gather all needed information **in a single prompt** — do not ask the user multiple times.
+
+### Information Gathering
+
+Before writing the description, ask the user **once** for anything you don't already know. Combine all questions into a single message:
+- **Issue link** — "Do you have an issue number or URL to link? (optional)"
+- **Cypress tags** — "Any Cypress test tags to run? (optional, leave blank for none)"
+- For `feat` PRs — motivation, user-facing behavior, how to test (if not already clear from context)
+- For `fix` PRs — root cause, reproduction steps (if not already clear from context)
+
+If the user has already provided this info (e.g., in the conversation or task description), or has explicitly said to skip it, do not ask again.
+
+### Description Structure
+
+```markdown
+## Description
+<!-- TL;DR required if description exceeds ~500 words or is highly technical -->
+
+<concise summary of what changed and why>
+
+<for feat: motivation, what's new, user-facing impact>
+<for fix: root cause, what was broken, how it's fixed>
+<for build/chore/refactor: what changed, why, compatibility notes>
+
+Fixes #<issue> or Fixes <URL>
+<!-- omit if no issue exists and user chose not to provide one -->
+
+## Automation
+
+/ok-to-test tags="<tags>"
+
+### :mag: Cypress test results
+<!-- leave this section untouched — CI auto-populates it -->
+
+## Communication
+Should the DevRel and Marketing teams inform users about this change?
+- [ ] Yes
+- [ ] No
+```
+
+### Content Rules by PR Type
+
+| Type | Required Content |
+|---|---|
+| `feat` | Motivation, what's new, user-facing behavior, how to verify |
+| `fix` | Root cause, what was broken, reproduction steps, how it's fixed |
+| `perf` | What was slow, what changed, expected improvement |
+| `build` / `chore` | What changed, why (e.g., vulnerability, compatibility), version details |
+| `refactor` | What was refactored, why, no behavior change confirmation |
+| `docs` / `style` / `ci` / `test` | Brief summary of what changed |
+
+### Additional Rules
+
+- **TL;DR**: Include a TL;DR at the top of the Description section when the body exceeds ~500 words or is highly technical.
+- **Links**: Include links to Notion, Figma, or other design docs when they exist and are relevant.
+- **Screenshots**: Include screenshots or recordings for UI changes.
+- **Cypress section**: Never modify the Cypress auto-generated comment block — CI manages it.
+- **Communication checkbox**: Leave unchecked by default. Check "Yes" only for user-facing features or breaking changes.
diff --git a/.cursor/rules/commit/semantic-pr.md b/.cursor/rules/commit/semantic-pr.md
@@ -1,82 +0,0 @@
-# Semantic PR Guidelines for Appsmith
-
-This guide outlines how to ensure your pull requests follow the Conventional Commits specification, which is enforced in this project using the [semantic-prs](https://github.com/Ezard/semantic-prs) GitHub app.
-
-## Current Configuration
-
-The project uses the following semantic PR configuration in `.github/semantic.yml`:
-
-```yaml
-# Always validate the PR title, and ignore the commits
-titleOnly: true
-```
-
-This means that only the PR title needs to follow the Conventional Commits spec, and commit messages are not validated.
-
-## Pull Request Title Format
-
-PR titles should follow this format:
-
-```
-type(scope): description
-```
-
-### Types
-
-Common types according to Conventional Commits:
-
-- `feat`: A new feature
-- `fix`: A bug fix
-- `docs`: Documentation changes
-- `style`: Changes that don't affect the code's meaning (formatting, etc.)
-- `refactor`: Code changes that neither fix a bug nor add a feature
-- `perf`: Performance improvements
-- `test`: Adding or fixing tests
-- `build`: Changes to build process, dependencies, etc.
-- `ci`: Changes to CI configuration files and scripts
-- `chore`: Other changes that don't modify source or test files
-- `revert`: Reverts a previous commit
-
-### Scope
-
-The scope is optional and represents the section of the codebase affected by the change (e.g., `client`, `server`, `widgets`, `plugins`).
-
-### Description
-
-A brief description of the changes. Should:
-- Use imperative, present tense (e.g., "add" not "added" or "adds")
-- Not capitalize the first letter
-- Not end with a period
-
-## Examples of Valid PR Titles
-
-- `feat(widgets): add new table widget capabilities`
-- `fix(auth): resolve login redirect issue`
-- `docs: update README with new setup instructions`
-- `refactor(api): simplify error handling logic`
-- `chore: update dependencies to latest versions`
-
-## Examples of Invalid PR Titles
-
-- `Added new feature` (missing type)
-- `fix - login bug` (improper format, missing scope)
-- `feat(client): Added new component.` (description should use imperative mood and not end with period)
-
-## Automated Validation
-
-The semantic-prs GitHub app will automatically check your PR title when you create or update a pull request. If your PR title doesn't follow the conventions, the check will fail, and you'll need to update your title.
-
-## Cursor Assistance
-
-Cursor will help enforce these rules by:
-
-1. Suggesting conventional PR titles when creating branches
-2. Validating PR titles against the conventional format
-3. Providing feedback on non-compliant PR titles
-4. Suggesting corrections for PR titles that don't meet the requirements
-
-## Resources
-
-- [Conventional Commits Specification](https://www.conventionalcommits.org/)
-- [semantic-prs GitHub App](https://github.com/Ezard/semantic-prs)
-- [Angular Commit Message Guidelines](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit) 
\ No newline at end of file
diff --git a/.cursor/rules/frontend.mdc b/.cursor/rules/frontend.mdc
@@ -0,0 +1,51 @@
+---
+description: React frontend — TypeScript SPA, monorepo packages, Redux-Saga, key directories, testing, and build commands
+globs:
+alwaysApply: false
+---
+# Frontend — `app/client/`
+
+- **Stack:** TypeScript, React, Redux, Redux-Saga
+- **Build:** Yarn 3.5.1 (workspaces monorepo), Webpack
+- **Entry point:** `src/index.tsx`
+- **Node:** v20.11.1
+
+## Monorepo Packages (`packages/`)
+
+| Package | Purpose |
+|---|---|
+| `design-system` | Component library (`ads`, `ads-old`, `headless`, `theming`, `widgets`, `widgets-old`) |
+| `ast` | JS AST parser utilities for binding expressions |
+| `dsl` | DSL schema/transformers for app JSON |
+| `icons` | Icon library |
+| `utils` | Shared utility functions |
+
+## Key `src/` Directories
+
+`pages/`, `widgets/`, `sagas/`, `reducers/`, `actions/`, `selectors/`, `components/`, `IDE/`, `git/`, `layoutSystems/`, `plugins/`, `ce/`, `ee/`, `enterprise/`
+
+## EE Pattern
+
+Look for `ce/`, `ee/`, and `enterprise/` directories under `src/`. Enterprise logic extends or overrides CE implementations.
+
+## Testing
+
+- **Unit:** Jest — `yarn run test:unit`
+- **E2E:** Cypress — `yarn cypress run --browser chrome --headless --spec {fileName}` (run from `app/client/`)
+- **Lint check:** ESLint + Prettier — `yarn run lint`
+- **Prettier check:** `yarn run prettier`
+- **Types:** `yarn run check-types`
+
+## Auto-fix Lint & Prettier (run from `app/client/`)
+
+```bash
+# Fix all Prettier formatting issues
+npx prettier --write ./src ./cypress
+
+# Fix all auto-fixable ESLint errors
+npx eslint --fix --cache ./src && npx eslint --fix -c ./cypress/.eslintrc.json --cache ./cypress
+```
+
+## Dev Proxy
+
+Nginx in `nginx/` for local dev. Caddy (`start-caddy.sh`) exists but WIP.
diff --git a/.cursor/rules/index.md b/.cursor/rules/index.md
@@ -1,45 +0,0 @@
-# Appsmith Cursor Rules
-
-This index provides an overview of all the rules available for Cursor AI in the Appsmith project.
-
-## Commit Rules
-
-- [Semantic PR Validator](commit/semantic-pr-validator.mdc): Validates that PR titles follow the Conventional Commits specification
-- [Semantic PR Guidelines](commit/semantic-pr.md): Guidelines for writing semantic PR titles and commit messages
-
-## Quality Rules
-
-- [Performance Optimizer](quality/performance-optimizer.mdc): Analyzes code for performance issues and suggests improvements
-- [Pre-commit Quality Checks](quality/pre-commit-checks.mdc): Checks code quality before commits
-
-## Testing Rules
-
-- [Test Generator](testing/test-generator.mdc): Automatically generates appropriate tests for code changes
-
-## Verification Rules
-
-- [Bug Fix Verifier](verification/bug-fix-verifier.mdc): Guides developers through proper bug fixing steps and verifies fix quality
-- [Feature Verifier](verification/feature-verifier.mdc): Verifies that new features are properly implemented and tested
-- [Feature Implementation Validator](verification/feature-implementation-validator.mdc): Validates that new features are completely and correctly implemented
-- [Workflow Validator](verification/workflow-validator.mdc): Validates development workflows
-
-## Available Commands
-
-| Command | Description | Rule |
-|---------|-------------|------|
-| `validate_pr_title` | Validates PR title format | Semantic PR Validator |
-| `verify_bug_fix` | Verifies bug fix quality | Bug Fix Verifier |
-| `validate_feature` | Validates feature implementation | Feature Implementation Validator |
-| `verify_feature` | Verifies feature implementation quality | Feature Verifier |
-| `generate_tests` | Generates tests for code changes | Test Generator |
-| `optimize_performance` | Analyzes code for performance issues | Performance Optimizer |
-| `update_docs` | Updates documentation based on code changes | [Auto Update Docs](../hooks/scripts/auto-update-docs.mdc) |
-
-## Triggering Rules
-
-Rules can be triggered:
-1. Automatically based on events (PR creation, file modification, etc.)
-2. Manually via commands in Cursor
-3. From CI/CD pipelines
-
-See each rule's documentation for specific trigger conditions and parameters. 
\ No newline at end of file
diff --git a/.cursor/rules/index.mdc b/.cursor/rules/index.mdc
@@ -1,136 +1,37 @@
 ---
-description: 
-globs: 
+description:
+globs:
 alwaysApply: true
 ---
- # Appsmith Cursor Rules
+# Appsmith — Architecture Overview
 
-```yaml
-name: Appsmith Cursor Rules
-description: A comprehensive set of rules for Cursor AI to enhance development for Appsmith
-author: Cursor AI
-version: 1.0.0
-tags:
-  - appsmith
-  - development
-  - quality
-  - verification
-activation:
-  always: true
-  event:
-    - pull_request
-    - file_change
-    - command
-triggers:
-  - pull_request.created
-  - pull_request.updated
-  - file.created
-  - file.modified
-  - command: "cursor_help"
 ```
-
-## Overview
-
-This is the main entry point for Cursor AI rules for the Appsmith codebase. These rules help enforce consistent coding standards, verify bug fixes and features, generate appropriate tests, and optimize performance.
-
-## Available Rules
-
-### 1. [Semantic PR Validator](mdc:semantic_pr_validator.mdc)
-
-Ensures pull request titles follow the Conventional Commits specification.
-
-```javascript
-// Example usage
-const semanticPR = require('./semantic_pr_validator');
-const validation = semanticPR.onPRTitleChange('feat(widgets): add new table component');
-console.log(validation.status); // 'success'
-```
-
-### 2. [Bug Fix Verifier](mdc:bug_fix_verifier.mdc)
-
-Guides developers through the proper steps to fix bugs and verifies that fixes meet quality standards.
-
-```javascript
-// Example usage
-const bugFixVerifier = require('./bug_fix_verifier');
-const verification = bugFixVerifier.verifyBugFix(changedFiles, testFiles, issueDetails);
-console.log(verification.score); // The verification score
-```
-
-### 3. [Test Generator](mdc:test_generator.mdc)
-
-Analyzes code changes and generates appropriate test cases to ensure proper test coverage.
-
-```javascript
-// Example usage
-const testGenerator = require('./test_generator');
-const testPlan = testGenerator.generateTests(changedFiles, codebase);
-console.log(testPlan.summary); // 'Generated X test plans'
+                    ┌───────────┐
+                    │   Caddy   │  (reverse proxy, TLS)
+                    └─────┬─────┘
+                          │
+             ┌────────────┼────────────┐
+             │            │            │
+    ┌────────▼───┐  ┌─────▼─────┐  ┌──▼──────┐
+    │   Client   │  │  Server   │  │   RTS   │
+    │ React SPA  │  │ Spring    │  │ Node.js │
+    │ TypeScript │  │ Boot/Java │  │ Express │
+    └────────────┘  └─────┬─────┘  └─────────┘
+                          │
+             ┌────────────┼────────────┐
+             │            │            │
+        ┌────▼───┐  ┌────▼────┐  ┌───▼──────┐
+        │MongoDB │  │Postgres │  │ Temporal │
+        │/ Redis │  │         │  │(workflows)│
+        └────────┘  └─────────┘  └──────────┘
 ```
 
-### 4. [Performance Optimizer](mdc:performance_optimizer.mdc)
-
-Identifies performance bottlenecks in code and suggests optimizations to improve efficiency.
-
-```javascript
-// Example usage
-const performanceOptimizer = require('./performance_optimizer');
-const analysis = performanceOptimizer.analyzePerformance(changedFiles, codebase);
-console.log(analysis.score); // The performance score
-```
-
-### 5. [Feature Implementation Validator](mdc:feature_implementation_validator.mdc)
-
-Ensures new feature implementations meet all requirements, follow best practices, and include appropriate tests.
-
-```javascript
-// Example usage
-const featureValidator = require('./feature_implementation_validator');
-const validation = featureValidator.validateFeature(
-  implementationFiles, 
-  codebase,
-  pullRequest
-);
-console.log(validation.score); // The feature implementation score
-```
-
-## Integration
-
-These rules are automatically integrated into Cursor AI when working with the Appsmith codebase. They will be triggered based on context and can also be manually invoked through commands.
-
-## Command Examples
-
-- `validate_pr_title` - Check if a PR title follows conventional commits format
-- `verify_bug_fix --pullRequest=123` - Verify a bug fix implementation
-- `generate_tests --file=src/utils/helpers.js` - Generate tests for a specific file
-- `optimize_performance --file=src/components/Table.tsx` - Analyze and optimize performance 
-- `validate_feature --pullRequest=123` - Validate a feature implementation
-
-## Configuration
-
-The behavior of these rules can be customized in the `.cursor/settings.json` file. For example:
-
-```json
-{
-  "development": {
-    "gitWorkflow": {
-      "semanticPR": {
-        "enabled": true,
-        "titleFormat": "type(scope): description",
-        "validTypes": [
-          "feat", "fix", "docs", "style", "refactor", 
-          "perf", "test", "build", "ci", "chore", "revert"
-        ]
-      }
-    }
-  }
-}
-```
-
-## Documentation
-
-For more detailed information about each rule and how to use it effectively, please refer to the individual rule files linked above.
+- **Client** (`app/client/`) — React + TypeScript SPA, Redux-Saga, Yarn monorepo
+- **Server** (`app/server/`) — Java 17, Spring Boot 3.x (Reactive WebFlux), Maven, MongoDB
+- **RTS** (`app/client/packages/rts/`) — Node.js Express real-time server, SCIM, workflow proxy
+- **Deploy** (`deploy/`) — Docker, Helm, AWS, Ansible, Caddy reverse proxy
+- **Orchestration** — supervisord in Docker, optional Keycloak (SSO)
 
-## Activation
+## EE vs CE Pattern
 
-To activate all rules, run `cursor_help` in the command palette. This will display available commands and provide guidance on using the rules for your specific task.
\ No newline at end of file
+Enterprise and community edition code coexist in the same repo. Look for `ce/` and `ee/` directories within both `app/server` and `app/client`. Enterprise-specific logic extends or overrides CE implementations.
diff --git a/.cursor/rules/infra.mdc b/.cursor/rules/infra.mdc
@@ -0,0 +1,42 @@
+---
+description: Infrastructure — RTS, deployment (Docker/Helm/AWS), Keycloak SSO, CI scripts
+globs:
+alwaysApply: false
+---
+# Infrastructure & Deployment
+
+## RTS — Real-Time Server (`app/client/packages/rts/`)
+
+- **Stack:** TypeScript, Express.js (Node.js)
+- **Build:** Yarn (part of client workspaces), custom `build.sh`
+- **Entry point:** `src/server.ts`
+- **Purpose:** Real-time features, SCIM user provisioning, workflow proxying (Temporal), analytics
+- **Instrumentation:** OpenTelemetry, Sentry
+- **Key dirs:** `controllers/`, `routes/`, `services/`, `middlewares/`, `scim/`, `workflowProxy/`, `ce/`, `ee/`
+
+## Deployment (`deploy/`)
+
+| Subdirectory | Purpose |
+|---|---|
+| `docker/` | Main deployment — `docker-compose.yml`, Caddy, entrypoints, healthchecks, run scripts |
+| `helm/` | Kubernetes Helm chart |
+| `aws/` | AWS deployment scripts |
+| `aws_ami/` | AMI building configs |
+| `ansible/` | Ansible playbooks |
+| `heroku/` | Heroku config |
+| `digital_ocean/` | DigitalOcean deployment |
+| `packer/` | Machine image templates |
+
+**Caddy (reverse proxy):** Config in `deploy/docker/fs/opt/appsmith/`. `caddy-reconfigure.mjs` generates Caddyfile from env vars. `run-caddy.sh` starts Caddy.
+
+## Keycloak SSO (`app/keycloak-docker-config/`)
+
+Systemd service template for Keycloak 16.1.1 as identity provider (SSO/SAML/OIDC) in enterprise deployments.
+
+## CI/CD Scripts (`scripts/`)
+
+Key scripts: `deploy_preview.sh`, `build_dp_from_branch.sh`, `cleanup_dp.sh`, `health_check.sh`, `generate_info_json.sh`, `prepare_server_artifacts.sh`, `local_testing.sh`
+
+## Developer Docs (`contributions/`)
+
+Setup guides (`ClientSetup.md`, `ServerSetup.md`), contribution guidelines, widget development guide, custom JS library docs.
diff --git a/.cursor/rules/quality/performance-optimizer.mdc b/.cursor/rules/quality/performance-optimizer.mdc
@@ -1,358 +1,30 @@
 ---
-description: 
-globs: 
-alwaysApply: true
+description: Performance anti-patterns to watch for in JS/TS, Java, and CSS code reviews
+globs:
+alwaysApply: false
 ---
-# Performance Optimizer
+# Performance Review Checklist
 
-```yaml
-name: Performance Optimizer
-description: Analyzes code for performance issues and suggests improvements
-author: Cursor AI
-version: 1.0.0
-tags:
-  - performance
-  - optimization
-  - analysis
-activation:
-  always: true
-  event:
-    - file_change
-    - pull_request
-    - command
-triggers:
-  - file.modified
-  - pull_request.created
-  - pull_request.updated
-  - command: "optimize_performance"
-```
+## JavaScript / TypeScript
 
-## Rule Definition
+- Avoid nested loops — use Map/Set for lookups instead
+- Don't chain `.map().filter()` on large arrays — combine into a single pass
+- Minimize direct DOM manipulation — batch updates or use DocumentFragment
+- Pair every `addEventListener` with `removeEventListener` to prevent memory leaks
+- Memoize expensive computations (useMemo, useCallback, reselect)
+- Use `requestAnimationFrame` for animations, not setTimeout
 
-This rule analyzes code changes for potential performance issues and suggests optimizations.
+## Java
 
-## Performance Analysis Logic
+- Use `StringBuilder` for string concatenation in loops
+- Use try-with-resources for all `Closeable`/`AutoCloseable` resources
+- Avoid excessive object creation in hot paths
+- Choose collections by access pattern: `ArrayList` for sequential, `HashMap` for lookup
+- Prefer primitives over wrapper classes where possible
 
-```javascript
-// Main function to analyze code for performance issues
-function analyzePerformance(files, codebase) {
-  const issues = [];
-  const suggestions = [];
-  let score = 100; // Start with perfect score
-  
-  // Process each file
-  for (const file of files) {
-    const fileIssues = findPerformanceIssues(file, codebase);
-    if (fileIssues.length > 0) {
-      issues.push(...fileIssues);
-      
-      // Reduce score based on severity of issues
-      score -= fileIssues.reduce((total, issue) => total + issue.severity, 0);
-      
-      // Generate optimization suggestions
-      const fileSuggestions = generateOptimizationSuggestions(file, fileIssues, codebase);
-      suggestions.push(...fileSuggestions);
-    }
-  }
-  
-  // Ensure score doesn't go below 0
-  score = Math.max(0, score);
-  
-  return {
-    score,
-    issues,
-    suggestions,
-    summary: generatePerformanceSummary(score, issues, suggestions)
-  };
-}
+## CSS
 
-// Find performance issues in a file
-function findPerformanceIssues(file, codebase) {
-  const issues = [];
-  
-  // Check file based on its type
-  if (file.path.includes('.ts') || file.path.includes('.js')) {
-    issues.push(...findJavaScriptPerformanceIssues(file));
-  } else if (file.path.includes('.java')) {
-    issues.push(...findJavaPerformanceIssues(file));
-  } else if (file.path.includes('.css')) {
-    issues.push(...findCssPerformanceIssues(file));
-  }
-  
-  return issues;
-}
-
-// Find performance issues in JavaScript/TypeScript files
-function findJavaScriptPerformanceIssues(file) {
-  const issues = [];
-  const content = file.content;
-  
-  // Check for common JavaScript performance issues
-  
-  // 1. Nested loops with high complexity (O(n²) or worse)
-  if (/for\s*\([^)]*\)\s*\{[^}]*for\s*\([^)]*\)/g.test(content)) {
-    issues.push({
-      type: 'nested_loops',
-      lineNumber: findLineNumber(content, /for\s*\([^)]*\)\s*\{[^}]*for\s*\([^)]*\)/g),
-      description: 'Nested loops detected, which may cause O(n²) time complexity',
-      severity: 8,
-      suggestion: 'Consider refactoring to reduce time complexity, possibly using maps/sets'
-    });
-  }
-  
-  // 2. Large array operations without memoization
-  if (/\.map\(.*\.filter\(|\.filter\(.*\.map\(/g.test(content)) {
-    issues.push({
-      type: 'chained_array_operations',
-      lineNumber: findLineNumber(content, /\.map\(.*\.filter\(|\.filter\(.*\.map\(/g),
-      description: 'Chained array operations may cause performance issues with large datasets',
-      severity: 5,
-      suggestion: 'Consider combining operations or using a different data structure'
-    });
-  }
-  
-  // 3. Frequent DOM manipulations
-  if (/document\.getElement(s?)By|querySelector(All)?/g.test(content) && 
-      content.match(/document\.getElement(s?)By|querySelector(All)?/g).length > 5) {
-    issues.push({
-      type: 'frequent_dom_manipulation',
-      lineNumber: findLineNumber(content, /document\.getElement(s?)By|querySelector(All)?/g),
-      description: 'Frequent DOM manipulations can cause layout thrashing',
-      severity: 7,
-      suggestion: 'Batch DOM manipulations or use DocumentFragment'
-    });
-  }
-  
-  // 4. Memory leaks in event listeners
-  if (/addEventListener\(/g.test(content) && 
-      !/removeEventListener\(/g.test(content)) {
-    issues.push({
-      type: 'potential_memory_leak',
-      lineNumber: findLineNumber(content, /addEventListener\(/g),
-      description: 'Event listener without corresponding removal may cause memory leaks',
-      severity: 6,
-      suggestion: 'Add corresponding removeEventListener calls where appropriate'
-    });
-  }
-  
-  // Add more JavaScript-specific performance checks here
-  
-  return issues;
-}
-
-// Find performance issues in Java files
-function findJavaPerformanceIssues(file) {
-  const issues = [];
-  const content = file.content;
-  
-  // Check for common Java performance issues
-  
-  // 1. Inefficient string concatenation
-  if (/String.*\+= |String.*= .*\+ /g.test(content)) {
-    issues.push({
-      type: 'inefficient_string_concat',
-      lineNumber: findLineNumber(content, /String.*\+= |String.*= .*\+ /g),
-      description: 'Inefficient string concatenation in loops',
-      severity: 4,
-      suggestion: 'Use StringBuilder instead of string concatenation'
-    });
-  }
-  
-  // 2. Unclosed resources
-  if (/new FileInputStream|new Connection/g.test(content) &&
-      !/try\s*\([^)]*\)/g.test(content)) {
-    issues.push({
-      type: 'unclosed_resources',
-      lineNumber: findLineNumber(content, /new FileInputStream|new Connection/g),
-      description: 'Resources may not be properly closed',
-      severity: 7,
-      suggestion: 'Use try-with-resources to ensure proper resource closure'
-    });
-  }
-  
-  // Add more Java-specific performance checks here
-  
-  return issues;
-}
-
-// Find performance issues in CSS files
-function findCssPerformanceIssues(file) {
-  const issues = [];
-  const content = file.content;
-  
-  // Check for common CSS performance issues
-  
-  // 1. Overqualified selectors
-  if (/div\.[a-zA-Z0-9_-]+|ul\.[a-zA-Z0-9_-]+/g.test(content)) {
-    issues.push({
-      type: 'overqualified_selectors',
-      lineNumber: findLineNumber(content, /div\.[a-zA-Z0-9_-]+|ul\.[a-zA-Z0-9_-]+/g),
-      description: 'Overqualified selectors may impact rendering performance',
-      severity: 3,
-      suggestion: 'Use more efficient selectors, avoiding element type with class'
-    });
-  }
-  
-  // 2. Universal selectors
-  if (/\*\s*\{/g.test(content)) {
-    issues.push({
-      type: 'universal_selector',
-      lineNumber: findLineNumber(content, /\*\s*\{/g),
-      description: 'Universal selectors can be very slow, especially in large documents',
-      severity: 5,
-      suggestion: 'Replace universal selectors with more specific ones'
-    });
-  }
-  
-  // Add more CSS-specific performance checks here
-  
-  return issues;
-}
-
-// Find line number for a regex match
-function findLineNumber(content, regex) {
-  const match = content.match(regex);
-  if (!match) return 0;
-  
-  const index = content.indexOf(match[0]);
-  return content.substring(0, index).split('\n').length;
-}
-
-// Generate optimization suggestions based on issues found
-function generateOptimizationSuggestions(file, issues, codebase) {
-  const suggestions = [];
-  
-  for (const issue of issues) {
-    const suggestion = {
-      file: file.path,
-      issue: issue.type,
-      description: issue.suggestion,
-      lineNumber: issue.lineNumber,
-      code: issue.suggestion // This would be actual code in a real implementation
-    };
-    
-    suggestions.push(suggestion);
-  }
-  
-  return suggestions;
-}
-
-// Generate a summary of the performance analysis
-function generatePerformanceSummary(score, issues, suggestions) {
-  const criticalIssues = issues.filter(issue => issue.severity >= 7).length;
-  const majorIssues = issues.filter(issue => issue.severity >= 4 && issue.severity < 7).length;
-  const minorIssues = issues.filter(issue => issue.severity < 4).length;
-  
-  return {
-    score,
-    issues: {
-      total: issues.length,
-      critical: criticalIssues,
-      major: majorIssues,
-      minor: minorIssues
-    },
-    suggestions: suggestions.length,
-    recommendation: getPerformanceRecommendation(score)
-  };
-}
-
-// Get a recommendation based on the performance score
-function getPerformanceRecommendation(score) {
-  if (score >= 90) {
-    return "Code looks good performance-wise. Only minor optimizations possible.";
-  } else if (score >= 70) {
-    return "Some performance issues found. Consider addressing them before deploying.";
-  } else if (score >= 50) {
-    return "Significant performance issues detected. Optimizations strongly recommended.";
-  } else {
-    return "Critical performance issues found. The code may perform poorly in production.";
-  }
-}
-
-// Run on activation
-function activate(context) {
-  // Register event handlers
-  context.on('file.modified', (event) => {
-    const file = context.getFileContent(event.file.path);
-    const codebase = context.getCodebase();
-    return analyzePerformance([file], codebase);
-  });
-  
-  context.on('pull_request.created', (event) => {
-    const files = context.getPullRequestFiles(event.pullRequest.id);
-    const codebase = context.getCodebase();
-    return analyzePerformance(files, codebase);
-  });
-  
-  context.on('pull_request.updated', (event) => {
-    const files = context.getPullRequestFiles(event.pullRequest.id);
-    const codebase = context.getCodebase();
-    return analyzePerformance(files, codebase);
-  });
-  
-  context.registerCommand('optimize_performance', (args) => {
-    const filePath = args.file || context.getCurrentFilePath();
-    if (!filePath) {
-      return {
-        status: "error",
-        message: "No file specified"
-      };
-    }
-    
-    const file = context.getFileContent(filePath);
-    const codebase = context.getCodebase();
-    return analyzePerformance([file], codebase);
-  });
-}
-
-// Export functions
-module.exports = {
-  activate,
-  analyzePerformance,
-  findPerformanceIssues,
-  generateOptimizationSuggestions,
-  generatePerformanceSummary
-};
-```
-
-## When It Runs
-
-This rule can be triggered:
-- When code changes might impact performance
-- When a pull request is created or updated
-- When a developer runs the `optimize_performance` command in Cursor
-- Before deploying to production environments
-
-## Usage Example
-
-1. Make code changes to a file
-2. Run `optimize_performance` in Cursor
-3. Review the performance analysis
-4. Implement the suggested optimizations
-5. Re-run the analysis to confirm improvements
-
-## Performance Optimization Best Practices
-
-### JavaScript/TypeScript
-
-- Avoid nested loops when possible
-- Use appropriate data structures (Map, Set) for lookups
-- Minimize DOM manipulations
-- Use event delegation instead of multiple event listeners
-- Memoize expensive function calls
-- Use requestAnimationFrame for animations
-
-### Java
-
-- Use StringBuilder for string concatenation
-- Use try-with-resources for proper resource management
-- Avoid excessive object creation
-- Choose appropriate collections (ArrayList, HashMap) based on use-case
-- Use primitive types where possible instead of wrapper classes
-
-### CSS
-
-- Avoid universal selectors and deeply nested selectors
-- Minimize the use of expensive properties (box-shadow, border-radius, etc.)
-- Prefer class selectors over tag selectors
-- Use CSS containment where appropriate
+- Avoid universal selectors (`* {}`) and deeply nested selectors
+- Minimize expensive properties in frequently repainted elements (box-shadow, border-radius, filter)
+- Prefer class selectors over element-type selectors
+- Use CSS containment (`contain: layout`) where appropriate
diff --git a/.cursor/rules/quality/pre-commit-checks.mdc b/.cursor/rules/quality/pre-commit-checks.mdc
@@ -1,310 +0,0 @@
----
-description: 
-globs: 
-alwaysApply: true
----
- # Pre-Commit Quality Checks
-
-```yaml
-name: Pre-Commit Quality Checks
-description: Runs quality checks similar to GitHub Actions locally before commits
-author: Cursor AI
-version: 1.0.0
-tags:
-  - quality
-  - pre-commit
-  - testing
-  - linting
-activation:
-  always: true
-  events:
-    - pre_commit
-    - command
-triggers:
-  - pre_commit
-  - command: "run_quality_checks"
-```
-
-## Rule Definition
-
-This rule runs the same quality checks locally that would normally run in CI, preventing commits that would fail in the GitHub workflow quality-checks.yml.
-
-## Implementation
-
-```javascript
-const { execSync } = require('child_process');
-const fs = require('fs');
-const path = require('path');
-
-/**
- * Determines which checks to run based on changed files
- * @param {string[]} changedFiles - List of changed files
- * @returns {Object} Object indicating which checks to run
- */
-function determineChecksToRun(changedFiles) {
-  const checks = {
-    serverChecks: false,
-    clientChecks: false,
-  };
-
-  // Check if server files have changed
-  checks.serverChecks = changedFiles.some(file => 
-    file.startsWith('app/server/')
-  );
-
-  // Check if client files have changed
-  checks.clientChecks = changedFiles.some(file => 
-    file.startsWith('app/client/')
-  );
-
-  return checks;
-}
-
-/**
- * Gets a list of changed files in the current git staging area
- * @returns {string[]} List of changed files
- */
-function getChangedFiles() {
-  try {
-    const output = execSync('git diff --cached --name-only', { encoding: 'utf8' });
-    return output.split('\n').filter(Boolean);
-  } catch (error) {
-    console.error('Error getting changed files:', error.message);
-    return [];
-  }
-}
-
-/**
- * Runs client-side quality checks
- * @returns {Object} Results of the checks
- */
-function runClientChecks() {
-  const results = {
-    success: true,
-    errors: [],
-    output: []
-  };
-
-  try {
-    // Run client lint
-    console.log('Running client lint checks...');
-    try {
-      const lintOutput = execSync('cd app/client && yarn lint', { encoding: 'utf8' });
-      results.output.push('✅ Client lint passed');
-    } catch (error) {
-      results.success = false;
-      results.errors.push('Client lint failed');
-      results.output.push(`❌ Client lint failed: ${error.message}`);
-    }
-
-    // Run client unit tests
-    console.log('Running client unit tests...');
-    try {
-      const testOutput = execSync('cd app/client && yarn test', { encoding: 'utf8' });
-      results.output.push('✅ Client unit tests passed');
-    } catch (error) {
-      results.success = false;
-      results.errors.push('Client unit tests failed');
-      results.output.push(`❌ Client unit tests failed: ${error.message}`);
-    }
-
-    // Check for cyclic dependencies
-    console.log('Checking for cyclic dependencies...');
-    try {
-      const cyclicCheckOutput = execSync('cd app/client && yarn check-circular-deps', { encoding: 'utf8' });
-      results.output.push('✅ No cyclic dependencies found');
-    } catch (error) {
-      results.success = false;
-      results.errors.push('Cyclic dependencies check failed');
-      results.output.push(`❌ Cyclic dependencies found: ${error.message}`);
-    }
-
-    // Run prettier check
-    console.log('Running prettier check...');
-    try {
-      const prettierOutput = execSync('cd app/client && yarn prettier', { encoding: 'utf8' });
-      results.output.push('✅ Prettier check passed');
-    } catch (error) {
-      results.success = false;
-      results.errors.push('Prettier check failed');
-      results.output.push(`❌ Prettier check failed: ${error.message}`);
-    }
-  } catch (error) {
-    results.success = false;
-    results.errors.push(`General error in client checks: ${error.message}`);
-  }
-
-  return results;
-}
-
-/**
- * Runs server-side quality checks
- * @returns {Object} Results of the checks
- */
-function runServerChecks() {
-  const results = {
-    success: true,
-    errors: [],
-    output: []
-  };
-
-  try {
-    // Run server unit tests
-    console.log('Running server unit tests...');
-    try {
-      const testOutput = execSync('cd app/server && ./gradlew test', { encoding: 'utf8' });
-      results.output.push('✅ Server unit tests passed');
-    } catch (error) {
-      results.success = false;
-      results.errors.push('Server unit tests failed');
-      results.output.push(`❌ Server unit tests failed: ${error.message}`);
-    }
-
-    // Run server spotless check
-    console.log('Running server spotless check...');
-    try {
-      const spotlessOutput = execSync('cd app/server && ./gradlew spotlessCheck', { encoding: 'utf8' });
-      results.output.push('✅ Server spotless check passed');
-    } catch (error) {
-      results.success = false;
-      results.errors.push('Server spotless check failed');
-      results.output.push(`❌ Server spotless check failed: ${error.message}`);
-    }
-  } catch (error) {
-    results.success = false;
-    results.errors.push(`General error in server checks: ${error.message}`);
-  }
-
-  return results;
-}
-
-/**
- * Runs all quality checks
- * @param {Object} context - The execution context
- * @returns {Object} Results of the checks
- */
-function runQualityChecks(context) {
-  console.log('Running pre-commit quality checks...');
-  
-  const changedFiles = getChangedFiles();
-  if (!changedFiles.length) {
-    return {
-      status: 'success',
-      message: 'No files to check'
-    };
-  }
-
-  const checksToRun = determineChecksToRun(changedFiles);
-  const results = {
-    success: true,
-    output: ['Starting quality checks for staged files...'],
-    clientChecks: null,
-    serverChecks: null
-  };
-
-  // Run client checks if client files have changed
-  if (checksToRun.clientChecks) {
-    results.output.push('\n=== Client Checks ===');
-    results.clientChecks = runClientChecks();
-    results.output = results.output.concat(results.clientChecks.output);
-    results.success = results.success && results.clientChecks.success;
-  }
-
-  // Run server checks if server files have changed
-  if (checksToRun.serverChecks) {
-    results.output.push('\n=== Server Checks ===');
-    results.serverChecks = runServerChecks();
-    results.output = results.output.concat(results.serverChecks.output);
-    results.success = results.success && results.serverChecks.success;
-  }
-
-  // If no checks were run, note that
-  if (!checksToRun.clientChecks && !checksToRun.serverChecks) {
-    results.output.push('No client or server files were changed, skipping checks');
-  }
-
-  if (results.success) {
-    return {
-      status: 'success',
-      message: 'All quality checks passed',
-      details: results.output.join('\n')
-    };
-  } else {
-    return {
-      status: 'failure',
-      message: 'Quality checks failed',
-      details: results.output.join('\n')
-    };
-  }
-}
-
-/**
- * Register command and hooks
- * @param {Object} context - The cursor context
- */
-function activate(context) {
-  // Register pre-commit hook
-  context.on('pre_commit', (event) => {
-    return runQualityChecks(context);
-  });
-  
-  // Register command for manual validation
-  context.registerCommand('run_quality_checks', () => {
-    return runQualityChecks(context);
-  });
-}
-
-module.exports = {
-  activate,
-  runQualityChecks
-};
-```
-
-## Usage
-
-This rule runs automatically on pre-commit events. You can also manually trigger it with the command `run_quality_checks`.
-
-### What It Checks
-
-1. **For Client-side Changes:**
-   - Runs linting checks
-   - Runs unit tests
-   - Checks for cyclic dependencies
-   - Runs prettier formatting validation
-
-2. **For Server-side Changes:**
-   - Runs unit tests
-   - Runs spotless formatting checks
-
-### Behavior
-
-- Only runs checks relevant to the files being committed (client and/or server)
-- Prevents commits if any checks fail
-- Provides detailed output about which checks passed or failed
-
-### Requirements
-
-- Node.js and yarn for client-side checks
-- Java and Gradle for server-side checks
-- Git for determining changed files
-
-### Customization
-
-You can customize which checks are run by modifying the `runClientChecks` and `runServerChecks` functions.
-
-### Example Output
-
-```
-Running pre-commit quality checks...
-Starting quality checks for staged files...
-
-=== Client Checks ===
-✅ Client lint passed
-✅ Client unit tests passed
-✅ No cyclic dependencies found
-✅ Prettier check passed
-
-=== Server Checks ===
-✅ Server unit tests passed
-✅ Server spotless check passed
-```
\ No newline at end of file
diff --git a/.cursor/rules/task-list.mdc b/.cursor/rules/task-list.mdc
@@ -1,100 +0,0 @@
-# Task List Management
-
-Guidelines for creating and managing task lists in Markdown files to track project progress
-
-## Task List Creation
-
-1. Create task lists in a markdown file (in the project root):
-   - Use `TASKS.md` or a descriptive name relevant to the feature (e.g., `ASSISTANT_CHAT.md`)
-   - Include a clear title and description of the feature being implemented
-
-2. Structure the file with these sections:
-   ```markdown
-   # Feature Name Implementation
-   
-   Brief description of the feature and its purpose.
-   
-   ## Completed Tasks
-   
-   - [x] Task 1 that has been completed
-   - [x] Task 2 that has been completed
-   
-   ## In Progress Tasks
-   
-   - [ ] Task 3 currently being worked on
-   - [ ] Task 4 to be completed soon
-   
-   ## Future Tasks
-   
-   - [ ] Task 5 planned for future implementation
-   - [ ] Task 6 planned for future implementation
-   
-   ## Implementation Plan
-   
-   Detailed description of how the feature will be implemented.
-   
-   ### Relevant Files
-   
-   - path/to/file1.ts - Description of purpose
-   - path/to/file2.ts - Description of purpose
-   ```
-
-## Task List Maintenance
-
-1. Update the task list as you progress:
-   - Mark tasks as completed by changing `[ ]` to `[x]`
-   - Add new tasks as they are identified
-   - Move tasks between sections as appropriate
-
-2. Keep "Relevant Files" section updated with:
-   - File paths that have been created or modified
-   - Brief descriptions of each file's purpose
-   - Status indicators (e.g., ✅) for completed components
-
-3. Add implementation details:
-   - Architecture decisions
-   - Data flow descriptions
-   - Technical components needed
-   - Environment configuration
-
-## AI Instructions
-
-When working with task lists, the AI should:
-
-1. Regularly update the task list file after implementing significant components
-2. Mark completed tasks with [x] when finished
-3. Add new tasks discovered during implementation
-4. Maintain the "Relevant Files" section with accurate file paths and descriptions
-5. Document implementation details, especially for complex features
-6. When implementing tasks one by one, first check which task to implement next
-7. After implementing a task, update the file to reflect progress
-
-## Example Task Update
-
-When updating a task from "In Progress" to "Completed":
-
-```markdown
-## In Progress Tasks
-
-- [ ] Implement database schema
-- [ ] Create API endpoints for data access
-
-## Completed Tasks
-
-- [x] Set up project structure
-- [x] Configure environment variables
-```
-
-Should become:
-
-```markdown
-## In Progress Tasks
-
-- [ ] Create API endpoints for data access
-
-## Completed Tasks
-
-- [x] Set up project structure
-- [x] Configure environment variables
-- [x] Implement database schema
-```
\ No newline at end of file
diff --git a/.cursor/rules/testing/test-generator.mdc b/.cursor/rules/testing/test-generator.mdc
@@ -1,295 +1,71 @@
 ---
-description: 
-globs: 
-alwaysApply: true
+description: Test conventions and examples for frontend (Jest/Cypress) and backend (JUnit) — file naming, frameworks, and patterns
+globs:
+alwaysApply: false
 ---
-# Test Generator
+# Testing Conventions
 
-```yaml
-name: Test Generator
-description: Automatically generates appropriate tests for code changes
-author: Cursor AI
-version: 1.0.0
-tags:
-  - testing
-  - automation
-  - quality
-activation:
-  always: true
-  event:
-    - file_change
-    - command
-triggers:
-  - file.created
-  - file.modified
-  - command: "generate_tests"
-```
-
-## Rule Definition
-
-This rule analyzes code changes and generates appropriate test cases to ensure proper test coverage.
-
-## Test Generation Logic
-
-```javascript
-// Main function to generate tests for code changes
-function generateTests(files, codebase) {
-  const testPlans = [];
-  
-  // Process each changed file
-  for (const file of files) {
-    if (shouldGenerateTestsFor(file)) {
-      const testPlan = createTestPlan(file, codebase);
-      testPlans.push(testPlan);
-    }
-  }
-  
-  return {
-    testPlans,
-    summary: `Generated ${testPlans.length} test plans`
-  };
-}
-
-// Determine if we should generate tests for a file
-function shouldGenerateTestsFor(file) {
-  // Skip test files, configuration files, etc.
-  if (file.path.includes('.test.') || file.path.includes('.spec.')) {
-    return false;
-  }
-  
-  // Skip certain file types
-  const skipExtensions = ['.md', '.json', '.yml', '.yaml', '.svg', '.png', '.jpg'];
-  if (skipExtensions.some(ext => file.path.endsWith(ext))) {
-    return false;
-  }
-  
-  return true;
-}
-
-// Create a test plan for the file
-function createTestPlan(file, codebase) {
-  const testType = determineTestType(file);
-  const testCases = analyzeFileForTestCases(file, codebase);
-  
-  return {
-    sourceFile: file.path,
-    testType,
-    testFile: generateTestFilePath(file, testType),
-    testCases,
-    testFramework: selectTestFramework(file)
-  };
-}
-
-// Determine the appropriate type of test
-function determineTestType(file) {
-  if (file.path.includes('app/client')) {
-    if (file.path.includes('/components/')) {
-      return 'component';
-    } else if (file.path.includes('/utils/')) {
-      return 'unit';
-    } else if (file.path.includes('/api/')) {
-      return 'integration';
-    }
-    return 'unit';
-  } else if (file.path.includes('app/server')) {
-    if (file.path.includes('/controllers/')) {
-      return 'controller';
-    } else if (file.path.includes('/services/')) {
-      return 'service';
-    } else if (file.path.includes('/repositories/')) {
-      return 'repository';
-    }
-    return 'unit';
-  }
-  
-  return 'unit'; // Default
-}
-
-// Analyze file to determine test cases needed
-function analyzeFileForTestCases(file, codebase) {
-  // This would contain complex analysis of the file
-  // to determine appropriate test cases
-  const testCases = [];
-  
-  // Example test cases for different file types
-  if (file.path.includes('.tsx') || file.path.includes('.jsx')) {
-    testCases.push(
-      { type: 'render', description: 'should render correctly' },
-      { type: 'props', description: 'should handle props correctly' },
-      { type: 'interaction', description: 'should handle user interactions' }
-    );
-  } else if (file.path.includes('.java')) {
-    testCases.push(
-      { type: 'normal', description: 'should execute successfully with valid input' },
-      { type: 'exception', description: 'should handle exceptions with invalid input' }
-    );
-  }
-  
-  return testCases;
-}
-
-// Generate path for the test file
-function generateTestFilePath(file, testType) {
-  if (file.path.includes('app/client')) {
-    const basePath = file.path.replace(/\.(ts|tsx|js|jsx)$/, '');
-    return `${basePath}.test.${file.path.split('.').pop()}`;
-  } else if (file.path.includes('app/server')) {
-    return file.path.replace(/\.java$/, 'Test.java');
-  }
-  
-  return file.path + '.test';
-}
-
-// Select appropriate test framework
-function selectTestFramework(file) {
-  if (file.path.includes('app/client')) {
-    if (file.path.includes('/cypress/')) {
-      return 'cypress';
-    }
-    return 'jest';
-  } else if (file.path.includes('app/server')) {
-    return 'junit';
-  }
-  
-  return 'jest'; // Default
-}
-
-// Generate actual test code based on the test plan
-function generateTestCode(testPlan) {
-  // This would create the actual test code based on the framework and test cases
-  // This is a placeholder that would contain complex logic to generate tests
-  return "// Generated test code would go here";
-}
-
-// Run on activation
-function activate(context) {
-  // Register event handlers
-  context.on('file.created', (event) => {
-    const file = context.getFileContent(event.file.path);
-    const codebase = context.getCodebase();
-    return generateTests([file], codebase);
-  });
-  
-  context.on('file.modified', (event) => {
-    const file = context.getFileContent(event.file.path);
-    const codebase = context.getCodebase();
-    return generateTests([file], codebase);
-  });
-  
-  context.registerCommand('generate_tests', (args) => {
-    const filePath = args.file || context.getCurrentFilePath();
-    if (!filePath) {
-      return {
-        status: "error",
-        message: "No file specified"
-      };
-    }
-    
-    const file = context.getFileContent(filePath);
-    const codebase = context.getCodebase();
-    return generateTests([file], codebase);
-  });
-}
-
-// Export functions
-module.exports = {
-  activate,
-  generateTests,
-  generateTestCode,
-  shouldGenerateTestsFor,
-  createTestPlan
-};
-```
-
-## When It Runs
-
-This rule can be triggered:
-- When code changes are made and tests need to be created
-- When a new file is created
-- When an existing file is modified
-- When a developer runs the `generate_tests` command in Cursor
-- When submitting a PR with code changes that lack tests
-
-## Usage Example
+## File Naming
 
-1. Make code changes to a file
-2. Run `generate_tests` in Cursor
-3. Review the generated test plan
-4. Accept or modify the suggested tests
-5. Run the tests to verify your changes
+- **Frontend unit:** `ComponentName.test.tsx` (colocated with source)
+- **Frontend E2E:** `cypress/e2e/**/*.spec.ts`
+- **Backend unit:** `ServiceNameTest.java`
+- **Backend integration:** `ServiceNameIntegrationTest.java`
 
-## Test Generation Best Practices
+## Frameworks
 
-### Frontend Tests
+| Area | Unit | Integration | E2E |
+|---|---|---|---|
+| Frontend | Jest + React Testing Library | — | Cypress |
+| Backend | JUnit + Mockito | JUnit + Spring Boot Test | — |
 
-For React components, tests should typically verify:
+## Frontend Test Pattern (Jest)
 
-- Component renders without crashing
-- Props are correctly handled
-- User interactions work as expected
-- Edge cases are handled properly
+```tsx
+import { render, screen, fireEvent } from "@testing-library/react";
+import Button from "./Button";
 
-Example Jest test for a React component:
-
-```jsx
-import React from 'react';
-import { render, screen, fireEvent } from '@testing-library/react';
-import Button from './Button';
-
-describe('Button component', () => {
-  it('renders correctly', () => {
+describe("Button", () => {
+  it("renders correctly", () => {
     render(<Button label="Click me" />);
-    expect(screen.getByText('Click me')).toBeInTheDocument();
+    expect(screen.getByText("Click me")).toBeInTheDocument();
   });
 
-  it('calls onClick handler when clicked', () => {
+  it("calls onClick handler when clicked", () => {
     const handleClick = jest.fn();
     render(<Button label="Click me" onClick={handleClick} />);
-    fireEvent.click(screen.getByText('Click me'));
+    fireEvent.click(screen.getByText("Click me"));
     expect(handleClick).toHaveBeenCalledTimes(1);
   });
 });
 ```
 
-### Backend Tests
-
-For Java services, tests should typically verify:
-
-- Methods return expected results for valid inputs
-- Proper exception handling for invalid inputs
-- Business logic is correctly implemented
-- Edge cases are handled properly
-
-Example JUnit test for a Java service:
+## Backend Test Pattern (JUnit + Reactive)
 
 ```java
-@RunWith(SpringRunner.class)
 @SpringBootTest
 public class UserServiceTest {
-    
+
     @Autowired
     private UserService userService;
-    
+
     @Test
     public void testCreateUser_ValidInput_ReturnsCreatedUser() {
         User user = new User("test@example.com", "password");
-        User result = userService.createUser(user).block();
-        
-        assertNotNull(result);
-        assertNotNull(result.getId());
-        assertEquals("test@example.com", result.getEmail());
+        StepVerifier.create(userService.createUser(user))
+                .assertNext(result -> {
+                    assertNotNull(result.getId());
+                    assertEquals("test@example.com", result.getEmail());
+                })
+                .verifyComplete();
     }
-    
+
     @Test
     public void testCreateUser_DuplicateEmail_ThrowsException() {
         User user = new User("existing@example.com", "password");
-        
-        // First creation should succeed
-        userService.createUser(user).block();
-        
-        // Second attempt with same email should fail
         StepVerifier.create(userService.createUser(user))
-                .expectError(DuplicateUserException.class)
+                .expectError(AppsmithException.class)
                 .verify();
     }
-} 
\ No newline at end of file
+}
+```
diff --git a/.cursor/rules/verification/bug-fix-verifier.mdc b/.cursor/rules/verification/bug-fix-verifier.mdc
@@ -1,717 +1,27 @@
 ---
-description: 
-globs: 
-alwaysApply: true
+description: Bug fix quality checklist — reproduction, root cause analysis, testing, and regression prevention
+globs:
+alwaysApply: false
 ---
----
-description: 
-globs: 
-alwaysApply: true
----
-# Bug Fix Verifier
-
-```yaml
-name: Bug Fix Verifier
-description: Guides developers through proper bug fixing steps and verifies fix quality
-author: Cursor AI
-version: 1.0.0
-tags:
-  - bug
-  - fixes
-  - verification
-  - testing
-activation:
-  always: true
-  event:
-    - pull_request
-    - command
-    - file_change
-triggers:
-  - pull_request.created
-  - pull_request.updated
-  - pull_request.labeled:bug
-  - pull_request.labeled:fix
-  - command: "verify_bug_fix"
-```
-
-## Rule Definition
-
-This rule guides developers through the proper steps to fix bugs and verifies that the fix meets quality standards.
-
-## Bug Fix Verification Logic
-
-```javascript
-// Main function to verify bug fixes
-function verifyBugFix(files, tests, issue) {
-  const results = {
-    reproduction: checkReproduction(issue),
-    testCoverage: checkTestCoverage(files, tests),
-    implementation: checkImplementation(files, issue),
-    regressionTesting: checkRegressionTesting(tests),
-    performance: checkPerformanceImplications(files),
-    score: 0,
-    issues: [],
-    recommendations: []
-  };
-  
-  // Calculate overall score
-  results.score = calculateScore(results);
-  
-  // Generate issues and recommendations
-  results.issues = identifyIssues(results);
-  results.recommendations = generateRecommendations(results.issues);
-  
-  return {
-    ...results,
-    summary: generateSummary(results)
-  };
-}
-
-// Check if the bug is properly reproduced in tests
-function checkReproduction(issue) {
-  const results = {
-    hasReproductionSteps: false,
-    hasReproductionTest: false,
-    clearStepsToReproduce: false,
-    missingElements: []
-  };
-  
-  if (!issue) {
-    results.missingElements.push('issue reference');
-    return results;
-  }
-  
-  // Check if there are clear steps to reproduce
-  results.hasReproductionSteps = 
-    issue.description && 
-    (issue.description.includes('Steps to reproduce') || 
-     issue.description.includes('Reproduction steps'));
-  
-  if (!results.hasReproductionSteps) {
-    results.missingElements.push('clear reproduction steps');
-  }
-  
-  // Check if reproduction steps are clear
-  if (results.hasReproductionSteps) {
-    const stepsSection = extractReproductionSteps(issue.description);
-    results.clearStepsToReproduce = stepsSection && stepsSection.split('\n').length >= 3;
-  }
-  
-  if (!results.clearStepsToReproduce) {
-    results.missingElements.push('detailed reproduction steps');
-  }
-  
-  // Check if there's a test that reproduces the bug
-  results.hasReproductionTest = issue.tests && issue.tests.some(test => 
-    test.includes('test') && test.includes('reproduce')
-  );
-  
-  if (!results.hasReproductionTest) {
-    results.missingElements.push('test that reproduces the bug');
-  }
-  
-  return results;
-}
-
-// Check test coverage of the bug fix
-function checkTestCoverage(files, tests) {
-  const results = {
-    hasTestsForFix: false,
-    testsVerifyFix: false,
-    hasRegressionTests: false,
-    hasUnitTests: false,
-    hasE2ETests: false,
-    testQuality: 0,
-    missingTests: []
-  };
-  
-  if (!tests || tests.length === 0) {
-    results.missingTests.push('any tests for this fix');
-    return results;
-  }
-  
-  // Check if there are tests for the fix
-  results.hasTestsForFix = true;
-  
-  // Check if tests verify the fix
-  results.testsVerifyFix = tests.some(test => 
-    (test.includes('assert') || test.includes('expect')) && 
-    !test.includes('.skip') && 
-    !test.includes('.todo')
-  );
-  
-  if (!results.testsVerifyFix) {
-    results.missingTests.push('tests that verify the fix works');
-  }
-  
-  // Check for regression tests
-  results.hasRegressionTests = tests.some(test => 
-    test.includes('regression') || 
-    test.includes('should not') || 
-    test.includes('should still')
-  );
-  
-  if (!results.hasRegressionTests) {
-    results.missingTests.push('regression tests');
-  }
-  
-  // Check for unit tests
-  results.hasUnitTests = tests.some(test => 
-    test.includes('.test.') || 
-    test.includes('Test.java') ||
-    test.includes('__tests__')
-  );
-  
-  if (!results.hasUnitTests) {
-    results.missingTests.push('unit tests to verify the specific fix');
-  }
-  
-  // Check for end-to-end tests for user-facing changes
-  const isUserFacingChange = files.some(file => 
-    file.path.includes('/components/') || 
-    file.path.includes('/pages/') ||
-    file.path.includes('/ui/') ||
-    file.path.includes('/views/')
-  );
-  
-  if (isUserFacingChange) {
-    results.hasE2ETests = tests.some(test => 
-      test.includes('/e2e/') || 
-      test.includes('/cypress/')
-    );
-    
-    if (!results.hasE2ETests) {
-      results.missingTests.push('end-to-end tests for this user-facing change');
-    }
-  }
-  
-  // Evaluate test quality (improved)
-  let qualityScore = 0;
-  if (results.hasTestsForFix) qualityScore += 20;
-  if (results.testsVerifyFix) qualityScore += 25;
-  if (results.hasRegressionTests) qualityScore += 20;
-  if (results.hasUnitTests) qualityScore += 20;
-  if (results.hasE2ETests || !isUserFacingChange) qualityScore += 15;
-  
-  results.testQuality = qualityScore;
-  
-  return results;
-}
-
-// Check the quality of the implementation
-function checkImplementation(files, issue) {
-  const results = {
-    addressesRootCause: false,
-    isMinimalChange: false,
-    hasNoHardcodedValues: true,
-    followsGoodPractices: true,
-    concerns: []
-  };
-  
-  if (!files || files.length === 0) {
-    results.concerns.push('no implementation files found');
-    return results;
-  }
-  
-  // Check if the implementation addresses the root cause
-  if (issue && issue.title) {
-    const keywords = extractKeywords(issue.title);
-    const filesContent = files.map(file => file.content).join(' ');
-    
-    results.addressesRootCause = keywords.some(keyword => 
-      filesContent.includes(keyword)
-    );
-  }
-  
-  if (!results.addressesRootCause) {
-    results.concerns.push('may not address the root cause');
-  }
-  
-  // Check if changes are minimal
-  const totalChangedLines = files.reduce((sum, file) => {
-    return sum + countChangedLines(file);
-  }, 0);
-  
-  results.isMinimalChange = totalChangedLines < 50;
-  
-  if (!results.isMinimalChange) {
-    results.concerns.push('changes are not minimal');
-  }
-  
-  // Check for hardcoded values
-  const hardcodedPattern = /'[a-zA-Z0-9]{10,}'/;
-  results.hasNoHardcodedValues = !files.some(file => 
-    hardcodedPattern.test(file.content)
-  );
-  
-  if (!results.hasNoHardcodedValues) {
-    results.concerns.push('contains hardcoded values');
-  }
-  
-  // Check for unsafe property access in Redux/React applications
-  const unsafePropertyAccess = files.some(file => {
-    // Check if this is a Redux/React file
-    const isReduxReactFile = file.path.includes('.jsx') || 
-                             file.path.includes('.tsx') ||
-                             file.content.includes('import { useSelector }') ||
-                             file.content.includes('import { connect }');
-                             
-    if (!isReduxReactFile) return false;
-    
-    // Check for potentially unsafe deep property access
-    const hasNestedProps = file.content.includes('?.');
-    const hasObjectChaining = /\w+\.\w+\.\w+/.test(file.content);
-    const usesLodashGet = file.content.includes('import get from') || 
-                          file.content.includes('lodash/get');
-                         
-    // If file has nested properties but doesn't use lodash get or optional chaining
-    return (hasObjectChaining && !hasNestedProps && !usesLodashGet);
-  });
-  
-  if (unsafePropertyAccess) {
-    results.followsGoodPractices = false;
-    results.concerns.push('contains unsafe nested property access, consider using lodash/get or optional chaining');
-  }
-  
-  // Check for good practices
-  const badPractices = [
-    { pattern: /\/\/ TODO:/, message: 'contains TODO comments' },
-    { pattern: /console\.log\(/, message: 'contains debug logging' },
-    { pattern: /Thread\.sleep\(/, message: 'contains blocking calls' },
-    { pattern: /alert\(/, message: 'contains alert() calls' }
-  ];
-  
-  badPractices.forEach(practice => {
-    if (files.some(file => practice.pattern.test(file.content))) {
-      results.followsGoodPractices = false;
-      results.concerns.push(practice.message);
-    }
-  });
-  
-  return results;
-}
-
-// Check regression testing
-function checkRegressionTesting(tests) {
-  const results = {
-    hasRegressionTests: false,
-    coversRelatedFunctionality: false,
-    hasEdgeCaseTests: false,
-    missingTestAreas: []
-  };
-  
-  if (!tests || tests.length === 0) {
-    results.missingTestAreas.push('regression tests');
-    results.missingTestAreas.push('related functionality tests');
-    results.missingTestAreas.push('edge case tests');
-    return results;
-  }
-  
-  // Check for regression tests
-  results.hasRegressionTests = tests.some(test => 
-    test.includes('regression') || 
-    test.includes('should not') || 
-    test.includes('should still')
-  );
-  
-  if (!results.hasRegressionTests) {
-    results.missingTestAreas.push('regression tests');
-  }
-  
-  // Check if tests cover related functionality
-  results.coversRelatedFunctionality = tests.some(test => 
-    test.includes('related') || 
-    test.includes('integration') || 
-    test.includes('with') || 
-    test.includes('when used')
-  );
-  
-  if (!results.coversRelatedFunctionality) {
-    results.missingTestAreas.push('tests for related functionality');
-  }
-  
-  // Check for edge case tests
-  results.hasEdgeCaseTests = tests.some(test => 
-    test.includes('edge case') || 
-    test.includes('boundary') || 
-    test.includes('limit') || 
-    test.includes('extreme')
-  );
-  
-  if (!results.hasEdgeCaseTests) {
-    results.missingTestAreas.push('edge case tests');
-  }
-  
-  return results;
-}
-
-// Check performance implications of the fix
-function checkPerformanceImplications(files) {
-  const results = {
-    noRegressions: true,
-    analyzedPerformance: false,
-    potentialIssues: []
-  };
-  
-  if (!files || files.length === 0) {
-    return results;
-  }
-  
-  // Check for performance regressions
-  const regressionPatterns = [
-    { pattern: /for\s*\([^)]*\)\s*\{[^}]*for\s*\([^)]*\)/, message: 'nested loops may cause performance issues' },
-    { pattern: /Thread\.sleep\(|setTimeout\(/, message: 'blocking calls may affect performance' },
-    { pattern: /new [A-Z][a-zA-Z0-9]*\(.*\)/g, message: 'excessive object creation may affect memory usage' }
-  ];
-  
-  regressionPatterns.forEach(pattern => {
-    if (files.some(file => pattern.pattern.test(file.content))) {
-      results.noRegressions = false;
-      results.potentialIssues.push(pattern.message);
-    }
-  });
-  
-  // Check if performance was analyzed
-  results.analyzedPerformance = files.some(file => 
-    file.content.includes('performance') || 
-    file.content.includes('benchmark') || 
-    file.content.includes('optimize')
-  );
-  
-  return results;
-}
-
-// Calculate overall score for the bug fix
-function calculateScore(results) {
-  let score = 100;
-  
-  // Deduct for missing reproduction elements
-  score -= results.reproduction.missingElements.length * 10;
-  
-  // Deduct for missing tests
-  score -= results.testCoverage.missingTests.length * 15;
-  
-  // Deduct for implementation concerns
-  score -= results.implementation.concerns.length * 10;
-  
-  // Deduct for missing regression test areas
-  score -= results.regressionTesting.missingTestAreas.length * 5;
-  
-  // Deduct for performance issues
-  score -= results.performance.potentialIssues.length * 8;
-  
-  return Math.max(0, Math.round(score));
-}
-
-// Identify issues from all verification checks
-function identifyIssues(results) {
-  const issues = [];
-  
-  // Add reproduction issues
-  results.reproduction.missingElements.forEach(element => {
-    issues.push({
-      type: 'reproduction',
-      severity: 'high',
-      message: `Missing ${element}`
-    });
-  });
-  
-  // Add test coverage issues
-  results.testCoverage.missingTests.forEach(test => {
-    issues.push({
-      type: 'testing',
-      severity: 'high',
-      message: `Missing ${test}`
-    });
-  });
-  
-  // Add implementation issues
-  results.implementation.concerns.forEach(concern => {
-    issues.push({
-      type: 'implementation',
-      severity: 'medium',
-      message: `Implementation ${concern}`
-    });
-  });
-  
-  // Add regression testing issues
-  results.regressionTesting.missingTestAreas.forEach(area => {
-    issues.push({
-      type: 'regression',
-      severity: 'medium',
-      message: `Missing ${area}`
-    });
-  });
-  
-  // Add performance issues
-  results.performance.potentialIssues.forEach(issue => {
-    issues.push({
-      type: 'performance',
-      severity: 'medium',
-      message: `Performance concern: ${issue}`
-    });
-  });
-  
-  return issues;
-}
-
-// Generate recommendations based on identified issues
-function generateRecommendations(issues) {
-  const recommendations = [];
-  
-  // Group issues by type
-  const issuesByType = {};
-  issues.forEach(issue => {
-    if (!issuesByType[issue.type]) {
-      issuesByType[issue.type] = [];
-    }
-    issuesByType[issue.type].push(issue);
-  });
-  
-  // Generate recommendations for requirements issues
-  if (issuesByType.requirements) {
-    recommendations.push({
-      type: 'requirements',
-      title: 'Complete the implementation of requirements',
-      steps: [
-        'Review the missing requirements and ensure they are implemented',
-        'Verify that the implementation matches the acceptance criteria',
-        'Update the code to address all missing requirements'
-      ]
-    });
-  }
-  
-  // Generate recommendations for testing issues
-  if (issuesByType.testing) {
-    recommendations.push({
-      type: 'testing',
-      title: 'Improve test coverage',
-      steps: [
-        'Add unit tests for untested files',
-        'Create integration tests where appropriate',
-        'Ensure all edge cases are covered in tests'
-      ]
-    });
-  }
-  
-  // Generate recommendations for code quality issues
-  if (issuesByType.code_quality) {
-    recommendations.push({
-      type: 'code_quality',
-      title: 'Address code quality issues',
-      steps: [
-        'Remove debugging code (console.log, TODO comments)',
-        'Fix formatting and indentation issues',
-        'Follow project coding standards and best practices',
-        'Use proper data access methods like lodash/get for deeply nested objects',
-        'Consider data nullability and use optional chaining or default values'
-      ]
-    });
-  }
-  
-  // Generate recommendations for documentation issues
-  if (issuesByType.documentation) {
-    recommendations.push({
-      type: 'documentation',
-      title: 'Improve documentation',
-      steps: [
-        'Add JSDoc or JavaDoc comments to public APIs and classes',
-        'Document complex components and their usage',
-        'Ensure all services have proper documentation'
-      ]
-    });
-  }
-  
-  return recommendations;
-}
-
-// Generate a summary of the verification results
-function generateSummary(results) {
-  const score = results.score;
-  let status = '';
-  
-  if (score >= 90) {
-    status = 'EXCELLENT';
-  } else if (score >= 70) {
-    status = 'GOOD';
-  } else if (score >= 50) {
-    status = 'NEEDS IMPROVEMENT';
-  } else {
-    status = 'POOR';
-  }
-  
-  return {
-    score,
-    status,
-    issues: results.issues.length,
-    critical: results.issues.filter(issue => issue.severity === 'high').length,
-    recommendations: results.recommendations.length,
-    message: generateSummaryMessage(score, status, results)
-  };
-}
-
-// Generate a summary message based on results
-function generateSummaryMessage(score, status, results) {
-  if (status === 'EXCELLENT') {
-    return 'The bug fix meets or exceeds all quality standards. Good job!';
-  } else if (status === 'GOOD') {
-    return `The bug fix is good overall but has ${results.issues.length} issues to address.`;
-  } else if (status === 'NEEDS IMPROVEMENT') {
-    const critical = results.issues.filter(issue => issue.severity === 'high').length;
-    return `The bug fix needs significant improvement with ${critical} critical issues.`;
-  } else {
-    return 'The bug fix is incomplete and does not meet minimum quality standards.';
-  }
-}
-
-// Helper function to extract reproduction steps from issue description
-function extractReproductionSteps(description) {
-  if (!description) return null;
-  
-  const stepSectionMarkers = [
-    'Steps to reproduce',
-    'Reproduction steps',
-    'To reproduce',
-    'How to reproduce'
-  ];
-  
-  for (const marker of stepSectionMarkers) {
-    const markerIndex = description.indexOf(marker);
-    if (markerIndex >= 0) {
-      const startIndex = markerIndex + marker.length;
-      let endIndex = description.indexOf('\n\n', startIndex);
-      if (endIndex < 0) endIndex = description.length;
-      
-      return description.substring(startIndex, endIndex).trim();
-    }
-  }
-  
-  return null;
-}
-
-// Helper function to extract keywords from issue title
-function extractKeywords(title) {
-  if (!title) return [];
-  
-  // Remove common words
-  const commonWords = ['a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'is'];
-  let words = title.split(/\s+/)
-    .map(word => word.toLowerCase().replace(/[^\w]/g, ''))
-    .filter(word => word.length > 2 && !commonWords.includes(word));
-  
-  return [...new Set(words)]; // Remove duplicates
-}
-
-// Helper function to count changed lines in a file
-function countChangedLines(file) {
-  if (!file.diff) return file.content.split('\n').length;
-  
-  let changedLines = 0;
-  const diffLines = file.diff.split('\n');
-  
-  for (const line of diffLines) {
-    if (line.startsWith('+') || line.startsWith('-')) {
-      changedLines++;
-    }
-  }
-  
-  return changedLines;
-}
-
-// Run on activation
-function activate(context) {
-  // Register event handlers
-  context.on('pull_request.created', (event) => {
-    const files = context.getPullRequestFiles(event.pullRequest.id);
-    const tests = context.getPullRequestTests(event.pullRequest.id);
-    const issue = context.getLinkedIssue(event.pullRequest);
-    return verifyBugFix(files, tests, issue);
-  });
-  
-  context.on('pull_request.updated', (event) => {
-    const files = context.getPullRequestFiles(event.pullRequest.id);
-    const tests = context.getPullRequestTests(event.pullRequest.id);
-    const issue = context.getLinkedIssue(event.pullRequest);
-    return verifyBugFix(files, tests, issue);
-  });
-  
-  context.on('pull_request.labeled:bug', (event) => {
-    const files = context.getPullRequestFiles(event.pullRequest.id);
-    const tests = context.getPullRequestTests(event.pullRequest.id);
-    const issue = context.getLinkedIssue(event.pullRequest);
-    return verifyBugFix(files, tests, issue);
-  });
-  
-  context.on('pull_request.labeled:fix', (event) => {
-    const files = context.getPullRequestFiles(event.pullRequest.id);
-    const tests = context.getPullRequestTests(event.pullRequest.id);
-    const issue = context.getLinkedIssue(event.pullRequest);
-    return verifyBugFix(files, tests, issue);
-  });
-  
-  context.registerCommand('verify_bug_fix', (args) => {
-    const prId = args.pullRequest;
-    if (!prId) {
-      return {
-        status: "error",
-        message: "No pull request specified"
-      };
-    }
-    
-    const files = context.getPullRequestFiles(prId);
-    const tests = context.getPullRequestTests(prId);
-    const issue = context.getLinkedIssue({id: prId});
-    return verifyBugFix(files, tests, issue);
-  });
-}
-
-// Export functions
-module.exports = {
-  activate,
-  verifyBugFix,
-  checkReproduction,
-  checkTestCoverage,
-  checkImplementation,
-  checkRegressionTesting,
-  checkPerformanceImplications
-};
-```
-
-## When It Runs
-
-This rule can be triggered:
-- When a bug fix pull request is created
-- When a pull request is updated
-- When a pull request is labeled with 'bug' or 'fix'
-- When a developer runs the `verify_bug_fix` command in Cursor
-- Before committing changes meant to fix a bug
-
-## Usage Example
-
-1. Create a pull request for a bug fix
-2. Run `verify_bug_fix --pullRequest=123` in Cursor
-3. Review the verification results
-4. Address any identified issues
-5. Re-run verification to confirm all issues are resolved
-
-## Bug Fix Best Practices
-
-### Reproduction Checklist
-
-- [ ] Document clear steps to reproduce the bug
-- [ ] Create a test that reproduces the bug before fixing
-- [ ] Ensure the reproduction is reliable and consistent
-
-### Fix Implementation Checklist
-
-- [ ] Address the root cause, not just symptoms
-- [ ] Make changes as minimal and focused as possible
-- [ ] Avoid introducing new bugs or regressions
-- [ ] Follow project coding standards and patterns
-
-### Testing Checklist
-
-- [ ] Verify the fix resolves the issue
-- [ ] Test related functionality that might be affected
-- [ ] Consider edge cases and boundary conditions
-- [ ] Ensure all tests pass after the fix
\ No newline at end of file
+# Bug Fix Checklist
+
+## Reproduction
+- Document clear steps to reproduce the bug
+- Write a failing test that demonstrates the bug before fixing
+
+## Implementation
+- Fix the root cause, not just symptoms
+- Keep changes minimal and focused
+- No hardcoded values, no TODO comments, no console.log/alert
+- Use optional chaining or lodash/get for nested property access
+
+## Testing
+- Unit test verifying the specific fix
+- Regression tests for related functionality
+- Edge case and boundary condition coverage
+- E2E test for user-facing changes (Cypress)
+
+## Verification
+- All existing tests still pass
+- No performance regressions introduced
+- Fix actually resolves the original issue
diff --git a/.cursor/rules/verification/feature-implementation-validator.mdc b/.cursor/rules/verification/feature-implementation-validator.mdc
@@ -1,744 +0,0 @@
----
-description: 
-globs: 
-alwaysApply: true
----
- # Feature Implementation Validator
-
-```yaml
-name: Feature Implementation Validator
-description: Validates that new features are completely and correctly implemented
-author: Cursor AI
-version: 1.0.0
-tags:
-  - feature
-  - implementation
-  - quality
-  - validation
-activation:
-  always: true
-  event:
-    - pull_request
-    - command
-triggers:
-  - pull_request.created
-  - pull_request.updated
-  - pull_request.labeled:feature
-  - command: "validate_feature"
-```
-
-## Rule Definition
-
-This rule ensures that new feature implementations meet quality standards, including proper testing, documentation, and adherence to best practices.
-
-## Feature Validation Logic
-
-```javascript
-// Main function to validate feature implementation
-function validateFeature(files, codebase, pullRequest) {
-  const results = {
-    completeness: checkCompleteness(files, codebase),
-    tests: checkTestCoverage(files, codebase),
-    documentation: checkDocumentation(files, codebase),
-    bestPractices: checkBestPractices(files, codebase),
-    accessibility: checkAccessibility(files, codebase),
-    score: 0,
-    issues: [],
-    recommendations: []
-  };
-  
-  // Calculate overall score
-  results.score = calculateScore(results);
-  
-  // Generate issues and recommendations
-  results.issues = identifyIssues(results);
-  results.recommendations = generateRecommendations(results.issues);
-  
-  return {
-    ...results,
-    summary: generateSummary(results)
-  };
-}
-
-// Check if the feature implementation is complete
-function checkCompleteness(files, codebase) {
-  const results = {
-    hasImplementation: false,
-    hasTests: false,
-    hasDocumentation: false,
-    missingComponents: []
-  };
-  
-  // Check for implementation files
-  const implementationFiles = files.filter(file => {
-    return !file.path.includes('.test.') && 
-           !file.path.includes('.spec.') && 
-           !file.path.includes('docs/') && 
-           !file.path.endsWith('.md');
-  });
-  
-  results.hasImplementation = implementationFiles.length > 0;
-  
-  // Check for test files
-  const testFiles = files.filter(file => {
-    return file.path.includes('.test.') || file.path.includes('.spec.');
-  });
-  
-  results.hasTests = testFiles.length > 0;
-  
-  // Check for documentation
-  const docFiles = files.filter(file => {
-    return file.path.includes('docs/') || file.path.endsWith('.md');
-  });
-  
-  results.hasDocumentation = docFiles.length > 0;
-  
-  // Identify missing components
-  if (!results.hasImplementation) {
-    results.missingComponents.push('implementation');
-  }
-  
-  if (!results.hasTests) {
-    results.missingComponents.push('tests');
-  }
-  
-  if (!results.hasDocumentation) {
-    results.missingComponents.push('documentation');
-  }
-  
-  // Check for missing components based on feature type
-  const featureType = identifyFeatureType(files);
-  if (featureType === 'ui' && !hasUiComponents(files)) {
-    results.missingComponents.push('UI components');
-  }
-  
-  if (featureType === 'api' && !hasApiEndpoints(files)) {
-    results.missingComponents.push('API endpoints');
-  }
-  
-  return results;
-}
-
-// Check test coverage of the feature
-function checkTestCoverage(files, codebase) {
-  const results = {
-    hasFunctionalTests: false,
-    hasUnitTests: false,
-    hasIntegrationTests: false,
-    coverage: 0,
-    untested: []
-  };
-  
-  // Get all non-test implementation files
-  const implFiles = files.filter(file => {
-    return !file.path.includes('.test.') && 
-           !file.path.includes('.spec.') && 
-           !file.path.endsWith('.md');
-  });
-  
-  // Check for different test types
-  const testFiles = files.filter(file => {
-    return file.path.includes('.test.') || file.path.includes('.spec.');
-  });
-  
-  results.hasFunctionalTests = testFiles.some(file => 
-    file.content.includes('test(') && 
-    (file.content.includes('render(') || file.content.includes('fireEvent'))
-  );
-  
-  results.hasUnitTests = testFiles.some(file => 
-    file.content.includes('test(') && 
-    !file.content.includes('render(')
-  );
-  
-  results.hasIntegrationTests = testFiles.some(file => 
-    file.content.includes('describe(') && 
-    file.content.includes('integration')
-  );
-  
-  // Calculate rough coverage
-  let testedFunctions = 0;
-  let totalFunctions = 0;
-  
-  implFiles.forEach(file => {
-    const functions = extractFunctions(file.content);
-    totalFunctions += functions.length;
-    
-    functions.forEach(func => {
-      // Check if function is tested in any test file
-      const isTested = testFiles.some(testFile => 
-        testFile.content.includes(func.name)
-      );
-      
-      if (isTested) {
-        testedFunctions++;
-      } else {
-        results.untested.push(func.name);
-      }
-    });
-  });
-  
-  results.coverage = totalFunctions ? (testedFunctions / totalFunctions) * 100 : 0;
-  
-  return results;
-}
-
-// Check if documentation is complete
-function checkDocumentation(files, codebase) {
-  const results = {
-    hasUserDocs: false,
-    hasDeveloperDocs: false,
-    hasApiDocs: false,
-    missingDocs: []
-  };
-  
-  // Check for documentation files
-  const docFiles = files.filter(file => {
-    return file.path.includes('docs/') || file.path.endsWith('.md');
-  });
-  
-  // Check for user documentation
-  results.hasUserDocs = docFiles.some(file => 
-    file.content.includes('user') || 
-    file.content.includes('guide') || 
-    file.path.includes('user')
-  );
-  
-  // Check for developer documentation
-  results.hasDeveloperDocs = docFiles.some(file => 
-    file.content.includes('developer') || 
-    file.content.includes('implementation') || 
-    file.path.includes('dev')
-  );
-  
-  // Check for API documentation
-  results.hasApiDocs = docFiles.some(file => 
-    file.content.includes('API') || 
-    file.content.includes('endpoint') || 
-    file.path.includes('api')
-  );
-  
-  // Identify missing documentation
-  if (!results.hasUserDocs) {
-    results.missingDocs.push('user documentation');
-  }
-  
-  if (!results.hasDeveloperDocs) {
-    results.missingDocs.push('developer documentation');
-  }
-  
-  const hasApiCode = files.some(file => 
-    file.path.includes('api') || 
-    file.content.includes('axios') || 
-    file.content.includes('fetch')
-  );
-  
-  if (hasApiCode && !results.hasApiDocs) {
-    results.missingDocs.push('API documentation');
-  }
-  
-  return results;
-}
-
-// Check adherence to best practices
-function checkBestPractices(files, codebase) {
-  const results = {
-    followsNamingConventions: true,
-    followsArchitecture: true,
-    hasCleanCode: true,
-    violations: []
-  };
-  
-  // Check for naming convention violations
-  files.forEach(file => {
-    if (file.path.includes('.tsx') || file.path.includes('.jsx')) {
-      // React component should use PascalCase
-      const filename = file.path.split('/').pop().split('.')[0];
-      if (!/^[A-Z][a-zA-Z0-9]*$/.test(filename)) {
-        results.followsNamingConventions = false;
-        results.violations.push(`React component "${filename}" should use PascalCase`);
-      }
-    }
-    
-    if (file.path.includes('.java')) {
-      // Java classes should use PascalCase
-      const filename = file.path.split('/').pop().split('.')[0];
-      if (!/^[A-Z][a-zA-Z0-9]*$/.test(filename)) {
-        results.followsNamingConventions = false;
-        results.violations.push(`Java class "${filename}" should use PascalCase`);
-      }
-    }
-  });
-  
-  // Check for architectural violations
-  files.forEach(file => {
-    if (file.path.includes('app/client/components') && file.content.includes('fetch(')) {
-      results.followsArchitecture = false;
-      results.violations.push('Components should not make API calls directly, use services instead');
-    }
-    
-    if (file.path.includes('app/server/controllers') && file.content.includes('Repository')) {
-      results.followsArchitecture = false;
-      results.violations.push('Controllers should not access repositories directly, use services instead');
-    }
-  });
-  
-  // Check for clean code issues
-  files.forEach(file => {
-    // Check for long functions (more than 50 lines)
-    const functions = extractFunctions(file.content);
-    functions.forEach(func => {
-      if (func.lines > 50) {
-        results.hasCleanCode = false;
-        results.violations.push(`Function "${func.name}" is too long (${func.lines} lines)`);
-      }
-    });
-    
-    // Check for high complexity (nested conditionals)
-    if (/if\s*\([^)]*\)\s*\{[^{}]*if\s*\([^)]*\)/g.test(file.content)) {
-      results.hasCleanCode = false;
-      results.violations.push('Nested conditionals detected, consider refactoring');
-    }
-    
-    // Check for commented-out code
-    if (/\/\/\s*[a-zA-Z0-9]+.*\(.*\).*\{/g.test(file.content)) {
-      results.hasCleanCode = false;
-      results.violations.push('Commented-out code detected, remove or refactor');
-    }
-  });
-  
-  return results;
-}
-
-// Check accessibility (for UI features)
-function checkAccessibility(files, codebase) {
-  const results = {
-    hasA11yAttributes: false,
-    hasKeyboardNavigation: false,
-    hasSemanticsHtml: false,
-    issues: []
-  };
-  
-  // Only check UI files
-  const uiFiles = files.filter(file => {
-    return (file.path.includes('.tsx') || file.path.includes('.jsx')) && 
-           file.path.includes('component');
-  });
-  
-  if (uiFiles.length === 0) {
-    // Not a UI feature, mark as not applicable
-    return {
-      notApplicable: true
-    };
-  }
-  
-  // Check for accessibility attributes
-  results.hasA11yAttributes = uiFiles.some(file => 
-    file.content.includes('aria-') || 
-    file.content.includes('role=')
-  );
-  
-  if (!results.hasA11yAttributes) {
-    results.issues.push('No ARIA attributes found in UI components');
-  }
-  
-  // Check for keyboard navigation
-  results.hasKeyboardNavigation = uiFiles.some(file => 
-    file.content.includes('onKeyDown') || 
-    file.content.includes('onKeyPress')
-  );
-  
-  if (!results.hasKeyboardNavigation) {
-    results.issues.push('No keyboard navigation handlers found');
-  }
-  
-  // Check for semantic HTML
-  results.hasSemanticsHtml = uiFiles.some(file => 
-    file.content.includes('<nav') || 
-    file.content.includes('<main') || 
-    file.content.includes('<section') || 
-    file.content.includes('<article') || 
-    file.content.includes('<aside') || 
-    file.content.includes('<header') || 
-    file.content.includes('<footer')
-  );
-  
-  if (!results.hasSemanticsHtml) {
-    results.issues.push('No semantic HTML elements found');
-  }
-  
-  return results;
-}
-
-// Calculate overall score based on all checks
-function calculateScore(results) {
-  let score = 100;
-  
-  // Deduct for missing components
-  score -= results.completeness.missingComponents.length * 15;
-  
-  // Deduct for low test coverage
-  if (results.tests.coverage < 80) {
-    score -= (80 - results.tests.coverage) / 4;
-  }
-  
-  // Deduct for missing documentation
-  score -= results.documentation.missingDocs.length * 10;
-  
-  // Deduct for best practice violations
-  score -= results.bestPractices.violations.length * 5;
-  
-  // Deduct for accessibility issues (if applicable)
-  if (!results.accessibility.notApplicable) {
-    score -= results.accessibility.issues.length * 10;
-  }
-  
-  return Math.max(0, Math.round(score));
-}
-
-// Identify issues from all validation checks
-function identifyIssues(results) {
-  const issues = [];
-  
-  // Add missing components as issues
-  results.completeness.missingComponents.forEach(component => {
-    issues.push({
-      type: 'completeness',
-      severity: 'high',
-      message: `Missing ${component}`
-    });
-  });
-  
-  // Add test coverage issues
-  if (results.tests.coverage < 80) {
-    issues.push({
-      type: 'testing',
-      severity: 'high',
-      message: `Low test coverage (${Math.round(results.tests.coverage)}%)`
-    });
-  }
-  
-  results.tests.untested.forEach(func => {
-    issues.push({
-      type: 'testing',
-      severity: 'medium',
-      message: `Function "${func}" lacks tests`
-    });
-  });
-  
-  // Add documentation issues
-  results.documentation.missingDocs.forEach(doc => {
-    issues.push({
-      type: 'documentation',
-      severity: 'medium',
-      message: `Missing ${doc}`
-    });
-  });
-  
-  // Add best practice violations
-  results.bestPractices.violations.forEach(violation => {
-    issues.push({
-      type: 'best_practice',
-      severity: 'medium',
-      message: violation
-    });
-  });
-  
-  // Add accessibility issues
-  if (!results.accessibility.notApplicable) {
-    results.accessibility.issues.forEach(issue => {
-      issues.push({
-        type: 'accessibility',
-        severity: 'high',
-        message: issue
-      });
-    });
-  }
-  
-  return issues;
-}
-
-// Generate recommendations based on identified issues
-function generateRecommendations(issues) {
-  const recommendations = [];
-  
-  // Group issues by type
-  const issuesByType = {};
-  issues.forEach(issue => {
-    if (!issuesByType[issue.type]) {
-      issuesByType[issue.type] = [];
-    }
-    issuesByType[issue.type].push(issue);
-  });
-  
-  // Generate recommendations for completeness issues
-  if (issuesByType.completeness) {
-    recommendations.push({
-      type: 'completeness',
-      title: 'Complete the feature implementation',
-      steps: issuesByType.completeness.map(issue => issue.message.replace('Missing ', 'Add '))
-    });
-  }
-  
-  // Generate recommendations for testing issues
-  if (issuesByType.testing) {
-    recommendations.push({
-      type: 'testing',
-      title: 'Improve test coverage',
-      steps: [
-        'Write more unit tests for untested functions',
-        'Add integration tests for component interactions',
-        'Ensure all edge cases are covered'
-      ]
-    });
-  }
-  
-  // Generate recommendations for documentation issues
-  if (issuesByType.documentation) {
-    recommendations.push({
-      type: 'documentation',
-      title: 'Complete the documentation',
-      steps: issuesByType.documentation.map(issue => issue.message.replace('Missing ', 'Add '))
-    });
-  }
-  
-  // Generate recommendations for best practice issues
-  if (issuesByType.best_practice) {
-    recommendations.push({
-      type: 'best_practice',
-      title: 'Follow best practices',
-      steps: issuesByType.best_practice.map(issue => issue.message)
-    });
-  }
-  
-  // Generate recommendations for accessibility issues
-  if (issuesByType.accessibility) {
-    recommendations.push({
-      type: 'accessibility',
-      title: 'Improve accessibility',
-      steps: [
-        'Add appropriate ARIA attributes to UI components',
-        'Implement keyboard navigation for all interactive elements',
-        'Use semantic HTML elements to improve screen reader experience'
-      ]
-    });
-  }
-  
-  return recommendations;
-}
-
-// Generate a summary of the validation results
-function generateSummary(results) {
-  const score = results.score;
-  let status = '';
-  
-  if (score >= 90) {
-    status = 'EXCELLENT';
-  } else if (score >= 70) {
-    status = 'GOOD';
-  } else if (score >= 50) {
-    status = 'NEEDS IMPROVEMENT';
-  } else {
-    status = 'INCOMPLETE';
-  }
-  
-  return {
-    score,
-    status,
-    issues: results.issues.length,
-    critical: results.issues.filter(issue => issue.severity === 'high').length,
-    recommendations: results.recommendations.length,
-    message: generateSummaryMessage(score, status, results)
-  };
-}
-
-// Generate a summary message based on results
-function generateSummaryMessage(score, status, results) {
-  if (status === 'EXCELLENT') {
-    return 'Feature implementation meets or exceeds all quality standards. Good job!';
-  } else if (status === 'GOOD') {
-    return `Feature implementation is good overall but has ${results.issues.length} issues to address.`;
-  } else if (status === 'NEEDS IMPROVEMENT') {
-    const critical = results.issues.filter(issue => issue.severity === 'high').length;
-    return `Feature implementation needs significant improvement with ${critical} critical issues.`;
-  } else {
-    return 'Feature implementation is incomplete and does not meet minimum quality standards.';
-  }
-}
-
-// Helper function to extract functions from code
-function extractFunctions(content) {
-  const functions = [];
-  
-  // JavaScript/TypeScript functions
-  const jsMatches = content.match(/function\s+([a-zA-Z0-9_]+)\s*\([^)]*\)\s*\{/g) || [];
-  jsMatches.forEach(match => {
-    const name = match.match(/function\s+([a-zA-Z0-9_]+)/)[1];
-    const startIndex = content.indexOf(match);
-    const endIndex = findClosingBrace(content, startIndex + match.indexOf('{'));
-    const functionBody = content.substring(startIndex, endIndex + 1);
-    const lines = functionBody.split('\n').length;
-    
-    functions.push({ name, lines });
-  });
-  
-  // Java methods
-  const javaMatches = content.match(/public|private|protected\s+[a-zA-Z0-9_<>]+\s+([a-zA-Z0-9_]+)\s*\([^)]*\)\s*\{/g) || [];
-  javaMatches.forEach(match => {
-    const nameParts = match.match(/\s+([a-zA-Z0-9_]+)\s*\(/);
-    if (nameParts && nameParts[1]) {
-      const name = nameParts[1];
-      const startIndex = content.indexOf(match);
-      const endIndex = findClosingBrace(content, startIndex + match.indexOf('{'));
-      const functionBody = content.substring(startIndex, endIndex + 1);
-      const lines = functionBody.split('\n').length;
-      
-      functions.push({ name, lines });
-    }
-  });
-  
-  return functions;
-}
-
-// Helper function to find closing brace
-function findClosingBrace(content, openBraceIndex) {
-  let braceCount = 1;
-  for (let i = openBraceIndex + 1; i < content.length; i++) {
-    if (content[i] === '{') {
-      braceCount++;
-    } else if (content[i] === '}') {
-      braceCount--;
-      if (braceCount === 0) {
-        return i;
-      }
-    }
-  }
-  return content.length - 1;
-}
-
-// Helper function to identify feature type
-function identifyFeatureType(files) {
-  const uiFiles = files.filter(file => {
-    return (file.path.includes('.tsx') || file.path.includes('.jsx')) && 
-           (file.path.includes('component') || file.path.includes('page'));
-  });
-  
-  const apiFiles = files.filter(file => {
-    return (file.path.includes('controller') || file.path.includes('service')) && 
-           (file.path.includes('.java') || file.path.includes('.ts'));
-  });
-  
-  if (uiFiles.length > apiFiles.length) {
-    return 'ui';
-  } else if (apiFiles.length > 0) {
-    return 'api';
-  } else {
-    return 'other';
-  }
-}
-
-// Helper function to check for UI components
-function hasUiComponents(files) {
-  return files.some(file => {
-    return (file.path.includes('.tsx') || file.path.includes('.jsx')) && 
-           file.path.includes('component');
-  });
-}
-
-// Helper function to check for API endpoints
-function hasApiEndpoints(files) {
-  return files.some(file => {
-    return (file.path.includes('controller') || file.path.includes('route')) && 
-           (file.path.includes('.java') || file.path.includes('.ts'));
-  });
-}
-
-// Run on activation
-function activate(context) {
-  // Register event handlers
-  context.on('pull_request.created', (event) => {
-    const files = context.getPullRequestFiles(event.pullRequest.id);
-    const codebase = context.getCodebase();
-    return validateFeature(files, codebase, event.pullRequest);
-  });
-  
-  context.on('pull_request.updated', (event) => {
-    const files = context.getPullRequestFiles(event.pullRequest.id);
-    const codebase = context.getCodebase();
-    return validateFeature(files, codebase, event.pullRequest);
-  });
-  
-  context.on('pull_request.labeled:feature', (event) => {
-    const files = context.getPullRequestFiles(event.pullRequest.id);
-    const codebase = context.getCodebase();
-    return validateFeature(files, codebase, event.pullRequest);
-  });
-  
-  context.registerCommand('validate_feature', (args) => {
-    const prId = args.pullRequest;
-    if (!prId) {
-      return {
-        status: "error",
-        message: "No pull request specified"
-      };
-    }
-    
-    const files = context.getPullRequestFiles(prId);
-    const codebase = context.getCodebase();
-    const pullRequest = context.getPullRequest(prId);
-    return validateFeature(files, codebase, pullRequest);
-  });
-}
-
-// Export functions
-module.exports = {
-  activate,
-  validateFeature,
-  checkCompleteness,
-  checkTestCoverage,
-  checkDocumentation,
-  checkBestPractices,
-  checkAccessibility
-};
-```
-
-## When It Runs
-
-This rule can be triggered:
-- When a new feature pull request is created
-- When a pull request is updated
-- When a pull request is labeled with 'feature'
-- When a developer runs the `validate_feature` command in Cursor
-- Before merging feature implementation
-
-## Usage Example
-
-1. Create a pull request for a new feature
-2. Run `validate_feature --pullRequest=123` in Cursor
-3. Review the validation results
-4. Address any identified issues
-5. Re-run validation to confirm all issues are resolved
-
-## Feature Implementation Best Practices
-
-### Completeness Checklist
-
-- [ ] Implementation code
-- [ ] Comprehensive tests
-- [ ] User documentation
-- [ ] Developer documentation
-- [ ] API documentation (if applicable)
-
-### Testing Requirements
-
-- Unit tests for all functions/methods
-- Integration tests for component interactions
-- Functional tests for UI components
-- Edge case coverage
-- Minimum 80% test coverage
-
-### Documentation Guidelines
-
-- **User Documentation**: Explain how to use the feature
-- **Developer Documentation**: Explain how the feature is implemented
-- **API Documentation**: Document endpoints, parameters, and responses
\ No newline at end of file
diff --git a/.cursor/rules/verification/feature-verifier.mdc b/.cursor/rules/verification/feature-verifier.mdc
@@ -1,628 +1,33 @@
 ---
-description: 
-globs: 
-alwaysApply: true
+description: Feature implementation checklist — requirements, code quality, testing, and documentation standards
+globs:
+alwaysApply: false
 ---
- # Feature Implementation Verifier
-
-```yaml
-name: Feature Implementation Verifier
-description: Verifies that new features are properly implemented and tested
-author: Cursor AI
-version: 1.0.0
-tags:
-  - feature
-  - implementation
-  - verification
-  - acceptance-criteria
-activation:
-  always: true
-  event:
-    - pull_request
-    - command
-triggers:
-  - pull_request.created
-  - pull_request.updated
-  - pull_request.labeled:feature
-  - command: "verify_feature"
-```
-
-## Rule Definition
-
-This rule ensures that new feature implementations meet all requirements, follow best practices, and include appropriate tests.
-
-## Verification Logic
-
-```javascript
-// Main function to verify feature implementation
-function verifyFeatureImplementation(files, tests, requirements) {
-  const results = {
-    requirementsCoverage: checkRequirementsCoverage(files, requirements),
-    testCoverage: checkTestCoverage(files, tests),
-    codeQuality: checkCodeQuality(files),
-    documentation: checkDocumentation(files, requirements),
-    performance: checkPerformance(files),
-    score: 0,
-    issues: [],
-    recommendations: []
-  };
-  
-  // Calculate overall score
-  results.score = calculateScore(results);
-  
-  // Generate issues and recommendations
-  results.issues = identifyIssues(results);
-  results.recommendations = generateRecommendations(results.issues);
-  
-  return {
-    ...results,
-    summary: generateSummary(results)
-  };
-}
-
-// Check if all requirements are implemented
-function checkRequirementsCoverage(files, requirements) {
-  const results = {
-    implementedRequirements: [],
-    missingRequirements: [],
-    implementationRate: 0
-  };
-  
-  if (!requirements || requirements.length === 0) {
-    results.missingRequirements.push('requirements definition');
-    return results;
-  }
-  
-  // For each requirement, check if it's implemented
-  for (const req of requirements) {
-    const isImplemented = files.some(file => fileImplementsRequirement(file, req));
-    
-    if (isImplemented) {
-      results.implementedRequirements.push(req);
-    } else {
-      results.missingRequirements.push(req);
-    }
-  }
-  
-  results.implementationRate = requirements.length > 0 
-    ? (results.implementedRequirements.length / requirements.length) * 100 
-    : 0;
-  
-  return results;
-}
-
-// Helper to check if a file implements a specific requirement
-function fileImplementsRequirement(file, requirement) {
-  // This would contain complex analysis logic to match code to requirements
-  // For now, we'll use a simple text matching approach
-  return file.content.includes(requirement.id) || 
-         file.content.toLowerCase().includes(requirement.description.toLowerCase());
-}
-
-// Check if tests cover all the new functionality
-function checkTestCoverage(files, tests) {
-  const results = {
-    testedFiles: [],
-    untestedFiles: [],
-    coverage: 0
-  };
-  
-  if (!tests || tests.length === 0) {
-    files.forEach(file => {
-      if (shouldHaveTests(file)) {
-        results.untestedFiles.push(file.path);
-      }
-    });
-    
-    return results;
-  }
-  
-  // Check each file to see if it has test coverage
-  for (const file of files) {
-    const hasTests = tests.some(test => testCoversFile(test, file));
-    
-    if (hasTests || !shouldHaveTests(file)) {
-      results.testedFiles.push(file.path);
-    } else {
-      results.untestedFiles.push(file.path);
-    }
-  }
-  
-  const filesToTest = files.filter(file => shouldHaveTests(file)).length;
-  results.coverage = filesToTest > 0 
-    ? (results.testedFiles.length / filesToTest) * 100 
-    : 100;
-  
-  return results;
-}
-
-// Helper to determine if a test covers a specific file
-function testCoversFile(test, file) {
-  // This would contain complex analysis to determine test coverage
-  // For now, we'll use a simple path matching approach
-  const filePath = file.path.replace(/\.(js|ts|jsx|tsx|java)$/, '');
-  const testPath = test.path;
-  
-  return testPath.includes(filePath) || 
-         test.content.includes(file.path) || 
-         test.content.includes(filePath);
-}
-
-// Helper to determine if a file should have tests
-function shouldHaveTests(file) {
-  // Skip certain files that don't need tests
-  const skipPaths = [
-    'app/client/public/',
-    'app/client/src/assets/',
-    'app/client/src/styles/',
-    'app/client/src/constants/',
-    'app/client/src/types/'
-  ];
-  
-  if (skipPaths.some(path => file.path.includes(path))) {
-    return false;
-  }
-  
-  // Skip certain file types
-  const skipExtensions = ['.md', '.json', '.yml', '.yaml', '.svg', '.png', '.jpg'];
-  if (skipExtensions.some(ext => file.path.endsWith(ext))) {
-    return false;
-  }
-  
-  return true;
-}
-
-// Check the code quality of the implementation
-function checkCodeQuality(files) {
-  const results = {
-    qualityIssues: [],
-    issueCount: 0,
-    qualityScore: 100
-  };
-  
-  // Check each file for quality issues
-  for (const file of files) {
-    const fileIssues = analyzeCodeQuality(file);
-    
-    if (fileIssues.length > 0) {
-      results.qualityIssues.push({
-        file: file.path,
-        issues: fileIssues
-      });
-      
-      results.issueCount += fileIssues.length;
-      results.qualityScore -= Math.min(fileIssues.length * 5, 20); // Max 20 points deduction per file
-    }
-  }
-  
-  results.qualityScore = Math.max(0, results.qualityScore);
-  
-  return results;
-}
-
-// Helper to analyze code quality in a file
-function analyzeCodeQuality(file) {
-  const issues = [];
-  const content = file.content;
-  
-  // Check for common code quality issues
-  if (file.path.includes('.js') || file.path.includes('.ts')) {
-    // Check for console.log statements
-    if (content.includes('console.log')) {
-      issues.push({
-        type: 'debugging',
-        line: findLineForPattern(content, 'console.log'),
-        description: 'Remove console.log statements before committing'
-      });
-    }
-    
-    // Check for TODO comments
-    if (content.includes('TODO')) {
-      issues.push({
-        type: 'incomplete',
-        line: findLineForPattern(content, 'TODO'),
-        description: 'Resolve TODO comments before committing'
-      });
-    }
-    
-    // Check for commented out code
-    if (content.match(/\/\/\s*[a-zA-Z0-9]+/)) {
-      issues.push({
-        type: 'cleanliness',
-        line: findLineForPattern(content, '//'),
-        description: 'Remove commented out code before committing'
-      });
-    }
-  }
-  
-  // Check for proper indentation and formatting
-  const lines = content.split('\n');
-  for (let i = 0; i < lines.length; i++) {
-    const line = lines[i];
-    if (line.length > 120) {
-      issues.push({
-        type: 'formatting',
-        line: i + 1,
-        description: 'Line exceeds 120 characters'
-      });
-    }
-    
-    // Check for inconsistent indentation
-    if (i > 0 && line.match(/^\s+/) && lines[i-1].match(/^\s+/)) {
-      const currentIndent = line.match(/^\s+/)[0].length;
-      const prevIndent = lines[i-1].match(/^\s+/)[0].length;
-      
-      if (Math.abs(currentIndent - prevIndent) % 2 !== 0 && Math.abs(currentIndent - prevIndent) !== 0) {
-        issues.push({
-          type: 'formatting',
-          line: i + 1,
-          description: 'Inconsistent indentation'
-        });
-      }
-    }
-  }
-  
-  return issues;
-}
-
-// Helper to find the line number for a pattern
-function findLineForPattern(content, pattern) {
-  const lines = content.split('\n');
-  for (let i = 0; i < lines.length; i++) {
-    if (lines[i].includes(pattern)) {
-      return i + 1;
-    }
-  }
-  return 1;
-}
-
-// Check for appropriate documentation
-function checkDocumentation(files, requirements) {
-  const results = {
-    documentedFiles: [],
-    undocumentedFiles: [],
-    documentationScore: 100
-  };
-  
-  // Check each file for documentation
-  for (const file of files) {
-    if (shouldHaveDocumentation(file)) {
-      if (hasAdequateDocumentation(file)) {
-        results.documentedFiles.push(file.path);
-      } else {
-        results.undocumentedFiles.push(file.path);
-        results.documentationScore -= 10; // 10 points deduction per undocumented file
-      }
-    }
-  }
-  
-  results.documentationScore = Math.max(0, results.documentationScore);
-  
-  return results;
-}
-
-// Helper to determine if a file should have documentation
-function shouldHaveDocumentation(file) {
-  // Public APIs, complex components, and services should have documentation
-  return file.path.includes('/api/') || 
-         file.path.includes('/services/') || 
-         file.path.includes('/components/') ||
-         file.path.endsWith('.java');
-}
-
-// Helper to check if a file has adequate documentation
-function hasAdequateDocumentation(file) {
-  const content = file.content;
-  
-  // Check for JSDoc, JavaDoc, or other documentation patterns
-  if (file.path.includes('.js') || file.path.includes('.ts')) {
-    return content.includes('/**') && content.includes('*/');
-  }
-  
-  if (file.path.includes('.java')) {
-    return content.includes('/**') && content.includes('*/') && content.includes('@param');
-  }
-  
-  // For other files, check for comment blocks
-  return content.includes('/*') && content.includes('*/');
-}
-
-// Check for performance implications
-function checkPerformance(files) {
-  // This would have comprehensive performance analysis
-  // For now, return an empty array for performance issues
-  return {
-    performanceIssues: [],
-    issueCount: 0
-  };
-}
-
-// Calculate overall score based on all checks
-function calculateScore(results) {
-  let score = 100;
-  
-  // Deduct for missing requirements
-  if (results.requirementsCoverage.implementationRate < 100) {
-    score -= (100 - results.requirementsCoverage.implementationRate) * 0.3;
-  }
-  
-  // Deduct for missing tests
-  if (results.testCoverage.coverage < 80) {
-    score -= (80 - results.testCoverage.coverage) * 0.3;
-  }
-  
-  // Deduct for code quality issues
-  score -= (100 - results.codeQuality.qualityScore) * 0.2;
-  
-  // Deduct for documentation issues
-  score -= (100 - results.documentation.documentationScore) * 0.2;
-  
-  return Math.max(0, Math.round(score));
-}
-
-// Identify issues from all verification checks
-function identifyIssues(results) {
-  const issues = [];
-  
-  // Add missing requirements as issues
-  results.requirementsCoverage.missingRequirements.forEach(req => {
-    issues.push({
-      type: 'requirements',
-      severity: 'high',
-      message: `Missing implementation for requirement: ${req.id || req}`
-    });
-  });
-  
-  // Add test coverage issues
-  if (results.testCoverage.untestedFiles.length > 0) {
-    issues.push({
-      type: 'testing',
-      severity: 'high',
-      message: `Missing tests for ${results.testCoverage.untestedFiles.length} files`
-    });
-    
-    results.testCoverage.untestedFiles.forEach(file => {
-      issues.push({
-        type: 'testing',
-        severity: 'medium',
-        message: `No tests for file: ${file}`
-      });
-    });
-  }
-  
-  // Add code quality issues
-  results.codeQuality.qualityIssues.forEach(fileIssue => {
-    fileIssue.issues.forEach(issue => {
-      issues.push({
-        type: 'code_quality',
-        severity: 'medium',
-        message: `${issue.description} in ${fileIssue.file} at line ${issue.line}`
-      });
-    });
-  });
-  
-  // Add documentation issues
-  results.documentation.undocumentedFiles.forEach(file => {
-    issues.push({
-      type: 'documentation',
-      severity: 'medium',
-      message: `Missing or inadequate documentation in ${file}`
-    });
-  });
-  
-  return issues;
-}
-
-// Generate recommendations based on identified issues
-function generateRecommendations(issues) {
-  const recommendations = [];
-  
-  // Group issues by type
-  const issuesByType = {};
-  issues.forEach(issue => {
-    if (!issuesByType[issue.type]) {
-      issuesByType[issue.type] = [];
-    }
-    issuesByType[issue.type].push(issue);
-  });
-  
-  // Generate recommendations for requirements issues
-  if (issuesByType.requirements) {
-    recommendations.push({
-      type: 'requirements',
-      title: 'Complete the implementation of requirements',
-      steps: [
-        'Review the missing requirements and ensure they are implemented',
-        'Verify that the implementation matches the acceptance criteria',
-        'Update the code to address all missing requirements'
-      ]
-    });
-  }
-  
-  // Generate recommendations for testing issues
-  if (issuesByType.testing) {
-    recommendations.push({
-      type: 'testing',
-      title: 'Improve test coverage',
-      steps: [
-        'Add unit tests for untested files',
-        'Create integration tests where appropriate',
-        'Ensure all edge cases are covered in tests'
-      ]
-    });
-  }
-  
-  // Generate recommendations for code quality issues
-  if (issuesByType.code_quality) {
-    recommendations.push({
-      type: 'code_quality',
-      title: 'Address code quality issues',
-      steps: [
-        'Remove debugging code (console.log, TODO comments)',
-        'Fix formatting and indentation issues',
-        'Follow project coding standards and best practices'
-      ]
-    });
-  }
-  
-  // Generate recommendations for documentation issues
-  if (issuesByType.documentation) {
-    recommendations.push({
-      type: 'documentation',
-      title: 'Improve documentation',
-      steps: [
-        'Add JSDoc or JavaDoc comments to public APIs and classes',
-        'Document complex components and their usage',
-        'Ensure all services have proper documentation'
-      ]
-    });
-  }
-  
-  return recommendations;
-}
-
-// Generate a summary of the verification results
-function generateSummary(results) {
-  const score = results.score;
-  let status = '';
-  
-  if (score >= 90) {
-    status = 'EXCELLENT';
-  } else if (score >= 70) {
-    status = 'GOOD';
-  } else if (score >= 50) {
-    status = 'NEEDS IMPROVEMENT';
-  } else {
-    status = 'INCOMPLETE';
-  }
-  
-  return {
-    score,
-    status,
-    issues: results.issues.length,
-    critical: results.issues.filter(issue => issue.severity === 'high').length,
-    recommendations: results.recommendations.length,
-    message: generateSummaryMessage(score, status, results)
-  };
-}
-
-// Generate a summary message based on results
-function generateSummaryMessage(score, status, results) {
-  if (status === 'EXCELLENT') {
-    return 'Feature implementation meets or exceeds all requirements and standards. Good job!';
-  } else if (status === 'GOOD') {
-    return `Feature implementation is good overall but has ${results.issues.length} issues to address.`;
-  } else if (status === 'NEEDS IMPROVEMENT') {
-    const critical = results.issues.filter(issue => issue.severity === 'high').length;
-    return `Feature implementation needs significant improvement with ${critical} critical issues.`;
-  } else {
-    return 'Feature implementation is incomplete and does not meet minimum requirements.';
-  }
-}
-
-// Run on activation
-function activate(context) {
-  // Register event handlers
-  context.on('pull_request.created', (event) => {
-    const files = context.getPullRequestFiles(event.pullRequest.id);
-    const tests = context.getPullRequestTests(event.pullRequest.id);
-    const requirements = context.getFeatureRequirements(event.pullRequest);
-    return verifyFeatureImplementation(files, tests, requirements);
-  });
-  
-  context.on('pull_request.updated', (event) => {
-    const files = context.getPullRequestFiles(event.pullRequest.id);
-    const tests = context.getPullRequestTests(event.pullRequest.id);
-    const requirements = context.getFeatureRequirements(event.pullRequest);
-    return verifyFeatureImplementation(files, tests, requirements);
-  });
-  
-  context.on('pull_request.labeled:feature', (event) => {
-    const files = context.getPullRequestFiles(event.pullRequest.id);
-    const tests = context.getPullRequestTests(event.pullRequest.id);
-    const requirements = context.getFeatureRequirements(event.pullRequest);
-    return verifyFeatureImplementation(files, tests, requirements);
-  });
-  
-  context.registerCommand('verify_feature', (args) => {
-    const prId = args.pullRequest;
-    if (!prId) {
-      return {
-        status: "error",
-        message: "No pull request specified"
-      };
-    }
-    
-    const files = context.getPullRequestFiles(prId);
-    const tests = context.getPullRequestTests(prId);
-    const requirements = context.getFeatureRequirements({ id: prId });
-    return verifyFeatureImplementation(files, tests, requirements);
-  });
-}
-
-// Export functions
-module.exports = {
-  activate,
-  verifyFeatureImplementation,
-  checkRequirementsCoverage,
-  checkTestCoverage,
-  checkCodeQuality,
-  checkDocumentation,
-  checkPerformance
-};
-```
-
-## When It Runs
-
-This rule can be triggered:
-- When a new feature pull request is created
-- When a pull request is updated
-- When a pull request is labeled with 'feature'
-- When a developer runs the `verify_feature` command in Cursor
-- Before merging a feature implementation
-
-## Usage Example
-
-1. Create a pull request for a new feature
-2. Run `verify_feature --pullRequest=123` in Cursor
-3. Review the verification results
-4. Address any identified issues
-5. Re-run verification to confirm all issues are resolved
-
-## Feature Implementation Checklist
-
-### Requirements
-- [ ] Understand the feature requirements and acceptance criteria
-- [ ] Design a solution that meets all requirements
-- [ ] Create a plan for implementing the feature
-- [ ] Consider edge cases and potential issues
-
-### Implementation
-- [ ] Follow the project's coding standards and architecture
-- [ ] Write clean, efficient, and maintainable code
-- [ ] Handle errors and edge cases gracefully
-- [ ] Ensure the feature integrates well with existing functionality
-
-### Testing
-- [ ] Write unit tests for all components
-- [ ] Create integration tests for complex interactions
-- [ ] Test across different environments if applicable
-- [ ] Verify that the feature meets all acceptance criteria
-
-### Review
-- [ ] Self-review the code before submission
-- [ ] Address feedback from automated checks
-- [ ] Ensure documentation is complete and accurate
-- [ ] Verify test coverage is adequate
-
-## Example: Verifying Acceptance Criteria
-
-For a file upload feature, the verifier would check for:
-
-- UI components for selecting files
-- Upload progress indicators
-- Success and error states
-- Backend API for handling file uploads
-- File validation and error handling
-- Tests for valid and invalid uploads
-- Performance considerations for large files
\ No newline at end of file
+# Feature Implementation Checklist
+
+## Requirements
+- Understand acceptance criteria before coding
+- Design a solution that meets all requirements
+- Consider edge cases and potential issues
+
+## Implementation
+- Follow project coding standards and architecture (CE/EE patterns)
+- Handle errors and edge cases gracefully
+- No console.log, TODO comments, or commented-out code
+- Components should not make API calls directly — use services
+- Controllers should not access repositories directly — use services
+
+## Testing
+- Unit tests for all new functions/methods
+- Integration tests for complex interactions
+- E2E tests for user-facing features (Cypress)
+- Verify acceptance criteria are met
+
+## Documentation
+- JSDoc/JavaDoc for public APIs and services
+- Document complex components and their usage
+
+## Accessibility (UI features)
+- ARIA attributes on interactive elements
+- Keyboard navigation support
+- Semantic HTML elements
diff --git a/.cursor/rules/verification/workflow-validator.mdc b/.cursor/rules/verification/workflow-validator.mdc
@@ -1,253 +1,23 @@
 ---
-description: 
-globs: 
-alwaysApply: true
+globs: .github/workflows/**/*.{yaml,yml}
+alwaysApply: false
 ---
- # Workflow Configuration Validator
+# GitHub Actions Workflow Validation
 
-```yaml
-name: Workflow Configuration Validator
-description: Validates GitHub workflow files before commits and pushes
-author: Cursor AI
-version: 1.0.0
-tags:
-  - ci
-  - workflows
-  - quality-checks
-  - validation
-activation:
-  always: true
-  events:
-    - pre_commit
-    - pre_push
-    - command
-triggers:
-  - pre_commit
-  - pre_push
-  - command: "validate_workflows"
-```
+When editing workflow files, ensure:
 
-## Rule Definition
+## Required Structure
 
-This rule ensures that GitHub workflow configuration files (especially `.github/workflows/quality-checks.yml`) are valid before allowing commits or pushes.
+Every workflow YAML must have:
+- `name` — descriptive workflow name
+- `on` — trigger configuration (push, pull_request, etc.)
+- `jobs` — at least one job defined
+- Each job must have `runs-on` specified
 
-## Validation Logic
+## Common Mistakes
 
-```javascript
-const yaml = require('js-yaml');
-const fs = require('fs');
-const { execSync } = require('child_process');
-
-/**
- * Main function to validate GitHub workflow files
- * @param {Object} context - The execution context
- * @returns {Object} Validation results
- */
-function validateWorkflows(context) {
-  const results = {
-    isValid: true,
-    errors: [],
-    warnings: []
-  };
-  
-  // Primary focus: quality-checks.yml
-  const qualityChecksPath = '.github/workflows/quality-checks.yml';
-  
-  try {
-    // Check if file exists
-    if (!fs.existsSync(qualityChecksPath)) {
-      results.errors.push(`${qualityChecksPath} file does not exist`);
-      results.isValid = false;
-      return results;
-    }
-    
-    // Check if file is valid YAML
-    try {
-      const fileContents = fs.readFileSync(qualityChecksPath, 'utf8');
-      const parsedYaml = yaml.load(fileContents);
-      
-      // Check for required fields in workflow
-      if (!parsedYaml.name) {
-        results.warnings.push(`${qualityChecksPath} is missing a name field`);
-      }
-      
-      if (!parsedYaml.jobs || Object.keys(parsedYaml.jobs).length === 0) {
-        results.errors.push(`${qualityChecksPath} doesn't contain any jobs`);
-        results.isValid = false;
-      }
-      
-      // Check for common GitHub Actions workflow validation
-      if (context.hasCommand('gh')) {
-        try {
-          // Use GitHub CLI to validate workflow if available
-          execSync(`gh workflow view ${qualityChecksPath} --json`, { stdio: 'pipe' });
-        } catch (error) {
-          results.errors.push(`GitHub CLI validation failed: ${error.message}`);
-          results.isValid = false;
-        }
-      } else {
-        // Basic structural validation if GitHub CLI is not available
-        const requiredKeys = ['on', 'jobs'];
-        for (const key of requiredKeys) {
-          if (!parsedYaml[key]) {
-            results.errors.push(`${qualityChecksPath} is missing required key: ${key}`);
-            results.isValid = false;
-          }
-        }
-      }
-      
-      // Check for other workflows
-      const workflowsDir = '.github/workflows';
-      if (fs.existsSync(workflowsDir)) {
-        const workflowFiles = fs.readdirSync(workflowsDir)
-          .filter(file => file.endsWith('.yml') || file.endsWith('.yaml'));
-        
-        // Validate all workflow files
-        for (const file of workflowFiles) {
-          if (file === 'quality-checks.yml') continue; // Already checked
-          
-          const filePath = `${workflowsDir}/${file}`;
-          try {
-            const contents = fs.readFileSync(filePath, 'utf8');
-            yaml.load(contents); // Just check if it's valid YAML
-          } catch (e) {
-            results.errors.push(`${filePath} contains invalid YAML: ${e.message}`);
-            results.isValid = false;
-          }
-        }
-      }
-    } catch (e) {
-      results.errors.push(`Failed to parse ${qualityChecksPath}: ${e.message}`);
-      results.isValid = false;
-    }
-  } catch (error) {
-    results.errors.push(`General error validating workflows: ${error.message}`);
-    results.isValid = false;
-  }
-  
-  return results;
-}
-
-/**
- * Check if workflow files have been modified in the current changes
- * @param {Object} context - The execution context
- * @returns {boolean} Whether workflow files have been modified
- */
-function haveWorkflowsChanged(context) {
-  try {
-    const gitStatus = execSync('git diff --name-only --cached', { encoding: 'utf8' });
-    const changedFiles = gitStatus.split('\n').filter(Boolean);
-    
-    return changedFiles.some(file => 
-      file.startsWith('.github/workflows/') && 
-      (file.endsWith('.yml') || file.endsWith('.yaml'))
-    );
-  } catch (error) {
-    // If we can't determine if workflows changed, assume they did to be safe
-    return true;
-  }
-}
-
-/**
- * Run the validation when triggered
- * @param {Object} context - The execution context
- * @returns {Object} The action result
- */
-function onTrigger(context, event) {
-  // For pre-commit and pre-push, only validate if workflow files have changed
-  if ((event === 'pre_commit' || event === 'pre_push') && !haveWorkflowsChanged(context)) {
-    return {
-      status: 'success',
-      message: 'No workflow files changed, skipping validation'
-    };
-  }
-  
-  const results = validateWorkflows(context);
-  
-  if (!results.isValid) {
-    return {
-      status: 'failure',
-      message: 'Workflow validation failed',
-      details: results.errors.join('\n'),
-      warnings: results.warnings.join('\n')
-    };
-  }
-  
-  return {
-    status: 'success',
-    message: 'All workflow files are valid',
-    warnings: results.warnings.length ? results.warnings.join('\n') : undefined
-  };
-}
-
-/**
- * Register command and hooks
- * @param {Object} context - The cursor context
- */
-function activate(context) {
-  // Register pre-commit hook
-  context.on('pre_commit', (event) => {
-    return onTrigger(context, 'pre_commit');
-  });
-  
-  // Register pre-push hook
-  context.on('pre_push', (event) => {
-    return onTrigger(context, 'pre_push');
-  });
-  
-  // Register command for manual validation
-  context.registerCommand('validate_workflows', () => {
-    return onTrigger(context, 'command');
-  });
-}
-
-module.exports = {
-  activate,
-  validateWorkflows
-};
-```
-
-## Usage
-
-This rule runs automatically on pre-commit and pre-push events. You can also manually trigger it with the command `validate_workflows`.
-
-### Pre-Commit Hook
-
-When committing changes, this rule will:
-1. Check if any workflow files were modified
-2. If so, validate that `.github/workflows/quality-checks.yml` is properly formatted
-3. Block the commit if validation fails
-
-### Examples
-
-**Valid Workflow:**
-```yaml
-name: Quality Checks
-on:
-  push:
-    branches: [ main ]
-  pull_request:
-    branches: [ main ]
-jobs:
-  lint:
-    runs-on: ubuntu-latest
-    steps:
-      - uses: actions/checkout@v3
-      - name: Run linters
-        run: |
-          npm ci
-          npm run lint
-```
-
-**Invalid Workflow (Will Fail Validation):**
-```yaml
-on:
-  push:
-jobs:
-  lint:
-    # Missing "runs-on" field
-    steps:
-      - uses: actions/checkout@v3
-      - name: Run linters
-        run: npm run lint
-```
\ No newline at end of file
+- Missing `runs-on` in a job definition
+- Invalid YAML syntax (bad indentation, missing colons)
+- Referencing non-existent secrets or variables
+- Using deprecated action versions (prefer `@v4` for checkout, setup-node, etc.)
+- Missing `permissions` block when workflow needs write access
PATCH

echo "Gold patch applied."
