# Add Visual Feedback for Organization Switching

## Problem

When users switch between organizations in the OpenHands frontend, there is no visual confirmation that the switch was successful. Users need feedback to know which organization they are now working in.

## Goal

Add a toast notification that displays when users switch between organizations, with different messages depending on the target:

1. **Switching to a regular organization**: Show a message that includes the organization name via i18n interpolation.
2. **Switching to personal workspace**: Show a fixed message with no interpolation.

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

Add two i18n keys to `declaration.ts` and `translation.json`. The keys must:

- Have translations in all **15** supported language codes: `en, ja, zh-CN, zh-TW, ko-KR, no, it, pt, es, ar, fr, tr, de, uk, ca`
- Use `{{name}}` interpolation for the team organization key

The English translations must be:
- Team organization key: `"You have switched to organization: {{name}}"`
- Personal workspace key: `"You have switched to your personal workspace."`

Name the keys something descriptive that clearly indicates their purpose (e.g., something like `ORG$SWITCHED_TO_ORGANIZATION` and `ORG$SWITCHED_TO_PERSONAL_WORKSPACE`).

### 2. Mutation hook changes

Modify `useSwitchOrganization` in `use-switch-organization.ts` to show a toast on successful organization switch:

- The mutation function needs to know the organization name and whether it's a personal workspace (derive this from the organization's `is_personal` field)
- In the `onSuccess` callback, use the appropriate i18n key to generate the toast message, passing the organization name as the interpolation argument for team organizations
- Import and use `displaySuccessToast` from `#/utils/custom-toast-handlers`
- Import and use `useTranslation` from react-i18next to call the `t()` function

### 3. Component changes

Modify `OrgSelector` in `org-selector.tsx` so that when the user selects an organization:

- Look up the organization object from the organizations list before calling the switch mutation
- Pass enough information to the mutation so it can display the appropriate toast (include whether it's a personal workspace so the hook can choose the right message)

### 4. Unit tests

Extend the test file `org-selector.test.tsx` with tests that verify the toast notifications appear correctly:

- One test that verifies the toast shows with the organization name when switching to a team organization (use organization name "Acme Corp" in the test)
- One test that verifies the toast shows the personal workspace message when switching to a personal workspace
- The mock for `useTranslation` should accept a `params` argument for handling interpolation
