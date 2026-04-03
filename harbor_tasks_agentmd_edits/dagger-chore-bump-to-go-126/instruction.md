# Bump Go to 1.26 and add a maintenance skill

## Problem

The Dagger repository is pinned to Go 1.25.7 across several configuration files. Go 1.26 has been released and the project needs to be updated to use it.

Additionally, the Go version bump is a recurring chore that currently has no documented procedure. Each time it happens, someone has to remember which files to touch. The project uses a `skills/` directory for reusable agent skill documents (see existing skills like `skills/cache-expert/` and `skills/dagger-codegen/` for examples).

## What needs to happen

1. **Update the Go version to 1.26** everywhere it's referenced:
   - The `GolangVersion` constant in `engine/distconsts/consts.go`
   - The `+default` annotation for the `version` parameter in `toolchains/go/main.go`

2. **Fix the Alpine package name separator**: In `toolchains/go/main.go`, the Go Alpine package is installed using the `~` version separator (e.g. `go~1.25.7`). Starting with Go 1.26, Alpine uses `go-` as the separator. Update this accordingly.

3. **Skip arm/windows cross-compilation**: In `toolchains/cli-dev/publish.go`, the `goreleaserBinaries` function skips building for `arm` on `darwin`. The `arm` + `windows` combination should also be skipped.

4. **Create a `dagger-chores` skill**: Add a new skill file at `skills/dagger-chores/SKILL.md` that documents repeatable maintenance chores. It should follow the same frontmatter and structure conventions as the existing skills. At minimum it should cover:
   - A Go version bump checklist referencing the specific files and constants to update
   - A procedure for regenerating generated files using the `dagger` CLI

## Files to look at

- `engine/distconsts/consts.go` — version constants
- `toolchains/go/main.go` — Go toolchain defaults and Alpine package installation
- `toolchains/cli-dev/publish.go` — cross-compilation matrix
- `skills/` — existing skill documents for structure reference
