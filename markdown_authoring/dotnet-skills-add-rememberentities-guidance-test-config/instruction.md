# Add RememberEntities guidance, test config reuse, and conditional Aspire config

Source: [Aaronontheweb/dotnet-skills#22](https://github.com/Aaronontheweb/dotnet-skills/pull/22)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/akka/hosting-actor-patterns/SKILL.md`
- `skills/akka/testing-patterns/SKILL.md`
- `skills/aspire/integration-testing/SKILL.md`

## What to add / change

## Summary

Addresses three related issues about improving skill documentation with real-world patterns discovered during development.

## Issue #13: Cluster Sharding RememberEntities Guidance

Added to `akka-hosting-actor-patterns`:
- `RememberEntities = false` should be the default (almost always correct)
- Table showing entity types and when to use true vs false
- Problems caused by incorrect `RememberEntities = true` (unbounded memory, slow startup, stale resurrection)
- Marker types with `WithShardRegion<T>` for consistent registry access
- Avoiding redundant `registry.Register<T>()` calls

## Issue #14: Reusing Production Config in Tests

Added new Pattern 5 to `akka-net-testing-patterns`:
- Anti-pattern: duplicating HOCON config in tests
- Correct pattern: reusing production `AkkaConfigurationBuilder` extension methods
- Benefits: DRY, no config drift, better coverage, catches real bugs

## Issue #17: Generalized Conditional Aspire Configuration

Expanded Pattern 6 in `aspire-integration-testing`:
- Renamed to "Conditional Resource Configuration for Tests"
- Comprehensive `AppHostConfiguration` class covering volumes, execution mode, auth, external services
- "Default to production-like" principle - tests override specific behaviors
- Test authentication pattern (`/dev-login` endpoint)
- Fake external services pattern
- Table of common conditional settings (volumes, execution mode, auth, replicas, etc.)

Closes #13, closes #14, closes #17

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
