#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vltpkg

# Idempotency guard
if grep -qF "This project itself uses catalogs \u2014 see root `vlt.json` for a real-world example" ".cursor/rules/catalogs.mdc" && grep -qF "`/` \u2192 `+`, special chars use `_X` escapes: `_c` = `:`, `_t` = `~`, `__` = `_`, `" ".cursor/rules/dep-id.mdc" && grep -qF "Use `<Code code=\"...\" title=\"Terminal\" lang=\"bash\" />` for command examples." ".cursor/rules/docs-website.mdc" && grep -qF "Limited subset for modifiers: `:root`, `:project`, `:workspace`, `#name` (id), `" ".cursor/rules/dss-breadcrumb.mdc" && grep -qF "globs: src/graph/src/install.ts,src/graph/src/reify/*,src/cli-sdk/src/commands/i" ".cursor/rules/install-build-phases.mdc" && grep -qF "Child deps inherit parent's registry by default. If `foo` comes from registry X," ".cursor/rules/registries-and-auth.mdc" && grep -qF "**Trust**: `:abandoned`, `:confused`, `:unmaintained`, `:unstable`, `:unknown`, " ".cursor/rules/security-archive.mdc" && grep -qF "Each test gets isolated `testdir` with separate `root/project/config/cache/data/" ".cursor/rules/smoke-tests.mdc" && grep -qF "Parses dependency specifiers into typed `Spec` objects. Used throughout the grap" ".cursor/rules/spec-parsing.mdc" && grep -qF "CLI args \u2192 project `vlt.json` \u2192 user `vlt.json` (XDG config dir) \u2192 defaults. Obj" ".cursor/rules/vlt-json-config.mdc" && grep -qF "- `vlx.resolve(positionals, options, promptFn?)` \u2192 `string | undefined` \u2014 core r" ".cursor/rules/vlx.mdc" && grep -qF "`cd` into a workspace dir \u2192 vlt auto-targets that workspace for install/run/etc." ".cursor/rules/workspaces.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/catalogs.mdc b/.cursor/rules/catalogs.mdc
@@ -0,0 +1,60 @@
+---
+description: Catalog protocol for centralized dependency version management
+globs: src/spec/src/*,src/graph/src/ideal/*,src/vlt-json/src/*
+alwaysApply: false
+---
+# Catalogs
+
+Centralized dependency specs in `vlt.json`, referenced via `catalog:` protocol in `package.json`.
+
+## Config (`vlt.json`)
+
+```json
+{
+  "catalog": { "typescript": "^5.0.0", "prettier": "^3.0.0" },
+  "catalogs": {
+    "testing": { "vitest": "^1.0.0" },
+    "build": { "esbuild": "^0.19.0" }
+  }
+}
+```
+
+## Usage in `package.json`
+
+```json
+{
+  "dependencies": {
+    "typescript": "catalog:",
+    "vitest": "catalog:testing"
+  }
+}
+```
+
+## CLI
+
+```bash
+vlt install typescript@catalog:
+vlt install vitest@catalog:testing
+```
+
+## How It Works
+
+1. `@vltpkg/spec` detects `catalog:` or `catalog:<name>` protocol during parsing
+2. Looks up the package name in `specOptions.catalog` (default) or `specOptions.catalogs[name]`
+3. Resolves to the actual spec string (e.g., `^5.0.0`)
+4. Stored in lockfile `options` field for reproducibility
+5. The resolved spec flows through graph building normally
+
+## Spec Properties
+
+- `spec.catalog` — the resolved catalog spec string
+- `spec.catalogName` — the named catalog (undefined for default catalog)
+
+## Errors
+
+- `"Named catalog not found"` — catalog name doesn't exist in `catalogs`
+- `"Name not found in catalog"` — package name not in the specified catalog
+
+## Tip
+
+This project itself uses catalogs — see root `vlt.json` for a real-world example with `tap`, `typescript`, `eslint`, `prettier`, etc.
diff --git a/.cursor/rules/dep-id.mdc b/.cursor/rules/dep-id.mdc
@@ -0,0 +1,73 @@
+---
+description: DepID format, encoding, and utilities
+globs: src/dep-id/src/*,src/dep-id/test/*
+alwaysApply: false
+---
+# DepID (`@vltpkg/dep-id`)
+
+Universal node identity format. `~`-delimited, filesystem-safe encoded strings.
+
+## Format
+
+```
+type~first~second[~extra]
+```
+
+- **registry**: `~~name@version` (default reg), `~npm~name@version`, `~http%3A...~name@ver`
+- **git**: `git~github:user/repo~branchname`, `git~git%2Bssh%3A...~semver:1.x`
+- **workspace**: `workspace~src/mything`
+- **file**: `file~.` (project root), `file~./path`
+- **remote**: `remote~https://example.com/pkg.tgz`
+
+**Extra** (4th segment): stores modifier query + `peerSetHash` (e.g., `peer.1`). See `joinExtra()`/`splitExtra()`.
+
+## Encoding
+
+`/` → `+`, special chars use `_X` escapes: `_c` = `:`, `_t` = `~`, `__` = `_`, `_d` = trailing `.`, control chars = `_XX` hex.
+
+## Key Functions
+
+```typescript
+// Create
+getId(spec, manifest, extra?) → DepID
+getTuple(spec, manifest, extra?) → DepIDTuple
+joinDepIDTuple(tuple) → DepID
+
+// Parse
+splitDepID(id) → DepIDTuple  // memoized
+baseDepID(id) → DepID         // strips extra
+hydrate(id, name?, options?) → Spec  // back to Spec
+
+// Extra parameter
+joinExtra({ modifier?, peerSetHash? }) → string | undefined
+splitExtra(extra) → { modifier?, peerSetHash? }
+// Detects 'peer.' delimiter to split modifier from peerSetHash
+
+// Cache management
+resetCaches()  // call when SpecOptions change
+```
+
+## DepIDTuple
+
+```typescript
+type DepIDTuple =
+  | [type: 'registry', registry: string, registrySpec: string, extra?: string]
+  | [type: 'git', gitRemote: string, gitSelector: string, extra?: string]
+  | [type: 'file', path: string, extra?: string]
+  | [type: 'remote', url: string, extra?: string]
+  | [type: 'workspace', workspace: string, extra?: string]
+```
+
+## Usage in Graph
+
+- `Node.id` is a DepID — unique identity in `graph.nodes` map
+- Resolution cache keys include `extra` for modifier/peer awareness
+- Lockfile keys are DepIDs
+- `hydrate()` reconstructs Spec from DepID for display/comparison
+
+## isPackageNameConfused
+
+```typescript
+isPackageNameConfused(spec?, name?) → boolean
+// true when manifest name differs from spec name (not aliased, registry type)
+```
diff --git a/.cursor/rules/docs-website.mdc b/.cursor/rules/docs-website.mdc
@@ -0,0 +1,60 @@
+---
+description: Documentation website development (Astro/Starlight)
+globs: www/docs/src/**/*
+alwaysApply: false
+---
+# Documentation Website (`www/docs/`)
+
+Astro/Starlight site → https://docs.vlt.sh
+
+## Content Structure
+
+```
+www/docs/src/content/docs/
+├── cli/
+│   ├── index.mdx           # CLI overview
+│   ├── configuring.mdx     # All CLI options/flags
+│   ├── selectors.mdx       # DSS selector reference
+│   ├── workspaces.mdx      # Workspace usage guide
+│   ├── catalogs.mdx        # Catalog protocol guide
+│   ├── registries.mdx      # Multi-registry guide
+│   ├── auth.mdx            # Authentication guide
+│   ├── security.mdx        # Security scanning guide
+│   ├── peer-dependencies.mdx
+│   ├── graph-modifiers.mdx
+│   └── commands/            # Per-command docs
+│       ├── install.mdx, build.mdx, query.mdx, ...
+├── registry/                # VSR (serverless registry) docs
+│   ├── api.mdx, configuring.mdx, deployment.mdx, ...
+└── index.mdx
+```
+
+## Format
+
+MDX files with Astro/Starlight components. Frontmatter:
+```mdx
+---
+title: Page Title
+sidebar:
+  label: Short Label
+  order: 1
+---
+import { Code } from '@astrojs/starlight/components'
+```
+
+Use `<Code code="..." title="Terminal" lang="bash" />` for command examples.
+
+## When to Update Docs
+
+- Adding/changing CLI options → update `cli/configuring.mdx`
+- Adding/changing commands → update/create `cli/commands/<cmd>.mdx`
+- Adding DSS selectors → update `cli/selectors.mdx`
+- Changing install/build behavior → update relevant command + concept docs
+
+## Dev
+
+```bash
+cd www/docs
+pnpm dev    # local dev server
+pnpm build  # production build
+```
diff --git a/.cursor/rules/dss-breadcrumb.mdc b/.cursor/rules/dss-breadcrumb.mdc
@@ -0,0 +1,55 @@
+---
+description: DSS parser and breadcrumb system for query/modifier traversal
+globs: src/dss-parser/src/*,src/dss-breadcrumb/src/*,src/dss-parser/test/*,src/dss-breadcrumb/test/*
+alwaysApply: false
+---
+# DSS Parser & Breadcrumb System
+
+Dependency Selector Syntax — CSS-like query language used by `vlt query`, `vlt build --target`, modifiers, `--scope`, `--allow-scripts`.
+
+## DSS Parser (`@vltpkg/dss-parser`)
+
+Parses DSS query strings into postcss-compatible AST nodes.
+
+**Node types** (check with helpers):
+- `isPseudoNode(node)` — `:pseudo` selectors (`:root`, `:dev`, `:malware`, etc.)
+- `isIdentifierNode(node)` — `#name` id selectors
+- `isCombinatorNode(node)` — `>` (child), ` ` (descendant), `~` (sibling)
+- `isTagNode(node)` — `*` universal selector
+- `isStringNode(node)` — quoted string values
+- `isCommentNode(node)` — comments
+- `isPostcssNodeWithChildren(node)` — has child nodes
+
+**Key exports**: `parse(query)` → AST, type guards above, `asStringNode()`, `asTagNode()`, `asPostcssNodeWithChildren()`
+
+## DSS Breadcrumb (`@vltpkg/dss-breadcrumb`)
+
+Interactive query walking for modifiers — walks a parsed query in lockstep with graph traversal.
+
+**Core concept**: A breadcrumb tracks position in a DSS query as the graph is traversed node-by-node. Used by `GraphModifier` to determine when a modifier's selector fully matches.
+
+### Key Types
+
+```typescript
+type ModifierBreadcrumb = { first: ModifierBreadcrumbItem, last: ModifierBreadcrumbItem }
+type ModifierBreadcrumbItem = { value: string, comparator: Function, next?: ModifierBreadcrumbItem }
+type ModifierInteractiveBreadcrumb = { current: ModifierBreadcrumbItem }
+type BreadcrumbSpecificity = { idCounter: number, commonCounter: number }
+```
+
+### Key Functions
+
+- `parseBreadcrumb(query)` → `ModifierBreadcrumb` — parses query into linked list of breadcrumb items
+- `specificitySort(entries)` — sorts modifier entries by CSS specificity (most specific first)
+- `removeQuotes(value)` — utility for processing string values
+
+### Supported Breadcrumb Selectors
+
+Limited subset for modifiers: `:root`, `:project`, `:workspace`, `#name` (id), `> #name` (child combinator). Pseudo selectors with semver params (`:semver(^1.0.0)`) supported via comparator functions.
+
+## Where DSS is Used
+
+- `src/query/` — full query engine with all pseudo-selectors (see `@query-pseudo-selector-creation.mdc`)
+- `src/graph/src/modifiers.ts` — modifier matching via breadcrumbs
+- `src/cli-sdk/` — `--scope`, `--allow-scripts`, `vlt build --target`
+- User-facing docs: `www/docs/src/content/docs/cli/selectors.mdx`
diff --git a/.cursor/rules/install-build-phases.mdc b/.cursor/rules/install-build-phases.mdc
@@ -0,0 +1,68 @@
+---
+description: Phased install/build model and install command options
+globs: src/graph/src/install.ts,src/graph/src/reify/*,src/cli-sdk/src/commands/install.ts,src/cli-sdk/src/commands/build.ts
+alwaysApply: false
+---
+# Phased Install & Build
+
+vlt separates installation into two phases for security.
+
+## Phase 1: `vlt install`
+
+Downloads and extracts packages into `node_modules` **without running lifecycle scripts**.
+
+Entry: `src/graph/src/install.ts` → `install(options, add?)`
+
+Flow:
+1. Validates options (frozen-lockfile vs clean-install conflicts)
+2. Reads/creates `package.json` (runs `vlt init` if missing)
+3. Loads unfiltered monorepo for full workspace coverage
+4. Loads actual graph → builds ideal graph → reifies changes
+5. Supports `--lockfile-only` mode (skip node_modules)
+
+### Key Options
+
+| Flag | Description |
+|------|-------------|
+| `--frozen-lockfile` | Fail if lockfile missing or out of sync with package.json |
+| `--expect-lockfile` | Fail if lockfile missing or outdated (used by `vlt ci`) |
+| `--lockfile-only` | Update only lockfile + package.json, skip node_modules |
+| `--allow-scripts=<selector>` | Allow scripts during install (DSS query) |
+| `-D` `--save-dev` | Save as devDependency |
+| `-O` `--save-optional` | Save as optionalDependency |
+| `--save-peer` | Save as peerDependency |
+
+## Phase 2: `vlt build`
+
+Runs lifecycle scripts selectively using DSS queries.
+
+**Default target**: `:scripts:not(:built):not(:malware)` — excludes already-built and malware-flagged packages.
+
+```bash
+vlt build                          # default target
+vlt build --target="#esbuild"      # specific package
+vlt build ":root > *"              # positional arg = target
+```
+
+### Build State
+
+Tracked per node: `'none' | 'needed' | 'built' | 'failed'`. Query with `:built`, `:scripts`, `:scripts:not(:built)`.
+
+Persist target: `vlt config set "command.build.target=<query>"`
+
+## `InstallOptions` Type
+
+```typescript
+type InstallOptions = LoadOptions & {
+  packageInfo: PackageInfoClient
+  cleanInstall?: boolean   // ci command
+  allowScripts: string     // DSS query for script permissions
+}
+```
+
+## Security Model
+
+- Install = download + extract only (safe)
+- Build = explicit opt-in to script execution
+- Default build excludes `:malware` packages
+- Use `--allow-scripts="*"` only if you need legacy npm behavior (not recommended)
diff --git a/.cursor/rules/registries-and-auth.mdc b/.cursor/rules/registries-and-auth.mdc
@@ -0,0 +1,61 @@
+---
+description: Multi-registry support and authentication system
+globs: src/registry-client/src/*,src/keychain/src/*,src/cli-sdk/src/commands/login.ts,src/cli-sdk/src/commands/logout.ts,src/cli-sdk/src/commands/token.ts
+alwaysApply: false
+---
+# Registries & Authentication
+
+## Registry Types
+
+1. **Default**: `--registry=<url>` (default: `https://registry.npmjs.org/`)
+2. **Named aliases**: `--registries=<name>=<url>` → use as `name:pkg@ver` in dependencies
+3. **Scope registries**: `--scope-registries=@scope=<url>` → `@scope/*` auto-routes
+4. **Built-in aliases**: `npm:` (public npm), `jsr:` (jsr.io), `gh:` (GitHub packages)
+
+## Registry Consistency
+
+Child deps inherit parent's registry by default. If `foo` comes from registry X, its dep `bar@1.x` also resolves from X — prevents accidental cross-registry resolution.
+
+## Config (`vlt.json`)
+
+```json
+{
+  "registry": "https://registry.npmjs.org/",
+  "registries": { "internal": "https://npm.internal.co/" },
+  "scope-registries": { "@myco": "https://npm.myco.com/" },
+  "jsr-registries": { "jsr": "https://npm.jsr.io/" }
+}
+```
+
+## Authentication
+
+### Interactive
+
+```bash
+vlt login                                    # default registry (npm web login)
+vlt login --registry=https://custom.reg/     # custom registry
+vlt logout                                   # remove + destroy token
+vlt token add                                # paste bearer token
+vlt token rm                                 # remove from local keychain only
+```
+
+### CI / Headless
+
+Env vars only (never in config files for security):
+- `VLT_TOKEN` — token for default registry
+- `VLT_TOKEN_https_my_registry_com` — replace non-alphanumeric chars with `_`
+- `VLT_OTP` — one-time password for MFA
+
+### Identities
+
+Separate credential sets. Switch via `vlt config set identity=corp` or in `vlt.json`:
+```json
+{ "identity": "corp" }
+```
+
+Tokens stored in XDG data dir: `vlt/auth/${identity}/keychain.json`
+
+### Key Modules
+
+- `src/registry-client/` — HTTP client for registry API
+- `src/keychain/` — secure token storage (`@vltpkg/keychain`)
diff --git a/.cursor/rules/security-archive.mdc b/.cursor/rules/security-archive.mdc
@@ -0,0 +1,63 @@
+---
+description: Socket.dev security data integration and security selectors
+globs: src/security-archive/src/*,src/security-archive/test/*,src/query/src/pseudo/*
+alwaysApply: false
+---
+# Security Archive (`@vltpkg/security-archive`)
+
+Fetches, caches, and serves Socket.dev security data for the query system.
+
+## Architecture
+
+- `src/security-archive/src/index.ts` — `SecurityArchive` class (extends `LRUCache<DepID, PackageReportData>`)
+- Uses Socket API v0 (`https://api.socket.dev/v0/purl?alerts=true`) with public API token
+- Stores in SQLite DB (XDG data dir) with TTL-based expiration
+- Only supports `https://registry.npmjs.org/` packages (via `targetSecurityRegistry`)
+
+## Data Flow
+
+1. Query uses a security pseudo-selector (`:malware`, `:cve`, etc.)
+2. `SecurityArchive` is instantiated and passed to query engine via `ParserState.securityArchive`
+3. Archive fetches reports for queried DepIDs from Socket API (batched POST)
+4. Results cached in LRU + SQLite for future queries
+5. Pseudo-selector implementation checks `PackageReportData` for matches
+
+## PackageReportData
+
+```typescript
+type PackageReportData = {
+  score?: { overall, license, maintenance, quality, supplyChain, vulnerability }
+  alerts?: Array<{ type: string, severity: string, ... }>
+  license?: { text: string }
+  published?: string  // ISO date
+  deprecated?: boolean
+}
+```
+
+## Security Pseudo-Selectors (in `src/query/src/pseudo/`)
+
+**Malware/threats**: `:malware`, `:malware(critical|high|medium|low)`, `:obfuscated`, `:eval`, `:shell`, `:scripts`
+
+**Vulnerabilities**: `:cve(CVE-ID)`, `:cwe(CWE-ID)`, `:severity(level)`, `:deprecated`
+
+**Behavioral**: `:fs`, `:network`, `:env`, `:native`, `:dynamic`, `:debug`, `:entropic`, `:minified`
+
+**Trust**: `:abandoned`, `:confused`, `:unmaintained`, `:unstable`, `:unknown`, `:unpopular`, `:trivial`, `:squat(type)`
+
+**Scoring**: `:score(rate, kind?)`, `:license(type)`, `:published(date)`
+
+**Meta**: `:scanned` (has security data)
+
+## CLI Usage
+
+```bash
+vlt query ':malware'                    # medium+ severity
+vlt query ':malware' --expect-results=0 # CI gate
+vlt query ':cve(CVE-2023-1234)'
+vlt query ':score("<0.5")'
+vlt build --target=':scripts:not(:malware)'  # default build target
+```
+
+## Docs
+
+User-facing: `www/docs/src/content/docs/cli/security.mdx`, `cli/selectors.mdx` (Security section)
diff --git a/.cursor/rules/smoke-tests.mdc b/.cursor/rules/smoke-tests.mdc
@@ -0,0 +1,80 @@
+---
+description: End-to-end smoke tests for compiled CLI binary
+globs: infra/smoke-test/test/*,infra/smoke-test/test/fixtures/*
+alwaysApply: false
+---
+# Smoke Tests (`infra/smoke-test/`)
+
+Integration tests running the actual CLI binary against real scenarios.
+
+## Running
+
+```bash
+cd infra/smoke-test
+pnpm test -Rtap --disable-coverage          # all tests
+pnpm test -Rtap --disable-coverage test/install.ts  # single test
+```
+
+Filter variants via env: `SMOKE_TEST_VARIANTS=Source,Bundle`
+
+## Variants
+
+Tests run against multiple CLI build variants: `Source` (dev), `Bundle` (bundled), `Compile` (compiled). Results are compared across variants for consistency.
+
+## Test Pattern
+
+```typescript
+import { runMultiple, defaultVariants } from './fixtures/run.ts'
+
+t.test('my test', async t => {
+  const result = await runMultiple(t, ['install'], {
+    packageJson: { name: 'test', dependencies: { foo: '^1' } },
+    project: { 'node_modules': {} },  // fixture files
+    test: async ({ t, stdout, status, run }) => {
+      t.equal(status, 0)
+      // run followup commands in same testdir:
+      const r2 = await run(['query', ':root > *'])
+      t.matchSnapshot(r2.stdout)
+    },
+  })
+})
+```
+
+## Key APIs (`test/fixtures/run.ts`)
+
+- `runMultiple(t, args?, options?)` — run across all variants, compare results
+- `runVariant(variant, t, args?, options?)` — run single variant
+- `source(t, args?, options?)`, `bundle(...)`, `compile(...)` — individual variant shortcuts
+
+### CommandOptions
+
+```typescript
+type CommandOptions = {
+  packageJson?: boolean | Record<string, unknown>  // auto-creates package.json
+  project?: FixtureDir     // files in project dir
+  config?: FixtureDir      // XDG config dir
+  cache?: FixtureDir       // XDG cache dir
+  env?: NodeJS.ProcessEnv  // extra env vars
+  tty?: boolean            // use node-pty for TTY simulation
+  timeout?: number
+  cleanOutput?: (output: string) => string
+}
+```
+
+### CommandResult
+
+```typescript
+type CommandResult = {
+  status: number | null, signal: string | null,
+  stdout: string, stderr: string, output: string,
+  dirs: Record<CommandFixtureDirectory, string>  // testdir paths
+}
+```
+
+## Isolation
+
+Each test gets isolated `testdir` with separate `root/project/config/cache/data/state/runtime` dirs. `HOME`/`XDG_*` env vars locked to testdir to prevent config leakage.
+
+## Existing Tests
+
+`test/install.ts`, `test/pkg.ts`, `test/version.ts`, `test/cache-unzip.ts`, `test/postinstall.ts`, `test/rollback-remove.ts`
diff --git a/.cursor/rules/spec-parsing.mdc b/.cursor/rules/spec-parsing.mdc
@@ -0,0 +1,70 @@
+---
+description: Package specifier parsing types and protocols
+globs: src/spec/src/*,src/spec/test/*
+alwaysApply: false
+---
+# Package Specifier Parsing (`@vltpkg/spec`)
+
+Parses dependency specifiers into typed `Spec` objects. Used throughout the graph system.
+
+## Spec Types (`SpecType`)
+
+- `registry` — `express@^1.0.0`, `npm:react@18`, `jsr:@am/foo@1`, `registry:URL#name@ver`
+- `git` — `github:user/repo#semver:^1`, `git+ssh://...#branch`
+- `file` — `file:./local-pkg`, `./my-lib`
+- `remote` — `https://example.com/pkg.tgz`
+- `workspace` — `workspace:*`, `workspace:../path`
+
+## Key Properties
+
+- `name` — package name
+- `bareSpec` — raw specifier string (e.g., `^1.0.0`)
+- `type` — one of the SpecTypes above
+- `final` — resolved Spec after alias/subspec unwrapping
+- `registry` — registry URL (for registry type)
+- `namedRegistry` — alias name (e.g., `npm`, `jsr`, `gh`)
+- `scopeRegistry` — URL from scope-registries config
+- `subspec` — inner Spec for aliases (`alias@npm:pkg@ver` → subspec is the npm spec)
+- `overridden` — true if spec was swapped by a graph modifier
+- `range` — parsed semver Range (if applicable)
+- `gitRemote`, `gitSelector`, `namedGitHost`, `namedGitHostPath` — git fields
+- `remoteURL` — for remote type
+- `catalog`, `catalogName` — catalog protocol fields
+
+## Usage
+
+```typescript
+import { Spec } from '@vltpkg/spec'
+const s = Spec.parse('react', '^18.0.0', specOptions)
+// s.type === 'registry', s.name === 'react', s.bareSpec === '^18.0.0'
+```
+
+## SpecOptions
+
+```typescript
+type SpecOptions = {
+  registry?: string              // default: 'https://registry.npmjs.org/'
+  registries?: Record<string, string>  // named registries (npm, gh, custom)
+  'jsr-registries'?: Record<string, string>
+  'scope-registries'?: Record<string, string>
+  'git-hosts'?: Record<string, string>  // template: $1/$2/$committish
+  'git-host-archives'?: Record<string, string>
+  catalog?: Record<string, string>
+  catalogs?: Record<string, Record<string, string>>
+}
+```
+
+## Defaults
+
+```typescript
+defaultRegistry = 'https://registry.npmjs.org/'
+defaultRegistries = { npm: defaultRegistry, gh: 'https://npm.pkg.github.com/' }
+defaultJsrRegistries = { jsr: 'https://npm.jsr.io/' }
+defaultScopeRegistries = { '@jsr': 'https://npm.jsr.io/' }
+```
+
+## Architecture
+
+- `src/spec/src/browser.ts` — core `Spec` class (browser-compatible, no node APIs)
+- `src/spec/src/index.ts` — Node.js wrapper adding `inspect()` and path resolution
+- `src/spec/src/types.ts` — type definitions
diff --git a/.cursor/rules/vlt-json-config.mdc b/.cursor/rules/vlt-json-config.mdc
@@ -0,0 +1,50 @@
+---
+description: vlt.json configuration file schema and precedence
+globs: src/vlt-json/src/*,src/vlt-json/test/*,vlt.json
+alwaysApply: false
+---
+# vlt.json Configuration
+
+Central project config file. Also used for workspaces, modifiers, catalogs, registries.
+
+## Config Precedence
+
+CLI args → project `vlt.json` → user `vlt.json` (XDG config dir) → defaults. Object values merge; set `null` to remove. Command-specific overrides via `command.{name}` nesting.
+
+## Top-Level Fields
+
+```json
+{
+  "workspaces": "packages/*",
+  "config": { "registry": "...", "tag": "latest" },
+  "modifiers": { "#react": "^19" },
+  "catalog": { "typescript": "^5.0.0" },
+  "catalogs": { "testing": { "vitest": "^1.0.0" } },
+  "registries": { "custom": "https://..." },
+  "scope-registries": { "@myco": "https://..." },
+  "jsr-registries": { "jsr": "https://npm.jsr.io/" },
+  "git-hosts": { "github": "git+ssh://..." },
+  "git-host-archives": { "github": "https://..." },
+  "identity": "corp",
+  "command": { "build": { "target": ":scripts:not(:malware)" } }
+}
+```
+
+## Module: `@vltpkg/vlt-json` (`src/vlt-json/src/index.ts`)
+
+**Types**: `WhichConfig = 'user' | 'project'`, `Validator<T> = (x: unknown, file: string) => asserts x is T`
+
+**Functions:**
+- `find(which?, cwd?)` — walks up from cwd looking for `vlt.json`; user config from XDG
+- `load<T>(field, validator, which?)` — reads field, validates, caches
+- `save(field, value, which?)` — writes field, checks mtime for concurrent modifications
+- `unload(which?)` — clears all caches (`datas`, `mtimes`, `paths`, `lstatCache`)
+- `reload(field, which?)` — unload + load
+
+**Caching**: module-level caches for parsed data, mtimes, paths, lstat results. Must `unload()` to get fresh reads. See `@config-reload-jackspeak-issues.mdc`.
+
+**JSON formatting**: preserves indentation/newlines from original file via `polite-json` symbols (`kIndent`, `kNewline`).
+
+## User Config Location
+
+`new XDG('vlt').config('vlt.json')` — platform-specific XDG config dir.
diff --git a/.cursor/rules/vlx.mdc b/.cursor/rules/vlx.mdc
@@ -0,0 +1,68 @@
+---
+description: vlt exec / exec-local / exec-cache commands and @vltpkg/vlx
+globs: src/cli-sdk/src/commands/exec.ts,src/cli-sdk/src/commands/exec-local.ts,src/cli-sdk/src/commands/exec-cache.ts,src/vlx/src/*.ts,www/docs/src/content/docs/cli/commands/exec*.mdx
+alwaysApply: false
+---
+# Exec Commands & vlx
+
+## `vlt exec` (alias: `x`)
+
+Runs a command from a package, installing into XDG data dir if needed. **Never modifies local `node_modules`.**
+
+Resolution order:
+1. If `--package=<pkg>` set → use that package
+2. If arg0 found in local `node_modules/.bin` → run it (no install)
+3. Otherwise treat arg0 as package spec → install to exec cache → run default bin
+
+Default bin inference: single `bin` entry, or `bin` matching package name (after `/` for scoped).
+
+```bash
+vlt exec eslint src/            # local or install + run
+vlt exec --package=typescript@5 tsc   # explicit package
+vlt exec                        # no args → interactive shell with local bins in PATH
+```
+
+## `vlt exec-local` (alias: `xl`)
+
+Runs command with local `node_modules/.bin` prepended to PATH. No remote installs. No args → spawns interactive shell.
+
+## `vlt exec-cache` (alias: `xc`)
+
+Manage the exec cache (XDG data dir installations).
+
+| Subcommand | Description |
+|------------|-------------|
+| `ls` | List cached packages (filter by name or key) |
+| `info <key>` | Extended info about a cached install |
+| `install <spec>...` | Pre-install packages into exec cache |
+| `delete [key...]` | Remove cached packages (all if no args) |
+
+## `@vltpkg/vlx` Module (`src/vlx/src/`)
+
+Entry point re-exports:
+
+- `vlx.resolve(positionals, options, promptFn?)` → `string | undefined` — core resolution logic: find local bin → find local package → install to cache → infer default executable. Returns `undefined` for interactive shell.
+- `vlx.install(spec, options, promptFn?)` → `VlxInfo` — install to XDG exec cache
+- `vlx.list()` → cached package list
+- `vlx.info(key)` → `VlxInfo` for a cached install
+- `vlx.delete(keys)` — remove from cache
+
+### Key Types
+
+```typescript
+type VlxInfo = {
+  name: string, version?: string,
+  path: string,      // synthetic project dir (cache) or projectRoot (local)
+  resolved: string,  // registry resolution or file URL for local
+  arg0?: string,     // inferred default bin path
+  integrity?: Integrity, signatures?: Resolution['signatures']
+}
+```
+
+### Internal Helpers
+
+- `findExecutable(arg0, projectRoot)` — searches `node_modules/.bin`
+- `findPackage(name, projectRoot, packageJson)` — checks local install satisfies
+- `inferDefaultExecutable(manifest)` — picks bin from manifest
+- `inferName(spec)` — package name from spec
+- `doPrompt(promptFn, spec, path, resolution)` — confirmation before install
diff --git a/.cursor/rules/workspaces.mdc b/.cursor/rules/workspaces.mdc
@@ -0,0 +1,76 @@
+---
+description: Workspace configuration, filtering, and monorepo operations
+globs: src/workspaces/src/index.ts,src/cli-sdk/src/index.ts,src/cli-sdk/src/exec-command.ts,www/docs/src/content/docs/cli/workspaces.mdx
+alwaysApply: false
+---
+# Workspaces (`@vltpkg/workspaces`)
+
+## vlt.json `workspaces` Config Shapes
+
+All canonicalized to `WorkspaceConfigObject = Record<string, string[]>` via `asWSConfig()`:
+
+```typescript
+// String → { packages: ["src/*"] }
+"workspaces": "src/*"
+
+// Array → { packages: ["src/*", "www/*"] }
+"workspaces": ["src/*", "www/*"]
+
+// Object (named groups) → kept as-is, values normalized to arrays
+"workspaces": {
+  "apps": "apps/*",           // → ["apps/*"]
+  "utils": ["utils/*", "www/utils"]  // kept
+}
+```
+
+A workspace can belong to multiple groups. Glob patterns matched via `globSync`.
+
+## CLI Flags
+
+- `-w<path> --workspace=<path>` — filter by path/glob (can repeat). Implies `--recursive`
+- `--workspace-group=<name>` — filter by group name (can repeat). Implies `--recursive`
+- `-r --recursive` — run across all workspaces. No effect in non-monorepo projects
+- `-b --bail` / `-B --no-bail` — stop/continue on failure during recursive operations
+
+## Workspace Inference
+
+`cd` into a workspace dir → vlt auto-targets that workspace for install/run/etc. For linked folders (`file:` protocol), the folder must already be in the dependency chain for `vlt install`/`vlt uninstall` to work.
+
+## Monorepo Class
+
+```typescript
+Monorepo.maybeLoad(projectRoot, options?)  // undefined if no workspaces config
+Monorepo.load(projectRoot, options?)       // throws if not monorepo
+
+monorepo.load(query?)        // load workspaces, optionally filtered by paths/groups
+monorepo.get(nameOrPath)     // lookup by name, relative path, or fullpath
+monorepo.filter({ workspace, 'workspace-group' })  // yields matching Workspaces in topo order
+monorepo.run(operation)      // async operation over workspaces in dependency order
+monorepo.runSync(operation)  // sync variant
+monorepo.group(name)         // Set<Workspace> for a group
+monorepo.getDeps(ws)         // workspace: deps found in loaded set
+```
+
+Iteration yields workspaces in **topological dependency order** via `graphRun`.
+
+## Workspace Class
+
+```typescript
+class Workspace {
+  id: DepID             // joinDepIDTuple(['workspace', path])
+  path: string          // relative path (e.g., 'src/semver')
+  fullpath: string      // absolute path
+  name: string          // manifest.name ?? path
+  manifest: NormalizedManifest
+  groups: string[]      // group names this workspace belongs to
+  keys: string[]        // [name, path, fullpath] for matching
+}
+```
+
+## Filter Behavior (`monorepo.filter()`)
+
+Checks in order: group name match → direct name/path match → glob pattern match against `ws.keys`. Yields in topological order.
+
+## `vlt init -w <path>`
+
+Creates workspace folder + `package.json`, adds to `vlt.json` workspaces config.
PATCH

echo "Gold patch applied."
