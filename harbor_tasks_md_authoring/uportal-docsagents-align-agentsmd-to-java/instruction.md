# docs(agents): align AGENTS.md to Java 11 reality

Source: [uPortal-Project/uPortal#2947](https://github.com/uPortal-Project/uPortal/pull/2947)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary

`AGENTS.md` had two pieces of outdated guidance that contradicted the project's actual Java 11 stance:

1. **Banned-patterns table** still flagged Java 9–11 features as banned (`var`, `List.of()`/`Map.of()`, `Optional.isEmpty()`, `String.isBlank()`), even though the file's own tech-stack section says "sourceCompatibility 11". Since uPortal compiles under Java 11, those features are allowed.

2. **SDKMAN section** told agents to install and use `java 8.0.472-amzn`, annotated as "required for uPortal-start". uPortal-start also moved to Java 11, so that guidance sends agents down a broken path.

## Changes

All documentation — no code changes.

### Banned-patterns table — the ban line shifts from "Java 9+" to "Java 12+"

Dropped rows for features allowed on Java 11:
- `var`
- `List.of()`, `Map.of()`
- `Optional.isEmpty()`
- `String.isBlank()`

Replaced the single "Records, text blocks, sealed classes" row with explicit per-feature rows, each annotated with the Java version that introduced it:
- Switch expressions with `->` (Java 14+)
- Text blocks `"""..."""` (Java 15+)
- Records (Java 16+)
- Pattern matching for `instanceof` (Java 16+)
- Sealed classes / `non-sealed` / `permits` (Java 17+)
- Pattern matching for `switch` (Java 21+)

Kept unchanged: JUnit 5 annotations, inline Gradle versions, `commons-logging`.

Added a short lead-in above the table clarifying that Java 9–11 features are fair game and the ban line is Java 12.

### Checklist + Boundaries

"No Java 9+

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
