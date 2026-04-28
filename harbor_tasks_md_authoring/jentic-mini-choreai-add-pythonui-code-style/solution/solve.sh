#!/usr/bin/env bash
set -euo pipefail

cd /workspace/jentic-mini

# Idempotency guard
if grep -qF "- **UI**: ESLint 9 (flat config) with Prettier as plugin. Config: `ui/eslint.con" ".claude/CLAUDE.md" && grep -qF "Formatting is `ruff format` \u2014 [PEP 8](https://peps.python.org/pep-0008/)-aligned" ".claude/rules/python-code-style.md" && grep -qF "- **Use UI library primitives, not raw HTML.** In `src/pages/` and `src/componen" ".claude/rules/ui-code-style.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/CLAUDE.md b/.claude/CLAUDE.md
@@ -101,20 +101,18 @@ The `ui/` directory contains a React 18 + Vite 7 admin frontend.
   - `@theme inline` maps CSS custom properties to Tailwind utility classes (e.g. `--color-primary: var(--primary)` → `bg-primary`, `text-primary`)
   - `:root` defines the full HSL color palette and semantic mappings
   - `@layer base` sets body, heading, and button cursor styles
-- **Icons**: Lucide React (SVG components, no emoji)
+- **Icons**: Lucide React
 - **Fonts**: Sora (body), Nunito Sans (headings), Geist Mono (code) — loaded via Google Fonts in `index.html`
 
 ### UI Component Library
-Shadcn-style owned components in `ui/src/components/ui/`. All components use `cn()` for class merging, semantic design tokens, and `forwardRef` where appropriate.
+Shadcn-style owned components in `ui/src/components/ui/`.
 
 - **Primitives**: `Button`, `Input`, `Label`, `Textarea`, `Select` — extend native HTML props, support error states and accessibility
 - **Layout**: `Dialog` (native `<dialog>`, zero deps), `EmptyState`, `PageHeader`, `ErrorAlert`, `LoadingState`, `BackButton`, `CopyButton`
 - **Data**: `DataTable` (generic typed columns), `Pagination`
 - **Shared hooks**: `useCopyToClipboard` in `ui/src/hooks/`
 - **Shared utilities**: `timeAgo`, `formatTimestamp`, `statusVariant`, `statusColor` in `ui/src/lib/`
 - **Barrel export**: `ui/src/components/ui/index.ts`
-- **ESLint guardrails**: `no-restricted-syntax` errors prevent raw `<button>`, `<input>`, `<select>`, `<textarea>` in `src/pages/`
-- **Convention**: New page code must use UI library components, not raw HTML elements
 
 ### Generated API client
 - **Source**: `ui/openapi.json` (static copy of `/openapi.json` from the running server)
@@ -145,13 +143,9 @@ All theming is in `ui/src/index.css`. To add a new semantic color:
 
 See @DEVELOPMENT.md for commands.
 
-## Python Code Style
-
-- **Top-level imports only** — never use local/inline imports inside functions. All imports must be at the top of the file. The only exception is avoiding circular imports (must be commented as such).
-
 ## Formatting & Linting
 
-- **UI**: ESLint 9 (flat config) with Prettier as plugin. `@/` imports enforced via `no-restricted-imports`. Config: `ui/eslint.config.js`, `ui/prettier.config.js`, `ui/.editorconfig`
+- **UI**: ESLint 9 (flat config) with Prettier as plugin. Config: `ui/eslint.config.js`, `ui/prettier.config.js`, `ui/.editorconfig`
 - **Husky + lint-staged**: pre-commit hook lints staged files automatically
 
 ## Data directory (all gitignored)
diff --git a/.claude/rules/python-code-style.md b/.claude/rules/python-code-style.md
@@ -0,0 +1,15 @@
+---
+paths:
+  - "**/*.py"
+---
+
+## Python code style
+
+Formatting is `ruff format` — [PEP 8](https://peps.python.org/pep-0008/)-aligned, line length 100 (project standard; PEP 8 recommends 79). `ruff check` enforces our selected rule subset (`E4`, `E7`, `E9`, `F`, `I`, `PLC0415`, `PLC2701`) — see `[tool.ruff.lint]` in `pyproject.toml`. Run `pdm run lint:fix` on files you touched before handing off.
+
+- **Top-level imports only.** Every `import` belongs at the module top, above the first definition. No function-local imports for lazy-loading or startup-cost reasons. Enforced by ruff `PLC0415`.
+  - **Exception: breaking an import cycle.** When you must inline an import to avoid a circular dependency, leave a one-line comment explaining why the cycle can't be untangled.
+
+- **Don't import other modules' private names.** Symbols prefixed with `_` are module-private. If another module needs one, promote it to public (rename without the leading underscore) rather than cross-importing `_foo`. Enforced by ruff `PLC2701`.
+
+- **Modern type syntax for Python 3.11.** Prefer `list[str]`, `dict[str, int]` ([PEP 585](https://peps.python.org/pep-0585/)) and `X | None` ([PEP 604](https://peps.python.org/pep-0604/)) over `typing.List` / `typing.Optional`.
\ No newline at end of file
diff --git a/.claude/rules/ui-code-style.md b/.claude/rules/ui-code-style.md
@@ -0,0 +1,27 @@
+---
+paths:
+  - "ui/**/*.ts"
+  - "ui/**/*.tsx"
+---
+
+## UI code style
+
+Most rules below are enforced by ESLint (`ui/eslint.config.js`) — run `npm run lint:fix` from `ui/` on files you touched before handing off (or `npm run lint` to check without modifying).
+
+Test files (`**/__tests__/**`, `**/*.test.{ts,tsx}`, `**/*.spec.{ts,tsx}`) and `e2e/**` have relaxed rules — see the test blocks in `eslint.config.js` before assuming every rule below applies.
+
+### Components
+- **Use UI library primitives, not raw HTML.** In `src/pages/` and `src/components/layout/`, replace raw `<button>`, `<input>`, `<select>`, `<textarea>`, `<a>`, and `react-router-dom`'s `<Link>` with `<Button>`, `<Input>`, `<Select>`, `<Textarea>`, and `<AppLink>` from `@/components/ui`. The same rule applies inside `src/components/ui/`, with the primitive files themselves (Button, Input, Select, Textarea) as the only exception.
+- **Merge class names with `cn()`.** Components that accept a `className` prop pass it through `cn()` from `@/lib/utils`.
+- **Named components use `function` declarations.** `forwardRef` primitives (Button, Input, Select, Textarea) take an anonymous function, so they write as `export const Name = forwardRef<...>((...) => ...)` — this is the ESLint config's unnamed-component path, not a custom exemption.
+
+### Styling
+- **Semantic design tokens only.** Use `bg-primary`, `text-muted-foreground`, `border-border` — not raw Tailwind colors like `bg-blue-500`. Add new tokens in `ui/src/index.css`; see CLAUDE.md for the four-step recipe.
+- **Icons are Lucide React SVG components.** No emoji in UI code.
+
+### Imports
+- **Absolute `@/` imports, never `../..`.** Relative parent paths are an ESLint error.
+- **Type-only imports use `import type`.** Enforced by `@typescript-eslint/consistent-type-imports`.
+
+### Generated code
+- **Never edit `ui/src/api/generated/`.** It is codegen output. When backend endpoints change, update `ui/openapi.json` and regenerate (command in CLAUDE.md).
\ No newline at end of file
PATCH

echo "Gold patch applied."
