# 📝 docs(skills): add sub-issue tree guide to linear skill

Source: [lobehub/lobe-chat#14076](https://github.com/lobehub/lobehub/pull/14076)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/linear/SKILL.md`

## What to add / change

#### 💻 Change Type

- [x] 📝 docs

#### 🔗 Related Issue

No linked issue — internal authoring improvement discovered while decomposing a parent task into a sub-issue tree via MCP.

#### 🔀 Description of Change

Adds a new **Creating Sub-issue Trees** section to the linear skill. Captures five rules learned while using `mcp__linear-server__save_issue` to decompose a parent issue:

1. **Always prefix titles with an ordering index** (`[1]`, `[4.1.1]`). The sub-issue panel defaults to newest-first `sortOrder`, and `save_issue` does not expose a `sortOrder` parameter, so creation order — parallel or serial — cannot produce the intended reading order.
2. **Nest by logical parent-child, not flat.** Linear supports unlimited depth; a flat pile of 8+ siblings is hard to scan.
3. **Creation order is dictated by `blockedBy`** — topologically sort the DAG; `blockedBy` is append-only.
4. **Don't chase parallelism.** MCP calls in a single message execute sequentially on the server, and dependent calls need blocker IDs from prior responses anyway.
5. **Keep each sub-issue description self-contained** — implementers may open only the child, not the parent.

The example tree uses neutral labels (`[db]`, `[service]`, `[api]`, `[sdk]`, `[app]`, `[ui]`) so the guidance applies to any Linear workspace, not just this project's directory structure.

#### 🧪 How to Test

- [x] Tested locally — rules validated while creating 8 sub-issues for a real parent task; all five points reflect real friction enc

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
