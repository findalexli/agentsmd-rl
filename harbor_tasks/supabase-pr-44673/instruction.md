# Fix Stale OG Images on Social Media

## Problem

Social-media crawlers (X, LinkedIn, etc.) cache Open Graph images from the `generate-og` Edge Function. Since the image URL remains unchanged between deployments, crawlers continue serving the same cached image even after the design changes.

**Symptom**: After deploying a blog post with updated OG image design, social-media previews still show the old image.

**Expected behavior**: Each deployment should produce image URLs that force crawlers to fetch fresh content.

## Scope

- Only affects `og:image` and `twitter:image` meta tags
- Only applies to URLs pointing to the dynamic `generate-og` Edge Function (URLs containing `/functions/v1/generate-og`)
- Static images (regular blog post images) must continue to work as before without any URL modifications

## Technical Context

The `getAbsoluteBlogSocialImage` function in `apps/www/lib/blog-images.ts` builds absolute URLs for blog social images. It is called at build time to generate the OG image meta tags for each blog post.

The fix should ensure that:
1. URLs containing `/functions/v1/generate-og` get a unique query parameter appended on each build
2. Static image URLs are returned unchanged

## References

- The existing test suite in `apps/www/lib/blog-images.test.ts` uses vitest
- Run tests with: `pnpm vitest --run lib/blog-images.test.ts` from the `apps/www` directory
- The test file imports `getAbsoluteBlogSocialImage` from `./blog-images`
- Add a test named `appends a cache-busting param to dynamic OG function URLs` that verifies the cache-busting behavior for OG function URLs
- Add a test named `does not append a cache-busting param to static image URLs` that verifies static images pass through unchanged

## What Not to Do

- Do not modify the `resolveBlogImagePath` or `toAbsoluteBlogImageUrl` helper functions — the fix belongs in `getAbsoluteBlogSocialImage`
- Do not add cache-busting to all URLs — static images must remain unchanged
- Do not change the function signature or return type of `getAbsoluteBlogSocialImage`