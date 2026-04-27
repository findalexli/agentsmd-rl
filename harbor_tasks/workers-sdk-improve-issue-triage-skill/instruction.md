# Improve the Issue Triage Skill

The repository has an agent skill at `.github/skills/issue-review.md` that
triages GitHub issues for `cloudflare/workers-sdk`. In its current form the
skill is too coarse: maintainers told us it leads to inconsistent
recommendations because the playbook only distinguishes "empty / invalid"
from "needs more info", and gives the agent no guidance about the many real
reasons issues get closed in this repo. The closure-reason field on GitHub
(`state_reason`) is also never mentioned, so the agent's recommendations
don't tell maintainers whether a close should be `completed` or
`not_planned`.

Your job is to expand and reorganize this skill so it covers the full set of
closure categories the team uses, calls out which `state_reason` applies to
each, separates closure-triage from "needs more info", and provides
ready-to-use comment templates.

## What needs to change

All edits live in **one file**: `.github/skills/issue-review.md`. Do not edit
any other file.

### 1. Step 1: extend the "extract and note" checklist

The Step 1 bullet list (which fields to extract from `context.json`) should
also tell the agent to capture:

- the issue's **labels** that are currently applied,
- the **issue age** (created date) and **last activity date**, and
- the **`state_reason`** if the issue is already closed.

### 2. Step 2: replace the narrow check with a broader **Check for Closeable Issues**

Replace the current `### Step 2: Check for Empty or Invalid Issues` step with
a step titled exactly `### Step 2: Check for Closeable Issues`.

This step must instruct the agent to walk through closure categories **in
order** and **stop at the first match**. Add a brief note up front
explaining that the `state_reason` values mentioned (`completed`,
`not_planned`) are informational — they tell the maintainer which GitHub
close reason to use, but they are not stored as a separate field in the
output report.

Then add the following sub-categories as `####` sub-headings, in this
order. For each one, state which recommendation applies (`CLOSE` with the
right `state_reason`, or `KEEP OPEN`), the trigger conditions, and (where a
maintainer comment is appropriate) one or more **`> `-quoted comment
templates** the agent can copy. Keep the sub-headings labelled with the
letters `2a`–`2k`.

| # | Heading                                | Recommendation                       |
|---|----------------------------------------|--------------------------------------|
| 2a | Spam or Junk                          | `CLOSE` (`not_planned`, no comment)  |
| 2b | Reporter Confirmed Resolved           | `CLOSE` (`completed`)                |
| 2c | Already Fixed in a Prior Release      | `CLOSE` (`completed`)                |
| 2d | Duplicate                             | `CLOSE` (`not_planned`)              |
| 2e | Not workers-sdk / Wrong Repo          | `CLOSE` (`not_planned`)              |
| 2f | Stale / No Response                   | `CLOSE` (`not_planned`)              |
| 2g | Transient Platform Issue              | `CLOSE` (`completed`)                |
| 2h | User Error / Misunderstanding         | `CLOSE` (`not_planned`)              |
| 2i | Breaking Change                       | **`KEEP OPEN`** — do not close       |
| 2j | Won't Fix / By Design                 | `CLOSE` (`not_planned`)              |
| 2k | Feature Superseded / Deprecated       | `CLOSE` (`completed`)                |

Notes for specific categories:

- **Spam or Junk** trigger conditions should call out random/nonsense
  bodies, advertising/SEO spam, and template-only / blank "test" issues.
- **Already Fixed in a Prior Release**: when a comment or linked PR shows
  the bug was already fixed, close as `completed` and cite the PR/release.
  Provide a template that fills in `PR #XXXX` and the wrangler version, and
  a fallback template for older issues where the specific fix can't be
  pinpointed.
