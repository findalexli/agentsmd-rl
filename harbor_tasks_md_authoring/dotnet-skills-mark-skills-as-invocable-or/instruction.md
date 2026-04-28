# Mark skills as invocable or reference-only

Source: [Aaronontheweb/dotnet-skills#25](https://github.com/Aaronontheweb/dotnet-skills/pull/25)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/akka/aspire-configuration/SKILL.md`
- `skills/akka/best-practices/SKILL.md`
- `skills/akka/hosting-actor-patterns/SKILL.md`
- `skills/akka/management/SKILL.md`
- `skills/akka/testing-patterns/SKILL.md`
- `skills/aspire/integration-testing/SKILL.md`
- `skills/aspire/service-defaults/SKILL.md`
- `skills/aspnetcore/transactional-emails/SKILL.md`
- `skills/csharp/api-design/SKILL.md`
- `skills/csharp/coding-standards/SKILL.md`
- `skills/csharp/concurrency-patterns/SKILL.md`
- `skills/csharp/type-design-performance/SKILL.md`
- `skills/data/database-performance/SKILL.md`
- `skills/data/efcore-patterns/SKILL.md`
- `skills/dotnet/local-tools/SKILL.md`
- `skills/dotnet/package-management/SKILL.md`
- `skills/dotnet/project-structure/SKILL.md`
- `skills/dotnet/serialization/SKILL.md`
- `skills/dotnet/slopwatch/SKILL.md`
- `skills/meta/marketplace-publishing/SKILL.md`
- `skills/meta/skills-index-snippets/SKILL.md`
- `skills/microsoft-extensions/configuration/SKILL.md`
- `skills/microsoft-extensions/dependency-injection/SKILL.md`
- `skills/playwright/ci-caching/SKILL.md`
- `skills/testing/crap-analysis/SKILL.md`
- `skills/testing/playwright-blazor/SKILL.md`
- `skills/testing/snapshot-testing/SKILL.md`
- `skills/testing/testcontainers/SKILL.md`

## What to add / change

## Summary

Categorize all skills according to their purpose by adding `invocable` flag to SKILL.md frontmatter.

**INVOCABLE SKILLS** (3 skills - user-callable slash commands):
- `slopwatch` - Actively runs code analysis to detect LLM shortcuts
- `crap-analysis` - Code coverage and CRAP score analysis  
- `marketplace-publishing` - Workflow skill for marketplace publication

**REFERENCE-ONLY SKILLS** (25 skills - auto-loaded when relevant):
- All remaining technical guidance, patterns, and best practices
- Includes Akka.NET, C#, data access, testing, Aspire, configuration guidance

This approach keeps the user interface clean (only essential workflow tools as slash commands) while ensuring technical guidance is always available when Claude detects relevant coding contexts.

## Changes

- Updated 28 SKILL.md files with `invocable: true` or `invocable: false`
- Follows categorization from issue #24

Closes #24

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
