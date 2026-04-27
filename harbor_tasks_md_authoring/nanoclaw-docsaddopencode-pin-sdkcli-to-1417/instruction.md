# docs(add-opencode): pin SDK/CLI to 1.4.17, overlay propagation, env vars

Source: [qwibitai/nanoclaw#1864](https://github.com/qwibitai/nanoclaw/pull/1864)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/add-opencode/SKILL.md`

## What to add / change

## Summary

- **Pin SDK + CLI to 1.4.17** — `opencode-ai@latest` silently upgraded to 1.14.x which has a breaking session API rewrite (UUID → `ses_` prefix) incompatible with the current provider code. Both must be the same version.
- **Step 7: propagate to existing per-group overlays** — each agent group has a live `data/v2-sessions/*/agent-runner-src/providers/` overlay that overrides the image at runtime and is never auto-updated by rebuilds. Groups wired before the skill runs need the new files copied in manually.
- **Build cache gotcha** — prune builder with `docker builder prune -f` if "Unknown provider: opencode" appears after a clean rebuild (buildkit caches COPY steps aggressively).
- **`ANTHROPIC_BASE_URL` documented as required** for non-anthropic providers — the container provider passes it as `baseURL` for the upstream provider config. Added correct values for DeepSeek and OpenRouter.
- **`OPENCODE_SMALL_MODEL` added to all examples.**
- **OneCLI credential grant documented** — `set-secrets` replaces the full list, not appends; existing secret IDs must be included.

## Test plan

- [ ] Fresh install: run `/add-opencode` steps 1–7 on a repo with no existing opencode files, verify `pnpm run chat` responds via opencode provider
- [ ] Existing group: confirm step 7 loop copies files into overlay and agent responds without "Unknown provider" error
- [ ] DeepSeek example: set env vars as shown, register secret, grant agent, verify response

🤖 Generated with [Claude Cod

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
