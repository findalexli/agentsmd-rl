# chore: add copilot instructions

Source: [SAP/terraform-provider-btp#1225](https://github.com/SAP/terraform-provider-btp/pull/1225)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Purpose
<!-- Describe the intention of the changes being proposed. What problem does it solve or functionality does it add? -->
- Add GH Copilot instructions to project under `.github/copilot-instructions.md`
- Use as baseline https://github.com/github/awesome-copilot/blob/main/instructions/go.instructions.md
- Enhance with project-specific guidelines created via GH Copilot (agent mode GPT-5)
- Prompt:

   ```bash
   I would like to add copilot-instructions to this repository. The repository is a Terraform provider for SAP BTP using the Terraform plugin framework

   Can you help with creating a first version of the .github/copilot-instructions.md file.

   The file should contain the following information:

    - Provide an overview of the project including its purpose, goals, and any relevant background information.
    - Include the folder structure of the repository, including any important directories or files that are relevant to the project.
    - Specify the coding standards and conventions that should be followed, such as naming conventions, formatting rules, and best practices. The project is A Go project
    - Include any specific tools, libraries, or frameworks that are used in the project
   ```

## Does this introduce a breaking change?
<!-- Mark one with an "x". -->
```
[ ] Yes
[X] No
```

## Pull Request Type

What kind of change does this Pull Request introduce?
<!-- Please check the one that applies to this PR using "X". -->
```
[ ] Bugfix
[ ] Feature
[ ]

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
