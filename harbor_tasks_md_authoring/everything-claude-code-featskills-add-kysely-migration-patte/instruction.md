# feat(skills): add Kysely migration patterns to database-migrations

Source: [affaan-m/everything-claude-code#731](https://github.com/affaan-m/everything-claude-code/pull/731)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/database-migrations/SKILL.md`

## What to add / change

## Summary
- Add Kysely (TypeScript/Node.js) section to database-migrations skill
- Covers kysely-ctl CLI workflow (`init`, `migrate make/latest/down/list`)
- Includes migration file structure with `up`/`down` using `Kysely<any>` pattern
- Documents programmatic `Migrator` + `FileMigrationProvider` setup with `allowUnorderedMigrations` option
- Updates frontmatter description to include Kysely in the ORM list

## Test plan
- [x] `node tests/run-all.js` passes (no new failures)
- [ ] Verify markdown renders correctly on GitHub

🤖 Generated with [Claude Code](https://claude.com/claude-code)

<!-- This is an auto-generated description by cubic. -->
---
## Summary by cubic
Adds `Kysely` migration patterns to the `database-migrations` skill (CLI via `kysely-ctl`, `up`/`down` with `Kysely<any>`, programmatic `Migrator` + `FileMigrationProvider`). Updates examples with ESM-only imports (CJS `__dirname` note), renames the sample to `create_user_profile`, keeps `allowUnorderedMigrations` commented with a prod warning, switches to an `avatar_url` index, and updates the frontmatter to include `Kysely`.

<sup>Written for commit e2cdf0747a0391a6ac5f1dc79ab21f533c3dcbc7. Summary will update on new commits.</sup>

<!-- End of auto-generated description by cubic. -->

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Added Kysely as a supported migration tool alongside Prisma, Drizzle, Django, TypeORM, and golang-migr

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
