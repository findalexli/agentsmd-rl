# [Agentic Skills]: Update documentation skill

Source: [openvinotoolkit/openvino.genai#3552](https://github.com/openvinotoolkit/openvino.genai/pull/3552)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/update-docs/SKILL.md`

## What to add / change

<!-- Keep your pull requests (PRs) as atomic as possible. That increases the likelihood that an individual PR won't be stuck because of adjacent problems, merge conflicts, or code review.
Your merged PR is going to appear in the automatically generated release notes on GitHub. So the clearer the title the better. -->
## Description
<!-- Please include a summary of the change. Also include relevant motivation and context. -->

Adds update-docs skill.

## Checklist:
- [x] This PR follows [GenAI Contributing guidelines](https://github.com/openvinotoolkit/openvino.genai?tab=contributing-ov-file#contributing). <!-- Always follow them. If there are deviations, explain what and why. -->
- [NA] Tests have been updated or added to cover the new code. <!-- Specify exactly which tests were added or updated. If the change isn't maintenance related, update the tests at https://github.com/openvinotoolkit/openvino.genai/tree/master/tests or explain in the description why the tests don't need an update. -->
- [x] This PR fully addresses the ticket. <!--- If not, explain clearly what is covered and what is not. If follow-up pull requests are needed, specify in the description. -->
- [NA] I have made corresponding changes to the documentation. <!-- Run github.com/\<username>/openvino.genai/actions/workflows/deploy_gh_pages.yml on your fork with your branch as a parameter to deploy a test version with the updated content. Replace this comment with the link to the built docs. If the d

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
