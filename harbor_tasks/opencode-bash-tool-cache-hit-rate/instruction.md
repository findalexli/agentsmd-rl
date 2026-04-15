# Bash Tool Description Hurts Prompt Cache Hit Rates

## Problem

The bash tool in `packages/opencode/src/tool/bash.ts` builds its description by reading a template from `packages/opencode/src/tool/bash.txt` and substituting several placeholders (`${directory}`, `${maxLines}`, `${maxBytes}`).

One of these placeholders — `${directory}` — is replaced with the current project's directory path (via `Instance.directory`). This means the tool description is **different for every project**, even though the tool behavior is identical.

Because LLM API providers cache prompts based on exact prefix matching, a project-specific string in the tool description breaks caching. Every time a user switches projects (or opens a new one), the entire tool description is treated as new content, wasting tokens and increasing latency.

## Expected behavior

The bash tool description should be **project-independent** so that it can be cached across different projects. The `${maxLines}` and `${maxBytes}` substitutions are fine since those are global constants, but the directory should not be baked into the description.

### Requirements for bash.txt

The template file must:
- **NOT** contain the `${directory}` placeholder (this breaks caching)
- Still **contain** the `${maxLines}` and `${maxBytes}` placeholders (these are acceptable global constants)
- Be substantial content: at least 20 lines, 100+ words, and mention at least 5 distinct concepts from: command, output, execute, run, shell, timeout, workdir, truncation, parameter, exit
- Describe the default working directory behavior (must mention: "working directory", "current directory", "default directory", or describe where commands run)
- Include guidance sections on: (1) proper quoting practices, (2) preference for specialized tools over bash for file operations, and (3) timeout/truncation behavior

### Requirements for bash.ts

The TypeScript file must:
- **NOT** inject `Instance.directory` or any project-specific path into the tool description
- **NOT** use `: any` type annotations
- Still export `BashTool`
- Still reference `DESCRIPTION` and set a tool description
- Still reference `MAX_LINES` and `MAX_BYTES` (or `maxLines`/`maxBytes`)
