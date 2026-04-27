# feat(skill): add qzcli skill for Qizhi platform job management

Source: [wanshuiyin/Auto-claude-code-research-in-sleep#150](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/pull/150)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/qzcli/SKILL.md`

## What to add / change

## Summary

- Adds a new `qzcli` skill for managing GPU compute jobs on the Qizhi (启智) platform via [tianyilt/qzcli_tool](https://github.com/tianyilt/qzcli_tool) — a kubectl/docker-style CLI
- Covers installation, MCP integration, authentication, resource discovery, interactive/non-interactive job submission, batch submission (JSON matrix config), HPC/CPU jobs, job management, and troubleshooting
- All credentials and institution-specific IDs replaced with placeholders (`YOUR_USERNAME`, `YOUR_WORKSPACE_ID`, etc.) — works with any Qizhi instance

## Motivation

The Qizhi (启智) platform is widely used by Chinese ML researchers for GPU compute. `qzcli` is an open-source CLI that makes managing jobs on it scriptable and agent-friendly. Many ARIS users running `/run-experiment` on Qizhi need this workflow, but there was no existing skill for it. This skill pairs naturally with `run-experiment` and `monitor-experiment`.

## What's in the skill

**Trigger keywords:** `qzcli`, `启智平台`, `submit job`, `stop job`, `查计算组`, `avail`, `batch submit`

**Key sections:**
- **Installation**: `pip install` deps + `pip install -e .` from GitHub
- **MCP integration**: `claude mcp add qzcli -- qzcli-mcp` / `codex mcp add qzcli -- qzcli-mcp`
- **Configuration**: `.env` file and env var methods, credential priority order
- **Resource discovery**: `qzcli res -u` to cache workspaces/compute groups/specs
- **Node availability**: `qzcli avail` with `-n`, `-e`, `--lp`, `-v` flags
- **Interactive submission*

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
