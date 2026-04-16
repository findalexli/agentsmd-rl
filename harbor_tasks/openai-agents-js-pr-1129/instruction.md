# Omit Empty Computer Safety Checks on Replay

## Symptom

When a `computer_call` or `computer_call_result` item is rebuilt for Responses API replay via `getInputItems()`, empty `pending_safety_checks` and `acknowledged_safety_checks` arrays are always included in the output object — even when they are empty.

The live OpenAI API rejects replayed `computer_call` items that carry empty `pending_safety_checks` arrays, responding with a 400 error: `pending_safety_checks is not supported for the 'computer' tool`. This breaks `computer-use` and `computer-use-hitl` flows that involve replay.

## Expected Behavior

After the fix, when rebuilding a `computer_call` item whose `providerData.pending_safety_checks` is an empty array, the rebuilt item must NOT contain the `pending_safety_checks` key at all.

Similarly, when rebuilding a `computer_call_result` item whose `providerData.acknowledged_safety_checks` is an empty array, the rebuilt item must NOT contain the `acknowledged_safety_checks` key at all.

Non-empty safety check arrays must still be preserved in the rebuilt item unchanged.

## How to Verify

Rebuild the `agents-openai` package and run its test suite. The test `"omits empty computer safety checks when rebuilding input items"` in `packages/agents-openai/test/openaiResponsesModel.helpers.test.ts` should pass.

The key behavioral assertions are:
- A rebuilt `computer_call` item does NOT contain a `pending_safety_checks` key when the original `providerData` had an empty `pending_safety_checks` array
- A rebuilt `computer_call_result` item does NOT contain an `acknowledged_safety_checks` key when the original `providerData` had an empty `acknowledged_safety_checks` array
- A rebuilt `computer_call` item DOES contain the `pending_safety_checks` key with its original array value when that array is non-empty
- A rebuilt `computer_call_result` item DOES contain the `acknowledged_safety_checks` key with its original array value when that array is non-empty

## Context

`getInputItems()` transforms internal protocol items into OpenAI Responses API input format. For item types that carry safety-check arrays in their `providerData`, the function should omit the corresponding key from the rebuilt item when the array is empty, matching the live API's behavior.
