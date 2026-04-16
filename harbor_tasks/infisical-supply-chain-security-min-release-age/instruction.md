# Supply Chain Security: npm Package Release Age

## Problem

The Infisical monorepo (`backend/` and `frontend/`) currently installs npm packages without any supply-chain protection. A newly published malicious version of a dependency could be immediately resolved and installed by `npm install`, with no delay for the community to detect and report issues.

## Expected Behavior

Both `backend/` and `frontend/` should be configured to refuse resolution of any npm package version that was published fewer than 7 days ago. npm has a built-in feature for this — consult the npm documentation to identify the relevant configuration mechanism and the minimum npm version that supports it.

Since this feature requires a recent npm version, ensure that anyone working in this repository will be alerted if their npm is too old. The minimum npm version that supports this feature is **11.10.0**; the engines field in both `backend/package.json` and `frontend/package.json` must require `npm >= 11.10.0`.

The npm configuration key for this feature is `min-release-age`, and the value to set is `7` (meaning refuse packages published fewer than 7 days ago). This must be configured in both `backend/.npmrc` and `frontend/.npmrc`.

Update the project's CLAUDE.md to document this new policy. Add a section titled **"Dependency Policy"** that describes the 7-day minimum release age enforcement as a supply-chain security measure, noting that both directories enforce this rule.

## Notes

- The project's CLAUDE.md states: "When making significant changes to the codebase [...] update the relevant CLAUDE.md file(s) with high-level findings."
- Preserve all existing CLAUDE.md sections and package.json fields (e.g., scripts, name).
