#!/usr/bin/env bash
set -euo pipefail

cd /workspace/inbox-zero

# Idempotency guard
if grep -qF "- Do not duplicate substantial logic or correctness-sensitive rules. If copied c" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -36,11 +36,12 @@
 - No re-export patterns. Import from the original source.
 - Prefer the `EmailProvider` abstraction; only use provider-type checks (`isGoogleProvider`, `isMicrosoftProvider`) at true provider boundary/integration code.
 - Infer types from Zod schemas using `z.infer<typeof schema>` instead of duplicating as separate interfaces
-- Avoid premature abstraction. Duplicating 2-3 times is fine; extract when a stable pattern emerges.
 - Default to inlining and co-locating logic at the call site.
-- Extract a helper when doing so makes the call site clearly easier to read — e.g., a non-obvious computation gets a name, or a nested branch becomes a clean lookup. The bar is "the call site is better," not "the helper looks nice."
+- Avoid premature abstraction. Small duplicated expressions are usually fine; extracting them often adds indirection without meaning.
+- Do not duplicate substantial logic or correctness-sensitive rules. If copied code must stay in sync to avoid bugs, extract or centralize it early.
+- Extract helpers when they make surrounding code clearer, name a meaningful domain concept, or keep shared behavior consistent across flows.
 - Don't extract helpers that just rename and forward parameters; that's a layer without meaning.
-- Avoid large/nested ternaries. Prefer a small helper, an early-return cascade, or a lookup table.
+- Avoid large/nested ternaries. Prefer straightforward control flow, a small helper, or a lookup table when it improves readability.
 - No barrel files. Import directly from source files.
 - Colocate page components next to their `page.tsx`. No nested `components/` subfolders in route directories.
 - Reusable components shared across pages go in `apps/web/components/`
PATCH

echo "Gold patch applied."
