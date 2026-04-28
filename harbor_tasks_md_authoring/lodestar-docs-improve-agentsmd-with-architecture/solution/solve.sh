#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lodestar

# Idempotency guard
if grep -qF "5. Reference the [Beacon APIs spec](https://github.com/ethereum/beacon-APIs) for" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -53,6 +53,9 @@ pnpm install
 # Build all packages
 pnpm build
 
+# Build a specific package (faster iteration)
+pnpm --filter @lodestar/beacon-node build
+
 # Run linter (biome)
 pnpm lint
 
@@ -62,15 +65,17 @@ pnpm lint:fix
 # Type check all packages
 pnpm check-types
 
+# Type check a specific package
+pnpm --filter @lodestar/beacon-node check-types
+
 # Run unit tests (fast, minimal preset)
 pnpm test:unit
 
-# Run specific test file (faster - run from package directory)
-cd packages/beacon-node
-pnpm vitest run test/unit/path/to/test.test.ts
+# Run specific test file with project filter
+pnpm vitest run --project unit test/unit/path/to/test.test.ts
 
 # Run tests matching a pattern
-pnpm vitest run -t "pattern"
+pnpm vitest run --project unit -t "pattern"
 
 # Run spec tests (requires downloading first)
 pnpm download-spec-tests
@@ -81,6 +86,13 @@ pnpm test:spec
 pnpm test:e2e
 ```
 
+**Tip:** For faster iteration, run tests from the specific package directory:
+
+```bash
+cd packages/beacon-node
+pnpm vitest run test/unit/chain/validation/block.test.ts
+```
+
 ## Code style
 
 Lodestar uses [Biome](https://biomejs.dev/) for linting and formatting.
@@ -94,6 +106,7 @@ Lodestar uses [Biome](https://biomejs.dev/) for linting and formatting.
 - **Types**: All functions must have explicit parameter and return types
 - **No `any`**: Avoid TypeScript `any` type
 - **Private fields**: No underscore prefix (use `private dirty`, not `private _dirty`)
+- **Named exports only**: No default exports
 
 ### Import organization
 
@@ -126,6 +139,91 @@ Metrics are critical for production monitoring:
 - Do NOT suffix code variables with units (no `Sec` suffix)
 - Time-based metrics must use seconds
 
+## Architecture patterns
+
+### Fork-aware code
+
+Code that varies by fork uses fork guards and type narrowing:
+
+```typescript
+import {isForkPostElectra, isForkPostFulu} from "@lodestar/params";
+
+// Check fork before accessing fork-specific fields
+if (isForkPostElectra(fork)) {
+  // electra and later forks
+}
+```
+
+The fork progression is: `phase0` → `altair` → `bellatrix` → `capella` →
+`deneb` → `electra` → `fulu` → `gloas`.
+
+### Configuration
+
+`ChainForkConfig` combines base chain config with computed fork information:
+
+```typescript
+// Access config values
+config.SLOTS_PER_EPOCH       // from params
+config.getForkName(slot)      // computed fork for a slot
+config.getForkTypes(fork)     // SSZ types for a fork
+```
+
+`@lodestar/params` holds constants (`SLOTS_PER_EPOCH`, etc.).
+`@lodestar/config` holds runtime chain configuration.
+
+### State access
+
+- Get current state via `chain.getHeadState()` — returns a tree-backed state
+- **Never hold references to old states** — they consume memory and can go stale
+- For read-only access, use the state directly; for mutations, use `state.clone()`
+- Beacon state is tree-backed (persistent data structure), making cloning cheap
+
+### SSZ types
+
+Types use `@chainsafe/ssz` and come in two forms:
+
+- **Value types**: Plain JS objects. Easy to work with, higher memory usage.
+- **View/ViewDU types**: Tree-backed. Memory-efficient, used for beacon state.
+
+```typescript
+// Type definition
+const MyContainer = new ContainerType({
+  field1: UintNumberType,
+  field2: RootType,
+}, {typeName: "MyContainer"});
+
+// Value usage
+const value = MyContainer.defaultValue();
+value.field1 = 42;
+
+// View usage (tree-backed)
+const view = MyContainer.toViewDU(value);
+view.field1 = 42;
+view.commit();
+```
+
+### Fork choice
+
+The fork choice store uses proto-array for efficient head computation:
+
+- `getHead()` returns a **cached** `ProtoBlock` — may be stale after mutations
+- After modifying proto-array node state (e.g., execution status), call
+  `recomputeForkChoiceHead()` to refresh the cache
+- This applies to any code that modifies proto-array outside normal block import
+
+### Logging
+
+Use structured logging with metadata objects:
+
+```typescript
+this.logger.debug("Processing block", {slot, root: toRootHex(root)});
+this.logger.warn("Peer disconnected", {peerId: peer.toString(), reason});
+```
+
+- Prefer structured fields over string concatenation
+- Use appropriate levels: `error` > `warn` > `info` > `verbose` > `debug` > `trace`
+- Include relevant context (slot, root, peer) as structured fields
+
 ## Testing guidelines
 
 ### Test organization
@@ -157,11 +255,18 @@ for (const block of blocks) {
 
 ### Running specific tests
 
-For faster iteration, run tests from the package directory:
+Use vitest project filters for targeted test runs:
 
 ```bash
