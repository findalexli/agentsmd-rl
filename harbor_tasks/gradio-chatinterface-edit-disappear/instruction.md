# Bug: Edited messages disappear in ChatInterface UI

## Summary

When using `ChatInterface` with `editable=True`, editing a user message causes it to temporarily vanish from the chatbot display while waiting for the callback to yield or return a response. The edited message reappears only after the callback completes.

## Reproduction

1. Create a `ChatInterface` with `editable=True` and a slow or streaming callback.
2. Send a message.
3. Edit the message in the chatbot.
4. Observe: the chatbot clears the edited message immediately after editing, showing a blank history until the callback finishes responding.

## Expected behavior

After editing a message, the edited user message should remain visible in the chatbot UI while waiting for the assistant response — the same way a freshly submitted message behaves.

## Where to look

- `gradio/chat_interface.py` — specifically the `_setup_events` method where the `self.chatbot.edit(...)` event chain is wired up.
- Compare how the edit event chain is set up versus the submit and retry event chains in the same method. The submit and retry paths both ensure the user message is appended to the visible chat history before the response callback runs, but the edit path is missing this step.

## Hints

- Look at `_append_message_to_history` and how it is used in the submit and retry event chains.
- The edit handler (`_edit_message`) truncates the history and saves the edited text, but the event chain never re-appends the edited message to the displayed chatbot before triggering the response callback.
- The textbox interactivity toggling (disabling during response, re-enabling after) that submit/retry chains do is also absent from the edit chain.
