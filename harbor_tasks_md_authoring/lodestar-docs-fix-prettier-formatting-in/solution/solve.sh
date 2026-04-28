#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lodestar

# Idempotency guard
if grep -qF "- **Forgetting `pnpm docs:lint` after editing docs**: Markdown files are" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -163,9 +163,9 @@ The fork progression is: `phase0` → `altair` → `bellatrix` → `capella` →
 
 ```typescript
 // Access config values
-config.SLOTS_PER_EPOCH       // from params
-config.getForkName(slot)      // computed fork for a slot
-config.getForkTypes(fork)     // SSZ types for a fork
+config.SLOTS_PER_EPOCH; // from params
+config.getForkName(slot); // computed fork for a slot
+config.getForkTypes(fork); // SSZ types for a fork
 ```
 
 `@lodestar/params` holds constants (`SLOTS_PER_EPOCH`, etc.).
@@ -187,10 +187,13 @@ Types use `@chainsafe/ssz` and come in two forms:
 
 ```typescript
 // Type definition
-const MyContainer = new ContainerType({
-  field1: UintNumberType,
-  field2: RootType,
-}, {typeName: "MyContainer"});
+const MyContainer = new ContainerType(
+  {
+    field1: UintNum64,
+    field2: Root,
+  },
+  {typeName: "MyContainer"}
+);
 
 // Value usage
 const value = MyContainer.defaultValue();
@@ -467,6 +470,9 @@ When implementing spec changes, reference the exact spec version.
 
 - **Forgetting `pnpm lint` before pushing**: Biome enforces formatting. Always
   run it before committing. CI will catch it, but it wastes a round-trip.
+- **Forgetting `pnpm docs:lint` after editing docs**: Markdown files are
+  formatted by Prettier. Run `pnpm docs:lint` (or `pnpm docs:lint:fix` to
+  auto-fix) before pushing changes to `.md` files.
 - **Editing `lib/` instead of `src/`**: Files in `packages/*/lib/` are build
   outputs. Always edit in `packages/*/src/`.
 - **Stale fork choice head**: After modifying proto-array execution status,
PATCH

echo "Gold patch applied."
