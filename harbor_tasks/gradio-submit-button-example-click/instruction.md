# Fix submit button not restored after example click

## Bug Description

In `ChatInterface`, clicking an example causes the submit button to disappear and not be restored. The root cause is a race condition in the event handler structure:

1. `_setup_stop_events()` registers a **separate handler** on `chatbot.example_select` that sets `submit_btn=False` on the textbox.
2. The frontend `dispatch` loop processes multiple handlers for the same event **sequentially**, so:
   - **Handler 1** (main example chain) runs to completion, then dispatches the restore `.then()` as an async fire-and-forget call.
   - **Handler 2** (`submit_btn=False` from `_setup_stop_events`) starts immediately after in the next loop iteration.
3. The restore and Handler 2 both make concurrent HTTP requests, creating a race condition.

With `run_examples_on_click=False`, the race consistently results in `submit_btn=False` winning (the textbox should never enter processing state at all in this case). With `run_examples_on_click=True`, the race was less likely to manifest in practice, but the same structural issue existed.

## What to Fix

In `gradio/chat_interface.py`:

1. **Remove `self.chatbot.example_select` from the `event_triggers` list** passed to `_setup_stop_events()` — this eliminates the separate handler that causes the race.

2. **Add `submit_btn=False` as a `.then()` step in the example select chain** (only when `run_examples_on_click=True` and `cache_examples=False`) — placed after `example_clicked` and before `submit_fn`, keeping it in a single sequential chain so the restore always fires strictly after it.

3. **Skip `events_to_cancel` for populate-only examples** (`run_examples_on_click=False`) — no inference runs, so no stop/cancel behavior is needed. Use the `example_select_runs` flag to conditionally include the event.

## Affected Code

- `gradio/chat_interface.py` — the `_setup_events()` method

## Acceptance Criteria

- `self.chatbot.example_select` is removed from `_setup_stop_events` event triggers
- A `.then()` step with `submit_btn=False` is added to the example chain when appropriate
- `events_to_cancel` only includes the example event when examples actually run
- The file remains syntactically valid Python
