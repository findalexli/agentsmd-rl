# feat: add agent-payment-x402 skill for autonomous agent payments

Source: [affaan-m/everything-claude-code#893](https://github.com/affaan-m/everything-claude-code/pull/893)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/agent-payment-x402/SKILL.md`

## What to add / change

## What

Adds `agent-payment-x402` — a skill that enables AI agents to make autonomous payments with built-in spending controls via the x402 HTTP payment protocol and MCP tools.

## Why

The skills directory covers coding, testing, deploying, researching, and security — but not payment execution. As agents compose more skills per session, some will need to purchase API calls, settle with other agents, or provision paid resources. This skill fills that gap.

## What's included

- **x402 protocol flow**: Machine-negotiable HTTP 402 → negotiate → sign → retry
- **Spending controls**: Per-task budgets, session limits, allowlisted recipients, rate limits
- **Non-custodial wallets**: ERC-4337 smart accounts — orchestrator sets policy, agent spends within bounds
- **MCP integration**: Drop-in `mcpServers` config with `npx agentwallet-sdk`
- **Best practices**: Fail-closed design, audit trails, testnet-first development

## Pairs with existing skills

- `mcp-server-patterns` — for building/configuring MCP servers
- `cost-aware-llm-pipeline` — for controlling LLM costs (this extends cost control to external payments)
- `security-review` — payment tools are high-privilege, same scrutiny as shell access

## Production references

- Merged into NVIDIA NeMo Agent Toolkit Examples ([PR #17](https://github.com/NVIDIA/NeMo-Agent-Toolkit-Examples/pull/17)) as the x402 payment tool
- npm: [`agentwallet-sdk`](https://www.npmjs.com/package/agentwallet-sdk)
- Protocol: [x402.org](https://x402.org

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
