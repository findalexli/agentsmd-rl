# Add an issue-reply skill for ant-design/ant-design

You are working on the [ant-design/ant-design](https://github.com/ant-design/ant-design)
repository (the source code for the `antd` React component library).

The maintainers want a reusable skill file that documents how AI assistants
(specifically Claude) should help triage and reply to incoming GitHub issues
in this repo. Today no such skill file exists, and the assistants give
inconsistent responses.

## What you need to do

Create a new Claude skill at the following path:

```
.claude/skills/issue-reply/SKILL.md
```

The file must follow Claude Code's SKILL.md format: it begins with a YAML
frontmatter block (delimited by `---` lines) containing at least the keys
`name` and `description`, followed by Markdown body content. The
`description` must be substantial enough (≥80 characters) to enumerate
the trigger conditions — when Claude should invoke this skill — including
references to "issue", "antd"/"Ant Design", and "GitHub issue management".

Add a companion reference document at:

```
.claude/skills/issue-reply/references/labels-and-resources.md
```

This file should list the project's commonly used issue labels and link to
relevant FAQ / community resources. The main `SKILL.md` should reference it
by path (`references/labels-and-resources.md`).

Finally, the repo's existing `.gitignore` excludes the entire `.claude/`
directory. You must adjust `.gitignore` so that files under `.claude/skills/`
can be committed (use a `!` negation pattern), while leaving the rest of
`.claude/` ignored so users' private session caches do not leak.

## Required topics in the skill body

The body of `SKILL.md` must give clear guidance on at least the following
topics (write naturally — do not just list keywords):

1. **Language policy** — when replying to an issue, use the same language
   as the *original issue body*, not the language of follow-up comments
   or bot replies. (The skill body must mention "language" / "语言".)

2. **Handling dosubot replies** — when the `@dosu` bot has already
   responded, the maintainer should review the bot's reply for accuracy
   and either confirm it or post a correction. The skill body must
   reference `@dosu` (note: mention the bot as `@dosu`, not `@dosubot`).

3. **Duplicate issues** — when an issue duplicates an earlier one, post
   the literal phrase `Duplicate of #` followed by the original issue
   number, then close. (The exact substring `Duplicate of #` must appear
   in the body, since downstream tooling matches against it.)

4. **The 7-day inactivity rule** — if a maintainer has asked the user
   for more information and the user has not replied in 7 days or more,
   close the issue politely. (The body should mention `7` days or
   `seven` days.)

5. **Bug vs Feature Request classification** — distinguish behavioural
   regressions in existing functionality (Bug) from requests for new
   capabilities (Feature Request). The body must use the phrase
   `Feature Request` (English) or `功能请求` (Chinese) when discussing
   feature requests.

6. **When to close vs leave open**, polite close-templates for the
   common scenarios (resolved, usage question, user inactive), and a
   reminder to use the right language at close time.

The references file should enumerate the project's issue labels (e.g.,
`🐛 Bug`, `💡 Feature Request`, `❓FAQ`, `help wanted`, `good first issue`,
`Inactive`) and link to FAQ / StackOverflow / SegmentFault / changelog
resources.

## Acceptance criteria

When you are done, all of the following must be true:

- `.claude/skills/issue-reply/SKILL.md` exists, starts with a YAML
  frontmatter block (`---` … `---`) containing non-empty `name:` and
  `description:` fields, with `description` covering the trigger
  conditions.
- The `SKILL.md` body covers each topic listed above (verifiable by
  string match: `Duplicate of #`, `dosu`, language/语言, 7/seven,
  Feature Request/功能请求).
- `.claude/skills/issue-reply/references/labels-and-resources.md`
  exists and is non-trivial (≥200 bytes).
- The string `references/labels-and-resources.md` appears somewhere
  in `SKILL.md`.
- `.gitignore` has been edited so that `git check-ignore` no longer
  reports `.claude/skills/issue-reply/SKILL.md` as ignored (use a
  `!` negation pattern that allows `.claude/skills/`).
- The repo's existing `package.json` and `AGENTS.md` are unchanged.
