# Add BlockRun: Agent Wallet for LLM Micropayments

Source: [sickn33/antigravity-awesome-skills#1](https://github.com/sickn33/antigravity-awesome-skills/pull/1)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/blockrun/SKILL.md`

## What to add / change

## Summary

Adds **BlockRun** - a skill that gives AI agents a crypto wallet (USDC on Base) to autonomously pay for capabilities they lack.

### What it does

| Agent Needs | BlockRun Provides |
|-------------|-------------------|
| Image generation | DALL-E, Nano Banana |
| Real-time X/Twitter data | Grok Live Search |
| Second opinions | GPT-5, DeepSeek, Gemini |
| Cost optimization | Route to cheaper models |

### Key features

- **No API keys** - wallet pays per token via x402 micropayments
- **Auto-wallet creation** on first use
- **Works with Claude Code AND Antigravity**
- **30+ models** from 5 providers (OpenAI, xAI, Google, DeepSeek, Anthropic)
- **Budget tracking** and spending controls

### Installation

```bash
pip install blockrun-llm
```

### Links

- **Repo:** https://github.com/BlockRunAI/blockrun-agent-wallet
- **Website:** https://blockrun.ai
- **x402 Protocol:** https://x402.org

### Category

This fits under **System Extension** - extends agent capabilities with wallet/payment infrastructure.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
