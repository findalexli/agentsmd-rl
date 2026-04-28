#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lago-front

# Idempotency guard
if grep -qF "const role = isAdmin ? (isManager ? \"Manager\" : \"Admin\") : \"User\";" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -104,6 +104,82 @@ const calculateTotal = (items: Item[]): number => {
 }
 ```
 
+### No Nested Ternary
+
+Prevent anything deeper than 2 levels.
+
+```tsx
+// ❌ Bad
+const role = isAdmin ? (isManager ? "Manager" : "Admin") : "User";
+
+// ✅ Good
+function getRole(): string {
+  if (!isAdmin) return "User"
+  if (isManager) return "Manager"
+
+  return "Admin"
+}
+
+const role = getRole()
+```
+
+### Prefer Early Returns
+
+Makes the code way more readable.
+
+```tsx
+// ❌ Bad
+function getStatus(user) {
+  let status;
+  if (user.isActive) {
+    if (user.isAdmin) {
+      status = "Admin";
+    } else {
+      status = "Active";
+    }
+  } else {
+    status = "Inactive";
+  }
+  return status;
+}
+
+// ✅ Good
+function getStatus(user) {
+  if (!user.isActive) return "Inactive";
+  if (user.isAdmin) return "Admin";
+  return "Active";
+}
+```
+
+### Prefer Logic Out of JSX
+
+Extract any logic above, when it starts to be complex.
+
+```tsx
+// ❌ Bad
+return (
+  <div>
+    {score > 80 ? "High" : score > 50 ? "Medium" : "Low"}
+  </div>
+);
+
+// ✅ Good
+let label;
+if (score > 80) {
+  label = "High";
+} else if (score > 50) {
+  label = "Medium";
+} else {
+  label = "Low";
+}
+
+return (
+  <div>
+    {label}
+  </div>
+);
+```
+
 ## Documentation & Library References
 
 ### Using Context7 MCP (If Installed)
PATCH

echo "Gold patch applied."
