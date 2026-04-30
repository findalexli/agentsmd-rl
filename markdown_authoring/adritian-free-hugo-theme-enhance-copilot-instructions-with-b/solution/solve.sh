#!/usr/bin/env bash
set -euo pipefail

cd /workspace/adritian-free-hugo-theme

# Idempotency guard
if grep -qF "This is a **Hugo theme** for personal websites/portfolios, not a standalone site" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -1,8 +1,22 @@
 # Adritian Hugo Theme - AI Coding Instructions
 
+## Project Overview
+
+This is a **Hugo theme** for personal websites/portfolios, not a standalone site (although a example site is provided, to demonstrate the usage of the theme itself). The theme provides layouts, styling, and functionality that users import via Hugo modules or as a git submodule.
+
+**Technology Stack:**
+- **Static Site Generator:** Hugo (v0.136+ extended version required)
+- **CSS Framework:** Bootstrap 5 (v5.3.8)
+- **CSS Preprocessor:** SCSS/Sass
+- **JavaScript Libraries:** Fuse.js (search), DOMPurify (XSS protection)
+- **Testing:** Playwright (E2E tests)
+- **Package Manager:** npm
+- **Templating:** Hugo Templates (Go templates)
+- **Build Tools:** Hugo's built-in asset pipeline, PostCSS, Autoprefixer
+
 ## Project Architecture
 
-This is a **Hugo theme** for personal websites/portfolios, not a standalone site. The theme provides layouts, styling, and functionality that users import via Hugo modules or as a git submodule, and importing the theme.
+This is a **Hugo theme** for personal websites/portfolios, not a standalone site. The theme provides layouts, styling, and functionality that users import via Hugo modules or as a git submodule.
 
 The theme provides a example site (`exampleSite/`) that demonstrates all features and serves as a starting point for users. It is also used for the integration tests.
 
@@ -124,4 +138,77 @@ npm install  # Installs Bootstrap + theme-helper
 
 E2E tests validate real user workflows rather than individual components. Tests include theme switching, language switching, navigation, search, and content rendering across different configurations (with/without menus).
 
-When modifying layouts or adding features, ensure corresponding E2E tests exist in `tests/e2e/`.
\ No newline at end of file
+When modifying layouts or adding features, ensure corresponding E2E tests exist in `tests/e2e/`.
+
+## Coding Standards and Conventions
+
+### HTML/Hugo Templates
+- Use semantic HTML5 elements for proper document structure
+- Follow Hugo's template naming conventions (lowercase with hyphens)
+- Partial templates should be in `layouts/partials/`
+- Shortcodes should be in `layouts/shortcodes/`
+- Use Hugo's built-in functions when available (e.g., `absURL`, `relURL`)
+
+### SCSS/CSS
+- Follow Bootstrap 5 conventions and utility classes where possible
+- Use BEM naming methodology for custom components when needed
+- Prefix custom variables with theme-specific identifiers
+- Keep files modular - one component per file
+- Use CSS custom properties for themeable values
+- File naming: lowercase with underscores (e.g., `_navbar.scss`, `_blog.scss`)
+
+### JavaScript
+- Use vanilla JavaScript (no jQuery)
+- Prefer modern ES6+ syntax
+- Keep JavaScript minimal - theme is primarily CSS-driven
+- Use DOMPurify for any user-generated content sanitization
+- Ensure all JavaScript is progressively enhanced (works without JS when possible)
+
+### Content and Configuration
+- YAML frontmatter for content files
+- TOML for Hugo configuration files
+- Follow existing frontmatter patterns for each content type
+- Use descriptive, human-readable keys
+
+### File Naming Conventions
+- Templates: lowercase with hyphens (e.g., `single.html`, `list.html`)
+- SCSS files: lowercase with underscores, prefixed with `_` for partials
+- Content files: lowercase with hyphens (e.g., `my-blog-post.md`)
+- Archetypes: match content type name (e.g., `blog.md`, `experience.md`)
+
+## Web Accessibility Requirements
+
+**This theme prioritizes accessibility (WCAG 2.1 AA compliance):**
+
+- All interactive elements must be keyboard accessible
+- Proper ARIA labels and roles for non-semantic elements
+- Color contrast ratios must meet WCAG AA standards (4.5:1 for normal text, 3:1 for large text)
+- Images must have descriptive `alt` attributes
+- Forms must have associated labels
+- Focus indicators must be visible and clear
+- Dark/light theme switching must maintain accessibility standards in both modes
+- Skip navigation links for keyboard users
+- Semantic HTML structure (proper heading hierarchy, landmarks, etc.)
+- Test changes with screen readers when modifying navigation or interactive elements
+
+## Security Best Practices
+
+- Never commit secrets, API keys, or sensitive data
+- Use DOMPurify for sanitizing any user-generated or external content
+- Validate and sanitize all user inputs in contact forms
+- Follow Hugo's security best practices for template rendering
+- Keep dependencies updated to patch security vulnerabilities
+- Use Hugo's built-in `safeHTML`, `safeCSS`, `safeJS` functions appropriately
+
+## Files and Directories to Ignore
+
+Copilot should **ignore** or be cautious with:
+- `node_modules/` - Third-party dependencies
+- `public/` - Hugo build output (generated files)
+- `resources/` - Hugo's asset cache
+- `.hugo_build.lock` - Hugo build lock file
+- `package-lock.json` - npm lock file (only update via npm commands)
+- `.git/` - Version control directory
+- `exampleSite/public/` - Example site build output
+- `exampleSite/resources/` - Example site cache
+- `.DS_Store` - macOS system files
\ No newline at end of file
PATCH

echo "Gold patch applied."
