#!/usr/bin/env bash
set -euo pipefail

cd /workspace/kubb

# Idempotency guard
if grep -qF "Kubb uses a plugin-based architecture where plugins generate code from OpenAPI s" "AGENTS.md" && grep -qF "This document provides essential guidelines for AI coding assistants (Cursor, Gi" "docs/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,332 @@
+# AGENTS.md
+
+This document provides essential information for AI coding assistants (Cursor, GitHub Copilot) working on the Kubb codebase.
+
+## Repository facts
+
+- **Monorepo**: Managed by pnpm workspaces and Turborepo
+- **Module system**: ESM-only (`type: "module"` across repo)
+- **Node version**: 20
+- **Versioning**: Changesets for versioning and publishing
+- **CI/CD**: GitHub Actions
+
+## Setup commands
+
+```bash
+pnpm install                # Install dependencies
+pnpm clean                  # Clean build artifacts
+pnpm build                  # Build all packages
+pnpm generate               # Generate code from OpenAPI specs
+pnpm perf                   # Run performance tests
+pnpm test                   # Run tests
+pnpm typecheck              # Type check all packages
+pnpm typecheck:examples     # Type check examples
+pnpm format                 # Format code
+pnpm lint                   # Lint code
+pnpm lint:fix               # Lint and fix issues
+pnpm changeset              # Create changelog entry
+pnpm run upgrade && pnpm i   # Upgrade dependencies
+```
+
+## Testing instructions
+
+- Find the CI plan in `.github/workflows/quality` folder
+- From package root, run `pnpm test` - all tests must pass before merging
+- Focus on specific tests: `pnpm test "<test name>"`
+- Fix all test and type errors until suite is green
+- After moving files or changing imports: `pnpm lint && pnpm typecheck`
+- Always add or update tests for code changes
+- **For docs changes**: Preview locally with `pnpm start` in `docs/` folder before committing
+
+## Code style
+
+- **Quotes**: Single quotes, no semicolons (see `biome.json`)
+- **Patterns**: Prefer functional patterns
+
+**TypeScript conventions:**
+- Module resolution: `"bundler"`; ESM only
+- Prefer strict typing; avoid `any`
+- Files: `.ts` for libraries, `.tsx` for React components, `.vue` for Vue components
+- DTS output managed by `tsdown`
+
+**Naming conventions:**
+- File/directory names: `camelCase`
+- Variables/functions: `camelCase`
+- Types/Interfaces: `PascalCase`
+- React components: `PascalCase`
+
+**Exports**: Packages use `"exports"` map and `typesVersions` as needed, keep public API stable
+
+**Testing**: Test files named `*.test.ts` or `*.test.tsx` in `src` folders
+
+## PR instructions
+
+### General
+
+- **Title format**: `[<plugin-name>] <Title>`
+- **Before committing**: Run `pnpm format && pnpm lint:fix`, `pnpm typecheck`, and `pnpm test`
+- **Before committing**: Run `pnpm generate` and `pnpm typecheck:examples` in a separate commit
+
+### Changelog and documentation
+
+- Always update `changelog.md` after major/minor/patch version
+- Always use `pnpm changeset` to create changelog
+- **Update docs in the same PR as code changes** (unless it's a docs-only PR)
+- Update docs when:
+  - Adding a new plugin or feature
+  - Changing plugin options or behavior
+  - Fixing bugs that affect user-facing behavior
+  - Adding new examples or tutorials
+  - Updating API signatures or types
+- When fixing bugs: update relevant docs if the fix changes behavior, add notes if it affects user workflow, update examples if they were incorrect
+
+### Review checklist for agent-created PRs
+
+- [ ] Does CI pass? (unit tests, linters, typechecks)
+- [ ] Is the change small and well-scoped?
+- [ ] Are there any secrets, tokens, or sensitive data accidentally added?
+- [ ] Are dependency updates pinned to safe versions and tested?
+- [ ] Documentation: is content accurate and matches repository conventions?
+- [ ] If AI-assisted: check for hallucinated facts, incorrect code assumptions, or missing context
+- [ ] Factual accuracy: verify all information is correct
+- [ ] Consistency: follow existing code and documentation patterns
+- [ ] Completeness: all features and options are documented
+
+### Security and secrets
+
+- **Never commit secrets or credentials**
+- If an agent PR contains secrets, immediately close the PR and rotate exposed secrets
+- Use repository secrets and Actions masked variables for CI
+
+### When to approve and merge
+
+- Approve only when review checklist is satisfied
+- Prefer squash merging small, single-purpose agent PRs
+- For larger updates, consider staged roll-out or incremental approach
+
+## Architecture instructions
+
+### Plugin system overview
+
+Kubb uses a plugin-based architecture where plugins generate code from OpenAPI specifications. The system is inspired by Rollup, Unplugin, and Snowpack.
+
+**Key concepts:**
+- **PluginManager**: Orchestrates plugin execution and manages file generation lifecycle
+- **Plugins**: Define generators, resolve paths/names, and hook into lifecycle events
+- **Generators**: Functions or React components that generate code files
+- **Components**: React components (using `@kubb/react-fabric`) that render code templates
+- **Options**: Plugin configuration that gets resolved and validated
+
+### Plugin structure
+
+Plugins follow this structure:
+
+```typescript
+export const definePlugin = createPlugin<PluginOptions>((options) => {
+  return {
+    name: pluginName,
+    options,
+    pre: [], // Plugins that must run before this one
+    post: [], // Plugins that run after this one
+    resolvePath(baseName, mode, options) { /* ... */ },
+    resolveName(name, type) { /* ... */ },
+    async install() { /* ... */ },
+  }
+})
+```
+
+### Components
+
+Components are React components (using `@kubb/react-fabric`) that generate code templates. They use JSX syntax to declaratively create files.
+
+**Location**: `packages/plugin-*/src/components/`
+
+**Example structure**:
+
+```tsx
+import { File, Function, FunctionParams } from '@kubb/react-fabric'
+import type { KubbNode } from '@kubb/react-fabric/types'
+
+export function Query({ name, operation, typeSchemas, ...props }: Props): KubbNode {
+  return (
+    <File.Source name={name} isExportable isIndexable>
+      <Function name={name} export params={params.toConstructor()}>
+        {/* Generated code */}
+      </Function>
+    </File.Source>
+  )
+}
+```
+
+**Key points**:
+- Components return `KubbNode` (JSX elements)
+- Use `@kubb/react-fabric` components like `<File>`, `<Function>`, `<Const>`, `<Type>`, etc.
+- Components are composable and reusable
+- Access plugin context via hooks: `usePluginManager()`, `useOas()`, `useOperationManager()`
+
+### Generators
+
+Generators define how code is generated. There are two types:
+
+#### 1. Function-based generators
+
+Return `Promise<KubbFile.File[]>`:
+
+```typescript
+import { createGenerator } from '@kubb/plugin-oas/generators'
+
+export const myGenerator = createGenerator({
+  name: 'my-generator',
+  async operation(props) {
+    // props: { generator, config, operation, plugin }
+    return [/* KubbFile.File[] */]
+  },
+  async operations(props) {
+    // props: { generator, config, operations, plugin }
+    return [/* KubbFile.File[] */]
+  },
+  async schema(props) {
+    // props: { generator, config, schema, plugin }
+    return [/* KubbFile.File[] */]
+  },
+})
+```
+
+#### 2. React-based generators (recommended)
+
+Use `createReactGenerator` and return JSX components:
+
+```tsx
+import { createReactGenerator } from '@kubb/plugin-oas/generators'
+import { File } from '@kubb/react-fabric'
+import { Query } from '../components/Query'
+
+export const queryGenerator = createReactGenerator<PluginOptions>({
+  name: 'query-generator',
+  Operation({ config, plugin, operation, generator }) {
+    // Return JSX component
+    return (
+      <File baseName="query.ts" path="./gen/query.ts">
+        <Query name="usePet" operation={operation} />
+      </File>
+    )
+  },
+  Operations({ config, plugin, operations, generator }) {
+    // Optional: Generate code for all operations
+    return null
+  },
+  Schema({ config, plugin, schema, generator }) {
+    // Optional: Generate code for schemas
+    return null
+  },
+})
+```
+
+**Key differences**:
+- React generators return `KubbNode` (JSX), function generators return `Promise<KubbFile.File[]>`
+- React generators are rendered by `react-fabric` and automatically converted to files
+- React generators provide better type safety and composability
+
+**Location**: `packages/plugin-*/src/generators/`
+
+### Options
+
+Plugin options are defined using `PluginFactoryOptions`:
+
+```typescript
+export type Options = {
+  output?: Output<Oas>
+  group?: Group
+  // ... other options
+}
+
+export type PluginOptions = PluginFactoryOptions<
+  'plugin-name',
+  Options,           // User-provided options
+  ResolvedOptions,   // Resolved/validated options
+  Context,           // Context exposed to other plugins
+  ResolvePathOptions // Options for resolvePath
+>
+```
+
+**Option resolution**:
+- Options are passed from `kubb.config.ts` to plugin
+- Plugins can resolve/transform options in their `install` hook
+- Resolved options are available via `plugin.options` in generators/components
+- Options can be overridden per-operation using `override` arrays
+
+### React-fabric usage
+
+`@kubb/react-fabric` is used throughout the plugin system to generate files using JSX.
+
+**Core concepts**:
+- **Fabric instance**: Created via `createReactFabric()` and passed to `PluginManager`
+- **File generation**: Components render JSX, fabric converts to files
+- **File management**: Fabric manages file queue, imports, exports, and deduplication
+
+**How it works**:
+1. PluginManager creates a fabric instance
+2. Generators use React components to define file structure
+3. Components are rendered via `fabric.render()` or `buildOperation()`/`buildOperations()`
+4. Fabric extracts files from rendered JSX and adds to FileManager
+5. Files are processed, transformed, and written to disk
+
+**Example flow**:
+
+```typescript
+// In OperationGenerator.build()
+if (generator.type === 'react') {
+  await buildOperation(operation, {
+    config,
+    fabric: this.context.fabric,
+    Component: generator.Operation,
+    generator: this,
+    plugin,
+  })
+}
+```
+
+**Available components** (`@kubb/react-fabric`):
+- `<File>`: File container with imports/exports
+- `<File.Source>`: Source code container
+- `<File.Import>`: Import statements
+- `<Function>`: Function declarations
+- `<Const>`: Constant declarations
+- `<Type>`: Type declarations
+- `<Interface>`: Interface declarations
+
+**Hooks** (`@kubb/react-fabric`):
+- `usePluginManager()`: Access PluginManager instance
+- `useOas()`: Access OpenAPI spec
+- `useOperationManager()`: Utilities for operation-based generation
+- `usePlugin()`: Access current plugin instance
+
+### Common patterns
+
+**Accessing other plugins**:
+
+```typescript
+const pluginManager = usePluginManager()
+const tsPlugin = pluginManager.getPluginByKey([pluginTsName])
+```
+
+**Resolving paths**:
+
+```typescript
+const file = getFile(operation, { pluginKey: [pluginTsName] })
+// Uses plugin's resolvePath hook
+```
+
+**Resolving names**:
+
+```typescript
+const name = getName(operation, { type: 'function', prefix: 'use' })
+// Uses plugin's resolveName hook
+```
+
+**Getting schemas**:
+
+```typescript
+const schemas = getSchemas(operation, { pluginKey: [pluginTsName], type: 'type' })
+// Returns: { request, response, pathParams, queryParams, headerParams, errors }
+```
diff --git a/docs/AGENTS.md b/docs/AGENTS.md
@@ -0,0 +1,317 @@
+# AGENTS.md
+
+This document provides essential guidelines for AI coding assistants (Cursor, GitHub Copilot) working on Kubb documentation. Repository docs are located in the `docs/` folder and use Markdown (MD or MDX) with VitePress.
+
+## When to update documentation
+
+See root `AGENTS.md` for general guidance on when to update documentation. This section covers documentation-specific details.
+
+## Folder structure
+
+```
+docs/
+├── .vitepress/           # VitePress configuration
+├── migration-guide.md    # Updated after major releases
+├── changelog.md          # Updated with every PR (via changeset)
+├── getting-started/      # Getting started guides
+├── blog/                 # Blog posts (after major releases)
+├── helpers/              # Extra packages (CLI, OAS core)
+├── knowledge-base/       # Feature deep-dives and how-tos
+│   ├── debugging.md
+│   ├── fetch.md
+│   ├── multipart-form-data.md
+│   └── ...
+├── plugins/              # Plugin documentation
+│   ├── core/             # Shared plugin options
+│   └── plugin-*/         # Individual plugin docs
+├── tutorials/            # Step-by-step tutorials
+├── examples/             # Playground and examples
+└── builders/             # Builder integrations (unplugin, etc.)
+```
+
+## File naming conventions
+
+- **Use kebab-case**: `how-to-do-thing.md`
+- **Be descriptive**: `multipart-form-data.md` not `form.md`
+- **Match URL structure**: File name becomes the URL path
+
+## Frontmatter
+
+Every documentation file must include YAML frontmatter. Required fields:
+
+```yaml
+---
+layout: doc          # Always use 'doc' for documentation pages
+title: Page Title     # Displayed in browser tab and page header
+outline: deep        # Enables deep table of contents
+---
+```
+
+### Plugin documentation frontmatter
+
+```yaml
+---
+layout: doc
+title: \@kubb/plugin-name  # Escape @ symbol
+outline: deep
+---
+```
+
+## Documentation structure
+
+### Plugin documentation template
+
+All plugin docs follow this structure:
+
+1. **Title and description**
+2. **Installation** (code-group with package managers)
+3. **Options** (with tables and descriptions)
+4. **Examples** (at the bottom)
+5. **Links** (if applicable, at the very end)
+
+### Options documentation format
+
+For each option, use this table format:
+
+```markdown
+### optionName
+
+Brief description of what this option does.
+
+> [!TIP]
+> Optional tip or important note
+
+|           |             |
+|----------:|:------------|
+|     Type: | `string`    |
+| Required: | `true`      |
+|  Default: | `'default'` |
+```
+
+**Rules:**
+- Use right-aligned column headers (`|----------:|`)
+- Type should be formatted as code (backticks)
+- Include `Required` field (true/false)
+- Include `Default` if there's a default value
+- Add tips using `> [!TIP]` or `> [!WARNING]` blocks
+
+### Code examples
+
+**Always include working examples** at the bottom of plugin docs:
+
+```typescript twoslash [kubb.config.ts]
+import { defineConfig } from '@kubb/core'
+import { pluginOas } from '@kubb/plugin-oas'
+import { pluginTs } from '@kubb/plugin-ts'
+import { pluginName } from '@kubb/plugin-name'
+
+export default defineConfig({
+  input: {
+    path: './petStore.yaml',
+  },
+  output: {
+    path: './src/gen',
+  },
+  plugins: [
+    pluginOas(),
+    pluginTs(),
+    pluginName({
+      // Show relevant options
+    }),
+  ],
+})
+```
+
+**Code example guidelines:**
+- Use `twoslash` annotation for TypeScript examples (enables type checking)
+- Show realistic, complete configurations
+- Include all required plugins
+- Use `petStore.yaml` as the standard example input
+- Place examples at the bottom of the page
+
+### Including shared content
+
+Use VitePress `@include` directive to reuse shared content:
+
+```markdown
+### contentType
+<!--@include: ../core/contentType.md-->
+```
+
+**Common includes:**
+- `../core/contentType.md` - Content type option
+- `../core/barrelTypes.md` - Barrel type explanations
+- `../core/group.md` - Grouping options
+- `../core/groupTypes.md` - Group type options
+
+**Location**: `docs/plugins/core/`
+
+## Documenting new features
+
+When adding a new feature:
+
+1. **Create or update relevant docs**:
+   - New plugin → Create `docs/plugins/plugin-name/index.md`
+   - New option → Add to existing plugin doc
+   - New concept → Add to `knowledge-base/` or appropriate section
+
+2. **Follow the template**:
+   - Use existing plugin docs as reference
+   - Include installation, options, and examples
+   - Link to related plugins/concepts
+
+3. **Update navigation**:
+   - Check `.vitepress/config.ts` for sidebar structure
+   - Add new items to appropriate sections
+
+4. **Add examples**:
+   - Ensure examples work with `petStore.yaml`
+   - Test examples locally before committing
+
+## Documenting bug fixes
+
+See root `AGENTS.md` for general guidance on documenting bug fixes. Focus on documentation-specific details here.
+
+## Code groups
+
+Use code groups for multiple package managers:
+
+```markdown
+::: code-group
+
+```shell [bun]
+bun add -d @kubb/plugin-name
+```
+
+```shell [pnpm]
+pnpm add -D @kubb/plugin-name
+```
+
+```shell [npm]
+npm install --save-dev @kubb/plugin-name
+```
+
+```shell [yarn]
+yarn add -D @kubb/plugin-name
+```
+:::
+```
+
+**Always include**: bun, pnpm, npm, yarn (in that order)
+
+## Images and assets
+
+- **Location**: `docs/public/`
+- **Reference**: Use relative paths from markdown files
+- **Formats**: Use optimized formats (`webp`/`png`/`jpg`)
+- **Sizing**: Keep file sizes reasonable
+- **Naming**: Use descriptive names: `plugin-react-query-example.png`
+
+## Links and cross-references
+
+- **Internal links**: Use relative paths: `/plugins/plugin-ts/`
+- **Anchor links**: Link to specific sections: `/plugins/plugin-ts/#output-path`
+- **External links**: Use full URLs with descriptive text
+- **Placement**: Add links section at the very end of the document
+
+**Example:**
+
+```markdown
+## Links
+
+- [Plugin OAS](/plugins/plugin-oas/)
+- [Getting Started](/getting-started/at-glance/)
+```
+
+## Writing style
+
+- **Be concise**: Short paragraphs, clear sentences
+- **Be actionable**: Use imperative mood ("Set the option to...")
+- **Use examples**: Show, don't just tell
+- **Include outputs**: Show expected results for commands
+- **Be consistent**: Follow existing documentation patterns
+
+## Testing documentation
+
+Before submitting docs changes:
+
+1. **Preview locally**: Run `pnpm start` in `docs/` folder (see root `AGENTS.md` for general testing)
+2. **Check links**: Verify all internal/external links work
+3. **Verify examples**: Ensure code examples are correct
+4. **Check formatting**: Tables, code blocks render correctly
+5. **Test navigation**: Verify sidebar navigation works
+
+## PR checklist for documentation
+
+- [ ] Documentation updated for all code changes
+- [ ] Frontmatter is correct (`layout: doc`, `title`, `outline: deep`)
+- [ ] Options documented with proper table format
+- [ ] Examples included and tested
+- [ ] Links verified (internal and external)
+- [ ] Images optimized and properly referenced
+- [ ] Code groups include all package managers
+- [ ] Shared content uses `@include` where appropriate
+- [ ] Navigation updated if needed (`.vitepress/config.ts`)
+- [ ] Changelog updated via `pnpm changeset`
+
+## Common patterns
+
+### Documenting a new plugin option
+
+```markdown
+### newOption
+
+Description of what this option does and when to use it.
+
+> [!TIP]
+> Optional helpful tip
+
+|           |             |
+|----------:|:------------|
+|     Type: | `string \| boolean` |
+| Required: | `false`     |
+|  Default: | `'default'` |
+```
+
+### Documenting breaking changes
+
+Add to `migration-guide.md`:
+
+```markdown
+## Breaking changes in vX.Y.Z
+
+### Plugin Name
+
+**Before:**
+```typescript
+pluginName({ oldOption: true })
+```
+
+**After:**
+```typescript
+pluginName({ newOption: true })
+```
+```
+
+### Adding a new tutorial
+
+1. Create file in `docs/tutorials/`
+2. Use step-by-step format
+3. Include complete working examples
+4. Link from getting-started or relevant plugin docs
+
+## Review guidance for agent-created docs
+
+See root `AGENTS.md` for general review checklist. Documentation-specific checks:
+
+- **No hallucinations**: Check that examples and code actually work
+- **Navigation**: Confirm frontmatter and file placement are correct
+- **Links**: Ensure all links resolve correctly
+- **VitePress formatting**: Verify frontmatter, code groups, and includes work correctly
+
+## Getting help
+
+- **Reference existing docs**: Use similar plugins as templates
+- **Check `.vitepress/config.ts`**: Understand navigation structure
+- **Review `docs/plugins/core/`**: See shared option documentation
+- **Test locally**: Always preview changes before committing
PATCH

echo "Gold patch applied."
