#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vltpkg

# Idempotency guard
if grep -qF "- `src/cli-sdk/src/config/definition.ts` \u2014 **Central file**: all CLI options, fl" ".cursor/rules/cli-sdk-workspace.mdc" && grep -qF "Run from the workspace dir (e.g., `cd src/semver`). If `package.json` deps chang" ".cursor/rules/code-validation-workflow.mdc" && grep -qF "1. JackSpeak parser retains internal state across instances \u2014 `setConfigValues()" ".cursor/rules/config-reload-jackspeak-issues.mdc" && grep -qF "Rule files (`.mdc`) go in `.cursor/rules/` only. Kebab-case filenames." ".cursor/rules/cursor-rules-location.mdc" && grep -qF "**Location**: `location` (default: `./node_modules/.vlt/<DepID>/node_modules/<na" ".cursor/rules/graph/data-structure.mdc" && grep -qF "Check `activeModifier?.interactiveBreadcrumb.current === modifier.breadcrumb.las" ".cursor/rules/graph/ideal-append-nodes.mdc" && grep -qF "`projectRoot`, `packageJson`, `scurry`, `monorepo` (shared instances), `packageI" ".cursor/rules/graph/ideal.mdc" && grep -qF "- **Ideal** (desired state): `ideal.build()` from Virtual or Actual \u2192 fetches ma" ".cursor/rules/graph/index.mdc" && grep -qF "`maybeApplyModifierToSpec()`: calls `modifiers.tryDependencies()` before placing" ".cursor/rules/graph/load-actual.mdc" && grep -qF "- `load.ts`: `load()` (from `vlt-lock.json`), `loadHidden()` (from hidden, sets " ".cursor/rules/graph/lockfiles.mdc" && grep -qF "type NodeModifierEntry = { type: 'node', query: string, breadcrumb: ModifierBrea" ".cursor/rules/graph/modifiers.mdc" && grep -qF "3. **Parent Declared Peer**: parent has alternative candidates \u2192 check via `grap" ".cursor/rules/graph/peers.mdc" && grep -qF "8. **Hoist**: `internalHoist()` \u2192 `node_modules/.vlt/node_modules/<name>` symlin" ".cursor/rules/graph/reify.mdc" && grep -qF "3. `pnpm test --reporter=tap` (single file: `pnpm test --reporter=tap test/compo" ".cursor/rules/gui-validation-workflow.mdc" && grep -qF "**Utilities:** `src/keychain`, `src/security-archive`, `src/semver`, `src/git`, " ".cursor/rules/index.mdc" && grep -qF "1. **Remove** the declaration (call expression without assignment if side-effect" ".cursor/rules/linting-error-handler.mdc" && grep -qF ".cursor/rules/monorepo-structure.mdc" ".cursor/rules/monorepo-structure.mdc" && grep -qF "Use `getSimpleGraph()` from `test/fixtures/graph.ts`. Build `ParserState` with `" ".cursor/rules/query-pseudo-selector-creation.mdc" && grep -qF "npm-compatible registry on Cloudflare Workers (Hono, D1, R2). Multi-upstream, st" ".cursor/rules/registry-development.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/cli-sdk-workspace.mdc b/.cursor/rules/cli-sdk-workspace.mdc
@@ -1,202 +1,50 @@
 ---
-description: 
-globs: src/cli-sdk/*
+description: CLI SDK architecture, commands, and config system
+globs: src/cli-sdk/src/**/*,src/cli-sdk/test/**/*
 alwaysApply: false
 ---
-# CLI SDK Workspace Guide
+# CLI SDK Workspace
 
-Development guide for the @vltpkg/cli-sdk workspace architecture and patterns.
+## Architecture
 
-<rule>
-name: cli_sdk_workspace_guide
-description: Guide for efficiently working within the @vltpkg/cli-sdk workspace
-filters:
-  # Match any work within the cli-sdk workspace
-  - type: path
-    pattern: "^src/cli-sdk/"
-  # Match CLI-related development tasks
-  - type: content
-    pattern: "cli|command|config|option|flag"
+- `src/cli-sdk/src/config/definition.ts` — **Central file**: all CLI options, flags, commands defined here (jackspeak)
+- `src/cli-sdk/src/config/index.ts` — Config parsing, option resolution
+- `src/cli-sdk/src/config/usage.ts` — Help text generation
+- `src/cli-sdk/src/commands/` — Command implementations
+- `src/cli-sdk/src/exec-command.ts` — Shared run/exec logic
 
-actions:
-  - type: architecture_guide
-    message: |
-      ## @vltpkg/cli-sdk Workspace Architecture
+## Adding CLI Options
 
-      The CLI SDK workspace is the core of vlt's command-line interface. Understanding its architecture is crucial for efficient development.
+Define in `definition.ts`, access via `conf.values['option-name']` or `conf.get('option-name')`:
+```typescript
+.opt({
+  'your-option': {
+    hint: 'value', short: 'y',
+    description: 'Description', default: 'default-value',
+  },
+})
+```
 
-      ### Core Architecture Files
+## Command Structure
 
-      **Configuration System:**
-      - `src/cli-sdk/src/config/definition.ts` - **CENTRAL FILE**: All CLI options, flags, and top-level commands are defined here
-      - `src/cli-sdk/src/config/index.ts` - Config parsing logic, option resolution, and configuration management
-      - `src/cli-sdk/src/config/usage.ts` - Usage text generation and help formatting
-      - `src/cli-sdk/src/config/merge.ts` - Configuration merging utilities
-      - `src/cli-sdk/src/index.ts` - Entry point
+Every command exports: `usage` (CommandUsage), `views` (Views), `command` (CommandFn). Pattern:
+```typescript
+const usageDef = { command: 'name', usage: '<args>', description: '...' } as const satisfies CommandUsageDefinition
+export const usage: CommandUsage = () => commandUsage(usageDef)
+export const views: Views<ReturnType> = { human: ViewClass, json: result => result }
+export const command: CommandFn<ReturnType> = async conf => { /* impl */ }
+```
 
-      **Command Implementation:**
-      - `src/cli-sdk/src/commands/` - Individual command implementations (exec.ts, cache.ts, run.ts, etc.)
-      - `src/cli-sdk/src/exec-command.ts` - Shared execution logic for run/exec commands
-      - `src/cli-sdk/src/view.ts` - Output formatting and view management
-      - `src/cli-sdk/src/output.ts` - Console output utilities
+## Adding Commands
 
-  - type: development_patterns
-    message: |
-      ## Key Development Patterns
+1. Add to `canonicalCommands` in `definition.ts`
+2. Create `src/cli-sdk/src/commands/your-command.ts`
+3. Add tests in `src/cli-sdk/test/commands/your-command.ts`
 
-      ### 1. Adding New CLI Options/Flags
-      **Always start with `definition.ts`:**
-      ```typescript
-      // In src/cli-sdk/src/config/definition.ts
-      .opt({
-        'your-option': {
-          hint: 'value',
-          short: 'y',
-          description: 'Description of your option',
-          default: 'default-value',
-        },
-      })
-      ```
+## Config Precedence
 
-      **Then access in commands:**
-      ```typescript
-      // In command implementations
-      const yourOption = conf.values['your-option']
-      ```
+CLI args → project vlt.json → user vlt.json → defaults. Command-specific: `command.{name}` in vlt.json.
 
-      ### 2. Command Structure Pattern
-      Every command follows this pattern:
-      ```typescript
-      // Command usage definition
-      const usageDef = {
-        command: 'command-name',
-        usage: '<args> [flags]',
-        description: 'Command description',
-        subcommands: { /* if applicable */ },
-        examples: { /* usage examples */ },
-      } as const satisfies CommandUsageDefinition
+## Testing
 
-      // Usage function
-      export const usage: CommandUsage = () => commandUsage(usageDef)
-
-      // Views for different output formats
-      export const views: Views<ReturnType> = {
-        human: ViewClass,
-        json: result => result,
-      }
-
-      // Main command function
-      export const command: CommandFn<ReturnType> = async conf => {
-        // Implementation
-      }
-      ```
-
-      ### 3. Config System Flow
-      1. **Definition** → `definition.ts` defines options with jackspeak
-      2. **Parsing** → `index.ts` loads config files and parses CLI args
-      3. **Access** → Commands use `conf.get('option-name')` to access values
-      4. **Types** → TypeScript ensures type safety throughout
-
-      ### 4. Testing Patterns
-      - Tests use `t.mockImport` for clean mocking
-      - Config objects are created with proper typing
-      - Commands are tested with `LoadedConfig` mock objects
-      - Snapshots are used for usage text and complex outputs
-
-  - type: common_tasks
-    message: |
-      ## Common Development Tasks
-
-      ### Adding a New Command
-      1. **Add to `definition.ts`:**
-         ```typescript
-         const canonicalCommands = {
-           // ...existing commands
-           'your-command': 'your-command',
-         }
-         ```
-
-      2. **Create command file:**
-         ```
-         src/cli-sdk/src/commands/your-command.ts
-         ```
-
-      3. **Follow the command structure pattern** (see above)
-
-      4. **Add tests:**
-         ```
-         src/cli-sdk/test/commands/your-command.ts
-         ```
-
-      ### Modifying CLI Options
-      1. **Update `definition.ts`** - Change option definition
-      2. **Update usage** - If command-specific, update in command files
-      3. **Update implementation** - Change how the option is used
-      4. **Update tests** - Ensure tests use new option names/values
-
-      ### Config System Integration
-      - **Config precedence:** CLI args → project vlt.json → user vlt.json → defaults
-      - **Command-specific config:** Use nested `command.{commandName}` in vlt.json
-      - **Type safety:** All config options are strongly typed through jackspeak
-
-      ### Working with Workspace Operations
-      - **Scope filtering:** Use `conf.get('scope')` for DSS query filtering
-      - **Workspace selection:** Use `conf.get('workspace')` and `conf.get('workspace-group')`
-      - **Monorepo handling:** `conf.options.monorepo` provides workspace management
-
-  - type: troubleshooting
-    message: |
-      ## Common Issues & Solutions
-
-      ### Option Not Available
-      - **Check `definition.ts`** - Option must be defined there first
-      - **Check typing** - Ensure TypeScript types are correctly inferred
-      - **Check config loading** - Verify config files are being loaded properly
-
-      ### Command Not Working
-      - **Check command mapping** - Verify command is in `canonicalCommands`
-      - **Check aliases** - Commands may have aliases defined
-      - **Check parsing** - Ensure positional args are handled correctly
-
-      ### Type Errors
-      - **Config types** - Use `LoadedConfig` type for fully parsed config
-      - **Option types** - Options are strongly typed from jackspeak definition
-      - **Command types** - Follow `CommandFn<ReturnType>` pattern
-
-      ### Testing Issues
-      - **Mock imports** - Use `t.mockImport` for clean test isolation
-      - **Config mocking** - Create proper `LoadedConfig` objects for tests
-      - **Async handling** - Most command functions are async
-
-examples:
-  - input: |
-      # Adding a new CLI option
-      1. Edit src/cli-sdk/src/config/definition.ts
-      2. Add to appropriate section (.opt, .flag, .optList)
-      3. Use conf.get('option-name') in commands
-      4. Update tests with new option usage
-    output: "Properly added new CLI option following architecture"
-
-  - input: |
-      # Working with existing commands
-      1. Check src/cli-sdk/src/commands/ for implementation
-      2. Review usage definitions for command structure
-      3. Follow existing patterns for consistency
-      4. Update tests to match changes
-    output: "Efficiently navigated command architecture"
-
-metadata:
-  priority: high
-  version: 1.0
-  tags:
-    - cli-sdk
-    - configuration
-    - commands
-    - architecture
-    - development-patterns
-  related_files:
-    - src/cli-sdk/src/config/definition.ts  # Central CLI definitions
-    - src/cli-sdk/src/config/index.ts       # Config parsing logic
-    - src/cli-sdk/src/commands/             # Command implementations
-    - src/cli-sdk/src/exec-command.ts       # Shared execution patterns
-</rule>
+Uses `t.mockImport` for mocking. Config objects typed as `LoadedConfig`.
diff --git a/.cursor/rules/code-validation-workflow.mdc b/.cursor/rules/code-validation-workflow.mdc
@@ -1,259 +1,27 @@
 ---
-description: 
-globs: 
+description: Code validation workflow (format, lint, test, coverage, typecheck)
+globs: src/*/src/**/*.ts,src/*/test/**/*.ts
 alwaysApply: false
 ---
 # Code Validation Workflow
 
-Rule for validating code quality, formatting, and test coverage using pnpm commands.
+Run from the workspace dir (e.g., `cd src/semver`). If `package.json` deps changed, run `pnpm install` from repo root first.
 
-<rule>
-name: code_validation_workflow
-description: Standards and workflow for validating code quality, formatting, and tests
-filters:
-  # Match any file that might need validation
-  - type: file_extension
-    pattern: "\\.(js|jsx|ts|tsx|json|md|css|scss)$"
-  # Match file modification events
-  - type: event
-    pattern: "file_modify"
+## Steps (run in order, stop on failure)
 
-actions:
-  - type: suggest
-    message: |
-      Before completing your work, run the following validation steps in sequence:
+1. **Format:** `pnpm format`
+2. **Lint:** `pnpm lint` — see `@linting-error-handler.mdc` for common fixes
+3. **Test:** `pnpm test -Rtap --disable-coverage` (single file: append `test/foo.ts`)
+4. **Coverage:** `pnpm test -Rsilent --coverage-report=text-lcov` (single file: append `test/foo.ts`)
+5. **Types:** `pnpm posttest`
 
-      ## Prerequisite: Dependency Management
-      
-      **IMPORTANT**: If you have modified any `package.json` files to add, remove, or update dependencies, you **MUST** run dependency installation first:
+## Snapshots
 
-      ```bash
-      # Navigate to the project root (monorepo root)
-      cd /path/to/vltpkg  # or wherever your project root is
-      
-      # Install/update dependencies for all workspaces
-      pnpm install
-      ```
+Update only when changes are intentional: `pnpm snap -Rtap --disable-coverage test/foo.ts`
 
-      **Why this is critical:**
-      - New dependencies won't be available until installed
-      - Tests and linting may fail with "Cannot find module" errors
-      - Type checking will fail for missing dependencies
-      - The workspace dependency graph needs to be updated
+## Test Quality
 
-      **When to run `pnpm install`:**
-      - ✅ After adding new dependencies to any workspace `package.json`
-      - ✅ After removing dependencies from any workspace `package.json`
-      - ✅ After updating dependency versions
-      - ✅ When switching branches that have different dependencies
-      - ✅ When you see "Cannot find module" errors during development
-
-      **Where to run it:**
-      - Always run `pnpm install` from the **project root** (where the main `package.json` and `pnpm-workspace.yaml` are located)
-      - Do NOT run it from individual workspace directories unless specifically needed
-
-      ---
-
-      1. Format code:
-         ```bash
-         pnpm format
-         ```
-         This ensures consistent code formatting across the codebase.
-         If formatting issues are found, fix them before proceeding.
-
-      2. Lint code:
-         ```bash
-         pnpm lint
-         ```
-         This checks for style guide violations and potential issues.
-         If linting errors are found:
-         - **For common linting issues (unused variables/imports)**: Refer to `@linting-error-handler.mdc` for systematic solutions
-         - Review each error message
-         - Fix the issues in the affected files
-         - Run `pnpm lint` again to verify fixes
-         
-         💡 **Pro tip**: Most linting errors fall into common patterns. Use the linting error handler rule for quick, systematic fixes.
-
-      3. Run tests:
-         ```bash
-         pnpm test -Rtap --disable-coverage
-         ```
-         This runs all tests without coverage reporting.
-         If tests fail:
-         - Review the test output for failures
-         - Fix any failing tests
-         - Run tests again to verify fixes
-
-         3.1. Running tests for a specific file:
-             ```bash
-             pnpm test -Rtap --disable-coverage <path-to-test-file.ts>
-             ```
-             Use this command when working on a specific module to iterate faster.
-             Example:
-             ```bash
-             pnpm test -Rtap --disable-coverage test/index.ts
-             ```
-
-         3.2. Updating snapshots:
-             ```bash
-             pnpm snap -Rtap --disable-coverage <path-to-test-file.ts>
-             ```
-             ⚠️ IMPORTANT: Snapshots are asserting expected results, they should only be updated if all breaking changes to tests are intentional.
-             Before updating snapshots:
-             - Review all snapshot changes carefully
-             - Ensure the changes are expected and intentional
-             - Document any breaking changes in your work
-             - Consider discussing major snapshot updates with the team
-
-      4. Check test coverage:
-         ```bash
-         pnpm test -Rsilent --coverage-report=text-lcov
-         ```
-         This generates a coverage report in lcov format.
-         If coverage is insufficient:
-         - Review the coverage report
-         - Add tests for uncovered code paths
-         - Run coverage check again to verify improvements
-
-         4.1. Checking coverage for a specific file:
-             ```bash
-             pnpm test -Rsilent --coverage-report=text-lcov <path-to-test-file.ts>
-             ```
-             Use this to focus coverage analysis on a specific module.
-             Example:
-             ```bash
-             pnpm test -Rsilent --coverage-report=text-lcov test/index.ts
-             ```
-
-      5. Run type checking:
-         ```bash
-         pnpm posttest
-         ```
-         This runs the TypeScript type checker for the current workspace.
-         Make sure you're in the appropriate folder for the workspace you're working on.
-         For example, to check types on the `@vltpkg/semver` workspace, navigate to the `src/semver` folder first.
-         
-         If type checking errors are found:
-         - Review each type error message carefully
-         - Fix type issues in the affected files
-         - Run `pnpm posttest` again to verify fixes
-         - Ensure all type definitions are correct and complete
-
-      ## Test Quality Guidelines
-
-      When writing tests, follow these guidelines to ensure high-quality, maintainable tests:
-
-      ### Respect Type Contracts
-      **CRITICAL**: Always respect the existing type structure when creating test scenarios:
-      
-      - **Never use `as any` to bypass type checking in tests** unless absolutely necessary for testing error conditions
-      - **Study the actual type definitions** before creating mock objects or test data
-      - **Use proper type-safe test fixtures** that match the real type contracts
-      - **Avoid creating impossible scenarios** that violate the type system
-      
-      **Example of what NOT to do:**
-      ```typescript
-      // ❌ BAD: Violates type contract - Edge.spec is required and non-nullable
-      const edge = {
-        spec: undefined as any, // This breaks the type contract
-        // ... other properties
-      }
-      ```
-      
-      **Example of what TO do:**
-      ```typescript
-      // ✅ GOOD: Respects type contract - creates proper Spec object
-      const spec = Spec.parse('package-name', '^1.0.0', specOptions)
-      const edge = {
-        spec, // Proper Spec object that matches the type contract
-        // ... other properties
-      }
-      ```
-
-      ### Test Realistic Scenarios
-      - **Test edge cases that can actually happen** in the real codebase
-      - **Use existing test fixtures** when possible rather than creating new ones
-      - **Consult similar tests** in the same module for patterns and approaches
-      - **Reference actual implementation code** to understand what scenarios are possible
-
-      ### Type-Safe Test Creation Process
-      1. **Read the type definitions** of the classes/interfaces you're testing
-      2. **Examine existing test files** in the same directory for patterns
-      3. **Use helper functions** from test fixtures when available
-      4. **Validate your test compiles** without type assertions (`as any`)
-      5. **Run type checking** to ensure your tests don't introduce type violations
-
-      Important notes:
-      - Always run these commands in sequence
-      - Do not proceed to the next step if the current step fails
-      - Complete your work only after all validation steps pass
-      - If you're unsure about any errors, ask for help
-
-examples:
-  - input: |
-      # Bad: Skipping validation steps or running tests with coverage
-      # Missing format, lint, and test steps
-      pnpm test -Rtap  # Running tests with coverage in one step
-      pnpm snap -Rtap  # Updating snapshots without reviewing changes
-
-      # Bad: Forgetting to install dependencies after modifying package.json
-      # ... modify package.json to add new dependency ...
-      pnpm format  # Will fail with "Cannot find module" errors
-      
-      # Good: Complete validation workflow (after modifying dependencies)
-      # First, install dependencies from project root
-      cd /path/to/project-root
-      pnpm install
-      # Then navigate back to workspace and continue validation
-      cd src/my-workspace
-      pnpm format
-      pnpm lint
-      pnpm test -Rtap --disable-coverage
-      pnpm test -Rsilent --coverage-report=text-lcov
-      pnpm posttest
-      
-      # Bad: Creating tests that violate type contracts
-      const edge = {
-        spec: undefined as any, // Violates Edge type contract
-        // ...
-      }
-      
-      # Good: Creating type-safe tests
-      const spec = Spec.parse('package-name', '^1.0.0', specOptions)
-      const edge = {
-        spec, // Respects Edge type contract
-        // ...
-      }
-
-      # Good: Iterative development workflow
-      pnpm test -Rtap --disable-coverage test/index.ts
-      # Make changes to the code
-      pnpm format
-      pnpm lint
-      pnpm test -Rtap --disable-coverage test/index.ts
-      # Review snapshot changes carefully
-      pnpm snap -Rtap --disable-coverage test/index.ts
-      # Check coverage for the specific file
-      pnpm test -Rsilent --coverage-report=text-lcov test/index.ts
-      # Type check
-      pnpm posttest
-    output: "Properly validated code changes"
-
-metadata:
-  priority: high
-  version: 1.6
-  tags:
-    - validation
-    - workflow
-    - testing
-    - coverage
-    - snapshots
-    - formatting
-    - linting
-    - type-safety
-    - test-quality
-    - dependency-management
-    - pnpm-install
-  related_rules:
-    - linting-error-handler  # For systematic handling of common linting errors
-</rule>
+- Never use `as any` to bypass types in tests — respect type contracts
+- Use existing test fixtures from `test/` dirs
+- Study similar tests in the module for patterns
+- Ensure 100% coverage
diff --git a/.cursor/rules/config-reload-jackspeak-issues.mdc b/.cursor/rules/config-reload-jackspeak-issues.mdc
@@ -1,223 +1,48 @@
-# Config Reload and JackSpeak Caching Issues
-
-A comprehensive guide to the challenges and solutions for implementing config reloading in the vlt GUI server, including deep insights into JackSpeak caching behavior.
-
-<rule>
-name: config_reload_jackspeak_issues
-description: Understanding config reloading challenges and JackSpeak caching limitations
-filters:
-  # Match config-related work
-  - type: path
-    pattern: "src/server/src/config-data\\.ts"
-  - type: path
-    pattern: "src/cli-sdk/src/config/"
-  # Match config reload implementations
-  - type: content
-    pattern: "config.*reload|reload.*config"
-  # Match JackSpeak usage
-  - type: content
-    pattern: "jackspeak|jack\\."
-
-actions:
-  - type: context
-    message: |
-      ## Problem Statement
-
-      The vlt GUI server's config endpoints (`POST /config`, `POST /config/set`) were returning stale configuration values even after successful config updates. The issue stemmed from multiple layers of caching in the config system.
-
-      ## Root Cause Analysis
-
-      ### JackSpeak Caching Limitations
-
-      **Primary Issue**: JackSpeak's `setConfigValues()` method does not provide a way to clear or override previously set "default" values from config files.
-
-      **Behavior**: When JackSpeak parses config files and sets defaults, subsequent calls to `setConfigValues()` cannot override these cached defaults, leading to persistent stale values.
-
-      **Impact**: Even creating "fresh" Config instances with `reload=true` still carried forward cached state from the JackSpeak parser.
-
-      ### Multi-Layer Caching Problems
-
-      1. **JackSpeak Parser Cache**: Internal caching of parsed config values
-      2. **Config.#options Cache**: Memoized options getter in Config class
-      3. **vlt-json Module Cache**: File system cache in vlt-json (`datas`, `mtimes`, `paths`, `lstatCache`)
-      4. **Config.#loaded Static Cache**: Static cache for loaded config instances
-
-      ## Solution Architecture
-
-      ### Hybrid Config Reading Approach
-
-      We implemented a hybrid solution that bypasses JackSpeak's caching limitations:
-
-      ```typescript
-      // 1. Clear vlt-json caches
-      const { unload, load: vltLoad } = await import('@vltpkg/vlt-json')
-      unload('user')
-      unload('project')
-      
-      // 2. Read fresh config directly from vlt-json
-      configSection = vltLoad('config', validator, 'project')
-      
-      // 3. Prioritize fresh values over Config system
-      if (configSection && key in configSection) {
-        return configSection[key]  // Fresh value
-      }
-      
-      // 4. Fallback to Config system
-      return await getConfigValue(this.config)
-      ```
-
-      ### Key Implementation Details
-
-      **For Individual Config Keys**:
-      - Read directly from `vlt-json` when available
-      - Fallback to Config system for missing keys
-      - Clear `vlt-json` caches on every request
-
-      **For Full Config Lists**:
-      - Get base config from Config system
-      - Overlay fresh `vlt-json` config values using `Object.assign()`
-      - Ensure fresh values take precedence
-
-      **For Config Writing**:
-      - Create completely fresh Config instances for each write operation
-      - Use direct file manipulation via `addConfigToFile()` and `deleteConfigKeys()`
-      - Bypass stale `setConfigValue`/`delConfigValue` functions
-
-      ## Technical Insights
-
-      ### Why Config.load(reload=true) Wasn't Sufficient
-
-      ```typescript
-      // This approach failed because:
-      const freshConfig = await Config.load(projectRoot, process.argv, true)
-      
-      // 1. JackSpeak parser retains internal state
-      // 2. Config.#options cache persists across instances
-      // 3. vlt-json caches weren't cleared
-      // 4. Static Config.#loaded cache interference
-      ```
-
-      ### Critical Discovery: File Path Resolution
-
-      **Issue**: `this.config.get('project-config')` returned `undefined`
-      **Cause**: Config system couldn't resolve project config file paths properly
-      **Solution**: Use `vlt-json.find()` directly to locate config files
-
-      ### Type Safety Challenges
-
-      **Problem**: Dynamic imports of `@vltpkg/vlt-json` caused TypeScript `error` type issues
-      **Solution**: Create typed interface and use type assertions:
-
-      ```typescript
-      type VltJsonModule = {
-        unload: (which?: 'user' | 'project') => void
-        load: <T>(field: string, validator: (x: unknown) => x is T, which?: 'user' | 'project') => T | undefined
-      }
-      
-      const { unload, load } = await import('@vltpkg/vlt-json') as VltJsonModule
-      ```
-
-      ## Performance Considerations
-
-      ### Dynamic Imports vs Static Imports
-
-      **Static imports caused**: "Unsafe call of `error` type" TypeScript errors
-      **Dynamic imports required**: Type assertions and try-catch blocks
-      **Trade-off**: Slight performance cost for type safety and error handling
-
-      ### Cache Clearing Strategy
-
-      **Aggressive Approach**: Clear all caches on every request
-      **Rationale**: Ensures absolute freshness at minimal performance cost
-      **Implementation**: Try-catch blocks prevent cache clearing failures from breaking functionality
-
-      ## Testing Challenges
-
-      ### Mock Complexity
-
-      **Issue**: Tests needed to account for new dynamic import patterns
-      **Solution**: Mock the dynamic imports and focus on integration testing
-
-      ### Coverage for Error Paths
-
-      **Challenge**: Ensuring error handling paths are tested
-      **Approach**: Add specific tests for error handling scenarios with `/* c8 ignore */` for unreachable paths
-
-      ## Lessons Learned
-
-      ### 1. JackSpeak Limitations
-
-      - JackSpeak is not designed for dynamic config reloading
-      - Multiple Config instances share internal parser state
-      - `setConfigValues()` cannot override previously cached defaults
-
-      ### 2. Layered Caching Complexity
-
-      - Multiple caching layers require coordinated clearing
-      - Static caches persist across instance creation
-      - File system caches need explicit management
-
-      ### 3. Hybrid Approaches Work
-
-      - Combining direct file reading with fallback systems provides robustness
-      - Prioritizing fresh data sources ensures consistency
-      - Graceful degradation maintains functionality
-
-      ### 4. Type Safety with Dynamic Imports
-
-      - Dynamic imports require careful type management
-      - Type assertions provide safety without sacrificing functionality
-      - Try-catch blocks are essential for error handling
-
-      ## Future Considerations
-
-      ### Potential Improvements
-
-      1. **JackSpeak Enhancement**: Contribute cache clearing methods to JackSpeak
-      2. **Config System Redesign**: Consider architecture that supports dynamic reloading
-      3. **Performance Optimization**: Cache fresh values with TTL-based invalidation
-
-      ### Monitoring
-
-      - Watch for performance impact of dynamic imports
-      - Monitor cache clearing effectiveness
-      - Track config consistency across server lifecycle
-
-examples:
-  - input: |
-      # Problem: Config not reloading after set
-      const config = await Config.load()
-      await setConfigValue(config, 'registry', 'new-value')
-      const value = config.get('registry') // Returns old value
-    output: "Use hybrid vlt-json + Config system approach"
-
-  - input: |
-      # Problem: TypeScript errors with vlt-json imports
-      import { unload } from '@vltpkg/vlt-json'
-      unload('project') // Error: Unsafe call of error type
-    output: "Use dynamic imports with type assertions"
-
-  - input: |
-      # Problem: Fresh Config instances still return stale values
-      const fresh = await Config.load(root, argv, true)
-      fresh.get('registry') // Still returns cached value
-    output: "JackSpeak parser retains internal state across instances"
-
-metadata:
-  priority: high
-  version: 1.0
-  tags:
-    - config
-    - jackspeak
-    - caching
-    - reload
-    - vlt-json
-    - gui-server
-  related_files:
-    - src/server/src/config-data.ts
-    - src/cli-sdk/src/config/index.ts
-    - src/vlt-json/src/index.ts
-  contributors:
-    - assistant: "Implemented hybrid config reload solution"
-    - user: "Identified GUI server config reload requirements"
-</rule>
\ No newline at end of file
+---
+description: Config reload and JackSpeak caching issues
+globs: src/server/src/config-data.ts,src/cli-sdk/src/config/*,src/vlt-json/src/*
+alwaysApply: false
+---
+# Config Reload & JackSpeak Caching
+
+## Problem
+
+GUI server config endpoints return stale values after updates due to multi-layer caching:
+1. JackSpeak parser retains internal state across instances — `setConfigValues()` can't override cached defaults
+2. `Config.#options` memoization persists
+3. `vlt-json` module has fs caches (`datas`, `mtimes`, `paths`, `lstatCache`)
+4. `Config.#loaded` static cache
+
+`Config.load(root, argv, true)` is NOT sufficient — JackSpeak parser retains state.
+
+## Solution: Hybrid Config Reading
+
+```typescript
+// 1. Clear vlt-json caches
+const { unload, load: vltLoad } = await import('@vltpkg/vlt-json')
+unload('user'); unload('project')
+
+// 2. Read fresh from vlt-json, fallback to Config system
+configSection = vltLoad('config', validator, 'project')
+if (configSection && key in configSection) return configSection[key]
+return await getConfigValue(this.config)
+```
+
+**For writes**: Create fresh Config instances per write. Use `addConfigToFile()`/`deleteConfigKeys()` directly.
+
+**Type safety**: Dynamic imports need type assertions:
+```typescript
+type VltJsonModule = {
+  unload: (which?: 'user' | 'project') => void
+  load: <T>(
+    field: string,
+    validator: (x: unknown, file: string) => asserts x is T,
+    which?: 'user' | 'project',
+  ) => T | undefined
+}
+const { unload, load } = await import('@vltpkg/vlt-json') as VltJsonModule
+```
+
+## Key Files
+
+`src/server/src/config-data.ts`, `src/cli-sdk/src/config/index.ts`, `src/vlt-json/src/index.ts`
diff --git a/.cursor/rules/cursor-rules-location.mdc b/.cursor/rules/cursor-rules-location.mdc
@@ -1,75 +1,12 @@
 ---
 description: Cursor Rules Location
-globs: *.mdc
+globs: **/*.mdc
+alwaysApply: false
 ---
 # Cursor Rules Location
 
