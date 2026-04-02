# Bash Tool Description Hurts Prompt Cache Hit Rates

## Problem

The bash tool in `packages/opencode/src/tool/bash.ts` builds its description by reading a template from `packages/opencode/src/tool/bash.txt` and substituting several placeholders (`${directory}`, `${maxLines}`, `${maxBytes}`).

One of these placeholders — `${directory}` — is replaced with the current project's directory path (via `Instance.directory`). This means the tool description is **different for every project**, even though the tool behavior is identical.

Because LLM API providers cache prompts based on exact prefix matching, a project-specific string in the tool description breaks caching. Every time a user switches projects (or opens a new one), the entire tool description is treated as new content, wasting tokens and increasing latency.

## Expected behavior

The bash tool description should be **project-independent** so that it can be cached across different projects. The `${maxLines}` and `${maxBytes}` substitutions are fine since those are global constants, but the directory should not be baked into the description.

## Files to investigate

- `packages/opencode/src/tool/bash.txt` — the description template
- `packages/opencode/src/tool/bash.ts` — where the template substitutions happen (look at the `description` field in the return object around line 59)

## Hints

- The `workdir` parameter's `.describe()` already mentions the directory, so users still know the default working directory.
- The template text referencing `${directory}` can be replaced with a static phrase that conveys the same meaning.
