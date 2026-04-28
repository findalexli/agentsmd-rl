#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sentry

# Idempotency guard
if grep -qF "Use <Text> from `@sentry/scraps/text` for text styling instead of styled compone" "static/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/static/AGENTS.md b/static/AGENTS.md
@@ -107,10 +107,10 @@ Always use Core components whenever available. Avoid using Emotion (styled compo
 
 ##### Grid
 
-Use <Grid> from `sentry/components/core/layout` for elements that require grid layout as opposed to styled components with `display: grid`
+Use <Grid> from `@sentry/scraps/layout` for elements that require grid layout as opposed to styled components with `display: grid`
 
 ```tsx
-import {Grid} from 'sentry/components/core/layout';
+import {Grid} from '@sentry/scraps/layout';
 
 // ❌ Do not use styled and create a new styled component
 const Component = styled('div')`
@@ -124,10 +124,10 @@ const Component = styled('div')`
 
 ##### Flex
 
-Use <Flex> from `sentry/components/core/layout` for elements that require flex layout as opposed to styled components with `display: flex`.
+Use <Flex> from `@sentry/scraps/layout` for elements that require flex layout as opposed to styled components with `display: flex`.
 
 ```tsx
-import {Flex} from 'sentry/components/core/layout';
+import {Flex} from '@sentry/scraps/layout';
 
 // ❌ Do not use styled and create a new styled component
 const Component = styled('div')`
@@ -141,10 +141,10 @@ const Component = styled('div')`
 
 ##### Container
 
-Use using <Container> from `sentry/components/core/layout` over simple elements that require a border or border radius.
+Use using <Container> from `@sentry/scraps/layout` over simple elements that require a border or border radius.
 
 ```tsx
-import {Container} from 'sentry/components/core/layout';
+import {Container} from '@sentry/scraps/layout';
 
 // ❌ Do not use styled and create a new styled component
 const Component = styled('div')`
@@ -161,7 +161,7 @@ const Component = styled('div')`
 Use responsive props instead of styled media queries for Flex, Grid and Container.
 
 ```tsx
-import {Flex} from 'sentry/components/core/layout';
+import {Flex} from '@sentry/scraps/layout';
 
 // ❌ Do not use styled and create a new styled component
 const Component = styled('div')`
@@ -180,7 +180,7 @@ const Component = styled('div')`
 Prefer the use of gap or padding over margin.
 
 ```tsx
-import {Flex} from 'sentry/components/core/layout';
+import {Flex} from '@sentry/scraps/layout';
 
 // ❌ Do not use styled and create a new styled component
 const Component = styled('div')`
@@ -200,10 +200,10 @@ const Component = styled('div')`
 
 ##### Heading
 
-Use <Heading> from `sentry/components/core/text` for headings instead of styled components that style heading typography.
+Use <Heading> from `@sentry/scraps/text` for headings instead of styled components that style heading typography.
 
 ```tsx
-import {Heading} from 'sentry/components/core/text';
+import {Heading} from '@sentry/scraps/text';
 
 // ❌ Do not use styled and create a new styled component
 const Title = styled('h2')`
@@ -218,7 +218,7 @@ const Title = styled('h2')`
 Do not use or style h1, h2, h3, h4, h5, h6 intrinsic elements. Prefer using <Heading as="h1...h6">title</Heading> component instead
 
 ```tsx
-import {Heading} from 'sentry/components/core/text';
+import {Heading} from '@sentry/scraps/text';
 
 // ❌ Do not use styled and create a new styled component
 const Title = styled('h4')`
@@ -242,10 +242,10 @@ function Component(){
 
 ##### Text
 
-Use <Text> from `sentry/components/core/text` for text styling instead of styled components that handle typography features like color, overflow, font-size, font-weight.
+Use <Text> from `@sentry/scraps/text` for text styling instead of styled components that handle typography features like color, overflow, font-size, font-weight.
 
 ```tsx
-import {Text} from 'sentry/components/core/text';
+import {Text} from '@sentry/scraps/text';
 
 // ❌ Do not use styled and create a new styled component
 const Label = styled('span')`
@@ -262,7 +262,7 @@ const Label = styled('span')`
 Do not use or style intrinsic elements like. Prefer using <Text as="p | span | div">text...</Text> component instead
 
 ```tsx
-import {Text} from 'sentry/components/core/text';
+import {Text} from '@sentry/scraps/text';
 
 // ❌ Do not style intrinsic elements directly
 const Paragraph = styled('p')`
@@ -325,7 +325,7 @@ const Component = styled('div')`
 
 ##### Image
 
-Use the core component <Image/> from `sentry/components/core/image` instead of intrinsic <img />.
+Use the core component <Image/> from `@sentry/scraps/image` instead of intrinsic <img />.
 
 ```tsx
 // ❌ Do not use raw intrinsic elements or static paths
@@ -336,7 +336,7 @@ function Component() {
 }
 
 // ✅ Use Image component and src loader
-import {Image} from 'sentry/componetn/core/image';
+import {Image} from '@sentry/scraps/image';
 import image from 'sentry-images/example.jpg';
 
 function Component() {
@@ -351,10 +351,12 @@ function Component() {
 Use the core avatar components (<UserAvatar/>, <TeamAvatar/>, <ProjectAvatar/>, <OrganizationAvatar/>, <SentryAppAvatar/>, <DocIntegrationAvatar/>) from `static/app/components/core/avatar` for avatars.
 
 ```tsx
-// ✅ Use Image component and src loader
-import {UserAvatar} from 'sentry/components/core/avatar/userAvatar';
+// ✅ Use Avatar component and useUser
+import {UserAvatar} from '@sentry/scraps/avatar/userAvatar';
 import {useUser} from 'sentry/utils/useUser';
 
+<UserAvatar user={user}>
+
 // ❌ Do not use raw intrinsic elements or static paths
 function Component() {
   return (
@@ -371,11 +373,37 @@ function Component() {
     />
   );
 }
+```
+
+For lists of avatars, use <AvatarList>.
+
+##### Disclosure
+
+Use the core disclosure component instead of building
+
+```tsx
+// ✅ Use Disclosure component
+<Disclosure>
+  <Disclosure.Title>Title</Disclosure.Title>
+  <Disclosure.Content>Content that is toggled based on expanded state</Disclosure.Content>
+</Disclosure>;
 
+// ❌ Do not reimplement disclosure pattern manually
 function Component() {
-  const user = useUser();
-  return <UserAvatar user={user} />;
+  const [isExpanded, setIsExpanded] = useState(false);
+
+  return (
+    <div>
+      <Button
+        onClick={() => setIsExpanded(!isExpanded)}
+        icon={<IconChevron direction={isExpanded ? 'down' : 'right'} />}
+      >
+        Title
+      </Button>
+      {isExpanded && (
+        <Container>Content that is toggled based on expanded state</Container>
+      )}
+    </div>
+  );
 }
 ```
-
-For lists of avatars, use <AvatarList>.
PATCH

echo "Gold patch applied."
