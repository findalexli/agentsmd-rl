# [DOC] Add AGENTS.md guidance

Source: [OpenMS/OpenMS#8537](https://github.com/OpenMS/OpenMS/pull/8537)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- add AGENTS.md with repo guidance, coding/test conventions, pyOpenMS wrapping notes, and doc links
- include Doxygen-derived conventions and developer links
- add agent change-impact checklist

## Testing
- Not run (docs only)

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Added a comprehensive project handbook covering repository conventions, layout, build/install and testing guidance, coding standards, contributor workflow, debugging and profiling tips, CI/packaging and container notes, external project references, and a change-impact checklist to help contributors and maintainers navigate and work with the repository.

<sub>✏️ Tip: You can customize this high-level summary in your review settings.</sub>
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
