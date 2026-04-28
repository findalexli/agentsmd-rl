# Remove hardcoded path from add-content skill references

Source: [debs-obrien/debbie.codes#542](https://github.com/debs-obrien/debbie.codes/pull/542)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/add-content/references/environment.md`

## What to add / change

Addresses feedback on #539: the `environment.md` reference file contained hardcoded paths making the skill non-portable across environments.

**Changes**
- Removed `cd /Users/debbieobrien/workspace/debbie.codes &&` from npm install and dev server commands in `.agents/skills/add-content/references/environment.md`
- Commands now execute in current working directory, assuming the agent is already in the repository root

**Before**
```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && cd /Users/debbieobrien/workspace/debbie.codes && npm install 2>&1 | tail -5
```

**After**
```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && npm install 2>&1 | tail -5
```

<!-- START COPILOT CODING AGENT TIPS -->
---

💬 We'd love your input! Share your thoughts on Copilot coding agent in our [2 minute survey](https://gh.io/copilot-coding-agent-survey).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
