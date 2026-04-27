# improve tubeify skill structure + eval score

Source: [davepoon/buildwithclaude#104](https://github.com/davepoon/buildwithclaude/pull/104)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/all-skills/skills/tubeify/SKILL.md`

## What to add / change

hey @davepoon, thanks for building the buildwithclaude hub. really like having a single place to discover skills, agents, and plugins across the Claude ecosystem. Kudos on passing `2.6k` stars! I've just starred it.

ran your tubeify skill through agent evals and spotted a few quick wins that took it from `~61%` to `~100%` performance:

- expanded description with trigger terms like _YouTube transcript, video summary, timestamp extraction_ so agents reliably match user requests

- restructured workflow into clear numbered steps + added error recovery for failed fetches

- tightened prose + removed redundant content to improve conciseness score

these were easy changes to bring the skill in line with what **performs well against Anthropic's best practices**. honest disclosure, I work at tessl.io where we build tooling around this. not a pitch, just fixes that were straightforward to make!

you've got `168` skills, if you want to do it yourself, spin up Claude Code and run `tessl skill review`. alternatively, let me know if you'd like an automatic review in your repo via GitHub Actions. it doesn't require signup, and this means you and your contributors get an instant quality signal before you have to review yourself.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
