#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nexent

# Idempotency guard
if grep -qF "- **Colocate subcomponents**: When a component file grows, extract logically dis" ".cursor/rules/frontend/component_layer_rules.mdc" && grep -qF "- **Avoid over-engineering**: Before abstracting code (extracting hooks, compone" ".cursor/rules/frontend/frontend_overview_rules.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/frontend/component_layer_rules.mdc b/.cursor/rules/frontend/component_layer_rules.mdc
@@ -1,20 +1,31 @@
 ---
-globs: frontend/components/**/*.tsx
-description: Component layer rules for reusable UI components
+globs: frontend/components/**/*.tsx,frontend/app/**/components/**/*.tsx
+description: Component layer rules for reusable and feature-specific UI components
 ---
 
 ### Purpose and Scope
 
-- Component layer contains reusable UI components for `frontend/components/**/*.tsx`
+- Component layer contains reusable UI components for `frontend/components/**/*.tsx` and feature-specific components under `frontend/app/**/components/**/*.tsx`
 - Responsibilities: Create reusable components, implement business logic, handle interactions, provide consistent UI
 - **MANDATORY**: All components must use TypeScript and functional components
 
+### UI Library and Icons
+
+- **Ant Design first**: Use Ant Design for forms, data display, modals, buttons, layouts. See [ui_standards_rules.mdc](mdc:frontend/ui_standards_rules.mdc).
+- **Icons**: Lucide icons primary (`lucide-react`), `@ant-design/icons` as fallback when Lucide lacks the icon.
+
+```tsx
+// Prefer Lucide
+import { Search, RefreshCw, Edit } from "lucide-react";
+
+// Fallback when Lucide has no equivalent (e.g. ExclamationCircleFilled for modal)
+import { ExclamationCircleFilled, InfoCircleFilled } from "@ant-design/icons";
+```
+
 ### Component Organization
 
-- **`components/ui/`** - Base UI components (buttons, inputs, dialogs, etc.)
 - **`components/auth/`** - Authentication-related components
 - **`components/providers/`** - Context providers and global state management
-- Use index files for clean imports: `export { Button } from './button'`
 
 ### Component Structure
 
@@ -23,6 +34,7 @@ description: Component layer rules for reusable UI components
 - Use React hooks for state management
 - Implement proper error boundaries where needed
 - Follow single responsibility principle
+- **Single component file should not exceed ~1000 lines**: Split into subcomponents or extract logic to hooks/utils when a file grows. keep files digestible.
 
 ### Props and State Management
 
@@ -31,11 +43,15 @@ description: Component layer rules for reusable UI components
 - Prefer controlled components over uncontrolled
 - Use local state for component-specific data
 - Use context for shared state across components
+- **Avoid Prop Drilling**: When a component receives more than ~7–10 props, or props are passed through multiple layers only to reach a deep child, prefer:
+  - **Context** for cross-cutting state (auth, theme, feature flags)
+  - **Composition** (children, render props) instead of passing many callbacks
+  - **Custom hooks** to encapsulate shared logic; let children use the hook instead of receiving props from parent
 - **CRITICAL**: All logging must use [logger.ts](mdc:frontend/lib/logger.ts) - never use console.log
 
 ### Styling and Design
 
-- Use Tailwind CSS classes for styling
+- Use Ant Design components + Tailwind for spacing and simple styling
 - Follow design system patterns and spacing
 - Ensure responsive design with mobile-first approach
 - Use CSS variables for theme colors
@@ -55,52 +71,48 @@ description: Component layer rules for reusable UI components
 - Provide meaningful error messages to users
 - Log errors appropriately for debugging
 
+### Other Considerations
+
+- **Colocate subcomponents**: When a component file grows, extract logically distinct subcomponents into separate files in the same folder. Avoid putting many unrelated components in one file.
+- **Lean interfaces**: Group related props into objects when they form a cohesive concern (e.g. `user: { email, avatarUrl, role }`) instead of passing many flat props.
+
 ### Example
 ```tsx
-// frontend/components/ui/button.tsx
-import React from 'react';
-import { useTranslation } from 'react-i18next';
-import { cn } from '@/lib/utils';
-
-interface ButtonProps {
-  children: React.ReactNode;
-  variant?: 'primary' | 'secondary' | 'outline';
-  size?: 'sm' | 'md' | 'lg';
-  disabled?: boolean;
-  loading?: boolean;
-  onClick?: () => void;
-  className?: string;
+// frontend/components/example-modal.tsx
+import React from "react";
+import { useTranslation } from "react-i18next";
+import { Modal } from "antd";
+import { AlertTriangle } from "lucide-react";
+
+interface ExampleModalProps {
+  open: boolean;
+  onClose: () => void;
+  onConfirm: () => void;
 }
 
-export function Button({
-  children,
-  variant = 'primary',
-  size = 'md',
-  disabled = false,
-  loading = false,
-  onClick,
-  className,
-}: ButtonProps) {
-  const { t } = useTranslation('common');
-  
+export function ExampleModal({
+  open,
+  onClose,
+  onConfirm,
+}: ExampleModalProps) {
+  const { t } = useTranslation("common");
+
   return (
-    <button
-      className={cn(
-        'inline-flex items-center justify-center rounded-md font-medium transition-colors',
-        variant === 'primary' && 'bg-primary text-primary-foreground hover:bg-primary/90',
-        variant === 'secondary' && 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
-        variant === 'outline' && 'border border-input bg-background hover:bg-accent',
-        size === 'sm' && 'h-9 px-3 text-sm',
-        size === 'md' && 'h-10 px-4 py-2',
-        size === 'lg' && 'h-11 px-8 text-lg',
-        className
-      )}
-      disabled={disabled || loading}
-      onClick={onClick}
+    <Modal
+      open={open}
+      onCancel={onClose}
+      centered
+      okText={t("common.confirm")}
+      cancelText={t("common.cancel")}
+      onOk={onConfirm}
     >
-      {loading && <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />}
-      {children}
-    </button>
+      <div className="flex items-center gap-3">
+        <AlertTriangle className="h-5 w-5 text-amber-500" />
+        <span>{t("modal.exampleMessage")}</span>
+      </div>
+    </Modal>  
+
+
   );
 }
 ```
