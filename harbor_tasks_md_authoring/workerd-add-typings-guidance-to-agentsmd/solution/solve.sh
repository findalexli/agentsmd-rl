#!/usr/bin/env bash
set -euo pipefail

cd /workspace/workerd

# Idempotency guard
if grep -qF "- **NEVER** use generic names for top-level ambient types in `types/defines/` (e" "AGENTS.md" && grep -qF "- **Index signatures (`[key: string]: unknown`) need justification.** Only add t" "types/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -178,21 +178,21 @@ Be aware that workerd uses tcmalloc for memory allocation in the typical case. W
 
 ### Where to Look
 
-| Task                   | Location                                                      | Notes                                                          |
-| ---------------------- | ------------------------------------------------------------- | -------------------------------------------------------------- |
-| Add/modify JS API      | `src/workerd/api/`                                            | C++ with JSG macros; see `jsg/jsg.h` for binding system        |
-| Add Node.js compat     | `src/workerd/api/node/` (C++) + `src/node/` (TS)              | Dual-layer; register in `api/node/node.h` NODEJS_MODULES macro |
-| Add Cloudflare API     | `src/cloudflare/`                                             | TypeScript; mock in `internal/test/<product>/`                 |
-| Modify compat flags    | `src/workerd/io/compatibility-date.capnp`                     | ~1400 lines; annotations define flag names + enable dates      |
-| Add autogate           | `src/workerd/util/autogate.h` + `.c++`                        | Enum + string map; both must stay in sync                      |
-| Config schema          | `src/workerd/server/workerd.capnp`                            | Cap'n Proto; capability-based security                         |
-| Worker lifecycle       | `src/workerd/io/worker.{h,c++}`                               | Isolate, Script, Worker, Actor classes                         |
-| Request lifecycle      | `src/workerd/io/io-context.{h,c++}`                           | IoContext: the per-request god object                          |
-| Durable Object storage | `src/workerd/io/actor-cache.{h,c++}` + `actor-sqlite.{h,c++}` | LRU cache over RPC / SQLite-backed                             |
-| Streams implementation | `src/workerd/api/streams/`                                    | Has 842-line README; dual internal/standard impl               |
-| Bazel build rules      | `build/`                                                      | Custom `wd_*` macros; `wd_test.bzl` generates 3 test variants  |
-| TypeScript types       | `types/`                                                      | Extracted from C++ RTTI + hand-written `defines/*.d.ts`        |
-| V8 patches             | `patches/v8/`                                                 | 33 patches; see `docs/v8-updates.md`                           |
+| Task                   | Location                                                      | Notes                                                                                                        |
+| ---------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
+| Add/modify JS API      | `src/workerd/api/`                                            | C++ with JSG macros; see `jsg/jsg.h` for binding system                                                      |
+| Add Node.js compat     | `src/workerd/api/node/` (C++) + `src/node/` (TS)              | Dual-layer; register in `api/node/node.h` NODEJS_MODULES macro                                               |
+| Add Cloudflare API     | `src/cloudflare/`                                             | TypeScript; mock in `internal/test/<product>/`                                                               |
+| Modify compat flags    | `src/workerd/io/compatibility-date.capnp`                     | ~1400 lines; annotations define flag names + enable dates                                                    |
+| Add autogate           | `src/workerd/util/autogate.h` + `.c++`                        | Enum + string map; both must stay in sync                                                                    |
+| Config schema          | `src/workerd/server/workerd.capnp`                            | Cap'n Proto; capability-based security                                                                       |
+| Worker lifecycle       | `src/workerd/io/worker.{h,c++}`                               | Isolate, Script, Worker, Actor classes                                                                       |
+| Request lifecycle      | `src/workerd/io/io-context.{h,c++}`                           | IoContext: the per-request god object                                                                        |
+| Durable Object storage | `src/workerd/io/actor-cache.{h,c++}` + `actor-sqlite.{h,c++}` | LRU cache over RPC / SQLite-backed                                                                           |
+| Streams implementation | `src/workerd/api/streams/`                                    | Has 842-line README; dual internal/standard impl                                                             |
+| Bazel build rules      | `build/`                                                      | Custom `wd_*` macros; `wd_test.bzl` generates 3 test variants                                                |
+| TypeScript types       | `types/`                                                      | Extracted from C++ RTTI + hand-written `defines/*.d.ts`; see `types/AGENTS.md` for detailed typings guidance |
+| V8 patches             | `patches/v8/`                                                 | 33 patches; see `docs/v8-updates.md`                                                                         |
 
 ## Coding Conventions
 
@@ -255,6 +255,9 @@ C++ classes are exposed to JavaScript via JSG macros in `src/workerd/jsg/`. See
 - `Ref<T>` stored in C++ objects visible from JS heap **MUST** implement `visitForGc()`; C++ reference cycles are **NEVER** collected
 - SQLite `SQLITE_MISUSE` errors always throw (never suppressed); transactions disallowed in DO SQLite
 - Module evaluation **MUST NOT** be in an IoContext; async I/O is **FORBIDDEN** in global scope
