# Parallelize the code-change-verification skill

The repository at `/workspace/openai-agents-js` ships a "code-change-verification" skill under `.agents/skills/code-change-verification/` that contributors run before marking work complete. Today the skill is implemented twice — once as a POSIX shell script and once as a PowerShell script — and both runners execute six pnpm commands strictly sequentially:

```
pnpm i
pnpm build
pnpm -r build-check
pnpm -r -F "@openai/*" dist:check
pnpm lint
pnpm test
```

The first two commands (`pnpm i`, `pnpm build`) must run in order because every later step depends on freshly installed deps and a fresh build. The remaining four (`build-check`, `dist:check`, `lint`, `test`) are independent of one another but are still being run sequentially, so a clean run takes the sum of all four.

Replace this with a single shared Node-based runner so that:

1. **Install and build remain sequential barriers.** `pnpm i` runs first, then `pnpm build`. If either fails the runner stops and exits with that step's exit code; no validation steps are started.

2. **The four validation steps run in parallel.** `pnpm -r build-check`, `pnpm -r -F "@openai/*" dist:check`, `pnpm lint`, and `pnpm test` are spawned concurrently after `pnpm build` completes successfully.

3. **Failures are fail-fast.** If any one parallel step exits non-zero, the runner must terminate the still-running parallel processes promptly and exit with the failed step's exit code. Surviving steps must not be allowed to keep running for their natural duration.

4. **Streamed output is disambiguated.** Because four steps now write to the same stdout/stderr, every line emitted by a step must be prefixed with `[<label>] ` where `<label>` is a short name for that step (the labels for the validation steps are `build-check`, `dist-check`, `lint`, `test`; the sequential steps are labelled `install` and `build`). The prefix lets a reader follow each step's output even when the streams are interleaved.

5. **The shell wrappers delegate.** Both `scripts/run.sh` and `scripts/run.ps1` should become thin wrappers that invoke the new Node runner and forward their arguments to it (so `bash scripts/run.sh --help` and `node scripts/run.mjs --help` behave the same).

6. **`--help` prints usage.** Invoking the Node runner with `--help` must print a short usage banner that includes the string `code-change-verification` and exit 0 without running any pnpm command.

7. **The runner is importable as a library.** From another ESM module it must be possible to do:

   ```js
   import { createDefaultPlan, runVerification } from "./run.mjs";
   ```

   - `createDefaultPlan()` returns an object `{ sequentialSteps, parallelSteps }`. Each step has at minimum `{ label, command, args, commandText }`. The `commandText` field is the human-readable string shown in the runner's "Running …" log line; for the default plan the `commandText` values are exactly `"pnpm i"`, `"pnpm build"`, `"pnpm -r build-check"`, `"pnpm -r -F @openai/* dist:check"`, `"pnpm lint"`, and `"pnpm test"`. Sequential labels are `install`, `build`; parallel labels are `build-check`, `dist-check`, `lint`, `test`.
   - `runVerification(options)` runs the plan and returns a Promise that resolves to a numeric exit code (0 on success, the failed step's exit code otherwise). It must accept an `options` object whose recognized keys include at least `sequentialSteps`, `parallelSteps`, and `repoRoot`, all optional and defaulting to the values produced by `createDefaultPlan()` and a git-toplevel lookup, respectively. Tests will pass `sequentialSteps`/`parallelSteps` arrays of `{ label, command, args, commandText }` to verify behavior without invoking pnpm.

Update `.agents/skills/code-change-verification/SKILL.md` and the root `AGENTS.md` so the documented run order reflects the new "two sequential barriers, then a parallel validation phase" execution model — readers must not be left believing that all six commands still run in strict sequence.

## Files of interest

- `.agents/skills/code-change-verification/scripts/run.sh`
- `.agents/skills/code-change-verification/scripts/run.ps1`
- `.agents/skills/code-change-verification/scripts/run.mjs` (does not exist yet)
- `.agents/skills/code-change-verification/SKILL.md`
- `AGENTS.md`

## Code Style Requirements

- The file added under `scripts/run.mjs` must be valid ESM JavaScript that parses cleanly with `node --check`.
- Per `AGENTS.md`, comments end with a period.
