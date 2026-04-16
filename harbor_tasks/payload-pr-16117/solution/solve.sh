#!/bin/bash
set -e

cd /workspace/payload

# Apply the gold patch
git apply <<'PATCH'
diff --git a/packages/next/src/utilities/meta.spec.ts b/packages/next/src/utilities/meta.spec.ts
new file mode 100644
index 00000000000..ef216bc42be
--- /dev/null
+++ b/packages/next/src/utilities/meta.spec.ts
@@ -0,0 +1,91 @@
+import { describe, expect, it } from 'vitest'
+
+import { generateMetadata } from './meta.js'
+
+describe('generateMetadata', () => {
+  it('should handle a string title with titleSuffix', async () => {
+    const result = await generateMetadata({
+      serverURL: 'http://localhost:3000',
+      title: 'Dashboard',
+      titleSuffix: '- My CMS',
+    })
+
+    expect(result.title).toBe('Dashboard - My CMS')
+  })
+
+  it('should apply titleSuffix to default and template fields of a TemplateString title object', async () => {
+    const result = await generateMetadata({
+      serverURL: 'http://localhost:3000',
+      title: { default: 'Dashboard', template: '%s | Dashboard' },
+      titleSuffix: '- My CMS',
+    })
+
+    expect(typeof result.title).toBe('object')
+    expect((result.title as { default: string; template: string }).default).toBe(
+      'Dashboard - My CMS',
+    )
+    expect((result.title as { default: string; template: string }).template).toBe(
+      '%s | Dashboard - My CMS',
+    )
+  })
+
+  it('should use the TemplateString default for ogTitle when title is a TemplateString object', async () => {
+    const result = await generateMetadata({
+      serverURL: 'http://localhost:3000',
+      title: { default: 'My CMS', template: '%s | My CMS' },
+      titleSuffix: '- Payload',
+    })
+
+    // OG title must be a plain string — extract from TemplateString.default and append titleSuffix
+    expect(result.openGraph?.title).toBe('My CMS - Payload')
+  })
+
+  it('should use the TemplateString absolute for ogTitle when title has absolute property', async () => {
+    const result = await generateMetadata({
+      serverURL: 'http://localhost:3000',
+      title: { absolute: 'My CMS Absolute' },
+      titleSuffix: '- Payload',
+    })
+
+    expect(result.openGraph?.title).toBe('My CMS Absolute - Payload')
+  })
+
+  it('should apply titleSuffix to the absolute field of a TemplateString title object', async () => {
+    const result = await generateMetadata({
+      serverURL: 'http://localhost:3000',
+      title: { absolute: 'My CMS Absolute' },
+      titleSuffix: '- Payload',
+    })
+
+    expect(typeof result.title).toBe('object')
+    expect((result.title as { absolute: string }).absolute).toBe('My CMS Absolute - Payload')
+  })
+
+  it('should use openGraph.title string over incomingMetadata.title for ogTitle', async () => {
+    const result = await generateMetadata({
+      serverURL: 'http://localhost:3000',
+      title: 'My CMS',
+      titleSuffix: '- Payload',
+      openGraph: { title: 'Custom OG Title' },
+    })
+
+    expect(result.openGraph?.title).toBe('Custom OG Title')
+  })
+
+  it('should return undefined for metaTitle when no title and no titleSuffix are set', async () => {
+    const result = await generateMetadata({
+      serverURL: 'http://localhost:3000',
+    })
+
+    expect(result.title).toBeUndefined()
+  })
+
+  it('should return just the title when no titleSuffix is set', async () => {
+    const result = await generateMetadata({
+      serverURL: 'http://localhost:3000',
+      title: 'My CMS',
+    })
+
+    expect(result.title).toBe('My CMS')
+  })
+})
diff --git a/packages/next/src/utilities/meta.ts b/packages/next/src/utilities/meta.ts
index a6539b82ad3..1ae5af91036 100644
--- a/packages/next/src/utilities/meta.ts
+++ b/packages/next/src/utilities/meta.ts
@@ -5,6 +5,44 @@ import type { MetaConfig } from 'payload'
 import { payloadFaviconDark, payloadFaviconLight, staticOGImage } from '@payloadcms/ui/assets'
 import * as qs from 'qs-esm'

+const appendTitleSuffix = (
+  title: Metadata['title'],
+  suffix: string | undefined,
+): Metadata['title'] => {
+  if (!suffix || !title) {
+    return title ?? undefined
+  }
+  if (typeof title === 'string') {
+    return `${title} ${suffix}`
+  }
+
+  if ('default' in title) {
+    return { default: `${title.default} ${suffix}`, template: `${title.template} ${suffix}` }
+  }
+
+  if ('template' in title) {
+    return {
+      absolute: `${title.absolute} ${suffix}`,
+      template: title.template !== null ? `${title.template} ${suffix}` : null,
+    }
+  }
+
+  return { absolute: `${title.absolute} ${suffix}` }
+}
+
+const getTitleString = (title: Metadata['title']): string | undefined => {
+  if (!title) {
+    return undefined
+  }
+  if (typeof title === 'string') {
+    return title
+  }
+  if ('absolute' in title) {
+    return title.absolute
+  }
+  return title.default
+}
+
 const defaultOpenGraph: Metadata['openGraph'] = {
   description:
     'Payload is a headless CMS and application framework built with TypeScript, Node.js, and React.',
@@ -43,11 +81,14 @@ export const generateMetadata = async (
       },
     ] satisfies Array<Icon>)

-  const metaTitle: Metadata['title'] = [incomingMetadata.title, titleSuffix]
-    .filter(Boolean)
-    .join(' ')
+  const metaTitle: Metadata['title'] = appendTitleSuffix(incomingMetadata.title, titleSuffix)
+
+  const titleStringForOg: string | undefined =
+    typeof incomingMetadata.openGraph?.title === 'string'
+      ? incomingMetadata.openGraph.title
+      : getTitleString(incomingMetadata.title)

-  const ogTitle = `${typeof incomingMetadata.openGraph?.title === 'string' ? incomingMetadata.openGraph.title : incomingMetadata.title} ${titleSuffix}`
+  const ogTitle = [titleStringForOg, titleSuffix].filter(Boolean).join(' ')

   const mergedOpenGraph: Metadata['openGraph'] = {
     ...(defaultOpenGraph || {}),
PATCH

# Verify the patch was applied by checking for the distinctive function
grep -q "appendTitleSuffix" packages/next/src/utilities/meta.ts && echo "Patch applied successfully"