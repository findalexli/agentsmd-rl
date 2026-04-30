# feat: improve skill scores for skillpack

Source: [CreminiAI/skillpack#8](https://github.com/CreminiAI/skillpack/pull/8)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/skillpack-creator/SKILL.md`
- `templates/builtin-skills/skill-creator/SKILL.md`

## What to add / change

Hey @yava 👋

I ran your skills through `tessl skill review` at work and found some targeted improvements. 


<img width="1312" height="682" alt="image" src="https://github.com/user-attachments/assets/5915de50-6315-425a-b53f-1997f06c3f65" />


Here's the full before/after:

| Skill | Before | After | Change |
|-------|--------|-------|--------|
| skillpack-creator | 94% | 94% | — |
| skill-creator | 90% | 100% | +10% |

This PR covers both skills in the repo.

<details>
<summary>Changes summary</summary>

### skillpack-creator (`skills/skillpack-creator/SKILL.md`)
- Added concrete JSON manifest example and YAML frontmatter template to improve actionability
- Merged Decision Rules into relevant workflow steps to eliminate redundancy
- Consolidated pack specification step with inline example
- Tightened wording throughout while preserving all workflow steps

### skill-creator (`templates/builtin-skills/skill-creator/SKILL.md`)
- Added complete SKILL.md template with YAML frontmatter and body structure as a concrete starting point
- Removed generic "Communicating with the user" section (Claude infers communication style)
- Condensed interview/research section into intent capture step
- Consolidated repeated path/location instructions across Pack-specific rules, Save location, and Completion checklist
- Removed duplicate "put when to use in description" guidance
- Tightened test-and-iterate section

</details>

---

Honest disclosure — I work 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
