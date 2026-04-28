#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remeda

# Idempotency guard
if grep -qF "Astro components (`.astro`) handle data loading and server rendering. React comp" "packages/docs/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/docs/CLAUDE.md b/packages/docs/CLAUDE.md
@@ -42,7 +42,7 @@ The site has six content collections, each with its own `content.config.ts` co-l
 
 ### Component Pattern
 
-Astro components (`.astro`) handle data loading and server rendering. React components (`.tsx`) are hydrated as islands using `client:*` directives — `client:visible` for interactive UI (navbar, collapsible signatures), `client:idle` for low-priority (theme switcher), `client:only="react"` for search (Algolia DocSearch). The `src/components/ui/` directory contains unmodified shadcn/ui components (Radix UI + Tailwind) — lint rules are relaxed for these files.
+Astro components (`.astro`) handle data loading and server rendering. React components (`.tsx`) are hydrated as islands using `client:*` directives — `client:visible` for interactive UI (navbar, collapsible signatures), `client:idle` for low-priority (theme switcher), `client:only="react"` for search (Algolia DocSearch). The `src/components/ui/` directory contains shadcn/ui components (Radix UI + Tailwind).
 
 ### Key Directories
 
PATCH

echo "Gold patch applied."
