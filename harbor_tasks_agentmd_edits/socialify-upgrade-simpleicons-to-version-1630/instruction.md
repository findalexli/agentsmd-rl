# Upgrade simple-icons and preserve removed icons

## Problem

The `simple-icons` package is outdated at version 15.x. Version 16.3.0 has been released, but it removes several icons that this project depends on — specifically Heroku, OpenAI, and Slack. After upgrading `simple-icons` in `package.json` and running `pnpm install`, the build fails because `siHeroku`, `siOpenai`, and `siSlack` are no longer exported by the package.

## Expected Behavior

After the upgrade to simple-icons 16.3.0:
1. The project builds and lints cleanly (`pnpm verify` passes)
2. Heroku, OpenAI, and Slack icons remain available in the language icon mapping
3. The removed icons are preserved using custom fallback definitions (following the existing pattern in `common/icons/customIcons.ts` where icons like Amazon, AWS, and Java are already handled this way)

## Files to Look At

- `package.json` — bump the `simple-icons` dependency
- `common/icons/customIcons.ts` — existing custom icon fallbacks; add new ones here
- `common/icons/languageMapping.ts` — maps language/tech names to icon objects; update imports for removed icons

After making the code changes, update the project's agent configuration and documentation to reflect the new workflow:
- `AGENTS.md` should be updated to document any new directories or skills added
- Consider adding a skill document under `.github/skills/` that describes the process for upgrading simple-icons in the future, so that the next upgrade follows a consistent workflow

Don't forget to create a changeset file for the version bump.
