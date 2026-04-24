# Hugo Theme Skeleton: CSS and JavaScript Build Configuration

## Problem

The theme skeleton in `create/skeletons/theme/` has CSS and JavaScript processing that doesn't properly handle build options for different environments. CSS styles for header and footer components are mixed into a single file instead of being organized as separate components. The templates for CSS and JavaScript resource building need to support environment-aware configuration for minification and source maps.

## Required Behavior

### Component CSS Files

The following component CSS files must exist with specific styles:

1. **Header component** (`create/skeletons/theme/assets/css/components/header.css`):
   - Must contain styles for the header element
   - Must include `border-bottom` property
   - Must include `margin-bottom` property

2. **Footer component** (`create/skeletons/theme/assets/css/components/footer.css`):
   - Must contain styles for the footer element
   - Must include `border-top` property
   - Must include `margin-top` property

### Main CSS Structure

The `create/skeletons/theme/assets/css/main.css` file must:
- Import the header component using `@import "components/header.css"`
- Import the footer component using `@import "components/footer.css"`
- Must NOT contain inline `header { ... }` or `footer { ... }` styles (these belong in component files)
- Must retain the existing `body { ... }` and `a { ... }` style blocks

### CSS Template

The `create/skeletons/theme/layouts/_partials/head/css.html` template must:
- Use `css.Build` for processing CSS resources
- Configure build options to enable minification in production but not in development
- Configure source map options to use "linked" format in development and "none" in production

### JavaScript Template

The `create/skeletons/theme/layouts/_partials/head/js.html` template must:
- NOT contain any `targetPath` option
- NOT use `"external"` as a sourceMap value (use "linked" instead for development)
- Use `js.Build` with matching build options as css.html:
  - Enable minification in production but not in development
  - Use "linked" source map in development and "none" in production

## Expected Configuration Behavior

When `hugo.IsDevelopment` is true (development mode):
- `minify` should be disabled (false)
- `sourceMap` should use "linked" format

When `hugo.IsDevelopment` is false (production mode):
- `minify` should be enabled (true)
- `sourceMap` should be "none"

## Verification

After implementation:
- Hugo should build successfully
- The templates should produce valid output in both development and production environments

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `gofmt (Go formatter)`
