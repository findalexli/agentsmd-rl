# Remove private utilities from the Angular Developer testing skill reference

The repository ships agent-facing skill instructions under `skills/dev-skills/angular-developer/`. The skill's `SKILL.md` loads a testing fundamentals reference at `skills/dev-skills/angular-developer/references/testing-fundamentals.md` whenever an agent works on testing tasks.

## Problem

The current testing fundamentals reference promotes APIs that come from a **private, internal-only** package path (`packages/private/testing/src/utils.ts`). Skill instructions are public-facing guidance for downstream Angular consumers — they must not direct users toward symbols that live in the framework's private testing internals, because those symbols are not part of Angular's public API surface and are not available to consumers of the framework.

The file currently opens with the top-level heading `# Testing Fundamentals` and contains several sections: `## Core Philosophy: Zoneless & Async-First` (which teaches the `Act, Wait, Assert` pattern), `### Basic Test Structure Example` (a runnable example using `fixture.whenStable()`), and `## TestBed and ComponentFixture`.

Concretely, the reference also contains a section headed `## Custom Utilities` that:

- Documents two helpers — `useAutoTick()` (a mock-clock fast-forwarder) and `` `await timeout(ms)` `` (a real-time delay helper) — and explicitly cites their source file as `packages/private/testing/src/utils.ts`.
- Closes with the recommendation "Always prefer `useAutoTick()` to keep tests efficient".

This entire block of guidance is inappropriate for a public Angular-developer skill reference because it advertises private framework internals as something a downstream consumer should reach for.

## What to fix

Update `skills/dev-skills/angular-developer/references/testing-fundamentals.md` so that **no part of the file references symbols, helpers, or paths from the private testing package**. After the change:

- The reference must not contain any heading, sentence, list item, or code reference that documents helpers from `packages/private/testing/src/utils.ts`.
- The `useAutoTick()` fast-forwarder helper and the `` `await timeout(ms)` `` delay helper described in that block must no longer be mentioned anywhere in this file.
- The remainder of the file (`# Testing Fundamentals`, the `## Core Philosophy: Zoneless & Async-First` section with its `Act, Wait, Assert` pattern, the `### Basic Test Structure Example` with its `fixture.whenStable()` usage, and the `## TestBed and ComponentFixture` section) should be left intact — only the guidance that promotes the private-package helpers needs to go.

The file's structure should still end with the `## TestBed and ComponentFixture` section as its final section.

## Scope

- Only `skills/dev-skills/angular-developer/references/testing-fundamentals.md` needs to change.
- Do **not** modify `AGENTS.md`, the `SKILL.md`, or any code under `packages/`.
- Do not add new sections or rewrite unrelated guidance — this is a focused removal of inappropriate content.
