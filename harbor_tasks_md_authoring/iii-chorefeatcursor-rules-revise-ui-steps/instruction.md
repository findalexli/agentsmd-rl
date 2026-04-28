# chore(feat:cursor rules): Revise UI Steps documentation for Motia

Source: [iii-hq/iii#686](https://github.com/iii-hq/iii/pull/686)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `packages/snap/src/cursor-rules/dot-files/.cursor/rules/ui-steps.mdc`

## What to add / change

Updated UI Steps documentation to reflect new patterns and requirements for Motia, including critical patterns, configuration requirements, and troubleshooting tips.

I have verified, Cursor rules working perfectly for UI `button`.



<img width="1495" height="837" alt="Screenshot 2025-09-11 at 18 19 23" src="https://github.com/user-attachments/assets/f84fc224-0d31-45fd-9d04-9cabcc1ac701" />

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
