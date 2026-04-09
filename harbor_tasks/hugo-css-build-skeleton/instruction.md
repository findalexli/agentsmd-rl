# Update Hugo Theme Skeleton to Use css.Build

## Problem

The Hugo theme skeleton currently processes CSS using the `minify` pipe directly in the template. This approach doesn't leverage Hugo's `css.Build` function, which provides better CSS processing including bundling, @import resolution, and source map generation.

## Files to Modify

You need to update the theme skeleton files located in `create/skeletons/theme/`:

1. **`assets/css/main.css`** - Should use `@import` to include component CSS instead of inline header/footer rules
2. **`layouts/_partials/head/css.html`** - Should use `css.Build` with `minify` and `sourceMap` options instead of direct minification
3. **`layouts/_partials/head/js.html`** - Should use `cond hugo.IsDevelopment` for `minify` and `sourceMap` options (matching the css.html pattern)

## Files to Create

You need to create two new CSS component files:

1. **`assets/css/components/header.css`** - Extract header styles from main.css
2. **`assets/css/components/footer.css`** - Extract footer styles from main.css

## Requirements

The changes should:

1. Split CSS into modular components (header.css, footer.css) that are imported via `@import` in main.css
2. Update css.html to:
   - Define an `$opts` dict with `"minify"` and `"sourceMap"` options
   - Use `cond hugo.IsDevelopment` for conditional values
   - Use `css.Build $opts` for processing
   - Keep fingerprinting for production builds
3. Update js.html to:
   - Use `cond hugo.IsDevelopment` for `minify` option (development=false, production=true)
   - Use `cond hugo.IsDevelopment` for `sourceMap` option (development="linked", production="none")
   - Remove the `targetPath` option (no longer needed)

## Reference

- Hugo's `css.Build` function: https://gohugo.io/hugo-pipes/resource-from-template/#cssbuild
- The theme skeleton is used by `hugo new theme` command
- Look at the existing js.html for the pattern to follow (but update it to match the new approach)

## Testing

You can test your changes by:
1. Creating a test site: `hugo new site /tmp/testsite && cd /tmp/testsite`
2. Adding minimal config: `echo 'title = "Test"' > hugo.toml`
3. Creating a theme: `hugo new theme mytheme`
4. Verifying the created theme has the correct structure
