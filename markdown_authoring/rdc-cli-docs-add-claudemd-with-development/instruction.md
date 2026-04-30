# docs: add CLAUDE.md with development rules for coding agents

Source: [BANANASJIM/rdc-cli#1](https://github.com/BANANASJIM/rdc-cli/pull/1)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

### **User description**
Adds CLAUDE.md to the repo root so all coding agents (Claude Code, Codex, OpenCode) automatically pick up development rules when entering the project.

Covers: source of truth, OpenSpec workflow, test-first, code standards, commit conventions, quality gates, output format rules, branch strategy, architecture.


___

### **PR Type**
Documentation


___

### **Description**
- Adds `CLAUDE.md` with comprehensive development rules for coding agents

- Covers source of truth (Obsidian docs), OpenSpec workflow, test-first approach

- Defines code standards, commit conventions, quality gates, output formats

- Documents branch strategy and architecture guidelines with key file references


___



### File Walkthrough

<table><thead><tr><th></th><th align="left">Relevant files</th></tr></thead><tbody><tr><td><strong>Documentation</strong></td><td><table>
<tr>
  <td>
    <details>
      <summary><strong>CLAUDE.md</strong><dd><code>Comprehensive development rules for coding agents</code>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; </dd></summary>
<hr>

CLAUDE.md

<ul><li>Establishes Obsidian design docs as single source of truth<br> <li> Defines mandatory OpenSpec workflow with proposal, test-plan, tasks, <br>and specs<br> <li> Enforces test-first development with mock renderdoc module<br> <li> Specifies code standards (English, type hints, pathlib, Google <br>docstrings)<br> <li> Documents conventional commits with forbidden AI-related keywords<br> 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
