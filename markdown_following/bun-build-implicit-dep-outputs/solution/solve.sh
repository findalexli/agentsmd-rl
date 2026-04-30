#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied
if grep -q 'implicit-dep signal for PCH/cc/no-PCH cxx' scripts/build/bun.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/scripts/build/CLAUDE.md b/scripts/build/CLAUDE.md
index de6b5b677ef..fc9270313fe 100644
--- a/scripts/build/CLAUDE.md
+++ b/scripts/build/CLAUDE.md
@@ -49,7 +49,7 @@ rule cc
   depfile = $out.d
   deps = gcc

-build obj/src/foo.c.o: cc ../../src/foo.c | codegen/generated.h || ../../vendor/zstd/.ref
+build obj/src/foo.c.o: cc ../../src/foo.c | deps/zstd/libzstd.a || codegen/generated.h
   cflags = -O2 -I...
 ```

@@ -74,12 +74,12 @@ All rules and edges are written to `build/<profile>/build.ninja` by `n.write()`
 Edge dependency types:

 - **explicit inputs** (`$in`) — listed on the build line, passed to the command
-- **implicit inputs** (`| foo.h`) — tracked for rebuild but not in `$in`. Use for files the command reads that aren't on its command line (generated headers, PCH)
-- **order-only inputs** (`|| stamp`) — must exist before this edge runs, but mtime doesn't trigger rebuild. Use for "X must be fetched/generated first, but the compiler's `.d` depfile will track which files I actually read"
+- **implicit inputs** (`| foo`) — tracked for rebuild but not in `$in`. Use for the PCH, dep lib outputs (invalidation signal for their headers), or a per-file generated header this source is known to read
+- **order-only inputs** (`|| stamp`) — must exist before this edge runs, but mtime doesn't trigger rebuild. Use for bulk codegen headers: "must be generated first, but the compiler's `.d` depfile will track which ones I actually read"

 **`restat = 1`** — after the command runs, re-stat outputs; if mtime didn't change, prune downstream. Critical for idempotent steps (fetch no-op, codegen unchanged).

-**`depfile`** — compiler writes `foo.o.d` listing every `#include`d header. Ninja reads it on the next build to know which headers this `.o` depends on. This is why cxx uses order-only for dep outputs: the depfile gives exact per-file header deps on build 2+; order-only just ensures headers exist for build 1.
+**`depfile`** — compiler writes `foo.o.d` listing every `#include`d header. Ninja reads it on the next build to know which headers this `.o` depends on. Codegen headers are order-only for this reason: they're declared outputs with restat, the depfile gives exact per-file header deps on build 2+, and order-only just ensures they exist for build 1. Dep outputs (`lib*.a`) are a different story — PCH, cc, and no-PCH cxx use them as _implicit_ deps, because local sub-builds (e.g. WebKit) rewrite forwarding headers as undeclared side effects and order-only would lag one build behind (see Gotchas).

 ## Iterating on the build system

