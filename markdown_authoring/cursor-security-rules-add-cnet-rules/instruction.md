# Add C#/.NET Rules

Source: [matank001/cursor-security-rules#7](https://github.com/matank001/cursor-security-rules/pull/7)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `secure-dev-c-sharp.mdc`

## What to add / change

Hello,

This pull request contains a new rules .mdc file with security rules for C#/.NET development.
I will probably add more rules to the file in the future, and focus on .NET libraries and frameworks, such as ASP.NET, EntityFramework and more.

Thanks,
Nimrod Kir'on
Senior Backend Engineer, LSports

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