-Rules for placing and organizing Cursor rule files in the repository.
+Rule files (`.mdc`) go in `.cursor/rules/` only. Kebab-case filenames.
 
-<rule>
-name: cursor_rules_location
-description: Standards for placing Cursor rule files in the correct directory
-filters:
-  # Match any .mdc files
-  - type: file_extension
-    pattern: "\\.mdc$"
-  # Match files that look like Cursor rules
-  - type: content
-    pattern: "(?s)<rule>.*?</rule>"
-  # Match file creation events
-  - type: event
-    pattern: "file_create"
-
-actions:
-  - type: reject
-    conditions:
-      - pattern: "^(?!\\.\\/\\.cursor\\/rules\\/.*\\.mdc$)"
-        message: "Cursor rule files (.mdc) must be placed in the .cursor/rules directory"
-
-  - type: suggest
-    message: |
-      When creating Cursor rules:
-
-      1. Always place rule files in PROJECT_ROOT/.cursor/rules/:
-         ```
-         .cursor/rules/
-         ├── your-rule-name.mdc
-         ├── another-rule.mdc
-         └── ...
-         ```
-
-      2. Follow the naming convention:
-         - Use kebab-case for filenames
-         - Always use .mdc extension
-         - Make names descriptive of the rule's purpose
-
-      3. Directory structure:
-         ```
-         PROJECT_ROOT/
-         ├── .cursor/
-         │   └── rules/
-         │       ├── your-rule-name.mdc
-         │       └── ...
-         └── ...
-         ```
-
-      4. Never place rule files:
-         - In the project root
-         - In subdirectories outside .cursor/rules
-         - In any other location
-
-examples:
-  - input: |
-      # Bad: Rule file in wrong location
-      rules/my-rule.mdc
-      my-rule.mdc
-      .rules/my-rule.mdc
-
-      # Good: Rule file in correct location
-      .cursor/rules/my-rule.mdc
-    output: "Correctly placed Cursor rule file"
-
-metadata:
-  priority: high
-  version: 1.0
-</rule>
+```
+.cursor/rules/your-rule-name.mdc
+```
diff --git a/.cursor/rules/graph/data-structure.mdc b/.cursor/rules/graph/data-structure.mdc
@@ -3,218 +3,70 @@ description: Graph core data structures (Graph, Node, Edge, Types)
 globs: src/graph/src/graph.ts,src/graph/src/node.ts,src/graph/src/edge.ts,src/graph/src/types.ts,src/graph/test/graph.ts,src/graph/test/node.ts,src/graph/test/edge.ts
 alwaysApply: false
 ---
-# Graph Core Data Structures
-
-Detailed reference for the data model used by `@vltpkg/graph`, covering `Graph`, `Node`, `Edge`, and public type shapes. Use this to inform future implementation work across the graph system.
-
-<rule>
-name: graph_data_structure
-description: In-depth documentation of Graph, Node, Edge, and their invariants and behaviors
-filters:
-  # Core data structure files
-  - type: path
-    pattern: "^src/graph/src/(graph|node|edge|types)\\.ts$"
-  # Files that consume these types frequently
-  - type: path
-    pattern: "^src/graph/src/(ideal|actual|lockfile|reify)/"
-  # Mentions of Graph/Node/Edge in content
-  - type: content
-    pattern: "class Graph|class Node|class Edge|GraphLike|NodeLike|EdgeLike"
-
-actions:
-  - type: guide
-    message: |
-      ## Overview
-
-      The graph library models a project's installable dependency universe using:
-      - `Graph` — global container of nodes and edges, with importer roots, caches, peer contexts, and helpers
-      - `Node` — unique package instance; identity provided by `@vltpkg/dep-id`
-      - `Edge` — directed dependency relationship from `from` to `to` with a parsed `Spec`
-
-      Public type shapes (`GraphLike`, `NodeLike`, `EdgeLike`) are defined in `src/graph/src/types.ts` for loose coupling with higher-level modules.
-
-  - type: architecture_guide
-    message: |
-      ## Graph (`src/graph/src/graph.ts`)
-
-      Construction:
-      - Initializes `mainImporter` from the project root manifest using a `file:.` DepID
-      - Discovers additional importer nodes from `@vltpkg/workspaces`, adding each as a root
-      - Initializes peer context tracking with an initial empty `PeerContext`
-
-      Core fields:
-      - `importers: Set<Node>` — roots of traversal (main project + workspaces)
-      - `mainImporter: Node` — the primary project importer
-      - `nodes: Map<DepID, Node>` — all nodes keyed by unique `DepID`
-      - `nodesByName: Map<string, Set<Node>>` — lookup by package name (deterministically sorted by DepID)
-      - `edges: Set<Edge>` — all edges across the graph
-      - `manifests: Map<DepID, NormalizedManifest>` — manifest inventory
-      - `resolutions: Map<string, Node>` / `resolutionsReverse: Map<Node, Set<string>>` — resolution caches
-      - `extraneousDependencies: Set<Edge>` — edges present on disk but not declared when loading Actual graphs
-      - `peerContexts: PeerContext[]` — array of peer context sets used for peer dependency resolution
-      - `currentPeerContextIndex: number` — tracks the current peer context index for unique hash generation
-
-      Important methods:
-      - `addNode(id?, manifest?, spec?, name?, version?)` — creates a node; populates indices and resolution cache; keeps `nodesByName` sorted by DepID
-      - `addEdge(type, spec, from, to?)` — creates/updates an edge; ensures spec naming; de-duplicates similar edges
-      - `placePackage(fromNode, depType, spec, manifest?, id?, extra?)` — high-level placement that either creates a missing edge (if no `manifest`/`id`) or ensures a node exists and connects the edge, setting dev/optional flags; splits `extra` into `modifier` and `peerSetHash`
-      - `findResolution(spec, fromNode, extra?)` — searches `nodesByName` for a satisfying node (via `@vltpkg/satisfies`), keyed by spec + from location + extra for caching
-      - `removeNode(node, replacement?, keepEdges?)` — deletes node and rewires or removes affected edges
-      - `removeEdgeResolution(edge, extra?)` — clears a specific cached resolution and potentially prunes the referenced node if orphaned
-      - `gc()` — trims unreachable nodes/edges not reachable from importers; used after optional failures
-      - `resetEdges()` — clears all edges while preserving nodes and resolution caches; marks nodes with manifests as `detached`; used when refreshing the ideal graph
-      - `nextPeerContextIndex()` — returns and increments `currentPeerContextIndex` for unique peer context identification
-      - `toJSON()` — serializes using `lockfileData()` to produce a stable, deterministic representation
-
-      Resolution cache key:
-      - `getResolutionCacheKey(spec.final, from.location, extra)`; file-based specs include `from.location` to avoid cross-importer leakage; `extra` combines modifier and peerSetHash
-
-  - type: architecture_guide
-    message: |
-      ## Node (`src/graph/src/node.ts`)
-
-      Identity and metadata:
-      - `id: DepID` — unique identity; from `getId(spec, manifest)` or explicit `id`
-      - `manifest?: NormalizedManifest` — may be undefined when not read (eg. Actual load without manifests)
-      - `name`, `version`, `integrity`, `resolved`, `registry`, `modifier`
-
-      Location and store model:
-      - `location: string` — defaults to `./node_modules/.vlt/<DepID>/node_modules/<name>` if not set
-      - `inVltStore()` — memoized check whether node is located in the store layout
-      - `nodeModules(scurry)` — directory where this node's dependencies are linked (store parent vs direct `node_modules`)
-      - `setImporterLocation(location)` — marks importer nodes and sets location
-      - `setDefaultLocation()` — relocates nodes into default store path when appropriate
-
-      Dependency flags and propagation:
-      - `dev` and `optional` flags indicate reachability via dev or optional/peerOptional edges
-      - Clearing `dev` or `optional` cascades to non-dev/non-optional children (ensures consistency)
-
-      State tracking:
-      - `detached = false` — marks nodes loaded from lockfile/actual that can be reused without manifest fetch; set by `graph.resetEdges()` for nodes with manifests
-      - `extracted = false` — tracks whether this node has been extracted to the file system
-      - `built = false` — legacy flag for build tracking
-      - `buildState: 'none' | 'needed' | 'built' | 'failed'` — granular build state tracking
-
-      Platform and binary info:
-      - `platform?: { engines?, os?, cpu? }` — platform requirements extracted from manifest; stored separately for optional deps to enable platform checks when manifest is not loaded
-      - `bins?: Record<string, string>` — binary names to their paths in the package
-
-      Peer dependency context:
-      - `peerSetHash?: string` — deterministic unique string identifying nodes affected by peer context modifications; appended to DepID as `extra` suffix (format: `peer.N`)
-
-      Workspaces:
-      - `workspaces: Map<string, Edge> | undefined` — only on `mainImporter`; maps workspace names to virtual edges connecting to workspace importer nodes
-
-      Confused manifests:
-      - `confused = false` — true if manifest name differs from requested spec name
-      - `maybeSetConfusedManifest(spec, manifest?)` sets `confused=true` when manifest name differs; preserves `rawManifest`
-
-  - type: architecture_guide
-    message: |
-      ## Edge (`src/graph/src/edge.ts`)
-
-      - `from: Node`, `to?: Node` — directed relation; `to` may be missing to model missing dependencies
-      - `type: DependencyTypeShort` — one of `prod | dev | peer | peerOptional | optional`
-      - `spec: Spec` — parsed from `@vltpkg/spec`; `spec.name` is enforced during creation for correctness
-      - Convenience flags: `dev`, `optional`, `peer`, `peerOptional`
-      - `valid()` checks satisfaction of `to.id` against `spec` using `@vltpkg/satisfies` with `from.location` and `projectRoot`
-
-  - type: data_format_guide
-    message: |
-      ## Public Type Shapes (`src/graph/src/types.ts`)
-
-      - `GraphLike` — minimal interface exposing graph fields and methods used by clients that should not depend on full implementation details
-      - `NodeLike` — minimal node shape with key fields (`id`, `edgesIn`, `edgesOut`, `manifest`, `location`, `name`, `platform`, `bins`, etc.) and behaviors (eg. `setResolved`, `maybeSetConfusedManifest`)
-      - `EdgeLike` — minimal edge shape including `from`, `spec`, `to?`, and flags
-
-      These types enable testing, visualization, and interop with modules like `ideal`, `actual`, `lockfile`, and `reify` without tightly coupling to class implementations.
-
-  - type: data_format_guide
-    message: |
-      ## Lockfile Types (`src/graph/src/lockfile/types.ts`)
-
-      Node representation:
-      - `LockfileNode` — tuple format: `[flags, name?, integrity?, resolved?, location?, manifest?, rawManifest?, platform?, bins?, buildState?]`
-      - `LockfileNodeFlags` — bit flags (0-3) for dev/optional combinations
-      - `LockfilePlatform` — `{ engines?, os?, cpu? }` for platform requirements
-      - `LockfileBuildState` — `undefined | 1 | 2 | 3` for none/needed/built/failed
-
-      Edge representation:
-      - `LockfileEdges` — record with key `${from.id} ${spec.name}` and value `${type} ${spec.bareSpec} ${to.id | 'MISSING'}`
-
-      Helper functions:
-      - `getFlagNumFromNode(node)` / `getBooleanFlagsFromNum(flags)` — convert between node flags and lockfile format
-      - `getBuildStateFromNode(node)` / `getBuildStateFromNum(state)` — convert between build state formats
-
-  - type: architecture_guide
-    message: |
-      ## Invariants and Modeling Notes
-
-      - Node identity (`DepID`) is unique across the graph; `nodes` map keys must not collide
-      - `nodesByName` collects multiple versions/locations of the same package name for resolution; kept sorted by DepID for deterministic resolution
-      - `edgesOut` is keyed by `spec.name`; Graph ensures spec name correctness, disallowing missing names for missing edges
-      - Missing dependencies are represented as edges with `to=undefined`
-      - Extraneous dependencies are tracked in `graph.extraneousDependencies` when loading Actual with manifests
-      - Resolution caching is extra-aware (includes both modifier and peerSetHash) to reflect modified specs
-      - Deterministic ordering is maintained in serialization to ensure stable lockfiles
-      - Peer contexts are tracked globally in `graph.peerContexts` array; each context has a unique `index` property
-
-  - type: development_workflow
-    message: |
-      ## Practical Usage Tips
-
-      - Prefer `placePackage()` for top-down placement (it handles node creation, flags, edges, and peer context)
-      - Use `findResolution()` before creating new nodes to reuse satisfying ones (crucial for Ideal builds)
-      - When removing nodes, consider `replacement` or `keepEdges` to preserve structure where valid
-      - After structural changes that may orphan nodes, use `gc()` to prune unreachable subgraphs
-      - Use `resetEdges()` when refreshing an ideal graph from modified dependencies; it preserves nodes for reuse
-      - When serializing, rely on `graph.toJSON()` which delegates to lockfile formatting for consistency
-      - Access peer contexts via `graph.peerContexts[index]`; use `graph.nextPeerContextIndex()` to generate unique indices
-
-examples:
-  - input: |
-      // Find a reusable node satisfying a spec before creating a new one
-      const reuse = graph.findResolution(spec, fromNode)
-      if (reuse) graph.addEdge('prod', spec, fromNode, reuse)
-    output: "Resolution cache leveraged; avoided unnecessary node creation"
-
-  - input: |
-      // Model a missing dependency
-      graph.addEdge('prod', spec, importer)
-    output: "Creates a dangling edge (to=undefined) representing a missing dep"
-
-  - input: |
-      // Place a package with peer context hash
-      import { joinExtra } from '@vltpkg/dep-id'
-      const extra = joinExtra({ peerSetHash: 'peer.1', modifier: undefined })
-      const node = graph.placePackage(fromNode, 'prod', spec, manifest, id, extra)
-    output: "Node placed with peer context tracking"
-
-  - input: |
-      // Refresh graph edges for ideal rebuild
-      if (add.modifiedDependencies || remove.modifiedDependencies) {
-        graph.resetEdges()
-      }
-    output: "Edges cleared; nodes with manifests marked detached for reuse"
-
-metadata:
-  priority: high
-  version: 2.0
-  tags:
-    - graph
-    - data-structures
-    - types
-    - nodes
-    - edges
-    - invariants
-    - peer-context
-    - lockfile
-  related_rules:
-    - graph_workspace_architecture
-    - graph_lockfiles
-    - graph_modifiers
-    - graph_load_actual
-    - graph_reify
-    - graph_peers
-    - monorepo-structure
-</rule>
+# Graph Data Structures
+
+## Graph (`graph.ts`)
+
+**Construction**: Seeds `mainImporter` from project root (`file:.` DepID), discovers workspaces, initializes peer contexts.
+
+**Fields:**
+- `importers: Set<Node>` — roots (main + workspaces)
+- `mainImporter: Node`
+- `nodes: Map<DepID, Node>`, `nodesByName: Map<string, Set<Node>>` (sorted by DepID)
+- `edges: Set<Edge>`, `manifests: Map<DepID, NormalizedManifest>`
+- `resolutions: Map<string, Node>` / `resolutionsReverse`
+- `extraneousDependencies: Set<Edge>`
+- `peerContexts: PeerContext[]`, `currentPeerContextIndex: number`
+
+**Key methods:**
+- `addNode()` — creates node, populates indices, keeps `nodesByName` sorted
+- `addEdge(type, spec, from, to?)` — creates/updates edge, de-duplicates
+- `placePackage(fromNode, depType, spec, manifest?, id?, extra?)` — high-level: creates node + edge, splits `extra` into `modifier`/`peerSetHash`
+- `findResolution(spec, fromNode, extra?)` — searches `nodesByName` for satisfying node, cached by spec+location+extra
+- `removeNode(node, replacement?, keepEdges?)`, `gc()` — prune unreachable
+- `resetEdges()` — clears edges, marks manifested nodes as `detached` for reuse
+- `nextPeerContextIndex()` — unique peer context ID generation
+- `toJSON()` → `lockfileData()` for deterministic serialization
+
+**Resolution cache key**: `getResolutionCacheKey(spec.final, from.location, extra)` — includes modifier+peerSetHash.
+
+## Node (`node.ts`)
+
+**Identity**: `id: DepID`, `manifest?`, `name`, `version`, `integrity`, `resolved`, `registry`, `modifier`
+
+**Location**: `location` (default: `./node_modules/.vlt/<DepID>/node_modules/<name>`), `inVltStore()` (memoized), `nodeModules(scurry)`, `setDefaultLocation()`
+
+**Flags**: `dev`, `optional` (cascade-clear to children), `detached`, `extracted`, `buildState: 'none'|'needed'|'built'|'failed'`
+
+**Platform/bins**: `platform?: { engines?, os?, cpu? }`, `bins?: Record<string, string>`
+
+**Peer**: `peerSetHash?: string` (format: `peer.N`, appended to DepID as `extra`)
+
+**Workspace**: `workspaces: Map<string, Edge>` (only on `mainImporter`)
+
+**Confused**: `confused = false` — true if manifest name ≠ spec name; preserves `rawManifest`
+
+## Edge (`edge.ts`)
+
+- `from: Node`, `to?: Node` (undefined = missing dep)
+- `type: DependencyTypeShort` — `prod | dev | peer | peerOptional | optional`
+- `spec: Spec` (name enforced at creation)
+- `valid()` — checks `to.id` satisfies `spec`
+
+## Public Types (`types.ts`)
+
+`GraphLike`, `NodeLike`, `EdgeLike` — minimal interfaces for loose coupling with consumers.
+
+## Lockfile Types (`lockfile/types.ts`)
+
+- `LockfileNode` tuple: `[flags, name?, integrity?, resolved?, location?, manifest?, rawManifest?, platform?, bins?, buildState?]`
+- `LockfileEdges`: `{ "${from.id} ${spec.name}": "${type} ${spec.bareSpec} ${to.id | 'MISSING'}" }`
+- Flags: 0=prod, 1=optional, 2=dev, 3=devOptional
+- Helpers: `getFlagNumFromNode()`, `getBooleanFlagsFromNum()`, `getBuildStateFromNode()`
+
+## Invariants
+
+- DepID uniqueness in `nodes` map
+- `edgesOut` keyed by `spec.name`; missing deps = `to=undefined`
+- Resolution cache is extra-aware (modifier+peerSetHash)
+- Deterministic ordering → stable lockfiles
diff --git a/.cursor/rules/graph/ideal-append-nodes.mdc b/.cursor/rules/graph/ideal-append-nodes.mdc
@@ -3,736 +3,81 @@ description: Breadth-first dependency graph building with peer context managemen
 globs: src/graph/src/ideal/append-nodes.ts,src/graph/src/ideal/refresh-ideal-graph.ts,src/graph/src/ideal/types.ts
 alwaysApply: false
 ---
-# Graph Ideal Append Nodes Architecture
+# Append Nodes Architecture
 
-Detailed guide for understanding and working with the `append-nodes.ts` module in `@vltpkg/graph`, which implements breadth-first dependency graph building with deterministic ordering and peer dependency context management.
+Core BFS graph builder in `src/graph/src/ideal/append-nodes.ts`.
 
-<rule>
-name: graph_ideal_append_nodes
-description: Architecture and implementation guide for the append-nodes module that builds dependency graphs in breadth-first order with peer context handling
-filters:
-  # Target the append-nodes module specifically
-  - type: path
-    pattern: "^src/graph/src/ideal/append-nodes\\.ts$"
-  # Target files that import or use appendNodes
-  - type: content
-    pattern: "import.*appendNodes|from.*append-nodes"
-  # Target files working with graph ideal building
-  - type: path
-    pattern: "^src/graph/src/ideal/"
-  # Target peer context related content
-  - type: content
-    pattern: "peerContext|peerSetHash|startPeerPlacement|endPeerPlacement|postPlacementPeerCheck"
+## 3-Phase BFS Loop (per level)
 
-actions:
-  - type: guide
-    message: |
-      ## Overview
+### Phase A: Parallel Fetch (read-only)
+`fetchManifestsForDeps()` fetches manifests without graph mutations. Returns `FetchResult`:
+- `placementTasks: NodePlacementTask[]` — nodes to place
+- `reuseTasks: ReuseTask[]` — deferred edge creation for existing nodes
+- `forkRequests: PeerContextEntryInput[]` — accumulated peer context fork entries
 
-      The `append-nodes.ts` module implements the core dependency graph building logic for the Ideal Graph construction phase. It processes dependencies in **breadth-first order** with **deterministic ordering** to ensure reproducible graph builds, while managing **peer dependency contexts** to handle version conflicts.
+### Phase B: Serial Mutations (deterministic)
+Sort results by `${node.id}::${depth}`. For each (in order):
+1. Apply `forkRequests` → `forkPeerContext()`
+2. Apply `reuseTasks` → `graph.addEdge()` (sorted)
+3. `processPlacementTasks()`:
+   - `startPeerPlacement()` → get `peerSetHash` + queued entries
+   - `graph.placePackage(from, type, spec, manifest, id, joinExtra({ peerSetHash, modifier }))`
+   - `endPeerPlacement()` → get `{ putEntries, resolvePeerDeps }` for Phase C
 
-      ### Key Responsibilities
-      - Fetch manifests for dependencies in parallel
-      - Place nodes in the graph with proper edges
-      - Handle modifiers, optional dependencies, and error conditions
-      - Process child dependencies level by level
-      - Maintain deterministic ordering for reproducible builds
-      - **Manage peer dependency contexts** to handle incompatible peer versions
-      - **Track and fork peer contexts** when version conflicts arise
-      - **Resolve peer dependencies** using context-aware node lookup
+### Phase C: Post-Placement Peer Check
+`postPlacementPeerCheck(graph, levelResults)`:
+1. `putEntries()` on all children → detect which need forking
+2. Fork/reuse sibling contexts
+3. `resolvePeerDeps()` from context
 
-      📋 **See `@graph/peers.mdc`** for detailed peer dependency isolation and `peerSetHash` mechanisms
+## Workspace Peer Isolation
 
-  - type: architecture_guide
-    message: |
-      ## Core Architecture
+Non-main importers get fresh peer contexts:
+```typescript
+if (fromNode.importer && fromNode !== graph.mainImporter) {
+  const nextPeerContext: PeerContext = new Map()
+  nextPeerContext.index = graph.nextPeerContextIndex()
+  initialPeerContext = nextPeerContext
+}
+```
 
-      The module uses a **3-phase BFS loop** for deterministic graph building:
+## Existing Edge Preference (Idempotency)
 
-      ### PHASE A: PARALLEL FETCH (READ-ONLY)
-      ```typescript
-      // Fetches manifests without mutating the graph
-      const fetchResults = await Promise.all(
-        currentLevelDeps.map(async ({ node, deps, peerContext, ... }) => {
-          const result = await fetchManifestsForDeps(
-            packageInfo, graph, node, sortedDeps, scurry, peerContext, modifierRefs, depth
-          )
-          return { entry, result }  // result: { placementTasks, reuseTasks, forkRequests }
-        })
-      )
-      ```
-      - **Read-only**: No graph mutations during parallel fetch
-      - Returns `FetchResult` with deferred tasks instead of immediately applying changes
-      - `reuseTasks`: Deferred edge creation for existing node reuse
-      - `forkRequests`: Accumulated peer context fork entries
-      - Prevents race conditions from network timing variations
+```typescript
+const existingEdge = fromNode.edgesOut.get(spec.name)
+if (existingEdge?.to && !existingEdge.to.detached && satisfiesFinal(existingEdge.to)) {
+  existingNode = existingEdge.to  // Preserve lockfile resolution
+} else {
+  existingNode = graph.findResolution(spec, fromNode, queryModifier)
+}
+```
 
-      ### PHASE B: SERIAL MUTATIONS (DETERMINISTIC ORDER)
-      ```typescript
-      // Sort by stable identifiers for deterministic ordering
-      const sortedResults = fetchResults.sort((a, b) => {
-        const keyA = `${a.entry.node.id}::${a.entry.depth}`
-        const keyB = `${b.entry.node.id}::${b.entry.depth}`
-        return keyA.localeCompare(keyB, 'en')
-      })
+## Candidate Fallback (Peer-Incompatible)
 
-      // Apply mutations serially
-      for (const { entry, result } of sortedResults) {
-        // 1. Apply accumulated fork requests
-        if (result.forkRequests.length > 0) {
-          entry.peerContext = forkPeerContext(graph, entry.peerContext, result.forkRequests)
-        }
-        // 2. Apply reuse edges in sorted order
-        for (const { type, spec, fromNode, toNode } of sortedReuseTasks) {
-          graph.addEdge(type, spec, fromNode, toNode)
-        }
-        // 3. Place nodes and collect child deps
-        const placed = await processPlacementTasks(graph, options, result.placementTasks, ...)
-        levelResults.push(placed)
-      }
-      ```
-      - Sorts results by DepID-based keys for stability
-      - Applies all mutations in deterministic order regardless of fetch completion order
+If first satisfying node fails peer check, lazy-load `graph.nodesByName.get(name)` candidates and try each until compatible one found.
 
-      ### PHASE C: POST-PLACEMENT PEER CHECK
-      ```typescript
-      postPlacementPeerCheck(graph, levelResults)
-      ```
-      - Calls `putEntries()` on all children to update peer contexts
-      - Forks contexts when conflicts detected, reuses sibling contexts when compatible
-      - Calls `resolvePeerDeps()` to resolve peer deps from context
+## Error Handling
 
-      ### Helper Functions
-      - `fetchManifestsForDeps()`: **Read-only** manifest fetching, returns `FetchResult`
-      - `processPlacementTasks()`: Serial node placement with peer lifecycle
+- **Optional deps**: `removeOptionalSubgraph()` if parent is optional; skip if edge is optional; throw if required
+- **Cycles**: `seen` Set checked before queueing children
+- **Nameless deps**: `fixupAddedNames()` for specs like `github:foo/bar`
 
-  - type: peer_integration_guide
-    message: |
-      ## Peer Dependency Integration
+## Modifier Integration
 
-      The append-nodes module integrates tightly with the peer dependency system (`peers.ts`) through a 3-step workflow:
+Check `activeModifier?.interactiveBreadcrumb.current === modifier.breadcrumb.last` for complete match. If complete and has `spec`, swap it. If `spec.bareSpec === '-'`, skip dep entirely. After placement: `modifiers.updateActiveEntry(node, active)`.
 
-      ### Step 1: Pre-Placement Compatibility Check (`fetchManifestsForDeps`)
-      ```typescript
-      // Check if existing node's peer edges are compatible with new parent
-      const peerCompatResult = existingNode ?
-        checkPeerEdgesCompatible(existingNode, fromNode, peerContext, graph)
-        : { compatible: true }
+## Key Types
 
-      // Accumulate fork request (deferred - applied in Phase B)
-      if (!peerCompatResult.compatible && peerCompatResult.forkEntry) {
-        forkRequests.push(peerCompatResult.forkEntry)
-        // Fork will be applied together with other fork requests from this fromNode
-      }
-      ```
-      - Validates that reusing an existing node won't cause peer version conflicts
-      - Returns `forkEntry` containing the conflicting spec and target when incompatible
-      - **Deferred**: Fork requests are accumulated, not applied immediately (read-only phase)
-      - Prevents incorrect node reuse that would break peer dependency contracts
+```typescript
+type FetchResult = { placementTasks: NodePlacementTask[], reuseTasks: ReuseTask[], forkRequests: PeerContextEntryInput[] }
+type ReuseTask = { type: DependencySaveType, spec: Spec, fromNode: Node, toNode: Node }
+type AppendNodeEntry = { node: Node, deps: Dependency[], depth: number, peerContext: PeerContext, updateContext: { putEntries, resolvePeerDeps }, modifierRefs? }
+type PeerContext = Map<string, PeerContextEntry> & { index?: number }
+```
 
