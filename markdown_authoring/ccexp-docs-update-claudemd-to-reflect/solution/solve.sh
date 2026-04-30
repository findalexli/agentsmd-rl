#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ccexp

# Idempotency guard
if grep -qF "**ccexp** (short for claude-code-explorer) - React Ink-based CLI tool for explor" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -4,7 +4,7 @@ This file provides guidance to Claude Code (claude.ai/code) when working with co
 
 ## Overview
 
-**ccexp** - React Ink-based CLI tool for exploring and managing Claude Code settings and slash commands. The tool provides an interactive terminal UI for file navigation, content preview, and file management operations.
+**ccexp** (short for claude-code-explorer) - React Ink-based CLI tool for exploring and managing Claude Code settings and slash commands. The tool provides an interactive terminal UI for file navigation, content preview, and file management operations. The package was renamed from `claude-code-explorer` to `ccexp` for brevity and easier command-line usage.
 
 ## Core Commands
 
@@ -26,6 +26,10 @@ bun run check:unsafe          # Biome unsafe auto-fix
 bun run knip                  # Check for unused dependencies/exports
 bun run ci                    # Full CI pipeline (build + check + typecheck + knip + test)
 
+# Release Management
+bun run release               # Interactive version bumping with bumpp
+bun run prepack              # Pre-publish build and package.json cleanup
+
 # CLI Usage
 ./dist/index.js               # Interactive React Ink TUI mode
 bun run start                 # Development mode with hot reload
@@ -56,24 +60,53 @@ src/
 │   ├── FileList/      # File navigation and menu
 │   │   ├── FileList.tsx      # Main file list with search
 │   │   ├── FileItem.tsx      # Individual file item
-│   │   ├── MenuActions.tsx   # File action menu
+│   │   ├── FileGroup.tsx     # File grouping by type
+│   │   ├── MenuActions/      # File action menu module
+│   │   │   ├── index.tsx     # Main menu component
+│   │   │   ├── Footer.tsx    # Menu footer controls
+│   │   │   ├── Header.tsx    # Menu header
+│   │   │   ├── MenuItem.tsx  # Individual menu item
+│   │   │   ├── MenuList.tsx  # Menu item container
+│   │   │   ├── StatusMessage.tsx # Action feedback
+│   │   │   ├── types.ts      # Menu types
+│   │   │   └── hooks/
+│   │   │       └── useMenu.ts    # Menu state management
 │   │   └── *.test.tsx        # Component tests
 │   ├── Layout/        # Layout components
 │   │   ├── SplitPane.tsx     # Two-pane layout
 │   │   └── *.test.tsx        # Layout tests
 │   ├── Preview/       # Content preview
 │   │   ├── Preview.tsx       # File preview pane
-│   │   └── MarkdownPreview.tsx # Markdown renderer
-│   └── ErrorBoundary.tsx     # Error handling component
+│   │   ├── MarkdownPreview.tsx # Markdown renderer
+│   │   └── *.test.tsx        # Preview tests
+│   ├── ErrorBoundary.tsx     # Error handling component
+│   ├── ErrorBoundary.test.tsx # Boundary tests
+│   ├── LoadingScreen.tsx     # Loading UI component
+│   └── LoadingScreen.test.tsx # Loading tests
 ├── hooks/             # React hooks
 │   ├── useFileNavigation.tsx # File scanning and state
+│   ├── useFileNavigation.test.tsx # Hook tests
 │   └── index.ts       # Hook exports
 ├── _types.ts          # Type definitions (including branded types)
 ├── _consts.ts         # Constants and configuration
 ├── _utils.ts          # Utility functions with InSource tests
+├── base-file-scanner.ts    # Abstract scanner base class
 ├── claude-md-scanner.ts    # CLAUDE.md file scanner
 ├── slash-command-scanner.ts # Slash command scanner
+├── default-scanner.ts      # Default file scanner implementation
 ├── fast-scanner.ts    # High-performance file scanner
