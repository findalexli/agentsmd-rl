# Add `welcomeEmailsDesignCustomization` private feature flag

## Problem

Ghost needs a new private feature flag called `welcomeEmailsDesignCustomization` to gate the upcoming welcome email design customization feature. The flag does not exist yet — it needs to be registered on the backend and exposed in the Labs settings UI so developers can toggle it.

## What needs to happen

1. Register the flag in the backend so Ghost recognizes it as a valid private feature flag.
2. Add a corresponding toggle in the Admin settings UI under the private features section, with an appropriate title and description.
3. The flag name must be consistent across the backend and frontend.

After making the code changes, create a reusable skill document (`.claude/skills/add-private-feature-flag/SKILL.md`) that describes the general process for adding a private feature flag to Ghost. This repo already has skill files for other common tasks (see `.claude/skills/`), and adding private feature flags is a recurring task that should be documented the same way.

## Files to look at

- `ghost/core/core/shared/labs.js` — where feature flags are registered
- `apps/admin-x-settings/src/components/settings/advanced/labs/private-features.tsx` — UI toggles for private features
- `.claude/skills/` — existing skill files to follow as examples