-      ### Step 2: Peer Placement Lifecycle (`processPlacementTasks`)
-      ```typescript
-      // START: Collect sibling deps and calculate peerSetHash
-      const { peerSetHash, queuedEntries } = startPeerPlacement(
-        peerContext, manifest, fromNode, options
-      )
+## Performance
 
-      // Place node with peer context hash
-      const node = graph.placePackage(
-        fromNode, type, spec, manifest, id,
-        joinExtra({ peerSetHash, modifier: queryModifier })
-      )
-
-      // END: Get context update functions for post-processing
-      const updateContext = endPeerPlacement(
-        peerContext, nextDeps, nextPeerDeps, graph, spec, fromNode, node, type, queuedEntries
-      )
-      ```
-      - `startPeerPlacement()`: Collects sibling dependencies, generates `peerSetHash` if manifest has peer deps
-      - `endPeerPlacement()`: Returns `{ putEntries, resolvePeerDeps }` functions for deferred execution
-
-      ### Step 3: Post-Level Peer Resolution (`appendNodes`)
-      ```typescript
-      // After processing all placement tasks at a level
-      postPlacementPeerCheck(graph, levelResults)
-      ```
-      - Calls `putEntries()` on all children to update peer contexts
-      - Detects which children need forked contexts and creates them
-      - Reuses sibling contexts when compatible (avoids unnecessary forking)
-      - Calls `resolvePeerDeps()` to resolve peer deps from context or add to next level
-
-      📋 **See `@graph/peers.mdc`** for `PeerContext`, `PeerContextEntry`, and forking algorithms
-
-  - type: data_structures_guide
-    message: |
-      ## Key Data Structures
-
-      ### `FetchResult` (returned by `fetchManifestsForDeps`)
-      ```typescript
-      type FetchResult = {
-        placementTasks: NodePlacementTask[]  // Nodes to place
-        reuseTasks: ReuseTask[]              // Deferred edge creation for existing nodes
-        forkRequests: PeerContextEntryInput[] // Accumulated peer context fork entries
-      }
-      ```
-      This structure enables read-only parallel fetching with deferred mutations.
-
-      ### `ReuseTask` (deferred edge creation)
-      ```typescript
-      type ReuseTask = {
-        type: DependencySaveType  // Edge type (prod, dev, etc.)
-        spec: Spec                // Dependency spec
-        fromNode: Node            // Parent node
-        toNode: Node              // Existing node to reuse
-      }
-      ```
-      Previously `graph.addEdge()` was called immediately during parallel fetch, causing
-      non-determinism. Now edges are collected and applied serially in Phase B.
-
-      ### `AppendNodeEntry` (defined in `types.ts`)
-      ```typescript
-      type AppendNodeEntry = {
-        node: Node                  // The node whose dependencies to process
-        deps: Dependency[]          // Dependencies to fetch and place
-        modifierRefs?: Map<string, ModifierActiveEntry>  // Active modifiers
-        depth: number               // Current processing depth
-        peerContext: PeerContext    // Current peer dependency context
-        updateContext: {            // Peer context update functions
-          putEntries: () => PeerContextEntryInput[] | undefined  // Add to context, return entries if fork needed
-          resolvePeerDeps: () => void  // Resolve peer deps from context
-        }
-      }
-      ```
-
-      ### `ManifestFetchTask`
-      ```typescript
-      type ManifestFetchTask = {
-        spec: Spec                                    // Dependency spec
-        type: DependencySaveType                      // Dependency type (prod, dev, etc.)
-        fromNode: Node                                // Parent node
-        fileTypeInfo?: FileTypeInfo                   // File spec info
-        activeModifier?: ModifierActiveEntry          // Active modifier
-        queryModifier?: string                        // Modifier query
-        edgeOptional: boolean                         // Is optional dependency
-        manifestPromise: Promise<Manifest | undefined> // Async manifest fetch
-        depth: number                                 // Processing depth
-        peerContext: PeerContext                      // Peer context for this fetch
-      }
-      ```
-
-      ### `NodePlacementTask`
-      ```typescript
-      type NodePlacementTask = {
-        fetchTask: ManifestFetchTask      // Original fetch context
-        manifest: Manifest | undefined    // Resolved manifest
-        node?: Node                       // Created node (set during processing)
-        childDeps?: Dependency[]          // Child dependencies to process
-        childModifierRefs?: Map<string, ModifierActiveEntry> // Child modifier refs
-        childPeerContext?: PeerContext    // Peer context for children
-      }
-      ```
-
-      ### `PeerContext` (from `types.ts`)
-      ```typescript
-      type PeerContext = Map<string, PeerContextEntry> & {
-        index?: number  // Unique index for peerSetHash generation
-      }
-      ```
-
-  - type: processing_flow_guide
-    message: |
-      ## Processing Flow with Peer Context
-
-      ### 1. Entry Point
-      ```typescript
-      appendNodes(packageInfo, graph, fromNode, deps, scurry, options, seen, add, modifiers, modifierRefs, ...)
-      ```
-      - **Input**: Node and its dependencies to process
-      - **Output**: Fully built graph with all transitive dependencies and resolved peer contexts
-
-      ### 2. Initial Peer Context Setup
-      ```typescript
-      // Get the initial peer context from the graph (main importer uses index 0)
-      let initialPeerContext = graph.peerContexts[0]
-      
-      // WORKSPACE ISOLATION: Non-main importers get fresh peer contexts
-      // This prevents cross-workspace peer leakage (e.g., root's react@18 affecting workspace's react@19)
-      if (fromNode.importer && fromNode !== graph.mainImporter) {
-        const nextPeerContext: PeerContext = new Map()
-        nextPeerContext.index = graph.nextPeerContextIndex()
-        graph.peerContexts[nextPeerContext.index] = nextPeerContext
-        initialPeerContext = nextPeerContext
-      }
-      
-      let currentLevelDeps: AppendNodeEntry[] = [{
-        node: fromNode,
-        deps,
-        modifierRefs,
-        depth: 0,
-        peerContext: initialPeerContext,
-        updateContext: { putEntries: () => undefined, resolvePeerDeps: () => {} }
-      }]
-      ```
-
-      ### 3. Level Processing Loop (3-Phase per Level)
-      ```typescript
-      while (currentLevelDeps.length > 0) {
-        // ========== PHASE A: PARALLEL FETCH (READ-ONLY) ==========
-        const fetchResults = await Promise.all(currentLevelDeps.map(async ({ node, deps, peerContext, ... }) => {
-          seen.add(node.id)
-          // Fetch manifests without mutating graph - returns FetchResult
-          const result = await fetchManifestsForDeps(packageInfo, graph, node, sortedDeps, ...)
-          return { entry: { node, deps, peerContext, ... }, result }
-        }))
-
-        // ========== PHASE B: SERIAL MUTATIONS (DETERMINISTIC) ==========
-        // Sort by stable identifiers (DepID::depth)
-        const sortedResults = fetchResults.sort((a, b) => 
-          `${a.entry.node.id}::${a.entry.depth}`.localeCompare(`${b.entry.node.id}::${b.entry.depth}`, 'en')
-        )
-
-        const levelResults = []
-        for (const { entry, result } of sortedResults) {
-          // Apply fork requests, reuse edges, and place nodes serially
-          if (result.forkRequests.length > 0) {
-            entry.peerContext = forkPeerContext(graph, entry.peerContext, result.forkRequests)
-          }
-          for (const reuseTask of sortedReuseTasks) graph.addEdge(...)
-          levelResults.push(await processPlacementTasks(...))
-        }
-
-        // ========== PHASE C: POST-PLACEMENT PEER CHECK ==========
-        postPlacementPeerCheck(graph, levelResults)
-
-        // Collect child dependencies for next level
-        currentLevelDeps = collectChildDependencies(levelResults)
-      }
-      ```
-
-      ### 4. Peer Context Flow Diagram (3-Phase Architecture)
-      ```
-      Initial Context (index: 0)
-             │
-             ▼
-      ┌─────────────────────────────────────────┐
-      │ PHASE A: PARALLEL FETCH (READ-ONLY)     │
-      │  - fetchManifestsForDeps() in parallel  │
-      │    ├─ checkPeerEdgesCompatible()        │
-      │    ├─ Accumulate forkRequests (deferred)│
-      │    └─ Accumulate reuseTasks (deferred)  │
-      │  - Returns FetchResult per entry        │
-      └─────────────────────────────────────────┘
-             │
-             ▼
-      ┌─────────────────────────────────────────┐
-      │ PHASE B: SERIAL MUTATIONS (DETERMINISTIC)│
-      │  - Sort results by DepID::depth         │
-      │  - For each (in order):                 │
-      │    ├─ Apply forkRequests → forkPeerContext│
-      │    ├─ Apply reuseTasks → graph.addEdge  │
-      │    └─ processPlacementTasks()           │
-      │        ├─ startPeerPlacement() → hash   │
-      │        └─ endPeerPlacement() → context  │
-      └─────────────────────────────────────────┘
-             │
-             ▼
-      ┌─────────────────────────────────────────┐
-      │ PHASE C: POST-PLACEMENT PEER CHECK      │
-      │  - putEntries() for each child          │
-      │  - forkPeerContext() if conflicts       │
-      │  - resolvePeerDeps() from context       │
-      └─────────────────────────────────────────┘
-             │
-             ▼
-      Level N+1 Processing (repeat)
-      ```
-
-  - type: error_handling_guide
-    message: |
-      ## Error Handling Patterns
-
-      ### Optional Dependency Failures
-      ```typescript
-      if (!manifest) {
-        if (!edgeOptional && fromNode.isOptional()) {
-          // Remove the entire optional subgraph
-          removeOptionalSubgraph(graph, fromNode)
-          continue
-        } else if (edgeOptional) {
-          // Ignore failed optional deps
-          continue
-        } else {
-          // Hard failure for required dependencies
-          throw error('failed to resolve dependency', { spec, from: fromNode.location })
-        }
-      }
-      ```
-
-      ### Cycle Prevention
-      ```typescript
-      // Mark nodes as seen when processing starts (not when complete)
-      seen.add(node.id)
-
-      // Check before adding to next level
-      if (!seen.has(childDep.node.id)) {
-        nextLevelDeps.push(childDep)
-      }
-      ```
-
-      ### Peer Dependency Node Reuse Validation
-      ```typescript
-      // Defines what nodes are eligible to be reused
-      const validExistingNode =
-        existingNode &&
-        !existingNode.detached &&
-        // Regular deps can always reuse.
-        // Peer deps can reuse as well if their peer edges are compatible.
-        (!peer || peerCompatResult.compatible) &&
-        // Check peer edge compatibility
-        peerCompatResult.compatible
-      ```
-      **Note**: Reuse is deferred - `reuseTasks` are collected during Phase A and
-      applied serially in Phase B for deterministic ordering.
-
-      ### Existing Edge Preference (Lockfile Idempotency)
-      ```typescript
-      // Prefer existing edge target if it satisfies the spec
-      // This ensures lockfile resolutions are preserved when still valid
-      const existingEdge = fromNode.edgesOut.get(spec.name)
-      let existingNode: Node | undefined
-      if (existingEdge?.to && !existingEdge.to.detached && satisfiesFinal(existingEdge.to)) {
-        existingNode = existingEdge.to  // Use locked resolution
-      } else {
-        existingNode = graph.findResolution(spec, fromNode, queryModifier)
-      }
-      ```
-      This ensures idempotency: re-running ideal graph building on a lockfile produces identical results.
-
-      ### Candidate Fallback for Peer-Incompatible Nodes
-      ```typescript
-      // Lazy-load candidates only when fallback needed (performance optimization)
-      if (existingNode && !peerCompatResult.compatible) {
-        const candidates = graph.nodesByName.get(final.name)
-        if (candidates && candidates.size > 1) {
-          for (const candidate of candidates) {
-            if (candidate === existingNode) continue  // Skip already checked
-            if (candidate.detached) continue          // Skip stale nodes
-            if (!satisfiesFinal(candidate)) continue  // Skip non-satisfying (memoized)
-            
-            const compat = checkPeerEdgesCompatible(candidate, fromNode, peerContext, graph)
-            if (compat.compatible) {
-              existingNode = candidate
-              peerCompatResult = compat
-              break
-            }
-          }
-        }
-      }
-      ```
-      This is crucial for multi-workspace scenarios where different workspaces may need different peer contexts.
-
-      ### Nameless Dependencies
-      ```typescript
-      // Handle specs like 'github:foo/bar' that don't specify a name
-      spec = fixupAddedNames(additiveMap, manifest, options, spec)
-      ```
-
-  - type: modifier_integration_guide
-    message: |
-      ## Modifier System Integration
-
-      ### Spec Swapping
-      ```typescript
-      // Check if a modifier should replace the spec
-      const queryModifier = activeModifier?.modifier.query
-      const completeModifier = activeModifier?.interactiveBreadcrumb.current ===
-                               activeModifier.modifier.breadcrumb.last
-
-      if (queryModifier && completeModifier && 'spec' in activeModifier.modifier) {
-        spec = activeModifier.modifier.spec
-        if (spec.bareSpec === '-') {
-          continue  // Skip this dependency
-        }
-      }
-      ```
-
-      ### Modifier and Peer Context Combined
-      ```typescript
-      // Both modifier query and peerSetHash are combined in the extra parameter
-      const node = graph.placePackage(
-        fromNode,
-        type,
-        spec,
-        normalizeManifest(manifest),
-        fileTypeInfo?.id,
-        joinExtra({ peerSetHash, modifier: queryModifier })  // Combined extra
-      )
-      ```
-
-      ### Modifier Updates
-      ```typescript
-      // Update modifier state after node placement
-      if (activeModifier) {
-        modifiers?.updateActiveEntry(node, activeModifier)
-      }
-
-      // Generate modifier refs for child dependencies
-      childModifierRefs = modifiers?.tryDependencies(node, nextDeps)
-      ```
-
-  - type: performance_optimization_guide
-    message: |
-      ## Performance Characteristics
-
-      ### Parallel Processing
-      - **Level Parallelism**: All nodes at the same depth processed simultaneously
-      - **Manifest Fetching**: All manifests for a level fetched in parallel
-      - **I/O Batching**: Reduces network round trips compared to depth-first
-
-      ### Memory Efficiency
-      - **Streaming Processing**: Processes level by level, not all at once
-      - **Seen Set**: Prevents duplicate processing and infinite cycles
-      - **Shared References**: Reuses existing nodes via `graph.findResolution()`
-      - **Peer Context Reuse**: Attempts to reuse sibling peer contexts before forking
-
-      ### Deterministic Ordering
-      - **Reproducible Builds**: Same input always produces same graph structure
-      - **Read-Only Fetch Phase**: No mutations during parallel network operations prevents timing-based non-determinism
-      - **Stable Sorting Keys**: Results sorted by `DepID::depth` before applying mutations
-      - **Deferred Edge Creation**: Reuse edges collected and applied in sorted order
-      - **Sorted Peer Context Processing**: `postPlacementPeerCheck` sorts by `node.id` for determinism
-      - **Debug Friendly**: Deterministic processing aids in debugging
-
-      ### Early Extraction
-      - Eligible nodes can be extracted to vlt store during graph building
-      - Extraction happens in parallel with graph construction
-      - Skips peer dependencies and optional dependencies for extraction
-
-  - type: integration_patterns
-    message: |
-      ## Integration with Graph System
-
-      ### Used By
-      - `src/graph/src/ideal/refresh-ideal-graph.ts` - High-level dependency resolution
-      - `src/graph/src/ideal/build-ideal-from-starting-graph.ts` - Ideal graph construction
-
-      ### Dependencies from `peers.ts`
-      - `checkPeerEdgesCompatible()` - Validate existing node peer compatibility
-      - `forkPeerContext()` - Create new peer context when conflicts arise
-      - `startPeerPlacement()` - Begin peer placement, get peerSetHash and queued entries
-      - `endPeerPlacement()` - End peer placement, get updateContext functions
-      - `postPlacementPeerCheck()` - Post-level peer context updates and resolution
-
-      ### Dependencies from Graph Core
-      - `graph.findResolution()` - Find existing satisfying nodes
-      - `graph.placePackage()` - Place new nodes with edges and extra (modifier + peerSetHash)
-      - `graph.addEdge()` - Create edges to existing nodes
-      - `graph.peerContexts` - Array of peer contexts tracked by the graph
-      - `graph.nextPeerContextIndex()` - Get next unique peer context index
-
-      ### Dependencies from Other Modules
-      - `removeOptionalSubgraph()` - Handle optional failures
-      - `joinExtra()` - Combine modifier and peerSetHash into extra parameter
-      - `fixupAddedNames()` - Handle nameless dependencies
-
-      ### Data Flow
-      ```
-      refresh-ideal-graph.ts
-             │
-             ▼
-      appendNodes()
-             │
-      ┌──────┴──────────────────────────────────────┐
-      │ PHASE A: PARALLEL FETCH (READ-ONLY)         │
-      │  fetchManifestsForDeps() → FetchResult      │
-      │    ├─► checkPeerEdgesCompatible()           │
-      │    ├─► Accumulate forkRequests              │
-      │    └─► Accumulate reuseTasks                │
-      └──────┬──────────────────────────────────────┘
-             │
-      ┌──────┴──────────────────────────────────────┐
-      │ PHASE B: SERIAL MUTATIONS                   │
-      │  Sort results by DepID::depth               │
-      │    ├─► forkPeerContext() (apply forkRequests)│
-      │    ├─► graph.addEdge() (apply reuseTasks)   │
-      │    └─► processPlacementTasks()              │
-      │          ├─► startPeerPlacement()           │
-      │          ├─► graph.placePackage()           │
-      │          └─► endPeerPlacement()             │
-      └──────┬──────────────────────────────────────┘
-             │
-      ┌──────┴──────────────────────────────────────┐
-      │ PHASE C: POST-PLACEMENT                     │
-      │  postPlacementPeerCheck()                   │
-      │    ├─► putEntries()                         │
-      │    ├─► forkPeerContext() (if conflicts)     │
-      │    └─► resolvePeerDeps()                    │
-      └─────────────────────────────────────────────┘
-      ```
-
-  - type: testing_considerations
-    message: |
-      ## Testing and Debugging
-
-      ### Test Coverage Requirements
-      - **100% Coverage**: All paths must be tested including error conditions
-      - **Edge Cases**: Optional failures, cycles, nameless deps, modifiers
-      - **Peer Context Cases**: Context forking, peerSetHash generation, peer resolution
-      - **Deterministic Output**: Tests verify consistent ordering
-
-      ### Peer-Related Test Cases
-      1. **Peer Edge Compatibility**: Test `checkPeerEdgesCompatible()` with compatible/incompatible scenarios
-      2. **Context Forking**: Verify `forkPeerContext()` creates isolated contexts
-      3. **PeerSetHash Assignment**: Confirm nodes with peer deps get correct peerSetHash
-      4. **Sibling Context Reuse**: Test that compatible siblings share peer contexts
-      5. **Peer Resolution from Context**: Verify peer deps resolve from context when satisfied
-      6. **Candidate Fallback**: Test that peer-incompatible first candidates trigger fallback loop
-      7. **Workspace Isolation**: Verify non-main importers get fresh peer contexts
-      8. **Fork Cache**: Test that `graph.peerContextForkCache` prevents duplicate contexts
-      9. **Lockfile Idempotency**: Test that existing edge targets are preferred when valid
-      10. **Context Mismatch Tolerance**: Verify compatible despite context/sibling having different targets
-
-      ### Common Issues
-      1. **Cycle Detection**: Ensure `seen` set is managed correctly
-      2. **Optional Handling**: Verify optional subgraph removal works
-      3. **Manifest Errors**: Test both network and parsing failures
-      4. **Modifier State**: Ensure modifiers are updated correctly
-      5. **Peer Context Leaks**: Verify forked contexts don't affect parent contexts
-      6. **Idempotency**: Re-running ideal build on same lockfile should produce identical graph
-
-      ### Debugging Tips
-      - Check `seen` set state for cycle issues
-      - Verify deterministic ordering with different input orders
-      - Trace level-by-level processing for dependency issues
-      - Monitor `graph.nodes` and `graph.edges` growth
-      - Inspect `graph.peerContexts` array for context forking behavior
-      - Check `node.peerSetHash` values to trace peer context assignments
-      - Check `graph.peerContextForkCache` size for fork efficiency
-      - Verify `graph.peerContexts.length > 1` for multi-workspace isolation
-
-examples:
-  - input: |
-      // Example: Adding a new dependency with peer context awareness
-      await appendNodes(
-        packageInfo,         // manifest fetcher
-        graph,               // target graph
-        importerNode,        // starting node
-        [{ spec: reactDomSpec, type: 'prod' }], // dependencies
-        scurry,              // path resolver
-        options,             // spec options
-        new Set(),           // seen set
-        add,                 // add map
-        modifiers,           // modifier system
-        modifierRefs,        // active modifier refs
-        extractPromises,     // early extraction promises
-        actual,              // actual graph for extraction
-        seenExtracted,       // extraction tracking set
-        remover,             // rollback remover
-        transientAdd,        // transient additions
-        transientRemove      // transient removals
-      )
-    output: "Breadth-first processing with peer context management and early extraction"
-
-  - input: |
-      // Example: Processing with peer context lifecycle (3-phase architecture)
-      // PHASE A - In fetchManifestsForDeps (read-only):
-      const peerCompatResult = checkPeerEdgesCompatible(existingNode, fromNode, peerContext, graph)
-      if (!peerCompatResult.compatible) {
-        forkRequests.push(peerCompatResult.forkEntry)  // Deferred, not applied yet
-      }
-      if (validExistingNode) {
-        reuseTasks.push({ type, spec, fromNode, toNode: existingNode })  // Deferred edge
-      }
-      return { placementTasks, reuseTasks, forkRequests }
-
-      // PHASE B - Serial mutations (deterministic order):
-      if (result.forkRequests.length > 0) {
-        entry.peerContext = forkPeerContext(graph, entry.peerContext, result.forkRequests)
-      }
-      for (const { type, spec, fromNode, toNode } of sortedReuseTasks) {
-        graph.addEdge(type, spec, fromNode, toNode)
-      }
-
-      // In processPlacementTasks:
-      const { peerSetHash, queuedEntries } = startPeerPlacement(peerContext, manifest, fromNode, options)
-      const node = graph.placePackage(fromNode, type, spec, manifest, id, joinExtra({ peerSetHash, modifier }))
-      const updateContext = endPeerPlacement(...)
-
-      // PHASE C - Post-placement:
-      postPlacementPeerCheck(graph, levelResults)
-    output: "Complete peer context lifecycle with read-only fetch and serial mutations"
-
-  - input: |
-      // Example: Post-placement peer check with context forking
-      // From postPlacementPeerCheck in peers.ts
-      for (const childDep of sortedChildDeps) {
-        const needsFork = childDep.updateContext.putEntries()
-        if (needsFork) {
-          needsForking.set(childDep, needsFork)
-        }
-      }
-
-      for (const [childDep, nextEntries] of sortedNeedsForkingEntries) {
-        if (prevContext && !checkEntriesToPeerContext(prevContext, nextEntries)) {
-          // Reuse sibling's context
-          childDep.peerContext = prevContext
-        } else {
-          // Fork new context
-          childDep.peerContext = forkPeerContext(graph, childDep.peerContext, nextEntries)
-          prevContext = childDep.peerContext
-        }
-      }
-
-      for (const childDep of sortedChildDeps) {
-        childDep.updateContext.resolvePeerDeps()
-      }
-    output: "Post-placement peer context forking and resolution with sibling context reuse"
-
-  - input: |
-      // Example: Testing workspace peer context isolation
-      // Each workspace importer should get its own peer context
-      const mainReactEdge = graph.mainImporter.edgesOut.get('react')
-      const wsReactEdge = wsImporter.edgesOut.get('react')
-      
-      t.equal(mainReactEdge?.to?.version, '18.3.1', 'main importer should have react@18')
-      t.equal(wsReactEdge?.to?.version, '19.2.0', 'workspace importer should have react@19')
-      t.ok(graph.peerContexts.length > 1, 'should have multiple peer contexts for isolation')
-    output: "Verified workspace peer context isolation prevents cross-workspace leakage"
-
-  - input: |
-      // Example: Candidate fallback when first satisfying node is peer-incompatible
-      // Setup: multiple foo candidates with different peer targets
-      const peerContext = graph.peerContexts[0]
-      peerContext.set('react', { target: react183, ... })  // Context expects react@18.3
-      
-      // foo@1.0.0 has peer edge to react@18.2 (incompatible)
-      // foo@1.0.2 has peer edge to react@18.3 (compatible)
-      await appendNodes(packageInfo, graph, mainImporter, [fooDep], ...)
-      
-      const edge = graph.mainImporter.edgesOut.get('foo')
-      t.equal(edge?.to?.id, foo102.id, 'should skip incompatible foo@1.0.0, use foo@1.0.2')
-    output: "Candidate fallback selects peer-compatible node over first satisfying node"
-
-metadata:
-  priority: high
-  version: 2.3
-  tags:
-    - graph
-    - ideal
-    - append-nodes
-    - breadth-first
-    - dependencies
-    - modifiers
-    - deterministic
-    - parallel
-    - peer-dependencies
-    - peer-context
-    - idempotency
-  related_rules:
-    - graph_data_structure
-    - graph_ideal
-    - graph_modifiers
-    - graph_peers
-    - graph_lockfiles
-    - monorepo_structure
-</rule>
+- Level parallelism for manifest fetching
+- Read-only fetch phase prevents timing-based non-determinism
+- `seen` Set prevents cycles and duplicate work
+- Early extraction for new nodes during graph building (skip peer/optional deps)
diff --git a/.cursor/rules/graph/ideal.mdc b/.cursor/rules/graph/ideal.mdc
@@ -5,195 +5,52 @@ alwaysApply: false
 ---
 # Building Ideal Graphs
 
