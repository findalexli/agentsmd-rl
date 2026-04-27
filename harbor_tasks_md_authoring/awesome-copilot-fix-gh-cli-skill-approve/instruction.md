# Fix gh cli skill approve PR command example

Source: [github/awesome-copilot#667](https://github.com/github/awesome-copilot/pull/667)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/gh-cli/SKILL.md`

## What to add / change

## Pull Request Checklist

- [x] I have read and followed the [CONTRIBUTING.md](https://github.com/github/awesome-copilot/blob/main/CONTRIBUTING.md) guidelines.
- [ ] My contribution adds a new instruction, prompt, agent, or skill file in the correct directory.
- [ ] The file follows the required naming convention.
- [ ] The content is clearly structured and follows the example format.
- [ ] I have tested my instructions, prompt, agent, or skill with GitHub Copilot.
- [ ] I have run `npm start` and verified that `README.md` is up to date.

---

## Description

<!-- Briefly describe your contribution and its purpose. Include any relevant context or usage notes. -->
Line 1154 appears to be a continuation of the previous command but is formatted incorrectly. The --approve-body flag should be part of the complete command on line 1152-1153, not a standalone line. This will cause syntax errors if copied as-is.

---

## Type of Contribution

- [ ] New instruction file.
- [ ] New prompt file.
- [ ] New agent file.
- [ ] New collection file.
- [ ] New skill file.
- [x] Update to existing instruction, prompt, agent, collection or skill.
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
