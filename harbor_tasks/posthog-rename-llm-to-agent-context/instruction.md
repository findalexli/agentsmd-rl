# Rename "LLM context" → "Agent context" in PR template and policy docs

You are working in the PostHog monorepo (a checkout is at `/workspace/posthog`). The repo's PR template and supporting policy docs currently call the agent-disclosure section "LLM context". That phrasing is an implementation detail that doesn't match the rest of the handbook — internally, the term used everywhere else is **agent**. Worse, the section itself is wrapped in an HTML comment so it only appears in PRs when an agent (or a human) remembers to uncomment it, which agents routinely forget.

## What's broken

In the PR template at `.github/pull_request_template.md`:

- The agent-disclosure section is committed as an HTML-commented block:

  ```
  <!-- ## 🤖 LLM context -->

  <!-- If an LLM agent co-authored or authored this PR, uncomment this section and leave any relevant context about the session, tools used, link to the session, or anything else that may help reviewers. -->
  ```

  Because the heading is commented out, the section is invisible by default. Agents are *told* to uncomment it but often submit PRs with the section missing entirely.

- The "How did you test this code?" section's agent-targeted note is buried in a long sentence and gets ignored:

  ```
  <!-- If you are an agent writing this, do NOT include manual tasks you have NOT completed. ...
  ```

In `AGENTS.md`, the PR-description rule reinforces the broken pattern:

```
Always uncomment and fill the `## LLM context` section for agent-authored PRs.
```

In `AI_POLICY.md`, the "Disclose AI usage" paragraph also says:

```
Our [PR template](.github/pull_request_template.md) includes an LLM context section — please use it (most agents will pick it up automatically).
If an LLM co-authored or authored your PR, say so and leave context about the tools and session.
```

All three files use "LLM" as the noun for the contributor, which is inconsistent with the rest of the handbook (it uses "agent" — see for example the existing skills under `.agents/skills/` and the AGENTS.md filename itself).

## What you need to do

Update **all three files** so the section is renamed to "Agent context", is **always visible** in the PR template (no HTML-comment wrapper around the heading), and the PR template inlines the agent-specific rules so agents actually read them at PR-creation time.

### `.github/pull_request_template.md`

1. The agent-disclosure section must become a real, uncommented heading:
   ```
   ## 🤖 Agent context
   ```
   (keep the robot emoji — humans should remove the whole section for fully human-authored PRs).
2. Below the heading, replace the old "If an LLM agent co-authored…" placeholder with HTML-comment guidance to the *author* explaining:
   - **when** to fill the section (when an agent co-authored or authored the PR; remove for fully human-authored PRs);
   - **what** to put in it (tools/agent used, link to session, key decisions, anything that helps reviewers);
   - the **rules for agent-authored PRs**, inlined directly in the template so agents read them at PR creation:
     - All PRs must be attributable to a human author, even if agent-assisted.
     - Do not add a human `Co-authored-by` just for the sake of attribution — if no human was involved in the changes, own it as agent-authored.
     - Agent-authored PRs always require human review — do not self-merge or auto-approve.
     - Do NOT claim manual testing you haven't done.
3. In the "How did you test this code?" section, tighten the agent guidance into a short, direct comment that says agents must not claim manual testing they haven't done — they should state they're an agent and list only the automated tests they actually ran. Replace the current rambling agent-targeted comment.
4. Remove every reference to "LLM context" from this file.

### `AGENTS.md`

In the `### PR descriptions` subsection, update the rule that currently says
``Always uncomment and fill the `## LLM context` section for agent-authored PRs.``
so it points at the new section name. Since the section is no longer commented out, the rule should be along the lines of
``Always fill the `## 🤖 Agent context` section when creating PRs.``

### `AI_POLICY.md`

In the "**Disclose AI usage.**" paragraph:

- Rename the phrase **"LLM context section"** → **"Agent context section"**.
- Rename **"If an LLM co-authored or authored your PR"** → **"If an agent co-authored or authored your PR"** (and make sure the rest of that sentence still flows).

## Constraints

- Don't reorder, remove, or rename any of the other PR-template sections (`## Problem`, `## Changes`, `## How did you test this code?`, `## Publish to changelog?`, `## Docs update`).
- Don't touch any of the other agent-instruction files (`.agents/skills/**`, `CLAUDE.md`, etc.) — they're out of scope for this PR.
- Use American English spelling.
- Keep all phrasing safe for a public open-source repo (PostHog is public). No references to internal customers, private incidents, or unreleased roadmap.
- Use semantic line breaks in markdown — do not hard-wrap long lines.
- Comments inside the template should explain *why* / *how to fill*, not restate what the section is.

## How this is graded

A pass requires:
- The PR template has an uncommented `## 🤖 Agent context` heading and no remaining `LLM context` mentions.
- The agent-authored-PR rules listed above are visible inline in the template (not behind another HTML-comment-only-when-relevant trick).
- AGENTS.md and AI_POLICY.md no longer say "LLM context"; both point to the new section name.
- All three files keep their existing headings and structure intact.