-Guidance for working with the Ideal Graph builder in `@vltpkg/graph`, which produces the desired end-state graph used for installs.
-
-<rule>
-name: graph_ideal
-description: How Ideal graphs are constructed, merged with add/remove, and expanded via remote manifests
-filters:
-  # Ideal builder implementation and helpers
-  - type: path
-    pattern: "^src/graph/src/ideal/"
-  - type: file_name
-    pattern: "^(build|build-ideal-from-starting-graph|append-nodes|get-importer-specs|remove-satisfied-specs|refresh-ideal-graph|remove-nodes|types)\\.ts$"
-  # High-level orchestration reference
-  - type: content
-    pattern: "ideal\\.build\(|buildIdealFromStartingGraph\("
-
-actions:
-  - type: guide
-    message: |
-      ## Overview
-
-      The Ideal Graph represents the desired post-install state. It is constructed by:
-      1. Selecting a starting graph: prefer Virtual (lockfile) and fall back to Actual (`node_modules`) when needed.
-      2. Merging user-provided `add`/`remove` requests with importer manifest deltas.
-      3. Expanding dependencies by fetching manifests/artifacts and recursively placing packages.
-      4. Reusing existing nodes that satisfy specs to minimize network and duplication.
-      5. Optionally extracting tarballs during graph construction for improved performance (early extraction).
-
-      Entry point: `src/graph/src/ideal/build.ts` → `ideal.build(options)`
-
-  - type: architecture_guide
-    message: |
-      ## Starting Graph Selection (`build.ts`)
-
-      - Attempts to load a Virtual Graph from lockfile first with `skipLoadingNodesOnModifiersChange: true`.
-      - On failure, loads the Actual Graph with the same skip flag.
-      - Uses shared instances of `packageJson`, `scurry`, and `monorepo` for efficiency.
-      - Delegates to `buildIdealFromStartingGraph()` for merging and expansion.
-
-  - type: architecture_guide
-    message: |
-      ## Merge and Expansion (`build-ideal-from-starting-graph.ts`)
-
-      - Computes importer deltas via `get-importer-specs.ts`:
-        - Builds `AddImportersDependenciesMap` and `RemoveImportersDependenciesMap` by comparing importer manifests to the starting graph.
-        - Prunes already-satisfied dependencies using `remove-satisfied-specs.ts`.
-        - Flags whether dependencies were modified (`modifiedDependencies`).
-      - Merges user-provided `add`/`remove` over computed deltas; user input wins.
-      - Invokes `refresh-ideal-graph.ts` to fetch and incorporate remote manifests and expand the graph.
-      - After expansion, calls `setDefaultLocation()` on nodes to normalize store layout hints.
-      - Finally, removes dependencies listed in `remove` via `remove-nodes.ts` and garbage-collects unreachable nodes (`graph.gc()`).
-
-  - type: architecture_guide
-    message: |
-      ## Node Appending and Reuse (`append-nodes.ts`, `refresh-ideal-graph.ts`)
-
-      - **Existing Edge Preference**: First checks if the existing edge target (from lockfile) satisfies the spec — preserves lockfile resolutions for idempotency.
-      - Resolves dependency specs to nodes by attempting `graph.findResolution()` to reuse existing nodes that satisfy the spec.
-      - **Peer Compatibility Check**: Before reusing a node, checks if its peer edges are compatible with the current peer context via `checkPeerEdgesCompatible()`.
-      - **Idempotency in Peer Checks**: `checkPeerEdgesCompatible()` now checks if existing edge targets satisfy specs despite context/sibling mismatches — avoids unnecessary forking when existing resolutions are valid.
-      - **Candidate Fallback**: If the first satisfying node is peer-incompatible, lazy-loads candidates and tries others deterministically until a compatible one is found.
-      - When a satisfying node is not found, fetches manifests/artifacts via `@vltpkg/package-info`, selects appropriate versions (respecting platform/engine constraints), and places new nodes with correct flags.
-      - Recursively descends into each newly placed node's dependencies, applying `@vltpkg/spec` parsing and honoring modifiers if present.
-      - Ensures added nodes have consistent `registry`, `resolved`, and `integrity` fields as available.
-
-      ### Deterministic Ordering Architecture
-      The BFS loop uses a 3-phase approach per level to ensure deterministic graph builds:
-      - **Phase A (Parallel Fetch)**: Fetches manifests without mutating the graph - read-only
-      - **Phase B (Serial Mutations)**: Sorts results by stable DepID keys, applies all mutations in deterministic order
-      - **Phase C (Post-Placement)**: Peer context updates and resolution
-
-      This architecture prevents non-determinism from network timing variations.
-
-      📋 **See `@graph/ideal-append-nodes.mdc`** for detailed BFS algorithm and peer context lifecycle
-
-  - type: architecture_guide
-    message: |
-      ## Early Extraction Feature (`append-nodes.ts`)
-
-      - When an `actual` graph is provided to the build process, the Ideal builder can perform early extraction of tarballs.
-      - As nodes are placed into the graph, if they don't exist in the actual graph and are destined for the vlt store, extraction begins immediately.
-      - Extraction happens in parallel with graph construction, improving overall install performance.
-      - The `node.extracted` property tracks whether a node has been extracted to avoid duplicate extractions.
-      - This optimization is particularly beneficial when no cached information is available.
-
-  - type: architecture_guide
-    message: |
-      ## Workspace Peer Context Isolation
-
-      In monorepos with multiple workspace importers, each workspace gets its **own peer context**:
-
-      - **Problem**: Without isolation, peer targets from the root importer could incorrectly influence workspace dependencies
-        - Example: Root has `react@^18`, workspace A needs `react@^19` for a peer-dependent package
-        - Without isolation, the peer dep might incorrectly resolve to react@18
-
-      - **Solution**: `appendNodes()` creates fresh peer contexts for non-main importers:
-        ```typescript
-        if (fromNode.importer && fromNode !== graph.mainImporter) {
-          const nextPeerContext: PeerContext = new Map()
-          nextPeerContext.index = graph.nextPeerContextIndex()
-          initialPeerContext = nextPeerContext
-        }
-        ```
-
-      - **Fork Caching**: `graph.peerContextForkCache` prevents duplicate contexts for identical fork operations
-      
-      📋 **See `@graph/peers.mdc`** for detailed peer context isolation and fork caching mechanisms
-
-  - type: integration_guide
-    message: |
-      ## Options and Inputs
-
-      - `projectRoot`, `packageJson`, `scurry`, `monorepo` — Required/shared instances for deterministic traversal and manifest access.
-      - `packageInfo: PackageInfoClient` — Required for remote manifest and artifact retrieval.
-      - `add?: AddImportersDependenciesMap` — Explicit dependencies to add per importer.
-      - `remove?: RemoveImportersDependenciesMap` — Explicit dependency names to remove per importer.
-      - `actual?: Graph` — Optional actual graph to enable early extraction optimization during ideal graph construction.
-      - Modifiers integration — If `modifiers` are provided, selectors can adjust specs during resolution; Ideal builder will then record modifier info on nodes for downstream awareness.
-
-      ### Behavior and Guarantees
-      - **Idempotency**: Re-running ideal build on an existing lockfile produces identical graph structure.
-      - Reuses nodes whenever they satisfy requested specs, preferring existing edge targets.
-      - Expands transitive dependencies recursively using resolved manifests.
-      - Produces a graph ready for hoisting and reification, with stable, default locations set where applicable.
-
-  - type: development_workflow
-    message: |
-      ## Practical Tips
-
-      - Always prefer the lockfile as the starting point for reproducibility.
-      - Keep `add`/`remove` mappings minimal; rely on `get-importer-specs.ts` to detect manifest drift.
-      - Pass shared `packageJson` and `scurry` instances across phases (Actual/Virtual load → Ideal build → Reify).
-      - Use `graph.findResolution()` aggressively in new features to avoid duplicate nodes and redundant network calls.
-
-examples:
-  - input: |
-      import { ideal } from '@vltpkg/graph'
-      const graph = await ideal.build({ projectRoot, packageInfo, packageJson, scurry })
-    output: "Ideal graph built from lockfile or actual as starting point"
-
-  - input: |
-      // Add and remove across importers
-      const add = new Map()
-      const remove = new Map()
-      const g = await ideal.build({ projectRoot, packageInfo, packageJson, scurry, add, remove })
-    output: "Importer deltas merged with user-provided add/remove and expanded"
-
-  - input: |
-      // Build ideal with early extraction optimization
-      import { ideal, actual } from '@vltpkg/graph'
-      const actualGraph = actual.load({ projectRoot, packageJson, scurry })
-      const idealGraph = await ideal.build({ 
-        projectRoot, 
-        packageInfo, 
-        packageJson, 
-        scurry,
-        actual: actualGraph 
-      })
-    output: "Ideal graph built with early tarball extraction for improved performance"
-
-  - input: |
-      // Multi-workspace monorepo with peer context isolation
-      // Root: react@^18, workspace-a: react@^19 with peer-dependent packages
-      const idealGraph = await ideal.build({ projectRoot, packageInfo, packageJson, scurry, monorepo })
-      
-      // Each workspace gets isolated peer contexts
-      t.ok(idealGraph.peerContexts.length > 1, 'should have multiple peer contexts')
-      t.equal(rootReact.version, '18.3.1', 'root has react@18')
-      t.equal(wsReact.version, '19.2.0', 'workspace has react@19')
-    output: "Ideal graph built with isolated peer contexts per workspace importer"
-
-metadata:
-  priority: high
-  version: 1.4
-  tags:
-    - graph
-    - ideal
-    - build
-    - manifests
-    - modifiers
-    - performance
-    - idempotency
-  related_rules:
-    - graph_workspace_architecture
-    - graph_data_structure
-    - graph_lockfiles
-    - graph_load_actual
-    - graph_modifiers
-    - graph_peers
-    - graph_reify
-    - monorepo-structure
-</rule>
+Entry: `src/graph/src/ideal/build.ts` → `ideal.build(options)`
 
