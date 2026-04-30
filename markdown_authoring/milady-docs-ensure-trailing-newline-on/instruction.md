# docs: ensure trailing newline on AGENTS.md

Source: [milady-ai/milady#1998](https://github.com/milady-ai/milady/pull/1998)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Appends a single trailing newline to AGENTS.md so the file ends cleanly per POSIX convention.

<!-- Macroscope's pull request summary starts here -->
<!-- Macroscope will only edit the content between these invisible markers, and the markers themselves will not be visible in the GitHub rendered markdown. -->
<!-- If you delete either of the start / end markers from your PR's description, Macroscope will append its summary at the bottom of the description. -->
> [!NOTE]
> ### Add trailing newline to AGENTS.md
> Adds a missing trailing newline to [AGENTS.md](https://github.com/milady-ai/milady/pull/1998/files#diff-a54ff182c7e8acf56acfd6e4b9c3ff41e2c41a31c9b211b2deb9df75d9a478f9). No content changes.
>
> <!-- Macroscope's review summary starts here -->
>
> <sup><a href="https://app.macroscope.com">Macroscope</a> summarized 13ce83a.</sup>
> <!-- Macroscope's review summary ends here -->
>
<!-- macroscope-ui-refresh -->
<!-- Macroscope's pull request summary ends here -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
