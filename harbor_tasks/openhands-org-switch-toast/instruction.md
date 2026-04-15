# Task: Add Visual Feedback for Organization Switching

## Problem

When users switch between organizations in the OpenHands frontend, there is no visual confirmation that the switch was successful. Users need feedback to know which organization they are now working in.

## Goal

Add a toast notification that displays when users switch between organizations, with different messages depending on the target:

1. **Switching to a regular organization**: Show `"You have switched to organization: {name}"` where `{name}` is interpolated via the i18n variable `{{name}}`.
2. **Switching to personal workspace**: Show `"You have switched to your personal workspace."`

## Relevant Files

1. **`frontend/src/hooks/mutation/use-switch-organization.ts`** — the mutation hook that handles organization switching
2. **`frontend/src/components/features/org/org-selector.tsx`** — the UI dropdown component that triggers the switch
3. **`frontend/src/i18n/declaration.ts`** — i18n key declarations
4. **`frontend/src/i18n/translation.json`** — translation strings for all languages
5. **`frontend/__tests__/components/features/org/org-selector.test.tsx`** — unit tests

## Technical Notes

- The project uses **TanStack Query** for mutations and **react-hot-toast** for toast notifications
- Use `displaySuccessToast()` from `#/utils/custom-toast-handlers` for showing success messages
- Use **react-i18next** with the `useTranslation()` hook for internationalization
- The organization object has an `is_personal` boolean field

## Requirements

### 1. i18n keys and translations

Add the following two i18n keys to `declaration.ts` and `translation.json`:

- **`ORG$SWITCHED_TO_ORGANIZATION`** — message for switching to a team org. Must use the `{{name}}` interpolation variable to embed the organization name.
- **`ORG$SWITCHED_TO_PERSONAL_WORKSPACE`** — message for switching to a personal workspace. No interpolation needed.

Both keys must have translations in all **15** supported language codes:

```
en, ja, zh-CN, zh-TW, ko-KR, no, it, pt, es, ar, fr, tr, de, uk, ca
```

The English translations must be:
- `ORG$SWITCHED_TO_ORGANIZATION`: `"You have switched to organization: {{name}}"`
- `ORG$SWITCHED_TO_PERSONAL_WORKSPACE`: `"You have switched to your personal workspace."`

### 2. Mutation hook changes

Modify `useSwitchOrganization` in `use-switch-organization.ts` so that:

- The mutation function accepts parameters named **`orgId`**, **`orgName`**, and **`isPersonal`** (the hook currently only receives `orgId`; extend it to also receive the org name and whether it is personal).
- It imports and uses **`displaySuccessToast`** and **`useTranslation`** from react-i18next.
- In the `onSuccess` callback, it selects the appropriate i18n key (`ORG$SWITCHED_TO_ORGANIZATION` or `ORG$SWITCHED_TO_PERSONAL_WORKSPACE`) based on `isPersonal`, calls `t()` with `{ name: orgName }` as the interpolation argument for the team-org case, and passes the result to `displaySuccessToast`.

### 3. Component changes

Modify `OrgSelector` in `org-selector.tsx` so that:

- Before calling `switchOrganization`, it finds the selected organization object from the organizations list using a lookup pattern like `organizations?.find(…)` matching by ID.
- It passes **`orgName`** and **`isPersonal`** (derived from the found org's `is_personal` field) to the mutation alongside `orgId`.

### 4. Unit tests

Extend the test file `org-selector.test.tsx` with:

- A test described as **`"should display toast with organization name when switching to a team organization"`** that verifies `displaySuccessToast` is called with the string `"You have switched to organization: Acme Corp"`.
- A test described as **`"should display toast for personal workspace when switching to personal workspace"`** that verifies `displaySuccessToast` is called with `"You have switched to your personal workspace."`.
- The mock for `useTranslation` must accept a `params` argument typed as `params?: Record<string, string>` and handle the interpolation via `params?.name` (or `params.name`).
- Spy on `displaySuccessToast` from `#/utils/custom-toast-handlers` to assert its calls.
