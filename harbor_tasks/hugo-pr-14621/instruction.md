# Hugo CSS Loader Resolution Fix

## Problem

When using Hugo's CSS bundling with `resources.Get` and `css.Build`, `url()` references
that are resolved by ESBuild's native resolver (rather than Hugo's resource resolver)
do not get proper file loader treatment. This causes static assets like images and fonts
to be incorrectly processed or omitted from the output.

### Symptom

CSS files with `url()` references to static files in the `static/` directory (or other
paths not managed as Hugo resources) fail to have their assets properly copied and
fingerprinted to the output directory.

Example CSS:
```css
div {
  background-image: url("static/b/image.png");
}
```

Before the fix: The image would not be processed or copied to the output.
After the fix: The image should be copied and fingerprinted like assets resolved by Hugo.

## Expected Behavior

CSS builds without an explicit `loaders` configuration must automatically handle
`url()` references to common static file types correctly. The build system should use
appropriate loader behavior for file extensions like `.png`, `.woff`, and `.svg` even
when those assets are resolved by ESBuild's native resolver rather than Hugo's resource
resolver.

The fix must:
1. Preserve correct behavior for JavaScript builds
2. Remain backward compatible with existing explicit `loaders` configurations
3. Be documented with explanatory comments in the relevant code

## Verification

The existing integration test `TestCSSBuildLoadersDefault` in the `tpl/css` package
must pass after the fix is applied. The esbuild package and tpl/css package must
both compile successfully, and `go vet` must report no issues.