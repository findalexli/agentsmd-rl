# Add a tracking-issue policy to `AGENTS.md`

You are working in a checkout of [`apache/airflow`](https://github.com/apache/airflow)
at `/workspace/airflow`. Your job is to extend the repository's
top-level `AGENTS.md` (the agent-instruction file) with a new policy
section that closes a concrete process gap described below.

## The problem

Recently, several PRs landed with **forward-looking language** in their
bodies — phrases like "will open a tracking issue" or "to be filed
later" — instead of a concrete, already-opened follow-up issue. After
those PRs merged, the deferred work was easy to forget, and future
readers of the source had no way to discover the linked context: there
was no tracking issue cited *at the workaround site in the code itself*.

The most recent example was the airflow-ctl `0.1.4rc3` release prep,
where PR
[#65607](https://github.com/apache/airflow/pull/65607) capped `httpx`
to `<1.0` with body text saying "will open a tracking issue", and the
follow-up issue
[#65609](https://github.com/apache/airflow/issues/65609) was filed
afterwards and only retro-linked via a PR comment — never embedded at
the cap itself in `pyproject.toml`. That's the failure mode this policy
is meant to prevent.

## What you need to do

Edit **`AGENTS.md`** at the repo root. Add a single new policy section
that codifies the rule that whenever a PR applies a **workaround,
version cap, mitigation, or partial fix** (rather than solving the
underlying problem), the author must:

1. **Open a tracking issue first**, before finalising the PR body — not
   "will open a tracking issue" later.
2. **Reference it in the PR body by issue number**, so reviewers can
   see what was deferred and why.
3. **Add a comment at the workaround site in the source file**
   pointing at the tracking issue, so the reference survives the merge
   and is visible to anyone reading the file later (e.g. when grepping
   in an editor or reading a terminal checkout — places where
   GitHub-only auto-linking does not apply).

The section must additionally:

- Make clear that the in-code comment must use the **full GitHub issue
  URL** (of the form `https://github.com/apache/airflow/issues/<N>`),
  not a bare `#NNNNN` reference, and explain *why* (bare refs don't
  auto-link outside GitHub's web UI).
- Show **at least one concrete example** of the in-code comment style
  using a real-looking workaround (e.g. an `httpx` version cap in
  `pyproject.toml`, a fallback branch in a Python module, etc.) that
  embeds a full `https://github.com/apache/airflow/issues/<N>` URL.
- Explicitly call out the vague phrase **"will open a tracking issue"**
  (and similar forward-looking language) as something authors should
  *not* write in PR bodies or code comments — open the issue first,
  then submit.
- Specify the minimum content of a good tracking issue: what the
  workaround is, why it was chosen, the concrete follow-up work, and
  acceptance criteria for removing the workaround.
- Tell authors who *already* opened a PR with such forward-looking
  language how to remediate: open the issue, add a PR comment
  referencing the URL, and push a follow-up commit that adds the
  tracking-issue URL as a comment at the workaround site.

## Where the section goes

`AGENTS.md` already has a `## Pull Request` flow that ends with a
`Remind the user to:` numbered list (about PR title length, body, and
related issues), followed immediately by `## Boundaries`. The new
policy is a refinement of the PR-creation workflow, so it belongs as a
`###` subsection inside that PR-creation `##` block — *before* the
`## Boundaries` heading, not after it.

Use a section heading that names the concept clearly: this is about
**tracking issues** for **deferred work**.

## Style and tone

Match the surrounding file. `AGENTS.md` uses concise imperative bullets
and numbered lists, bold for emphasis on key terms, and fenced code
blocks (with language tags like `toml`, `python`, `bash`) for examples.
Keep prose tight — this is a reference file, not a tutorial.

Do not modify any other file. The full diff for this task should touch
only `AGENTS.md`.
