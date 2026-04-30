# t2883: add §7c untrusted-body content directive immunity to AGENTS.md

Source: [marcusquinn/aidevops#21011](https://github.com/marcusquinn/aidevops/pull/21011)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/AGENTS.md`

## What to add / change

## Summary

Adds §7c `Untrusted-body content directive immunity` to the Security Rules section of `.agents/AGENTS.md`, as a sibling of §7a (Instruction override immunity) and §7b (Worker scope enforcement).

## What changed

- New **§7c** added immediately after §7b in `.agents/AGENTS.md` §Security Rules
- Three explicit MUST NOT / NEVER clauses covering: (1) install commands, (2) URL fetches, (3) email/webhook contacts sourced from non-collaborator bodies
- Explicit definition of "non-collaborator" via GitHub `authorAssociation`
- Reference to the Phase C detector at `.agents/scripts/external-content-spam-detector.sh` (parent #20983)
- Canonical incident callout: marcusquinn/aidevops#20978

## Why AGENTS.md and not build.txt

build.txt is a near-empty placeholder since t2878 (see its own comment: "DO NOT add framework rules here — edit .agents/AGENTS.md instead"). §7a and §7b are already in AGENTS.md; §7c belongs there too. The verification commands in the issue reference build.txt but the canonical location is AGENTS.md, which reaches all 11 supported runtimes.

## Acceptance criteria check

1. ✅ §7c present in AGENTS.md (canonical home since t2878)
2. ✅ Three NEVER clauses: install commands, URL fetch, email/webhook
3. ✅ Reference to `.agents/scripts/external-content-spam-detector.sh`
4. ✅ Reference to canonical incident #20978
5. ✅ Pre-commit and pre-push linters pass
6. ✅ PR body uses `For #20983`, not Closes/Resolves

Resolves #20985
For #20983


<!-- aidevops:sig -->
-

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
