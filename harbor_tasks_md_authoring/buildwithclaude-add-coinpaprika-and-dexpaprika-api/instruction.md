# Add CoinPaprika and DexPaprika API skills

Source: [davepoon/buildwithclaude#103](https://github.com/davepoon/buildwithclaude/pull/103)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/all-skills/skills/coinpaprika-api/SKILL.md`
- `plugins/all-skills/skills/dexpaprika-api/SKILL.md`

## What to add / change

## Summary
Adds two new skills to the all-skills collection for free cryptocurrency data access via hosted MCP servers:

- **coinpaprika-api**: 29 MCP tools for crypto market data — 12,000+ coins, 350+ exchanges, OHLCV, contract lookups, search. Free: 20K calls/month, no API key.
- **dexpaprika-api**: 14 MCP tools for DeFi analytics — 34+ blockchains, 30M+ pools, tokens, transactions. Free: 10K req/day, no API key.

## How it works
Both skills connect to hosted MCP servers — no local setup, no API key, no registration needed. Users can add the MCP URL directly or install via the full plugin marketplace:

```
/plugin marketplace add coinpaprika/claude-marketplace
```

## Links
- Plugin repo: https://github.com/coinpaprika/claude-marketplace
- CoinPaprika docs: https://docs.coinpaprika.com
- DexPaprika docs: https://docs.dexpaprika.com
- MCP servers: mcp.coinpaprika.com/sse and mcp.dexpaprika.com/sse

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
