# Add comprehensive linting instructions to AGENTS.md

Source: [cschleiden/go-workflows#452](https://github.com/cschleiden/go-workflows/pull/452)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

The AGENTS.md file had minimal linting documentation that only showed a workaround approach. This updates it with complete instructions for running the project's linter.

### Changes

- **Linting section**: Added three approaches (preferred `make lint`, manual with correct v2.4.0 version, and workaround for analyzer issues)
- **Version specification**: Documented that golangci-lint v2.4.0 is required (v1.x incompatible with `.golangci.yml`)
- **Available linters**: Listed configured linters by category (code quality, bug detection, style, testing)
- **Pre-commit validation**: Updated from vague "Basic Linting" to specific commands and added formatting step

### Usage

```bash
# Recommended approach
make lint

# Or manually with correct version
go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.4.0
golangci-lint run --timeout=5m
```

<!-- START COPILOT CODING AGENT SUFFIX -->



<details>

<summary>Original prompt</summary>

> Add instructions on running the linter to AGENTS.md


</details>



<!-- START COPILOT CODING AGENT TIPS -->
---

💬 We'd love your input! Share your thoughts on Copilot coding agent in our [2 minute survey](https://gh.io/copilot-coding-agent-survey).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
