# docs: create AGENTS.md

Source: [uPortal-Project/uPortal#2919](https://github.com/uPortal-Project/uPortal/pull/2919)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

##### Checklist

-   [x] the [individual contributor license agreement][] is signed
-   [x] commit message follows [commit guidelines][]
-   [x] documentation is changed or added

##### Description of change

## Add `agents.md` — AI coding tool guidance for uPortal

### Motivation

AI coding tools — GitHub Copilot, Claude, Cursor, and others — are becoming part of how contributors work on open source projects. When these tools operate on uPortal without project context, they produce plausible-looking code that fails in predictable ways: Java 9+ features that break our Java 8 source compatibility, JUnit 5 tests in a JUnit 4 codebase, hardcoded Gradle dependency versions, and sprawling "improvements" to code that wasn't part of the task.

The root cause isn't that the tools are bad — it's that they're missing the same institutional knowledge a new contributor would need on day one. What Java version do we target? What test framework do we use? Where do dependency versions go? What parts of the codebase are fragile? How do I even run this thing locally?

Today that knowledge lives in scattered docs, tribal memory, and PR review feedback after the fact. `agents.md` puts it where the tools can find it before they start writing code.

### Intentions

This file is written for machines, not humans (though humans can read it fine). The goals are:

1. **Prevent the predictable mistakes** — A banned patterns table tells the tool exactly what not to use (`var`, `Lis

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
