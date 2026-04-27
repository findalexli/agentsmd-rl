#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agentrove

# Idempotency guard
if grep -qF "- Do not use absolute positioning for layout of sibling elements within a contai" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -208,6 +208,8 @@
 - Search highlights: `bg-surface-active` / `dark:bg-surface-dark-hover` — never `bg-brand-*`
 - Selected/active states: `bg-surface-active` / `dark:bg-surface-dark-active` — never `bg-brand-*`
 - Semantic colors (`success`, `error`, `warning`, `info`) are only for status indicators, not layout
+- Do not use semantic colors (`error-*`, `warning-*`, `success-*`) for interactive button backgrounds — use monochrome surface tokens; semantic colors are for status badges and text indicators only
+- Every `dark:text-*` / `dark:bg-*` class must have a corresponding light-mode class — never rely on browser defaults or inherited color for one mode while explicitly setting the other
 - Use opacity modifiers sparingly for glassmorphism (`/50`, `/30` are common) — white/black only as opacity overlays (`bg-white/5`, `bg-black/50`), never solid
 
 ### Typography
@@ -221,6 +223,7 @@
 - Standard border pattern: `border border-border/50 dark:border-border-dark/50` for most containers — use full opacity `border-border dark:border-border-dark` only for prominent dividers
 - Radius hierarchy: `rounded-md` for small elements (buttons, inputs), `rounded-lg` for standard containers and cards (most common), `rounded-xl` for prominent cards and dropdowns, `rounded-2xl` for overlays — button sizes follow `sm: rounded-md`, `md: rounded-lg`, `lg: rounded-xl`
 - Shadow hierarchy: `shadow-sm` for interactive elements, `shadow-medium` for dropdowns and panels, `shadow-strong` for modals — use `backdrop-blur-xl` with `bg-*/95` for frosted glass dropdowns
+- Do not use custom shadow tokens (`shadow-soft`, `shadow-harsh`, etc.) — use only the defined hierarchy: `shadow-sm`, `shadow-medium`, `shadow-strong`
 
 ### Icons
 - Default icon size is `h-3.5 w-3.5` for toolbars, action buttons, and small controls
@@ -246,6 +249,9 @@
 - Dropdowns: `animate-fadeIn` for entry — no scale transforms on buttons
 
 ### Button Layout
+### Layout
+
+- Do not use absolute positioning for layout of sibling elements within a container — use flexbox (`flex`, `justify-between`, `gap-*`); reserve `absolute` for overlays, tooltips, dropdowns, and decorative elements only
 - When action buttons have variable-length or long text labels, stack them vertically (`flex-col`) at full width instead of placing them in a horizontal row — horizontal layouts break awkwardly when text wraps or buttons have uneven widths
 
 ## Code Review Guidelines
PATCH

echo "Gold patch applied."
