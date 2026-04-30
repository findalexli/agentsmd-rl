# Update Ant Design's CLAUDE.md emoji policy and apply it

You are working in `/workspace/ant-design`, a checkout of
[ant-design/ant-design](https://github.com/ant-design/ant-design) at base
commit `f24ee27f7bd10d9f56f9293e129496e1c2188ef1`.

## Background

`CLAUDE.md` at the repository root is the project's agent-instructions file.
Inside it, the `## Changelog 规范` section documents the conventions for
authoring entries in `CHANGELOG.en-US.md` and `CHANGELOG.zh-CN.md`. The
section lists an Emoji table that maps emojis to entry categories.

A subtle inconsistency has crept in: the table shows `⌨️ ♿` as the marker
for accessibility-related changes, and a few entries in the *unreleased*
section of both changelog files use that two-emoji prefix. Maintainers want
the project to standardize on **one emoji per changelog entry** to keep the
visual rhythm consistent across the file.

## What you must do

1. **Add a rule to `CLAUDE.md`** stating that each Changelog entry must
   select only a single emoji and that multiple emojis must not be stacked
   on the same entry. Use Chinese (matching the rest of the document). The
   exact wording you must add is:

   ```
   每条 Changelog 仅选择一个 Emoji，不要在同一条目中叠加多个 Emoji。
   ```

   Place this new rule inside the `## Changelog 规范` section, after the
   Emoji table and before the existing line that begins
   `编写 Changelog 时，请参考 …`. Surround it with blank lines so it reads
   as its own paragraph.

2. **Apply the new rule to the unreleased changelog entries.** Locate the
   single existing entry in *each* of `CHANGELOG.en-US.md` and
   `CHANGELOG.zh-CN.md` whose unreleased section currently uses two stacked
   emojis (`⌨️ ♿`) — it is the entry that links to pull request `#57266`
   (the App-component `:focus-visible` accessibility improvement). Drop the
   redundant `♿`; keep the `⌨️`. Do not change any of the body text, link,
   or contributor mention. After your edit, the resulting English line must
   read exactly:

   ```
   - ⌨️ Improve App link `:focus-visible` outline to enhance keyboard accessibility. [#57266](https://github.com/ant-design/ant-design/pull/57266) [@ug-hero](https://github.com/ug-hero)
   ```

   And the resulting Chinese line must read exactly:

   ```
   - ⌨️ 优化 App 链接的 `:focus-visible` 外框样式，提升键盘可访问性。[#57266](https://github.com/ant-design/ant-design/pull/57266) [@ug-hero](https://github.com/ug-hero)
   ```

## What you must NOT do

- **Do not modify older, already-released entries** further down the
  changelog files. Several of them (referencing PRs #56902, #56521, #56716,
  etc.) also use `⌨️ ♿` — they are historical and must stay as-is. The
  new convention applies only to the unreleased section.
- **Do not alter the Emoji table itself** in `CLAUDE.md`. The row
  `| ⌨️ ♿  | 可访问性增强  |` stays untouched in this PR.
- **Do not introduce unrelated edits** to either changelog file. The
  expected diff is exactly +1 / −1 line per changelog file.
- **Do not edit only one of the two languages.** Per the existing
  Changelog 规范 in `CLAUDE.md`, changelog updates must always be applied
  bilingually.

## Files in scope

- `CLAUDE.md`
- `CHANGELOG.en-US.md`
- `CHANGELOG.zh-CN.md`

No other files should change.
