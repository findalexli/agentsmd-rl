# Agents md and split skill

Source: [focus-shift/jollyday#1042](https://github.com/focus-shift/jollyday/pull/1042)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/add-holiday-calendar-xml/SKILL.md`
- `.agents/skills/add-holiday-description-properties/SKILL.md`
- `.agents/skills/add-subdivision/SKILL.md`
- `.agents/skills/how-to-add-a-new-holiday-calendar-for-a-country/SKILL.md`
- `.agents/skills/register-holiday-calendar/SKILL.md`
- `.agents/skills/write-holiday-tests/SKILL.md`
- `agents.md`

## What to add / change

<!--

Thanks for contributing.
Please review the following notes before submitting you pull request.

Please look for other issues or pull requests which already work on this topic. Is somebody already on it? Do you need to synchronize?

# Security Vulnerabilities

🛑 STOP! 🛑 If your contribution fixes a security vulnerability, please do not submit it.
Instead, please write an E-Mail to to one of the maintainer with all the information
to recreate the security vulnerability.

# Describing Your Changes

If, having reviewed the notes above, you're ready to submit your pull request, please
provide a brief description of the proposed changes.

If they:
 🐞 fix a bug, please describe the broken behaviour and how the changes fix it.
    Please label with 'type: bug' and 'status: new'
    
 🎁 make an enhancement, please describe the new functionality and why you believe it's useful.
    Please label with 'type: enhancement' and 'status: new'
 
If your pull request relates to any existing issues,
please reference them by using the issue number prefixed with #.

-->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