@@ -224,9 +224,7 @@ Why not auto-register in emit functions? Some rules are shared (`dep_configure`

 **Dep order in `allDeps` matters.** `fetchDeps: ["X"]` means X must come first (its `.ref` stamp node must exist). Link order matters too: static linking resolves left→right, providers after users.

-**PCH needs implicit dep on `depOutputs`**, not order-only. Local WebKit regenerates headers mid-build; order-only would let ninja think PCH is fresh while headers change under it → "file modified since PCH was built".
-
-**cxx needs order-only dep on `depOutputs`**, not implicit. Depfile tracks actual header deps. Implicit would recompile every `.c` when `libJavaScriptCore.a` changes — but `.c` files don't include JSC headers.
+**PCH, cc, and no-PCH cxx need implicit dep on `depOutputs`**, not order-only. Local WebKit's sub-build rewrites forwarding headers as an undeclared side effect (only `lib*.a` are declared outputs). Depfiles record those headers, but ninja stats them before the sub-build runs — order-only lags one build. The lib itself is the invalidation signal. Codegen headers stay order-only: they're declared outputs with restat, so depfile tracking is exact.

 **Windows `ReleaseFast` → `ReleaseSafe`** in `zig.ts`. Load-bearing since Bun 1.1; caught more crashes. Don't "fix" it.

diff --git a/scripts/build/bun.ts b/scripts/build/bun.ts
index e311f2c7ee0..24f43084554 100644
--- a/scripts/build/bun.ts
+++ b/scripts/build/bun.ts
@@ -168,7 +168,7 @@ export function emitBun(n: Ninja, cfg: Config, sources: Sources): BunOutput {
   // instead of a .a — we compile those alongside bun's own sources).
   const depLibs: string[] = [];
   const depIncludes: string[] = [];
-  const depOutputs: string[] = []; // PCH order-only-deps on these
+  const depOutputs: string[] = []; // implicit-dep signal for PCH/cc/no-PCH cxx
   for (const d of deps) {
     depLibs.push(...d.libs);
     depIncludes.push(...d.includes);
@@ -283,17 +283,23 @@ export function emitBun(n: Ninja, cfg: Config, sources: Sources): BunOutput {
   cxxSources.push(...codegen.bindgenV2Cpp);

   // All deps must be ready (headers extracted, libs built) before compile.
-  // ORDER-ONLY, not implicit: the compiler's .d depfile tracks ACTUAL header
-  // dependencies on subsequent builds. Order-only ensures first-build ordering;
-  // after that, touching libJavaScriptCore.a doesn't recompile every .c file
-  // (.c files don't include JSC headers — depfile knows this).
   //
-  // PCH is different: it has IMPLICIT deps on depOutputs because root.h
-  // transitively includes WebKit headers, and the PCH encodes those. If
-  // WebKit headers change (lib rebuilt), PCH must invalidate. The depfile
-  // mechanism doesn't work for PCH-invalidation because the .cpp's depfile
-  // says "depends on root.h.pch", not on what root.h.pch was built from.
-  const depOrderOnly = [...depOutputs, ...codegen.cppAll];
+  // depOutputs are IMPLICIT inputs, not order-only. A locally-built dep's
+  // sub-build (e.g. WebKit) rewrites forwarding headers as an undeclared side
+  // effect of the edge whose declared outputs are only lib*.a. Depfiles record
+  // those headers, but ninja stats them BEFORE the sub-build runs — so with
+  // order-only, any compile that #includes a dep header lags one build behind
+  // a dep rebuild (observed: asan-config.c / uv-posix-*.c → wtf/Compiler.h).
+  // Implicit deps on the libs make "dep rebuilt" itself the invalidation
+  // signal. Cost is negligible: if the libs changed you're relinking anyway.
+  //
+  // codegen.cppAll stays order-only: those headers ARE declared ninja outputs
+  // with restat, so depfile tracking is exact and doesn't lag.
+  //
+  // PCH also has implicit deps on depOutputs (see above). When PCH is enabled,
+  // cxx inherits the dep transitively via its implicit dep on the PCH, so we
+  // don't add it again.
+  const codegenOrderOnly = codegen.cppAll;

   // Compile all .cpp with PCH.
   const cxxObjects: string[] = [];
@@ -305,21 +311,25 @@ export function emitBun(n: Ninja, cfg: Config, sources: Sources): BunOutput {
     };
     if (pchOut !== undefined) {
       // PCH has implicit deps on depOutputs. cxx has implicit dep on PCH.
-      // Transitively: cxx waits for deps. No need for order-only here.
+      // Transitively: cxx waits for deps. No need to repeat them here.
       opts.pch = pchOut.pch;
       opts.pchHeader = pchOut.wrapperHeader;
     } else {
-      // No PCH (windows) — each cxx needs direct ordering on deps.
-      // Order-only: depfile tracks actual headers after first build.
-      opts.orderOnlyInputs = depOrderOnly;
+      // No PCH (windows) — each cxx needs the dep signal directly.
+      opts.implicitInputs = depOutputs;
+      opts.orderOnlyInputs = codegenOrderOnly;
     }
     cxxObjects.push(cxx(n, cfg, src, opts));
   }

-  // Compile all .c files. No PCH. Order-only on deps for first-build ordering.
+  // Compile all .c files. No PCH — dep signal applied directly.
   const cObjects: string[] = [];
   const compileC = (src: string): string => {
-    const obj = cc(n, cfg, src, { flags: cFlagsFull, orderOnlyInputs: depOrderOnly });
+    const obj = cc(n, cfg, src, {
+      flags: cFlagsFull,
+      implicitInputs: depOutputs,
+      orderOnlyInputs: codegenOrderOnly,
+    });
     cObjects.push(obj);
     return obj;
   };
diff --git a/scripts/build/compile.ts b/scripts/build/compile.ts
index 399c14f7807..f6390eea00d 100644
--- a/scripts/build/compile.ts
+++ b/scripts/build/compile.ts
@@ -143,19 +143,22 @@ export interface CompileOpts {
   /** Original header the PCH was built from (needed for clang-cl /Yu). */
   pchHeader?: string;
   /**
-   * Extra implicit deps. Use for generated headers this specific .cpp needs.
-   * E.g. ErrorCode.cpp depends on ErrorCode+List.h.
+   * Extra implicit deps. Use for generated headers this specific .cpp needs
+   * (e.g. ErrorCode.cpp depends on ErrorCode+List.h), and for dep outputs
+   * (lib*.a) — local sub-builds rewrite forwarding headers as undeclared
+   * side effects, so the lib is the invalidation signal; order-only would
+   * lag one build behind.
    */
   implicitInputs?: string[];
   /**
    * Order-only deps. Must exist before compile, but mtime not tracked.
    * The compiler's .d depfile tracks ACTUAL header dependencies on
-   * subsequent builds — order-only is for "dep libs/headers must be
-   * extracted before first compile attempts to #include them".
+   * subsequent builds — order-only is for "header must be generated
+   * before first compile attempts to #include it".
    *
-   * Prefer this over implicitInputs for dep outputs: if you touch
-   * libJavaScriptCore.a, you don't want every .c file to recompile
-   * (.c files don't include JSC headers). The depfile knows better.
+   * Use for codegen headers (declared ninja outputs with restat, so
+   * depfile tracking is exact). Dep outputs (lib*.a) go in
+   * implicitInputs instead — see above.
    */
   orderOnlyInputs?: string[];
   /** Job pool override. */

PATCH

echo "Patch applied successfully."
