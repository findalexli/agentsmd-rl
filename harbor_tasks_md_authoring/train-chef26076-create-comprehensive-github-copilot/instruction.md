# CHEF-26076: Create comprehensive GitHub Copilot instructions 

Source: [inspec/train#805](https://github.com/inspec/train/pull/805)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

… Train repository

- Add complete copilot-instructions.md with Train-specific guidelines
- Include JIRA integration workflow with atlassian-mcp-server
- Document testing requirements with >80% coverage mandate
- Add prompt-based workflow with explicit confirmations
- Include GitHub CLI workflow and PR creation standards
- Document Train transport development and plugin architecture
- Add comprehensive testing, linting, and documentation requirements

<!--- Provide a short summary of your changes in the Title above -->

## Description
<!--- Describe your changes in detail, what problems does it solve? -->

## Related Issue
<!--- If you are suggesting a new feature or change, please create an issue first -->
<!--- Please link to the issue, discourse, or stackoverflow here: -->

## Types of changes
<!--- What types of changes does your code introduce? Put an `x` in all the boxes that apply: -->
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New content (non-breaking change)
- [ ] Breaking change (a content change which would break existing functionality or processes)

## Checklist:
<!--- Go over all the following points, and put an `x` in all the boxes that apply. -->
<!--- If you're unsure about any of these, don't hesitate to ask. We're here to help! -->
- [ ] I have read the **CONTRIBUTING** document.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
