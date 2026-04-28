# Clarify PR body language guidance in ant-design CLAUDE.md

The ant-design repository's `CLAUDE.md` (the project's AI-assistant guide) currently has a PR-authoring rule that is too restrictive about the language of the PR body.

## Current rule (too restrictive)

Inside `CLAUDE.md`, under the section `## PR 规范` → `### 标题与内容`, the body-language rule reads:

> `- PR 内容默认使用英文`

This says the PR body must default to English, but it does not acknowledge that contributors who are more comfortable in Simplified Chinese may legitimately write the PR body in Chinese — which is in fact the convention several maintainers follow.

## What needs to change

Update that single rule so it still defaults to English but explicitly allows the contributor to choose Chinese or English based on their own language habits. The PR **title** rule (always English) is unchanged.

The replacement rule must be written in Simplified Chinese to match the surrounding lines and must read **exactly**:

```
- PR 内容默认使用英文，可根据用户语言习惯决定使用中文或英文
```

That line replaces the existing `- PR 内容默认使用英文` line in-place — same bullet position, same surrounding rules (title rule above, example rule below).

## Constraints

- Only `CLAUDE.md` should be edited.
- Do not touch any other rule (API-table format, anchor IDs, branch strategy, Emoji conventions, Changelog format, etc.).
- Keep the PR-title rule ("PR 标题始终使用英文，格式：`类型: 简短描述`") and its example ("fix: fix button style issues in Safari browser") intact.
- Keep the file's top-level heading `# Ant Design 项目开发指南` and overall structure intact (sections, code fences, tables must remain well-formed).
- The new rule must live inside the existing `## PR 规范` section — do not create a new top-level section for it.

## Working directory

The repo is checked out at `/workspace/ant-design`. Edit `CLAUDE.md` in place.
