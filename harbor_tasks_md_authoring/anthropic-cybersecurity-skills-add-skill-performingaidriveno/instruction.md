# Add skill: performing-ai-driven-osint-correlation

Source: [mukul975/Anthropic-Cybersecurity-Skills#11](https://github.com/mukul975/Anthropic-Cybersecurity-Skills/pull/11)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/performing-ai-driven-osint-correlation/SKILL.md`

## What to add / change

## New Skill: performing-ai-driven-osint-correlation

### What this adds

A new cybersecurity skill for **AI-driven OSINT correlation** — using LLMs to cross-reference and correlate findings from multiple OSINT sources into unified intelligence profiles with confidence scoring.

### Why it's valuable

The existing skill set covers individual OSINT tools (SpiderFoot, Maltego, etc.) but lacks a skill focused on the **correlation layer** — the process of linking fragmented findings across sources into coherent entity profiles. This is increasingly the hardest and most time-consuming part of OSINT work, and AI/LLMs are uniquely suited to it.

This skill covers:
- **Multi-source collection** using Sherlock, theHarvester, SpiderFoot, and breach databases
- **Data normalization** into a common schema for cross-tool analysis
- **AI-powered correlation** with confidence scoring (0.0–1.0) for identity linkage
- **Entity resolution** to deduplicate and merge records across fragmented datasets
- **False positive detection** using LLM reasoning to separate coincidental from genuine matches
- **Structured reporting** in JSON and Markdown with Maltego-compatible export

### Subdomain
`threat-intelligence`

### Checklist
- [x] Name is lowercase kebab-case
- [x] Description includes agent-discovery keywords
- [x] Instructions are actionable with real commands and tool names
- [x] Domain and subdomain set correctly
- [x] Tags include relevant tools, frameworks, and techniques
- [x] Follows CON

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
