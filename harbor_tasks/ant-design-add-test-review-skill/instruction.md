# Add an `antd-test-review` skill

Ant Design's repo hosts a set of agent skill files under `.agents/skills/<skill-name>/SKILL.md`
(siblings include `changelog-collect`, `commit-msg`, `create-pr`, `issue-reply`,
`version-release`). Each file is a self-contained Markdown document with a YAML
frontmatter declaring the skill's `name` and a `description` that the agent
loader uses for keyword matching.

The repo currently has no skill that helps a reviewer decide whether a unit
test in `components/**/__tests__/` is worth keeping. Maintainers regularly see
tests that prove nothing — for instance, a test that re-derives `expected`
from the production helper it is supposed to be guarding (a "用 A 证明 A"
tautology), tests that lock onto irrelevant implementation details such as a
specific CSS class name or the `whiteSpace: 'nowrap'` style, and tests that
duplicate coverage already provided by `mountTest` / `rtlTest`.

Your task is to add a new skill that codifies how to triage these cases.

## Where the file goes

Create exactly one new file at:

```
.agents/skills/test-review/SKILL.md
```

Do not modify any existing file. The directory `.agents/skills/test-review/`
does not yet exist — create it.

## Required frontmatter

The file must begin with a YAML frontmatter block delimited by `---` lines.
The frontmatter must contain:

- `name: antd-test-review` — exactly this skill name (the loader matches on it).
- `description:` — a substantive (≥20 chars) one-line description that:
  - signals an audit / review intent (use the word **审查** or **review**), and
  - explicitly references **测试** (the test cases being reviewed),
  so the skill is discoverable when a user asks to review test quality.

## Required body content

The body (everything after the closing `---`) must be substantive — at least
**1500 characters** of guidance, not a stub. It must include the following
substantive elements (you have freedom over headings, ordering, and wording
beyond the literal terms called out):

1. **Anti-pattern keyword.** The body must reference the **`用 A 证明 A`**
   anti-pattern by name (uppercase `A` or lowercase `a` is acceptable). This is
   the central failure mode the skill exists to catch: a test whose `expected`
   value is computed from the same production code path it is supposed to be
   guarding.

2. **Default to static review.** The body must encode the rule that this skill
   defaults to **静态审查** and does not run tests by default. State this
   explicitly using a phrase such as **不默认运行**, **不主动 [运行/执行]**,
   or **不运行**, alongside the term **静态审查**. The skill should only run
   tests when the user explicitly asks for a red/green check.

3. **Three-verdict vocabulary.** The skill must prescribe a fixed three-way
   classification with these exact verdict labels (each must appear verbatim
   somewhere in the body):
   - `此用例可保留` — the test guards an independent, observable contract.
   - `此用例需要改写` — the intent is plausible but the assertion locks onto
     implementation detail or the evidence is weak.
   - `此用例无实际作用` — `expected` comes from the same source as the
     implementation, the test only checks existence, or it duplicates existing
     coverage.

Beyond these required elements, the body should give the reviewer enough
guidance to reach a verdict — for example: how to identify whether `expected`
comes from an independent source (issue/PR description, component docs/demo,
DOM/ARIA semantics, user-observable text) versus a tautological one (a shared
helper, a copied implementation), what kinds of assertions tend to lock onto
implementation detail (`toHaveStyle`, `toHaveClass`, asserting specific CSS
properties or transient class names), and when a new test is redundant
(coverage already provided by `mountTest` / `rtlTest`, identical props
combinations, only renaming variables). Keep the framing consistent with the
sibling skills already in `.agents/skills/`.

## Out of scope

- Do not add or modify any tests under `components/**/__tests__/`.
- Do not modify any production component code.
- Do not edit `CLAUDE.md`, `AGENTS.md`, the other skills, or any unrelated
  file. The diff for this task should be a single new file.
