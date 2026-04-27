# Add author credits skills

Source: [github/awesome-copilot#1379](https://github.com/github/awesome-copilot/pull/1379)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/gsap-framer-scroll-animation/SKILL.md`
- `skills/premium-frontend-ui/SKILL.md`

## What to add / change

## Pull Request Checklist

- [x] I have read and followed the [CONTRIBUTING.md](https://github.com/github/awesome-copilot/blob/main/CONTRIBUTING.md) guidelines.
- [x] I have read and followed the [Guidance for submissions involving paid services](https://github.com/github/awesome-copilot/discussions/968).
- [ ] My contribution adds a new instruction, prompt, agent, skill, or workflow file in the correct directory.
- [x] The file follows the required naming convention.
- [x] The content is clearly structured and follows the example format.
- [x] I have tested my instructions, prompt, agent, skill, or workflow with GitHub Copilot.
- [x] I have run `npm start` and verified that `README.md` is up to date.
- [x] I am targeting the `staged` branch for this pull request.

---

## Description

Added authorship credits (name and GitHub profile link) to the YAML frontmatter and markdown content of two existing GitHub Copilot skills to properly attribute the work:
- `premium-frontend-ui`
- `gsap-framer-scroll-animation`

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

These changes ensure the author is visibly credited at both the metadata layer (YAML frontmatter) and in the UI layer (document f

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
