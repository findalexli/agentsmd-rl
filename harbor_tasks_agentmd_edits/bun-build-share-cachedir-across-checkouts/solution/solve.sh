#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied
if grep -q 'build-cache' scripts/build/config.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/scripts/build/CLAUDE.md b/scripts/build/CLAUDE.md
index ddb2b651548..de6b5b677ef 100644
--- a/scripts/build/CLAUDE.md
+++ b/scripts/build/CLAUDE.md
@@ -234,6 +234,8 @@ Why not auto-register in emit functions? Some rules are shared (`dep_configure`
 
 **cmd.exe quoting is partial.** `shell.ts` quote() handles spaces/special chars but NOT `%VAR%` expansion, `^` escape, `&|>` redirection. If an arg contains those, switch to powershell.
 
+**`rm -rf build/` doesn't clear the cache locally.** `cfg.cacheDir` is machine-shared at `$BUN_INSTALL/build-cache` for non-CI builds (ccache, zig, tarballs, prebuilt WebKit). Everything there is content-addressed or version-stamped, so a stale entry can't be hit — don't reach for `bun run clean cache` as a debugging step. If a build misbehaves, the bug is in the inputs or the graph, not the cache; nuking it just costs you a cold rebuild. CI keeps `<buildDir>/cache` so `rm -rf build/` is still a full reset there.
+
 ## Node compatibility
 
 The build system runs under Node 24+ with `--experimental-strip-types` (or Node 25+ without the flag). CI invokes it this way via `process.execPath` in `.buildkite/ci.mjs`.
diff --git a/scripts/build/clean.ts b/scripts/build/clean.ts
index c91b7b863b4..44b6afd65d4 100644
--- a/scripts/build/clean.ts
+++ b/scripts/build/clean.ts
@@ -7,11 +7,15 @@
 
 import { existsSync, readdirSync } from "node:fs";
 import { rm } from "node:fs/promises";
+import { homedir } from "node:os";
 import { dirname, resolve } from "node:path";
 import { fileURLToPath } from "node:url";
 import { allDeps } from "./deps/index.ts";
 
 const cwd = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");
+// Machine-shared cache (ccache/zig/tarballs/webkit). Matches resolveConfig()'s
+// non-CI default. `clean` is a dev-machine tool so we don't branch on CI here.
+const sharedCacheDir = resolve(process.env.BUN_INSTALL || resolve(homedir(), ".bun"), "build-cache");
 
 const args = process.argv.slice(2);
 const dryRun = args.includes("--dry-run");
@@ -29,6 +33,8 @@ presets:
   release-local    build/release-local/ + vendor/WebKit/WebKitBuild/Release{,LTO}
   zig              zig caches + bun-zig.o across all profiles, .zig-cache, zig-out
   cpp              C++ obj/ + pch/ across all profiles
+  cache            machine-shared build cache (~/.bun/build-cache: ccache, zig,
+                   tarballs, prebuilt webkit) — affects ALL checkouts
   deep             build/, .zig-cache, zig-out, vendor/* (except manually
                    managed deps like WebKit)
 
@@ -69,6 +75,7 @@ const presets: Record<string, () => string[]> = {
 
   zig: () => [
     ...buildProfiles().flatMap(p => [resolve(p, "cache", "zig"), resolve(p, "bun-zig.o")]),
+    resolve(sharedCacheDir, "zig"),
     resolve(cwd, "build", "debug", "zig-check-cache"),
     resolve(cwd, ".zig-cache"),
     resolve(cwd, "zig-out"),
@@ -76,6 +83,8 @@ const presets: Record<string, () => string[]> = {
 
   cpp: () => buildProfiles().flatMap(p => [resolve(p, "obj"), resolve(p, "pch")]),
 
+  cache: () => [sharedCacheDir],
+
   deep: () => [
     resolve(cwd, "build"),
     resolve(cwd, "vendor", "zig"),
diff --git a/scripts/build/config.ts b/scripts/build/config.ts
index 9f5a0b7b7d5..d0a367680df 100644
--- a/scripts/build/config.ts
+++ b/scripts/build/config.ts
@@ -8,7 +8,7 @@
 
 import { execSync } from "node:child_process";
 import { existsSync, readFileSync, realpathSync } from "node:fs";
-import { arch as hostArch, platform as hostPlatform } from "node:os";
+import { homedir, arch as hostArch, platform as hostPlatform } from "node:os";
 import { isAbsolute, join, relative, resolve, sep } from "node:path";
 import { NODEJS_ABI_VERSION, NODEJS_VERSION } from "./deps/nodejs-headers.ts";
 import { WEBKIT_VERSION } from "./deps/webkit.ts";
@@ -435,12 +435,20 @@ export function resolveConfig(partial: PartialConfig, toolchain: Toolchain): Con
         : resolve(cwd, partial.buildDir)
       : resolve(cwd, "build", defaultBuildDirName);
   const codegenDir = resolve(buildDir, "codegen");
+  // Local builds share $BUN_INSTALL/build-cache across checkouts and profiles
+  // so ccache/zig/tarballs/webkit reuse one another's work. CI stays per-build
+  // so runners remain hermetic and `rm -rf build/` is a full reset.
+  // Relative BUN_INSTALL is anchored to repo root (not process.cwd()) so the
+  // ninja regen rule — which runs from buildDir — resolves the same path.
+  const bunInstall = process.env.BUN_INSTALL ? resolve(cwd, process.env.BUN_INSTALL) : join(homedir(), ".bun");
   const cacheDir =
     partial.cacheDir !== undefined
       ? isAbsolute(partial.cacheDir)
         ? partial.cacheDir
         : resolve(cwd, partial.cacheDir)
-      : resolve(buildDir, "cache");
+      : ci
+        ? resolve(buildDir, "cache")
+        : resolve(bunInstall, "build-cache");
   const vendorDir = resolve(cwd, "vendor");
 
   // ─── Validation ───
diff --git a/scripts/build/configure.ts b/scripts/build/configure.ts
index 1950fdf6ad3..8a2d0dd032a 100644
--- a/scripts/build/configure.ts
+++ b/scripts/build/configure.ts
@@ -158,8 +158,8 @@ function emitGeneratorRule(n: Ninja, cfg: Config, partial: PartialConfig): void
 }
 
 /**
- * ccache environment to set for compile commands. Points ccache into the
- * build dir (not ~/.ccache) so `rm -rf build/` is a complete reset.
+ * ccache environment to set for compile commands. Points ccache into
+ * cfg.cacheDir (machine-shared locally, per-build in CI — see resolveConfig).
  */
 function ccacheEnv(cfg: Config): Record<string, string> {
   if (cfg.ccache === undefined) return {};
diff --git a/scripts/build/download.ts b/scripts/build/download.ts
index c33ff951200..b8b261ab863 100644
--- a/scripts/build/download.ts
+++ b/scripts/build/download.ts
@@ -57,8 +57,7 @@ export async function downloadWithRetry(url: string, dest: string, logPrefix: st
         continue;
       }
 
-      const tmpPath = `${dest}.partial`;
-      await rm(tmpPath, { force: true });
+      const tmpPath = `${dest}.${process.pid}.partial`;
       const buf = await res.arrayBuffer();
       await writeFile(tmpPath, new Uint8Array(buf));
       await rename(tmpPath, dest);
@@ -186,43 +185,61 @@ export async function fetchPrebuilt(
 
   console.log(`fetching ${url}`);
 
+  // Process-unique temp paths so concurrent builds (shared cacheDir across
+  // checkouts) can't stomp each other's download/extraction.
+  const suffix = `.${process.pid}.${Date.now().toString(36)}`;
+
   // ─── Download ───
   const destParent = resolve(dest, "..");
   await mkdir(destParent, { recursive: true });
-  const tarballPath = `${dest}.download.tar.gz`;
+  const tarballPath = `${dest}${suffix}.tar.gz`;
   await downloadWithRetry(url, tarballPath, name);
 
   // ─── Extract ───
-  // Wipe dest first — no stale files from a previous version.
-  // Extract to staging dir, then hoist. We don't extract directly into dest/
-  // because the tarball's top-level dir name is unpredictable (e.g.
-  // `bun-webkit/` vs `libfoo-1.2.3/`).
-  await rm(dest, { recursive: true, force: true });
-  const stagingDir = `${dest}.staging`;
-  await rm(stagingDir, { recursive: true, force: true });
+  // Extract to a private staging dir, then hoist. We don't extract directly
+  // into dest/ because the tarball's top-level dir name is unpredictable
+  // (e.g. `bun-webkit/` vs `libfoo-1.2.3/`).
+  const stagingDir = `${dest}${suffix}.staging`;
   await mkdir(stagingDir, { recursive: true });
 
-  // stripComponents=0: keep top-level dir for hoisting.
-  await extractTarGz(tarballPath, stagingDir, 0);
-  await rm(tarballPath, { force: true });
-
-  // Hoist: if single top-level dir, promote its contents to dest.
-  // If multiple entries (unusual), the staging dir becomes dest.
-  const entries = await readdir(stagingDir);
-  assert(entries.length > 0, `tarball extracted nothing`, { file: url });
-  const hoistFrom = entries.length === 1 ? resolve(stagingDir, entries[0]!) : stagingDir;
-  await rename(hoistFrom, dest);
-  await rm(stagingDir, { recursive: true, force: true });
-
-  // ─── Post-extract cleanup ───
-  // Before stamp so failure → next build retries. force:true → no error if
-  // path already gone (idempotent re-fetch).
-  for (const p of rmPaths) {
-    await rm(resolve(dest, p), { recursive: true, force: true });
-  }
+  try {
+    // stripComponents=0: keep top-level dir for hoisting.
+    await extractTarGz(tarballPath, stagingDir, 0);
+    await rm(tarballPath, { force: true });
+
+    // Hoist: if single top-level dir, promote its contents to dest.
+    // If multiple entries (unusual), the staging dir becomes dest.
+    const entries = await readdir(stagingDir);
+    assert(entries.length > 0, `tarball extracted nothing`, { file: url });
+    const hoistFrom = entries.length === 1 ? resolve(stagingDir, entries[0]!) : stagingDir;
+
+    // ─── Post-extract cleanup + stamp (inside staging) ───
+    // Done BEFORE publish so the rename below is the single step that makes
+    // a complete, stamped tree visible at dest.
+    for (const p of rmPaths) {
+      await rm(resolve(hoistFrom, p), { recursive: true, force: true });
+    }
+    await writeFile(resolve(hoistFrom, ".identity"), identity + "\n");
 
-  // ─── Write stamp ───
-  // LAST — if anything above throws, no stamp means next build retries.
-  await writeFile(stampPath, identity + "\n");
-  console.log(`extracted to ${dest}`);
+    // ─── Publish ───
+    // Directory rename can't overwrite on any platform, so rm first. If a
+    // concurrent fetch won the race, our rename fails — treat a matching
+    // stamp at dest as success.
+    try {
+      await rm(dest, { recursive: true, force: true });
+      await rename(hoistFrom, dest);
+    } catch (err) {
+      const landed = existsSync(stampPath) ? readFileSync(stampPath, "utf8").trim() : undefined;
+      if (landed === identity) {
+        console.log(`up to date (concurrent fetch won)`);
+        return;
+      }
+      throw err;
+    }
+
+    console.log(`extracted to ${dest}`);
+  } finally {
+    await rm(stagingDir, { recursive: true, force: true });
+    await rm(tarballPath, { force: true });
+  }
 }
PATCH

echo "Patch applied successfully."
