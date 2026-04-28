# Add FormatMessage method with SkipLocalsInit

Source: [Aaronontheweb/dotnet-skills#16](https://github.com/Aaronontheweb/dotnet-skills/pull/16)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/csharp/coding-standards/SKILL.md`

## What to add / change

Added example of using SkipLocalsInit with stackalloc and Span<T>.

Fixes #

## Changes

Please provide a brief description of the changes here.

## Checklist

For significant changes, please ensure that the following have been completed (delete if not relevant):

* [ ] This change follows the [Akka.NET API Compatibility Guidelines](https://getakka.net/community/contributing/api-changes-compatibility.html).
* [ ] This change follows the [Akka.NET Wire Compatibility Guidelines](https://getakka.net/community/contributing/wire-compatibility.html).
* [x] I have [reviewed my own pull request](https://getakka.net/community/contributing/index.html#review-your-own-pull-requests).
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
