# Add presenton skill

Source: [besoeasy/open-skills#14](https://github.com/besoeasy/open-skills/pull/14)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/presenton/SKILL.md`

## What to add / change

Adds a skill for [Presenton](https://github.com/presenton/presenton), an open-source, locally-run AI presentation generator with a built-in MCP server.

### New skill: `skills/presenton/SKILL.md`

- **Docker setup** — one-command deployment with configurable LLM and image providers (OpenAI, Gemini, Anthropic, Ollama, DALL-E 3, Pexels, etc.)
- **REST API usage** — `POST /api/v1/ppt/generate` to produce PPTX/PDF from a prompt, with Bash and Node.js examples
- **MCP integration** — connect agent tools directly to `http://localhost:5000/mcp` via `generate_presentation` tool call
- **Custom templates** — upload existing PPTX via `/api/v1/ppt/upload-template` to generate on-brand slides
- **Agent prompt, troubleshooting, output format, and best practices** sections following existing skill conventions

<!-- START COPILOT ORIGINAL PROMPT -->



<details>

<summary>Original prompt</summary>

> 
> ----
> 
> *This section details on the original issue you should resolve*
> 
> <issue_title>Add presenton as skill</issue_title>
> <issue_description>GitHub Repo https://github.com/presenton/presenton</issue_description>
> 
> ## Comments on the Issue (you are @copilot in this section)
> 
> <comments>
> </comments>
> 


</details>



<!-- START COPILOT CODING AGENT SUFFIX -->

- Fixes besoeasy/open-skills#13

<!-- START COPILOT CODING AGENT TIPS -->
---

🔒 GitHub Advanced Security automatically protects Copilot coding agent pull requests. You can protect all pull requests by enabling Advanced

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