+## Overview
+
+1. Select starting graph: prefer Virtual (lockfile), fallback to Actual
+2. Merge `add`/`remove` with importer manifest deltas
+3. Expand via manifest fetching, recursively placing packages
+4. Reuse existing satisfying nodes to minimize network
+5. Optionally extract tarballs during construction (early extraction)
+
+## Starting Graph (`build.ts`)
+
+Loads Virtual from `vlt-lock.json` (`lockfile.load()`), falls back to Actual (`actual.load()`). Delegates to `buildIdealFromStartingGraph()`.
+
+## Merge & Expansion (`build-ideal-from-starting-graph.ts`)
+
+- Computes importer deltas via `get-importer-specs.ts` (compares manifests to graph)
+- Prunes satisfied deps via `remove-satisfied-specs.ts`
+- User `add`/`remove` overrides computed deltas
+- `refresh-ideal-graph.ts` orders importers, calls `appendNodes()` per importer
+- After expansion: `setDefaultLocation()`, `remove-nodes.ts`, `graph.gc()`
+
+## Node Appending (`append-nodes.ts`)
+
+- **Existing edge preference**: lockfile target preferred if it satisfies spec (idempotency)
+- **Peer compatibility**: `checkPeerEdgesCompatible()` before reuse, with idempotency checks
+- **Candidate fallback**: if first node is peer-incompatible, tries others deterministically
+- **New nodes**: fetch manifest → pick version → place node → recurse children
+- **3-phase BFS per level**: A) parallel fetch (read-only) → B) serial mutations (sorted by DepID) → C) peer check
+
+See `@graph/ideal-append-nodes.mdc` for full BFS architecture, `@graph/peers.mdc` for peer contexts.
+
+## Early Extraction
+
+When `actual` graph provided, new nodes destined for vlt store are extracted in parallel during construction. Tracked via `node.extracted`.
+
+## Workspace Peer Isolation
+
+Non-main importers get fresh peer contexts in `appendNodes()` to prevent cross-workspace peer leakage. Fork cache prevents duplicate contexts.
+
+## Options
+
+`projectRoot`, `packageJson`, `scurry`, `monorepo` (shared instances), `packageInfo` (required), `add?`, `remove?`, `actual?` (for early extraction), `modifiers?`
+
+## Guarantees
+
+- **Idempotent**: same lockfile → identical graph
+- Reuses nodes satisfying specs, preferring existing edge targets
+- Stable locations set where applicable
diff --git a/.cursor/rules/graph/index.mdc b/.cursor/rules/graph/index.mdc
@@ -3,232 +3,55 @@ description: Graph workspace architecture and dependency graph concepts
 globs: src/graph/**
 alwaysApply: false
 ---
-# Graph
+# @vltpkg/graph Overview
 
-Understanding and working with graphs in the vlt package manager.
+Dependency graph modeling installs. Foundation for the vlt installer.
 
-<rule>
-name: graph_workspace_architecture
-description: High-level architecture, concepts, and workflows of the @vltpkg/graph workspace
-filters:
-  # Trigger when working inside the graph workspace
-  - type: path
-    pattern: "^src/graph/"
-  # Trigger when editing core graph API entry points
-  - type: file_name
-    pattern: "^(index|graph|node|edge|diff)\.ts$"
-  # Trigger when working with lockfile or reify subsystems
-  - type: path
-    pattern: "^src/graph/src/(lockfile|reify|ideal|actual)/"
-  # Trigger when working with visualization outputs
-  - type: path
-    pattern: "^src/graph/src/visualization/"
-  # Trigger when referencing monorepo-wide deps used by graph
-  - type: path
-    pattern: "^src/(dep-id|spec|semver|package-info|package-json|workspaces)/"
-  # Trigger when editing README/docs for the graph workspace
-  - type: file_name
-    pattern: "README\.md$"
+## Core Classes
 
-actions:
-  - type: guide
-    message: |
-      ## @vltpkg/graph Overview
+- **`Graph`** (`graph.ts`) — Container of nodes/edges, importer roots, resolution caches, peer contexts
+- **`Node`** (`node.ts`) — Unique package instance (identity via `@vltpkg/dep-id`). Tracks build state, platform, peerSetHash
+- **`Edge`** (`edge.ts`) — Dependency relationship (prod/dev/peer/optional) with parsed `Spec`
+- **`Diff`** (`diff.ts`) — Minimal change set: Actual → Ideal
 
-      The `@vltpkg/graph` workspace implements a dependency graph that models a JavaScript/TypeScript project's installed and desired package state. It is the foundation used by the installer to compute and apply filesystem changes under `node_modules`.
+## Graph Variants
 
-      - **`@graph/package.json`**: The workspace manifest defining the library name and its dependencies.
-      - **`@graph/src/index.ts`**: The public entry point re-exporting internal types, helpers, and submodules.
+- **Virtual** (lockfile): `lockfile.load()` from `vlt-lock.json`; `lockfile.loadHidden()` from `node_modules/.vlt-lock.json`
+- **Actual** (filesystem): `actual.load()` traverses `node_modules`; shortcut via hidden lockfile
+- **Ideal** (desired state): `ideal.build()` from Virtual or Actual → fetches manifests → expands graph. Idempotent; re-running on same lockfile = identical result
 
-      ### Core Data Structures
-      - **`Graph` (`@graph/src/graph.ts`)**: Represents the package relationship graph for a project. It is the authoritative source used to determine how `node_modules` should be structured. Manages peer context sets for peer dependency resolution.
-      - **`Node` (`@graph/src/node.ts`)**: Represents a unique package instance. Uniqueness is defined by `@vltpkg/dep-id` which encodes package identity into a single string identifier. Tracks build state, platform requirements, and peer context hashes.
-      - **`Edge` (`@graph/src/edge.ts`)**: Represents a dependency relationship (eg. entries from `dependencies`, `devDependencies`, `peerDependencies`, etc.) between two nodes.
-      - **`Diff` (`@graph/src/diff.ts`)**: Computes and stores the minimal set of changes to transform one graph (Actual) into another (Ideal).
+After Ideal + Actual, compute `Diff` → apply via `reify()`.
 
-      See the npm documentation for `package.json` format and semantics: [npm package.json docs](https://raw.githubusercontent.com/npm/cli/refs/heads/latest/docs/lib/content/configuring-npm/package-json.md).
+## Ideal Build Pipeline (`src/graph/src/ideal/`)
 
-  - type: architecture_guide
-    message: |
-      ## Architectural Dependencies (Workspaces)
+1. `build.ts` — loads Virtual or Actual as starting point
+2. `build-ideal-from-starting-graph.ts` — merges `add`/`remove` with importer specs
+3. `refresh-ideal-graph.ts` — orders importers, calls `appendNodes()` per importer
+4. `append-nodes.ts` — BFS: parallel fetch → serial mutations → peer check (see `@graph/ideal-append-nodes.mdc`)
+5. `peers.ts` — peer context management (see `@graph/peers.mdc`)
 
-      The graph workspace integrates tightly with other internal workspaces:
-      - **`@vltpkg/dep-id`**: Generates unique IDs for packages, enabling `Node` identity and efficient graph operations. Provides `joinExtra`/`splitExtra` for combining modifier and peerSetHash.
-      - **`@vltpkg/spec`**: Parses and normalizes dependency specs (eg. ranges, tags, git, file, workspace). Provides registry and scope semantics.
-      - **`@vltpkg/semver`**: Semantic Versioning operations underpinning spec satisfaction. Learn more at [semver.org](https://raw.githubusercontent.com/semver/semver.org/refs/heads/gh-pages/index.md).
-      - **`@vltpkg/package-info`**: Fetches remote manifests and artifacts for registry, git, and tarball sources.
-      - **`@vltpkg/package-json`**: Reads and caches local `package.json` files with normalization helpers.
-      - **`@vltpkg/workspaces`**: Discovers and manages monorepo workspaces. Importers in the graph include the main project and all configured workspaces.
-      - **`@vltpkg/rollback-remove`**: Handles safe file removal with rollback capability during extraction and reification.
-      - **`@vltpkg/satisfies`**: Checks if a DepID satisfies a Spec, used throughout resolution.
+## Dependencies
 
-      In the graph, root-level nodes are called **importers**. The `mainImporter` corresponds to the project root (its `package.json`), and other importers come from `@vltpkg/workspaces` discovery. These serve as starting points when loading/constructing graphs.
+- `@vltpkg/dep-id` — node IDs, `joinExtra`/`splitExtra`
+- `@vltpkg/spec` — spec parsing
+- `@vltpkg/semver` — version satisfaction
+- `@vltpkg/package-info` — remote manifests/artifacts
+- `@vltpkg/package-json` — local manifest reading
+- `@vltpkg/workspaces` — monorepo workspace discovery
+- `@vltpkg/satisfies` — DepID↔Spec checks
+- `@vltpkg/rollback-remove` — safe file removal
 
-  - type: architecture_guide
-    message: |
-      ## Graph Construction Modes
+**Importers** = root nodes. `mainImporter` = project root. Others from workspace discovery.
 
-      The graph system builds three primary graph variants, which are then used to produce npm-compatible installs:
+## Public API (`src/graph/src/index.ts`)
 
-      - **Virtual Graphs** (Lockfile-based)
-        - Loaded from lockfiles; entry points in `@graph/src/lockfile/`:
-          - Load: `load.ts` (`load()`), Hidden: `loadHidden()`
-          - Save: `save.ts` (`save()` for `vlt-lock.json`, `saveHidden()` for `node_modules/.vlt-lock.json`)
-        - See the lockfile rule for format and integration details.
+- `actual.load(options)`, `ideal.build(options)`, `lockfile.load/save`, `reify(options)`
+- `install(options, add?)` — high-level: validates options, loads actual, builds ideal, reifies
+- Visualization: `mermaidOutput()`, `humanReadableOutput()`, `jsonOutput()`, `objectLikeOutput()`
 
-      - **Actual Graphs** (Filesystem-based)
-        - Loaded from `node_modules` by recursively traversing symlinks and directories: `@graph/src/actual/load.ts`.
-        - May be shortcut by the Hidden Lockfile (`node_modules/.vlt-lock.json`) for performance.
-        - Applied to disk via the `reify/` subsystem, which encodes the minimal filesystem operations required by Node.js module resolution.
+## Tips
 
-      - **Ideal Graphs** (Desired end state)
-        - Entry point: `@graph/src/ideal/build.ts`
-        - Starts from either a Virtual Graph (preferred) or falls back to an Actual Graph.
-        - **Idempotent**: Re-running on same lockfile produces identical graph structure.
-        - Merges explicit `add`/`remove` requests with importer manifests via `get-importer-specs.ts`.
-        - Resolves new nodes by fetching manifests/artifacts using `@vltpkg/package-info`, recursively expanding the graph.
-        - Uses breadth-first processing with deterministic ordering in `append-nodes.ts` for reproducible builds.
-        - Prefers existing edge targets (lockfile resolutions) over alternatives when both satisfy specs.
-        - Reuses existing nodes that satisfy specs to avoid unnecessary network calls.
-        - Manages peer dependency contexts to handle version conflicts via `peers.ts`.
-        - Supports early extraction of tarballs during graph construction for improved performance.
-
-      After building the Ideal and loading the Actual, the installer computes a `Diff` and applies it using the `reify/` subsystem to minimize work.
-
-  - type: architecture_guide
-    message: |
-      ## Ideal Graph Building Pipeline
-
-      The ideal graph build pipeline (`src/graph/src/ideal/`):
-
-      1. **`build.ts`** — Entry point; loads Virtual or Actual graph as starting point
-      2. **`build-ideal-from-starting-graph.ts`** — Merges `add`/`remove` with importer specs from `get-importer-specs.ts`
-      3. **`refresh-ideal-graph.ts`** — Orchestrates graph refresh:
-         - Orders importers (non-peer deps first, then peer deps, alphabetically)
-         - Calls `graph.resetEdges()` when dependencies are modified
-         - Iterates importers calling `appendNodes()` for each
-         - Sets default node locations
-         - Waits for early extraction promises
-      4. **`append-nodes.ts`** — Breadth-first dependency processing:
-         - `findCompatibleResolution()` — Prefers existing edge targets for idempotency, with memoized satisfies checks
-         - `fetchManifestsForDeps()` — Parallel manifest fetching with peer compatibility checks
-         - `processPlacementTasks()` — Places nodes, handles modifiers, triggers early extraction
-         - Manages peer context lifecycle via `startPeerPlacement()`/`endPeerPlacement()`
-         - Calls `postPlacementPeerCheck()` after each level for context forking and peer resolution
-      5. **`peers.ts`** — Peer dependency context management:
-         - `checkPeerEdgesCompatible()` — Validates node reuse compatibility with idempotency checks
-         - Per-call memoization for `satisfies()` calls to improve performance
-         - Uses `nodesByName` for efficient candidate lookup (not full graph scan)
-         - `forkPeerContext()` — Creates isolated peer contexts when conflicts arise
-         - `addEntriesToPeerContext()` — Tracks dependencies in context sets
-         - Generates `peerSetHash` for affected nodes (format: `peer.N`)
-
-      📋 **See `@graph/ideal-append-nodes.mdc`** for detailed append-nodes architecture
-      📋 **See `@graph/peers.mdc`** for peer dependency context isolation details
-
-  - type: architecture_guide
-    message: |
-      ## Visualization Outputs (`src/graph/src/visualization/`)
-
-      The visualization module provides multiple output formats for graph data:
-
-      - **`mermaidOutput()`** (`mermaid-output.ts`) — Generates Mermaid flowchart syntax for docs/dashboards
-      - **`humanReadableOutput()`** (`human-readable-output.ts`) — ASCII tree with colors (like `npm ls`)
-      - **`jsonOutput()`** (`json-output.ts`) — Array of `{name, fromID, spec, type, to, overridden}` items
-      - **`objectLikeOutput()`** (`object-like-output.ts`) — Node.js `inspect()` output for debugging
-
-      All outputs accept filtered `{edges, nodes, importers}` from query results, enabling visualization of subsets.
-
-  - type: integration_guide
-    message: |
-      ## Key Entry Points and Public API (`@graph/src/index.ts`)
-
-      The main entry point re-exports the public API:
-      - `actual.load(options)` — Load from `node_modules` (or from Hidden Lockfile when available).
-      - `ideal.build(options)` — Build an Ideal Graph starting from a Virtual or Actual starting point.
-      - `lockfile.load/save` — Read and write lockfiles.
-      - `reify(options)` — Compute a `Diff` between Actual and Ideal and apply filesystem changes.
-      - `install(options, add?)` — High-level install orchestration (`src/graph/src/install.ts`):
-        - Validates options (frozen-lockfile, clean-install, lockfile-only)
-        - Handles `vlt init` if no package.json exists
-        - Loads actual graph, builds ideal, reifies changes
-        - Supports `--lockfile-only` mode for lockfile-only updates
-      - Types and utilities: `Graph`, `Node`, `Edge`, `Diff`, dependency helpers, visualization outputs, etc.
-
-  - type: development_workflow
-    message: |
-      ## Development Workflow Tips
-
-      - Share instances of `monorepo`, `packageJson`, and `scurry` across loader/build steps for performance.
-      - Prefer Hidden Lockfile (`node_modules/.vlt-lock.json`) when available for faster Actual loads.
-      - When modifiers or installer options change, you'll often rebuild the Ideal Graph with `skipLoadingNodesOnModifiersChange` to avoid loading stale dependency nodes.
-      - Determinism: Node and Edge ordering is intentionally stable to produce reproducible lockfiles.
-      - Use `graph.resetEdges()` when refreshing dependencies; it preserves nodes marked as `detached` for reuse.
-      - Pass `actual` graph to `ideal.build()` to enable early extraction optimization.
-      - Use `RollbackRemove` for safe extraction with rollback capability.
-
-      ### Useful References
-      - Monorepo concepts and related workspaces: see the monorepo structure rule and `www/docs`.
-      - `package.json` behavior: [npm package.json docs](https://raw.githubusercontent.com/npm/cli/refs/heads/latest/docs/lib/content/configuring-npm/package-json.md)
-      - Semantic Versioning: [semver.org](https://raw.githubusercontent.com/semver/semver.org/refs/heads/gh-pages/index.md)
-
-examples:
-  - input: |
-      // Build an Ideal Graph and reify changes
-      import { ideal, reify } from '@vltpkg/graph'
-      
-      const graph = await ideal.build({ projectRoot, packageInfo, packageJson, scurry })
-      await reify({ graph, packageInfo, packageJson, scurry })
-    output: "Ideal graph built and applied to disk via reify"
-
-  - input: |
-      // Build ideal with early extraction optimization
-      import { ideal, actual } from '@vltpkg/graph'
-      const actualGraph = actual.load({ projectRoot, packageJson, scurry })
-      const idealGraph = await ideal.build({ 
-        projectRoot, 
-        packageInfo, 
-        packageJson, 
-        scurry,
-        actual: actualGraph,
-        remover: new RollbackRemove()
-      })
-    output: "Ideal graph built with early tarball extraction for improved performance"
-
-  - input: |
-      // Generate visualization outputs
-      import { mermaidOutput, humanReadableOutput, jsonOutput } from '@vltpkg/graph'
-      
-      const graphData = {
-        edges: [...graph.edges],
-        nodes: [...graph.nodes.values()],
-        importers: graph.importers,
-      }
-      
-      const mermaid = mermaidOutput(graphData)
-      const tree = humanReadableOutput(graphData, { colors: true })
-      const json = jsonOutput(graphData)
-    output: "Graph visualized in multiple formats"
-
-metadata:
-  priority: high
-  version: 2.1
-  tags:
-    - graph
-    - architecture
-    - lockfiles
-    - install
-    - workspaces
-    - peer-dependencies
-    - visualization
-    - idempotency
-  related_rules:
-    - graph_ideal
-    - graph_ideal_append_nodes
-    - graph_data_structure
-    - graph_load_actual
-    - graph_lockfiles
-    - graph_modifiers
-    - graph_reify
-    - graph_peers
-</rule>
+- Share `monorepo`, `packageJson`, `scurry` instances across phases
+- Use hidden lockfile for faster Actual loads
+- `graph.resetEdges()` preserves detached nodes for reuse
+- Pass `actual` to `ideal.build()` for early extraction optimization
diff --git a/.cursor/rules/graph/load-actual.mdc b/.cursor/rules/graph/load-actual.mdc
@@ -3,166 +3,51 @@ description: Loading Actual Graphs from node_modules
 globs: src/graph/src/actual/*,src/graph/test/actual/*
 alwaysApply: false
 ---
-# Loading Actual Graphs (node_modules)
+# Loading Actual Graphs
 
-Understanding how `@vltpkg/graph` loads an Actual Graph by traversing a project's `node_modules` and how to use the returned structure.
+Entry: `src/graph/src/actual/load.ts` → `actual.load(options)`
 
-<rule>
-name: graph_load_actual
-description: Detailed guidance for loading Actual Graphs from node_modules and using the resulting structure
-filters:
-  # Core implementation file and directory
-  - type: path
-    pattern: "^src/graph/src/actual/load\\.ts$"
-  - type: path
-    pattern: "^src/graph/src/actual/"
-  # Hidden lockfile shortcut integration
-  - type: content
-    pattern: "loadHidden\(\)"
-  # Option flags commonly used with actual.load
-  - type: content
-    pattern: "skipHiddenLockfile|loadManifests|skipLoadingNodesOnModifiersChange"
+Represents what's currently installed on disk.
 
-actions:
-  - type: guide
-    message: |
-      ## What is an Actual Graph?
+## Flow
 
-      An Actual Graph is a representation of what's currently installed on disk in a project, derived by traversing `node_modules`. Its purpose is to reflect the real state of the install so that it can be compared to an Ideal Graph for minimal-change reification.
+1. Resolve `mainManifest` (from options or `packageJson.read()`)
+2. **Fast path**: if `!skipHiddenLockfile`, try `lockfile.loadHidden()` from `node_modules/.vlt-lock.json`
+3. Construct `Graph` with importers (project + workspaces)
+4. Compare stored modifiers (`node_modules/.vlt/vlt.json`) to current; if changed and `skipLoadingNodesOnModifiersChange`, load importers only
+5. BFS traversal from each importer's `node_modules`:
+   - Read entries, descend into `@scope` folders, follow symlinks
+   - Place nodes/edges, read manifests when `loadManifests=true`
+6. Mark extraneous deps (on disk but not declared), add dangling edges for missing deps
+7. `modifiers.rollbackActiveEntries()` to clean up
+8. Cache loaded graph to hidden lockfile
 
-      Entry point: `src/graph/src/actual/load.ts` → `actual.load(options)`
+**Helpers**: `readDir()` (scans `node_modules`), `parseDir()` (places packages, applies modifiers, queues BFS)
 
-  - type: architecture_guide
-    message: |
-      ## High-level Flow
+## Identity/Path Handling
 
-      1. Resolve `mainManifest` (from `options.mainManifest` or `packageJson.read(projectRoot)`).
-      2. If `skipHiddenLockfile` is not set, attempt fast-path by loading the Hidden Lockfile via `lockfile.loadHidden()` (file: `node_modules/.vlt-lock.json`). If successful, return that Graph.
-      3. Otherwise, construct a new `Graph` seeded with importers (the project and discovered workspaces).
-      4. Optionally compare stored modifiers (`node_modules/.vlt/vlt.json`) to `options.modifiers.config`. If `skipLoadingNodesOnModifiersChange` is true and modifiers changed, only importers are loaded (skip dependency traversal).
-      5. For each importer, call `modifiers.tryImporter(importer)` to initialize modifier tracking.
-      6. Perform a breadth-first traversal starting from each importer's `node_modules` folder:
-         - Read entries (skipping hidden items), descend into `@scope` folders, and consider only symbolic links as potential dependency links.
-         - Resolve real paths, derive alias (symlink name) and normalized package name (handling scopes) for each entry.
-         - Place nodes and edges in the graph, reading manifests when required.
-      7. Mark extraneous dependencies (present on disk but not listed in importer manifests) when manifests are loaded.
-      8. Add dangling edges for missing dependencies (declared but not found on disk).
-      9. Call `modifiers.rollbackActiveEntries()` to clean up partially applied modifier entries.
-      10. Cache the loaded graph to hidden lockfile (`node_modules/.vlt-lock.json`) if `node_modules` exists.
+- Path-based specs → `getPathBasedId()`
+- Store-based → `findDepID()` walks parents to `.vlt/` layout
+- `node.location` = relative path like `./node_modules/...`
 
-      The traversal is implemented by helper functions within `load.ts`:
-      - `readDir(scurry, currDir, fromNodeName?)` — Scans `node_modules`, recursing into `@scope` directories, returning alias/name/realpath for symlink entries.
-      - `parseDir(options, scurry, packageJson, depsFound, graph, fromNode, currDir)` — Places packages, applies modifiers, records extraneous/missing, and queues nested `node_modules` for BFS.
+## Modifier Application
 
-  - type: architecture_guide
-    message: |
-      ## Identity and Path Handling
+`maybeApplyModifierToSpec()`: calls `modifiers.tryDependencies()` before placing, swaps spec if complete breadcrumb match (marks as `overridden`).
 
-      - Path-based specs (`file`, `workspace`) get IDs directly from their path via `getPathBasedId()`.
-      - For store-based installs, `findDepID()` walks parent paths until it reaches `.vlt/` store layout (`.vlt/<DepID>/node_modules/<name>`), extracting the `DepID`.
-      - `findNodeModules()` finds the nearest `node_modules` directory for a placed node.
-      - `findName()` normalizes names, including scoped package folders.
+## Options
 
-      Placed nodes set `node.location` to a relative path like `./node_modules/...` or `./<realpath>`. Nodes outside the store are treated accordingly by `node.nodeModules(scurry)`.
+- `projectRoot`, `packageJson`, `scurry` (required), `monorepo?`, `mainManifest?`
+- `modifiers?` — active modifiers for spec resolution
+- `loadManifests?: boolean` — true: accurate dep types, extraneous/missing detection; false: infer prod edges, no missing/extraneous
+- `skipHiddenLockfile?` — skip fast path
+- `skipLoadingNodesOnModifiersChange?` — importers only if modifiers changed
+- `expectLockfile?` — fail if lockfile missing/stale (CI)
+- `frozenLockfile?` — stricter: fail if out of sync with package.json
+- `lockfileOnly?` — only update lockfile, skip node_modules operations
 
-  - type: architecture_guide
-    message: |
-      ## Modifiers Application
+## Tips
 
-      The loader uses `maybeApplyModifierToSpec()` helper to apply modifiers:
-      - Before placing packages, calls `modifiers.tryDependencies(fromNode, deps)` to find active selectors.
-      - For each dependency, checks if a modifier is complete (breadcrumb fully matched).
-      - If complete and modifier has a spec, replaces the original spec with the modifier's spec (marked as `overridden`).
-      - Records `queryModifier` with the node for later phases to reason about modified resolutions.
-      - After placing a package, calls `modifiers.updateActiveEntry(node, activeModifier)` to track progress.
-      - After traversal, `modifiers.rollbackActiveEntries()` clears any partially applied entries.
-
-      Modifiers are also applied to missing dependencies (declared but not found on disk).
-
-  - type: integration_guide
-    message: |
-      ## Options and Behavior
-
-      - `projectRoot: string` — Required. Project directory to scan.
-      - `packageJson` (required), `scurry` (required), `monorepo` (optional) — Shared instances; reuse them for performance.
-      - `mainManifest?: NormalizedManifest` — Optionally provide the root manifest; otherwise read from disk.
-      - `modifiers?: GraphModifier` — Active modifiers affecting spec resolution and node placement.
-      - `loadManifests?: boolean` —
-        - `true`: Read package manifests for accurate dependency types/specs, and to detect extraneous dependencies.
-        - `false`: Do not read manifests; infer default `prod` edges and hydrate specs from `DepID` when possible. No missing/extraneous detection.
-      - `skipHiddenLockfile?: boolean` — If `false` (default), attempt Hidden Lockfile fast-path.
-      - `skipLoadingNodesOnModifiersChange?: boolean` — Load only importers if modifiers differ from `node_modules/.vlt/vlt.json` saved config.
-      - `expectLockfile?: boolean` — Fail if lockfile is missing or out of date (used by `ci` command).
-      - `frozenLockfile?: boolean` — Fail if lockfile is missing or out of sync with package.json. Stricter than `expectLockfile`.
-      - `lockfileOnly?: boolean` — Only update the lockfile without node_modules operations. Skips package extraction, filesystem operations, and hidden lockfile saves.
-
-  - type: development_workflow
-    message: |
-      ## Using the Returned Actual Graph
-
-      - Nodes may lack manifests when `loadManifests=false`. Avoid relying on dependency type info or declared specs in that mode.
-      - Missing dependencies are represented by edges with no `to` node (dangling edges) when manifests are processed; extraneous dependencies are recorded in `graph.extraneousDependencies`.
-      - Each node has a `location` and can compute its `nodeModules(scurry)` directory for linking operations.
-      - The Actual Graph is commonly diffed against an Ideal Graph using `new Diff(actual, ideal)`, then applied by `reify`.
-      - Prefer the Hidden Lockfile fast-path when available to skip filesystem traversal.
-
-      ### Store Config Object
-      The loader reads/validates `node_modules/.vlt/vlt.json` via `isStoreConfigObject()` and `asStoreConfigObject()`:
-      - Contains `modifiers` record used to detect modifier changes between installs.
-      - If modifiers changed and `skipLoadingNodesOnModifiersChange` is set, only importers are loaded.
-
-      ### Performance Tips
-      - Reuse `packageJson`, `scurry`, and `monorepo` instances across phases.
-      - Use `skipLoadingNodesOnModifiersChange` strategically when rebuilding after modifier changes.
-      - Hidden lockfile is automatically saved after traversal to speed up subsequent loads.
-
-examples:
-  - input: |
-      // Load Actual with manifests for accurate extraneous/missing detection
-      import { actual } from '@vltpkg/graph'
-      const from = actual.load({
-        projectRoot,
-        packageJson: sharedPackageJson,
-        scurry: sharedScurry,
-        monorepo: sharedMonorepo,
-        loadManifests: true,
-      })
-    output: "Actual graph loaded from node_modules with manifests"
-
-  - input: |
-      // Fast-path from Hidden Lockfile (if present and not skipped)
-      import { actual } from '@vltpkg/graph'
-      const from = actual.load({
-        projectRoot,
-        packageJson,
-        scurry,
-        // skipHiddenLockfile: false (default)
-      })
-    output: "Actual graph loaded from node_modules/.vlt-lock.json when available"
-
-  - input: |
-      // No-manifest mode (faster, limited details, defaults to prod edges)
-      const from = actual.load({ projectRoot, packageJson, scurry, loadManifests: false })
-    output: "Actual graph loaded without reading manifests; no extraneous/missing computed"
-
-  - input: |
-      // Lockfile-only mode (skip node_modules operations)
-      const from = actual.load({ projectRoot, packageJson, scurry, lockfileOnly: true })
-    output: "Actual graph loaded for lockfile-only updates"
-
-metadata:
-  priority: high
-  version: 1.1
-  tags:
-    - graph
-    - actual
-    - node_modules
-    - filesystem
-    - performance
-    - modifiers
-  related_rules:
-    - graph_workspace_architecture
-    - graph_data_structure
-    - graph_lockfiles
-    - graph_modifiers
-</rule>
+- Missing deps = dangling edges (`to=undefined`); extraneous in `graph.extraneousDependencies`
+- Common usage: diff Actual vs Ideal → reify
+- Prefer hidden lockfile fast path when available
+- Reuse shared instances across phases
diff --git a/.cursor/rules/graph/lockfiles.mdc b/.cursor/rules/graph/lockfiles.mdc
@@ -5,316 +5,51 @@ alwaysApply: false
 ---
 # Graph Lockfiles
 
-Understanding and working with lockfiles in the vlt package manager.
+Auto-generated on install. Ensures reproducible installs, readable diffs, performance optimization.
 
-<rule>
-name: graph_lockfiles
-description: Guide for understanding and working with lockfiles in the vlt package manager
-filters:
-  # Match lockfile-related files
-  - type: path
-    pattern: "^src/graph/src/lockfile/"
-  - type: path  
-    pattern: "^src/graph/test/lockfile/"
-  # Match files that interact with lockfiles
-  - type: path
-    pattern: "^src/graph/src/(ideal/build|actual/load|reify/index)\\.ts$"
-  # Match lockfile files in projects
-  - type: file_name
-    pattern: "vlt-lock\\.json$"
-  - type: file_name
-    pattern: "\\.vlt-lock\\.json$"
-  # Match CLI commands that use lockfiles
-  - type: content
-    pattern: "lockfile\\.(load|save|loadHidden|saveHidden)"
+## Files
 
-actions:
-  - type: guide
-    message: |
-      ## Lockfiles in vlt Package Manager
+- `vlt-lock.json` — main lockfile (committed to source control)
+- `node_modules/.vlt-lock.json` — hidden lockfile with manifests+build data (perf optimization)
 
-      A **lockfile** is automatically generated for any operations where vlt modifies either the `node_modules` graph or `package.json`. It describes the exact graph that was generated, such that subsequent installs are able to generate identical graphs, regardless of intermediate dependency updates.
+## Module Architecture (`src/graph/src/lockfile/`)
 
-      ### Purpose and Benefits
+**Entry points:**
+- `load.ts`: `load()` (from `vlt-lock.json`), `loadHidden()` (from hidden, sets `throwOnMissingManifest`), `loadObject()` (in-memory, merges lockfile options)
+- `save.ts`: `save()` (minimal), `saveHidden()` (with manifests+build data), `lockfileData()` (Graph→data)
 
-      **Primary Goals:**
-      - **Reproducible Installs**: Teammates, deployments, and CI get exactly the same dependencies
-      - **Time Travel**: Return to previous states of `node_modules` without committing the directory
-      - **Visibility**: Readable source control diffs show dependency graph changes
-      - **Performance**: Skip repeated metadata resolutions for previously-installed packages
-      - **Complete Picture**: Enough information to understand the package graph without reading all `package.json` files
+**Support:** `types.ts` (formats, flag helpers), `load-nodes.ts`, `load-edges.ts`
 
-      **File Locations:**
-      - `vlt-lock.json` - Main lockfile (committed to source control)
-      - `node_modules/.vlt-lock.json` - Hidden lockfile with full manifest data (performance optimization)
+## Data Format
 
-  - type: architecture_guide
-    message: |
-      ## Lockfile Module Architecture
+```typescript
+type LockfileData = {
+  lockfileVersion: number
+  options: SpecOptions & { modifiers?: Record<string, string> }
+  nodes: Record<DepID, LockfileNode>  // tuple: [flags, name?, integrity?, resolved?, location?, manifest?, rawManifest?, platform?, bins?, buildState?]
+  edges: LockfileEdges  // { "${fromId} ${name}": "${type} ${bareSpec} ${toId|MISSING}" }
+}
+```
 
-      ### Core Implementation (`src/graph/src/lockfile/`)
+Flags: 0=prod, 1=optional, 2=dev, 3=devOptional
 
-      **Main Entry Points:**
-      - `load.ts` - Loading lockfiles into Graph objects
-        - `load()` - Load from `vlt-lock.json`
-        - `loadHidden()` - Load from `node_modules/.vlt-lock.json` (sets `throwOnMissingManifest=true`)
-        - `loadObject()` - Load from in-memory lockfile data; merges options from lockfile (catalog, registries, git-hosts, etc.)
-      - `save.ts` - Saving Graph objects to lockfiles
-        - `save()` - Save to `vlt-lock.json` (minimal format, no manifests)
-        - `saveHidden()` - Save to `node_modules/.vlt-lock.json` (with manifests and build data)
-        - `lockfileData()` - Convert Graph to lockfile data structure
+Options stored: `modifiers`, `catalog`, `catalogs`, `scope-registries`, `jsr-registries`, `registry`, `registries`, `git-hosts`, `git-host-archives`
 
-      **Supporting Modules:**
-      - `types.ts` - TypeScript definitions and utilities
-        - `LockfileData` - Main lockfile structure
-        - `LockfileNode` - Node representation with flags
-        - `LockfileEdges` - Edge representation as key-value pairs
-        - `getFlagNumFromNode()` / `getBooleanFlagsFromNum()` - Flag conversion helpers
-        - `getBuildStateFromNode()` / `getBuildStateFromNum()` - Build state conversion
-      - `load-nodes.ts` - Implementation for loading nodes from lockfile
-      - `load-edges.ts` - Implementation for loading edges from lockfile
+## Integration
 
-      **Testing:**
-      - `test/lockfile/` - Comprehensive unit tests for all lockfile operations
-      - Tests cover loading, saving, edge cases, and format validation
+- `ideal/build.ts`: loads lockfile first (prefer Virtual), falls back to Actual
+- `actual/load.ts`: uses hidden lockfile for fast path
+- After loading: hydrates missing node registry data from first incoming edge
 
-  - type: integration_guide
-    message: |
-      ## Lockfile Integration Points
+## Performance (>50 nodes)
 
-      ### Build Process (`src/graph/src/ideal/build.ts`)
-      ```typescript
-      // Always attempts to load lockfile first when building ideal graph
-      try {
-        graph = loadVirtual({
-          ...options,
-          skipLoadingNodesOnModifiersChange: true,
-        })
-      } catch {
-        // Falls back to actual graph if lockfile load fails
-        graph = loadActual({...options})
-      }
-      ```
+- `load-nodes.ts`: `registryVersionCache` avoids repeated string splitting
+- `load-edges.ts`: `seenNodes` Map caches node lookups, `edgeProcessingQueue` batches mutations, uses `fastSplit()`
+- Hidden lockfile skips filesystem traversal entirely
 
-      ### Actual Loading (`src/graph/src/actual/load.ts`)
-      ```typescript
-      // Uses hidden lockfile for performance when available
-      if (!skipHiddenLockfile) {
-        try {
-          const graph = loadHidden({
-            projectRoot,
-            mainManifest,
-            packageJson,
-            monorepo,
-            scurry,
-          })
-          return graph // Skip filesystem traversal
-        } catch {}
-      }
-      ```
+## Tips
 
-      ### Post-Load Registry Hydration
-      After loading nodes and edges, `loadObject()` hydrates missing node-level registry data:
-      ```typescript
-      for (const node of graph.nodes.values()) {
-        const [firstEdge] = node.edgesIn
-        if (firstEdge?.spec.registry) {
-          node.registry = firstEdge.spec.registry
-        }
-      }
-      ```
-
-  - type: data_format_guide
-    message: |
-      ## Lockfile Data Format
-
-      ### Structure Overview
-      ```typescript
-      type LockfileData = {
-        lockfileVersion: number
-        options: SpecOptions & { modifiers?: Record<string, string> }
-        nodes: Record<DepID, LockfileNode>
-        edges: LockfileEdges
-      }
-      ```
-
-      ### Node Format (Tuple Array)
-      ```typescript
-      type LockfileNode = [
-        flags: LockfileNodeFlags,               // [0] 0-3: dev/optional flags
-        name?: string | null,                   // [1] Package name
-        integrity?: Integrity | null,           // [2] SHA integrity hash
-        resolved?: string | null,               // [3] Custom registry URL (skip for remote type)
-        location?: string | null,               // [4] Non-standard install location
-        manifest?: NormalizedManifest | null,   // [5] Full manifest (hidden only)
-        rawManifest?: NormalizedManifest | null,// [6] Original manifest if confused
-        platform?: LockfilePlatform | null,     // [7] Platform requirements (optional deps)
-        bins?: Record<string, string> | null,   // [8] Binary executables
-        buildState?: number | null,             // [9] Build state data (hidden only)
-      ]
-      ```
-
-      ### Edge Format
-      ```typescript
-      type LockfileEdges = {
-        [key: `${DepID} ${string}`]: `${DependencyTypeShort} ${Spec['bareSpec']} ${DepID | 'MISSING'}`
-      }
-      // Example: "registry:foo@1.0.0 bar": "prod ^2.0.0 registry:bar@2.1.0"
-      ```
-
-      ### Flags System
-      ```typescript
-      const LockfileNodeFlagNone = 0        // Production dependency
-      const LockfileNodeFlagOptional = 1    // Optional dependency
-      const LockfileNodeFlagDev = 2         // Development dependency  
-      const LockfileNodeFlagDevOptional = 3 // Both dev and optional
-      ```
-
-      ### Options Stored in Lockfile
-      - `modifiers` - Query modifiers config
-      - `catalog` / `catalogs` - Dependency catalogs
-      - `scope-registries` - Scoped package registries
-      - `jsr-registries` - JSR registries
-      - `registry` / `registries` - Custom registries
-      - `git-hosts` / `git-host-archives` - Git hosting config
-
-  - type: performance_guide
-    message: |
-      ## Performance Optimizations
-
-      ### Large Graph Optimizations (>50 nodes/edges)
-      The lockfile loader applies performance optimizations for non-trivial graphs:
-
-      **`load-nodes.ts`:**
-      - Uses `registryVersionCache` Map to cache parsed version strings for registry specs
-      - Avoids repeated string splitting for the same spec patterns
-
-      **`load-edges.ts`:**
-      - Uses `seenNodes` Map to cache node lookups, avoiding repeated `graph.nodes.get()` calls
-      - Batches edge processing into `edgeProcessingQueue` array before final graph mutation
-      - Uses `fastSplit()` from `@vltpkg/fast-split` for optimized string parsing
-
-      ### Hidden Lockfile Benefits
-      - Contains full manifests (`saveManifests: true`)
-      - Contains build state data (`saveBuildData: true`)
-      - Throws on missing manifests (`throwOnMissingManifest: true`)
-      - Allows skipping filesystem traversal entirely on subsequent loads
-
-  - type: development_workflow
-    message: |
-      ## Development Workflow
-
-      ### Working with Lockfiles
-
-      **Key Principles:**
-      1. **Shared Instances**: Always use shared `monorepo`, `packageJson`, and `scurry` instances
-      2. **Error Handling**: Lockfile loading should gracefully fall back to alternative methods
-      3. **Performance**: Hidden lockfiles include full manifest data to avoid filesystem reads
-      4. **Deterministic**: Node and edge ordering is deterministic for reproducible diffs
-
-      **Save Options:**
-      ```typescript
-      type SaveOptions = SpecOptions & {
-        graph: Graph
-        modifiers?: GraphModifier
-        saveManifests?: boolean        // Include full manifests
-        saveBuildData?: boolean        // Include build state
-        throwOnMissingManifest?: boolean // Error if manifest missing
-      }
-      ```
-
-      **Load Options:**
-      ```typescript
-      type LoadOptions = SpecOptions & {
-        projectRoot: string
-        mainManifest: NormalizedManifest
-        modifiers?: GraphModifier
-        monorepo?: Monorepo
-        packageJson?: PackageJson
-        scurry?: PathScurry
-        actual?: Graph                 // Reference graph for hydrating missing data
-        throwOnMissingManifest?: boolean
-      }
-      ```
-
-      **Testing Considerations:**
-      - Test both regular and hidden lockfile formats
-      - Verify deterministic output (same input = same lockfile)
-      - Test modifier change detection logic
-      - Validate edge cases (missing nodes, malformed data)
-      - Test performance with large dependency graphs (>50 nodes)
-      - Test platform and bins data persistence
-
-      **Debugging Tips:**
-      - Check `lockfileVersion` compatibility
-      - Verify modifier configurations match between load/save
-      - Examine node flags for dependency type issues
-      - Validate edge key/value format consistency
-      - Check `throwOnMissingManifest` behavior for hidden lockfiles
-
-examples:
-  - input: |
-      # Loading a lockfile with proper error handling
-      import { load, loadHidden } from '@vltpkg/graph/lockfile'
-      
-      const graph = load({
-        projectRoot: '/path/to/project',
-        mainManifest,
-        packageJson: sharedPackageJson,
-        monorepo: sharedMonorepo,
-        scurry: sharedScurry,
-      })
-    output: "Properly loaded lockfile with shared instances"
-
-  - input: |
-      # Saving lockfiles after install
-      import { save, saveHidden } from '@vltpkg/graph/lockfile'
-      
-      // Save main lockfile (committed)
-      save({ graph, ...options })
-      
-      // Save hidden lockfile (with manifests and build data)
-      saveHidden({ graph, ...options })
-    output: "Correctly saved both lockfile formats"
-
-  - input: |
-      # Working with lockfile data format (including new fields)
-      const lockfileData = {
-        lockfileVersion: 1,
-        options: { registry: 'https://registry.npmjs.org/' },
-        nodes: {
-          'registry:foo@1.0.0': [
-            0,              // flags
-            'foo',          // name
-            'sha512-...',   // integrity
-            null,           // resolved
-            null,           // location
-            null,           // manifest (hidden only)
-            null,           // rawManifest
-            { os: ['linux'] }, // platform (optional deps)
-            { foo: 'bin/foo.js' }, // bins
-            1               // buildState (hidden only)
-          ]
-        },
-        edges: {
-          'file:. foo': 'prod ^1.0.0 registry:foo@1.0.0'
-        }
-      }
-    output: "Properly structured lockfile data with all fields"
-
-metadata:
-  priority: high
-  version: 1.1
-  tags:
-    - lockfiles
-    - graph
-    - performance
-    - install
-    - dependencies
-  related_rules:
-    - graph_workspace_architecture
-    - graph_data_structure
-    - graph_load_actual
-    - graph_modifiers
-    - cli-sdk-workspace
-</rule>
+- Share `monorepo`, `packageJson`, `scurry` instances
+- Lockfile loading should gracefully fallback
+- Deterministic node/edge ordering for reproducible diffs
+- Test both regular and hidden formats, modifier change detection, large graphs
diff --git a/.cursor/rules/graph/modifiers.mdc b/.cursor/rules/graph/modifiers.mdc
@@ -5,330 +5,70 @@ alwaysApply: false
 ---
 # Graph Modifiers
 
-Understanding and working with Graph Modifiers in the vlt package manager.
+Overrides/resolutions and package extensions via DSS selectors in `vlt.json`.
 
-<rule>
-name: graph_modifiers
-description: Guide for configuring and integrating Graph Modifiers (overrides/resolutions and package extensions)
-filters:
-  # Modifier core and Ideal integration points
-  - type: path
-    pattern: "^src/graph/src/modifiers\\.ts$"
-  - type: path
-    pattern: "^src/graph/src/ideal/"
-  # DSS parsing/building utilities used by modifiers
-  - type: path
-    pattern: "^src/dss-(parser|breadcrumb)/"
-  # Detect vlt.json modifier usage
-  - type: content
-    pattern: "\"modifiers\"\s*:"
+## Concepts
 
-actions:
-  - type: guide
-    message: |
-      ## What are Graph Modifiers?
+- **Edge modifiers** (overrides): Replace dependency specs. Value = string spec (e.g., `"^1.0.0"`, `"-"` to remove)
+- **Node modifiers** (package extensions): Augment manifests. Value = object with deps/peerDeps/etc.
+- Uses DSS (Dependency Selector Syntax) for matching. Most specific selector wins (CSS specificity).
 
-      Graph Modifiers are a common API enabling advanced customization of dependency resolution and graph construction:
-      - **Overrides / Resolutions**: Replace or pin dependency specs throughout the graph (direct or transitive).
-      - **Package Extensions**: Augment package manifests with extra dependency metadata (eg. add missing peerDeps or mark peer deps optional).
+## User Config (`vlt.json`)
 
-      ### Motivation
-      Power users frequently need to patch dependency trees quickly—eg. to address security issues, unify versions, or work around abandoned packages. By using the Dependency Selector Syntax (DSS) as the user-facing language, vlt provides expressive, precise, and composable control over graph shape and versions.
+```json
+{
+  "modifiers": {
+    ":root > #a > #b": "^1.0.0",
+    "#react": "^19",
+    "#unwanted": "-",
+    "#some-pkg": { "peerDependencies": { "react": "^18 || ^19" } }
+  }
+}
+```
 
-  - type: architecture_guide
-    message: |
-      ## Key Modules
-      - `src/graph/src/modifiers.ts` — `GraphModifier` class that tracks graph traversal and applies active modifiers to nodes/edges.
-      - `src/graph/src/ideal/*` — Builds the Ideal graph and integrates modifier application during dependency expansion.
-      - `src/dss-parser/` — Parses DSS queries into AST.
-      - `src/dss-breadcrumb/` — Interactive representation that allows walking a query in lockstep with graph traversal; provides `parseBreadcrumb()` and `specificitySort()`.
-      - `src/vlt-json/` — Loads `vlt.json` configuration including `modifiers` key.
+Importer selectors: `:root` (main), `:workspace` (any workspace), `:project` (any importer)
 
-  - type: architecture_guide
-    message: |
-      ## Type Definitions
+## Key Modules
 
-      ### Entry Types
-      ```typescript
-      // Base modifier info
-      type BaseModifierEntry = {
-        type: 'edge' | 'node'
-        query: string                    // Original DSS query string
-        breadcrumb: ModifierBreadcrumb   // Parsed breadcrumb for traversal
-        value: string | NormalizedManifest
-        refs: Set<{ name: string; from: Node }>  // Tracking references
-      }
+- `src/graph/src/modifiers.ts` — `GraphModifier` class
+- `src/dss-parser/` — DSS query AST
+- `src/dss-breadcrumb/` — Interactive breadcrumb walking (provides `parseBreadcrumb()`, `specificitySort()`)
+- `src/vlt-json/` — loads config
 
-      // Edge modifier - replaces dependency specs
-      type EdgeModifierEntry = BaseModifierEntry & {
-        type: 'edge'
-        spec: Spec       // Parsed replacement spec
-        value: string    // Original spec string
-      }
+## Type Definitions
 
-      // Node modifier - augments manifests (package extensions)
-      type NodeModifierEntry = BaseModifierEntry & {
-        type: 'node'
-        manifest: NormalizedManifest  // Manifest additions
-      }
+```typescript
+type EdgeModifierEntry = { type: 'edge', query: string, breadcrumb: ModifierBreadcrumb, spec: Spec, value: string, refs: Set<{name, from}> }
+type NodeModifierEntry = { type: 'node', query: string, breadcrumb: ModifierBreadcrumb, manifest: NormalizedManifest, refs: Set<{name, from}> }
+type ModifierActiveEntry = { modifier: ModifierEntry, interactiveBreadcrumb, originalFrom: Node, originalEdge?, modifiedEdge? }
+```
 
-      type ModifierEntry = EdgeModifierEntry | NodeModifierEntry
-      ```
+## GraphModifier Class
 
-      ### Active Entry Tracking
-      ```typescript
-      // Tracks a modifier during graph traversal
-      type ModifierActiveEntry = {
-        modifier: ModifierEntry
-        interactiveBreadcrumb: ModifierInteractiveBreadcrumb  // Current parse state
-        originalFrom: Node              // First matched node
-        originalEdge?: Edge             // Original edge (for rollback)
-        modifiedEdge?: Edge             // Replacement edge
-      }
-      ```
+**Static**: `maybeLoad(options)` (returns instance or undefined), `load(options)` (throws if no vlt.json)
 
-  - type: architecture_guide
-    message: |
-      ## GraphModifier Class
+**Methods:**
+- `tryImporter(importer)` — match against `:root`/`:workspace`/`:project`
+- `tryNewDependency(from, spec)` — returns highest-specificity match
+- `tryDependencies(from, deps)` → `Map<string, ModifierActiveEntry>`
+- `updateActiveEntry(from, active)` — advance breadcrumb
+- `rollbackActiveEntries()` — restore original edges for incomplete matches
 
-      ### Private Fields
-      - `#config` — Cached `GraphModifierConfigObject` from vlt.json
-      - `#modifiers` — Set of all loaded `ModifierEntry` instances
-      - `#edgeModifiers` — Set of edge modifiers only
-      - `#nodeModifiers` — Set of node modifiers only
-      - `#initialEntries` — Map from first breadcrumb name → Set of modifiers (for non-importer starting queries like `#a > #b`)
-      - `#activeEntries` — Multi-level map: `ModifierEntry → name → Node → ModifierActiveEntry`
+## Integration with Ideal Build
 
-      ### Public Fields
-      - `activeModifiers: Set<ModifierActiveEntry>` — Currently active (in-progress) modifiers
-      - `modifierNames: Set<string>` — All modifier query strings from config
+```typescript
+const modifiers = GraphModifier.maybeLoad(options)
+for (const importer of importers) {
+  modifiers?.tryImporter(importer)
+  const refs = modifiers?.tryDependencies(importer, deps)
+  await appendNodes(..., modifiers, refs, ...)
+}
+// In append-nodes: check activeModifier, swap spec if complete, update after placement
+// queryModifier included in DepID extra via joinExtra()
+```
 
-      ### Static Methods
-      - `GraphModifier.maybeLoad(options)` — Returns instance if vlt.json has modifiers, else `undefined`
-      - `GraphModifier.load(options)` — Returns instance, throws if no vlt.json
+## Tips
 
-      ### Instance Methods
-      - `load(options)` — Parses vlt.json modifiers into entries
-      - `tryImporter(importer)` — Match importer against top-level selectors (`:root`, `:workspace`, `:project`)
-      - `tryNewDependency(from, spec)` — Match spec against active modifiers; returns highest-specificity match
-      - `tryDependencies(from, deps)` — Helper returning `Map<string, ModifierActiveEntry>` for all deps
-      - `updateActiveEntry(from, active)` — Advance breadcrumb state; register in `#activeEntries`
-      - `newModifier(from, modifier)` — Create new `ModifierActiveEntry`
-      - `deregisterModifier(modifier)` — Remove modifier from active tracking
-      - `rollbackActiveEntries()` — Restore original edges for incomplete modifiers after traversal
-
-  - type: integration_guide
-    message: |
-      ## Integration with Ideal Graph Building
-
-      ### In `refresh-ideal-graph.ts`
-      ```typescript
-      // Load modifiers once before processing importers
-      const modifiers = GraphModifier.maybeLoad(options)
-
-      for (const importer of orderedImporters) {
-        // Register importer-level selectors
-        modifiers?.tryImporter(importer)
-
-        // Get modifier refs for this importer's dependencies
-        const modifierRefs = modifiers?.tryDependencies(importer, deps)
-
-        await appendNodes(..., modifiers, modifierRefs, ...)
-      }
-      ```
-
-      ### In `append-nodes.ts`
-      ```typescript
-      // Check if modifier applies to this dependency
-      const activeModifier = modifierRefs?.get(spec.name)
-      const queryModifier = activeModifier?.modifier.query
-
-      // Swap spec if edge modifier is complete
-      if (queryModifier && completeModifier && 'spec' in activeModifier.modifier) {
-        spec = activeModifier.modifier.spec
-        if (spec.bareSpec === '-') continue  // Skip dependency entirely
-      }
-
-      // After placing node, update modifier state
-      if (activeModifier) {
-        modifiers?.updateActiveEntry(node, activeModifier)
-      }
-
-      // Get modifier refs for child dependencies
-      childModifierRefs = modifiers?.tryDependencies(node, nextDeps)
-      ```
-
-      ### Query Modifier in DepID
-      The `queryModifier` string is included in the node's DepID `extra` parameter (combined with `peerSetHash`), ensuring modified nodes are uniquely identified in resolution caches.
-
-  - type: integration_guide
-    message: |
-      ## User-facing Syntax and UX
-
-      All configuration lives in the project's `vlt.json` under the top-level `"modifiers"` key.
-
-      ### The `modifiers` key
-      ```json
-      {
-        "workspaces": "packages/*",
-        "modifiers": {
-          
-        }
-      }
-      ```
-
-      ### Edge Modifiers (Overrides / Resolutions)
-      Provide a string spec to replace the matched dependency's version/spec:
-      ```json
-      {
-        "modifiers": {
-          ":root > #a > #b": "^1.0.0"
-        }
-      }
-      ```
-
-      When multiple selectors match, the most specific selector wins (CSS specificity). Example (result is `1`):
-      ```json
-      {
-        "dependencies": {
-          "a": "^1.0.0"
-        },
-        "modifiers": {
-          ":root > #a > #b": "1",
-          "#a > #b": "2"
-        }
-      }
-      ```
-
-      Set a unique version for a given dependency across the graph:
-      ```json
-      {
-        "modifiers": {
-          "#react": "^19"
-        }
-      }
-      ```
-
-      Remove a dependency entirely with `-`:
-      ```json
-      {
-        "modifiers": {
-          "#unwanted-dep": "-"
-        }
-      }
-      ```
-
-      ### Package Extensions (Node Modifiers)
-      Add or adjust dependency declarations for specific packages. Provide an object instead of a string:
-      ```json
-      {
-        "modifiers": {
-          "#some-package": {
-            "peerDependencies": {
-              "react": "^18 || ^19"
-            },
-            "peerDependenciesMeta": {
-              "react": { "optional": true }
-            }
-          }
-        }
-      }
-      ```
-
-      ### Importer Selectors
-      - `:root` — Matches only the main project importer
-      - `:workspace` — Matches any workspace importer
-      - `:project` — Matches any importer (root or workspace)
-
-      ### References
-      - npm Overrides: <https://docs.npmjs.com/cli/v11/configuring-npm/package-json#overrides>
-      - pnpm Overrides: <https://pnpm.io/settings#overrides>
-      - Yarn Resolutions: <https://classic.yarnpkg.com/lang/en/docs/selective-version-resolutions/>
-      - Yarn Extensions DB: <https://github.com/yarnpkg/berry/blob/master/packages/yarnpkg-extensions/sources/index.ts>
-      - pnpm Package Extensions: <https://pnpm.io/settings#packageextensions>
-
-  - type: development_workflow
-    message: |
-      ## Development Workflow and Considerations
-
-      ### Loading Modifiers
-      - Use `GraphModifier.maybeLoad(options)` when modifiers are optional
-      - Use `GraphModifier.load(options)` when modifiers are required
-      - Modifiers are loaded from `vlt.json` via `@vltpkg/vlt-json`
-
-      ### Graph Building Integration
-      - Call `tryImporter()` for each importer before processing its dependencies
-      - Call `tryDependencies()` to get modifier refs for a node's dependencies
-      - Call `updateActiveEntry()` after placing a node to advance breadcrumb state
-      - The `queryModifier` string is passed through to `placePackage()` via `joinExtra()`
-
-      ### Rollback Mechanism
-      - `rollbackActiveEntries()` restores original edges for any modifiers that didn't complete their breadcrumb
-      - Called after graph traversal to clean up partial matches
-
-      ### Performance Considerations
-      - Prefer sharing `monorepo`, `packageJson`, and `scurry` instances across loaders/builders
-      - Use `skipLoadingNodesOnModifiersChange` when reusing a starting graph but modifiers changed since last build
-      - Hidden Lockfile (`node_modules/.vlt-lock.json`) accelerates Actual graph loads. If modifiers changed, rebuild Ideal.
-      - Deterministic ordering ensures reproducible lockfiles after modifier changes
-
-      ### Testing
-      - Validate selector specificity precedence (use `specificitySort()` from `@vltpkg/dss-breadcrumb`)
-      - Test overrides across direct and transitive dependencies
-      - Verify package extensions effect on peer/optional semantics
-      - Test rollback behavior for incomplete modifier matches
-      - Confirm Ideal graph reuses satisfying nodes to avoid unnecessary network fetches
-
-examples:
-  - input: |
-      # Override a transitive dependency
-      {
-        "modifiers": {
-          ":root > #webpack > #browserslist": "^4.23.0"
-        }
-      }
-    output: "Transitive browserslist spec overridden via DSS selector"
-
-  - input: |
-      # Pin a single version across the graph
-      {
-        "modifiers": {
-          "#react": "^19"
-        }
-      }
-    output: "All matching react specs unified to ^19"
-
-  - input: |
-      # Using modifiers in code
-      const modifiers = GraphModifier.maybeLoad(options)
-      modifiers?.tryImporter(graph.mainImporter)
-      const refs = modifiers?.tryDependencies(node, deps)
-      const active = refs?.get('react')
-      if (active) modifiers?.updateActiveEntry(placedNode, active)
-    output: "Modifier tracking during graph traversal"
-
-  - input: |
-      # Remove an unwanted dependency
-      {
-        "modifiers": {
-          "#deprecated-package": "-"
-        }
-      }
-    output: "Dependency skipped entirely when bareSpec is '-'"
-
-metadata:
-  priority: high
-  version: 2.0
-  tags:
-    - modifiers
-    - graph
-    - overrides
-    - extensions
-    - dss
-    - breadcrumb
-  related_rules:
-    - graph_workspace_architecture
-    - graph_data_structure
-    - graph_lockfiles
-    - graph_ideal_append_nodes
-</rule>
+- `rollbackActiveEntries()` called after traversal to clean partial matches
+- Use `skipLoadingNodesOnModifiersChange` when reusing graph but modifiers changed
+- Deterministic ordering ensures reproducible lockfiles after changes
diff --git a/.cursor/rules/graph/peers.mdc b/.cursor/rules/graph/peers.mdc
@@ -3,383 +3,92 @@ description: Peer dependency context isolation and resolution in vlt graphs
 globs: src/graph/src/ideal/peers.ts,src/graph/test/ideal/peers.ts,src/graph/src/graph.ts,src/dep-id/src/browser.ts
 alwaysApply: false
 ---
-# Peer Dependencies in Graph
+# Peer Dependencies
 
-Comprehensive guide to peer dependency handling in `@vltpkg/graph`, covering context isolation, package duplication, and the `peerSetHash` mechanism.
+How vlt isolates peer contexts and duplicates packages when peer requirements differ.
 
-<rule>
-name: graph_peers
-description: How vlt isolates peer dependency contexts and duplicates packages when peer requirements differ
-filters:
-  # Peer dependency implementation files
-  - type: path
-    pattern: "^src/graph/src/ideal/peers\\.ts$"
-  - type: path
-    pattern: "^src/graph/test/ideal/peers\\.ts$"
-  # DepID utilities for extra parameter handling
-  - type: path
-    pattern: "^src/dep-id/src/(browser|index)\\.ts$"
-  # Graph core that handles peerSetHash
-  - type: path
-    pattern: "^src/graph/src/graph\\.ts$"
-  # Node class with peerSetHash property
-  - type: path
-    pattern: "^src/graph/src/node\\.ts$"
-  # Mentions of peer dependencies in content
-  - type: content
-    pattern: "peerSetHash|peerDependencies|splitExtra|joinExtra|peer context"
+## Behavior
 
-actions:
-  - type: guide
-    message: |
-      ## Overview
+1. **Attempt reuse first**: try single version satisfying all peer contexts
+2. **Fork when needed**: subdivide graph into peer context groups on conflict
+3. **Duplicate packages**: clone nodes needing different peer versions
+4. **Track via `peerSetHash`**: `peer.N` identifier in DepID extra
 
-      vlt handles peer dependencies by **isolating peer contexts**, allowing multiple versions of the same package to coexist when different dependency trees require incompatible peer versions.
+## Core Algorithm (`src/graph/src/ideal/peers.ts`)
 
-      Key behaviors:
-      - **Attempts reuse first**: vlt tries to resolve to a single unique version that satisfies all peer contexts
-      - **Forks contexts when needed**: when a single version cannot satisfy all requirements, vlt subdivides the dependency graph into peer context groups
-      - **Duplicates packages**: packages requiring different peer versions are duplicated in the vlt store
-      - **Tracks contexts**: uses `peerSetHash` internally to identify and duplicate nodes affected by peer context modifications
+### `checkPeerEdgesCompatible()` — 4-Phase Check
 
-  - type: architecture_guide
-    message: |
-      ## Peer Context Isolation (`src/graph/src/ideal/peers.ts`)
+0. **Unprocessed Node**: peer edge doesn't exist yet → incompatible (conservative)
+1. **Context Mismatch**: context has different target → idempotency check first (existing target satisfies all specs?) → compatible or fork
+2. **Sibling Mismatch**: sibling edge differs → idempotency check → compatible or fork
+3. **Parent Declared Peer**: parent has alternative candidates → check via `graph.nodesByName.get(peerName)` → fork if alternative satisfies both
 
-      Core algorithm:
-      1. **Analyze current peer context**: Check if existing resolved nodes can satisfy new peer dependencies
-      2. **Attempt reuse**: Try to use a single version across all occurrences of the peer dependency
-      3. **Fork when necessary**: Create new peer contexts when version conflicts arise
-      4. **Duplicate nodes**: Clone package nodes that need different peer versions
-      5. **Track with peerSetHash**: Append unique identifiers to DepIDs to distinguish peer contexts
+Uses per-call memoization (`satisfiesMemo` Map) for `satisfies()` calls.
 
-      Implementation details:
-      - Peer contexts are deterministically identified using `peerSetHash` strings (format: `peer.N` where N is a numeric identifier)
-      - The `peerSetHash` is appended to the node's DepID as part of the `extra` parameter
-      - Multiple versions of the same package can exist in the graph, differentiated by their `peerSetHash`
+### `resolvePeerDeps()` — 4-Priority Resolution
 
-      ### Helper Functions
-      The module uses several internal helper functions to reduce duplication:
-      - **`nodeSatisfiesSpec(node, spec, fromNode, graph)`**: Wraps common `satisfies()` call pattern
-      - **`parseSpec(name, bareSpec, fromNode, graph)`**: Wraps `Spec.parse` with registry options
-      - **`getForkKey(peerContext, entries)`**: Generates cache key for fork operations (format: `{baseIndex}::{signatures}`)
-      - **`shouldIgnoreContextMismatch()`**: Prevents cross-importer peer context leakage
-      - **`buildIncompatibleResult()`**: Creates fork entry when target satisfies peer spec
-      - **`findFromPeerClosure()`**: BFS search through peer edges (depth limit: 3) for cycle resolution
+1. Direct sibling (same-level dep)
+2. Peer closure: BFS through peer edges of sibling targets (depth limit: 3)
+3. Peer context lookup
+4. Defer to next level
 
-      ### Per-Call Memoization in `checkPeerEdgesCompatible()`
-      The function uses per-call memoization to avoid redundant `satisfies()` calls:
-      ```typescript
-      const satisfiesMemo = new Map<string, boolean>()
-      const satisfiesNodeSpec = (node: Node, spec: Spec): boolean => {
-        const key = `${node.id}\0${spec.type}\0${spec.bareSpec}\0${String(spec.final)}`
-        let result = satisfiesMemo.get(key)
-        if (result === undefined) {
-          result = satisfies(node.id, spec, fromLocation, projectRoot, monorepo)
-          satisfiesMemo.set(key, result)
-        }
-        return result
-      }
-      ```
-      This improves performance when the same node/spec pairs are checked multiple times.
+### `postPlacementPeerCheck()` — 3-Phase Post-Level
 
-  - type: architecture_guide
-    message: |
-      ## DepID Extra Parameter (`src/dep-id/src/browser.ts`)
+1. `putEntries()` on all children → collect which need forking
+2. Fork or reuse sibling contexts
+3. `resolvePeerDeps()` on all children
 
-      The `extra` parameter in DepIDs now serves dual purposes:
-      1. **Modifier**: Query-based graph modifications (e.g., `:root > #package`)
-      2. **peerSetHash**: Peer context identifier (e.g., `peer.1`, `peer.2`)
+### Helper Functions
 
-      ### Utilities
+- `nodeSatisfiesSpec(node, spec, fromNode, graph)` — wraps `satisfies()`
+- `parseSpec(name, bareSpec, fromNode, graph)` — wraps `Spec.parse` with registry options
+- `getForkKey(peerContext, entries)` — cache key: `{baseIndex}::{signatures}`
+- `shouldIgnoreContextMismatch()` — prevents cross-importer peer leakage
+- `findFromPeerClosure()` — BFS through peer edges (depth limit: 3)
 
-      **`joinExtra({ modifier?, peerSetHash? })`**
-      - Combines modifier and peerSetHash into a single string
-      - Returns `undefined` if both are empty
-      - Concatenates without separator when both present: `${modifier}${peerSetHash}`
-      - Examples:
-        - `joinExtra({ modifier: ':root > #pkg' })` → `':root > #pkg'`
-        - `joinExtra({ peerSetHash: 'peer.1' })` → `'peer.1'`
-        - `joinExtra({ modifier: ':root > #pkg', peerSetHash: 'peer.1' })` → `':root > #pkgpeer.1'`
+## DepID Extra Parameter (`src/dep-id/src/browser.ts`)
 
-      **`splitExtra(extra: string)`**
-      - Parses an extra string into its components
-      - Detects peerSetHash by looking for `peer.` delimiter
-      - Returns `{ modifier?, peerSetHash? }`
-      - Examples:
-        - `splitExtra('peer.1')` → `{ peerSetHash: 'peer.1' }`
-        - `splitExtra(':root > #pkg')` → `{ modifier: ':root > #pkg' }`
-        - `splitExtra(':root > #pkgpeer.2')` → `{ modifier: ':root > #pkg', peerSetHash: 'peer.2' }`
+`extra` serves dual purpose: modifier + peerSetHash.
 
-  - type: architecture_guide
-    message: |
-      ## Node peerSetHash Property (`src/graph/src/node.ts`)
+- `joinExtra({ modifier?, peerSetHash? })` → combined string or undefined
+- `splitExtra(extra)` → `{ modifier?, peerSetHash? }` (detects `peer.` delimiter)
 
-      Nodes now have an optional `peerSetHash?: string` property:
-      - Set during ideal graph construction when peer context forking occurs
-      - Included in node serialization (lockfile, JSON output)
-      - Preserved during graph operations (reset, gc, etc.)
-      - Used to identify nodes that are duplicates for peer context isolation
+## Node `peerSetHash` (`node.ts`)
 
-      The property is:
-      - Parsed from DepID's extra parameter during lockfile load
-      - Set by peer resolution logic during ideal graph building
-      - Combined with modifier when constructing resolution cache keys
+Optional `peerSetHash?: string`. Set during ideal build on context forking. Preserved in serialization, parsed from DepID extra on lockfile load.
 
-  - type: architecture_guide
-    message: |
-      ## Graph Integration (`src/graph/src/graph.ts`)
+## Graph Integration (`graph.ts`)
 
-      ### Resolution Cache
-      - Cache keys now include the full `extra` string (both modifier and peerSetHash)
-      - `getResolutionCacheKey(spec, location, extra)` incorporates both components
-      - Ensures nodes with different peer contexts don't incorrectly share resolution cache entries
+- Resolution cache keys include full `extra` (modifier+peerSetHash)
+- `placePackage()` splits `extra` → assigns `node.modifier` and `node.peerSetHash`
+- `nodesByName` sorted by DepID for deterministic resolution
+- `peerContextForkCache: Map<string, PeerContext>` — prevents duplicate contexts. Key: `{baseIndex}::{sortedEntrySignatures}`
 
-      ### Node Placement
-      - `placePackage()` accepts `extra` parameter containing combined modifier + peerSetHash
-      - Automatically splits `extra` and assigns to `node.modifier` and `node.peerSetHash`
-      - `findResolution()` accepts `extra` for cache key construction
+## Workspace Isolation
 
-      ### nodesByName Ordering
-      - The `nodesByName` set is now sorted deterministically by DepID
-      - Ensures consistent graph resolution when reusing nodes across peer contexts
-      - Sorting happens in `addNode()` after adding new nodes to the set
+Each non-main importer gets fresh peer context:
+```typescript
+if (fromNode.importer && fromNode !== graph.mainImporter) {
+  const nextPeerContext: PeerContext = new Map()
+  nextPeerContext.index = graph.nextPeerContextIndex()
+  initialPeerContext = nextPeerContext
+}
+```
 
-      ### Peer Context Fork Cache
-      - `graph.peerContextForkCache: Map<string, PeerContext>` caches forked contexts
-      - Prevents creating duplicate contexts for identical fork operations
-      - Key format: `{baseIndex}::{sortedEntrySignatures}` (constructed by `getForkKey()`)
-      - Significantly reduces memory usage in multi-workspace scenarios
+## DSS Selectors
 
-  - type: architecture_guide
-    message: |
-      ## Key Algorithms
+`:peer`, `:peer:optional`, `:has(:peer)`, `:peerOptional`
 
-      ### `checkPeerEdgesCompatible()` - 4-Phase Compatibility Check
-      Determines if a node can be reused given the current peer context:
+## Lockfile Format
 
-      0. **CHECK 0 - Unprocessed Node**: If peer edge doesn't exist yet on the existing node
-         - Returns incompatible (cannot verify compatibility)
-         - Peer resolution depends on original placement context, which may differ
-         - Conservative check prevents incorrect reuse when placement order varies
-         - Note: Dangling edges (edge exists but no target) are handled separately
+```
+"~~package@1.0.0~peer.1": [...]     // node with peerSetHash
+"file~. package": "prod ^1.0.0 ~~package@1.0.0~peer.1"  // edge to peer context
+```
 
-      1. **CHECK 1 - Context Mismatch**: If peer context has a different target for this peer name
-         - **Idempotency Check**: First checks if existing edge target satisfies the peer spec
-         - If existing target satisfies spec AND all context specs → returns compatible (no conflict)
-         - Otherwise returns incompatible with fork entry pointing to context's preferred target
-         - Exception: Ignores mismatch if parent's direct dep satisfies a different spec
+## Tips
 
-      2. **CHECK 2 - Sibling Mismatch**: If sibling edge has different target than existing peer edge
-         - **Idempotency Check**: First checks if existing edge target satisfies both peer spec and sibling spec
-         - If existing target satisfies both → returns compatible (prefer keeping existing)
-         - Otherwise returns incompatible with fork entry
-
-      3. **CHECK 3 - Parent Declared Peer**: If parent manifest declares a peer with potential alternatives
-         - **Early Continue**: If existing edge target satisfies parent's declared spec → compatible
-         - Uses `graph.nodesByName.get(peerName)` for efficient candidate lookup (not full graph scan)
-         - Only searches for alternatives if existing target is incompatible with parent spec
-         - Returns incompatible if an alternative candidate satisfies both parent and peer specs
-
-      ### `resolvePeerDeps()` - 4-Priority Resolution
-      Resolves peer dependencies after node placement:
-
-      1. **PRIORITY 1 - Direct Sibling**: Sibling of the same parent (same-level dep)
-      2. **PRIORITY 2 - Peer Closure**: BFS through peer edges of sibling targets (depth limit: 3)
-         - Handles cycles like A→B(peer)→C(peer)→A(peer)
-      3. **PRIORITY 3 - Peer Context**: Look up target in peer context entries
-      4. **PRIORITY 4 - Defer**: Add to next level deps for later resolution
-
-      ### `postPlacementPeerCheck()` - 3-Phase Post-Level Processing
-      Called after all nodes at a level are placed:
-
-      1. **PHASE 1 - Collect**: Call `putEntries()` on all children, collect which need forking
-      2. **PHASE 2 - Fork/Reuse**: Create new contexts or reuse sibling contexts when compatible
-      3. **PHASE 3 - Resolve**: Call `resolvePeerDeps()` on all children
-
-  - type: integration_guide
-    message: |
-      ## Query Selectors for Peer Dependencies
-
-      Users can inspect peer dependencies using DSS selectors:
-
-      - `:peer` — Returns all peer dependencies in the project
-      - `:peer:optional` — Returns optional peer dependencies (potentially missing)
-      - `:has(:peer)` — Returns packages that have direct peer dependencies
-      - `:peerOptional` — Returns peer dependencies marked as both peer and optional
-
-      These selectors are documented in the user-facing docs at `www/docs/src/content/docs/cli/peer-dependencies.mdx`
-
-  - type: data_format_guide
-    message: |
-      ## Lockfile Representation
-
-      Peer context information is preserved in lockfiles:
-
-      **Nodes**: DepID includes peerSetHash in the extra parameter
-      ```
-      "~~package@1.0.0~peer.1": [...]
-      "~~package@1.0.0~peer.2": [...]
-      ```
-
-      **Edges**: References include the full DepID with peerSetHash
-      ```
-      "file~. package": "prod ^1.0.0 ~~package@1.0.0~peer.1"
-      ```
-
-      **Loading**: `loadNodes()` in `src/graph/src/lockfile/load-nodes.ts` uses `splitExtra()` to parse both modifier and peerSetHash from the DepID
-
-  - type: architecture_guide
-    message: |
-      ## Workspace Peer Context Isolation
-
-      Each workspace importer gets its **own peer context** to prevent cross-workspace peer leakage.
-
-      ### The Problem
-      Without isolation, peer targets from the root importer could incorrectly influence workspace dependencies:
-      - Root: `react@^18` → resolves to `react@18.3.1`
-      - Workspace A: `react@^19` with peer-dependent package
-      - Without isolation: peer dep might incorrectly resolve to 18.3.1
-
-      ### The Solution
-      In `appendNodes()`, non-main importers get fresh peer contexts:
-      ```typescript
-      if (fromNode.importer && fromNode !== graph.mainImporter) {
-        const nextPeerContext: PeerContext = new Map()
-        nextPeerContext.index = graph.nextPeerContextIndex()
-        graph.peerContexts[nextPeerContext.index] = nextPeerContext
-        initialPeerContext = nextPeerContext
-      }
-      ```
-
-      ### Test Coverage
-      - `test/ideal/peers.ts`: "multi-workspace peer context isolation with 4 workspaces"
-      - `test/ideal/append-nodes.ts`: "creates fresh peer context for non-main workspace importers"
-
-  - type: development_workflow
-    message: |
-      ## Testing Peer Dependencies
-
-      Test files: `src/graph/test/ideal/peers.ts`
-
-      Key test scenarios:
-      - Multiple major versions of the same peer (React 18 vs 19)
-      - Peer dependency cycles (e.g., `@isaacs/peer-dep-cycle-a/b/c`)
-      - Optional peer dependencies
-      - Flexible peer ranges that can be satisfied by multiple versions
-      - Mixed contexts where some dependencies share peers and others don't
-      - **Multi-workspace peer context isolation** (4+ workspaces with different peer requirements)
-      - **Outlier peer contexts** (workspace sibling with different peer targets)
-      - **Idempotency from lockfile**: Re-running ideal build produces identical graph
-      - **Context mismatch tolerance**: Existing edge satisfies spec despite different context target
-      - **Sibling mismatch tolerance**: Existing edge satisfies both specs despite different sibling target
-
-      Testing patterns:
-      - Build ideal graphs with packages declaring peer dependencies
-      - Verify correct number of duplicate nodes created
-      - Check that peerSetHash values are assigned and unique
-      - Validate lockfile serialization includes peerSetHash
-      - Confirm query selectors return expected peer dependency sets
-      - Test mermaid diagram generation showing peer context isolation
-      - **Verify `graph.peerContexts.length > 1` for multi-workspace isolation**
-
-  - type: development_workflow
-    message: |
-      ## Practical Tips
-
-      When working with peer dependencies:
-      - **Always use joinExtra()**: When constructing extra parameters, use `joinExtra({ modifier, peerSetHash })` rather than string concatenation
-      - **Always use splitExtra()**: When parsing extra parameters, use `splitExtra(extra)` to correctly handle both components
-      - **Preserve peerSetHash**: When copying or transforming nodes, ensure peerSetHash is maintained
-      - **Cache key awareness**: Resolution cache keys must include the full extra string to avoid incorrect cache hits
-      - **Test with real packages**: Use actual npm packages with peer dependencies (like React ecosystem) for integration tests
-      - **Check lockfile round-trips**: Verify that peerSetHash survives serialization and deserialization
-
-examples:
-  - input: |
-      // Correctly combining modifier and peerSetHash
-      const extra = joinExtra({ 
-        modifier: ':root > #react-dom', 
-        peerSetHash: 'peer.1' 
-      })
-      const node = graph.placePackage(from, 'prod', spec, manifest, id, extra)
-    output: "Node placed with both modifier and peer context tracking"
-
-  - input: |
-      // Parsing extra from DepID during lockfile load
-      const { modifier, peerSetHash } = splitExtra(extra)
-      if (modifier) node.modifier = modifier
-      if (peerSetHash) node.peerSetHash = peerSetHash
-    output: "Extra parameter correctly split into components"
-
-  - input: |
-      // Finding resolution with peer context
-      const extra = joinExtra({ peerSetHash: 'peer.2' })
-      const resolved = graph.findResolution(spec, fromNode, extra)
-    output: "Resolution respects peer context isolation"
-
-  - input: |
-      // Using helper functions to check peer compatibility
-      import { nodeSatisfiesSpec, parseSpec, checkPeerEdgesCompatible } from './peers.ts'
-      
-      // Check if node satisfies spec with proper context
-      const satisfies = nodeSatisfiesSpec(candidateNode, peerSpec, fromNode, graph)
-      
-      // Parse spec with registry options from main importer
-      const spec = parseSpec('react', '^18.0.0', fromNode, graph)
-      
-      // Full peer compatibility check (3 phases)
-      const result = checkPeerEdgesCompatible(existingNode, fromNode, peerContext, graph)
-      if (!result.compatible && result.forkEntry) {
-        // Need to fork context with this entry
-        const forked = forkPeerContext(graph, peerContext, [result.forkEntry])
-      }
-    output: "Peer compatibility checked using helper functions and context forked if needed"
-
-  - input: |
-      // Peer context fork caching in action
-      // In forkPeerContext():
-      const cacheKey = getForkKey(base, entries)  // e.g., "0::react:^18.0.0:npm:react@18.3.1"
-      const cached = graph.peerContextForkCache.get(cacheKey)
-      if (cached) return cached  // Reuse existing forked context
-      
-      // Create new context and cache it
-      const forked = new Map(base) as PeerContext
-      forked.index = graph.nextPeerContextIndex()
-      graph.peerContextForkCache.set(cacheKey, forked)
-    output: "Fork caching prevents duplicate peer contexts in multi-workspace scenarios"
-
-  - input: |
-      // Idempotency test: rebuild from lockfile produces identical graph
-      // First build
-      await appendNodes(packageInfo, graph, mainImporter, deps, ...)
-      const firstNodeIds = new Set([...graph.nodes.values()].map(n => n.id))
-      const firstLibAUi = libA.edgesOut.get('ui-component')?.to
-      
-      // Second build on same graph (simulates re-install from lockfile)
-      await appendNodes(packageInfo, graph, mainImporter, deps, ...)
-      const secondNodeIds = new Set([...graph.nodes.values()].map(n => n.id))
-      const secondLibAUi = libA.edgesOut.get('ui-component')?.to
-      
-      t.same(secondNodeIds, firstNodeIds, 'should have identical nodes (idempotent)')
-      t.equal(secondLibAUi?.id, firstLibAUi?.id, 'should reuse same ui-component node')
-    output: "Idempotency verified: existing valid resolutions are preserved"
-
-metadata:
-  priority: high
-  version: 1.4
-  tags:
-    - graph
-    - peer-dependencies
-    - context-isolation
-    - node-duplication
-    - dep-id
-    - lockfile
-    - idempotency
-  related_rules:
-    - graph_data_structure
-    - graph_ideal
-    - graph_ideal_append_nodes
-    - graph_lockfiles
-    - monorepo-structure
-</rule>
+- Always use `joinExtra()`/`splitExtra()` — never string concatenation
+- Preserve `peerSetHash` when copying/transforming nodes
+- Resolution cache must include full `extra` to avoid incorrect hits
+- Test idempotency: rebuild from lockfile → identical graph
diff --git a/.cursor/rules/graph/reify.mdc b/.cursor/rules/graph/reify.mdc
@@ -3,146 +3,40 @@ description: Reify process (applying Diff to node_modules)
 globs: src/graph/src/reify/*,src/graph/test/reify/*
 alwaysApply: false
 ---
-# Reify (Apply Graph Changes to node_modules)
+# Reify (Apply Graph Changes)
 
-Guidance for working with the Reify step in `@vltpkg/graph`, which transforms an Actual Graph on disk to match an Ideal Graph by applying the minimal set of filesystem operations.
+Entry: `src/graph/src/reify/index.ts` → `reify(options)`
 
-<rule>
-name: graph_reify
-description: How reify computes and applies minimal filesystem changes, with module responsibilities and integration tips
-filters:
-  # Reify implementation and helpers
-  - type: path
-    pattern: "^src/graph/src/reify/"
-  - type: file_name
-    pattern: "^(index|refresh-ideal-graph|add-edges|add-edge|delete-nodes|delete-edges|delete-edge|internal-hoist|build|rollback|optional-fail|bin-paths|calculate-save-value|update-importers-package-json)\\.ts$"
-  # Diff usage is central to reify
-  - type: content
-    pattern: "new Diff\(actual, graph\)|diff\\.nodes|diff\\.edges"
+Makes on-disk install (Actual) match desired state (Ideal) via minimal filesystem ops.
 
-actions:
-  - type: guide
-    message: |
-      ## Overview
+## Flow
 
-      The `reify(options)` function makes the on-disk install (Actual Graph) match the desired state (Ideal Graph). It:
-      1. Loads the Actual Graph (if not provided) with `loadManifests: true`.
-      2. Computes a `Diff(actual, ideal)` and returns early if there are no changes.
-      3. Applies a minimal sequence of filesystem operations to add/extract nodes, create or remove dependency links, hoist internal links, run lifecycle scripts, and write lockfiles.
+1. Load Actual (if not provided) with `loadManifests: true`
+2. Compute `Diff(actual, ideal)` — return early if no changes
+3. Prepare `RollbackRemove` for reversibility
+4. **Extract nodes**: `addNodes()` → fetch/extract into `.vlt` store. Optional deps use `optionalFail()` to prune subgraphs instead of failing
+5. **Delete edges**: `deleteEdges()` → remove outdated links + bins
+6. Run extraction+deletion via `callLimit(actions, { limit })` where `limit = Math.max(availableParallelism()-1, 1) * 8`
+7. **Add edges**: `addEdges()` → create symlinks + bin links (Windows: `@vltpkg/cmd-shim`)
+8. **Hoist**: `internalHoist()` → `node_modules/.vlt/node_modules/<name>` symlinks. Preference: importer deps > registry > highest version > lexicographic DepID
+9. **Build**: `build()` → lifecycle scripts (preinstall/install/postinstall/prepare), chmod bins
+10. **Lockfiles**: save main `vlt-lock.json` (`saveData()`), hidden `node_modules/.vlt-lock.json` (`saveHidden()`)
+11. **Cleanup**: gc if optional failures, delete removed nodes, update importer `package.json` if `add/remove` changed deps, confirm rollback
 
-      Entry point: `src/graph/src/reify/index.ts` → `reify(options)`
+## Module Responsibilities
 
-  - type: architecture_guide
-    message: |
-      ## Execution Flow
+- `index.ts` — orchestrator
+- `add-nodes.ts`/`extract-node.ts` — extract into store via `packageInfo.extract()`, platform gating, optional fail
+- `add-edge.ts`/`add-edges.ts` — symlinks + bin links
+- `delete-edge.ts`/`delete-edges.ts` — remove links + `.bin` entries
+- `internal-hoist.ts` — preferred candidate selection + symlinks
+- `build.ts` — lifecycle scripts, chmod bins
+- `optional-fail.ts` — `removeOptionalSubgraph`, flags `diff.hadOptionalFailures`
+- `rollback.ts` — best-effort revert
+- `update-importers-package-json.ts`/`calculate-save-value.ts` — save deps to importers
 
-      - Build `Diff`:
-        - `const diff = new Diff(actual, graph)`; if `!diff.hasChanges()`, return early.
+## Usage
 
-      - Prepare rollback:
-        - Use `RollbackRemove` to ensure all steps are reversible until confirmed.
-
-      - Node extraction and edge deletions:
-        - `addNodes(diff, scurry, remover, options, packageInfo)` → returns async actions to fetch/extract nodes into the `.vlt` store (registry/git/tarball installs). Optional deps use `optionalFail()` to remove subgraphs instead of failing the whole reify.
-        - `deleteEdges(diff, scurry, remover)` → returns async actions removing outdated links and their bins.
-        - Actions run via `callLimit(actions, { limit })` where `limit = (availableParallelism() - 1) * 8`.
-
-      - Link creation:
-        - `addEdges(diff, packageJson, scurry, remover)` → creates symlinks in importer `node_modules` and links package bins into `.bin`. On Windows, uses `@vltpkg/cmd-shim` for executables.
-
-      - Hoisting:
-        - `internalHoist(diff.to, options, remover)` → sets up `node_modules/.vlt/node_modules/<name>` symlinks to preferred candidates per package name. Preference:
-          - Prefer dependencies that are direct deps of an importer.
-          - Prefer registry deps over non-registry.
-          - For registry deps, prefer highest version (via `@vltpkg/semver`).
-          - Otherwise, pick lexicographically highest `DepID`.
-
-      - Build phase:
-        - `build(diff, packageJson, scurry)` walks from importers, reading manifests as needed, then:
-          - Runs `install` lifecycle (preinstall/install/postinstall) where present.
-          - Runs `prepare` for importers, git deps, or non-store deps.
-          - Ensures package bin files are executable (chmod adds `0o111`).
-
-      - Lockfiles and state persistence:
-        - Save minimal main lockfile with `lockfile.save(options)`.
-        - Save hidden lockfile with manifests using `saveHidden(options)`.
-        - Persist resolved ideal data with `saveData(lockfileData(options), scurry.resolve('vlt-lock.json'), false)`.
-        - If `vlt.json` exists, copy to `node_modules/.vlt/vlt.json` to commit modifier config in the store.
-
-      - Cleanup:
-        - If optional failures occurred, call `graph.gc()` and adjust `diff` sets accordingly.
-        - Remove deleted nodes from the store via `deleteNodes(diff, remover, scurry)`.
-        - If `add/remove` modified importer dependencies, write updated `package.json` files via `updatePackageJson()`.
-        - Confirm rollback on success; otherwise `rollback()` cleans partial changes.
-
-  - type: architecture_guide
-    message: |
-      ## Module Responsibilities
-
-      - `index.ts` — Orchestrates the entire reify process; loads Actual, computes Diff, coordinates steps, writes lockfiles.
-      - `refresh-ideal-graph.ts` — Extracts new nodes into the store using `@vltpkg/package-info.extract()`; handles platform gating and deprecated/optional cases with `optionalFail()`.
-      - `add-edge.ts` / `add-edges.ts` — Creates symlinks and bin links; on Windows, uses cmd shims via `@vltpkg/cmd-shim`.
-      - `delete-edge.ts` / `delete-edges.ts` — Removes outdated links and related `.bin` entries (including `*.cmd`/`*.ps1` on Windows).
-      - `internal-hoist.ts` — Determines and symlinks preferred candidates into `node_modules/.vlt/node_modules`.
-      - `build.ts` — Runs lifecycle scripts and ensures bins are executable; traverses dependency graph using `graph-run`.
-      - `optional-fail.ts` — On failures of optional nodes, removes their reachable optional subgraphs from the target graph via `removeOptionalSubgraph` and flags `diff.hadOptionalFailures`.
-      - `rollback.ts` — Best-effort revert of partially applied changes using a fresh `RollbackRemove` and the accumulated remover.
-      - `update-importers-package-json.ts` / `calculate-save-value.ts` — Writes updated dependency specs to importers based on `add/remove`, preserving expected save semantics (eg. `^` ranges for registry deps).
-
-  - type: integration_guide
-    message: |
-      ## Using reify()
-
-      - Provide: `graph` (Ideal), and either let reify load Actual or pass `actual` explicitly.
-      - Required shared instances: `packageInfo`, `packageJson`, `scurry`. Reuse these across phases.
-      - Side effects:
-        - Filesystem changes under `node_modules` and `.vlt` store
-        - `vlt-lock.json` and `node_modules/.vlt-lock.json` writes
-        - Optional `package.json` updates for importers (when `add/remove` change manifests)
-      - Platform considerations:
-        - Symlinks differ across platforms; Windows uses cmd shims for bins and EEXIST is tolerated when multiple paths could write the same link.
-      - Performance:
-        - Parallelize extraction and deletions with `callLimit`; link and remove steps often batch with `Promise.all`.
-
-  - type: development_workflow
-    message: |
-      ## Practical Tips
-
-      - If you already have `actual` loaded (eg. for inspection), pass it to avoid re-reading.
-      - For dry runs, compute `new Diff(actual, ideal)` yourself and inspect `hasChanges()` and the sets, but note `reify()` always applies changes when invoked.
-      - Ensure modifiers and options used to build the Ideal graph are reflected in lockfile saves to maintain reproducibility.
-      - Handle optional dependency failures gracefully; reify already prunes optional subgraphs instead of failing the install.
-
-examples:
-  - input: |
-      import { actual, ideal, reify } from '@vltpkg/graph'
-      
-      const from = actual.load({ projectRoot, packageJson, scurry, loadManifests: true })
-      const to = await ideal.build({ projectRoot, packageInfo, packageJson, scurry })
-      const diff = await reify({ graph: to, actual: from, packageInfo, packageJson, scurry })
-    output: "Applied minimal changes to align Actual with Ideal; diff returned"
-
-  - input: |
-      // Update importer manifests when add/remove modified dependencies
-      await reify({ graph, packageInfo, packageJson, scurry, add, remove })
-    output: "Importer package.json files updated; lockfiles saved; store hoisted"
-
-metadata:
-  priority: high
-  version: 1.0
-  tags:
-    - graph
-    - reify
-    - diff
-    - lifecycle
-    - lockfiles
-    - hoist
-  related_rules:
-    - graph_workspace_architecture
-    - graph_data_structure
-    - graph_lockfiles
-    - graph_modifiers
-    - graph_load_actual
-    - monorepo-structure
-</rule>
+Provide `graph` (Ideal). Optionally pass `actual` to skip reload. Required shared instances: `packageInfo`, `packageJson`, `scurry`.
 
+Side effects: filesystem changes under `node_modules`/`.vlt`, lockfile writes, optional `package.json` updates.
diff --git a/.cursor/rules/gui-validation-workflow.mdc b/.cursor/rules/gui-validation-workflow.mdc
@@ -1,165 +1,26 @@
 ---
-description: 
-globs: src/gui/*
+description: GUI workspace validation (Vitest, no coverage)
+globs: src/gui/src/**/*,src/gui/test/**/*
 alwaysApply: false
 ---
