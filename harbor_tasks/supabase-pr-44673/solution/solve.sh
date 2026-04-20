#!/bin/bash
set -e

cd /workspace/supabase

# Apply the gold patch
git apply <<'PATCH'
diff --git a/apps/www/lib/blog-images.test.ts b/apps/www/lib/blog-images.test.ts
index 09f2ecf879b63..e92daff955670 100644
--- a/apps/www/lib/blog-images.test.ts
+++ b/apps/www/lib/blog-images.test.ts
@@ -53,6 +53,25 @@ describe('blog image helpers', () => {
     ).toBe('https://supabase.com/images/blog/example/og.png')
   })

+  it('appends a cache-busting param to dynamic OG function URLs', () => {
+    const url = getAbsoluteBlogSocialImage(
+      {
+        imgSocial:
+          'https://zhfonblqamxferhoguzj.supabase.co/functions/v1/generate-og?template=announcement',
+      },
+      'https://supabase.com'
+    )
+    expect(url).toMatch(
+      /^https:\/\/zhfonblqamxferhoguzj\.supabase\.co\/functions\/v1\/generate-og\?template=announcement&v=.+$/
+    )
+  })
+
+  it('does not append a cache-busting param to static image URLs', () => {
+    expect(
+      getAbsoluteBlogSocialImage({ imgSocial: 'example/og.png' }, 'https://supabase.com')
+    ).toBe('https://supabase.com/images/blog/example/og.png')
+  })
+
   it('uses the placeholder when neither image is present', () => {
     expect(getBlogThumbnailImage({})).toBe(BLOG_PLACEHOLDER_IMAGE)
     expect(getBlogThumbnailImage({}, { fallbackToPlaceholder: false })).toBeUndefined()
diff --git a/apps/www/lib/blog-images.ts b/apps/www/lib/blog-images.ts
index af5145eee7d65..29ddb28e862cc 100644
--- a/apps/www/lib/blog-images.ts
+++ b/apps/www/lib/blog-images.ts
@@ -61,12 +61,29 @@ export function getBlogSocialImage({ imgThumb, imgSocial }: BlogImageFields) {
   return image ? resolveBlogImagePath(image) : undefined
 }

+/**
+ * Build-time ID appended to OG image URLs that point to the dynamic
+ * `generate-og` Edge Function. A fresh value on every deploy forces
+ * social-media crawlers (X, LinkedIn, etc.) to bypass their image cache.
+ */
+const buildId = Date.now()
+
 export function getAbsoluteBlogSocialImage(
   { imgThumb, imgSocial }: BlogImageFields,
   siteOrigin: string = SITE_ORIGIN
 ) {
   const image = imgSocial || imgThumb
-  return image ? toAbsoluteBlogImageUrl(image, siteOrigin) : undefined
+  if (!image) return undefined
+
+  const url = toAbsoluteBlogImageUrl(image, siteOrigin)
+
+  // Only bust cache for the dynamic OG function, not static images
+  if (url.includes('/functions/v1/generate-og')) {
+    const separator = url.includes('?') ? '&' : '?'
+    return `${url}${separator}v=${buildId}`
+  }
+
+  return url
 }

 export function validateBlogFrontmatterImages(
PATCH

# Verify patch was applied by checking for distinctive line
grep -q "const buildId = Date.now()" apps/www/lib/blog-images.ts