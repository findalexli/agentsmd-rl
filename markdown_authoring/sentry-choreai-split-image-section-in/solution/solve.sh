#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sentry

# Idempotency guard
if grep -qF "Use the core avatar components (<UserAvatar/>, <TeamAvatar/>, <ProjectAvatar/>, " "static/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/static/AGENTS.md b/static/AGENTS.md
@@ -302,6 +302,27 @@ function Content() {
 }
 ```
 
+##### Splitting layout and typography
+
+- Split Layout from Typography by directly using Flex, Grid, Stack or Container and Text or Heading components
+
+```tsx
+// ❌ Do not couple typography with layout
+const Component = styled('div')`
+  display: flex;
+  flex-directon: column;
+  color: ${p => p.theme.subText};
+  font-size: ${p => p.theme.fontSize.lg};
+`;
+
+// ✅ Use the Layout primitives and Text component
+<Flex direction="column">
+  <Text muted size="lg">...</Text>
+<Flex>
+```
+
+#### Assets
+
 ##### Image
 
 Use the core component <Image/> from `sentry/components/core/image` instead of intrinsic <img />.
@@ -325,21 +346,36 @@ function Component() {
 }
 ```
 
-##### Splitting layout and typography
+##### Avatars
 
-- Split Layout from Typography by directly using Flex, Grid, Stack or Container and Text or Heading components
+Use the core avatar components (<UserAvatar/>, <TeamAvatar/>, <ProjectAvatar/>, <OrganizationAvatar/>, <SentryAppAvatar/>, <DocIntegrationAvatar/>) from `static/app/components/core/avatar` for avatars.
 
 ```tsx
-// ❌ Do not couple typography with layout
-const Component = styled('div')`
-  display: flex;
-  flex-directon: column;
-  color: ${p => p.theme.subText};
-  font-size: ${p => p.theme.fontSize.lg};
-`;
+// ✅ Use Image component and src loader
+import {UserAvatar} from 'sentry/components/core/avatar/userAvatar';
+import {useUser} from 'sentry/utils/useUser';
 
-// ✅ Use the Layout primitives and Text component
-<Flex direction="column">
-  <Text muted size="lg">...</Text>
-<Flex>
+// ❌ Do not use raw intrinsic elements or static paths
+function Component() {
+  return (
+    <img
+      src="/path/to/image.jpg"
+      style={{
+        border,
+        width: 20,
+        height: 20,
+        borderRadius: '50%',
+        objectFit: 'cover',
+        display: 'inline-block',
+      }}
+    />
+  );
+}
+
+function Component() {
+  const user = useUser();
+  return <UserAvatar user={user} />;
+}
 ```
+
+For lists of avatars, use <AvatarList>.
PATCH

echo "Gold patch applied."
