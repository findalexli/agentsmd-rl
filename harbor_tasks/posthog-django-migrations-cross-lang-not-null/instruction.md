# Task: document the cross-language `NOT NULL` hazard in the django-migrations skill

You are working in the PostHog monorepo at `/workspace/posthog`.

## Background

PostHog uses an in-repo agent skill at `.agents/skills/django-migrations/SKILL.md` to teach coding agents how to safely write Django migrations against the Postgres `posthog_*` schema.

In the current Workflow, step 1 ("Classify") only asks the author to decide whether a change is **additive** (e.g. a new nullable column) or **risky** (`NOT NULL`, drops, renames, indexes, constraints, large data updates, model moves). That classification misses a real hazard that the skill currently does **not** warn about.

## The hazard

When a Django model declares a non-null field with a Python-side default — e.g. `JSONField(default=list)`, `JSONField(default=dict)`, or `models.<X>Field(default=<callable>)` — Django's `default=` is applied **only in Python**, by the ORM, before the row is sent to Postgres. The generated migration sets the column `NOT NULL` but does **not** add a Postgres-level column `DEFAULT`. From Postgres's point of view, the column is `NOT NULL` with no default.

Most of the time this is fine, because all writes go through the Django ORM. But several PostHog tables are also written by **non-Django** code:

- the plugin-server in `nodejs/` (which writes via raw SQL fixtures and runtime inserts),
- Rust services in `rust/`,
- Temporal workers,
- ad-hoc scripts under `products/` and `services/`.

Any non-Django writer that issues a raw `INSERT` and omits the new column will fail with a Postgres `null value in column "..." violates not-null constraint` error at runtime — typically caught only by post-merge CI on master, after the migration has already shipped.

## What to change

Edit `.agents/skills/django-migrations/SKILL.md` so that the next agent reading the skill understands and avoids this hazard.

Your update must:

1. **Add a new top-level section** to the file — a `##` heading whose title names the *cross-language* `NOT NULL` *hazard* (use that wording, with `NOT NULL` styled however you like in the heading text). Place the new section after the existing four-step Workflow.

2. In that section, **explain the mechanism** in prose:
   - Name the Django patterns that trigger it: `default=list`, `default=dict`, and `default=<callable>` on a non-nullable field.
   - State explicitly that Django applies these defaults **in Python only**, so Postgres sees the column with no column `DEFAULT`.
   - State that any non-Django writer doing a raw `INSERT` that omits the new column will hit the `NOT NULL` constraint.

3. **Name at least two concrete non-Django writers** the reader should grep for. The skill should mention at least two of: the plugin-server `nodejs/` tree, Rust services in `rust/`, Temporal workers, and ad-hoc raw-SQL scripts.

4. **Show the remediation** as a concrete `migrations.RunSQL(...)` snippet that runs `ALTER TABLE <table> ALTER COLUMN <col> SET DEFAULT ...` (with a matching `reverse_sql` that drops the default). The reader should be able to copy the snippet and adapt it.

5. **Cross-link from step 1 of the Workflow** ("Classify") to the new section, so an agent reading the Workflow in order discovers the hazard before classifying. Add a short pointer to the cross-language `NOT NULL` hazard at the end of step 1's bullet — keep step 1 itself otherwise intact.

The four original Workflow steps (1. Classify, 2. Generate, 3. Apply safety rules, 4. Validate) must all remain. The existing YAML frontmatter (`name: django-migrations`, `description: ...`) must remain. The existing pointer to the `clickhouse-migrations` skill must remain.

## Style requirements

This is a markdown skill file — it must follow the repo's markdown conventions.

- **Semantic line breaks**: prefer one sentence per line, no hard wrapping at a column limit. Long sentences may stay on a single line.
- **American English** spelling.
- Keep the prose terse and authoritative, in the same voice as the rest of `SKILL.md`. Describe the workflow and reasoning — do not write a rigid step-by-step script.
- Only the file `.agents/skills/django-migrations/SKILL.md` should be modified. Do not touch unrelated files.
- The PostHog repo enforces conventional-commit messages and has a public-facing OSS policy (no internal incident references in committed prose); keep the new skill content PR-agnostic and free of incident references.

## How your work is evaluated

A test suite reads `/workspace/posthog/.agents/skills/django-migrations/SKILL.md` and checks that:
- the new heading mentions the cross-language `NOT NULL` hazard,
- the prose names `default=list` / `default=dict` / `default=<callable>` and explains the Python-only / no-Postgres-DEFAULT mechanism,
- at least two non-Django writers are listed,
- a `migrations.RunSQL(...)` snippet with `ALTER TABLE ... ALTER COLUMN ... SET DEFAULT` is present,
- step 1 ("Classify") of the Workflow links to the new section,
- the original frontmatter, four workflow steps, and the `clickhouse-migrations` pointer are all preserved.
