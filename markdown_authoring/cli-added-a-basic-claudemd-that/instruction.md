# Added a basic CLAUDE.md that points to our cursor rules

Source: [Shopify/cli#6653](https://github.com/Shopify/cli/pull/6653)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/CLAUDE.md`

## What to add / change

### WHY are these changes introduced?

I use Claude Code a lot and it would benefit from having more context on Shopify CLI.

### WHAT is this pull request doing?

Adds a `CLAUDE.md` that points to our cursor rules.

<img width="1177" height="872" alt="image" src="https://github.com/user-attachments/assets/d6eb07b6-cebb-4ae0-a486-54011a10bd45" />

### How to test your changes?

```
git switch basic_claude_md
claude -p "How do I add a command to Shopify CLI?"
```

Or prompt of your choice.

### Measuring impact

How do we know this change was effective? Please choose one:

- [x] n/a - this doesn't need measurement, e.g. a linting rule or a bug-fix
- [ ] Existing analytics will cater for this addition
- [ ] PR includes analytics changes to measure impact

### Checklist

- [x] I've considered possible cross-platform impacts (Mac, Linux, Windows)
- [x] I've considered possible [documentation](https://shopify.dev) changes

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
