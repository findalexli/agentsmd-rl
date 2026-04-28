# ✨ Add Copilot instructions for repository

Source: [argoproj-labs/gitops-promoter#579](https://github.com/argoproj-labs/gitops-promoter/pull/579)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This PR adds comprehensive GitHub Copilot instructions to help the coding agent provide more accurate and context-aware suggestions when working on this repository.

## Changes

Created `.github/copilot-instructions.md` with detailed guidance covering:

### Project Context
- Overview of GitOps Promoter as a Kubernetes operator
- Key technologies: Go 1.24+, TypeScript/React, Kubernetes, Argo CD
- SCM provider support (GitHub, GitLab, Forgejo/Codeberg)

### Development Workflow
- Prerequisites and setup requirements
- Build commands for backend (`make build`, `make test`) and UI (`make build-dashboard`, `make build-extension`)
- Testing commands including parallel test execution
- Linting and code quality commands

### Code Standards
- Go code style (go fmt, golangci-lint rules)
- TypeScript/React conventions (ESLint, type-checking)
- Testing patterns with Ginkgo/Gomega

### Architecture &amp; Structure
- Directory layout and purpose of key directories (`api/`, `internal/`, `ui/`)
- Complete CRD list including PromotionStrategy, GitRepository, ScmProvider, ClusterScmProvider, PullRequest, CommitStatus, ArgoCDCommitStatus, ChangeTransferPolicy, RevertCommit, and ControllerConfiguration
- Controller patterns and relationships between resources
- Generated files that should not be manually edited

### Common Patterns
- Controller-runtime patterns for Kubernetes operators
- Structured logging with `logr`
- Git operations and SCM provider interfaces
- Error handling and retry logic


## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
