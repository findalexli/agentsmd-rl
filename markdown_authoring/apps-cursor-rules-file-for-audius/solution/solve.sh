#!/usr/bin/env bash
set -euo pipefail

cd /workspace/apps

# Idempotency guard
if grep -qF "description: TypeScript/React coding standards - prefer null coalescing, optiona" ".cursor/rules/audius-style-guide.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/audius-style-guide.mdc b/.cursor/rules/audius-style-guide.mdc
@@ -0,0 +1,53 @@
+---
+description: TypeScript/React coding standards - prefer null coalescing, optional chaining, ternaries for rendering, optional types, and organized string constants
+globs:
+alwaysApply: true
+---
+
+# TypeScript Best Practices
+
+## Null Coalescing & Optional Chaining
+
+Use `??` and `?.` instead of `&&`/`||` for null checks.
+
+```typescript
+// ✅ Good
+const value = user?.name ?? 'Anonymous'
+const displayName = user?.profile?.displayName ?? 'Unknown'
+
+// ❌ Bad
+const value = (user && user.name) || 'Anonymous'
+const displayName =
+  (user && user.profile && user.profile.displayName) || 'Unknown'
+```
+
+## Conditional Rendering
+
+Use ternaries instead of `&&` for JSX conditional rendering.
+
+```tsx
+// ✅ Good
+return !user ? null : <UserProfile user={user} />
+return list.length === 0 ? null : <List items={list} />
+
+// ❌ Bad
+return user && <UserProfile user={user} />
+return list.length && <List items={list} />
+```
+
+## String Constants
+
+Organize user-facing strings in a `messages` object at the top of components.
+
+```tsx
+// ✅ Good
+const messages = {
+  title: 'Welcome',
+  error: 'Something went wrong'
+}
+
+return <h1>{messages.title}</h1>
+
+// ❌ Bad
+return <h1>Welcome</h1>
+```
PATCH

echo "Gold patch applied."
