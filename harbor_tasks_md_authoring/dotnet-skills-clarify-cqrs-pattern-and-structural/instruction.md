# Clarify CQRS pattern and structural differences in database-performance skill

Source: [Aaronontheweb/dotnet-skills#26](https://github.com/Aaronontheweb/dotnet-skills/pull/26)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/data/database-performance/SKILL.md`

## What to add / change

## Summary

Enhance the database-performance skill to better explain the CQRS (Command Query Responsibility Segregation) pattern and the structural differences between read and write models.

## Changes

1. **Added CQRS metadata tags** for agent discovery
   - Tags: `cqrs`, `performance`, `patterns`

2. **Clarified read/write model separation**
   - Emphasized that read and write models have fundamentally different shapes
   - Read models: denormalized, multiple specialized projections (UserProfile, UserSummary, etc.)
   - Write models: normalized, validation-focused, accept strongly-typed commands
   - Not just separate interfaces - different data shapes and access patterns

3. **Improved code samples**
   - Updated architecture diagram to show separate DTO and command types
   - Added inline comments explaining why each method returns its specific type
   - Illustrated how read store returns multiple different return types
   - Showed how write store returns minimal data (UserId only, void for others)

4. **Added clarity on key differences**
   - Read queries are stateless projections (no change tracking)
   - Write operations focus on validation, not data retrieval
   - Different databases/tables can back read vs write side (eventual consistency)

This helps agents and developers understand that CQRS is about fundamentally different access patterns, not just interface separation.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
