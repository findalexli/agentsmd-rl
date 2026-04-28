# 🌱 Enhance AGENTS.md for Kubebuilder repo

Source: [kubernetes-sigs/kubebuilder#5296](https://github.com/kubernetes-sigs/kubebuilder/pull/5296)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

<!--

Hiya!  Welcome to Kubebuilder!  For a smooth PR process, please ensure
that you include the following information:

* a description of the change
* the motivation for the change
* what issue it fixes, if any, in GitHub syntax (e.g. Fixes #XYZ)

Both the description and motivation may reference other issues and PRs,
but should be mostly understandable without following the links (e.g. when
reading the git commit log).

Please don't @-mention people in PR or commit messages (do so in an
additional comment).

please add an icon to the title of this PR depending on the type:

- ⚠ (:warning:): breaking
- ✨ (:sparkles:): new non-breaking feature
- 🐛 (:bug:): bugfix
- 📖 (:book:): documentation
- 🌱 (:seedling:): infrastructure/other

See https://sigs.k8s.io/kubebuilder-release-tools for more information.

**PLEASE REMOVE THIS COMMENT BLOCK BEFORE SUBMITTING THE PR** (the bits
between the arrows)

-->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
