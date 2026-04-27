# Fix outdated Copilot skill references for agents and skills in github-copilot-starter

Source: [github/awesome-copilot#918](https://github.com/github/awesome-copilot/pull/918)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/github-copilot-starter/SKILL.md`

## What to add / change

## Pull Request Checklist

- [x] I have read and followed the [CONTRIBUTING.md](https://github.com/github/awesome-copilot/blob/main/CONTRIBUTING.md) guidelines.
- [ ] My contribution adds a new instruction, prompt, agent, skill, or workflow file in the correct directory.
- [x] The file follows the required naming convention.
- [x] The content is clearly structured and follows the example format.
- [x] I have tested my instructions, prompt, agent, skill, or workflow with GitHub Copilot.
- [x] I have run `npm start` and verified that `README.md` is up to date.

---

## Description

This pull request updates an existing Copilot skill to align it with the current structure of the `github/awesome-copilot` repository.

The changes are intentionally minimal and focused on fixing outdated references and output guidance:
- replaces outdated chat mode references with agents
- removes old collections guidance
- removes old prompt-folder assumptions and points to skills instead
- updates repository resource references to match the current repo structure
- fixes an outdated internal instructions reference
- tightens checklist language around formatter and metadata requirements
- Added engineer.agent.md with awesome-copilot lookup pattern
- Added templates for copilot-instructions.md, instructions, and skills
- Replaced team-size tiers with minimal one fits all set up.
- makes workflow creation optional 

---

## Type of Contribution

- [ ] New instruction fi

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
