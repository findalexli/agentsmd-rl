#!/usr/bin/env bash
set -euo pipefail

cd /workspace/taiga-ui

# Idempotency guard
if grep -qF "- Never add comments that restate what the code already says. Comment only non-o" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -14,13 +14,36 @@ the HTML template in the `.html` file (unless the component is trivial and alrea
 - Drop unused variables (and imports).
 - Do not use `console.log` in the codebase.
 - JSDoc is optional for public API surfaces; prefer meaningful names and self‑documenting code.
-- First, write unit and E2E tests and make sure they fail before you start writing the bug fix.
+- For bug fixes, add the smallest failing automated test first and make sure it fails before implementing the fix.
+- Prefer unit or integration tests by default; add E2E coverage only when the bug affects a real user flow across
+  multiple layers.
+
+## Engineering Excellence
+
+- Prefer clarity to cleverness.
+- Write code that is easy to read, easy to change, and hard to misuse.
+- Make the smallest change that fully solves the problem.
+- Preserve existing architecture unless there is a strong reason to improve it.
+
+## Problem-Solving
+
+- Identify the actual constraint, invariant, and bottleneck before coding.
+- Prefer solving the root cause over patching symptoms.
+- Break complex problems into smaller, testable steps.
+- For non-trivial logic, reason explicitly about correctness, complexity, and edge cases.
 
 ## TypeScript guideline
 
 - Use `strict` type checking (`tsconfig.json` → `"strict": true`).
+- Model the domain with precise types.
+- Make invalid states hard to represent.
 - Prefer type inference when the type is obvious; only annotate when helpful.
+- Prefer discriminated unions over multiple boolean flags.
 - Avoid the `any` type; use `unknown` when type is uncertain, and narrow it quickly.
+- Prefer `satisfies` over `as` when validating object shapes.
+- Avoid unnecessary type-level complexity.
+- Prefer explicit return types for exported APIs.
+- Prefer immutable transformations unless controlled mutation is clearly beneficial.
 - Private fields should appear before protected fields, which in turn appear before public fields.
 - Prefer readonly where appropriate.
 - Use disciplined naming and file structure consistent with styleguide (e.g., PascalCase for classes, camelCase for
@@ -87,11 +110,24 @@ the HTML template in the `.html` file (unless the component is trivial and alrea
 - Keep templates simple: avoid complex logic, method calls in loops, deeply nested computations.
 - Use `[class.xyz]`, `[style.prop]`, bindings rather than `ngClass/ngStyle`.
 - Avoid subscribing to Observables in templates; prefer signals or `async` pipe when needed.
-- Prefer structural directives like `*ngIf`, `*ngFor` for flow control, but keep them shallow.
+- Prefer Angular built-in control flow like `@if`, `@for`, and `@switch` in new templates; keep flow control shallow.
+- Preserve existing legacy `*ngIf` / `*ngFor` code when touching older templates unless there is a clear reason to
+  migrate it as part of the change.
 - Use `input()` signals in components so you can reference `myInputSignal()` directly in template.
 - Writable signals are valid with Angular two-way binding syntax (`[(...)]`). Example: `[(open)]="isOpen"` is allowed
   when `isOpen` is a writable signal.
 
+## Readability
+
+- Write boring code in the best sense: obvious, predictable, and maintainable.
+- Prefer early returns to deep nesting.
+- Keep functions small and focused.
+- Keep one level of abstraction per function when practical.
+- Use names that describe intent and domain meaning.
+- Prefer descriptive parameter names over short or ambiguous abbreviations, especially in callbacks.
+- Rewrite surprising code until it becomes obvious.
+- Never add comments that restate what the code already says. Comment only non-obvious intent, constraints, or gotchas.
+
 ## Accessibility & Performance
 
 - Use semantic HTML elements.
@@ -101,6 +137,9 @@ the HTML template in the `.html` file (unless the component is trivial and alrea
 - Avoid unnecessary re‑rendering by leveraging signals and OnPush.
 - Optimize bundle size via lazy loading, tree‑shaking, standalone components.
 - Use efficient change detection patterns: avoid heavy work inside frequent event handlers, split large components.
+- Focus performance work on hot paths, large collections, repeated rendering, and critical startup code.
+- Prefer algorithmic improvements over micro-optimizations.
+- Avoid unnecessary allocations and repeated recomputation in frequently executed code.
 
 ## Style & Architecture
 
@@ -120,6 +159,31 @@ the HTML template in the `.html` file (unless the component is trivial and alrea
 - Document public APIs in services/components when necessary with JSDoc (optional).
 - Use meaningful commit messages, consistent linting, and code reviews.
 
+## API Design
+
+- Design APIs that are easy to understand and hard to misuse.
+- Prefer explicit options to boolean traps.
+- Keep signatures small and intention-revealing.
+- Preserve backward compatibility for public APIs unless a breaking change is required.
+- Optimize APIs for readability at the call site.
+
+## Change Discipline
+
+- Keep diffs small and review-friendly.
+- Do not refactor unrelated code.
+- State assumptions clearly.
+- Briefly explain the plan before significant changes.
+- Summarize trade-offs and verification after implementation.
+
+## Deprecated APIs
+
+- Never use deprecated methods, utilities, or constants from libraries, frameworks, or project code.
+- If a deprecated API is encountered, replace it with the recommended alternative.
+
+## Files
+
+- Every new file must end with a trailing newline.
+
 ## Upgrade & Migration Notes
 
 - Since Angular 19 makes standalone components, directives and pipes default, you can remove `NgModule` boilerplate and
PATCH

echo "Gold patch applied."
