# Add a `suggesting-data-imports` agent skill to PostHog's data warehouse product

This repository teaches AI coding agents how to use PostHog's MCP tools by
shipping markdown "skills" — job-to-be-done templates checked into the
repo and published downstream by CI.

A workflow gap exists: when a user asks an agent about data PostHog
**doesn't** collect natively (revenue, payments, subscriptions, billing,
CRM deals, support tickets, production-database tables, …), the agent has
no skill telling it how to recognise the gap, check existing data
warehouse sources, identify the right source type, and either point at
already-imported tables or hand off to the source-creation flow. Your job
is to add that skill.

## What to add

Create one new file:

```
products/data_warehouse/skills/suggesting-data-imports/SKILL.md
```

It must be a complete, build-passable skill following the rules in
`.agents/skills/writing-skills/SKILL.md` and the established pattern of
the sibling skills under `products/data_warehouse/skills/` (e.g.
`setting-up-a-data-warehouse-source`, `diagnosing-failed-warehouse-syncs`).

Read both before writing.

### Frontmatter

* YAML frontmatter, delimited by `---` lines, on the very first line of
  the file.
* `name: suggesting-data-imports` — exact match with the directory slug,
  lowercase kebab-case, gerund form, no `posthog-` prefix (see meta-skill).
* `description:` — third-person, specific. The description is what the
  routing layer uses to decide whether to load this skill, so it must
  enumerate the trigger domains so an agent can recognise the situation:
  **revenue / payments / subscriptions / billing / CRM deals / support
  tickets / production database tables**, plus the failure mode "a query
  fails because the table does not exist." It should also mention that
  the data warehouse imports from SaaS tools (Stripe, Hubspot, …),
  production databases (Postgres, MySQL, BigQuery, Snowflake), and other
  sources. Keep under the 1024-character limit from the meta-skill.

### Body sections

The body must teach the agent the workflow, not just enumerate tools.
Cover, at a minimum:

1. **What PostHog collects natively vs what must be imported** — make the
   distinction explicit so the agent knows when to suggest an import.
2. **When to use this skill** — list concrete trigger signals (HogQL
   "table not found", user mentions Stripe/Hubspot/their prod DB, etc.).
3. **Workflow**, in this order:
   1. Identify what data is missing.
   2. **Check what's already connected first.** The data may already be
      imported under a prefixed table name the user does not know.
      Reference the relevant `posthog:` prefixed MCP tools the agent
      should call here — at minimum
      `posthog:external-data-sources-list`,
      `posthog:external-data-schemas-list`, and
      `posthog:read-data-warehouse-schema`. (Browse
      `products/data_warehouse/mcp/` if you need to confirm tool names.)
   3. Identify the right source type via
      `posthog:external-data-sources-wizard`, then suggest the import
      and explain what tables become available.
   4. Hand off to the existing **`setting-up-a-data-warehouse-source`**
      skill for the actual creation flow — do **not** duplicate that
      workflow here.
   5. Show what's possible after import (a join example using
      `posthog:execute-sql`).
4. **A markdown lookup table** mapping user needs to source types and
   key tables. It must be a real markdown pipe table with columns for
   *user need*, *source type*, and *key tables*, and must cover at least:
   revenue/payments (Stripe and similar), CRM (Hubspot/Salesforce),
   support (Zendesk), and the user's own production database (Postgres,
   MySQL, BigQuery, Snowflake, etc.).
5. **Important notes / gotchas** — at least: don't guess table names,
   imported tables are usually prefixed (`stripe_charges`, not
   `charges`), OAuth-based sources require the PostHog UI rather than
   MCP, and not every system is supported (suggest Postgres/MySQL as a
   bridge).
6. **Related tools** — bullet list of the `posthog:` prefixed MCP tools
   the workflow references.
7. **Related skills** — link to `setting-up-a-data-warehouse-source`
   for the hand-off.

### Constraints (from `.agents/skills/writing-skills/SKILL.md`)

* `SKILL.md` is the entry point — keep it under 500 lines.
* Tone: describe the workflow and reasoning, not a rigid script.
* Conciseness: the agent is smart, only include context it does not
  already have.
* Do not change any other file. The PR is exactly one new file.

## Code Style Requirements

* Markdown: prefer semantic line breaks; no hard wrapping (per the root
  `AGENTS.md`).
* Use American English spelling.
* Product names use Sentence casing (e.g. *Product analytics*, not
  *Product Analytics*).
* No `posthog-*` prefix on the skill name.
