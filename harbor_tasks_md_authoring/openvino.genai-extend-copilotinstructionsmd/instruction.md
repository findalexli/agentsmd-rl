# Extend copilot-instructions.md

Source: [openvinotoolkit/openvino.genai#3377](https://github.com/openvinotoolkit/openvino.genai/pull/3377)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Description
Enforce pull_request_template.md

## Checklist:
- [x] This PR follows [GenAI Contributing guidelines](https://github.com/openvinotoolkit/openvino.genai?tab=contributing-ov-file#contributing). <!-- Always follow them. If there are deviations, explain what and why. -->
- N/A Tests have been updated or added to cover the new code. <!-- Specify exactly which tests were added or updated. If the change isn't maintenance related, update the tests at https://github.com/openvinotoolkit/openvino.genai/tree/master/tests or explain in the description why the tests don't need an update. -->
- N/A This PR fully addresses the ticket. <!--- If not, explain clearly what is covered and what is not. If follow-up pull requests are needed, specify in the description. -->
- N/A I have made corresponding changes to the documentation. <!-- Run github.com/\<username>/openvino.genai/actions/workflows/deploy_gh_pages.yml on your fork with your branch as a parameter to deploy a test version with the updated content. Replace this comment with the link to the built docs. If the documentation is updated in a separate PR, clearly specify it. -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