- **Not workers-sdk / Wrong Repo** must distinguish (a) Workers **runtime**
  behaviour that belongs in [`cloudflare/workerd`](https://github.com/cloudflare/workerd),
  (b) third-party framework bugs (Nuxt, SvelteKit, Remix, Hono, React
  Router), (c) upstream-tool bugs (esbuild, Bun, Vite core), and (d)
  Cloudflare account/billing/abuse problems that belong in Cloudflare
  Support. Provide a different comment template for each. For runtime
  issues, the action field should ask a maintainer to **transfer** the
  issue to `cloudflare/workerd`.
- **Stale / No Response** should trigger when an issue with `awaiting
  reporter response` or `needs reproduction` has had no activity for >30
  days, or when an issue is >12 months old with no activity in the last 6
  months.
- **Breaking Change** is the only **`KEEP OPEN`** category in this section.
  Recommend the `breaking change` label, and have the action field tell the
  maintainer to apply the label and post the comment.
- **User Error / Misunderstanding**: the comment template should explain
  the correct behaviour, link the docs, and offer help on the Cloudflare
  Discord — never be dismissive.

### 3. Renumber and split the rest of the steps

After the closeable-issue triage above, add a **`### Step 3: Check for
Insufficient Information`** step that captures the existing "needs more
info" rules (no reproduction, missing version, vague description) and adds:

- *missing or truncated error message* as another trigger,
- a `> `-quoted comment template asking specific questions plus a request
  for a minimal reproduction repo, and
- a note that the appropriate label is `awaiting reporter response`
  (optionally also `needs reproduction`).

End this step with the same "STOP HERE if … skip to Output" instruction.

Renumber the existing **Identify Component** step to `### Step 4` and
**Assess Reproducibility and Severity** to `### Step 5`.

### 4. Expand the component-mapping table

In the renumbered Step 4 component-mapping table, add rows that cover the
package categories the original table missed. The new table must include
rows whose Signal column references the literal substrings:

- `Workers + Assets`
- `containers`
- `workflows`
- `kv-asset-handler`

(plus `workers-builds`, `python` Workers, `workers for platforms`, `types`
for `wrangler types`, and `node compat` / `nodejs compat`). Make the
existing rows more specific where helpful — e.g. mention `wrangler.json`
alongside `wrangler.toml`, and `_routes.json` / `_headers` for Pages.

Also make the existing "Workers runtime" row point at
`cloudflare/workerd` (rather than the previous "may be a platform issue").

### 5. Step 5 evaluation criteria

In the renumbered Step 5, add to the bug-report bullet list a check for
**Version gap** ("Is the reporter on an old version? Could updating fix
this?"), and to the feature-request bullet list a check for **Existing
alternatives** ("Is there already a way to achieve this, even if less
convenient?").

### 6. Output template tweaks

In the report Markdown template:

- The **Analysis** placeholder should mention staleness indicators and
  duplicate candidates as things to comment on (in addition to component,
  reproducibility, and severity).
- The **Suggested Labels** placeholder should remind the agent to use
  existing repo labels only.
- The **Suggested Comment** placeholder must list these key principles
  (rendered as nested bullet points inside the `> `-quoted block):
  always offer an escape hatch (*"feel free to open a new issue"*); link to
  specific PRs, releases, or docs when available; be concise for
  straightforward closures, more detailed for design decisions; never be
  dismissive or snarky, even for spam (close silently) or user error; for
  NEEDS MORE INFO, ask **specific** questions instead of generic ones; and
  omit the section entirely for spam closes or when no comment is needed.

In the summary-line spec, change the seventh-column legend so that
`Suggested Comment` is `Yes` if a template is provided and `No` otherwise
(drop `N/A`).

## Things to leave alone

- Frontmatter (`name: github-issue-review`, the description) must remain
  unchanged.
- The `# GitHub Issue Triage Skill` H1 heading must remain.
- The "runs without bash or network access" note and the
  `data/<issue_number>/context.json` input description must remain.
- The summary-line tab-separated format must still use real tab characters.

## How this is graded

Two tracks:

1. **Structural check.** A small pytest battery greps the rewritten file
   for the new headings, the `state_reason` terminology, the
   breaking-change `KEEP OPEN` recommendation, the `Insufficient
   Information` step, and the new component-table rows listed above. The
   file should also grow substantially (it is roughly doubling in size).

2. **Semantic comparison.** The rewritten file is diffed against the gold
   reference; the closer your structure, ordering, terminology, and
   comment-template tone match the team's playbook, the higher the score.
