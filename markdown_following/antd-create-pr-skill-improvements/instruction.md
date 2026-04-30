# Improve the `create-pr` agent skill

The repository ships an agent skill at
`.claude/skills/create-pr/` that tells AI assistants how to draft and
open pull requests against `ant-design/ant-design`. Maintainers report
several gaps in the current version of the skill that lead to bad PR
behavior in practice. Update the skill so that it covers the
requirements below.

The skill is split across two files; both need updating:

- `.claude/skills/create-pr/SKILL.md`
- `.claude/skills/create-pr/references/template-notes-and-examples.md`

You may freely re-number existing sections, add new sections, and
restructure prose. Keep the file in Chinese (matching the existing
voice). Do **not** delete the YAML frontmatter or change the skill's
`name` field.

## Required behavior changes

### 1. Confirmation step before `gh pr create`

Currently the skill lets the agent jump straight to `gh pr create`. We
want a hard rule: before any `gh pr create` invocation, the agent must
present a draft of the `base`, `title`, and `body` to the user and
wait for explicit confirmation. If the user requests edits to title,
type, changelog, or target branch, the draft must be updated and
re-confirmed.

This rule should appear both:

- as a top-level objective near the start of `SKILL.md` (alongside the
  existing "目标" entries), and
- as a dedicated execution step that comes between "produce the PR
  body draft" and "actually run `gh pr create`".

### 2. Smarter base-branch inference

The current step "确定基线分支" defaults to `master` whenever the
remote default is `master`. This is wrong when the branch was cut
from a feature branch. The new rule must instruct the agent to:

- not blindly default to `master`,
- prefer real Git evidence about where the current branch was checked
  out from. The skill must explicitly recommend `git reflog show` (with
  the current branch name) as the primary source of truth, and
  `git branch -vv` (tracking / upstream) plus `git merge-base` as
  supporting evidence,
- fall back to the remote default branch only when no reliable
  inference is possible,
- annotate the result as an inferred value when the agent isn't sure.

The recommended-commands code block should be updated to include
`git reflog show` against the current branch.

In addition, when the inferred change type is `feat` (new public
capability) and the chosen base is not an obvious `feature/*` branch,
the skill must remind the user (without auto-changing the base) to
double-check whether the work should target a feature branch instead.

The same baseline-inference guidance must also be added as a
standalone section in
`references/template-notes-and-examples.md` (heading `基线分支判断建议`),
including the recommended Git commands and a note that
upstream/tracking is only a hint while reflog is the closest signal.

### 3. PR-type judgement order

`SKILL.md` currently does not give a priority order for choosing the
PR type and tends to pick `fix` whenever logic code is touched. Add a
new step (between "判断模板语言" and "归纳 PR 的核心信息") that
specifies this priority:

1. site / docs / demo first (when the main intent is the site,
   documentation, demos, or theme/preview pages — even if some logic
   code is touched along the way),
2. then ci / chore (workflows, scripts, release processes),
3. then `fix` (only for genuine component bugs / behavior or style
   defects),
4. then `feat` (only for newly exposed public capability),
5. then `refactor` / `test` / `type` / `perf`.

Include short example mappings (e.g. theme-preview button glitch on
the docs site → `site:`, GitHub Actions tweak → `ci:`, real component
bug → `fix(Component): ...`).

The same priority guidance must also be summarized in
`references/template-notes-and-examples.md` (under a new heading such
as `类型判断补充说明`), with the rule that
**`site` / `docs` / `demo` / `ci` should be preferred over `fix`** when
the dominant intent is non-component.

### 4. Change-log placeholder rule

The skill currently tells the agent to "write impact" but has no
guidance for PR types where there is no user-visible impact. Add a
dedicated step that says:

- For `site`, `docs`, `demo`, `ci`, pure tests, or purely-internal
  maintenance, the agent must NOT fabricate a changelog. Instead,
  keep the template's changelog section but use a short placeholder.
- Acceptable placeholder strings include `N/A`,
  `No changelog required`, and `无需更新日志`.
- Real changelog text is reserved for changes that affect component
  consumers, public API, interaction, visuals, or release artifacts.

Update both files:

- `SKILL.md`: add the rule as its own execution step, and update the
  "写法要求 → Change Log" bullets and the top-level "禁止" list to
  reflect the new placeholder policy.
- `references/template-notes-and-examples.md`: split the "Change Log
  写法" section into two sub-sections — one for the
  "needs a real changelog" case (existing example), one for the
  "no changelog required" case with both English and Chinese
  placeholder table examples.

### 5. Confirmation phrasing example in references

Add a new section to `references/template-notes-and-examples.md`
(heading `创建 PR 前确认话术建议`) showing a sample confirmation
message the agent can give the user before `gh pr create`. The
example must include the four lines `Base branch`, `PR title`,
`PR type`, and `Change Log`, and offer the user a choice between
proceeding or first making edits.

### 6. Add `perf` to the supported types list

Both files currently list the allowed PR `type` values
(`feat`, `fix`, `docs`, `refactor`, `type`, `site`, `demo`, `test`,
`ci`, `chore`) but omit `perf`. Add `perf` (performance optimization)
to:

- `SKILL.md`'s "写法要求 → 标题 → 常用 type 参考" list, and
- `references/template-notes-and-examples.md`'s PR-title
  type-prefix bullet list.

Also add at least one `ci:` example title (e.g. about adjusting a
pull-request label workflow) to the references file's English example
section, and at least one `site:` example title in the "更贴近当前
分支时" example block.

## Style notes

- Keep all wording in Simplified Chinese to match the existing skill
  voice (English code keywords, type names, and command names stay in
  English).
- Preserve existing Markdown conventions: headings use `###` /
  `####`, bullet lists use `-`, fenced code blocks use triple
  backticks with a language tag where appropriate.
- Do not delete the YAML frontmatter; do not rename the skill.
- Keep the closing `## 参考` pointer in `SKILL.md` and update its
  one-line summary to reflect the new content (type judgement, base
  inference, confirmation phrasing, more title examples).