-# GUI Workspace Validation Workflow
+# GUI Workspace Validation
 
-Rule for validating code quality, formatting, and tests specifically for the `src/gui` workspace.
+Differs from `@code-validation-workflow.mdc`: uses **Vitest** (not tap), **no code coverage**.
 
-<rule>
-name: gui_validation_workflow
-description: Standards and workflow for validating code quality, formatting, and tests in the src/gui workspace
-filters:
-  # Match files specifically within the src/gui workspace
-  - type: path
-    pattern: "^src/gui/"
-  # Match any file that might need validation within gui workspace
-  - type: file_extension
-    pattern: "\\.(js|jsx|ts|tsx|json|md|css|scss)$"
-  # Match file modification events in gui workspace
-  - type: event
-    pattern: "file_modify"
+## Steps (from `src/gui` dir)
 
-actions:
-  - type: suggest
-    message: |
-      **GUI Workspace Validation Steps**
-      
-      When working in the `src/gui` workspace, use these modified validation steps:
+1. `pnpm format`
+2. `pnpm lint`
+3. `pnpm test --reporter=tap` (single file: `pnpm test --reporter=tap test/components/Foo.test.tsx`)
+4. **Skip coverage** — not measured in GUI workspace
+5. `pnpm posttest` (type check)
 
