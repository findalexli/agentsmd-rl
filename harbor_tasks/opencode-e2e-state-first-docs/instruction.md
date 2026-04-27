# Task: Add state-first conventions to the e2e testing guide

You are working in the `opencode` monorepo. The e2e testing guide for the
desktop/web app lives at:

```
packages/app/e2e/AGENTS.md
```

The guide is the canonical instruction file new contributors and AI agents
read before writing or modifying Playwright e2e tests under
`packages/app/e2e/**/*.spec.ts`.

## What's missing

The guide currently has a `## Test Patterns` chapter and a `## Code Style
Guidelines` chapter. The Code Style Guidelines chapter ends with a
`### Terminal Tests` subsection that already tells contributors to
"Avoid `waitForTimeout` and custom DOM or `data-*` readiness checks" — but
*only* in the narrow context of terminal tests.

Three broader e2e conventions have emerged from recent flake-fix work and
are not documented anywhere:

1. **State-based waiting** — never `page.waitForTimeout(...)`; always wait
   on observable state via `expect(...)`, `expect.poll(...)`, or existing
   helpers. Locator assertions (`toBeVisible()`, `toHaveCount(0)`,
   `toHaveAttribute(...)`) are the right tool for normal UI state;
   `expect.poll(...)` is reserved for probe, mock, or backend state.

2. **Test-only hooks** — when the state a test needs to assert on isn't
   observable from the rendered UI (e.g. internal store transitions,
   pre-render dock states, mock-route resolution), the right answer is a
   small **test-only driver or probe** added to app code. The canonical
   reference implementation already in the tree is
   `packages/app/src/testing/terminal.ts`. Hooks must be inert unless
   explicitly enabled — they cannot add normal-runtime listeners, reactive
   subscriptions, or per-update allocations just to support e2e.

3. **Fluent helpers** — when an interaction is locator-heavy or when intent
   would otherwise be buried in selectors, prefer a fluent helper or
   driver. When the interaction is one or two locators, a helper is just
   noise; use direct locators.

## What to do

Open `packages/app/e2e/AGENTS.md` and add three new H3 (`###`) subsections
to the existing `## Code Style Guidelines` chapter — placed **immediately
after** the `### Terminal Tests` subsection that ends with the
`waitForTimeout` bullet, and **before** the `## Writing New Tests` chapter
that follows.

The three subsections must be titled, in this order:

1. `### Wait on state`
2. `### Add hooks`
3. `### Prefer helpers`

Each subsection must be a short bulleted list (2–4 bullets) of concrete,
imperative guidance — match the voice of the rest of the file. Do not
restate any existing rule verbatim; the new sections expand the existing
terminal-only `waitForTimeout` warning into general principles.

### Required content the test verifies

These specific strings must appear in the output and are checked
programmatically:

- `### Wait on state` (literal heading line) and, inside that section,
  the literal token `page.waitForTimeout` — naming the wall-clock
  anti-pattern explicitly so the rule is actionable.

- `### Add hooks` (literal heading line) and, inside that section, the
  path `packages/app/src/testing/terminal.ts` — citing the existing test-
  only terminal driver as the style template hooks must follow.

- `### Prefer helpers` (literal heading line). The body must be coherent
  bulleted guidance distinguishing helper-worthy interactions from
  one-locator interactions.

### Out of scope

- Do not modify any `.tsx`, `.ts`, or `.spec.ts` file — this task is
  documentation only.
- Do not add a new top-level `##` chapter; the new content goes inside
  the existing `## Code Style Guidelines` chapter.
- Do not remove or rewrite the existing `### Terminal Tests` subsection.

## Style

Follow the file's existing voice: short imperative bullets, backticks
around code identifiers and selector-API methods, no prose paragraphs.
The file is read by agents that prefer scannable rules.
