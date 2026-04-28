# Add .github/copilot-instructions.md for Copilot coding agent onboarding

Source: [dapr/dapr#9534](https://github.com/dapr/dapr/pull/9534)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Adds agent onboarding instructions so Copilot coding agents can work efficiently in this repo without needing to rediscover conventions through trial and error.

## What's included

- **Build**: `make build`, direct `go build -tags=allcomponents`, cross-compile, and sidecar flavor build tags (`allcomponents` / `stablecomponents`)
- **Testing**: Unit (`make test`, `go test -tags=unit,allcomponents`), integration (`make test-integration`, requires `CGO_ENABLED=1`), and E2E (Kubernetes/CI only) — with `gotestsum` install instructions
- **Linting**: `make lint` with golangci-lint **v1.64.6** (exact version required); `make lint-fix` for auto-fixable issues
- **Code conventions**: Apache 2.0 license header required on every file, `goimports` local prefix `github.com/dapr/`, testify `require` vs `assert` usage, `dapr/kit/logger` pattern
- **Protobuf**: `make gen-proto`; never manually edit `pkg/proto/`
- **DCO**: `git commit -s` required on every commit
- **CI failure guide**: Common causes (`go.mod` drift, missing license headers, wrong lint version) with exact remediation commands
- **Directory map**: Annotated layout of `cmd/`, `pkg/`, `dapr/proto/`, `tests/`

## Checklist

Please make sure you've completed the relevant tasks for this PR, out of the following list:

- [ ] Code compiles correctly
- [ ] Created/updated tests
- [ ] Unit tests passing
- [ ] End-to-end tests passing
- [ ] Extended the documentation / Created issue in the <https://github.com/dapr/docs/> repo: dapr/doc

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
