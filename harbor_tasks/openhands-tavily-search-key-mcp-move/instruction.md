# Move the Tavily search API key off the LLM Settings page

## Background

This is the OpenHands web app frontend (Vite + React Router + TypeScript +
TanStack Query, tested with Vitest). User settings are split across separate
pages: an **LLM Settings** page (model, API key, advanced LiteLLM knobs, …)
and an **MCP Settings** page (general MCP servers and other tool-side
credentials).

The "Tavily" web-search API key (`search_api_key` on the user-settings model)
is a credential consumed by an MCP-style search tool, not by the LLM
provider. Today it is rendered as a field on the **LLM Settings** page.

## The bug

Because the Tavily key lives inside the LLM settings form, **saving the LLM
form clears the Tavily key**:

1. User opens LLM Settings while a Tavily key is already configured.
2. User edits any LLM-owned field (e.g. switches model) and clicks **Save**.
3. The save mutation submits the entire form, including an empty
   `search_api_key` (the page never displayed the actual value).
4. The backend persists `search_api_key=""`, wiping the previously stored
   Tavily credential.

The same bug also surfaces in the page's view-mode logic: when the refetched
settings still contain a non-empty `search_api_key` (e.g. set by another
client), the page incorrectly classifies that as an "all-only" advanced
field and forces the user out of the basic view.

## What you need to change

**The Tavily search key must move out of LLM Settings entirely and become an
MCP-owned setting.** Concretely:

1. **Remove the Tavily field from the LLM Settings page.**
   - The advanced view must not render an element with
     `data-testid="search-api-key-input"`.
   - The LLM save mutation payload must not contain a `search_api_key`
     property at all (not `""`, not `undefined` — the key must be absent).
   - Hidden-state / view-classification logic on the LLM page must ignore
     `search_api_key` so a refetched MCP-owned key never forces the user
     into the all-fields view.

2. **Add a built-in Tavily search section to the MCP Settings page.**

   The new section must satisfy these contractual selectors (the test suite
   targets them by `data-testid`):

   | `data-testid`                     | Required role                                                                       |
   | --------------------------------- | ----------------------------------------------------------------------------------- |
   | `mcp-search-settings-section`     | Wrapper element for the new built-in search/Tavily panel.                           |
   | `search-api-key-input`            | The text/password input for the Tavily key, pre-populated with the persisted value. |
   | `save-search-api-key-button`      | Click-target that persists the edited key.                                          |

   Behavioural requirements for the new section:
   - On mount, the input must show the value returned by `getSettings()`
     (i.e. the existing persisted `search_api_key`).
   - Clicking the save button must call `SettingsService.saveSettings` with
     **exactly** `{ search_api_key: <current input value> }` and nothing
     else — saving the Tavily key must not also push LLM-owned fields.
   - After save, the input value must reflect what the user typed (i.e. the
     refetched settings, including the new key, drive the input).

3. **i18n**: any new user-visible string you add for this section must be a
   translation key, declared in both `frontend/src/i18n/translation.json`
   and `frontend/src/i18n/declaration.ts` (per the project's "Adding User
   Settings" guidance in `AGENTS.md`).

4. **No regressions**: every existing case in
   `frontend/__tests__/routes/llm-settings.test.tsx` and
   `frontend/__tests__/routes/mcp-settings.test.tsx` must continue to pass.

## Code Style Requirements

The grader runs the project's own `npm run lint` (which is
`npm run typecheck && eslint src --ext .ts,.tsx,.js && prettier --check src/**/*.{ts,tsx}`).
Your change must pass:

- TypeScript compiles cleanly (`tsc` via `react-router typegen && tsc`).
- ESLint reports no new errors.
- Prettier reports the code is formatted (`prettier --check`).

`AGENTS.md` requires `cd frontend && npm run lint:fix && npm run build` to
succeed before pushing frontend changes. The build step is not part of the
grader, but the lint step is.

## Where to look

- The LLM Settings route (`frontend/src/routes/llm-settings.tsx`) currently
  owns the search-API-key field and includes it in the form's hidden /
  payload state — this is what causes the bug.
- The MCP Settings route (`frontend/src/routes/mcp-settings.tsx`) is the
  destination for the new built-in search section.
- Settings types live under `frontend/src/types/` and the data-access layer
  is `frontend/src/api` wrapped by hooks under `frontend/src/hooks/`. Per
  `AGENTS.md`, components must go through TanStack Query hooks and not call
  the API client directly.

## How your change is graded

The grader runs `vitest` on the two affected test files and `npm run lint`.
Specifically, the following test cases (in
`frontend/__tests__/routes/llm-settings.test.tsx` and
`frontend/__tests__/routes/mcp-settings.test.tsx`) must pass:

- `LlmSettingsScreen does not include search API key updates when saving basic LLM settings`
- `LlmSettingsScreen does not render the search API key input in advanced LLM settings`
- `LlmSettingsScreen does not reveal all-only fields after save when refetch includes an MCP-owned search API key`
- `MCPSettingsScreen renders and saves the built-in Tavily search settings on the MCP page`
- `MCPSettingsScreen removes a newly added MCP server after the delete flow completes`

…together with all other pre-existing cases in those two files.
