# Update the issue-reply skill

You are working in a checkout of the `ant-design/ant-design` repository.

The repository ships a Claude skill that guides maintainers when they reply
to GitHub issues. The skill lives at:

```
.claude/skills/issue-reply/SKILL.md
```

Two parts of this skill need to be updated. Make these edits **in place**
in that file. Do not move or rename the file, do not modify any other files,
and do not change the YAML frontmatter at the top of the file (the `name`
and `description` keys).

## Change 1 — Version-check guidance for Bug reports

Under the heading that opens the **Bug 报告** ("Bug report") section, the
skill currently lists how to act on a version check before triaging. The
existing list contains exactly one bullet:

```
- 老版本 + changelog 中已修复 → 引导用户升级验证
```

This list does not currently cover the case where a fix has already been
**merged** in the repository but the project has **not yet published a new
version that contains the fix**. In that situation the maintainer should not
tell the user "it's already fixed" (because the published release does not
yet contain the fix); the maintainer should instead tell the user to wait
for the next release.

Add the following bullet — verbatim, in Chinese, in this exact form — to
that same version-check list, immediately after the existing bullet so
that the two bullets sit together as a coherent sub-list:

```
- PR 已合并但新版本未发布 → 告知用户等待新版本发布
```

## Change 2 — Simplify the polite-closing block

Inside the section about closing issues (the section whose heading is
about closing issues with care), the skill today contains a sub-block
that:

1. starts with the bold lead-in **关闭时保持礼貌：** ("be polite when
   closing"),
2. then walks through three different example reply templates wrapped in
   triple-backtick fenced code blocks: one English example for
   "issue resolved", one Chinese example for "usage question", and one
   Chinese example for "user has not replied for a long time".

The maintainers no longer want the skill to prescribe exact reply text in
the closing section — the desired behaviour is that the maintainer simply
acts politely and briefly states the reason for closing, without copy-and-
pasting a fixed script.

Replace that entire sub-block (the bold heading **and** all three fenced
code-block examples and the short label lines that introduce them) with
this single line — verbatim, in Chinese, with the bold markers:

```
**关闭时保持礼貌，简要说明关闭原因即可。**
```

Nothing else in that section should change. In particular:

- The bullet list of conditions under **可关闭：** that immediately
  precedes this block must remain intact and unchanged.
- The **不要关闭：** ("do not close") sub-block that immediately follows
  this area must remain intact and unchanged.
- All section headings must remain intact and unchanged.

## Out of scope

- Do not edit any file other than `.claude/skills/issue-reply/SKILL.md`.
- Do not change the YAML frontmatter at the top of the file.
- Do not restructure unrelated sections (language policy, dosubot
  handling, FAQ guidance, Bug-vs-Feature classification, "do not close",
  "no promises", "tone and style", etc.).
- Do not edit the English-language Copilot instructions or `AGENTS.md`.

## Style notes

- Both new lines are Chinese; preserve the single ASCII space between
  Chinese characters and any adjacent English / digits / arrows that
  matches the rest of the file's style.
- Do not introduce trailing whitespace.
- Use the exact bold markers (`**…**`) shown above in Change 2 — that
  bold form is part of the file's existing typographic convention for
  inline emphasis lines.
