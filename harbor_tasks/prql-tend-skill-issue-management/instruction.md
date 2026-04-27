# Add issue-management guidance to the running-tend skill

You are working in a clone of the [PRQL/prql](https://github.com/PRQL/prql)
repository at `/workspace/prql`. The repo uses an agent-instruction file at
`.claude/skills/running-tend/SKILL.md` that gives the bot (`prql-bot`)
PRQL-specific guidance for its automated maintenance ("tend") runs.

## Symptom

`prql-bot` opens housekeeping issues automatically (nightly-test failures,
code-quality reports, upstream/infra bug reports). When the underlying cause
is later resolved — for instance a fix PR merges and the failing CI goes
green — the bot has been leaving the issue open and posting a comment along
the lines of "Leaving open for a maintainer to close". Maintainers have asked
for the bot to close these itself.

Two recent occurrences:

- **Issue PRQL/prql#5802** ("Nightly tests failed", 2026-04-16): fix PRs
  PRQL/prql#5801 and PRQL/prql#5803 merged, main CI went green, and the bot
  still left the issue open. A maintainer pushed back: *"@prql-bot you should
  close these when things pass"* and *"presumably we need to add this to the
  tend skill?"*.
- **Issue PRQL/prql#5809** (2026-04-19): the bot acknowledged the issue was
  already addressed but again deferred closing to a maintainer.

The running-tend SKILL.md currently has no rule covering issue closure, so
the bot has nothing to follow.

## What you need to do

Edit `.claude/skills/running-tend/SKILL.md` to add a new top-level section
**`## Issue management`** that authorises and instructs the bot to close
its own resolved issues.

### Required content of the new section

The section must cover the following points; you choose the wording:

1. **Which issues**: those authored by `prql-bot` — i.e., GitHub issues
   where `author.login == prql-bot`. Include this `author.login == prql-bot`
   condition explicitly so the bot can match issues programmatically.
2. **When to close**: once the underlying cause is resolved — e.g., the fix
   PR has merged, or the upstream problem has been addressed. Mention at
   least one example category of bot-authored issue (e.g., nightly
   "tests failed", code-quality reports, infra/upstream bug reports).
3. **How to close**: by leaving a short comment that cites the resolution.
   Use the phrasing **`Resolved by #NNNN — closing`** (or close to it) as the
   example template, where `#NNNN` references the resolving PR or issue.
4. **What not to do**: do *not* leave the issue open for a maintainer when
   it has actually been resolved.

### Where the section goes

Append the new section to the **end** of
`.claude/skills/running-tend/SKILL.md`, after the existing `## CI structure`
section. Do not modify or remove any of the existing sections (`## PR
conventions`, `## CI structure`).

### Style requirements

Match the existing style of the file:

- Top-level section heading using `##`
- Bullet-list body
- Roughly 80-column line wrapping (see the existing `## PR conventions`
  and `## CI structure` sections as reference)
- File should end with a trailing newline

### Why this skill, not a higher-level one

The parent tend skills (`nightly`, `triage`, `running-in-ci`) deliberately
defer issue-closing authorisation to the adopter repo's overlay, because
different repos have different policies on who may close issues. PRQL is
fine with bot-initiated housekeeping on its own bot-authored issues, so
the authorisation belongs in this repo's `running-tend` overlay — not in
the upstream skills, and not in the repo-root `CLAUDE.md` (which is for
project build/test/error conventions and explicitly says the running-tend
SKILL.md should not duplicate them).

## Out of scope

- Do **not** modify any other files (no code changes, no workflow changes,
  no edits to `CLAUDE.md` or other `SKILL.md` files).
- Do **not** restate generic project conventions (build, test, lint,
  error-handling) — those live in the repo-root `CLAUDE.md` and the
  running-tend SKILL.md explicitly says not to duplicate them.
