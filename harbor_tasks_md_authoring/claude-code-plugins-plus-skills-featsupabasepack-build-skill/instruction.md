# feat(supabase-pack): build skill 17/30 — supabase-cost-tuning

Source: [jeremylongshore/claude-code-plugins-plus-skills#453](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/453)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/saas-packs/supabase-pack/skills/supabase-cost-tuning/SKILL.md`

## What to add / change

## Summary
- Rewrites `supabase-cost-tuning` SKILL.md with production-grade content
- Covers Free/Pro/Team pricing tiers, compute add-on pricing, and read replicas vs scaling decision framework
- 3 structured steps: audit usage (SQL + TypeScript), optimize DB/storage/bandwidth, right-size compute + Edge Functions
- Includes connection pooling with Supavisor, Edge Function cold start reduction, and usage monitoring via pg_cron
- Adds Examples section with cost estimation script and quick audit snippet
- 7-row error handling table covering all major cost scenarios
- 7 resource links to official Supabase docs

## Test plan
- [ ] `python3 scripts/validate-skills-schema.py --enterprise plugins/saas-packs/supabase-pack/` passes with no ERRORs for this skill
- [ ] All required sections present: Overview, Prerequisites, Instructions (3 Steps), Output, Error Handling, Examples, Resources, Next Steps
- [ ] Code blocks use `createClient` from `@supabase/supabase-js` per SDK patterns
- [ ] Pricing tables match current supabase.com/pricing

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
