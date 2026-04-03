# Agent Config Files for supabase-queue-sql-escape

Repo: supabase/supabase
Commit: 273102323d2959bf5e24678a3388409e91e2ccb4
Files found: 13


---
## .claude/CLAUDE.md

```
   1 | # Supabase Monorepo
   2 | 
   3 | pnpm 10 + Turborepo monorepo. Requires Node >= 22.
   4 | 
   5 | ## Structure
   6 | 
   7 | | Directory         | Purpose                                                      |
   8 | | ----------------- | ------------------------------------------------------------ |
   9 | | `apps/studio`     | Supabase Studio/Dashboard — Next.js (pages router), React 18 |
  10 | | `apps/docs`       | Documentation site                                           |
  11 | | `apps/www`        | Marketing website                                            |
  12 | | `packages/ui`     | Shared UI components (shadcn/ui based)                       |
  13 | | `packages/common` | Shared utilities and telemetry constants                     |
  14 | | `e2e/studio`      | Playwright E2E tests for Studio                              |
  15 | 
  16 | ## Common Commands
  17 | 
  18 | ```bash
  19 | pnpm install                          # install dependencies
  20 | pnpm dev:studio                       # run Studio dev server
  21 | pnpm test:studio                      # run Studio unit tests (vitest)
  22 | pnpm --prefix e2e/studio run e2e       # run Studio E2E tests (playwright)
  23 | pnpm build --filter=studio             # build Studio
  24 | pnpm lint --filter=studio              # lint Studio
  25 | pnpm typecheck                        # typecheck all packages
  26 | ```
  27 | 
  28 | ## Conventions
  29 | 
  30 | **UI** — import from `'ui'`, use `_Shadcn_` suffixed variants for form primitives. Check `packages/ui/index.tsx` before creating new primitives.
  31 | 
  32 | **Styling** — Tailwind only, semantic tokens (`bg-muted`, `text-foreground-light`), no hardcoded colors.
  33 | 
  34 | ## Studio
  35 | 
  36 | Pages router. Co-locate sub-components with parent. Avoid barrel re-export files.
  37 | 
  38 | See studio-* skills for detailed studio conventions.
```


---
## .github/copilot-instructions.md

```
   1 | # Copilot Code Review Instructions
   2 | 
   3 | ## Review Policy — Read This First
   4 | 
   5 | You are a code reviewer for a large TypeScript/Next.js/React monorepo. Your reviews must be **low-noise and high-signal**. The team acts on fewer than 20% of default Copilot suggestions, so every comment you leave must earn its place.
   6 | 
   7 | ### Confidence Threshold
   8 | 
   9 | Only comment when you are **>85% confident** the issue is a real bug, security vulnerability, or logic error. If you are unsure, do not comment. Silence is better than noise.
  10 | 
  11 | ### What NOT to Comment On
  12 | 
  13 | Our CI pipeline already validates the following. **Never comment on these topics:**
  14 | 
  15 | - **Formatting or whitespace** — Prettier runs on every PR
  16 | - **Linting issues** — ESLint with auto-fix runs on every PR
  17 | - **Type errors** — TypeScript strict-mode typecheck runs on every PR
  18 | - **Typos or spelling** — Automated typo detection runs on every PR
  19 | - **Missing tests for trivial changes** — Handled by topic-specific test instructions
  20 | - **Import ordering or grouping** — Handled by linter
  21 | - **Naming style preferences** (camelCase vs snake_case debates) — Follow existing file conventions
  22 | - **Accessibility attributes on shadcn/Radix UI components** — See `studio-shadcn-components.instructions.md` for details
  23 | 
  24 | ### What TO Comment On (Priority Order)
  25 | 
  26 | 1. **Logic errors and bugs** — Off-by-one, null derefs, wrong conditional, unreachable code, incorrect early returns
  27 | 2. **Security vulnerabilities** — XSS, SQL injection, auth bypass, secrets in code, unsafe `dangerouslySetInnerHTML`
  28 | 3. **Race conditions and async bugs** — Missing `await`, unhandled promise rejections, stale closures, effect cleanup issues
  29 | 4. **Data loss risks** — Destructive operations without confirmation, missing error handling on writes
  30 | 5. **API contract violations** — Wrong HTTP method, missing auth headers, incorrect request/response shapes
  31 | 
  32 | ### Comment Style
  33 | 
  34 | - **Be advisory, not prescriptive.** Use "Consider..." or "This may..." — never demand changes.
  35 | - **One comment per distinct issue.** Do not leave multiple comments about the same underlying problem.
  36 | - **No self-contradictions.** If you suggest a change, do not then flag a problem with your own suggestion.
  37 | - **Do not comment on individual commits.** Review the final state of the PR diff only.
  38 | 
  39 | ## Repo Context
  40 | 
  41 | This is a TypeScript/Next.js/React monorepo:
  42 | 
  43 | - `apps/studio/` — Supabase Dashboard (primary review target)
  44 | - `apps/www/` — Marketing site
  45 | - `apps/docs/` — Documentation
  46 | - `packages/common/` — Shared code including telemetry definitions
  47 | 
  48 | ## Topic-Specific Guidelines
  49 | 
  50 | Path-specific rules in `.github/instructions/`:
  51 | 
  52 | - **Telemetry**: `studio-telemetry.instructions.md` — event naming, property conventions, feature flag measurement
  53 | - **Testing**: `studio-testing.instructions.md` — test strategy, extraction patterns, coverage expectations
  54 | - **Error Handling**: `studio-error-handling.instructions.md` — error classification, `ErrorMatcher` usage
  55 | - **E2E Tests**: `studio-e2e-tests.instructions.md` — selector priority, anti-patterns (`waitForTimeout`, `force: true`)
  56 | - **Composition Patterns**: `studio-composition-patterns.instructions.md` — avoid boolean props, use compound components
  57 | - **shadcn/Radix Components**: `studio-shadcn-components.instructions.md` — accessibility handled by primitives, do not flag
  58 | 
  59 | These files are scoped to `apps/studio/` and applied automatically during reviews.
```


