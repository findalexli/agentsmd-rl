# Add a Claude skill for collecting changelog entries

You are working in the [ant-design/ant-design](https://github.com/ant-design/ant-design)
repository. The repository already publishes guidance for AI assistants under
`AGENTS.md`, plus three Claude Code skills under `.claude/skills/` (named
`commit-msg`, `create-pr`, `issue-reply`).

The maintainers want a **fourth** skill that documents how to collect a
changelog between two ant-design refs (a release tag and the destination
branch) and turn it into entries appended to `CHANGELOG.zh-CN.md` and
`CHANGELOG.en-US.md`.

Create the new skill, then make small clarifying edits to `AGENTS.md`.

## What to add

### 1. New skill file

Create `.claude/skills/changelog-collect/SKILL.md` (a brand-new file — the
directory does not yet exist). It must be written in the same Chinese-first
style as the existing skills under `.claude/skills/` and must document a
multi-phase workflow that an AI assistant can follow end-to-end.

The workflow the skill describes must, at minimum, cover the following:

1. **Discover the diff range**: list available release tags (e.g.
   `git tag --list`), filter out experimental / alpha / resource tags, and
   ask the user to pick a starting tag and a target branch (e.g.
   `master`, `feature`).
2. **Determine the new version number** *before* collecting commits, and
   write it into the header of the temporary changelog file (so that file
   is always usable even if the run is interrupted).
3. **Enumerate commits** in the chosen range with `git log <from>..<to>`,
   parse each line, and extract the PR number from the commit subject.
4. **Fetch every PR's details** via `gh pr view <pr-number> --json title,body,author`
   and, for each PR, **append** an entry to a temporary working file
   (`~changelog.md`) — appending after each PR is fetched, not at the end —
   so the file is always up-to-date.
5. **Extract Chinese and English descriptions** from each PR's body
   (handling both the `🇺🇸 English` / `🇨🇳 Chinese` and `English:` /
   `Chinese:` patterns) and fall back to the PR title when those sections
   are missing.
6. **Tag each entry with a component category** by matching component
   names (case-insensitive substring match) against a fixed list of antd
   component names.
7. **Process the temporary file** according to the rules already
   documented in `AGENTS.md` — filter out user-invisible commits, group
   entries with multiple changes per component, normalize the
   Emoji-prefixed Chinese and English sentence forms, and confirm with the
   user before continuing.
8. **Write into both `CHANGELOG.zh-CN.md` and `CHANGELOG.en-US.md`** by
   inserting the new section after the leading `---` front matter and
   before the first existing version heading. Both files must be updated
   in the same run, and the wording must stay synchronized between
   languages.
9. **Optionally bump `package.json`** with `npm version minor` /
   `npm version patch` after a confirmation prompt.
10. **Clean up** the temporary file once the real changelogs have been
    written.

The skill should also list the shell commands it expects to be available
(at minimum: `git tag --list`, `git log`, `gh pr view`, `git show`,
`npm version`) and call out that `gh` requires authentication
(`gh auth login`).

The exact wording is yours to write — the skill must be coherent,
self-contained, and consistent with the conventions in `AGENTS.md` and the
three existing skills.

### 2. Clarifications to `AGENTS.md`

In the `Changelog 规范` → `格式与结构规范` subsection, two existing rules
need a tiny clarification:

- The rule that says component names are **not** wrapped in backticks,
  but attribute names / API names / tokens **are**, currently has no
  concrete examples of *which* tokens stay backticked. Append two short,
  concrete examples to that rule — use `picture-card` and `defaultValue`
  (one is a string-valued attribute, the other a prop name) so
  contributors do not have to guess what kind of token stays backticked.
- The rule that gives the English sentence template currently shows
  exactly one example. The same line should also show that the
  *component name* should appear early in the English description, with
  one concrete positive example (good ordering — component first) and
  one negative example (bad ordering — component buried after a verb +
  generic noun) so the rule is unambiguous. The existing positive
  example for the Button case may stay; the new examples should be
  added inline on the same bullet so the rule stays a single coherent
  sentence.

Do **not** introduce new top-level sections in `AGENTS.md`. Only the two
specific bullet lines need to grow; surrounding structure must remain
identical.

## What you must NOT do

- Do not delete or rename the three existing skills (`commit-msg`,
  `create-pr`, `issue-reply`). They remain in place.
- Do not modify any source code, package manifests, lockfiles, demos, or
  CI configuration. The change is purely Markdown / agent-instruction.
- Do not modify `CLAUDE.md`, `.github/copilot-instructions.md`, or any
  CHANGELOG file directly.

## Repository layout reminders

- `AGENTS.md` lives at the repository root and already contains a
  `Changelog 规范` section you should align the new skill with.
- The three existing skills under `.claude/skills/*/SKILL.md` are good
  references for tone and structure, but the new skill does **not** need
  YAML frontmatter — pick whichever style is most consistent with what
  you write.
- The two release-changelog files are `CHANGELOG.zh-CN.md` and
  `CHANGELOG.en-US.md` at the repository root.

## Working directory

The repository is checked out at `/workspace/ant-design` at the base
commit `777b4affe8c0d6075ba418ecf6013b510b57d4e4`. Read the surrounding
files before editing — the skill's wording should feel like it was
written by the same author as the existing three skills.
