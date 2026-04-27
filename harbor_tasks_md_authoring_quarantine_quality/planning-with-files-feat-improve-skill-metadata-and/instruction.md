# feat: improve skill metadata and description for better discoverability

Source: [OthmanAdi/planning-with-files#83](https://github.com/OthmanAdi/planning-with-files/pull/83)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/planning-with-files/SKILL.md`

## What to add / change

👋  hullo @OthmanAdi 

I ran your skills through a `tessl skill review` and found some ways to improve discoverability and usability. I hope this is welcome, and helpful.

Summary: 

| Area | Before | After |
|------|--------|-------|
| Description score | 0% (blocked) | 100% |
| Content score | 0% (blocked) | 100% |
| allowed-tools format | YAML list (invalid) | comma-separated string (valid) | | metadata.version | missing | added (2.10.0) |
| trigger terms | limited | added "plan out", "break down", "organize", "track progress" |

Details:

- Fixed `allowed-tools` from YAML list to string format (was causing validation failure)
- Moved `version` from top-level frontmatter to `metadata.version` (standard location)
- Enriched description with natural trigger terms for better skill matching
- No changes to skill behaviour, templates, scripts, or content

These were pretty straightforward changes to bring the skill in line with what performs well against Anthropic's best practices. Full disclosure, I work at @tesslio where we build tooling around this. Not a pitch, just fixes that were not time consuming to make, so I thought I'd offer them as a PR.

Of course, if you'd like to get all your skills to 100%, click [here](https://tessl.io/registry/skills/submit) to trigger the evals and iterate some more, otherwise I'm happy to offer more improvements as I find them.

Thanks in advance! Have a great day! 😸

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
