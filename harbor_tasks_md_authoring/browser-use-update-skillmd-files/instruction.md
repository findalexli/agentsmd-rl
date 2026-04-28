# update SKILL.md files

Source: [browser-use/browser-use#4122](https://github.com/browser-use/browser-use/pull/4122)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/browser-use/SKILL.md`
- `skills/remote-browser/SKILL.md`

## What to add / change

<!-- This is an auto-generated description by cubic. -->
## Summary by cubic
Streamlined and standardized the SKILL docs for browser-use and remote-browser to make them shorter, clearer, and easier for agents to follow. Added a direct README link for deeper reference.

- **Refactors**
  - Replaced lengthy install/setup with a simple Prerequisites section and `browser-use doctor`, and added a README link for detailed docs.
  - Organized content into Essential Commands and concise sections; merged Navigation & Tabs; clarified token‑efficient `task status` flags.
  - Clarified browser modes and profile use: real vs remote, local vs cloud profiles, cookie syncing workflow; noted `--profile` works with `open/session create` but not with `run` (use `--session-id`); vision enabled by default.
  - Added Common Workflows for tunnels (exposing dev servers), authenticated browsing with profiles, and running subagents (parallel/sequential), plus improved troubleshooting on stuck tasks and session reuse after `task stop`.
  - Standardized flags and examples (e.g., `--proxy-country uk`, judge options), trimmed duplicated content, and added explicit cleanup commands for sessions and tunnels.

<sup>Written for commit f9694b6af3b5ceb69e1e450391e374368de2f301. Summary will update on new commits.</sup>

<!-- End of auto-generated description by cubic. -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