+├── scan-exclusions.ts # File/directory exclusion patterns
+├── test-setup.ts      # Global test setup
+├── test-utils.ts      # Common test utilities
+├── test-fixture-helpers.ts # fs-fixture utilities
+├── test-keyboard-helpers.ts # Keyboard interaction testing
+├── test-interaction-helpers.ts # UI interaction testing
+├── test-navigation.ts # Navigation test helpers
+├── boundary.test.tsx  # Error boundary integration tests
+├── e2e.test.tsx       # End-to-end tests
+├── vitest.d.ts        # Vitest type definitions
+├── styles/
+│   └── theme.ts       # UI color theme constants
 ├── App.tsx            # Main React application
 └── index.tsx          # Entry point with React Ink render
 ```
@@ -93,17 +126,18 @@ src/
    }
    ```
 
-2. **Branded Types + Runtime Validation**: Compile-time & runtime type safety
+2. **Simplified Type System**: Clean types with runtime validation where needed
 
    ```typescript
-   // Type-level branding
-   export type ClaudeFilePath = string & { readonly [ClaudeFilePathBrand]: true };
+   // Simple type alias approach
+   export type ClaudeFilePath = string;
 
-   // Runtime validation
-   export const ClaudeFilePathSchema = z.string().refine(/* validation */);
+   // Runtime validation helper
    export const createClaudeFilePath = (path: string): ClaudeFilePath => {
-     ClaudeFilePathSchema.parse(path);
-     return path as ClaudeFilePath;
+     if (path.length === 0) {
+       throw new Error('Path must not be empty');
+     }
+     return path;
    };
    ```
 
