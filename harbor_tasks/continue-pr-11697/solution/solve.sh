#!/bin/bash
set -e
cd /workspace/continue

# Apply the fix patch
git apply <<'PATCH'
diff --git a/extensions/cli/src/commands/review/resolveReviews.test.ts b/extensions/cli/src/commands/review/resolveReviews.test.ts
new file mode 100644
index 00000000000..c8fa38a796b
--- /dev/null
+++ b/extensions/cli/src/commands/review/resolveReviews.test.ts
@@ -0,0 +1,121 @@
+import * as fs from "fs";
+import * as path from "path";
+
+import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
+
+import { resolveReviews } from "./resolveReviews.js";
+
+vi.mock("../../auth/workos.js", () => ({
+  loadAuthConfig: vi.fn(() => null),
+  getAccessToken: vi.fn(() => null),
+}));
+
+vi.mock("../../env.js", () => ({
+  env: { apiBase: "https://api.continue.dev" },
+}));
+
+vi.mock("../../util/logger.js", () => ({
+  logger: { debug: vi.fn() },
+}));
+
+vi.mock("fs", async () => {
+  const actual = await vi.importActual("fs");
+  return {
+    ...actual,
+    existsSync: vi.fn(),
+    readdirSync: vi.fn(),
+  };
+});
+
+describe("resolveReviews local discovery", () => {
+  const originalCwd = process.cwd;
+
+  beforeEach(() => {
+    process.cwd = () => "/test/repo";
+    vi.mocked(fs.existsSync).mockReturnValue(false);
+    vi.mocked(fs.readdirSync).mockReturnValue([]);
+  });
+
+  afterEach(() => {
+    process.cwd = originalCwd;
+    vi.restoreAllMocks();
+  });
+
+  it("discovers files from .continue/agents/", async () => {
+    vi.mocked(fs.existsSync).mockImplementation((p) => {
+      return p === path.join("/test/repo", ".continue", "agents");
+    });
+    vi.mocked(fs.readdirSync).mockImplementation(((p: fs.PathLike) => {
+      if (p === path.join("/test/repo", ".continue", "agents")) {
+        return ["security-review.md", "style-check.md"];
+      }
+      return [];
+    }) as typeof fs.readdirSync);
+
+    const reviews = await resolveReviews();
+    expect(reviews).toHaveLength(2);
+    expect(reviews[0].name).toBe("security review");
+    expect(reviews[0].sourceType).toBe("local");
+    expect(reviews[0].source).toContain("agents");
+  });
+
+  it("discovers files from .continue/checks/", async () => {
+    vi.mocked(fs.existsSync).mockImplementation((p) => {
+      return p === path.join("/test/repo", ".continue", "checks");
+    });
+    vi.mocked(fs.readdirSync).mockImplementation(((p: fs.PathLike) => {
+      if (p === path.join("/test/repo", ".continue", "checks")) {
+        return ["anti-slop.md"];
+      }
+      return [];
+    }) as typeof fs.readdirSync);
+
+    const reviews = await resolveReviews();
+    expect(reviews).toHaveLength(1);
+    expect(reviews[0].name).toBe("anti slop");
+    expect(reviews[0].source).toContain("checks");
+  });
+
+  it("discovers files from both directories without duplicates", async () => {
+    vi.mocked(fs.existsSync).mockReturnValue(true);
+    vi.mocked(fs.readdirSync).mockImplementation(((p: fs.PathLike) => {
+      const dir = String(p);
+      if (dir.endsWith("agents")) {
+        return ["security-review.md", "shared.md"];
+      }
+      if (dir.endsWith("checks")) {
+        return ["anti-slop.md", "shared.md"];
+      }
+      return [];
+    }) as typeof fs.readdirSync);
+
+    const reviews = await resolveReviews();
+    // agents/security-review.md, agents/shared.md, checks/anti-slop.md
+    // checks/shared.md is skipped (duplicate filename, agents/ takes precedence)
+    expect(reviews).toHaveLength(3);
+    const names = reviews.map((r) => r.name);
+    expect(names).toContain("security review");
+    expect(names).toContain("shared");
+    expect(names).toContain("anti slop");
+
+    // The "shared" entry should come from agents/, not checks/
+    const shared = reviews.find((r) => r.name === "shared");
+    expect(shared?.source).toContain("agents");
+  });
+
+  it("returns empty array when neither directory exists", async () => {
+    vi.mocked(fs.existsSync).mockReturnValue(false);
+    const reviews = await resolveReviews();
+    expect(reviews).toHaveLength(0);
+  });
+
+  it("handles directory read errors gracefully", async () => {
+    vi.mocked(fs.existsSync).mockReturnValue(true);
+    vi.mocked(fs.readdirSync).mockImplementation(() => {
+      throw new Error("Permission denied");
+    });
+
+    const reviews = await resolveReviews();
+    expect(reviews).toHaveLength(0);
+  });
+});
diff --git a/extensions/cli/src/commands/review/resolveReviews.ts b/extensions/cli/src/commands/review/resolveReviews.ts
index 1763b866d0f..32e595b345a 100644
--- a/extensions/cli/src/commands/review/resolveReviews.ts
+++ b/extensions/cli/src/commands/review/resolveReviews.ts
@@ -19,7 +19,7 @@ export interface ResolvedReview {
  * Determine which reviews to run, using three sources in order:
  * 1. CLI --agent flags (highest priority)
  * 2. Hub API (if logged in and no --agent flags)
- * 3. Local .continue/agents/*.md (fallback)
+ * 3. Local .continue/agents/*.md and .continue/checks/*.md (fallback)
  */
 export async function resolveReviews(
   agentFlags?: string[],
@@ -39,7 +39,7 @@ export async function resolveReviews(
     return hubReviews;
   }

-  // Source 3: Local .continue/agents/*.md
+  // Source 3: Local .continue/agents/*.md and .continue/checks/*.md
   const localReviews = resolveFromLocal();
   if (localReviews.length > 0) {
     return localReviews;
@@ -107,24 +107,41 @@ async function resolveFromHub(): Promise<ResolvedReview[]> {
 }

 /**
- * Resolve reviews from local .continue/agents/*.md files.
+ * Resolve reviews from local .continue/agents/*.md and .continue/checks/*.md files.
+ * Agents take precedence over checks if the same filename exists in both directories.
  */
 function resolveFromLocal(): ResolvedReview[] {
-  const agentsDir = path.join(process.cwd(), ".continue", "agents");
-  if (!fs.existsSync(agentsDir)) {
-    return [];
+  const cwd = process.cwd();
+  const dirs = [
+    path.join(cwd, ".continue", "agents"),
+    path.join(cwd, ".continue", "checks"),
+  ];
+
+  const seen = new Set<string>();
+  const results: ResolvedReview[] = [];
+
+  for (const dir of dirs) {
+    if (!fs.existsSync(dir)) {
+      continue;
+    }
+    try {
+      const files = fs.readdirSync(dir).filter((f) => f.endsWith(".md"));
+      for (const file of files) {
+        if (!seen.has(file)) {
+          seen.add(file);
+          results.push({
+            name: path.basename(file, ".md").replace(/[-_]/g, " "),
+            source: path.join(dir, file),
+            sourceType: "local" as const,
+          });
+        }
+      }
+    } catch {
+      // Directory read failed, skip
+    }
   }

-  try {
-    const files = fs.readdirSync(agentsDir).filter((f) => f.endsWith(".md"));
-    return files.map((file) => ({
-      name: path.basename(file, ".md").replace(/[-_]/g, " "),
-      source: path.join(agentsDir, file),
-      sourceType: "local" as const,
-    }));
-  } catch {
-    return [];
-  }
+  return results;
 }

 function isLocalPath(agent: string): boolean {
PATCH

# Idempotency check — look for a distinctive line from the patch
grep -q "continue/checks" extensions/cli/src/commands/review/resolveReviews.ts && echo "Patch applied successfully"
