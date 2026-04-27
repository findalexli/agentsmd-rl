# feat: Add EmblemAI crypto wallet skill

Source: [sickn33/antigravity-awesome-skills#210](https://github.com/sickn33/antigravity-awesome-skills/pull/210)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/emblemai-crypto-wallet/SKILL.md`

## What to add / change

## New Skill: EmblemAI Crypto Wallet

**Category:** Web3 / Blockchain / DeFi

Crypto wallet management across 7 blockchains (Solana, Ethereum, Base, BSC, Polygon, Hedera, Bitcoin) via the EmblemAI Agent Hustle API.

### Capabilities
- Balance checks across all supported chains
- Token swaps and transfers
- Portfolio analysis
- Token research and contract verification

### Source
- **GitHub:** [EmblemCompany/Agent-skills](https://github.com/EmblemCompany/Agent-skills)
- **npm:** [@emblemvault/agentwallet](https://www.npmjs.com/package/@emblemvault/agentwallet) (v1.3.0)
- **License:** MIT
- **Built by:** [EmblemCompany](https://github.com/EmblemCompany) — creators of [Emblem Vault](https://emblemvault.io)

Follows the Agent Skills specification with progressive disclosure structure. Compatible with Claude Code, Codex, Cursor, Windsurf, Gemini CLI, and more.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
