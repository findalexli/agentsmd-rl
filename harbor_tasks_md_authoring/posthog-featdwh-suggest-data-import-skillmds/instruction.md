# feat(dwh): suggest data import SKILL.md's

Source: [PostHog/posthog#55950](https://github.com/PostHog/posthog/pull/55950)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `products/data_warehouse/skills/suggesting-data-imports/SKILL.md`

## What to add / change

## Problem

Agents using the data warehouse MCP tools didn't have guidance on how to approach common workflows — setting up a new source, debugging sync failures, or recognizing when missing data could be resolved with an import. The tools existed but agents didn't know the right order, what to check, or common pitfalls.

```
❯ can you give my highest mrr customers?                                                                                             

⏺ MRR data comes from a payment processor (typically Stripe), not from PostHog's native event collection. Let me check if you already
   have a relevant data source connected.

  Called posthog-local (ctrl+o to expand)

⏺ You don't have any source connected that contains MRR or subscription data. Your current sources are MySQL, Snowflake, BigQuery,
  MSSQL, Supabase, and none of them have billing/revenue tables.

  To get MRR data, you'd need to connect a source that has subscription/payment information — most commonly Stripe. PostHog has a
  native Stripe integration that imports tables like charges, customers, invoices, subscriptions, and products.

  If your billing data lives somewhere else (e.g., a table in one of your existing databases), you could sync that table instead.
  Where does your subscription/billing data live?
```

## Changes

Add three data warehouse skills:

- **`setting-up-data-warehouse-source`** — Guides through the full source setup flow: wizard → db-schema → create. Covers credential collection, t

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
