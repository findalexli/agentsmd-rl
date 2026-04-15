# Fix submit button not restored after example click

## Bug Description

In the `ChatInterface` class in `gradio/chat_interface.py`, clicking an example causes the submit button to disappear and not be restored.

The root cause is a race condition: a handler on the example select event unconditionally sets `submit_btn=False` on the textbox, competing with the main example chain's own restore logic. The two handlers run as separate registrations on the same event, so their effects race.

With `run_examples_on_click=False`, the race consistently loses the submit button because the textbox should never enter a processing state at all in that mode. With `run_examples_on_click=True`, the race can also cause intermittent failures.

## Expected Behavior After Fix

- The example select event should only be managed within the main example event chain — it should not be registered as an additional trigger in the stop-events setup, which creates the competing handler.
- When examples actually trigger inference, the submit button should still be temporarily hidden (to indicate processing) via a `.then()` step within the example chain, so it correctly reflects processing state during execution.
- For populate-only examples where no inference runs, no cancellation events should be registered for the example flow. The collection of events eligible for cancellation should only include the example event when examples actually execute.

## Acceptance Criteria

- The submit button is properly restored after clicking an example
- `gradio/chat_interface.py` remains syntactically valid Python
- Code passes `ruff format` and `ruff check`
- All existing `ChatInterface` unit tests continue to pass
