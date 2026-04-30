# Add a `create-pr` Claude Code skill for ant-design

The `ant-design/ant-design` repository ships a small set of Claude Code
skills under `.claude/skills/` (for example `commit-msg/SKILL.md` and
`issue-reply/SKILL.md`). The maintainers want a new skill that helps
Claude draft and open pull requests against this repository in a way
that follows the project's PR conventions, instead of inventing its own
PR structure or copy-pasting the latest commit message.

You are working at the repo root inside `/workspace/ant-design`. There
are no source-code changes — this task is to author two new markdown
files. Do not modify any existing files.

## What you need to create

Two new files (and the directory that holds them):

1. `.claude/skills/create-pr/SKILL.md` — the skill definition itself.
2. `.claude/skills/create-pr/references/template-notes-and-examples.md` —
   a companion reference file with extra notes and examples.

## `SKILL.md` requirements

### Frontmatter

`SKILL.md` must begin with YAML frontmatter delimited by `---`. It
must include at least these two fields:

- `name: antd-create-pr`
- `description:` — a real, descriptive sentence explaining when the
  skill should be used (creating PRs, writing PR titles or bodies,
  summarizing branch changes for a PR, etc.). It must be a meaningful
  sentence, not a one-word stub.

### Content the skill must cover

The body of the skill must teach Claude the following rules. The
exact prose is up to you, but every rule below has to be present in
some form, and the specific path/token literals listed must appear
verbatim:

1. **Use the repository's PR templates by exact path.** The skill
   must reference both:
   - the Chinese template `.github/PULL_REQUEST_TEMPLATE_CN.md`, and
   - the English template `.github/PULL_REQUEST_TEMPLATE.md`.

   The user's language habit decides which one to use. The skill must
   not invent its own PR sections.

2. **PR titles are always English.** Even when the PR body uses the
   Chinese template, the PR title is in English. Make this explicit
   (for example "PR title must be English" or "标题始终使用英文").

3. **Read the full branch diff, not just the last commit.** The skill
   must instruct the agent to inspect the whole delta from the base
   branch to `HEAD`. Include git invocations that reference
   `<base>..HEAD` or `<base>...HEAD` (for example
   `git log <base>..HEAD`, `git diff <base>...HEAD`). It is wrong to
   summarize a PR from only the latest commit or from uncommitted
   working-tree changes.

4. **PR title format and types.** Titles follow Conventional-Commit
   style: `type: subject` or `type(scope): subject`. The skill must
   enumerate the allowed `type` tokens, written **in backticks**. At a
   minimum these tokens must appear in backticks somewhere in
   `SKILL.md`: `` `feat` ``, `` `fix` ``, `` `docs` ``,
   `` `refactor` ``, `` `chore` ``. Other common types
   (`site`, `demo`, `test`, `ci`, `type`) are also appropriate.

5. **Point to the reference file.** Somewhere in `SKILL.md` (for
   example a "References" or "参考" section near the end), include
   the relative path `references/template-notes-and-examples.md` so
   readers know where the extended notes live.

## `references/template-notes-and-examples.md` requirements

This companion file should hold the longer, more example-heavy material
so `SKILL.md` itself stays focused on rules. Cover at minimum:

- Suggested PR-type checklist mappings (which checkbox to tick for a
  bug fix vs. a feature vs. a docs change, etc.).
- How to write `Related Issues` (`close #N`, `fix #N`, or `None`).
- Short "Background and Solution" example bodies (Chinese and English).
- Short "Change Log" example tables.
- Example PR titles that follow the title format.

It must also enumerate at least these PR title types in backticks:
`` `feat` ``, `` `fix` ``, `` `docs` ``, `` `chore` ``.

## Style

- Either Chinese or English prose is acceptable in the skill body.
  The pre-existing skills under `.claude/skills/` (`commit-msg`,
  `issue-reply`) are written in Chinese — matching that style is the
  natural choice if you have no other reason to pick.
- Frontmatter must be valid YAML.
- Do not modify any pre-existing files. The existing
  `.claude/skills/commit-msg/SKILL.md` and
  `.claude/skills/issue-reply/SKILL.md` must remain untouched.
- Do not create any commits — leave the new files as untracked
  working-tree additions. Only the file contents and paths are
  evaluated.
