# Add Start Over Action for First Chat Request

In VS Code's chat interface, when a user is at the first request (the very first message in a session), the checkpoint menu shows "Fork" and "Restore Checkpoint" actions. However, "Fork" doesn't make sense for the first request (there's nothing before it to fork from), and "Restore Checkpoint" should be renamed to "Start Over" since restoring the first checkpoint effectively clears everything.

The fix should:
1. Add an `isFirstRequest` context key (`chatFirstRequest`) in `chatContextKeys.ts`
2. Bind `isFirstRequest` in `chatListRenderer.ts` by checking if the request is the first in the model
3. Hide the Fork action when `isFirstRequest` is true (add `.negate()` to its `when` clause)
4. Hide Restore Checkpoint when `isFirstRequest` is true
5. Add a new `StartOverAction` that shows only on the first request, with label "Start Over" and tooltip "Clears the chat and undoes all changes"
