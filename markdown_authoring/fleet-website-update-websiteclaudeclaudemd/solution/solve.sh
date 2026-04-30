#!/usr/bin/env bash
set -euo pipefail

cd /workspace/fleet

# Idempotency guard
if grep -qF "New pages should mirror the structure and styling of existing landing pages rath" "website/.claude/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/website/.claude/CLAUDE.md b/website/.claude/CLAUDE.md
@@ -239,7 +239,26 @@ The build script enforces several rules and will throw errors for:
 - Missing required meta tags per content type
 
 ## Creating new pages
-Use `sails generate page <folder>/<name>` — scaffolds controller, view, page script, and LESS file. Then: add the route in `config/routes.js`, add the LESS `@import` to `importer.less`, and update `config/policies.js` if bypassing `is-logged-in` (not needed under folders like `landing-pages/` that already bypass it).
+
+**Always use `sails generate page <name>` or `sails generate page <folder>/<name>` — don't hand-create the controller/view/script/LESS files.** The generator produces the correct Actions2 shape, view path, and locals boilerplate; manual scaffolding is error-prone (wrong exits, missing `exposeLocalsToBrowser()` footer, etc.).
+
+The generator creates four files. For root-level pages, use `<name>` paths; for nested pages, include the `<folder>/` segment:
+- `api/controllers/view-<name>.js` or `api/controllers/<folder>/view-<name>.js`
+- `views/pages/<name>.ejs` or `views/pages/<folder>/<name>.ejs`
+- `assets/js/pages/<name>.page.js` or `assets/js/pages/<folder>/<name>.page.js`
+- `assets/styles/pages/<name>.less` or `assets/styles/pages/<folder>/<name>.less`
+
+### After running the generator
+1. Add the route in `config/routes.js` with `pageTitleForMeta` and `pageDescriptionForMeta` under `locals`.
+2. Add the matching import to `assets/styles/importer.less`: `@import 'pages/<name>.less';` for root-level pages or `@import 'pages/<folder>/<name>.less';` for nested pages.
+3. If the page needs to bypass `is-logged-in`, update `config/policies.js` (not needed under folders already bypassing it, e.g. `landing-pages/`).
+4. Re-lift the dev server — backend changes don't hot-reload.
+
+### Reuse existing styles, layout, and elements
+New pages should mirror the structure and styling of existing landing pages rather than inventing new patterns. Before writing markup or LESS, open 1–2 existing landing pages in `views/pages/landing-pages/` (e.g. `linux-management.ejs`, `replace-jamf.ejs`) and their paired stylesheets in `assets/styles/pages/landing-pages/`, and copy the section scaffolding — hero, feature rows, `<scrollable-tweets>`, `bottom-gradient`, `<parallax-city>` footer — along with the `[purpose='...']` naming conventions. Reuse existing components (`<logo-carousel>`, `<animated-arrow-button>`, `<modal>`, video modal pattern) instead of building one-off equivalents. Only introduce new `[purpose]` blocks or LESS variables when nothing existing fits.
+
+### Deprecated
+Do **not** use `sails generate landing-page` (the custom generator under `website/generators/landing-page/`). It's deprecated; use `sails generate page` for landing pages too.
 
 ## Code style
 
PATCH

echo "Gold patch applied."
