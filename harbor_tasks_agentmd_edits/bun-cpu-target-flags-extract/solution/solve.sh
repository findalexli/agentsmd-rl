#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotency check: if already patched, exit
if grep -q 'computeCpuTargetFlags' scripts/build/flags.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/scripts/build/CLAUDE.md b/scripts/build/CLAUDE.md
index de6b5b677ef..618e0f8d9a3 100644
--- a/scripts/build/CLAUDE.md
+++ b/scripts/build/CLAUDE.md
@@ -119,7 +119,7 @@ Build flags must come before exec args. `bun bd --asan=off test foo.ts` works; `
 { flag: "-fno-foo", when: c => c.linux && c.release, desc: "why this flag" },
 ```

-Tables: `globalFlags` (bun + all deps), `bunOnlyFlags` (just bun), `linkFlags`, `stripFlags`. Use `lang: "cxx"` to restrict to C++.
+Tables: `cpuTargetFlags` (`-march`/`-mcpu`/`-mtune` — also forwarded to local WebKit via `computeCpuTargetFlags()`), `globalFlags` (bun + all deps), `bunOnlyFlags` (just bun), `linkFlags`, `stripFlags`. Use `lang: "cxx"` to restrict to C++.

 **Bump a dependency** — edit the `commit` in `scripts/build/deps/<name>.ts`. See `deps/README.md` for adding/removing deps.

