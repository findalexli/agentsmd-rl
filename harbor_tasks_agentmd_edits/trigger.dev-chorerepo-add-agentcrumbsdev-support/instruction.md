# Add agentcrumbs debug tracing support

## Problem

The team wants to adopt [agentcrumbs](https://agentcrumbs.dev) for debug tracing across the monorepo. Currently there is no way for developers to leave temporary debug breadcrumbs (`// @crumbs` markers) in the code during development that get automatically stripped before merge.

The `agentcrumbs` package needs to be integrated into the project so developers can use it during local development and the webapp can bundle it for server-side use.

## What needs to happen

1. **Install the dependency**: Add `agentcrumbs` (version `^0.5.0`) as a root-level dependency so it's available across the monorepo.

2. **Configure the webapp bundler**: The Remix app at `apps/webapp/` uses `remix.config.js` to specify which packages should be server-bundled. `agentcrumbs` needs to be included in that list.

3. **Exclude from release age checks**: The `pnpm-workspace.yaml` has a `minimumReleaseAgeExclude` list for packages that should skip the minimum release age policy. `agentcrumbs` should be added there.

4. **Update CLAUDE.md**: After making the code changes, update the project's `CLAUDE.md` to document how to use agentcrumbs. This should include:
   - Skill mappings that point to the agentcrumbs skill files (in `node_modules/agentcrumbs/skills/`)
   - A section explaining the `@crumbs` marker syntax and that crumbs are stripped before merge
   - A namespace catalog mapping project areas to agentcrumbs namespaces (use existing package names from the repo structure — don't invent new ones)
   - CLI commands for collecting, tailing, and clearing crumbs
   - A note for PR reviewers that `@crumbs` markers are temporary and should not be flagged

## Files to Look At

- `package.json` — root monorepo package, where the dependency should be added
- `apps/webapp/remix.config.js` — Remix server bundle configuration
- `pnpm-workspace.yaml` — workspace configuration with release age exclusions
- `CLAUDE.md` — agent instruction file that needs documentation updates
