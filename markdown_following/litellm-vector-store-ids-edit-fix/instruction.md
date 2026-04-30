# Fix: Model Edit Form Injects Empty vector_store_ids

## Problem

When a model is edited through the LiteLLM admin dashboard and the model has no vector stores configured, the edit form incorrectly includes `vector_store_ids: []` (an empty array) in the update payload sent to the backend. This empty array gets merged into `litellm_params` and is then propagated to every subsequent inference call for that model.

Providers that do not expect a `vector_store_ids` field (such as Anthropic) reject or mishandle the request, breaking completions for models that were working before the edit.

## Reproduction Steps

1. Add any model via the dashboard (e.g., an Anthropic model with no vector store configuration)
2. Open the model's detail view and click **Edit Settings**
3. Without touching any vector-store-related fields, click **Save Changes**
4. Observe that the PATCH request payload contains `litellm_params.vector_store_ids: []`
5. Subsequent completion calls to that model now fail

## Expected Behavior

- When a model **has no vector stores** and the user edits it without touching vector store settings, the `vector_store_ids` key must **not appear** in the update payload at all. The backend should receive no indication that vector stores changed.
- When a model **has vector stores** and they are left unchanged during editing, the existing IDs should be preserved in the payload.
- When a user **explicitly clears** previously-configured vector stores, the payload should send an empty array `[]` so the backend knows to remove them.

## Constraints

- The fix must be in the dashboard UI component that handles model editing
- The existing 34 vitest tests for the model info view component must continue to pass
- A regression test should verify that editing a model with no vector stores does not inject `vector_store_ids` into the update payload
- The codebase uses **Vitest** and **React Testing Library** for UI tests
