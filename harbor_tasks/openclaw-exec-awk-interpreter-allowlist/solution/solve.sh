#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openclaw

# Idempotency check
if grep -q '"nawk"' src/infra/exec-inline-eval.ts 2>/dev/null; then
  echo "Patch already applied"
  exit 0
fi

git apply - <<'PATCH'
diff --git a/src/infra/exec-approvals-allow-always.test.ts b/src/infra/exec-approvals-allow-always.test.ts
index 6ad13a7931fb..849cd491c4b8 100644
--- a/src/infra/exec-approvals-allow-always.test.ts
+++ b/src/infra/exec-approvals-allow-always.test.ts
@@ -174,6 +174,26 @@ describe("resolveAllowAlwaysPatterns", () => {
     expect(patterns).toEqual([exe]);
   });

+  it("does not persist interpreter-like executables for allow-always", () => {
+    const awk = path.join("/tmp", "awk");
+    const patterns = resolveAllowAlwaysPatterns({
+      segments: [
+        {
+          raw: `${awk} '{print $1}' data.csv`,
+          argv: [awk, "{print $1}", "data.csv"],
+          resolution: makeMockCommandResolution({
+            execution: makeMockExecutableResolution({
+              rawExecutable: awk,
+              resolvedPath: awk,
+              executableName: "awk",
+            }),
+          }),
+        },
+      ],
+    });
+    expect(patterns).toEqual([]);
+  });
+
   it("unwraps shell wrappers and persists the inner executable instead", () => {
     if (process.platform === "win32") {
       return;
@@ -619,6 +639,70 @@ $0 \\"$1\\"" touch {marker}`,
     });
   });

