# Distinguish "user cancelled" from "succeeded" in `compose publish`

You are working on Docker Compose (Go module `github.com/docker/compose/v5`,
checked out at `/workspace/compose`). The CLI command `docker compose
publish` packages a Compose project as an OCI artifact and pushes it to a
registry.

Before publishing, the implementation runs a set of pre-checks that may
require interactive confirmation:

1. **Bind-mount declarations.** If any service declares `bind` volumes,
   the user is shown the message
   `"you are about to publish bind mounts declaration within your OCI
   artifact."` followed by the list of bind sources, and is asked
   `"Are you ok to publish these bind mount declarations?"`.
2. **Sensitive data in env files.** If the DefangLabs secret detector
   flags any secret (e.g., an `AWS_SECRET_ACCESS_KEY=...` line in a file
   referenced by `env_file:`), the user is shown
   `"you are about to publish sensitive data within your OCI artifact."`
   and is asked `"Are you ok to publish these sensitive data?"`.

Either prompt accepts a yes/no answer. The shared confirmation routine
returns `(accept bool, err error)` from these prompts.

## The bug

If the user answers **no** to either prompt, the publish operation is
correctly aborted — but the function in charge of orchestrating the
publish returns `nil`. To callers (and to shell scripts checking the
process exit code) this is **indistinguishable from a successful
publish**: both yield exit status `0`. As a result, automation that runs
`docker compose publish` cannot tell whether the artifact was actually
pushed or whether the user bailed out at the confirmation prompt.

The package `github.com/docker/compose/v5/pkg/api` already defines a
sentinel error for this exact situation:

```go
// ErrCanceled is returned when the command was canceled by user
ErrCanceled = errors.New("canceled")
```

The CLI also has a `IsErrCanceled(err error) bool` helper built on top
of `errors.Is`, and elsewhere in the codebase a user-cancelled run is
expected to translate into shell exit code **130**.

## What to fix

The orchestrating publish function in `pkg/compose` (the unexported
method called by `composeService.Publish`) currently returns a bare
`nil` whenever pre-checks report that the user declined. Make it return
the existing `api.ErrCanceled` sentinel instead, so that:

- `errors.Is(err, api.ErrCanceled)` is `true` after a declined prompt.
- The CLI surfaces a non-zero exit code (the existing `IsErrCanceled`
  → exit code 130 path) on user decline.
- The behavior on the **accept** path is unchanged: a successful
  publish must still return `nil`, and `errors.Is(returned, api.ErrCanceled)`
  must remain `false` in that case.

Both decline paths (bind-mount decline and sensitive-data decline) must
be covered by the same change — they share a single pre-check
short-circuit. Do not introduce a new sentinel; reuse `api.ErrCanceled`.

## Constraints

- Do not change the signature or visibility of any exported function.
- Do not change the prompt wording, the order of pre-checks, or the
  conditions under which a prompt is shown.
- Do not modify `pkg/compose/publish_test.go` or any other test file —
  the grading harness adds its own tests against the public behavior.

## Code Style Requirements

This repository enforces strict Go style rules (see `CLAUDE.md` and
`.golangci.yml`). In particular, your change must:

- Pass `go vet ./pkg/compose/...` cleanly.
- Pass `golangci-lint run --build-tags "e2e" ./...` cleanly
  (`gofumpt` formatting, `gci` import order: stdlib → third-party →
  `github.com/docker/compose/v5/...`).
- Not introduce any of the banned imports: `io/ioutil`,
  `github.com/pkg/errors`, `gopkg.in/yaml.v2`,
  `golang.org/x/exp/maps`, `golang.org/x/exp/slices`.
- Use `github.com/containerd/errdefs` if you need errdefs (never
  `github.com/docker/docker/errdefs`).
- If you add any tests, use `t.Context()` rather than
  `context.Background()` / `context.TODO()`.
