# Set up GitHub Copilot instructions [skip-ci]

Source: [sammcj/mcp-devtools#179](https://github.com/sammcj/mcp-devtools/pull/179)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Summary

Configured `.github/copilot-instructions.md` with comprehensive development guidance extracted from `CLAUDE.md`, `README.md`, and `docs/creating-new-tools.md` to provide GitHub Copilot users with equivalent context to Claude Code users.

## Type of Change

- [x] Documentation update

## Changes Made

**Added Critical Development Guidance:**
- Tool registration checklist emphasizing secure-by-default (all new tools disabled unless explicitly approved)
- Go modernisation rules (`any` vs `interface{}`, `strings.CutPrefix`, modern loops/maps/slices)
- Correct tool import location: `internal/imports/tools.go` (NOT `main.go`)

**Added MCP Development Best Practices:**
- Build workflow-oriented tools, not API wrappers
- Optimise for limited context windows (token efficiency)
- Design actionable error messages
- Tool descriptions: action-oriented, <200 chars, focus on WHAT not WHY

**Added Technical Patterns:**
- OpenTelemetry tracing patterns (session span flush requirements)
- Tool development pattern (struct → init → Definition → Execute)
- Security integration requirements
- File/directory permission standards (0600/0700)

**Enhanced Review Checklist:**
- Expanded from 8 to 12 verification items
- Added modernisation rules compliance check
- Added tool import location verification
- Added default enablement verification

**Added Operational Guidance:**
- Quick debugging tips for interactive tool testing
- Build/test/lint requirements before completion
- British Englis

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
