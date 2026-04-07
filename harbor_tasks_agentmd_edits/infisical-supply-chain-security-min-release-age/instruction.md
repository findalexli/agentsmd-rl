# Supply Chain Security: npm Minimum Release Age

## Problem

The Infisical monorepo (`backend/` and `frontend/`) currently installs npm packages without any supply-chain protection. A newly published malicious version of a dependency could be immediately resolved and installed by `npm install`, with no delay for the community to detect and report issues.

## Expected Behavior

Both `backend/` and `frontend/` should enforce a **minimum release age of 7 days** for npm packages. This means `npm install` should only resolve package versions that were published at least 7 days ago. The required npm version should be pinned via `engines` in each `package.json` to ensure the feature is supported.

## Files to Look At

- `backend/package.json` and `frontend/package.json` — add the npm engine requirement
- `backend/.npmrc` and `frontend/.npmrc` — configure the min-release-age setting (these files may not exist yet)
- `CLAUDE.md` — update to document this new dependency policy as a supply-chain security measure

The project's CLAUDE.md states: "When making significant changes to the codebase [...] update the relevant CLAUDE.md file(s) with high-level findings." Make sure the root CLAUDE.md is updated to reflect this new policy.
