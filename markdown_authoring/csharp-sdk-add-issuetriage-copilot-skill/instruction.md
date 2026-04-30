# Add issue-triage Copilot skill

Source: [modelcontextprotocol/csharp-sdk#1412](https://github.com/modelcontextprotocol/csharp-sdk/pull/1412)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/issue-triage/SKILL.md`
- `.github/skills/issue-triage/references/cross-sdk-repos.md`
- `.github/skills/issue-triage/references/report-format.md`

## What to add / change

## Issue Triage Copilot Skill

Adds a new Copilot skill at `.github/skills/issue-triage/` that generates prioritized issue triage reports for the C# MCP SDK repository.

### What it does

The skill runs an 8-step workflow:

1. **Fetches live Tier 1 SLA criteria** from the [SDK Tiering documentation](https://modelcontextprotocol.io/sdk-tiers) — stops if the fetch fails (no stale fallback)
2. **Fetches all open issues** via the GitHub API with full metadata
3. **Classifies triage status** — triaged vs. untriaged, SLA compliance, label coverage
4. **Identifies issues needing attention** — SLA violations, missing labels, potential P0/P1 candidates, stale `needs confirmation` / `needs repro` issues (>14 days without author response), and duplicate/consolidation candidates
5. **Deep-dive reviews** every attention item by reading the full issue description and all comments, then summarizing current status and recommending labels and next steps
6. **Cross-SDK analysis** — searches the other 9 MCP SDK repos for related issues, grouped by theme (OAuth, SSE, Streamable HTTP, structured content, dynamic tools, etc.)
7. **Generates a BLUF report** — urgent items first, full backlog collapsed in a `<details>` element
8. **Presents a console summary** with key metrics and where the report was saved

### Report structure

The report follows a **BLUF (Bottom Line Up Front)** pattern:

- 🚨 SLA violations with full comment review and recommended actions
- ⚠️ Potential P0/P

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