---
## .claude/skills/studio-best-practices/SKILL.md

```
   1 | ---
   2 | name: studio-best-practices
   3 | description: React and TypeScript best practices for Supabase Studio.
   4 | ---
   5 | 
   6 | # Studio Best Practices
   7 | 
   8 | Applies to `apps/studio/**/*.{ts,tsx}`.
   9 | 
  10 | ## Boolean Naming
  11 | 
  12 | Use descriptive prefixes — derive from existing state rather than storing separately:
  13 | - `is` — state/identity: `isLoading`, `isPaused`, `isNewRecord`
  14 | - `has` — possession: `hasPermission`, `hasData`
  15 | - `can` — capability: `canUpdateColumns`, `canDelete`
  16 | - `should` — conditional behavior: `shouldFetch`, `shouldRender`
  17 | 
  18 | ## Component Structure
  19 | 
  20 | Keep components under 200-300 lines. Split when you see multiple distinct UI sections,
  21 | complex conditional rendering, or multiple unrelated useState calls.
  22 | Co-locate sub-components in the same directory as the parent. Avoid barrel re-export files.
  23 | 
  24 | ## Data Fetching
  25 | 
  26 | All data fetching uses TanStack Query (React Query).
  27 | 
  28 | ## State Management
  29 | 
  30 | Keep state as local as possible; lift only when needed.
  31 | Group related form state with react-hook-form rather than multiple useState calls.
  32 | 
  33 | ## TypeScript
  34 | 
  35 | Define prop interfaces explicitly. Use discriminated unions for complex state.
  36 | Avoid `as any` / `as Type` casts. Validate at boundaries with zod.
  37 | 
  38 | ## Testing
  39 | 
  40 | Extract logic into `.utils.ts` pure functions and test exhaustively.
```


---
## .claude/skills/studio-error-handling/SKILL.md

```
   1 | ---
   2 | name: studio-error-handling
   3 | description: Error display and troubleshooting pattern for Supabase Studio.
   4 | ---
   5 | 
   6 | # Studio Error Handling Pattern
   7 | 
   8 | Classification happens in the data layer: handleError in data/fetchers.ts tests the error
   9 | message against ERROR_PATTERNS and throws the matching error subclass.
  10 | 
  11 | Key files: data/error-patterns.ts, types/api-errors.ts, ErrorMatcher.tsx, error-mappings.tsx
  12 | 
  13 | Pass the full error object from React Query — not error.message.
  14 | Do not put regex patterns in error-mappings.tsx — they belong in data/error-patterns.ts.
```


