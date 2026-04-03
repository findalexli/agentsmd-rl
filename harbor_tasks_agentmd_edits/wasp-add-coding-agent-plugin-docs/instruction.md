# Replace Wasp AI / Mage docs with AI Agent Plugin documentation

## Problem

The Wasp documentation currently has a "Wasp AI" section that documents the deprecated Mage tool — an experimental AI code generator powered by GPT. This section includes two pages (`creating-new-app.md` and `developing-existing-app.md`) and references to `usemage.ai`.

Wasp now has official AI agent plugins (`wasp-agent-plugins`) that work with modern coding agents like Claude Code, Cursor, Codex, Gemini CLI, GitHub Copilot, and others. The documentation needs to be updated to replace the old Mage content with the new agent plugin documentation.

## What needs to change

1. **Create a new docs page** at `web/docs/wasp-ai/coding-agent-plugin.md` documenting the agent plugins — including installation instructions for Claude Code and other agents, features, and setup steps.

2. **Update the sidebar** (`web/sidebars.ts`) to rename the "Wasp AI" category and replace the old page references with the new page.

3. **Update the quick-start guide** (`web/docs/introduction/quick-start.md`) to include a step for installing the agent plugin instead of linking to the old Wasp AI page.

4. **Remove the old Mage documentation pages** that are no longer relevant.

5. **Update the README** to reflect the change from Mage to agent plugins. The project's README.md currently has a "Wasp AI / Mage" section that should be updated to describe the new agent plugins instead.

## Files to Look At

- `web/sidebars.ts` — sidebar configuration for the docs site
- `web/docs/wasp-ai/` — current Wasp AI docs directory
- `web/docs/introduction/quick-start.md` — getting started guide
- `README.md` — project README with Wasp AI / Mage section

## References

- The agent plugins repository is at `wasp-lang/wasp-agent-plugins`
- The new docs page URL should be `wasp.sh/docs/wasp-ai/coding-agent-plugin`
- The plugins support Claude Code, Cursor, Codex, Gemini CLI, Copilot, OpenCode, and more
