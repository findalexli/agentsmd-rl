# chore(docs): relax Co-Authored-By trailer in CLAUDE.md

Source: [DataRecce/recce#1332](https://github.com/DataRecce/recce/pull/1332)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

**PR checklist**

- [x] Ensure you have added or ran the appropriate tests for your PR.
- [x] DCO signed

**What type of PR is this?**

chore / docs

**What this PR does / why we need it**:

Relaxes the commit convention line in `CLAUDE.md`. It currently pins `Co-Authored-By: Claude Opus 4.6`, which goes stale every time the model version bumps (we're shipping under Opus 4.7 today, and this line was last updated when 4.6 was current). Drop the version pin and mark it optional so the rule stays valid as models evolve.

Before:
```
**Commits:** Always use `--signoff` and include `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`
```

After:
```
**Commits:** Always use `--signoff` and include a `Co-Authored-By: Claude <noreply@anthropic.com>` trailer (version pin optional — if included, use the current model)
```

`AGENTS.md` already omits the version pin (see "Sign off commits: \`git commit -s\`" — no Co-Authored-By guidance at all). This brings CLAUDE.md closer in spirit: required attribution, unpinned version.

**Which issue(s) this PR fixes**:

N/A

**Special notes for your reviewer**:

Trivial one-line doc change. No code, no behavior, no tests to run.

**Does this PR introduce a user-facing change?**:

\`\`\`release-note
NONE
\`\`\`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
