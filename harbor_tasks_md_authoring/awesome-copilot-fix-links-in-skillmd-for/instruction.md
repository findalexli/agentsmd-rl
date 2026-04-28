# Fix links in SKILL.md for project template instructions

Source: [github/awesome-copilot#1470](https://github.com/github/awesome-copilot/pull/1470)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/create-spring-boot-java-project/SKILL.md`
- `skills/create-spring-boot-kotlin-project/SKILL.md`

## What to add / change

## Pull Request Checklist

- [x] I have read and followed the [CONTRIBUTING.md](https://github.com/github/awesome-copilot/blob/main/CONTRIBUTING.md) guidelines.
- [x] I have read and followed the [Guidance for submissions involving paid services](https://github.com/github/awesome-copilot/discussions/968).
- [ ] My contribution adds a new instruction, prompt, agent, skill, or workflow file in the correct directory.
- [ ] The file follows the required naming convention.
- [ ] The content is clearly structured and follows the example format.
- [ ] I have tested my instructions, prompt, agent, skill, or workflow with GitHub Copilot.
- [ ] I have run `npm start` and verified that `README.md` is up to date.
- [x] I am targeting the `staged` branch for this pull request.

---

## Description

<!-- Briefly describe your contribution and its purpose. Include any relevant context or usage notes. -->

---

## Type of Contribution

- [ ] New instruction file.
- [ ] New prompt file.
- [ ] New agent file.
- [ ] New plugin.
- [ ] New skill file.
- [ ] New agentic workflow.
- [x] Update to existing instruction, prompt, agent, plugin, skill, or workflow.
- [ ] Other (please specify):

---

## Additional Notes

<!-- Add any additional information or context for reviewers here. -->

---

By submitting this pull request, I confirm that my contribution abides by the [Code of Conduct](../CODE_OF_CONDUCT.md) and will be licensed under the MIT License.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
