#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ledger-live

# Idempotency guard
if grep -qF "- Scope is optional but recommended (`desktop`, `mobile`, `coin`, `common`, etc." ".cursor/rules/git-workflow.mdc" && grep -qF "@node_modules/@ledgerhq/ldls-ui-react/ai-rules/RULES.md" ".cursor/rules/ldls.mdc" && grep -qF "description: General React and React Native engineering rules for Ledger Live" ".cursor/rules/react-general.mdc" && grep -qF "- Integration tests ensure that screens, components, hooks, and navigation work " ".cursor/rules/react-new-arch.mdc" && grep -qF "- use MSW for Network API calls (use same pattern as `apps/ledger-live-mobile/__" ".cursor/rules/testing.mdc" && grep -qF "- Prefer **React.FC** only when children typing is needed; otherwise avoid." ".cursor/rules/typescript.mdc" && grep -qF ".cursorrules" ".cursorrules"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/git-workflow.mdc b/.cursor/rules/git-workflow.mdc
@@ -0,0 +1,90 @@
+---
+description: Git workflow and commit conventions for Ledger Wallet
+globs: ["**/*"]
+alwaysApply: true
+---
+
+# Git Workflow & Commit Conventions
+
+## Branch Naming
+
+Branches must use a clear prefix based on their purpose:
+
+- **feat/** — New features
+- **bugfix/** — Bug fixes
+- **support/** — Refactor, tests, CI, improvements
+- **chore** — Maintenance, tooling, configs
+
+### Examples
+
+- `feat/add-ethereum-staking`
+- `bugfix/fix-transaction-signing`
+- `support/update-dependencies`
+
+### Best Practices
+
+- Use **kebab-case**
+- Keep names **short, explicit, action-oriented**
+- One branch = **one isolated concern**
+
+---
+
+## Commit Message Format
+
+Follow the **Conventional Commits** standard.
+
+### Format
+
+```
+
+<type>[optional scope]: <description>
+
+[optional body]
+
+[optional footer(s)]
+
+```
+
+### Rules
+
+- Description must be **imperative, clear, lowercase**
+- Scope is optional but recommended (`desktop`, `mobile`, `coin`, `common`, etc.)
+- Add body for complex or user-facing changes
+- If needed, include footers:
+  - `BREAKING CHANGE: ...`
+  - Jira ticket (`LL-1234`)
+
+---
+
+## Commit Types
+
+- **feat** — New feature
+- **fix** — Bug fix
+- **docs** — Docs only
+- **style** — Formatting, no code change
+- **refactor** — Restructure without behavior change
+- **test** — Add/update tests
+- **chore** — Maintenance, tooling, configs
+- **perf** — Performance improvements
+- **ci** — CI/CD changes
+
+### Examples
+
+```
+feat(desktop): add dark mode toggle
+fix(mobile): resolve transaction signing issue
+docs(common): update API documentation
+refactor(account): simplify account syncing logic
+test(coin): add bitcoin integration tests
+```
+
+---
+
+## Workflow Best Practices
+
+- Commits must be **small, isolated, meaningful**
+- One commit = **one logical change**
+- Prefer **multiple focused commits** over large mixed ones
+- Never mix refactor + fix + feature
+- Rebase before PR to keep history clean
+- Squash only for trivial branches (`support/cleanup`)
diff --git a/.cursor/rules/ldls.mdc b/.cursor/rules/ldls.mdc
@@ -0,0 +1,7 @@
+---
+description: LDLS UI React design system rules
+globs: ["**/*.tsx", "**/*.jsx"]
+alwaysApply: true
+---
+
+@node_modules/@ledgerhq/ldls-ui-react/ai-rules/RULES.md
diff --git a/.cursor/rules/react-general.mdc b/.cursor/rules/react-general.mdc
@@ -0,0 +1,120 @@
+---
+alwaysApply: true
+description: General React and React Native engineering rules for Ledger Live
+globs: ["**/*.{ts,tsx}"]
+---
+
+# General React & React Native Patterns
+
+_These rules apply to all files, including those inside `src/newArch/`._
+
+## Component Architecture
+
+- Prefer functional components.
+- Keep components focused and reasonably sized.
+- Decompose large UI into smaller reusable elements.
+- Use composition for extensibility.
+
+## State Management
+
+- Prioritize local state for UI-only concerns.
+- Use RTK Query (with slices) only when necessary for app-wide state.
+- Apply optimized selectors to limit re-rendering.
+- Connect Redux at the lowest component level when possible.
+
+## Styling
+
+### Mobile (React Native)
+
+- Define styles with `StyleSheet.create()`.
+- Follow design-system tokens.
+- Typography uses design-system components.
+- All styles support theme switching.
+
+### Desktop
+
+- Use CSS modules or styled-components.
+- Follow design-system foundations (colors, spacing, typography).
+- Full compatibility with dark/light mode is required.
+
+## Performance
+
+- Memoize expensive operations with `useMemo`.
+- Stabilize callbacks with `useCallback`.
+- Wrap costly components in `React.memo`.
+- Apply list virtualization where needed.
+- Use lazy loading for large screens or modules.
+
+## Navigation
+
+### Mobile
+
+- Use React Navigation.
+- Ensure correct deep-link support.
+- Keep navigation types strict and consistent.
+
+### Desktop
+
+- Use React Router.
+- Implement route guards when necessary.
+- Maintain clear history logic.
+
+## Data Fetching
+
+- Use RTK Query
+  - `dada-client` or `cal-client` are good examples to follow
+- Use consistent loading, retry, and error states.
+- Prefer optimistic UI when appropriate.
+- Apply caching and stale-time strategies.
+
+## Accessibility
+
+### Mobile
+
+- Provide accessible labels for all interactive elements.
+- Support screen reader flows.
+- Ensure proper focus transitions.
+
+### Desktop
+
+- Use semantic HTML tags.
+- Implement full keyboard navigation.
+- Apply meaningful ARIA attributes when required.
+
+## Error Boundaries
+
+- Wrap critical areas in error boundaries.
+- Report errors to monitoring services.
+- Provide clean, user-friendly fallback UIs.
+
+## Platform-Specific Code
+
+### React Native
+
+- Use `Platform.select` for small platform variations.
+- Ensure behavior parity across iOS and Android.
+
+### Desktop
+
+- Use environment flags for Electron/Web differences.
+- Keep platform abstraction consistent.
+
+## Animations
+
+### Mobile
+
+- Use the native driver whenever feasible.
+- Prefer `Animated` and layout animations for performance.
+
+### Desktop
+
+- Use CSS transitions for lightweight animations.
+- Use Framer Motion for structured or complex animations.
+- Respect reduced-motion system preferences.
+
+## Internationalization (i18n)
+
+- Use `react-i18next` consistently.
+- Keep translation keys descriptive and structured.
+- Support pluralization, gender, and variable interpolation.
+- Validate components across multiple locales.
diff --git a/.cursor/rules/react-new-arch.mdc b/.cursor/rules/react-new-arch.mdc
@@ -0,0 +1,116 @@
+---
+alwaysApply: true
+description: React New Architecture engineering rules (newArch) for Ledger Live
+globs: ["**/*.ts", "**/*.tsx"]
+---
+
+# React New Architecture (`newArch`)
+
+_Mandatory rules for all files inside `src/newArch/`._
+
+## Migration Principles
+
+- New code must conform to `newArch` patterns.
+- Upon completion, `src/newArch` replaces `src/` entirely.
+- Applies equally to `ledger-live-mobile` and `ledger-live-desktop` codebases.
+- Code reviews enforce strict adherence.
+
+## Folder & Project Structure
+
+### High-Level Structure
+
+```
+src/newArch/
+├── features/
+│   └── FeatureName/
+│       ├── __integrations__/
+│       ├── components/
+│       ├── screens/
+│       ├── hooks/
+│       └── utils/
+├── components/
+├── hooks/
+└── utils/
+```
+
+### Feature Folder Responsibilities
+
+- `components/` gathers reusable UI elements across multiple screens.
+- `screens/` contains individual screen folders and their private building blocks.
+- `hooks/` contains feature-specific reusable hooks.
+- `utils/` contains feature-scoped utilities.
+
+### Nesting Guidelines
+
+- Place elements inside the closest folder matching their reuse scope.
+- Screen-specific building blocks stay inside the screen folder.
+- Feature-level components belong to `FeatureName/components/`.
+- Global shared UI belongs to `src/newArch/components/`.
+
+## Component & File Patterns
+
+### Index-Based Structure
+
+- Each component resides in its own folder.
+- Entry file: `index.tsx`.
+- Support files live alongside it:
+
+  - `use<ComponentName>ViewModel.ts`
+  - `types.ts`
+  - `styles.ts`
+
+### Naming Rules
+
+- Let folder hierarchy convey context; component names remain concise.
+- Use the **List / Detail** naming pattern for multi-view workflows.
+- ViewModel hooks always follow the naming: `use<ComponentName>ViewModel.ts`
+
+### Constants & Utils
+
+- Store utilities in a `utils/` directory near their consumers.
+- Shared constants belong to `utils/constants/`.
+- Utilities remain separate from component folders.
+
+## Import Rules
+
+- Keep relative imports shallow (within one directory level).
+- Use TypeScript path aliases for broader access.
+- Import directories via alias paths instead of long relative chains.
+- Importing `index.tsx` explicitly is discouraged — rely on folder alias exports.
+
+## ViewModel Pattern
+
+- Components needing external logic use: `Container → ViewModel → View`.
+- The ViewModel produces data and handlers.
+- The View receives everything via props.
+- The View does not directly call hooks that connect to external systems.
+
+## Data Fetching & State Management
+
+- Use RTK Query
+  - `dada-client` or `cal-client` are good examples to follow
+- Use consistent loading, retry, and error states.
+- Prefer optimistic UI when appropriate.
+- Apply caching and stale-time strategies.
+
+## Testing
+
+### Integration Tests
+
+- Every new feature under `src/newArch/` **must include an integration test** located inside its `__integrations__/` folder.
+- A **minimal integration test** must be created as soon as the feature folder is added.
+- This test should be expanded and updated progressively as the feature grows.
+- Integration tests ensure that screens, components, hooks, and navigation work together as expected within the New Architecture.
+- use MSW to mock Network API calls
+
+### Hooks & Utils
+
+- All **hooks** must have dedicated tests validating their logic, edge cases, and interactions with external systems.
+- **Utilities (`utils/`)** must also be covered by unit tests to ensure stability and prevent regressions.
+- Keep test files close to their source whenever appropriate (e.g., `utils/` and `hooks/` can contain their own `__tests__/`).
+
+### General Guidelines
+
+- Prefer **integration-first** testing where possible, to validate the complete behavior of the feature.
+- Keep mocks minimal—favor realistic wiring of components through the New Architecture patterns.
+- Follow the project's existing **custom test renderer** conventions and best practices.
diff --git a/.cursor/rules/testing.mdc b/.cursor/rules/testing.mdc
@@ -0,0 +1,45 @@
+---
+globs: ["*.test.*", "*.spec.*", "**/tests/**", "**/__tests__/**"]
+description: General, Desktop, and Mobile testing patterns for Ledger Wallet
+alwaysApply: true
+---
+
+# Testing Rules
+
+- **Stack:** Jest, MSW, coin-tester
+- **File Structure:**
+  - Tests next to source files
+  - `.test.ts` / `.spec.ts`
+  - `__tests__` for grouped tests
+  - `__integrations__` for integration tests
+- **Test Types:** Unit, Integration (prefer integration for complex features)
+- **Rules:**
+  - Test behavior, not implementation
+  - Deterministic tests
+  - Keep mocks minimal
+  - use MSW for Network API calls (use same pattern as `apps/ledger-live-mobile/__tests__/server.ts` with `handlers`)
+  - Integrate Redux when relevant
+  - Async: use `async/await` + `waitFor`
+- **Test Data:** Fixtures under `__fixtures__`, use factories/builders, avoid hardcoded/unrealistic values
+- **Maintenance:** Keep tests minimal/focused, remove obsolete tests
+- **Query Priority:** ByRole > ByLabelText > ByText > ByTestId
+
+---
+
+# Desktop Testing
+
+- **Environment:** ledger-live-desktop
+- **Render function:** imported from `tests/testSetup`
+- **Mocking Network** `apps/ledger-live-desktop/tests/server.ts`
+- **Stack:** + React Testing Library + MSW
+- **Command** inside ledger-live-desktop `pnpm test:jest "filename"` or `pnpm test:jest` to run them all
+
+---
+
+# Mobile Testing
+
+- **Environment:** ledger-live-mobile
+- **Render function:** imported from `@tests/test-renderer`
+- **Mocking Network** `apps/ledger-live-mobile/__tests__/server.ts`
+- **Stack:** + React Native Testing Library + MSW
+- **Command** inside ledger-live-mobile `pnpm test:jest "filename"` or `pnpm test:jest` to run them all
diff --git a/.cursor/rules/typescript.mdc b/.cursor/rules/typescript.mdc
@@ -0,0 +1,72 @@
+---
+alwaysApply: true
+globs: ["**/*.ts", "**/*.tsx"]
+description: React and React Native development patterns for Ledger Wallet
+---
+
+## **Components**
+
+- Use **function components** with typed props.
+- Prefer **React.FC** only when children typing is needed; otherwise avoid.
+- Memoize when beneficial (`React.memo`, `useMemo`, `useCallback`).
+
+---
+
+## **Props & State**
+
+- Type props with **interfaces** or **type aliases** (PascalCase).
+- Use `readonly` for immutable props/state shapes.
+- Avoid `any`; use `unknown` when necessary.
+- Prefer discriminated unions for state machines.
+
+---
+
+## **Hooks**
+
+- Extract logic into **custom hooks**.
+- Type hook return values explicitly.
+- Avoid unnecessary dependencies in hook arrays.
+
+---
+
+## **Data & Types**
+
+- Store types in `types.ts` files.
+- Use **Zod** for runtime validation.
+
+---
+
+## **Imports & Exports**
+
+- Prefer **named imports** and **named exports**.
+- Always declare imports at the beginning of source files.
+- Import order:
+
+  1. External libs
+  2. Internal modules
+  3. Types
+
+- Avoid default exports.
+
+---
+
+## **Error Handling**
+
+- Use custom error classes with `code` and optional context.
+- Prefer **Result<T, E>** patterns for recoverable failures.
+
+---
+
+## **Async Patterns**
+
+- Use `async/await`.
+- Wrap async code with `try/catch`.
+- Avoid inline Promises inside JSX.
+
+---
+
+## **Performance**
+
+- Use `as const` for literals.
+- Use mapped types for transformations.
+- Use memoization and stable references to reduce re-renders.
diff --git a/.cursorrules b/.cursorrules
@@ -1,5 +0,0 @@
-# Ledger Live - Cursor Rules
-
-## Design System - LDLS (Lumen)
-
-@node_modules/@ledgerhq/ldls-ui-react/ai-rules/RULES.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