@@ -179,7 +179,7 @@ Split CI modes: `zig-only` (zstd+codegen+zig), `cpp-only` (deps+codegen+compile
 | `config.ts`                    | `Config`/`PartialConfig`/`Toolchain`/`Host` types, `resolveConfig()`    |
 | `profiles.ts`                  | Named `PartialConfig` presets + `getProfile()`                          |
 | `tools.ts`                     | Tool discovery: `findTool()`, `resolveLlvmToolchain()`, version parsing |
-| `flags.ts`                     | Flat flag tables, `computeFlags()`, `computeDepFlags()`                 |
+| `flags.ts`                     | Flat flag tables, `computeFlags()`, `computeDepFlags()`, `computeCpuTargetFlags()` |
 | `ninja.ts`                     | `Ninja` class — the build-file writer                                   |
 | `rules.ts`                     | `registerAllRules()` — calls each module's `registerXxxRules()`         |
 | `compile.ts`                   | `cc`/`cxx`/`pch`/`link`/`ar` + `registerCompileRules()`                 |
diff --git a/scripts/build/deps/webkit.ts b/scripts/build/deps/webkit.ts
index bd204c95be9..533f4839519 100644
--- a/scripts/build/deps/webkit.ts
+++ b/scripts/build/deps/webkit.ts
@@ -26,10 +26,10 @@ export const WEBKIT_VERSION = "c2010c47d12c525d36adabe3a17b2eb6ec850960";
  *   `vendor/WebKit/WebKitBuild/`. Better: consistent, cleaned by `rm -rf
  *   build/`, separate per-profile.
  *
- * - Flags: WebKit's own cmake machinery sets compiler flags. We set
- *   `CMAKE_C_FLAGS: ""` in our args to clear the global dep flags
- *   (which would otherwise conflict). Dep args go LAST in source.ts,
- *   so they override.
+ * - Flags: WebKit's own cmake machinery sets -O/-g/sanitizer flags. We
+ *   override `CMAKE_C_FLAGS` to drop the global dep flags (which would
+ *   conflict) but DO forward -march/-mcpu + LTO/PGO, which WebKit never
+ *   sets. Dep args go LAST in source.ts, so they override.
  *
  * - Windows local mode: ICU built from source via preBuild hook
  *   (build-icu.ps1 → msbuild) before cmake configure. Output goes in
@@ -39,6 +39,7 @@ export const WEBKIT_VERSION = "c2010c47d12c525d36adabe3a17b2eb6ec850960";

 import { resolve } from "node:path";
 import type { Config } from "../config.ts";
+import { computeCpuTargetFlags } from "../flags.ts";
 import { slash } from "../shell.ts";
 import { type Dependency, type NestedCmakeBuild, type Source, depBuildDir, depSourceDir } from "../source.ts";

@@ -182,16 +183,20 @@ export const webkit: Dependency = {

     // Local: nested cmake, target=jsc.
     //
-    // CMAKE_C_FLAGS/CMAKE_CXX_FLAGS: clears the global dep flags source.ts
-    // would otherwise pass — WebKit's cmake sets its own -O/-march/etc.;
-    // ours would conflict. Dep args go LAST so they override. We DO forward
-    // LTO/PGO since WebKit's cmake doesn't set those itself.
+    // CMAKE_C_FLAGS/CMAKE_CXX_FLAGS: overrides the global dep flags source.ts
+    // would otherwise pass — WebKit's cmake sets its own -O/-g/sanitizer
+    // flags; ours would conflict. Dep args go LAST so they override. We DO
+    // forward:
+    //   - CPU target (-march/-mcpu): WebKit never sets this — without it,
+    //     local builds target generic x86-64 while bun + prebuilt WebKit
+    //     target haswell/nehalem.
+    //   - LTO/PGO: WebKit's cmake doesn't set those itself.
     //
     // Windows: ICU built from source via preBuild before cmake configure.
     // WebKit's cmake finds it via ICU_ROOT. On posix, system ICU is used
     // (macOS: Homebrew headers + system libs; Linux: libicu-dev) — cmake
     // auto-detects.
-    const optFlags: string[] = [];
+    const optFlags: string[] = computeCpuTargetFlags(cfg);
     if (cfg.lto) optFlags.push("-flto=full");
     if (cfg.pgoGenerate) optFlags.push(`-fprofile-generate=${cfg.pgoGenerate}`);
     if (cfg.pgoUse) {
diff --git a/scripts/build/flags.ts b/scripts/build/flags.ts
index 2cf683218bb..a427d170e89 100644
--- a/scripts/build/flags.ts
+++ b/scripts/build/flags.ts
@@ -29,26 +29,18 @@ export interface Flag {
 }

 // ═══════════════════════════════════════════════════════════════════════════
-// GLOBAL COMPILER FLAGS
-//   Applied to BOTH bun's own sources AND forwarded to vendored deps
-//   via -DCMAKE_C_FLAGS / -DCMAKE_CXX_FLAGS.
+// CPU TARGET FLAGS
+//   -march/-mcpu/-mtune. Split out so deps that manage their own optimization
+//   and sanitizer flags (WebKit) can still inherit the target arch without
+//   the rest of globalFlags.
 // ═══════════════════════════════════════════════════════════════════════════

-export const globalFlags: Flag[] = [
-  // ─── CPU target ───
+export const cpuTargetFlags: Flag[] = [
   {
     flag: "-mcpu=apple-m1",
     when: c => c.darwin && c.arm64,
     desc: "Target Apple M1 (works on all Apple Silicon)",
   },
-  {
-    // CMake auto-added these via CMAKE_OSX_DEPLOYMENT_TARGET/CMAKE_OSX_SYSROOT;
-    // we must add explicitly. Without this, clang/ld64 default to the host SDK
-    // version — CI builds get minos=15.0, breaking macOS 13/14 users at launch.
-    flag: c => [`-mmacosx-version-min=${c.osxDeploymentTarget!}`, "-isysroot", c.osxSysroot!],
-    when: c => c.darwin && c.osxDeploymentTarget !== undefined && c.osxSysroot !== undefined,
-    desc: "macOS deployment target + SDK (sets LC_BUILD_VERSION minos)",
-  },
   {
     flag: ["-march=armv8-a+crc", "-mtune=ampere1"],
     when: c => c.linux && c.arm64,
@@ -69,6 +61,25 @@ export const globalFlags: Flag[] = [
     when: c => c.x64 && !c.baseline,
     desc: "x64 default: Haswell (2013) — AVX2, BMI2 available",
   },
+];
+
+// ═══════════════════════════════════════════════════════════════════════════
+// GLOBAL COMPILER FLAGS
+//   Applied to BOTH bun's own sources AND forwarded to vendored deps
+//   via -DCMAKE_C_FLAGS / -DCMAKE_CXX_FLAGS.
+// ═══════════════════════════════════════════════════════════════════════════
+
+export const globalFlags: Flag[] = [
+  // ─── CPU target ───
+  ...cpuTargetFlags,
+  {
+    // CMake auto-added these via CMAKE_OSX_DEPLOYMENT_TARGET/CMAKE_OSX_SYSROOT;
+    // we must add explicitly. Without this, clang/ld64 default to the host SDK
+    // version — CI builds get minos=15.0, breaking macOS 13/14 users at launch.
+    flag: c => [`-mmacosx-version-min=${c.osxDeploymentTarget!}`, "-isysroot", c.osxSysroot!],
+    when: c => c.darwin && c.osxDeploymentTarget !== undefined && c.osxSysroot !== undefined,
+    desc: "macOS deployment target + SDK (sets LC_BUILD_VERSION minos)",
+  },

   // ─── MSVC runtime (Windows) ───
   {
@@ -1006,6 +1017,20 @@ export function computeDepFlags(cfg: Config): { cflags: string[]; cxxflags: stri
   return { cflags, cxxflags };
 }

+/**
+ * Just the -march/-mcpu/-mtune flags. For deps (WebKit) whose own build system
+ * sets -O/-g/sanitizer flags but never sets a CPU target, so without this they
+ * end up targeting generic x86-64 while the rest of bun targets haswell.
+ */
+export function computeCpuTargetFlags(cfg: Config): string[] {
+  const out: string[] = [];
+  for (const f of cpuTargetFlags) {
+    if (f.when && !f.when(cfg)) continue;
+    out.push(...resolveFlagValue(f.flag, cfg));
+  }
+  return out;
+}
+
 /**
  * Per-file extra flags lookup. Call after computeFlags() when compiling a
  * specific source. Returns extra flags to append (may be empty).
PATCH
