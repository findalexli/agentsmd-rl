#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-boilerplate

# Idempotency guard
if grep -qF "function updateUser(id: string, data: UpdateUserInput): Promise<User> { ... }" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -203,9 +203,70 @@ Before adopting any new technology:
 **Rules:**
 - Always use `strict: true`
 - Prefer `type` over `interface` (unless extending)
-- Never use `any` - use `unknown` with type guards
 - Use Zod for runtime validation
 
+#### Type Safety Requirements (STRICT)
+
+| Type | Status | Guideline |
+|------|--------|-----------|
+| `any` | **BANNED** | Never use `any` under any circumstances |
+| `unknown` | Allowed (avoid) | Acceptable but prefer explicit types |
+| Explicit types | **PREFERRED** | Always use concrete, specific types |
+
+**`any` Type - ABSOLUTE BAN:**
+```typescript
+// ❌ BANNED - No exceptions, including test files
+function process(data: any) { ... }
+const result: any = fetchData();
+(value as any).property  // Type casting to any
+
+// ❌ BANNED - Even in test files
+const mockData: any = { ... };
+expect(result as any).toBe(...);
+```
+
+**`unknown` Type - Use Sparingly:**
+```typescript
+// ⚠️ ACCEPTABLE but avoid when possible
+function parseJson(input: string): unknown {
+  return JSON.parse(input);
+}
+
+// ✅ PREFERRED - Use type guards with unknown
+function isUser(value: unknown): value is User {
+  return typeof value === "object" && value !== null && "id" in value;
+}
+
+// ✅ BEST - Use explicit types with validation
+function parseUser(input: string): User {
+  const data = JSON.parse(input);
+  return userSchema.parse(data);  // Zod validation
+}
+```
+
+**Explicit Types - ALWAYS PREFERRED:**
+```typescript
+// ✅ CORRECT - Explicit return types
+function getUser(id: string): Promise<User> { ... }
+
+// ✅ CORRECT - Explicit parameter types
+function updateUser(id: string, data: UpdateUserInput): Promise<User> { ... }
+
+// ✅ CORRECT - Explicit variable types when inference is unclear
+const users: User[] = [];
+const config: AppConfig = loadConfig();
+```
+
+**Handling Third-Party Libraries:**
+```typescript
+// If library returns any, immediately type it
+const response = await fetch(url);
+const data: UserResponse = await response.json();  // Type immediately
+
+// Use Zod for runtime validation of external data
+const validatedData = userResponseSchema.parse(data);
+```
+
 ### 3.2 Python
 
 ```toml
PATCH

echo "Gold patch applied."
