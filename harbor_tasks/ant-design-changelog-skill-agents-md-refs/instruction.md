# Fix broken AGENTS.md cross-references in the changelog-collect skill

The skill file `.agents/skills/changelog-collect/SKILL.md` contains a "AGENTS.md 规范引用" (AGENTS.md spec references) section with four bulleted markdown links of the form `[label](path#anchor)` that point into the project's root `AGENTS.md`. **Both parts of every link in that section are currently broken** and need to be fixed:

1. **Path component is wrong.** The links use `./AGENTS.md`, but `SKILL.md` lives at `.agents/skills/changelog-collect/SKILL.md` — three levels deep — and there is no `AGENTS.md` next to it. The only `AGENTS.md` in the repository is at the repo root. The link path must therefore be a working relative path *from the SKILL.md file's location to the root `AGENTS.md`*.

2. **Anchor names do not match real headings.** The current anchors (`#核心原则`, `#格式与结构规范`, `#emoji-规范严格执行`, `#输出示例参考`) were copied from an older draft. Three of them no longer correspond to any heading in the root `AGENTS.md` at the current commit. Open `AGENTS.md`, look at the headings under the `## Changelog 规范` section (and its subheadings), and update each link's anchor and visible label so that:

    - The anchor (the part after `#`) is the GitHub-flavored auto-generated anchor of an actual heading that exists in `AGENTS.md`.
    - The visible label text (in `[ ]`) matches the heading text it points to. Don't keep a label that no longer matches the target.

The four bullets must remain four bullets, in the same order, with the same trailing descriptions (` - 有效性过滤规则`, ` - 分组、描述、Emoji 规范`, ` - 根据 commit 类型自动标记`, ` - 中英文格式参考`). Only the link target and the visible label of each bullet should change. Do not touch any other section of the file.

After your fix, every one of these four links must:

- Resolve to the existing root `AGENTS.md` file when interpreted as a relative path from `SKILL.md`.
- Point to an anchor whose corresponding heading actually exists in that `AGENTS.md`.

The intended targets in `AGENTS.md` are, in order: the "core principles" subsection, the "format conventions" subsection, the "emoji conventions" subsection, and the "sentence-form / output style" subsection — all of which live under the changelog-spec part of `AGENTS.md`. Use whatever heading names the file actually uses today; do not invent anchor names.
