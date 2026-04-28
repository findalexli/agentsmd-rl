# First version of an OpenTelemetry .NET Instrumentation skill

Source: [Aaronontheweb/dotnet-skills#52](https://github.com/Aaronontheweb/dotnet-skills/pull/52)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/opentelementry-dotnet-instrumentation/skill.md`

## What to add / change

## Changes

Add a first version of an OpenTelemetry .NET Instrumentation skill. I have already used this extensively in multiple situations while implementing OTel for some [NServiceBus](https://github.com/Particular/NServiceBus.Envelope.CloudEvents/pull/39) or [ServiceComposer](https://github.com/ServiceComposer/ServiceComposer.AspNetCore/pull/1027) features.

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