-      1. Format code:
-         ```bash
-         pnpm format
-         ```
-         This ensures consistent code formatting across the codebase.
-         If formatting issues are found, fix them before proceeding.
+## Snapshots
 
-      2. Lint code:
-         ```bash
-         pnpm lint
-         ```
-         This checks for style guide violations and potential issues.
-         If linting errors are found:
-         - **For common linting issues (unused variables/imports)**: Refer to `@linting-error-handler.mdc` for systematic solutions
-         - Review each error message
-         - Fix the issues in the affected files
-         - Run `pnpm lint` again to verify fixes
-         
-         💡 **Pro tip**: Most linting errors fall into common patterns. Use the linting error handler rule for quick, systematic fixes.
+`pnpm snap --reporter=tap` — review changes carefully before updating.
 
-      3. Run tests:
-         ```bash
-         pnpm test --reporter=tap
-         ```
-         📋 **Testing Framework**: The GUI workspace uses **Vitest** as its testing framework (NOT tap).
-         Test files should use Vitest syntax with `describe()`, `it()`, and `expect()` functions.
-         Import pattern: `import { describe, it, expect } from 'vitest'`
-         
-         This runs all tests in the GUI workspace with TAP reporter.
-         If tests fail:
-         - Review the test output for failures
-         - Fix any failing tests
-         - Run tests again to verify fixes
+## Test Syntax
 
-         3.1. Running tests for a specific file:
-             ```bash
-             pnpm test --reporter=tap <path-to-test-file.ts>
-             ```
-             Use this command when working on a specific module to iterate faster.
-             Example:
-             ```bash
-             pnpm test --reporter=tap test/components/Button.test.tsx
-             ```
+Uses Vitest: `import { describe, it, expect } from 'vitest'` with `describe()`/`it()`/`expect()`.
 
-         3.2. Updating snapshots:
-             ```bash
-             pnpm snap --reporter=tap
-             ```
-             ⚠️ IMPORTANT: Snapshots are asserting expected results, they should only be updated if all breaking changes to tests are intentional.
-             Before updating snapshots:
-             - Review all snapshot changes carefully
-             - Ensure the changes are expected and intentional
-             - Document any breaking changes in your work
-             - Consider discussing major snapshot updates with the team
-
-      4. ⚠️ **Code Coverage**: 
-         **Code coverage is NOT measured or validated in the `src/gui` workspace.**
-         Skip any coverage-related validation steps when working in this workspace.
-
-      5. Run type checking:
-         ```bash
-         pnpm posttest
-         ```
-         This runs the TypeScript type checker for the GUI workspace.
-         Make sure you're in the `src/gui` folder when running this command.
-         
-         If type checking errors are found:
-         - Review each type error message carefully
-         - Fix type issues in the affected files
-         - Run `pnpm posttest` again to verify fixes
-         - Ensure all type definitions are correct and complete
-
-      **Important Notes for GUI Workspace:**
-      - Always run these commands from within the `src/gui` directory
-      - **Testing Framework**: GUI workspace uses **Vitest** (not tap) - use `describe()`, `it()`, `expect()` syntax
-      - The GUI workspace uses different test reporter flags than other workspaces
-      - Code coverage validation is intentionally skipped for this workspace
-      - Do not proceed to the next step if the current step fails
-      - Complete your work only after all applicable validation steps pass
-
-examples:
-  - input: |
-      # Bad: Using wrong test commands, frameworks, or attempting coverage validation
-      pnpm test -Rtap --disable-coverage  # Wrong command for GUI
-      pnpm test -Rsilent --coverage-report=text-lcov  # Coverage not used in GUI
-      # Bad: Using tap syntax in test files
-      import { test } from 'tap'  # GUI uses Vitest, not tap
-
-      # Good: GUI workspace validation workflow
-      cd src/gui
-      pnpm format
-      pnpm lint
-      pnpm test --reporter=tap
-      # Skip coverage step - not applicable to GUI workspace
-      pnpm posttest
-
-      # Good: Test file syntax for GUI workspace (uses Vitest)
-      import { describe, it, expect } from 'vitest'
-      describe('Component', () => {
-        it('should work correctly', () => {
-          expect(result).toBe(expected)
-        })
-      })
-
-      # Good: Iterative development workflow for GUI
-      cd src/gui
-      pnpm test --reporter=tap test/components/Button.test.tsx
-      # Make changes to the code
-      pnpm format
-      pnpm lint
-      pnpm test --reporter=tap test/components/Button.test.tsx
-      # Review snapshot changes carefully
-      pnpm snap --reporter=tap
-      # Type check
-      pnpm posttest
-    output: "Properly validated GUI workspace changes with correct Vitest syntax"
-
-metadata:
-  priority: high
-  version: 1.0
-  tags:
-    - gui
-    - validation
-    - workflow
-    - testing
-    - vitest
-    - frontend
-    - react
-    - formatting
-    - linting
-  related_rules:
-    - code-validation-workflow  # General validation workflow for other workspaces
-    - linting-error-handler     # For systematic handling of common linting errors
-    - monorepo-structure       # For understanding workspace organization
-</rule>
+**Do NOT use tap syntax** (`import { test } from 'tap'`) in this workspace.
diff --git a/.cursor/rules/index.mdc b/.cursor/rules/index.mdc
@@ -0,0 +1,35 @@
+---
+description: Monorepo structure, workspace map, and development workflow
+globs: **/*
+alwaysApply: true
+---
+# vltpkg Monorepo
+
+pnpm monorepo. Workspaces in `src/*`, `infra/*`, `www/*`. Workspaces published as `@vltpkg/*`, the built vlt CLI itself is published as `vlt`.
+
+## Development
+
+- `cd` into workspace dir before running commands (e.g., `cd src/semver`)
+- Each workspace has own `package.json`, `test/` folder
+- 100% test coverage required. Use pnpm. Strict TypeScript.
+- See `@code-validation-workflow.mdc` for format/lint/test/coverage/typecheck steps
+
+## Workspaces
+
+**Graph (core install engine):** `src/graph` — See `@graph/index.mdc` and sub-rules: `data-structure`, `ideal`, `ideal-append-nodes`, `load-actual`, `modifiers`, `lockfiles`, `reify`, `peers`
+
+**Core:** `src/cache`, `src/cache-unzip`, `src/types`, `src/dep-id` (node IDs), `src/spec` (specifier parsing), `src/satisfies` (DepID↔Spec)
+
+**DSS Query:** `src/dss-parser`, `src/dss-breadcrumb`, `src/query` — See `@query-pseudo-selector-creation.mdc`
+
+**Package Mgmt:** `src/package-info`, `src/package-json`, `src/registry-client`, `src/tar`, `src/workspaces`
+
+**CLI:** `src/cli-sdk` (framework — see `@cli-sdk-workspace.mdc`), `src/init`, `src/vlx`, `src/run`
+
+**Utilities:** `src/keychain`, `src/security-archive`, `src/semver`, `src/git`, `src/error-cause`, `src/output`, `src/xdg`, `src/url-open`, `src/promise-spawn`, `src/cmd-shim`, `src/rollback-remove`, `src/dot-prop`, `src/fast-split`, `src/pick-manifest`, `src/vlt-json`, `src/which`
+
+**Frontend:** `src/gui` (React/Zustand — see `@gui-validation-workflow.mdc`), `src/server`
+
+**Infra:** `infra/benchmark`, `infra/cli`, `infra/cli-compiled`, `infra/cli-{platform}`, `infra/smoke-test`
+
+**Docs:** `www/docs` → https://docs.vlt.sh
diff --git a/.cursor/rules/linting-error-handler.mdc b/.cursor/rules/linting-error-handler.mdc
@@ -1,308 +1,36 @@
 ---
-description: 
-globs: 
+description: Fixing common linting errors (unused vars, imports, type guards)
+globs: src/*/src/**/*.ts,src/*/test/**/*.ts
 alwaysApply: false
 ---
-# Linting Error Handler
+# Linting Error Fixes
 
-Rule for efficiently identifying and fixing common linting errors, particularly unused variables and imports.
+## Unused Variables (`@typescript-eslint/no-unused-vars`)
 
-<rule>
-name: linting_error_handler
-description: Systematic approach to fixing common linting errors with clear patterns and solutions
-filters:
-  # Match TypeScript and JavaScript files
-  - type: file_extension
-    pattern: "\\.(js|jsx|ts|tsx)$"
-  # Match linting-related events
-  - type: event
-    pattern: "lint_error"
+Preference order:
+1. **Remove** the declaration (call expression without assignment if side-effects needed)
+2. **Use** the variable if it should be used
+3. **Prefix with `_`** (last resort)
 
-actions:
-  - type: suggest
-    message: |
-      When encountering linting errors, follow these systematic steps:
+## Unused Imports
 
-      ## 1. Identify Error Patterns
+1. Remove unused imports from the import statement
+2. Remove entire import line if all imports unused
+3. Separate `import type {}` from value imports when needed
 
-      ### Common Error Types and Solutions:
+## Type Guards for Array Filtering
 
-      #### A. Unused Variables (`@typescript-eslint/no-unused-vars`)
-      **Pattern**: `'variableName' is assigned a value but never used. Allowed unused vars must match /^_/u`
-      
-      **Solutions** (in order of preference):
-      1. **Remove the variable declaration**:
-         ```typescript
-         // ❌ Before
-         const foo = doesSomethingAndReturnsFoo()
-         
-         // ✅ After
-         doesSomethingAndReturnsFoo()
-         ```
+Use type predicates instead of non-null assertions (`!`):
+```typescript
+// BAD: n.location! causes @typescript-eslint/no-non-null-assertion
+const paths = nodes.filter(n => n.location !== undefined).map(n => n.location!)
 
-      2. **Remove the variable entirely** (if truly unused):
-         ```typescript
-         // ❌ Before
-         const isWorkspaceOrProject = isPseudoNode(item) && (item.value === ':workspace' || item.value === ':project')
-         const allowedPseudoNodes = isPseudoNode(item) && (item.value === ':root' || item.value === ':workspace')
-         
-         // ✅ After
-         const allowedPseudoNodes = isPseudoNode(item) && (item.value === ':root' || item.value === ':workspace')
-         ```
+// GOOD: type predicate narrows correctly
+const paths = nodes
+  .filter((n): n is { location: string } => typeof n.location === 'string')
+  .map(n => n.location)
+```
 
-      3. **Use the variable** (if it should be used):
-         ```typescript
-         // ❌ Before
-         const result = calculateValue()
-         return defaultValue
-         
-         // ✅ After
-         const result = calculateValue()
-         return result
-         ```
+## Workflow
 
-      4. **Prefix with underscore** (keep declaration for reference, last resort only):
-         ```typescript
-         // ❌ Before
-         const isWorkspaceOrProject = isPseudoNode(item) && (item.value === ':workspace' || item.value === ':project')
-         
-         // ✅ After
-         const _isWorkspaceOrProject = isPseudoNode(item) && (item.value === ':workspace' || item.value === ':project')
-         ```
-
-      #### B. Unused Imports (`@typescript-eslint/no-unused-vars`)
-      **Pattern**: `'ImportName' is defined but never used. Allowed unused vars must match /^_/u`
-      
-      **Solutions**:
-      1. **Remove from import statement**:
-         ```typescript
-         // ❌ Before
-         import { usedFunction, UnusedType, anotherUsedFunction } from 'module'
-         
-         // ✅ After
-         import { usedFunction, anotherUsedFunction } from 'module'
-         ```
-
-      2. **Remove entire import line** (if all imports unused):
-         ```typescript
-         // ❌ Before
-         import type { PostcssNode } from '@vltpkg/dss-parser'
-         import { error } from '@vltpkg/error-cause'
-         
-         // ✅ After
-         import { error } from '@vltpkg/error-cause'
-         ```
-
-      3. **Separate type and value imports**:
-         ```typescript
-         // ❌ Before
-         import { function1, Type1, function2 } from 'module'
-         
-         // ✅ After  
-         import { function1, function2 } from 'module'
-         import type { Type1 } from 'module'
-         ```
-
-      #### C. Type Guard Functions for Array Filtering (`@typescript-eslint/prefer-nullish-coalescing`, non-null assertions)
-      **Pattern**: Filtering arrays with optional properties and needing proper type narrowing without non-null assertions
-      
-      **Problem**: When filtering arrays to remove undefined/null values, TypeScript doesn't automatically narrow the type, leading to:
-      - Using non-null assertions (`!`) which will cause a @typescript-eslint/no-non-null-assertion error
-      - Type errors when chaining array methods
-      
-      **Solution**: Use type guard functions (type predicates) for proper type narrowing:
-      
-      1. **Create reusable type guard functions**:
-         ```typescript
-         // ✅ Generic type guard for filtering undefined values
-         const isNotUndefined = <T>(value: T | undefined): value is T => value !== undefined
-         
-         // ✅ Generic type guard for filtering both null and undefined
-         const isDefined = <T>(value?: T): value is T => 
-           value !== null && value !== undefined
-         ```
-
-      2. **Apply in array filtering chains**:
-         ```typescript
-         // ❌ Before (using non-null assertions - unsafe and causes linting errors)
-         const scopePaths = nodes
-           .filter(n => n.location !== undefined)
-           .map(n => n.location!) // Non-null assertion warning!
-         
-         // ✅ After (using type guard - safe and type-correct)
-         const scopePaths = nodes
-           .filter((n): n is NodeWithLocation => n.location !== undefined)
-           .map(n => n.location) // TypeScript knows n.location is string, not string | undefined
-         ```
-
-      3. **Advanced patterns with custom type guards**:
-         ```typescript
-         // ✅ Custom type guard for specific conditions
-         type NodeWithLocation = {
-           location: string
-         } & Node
-         
-         const hasLocation = (node: Node): node is NodeWithLocation => 
-           node.location !== undefined
-         
-         // Usage
-         const locatedNodes = allNodes
-           .filter(hasLocation)
-           .map(node => node.location) // TypeScript knows location is defined
-         ```
-
-      4. **Inline type predicates for simple cases**:
-         ```typescript
-         // ✅ Inline type predicate
-         const validIds = items
-           .filter((item): item is ItemWithId => item.id !== undefined)
-           .map(item => item.id)
-         
-         // ✅ For property existence checks
-         const activeItems = items
-           .filter((item): item is ActiveItem => item.active === true)
-           .forEach(item => item.doSomething())
-         ```
-
-      **Why Type Guards Are Better Than Non-Null Assertions:**
-      - **Type Safety**: Compiler verifies the type narrowing logic
-      - **Linting Compliance**: No warnings about non-null assertions
-      - **Readability**: Explicit about what condition is being checked
-      - **Reusability**: Type guard functions can be reused across the codebase
-      - **Runtime Safety**: Actually checks the condition, doesn't just silence TypeScript
-
-      **Common Patterns:**
-      ```typescript
-      // ✅ Filter and map with location property
-      const paths = nodes
-        .filter((n): n is { location: string } => typeof n.location === 'string')
-        .map(n => n.location)
-      
-      // ✅ Filter and process with multiple properties
-      const workspaceNodes = nodes
-        .filter((n): n is WorkspaceNode => n.importer && n.location !== undefined)
-        .forEach(n => processWorkspace(n.location, n.importer))
-      ```
-
-      ## 2. Quick Fix Workflow
-
-      ### Step-by-Step Process:
-      1. **Run linter to get error details**:
-         ```bash
-         pnpm lint
-         ```
-
-      2. **Identify the exact line numbers and error types**:
-         - Note the file path
-         - Note the line numbers
-         - Note the specific variable/import names
-         - Note the error type (`no-unused-vars`, etc.)
-
-      3. **Apply fixes systematically**:
-         - Start with unused imports (usually easier)
-         - Then handle unused variables
-         - Use search-replace for precision
-
-      4. **Verify fixes**:
-         ```bash
-         pnpm lint
-         ```
-
-      ## 3. Search-Replace Patterns
-
-      ### For Unused Imports:
-      ```bash
-      # Pattern: Remove single import from list
-      OLD: import { keepThis, REMOVE_THIS, keepThat } from 'module'
-      NEW: import { keepThis, keepThat } from 'module'
-
-      # Pattern: Remove entire import line
-      OLD: import type { UnusedType } from '@vltpkg/module'
-      NEW: (delete entire line)
-      ```
-
-      ### For Unused Variables:
-      ```bash
-      # Pattern: Remove variable declaration
-      OLD: const unusedVar = someExpression()
-          const usedVar = anotherExpression()
-      NEW: someExpression()
-          const usedVar = anotherExpression()
-
-      # Pattern: Prefix with underscore
-      OLD: const myVar = getValue()
-      NEW: const _myVar = getValue()
-      ```
-
-      ## 4. Advanced Patterns
-
-      ### Multiple Unused Items:
-      ```typescript
-      // ❌ Before
-      import { 
-        usedFunc, 
-        UnusedType1, 
-        UnusedType2, 
-        anotherUsedFunc,
-        UnusedFunc 
-      } from 'module'
-
-      // ✅ After
-      import { usedFunc, anotherUsedFunc } from 'module'
-      ```
-
-      ### Conditional Usage:
-      ```typescript
-      // If variable is used conditionally, consider refactoring
-      // ❌ Before
-      const expensiveCalculation = heavyOperation()
-      if (someCondition) {
-        // expensiveCalculation never used here
-      }
-
-      // ✅ After
-      if (someCondition) {
-        const expensiveCalculation = heavyOperation()
-        // use expensiveCalculation
-      }
-      ```
-
-      ## 5. Prevention Tips
-
-      ### During Development:
-      - Remove imports immediately when removing usage
-      - Use IDE features to detect unused items early  
-      - Run `pnpm lint` frequently during development
-      - Avoid using `_` prefix for unused variables, use it as a last resort only
-
-      ### Code Review:
-      - Check for unused imports in new code
-      - Verify that all declared variables are used
-      - Remove dead code promptly
-
-examples:
-  - input: |
-      # Error: 'PostcssNode' is defined but never used
-      import type { PostcssNode } from '@vltpkg/dss-parser'
-      import type { ModifierBreadcrumb } from './types.ts'
-
-      # Error: 'isWorkspaceOrProject' is never used  
-      const isWorkspaceOrProject = isPseudoNode(item) && (item.value === ':workspace')
-      const allowedPseudoNodes = isPseudoNode(item) && (item.value === ':root')
-    output: |
-      # Fixed: Remove unused import
-      import type { ModifierBreadcrumb } from './types.ts'
-
-      # Fixed: Remove unused variable
-      const allowedPseudoNodes = isPseudoNode(item) && (item.value === ':root')
-
-metadata:
-  priority: high
-  version: 1.0
-  tags:
-    - linting
-    - error-handling
-    - unused-variables
-    - unused-imports
-    - code-quality
-</rule>
+`pnpm lint` → fix issues → `pnpm lint` again to verify.
diff --git a/.cursor/rules/monorepo-structure.mdc b/.cursor/rules/monorepo-structure.mdc
@@ -1,174 +0,0 @@
----
-description: 
-globs: 
-alwaysApply: true
----
-# vltpkg/vltpkg Monorepo Structure
-
-Understanding and navigating the vltpkg monorepo workspace structure.
-
-<rule>
-name: monorepo_structure
-description: Guide for understanding and working within the vltpkg monorepo structure
-filters:
-  # Match any work within workspace directories
-  - type: path
-    pattern: "^(src|infra|www)/"
-  # Match package.json files in workspaces
-  - type: file_name
-    pattern: "package\\.json$"
-  # Match workspace-related operations
-  - type: event
-    pattern: "workspace_.*"
-
-actions:
-  - type: guide
-    message: |
-      ## vltpkg Monorepo Overview
-
-      The https://github.com/vltpkg/vltpkg repository is a monorepo with workspaces organized in three main directories:
-      - `src/*` - Reusable packages published to npm registry
-      - `infra/*` - Internal infrastructure and build tools
-      - `www/*` - Documentation website
-
-      **Package Manager**: This repository uses `pnpm` for dependency management and workspace operations.
-
-      **Monorepo Resources**: Learn more at https://monorepo.tools/
-
-  - type: workspace_guide
-    message: |
-      ## Workspace Categories
-
-      ### Reusable Packages (`src/*`)
-      These are published to npm as `@vltpkg/*` packages:
-
-      **Core Infrastructure:**
-      - `src/cache` (`@vltpkg/cache`) - Cache system
-      - `src/cache-unzip` (`@vltpkg/cache-unzip`) - Cache entry optimization
-      - `src/graph` (`@vltpkg/graph`) - Main data structure managing package installs
-        - 📋 **See `@graph/index.mdc`** for understanding installs and the graph library
-        - 📋 **See `@graph/data-structure.mdc`** for understanding the graph data structure
-        - 📋 **See `@graph/ideal.mdc`** for building Ideal graphs
-        - 📋 **See `@graph/load-actual.mdc`** for understanding loading Graph data from node_modules folders
-        - 📋 **See `@graph/modifiers.mdc`** for understanding Graph modifiers
-        - 📋 **See `@graph/lockfiles.mdc`** for working with lockfiles
-        - 📋 **See `@graph/reify.mdc`** for understanding how to save packages to node_modules folders
-        - 📋 **See `@graph/peers.mdc`** for understanding peer dependency context isolation and resolution
-      - `src/types` (`@vltpkg/types`) - Common TypeScript types
-      - `src/dep-id` (`@vltpkg/dep-id`) - Unique Graph node identifiers
-      - `src/spec` (`@vltpkg/spec`) - Package specifier parsing
-      - `src/satisfies` (`@vltpkg/satisfies`) - DepID to Spec comparison
-
-      **Dependency Selector Syntax Query Language:**
-      - `src/dss-parser` (`@vltpkg/dss-parser`) - Dependency Selector Syntax parser
-      - `src/dss-breadcrumb` (`@vltpkg/dss-breadcrumb`) - Interactive DSS query matching
-      - `src/query` (`@vltpkg/query`) - Query language implementation
-        - 📋 **See `@query-pseudo-selector-creation.mdc`** for implementing new pseudo-selectors
-
-      **Package Management Infrastructure:**
-      - `src/package-info` (`@vltpkg/package-info`) - Package information retrieval
-      - `src/package-json` (`@vltpkg/package-json`) - package.json file handling
-      - `src/registry-client` (`@vltpkg/registry-client`) - Registry API client
-      - `src/tar` (`@vltpkg/tar`) - Tarball unpacking
-      - `src/workspaces` (`@vltpkg/workspaces`) - Workspace management
-
-      **CLI Commands:**
-      - `src/cli-sdk` (`@vltpkg/cli-sdk`) - Core CLI framework and entry point
-        - 📋 **See `@cli-sdk-workspace.mdc`** for CLI architecture and development patterns
-      - `src/init` (`@vltpkg/init`) - `vlt init` command logic
-      - `src/vlx` (`@vltpkg/vlx`) - `vlt exec` command logic
-      - `src/run` (`@vltpkg/run`) - Command execution utilities
-
-      **Utilities:**
-      - `src/keychain` (`@vltpkg/keychain`) - Secure token storage
-      - `src/security-archive` (`@vltpkg/security-archive`) - Socket.dev security data cache
-      - `src/semver` (`@vltpkg/semver`) - Semantic version parsing/comparison
-      - `src/git` (`@vltpkg/git`) - Git utility spawning
-      - `src/error-cause` (`@vltpkg/error-cause`) - Standardized error messages
-      - `src/output` (`@vltpkg/output`) - CLI output formatting
-
-      **System Integration:**
-      - `src/xdg` (`@vltpkg/xdg`) - OS-specific config/data locations
-      - `src/url-open` (`@vltpkg/url-open`) - Default browser URL opening
-      - `src/promise-spawn` (`@vltpkg/promise-spawn`) - Process spawning utilities
-      - `src/cmd-shim` (`@vltpkg/cmd-shim`) - Command shimming
-      - `src/rollback-remove` (`@vltpkg/rollback-remove`) - Safe removal operations
-
-      **Optimized Utilities:**
-      - `src/dot-prop` (`@vltpkg/dot-prop`) - Forked dot-prop implementation
-      - `src/fast-split` (`@vltpkg/fast-split`) - Optimized String.split() replacement
-      - `src/pick-manifest` (`@vltpkg/pick-manifest`) - Manifest selection logic
-      - `src/vlt-json` (`@vltpkg/vlt-json`) - Utility to manage the vlt.json file
-      - `src/which` (`@vltpkg/which`) - Command location utilities
-
-      **Frontend:**
-      - `src/gui` - React/Zustand frontend for Graph visualization (dist files in nested `dist/` folder)
-        - 📋 **See `@gui-validation-workflow.mdc`** for GUI-specific testing and validation
-      - `src/server` (`@vltpkg/server`) - Backend server for GUI APIs
-
-      ### Infrastructure (`infra/*`)
-      Internal tools and build systems:
-      - `infra/benchmark` - Performance benchmarking scripts
-      - `infra/cli` - The main vlt CLI distribution
-      - `infra/cli-compiled` - Compiled CLI build
-      - `infra/cli-*` - Platform-specific CLI builds (darwin-arm64, darwin-x64, linux-arm64, linux-x64, win32-x64)
-      - `infra/smoke-test` - CLI integration tests
-
-      ### Documentation (`www/*`)
-      - `www/docs` - Source for https://docs.vlt.sh documentation website
-
-  - type: development_workflow
-    message: |
-      ## Development Workflow
-
-      **Working with Workspaces:**
-      1. Navigate to the specific workspace directory (e.g., `cd src/semver`)
-      2. Each workspace has its own `package.json` and dependencies
-      3. Unit tests are located in each workspace's `test/` folder
-
-      **Code Validation:**
-      For all code formatting, linting, testing, coverage, and type checking operations, follow the standardized workflow defined in `@code-validation-workflow.mdc`.
-
-      **Key Development Points:**
-      - **100% Test Coverage Required**: All workspaces must maintain complete test coverage
-      - **Unit Tests**: Every component has tests in nested `test/` folders - consult these for API usage examples
-      - **Type Safety**: All workspaces use TypeScript with strict type checking
-      - **Consistent Tooling**: Use pnpm for all package management operations
-
-examples:
-  - input: |
-      # Working on the semver workspace
-      cd src/semver
-      # Follow @code-validation-workflow.mdc for validation steps
-      
-      # Working on the graph workspace  
-      cd src/graph
-      # Follow @code-validation-workflow.mdc for validation steps
-    output: "Properly navigated to workspace and followed validation workflow"
-
-  - input: |
-      # Bad: Running commands from wrong directory
-      pnpm test  # from repo root
-      
-      # Good: Navigate to workspace first
-      cd src/semver
-      # Follow @code-validation-workflow.mdc
-    output: "Correctly positioned in workspace for development"
-
-metadata:
-  priority: high
-  version: 2.0
-  tags:
-    - monorepo
-    - workspaces
-    - structure
-    - navigation
-    - packages
-  related_rules:
-    - code-validation-workflow     # For all testing, formatting, linting, coverage operations
-    - cursor-rules-location        # For proper rule file placement
-    - cli-sdk-workspace           # CLI SDK workspace architecture and patterns
-    - gui-validation-workflow     # GUI workspace specific validation workflow
-    - query-pseudo-selector-creation  # Guide for implementing new query pseudo-selectors
-    - graph_workspace_architecture  # Understanding installs and the graph library
-</rule>
diff --git a/.cursor/rules/query-pseudo-selector-creation.mdc b/.cursor/rules/query-pseudo-selector-creation.mdc
@@ -1,320 +1,48 @@
 ---