+# Unit tests only (from repo root)
+pnpm vitest run --project unit test/unit/chain/validation/block.test.ts
+
+# With pattern matching
+pnpm vitest run --project unit -t "should reject"
+
+# From package directory (no project filter needed)
 cd packages/beacon-node
-pnpm vitest run test/unit/chain/validation/block.test.ts -t "should reject"
+pnpm vitest run test/unit/chain/validation/block.test.ts
 ```
 
 For spec tests with minimal preset (faster):
@@ -215,7 +320,8 @@ refactor(reqresp)!: support byte based handlers
 - Keep PRs as drafts until ready for review
 - Don't force push after review starts (use incremental commits)
 - Close stale PRs rather than letting them sit
-- Respond to review feedback promptly
+- Respond to review feedback promptly — reply to every comment, including bot reviewers
+- When updating based on feedback, respond in-thread to acknowledge
 
 ## Common tasks
 
@@ -241,6 +347,14 @@ refactor(reqresp)!: support byte based handlers
 3. The type will be automatically aggregated (no central `sszTypes` to modify)
 4. Run `pnpm check-types` to verify
 
+### Adding a new API endpoint
+
+1. Define the route in `packages/api/src/beacon/routes/<resource>.ts`
+2. Add request/response SSZ codecs alongside the route definition
+3. Implement the server handler in `packages/beacon-node/src/api/impl/beacon/<resource>.ts`
+4. Add tests for the new endpoint
+5. Reference the [Beacon APIs spec](https://github.com/ethereum/beacon-APIs) for the endpoint contract
+
 ## Style learnings from reviews
 
 ### Prefer inline logic over helper functions
@@ -348,3 +462,18 @@ Edit source files in `packages/*/src/` instead.
 
 The `specrefs/` directory contains pinned consensus spec versions.
 When implementing spec changes, reference the exact spec version.
+
+## Common pitfalls
+
+- **Forgetting `pnpm lint` before pushing**: Biome enforces formatting. Always
+  run it before committing. CI will catch it, but it wastes a round-trip.
+- **Editing `lib/` instead of `src/`**: Files in `packages/*/lib/` are build
+  outputs. Always edit in `packages/*/src/`.
+- **Stale fork choice head**: After modifying proto-array execution status,
+  the cached head from `getHead()` is stale. Call `recomputeForkChoiceHead()`.
+- **Holding state references**: Beacon state objects are large. Don't store
+  references beyond their immediate use — let them be garbage collected.
+- **Missing `.js` extension**: Relative imports must use `.js` even though
+  source files are `.ts`. This is required for Node.js ESM resolution.
+- **Force pushing after review**: Never force push once a reviewer has started.
+  Use incremental commits — reviewers track changes between reviews.
PATCH

echo "Gold patch applied."
