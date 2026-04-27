# Reduce token usage of PRQL's test/build output

You are working on the [PRQL](https://github.com/PRQL/prql) repository
(a Rust workspace built around `prqlc`). The repo is checked out at
`/workspace/prql`.

When an agent (or developer) runs the project's test suite via the
top-level `Taskfile.yaml`, the output is far longer than it needs to be:
about **1128 lines (~9k tokens)** for a passing run, dominated by
`cargo build` compilation chatter and per-test PASS lines from
`nextest`. The point of this task is to **shrink that output without
losing any signal when something fails** — passes should be quiet,
failures should still show full diagnostics.

You should change two things:

## 1. `Taskfile.yaml` — quiet down cargo and nextest

The `Taskfile.yaml` at the repo root drives all build/test commands.
Two tasks need to become quieter:

- **`build-all`**: every `cargo build …` invocation in this task,
  *and* the `cargo doc …` invocation, should pass cargo's `--quiet`
  flag so that compiler progress is suppressed when the build succeeds.
- **`build-each-crate`**: this task contains a templated
  `cargo build … -p {{ . }}` line that is run once per workspace
  crate; that template line also needs `--quiet`.
- **`test-rust`**: this task runs the Rust test suite under
  [`cargo-nextest`](https://nexte.st/). Configure it via task-level
  environment variables so that:
  - `NEXTEST_STATUS_LEVEL` is `fail` (only failing tests are printed
    while the run is in progress; passes are not), and
  - `NEXTEST_FINAL_STATUS_LEVEL` is `slow` (the run summary still
    surfaces unusually slow tests).

  These are real environment variables understood by nextest — see the
  [nextest configuration docs](https://nexte.st/docs/configuration/#environment-variables).
  Add them in an `env:` block on the `test-rust` task itself, *not*
  globally, so they only apply when that task runs.

Do not change which commands run or in what order — only their
verbosity. Failures must still emit full output. Behavior on the test
runner side (e.g. `cargo insta test --accept …`) must be preserved.

## 2. `CLAUDE.md` — document the new workflow

`CLAUDE.md` at the repo root is the agent-instruction file. It
currently has a single `## Tests` section that mixes "how to run a
focused test" with "how to run everything". Reorganise the top of the
file so it explicitly distinguishes two phases of the development
loop:

- An **inner loop** — fast, focused commands the agent should reach
  for during iteration on a specific change (e.g. running the linter,
  running a single integration test, running the unit tests for one
  module).
- An **outer loop** — the comprehensive, run-everything command
  (`task test-all`) that should be run before handing back to the
  user.

Use the literal headings **"Inner loop"** and **"Outer loop"** so the
distinction is obvious. After the two loop blocks, briefly document
that the test suite is configured to minimize token usage — calling
out both the **nextest** status-level filtering and the cargo
`--quiet` flag — so a future reader understands why the output is
quieter than the cargo defaults.

The existing guidance on `cargo insta`, inline snapshots
(`insta::assert_snapshot!(result, @"…")`), and `task test-all` should
be preserved. The reorganised `## Tests` section should still appear
below the workflow content.

## Summary of literals the tests look for

To make the verifier deterministic, the changes must use these exact
strings:

- The cargo flag is spelled **`--quiet`**.
- The nextest env var values are **`fail`** and **`slow`**, on keys
  **`NEXTEST_STATUS_LEVEL`** and **`NEXTEST_FINAL_STATUS_LEVEL`**.
- `CLAUDE.md` mentions the words **`Inner loop`** and **`Outer loop`**,
  the word **`nextest`**, and the literal **`--quiet`**.

Do not introduce other behavioral changes (no version bumps, no test
deletions, no refactoring of unrelated tasks).