@@ -154,13 +188,45 @@ src/
    }, { isActive: true });
    ```
 
+6. **Scanner Hierarchy**: Modular scanner architecture with base class
+
+   ```typescript
+   // Base scanner provides common functionality
+   export abstract class BaseFileScanner<T> {
+     protected abstract readonly maxFileSize: number;
+     protected abstract readonly fileType: string;
+     
+     async processFile(filePath: string): Promise<T | null> {
+       // Common file processing logic
+     }
+     
+     protected abstract parseContent(
+       filePath: string,
+       content: string,
+       stats: Stats,
+     ): Promise<T | null>;
+   }
+   
+   // Specialized scanners extend base
+   class ClaudeMdScanner extends BaseFileScanner<ClaudeFileInfo> {
+     protected readonly maxFileSize = FILE_SIZE_LIMITS.MAX_CLAUDE_MD_SIZE;
+     protected readonly fileType = 'Claude.md';
+   }
+   ```
+
 ### Data Flow Architecture
 
-- **Scanners**: `claude-md-scanner.ts` + `slash-command-scanner.ts` → discover files
+- **Scanners**: Multiple specialized scanners → discover files
+  - `base-file-scanner.ts` → Abstract base class for all scanners
+  - `claude-md-scanner.ts` → CLAUDE.md file discovery
+  - `slash-command-scanner.ts` → Slash command discovery
+  - `default-scanner.ts` → Combined scanner for all file types
+  - `fast-scanner.ts` → High-performance directory traversal
 - **Type System**: `_types.ts` → branded types + zod schemas for data integrity
 - **React State**: `useFileNavigation` hook → file loading and selection state
 - **Components**: React Ink components → interactive terminal UI
 - **File Operations**: clipboard, file opening via system integrations
+- **Exclusions**: `scan-exclusions.ts` → Configurable file/directory filtering
 
 ### Target File Discovery
 
@@ -180,7 +246,9 @@ The tool automatically discovers these file types:
 - `noImplicitReturns: true` → All code paths must return
 - Immutable design with `readonly` properties throughout
 
-### Testing Philosophy
+### Testing Philosophy & Strategy
+
+#### Core Testing Principles
 
 - **InSource Testing**: Tests live with source code for component co-location
 - **fs-fixture**: File system test fixtures for reliable testing
@@ -189,6 +257,84 @@ The tool automatically discovers these file types:
 - **No test shortcuts**: All quality checks must pass before completion
 - **Comprehensive coverage**: React components, hooks, and business logic tested
 
+#### Efficient Test Architecture with fs-fixture
+
+The project employs a sophisticated testing strategy using `fs-fixture` for creating isolated file system environments:
+
+```typescript
+// Example from test-fixture-helpers.ts
+export async function withTempFixture<T>(
+  fileTree: FileTree,
+  callback: (fixture: FsFixture) => Promise<T>,
+): Promise<T> {
+  await using fixture = await createFixture(fileTree);
+  return callback(fixture);
+}
+
+// Usage example
+await withTempFixture(
+  { 'test.md': '# Test content' },
+  async (fixture) => {
+    const content = await fixture.readFile('test.md', 'utf-8');
+    // Test logic here
+  }
+);
+```
+
+#### Scanner Testing Strategy
+
+File scanners are tested using fs-fixture to create isolated file environments:
+
+```typescript
+// Example from claude-md-scanner.ts tests
+await using fixture = await createClaudeProjectFixture({
+  projectName: 'test-scan',
+  includeLocal: true,
+  includeCommands: true,
+});
+
+const result = await scanClaudeFiles({
+  path: fixture.getPath('test-scan'),
+  recursive: false,
+});
+
+// The scanner internally uses a singleton pattern
+const scanner = new ClaudeMdScanner();
+const fileInfo = await scanner.processFile(filePath);
+```
+
+#### Test Helper Architecture
+
+- **test-fixture-helpers.ts**: Factory functions for creating test file structures
+- **test-keyboard-helpers.ts**: Keyboard event simulation for React Ink components
+- **test-interaction-helpers.ts**: UI interaction testing utilities
+- **test-navigation.ts**: Navigation flow testing helpers
+- **test-utils.ts**: Common testing utilities and assertions
+
+#### Testing Configuration
+
+**vitest.config.ts**:
+```typescript
+export default defineConfig({
+  test: {
+    includeSource: ['src/**/*.{js,ts,tsx}'],
+    exclude: ['node_modules'],
+    globals: true,
+    environment: 'node',
+    setupFiles: ['./src/test-setup.ts'],
+  },
+  esbuild: {
+    jsx: 'automatic',
+  },
+});
+```
+
+This configuration enables:
+- InSource testing pattern
+- Global test functions without imports
+- Proper React JSX transformation
+- Consistent test environment setup
+
 ### React Ink User Experience
 
 - **Interactive TUI**: Full-screen terminal interface with React Ink
@@ -199,6 +345,12 @@ The tool automatically discovers these file types:
 - **Focus management**: `isActive` pattern prevents input conflicts
 - **Error handling**: StatusMessage component with graceful degradation
 - **Loading states**: Spinner component during file scanning
+- **File grouping**: Organized display by file type with collapsible groups
+  - CLAUDE.md files (Project configurations)
+  - CLAUDE.local.md files (Local overrides)
+  - Global CLAUDE.md (User-wide settings)
+  - Slash commands (Custom command definitions)
+  - Groups can be collapsed/expanded with arrow keys
 
 ## Quality Management Rules
 
@@ -258,6 +410,17 @@ bun run ci                    # Runs build + check + typecheck + knip + test in
 - Run `bun run check:write` frequently to auto-fix formatting
 - Verify with `bun run ci` before considering task complete
 
+## Git Hooks
+
+The project uses Lefthook for pre-commit hooks:
+
+```bash
+# Automatically runs on git commit:
+bun run ci  # Full quality pipeline
+```
+
+This ensures all code meets quality standards before committing.
+
 ## Release Management
 
 ### npm Publishing Setup
@@ -303,3 +466,20 @@ Before first release:
 3. Ensure npm account has publishing permissions
 
 See `VERSIONING.md` for detailed versioning strategy and commit message conventions.
+
+## CI/CD Pipeline
+
+The project uses GitHub Actions for continuous integration:
+
+### CI Workflow (`.github/workflows/ci.yml`)
+
+Runs on every push and pull request with the following jobs:
+
+1. **Build** - Verifies the project builds correctly
+2. **Lint & Format** - Ensures code style compliance with Biome
+3. **TypeScript Check** - Validates type safety
+4. **Knip** - Checks for unused dependencies
+5. **Tests** - Runs all unit and integration tests
+6. **Preview Package** - Publishes preview packages for PRs via `pkg-pr-new`
+
+All jobs run in parallel for efficiency, with PR preview packages only published after all checks pass.
PATCH

echo "Gold patch applied."
