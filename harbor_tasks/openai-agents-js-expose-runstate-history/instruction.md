# Expose Combined Run History from RunState

## Summary

The `RunState` class in `@openai/agents-core` tracks the state of an agent run through two internal fields: `_originalInput` (the initial user input items) and `_generatedItems` (items produced during the run). Currently, there is no public property to retrieve the full conversation history as a single combined sequence — consumers must manually access both internal fields and merge them.

## Task

Add a public, read-only `history` property on the `RunState` class that returns the full conversation history as an `AgentInputItem[]` — the original input item(s) followed by any generated output items, combined into a single array in temporal order.

The history must:

- Return an array where the first element(s) are the original input item(s)
- Include generated items after they are pushed to `_generatedItems`
- Survive a JSON serialization round-trip via `state.toString()` and `RunState.fromString()`

## Code Style Requirements

- Run `pnpm lint` and ensure no ESLint errors.
- Code must pass `pnpm -r build-check` (TypeScript compilation and type checking).
- Follow existing JSDoc conventions for public API documentation (comments must end with a period).

## Testing

- Run `CI=1 npx vitest run packages/agents-core/test/` to verify existing unit tests pass.
- Add tests in `packages/agents-core/test/runState.test.ts` to cover the new property's behavior, including a serialization round-trip edge case.
