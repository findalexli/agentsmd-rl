#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openclaw

# Idempotency: check if already fixed
if grep -q 'security_scan_blocked\|security_scan_failed' src/plugins/install-security-scan.runtime.ts 2>/dev/null; then
  echo "Fix already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/src/plugins/install-security-scan.runtime.ts b/src/plugins/install-security-scan.runtime.ts
index 5c90f2df94f0..d45d3acf999f 100644
--- a/src/plugins/install-security-scan.runtime.ts
+++ b/src/plugins/install-security-scan.runtime.ts
@@ -35,6 +35,7 @@ type PluginInstallRequestKind =

 export type InstallSecurityScanResult = {
   blocked?: {
+    code?: "security_scan_blocked" | "security_scan_failed";
     reason: string;
   };
 };
@@ -48,6 +49,17 @@ function buildCriticalDetails(params: {
     .join("; ");
 }

+function buildCriticalBlockReason(params: {
+  findings: Array<{ file: string; line: number; message: string; severity: string }>;
+  targetLabel: string;
+}) {
+  return `${params.targetLabel} blocked: dangerous code patterns detected: ${buildCriticalDetails({ findings: params.findings })}`;
+}
+
+function buildScanFailureBlockReason(params: { error: string; targetLabel: string }) {
+  return `${params.targetLabel} blocked: code safety scan failed (${params.error}). Run "openclaw security audit --deep" for details.`;
+}
+
 function buildBuiltinScanFromError(error: unknown): BuiltinInstallScan {
   return {
     status: "error",
@@ -81,7 +93,6 @@ async function scanDirectoryTarget(params: {
   includeFiles?: string[];
   logger: InstallScanLogger;
   path: string;
-  scanFailureMessage: string;
   suspiciousMessage: string;
   targetName: string;
   warningMessage: string;
@@ -104,15 +115,42 @@ async function scanDirectoryTarget(params: {
     }
     return builtinScan;
   } catch (err) {
-    params.logger.warn?.(params.scanFailureMessage.replace("{error}", String(err)));
     return buildBuiltinScanFromError(err);
   }
 }

+function buildBlockedScanResult(params: {
+  builtinScan: BuiltinInstallScan;
+  targetLabel: string;
+}): InstallSecurityScanResult | undefined {
+  if (params.builtinScan.status === "error") {
+    return {
+      blocked: {
+        code: "security_scan_failed",
+        reason: buildScanFailureBlockReason({
+          error: params.builtinScan.error ?? "unknown error",
+          targetLabel: params.targetLabel,
+        }),
+      },
+    };
+  }
+  if (params.builtinScan.critical > 0) {
+    return {
+      blocked: {
+        code: "security_scan_blocked",
+        reason: buildCriticalBlockReason({
+          findings: params.builtinScan.findings,
+          targetLabel: params.targetLabel,
+        }),
+      },
+    };
+  }
+  return undefined;
+}
+
 async function scanFileTarget(params: {
   logger: InstallScanLogger;
   path: string;
-  scanFailureMessage: string;
   suspiciousMessage: string;
   targetName: string;
   warningMessage: string;
@@ -122,7 +160,6 @@ async function scanFileTarget(params: {
     includeFiles: [params.path],
     logger: params.logger,
     path: directory,
-    scanFailureMessage: params.scanFailureMessage,
     suspiciousMessage: params.suspiciousMessage,
     targetName: params.targetName,
     warningMessage: params.warningMessage,
@@ -223,13 +260,16 @@ export async function scanBundleInstallSourceRuntime(params: {
   const builtinScan = await scanDirectoryTarget({
     logger: params.logger,
     path: params.sourceDir,
-    scanFailureMessage: `Bundle "${params.pluginId}" code safety scan failed ({error}). Installation continues; run "openclaw security audit --deep" after install.`,
     suspiciousMessage: `Bundle "{target}" has {count} suspicious code pattern(s). Run "openclaw security audit --deep" for details.`,
     targetName: params.pluginId,
     warningMessage: `WARNING: Bundle "${params.pluginId}" contains dangerous code patterns`,
   });
+  const builtinBlocked = buildBlockedScanResult({
+    builtinScan,
+    targetLabel: `Bundle "${params.pluginId}" installation`,
+  });

-  return await runBeforeInstallHook({
+  const hookResult = await runBeforeInstallHook({
     logger: params.logger,
     installLabel: `Bundle "${params.pluginId}" installation`,
     origin: "plugin-bundle",
@@ -248,6 +288,7 @@ export async function scanBundleInstallSourceRuntime(params: {
       ...(params.version ? { version: params.version } : {}),
     },
   });
+  return hookResult?.blocked ? hookResult : builtinBlocked;
 }

 export async function scanPackageInstallSourceRuntime(params: {
@@ -283,13 +324,16 @@ export async function scanPackageInstallSourceRuntime(params: {
     includeFiles: forcedScanEntries,
     logger: params.logger,
     path: params.packageDir,
-    scanFailureMessage: `Plugin "${params.pluginId}" code safety scan failed ({error}). Installation continues; run "openclaw security audit --deep" after install.`,
     suspiciousMessage: `Plugin "{target}" has {count} suspicious code pattern(s). Run "openclaw security audit --deep" for details.`,
     targetName: params.pluginId,
     warningMessage: `WARNING: Plugin "${params.pluginId}" contains dangerous code patterns`,
   });
+  const builtinBlocked = buildBlockedScanResult({
+    builtinScan,
+    targetLabel: `Plugin "${params.pluginId}" installation`,
+  });

-  return await runBeforeInstallHook({
+  const hookResult = await runBeforeInstallHook({
     logger: params.logger,
     installLabel: `Plugin "${params.pluginId}" installation`,
     origin: "plugin-package",
@@ -310,6 +354,7 @@ export async function scanPackageInstallSourceRuntime(params: {
       extensions: params.extensions.slice(),
     },
   });
+  return hookResult?.blocked ? hookResult : builtinBlocked;
 }

 export async function scanFileInstallSourceRuntime(params: {
@@ -322,13 +367,16 @@ export async function scanFileInstallSourceRuntime(params: {
   const builtinScan = await scanFileTarget({
     logger: params.logger,
     path: params.filePath,
-    scanFailureMessage: `Plugin file "${params.pluginId}" code safety scan failed ({error}). Installation continues; run "openclaw security audit --deep" after install.`,
     suspiciousMessage: `Plugin file "{target}" has {count} suspicious code pattern(s). Run "openclaw security audit --deep" for details.`,
     targetName: params.pluginId,
     warningMessage: `WARNING: Plugin file "${params.pluginId}" contains dangerous code patterns`,
   });
+  const builtinBlocked = buildBlockedScanResult({
+    builtinScan,
+    targetLabel: `Plugin file "${params.pluginId}" installation`,
+  });

-  return await runBeforeInstallHook({
+  const hookResult = await runBeforeInstallHook({
     logger: params.logger,
     installLabel: `Plugin file "${params.pluginId}" installation`,
     origin: "plugin-file",
@@ -346,4 +394,5 @@ export async function scanFileInstallSourceRuntime(params: {
       extensions: [path.basename(params.filePath)],
     },
   });
+  return hookResult?.blocked ? hookResult : builtinBlocked;
 }
diff --git a/src/plugins/install.test.ts b/src/plugins/install.test.ts
index 6d8b76b77290..0a9120d6d814 100644
--- a/src/plugins/install.test.ts
+++ b/src/plugins/install.test.ts
@@ -251,6 +251,19 @@ async function installFromDirWithWarnings(params: { pluginDir: string; extension
   return { result, warnings };
 }

+async function installFromFileWithWarnings(params: { extensionsDir: string; filePath: string }) {
+  const warnings: string[] = [];
+  const result = await installPluginFromFile({
+    filePath: params.filePath,
+    extensionsDir: params.extensionsDir,
+    logger: {
+      info: () => {},
+      warn: (msg: string) => warnings.push(msg),
+    },
+  });
+  return { result, warnings };
+}
+
 function setupManifestInstallFixture(params: { manifestId: string }) {
   const caseDir = makeTempDir();
   const stateDir = path.join(caseDir, "state");
@@ -723,7 +736,7 @@ describe("installPluginFromArchive", () => {
     expect.unreachable("expected install to fail without openclaw.extensions");
   });

-  it("warns when plugin contains dangerous code patterns", async () => {
+  it("blocks package installs when plugin contains dangerous code patterns", async () => {
     const { pluginDir, extensionsDir } = setupPluginInstallDirs();

     fs.writeFileSync(
@@ -741,7 +754,29 @@ describe("installPluginFromArchive", () => {

     const { result, warnings } = await installFromDirWithWarnings({ pluginDir, extensionsDir });

-    expect(result.ok).toBe(true);
+    expect(result.ok).toBe(false);
+    if (!result.ok) {
+      expect(result.code).toBe(PLUGIN_INSTALL_ERROR_CODE.SECURITY_SCAN_BLOCKED);
+      expect(result.error).toContain('Plugin "dangerous-plugin" installation blocked');
+      expect(result.error).toContain("dangerous code patterns detected");
+    }
+    expect(warnings.some((w) => w.includes("dangerous code pattern"))).toBe(true);
+  });
+
+  it("blocks bundle installs when bundle contains dangerous code patterns", async () => {
+    const { pluginDir, extensionsDir } = setupBundleInstallFixture({
+      bundleFormat: "codex",
+      name: "Dangerous Bundle",
+    });
+    fs.writeFileSync(path.join(pluginDir, "payload.js"), "eval('danger');\n", "utf-8");
+
+    const { result, warnings } = await installFromDirWithWarnings({ pluginDir, extensionsDir });
+
+    expect(result.ok).toBe(false);
+    if (!result.ok) {
+      expect(result.code).toBe(PLUGIN_INSTALL_ERROR_CODE.SECURITY_SCAN_BLOCKED);
+      expect(result.error).toContain('Bundle "dangerous-bundle" installation blocked');
+    }
     expect(warnings.some((w) => w.includes("dangerous code pattern"))).toBe(true);
   });

@@ -835,6 +870,7 @@ describe("installPluginFromArchive", () => {
     expect(result.ok).toBe(false);
     if (!result.ok) {
       expect(result.error).toBe("Blocked by enterprise policy");
+      expect(result.code).toBeUndefined();
     }
     expect(handler).toHaveBeenCalledTimes(1);
     expect(handler.mock.calls[0]?.[0]).toMatchObject({
@@ -886,12 +922,12 @@ describe("installPluginFromArchive", () => {

     const { result, warnings } = await installFromDirWithWarnings({ pluginDir, extensionsDir });

-    expect(result.ok).toBe(true);
+    expect(result.ok).toBe(false);
     expect(warnings.some((w) => w.includes("hidden/node_modules path"))).toBe(true);
     expect(warnings.some((w) => w.includes("dangerous code pattern"))).toBe(true);
   });

-  it("continues install when scanner throws", async () => {
+  it("blocks install when scanner throws", async () => {
     const scanSpy = vi
       .spyOn(installSecurityScan, "scanPackageInstallSource")
       .mockRejectedValueOnce(new Error("scanner exploded"));
@@ -910,8 +946,12 @@ describe("installPluginFromArchive", () => {

     const { result, warnings } = await installFromDirWithWarnings({ pluginDir, extensionsDir });

-    expect(result.ok).toBe(true);
-    expect(warnings.some((w) => w.includes("code safety scan failed"))).toBe(true);
+    expect(result.ok).toBe(false);
+    if (!result.ok) {
+      expect(result.code).toBe(PLUGIN_INSTALL_ERROR_CODE.SECURITY_SCAN_FAILED);
+      expect(result.error).toContain("code safety scan failed (Error: scanner exploded)");
+    }
+    expect(warnings).toEqual([]);
     scanSpy.mockRestore();
   });
 });
@@ -1226,6 +1266,27 @@ describe("installPluginFromPath", () => {
     });
   });

+  it("blocks plain file installs when the scanner finds dangerous code patterns", async () => {
+    const baseDir = makeTempDir();
+    const extensionsDir = path.join(baseDir, "extensions");
+    fs.mkdirSync(extensionsDir, { recursive: true });
+
+    const sourcePath = path.join(baseDir, "payload.js");
+    fs.writeFileSync(sourcePath, "eval('danger');\n", "utf-8");
+
+    const { result, warnings } = await installFromFileWithWarnings({
+      filePath: sourcePath,
+      extensionsDir,
+    });
+
+    expect(result.ok).toBe(false);
+    if (!result.ok) {
+      expect(result.code).toBe(PLUGIN_INSTALL_ERROR_CODE.SECURITY_SCAN_BLOCKED);
+      expect(result.error).toContain('Plugin file "payload" installation blocked');
+    }
+    expect(warnings.some((w) => w.includes("dangerous code pattern"))).toBe(true);
+  });
+
   it("blocks hardlink alias overwrites when installing a plain file plugin", async () => {
     const baseDir = makeTempDir();
     const extensionsDir = path.join(baseDir, "extensions");
diff --git a/src/plugins/install-security-scan.ts b/src/plugins/install-security-scan.ts
index 1cd6dce6e3ea..dc5929618740 100644
--- a/src/plugins/install-security-scan.ts
+++ b/src/plugins/install-security-scan.ts
@@ -4,6 +4,7 @@ type InstallScanLogger = {

 export type InstallSecurityScanResult = {
   blocked?: {
+    code?: "security_scan_blocked" | "security_scan_failed";
     reason: string;
   };
 };
diff --git a/src/plugins/install.ts b/src/plugins/install.ts
index 66ba0196e6ae..34d4093d15d5 100644
--- a/src/plugins/install.ts
+++ b/src/plugins/install.ts
@@ -8,6 +8,7 @@ import {
 } from "../infra/install-safe-path.js";
 import { type NpmIntegrityDrift, type NpmSpecResolution } from "../infra/install-source-utils.js";
 import { CONFIG_DIR, resolveUserPath } from "../utils.js";
+import type { InstallSecurityScanResult } from "./install-security-scan.js";
 import {
   resolvePackageExtensionEntries,
   type PackageManifest as PluginPackageManifest,
@@ -48,6 +49,8 @@ export const PLUGIN_INSTALL_ERROR_CODE = {
   EMPTY_OPENCLAW_EXTENSIONS: "empty_openclaw_extensions",
   NPM_PACKAGE_NOT_FOUND: "npm_package_not_found",
   PLUGIN_ID_MISMATCH: "plugin_id_mismatch",
+  SECURITY_SCAN_BLOCKED: "security_scan_blocked",
+  SECURITY_SCAN_FAILED: "security_scan_failed",
 } as const;

 export type PluginInstallErrorCode =
@@ -212,6 +215,20 @@ function buildDirectoryInstallResult(params: {
   };
 }

+function buildBlockedInstallResult(params: {
+  blocked: NonNullable<NonNullable<InstallSecurityScanResult>["blocked"]>;
+}): Extract<InstallPluginResult, { ok: false }> {
+  return {
+    ok: false,
+    error: params.blocked.reason,
+    ...(params.blocked.code === "security_scan_failed"
+      ? { code: PLUGIN_INSTALL_ERROR_CODE.SECURITY_SCAN_FAILED }
+      : params.blocked.code === "security_scan_blocked"
+        ? { code: PLUGIN_INSTALL_ERROR_CODE.SECURITY_SCAN_BLOCKED }
+        : {}),
+  };
+}
+
 type PackageInstallCommonParams = {
   extensionsDir?: string;
   timeoutMs?: number;
@@ -394,12 +411,14 @@ async function installBundleFromSourceDir(
       version: manifestRes.manifest.version,
     });
     if (scanResult?.blocked) {
-      return { ok: false, error: scanResult.blocked.reason };
+      return buildBlockedInstallResult({ blocked: scanResult.blocked });
     }
   } catch (err) {
-    logger.warn?.(
-      `Bundle "${pluginId}" code safety scan failed (${String(err)}). Installation continues; run "openclaw security audit --deep" after install.`,
-    );
+    return {
+      ok: false,
+      error: `Bundle "${pluginId}" installation blocked: code safety scan failed (${String(err)}). Run "openclaw security audit --deep" for details.`,
+      code: PLUGIN_INSTALL_ERROR_CODE.SECURITY_SCAN_FAILED,
+    };
   }

   return await installPluginDirectoryIntoExtensions({
@@ -573,12 +592,14 @@ async function installPluginFromPackageDir(
       version: typeof manifest.version === "string" ? manifest.version : undefined,
     });
     if (scanResult?.blocked) {
-      return { ok: false, error: scanResult.blocked.reason };
+      return buildBlockedInstallResult({ blocked: scanResult.blocked });
     }
   } catch (err) {
-    logger.warn?.(
-      `Plugin "${pluginId}" code safety scan failed (${String(err)}). Installation continues; run "openclaw security audit --deep" after install.`,
-    );
+    return {
+      ok: false,
+      error: `Plugin "${pluginId}" installation blocked: code safety scan failed (${String(err)}). Run "openclaw security audit --deep" for details.`,
+      code: PLUGIN_INSTALL_ERROR_CODE.SECURITY_SCAN_FAILED,
+    };
   }

   const deps = manifest.dependencies ?? {};
@@ -736,12 +757,14 @@ export async function installPluginFromFile(params: {
       requestedSpecifier: installPolicyRequest.requestedSpecifier,
     });
     if (scanResult?.blocked) {
-      return { ok: false, error: scanResult.blocked.reason };
+      return buildBlockedInstallResult({ blocked: scanResult.blocked });
     }
   } catch (err) {
-    logger.warn?.(
-      `Plugin file "${pluginId}" code safety scan failed (${String(err)}). Installation continues; run "openclaw security audit --deep" after install.`,
-    );
+    return {
+      ok: false,
+      error: `Plugin file "${pluginId}" installation blocked: code safety scan failed (${String(err)}). Run "openclaw security audit --deep" for details.`,
+      code: PLUGIN_INSTALL_ERROR_CODE.SECURITY_SCAN_FAILED,
+    };
   }

   logger.info?.(`Installing to ${targetFile}…`);

PATCH

echo "Fix applied: plugin install now blocks on scan critical findings and scan failures."
