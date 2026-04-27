# Update `MaxBreadcrumbs` behavior in sentry-go

You are working in the `sentry-go` SDK repository (Go module
`github.com/getsentry/sentry-go`). The repository is checked out at
`/workspace/sentry-go`.

## What is broken / what to change

The SDK currently bounds the number of breadcrumbs that a `Hub` will keep on
its `Scope` in two ways that are out of sync with other Sentry SDKs:

1. **Hard ceiling.** When a user constructs a client with
   `ClientOptions{MaxBreadcrumbs: N}` and `N` is greater than 100, the SDK
   silently clamps the limit to 100. Concretely: with `MaxBreadcrumbs = 500`
   and 600 calls to `hub.AddBreadcrumb(...)`, only 100 breadcrumbs end up on
   the scope. There must be **no upper bound** imposed by the SDK — the user's
   configured value must be honored exactly. After 600 `AddBreadcrumb` calls
   with `MaxBreadcrumbs = 500`, the scope must contain 500 breadcrumbs.

2. **Default is too small.** When `ClientOptions{}` leaves `MaxBreadcrumbs`
   at its zero value, the SDK falls back to its built-in default. That default
   today produces a scope of length 30 after many `AddBreadcrumb` calls. The
   default must instead produce a scope of length **100**. After 150
   `AddBreadcrumb` calls with the default options, the scope must contain
   exactly 100 breadcrumbs.

Both of these limits are expressed as package-level constants in the `sentry`
package. The SDK also calls `Scope.AddBreadcrumb` from one code path
(when `Hub.AddBreadcrumb` is invoked with no client bound) using a
breadcrumb-limit constant — that call site must continue to compile and to
yield the new defaults consistent with item 2.

The behavior is exercised through the public API:

```go
client, _ := sentry.NewClient(sentry.ClientOptions{MaxBreadcrumbs: N})
hub := sentry.NewHub(client, sentry.NewScope())
for i := 0; i < M; i++ {
    hub.AddBreadcrumb(&sentry.Breadcrumb{Message: "x"}, nil)
}
// len(scope.breadcrumbs) must equal min(N, M) — no other ceiling.
```

The pre-existing test `TestAddBreadcrumbShouldNeverExceedMaxBreadcrumbsConst`
in `hub_test.go` encodes the *old* (buggy) clamping behavior and is no longer
correct; it must be removed (or updated) so the test suite passes.

## CHANGELOG

Add a release entry for **0.36.0** to `CHANGELOG.md` describing this as a
breaking change. The repository's changelog conventions
(`.cursor/rules/changelog.mdc`) require:

- A new top-level section `## 0.36.0`.
- A `### Breaking Changes` subsection inside it.
- An entry in that subsection mentioning the `MaxBreadcrumbs` option.
- A pull-request reference using the exact format
  `([#1106](https://github.com/getsentry/sentry-go/pull/1106))`.

## Acceptance

- `go build ./...` succeeds.
- `go vet .` succeeds in the root package.
- The full root-package `go test` suite passes — in particular all
  `TestAddBreadcrumb*`, `TestScopeParentChangedInheritance`,
  `TestScopeChildOverrideInheritance`, and `TestClearAndReconfigure` cases.
- A user-level program that sets `MaxBreadcrumbs: 500` and calls
  `AddBreadcrumb` 600 times observes 500 breadcrumbs on the scope (not 100).
- A user-level program with default `ClientOptions{}` that calls
  `AddBreadcrumb` 150 times observes 100 breadcrumbs on the scope (not 30).
