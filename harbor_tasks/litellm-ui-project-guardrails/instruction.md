# Add guardrails to the LiteLLM project create/edit forms

The LiteLLM proxy backend already accepts a top-level `guardrails: string[]`
field on its project create/update API. The dashboard UI, however, has no
way for users to set this field — there is no form control for it, the
TypeScript types do not allow it, and edit mode silently drops the
project's existing guardrails.

This task is to wire guardrails through the project create/edit dashboard
forms, end-to-end, so that an admin can pick (or type) one or more
guardrail names when creating a project, see them when editing the project
again, and have the dashboard send them to the backend.

The repository is checked out at `/workspace/litellm`; the UI lives under
`ui/litellm-dashboard/`.

## What is broken today (symptoms)

1. **`buildProjectApiParams(values)`** (the helper that converts form
   values into the POST/PATCH payload) does not recognise
   `values.guardrails`. Even if a `guardrails` array were on the
   `ProjectFormValues` object, the helper would not forward it to the
   request body. As a result, projects are always created without
   guardrails.

2. **`ProjectFormValues`**, **`ProjectCreateParams`**, and
   **`ProjectUpdateParams`** TypeScript interfaces have no `guardrails`
   field. Anything the form puts there is currently typed away.

3. **`ProjectBaseForm`** has no UI control for guardrails. Users cannot
   select existing guardrails or enter new ones from the project form.

4. **`EditProjectModal`** does not pre-populate the form's `guardrails`
   field from `project.metadata.guardrails`. Worse, when the backend
   returns guardrails inside `metadata` (as it does for some legacy data
   paths and some configurations), the modal currently displays
   `guardrails` as a regular user-facing key/value metadata row, which
   confuses users and lets them edit it as a free-form string.

## The fix (what to deliver)

Make the dashboard send and receive a top-level `guardrails: string[]`
parameter wherever projects are created or edited, while keeping the
existing behaviour of every other form field intact.

Concretely, you must:

1. Update the `ProjectFormValues` interface to allow an optional
   `guardrails?: string[]` field, and add the same field to both the
   `ProjectCreateParams` and `ProjectUpdateParams` interfaces.
2. Update `buildProjectApiParams` so that when `values.guardrails` is a
   non-empty array, the returned object has a top-level
   `guardrails` array (NOT nested under `metadata`). When `guardrails` is
   missing, `undefined`, or an empty array, the returned object must NOT
   contain a `guardrails` key at all.
3. Add a `Guardrails` form item to `ProjectBaseForm`, located inside the
   existing **Advanced Settings** collapse panel. The control must:
   - Use a multi-select that allows free entry of new tag values (so
     admins can type a guardrail name that is not already configured on
     the proxy).
   - Be labelled `Guardrails`.
   - Pre-populate its option list from the existing guardrails available
     on the proxy (use the helper exported from `@/components/networking`
     that returns the guardrails the proxy knows about).
4. Update `EditProjectModal` so that when a project is opened for editing:
   - If `project.metadata.guardrails` is an array, the form's
     `guardrails` field is pre-populated from it.
   - The string `guardrails` is treated as an internal metadata key and
     therefore filtered out of the user-facing key/value metadata table
     (alongside the existing internal keys for model rate limits).

## How the field maps to the API

After the fix, calling `buildProjectApiParams(values)` with
`values.guardrails = ["pii-check", "content-filter"]` must return an
object whose top-level `guardrails` property equals
`["pii-check", "content-filter"]` exactly. With `guardrails: []` or no
`guardrails` at all, the returned object must not have a `guardrails`
property (use `not.toHaveProperty("guardrails")` semantics — no
`undefined` placeholder either).

## Out of scope

- No backend changes are required. The proxy already accepts the
  top-level `guardrails` array.
- No new networking helper is needed; reuse the one that already lists
  guardrails on the proxy.
- No documentation changes are required for this task.

## Code Style Requirements

The repository uses:

- **Vitest** + **React Testing Library** for unit/component tests.
- **TypeScript** with `tsc --noEmit` as part of CI — your changes must
  type-check cleanly under the existing `tsconfig.json`.
- **Ant Design** (`antd`) form primitives — the existing form fields use
  `Form.Item` with `label` and `name` props, and the `Select` component
  for multi-value pickers. Match that style.

Per `AGENTS.md` UI guidelines:

- Tremor is deprecated; do not introduce new Tremor components.
- Prefer queries in this priority order in any tests you add:
  `getByRole`, `getByLabelText`, `getByPlaceholderText`, `getByText`,
  `getByTestId`. Always use `screen` rather than destructuring from
  `render()`. Test names should start with `should ...`.

Per `CLAUDE.md`:

- Place all imports at module top — avoid imports inside function bodies.
- When the UI is wired to an existing backend endpoint, match the API
  contract (here: a top-level `guardrails: string[]`, not nested in
  `metadata`).

## Where to look (orientation)

- The project form lives under
  `ui/litellm-dashboard/src/components/Projects/ProjectModals/`.
- The hooks for create and update are under
  `ui/litellm-dashboard/src/app/(dashboard)/hooks/projects/`.
- The networking module that lists guardrails is exported from
  `@/components/networking`.
- The Advanced Settings panel in the form is the right place to add the
  new control — between the existing "Block Project" toggle and the
  model-specific rate-limits table.

After your changes, the existing repo tests must still pass:

```
cd ui/litellm-dashboard
npx vitest run src/components/Projects/ProjectModals/projectFormUtils.test.ts
npx vitest run src/components/Projects/ProjectModals/ProjectBaseForm.test.tsx
npx tsc --noEmit
```
