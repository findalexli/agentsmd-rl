#!/usr/bin/env bash
set -euo pipefail

cd /workspace/boost

# Idempotency guard
if grep -qF "Flux includes [Heroicons](https://heroicons.com/) as its default icon set. Searc" ".ai/fluxui-free/skill/fluxui-development/SKILL.md" && grep -qF "Flux includes [Heroicons](https://heroicons.com/) as its default icon set. Searc" ".ai/fluxui-pro/skill/fluxui-development/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.ai/fluxui-free/skill/fluxui-development/SKILL.md b/.ai/fluxui-free/skill/fluxui-development/SKILL.md
@@ -36,6 +36,20 @@ Use Flux UI components when available. Fall back to standard Blade components wh
 
 Available: avatar, badge, brand, breadcrumbs, button, callout, checkbox, dropdown, field, heading, icon, input, modal, navbar, otp-input, profile, radio, select, separator, skeleton, switch, text, textarea, tooltip
 
+## Icons
+
+Flux includes [Heroicons](https://heroicons.com/) as its default icon set. Search for exact icon names on the Heroicons site - do not guess or invent icon names.
+
+<code-snippet name="Icon Button" lang="blade">
+<flux:button icon="arrow-down-tray">Export</flux:button>
+</code-snippet>
+
+For icons not available in Heroicons, use [Lucide](https://lucide.dev/). Import the icons you need with the Artisan command:
+
+```bash
+php artisan flux:icon crown grip-vertical github
+```
+
 ## Common Patterns
 
 ### Form Fields
diff --git a/.ai/fluxui-pro/skill/fluxui-development/SKILL.md b/.ai/fluxui-pro/skill/fluxui-development/SKILL.md
@@ -37,6 +37,20 @@ Use Flux UI components when available. Fall back to standard Blade components wh
 
 Available: accordion, autocomplete, avatar, badge, brand, breadcrumbs, button, calendar, callout, card, chart, checkbox, command, composer, context, date-picker, dropdown, editor, field, file-upload, heading, icon, input, kanban, modal, navbar, otp-input, pagination, pillbox, popover, profile, radio, select, separator, skeleton, slider, switch, table, tabs, text, textarea, time-picker, toast, tooltip
 
+## Icons
+
+Flux includes [Heroicons](https://heroicons.com/) as its default icon set. Search for exact icon names on the Heroicons site - do not guess or invent icon names.
+
+<code-snippet name="Icon Button" lang="blade">
+<flux:button icon="arrow-down-tray">Export</flux:button>
+</code-snippet>
+
+For icons not available in Heroicons, use [Lucide](https://lucide.dev/). Import the icons you need with the Artisan command:
+
+```bash
+php artisan flux:icon crown grip-vertical github
+```
+
 ## Common Patterns
 
 ### Form Fields
PATCH

echo "Gold patch applied."
