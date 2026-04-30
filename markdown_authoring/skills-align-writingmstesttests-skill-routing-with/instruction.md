# Align `writing-mstest-tests` skill routing with anti-pattern disambiguation

Source: [dotnet/skills#553](https://github.com/dotnet/skills/pull/553)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/dotnet-test/skills/writing-mstest-tests/SKILL.md`

## What to add / change

This updates `writing-mstest-tests` to match the review-thread requirement: anti-pattern/test-quality audits should route to `test-anti-patterns`, while this skill stays focused on writing and modernizing MSTest tests.

- **Routing and scope alignment**
  - Removed anti-pattern review positioning from **When to Use**
  - Added explicit redirect in **When Not to Use** for anti-pattern/test-quality audits → `test-anti-patterns`

- **Input wording cleanup**
  - Updated the “Existing test code” input description to emphasize **improve/modernize** instead of **review**

- **Result**
  - Frontmatter/body guidance is now consistent and avoids conflicting activation signals between the two skills.

```md
## When Not to Use

- User needs to review or audit existing tests for anti-patterns or test quality (use `test-anti-patterns`)
```

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
