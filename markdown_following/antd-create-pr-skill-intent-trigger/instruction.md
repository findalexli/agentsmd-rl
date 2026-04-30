# Refine the create-pr skill so it triggers by intent, not by phrase

The repository's `.agents/skills/create-pr/SKILL.md` file tells AI coding
assistants when to enter the "create a pull request" workflow for ant-design.
The current version triggers on a hard-coded list of specific phrases, which
is brittle: every new colloquial way to ask for a PR requires another
phrase, and the skill mis-fires on text that merely *discusses* PRs.

## What is wrong today

Two pieces of the file are phrase-based and need to become intent-based:

### 1. The frontmatter `description`

The current `description:` field reads (verbatim):

> Create pull requests for ant-design using the repository's official PR
> templates. **Use when the user asks to create a PR, open a pull request,
> write PR title/body, summarize branch changes for a PR, or prepare an
> ant-design PR in Chinese or English.** The skill must choose
> `.github/PULL_REQUEST_TEMPLATE_CN.md` or `.github/PULL_REQUEST_TEMPLATE.md`
> based on the user's language habit and keep the content aligned with
> ant-design's PR sections.

The bolded enumeration of trigger situations must be replaced with intent-based
guidance. The new `description` must:

- Direct the assistant to use the skill whenever the user asks to create or
  open a PR, draft PR title/body, summarize branch changes for a PR, or
  otherwise prepare PR content.
- Contain the literal English phrase **`Judge by intent rather than fixed phrases`**.
- Explicitly note that short colloquial requests still count when the user
  is asking to create a PR rather than just discussing PR concepts.

The old "Use when the user asks to create a PR, open a pull request, write PR
title/body, summarize branch changes for a PR, or prepare an ant-design PR
in Chinese or English" wording must not appear anymore.

### 2. The `## 触发场景` section

The body has a `## 触发场景` ("trigger scenarios") section that lists ~20
specific Chinese and English trigger phrases:

```
- 创建 PR、发起 pull request
- 写 PR 标题或 PR 描述
- 总结当前分支改动用于提 PR
- 用 `gh pr create` 为 `ant-design` 开 PR
…
- 中文：`创建pr`、`创建 PR`、`开pr`、`开个pr`、`提pr`、`提个pr`、
  `帮我提个pr`、`发pr`、`写pr`、`准备pr`。
- 英文：`create pr`、`create a pr`、`open pr`、`open a pr`、`submit pr`、
  `send pr`、`draft pr`、`prepare pr`、`help me create a pr`、
  `open a pull request`。

这类短句默认表示：先分析当前分支改动并整理待确认的 `base`、`title`、`body`
草稿，等用户确认后再真正创建 PR。
```

The whole `## 触发场景` section (the heading itself, both bullet lists, and
the "这类短句默认表示…" paragraph) must be deleted.

## What the file should look like after your edit

1. **Updated frontmatter `description`** as described above (must contain
   `Judge by intent rather than fixed phrases`; must not contain the old
   "Use when the user asks to create a PR, open a pull request, write PR
   title/body, summarize branch changes for a PR, or prepare an ant-design
   PR in Chinese or English" phrase).

2. **No `## 触发场景` section.** None of the hard-coded trigger fragments
   should remain — including `创建 PR、发起 pull request`, `` `帮我提个pr` ``,
   `` `help me create a pr` ``, and the closing line that begins
   `这类短句默认表示`.

3. **A new `### 一、按意图触发，不按短语触发` subsection** at the **top** of
   the existing `## 基本规则` section. Its body (in Chinese) must:
   - Explain that the skill should be used whenever the user's intent is to
     request creating a PR or to prepare for creating a PR. The sentence
     `只要能判断用户是在请求创建 PR，或为创建 PR 做准备，就应使用本 skill。`
     captures this.
   - Instruct the reader **not to limit triggering to fixed phrases** —
     short, colloquial, or incomplete user messages should still enter the
     workflow as long as the user is not merely discussing PR concepts.
     The sentence `不要把触发限制成固定说法。` opens this paragraph.

4. **The existing six rule subsections must be renumbered.** Because the new
   intent-triggering rule is now `### 一`, the rules that follow must shift
   from 一-六 to 二-七. After your edit, the headings inside `## 基本规则`
   must read, in this order:

   - `### 一、按意图触发，不按短语触发` (new)
   - `### 二、必须以仓库模板为准`
   - `### 三、模板语言由用户习惯决定，但标题固定英文`
   - `### 四、先分析分支，再写 PR`
   - `### 五、先给草稿，后创建 PR`
   - `### 六、标题和正文要分工明确`
   - `### 七、信息不足时不要硬写`

   The body content under each renumbered rule must remain otherwise
   unchanged. Do not rewrite or trim the rule bodies; only the heading
   numerals change.

The rest of the file (the `# Ant Design PR 创建规范` H1, the `## 目标`
section, the `## 执行步骤` section, the `## 写法要求` section, and the
`## 参考` footer) must be left intact.
