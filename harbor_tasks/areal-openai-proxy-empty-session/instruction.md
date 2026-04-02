# Bug: OpenAI Proxy Workflow crashes on empty sessions in online mode

## Context

AReaL's OpenAI proxy workflow (`areal/experimental/openai/proxy/workflow.py`) supports an "online" mode where external users connect to generate training trajectories. The `arun_episode` method exports interactions from a completed session and records reward stats.

## Problem

When a user connects to the proxy but never actually sends any chat/completions requests (i.e., the session completes with zero interactions), the online-mode code path in `arun_episode` silently returns an empty `interactions` dict. This has two problems:

1. **Incorrect stats recording**: The code attempts `list(interactions.keys())[-1]` which raises an `IndexError` on an empty dict. Although there's a guard `if interactions else None`, the logic flow still falls through to `return interactions` — returning an empty dict instead of `None`, which downstream consumers interpret as a valid (but empty) trajectory rather than a rejected one.

2. **Missing warning**: Unlike the normal-mode error handling path which logs when an agent task fails, the online-mode path gives no indication that an empty session occurred, making debugging difficult.

## Expected behavior

- If a session has no interactions, the method should return `None` (indicating a rejected trajectory) and log a warning
- Stats should only be recorded when there are actual interactions
- The stats-recording code should be simplified to avoid the redundant empty-check pattern

## Files to investigate

- `areal/experimental/openai/proxy/workflow.py` — the `arun_episode` method, specifically the online-mode branch starting around the `# Record stats` comment
