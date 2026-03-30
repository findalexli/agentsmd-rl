# Fix DuplicateBlockError in multi-page apps with gr.render during reload

## Bug Description

When running a multi-page Gradio app with `gradio app.py` (reload mode), a `DuplicateBlockError` occurs when `gr.render` fires on the first page load. The root cause is a block ID collision:

1. The initial execution imports child page modules (e.g., `page1.py`, `page2.py`), creating blocks with sequential IDs starting from 0.
2. When `watchfn` detects changes and re-executes the main module, it resets `Context.id = 0` and calls `exec()` on the module.
3. Since child modules are already in `sys.modules`, they are not re-imported, so their blocks retain their original IDs.
4. After `exec()`, `Context.id` ends up at a low value because only the root `Blocks` was re-created.
5. When `gr.render` fires on the first page load, dynamically created blocks receive IDs that collide with existing block IDs from the child page modules, causing `DuplicateBlockError`.

## What to Fix

In `gradio/utils.py`, in the `watchfn` function, after the `exec()` call that re-executes the module source code, ensure that `Context.id` is set to be higher than all existing block IDs. Specifically, after `exec(no_reload_source_code, module.__dict__)`, retrieve the demo object and set `Context.id` to `max(existing_block_ids) + 1` so that dynamically created blocks from `gr.render` callbacks will not collide with blocks from already-imported child page modules.

## Affected Code

- `gradio/utils.py`: the `watchfn` function, specifically the section after `exec(no_reload_source_code, module.__dict__)`

## Acceptance Criteria

- After module re-execution in `watchfn`, `Context.id` is advanced past all existing block IDs
- Multi-page apps with `gr.render` no longer raise `DuplicateBlockError` during reload
- The file remains syntactically valid Python
- Single-page apps and normal reload behavior are unaffected
