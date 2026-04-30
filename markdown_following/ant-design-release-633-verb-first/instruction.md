# Release antd 6.3.3 with Updated Format Rules

You are a maintainer of the `ant-design/ant-design` repository (npm package `antd`). The repo is checked out at `/workspace/ant-design`. You need to cut release **6.3.3** and ALSO refresh the project's changelog formatting rules so they match the format that has been adopted in practice.

The release date is **`2026-03-16`**.

## 1. Update the format rules first

Before writing the new release notes, two rules need to be tightened so that the AI helpers in this repo (Claude / Cursor / etc.) follow the format the team has been using for a while.

### 1a. `CLAUDE.md` — Chinese sentence pattern

In `CLAUDE.md`, the *Changelog 规范* → *句式* table currently lists the Chinese row as:

| 中文 | `Emoji 组件名 动词/描述` | `🐞 Button 修复暗色主题下 \`color\` 的问题。` |

Switch the Chinese row so that the verb leads the sentence (the same convention the English row already uses). The new row must use the format string `Emoji 动词 组件名 描述`（动词在前） and use the example sentence `🐞 修复 Button 在暗色主题下 \`color\` 的问题。`.

### 1b. `CLAUDE.md` — Contributor link policy

In the same file, the *核心原则* section currently says:

```
- 尽量给出 PR 链接，社区 PR 加贡献者链接
```

We are dropping the "community-only" carve-out: from now on **every** entry gets a contributor link (no team-vs-community distinction). Update that bullet so it reads:

```
- 尽量给出 PR 链接，并统一添加贡献者链接
```

### 1c. `.claude/skills/changelog-collect/SKILL.md` — Codify the new rules

The changelog-collect skill at `.claude/skills/changelog-collect/SKILL.md` also needs to encode the same two rules. Make these edits:

**Add a new sub-section** between the end of *阶段二：处理临时文件* and the start of *阶段三：写入文件*. The new sub-section MUST:

- Be titled exactly `#### 描述与署名补充规则`
- Contain three bullets, written in Chinese, that together state:
  1. *描述必须以动作开头* — Chinese descriptions should lead with verbs such as `修复`、`优化`、`新增`、`重构`; English descriptions should lead with `Fix`、`Improve`、`Add`、`Refactor`.
  2. Even with the action-first rule, the body must still contain the component name. Use `修复 Select ...` and `Fix Select ...` as positive examples.
  3. Every changelog entry must include a *PR 作者链接* (e.g. `[@username](https://github.com/username)`); the previous "team member only" carve-out no longer applies.

**Fix the bottom "注意事项" bullets**: the current line reads:

```
- 组件名在正文中要出现（如 `Select 修复...`，不是 `修复 Select...`）
```

It is wrong now (it forbids the very pattern we want). Replace it with two bullets:

1. One that says descriptions lead with the action **and** the body still contains the component name (use `修复 Select ...` and `Fix Select ...` as positive examples).
2. One that says every entry adds a PR author link, with no team/community distinction.

## 2. Bump the package version

In `package.json`, change `"version"` from `"6.3.2"` to `"6.3.3"`.

## 3. Add the 6.3.3 release notes

Add a new `## 6.3.3` section to **both** `CHANGELOG.en-US.md` and `CHANGELOG.zh-CN.md`. It must be inserted directly above the existing `## 6.3.2` section (i.e. as the new top-most release entry under the `---` front matter divider).

The first line under the heading is the release date, formatted as `` `2026-03-16` `` (the date in backticks, on its own line).

The release contains six PRs. Two of them are Image fixes that need to be grouped under an `- Image` sub-list. The other four are top-level bullets.

| Emoji  | PR                                                          | Author        | Component | English description                                                                                                                                          | Chinese description                                                                                                       |
|--------|-------------------------------------------------------------|---------------|-----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| 💄     | [#57299](https://github.com/ant-design/ant-design/pull/57299) | @mango766      | Image     | Improve Image preview mask blur transition for `backdrop-filter` to reduce flicker perception.                                                                | 优化 Image 预览蒙层 blur 效果的 `backdrop-filter` 过渡，减少闪烁感。                                                       |
| 🐞     | [#57288](https://github.com/ant-design/ant-design/pull/57288) | @ug-hero       | Image     | Fix Image showing move cursor when `movable={false}`.                                                                                                          | 修复 Image 在 `movable={false}` 时仍显示 move 光标的问题。                                                                |
| ⌨️ ♿   | [#57266](https://github.com/ant-design/ant-design/pull/57266) | @ug-hero       | App       | Improve App link `:focus-visible` outline to enhance keyboard accessibility.                                                                                  | 优化 App 链接的 `:focus-visible` 外框样式，提升键盘可访问性。                                                              |
| 🐞     | [#57273](https://github.com/ant-design/ant-design/pull/57273) | @mavericusdev  | Form      | Fix Form required mark using hardcoded `SimSun` font.                                                                                                          | 修复 Form 必填标记文案中硬编码 `SimSun` 字体的问题。                                                                       |
| 🐞     | [#57246](https://github.com/ant-design/ant-design/pull/57246) | @guoyunhe      | Grid      | Fix Grid media size mapping issue for `xxxl` breakpoint.                                                                                                       | 修复 Grid `xxxl` 断点在媒体尺寸映射中的错误。                                                                              |
| 🐞     | [#57242](https://github.com/ant-design/ant-design/pull/57242) | @aojunhao123   | Tree      | Fix Tree scrolling to top when clicking node.                                                                                                                  | 修复 Tree 点击节点时页面回滚到顶部的问题。                                                                                 |

### Required formatting (applies to both languages)

- Each entry begins with its emoji.
- Verb-first sentence pattern (`Emoji 动词 组件名 描述` in Chinese; `Emoji Verb Component description` in English) — the same pattern you just put into `CLAUDE.md`.
- Append the PR link in the form `[#NNN](https://github.com/ant-design/ant-design/pull/NNN)`.
- Append the author link in the form `[@username](https://github.com/username)` immediately after the PR link.
- For the **English** changelog, separate the trailing PR link from the description with a single space (the description ends with `.` then a space then `[#NNN]`).
- For the **Chinese** changelog, the description ends with `。` (full-width period) and the PR link follows directly with no extra space (consistent with the existing entries in the file — look at `## 6.3.2` for reference).
- The two Image entries (`#57299`, `#57288`) are nested under a `- Image` group line, indented with two spaces. The other four entries are top-level `- ` bullets.
- The order within the section must match the table above: Image group first, then App, Form, Grid, Tree.

After your section, leave one blank line, then the existing `## 6.3.2` heading should follow unchanged.

## Output expectations

When you are done, the working tree should contain exactly five modified files:

- `CHANGELOG.en-US.md`
- `CHANGELOG.zh-CN.md`
- `CLAUDE.md`
- `.claude/skills/changelog-collect/SKILL.md`
- `package.json`

Do not modify any other files.
