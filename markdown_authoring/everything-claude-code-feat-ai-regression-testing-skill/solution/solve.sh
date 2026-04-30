#!/usr/bin/env bash
set -euo pipefail

cd /workspace/everything-claude-code

# Idempotency guard
if grep -qF "description: Regression testing strategies for AI-assisted development. Sandbox-" "skills/ai-regression-testing/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/ai-regression-testing/SKILL.md b/skills/ai-regression-testing/SKILL.md
@@ -0,0 +1,385 @@
+---
+name: ai-regression-testing
+description: Regression testing strategies for AI-assisted development. Sandbox-mode API testing without database dependencies, automated bug-check workflows, and patterns to catch AI blind spots where the same model writes and reviews code.
+origin: ECC
+---
+
+# AI Regression Testing
+
+Testing patterns specifically designed for AI-assisted development, where the same model writes code and reviews it — creating systematic blind spots that only automated tests can catch.
+
+## When to Activate
+
+- AI agent (Claude Code, Cursor, Codex) has modified API routes or backend logic
+- A bug was found and fixed — need to prevent re-introduction
+- Project has a sandbox/mock mode that can be leveraged for DB-free testing
+- Running `/bug-check` or similar review commands after code changes
+- Multiple code paths exist (sandbox vs production, feature flags, etc.)
+
+## The Core Problem
+
+When an AI writes code and then reviews its own work, it carries the same assumptions into both steps. This creates a predictable failure pattern:
+
+```
+AI writes fix → AI reviews fix → AI says "looks correct" → Bug still exists
+```
+
+**Real-world example** (observed in production):
+
+```
+Fix 1: Added notification_settings to API response
+  → Forgot to add it to the SELECT query
+  → AI reviewed and missed it (same blind spot)
+
+Fix 2: Added it to SELECT query
+  → TypeScript build error (column not in generated types)
+  → AI reviewed Fix 1 but didn't catch the SELECT issue
+
+Fix 3: Changed to SELECT *
+  → Fixed production path, forgot sandbox path
+  → AI reviewed and missed it AGAIN (4th occurrence)
+
+Fix 4: Test caught it instantly on first run ✅
+```
+
+The pattern: **sandbox/production path inconsistency** is the #1 AI-introduced regression.
+
+## Sandbox-Mode API Testing
+
+Most projects with AI-friendly architecture have a sandbox/mock mode. This is the key to fast, DB-free API testing.
+
+### Setup (Vitest + Next.js App Router)
+
+```typescript
+// vitest.config.ts
+import { defineConfig } from "vitest/config";
+import path from "path";
+
+export default defineConfig({
+  test: {
+    environment: "node",
+    globals: true,
+    include: ["__tests__/**/*.test.ts"],
+    setupFiles: ["__tests__/setup.ts"],
+  },
+  resolve: {
+    alias: {
+      "@": path.resolve(__dirname, "."),
+    },
+  },
+});
+```
+
+```typescript
+// __tests__/setup.ts
+// Force sandbox mode — no database needed
+process.env.SANDBOX_MODE = "true";
+process.env.NEXT_PUBLIC_SUPABASE_URL = "";
+process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY = "";
+```
+
+### Test Helper for Next.js API Routes
+
+```typescript
+// __tests__/helpers.ts
+import { NextRequest } from "next/server";
+
+export function createTestRequest(
+  url: string,
+  options?: {
+    method?: string;
+    body?: Record<string, unknown>;
+    headers?: Record<string, string>;
+    sandboxUserId?: string;
+  },
+): NextRequest {
+  const { method = "GET", body, headers = {}, sandboxUserId } = options || {};
+  const fullUrl = url.startsWith("http") ? url : `http://localhost:3000${url}`;
+  const reqHeaders: Record<string, string> = { ...headers };
+
+  if (sandboxUserId) {
+    reqHeaders["x-sandbox-user-id"] = sandboxUserId;
+  }
+
+  const init: { method: string; headers: Record<string, string>; body?: string } = {
+    method,
+    headers: reqHeaders,
+  };
+
+  if (body) {
+    init.body = JSON.stringify(body);
+    reqHeaders["content-type"] = "application/json";
+  }
+
+  return new NextRequest(fullUrl, init);
+}
+
+export async function parseResponse(response: Response) {
+  const json = await response.json();
+  return { status: response.status, json };
+}
+```
+
+### Writing Regression Tests
+
+The key principle: **write tests for bugs that were found, not for code that works**.
+
+```typescript
+// __tests__/api/user/profile.test.ts
+import { describe, it, expect } from "vitest";
+import { createTestRequest, parseResponse } from "../../helpers";
+import { GET, PATCH } from "@/app/api/user/profile/route";
+
+// Define the contract — what fields MUST be in the response
+const REQUIRED_FIELDS = [
+  "id",
+  "email",
+  "full_name",
+  "phone",
+  "role",
+  "created_at",
+  "avatar_url",
+  "notification_settings",  // ← Added after bug found it missing
+];
+
+describe("GET /api/user/profile", () => {
+  it("returns all required fields", async () => {
+    const req = createTestRequest("/api/user/profile");
+    const res = await GET(req);
+    const { status, json } = await parseResponse(res);
+
+    expect(status).toBe(200);
+    for (const field of REQUIRED_FIELDS) {
+      expect(json.data).toHaveProperty(field);
+    }
+  });
+
+  // Regression test — this exact bug was introduced by AI 4 times
+  it("notification_settings is not undefined (BUG-R1 regression)", async () => {
+    const req = createTestRequest("/api/user/profile");
+    const res = await GET(req);
+    const { json } = await parseResponse(res);
+
+    expect("notification_settings" in json.data).toBe(true);
+    const ns = json.data.notification_settings;
+    expect(ns === null || typeof ns === "object").toBe(true);
+  });
+});
+```
+
+### Testing Sandbox/Production Parity
+
+The most common AI regression: fixing production path but forgetting sandbox path (or vice versa).
+
+```typescript
+// Test that sandbox responses match the expected contract
+describe("GET /api/user/messages (conversation list)", () => {
+  it("includes partner_name in sandbox mode", async () => {
+    const req = createTestRequest("/api/user/messages", {
+      sandboxUserId: "user-001",
+    });
+    const res = await GET(req);
+    const { json } = await parseResponse(res);
+
+    // This caught a bug where partner_name was added
+    // to production path but not sandbox path
+    if (json.data.length > 0) {
+      for (const conv of json.data) {
+        expect("partner_name" in conv).toBe(true);
+      }
+    }
+  });
+});
+```
+
+## Integrating Tests into Bug-Check Workflow
+
+### Custom Command Definition
+
+```markdown
+<!-- .claude/commands/bug-check.md -->
+# Bug Check
+
+## Step 1: Automated Tests (mandatory, cannot skip)
+
+Run these commands FIRST before any code review:
+
+    npm run test       # Vitest test suite
+    npm run build      # TypeScript type check + build
+
+- If tests fail → report as highest priority bug
+- If build fails → report type errors as highest priority
+- Only proceed to Step 2 if both pass
+
+## Step 2: Code Review (AI review)
+
+1. Sandbox / production path consistency
+2. API response shape matches frontend expectations
+3. SELECT clause completeness
+4. Error handling with rollback
+5. Optimistic update race conditions
+
+## Step 3: For each bug fixed, propose a regression test
+```
+
+### The Workflow
+
+```
+User: "バグチェックして" (or "/bug-check")
+  │
+  ├─ Step 1: npm run test
+  │   ├─ FAIL → Bug found mechanically (no AI judgment needed)
+  │   └─ PASS → Continue
+  │
+  ├─ Step 2: npm run build
+  │   ├─ FAIL → Type error found mechanically
+  │   └─ PASS → Continue
+  │
+  ├─ Step 3: AI code review (with known blind spots in mind)
+  │   └─ Findings reported
+  │
+  └─ Step 4: For each fix, write a regression test
+      └─ Next bug-check catches if fix breaks
+```
+
+## Common AI Regression Patterns
+
+### Pattern 1: Sandbox/Production Path Mismatch
+
+**Frequency**: Most common (observed in 3 out of 4 regressions)
+
+```typescript
+// ❌ AI adds field to production path only
+if (isSandboxMode()) {
+  return { data: { id, email, name } };  // Missing new field
+}
+// Production path
+return { data: { id, email, name, notification_settings } };
+
+// ✅ Both paths must return the same shape
+if (isSandboxMode()) {
+  return { data: { id, email, name, notification_settings: null } };
+}
+return { data: { id, email, name, notification_settings } };
+```
+
+**Test to catch it**:
+
+```typescript
+it("sandbox and production return same fields", async () => {
+  // In test env, sandbox mode is forced ON
+  const res = await GET(createTestRequest("/api/user/profile"));
+  const { json } = await parseResponse(res);
+
+  for (const field of REQUIRED_FIELDS) {
+    expect(json.data).toHaveProperty(field);
+  }
+});
+```
+
+### Pattern 2: SELECT Clause Omission
+
+**Frequency**: Common with Supabase/Prisma when adding new columns
+
+```typescript
+// ❌ New column added to response but not to SELECT
+const { data } = await supabase
+  .from("users")
+  .select("id, email, name")  // notification_settings not here
+  .single();
+
+return { data: { ...data, notification_settings: data.notification_settings } };
+// → notification_settings is always undefined
+
+// ✅ Use SELECT * or explicitly include new columns
+const { data } = await supabase
+  .from("users")
+  .select("*")
+  .single();
+```
+
+### Pattern 3: Error State Leakage
+
+**Frequency**: Moderate — when adding error handling to existing components
+
+```typescript
+// ❌ Error state set but old data not cleared
+catch (err) {
+  setError("Failed to load");
+  // reservations still shows data from previous tab!
+}
+
+// ✅ Clear related state on error
+catch (err) {
+  setReservations([]);  // Clear stale data
+  setError("Failed to load");
+}
+```
+
+### Pattern 4: Optimistic Update Without Proper Rollback
+
+```typescript
+// ❌ No rollback on failure
+const handleRemove = async (id: string) => {
+  setItems(prev => prev.filter(i => i.id !== id));
+  await fetch(`/api/items/${id}`, { method: "DELETE" });
+  // If API fails, item is gone from UI but still in DB
+};
+
+// ✅ Capture previous state and rollback on failure
+const handleRemove = async (id: string) => {
+  const prevItems = [...items];
+  setItems(prev => prev.filter(i => i.id !== id));
+  try {
+    const res = await fetch(`/api/items/${id}`, { method: "DELETE" });
+    if (!res.ok) throw new Error("API error");
+  } catch {
+    setItems(prevItems);  // Rollback
+    alert("削除に失敗しました");
+  }
+};
+```
+
+## Strategy: Test Where Bugs Were Found
+
+Don't aim for 100% coverage. Instead:
+
+```
+Bug found in /api/user/profile     → Write test for profile API
+Bug found in /api/user/messages    → Write test for messages API
+Bug found in /api/user/favorites   → Write test for favorites API
+No bug in /api/user/notifications  → Don't write test (yet)
+```
+
+**Why this works with AI development:**
+
+1. AI tends to make the **same category of mistake** repeatedly
+2. Bugs cluster in complex areas (auth, multi-path logic, state management)
+3. Once tested, that exact regression **cannot happen again**
+4. Test count grows organically with bug fixes — no wasted effort
+
+## Quick Reference
+
+| AI Regression Pattern | Test Strategy | Priority |
+|---|---|---|
+| Sandbox/production mismatch | Assert same response shape in sandbox mode | 🔴 High |
+| SELECT clause omission | Assert all required fields in response | 🔴 High |
+| Error state leakage | Assert state cleanup on error | 🟡 Medium |
+| Missing rollback | Assert state restored on API failure | 🟡 Medium |
+| Type cast masking null | Assert field is not undefined | 🟡 Medium |
+
+## DO / DON'T
+
+**DO:**
+- Write tests immediately after finding a bug (before fixing it if possible)
+- Test the API response shape, not the implementation
+- Run tests as the first step of every bug-check
+- Keep tests fast (< 1 second total with sandbox mode)
+- Name tests after the bug they prevent (e.g., "BUG-R1 regression")
+
+**DON'T:**
+- Write tests for code that has never had a bug
+- Trust AI self-review as a substitute for automated tests
+- Skip sandbox path testing because "it's just mock data"
+- Write integration tests when unit tests suffice
+- Aim for coverage percentage — aim for regression prevention
PATCH

echo "Gold patch applied."
