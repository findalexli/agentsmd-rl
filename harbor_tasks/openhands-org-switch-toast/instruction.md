# Task: Add Visual Feedback for Organization Switching

## Problem

When users switch between organizations in the OpenHands frontend, there is no visual confirmation that the switch was successful. Users need feedback to know which organization they are now working in.

## Goal

Add a toast notification that displays when users switch between organizations, with different messages depending on the target:

1. **Switching to a regular organization**: Show "You have switched to organization: {name}"
2. **Switching to personal workspace**: Show "You have switched to your personal workspace."

## Relevant Files

The organization switching functionality is in these files:

1. **`frontend/src/hooks/mutation/use-switch-organization.ts`** - The mutation hook that handles organization switching
2. **`frontend/src/components/features/org/org-selector.tsx`** - The UI component that triggers the switch
3. **`frontend/src/i18n/declaration.ts`** - i18n key declarations
4. **`frontend/src/i18n/translation.json`** - Translation strings (15 languages supported)
5. **`frontend/__tests__/components/features/org/org-selector.test.tsx`** - Unit tests

## Technical Notes

- The project uses **TanStack Query** for mutations and **react-hot-toast** for toast notifications
- The `displaySuccessToast()` utility from `#/utils/custom-toast-handlers` should be used for showing success messages
- Use **react-i18next** with `useTranslation()` hook for internationalization
- All i18n keys must follow the pattern `ORG$KEY_NAME` for organization-related strings
- The organization object has an `is_personal` boolean field

## Requirements

1. **i18n**: Add translation keys and strings for both messages in all 15 supported languages
2. **Hook**: Modify `useSwitchOrganization` to display the appropriate toast message based on whether the target is personal workspace or a team organization
3. **Component**: Modify `OrgSelector` to pass the organization name and `is_personal` flag when calling `switchOrganization`
4. **Tests**: Add unit tests that verify the toast notification is displayed with the correct message for both cases

## Hint

Look at how other mutation hooks in the codebase use `displaySuccessToast()` and how they structure their `mutationFn` and `onSuccess` callbacks. The hook currently only receives `orgId` - you'll need to extend it to also receive the organization name and whether it's a personal workspace.