---
## .claude/skills/studio-queries/SKILL.md

```
   1 | ---
   2 | name: studio-queries
   3 | description: React Query conventions for Supabase Studio.
   4 | ---
   5 | 
   6 | # Studio Query Conventions
   7 | 
   8 | Uses queryOptions pattern. Keys in dedicated keys.ts files.
   9 | Mutation hooks use useMutation + useQueryClient for cache invalidation.
  10 | Imperative fetching via executeSql for raw SQL queries.
```


---
## .claude/skills/studio-testing/SKILL.md

```
   1 | ---
   2 | name: studio-testing
   3 | description: Testing strategy for Supabase Studio.
   4 | ---
   5 | 
   6 | # Studio Testing Strategy
   7 | 
   8 | Extract logic into .utils.ts pure functions and test exhaustively.
   9 | Component tests only for complex UI interactions.
  10 | E2E tests (Playwright) for shared features and critical user journeys.
```


---
## .claude/skills/studio-ui-patterns/SKILL.md

```
   1 | ---
   2 | name: studio-ui-patterns
   3 | description: Layout and UI component patterns for Supabase Studio.
   4 | ---
   5 | 
   6 | # Studio UI Patterns
   7 | 
   8 | Layout: PageContainer/PageHeader/PageSection.
   9 | Forms: react-hook-form + zod, FormItemLayout.
  10 | Tables: DataGrid for large datasets.
  11 | Empty states: use shared EmptyState component.
```


---
## .claude/skills/telemetry-standards/SKILL.md

```
   1 | ---
   2 | name: telemetry-standards
   3 | description: PostHog event naming and property standards for Supabase.
   4 | ---
   5 | 
   6 | # Telemetry Standards
   7 | 
   8 | Event naming: [object]_[verb] in snake_case. Properties in camelCase.
   9 | Use useTrack hook. Define events in telemetry-constants.ts.
  10 | Do not track PII or sensitive data.
```


---
## .claude/skills/use-static-effect-event/SKILL.md

```
   1 | ---
   2 | name: use-static-effect-event
   3 | description: Documents the useStaticEffectEvent hook (polyfill for React's useEffectEvent).
   4 | ---
   5 | 
   6 | # useStaticEffectEvent
   7 | 
   8 | Polyfill for React's useEffectEvent. Use when you need to read latest state in Effects
   9 | without re-triggering. Do not use in render or event handlers.
```


---
## .claude/skills/vercel-composition-patterns/SKILL.md

```
   1 | ---
   2 | name: vercel-composition-patterns
   3 | description: React composition patterns — avoid boolean prop proliferation, use compound components.
   4 | ---
   5 | 
   6 | # React Composition Patterns
   7 | 
   8 | Avoid boolean prop proliferation. Use compound components.
   9 | Decouple state from UI. Use generic context interfaces.
  10 | Prefer children over render props. Explicit component variants.
```


---
## .claude/skills/vercel-composition-patterns/AGENTS.md

```
   1 | # React Composition Patterns (Full Reference)
   2 | 
   3 | Comprehensive guide covering: avoid boolean prop proliferation, compound components,
   4 | decouple state from UI, generic context interfaces, lift state into providers,
   5 | explicit component variants, prefer children over render props, React 19 API changes.
   6 | (947 lines — see full file in repo)
```


---
## .agents/skills/vitest/SKILL.md

```
   1 | ---
   2 | name: vitest
   3 | description: Vitest fast unit testing framework powered by Vite with Jest-compatible API.
   4 | ---
   5 | 
   6 | # Vitest
   7 | 
   8 | Next-generation testing framework powered by Vite. Jest-compatible API.
   9 | Native ESM, TypeScript, JSX support. Smart watch mode.
  10 | Multi-threaded workers. Built-in coverage via V8 or Istanbul.
```


---
## .claude/skills/studio-e2e-tests/SKILL.md

```
   1 | ---
   2 | name: studio-e2e-tests
   3 | description: Playwright E2E test patterns for Supabase Studio.
   4 | ---
   5 | 
   6 | # Studio E2E Tests
   7 | 
   8 | Playwright-based. Use data-testid selectors. Avoid waitForTimeout and force: true.
   9 | API mocking for external services. Proper cleanup in afterEach.
  10 | CI vs local debugging considerations.
```
