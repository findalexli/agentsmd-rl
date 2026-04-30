# docs: update Cursor Cloud Supabase workaround and env vars

Source: [Asymmetric-al/core#174](https://github.com/Asymmetric-al/core/pull/174)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

<!-- CURSOR_AGENT_PR_BODY_BEGIN -->
## Summary

Updates the `## Cursor Cloud specific instructions` section in `AGENTS.md` with more accurate Supabase local startup workaround based on actual setup experience.

### Changes
- Expanded migration workaround to cover **all** `2026*` migrations (not just `foundation_1_schema.sql`)
- Documented the `authz_memberships_foundation` migration issue where Postgres rejects the `COALESCE(staff_role::text, '')` index expression as non-IMMUTABLE
- Added `SKIP_ENV_VALIDATION=1` to recommended env vars for local dev (needed when optional keys like Stripe/Sentry are not set)

### Environment Setup Verification

All checks pass on this branch:

- **Lint**: 13/13 packages pass
- **Typecheck**: 13/13 packages pass
- **Unit tests**: 94 test files, 379 tests pass
- **Build**: All 3 apps build successfully (ci:preflight passes)
- **Donor app dev server**: Serves HTTP 200 on port 3000

### Demo

<a href="https://cursor.com/agents/bc-96a1d73b-1615-4e1c-8f8a-c153bc2e3ec4/artifacts?path=%2Fopt%2Fcursor%2Fartifacts%2Fdonor_app_registration_demo.mp4"><img src="https://cursor.com/artifacts/c/art-172df98a-1d94-4db3-af1c-0a833a4bc9d3" alt="donor_app_registration_demo.mp4" /></a>

Donor app homepage, login, and registration flow working end-to-end:

![Donor homepage](https://cursor.com/artifacts/c/art-cc24cf5e-1a0b-45ad-ad1a-456f72cbbaf7)
![Donor login page](https://cursor.com/artifacts/c/art-ab56d06b-6074-4883-a287-b9a3d581ab3b)
![Registration success](https

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
