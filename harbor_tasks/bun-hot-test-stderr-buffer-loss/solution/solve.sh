#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Check if already applied (look for the driveErrorReloadCycle helper)
if grep -q 'driveErrorReloadCycle' test/cli/hot/hot.test.ts 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/test/cli/hot/hot.test.ts b/test/cli/hot/hot.test.ts
index 1a4ad85951a..3e3f4b32789 100644
--- a/test/cli/hot/hot.test.ts
+++ b/test/cli/hot/hot.test.ts
@@ -7,6 +7,84 @@ import { join } from "path";
 const timeout = isDebug ? Infinity : 10_000;
 const longTimeout = isDebug ? Infinity : 30_000;

+/**
+ * Helper to parse stderr from a --hot process that throws errors.
+ * Drives the reload cycle: reads error lines from stderr, verifies them,
+ * and calls onReload to trigger the next file change.
+ *
+ * This fixes the original `continue outer` pattern which discarded any
+ * remaining buffered lines from the current chunk when a duplicate error
+ * was encountered, potentially losing data and causing test hangs.
+ */
+async function driveErrorReloadCycle(
+  runner: ReturnType<typeof spawn>,
+  opts: {
+    targetCount: number;
+    onReload: (counter: number) => void;
+    verifyLine?: (errorLine: string, nextLine: string | undefined, counter: number) => void;
+  },
+): Promise<number> {
+  const { targetCount, onReload, verifyLine } = opts;
+  let reloadCounter = 0;
+  let str = "";
+
+  for await (const chunk of runner.stderr) {
+    str += new TextDecoder().decode(chunk);
+    // Need at least one error line followed by a newline, then another line followed by a newline
+    if (!/error: .*[0-9]\n.*?\n/g.test(str)) continue;
+
+    const lines = str.split("\n");
+    // Preserve trailing partial line for the next chunk
+    str = lines.pop() ?? "";
+    let triggered = false;
+
+    for (let i = 0; i < lines.length; i++) {
+      const line = lines[i];
+      if (!line.includes("error:")) continue;
+
+      if (reloadCounter >= targetCount) {
+        runner.kill();
+        return reloadCounter;
+      }
+
+      // If we see the previous error repeated, the pending reload hasn't
+      // taken effect yet. Re-save the file and put remaining unprocessed
+      // lines back into the buffer so they aren't lost.
+      if (line.includes(`error: ${reloadCounter - 1}`)) {
+        const remaining = lines.slice(i + 1).join("\n");
+        if (remaining) {
+          str = `${remaining}\n${str}`;
+        }
+        onReload(reloadCounter);
+        triggered = false; // onReload already called; skip post-loop call
+        break;
+      }
+
+      expect(line).toContain(`error: ${reloadCounter}`);
+
+      const nextLine = lines[i + 1];
+      if (verifyLine) {
+        verifyLine(line, nextLine, reloadCounter);
+        i++; // Skip the next line (stack trace)
+      }
+
+      reloadCounter++;
+      triggered = true;
+
+      if (reloadCounter >= targetCount) {
+        runner.kill();
+        return reloadCounter;
+      }
+    }
+
+    if (triggered) {
+      onReload(reloadCounter);
+    }
+  }
+
+  return reloadCounter;
+}
+
 let hotRunnerRoot: string = "",
   cwd = "";
 beforeEach(() => {
@@ -414,7 +492,8 @@ it(
   timeout,
 );

-const comment_spam = ("//" + "B".repeat(2000) + "\n").repeat(1000);
+const comment_line = "//" + Buffer.alloc(2000, "B").toString() + "\n";
+const comment_spam = Buffer.alloc(comment_line.length * 1000, comment_line).toString();
 it(
   "should work with sourcemap generation",
   async () => {
@@ -432,50 +511,24 @@ throw new Error('0');`,
       stderr: "pipe",
       stdin: "ignore",
     });
-    let reloadCounter = 0;
-    function onReload() {
-      writeFileSync(
-        hotRunnerRoot,
-        `// source content
+    const reloadCounter = await driveErrorReloadCycle(runner, {
+      targetCount: 50,
+      onReload: counter => {
+        writeFileSync(
+          hotRunnerRoot,
+          `// source content
 ${comment_spam}
-${" ".repeat(reloadCounter * 2)}throw new Error(${reloadCounter});`,
-      );
-    }
-    let str = "";
-    outer: for await (const chunk of runner.stderr) {
-      str += new TextDecoder().decode(chunk);
-      var any = false;
-      if (!/error: .*[0-9]\n.*?\n/g.test(str)) continue;
-
-      let it = str.split("\n");
-      let line;
-      while ((line = it.shift())) {
-        if (!line.includes("error:")) continue;
-        str = "";
-
-        if (reloadCounter === 50) {
-          runner.kill();
-          break;
-        }
-
-        if (line.includes(`error: ${reloadCounter - 1}`)) {
-          onReload(); // re-save file to prevent deadlock
-          continue outer;
-        }
-        expect(line).toContain(`error: ${reloadCounter}`);
-        reloadCounter++;
-
-        let next = it.shift()!;
-        if (!next) throw new Error(line);
-        const match = next.match(/\s*at.*?:1003:(\d+)$/);
-        if (!match) throw new Error("invalid string: " + next);
+${Buffer.alloc(counter * 2, " ").toString()}throw new Error(${counter});`,
+        );
+      },
+      verifyLine: (errorLine, nextLine, counter) => {
+        if (!nextLine) throw new Error(errorLine);
+        const match = nextLine.match(/\s*at.*?:1003:(\d+)$/);
+        if (!match) throw new Error("invalid string: " + nextLine);
         const col = match[1];
-        expect(Number(col)).toBe(1 + "throw new ".length + (reloadCounter - 1) * 2);
-        any = true;
-      }
-
-      if (any) await onReload();
-    }
+        expect(Number(col)).toBe(1 + "throw new ".length + counter * 2);
+      },
+    });
     await runner.exited;
     expect(reloadCounter).toBe(50);
   },
@@ -498,8 +551,8 @@ throw new Error('0');`,
       cmd: [bunExe(), "build", "--watch", bundleIn, "--target=bun", "--sourcemap=inline", "--outfile", hotRunnerRoot],
       env: bunEnv,
       cwd,
-      stdout: "inherit",
-      stderr: "inherit",
+      stdout: "ignore",
+      stderr: "ignore",
       stdin: "ignore",
     });
     waitForFileToExist(hotRunnerRoot, 20);
@@ -511,57 +564,42 @@ throw new Error('0');`,
       stderr: "pipe",
       stdin: "ignore",
     });
-    let reloadCounter = 0;
-    function onReload() {
-      writeFileSync(
-        bundleIn,
-        `// source content
+    let done = false;
+    const reloadCounter = await Promise.race([
+      driveErrorReloadCycle(runner, {
+        targetCount: 50,
+        onReload: counter => {
+          writeFileSync(
+            bundleIn,
+            `// source content
 // etc etc
 // etc etc
-${" ".repeat(reloadCounter * 2)}throw new Error(${reloadCounter});`,
-      );
-    }
-    let str = "";
-    outer: for await (const chunk of runner.stderr) {
-      const s = new TextDecoder().decode(chunk);
-      str += s;
-      var any = false;
-      if (!/error: .*[0-9]\n.*?\n/g.test(str)) continue;
-
-      let it = str.split("\n");
-      let line;
-      while ((line = it.shift())) {
-        if (!line.includes("error:")) continue;
-        str = "";
-
-        if (reloadCounter === 50) {
-          runner.kill();
-          break;
-        }
-
-        if (line.includes(`error: ${reloadCounter - 1}`)) {
-          onReload(); // re-save file to prevent deadlock
-          continue outer;
-        }
-        expect(line).toContain(`error: ${reloadCounter}`);
-        reloadCounter++;
-
-        let next = it.shift()!;
-        expect(next).toInclude("bundle_in.ts");
-        const col = next.match(/\s*at.*?:4:(\d+)$/)![1];
-        expect(Number(col)).toBe(1 + "throw ".length + (reloadCounter - 1) * 2);
-        any = true;
-      }
-
-      if (any) await onReload();
-    }
+${Buffer.alloc(counter * 2, " ").toString()}throw new Error(${counter});`,
+          );
+        },
+        verifyLine: (_errorLine, nextLine, counter) => {
+          if (!nextLine) throw new Error(_errorLine);
+          expect(nextLine).toInclude("bundle_in.ts");
+          const match = nextLine.match(/\s*at.*?:4:(\d+)$/);
+          if (!match) throw new Error("invalid stack trace: " + nextLine);
+          const col = match[1];
+          expect(Number(col)).toBe(1 + "throw ".length + counter * 2);
+        },
+      }).finally(() => {
+        done = true;
+      }),
+      bundler.exited.then(code => {
+        if (!done) throw new Error(`bundler exited early with code ${code}`);
+        return -1; // Ignored — race already resolved
+      }),
+    ]);
     expect(reloadCounter).toBe(50);
     bundler.kill();
   },
   timeout,
 );

-const long_comment = "BBBB".repeat(100000);
+const long_comment = Buffer.alloc(400000, "BBBB").toString();

 it(
   "should work with sourcemap loading with large files",
@@ -604,68 +642,43 @@ throw new Error('0');`,
       ],
       env: bunEnv,
       cwd,
-      stdout: "inherit",
+      stdout: "ignore",
       stderr: "pipe",
       stdin: "ignore",
     });
-    let reloadCounter = 0;
-    function onReload() {
-      writeFileSync(
-        bundleIn,
-        `// ${long_comment}
+    let done2 = false;
+    const reloadCounter = await Promise.race([
+      driveErrorReloadCycle(runner, {
+        targetCount: 50,
+        onReload: counter => {
+          writeFileSync(
+            bundleIn,
+            `// ${long_comment}
 console.error("RSS: %s", process.memoryUsage().rss);
 //
-${" ".repeat(reloadCounter * 2)}throw new Error(${reloadCounter});`,
-      );
-    }
-    let str = "";
-    let sampleMemory10: number | undefined;
-    let sampleMemory100: number | undefined;
-    outer: for await (const chunk of runner.stderr) {
-      str += new TextDecoder().decode(chunk);
-      var any = false;
-      if (!/error: .*[0-9]\n.*?\n/g.test(str)) continue;
-
-      let it = str.split("\n");
-      let line;
-      while ((line = it.shift())) {
-        if (!line.includes("error:")) continue;
-        let rssMatch = str.match(/RSS: (\d+(\.\d+)?)\n/);
-        let rss;
-        if (rssMatch) rss = Number(rssMatch[1]);
-        str = "";
-
-        if (reloadCounter == 10) {
-          sampleMemory10 = rss;
-        }
-
-        if (reloadCounter >= 50) {
-          sampleMemory100 = rss;
-          runner.kill();
-          break;
-        }
-
-        if (line.includes(`error: ${reloadCounter - 1}`)) {
-          onReload(); // re-save file to prevent deadlock
-          continue outer;
-        }
-        expect(line).toContain(`error: ${reloadCounter}`);
-
-        reloadCounter++;
-        let next = it.shift()!;
-        expect(next).toInclude("bundle_in.ts");
-        const col = next.match(/\s*at.*?:4:(\d+)$/)![1];
-        expect(Number(col)).toBe(1 + "throw ".length + (reloadCounter - 1) * 2);
-        any = true;
-      }
-
-      if (any) await onReload();
-    }
+${Buffer.alloc(counter * 2, " ").toString()}throw new Error(${counter});`,
+          );
+        },
+        verifyLine: (_errorLine, nextLine, counter) => {
+          if (!nextLine) throw new Error(_errorLine);
+          expect(nextLine).toInclude("bundle_in.ts");
+          const match = nextLine.match(/\s*at.*?:4:(\d+)$/);
+          if (!match) throw new Error("invalid stack trace: " + nextLine);
+          const col = match[1];
+          expect(Number(col)).toBe(1 + "throw ".length + counter * 2);
+        },
+      }).finally(() => {
+        done2 = true;
+      }),
+      bundler.exited.then(code => {
+        if (!done2) throw new Error(`bundler exited early with code ${code}`);
+        return -1; // Ignored — race already resolved
+      }),
+    ]);
     expect(reloadCounter).toBe(50);
     bundler.kill();
     await runner.exited;
     // TODO: bun has a memory leak when --hot is used on very large files
-    // console.log({ sampleMemory10, sampleMemory100 });
   },
   longTimeout,
 );

PATCH
