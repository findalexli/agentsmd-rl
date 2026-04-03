# Add Agent Skills documentation and navigation entry

## Problem

The Angular project has recently added official Agent Skills — specialized instructions for AI agents (like `angular-developer` and `angular-new-app`) — but the documentation site doesn't mention them anywhere. Users have no way to discover these skills through the Angular docs.

The "Build with AI" section of the docs site needs a new "Agent Skills" page that explains what these skills are, lists the available ones, and shows how to use them with agentic coding tools.

## What Needs to Happen

1. **Add a new documentation page** at `adev/src/content/ai/agent-skills.md` that describes the Agent Skills concept, lists the available skills (`angular-developer`, `angular-new-app`), and explains how to use them.

2. **Update the site navigation** in `adev/src/app/routing/navigation-entries/index.ts` to add an "Agent Skills" entry in the "Build with AI" section. It should appear before the "Design Patterns" entry, and be marked as new content.

3. **Update the AI overview page** (`adev/src/content/ai/overview.md`) to include a link to the new agent-skills page in the "Next steps" section.

4. **Add a README** to `skills/dev-skills/` that documents the available Angular skills and how to contribute to them.

## Files to Look At

- `adev/src/app/routing/navigation-entries/index.ts` — navigation config for the docs site
- `adev/src/content/ai/overview.md` — the AI overview page with links to related guides
- `adev/src/content/ai/` — existing AI documentation pages (for style reference)
- `skills/dev-skills/` — the skills directory that needs a README
