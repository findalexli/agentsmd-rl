# Fix subclass error names in `@openai/agents-core`

## Problem

In the `@openai/agents-core` package, every concrete error class extends an
abstract base class:

```ts
export abstract class AgentsError extends Error {
  state?: RunState<any, Agent<any, any>>;

  constructor(message: string, state?: RunState<any, Agent<any, any>>) {
    super(message);
    this.state = state;
  }
}
```

Concrete subclasses such as `MaxTurnsExceededError`, `ModelBehaviorError`,
`UserError`, `SystemError`, `GuardrailExecutionError`, `ToolCallError`,
`InputGuardrailTripwireTriggered`, `OutputGuardrailTripwireTriggered`,
`ToolInputGuardrailTripwireTriggered`, `ToolOutputGuardrailTripwireTriggered`,
and `InvalidToolInputError` all extend `AgentsError` (directly or transitively).

After construction, every one of these subclass instances reports the wrong
`.name`:

```js
new MaxTurnsExceededError('boom').name // → 'Error'   (current)
new UserError('boom').name              // → 'Error'   (current)
new ToolCallError('boom', cause).name   // → 'Error'   (current)
String(new UserError('boom'))           // → 'Error: boom'
```

The `.name` field is the standard JavaScript `Error.name` property — it is
what `Error.prototype.toString()` (and therefore `String(err)` and `err.stack`'s
first line) prefixes the message with. Because no constructor in the chain
sets `this.name`, every subclass inherits the default `'Error'` from
`Error.prototype`, masking the concrete error type in logs, stack traces, and
any string-formatted error output.

A visible symptom appears in the agent-tool error path: when an
`InvalidToolInputError` is wrapped by the tool runner and rendered to a
string, the resulting message reads

```
'An error occurred while running the tool. Please try again. Error: Error: Invalid JSON input for tool'
```

with `Error: Error:` doubled — the outer `Error: ` is a literal prefix and the
inner `Error:` comes from `String(invalidToolInputError)` because
`invalidToolInputError.name === 'Error'`. After the fix it should read

```
'An error occurred while running the tool. Please try again. Error: InvalidToolInputError: Invalid JSON input for tool'
```

## Required behavior

For every concrete subclass of `AgentsError` exported from
`@openai/agents-core`, an instance constructed with `new SubclassName(...)`
must satisfy:

- `instance.name === 'SubclassName'` (the exact subclass class name, as a
  string).
- `String(instance)` must start with `'<SubclassName>: '` — i.e. the
  `Error.prototype.toString()` representation reflects the concrete subclass.
- This must hold without modifying any subclass constructor — the abstract
  base class `AgentsError` should set the name once, and every direct or
  transitive subclass must inherit the correct value automatically (including
  subclasses such as `InvalidToolInputError` that extend `ModelBehaviorError`
  rather than `AgentsError` directly).

The list of subclasses whose `.name` must equal their class name includes
(but is not limited to):

- `MaxTurnsExceededError`
- `ModelBehaviorError`
- `UserError`
- `SystemError`
- `GuardrailExecutionError`
- `ToolCallError`
- `InputGuardrailTripwireTriggered`
- `OutputGuardrailTripwireTriggered`
- `ToolInputGuardrailTripwireTriggered`
- `ToolOutputGuardrailTripwireTriggered`
- `InvalidToolInputError`

## What to update

1. The fix lives in the abstract base class declared in
   `packages/agents-core/src/errors.ts`. Make a single, minimal change in the
   abstract constructor so that every concrete subclass inherits the correct
   `name` automatically — do not patch every subclass individually.
2. Update any existing test in `packages/agents-core/test/` whose assertion
   string was written against the buggy `Error: Error:` doubling so that it
   now matches the correctly-named subclass output.
3. Add a regression test under `packages/agents-core/test/errors.test.ts`
   that asserts on the `.name` of constructed subclass instances.
4. Add a changeset file under `.changeset/` describing the fix as a `patch`
   bump for `@openai/agents-core`. Follow the repository's existing changeset
   format (see `.changeset/README.md` and other files in that directory).

## Code Style Requirements

The repo's CI runs `pnpm lint` (ESLint with the project's config in
`eslint.config.mjs`) and a `tsc --noEmit` build-check; both must pass. Do not
introduce unused imports or `any` casts beyond what already exists in the
surrounding code. Follow the Prettier defaults already used in the file.

## Verification

The test harness runs from the repo root and validates:

- For every listed subclass, `new Subclass(...).name` equals the subclass's
  class name.
- `String(new UserError('boom', {}))` begins with `'UserError: '`.
- `String(new ToolCallError('boom', new Error('cause'), {}))` begins with
  `'ToolCallError: '`.
- `pnpm lint` and `pnpm -F @openai/agents-core build-check` succeed.
- The upstream `errors.test.ts` vitest suite passes.

You may need to rebuild the agents-core dist (e.g. `pnpm exec tsc-multi`) so
the runtime exports reflect your source change before the harness imports
`@openai/agents-core`.
