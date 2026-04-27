# skill: design proposal

Source: [dagger/dagger#11794](https://github.com/dagger/dagger/pull/11794)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/dagger-design-proposals/SKILL.md`

## What to add / change

A skill for writing design proposals for improving Dagger. Extracted from recent "vibe spec-ing" sessions.

---
name: dagger-design-proposals
description: Write design proposals for Dagger features. Use when asked to draft, review, or iterate on Dagger design documents, RFCs, or proposals.
---

# Dagger Design Proposals

Guidelines for writing design proposals for Dagger features.

## Before Writing

**Always research first:**
1. Check existing skills (dagger-codegen, cache-expert, etc.) for relevant context
2. Look at related code in the Dagger codebase:
   - GraphQL schema: `core/schema/*.go`
   - CLI commands: `cmd/dagger/*.go`
   - Core types: `core/*.go`
3. Understand existing patterns before proposing new ones

## Structure

```markdown
# Part N: Title

*Builds on [Part N-1: Title](link)*

## Table of Contents
- [Problem](#problem)
- [Solution](#solution)
- [Core Concept](#core-concept)
- [CLI](#cli)
- [Status](#status)

## Problem

Numbered, concise limitations:

1. **Short title** - One sentence explanation.
2. **Short title** - One sentence explanation.

## Solution

One paragraph summary.

## Core Concept

GraphQL type definitions with inline docstrings:

```graphql
"""
Type description here.
"""
type Example {
  """Method description."""
  method(arg: String!): Result!
}
```

Go for implementation examples:

```go
func New(ws dagger.Workspace) *Example {
    // ...
}
```

## CLI

Real command exa

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
