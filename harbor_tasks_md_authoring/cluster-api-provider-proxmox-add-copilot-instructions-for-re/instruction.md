# Add Copilot instructions for repository context

Source: [ionos-cloud/cluster-api-provider-proxmox#631](https://github.com/ionos-cloud/cluster-api-provider-proxmox/pull/631)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Adds `.github/copilot-instructions.md` to provide Copilot coding agents with repository-specific context and development workflows.

## Changes

- **Project context**: Go 1.25.0, Kubebuilder v4, Cluster API v1.10.4 provider for Proxmox VE
- **Repository structure**: API definitions (`api/v1alpha1/`), controllers (`internal/controller/`), shared packages (`pkg/`), kustomize configs (`config/`)
- **Development workflow**:
  - `make verify` - validates generated files and modules (run before committing)
  - `make test WHAT=./pkg/...` - runs unit tests with envtest
  - `make manifests generate` - regenerates CRDs and DeepCopy methods after API changes
  - `./hack/start-capi-tilt.sh` - sets up hot-reload development environment
- **CI pipeline**: test.yml (verify + test + SonarQube), lint.yml (golangci-lint, yamllint, actionlint), e2e.yml
- **Testing conventions**: testify/gomega assertions, mockery-generated mocks, e2e tests require Proxmox instance

File is 147 lines (~5KB), within recommended 2-page limit for Copilot instructions.

> [!WARNING]
>
> <details>
> <summary>Firewall rules blocked me from connecting to one or more addresses (expand for details)</summary>
>
> #### I tried to connect to the following addresses, but was blocked by firewall rules:
>
> - `gh.io`
>   - Triggering command: `/home/REDACTED/work/_temp/ghcca-node/node/bin/node /home/REDACTED/work/_temp/ghcca-node/node/bin/node --enable-source-maps /home/REDACTED/work/_temp/copilot-developer-action-main/dist/in

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
