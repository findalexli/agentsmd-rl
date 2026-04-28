# Fix Error Subclass Name Reporting

The `AgentsError` base class and its subclasses in the `agents-core` package define the library's error types:

- `MaxTurnsExceededError`
- `ModelBehaviorError`
- `UserError`
- `InputGuardrailTripwireTriggered`
- `OutputGuardrailTripwireTriggered`
- `GuardrailExecutionError`
- `ToolCallError`
- `InvalidToolInputError` (extends `ModelBehaviorError`)
- `SystemError`

## The Bug

According to the ECMAScript specification, the `Error` constructor hardcodes `this.name` to the string `"Error"`. Subclasses are expected to override this to their own class name. The `AgentsError` base class does not do this, so every subclass instance reports `.name === "Error"` instead of the specific subclass name.

This means:

- `new MaxTurnsExceededError('Test error', {}).name` returns `"Error"` instead of `"MaxTurnsExceededError"`
- `new ModelBehaviorError('Test error', {}).name` returns `"Error"` instead of `"ModelBehaviorError"`
- `new UserError('Test error', {}).name` returns `"Error"` instead of `"UserError"`
- `new InputGuardrailTripwireTriggered('Test error', {}, {}).name` returns `"Error"` instead of `"InputGuardrailTripwireTriggered"`
- `new OutputGuardrailTripwireTriggered('Test error', {}, {}).name` returns `"Error"` instead of `"OutputGuardrailTripwireTriggered"`
- `new GuardrailExecutionError('Test error', new Error('cause'), {}).name` returns `"Error"` instead of `"GuardrailExecutionError"`
- `new ToolCallError('Test error', new Error('cause'), {}).name` returns `"Error"` instead of `"ToolCallError"`
- `InvalidToolInputError.toString()` produces `"Error: Invalid JSON input for tool"` instead of `"InvalidToolInputError: Invalid JSON input for tool"`

## Expected Behavior

Each `AgentsError` subclass instance must have its `.name` property equal to the class name string (e.g., `"MaxTurnsExceededError"`, `"ModelBehaviorError"`, `"UserError"`, etc.). This ensures that `toString()` and error logging reflect the concrete error type.

The `agents-core` package must build successfully (`pnpm -F agents-core build`) and pass type checking including test files (`pnpm -F agents-core build-check`).
