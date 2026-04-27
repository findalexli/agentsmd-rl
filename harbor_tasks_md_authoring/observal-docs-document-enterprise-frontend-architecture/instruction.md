# docs: document enterprise frontend architecture decisions

Source: [BlazeUp-AI/Observal#507](https://github.com/BlazeUp-AI/Observal/pull/507)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `ee/AGENTS.md`
- `web/AGENTS.md`

## What to add / change

## Purpose / Description
Document the architectural decision for enterprise frontend code placement, based on industry research of Langfuse, PostHog, Infisical, Cal.com, Formbricks, and Lago.

## Fixes
* N/A — architecture documentation

## Approach
**Decision: No `web/ee/` directory.** Enterprise frontend code lives in `web/src/`, gated server-side via `useDeploymentConfig()`.

**Why:** 4 of 6 researched platforms (PostHog, Infisical, Cal.com, Lago) keep a single frontend codebase. Langfuse and Formbricks have `ee/` frontend dirs but allow bidirectional imports — the separation is legal, not architectural. Since our frontend is already AGPL and the licensing boundary is at `ee/` (backend), a second legal boundary in the frontend adds complexity for no benefit.

**Key decisions documented:**
- Enterprise pages go in `web/src/app/(admin)/` with `deploymentMode === "enterprise"` checks
- Future resource-based ACL follows PostHog's annotation pattern (`user_access_level` on API responses)
- No CASL or client-side policy engine — server filters results, frontend reads annotations

**Files changed:**
- `ee/AGENTS.md` — added "Frontend architecture" section
- `web/AGENTS.md` — added "Enterprise feature gating" section

## How Has This Been Tested?
Documentation-only change.

## Checklist
- [x] All commits are signed off (`git commit -s`) per the [DCO](https://developercertificate.org/)
- [x] You have a descriptive commit message with a short title (first line, max 50 chars).
- [x] 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
