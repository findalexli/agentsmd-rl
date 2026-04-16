# Fix TTD (Text-to-Diagram) Error Handling Issues

The TTD feature's error handling has inconsistent translation keys and fragmented logic that causes incorrect error messages and incomplete cleanup when rate limits are exceeded.

## Problems

1. **Translation key inconsistencies**: Mermaid syntax errors use a translation key in the old `ttd` namespace (`ttd.errorMermaidSyntax`) instead of the `chat.errors` namespace used by other error messages. This creates inconsistency in how errors are displayed.

2. **Fragmented error handling**: Rate limit errors (HTTP 429) and zero-remaining rate limit checks are handled in separate code paths with redundant logic. When rate limits are exceeded, the partial assistant message is not properly cleaned up from the chat history.

3. **Missing analytics tracking**: Successful mermaid parsing is not being tracked, making it difficult to measure TTD feature adoption and diagnose parsing issues.

4. **Incorrect error messages**: Some error scenarios display messages with wrong translation keys, showing generic or confusing text to users.

## Required Behavior

### Translation Keys in `packages/excalidraw/locales/en.json`

The following translation keys must exist with these exact values:
- `chat.errors.mermaidParseError`: `"Mermaid syntax error"`
- `chat.errors.requestFailed`: `"Failed to send request, please try again later"`
- `chat.errors.generationFailed`: `"Failed to generate diagram"`

The old key `ttd.errorMermaidSyntax` must no longer exist in the locales file.

### Behavior in `packages/excalidraw/components/TTDDialog/TTDDialogOutput.tsx`

When displaying mermaid syntax errors, the component must use translation key `chat.errors.mermaidParseError`. The old translation key `ttd.errorMermaidSyntax` must no longer be used.

### Behavior in `packages/excalidraw/components/TTDDialog/hooks/useTextGeneration.ts`

1. **Error translation key usage**:
   - Network request failures must display the error using translation key `chat.errors.requestFailed`
   - Generation failures must display the error using translation key `chat.errors.generationFailed`
   - Mermaid parse errors must display the error using translation key `chat.errors.mermaidParseError`

2. **Rate limit error handling**: HTTP 429 status and rate limit remaining checks must be handled together in a single conditional check. When a rate limit error occurs, the partial assistant message must be removed from the chat history.

3. **Analytics tracking**: After successful mermaid parsing completes, an event tracking call must be made with the arguments `("ai", "mermaid parse success", "ttd")`.

4. **Code organization**: Error handling logic is currently wrapped in helper functions that add unnecessary indirection and use incorrect translation keys. The error handling should be directly visible in the main flow for clarity, and any translation keys that do not follow the `chat.errors.*` naming convention should be corrected.

## Validation

After making changes:
- Run `yarn test:typecheck` to verify TypeScript compiles
- Run `yarn test:code` to verify ESLint passes
- Run `yarn test:other` to verify Prettier formatting
- Run TTD-related tests to verify functionality

See `.github/copilot-instructions.md` and `CLAUDE.md` for coding standards.
