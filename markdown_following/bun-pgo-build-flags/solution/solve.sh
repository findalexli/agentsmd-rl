#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied
if grep -q '"--pgo-generate and --pgo-use are mutually exclusive"' scripts/build/config.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
git apply - <<'PATCH'
diff --git a/scripts/build.ts b/scripts/build.ts
index 1b81f743a36..cbd5c6a367d 100644
--- a/scripts/build.ts
+++ b/scripts/build.ts
@@ -314,6 +314,8 @@ function parseArgs(argv: string[]): CliArgs {
     "nodejsAbiVersion",
     "zigCommit",
     "webkitVersion",
+    "pgoGenerate",
+    "pgoUse",
   ]);

   for (let i = 0; i < argv.length; i++) {
diff --git a/scripts/build/config.ts b/scripts/build/config.ts
index 3a9274336a8..9f5a0b7b7d5 100644
--- a/scripts/build/config.ts
+++ b/scripts/build/config.ts
@@ -100,6 +100,10 @@ export interface Config {

   // ─── Features (all explicit booleans) ───
   lto: boolean;
+  /** IR PGO: directory for .profraw output (instrumented build). Mutually exclusive with pgoUse. */
+  pgoGenerate: string | undefined;
+  /** IR PGO: .profdata file path (optimized build). Mutually exclusive with pgoGenerate. */
+  pgoUse: string | undefined;
   asan: boolean;
   zigAsan: boolean;
   assertions: boolean;
@@ -207,6 +211,8 @@ export interface PartialConfig {
   buildType?: BuildType;
   mode?: BuildMode;
   lto?: boolean;
+  pgoGenerate?: string;
+  pgoUse?: string;
   asan?: boolean;
   zigAsan?: boolean;
   assertions?: boolean;
@@ -391,6 +397,13 @@ export function resolveConfig(partial: PartialConfig, toolchain: Toolchain): Con
     lto = false;
   }

+  // PGO: paths resolved to absolute. generate/use are mutually exclusive.
+  const pgoGenerate = partial.pgoGenerate ? resolve(partial.pgoGenerate) : undefined;
+  const pgoUse = partial.pgoUse ? resolve(partial.pgoUse) : undefined;
+  if (pgoGenerate && pgoUse) {
+    throw new BuildError("--pgo-generate and --pgo-use are mutually exclusive");
+  }
+
   // Logs: on by default in debug non-test
   const logs = partial.logs ?? debug;

@@ -480,6 +493,8 @@ export function resolveConfig(partial: PartialConfig, toolchain: Toolchain): Con
     release,
     mode: partial.mode ?? "full",
     lto,
+    pgoGenerate,
+    pgoUse,
     asan,
     zigAsan,
     assertions,
@@ -754,6 +769,8 @@ export function formatConfig(cfg: Config, exe: string): string {
   ];
   const features: string[] = [];
   if (cfg.lto) features.push("lto");
+  if (cfg.pgoGenerate) features.push("pgo-gen");
+  if (cfg.pgoUse) features.push("pgo-use");
   if (cfg.asan) features.push("asan");
   if (cfg.assertions) features.push("assertions");
   if (cfg.logs) features.push("logs");
diff --git a/scripts/build/deps/webkit.ts b/scripts/build/deps/webkit.ts
index 9a76b8b1f11..4b4152a42ce 100644
--- a/scripts/build/deps/webkit.ts
+++ b/scripts/build/deps/webkit.ts
@@ -182,17 +182,30 @@ export const webkit: Dependency = {

     // Local: nested cmake, target=jsc.
     //
-    // CMAKE_C_FLAGS/CMAKE_CXX_FLAGS set to empty: clears the global dep
-    // flags source.ts would otherwise pass. WebKit's cmake sets its own
-    // -O/-march/etc.; ours would conflict. Dep args go LAST so they override.
+    // CMAKE_C_FLAGS/CMAKE_CXX_FLAGS: clears the global dep flags source.ts
+    // would otherwise pass — WebKit's cmake sets its own -O/-march/etc.;
+    // ours would conflict. Dep args go LAST so they override. We DO forward
+    // LTO/PGO since WebKit's cmake doesn't set those itself.
     //
     // Windows: ICU built from source via preBuild before cmake configure.
     // WebKit's cmake finds it via ICU_ROOT. On posix, system ICU is used
     // (macOS: Homebrew headers + system libs; Linux: libicu-dev) — cmake
     // auto-detects.
+    const optFlags: string[] = [];
+    if (cfg.lto) optFlags.push("-flto=full");
+    if (cfg.pgoGenerate) optFlags.push(`-fprofile-generate=${cfg.pgoGenerate}`);
+    if (cfg.pgoUse) {
+      optFlags.push(
+        `-fprofile-use=${cfg.pgoUse}`,
+        "-Wno-profile-instr-out-of-date",
+        "-Wno-profile-instr-unprofiled",
+        "-Wno-backend-plugin",
+      );
+    }
+    const optFlagStr = optFlags.join(" ");
     const args: Record<string, string> = {
-      CMAKE_C_FLAGS: "",
-      CMAKE_CXX_FLAGS: "",
+      CMAKE_C_FLAGS: optFlagStr,
+      CMAKE_CXX_FLAGS: optFlagStr,
       PORT: "JSCOnly",
       ENABLE_STATIC_JSC: "ON",
       USE_THIN_ARCHIVES: "OFF",
@@ -220,8 +233,8 @@ export const webkit: Dependency = {
       args.ICU_INCLUDE_DIR = slash(resolve(icu, "include"));
       // U_STATIC_IMPLEMENTATION: ICU headers default to dllimport; we
       // link statically. Matches what the old cmake's SetupWebKit did.
-      args.CMAKE_C_FLAGS = "/DU_STATIC_IMPLEMENTATION";
-      args.CMAKE_CXX_FLAGS = "/DU_STATIC_IMPLEMENTATION /clang:-fno-c++-static-destructors";
+      args.CMAKE_C_FLAGS = `/DU_STATIC_IMPLEMENTATION ${optFlagStr}`.trim();
+      args.CMAKE_CXX_FLAGS = `/DU_STATIC_IMPLEMENTATION /clang:-fno-c++-static-destructors ${optFlagStr}`.trim();
       // Static CRT to match bun + all other deps (we build everything
       // with /MTd or /MT). Without this, cmake defaults to /MDd →
       // RuntimeLibrary mismatch at link.
diff --git a/scripts/build/flags.ts b/scripts/build/flags.ts
index fd9c2bd7302..2cf683218bb 100644
--- a/scripts/build/flags.ts
+++ b/scripts/build/flags.ts
@@ -320,6 +320,23 @@ export const globalFlags: Flag[] = [
     desc: "Enable devirtualization across whole program (LTO only)",
   },

+  // ─── PGO (compile-side) ───
+  {
+    flag: c => `-fprofile-generate=${c.pgoGenerate}`,
+    when: c => c.unix && !!c.pgoGenerate,
+    desc: "IR PGO: instrument for profile generation",
+  },
+  {
+    flag: c => [
+      `-fprofile-use=${c.pgoUse}`,
+      "-Wno-profile-instr-out-of-date",
+      "-Wno-profile-instr-unprofiled",
+      "-Wno-backend-plugin",
+    ],
+    when: c => c.unix && !!c.pgoUse,
+    desc: "IR PGO: optimize with profile data",
+  },
+
   // ─── Path remapping (CI reproducibility) ───
   {
     flag: c => [
@@ -608,6 +625,18 @@ export const linkerFlags: Flag[] = [
     desc: "LTO codegen at -Os (matches compile-side opt level)",
   },

+  // ─── PGO (link-side) ───
+  {
+    flag: c => `-fprofile-generate=${c.pgoGenerate}`,
+    when: c => c.unix && !!c.pgoGenerate,
+    desc: "IR PGO: link profiling runtime",
+  },
+  {
+    flag: c => `-fprofile-use=${c.pgoUse}`,
+    when: c => c.unix && !!c.pgoUse,
+    desc: "IR PGO: LTO+PGO at link time",
+  },
+
   // ─── Windows ───
   {
     flag: ["/STACK:0x1200000,0x200000", "/errorlimit:0"],

PATCH

echo "Patch applied successfully."
