#!/usr/bin/env bash
set -euo pipefail

cd /workspace/docs

# Idempotency guard
if grep -qF "- Common Tabler names that differ from FontAwesome: `home` (not `house`), `tool`" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -65,6 +65,16 @@ Snippet files in `src/snippets/` are reusable MDX content that can be imported i
 
 **Important:** When writing links in snippets, be careful about path segments. Read the docstrings and comments in `pipeline/core/builder.py` method `_process_snippet_markdown_file` (lines 807-872) to understand how snippet link preprocessing works and why certain path structures are required.
 
+## Icons
+
+This project uses the **Tabler** icon library (`"icons": { "library": "tabler" }` in `docs.json`). When adding or updating icons:
+
+- Use Tabler icon names only. Browse available icons at https://tabler.io/icons
+- Tabler uses lowercase kebab-case (e.g., `home`, `settings`, `alert-triangle`, `player-play`)
+- Brand icons require the `brand-` prefix (e.g., `brand-github`, `brand-python`, `brand-openai`)
+- For providers or brands without a Tabler icon, use a local SVG file in `src/images/providers/` with `currentColor` for theme adaptability (e.g., `icon="/images/providers/anthropic-icon.svg"`)
+- Common Tabler names that differ from FontAwesome: `home` (not `house`), `tool`/`tools` (not `wrench`), `player-play` (not `play`), `bulb` (not `lightbulb`), `alert-triangle` (not `exclamation-triangle`), `school` (not `graduation-cap`)
+
 ## Style guide
 
 In general, follow the [Google Developer Documentation Style Guide](https://developers.google.com/style). You can also access this style guide through the [Vale-compatible implementation](https://github.com/errata-ai/Google).
@@ -91,6 +101,7 @@ In general, follow the [Google Developer Documentation Style Guide](https://deve
 - Do not make assumptions - always ask for clarification
 - Do not include localization in relative links (e.g., `/python/` or `/javascript/`) - these are resolved automatically by the build pipeline
 - Do not use model aliases (e.g., "claude-sonnet-4-5") in code examples; always use full model names / identifiers (e.g., "claude-sonnet-4-5-20250929")
+- Do not use FontAwesome icon names — this project uses the Tabler icon library. Verify icon names at https://tabler.io/icons
 - Do not use nested double quotes in Mintlify component attributes (e.g., `default='["a", "b"]'`). This causes escape characters to render in the frontend. Instead, use single quotes inside double quotes: `default="['a', 'b']"`
 
 For questions, refer to the Mintlify docs (either via MCP, if available), or at the [Mintlify documentation](https://docs.mintlify.com/docs/introduction).
PATCH

echo "Gold patch applied."
