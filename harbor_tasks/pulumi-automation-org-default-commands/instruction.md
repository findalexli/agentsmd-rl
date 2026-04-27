# Add `org get-default` / `org set-default` to the Pulumi Automation API

You are working in the Pulumi monorepo (`pulumi/pulumi`). The repository is
checked out at `/workspace/pulumi`.

The Pulumi CLI exposes two commands for managing the *default organization*
the CLI uses for the current backend:

```text
pulumi org get-default              # prints the current default org to stdout
pulumi org set-default <org_name>   # sets the default org
```

The Pulumi Automation API — the programmatic SDK that wraps the CLI — already
exposes `WhoAmI`, `WhoAmIDetails`, etc. but **does not yet expose the
`org get-default` / `org set-default` commands**. Your job is to add these
methods to the Automation API in *both* the **Go SDK** (`sdk/go/auto/`) and
the **Python SDK** (`sdk/python/lib/pulumi/automation/`), mirroring the
shape and conventions of the existing methods.

## What you need to add

### Go SDK (`sdk/go/auto/`)

1. Two new methods on the `Workspace` *interface* (in `workspace.go`),
   placed immediately after the existing `WhoAmIDetails` method:

   - `OrgGetDefault(ctx context.Context) (string, error)` — returns the
     default organization for the current backend.
   - `OrgSetDefault(ctx context.Context, orgName string) error` — sets the
     default organization for the current backend.

2. Implementations of both methods on `*LocalWorkspace` (in
   `local_workspace.go`), placed near the existing `WhoAmI` /
   `WhoAmIDetails` implementations. They must shell out to the Pulumi CLI:

   - `OrgGetDefault` runs `pulumi org get-default` and returns stdout
     with surrounding whitespace stripped.
   - `OrgSetDefault` runs `pulumi org set-default <orgName>` and returns
     any error from the underlying command.

   Follow the error-wrapping convention used by the existing methods in
   the same file (e.g. `WhoAmI`, `WhoAmIDetails`).

### Python SDK (`sdk/python/lib/pulumi/automation/`)

1. Two new abstract methods on the `Workspace` base class (in
   `_workspace.py`), placed after the existing `who_am_i` abstract method.
   Both must be decorated with `@abstractmethod` and carry docstrings in
   the same style as neighbouring abstract methods:

   - `org_get_default(self) -> str`
   - `org_set_default(self, org_name: str) -> None`

2. Concrete implementations on `LocalWorkspace` (in `_local_workspace.py`),
   placed near the existing `who_am_i` implementation. They must call
   `self._run_pulumi_cmd_sync(...)`:

   - `org_get_default` invokes the CLI with the argument list
     `["org", "get-default"]` and returns `result.stdout.strip()`.
   - `org_set_default` invokes the CLI with the argument list
     `["org", "set-default", org_name]` and returns nothing (`None`).

## Behavioral contract (what the tests check)

The hidden test suite asserts the following behavior. Any implementation
that satisfies it is correct.

**Python `Workspace` (abstract base class):**

- `Workspace.org_get_default` exists and is marked with
  `@abstractmethod` (i.e. `Workspace.org_get_default.__isabstractmethod__`
  is `True`).
- `Workspace.org_set_default` exists and is marked with
  `@abstractmethod`.

**Python `LocalWorkspace`:**

- Calling `org_get_default()` invokes `self._run_pulumi_cmd_sync` *exactly
  once* with the argument list `["org", "get-default"]`, and returns the
  resulting `CommandResult.stdout` *with surrounding whitespace stripped*
  (so e.g. stdout `"  my-default-org \n"` produces the return value
  `"my-default-org"`).
- Calling `org_set_default(name)` invokes `self._run_pulumi_cmd_sync`
  *exactly once* with the argument list `["org", "set-default", name]`
  for any `name` value (the org name must be passed through verbatim, not
  hardcoded). The return value must be `None`.

**Go `Workspace` (interface):**

- The interface exposes the methods
  `OrgGetDefault(context.Context) (string, error)` and
  `OrgSetDefault(ctx context.Context, orgName string) error`. Consumer
  code that holds a `Workspace` value (not `*LocalWorkspace`) must be
  able to call both.

**Go `*LocalWorkspace`:**

- Calling `OrgGetDefault(ctx)` invokes the underlying `PulumiCommand.Run`
  with positional args `[]string{"org", "get-default"}` (no extra
  flags), and returns the trimmed stdout.
- Calling `OrgSetDefault(ctx, name)` invokes the underlying
  `PulumiCommand.Run` with positional args
  `[]string{"org", "set-default", name}` for any `name` string.

The Go tests use the existing `mockPulumiCommand` test helper from
`sdk/go/auto/local_workspace_test.go` (a stub `PulumiCommand` that
captures `args` and returns canned `stdout`/`stderr`/`exitCode`/`err`).
You may consult that helper to understand how the harness verifies args
and stdout-trimming.

## Repository conventions

This repo has top-level `AGENTS.md` (with `CLAUDE.md` redirecting to it)
and per-package `AGENTS.md` under `sdk/go/` and `sdk/python/`. Read them
before submitting. In particular:

- **Changelog entries are required for most PRs.** This change is a
  user-facing feature in two SDK scopes, so add a changelog YAML entry
  under `changelog/pending/` for each scope (`auto/python` and
  `sdk/go`). Use `mise exec -- make changelog` if available, otherwise
  follow the existing entries' format.
- **Do not make sweeping changes, refactor unrelated code, or add
  unnecessary abstractions.** The scope of this PR is just adding the
  two methods on each side.
- **Copyright headers for new files** should be stamped with the current
  year (only relevant if you add new source files — most agents won't
  need to).

## Code Style Requirements

- Go code should follow standard Go formatting (`gofmt`). The existing
  `Workspace` interface uses godoc comments above every method
  (`// MethodName ...`). Match that.
- Python code should follow the docstring style of the surrounding
  abstract methods on `Workspace` (one-line summary, `:param:` /
  `:returns:` lines).
- This PR does not require running the full repo lint, but new code
  should not introduce obvious style regressions.

## Testing your work

The hidden tests run inside a Docker image that ships with:

- The Pulumi repo cloned at `/workspace/pulumi` at the base commit.
- Go 1.24 with all `sdk/go` modules pre-downloaded.
- Python 3.12 with the Pulumi Python SDK installed in editable mode and
  `pytest` available.

You can manually verify your work with:

```bash
cd /workspace/pulumi/sdk/go && go build ./...
cd /workspace/pulumi && python3 -c "from pulumi.automation import LocalWorkspace, Workspace; print('ok')"
```

You do **not** need a real Pulumi Cloud login or Pulumi binary — the tests
verify behavior through stubs, not through a live backend.
