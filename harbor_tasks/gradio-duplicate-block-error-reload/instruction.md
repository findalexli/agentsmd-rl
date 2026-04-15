# Fix DuplicateBlockError in multi-page apps with gr.render during reload

## Bug Description

When running a multi-page Gradio app with `gradio app.py` (reload mode), a `DuplicateBlockError` occurs when `gr.render` fires on the first page load after a code change is detected and the module is re-executed.

The root cause is a block ID collision during the reload cycle:

1. The initial execution imports child page modules (e.g., `page1.py`, `page2.py`), creating blocks with sequential IDs
2. When the reload watcher detects changes and re-executes the main module, `Context.id` is reset to 0 before the `exec()` call
3. Since child modules are already in `sys.modules`, they are not re-imported, so their blocks retain their original IDs
4. After `exec()`, `Context.id` ends up at a low value because only the root `Blocks` was re-created
5. When `gr.render` fires on the first page load, dynamically created blocks receive IDs that collide with existing block IDs from the child page modules

## What to Fix

The reload watcher code in the Gradio utility module performs the following sequence:
1. Resets `Context.id = 0`
2. Calls `exec(no_reload_source_code, module.__dict__)` to re-execute the module
3. Registers the module in `sys.modules`

The code region between the `exec()` call and the `sys.modules` registration (or the subsequent `while` loop) has access to:
- A `Context` class with an `id` attribute (initialized to 0 before the exec)
- A `module` object containing the re-executed module
- A `reloader` object with a `demo_name` attribute indicating which attribute on the module contains the demo object
- The demo object's `blocks` attribute, which is a dictionary mapping block IDs (integers) to block objects

After the `exec()` call completes, ensure that `Context.id` is advanced past all existing block IDs in `demo.blocks` so that dynamically created blocks from `gr.render` callbacks will not collide with blocks from already-imported child page modules.

## Acceptance Criteria

- After module re-execution in the reload watcher, `Context.id` is advanced past all existing block IDs (keys in the `demo.blocks` dictionary)
- Multi-page apps with `gr.render` no longer raise `DuplicateBlockError` during reload
- The utility module remains syntactically valid Python
- Single-page apps and normal reload behavior are unaffected
- All existing reload tests continue to pass
- All ruff linting and formatting checks pass on the modified module
