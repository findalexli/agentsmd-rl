# Add Agent Prompt Card to Local Explorer UI

## Task

The Local Explorer homepage is missing a feature to help AI coding agents discover and use the Local Explorer API. Add a "Copy prompt for agent" card to the homepage that generates and copies a prompt instructing an LLM/agent how to use the local Explorer API.

## Background

Cloudflare Workers SDK includes a Local Explorer UI (`@cloudflare/local-explorer-ui`) that provides a web interface for managing local Cloudflare resources (KV, R2, D1, Durable Objects, Workflows) during development. The Local Explorer exposes a REST API at a path like `/cdn-cgi/explorer/api` that agents can use to programmatically interact with these resources.

Currently, an AI agent connecting to the Local Explorer has no way to discover this API. We need a prompt that tells the agent what services are available and how to find the API endpoints.

## Requirements

### 1. Utility Module

Create a new utility module `agent-prompt.ts` for agent prompt functionality. Place it in the `packages/local-explorer-ui/src/utils/` directory. It must export three functions:

**`getLocalExplorerApiEndpoint(origin: string, apiPath: string): string`**
- Concatenates the page `origin` and `apiPath` to produce a fully-qualified API endpoint URL.
- For example, origin `http://localhost:8787` and path `/cdn-cgi/explorer/api` should produce `http://localhost:8787/cdn-cgi/explorer/api`.

**`createLocalExplorerPrompt(apiEndpoint: string): string`**
- Returns a prompt string that an AI agent/LLM can read to understand how to use the Explorer API.
- The prompt must mention that the following Cloudflare services are available locally: **KV, R2, D1, Durable Objects, and Workflows** — the exact phrase `"KV, R2, D1, Durable Objects, and Workflows"` must appear verbatim.
- The prompt must include the phrase `"API endpoint:"` followed by the resolved API endpoint URL.
- The prompt must instruct the agent to `"Fetch the OpenAPI schema from"` the API endpoint URL.
- The prompt template must use `{{apiEndpoint}}` as a placeholder that gets replaced by the actual endpoint. The function must replace ALL occurrences of this placeholder (use `replaceAll`).

**`copyTextToClipboard(text: string, clipboard: Pick<Clipboard, "writeText">): Promise<void>`**
- Copies text by calling `writeText` on the provided clipboard object.
- The clipboard parameter has a default value — when not provided, it uses the browser's `navigator.clipboard`.
- The function must be `async` and return a `Promise<void>`.

### 2. Homepage Integration

Update the homepage route (`index.tsx`) to display a "Copy prompt for agent" card:

- Import `Button`, `LayerCard`, and `useKumoToastManager` from `"@cloudflare/kumo"`.
- Import `CopyIcon` from `"@phosphor-icons/react"`.
- In the route's `loader`, compute the API endpoint by calling `getLocalExplorerApiEndpoint` with `window.location.origin` and `import.meta.env.VITE_LOCAL_EXPLORER_API_PATH`, then generate the prompt with `createLocalExplorerPrompt`. The component must access loader data via `useLoaderData`.
- Wrap the existing content (logo, title, subtitle) in a centered container with `max-w-sm` and appropriate spacing classes.
- Below the existing content, add a `LayerCard` containing:
  - A header section (`LayerCard.Secondary`) with the title text **"Copy prompt for agent"** and a `Button` that triggers the copy action. The button must use:
    - `icon={CopyIcon}`
    - `size="sm"`
    - `variant="ghost"`
    - `onClick` handler that calls the copy function (the promise must be explicitly voided with the `void` keyword to satisfy the no-floating-promises rule).
  - A body section (`LayerCard.Primary`) that displays the prompt text in a monospace font with `max-h-16 overflow-auto p-3 text-left` styling.
- The copy action on success must show a toast with title `"Copied to clipboard"` and variant `"success"`.
- The copy action on failure must show a toast with title `"Failed to copy to clipboard"`, description `"Something went wrong when trying to copy the prompt."`, and variant `"default"`.

### 3. Tests

Include unit tests for all three utility functions. For `copyTextToClipboard`, use Vitest's `vi.fn()` to mock the clipboard parameter and assert that `writeText` is called exactly once with the correct text.

### 4. Dependency Update

Update `@cloudflare/kumo` from `^1.17.0` to `^1.18.0` in the package's `package.json` dependencies.

## Code Style Requirements

- The project uses **oxfmt** for formatting: tabs (not spaces), double quotes, semicolons, trailing commas. Format code accordingly.
- No floating promises: promises must be awaited or explicitly voided.
- Always use curly braces for control flow statements.
- Import order: third-party imports first, then local/sibling imports.
