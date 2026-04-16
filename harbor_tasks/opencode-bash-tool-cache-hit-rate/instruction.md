# Bash Tool Description Hurts Prompt Cache Hit Rates

## Problem

The Bash tool description is currently **project-dependent**, causing poor cache hit rates with LLM API providers. Because tool descriptions are included in every prompt, project-specific strings in the description break prefix-based caching. Every time a user switches projects, the entire tool description is treated as new content, wasting tokens and increasing latency.

The root cause is that the tool description template contains a placeholder for the project's working directory, which gets substituted with a unique path for each project. This makes the description different across projects even though the tool behavior is identical.

## Expected Behavior

The Bash tool description should be **project-independent** so that it can be cached across different projects. Global constants like maximum output limits are acceptable substitutions, but project-specific paths should not be baked into the description.

### Requirements for the Tool Description Template

The template file (read by the Bash tool implementation) must:
- **NOT** contain any placeholder that gets replaced with a project-specific directory path (this breaks caching)
- Still **CONTAIN** placeholders for global constants like `${maxLines}` and `${maxBytes}` (these are acceptable since they're consistent across all projects)
- Be substantial documentation: at least 20 lines, 100+ words, and mention at least 5 distinct concepts from: command, output, execute, run, shell, timeout, workdir, truncation, parameter, exit
- Describe the default working directory behavior (must mention "working directory", "current directory", "default directory", or describe where commands run)
- Include guidance sections covering:
  1. Proper quoting practices (mention "quote", "quoting", or "double quote")
  2. Preference for specialized tools over bash for file operations (mention "specialized tool", "dedicated tool", or "DO NOT use" with reading/writing/editing/searching)
  3. Timeout and truncation behavior (mention "timeout", "time out", or "truncat")

### Requirements for the Tool Implementation

The TypeScript implementation that registers the Bash tool must:
- **NOT** inject any project-specific path (like the current working directory or project root) into the tool description
- **NOT** use `: any` type annotations anywhere in the file
- Still export the BashTool class or object
- Still reference a DESCRIPTION constant and set a tool description property
- Still reference the maximum line and byte constants (MAX_LINES/MAX_BYTES or maxLines/maxBytes)
