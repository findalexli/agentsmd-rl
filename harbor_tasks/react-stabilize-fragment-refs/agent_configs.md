# Agent Config Files — facebook/react @ e6f1c33acf81d9865863ab149d24726f43a56db0

## CLAUDE.md (root)

```
     1	# React
     2	
     3	React is a JavaScript library for building user interfaces.
     4	
     5	## Monorepo Overview
     6	
     7	- **React**: All files outside `/compiler/`
     8	- **React Compiler**: `/compiler/` directory (has its own instructions)
```

## compiler/CLAUDE.md

> Not applicable — this task modifies packages outside `/compiler/`.

<details>
<summary>Full content (260 lines, compiler-only)</summary>

```
     1	# React Compiler Knowledge Base
     2	
     3	This document contains knowledge about the React Compiler gathered during development sessions. It serves as a reference for understanding the codebase architecture and key concepts.
     4	
     5	## Project Structure
     6	
     7	When modifying the compiler, you MUST read the documentation about that pass in `compiler/packages/babel-plugin-react-compiler/docs/passes/` to learn more about the role of that pass within the compiler.
     8	
     9	- `packages/babel-plugin-react-compiler/` - Main compiler package
    10	  - `src/HIR/` - High-level Intermediate Representation types and utilities
    11	  - `src/Inference/` - Effect inference passes (aliasing, mutation, etc.)
    12	  - `src/Validation/` - Validation passes that check for errors
    13	  - `src/Entrypoint/Pipeline.ts` - Main compilation pipeline with pass ordering
    14	  - `src/__tests__/fixtures/compiler/` - Test fixtures
```

(truncated — full content available via `gh api repos/facebook/react/contents/compiler/CLAUDE.md?ref=e6f1c33acf81d9865863ab149d24726f43a56db0`)

</details>

## .claude/skills/extract-errors/SKILL.md

```
     1	---
     2	name: extract-errors
     3	description: Use when adding new error messages to React, or seeing "unknown error code" warnings.
     4	---
     5	
     6	# Extract Error Codes
     7	
     8	## Instructions
     9	
    10	1. Run `yarn extract-errors`
    11	2. Report if any new errors need codes assigned
    12	3. Check if error codes are up to date
```

## .claude/skills/feature-flags/SKILL.md

```
     1	---
     2	name: feature-flags
     3	description: Use when feature flag tests fail, flags need updating, understanding @gate pragmas, debugging channel-specific test failures, or adding new flags to React.
     4	---
     5	
     6	# React Feature Flags
     7	
     8	## Flag Files
     9	
    10	| File | Purpose |
    11	|------|---------|
    12	| `packages/shared/ReactFeatureFlags.js` | Default flags (canary), `__EXPERIMENTAL__` overrides |
    13	| `packages/shared/forks/ReactFeatureFlags.www.js` | www channel, `__VARIANT__` overrides |
    14	| `packages/shared/forks/ReactFeatureFlags.native-fb.js` | React Native, `__VARIANT__` overrides |
    15	| `packages/shared/forks/ReactFeatureFlags.test-renderer.js` | Test renderer |
```

## .claude/skills/fix/SKILL.md

```
     1	---
     2	name: fix
     3	description: Use when you have lint errors, formatting issues, or before committing code to ensure it passes CI.
     4	---
     5	
     6	# Fix Lint and Formatting
     7	
     8	## Instructions
     9	
    10	1. Run `yarn prettier` to fix formatting
    11	2. Run `yarn linc` to check for remaining lint issues
    12	3. Report any remaining manual fixes needed
```

## .claude/skills/flags/SKILL.md

```
     1	---
     2	name: flags
     3	description: Use when you need to check feature flag states, compare channels, or debug why a feature behaves differently across release channels.
     4	---
     5	
     6	# Feature Flags
     7	
     8	Arguments:
     9	- $ARGUMENTS: Optional flags
```

## .claude/skills/flow/SKILL.md

```
     1	---
     2	name: flow
     3	description: Use when you need to run Flow type checking, or when seeing Flow type errors in React code.
     4	---
     5	
     6	# Flow Type Checking
     7	
     8	Arguments:
     9	- $ARGUMENTS: Renderer to check (default: dom-node)
```

## .claude/skills/test/SKILL.md

```
     1	---
     2	name: test
     3	description: Use when you need to run tests for React core. Supports source, www, stable, and experimental channels.
     4	---
     5	
     6	Run tests for the React codebase.
     7	
     8	Arguments:
     9	- $ARGUMENTS: Channel, flags, and test pattern
```

## .claude/skills/verify/SKILL.md

```
     1	---
     2	name: verify
     3	description: Use when you want to validate changes before committing, or when you need to check all React contribution requirements.
     4	---
     5	
     6	# Verification
     7	
     8	Run all verification steps.
     9	
    10	Arguments:
    11	- $ARGUMENTS: Test pattern for the test step
```

---

## Rule Analysis

**Modified files (PR #35642):**
- `packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js`
- `packages/react-native-renderer/src/ReactFiberConfigFabric.js`
- `packages/react-dom/src/__tests__/ReactDOMFragmentRefs-test.js`

**Applicable configs:** Root `CLAUDE.md` only (compiler/CLAUDE.md is for `/compiler/` directory only).

**Programmatic rules:** None — root CLAUDE.md contains no coding rules.

**Soft/subjective rules:** None applicable — skill files contain process rules (how to test, format, verify) not coding style rules.

**Irrelevant:** compiler/CLAUDE.md (wrong directory), all skill files (process rules about tooling, not code style).