\ No newline at end of file
diff --git a/.cursor/rules/frontend/frontend_overview_rules.mdc b/.cursor/rules/frontend/frontend_overview_rules.mdc
@@ -0,0 +1,82 @@
+---
+globs: frontend/**/*.{ts,tsx}
+description: Frontend overview - directory structure, layer responsibilities, and dependency rules
+alwaysApply: false
+---
+
+# Frontend Overview
+
+## Directory Structure
+
+```
+frontend/
+├── app/[locale]/              # Routes with i18n (Next.js App Router)
+│   ├── layout.tsx, page.tsx    # Root layout and home
+│   ├── i18n.tsx                # i18n config
+│   └── {feature}/              # e.g. chat, agents, knowledges, models
+│       ├── page.tsx            # Page entry (thin wrapper)
+│       ├── components/         # Feature-specific components
+│       └── {submodule}/        # e.g. versions/
+├── components/                 # Cross-feature reusable components
+│   ├── auth/                   # Auth-related UI
+│   ├── providers/              # Global context providers
+│   └── ...                     # Base UI: use Ant Design; avoid custom wrappers
+├── hooks/                      # Custom hooks (organized by domain)
+│   ├── auth/                   # useSessionManager, useAuthentication, etc.
+│   ├── agent/                  # useAgentList, useAgentInfo, etc.
+│   ├── chat/                   # useConversationManagement, etc.
+│   └── ...
+├── services/                   # API calls (api.ts, *Service.ts)
+├── lib/                        # Utilities (logger, session, utils, etc.)
+├── types/                      # Shared type definitions
+├── const/                      # Constants and config
+├── stores/                     # Global state stores (if any)
+├── styles/                     # Global styles (theme, reset, AntD overrides)
+└── public/                     # Static assets
+```
+
+## Layer Responsibilities
+
+| Directory | Purpose | Notes |
+|-----------|---------|-------|
+| `app/[locale]/{feature}/page.tsx` | Route entry, auth guard, config load | Thin wrapper; delegate UI to internal/components |
+| `app/.../components/` | Feature-only UI pieces | Ant Design first; Lucide icons primary, `@ant-design/icons` fallback |
+| `components/` | Shared UI across features | Ant Design first; Lucide icons primary, `@ant-design/icons` fallback |
+| `hooks/` | State and side-effects | Shared API data: use TanStack React Query (`useQuery`); client-side filter/sort: `useMemo` on query data; mutations: `useMutation` + `queryClient.invalidateQueries` |
+| `services/` | API calls | — |
+| `lib/` | Pure utilities | — |
+| `types/` | Type definitions only | `interface`, `type` only; do not store constants |
+| `const/` | Runtime constants | Literals, enums, config objects, status codes; do not store `interface`/`type` |
+| `styles/` | Global styles | Theme vars, reset, AntD overrides only; component-specific CSS: colocate in component (e.g. `*.module.css`) |
+
+## General Principles
+
+- **Avoid over-engineering**: Before abstracting code (extracting hooks, components, utils), confirm there is a concrete need (reuse, testability, or complexity). Prefer simple, inline solutions until the need is clear.
+
+## Dependency Rules
+
+- **No cross-feature imports**: Feature-level code (`components/` under a feature) must not import from other features. Use shared `components/` for cross-feature reuse.
+- **Infrastructure does not depend on UI**: `services/`, `lib/`, `types/` must not import from `app/` or `components/`.
+- **Minimize CSS**: Prefer Tailwind + Ant Design. Use CSS only when necessary; keep component-specific styles colocated (e.g. `*.module.css` next to the component).
+
+## Path Aliases
+
+- `@/*` → `frontend/*`
+- `@/app/*` → `frontend/app/[locale]/*` (import without `[locale]` segment)
+
+Example: `import { ChatInterface } from "@/app/chat/internal/chatInterface"`
+
+## Where to Put New Code
+
+| If you are adding... | Put it in |
+|----------------------|-----------|
+| A new route | `app/[locale]/{feature}/page.tsx` |
+| Core feature logic | `app/[locale]/{feature}/internal/` |
+| UI used only by one feature | `app/[locale]/{feature}/components/` |
+| UI used by multiple features | `components/` (auth/, providers/, etc.); base UI from Ant Design |
+| State/effect logic | `hooks/{domain}/` |
+| API call | `services/` |
+| Pure helper | `lib/` |
+| Shared type | `types/` |
+| Shared constant value | `const/` |
+| Global styles (theme, reset) | `styles/` |
PATCH

echo "Gold patch applied."
