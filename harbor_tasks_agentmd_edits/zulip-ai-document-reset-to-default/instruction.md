# Document "Reset settings for users" feature

## Problem

Zulip has a feature that allows organization administrators to reset user preference and notification settings back to the organization default. However, there is no help center documentation for this feature, and the existing "Configure default settings for new users" page doesn't mention it.

Additionally, the `configure-default-new-user-settings.mdx` page has an inline list of resettable settings (preferences and notifications) that is duplicated — both this page and the new reset page need the same list. This should be extracted into a shared include file.

## What needs to happen

1. **Create a new help center page** at `starlight_help/src/content/docs/reset-settings-for-users.mdx` documenting the reset feature. The page should explain:
   - That admins can reset preference and notification settings to organization defaults
   - The two reset scopes (all users vs. only those who haven't customized)
   - That privacy settings cannot be reset
   - Step-by-step instructions for using the feature

2. **Extract the settings list** (preferences + notifications) from `configure-default-new-user-settings.mdx` into a shared include file `starlight_help/src/content/include/_DefaultUserSettingsList.mdx`, and use it from both pages.

3. **Update the existing page** (`configure-default-new-user-settings.mdx`) to mention the reset feature and link to the new page. Use the shared include instead of the inline list.

4. **Add a sidebar entry** for the new page in `starlight_help/astro.config.mjs`.

5. **Add cross-links** to the new page from related help center articles (manage-a-user, configure-home-view, customize-settings-for-new-users, manage-user-channel-subscriptions).

6. **Update `.claude/CLAUDE.md`** to document any new components or conventions used in this work. In particular, if you use components like `FlattenedList` that aren't yet documented in the help center section of CLAUDE.md, add documentation for them. Also update any help center writing guidance that should be refined based on this work.

## Files to look at

- `starlight_help/src/content/docs/configure-default-new-user-settings.mdx` — existing page to refactor
- `starlight_help/astro.config.mjs` — sidebar configuration
- `.claude/CLAUDE.md` — agent configuration with help center writing guide
- `docs/documentation/helpcenter.md` — full help center writing guide
- `starlight_help/src/content/include/` — where shared include files live
