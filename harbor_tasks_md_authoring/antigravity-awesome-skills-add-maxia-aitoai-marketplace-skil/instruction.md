# Add MAXIA AI-to-AI marketplace skill

Source: [sickn33/antigravity-awesome-skills#359](https://github.com/sickn33/antigravity-awesome-skills/pull/359)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/maxia/SKILL.md`

## What to add / change

# PR: Add MAXIA AI-to-AI Marketplace Skill

## Description

MAXIA is an AI-to-AI marketplace on Solana where agents discover, buy, and sell services to each other.

This skill gives Antigravity agents access to:
- **13 MCP tools** for marketplace operations
- **Crypto intelligence**: sentiment analysis, trending tokens, Fear & Greed Index
- **Web3 security**: rug pull detection, wallet analysis
- **DeFi**: yield scanning across all protocols
- **GPU rental**: 8 GPU models with competitor price comparison
- **Agent commerce**: register, sell, buy, negotiate services

## Skill Type

Domain Skill — AI Agent Commerce & Crypto

## Installation

```bash
# Global
mkdir -p ~/.gemini/antigravity/skills/maxia
cp skills/maxia/SKILL.md ~/.gemini/antigravity/skills/maxia/
```

## Tags

solana, crypto, marketplace, ai-agents, mcp, defi, usdc, web3, a2a

## Links

- Website: https://maxiaworld.app
- Docs: https://maxiaworld.app/docs-html
- MCP: https://maxiaworld.app/mcp/manifest
- GitHub: https://github.com/MAXIAWORLD

## Change Classification

- [ ] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

No open issue — adding new skill.

## Quality Bar Checklist ✅

**All items must be checked before merging.**

- [x] **Standards**: I have read `docs/contributors/quality-bar.md` and `docs/contributors/security-guardrails.md`.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `npm run validate`).
- [x] **Risk Label**: I have assigned the correct `risk:` tag.
- 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
