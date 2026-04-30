# feat(skills): Add django-models agent skill

Source: [getsentry/sentry#113837](https://github.com/getsentry/sentry/pull/113837)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/django-models/SKILL.md`
- `.agents/skills/generate-migration/SKILL.md`

## What to add / change

Adds a new agent skill at `.agents/skills/django-models/` that captures Sentry specific conventions for writing Django ORM models. Derived from analyzing recently added/modified models across the codebase (seer, preprod, explore, workflow_engine, hybridcloud, and more) to surface the patterns that have become de facto norms.

Focuses on the decisions an agent needs Sentry context to get right: silo placement, cross-silo replication, `RelocationScope`, foreign key type choice, and the handful of field/Meta patterns that aren't obvious from `django.db.models`. Defers migration generation and outbox plumbing to the existing `generate-migration` and `hybrid-cloud-outboxes` skills so the three compose without overlap.

Dogfooded on my in-flight seer-run-schema branch during authoring, which caught a few rough edges and drove some refinements.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