+- **NEVER** use generic names for top-level ambient types in `types/defines/` (e.g., `Identity`, `Preview`, `Config`); always prefix with the product/feature name (e.g., `CloudflareAccessIdentity`, `TracePreviewInfo`, `AiSearchConfig`)
+- **NEVER** use bare `object` as a type in `types/defines/`; use a proper interface with known fields (optionally extending `Record<string, unknown>` for forward-compatibility)
+- **NEVER** edit `types/generated-snapshot/` directly; fix the source layer and run `just generate-types`
 
 ## Backward Compatibility
 
diff --git a/types/AGENTS.md b/types/AGENTS.md
@@ -23,3 +23,61 @@ Generates `@cloudflare/workers-types` `.d.ts` files from C++ RTTI (via `jsg/rtti
 | `generated-snapshot/` | Checked-in `latest/` + `experimental/` output; CI diff-checked                   |
 | `scripts/`            | `build-types.ts` (full generation), `build-worker.ts` (worker bundle)            |
 | `test/`               | Vitest specs for generator, transforms, print; type-check tests in `test/types/` |
+
+## ADDING OR UPDATING TYPES
+
+### Where type changes belong
+
+Types in this project come from three layers. Changes must be made in the correct layer:
+
+| Layer                    | Location                                           | When to use                                                                                                |
+| ------------------------ | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
+| **C++ RTTI**             | `src/workerd/api/*.h` (JSG macros)                 | Types derived from C++ classes — the generator extracts these automatically                                |
+| **`JSG_TS_OVERRIDE`**    | Same `.h` files, inside `JSG_RESOURCE_TYPE` blocks | When the auto-generated TS signature needs adjustment (e.g., conditional properties, union narrowing)      |
+| **Hand-written defines** | `types/defines/*.d.ts`                             | Types for APIs not expressible via C++ RTTI (Cloudflare product bindings like AI, D1, R2, Vectorize, etc.) |
+
+Do **not** edit files in `generated-snapshot/` directly — they are overwritten by `just generate-types`. If the generated output looks wrong, fix the source layer (C++ RTTI, `JSG_TS_OVERRIDE`, or `defines/`).
+
+### Naming conventions
+
+Types in `defines/*.d.ts` become **top-level ambient declarations** visible to every Worker project. Generic names will collide or confuse.
+
+- **Prefix types with the product or feature name.** For example: `D1Meta`, `AiSearchConfig`, `VectorizeVector` — not `Meta`, `Config`, or `Vector`.
+- **Follow the existing convention** for the relevant product. Check the existing `defines/` file for that product (e.g., `cf.d.ts` uses `IncomingRequestCfProperties*`, `d1.d.ts` uses `D1*`, `ai-search.d.ts` uses `AiSearch*`).
+- **When in doubt, be more specific.** A name like `TracePreviewInfo` is better than `Preview`. The cost of a verbose name is low; the cost of a naming collision in every user's project is high.
+
+### Interface design
+
+- **Never use bare `object` as a type.** `type Foo = object` prevents all property access without casting, providing no value to users. Use a proper interface with known fields instead.
+- **Use interfaces with known fields + index signature** for types where the shape is partially known but extensible. Follow the `IncomingRequestCfPropertiesBase` pattern:
+  ```typescript
+  interface CloudflareAccessIdentity extends Record<string, unknown> {
+    email?: string;
+    name?: string;
+    // ... other known fields
+  }
+  ```
+- **Index signatures (`[key: string]: unknown`) need justification.** Only add them when forward-compatibility is genuinely required (e.g., the API frequently adds new fields across releases). Document the reason in a JSDoc comment. Do not add index signatures by default.
+- **Add JSDoc comments** to interfaces and their fields, especially for types used in `defines/`. These comments appear in users' IDEs.
+
+### Snapshot regeneration
+
+After any change that affects types (C++ API changes, `JSG_TS_OVERRIDE` edits, `defines/` modifications), regenerate the snapshot:
+
+```shell
+just generate-types
+```
+
+CI will fail if `generated-snapshot/` does not match the generated output. Always commit the updated snapshot alongside your source changes.
+
+### Type tests
+
+Type-level tests live in `test/types/` (e.g., `test/types/rpc.ts`). These are compile-time checks — they verify that type expressions are accepted or rejected by the TypeScript compiler.
+
+- When adding new types or changing existing ones, add or update type tests to cover the new shapes.
+- Review type test changes carefully — a test that compiles successfully may still be asserting the wrong thing.
+
+### PR hygiene for type changes
+
+- **Do not include unrelated formatting changes** in PRs that modify types. If formatting needs fixing, do it in a separate commit or PR.
+- **Type changes in feature PRs need review** from someone familiar with the types system. The Wrangler team typically reviews type changes that affect `@cloudflare/workers-types`.
PATCH

echo "Gold patch applied."
