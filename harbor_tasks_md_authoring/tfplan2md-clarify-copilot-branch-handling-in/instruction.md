# Clarify `copilot/*` branch handling in workflow guidance

Source: [oocx/tfplan2md#601](https://github.com/oocx/tfplan2md/pull/601)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`
- `docs/agents.md`

## What to add / change

### Summary

Clarifies that GitHub-managed coding-agent PR branches may use the `copilot/*` prefix, and that this does not change the underlying `feature/`, `fix/`, `workflow/`, or `website/` work-item convention.

- **Branch naming rules**
  - Added an explicit `copilot/*` exception to `/docs/agents.md` under **Branch Naming Conventions**
  - Makes clear that `copilot/*` is an execution-context detail for the PR, not a workflow violation

- **Coding-agent instructions**
  - Updated `/.github/copilot-instructions.md` to tell agents to stay on GitHub-managed `copilot/*` branches
  - Clarifies that work-item folders and workflow type still follow the documented repository conventions

Example of the clarified guidance:

```md
**GitHub Copilot PR branch exception:** When GitHub creates a coding-agent pull request, it may place the work on an auto-generated `copilot/*` branch. That branch name is an execution-context detail for the existing PR, not a replacement for the underlying `feature/`, `fix/`, `workflow/`, or `website/` work-item convention.
```

---

### Checklist

- [ ] All checks pass (build, test, lint)
- [x] Commits follow Conventional Commits
- [x] PR description uses the standard template (Problem / Change / Verification)

**Merge method:** Use **Rebase and merge** to maintain a linear history. The repository enforces rebase-only merges by default.

**Create & merge guidance:** Use `scripts/pr-github.sh create` to create PRs, and `scripts/pr-github.sh create-and-mer

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
