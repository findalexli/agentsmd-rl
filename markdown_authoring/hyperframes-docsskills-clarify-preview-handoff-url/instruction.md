# docs(skills): clarify preview handoff URL

Source: [heygen-com/hyperframes#504](https://github.com/heygen-com/hyperframes/pull/504)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/hyperframes-cli/SKILL.md`
- `skills/website-to-hyperframes/SKILL.md`
- `skills/website-to-hyperframes/references/step-7-validate.md`

## What to add / change

## Problem

HyperFrames plugin guidance told agents to run `hyperframes preview`, but it did not make the Studio project URL the required handoff surface. That left room for agents to label `index.html` as the project link, even though the user-facing project is the running Studio route like `http://localhost:<port>/#project/<project-name>`.

## What this fixes

- Updates the `hyperframes-cli` skill preview section to require the Studio project URL in handoffs.
- Updates `website-to-hyperframes` Step 7 to say the final response must include the active localhost Studio URL.
- Adds explicit guidance that `index.html` is source-code context only, not the project or preview link.

## Root cause

The plugin registers `./skills/` through `.codex-plugin/plugin.json`, and the relevant skill docs had preview instructions but no final-delivery contract for the URL shape. The missing contract caused ambiguous handoffs.

## Verification

### Local checks

- `git diff --check`
- `node -e "JSON.parse(require('fs').readFileSync('.codex-plugin/plugin.json','utf8')); console.log('plugin.json ok')"`
- `rg -n 'localhost:<port>|#project/<project-name>|final response includes the active Studio project URL|source \`index.html\` path' skills/website-to-hyperframes/SKILL.md skills/website-to-hyperframes/references/step-7-validate.md skills/hyperframes-cli/SKILL.md`
- commit hook: `format` and `commitlint` passed

### Browser verification

- Reopened the prior HyperFrames project at `http://localhost

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
