# Add Guidance for GitHub Actions Version Pinning

The file `AGENTS.md` at the root of this repository is a contributor guide that
tells coding agents how to work in this codebase. It is currently missing
guidance about checking whether referenced GitHub Actions are up-to-date.

When a contributor edits a `.github/workflows/*.yml` file and references an
official GitHub Action (such as `actions/checkout` or `actions/setup-node`),
the version pin might be stale. The AGENTS.md should remind contributors to
check that they are using the latest stable major version of any official
action they reference.

## What to do

Add a short, actionable tip to the "Tips for Navigating the Repo" section at
the bottom of `AGENTS.md`. The tip should tell contributors who edit GitHub
Actions workflows to web-search for the latest stable major version of any
official action before changing or adding a version pin.

The tip should be a bullet point at the end of the existing list of tips,
matching the style and tone of the other entries in that section.

## Evaluation

Your changes will be checked by looking for two key phrases in the updated
`AGENTS.md`:

- "web-search for the latest stable major versions of official actions"
- "before updating version pins"

If both phrases are present, the task passes.
