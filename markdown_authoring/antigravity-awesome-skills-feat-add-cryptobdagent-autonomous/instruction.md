# feat: add crypto-bd-agent — autonomous BD patterns for exchanges

Source: [sickn33/antigravity-awesome-skills#92](https://github.com/sickn33/antigravity-awesome-skills/pull/92)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/crypto-bd-agent/SKILL.md`

## What to add / change

## New Skill: crypto-bd-agent

Production-tested patterns for building autonomous crypto business development 
agents, extracted from Buzz BD Agent (SolCex Exchange).

### What it covers
- Multi-chain token scanning and discovery (13 intelligence sources)
- 100-point weighted scoring system with catalyst adjustments
- Wallet forensics (deployer analysis, fund flow, cross-chain detection)
- x402 autonomous micropayments for premium intelligence
- ERC-8004 on-chain agent identity (dual-chain registration)
- Cost-efficient LLM cascade routing
- 10-stage pipeline management with human-in-the-loop
- Security rules for crypto agent operations

### Quality Bar Checklist
- [x] Standards: Read QUALITY_BAR.md and SECURITY_GUARDRAILS.md
- [x] Metadata: SKILL.md frontmatter is valid
- [x] Risk Label: risk: safe
- [x] Triggers: "When to use" section is clear and specific
- [x] Security: N/A (not offensive skill)
- [x] Local Test: Verified skill works locally on Akash container
- [x] Credits: Reference implementation linked in skill

### Type of Change
- [x] New Skill (Feature)

### Reference
- GitHub: https://github.com/buzzbysolcex/buzz-bd-agent
- ERC-8004: ETH Agent #25045 | Base Agent #17483
- Category suggestion: Business

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
