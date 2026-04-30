# Add a `CLAUDE.md` for AI assistant context

## Background

You are working in a checkout of [`ant-design/ant-design`](https://github.com/ant-design/ant-design)
(the source for the `antd` React component library).

The project already has a long-form, canonical contributor spec at the repo
root called `AGENTS.md` (read it — it is your source of truth). It covers
project background, code conventions, naming rules, TypeScript rules, demo
rules, the changelog rule set, the PR rule set, and more. It is several
thousand lines long.

Claude Code, however, automatically loads a file named `CLAUDE.md` from the
project root at the start of every session. There is no such file in this
repo yet, which means Claude starts each session blind to the project's
conventions and has to be told them every time.

## Your task

Create a new file `CLAUDE.md` at the **repo root** that gives Claude Code a
concise project-context summary. It should be a *quick reference* — short
enough to be loaded into every Claude session — and should explicitly defer
to `AGENTS.md` for the full specification. It must not be a verbatim copy
of `AGENTS.md`.

The file should be written in **Chinese**, mirroring the existing tone and
style of `AGENTS.md` (which is also primarily Chinese).

### Required content

The summary must cover, at minimum, the following areas. The bracketed
phrases are the exact literals the verifier looks for; surrounding wording
is up to you.

**1. Project context and common commands.** Briefly describe the project
(React component library published as the npm package `antd`, written in
TypeScript, CSS-in-JS architecture, design-token theme system). Then list
the project's day-to-day npm scripts in a fenced code block — at minimum
`npm start`, `npm run build`, `npm test`, `npm run lint`, and
`npm run format`. (These are the same scripts documented in `AGENTS.md`.)

**2. Core coding conventions.** Surface the most important conventions
from `AGENTS.md` so they're loaded into every session. Include at least:
function components with hooks (no class components), use of `forwardRef`,
`clsx`, `displayName`, the Semantic styles system (`classNames` /
`styles`), PascalCase component names, camelCase prop names, and the
panel-open-state rule that prefers `open` over `visible` (both names must
appear so the convention is unambiguous). Also state the project's 100%
test-coverage requirement.

**3. PR rules.** Summarise the most actionable PR rules from `AGENTS.md`:
PR titles must be in English with a `type: short description` format; PR
body content should be in English; the project provides PR templates at
both `.github/PULL_REQUEST_TEMPLATE.md` (English) and
`.github/PULL_REQUEST_TEMPLATE_CN.md` (Chinese) — both paths should appear
in the file. Cover the branch naming convention (e.g. `feat/...`,
`fix/...`, `docs/...`, `refactor/...`) and the PR-type emoji legend.

**4. Changelog rules.** State the changelog file pair: every changelog
update goes into BOTH `CHANGELOG.en-US.md` AND `CHANGELOG.zh-CN.md`. Cover
the entry format rules (emoji-first, no colon after component name,
component name must appear in every entry, single space between Chinese
and English/numbers/links) and include the project's emoji legend.

**5. Pointer back to `AGENTS.md`.** The file should explicitly reference
`AGENTS.md` (by filename, e.g. as a Markdown link) so Claude knows where
to look for the full spec. Mention this both near the top of the file and
near the bottom — the goal is to discourage Claude from treating the
summary as exhaustive.

### What to avoid

- Don't blindly copy `AGENTS.md` into `CLAUDE.md` — the whole point of the
  separate file is to be a *short* per-session preamble.
- Don't add rules that aren't in `AGENTS.md` — this is a summary, not a
  new spec.
- Don't change `AGENTS.md` itself, the changelog files, or any other
  existing file. The PR is purely additive: one new file.

## Verifier

The grader will check that `CLAUDE.md` exists at the repo root and contains
the literals enumerated above. A separate semantic judge will compare the
breadth and faithfulness of your summary against the reference version, so
covering all five areas above is what matters — not exact wording.
