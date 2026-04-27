# Streamed final output leaks past output guardrails in `@openai/agents-core`

You are working in the OpenAI Agents JS monorepo at
`/workspace/openai-agents-js`. The fix lives somewhere in
`packages/agents-core` — finding it is part of the task.

## Symptom

When a streamed run reaches its final output and the run has output guardrails
configured, the runtime calls `runOutputGuardrails(...)` on the produced
output. If a guardrail's `tripwireTriggered` is `true`, the runtime is
expected to throw `OutputGuardrailTripwireTriggered` from
`StreamedRunResult.completed`.

It does throw — but the blocked output is also still observable via the
result's other accessors:

1. `result.state._currentStep?.type` is still `'next_step_final_output'`
   after the guardrail trips.
2. `result.finalOutput` returns the blocked text instead of `undefined`.
3. Reading `result.finalOutput` on a run that did not complete successfully
   normally logs a warning. Because the runtime mistakenly believes the run
   *did* reach its final output step, that warning is suppressed and the
   caller silently receives the blocked content.

In other words: `await result.completed` rejects with
`OutputGuardrailTripwireTriggered`, yet
`result.finalOutput` exposes the very content the guardrail just blocked.
Output that the guardrail *just refused* must not be readable through
`StreamedRunResult` after the failure.

## Expected behavior

After an output guardrail trips during a streamed run:

1. `await result.completed` rejects with `OutputGuardrailTripwireTriggered`
   (already correct — do not change this).
2. **Input persistence stays as it was.** Existing tests already assert that
   `saveStreamInputToSession` is called once and
   `saveStreamResultToSession` is *not* called; the fix must not regress
   that.
3. `result.state._currentStep?.type` must **not** be
   `'next_step_final_output'` after the failure — it must not look like the
   run reached its final-output step.
4. `result.finalOutput` must be `undefined`.
5. Because no completed result is available, reading `result.finalOutput`
   must trigger the standard warning emitted via `logger.warn` with the
   message:

   ```
   Accessed finalOutput before agent run is completed.
   ```

   (verbatim, including the trailing period).

## Scope

- The fix is contained to streaming-run handling in `@openai/agents-core`.
- Do **not** alter the non-streaming run loop's guardrail behavior — that
  loop is correct.
- Keep the change small and behavior-preserving for the success path: when
  no guardrail trips, `result.finalOutput` and the session persistence
  callbacks must still behave exactly as before.

## Repo conventions

This monorepo's `AGENTS.md` lists rules contributors must follow. The ones
that apply to this change:

- The streaming and non-streaming run loops should remain behaviorally
  aligned. If your fix would create a divergence, reconsider the approach.
- Comments must end with a period.
- Do not add a changeset; the verifier ignores `.changeset/` and the test
  harness does not require one for this task.

## Code Style Requirements

The verifier runs `pnpm -F @openai/agents-core run build-check`, which
type-checks both `src/**/*.ts` and `test/**/*.ts` with the package's
`tsconfig.test.json`. Any TypeScript error there will fail the task. Do not
introduce `any`-cast workarounds or disable rules in tsconfig.

## How the fix is verified

The verifier replays the existing streamed-output-guardrail scenario
(model emits `'PII: 123-456-7890'`, an output guardrail trips with reason
`'pii'`) and asserts items 3, 4, and 5 above on the resulting
`StreamedRunResult`. It also re-runs adjacent tests to ensure the success
path and input-guardrail behavior have not regressed.
