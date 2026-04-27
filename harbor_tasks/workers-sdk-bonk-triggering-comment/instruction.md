# Bonk: act on the triggering comment instead of doing a generic review

## Background

The `cloudflare/workers-sdk` repository runs an on-demand agent called
**Bonk** for `/bonk` and `@ask-bonk` mentions in PR/issue comments. The
agent is configured by:

- `.github/workflows/bonk.yml` — the GitHub Actions workflow that wires up
  the comment trigger and invokes the `ask-bonk/ask-bonk/github` action.
- `.opencode/agents/bonk.md` — the agent persona / instruction file Bonk
  reads at runtime. It contains sections like `<non_negotiable_rules>`,
  `<mode_selection>`, `<implementation>`, `<examples>`, and
  `<anti_patterns>`.

## The bug

When a maintainer leaves a comment such as

> /bonk fix the formatting in this PR and commit the result

(after Bonk has *already* reviewed the same PR), Bonk ignores the
specific request, performs a second full PR review, and posts new review
comments rather than making the requested change. The maintainer asked
for a code change and a commit; Bonk delivers another review.

Two cooperating defects produce this:

1. **The workflow never tells the agent what triggered it.** The
   `Run Bonk` step calls the `ask-bonk` action without ever forwarding
   the triggering comment's body, so the agent has no first-class signal
   about *why* it was invoked. (Compare with the auto PR-review
   workflow, which does construct and pass a `prompt`.) The agent ends
   up falling back to whatever generic behavior it defaults to when no
   prompt is supplied.

2. **The agent's instruction file does not prioritize the triggering
   comment.** The implementation-mode workflow currently begins by
   reading the entire issue or PR, and the non-negotiable-rules section
   has no rule that names the triggering comment as the primary task.
   Nothing tells the agent that re-reviewing instead of acting is wrong
   when the request is a fixup.

## What you must change

You need to update both files. Network access (to GitHub/Actions) is not
available during evaluation — your changes are validated against the
file contents directly.

### 1. `.github/workflows/bonk.yml`

Add a step **before** the `Run Bonk` step that assembles a prompt from
the triggering comment, and pass that prompt to the `ask-bonk` action.

Concrete requirements:

- The new step's `name` must be exactly `Build prompt with triggering
  comment`.
- The step's `id` must be `prompt`.
- The step must read the triggering comment body via an env variable
  (i.e. `COMMENT_BODY: ${{ github.event.comment.body }}` under `env:`)
  and reference `$COMMENT_BODY` from the shell — *do not* interpolate
  `${{ github.event.comment.body }}` directly into the run script
  (shell-injection risk).
- The assembled value must be written to `$GITHUB_OUTPUT` so the next
  step can consume it.
- The existing `Run Bonk` step's `with:` block must gain a `prompt:`
  parameter that references the new step's output — i.e.
  `${{ steps.prompt.outputs.value }}`.

The build step must run **before** `Run Bonk` (it produces the value
`Run Bonk` consumes).

### 2. `.opencode/agents/bonk.md`

Make three edits:

**a. Add two new non-negotiable rules** inside the existing
`<non_negotiable_rules>` block. Their bullet labels must read exactly:

- `Triggering comment is the task` — the comment that invoked Bonk is
  the primary instruction. Bonk must read it first, parse what it asks
  for, and gather only the context needed to execute that request,
  rather than falling back to a generic PR review when a specific action
  was requested.
- `No re-reviewing on fixup requests` — if Bonk previously reviewed the
  PR and the maintainer now asks Bonk to fix something, Bonk must act on
  the triggering comment instead of reviewing again.

**b. Restructure the `<implementation>` numbered workflow** so that
**step 1** starts from the triggering comment (parsing what it asks for
and identifying the concrete action requested), and step 2 narrows
context-gathering to what that task requires. The current step 1 ("Read
the full issue or PR first…") is what produces the bug — it must no
longer be step 1.

**c. Update the examples section.** The existing single negative
example must become plural (heading: `Negative examples:`), and at
least one new negative example must capture the observed failure mode:
a fixup request that arrives **after** Bonk previously reviewed the PR
(use phrasing such as "previously reviewed" or "already reviewed"), and
specifically include a trigger of the form
`address the review comments` so the example matches the real-world
failure case.

## What success looks like

After your edits:

- `.github/workflows/bonk.yml` parses as valid YAML; the `bonk` job has
  a `Build prompt with triggering comment` step (id `prompt`) that runs
  before `Run Bonk`; `Run Bonk`'s `with.prompt` references
  `steps.prompt.outputs`.
- `.opencode/agents/bonk.md` contains both new non-negotiable rules
  inside the `<non_negotiable_rules>` block; the implementation
  workflow's step 1 mentions the triggering comment; the examples
  section uses the heading `Negative examples:` (plural) and covers the
  post-review fixup failure mode.

## Out of scope

- You do not need to run, test, or simulate the GitHub Actions workflow.
- You do not need to add a changeset (this PR touches non-published
  workflow + agent-config files only).
- You do not need to touch any other file in the repository.