+  it("prevents allow-always bypass for awk interpreters", () => {
+    if (process.platform === "win32") {
+      return;
+    }
+    const dir = makeTempDir();
+    makeExecutable(dir, "awk");
+    const env = makePathEnv(dir);
+    const safeBins = resolveSafeBins(undefined);
+
+    const { persisted } = resolvePersistedPatterns({
+      command: "awk '{print $1}' data.csv",
+      dir,
+      env,
+      safeBins,
+    });
+    expect(persisted).toEqual([]);
+
+    const second = evaluateShellAllowlist({
+      command: `awk 'BEGIN{system("id > ${path.join(dir, "marker")}")}'`,
+      allowlist: persisted.map((pattern) => ({ pattern })),
+      safeBins,
+      cwd: dir,
+      env,
+      platform: process.platform,
+    });
+    expect(second.allowlistSatisfied).toBe(false);
+    expect(
+      requiresExecApproval({
+        ask: "on-miss",
+        security: "allowlist",
+        analysisOk: second.analysisOk,
+        allowlistSatisfied: second.allowlistSatisfied,
+      }),
+    ).toBe(true);
+  });
+
+  it("prevents allow-always bypass for shell-carried awk interpreters", () => {
+    if (process.platform === "win32") {
+      return;
+    }
+    const dir = makeTempDir();
+    makeExecutable(dir, "awk");
+    const env = makePathEnv(dir);
+    const safeBins = resolveSafeBins(undefined);
+
+    const { persisted } = resolvePersistedPatterns({
+      command: `sh -lc '$0 "$@"' awk '{print $1}' data.csv`,
+      dir,
+      env,
+      safeBins,
+    });
+    expect(persisted).toEqual([]);
+
+    const second = evaluateShellAllowlist({
+      command: `sh -lc '$0 "$@"' awk 'BEGIN{system("id > /tmp/pwned")}'`,
+      allowlist: persisted.map((pattern) => ({ pattern })),
+      safeBins,
+      cwd: dir,
+      env,
+      platform: process.platform,
+    });
+    expect(second.allowlistSatisfied).toBe(false);
+  });
+
   it("prevents allow-always bypass for script wrapper chains", () => {
     if (process.platform !== "darwin" && process.platform !== "freebsd") {
       return;
diff --git a/src/infra/exec-approvals-allowlist.ts b/src/infra/exec-approvals-allowlist.ts
index f0d54cb4e022..c37578344e95 100644
--- a/src/infra/exec-approvals-allowlist.ts
+++ b/src/infra/exec-approvals-allowlist.ts
@@ -15,6 +15,7 @@ import {
   type ExecutableResolution,
 } from "./exec-approvals-analysis.js";
 import type { ExecAllowlistEntry } from "./exec-approvals.js";
+import { isInterpreterLikeAllowlistPattern } from "./exec-inline-eval.js";
 import {
   DEFAULT_SAFE_BINS,
   SAFE_BIN_PROFILES,
@@ -521,6 +522,9 @@ function collectAllowAlwaysPatterns(params: {
   if (!candidatePath) {
     return;
   }
+  if (isInterpreterLikeAllowlistPattern(candidatePath)) {
+    return;
+  }
   if (!trustPlan.shellWrapperExecutable) {
     params.out.add(candidatePath);
     return;
@@ -531,6 +535,9 @@ function collectAllowAlwaysPatterns(params: {
     env: params.env,
   });
   if (positionalArgvPath) {
+    if (isInterpreterLikeAllowlistPattern(positionalArgvPath)) {
+      return;
+    }
     params.out.add(positionalArgvPath);
     return;
   }
diff --git a/src/infra/exec-inline-eval.test.ts b/src/infra/exec-inline-eval.test.ts
index ff2e6673220c..ed8b67958ef7 100644
--- a/src/infra/exec-inline-eval.test.ts
+++ b/src/infra/exec-inline-eval.test.ts
@@ -11,6 +11,8 @@ describe("exec inline eval detection", () => {
     { argv: ["/usr/bin/node", "--eval", "console.log('hi')"], expected: "node --eval" },
     { argv: ["perl", "-E", "say 1"], expected: "perl -e" },
     { argv: ["osascript", "-e", "beep"], expected: "osascript -e" },
+    { argv: ["awk", "BEGIN { print 1 }"], expected: "awk inline program" },
+    { argv: ["gawk", "-F", ",", "{print $1}", "data.csv"], expected: "gawk inline program" },
   ] as const)("detects interpreter eval flags for %j", ({ argv, expected }) => {
     const hit = detectInterpreterInlineEvalArgv([...argv]);
     expect(hit).not.toBeNull();
@@ -20,11 +22,16 @@ describe("exec inline eval detection", () => {
   it("ignores normal script execution", () => {
     expect(detectInterpreterInlineEvalArgv(["python3", "script.py"])).toBeNull();
     expect(detectInterpreterInlineEvalArgv(["node", "script.js"])).toBeNull();
+    expect(detectInterpreterInlineEvalArgv(["awk", "-f", "script.awk", "data.csv"])).toBeNull();
   });

   it("matches interpreter-like allowlist patterns", () => {
     expect(isInterpreterLikeAllowlistPattern("/usr/bin/python3")).toBe(true);
     expect(isInterpreterLikeAllowlistPattern("**/node")).toBe(true);
+    expect(isInterpreterLikeAllowlistPattern("/usr/bin/awk")).toBe(true);
+    expect(isInterpreterLikeAllowlistPattern("**/gawk")).toBe(true);
+    expect(isInterpreterLikeAllowlistPattern("/usr/bin/mawk")).toBe(true);
+    expect(isInterpreterLikeAllowlistPattern("nawk")).toBe(true);
     expect(isInterpreterLikeAllowlistPattern("/usr/bin/rg")).toBe(false);
   });
 });
diff --git a/src/infra/exec-inline-eval.ts b/src/infra/exec-inline-eval.ts
index 0d719b4aa4f2..ca26afdc3ba9 100644
--- a/src/infra/exec-inline-eval.ts
+++ b/src/infra/exec-inline-eval.ts
@@ -13,6 +13,14 @@ type InterpreterFlagSpec = {
   prefixFlags?: readonly string[];
 };

+type PositionalInterpreterSpec = {
+  names: readonly string[];
+  fileFlags: ReadonlySet<string>;
+  fileFlagPrefixes?: readonly string[];
+  exactValueFlags: ReadonlySet<string>;
+  prefixValueFlags?: readonly string[];
+};
+
 const INTERPRETER_INLINE_EVAL_SPECS: readonly InterpreterFlagSpec[] = [
   { names: ["python", "python2", "python3", "pypy", "pypy3"], exactFlags: new Set(["-c"]) },
   {
@@ -26,8 +34,32 @@ const INTERPRETER_INLINE_EVAL_SPECS: readonly InterpreterFlagSpec[] = [
   { names: ["osascript"], exactFlags: new Set(["-e"]) },
 ];

-const INTERPRETER_INLINE_EVAL_NAMES = new Set(
-  INTERPRETER_INLINE_EVAL_SPECS.flatMap((entry) => entry.names),
+const POSITIONAL_INTERPRETER_INLINE_EVAL_SPECS: readonly PositionalInterpreterSpec[] = [
+  {
+    names: ["awk", "gawk", "mawk", "nawk"],
+    fileFlags: new Set(["-f", "--file"]),
+    fileFlagPrefixes: ["-f", "--file="],
+    exactValueFlags: new Set([
+      "-f",
+      "--file",
+      "-F",
+      "--field-separator",
+      "-v",
+      "--assign",
+      "-i",
+      "--include",
+      "-l",
+      "--load",
+      "-W",
+    ]),
+    prefixValueFlags: ["-F", "--field-separator=", "-v", "--assign=", "--include=", "--load="],
+  },
+];
+
+const INTERPRETER_ALLOWLIST_NAMES = new Set(
+  INTERPRETER_INLINE_EVAL_SPECS.flatMap((entry) => entry.names).concat(
+    POSITIONAL_INTERPRETER_INLINE_EVAL_SPECS.flatMap((entry) => entry.names),
+  ),
 );

 function findInterpreterSpec(executable: string): InterpreterFlagSpec | null {
@@ -40,6 +72,16 @@ function findInterpreterSpec(executable: string): InterpreterFlagSpec | null {
   return null;
 }

+function findPositionalInterpreterSpec(executable: string): PositionalInterpreterSpec | null {
+  const normalized = normalizeExecutableToken(executable);
+  for (const spec of POSITIONAL_INTERPRETER_INLINE_EVAL_SPECS) {
+    if (spec.names.includes(normalized)) {
+      return spec;
+    }
+  }
+  return null;
+}
+
 export function detectInterpreterInlineEvalArgv(
   argv: string[] | undefined | null,
 ): InterpreterInlineEvalHit | null {
@@ -51,7 +93,37 @@ export function detectInterpreterInlineEvalArgv(
     return null;
   }
   const spec = findInterpreterSpec(executable);
-  if (!spec) {
+  if (spec) {
+    for (let idx = 1; idx < argv.length; idx += 1) {
+      const token = argv[idx]?.trim();
+      if (!token) {
+        continue;
+      }
+      if (token === "--") {
+        break;
+      }
+      const lower = token.toLowerCase();
+      if (spec.exactFlags.has(lower)) {
+        return {
+          executable,
+          normalizedExecutable: normalizeExecutableToken(executable),
+          flag: lower,
+          argv,
+        };
+      }
+      if (spec.prefixFlags?.some((prefix) => lower.startsWith(prefix))) {
+        return {
+          executable,
+          normalizedExecutable: normalizeExecutableToken(executable),
+          flag: lower,
+          argv,
+        };
+      }
+    }
+  }
+
+  const positionalSpec = findPositionalInterpreterSpec(executable);
+  if (!positionalSpec) {
     return null;
   }
   for (let idx = 1; idx < argv.length; idx += 1) {
@@ -60,30 +132,55 @@ export function detectInterpreterInlineEvalArgv(
       continue;
     }
     if (token === "--") {
-      break;
-    }
-    const lower = token.toLowerCase();
-    if (spec.exactFlags.has(lower)) {
+      const nextToken = argv[idx + 1]?.trim();
+      if (!nextToken) {
+        return null;
+      }
       return {
         executable,
         normalizedExecutable: normalizeExecutableToken(executable),
-        flag: lower,
+        flag: "<program>",
         argv,
       };
     }
-    if (spec.prefixFlags?.some((prefix) => lower.startsWith(prefix))) {
-      return {
-        executable,
-        normalizedExecutable: normalizeExecutableToken(executable),
-        flag: lower,
-        argv,
-      };
+    if (positionalSpec.fileFlags.has(token)) {
+      return null;
     }
+    if (
+      positionalSpec.fileFlagPrefixes?.some(
+        (prefix) => token.startsWith(prefix) && token.length > prefix.length,
+      )
+    ) {
+      return null;
+    }
+    if (positionalSpec.exactValueFlags.has(token)) {
+      idx += 1;
+      continue;
+    }
+    if (
+      positionalSpec.prefixValueFlags?.some(
+        (prefix) => token.startsWith(prefix) && token.length > prefix.length,
+      )
+    ) {
+      continue;
+    }
+    if (token.startsWith("-")) {
+      continue;
+    }
+    return {
+      executable,
+      normalizedExecutable: normalizeExecutableToken(executable),
+      flag: "<program>",
+      argv,
+    };
   }
   return null;
 }

 export function describeInterpreterInlineEval(hit: InterpreterInlineEvalHit): string {
+  if (hit.flag === "<program>") {
+    return `${hit.normalizedExecutable} inline program`;
+  }
   return `${hit.normalizedExecutable} ${hit.flag}`;
 }

@@ -93,11 +190,11 @@ export function isInterpreterLikeAllowlistPattern(pattern: string | undefined |
     return false;
   }
   const normalized = normalizeExecutableToken(trimmed);
-  if (INTERPRETER_INLINE_EVAL_NAMES.has(normalized)) {
+  if (INTERPRETER_ALLOWLIST_NAMES.has(normalized)) {
     return true;
   }
   const basename = trimmed.replace(/\\/g, "/").split("/").pop() ?? trimmed;
   const withoutExe = basename.endsWith(".exe") ? basename.slice(0, -4) : basename;
   const strippedWildcards = withoutExe.replace(/[*?[\]{}()]/g, "");
-  return INTERPRETER_INLINE_EVAL_NAMES.has(strippedWildcards);
+  return INTERPRETER_ALLOWLIST_NAMES.has(strippedWildcards);
 }
diff --git a/src/security/audit.test.ts b/src/security/audit.test.ts
index c45d8f6a408e..8397ebd02ba2 100644
--- a/src/security/audit.test.ts
+++ b/src/security/audit.test.ts
@@ -909,7 +909,7 @@ description: test skill
           allowlist: [{ pattern: "/usr/bin/python3" }],
         },
         ops: {
-          allowlist: [{ pattern: "/usr/local/bin/node" }],
+          allowlist: [{ pattern: "/usr/local/bin/awk" }],
         },
       },
     });

PATCH

echo "Gold patch applied successfully"
