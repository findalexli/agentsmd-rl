# feat(business): add gdpr and licensing compliance skills

Source: [cwinvestments/memstack#7](https://github.com/cwinvestments/memstack/pull/7)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/business/gdpr/SKILL.md`
- `skills/business/licensing/SKILL.md`

## What to add / change

## Summary
Two new repo-driven compliance skills under `skills/business/`, following the existing SKILL.md format used by `contract-template`.

- **`gdpr/`** — Scans the repo for personal-data signals (DB schemas, form fields, API DTOs, auth config, analytics SDKs, cookies, logging, third-party integrations), classifies sensitivity (Identifier / Financial / Location / Behavioral / Gov ID / Art 9 special category / Art 8 children / Art 10 criminal), then issues a verdict on whether GDPR applies and how critical it is. Maps required roles (Controller / Processor / DPO / Art 27 representative), triggered articles (Art 5/6/7/8/9/13/14/15-22/25/28/30/32/33/34/35/37-39 + Chapter V transfers), gap-analyses against existing privacy artifacts, and produces a remediation plan with an exposure summary (Art 83 fines).
- **`licensing/`** — Scans every manifest, lockfile, vendored dir, and asset folder across Node/Python/Rust/Go/Java/Ruby/PHP/.NET/containers, resolves the actual upstream LICENSE (not metadata), classifies into a 9-class taxonomy, and produces a per-package verdict table driven by the project's distribution model (SaaS / Binary / Library / Internal). Each row is marked ✅ Ready / 📝 Citation required / ❓ Needs info / ❌ Not allowed for commercial use, with the required action. Generates a `THIRD_PARTY_LICENSES.md` attribution bundle and flags version-change traps (Elastic/Mongo/Redis/Terraform/HashiCorp/Sentry).

Both skills include the standard sections (Activation, Con

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
