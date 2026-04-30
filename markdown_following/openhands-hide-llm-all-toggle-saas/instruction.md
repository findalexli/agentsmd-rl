# Hide the "All" LLM-settings toggle in SaaS mode

You are working in the OpenHands frontend (`frontend/`, React + TypeScript +
React Router + Vitest).

## Background

The settings UI has three view tiers — **Basic**, **Advanced**, and **All** —
and the toggle bar at the top of each settings section lets the user switch
between them. The `All` tier exposes low-level fields (prominence `minor`)
that are only meaningful for power users; surfacing them in the SaaS/OHE
deployment leaks low-level configuration that should not be shown there.

The settings tier-toggle bar lives in the shared component used by every SDK
settings section. Each toggle is rendered with a stable `data-testid`:

| toggle   | `data-testid`                  |
|----------|--------------------------------|
| Basic    | `sdk-section-basic-toggle`     |
| Advanced | `sdk-section-advanced-toggle`  |
| All      | `sdk-section-all-toggle`       |

App mode is exposed by the existing config query as `config.app_mode`, with
the values `"oss"` and `"saas"`.

The LLM settings route renders inside `<SdkSectionPage sectionKeys={["llm"]} …/>`.

## What is broken

Two related symptoms on the LLM settings screen:

1. **`All` toggle is exposed in SaaS mode.** When `config.app_mode === "saas"`,
   the LLM settings page currently still renders the `All` toggle whenever the
   schema contains any minor-prominence field. SaaS builds must instead show
   only `Basic` and `Advanced` for the LLM screen — the `All` toggle must not
   appear in the DOM at all.

2. **`Advanced` toggle disappears when the LLM schema has no major-prominence
   fields.** The default LLM schema is dominated by `critical` fields (model,
   API key, base URL). With the current logic, `Advanced` is only rendered
   when the schema contains at least one `major` field, so on a SaaS-shaped,
   critical-only LLM schema the user is dropped to `Basic`-only, with no way
   to reach the `Advanced` form (custom-model input, base-URL input, etc.).
   The LLM screen must always offer the `Advanced` tier even when the filtered
   schema has no `major` fields, so the user can always reach
   `data-testid="llm-settings-form-advanced"`,
   `data-testid="llm-custom-model-input"` and
   `data-testid="base-url-input"` from the toggle bar.

The fix must apply only to the LLM screen — other consumers of the shared
section component (e.g. agent settings, conversation settings) must keep the
existing behaviour where `Advanced` only shows up when the schema has major
fields, and `All` only shows up when the schema has minor fields.

## Required behaviour (matches the test contract)

Update the shared SDK settings section component so that callers can opt in /
opt out of the Advanced and All toggles independently of the schema, then
wire the LLM route to use them:

- The shared section component must accept two new boolean props (any
  reasonable names — the test suite passes them as **`forceShowAdvancedView`**
  and **`allowAllView`**, and you must use those exact prop names so the
  tests can configure the component):
  - `forceShowAdvancedView` (default `false`) — when `true`, the Advanced
    toggle is rendered even if the filtered schema has no `major` fields.
  - `allowAllView` (default `true`) — when `false`, the All toggle is
    *not* rendered, even if the filtered schema has `minor` fields.
- The currently-selected view must be **normalized** against the props so the
  page never lands on a tier whose toggle is hidden:
  - If the resolved initial view is `"all"` but the All toggle is hidden, fall
    back to `"advanced"` if Advanced is shown, otherwise to `"basic"`.
  - If the resolved initial view is `"advanced"` but the Advanced toggle is
    hidden, fall back to `"all"` if All is shown, otherwise to `"basic"`.
- The LLM settings route must opt the LLM screen in to forced-advanced and
  must disable the All toggle exactly when the app is in SaaS mode (i.e.
  `allowAllView={!isSaasMode}` and `forceShowAdvancedView` always set).

## How to verify

The repo's vitest suite covers all three behaviours. Two test files matter:

- `frontend/__tests__/routes/llm-settings.test.tsx`
- `frontend/__tests__/components/features/settings/sdk-settings/sdk-section-page.test.tsx`

Specifically, the following named tests must pass:

1. `"shows the advanced toggle when it is forced for a critical-only schema"`
   in the `SdkSectionPage` describe block — asserts that with
   `forceShowAdvancedView: true` and a critical-only schema, the
   `sdk-section-advanced-toggle` is in the DOM and the `sdk-section-all-toggle`
   is **not**.
2. `"shows Advanced and All toggles in OSS mode for the default LLM route schema"`
   in the `LlmSettingsScreen` describe block — asserts both toggles are
   present in OSS.
3. `"keeps Advanced visible but hides All in SaaS mode for the default LLM route schema"`
   — asserts the Advanced toggle is present, the All toggle is **not**
   present, and that clicking Advanced reveals
   `llm-settings-form-advanced`, `llm-custom-model-input` and
   `base-url-input`.

Runner commands (cwd = `frontend/`):

```bash
npx vitest run __tests__/routes/llm-settings.test.tsx
npx vitest run __tests__/components/features/settings/sdk-settings/sdk-section-page.test.tsx
```

The full file in each case must pass — your change must not regress any
existing test in either file.

## Code Style Requirements

The repo's frontend toolchain enforces formatting and types. Per
`AGENTS.md`, frontend changes must satisfy:

- `npm run typecheck` — runs `react-router typegen && tsc`. **This is checked
  by the verifier.** TypeScript errors anywhere in `frontend/` will fail the
  task.
- `npm run lint:fix` and `npm run build` are part of the repo's pre-push
  workflow; keep your changes lint-clean (`eslint`, `prettier`).

## Constraints

- Stay inside `frontend/`. Do not modify backend or `enterprise/` code.
- Do not edit anything under `frontend/__tests__/` or
  `frontend/src/mocks/`. The verifier expects those files unchanged from
  the state you find them in.
- Preserve the existing data-flow architecture: UI components go through
  TanStack Query hooks (`frontend/src/hooks/query/`,
  `frontend/src/hooks/mutation/`) and never call `frontend/src/api/*`
  directly. The LLM screen is a "Pattern 2 / Manual Save" form — keep its
  `useSaveSettings` flow and `isDirty` tracking; do not switch it to
  immediate-save.
- The repo's working tree at task start has the new test cases and an extra
  `llm.temperature` minor field already added to the mock schema. Treat them
  as part of the spec — do not remove or alter them.

## Suggested working files

You'll likely need to touch the shared SDK section component and the LLM
route component. Use repository search (`grep`, `rg`) to locate them — file
paths are intentionally not given here so localization is part of the task.
