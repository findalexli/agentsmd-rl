# Add ilspy-decompile skill documentation

Source: [Aaronontheweb/dotnet-skills#45](https://github.com/Aaronontheweb/dotnet-skills/pull/45)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/ilspy-decompile/SKILL.md`

## What to add / change

Added documentation for the ilspy-decompile skill, including prerequisites, quick start, common assembly locations, core workflow, and commands for decompilation.

Slightly tweaked from https://github.com/davidfowl/dotnet-skillz/blob/main/skills/ilspy-decompile/SKILL.md

Fixes #

## Changes

Please provide a brief description of the changes here.

## Checklist

For significant changes, please ensure that the following have been completed (delete if not relevant):

* [ ] This change follows the [Akka.NET API Compatibility Guidelines](https://getakka.net/community/contributing/api-changes-compatibility.html).
* [ ] This change follows the [Akka.NET Wire Compatibility Guidelines](https://getakka.net/community/contributing/wire-compatibility.html).
* [ ] I have [reviewed my own pull request](https://getakka.net/community/contributing/index.html#review-your-own-pull-requests).
* [ ] Design discussion issue #
* [ ] Changes in public API reviewed, if any.
* [ ] I have added website documentation for this feature.

### Latest `dev` Benchmarks 

Include data from the [relevant benchmark](https://getakka.net/community/contributing/index.html#improve-performance) prior to this change here.

### This PR's Benchmarks

Include data from after this change here.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