-description: 
-globs: 
+description: Guide for implementing new query pseudo-selectors
+globs: src/query/src/pseudo/*,src/query/test/pseudo/*,src/query/src/pseudo.ts
 alwaysApply: false
 ---
-# Query Pseudo-Selector Creation Guide
+# Creating Query Pseudo-Selectors
 
-Guide for implementing new pseudo-selectors in the vltpkg Dependency Selector Syntax query language.
+Guide for adding pseudo-selectors to `src/query/`.
 
-<rule>
-name: query_pseudo_selector_creation
-description: Comprehensive guide for creating new pseudo-selectors in the query language
-filters:
-  # Match work within the query workspace
-  - type: path
-    pattern: "^src/query/"
-  # Match pseudo-selector related files
-  - type: file_name
-    pattern: "pseudo.*\\.(ts|js)$"
-  # Match selector implementation requests
-  - type: content
-    pattern: "(?i)(pseudo.?selector|query.?selector|dependency.?selector)"
+## Steps
 
-actions:
-  - type: guide
-    message: |
-      ## Creating New Pseudo-Selectors
+1. **Study patterns**: `src/query/src/pseudo/` — see `missing.ts` (edge), `private.ts` (node), `overridden.ts` (edge property)
+2. **Create**: `src/query/src/pseudo/your-selector.ts`
+3. **Register**: import in `src/query/src/pseudo.ts`, add to `pseudoSelectors` Map
+4. **Test**: `src/query/test/pseudo/your-selector.ts`
+5. **Validate**: follow `@code-validation-workflow.mdc`
 
-      This guide provides a step-by-step process for implementing new pseudo-selectors in the vltpkg query language, based on patterns established by existing selectors like `:overridden`, `:missing`, `:dev`, etc.
+## Implementation Template
 
-      ### Understanding Pseudo-Selectors
+```typescript
+import type { ParserState } from '../types.ts'
+import { removeEdge, removeUnlinkedNodes } from './helpers.ts'
 
-      Pseudo-selectors filter the dependency graph based on specific criteria:
-      - **Edge-based selectors** (like `:overridden`, `:dev`) filter based on edge properties
-      - **Node-based selectors** (like `:empty`, `:private`) filter based on node properties  
-      - **Relationship selectors** (like `:missing`) filter based on edge-node relationships
+export const yourSelector = async (state: ParserState) => {
+  // Edge-based: iterate state.partial.edges, call removeEdge()
+  // Node-based: iterate state.partial.nodes, call removeNode()
+  for (const edge of state.partial.edges) {
+    if (/* condition */) removeEdge(state, edge)
+  }
+  removeUnlinkedNodes(state) // after edge filtering
+  return state
+}
+```
 
-      ### Implementation Steps
+## Helpers (`helpers.ts`)
 
-      #### 1. Study Existing Patterns
-      
-      **Required Reading:**
-      - `src/query/src/pseudo/` - Review similar selectors for patterns
-      - `src/query/src/pseudo/helpers.ts` - Available helper functions
-      - `src/query/src/types.ts` - Understanding `ParserState` and related types
-      - `@vltpkg/graph` types - Understanding `EdgeLike`, `NodeLike` structures
+- `removeNode(state, node)` — removes node + incoming edges
+- `removeEdge(state, edge)` — removes edge + outgoing node
+- `removeDanglingEdges(state)` — edges with no destination
+- `removeUnlinkedNodes(state)` — nodes with no incoming edges
 
-      **Key Reference Selectors:**
-      - `:missing` (`src/query/src/pseudo/missing.ts`) - Simple edge filtering
-      - `:dev` (`src/query/src/pseudo/dev.ts`) - Edge type filtering with node cleanup
-      - `:overridden` (`src/query/src/pseudo/overridden.ts`) - Edge property filtering
-      - `:private` (`src/query/src/pseudo/private.ts`) - Node property filtering
+## Test Pattern
 
-      #### 2. Create the Selector Implementation
+Use `getSimpleGraph()` from `test/fixtures/graph.ts`. Build `ParserState` with `postcssSelectorParser().astSync(query)`. Assert on `res.partial.nodes`/`res.partial.edges` using snapshots.
 
-      **File Location:** `src/query/src/pseudo/YOUR_SELECTOR_NAME.ts`
+## Docs
 
-      - ⚠️ IMPORTANT: The decision to use a edge-based filtering or a node-based
-      filtering is going to depend on what values need to be used to perform
-      the checks.
-
-      **Template Structure:**
-      ```typescript
-      import type { ParserState } from '../types.ts'
-      import { removeEdge, removeUnlinkedNodes } from './helpers.ts'
-      // Add other imports as needed
-
-      /**
-       * :your-selector Pseudo-Selector, matches [DESCRIPTION OF WHAT IT MATCHES].
-       * [DETAILED DESCRIPTION OF BEHAVIOR]
-       */
-      export const yourSelector = async (state: ParserState) => {
-        // Filter logic here - iterate over state.partial.edges or state.partial.nodes
-        for (const edge of state.partial.edges) {
-          if (/* YOUR FILTERING CONDITION */) {
-            removeEdge(state, edge)
-          }
-        }
-
-        // OR for node-based filtering:
-        // for (const node of state.partial.nodes) {
-        //   if (/* YOUR FILTERING CONDITION */) {
-        //     removeNode(state, node)
-        //   }
-        // }
-
-        // Clean up unlinked nodes if you're filtering edges
-        removeUnlinkedNodes(state)
-
-        return state
-      }
-      ```
-
-      **Available Helper Functions (`helpers.ts`):**
-      - `removeNode(state, node)` - Removes a node and its incoming edges
-      - `removeEdge(state, edge)` - Removes an edge and its outgoing node
-      - `removeDanglingEdges(state)` - Removes edges with no destination node
-      - `removeUnlinkedNodes(state)` - Removes nodes with no incoming edges
-      - `removeQuotes(value)` - Utility for processing string values
-
-      #### 3. Integrate into Pseudo-Selector Registry
-
-      **File:** `src/query/src/pseudo.ts`
-
-      **Steps:**
-      1. **Add import:** 
-         ```typescript
-         import { yourSelector } from './pseudo/your-selector.ts'
-         ```
-
-      2. **Add to pseudoSelectors Map:**
-         ```typescript
-         const pseudoSelectors = new Map<string, ParserFn>(
-           Object.entries({
-             // ... existing selectors ...
-             yourSelector,
-             // ... rest of selectors ...
-           }),
-         )
-         ```
-
-      3. **Remove any TODO comments** related to your selector
-
-      #### 4. Create Comprehensive Tests
-
-      **File Location:** `src/query/test/pseudo/YOUR_SELECTOR_NAME.ts`
-
-      **Critical Test Guidelines:**
-      - ⚠️ **NEVER violate type contracts** - Study actual type definitions first
-      - ✅ **Use existing test fixtures** when possible (`../fixtures/graph.ts`)
-      - ✅ **Create type-safe test data** that respects the actual object structures
-      - ✅ **Test realistic scenarios** that can actually occur in the codebase
-
-      **Test Template:**
-      ```typescript
-      import t from 'tap'
-      import postcssSelectorParser from 'postcss-selector-parser'
-      import type { ParserState } from '../../src/types.ts'
-      import { yourSelector } from '../../src/pseudo/your-selector.ts'
-      import {
-        getSimpleGraph,
-        // Import other test fixtures as needed
-      } from '../fixtures/graph.ts'
-
-      t.test('your selector description', async t => {
-        const getState = (query: string, graph = getSimpleGraph()) => {
-          const ast = postcssSelectorParser().astSync(query)
-          const current = ast.first.first
-          const state: ParserState = {
-            comment: '',
-            current,
-            initial: {
-              edges: new Set(graph.edges.values()),
-              nodes: new Set(graph.nodes.values()),
-            },
-            partial: {
-              edges: new Set(graph.edges.values()),
-              nodes: new Set(graph.nodes.values()),
-            },
-            collect: {
-              edges: new Set(),
-              nodes: new Set(),
-            },
-            cancellable: async () => {},
-            walk: async i => i,
-            retries: 0,
-            securityArchive: undefined,
-            specOptions: {},
-            signal: new AbortController().signal,
-            scopeIDs: [],
-            specificity: { idCounter: 0, commonCounter: 0 },
-          }
-          return state
-        }
-
-        await t.test('main functionality test', async t => {
-          const res = await yourSelector(getState(':your-selector'))
-          // Add your assertions here
-          t.matchSnapshot({
-            nodes: [...res.partial.nodes].map(n => n.name).sort(),
-            edges: [...res.partial.edges].map(e => e.name).sort(),
-          })
-        })
-
-        // Add more test cases:
-        // - Empty state handling
-        // - Edge cases specific to your selector
-        // - Different graph scenarios
-      })
-      ```
-
-      **Essential Test Scenarios:**
-      - ✅ Main functionality with expected results
-      - ✅ Empty partial state handling
-      - ✅ Edge cases specific to your selector's logic
-      - ✅ Different graph configurations
-      - ✅ Proper node cleanup verification
-
-      #### 5. Follow Code Validation Workflow
-
-      **Required Steps** (from `@code-validation-workflow.mdc`):
-      ```bash
-      # 1. Format code
-      pnpm format
-
-      # 2. Lint code  
-      pnpm lint
-
-      # 3. Run tests (create snapshots first)
-      TAP_SNAPSHOT=1 pnpm test -Rtap --disable-coverage test/pseudo/your-selector.ts
-      pnpm test -Rtap --disable-coverage test/pseudo/your-selector.ts
-
-      # 4. Check coverage
-      pnpm test -Rsilent --coverage-report=text-lcov test/pseudo/your-selector.ts
-
-      # 5. Type check
-      pnpm posttest
-      ```
-
-      ### Common Patterns & Best Practices
-
-      #### Edge-Based Filtering Pattern
-      ```typescript
-      // Filter edges based on edge properties
-      for (const edge of state.partial.edges) {
-        if (!edge.someProperty) {
-          removeEdge(state, edge)
-        }
-      }
-      removeUnlinkedNodes(state) // Clean up orphaned nodes
-      ```
-
-      #### Node-Based Filtering Pattern  
-      ```typescript
-      // Filter nodes based on node properties
-      for (const node of state.partial.nodes) {
-        if (!node.someProperty) {
-          removeNode(state, node)
-        }
-      }
-      removeDanglingEdges(state) // Clean up orphaned edges
-      ```
-
-      #### Type Safety in Tests
-      ```typescript
-      // ❌ NEVER do this - violates type contracts
-      const edge = {
-        spec: undefined as any, // Breaks Edge type contract
-      }
-
-      // ✅ ALWAYS do this - respects type contracts  
-      const spec = Spec.parse('package-name', '^1.0.0', specOptions)
-      const edge = {
-        spec, // Proper Spec object
-        // ... other required properties
-      }
-      ```
-
-      ### Documentation Requirements
-
-      After implementation, consider updating:
-      - `www/docs/src/content/docs/cli/selectors.mdx` - Add documentation for end users
-      - Add examples and use cases for the new selector
-
-examples:
-  - input: |
-      # Creating the :overridden selector (real example)
-      
-      # 1. Implementation
-      src/query/src/pseudo/overridden.ts:
-      ```typescript
-      export const overridden = async (state: ParserState) => {
-        for (const edge of state.partial.edges) {
-          if (!edge.spec.overridden) {
-            removeEdge(state, edge)
-          }
-        }
-        removeUnlinkedNodes(state)
-        return state
-      }
-      ```
-      
-      # 2. Integration
-      src/query/src/pseudo.ts:
-      ```typescript
-      import { overridden } from './pseudo/overridden.ts'
-      // ...
-      const pseudoSelectors = new Map<string, ParserFn>(
-        Object.entries({
-          // ...
-          overridden,
-          // ...
-        }),
-      )
-      ```
-      
-      # 3. Tests (type-safe)
-      src/query/test/pseudo/overridden.ts:
-      ```typescript
-      // ✅ Proper type-safe edge creation
-      const spec = Spec.parse('package', '^1.0.0', specOptions)
-      spec.overridden = true
-      const edge = { spec, /* ... other props */ }
-      ```
-    output: "Successfully implemented new pseudo-selector following established patterns"
-
-metadata:
-  priority: high
-  version: 1.0
-  tags:
-    - query-language
-    - pseudo-selectors
-    - implementation-guide
-    - type-safety
-    - testing-patterns
-    - graph-filtering
-  related_rules:
-    - code-validation-workflow  # For validation steps
-    - monorepo-structure        # For understanding workspace structure
-</rule>
+Update `www/docs/src/content/docs/cli/selectors.mdx` after implementation.
diff --git a/.cursor/rules/registry-development.mdc b/.cursor/rules/registry-development.mdc
@@ -1,149 +1,47 @@
 ---
-description: 
-globs: 
+description: Registry (vsr) development patterns and architecture
+globs: src/vsr/src/**/*,src/vsr/test/**/*
 alwaysApply: false
 ---
-# vltpkg Registry Development Rules
+# Registry Development (src/vsr/)
 
-## Registry Overview
-The vltpkg registry (`src/vsr/`) is a high-performance npm-compatible package registry built on Cloudflare Workers with:
-- **Multi-upstream support**: Routes packages to different registries (npm, jsr, local, custom)
-- **Intelligent caching**: Stale-while-revalidate strategy with racing cache for performance
-- **Proxy capabilities**: Can proxy packages from upstream registries while maintaining local packages
-- **Security integration**: Socket.dev security data integration
-- **Modern stack**: Hono framework, D1 database, R2 storage, TypeScript
+npm-compatible registry on Cloudflare Workers (Hono, D1, R2). Multi-upstream, stale-while-revalidate caching. Security audit endpoints are placeholders today (Socket.dev planned for v1.x).
 
-## Core Architecture Patterns
+## Architecture
 
-### Never Stub
+- **Routing order matters**: upstream routes (`/:upstream/...`) validate + `c.set('upstream', upstream)` before local package routes (`/:pkg...`). Final `/*` is static assets fallback.
+- **Upstream config**: `env.ORIGIN_CONFIG` (worker env) resolved via `getUpstreamConfig(upstream, c)` (`src/utils/upstream.ts`)
+- **Proxy mode**: `PROXY=true` → prefer local DB/R2, then fallback upstream (default via `getDefaultUpstream()`)
 
-Never stub out an endpoint in the source code (tests are fine). Either you fully realize the functionality or you bail & document why you are not creating an endpoint because of some limitation. Leaving a feature/endpoint half-implemented is the worst state.
+## Not Implemented Endpoints
 
-### Route Handling
-- **Catch-all routing**: Main router uses catch-all pattern `/*` to handle all package routes
-- **Upstream detection**: Routes like `/npm/package` set upstream context via `c.set('upstream', 'npm')`
-- **Parameter extraction**: For upstream routes, extract package names from path since route params aren't available
-- **Reserved routes**: Check against RESERVED_ROUTES before treating as package names
+Avoid silent stubs. If an endpoint isn’t implemented yet, return an explicit 501 + docstring (see `src/routes/misc.ts` `auditRoute`).
 
-### Package Name Extraction
-```typescript
-// Always handle both route parameters AND path extraction for upstream routes
-const upstream = c.get('upstream') as string
-if (!scope && !pkg && upstream) {
-  // Extract from path: /npm/lodash -> lodash, /npm/@scope/pkg -> @scope/pkg
-  const pathSegments = path.split('/').filter(Boolean)
-  const packageSegments = pathSegments.slice(1) // Remove upstream prefix
-  // Handle scoped vs unscoped packages
-}
-```
+## Package Name Extraction
 
-### Upstream Configuration
-- **Config-driven**: Upstreams defined in `config.ts` ORIGIN_CONFIG
-- **URL resolution**: Use `getUpstreamConfig(upstream)` to get upstream-specific URLs
-- **Proxy logic**: When PROXY=true, check local first, then upstream for missing packages
+For upstream routes, extract from path since route params aren't available. Handle both scoped (`@scope/pkg`) and unscoped. Check against RESERVED_ROUTES.
 
-### Error Handling
-- **Consistent errors**: Use standard error format `{ error: 'message' }` with appropriate HTTP status
-- **Upstream errors**: 502 for upstream failures, 404 for not found, 400 for invalid requests
-- **Graceful fallbacks**: Always provide fallback behavior for upstream failures
+## DB Patterns
 
-## Database Patterns
+- Packages: name, tags (dist-tags), lastUpdated. Versions: `package@version` format
+- Proxy packages: `source='proxy'` prevents local operations
+- Cache: `getCachedPackageWithRefresh` (short TTL), `getCachedVersionWithRefresh` (longer TTL)
+- Background refresh via `c.executionCtx.waitUntil()`
 
-### Package Storage
-- **Consistent structure**: All packages have name, tags (dist-tags), lastUpdated
-- **Version specs**: Store as "package@version" format for versions table
-- **Proxy marking**: Mark proxied packages with source='proxy' to prevent local operations
+## Key Patterns
 
-### Cache Strategy
-- **Racing cache**: Use `getCachedPackageWithRefresh` for packuments (short TTL)
-- **Longer TTL**: Use `getCachedVersionWithRefresh` for manifests (longer TTL)
-- **Background refresh**: Queue refresh tasks via `c.executionCtx.waitUntil()`
-- **Key consistency**: Use 'dist-tags' not 'tags' in cache functions
+- **Slim manifests**: `slimManifest(manifest, context, c)` in `src/utils/packages.ts`
+- **Tarball URLs**: local uses `${c.env.URL}/${createFile({ pkg, version })}`; upstream rewrites to `/${upstream}/${pkg}/-/<file>.tgz`
+- **Cache headers**: manifests `public, max-age=300`; tarballs `public, max-age=31536000`
 
-## Testing Best Practices
+## Dev Commands
 
-### Mock Setup
-- **Complete mocks**: Always mock all required methods (getPackage, getVersion, getCachedPackage, upsertCachedPackage)
-- **Context mocking**: Include `get` method for upstream context and `executionCtx.waitUntil` for background tasks
-- **Parameter structure**: For dist-tags, unscoped packages use scope parameter, scoped use scope='@scope' + pkg
-
-### Route Testing
-- **Upstream routes**: Test both direct routes (`/package`) and upstream routes (`/npm/package`)
-- **Parameter extraction**: Verify package name extraction works for both parameter-based and path-based routes
-- **Error scenarios**: Test 404s, 400s, 502s with appropriate error messages
-
-## Code Quality
-
-### TypeScript
-- **Strict typing**: Use proper types, avoid `any` except for upstream response parsing
-- **Error handling**: Always wrap external calls in try-catch with appropriate error responses
-- **Interface consistency**: Use existing interfaces (HonoContext, PackageManifest, etc.)
-
-### Performance
-- **Minimize database calls**: Batch operations where possible
-- **Stream large responses**: Use streaming for tarballs >10MB
-- **Cache headers**: Set appropriate Cache-Control headers for different content types
-- **Background tasks**: Use waitUntil for non-critical operations (storage, cache updates)
-
-### Security
-- **Input validation**: Always validate package names, versions, and user input
-- **URL encoding**: Properly decode URL-encoded package names and versions
-- **Integrity checks**: Validate tarball integrity when headers provided
-- **Access control**: Check permissions for dist-tag operations and publishing
-
-## Common Patterns
-
-### Manifest Handling
-```typescript
-// Always slim manifests for responses
-const slimmedManifest = slimManifest(versionData.manifest)
-// Rewrite tarball URLs to point to our registry
-if (manifest.dist?.tarball) {
-  manifest.dist.tarball = `${DOMAIN}/${createFile({ pkg, version })}`
-}
-```
-
-### Upstream Proxying
-```typescript
-// Check local first, then upstream if PROXY enabled
-const localData = await c.db.getPackage(name)
-if (!localData && upstream && PROXY) {
-  const upstreamConfig = getUpstreamConfig(upstream)
-  const response = await fetch(`${upstreamConfig.url}/${name}`)
-  // Handle response, cache if needed
-}
-```
-
-### Response Headers
-```typescript
-// Set appropriate headers for different content types
-c.header('Content-Type', 'application/json')
-c.header('Cache-Control', 'public, max-age=300') // 5 min for manifests
-c.header('Cache-Control', 'public, max-age=31536000') // 1 year for tarballs
-```
-
-## Development Workflow
-
-### Testing
-- **Run full suite**: `pnpm test` runs all tests including e2e
-- **Individual tests**: `pnpm test:unit` for unit tests only
-- **Database setup**: `pnpm test:setup` to initialize test database
-- **Cleanup**: `pnpm test:cleanup` to kill wrangler processes
-
-### Local Development
-- **Dev server**: `pnpm serve:dev` starts wrangler dev with hot reload
-- **Database**: `pnpm db:setup` initializes local D1 database
-- **Assets**: `pnpm build:assets` copies GUI assets to serve folder
-
-### Debugging
-- **Wrangler logs**: Check wrangler dev output for request/response logs
-- **Database studio**: `pnpm db:studio` opens Drizzle Studio on port 4985
-- **Test isolation**: Each test cleans up its own state to avoid interference
+- `pnpm serve:build` — build + run `dist/bin/vsr.js --debug`
+- `pnpm serve:watch` — chokidar watch: rebuild + restart
+- `pnpm deploy` — build + `wrangler deploy`
+- `pnpm db:setup` / `pnpm db:studio` (port 4985)
+- `pnpm test`, `pnpm snap`, `pnpm typecheck`
 
 ## Key Files
-- `src/index.ts`: Main router and catch-all handler
-- `src/routes/packages.ts`: Core package route handlers
-- `src/utils/cache.ts`: Caching strategy implementation
-- `src/utils/upstream.ts`: Upstream configuration and URL building
-- `config.ts`: Registry configuration and upstream definitions
-- `test/`: Comprehensive test suite with e2e, unit, and integration tests
+
+`src/index.ts` (router), `src/routes/packages.ts`, `src/routes/misc.ts`, `src/utils/cache.ts`, `src/utils/upstream.ts`, `src/utils/packages.ts`, `config.ts`
PATCH

echo "Gold patch applied."
