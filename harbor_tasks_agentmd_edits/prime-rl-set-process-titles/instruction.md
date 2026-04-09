# feat: set process titles on all entrypoints

## Problem

When running PRIME-RL training jobs, the process tree is difficult to inspect using standard tools like `ps`, `htop`, or `pstree`. All processes show up as generic `python` or `uv` commands, making it hard to identify which process is the launcher, trainer, inference server, orchestrator, etc.

This makes debugging and monitoring production training runs unnecessarily difficult, especially when multiple components are running on the same machine.

## Expected Behavior

1. All major PRIME-RL entrypoints should set descriptive process titles using the `setproctitle` library
2. Process titles should follow the format `PRIME-RL::{ComponentName}` (e.g., `PRIME-RL::Launcher`, `PRIME-RL::Trainer`)
3. The `skills/monitor-run/SKILL.md` file should be updated to document:
   - The process title conventions
   - How to inspect the process tree using `ps` and `pstree`
   - An example process tree showing all components

## Files to Look At

- `src/prime_rl/utils/process.py` — add the `set_proc_title()` utility function
- `src/prime_rl/entrypoints/inference.py` — call set_proc_title in main()
- `src/prime_rl/entrypoints/rl.py` — call set_proc_title in main()
- `src/prime_rl/entrypoints/sft.py` — call set_proc_title in main()
- `src/prime_rl/orchestrator/orchestrator.py` — call set_proc_title in main()
- `src/prime_rl/orchestrator/env_server/env_server.py` — call set_proc_title in main()
- `src/prime_rl/trainer/rl/train.py` — call set_proc_title in main()
- `src/prime_rl/trainer/sft/train.py` — call set_proc_title in main()
- `pyproject.toml` — add `setproctitle>=1.3.0` dependency
- `skills/monitor-run/SKILL.md` — document process titles and inspection commands

## Implementation Notes

- Use the `setproctitle` library (already available in the environment)
- Define a constant `PRIME_RL_PROC_PREFIX = "PRIME-RL"` for consistency
- Each component should set its title as soon as it starts (in the `main()` function)
- The SKILL.md update should include a table or list of all process titles and example commands for viewing them

Remember: per AGENTS.md, when you make changes to the codebase, check if any skills need to be updated to stay accurate. The process title feature should be documented in the monitor-run skill.
