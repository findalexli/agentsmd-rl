# Add MCP & LLMs.txt AI integration docs to Ant Design

You are working in the `ant-design/ant-design` repository at
`/workspace/antd`. The Ant Design site already ships an `LLMs.txt` guide
under `docs/react/llms.{en-US,zh-CN}.md`. Maintainers want to expand the
project's AI-integration story in three ways. Implement all three.

## 1. Add a code-style rule to `CLAUDE.md`

In the **核心规范** ("core conventions") bullet list of the repository
root `CLAUDE.md`, append a new bullet stating that **all files must end
with a newline character**, and noting that this avoids the
`final-newline` lint warning. Use the existing Chinese-language style of
the surrounding bullets and bold the rule itself (e.g. with `**…**`),
matching the formatting used on adjacent emphasised rules.

The literal phrase **`所有文件必须以换行符结尾`** must appear in the new
bullet, and the bullet must mention `final-newline` so the lint rule it
guards against is discoverable.

## 2. Create the MCP Server guide

Add two **new** files:

- `docs/react/mcp.en-US.md`
- `docs/react/mcp.zh-CN.md`

Both files share the same dumi-style frontmatter:

```yaml
---
group:
  title: AI
  order: 0.9
order: 2
title: MCP Server
tag: New
---
```

Body requirements (write the English file in English, the Chinese file
in Simplified Chinese with parallel structure):

- Open with one short sentence describing the page's purpose: explaining
  how to use Ant Design with AI tools through the Model Context Protocol.
- A `## What is MCP?` section (Chinese: `## 什么是 MCP？`) with one
  paragraph that links to the upstream protocol homepage at
  <https://modelcontextprotocol.io/>.
- A `## Community MCP Server` section (Chinese: `## 社区 MCP Server`)
  recommending the community-maintained server
  **`@jzone-mcp/antd-components-mcp`** (link it to its npm page at
  <https://www.npmjs.com/package/@jzone-mcp/antd-components-mcp>).
  Then list the four tools the server exposes:
  - `list-components` — list all available Ant Design components
  - `get-component-docs` — get documentation for a specific component
  - `list-component-examples` — get code examples for a component
  - `get-component-changelog` — get the changelog for a component
- A `## Usage with AI Tools` section (Chinese: `## 在 AI 工具中的使用`)
  containing a three-column markdown table with headers
  **Tool / Description / Prompt** (Chinese: **工具 / 说明 / 提示词**)
  and one row per tool. Every row's prompt cell must be a fenced
  configuration snippet that registers the recommended npx command
  (`npx -y @jzone-mcp/antd-components-mcp`) under an `mcpServers` key
  named `antd-components`. Cover every tool listed below in the order
  given:
  1. **Cursor**
  2. **Windsurf**
  3. **Claude Code**
  4. **Codex**
  5. **Gemini CLI**
  6. **Trae**
  7. **Qoder**
  8. **Neovate Code**
- An `## Alternative: Using LLMs.txt` section (Chinese:
  `## 备选方案：使用 LLMs.txt`) pointing readers at the existing
  LLMs.txt guide and listing `llms.txt` and `llms-full.txt` as fallback
  resources.
- A closing `## Learn More` section (Chinese: `## 了解更多`) linking to
  the MCP protocol docs, the local LLMs.txt guide, and the npm page for
  `@jzone-mcp/antd-components-mcp`.

## 3. Refactor `docs/react/llms.{en-US,zh-CN}.md`

The existing guide lists each AI tool under its own `###` subsection
with prose. Restructure it so that:

- The opening sentence no longer name-drops "Cursor, Windsurf, and
  Claude" — make it generic ("AI tools" / "AI 工具").
- The `## Available Routes` heading is renamed to `## Available
  Resources` (Chinese stays `## 可用资源`).
- Under that heading add three subsections:
  - `### LLMs.txt Aggregated Files` (Chinese: `### LLMs.txt 聚合文件`)
    presenting a two-column markdown table (**File / Description**) that
    lists, in this order:
    - `llms.txt`
    - `llms-full.txt`
    - **`llms-full-cn.txt`** *(new — Chinese full documentation)*
    - **`llms-semantic.md`** *(new — English semantic descriptions with
      DOM structure and usage patterns)*
    - **`llms-semantic-cn.md`** *(new — Chinese semantic descriptions)*
  - `### Single Component Documentation` (Chinese: `### 单个组件文档`)
    explaining the per-component `.md` URL pattern with two examples
    (English and Chinese variants of the Button component).
  - `### Semantic Documentation` (Chinese: `### 语义文档`) explaining
    the per-component `semantic.md` URL pattern with the same two
    examples and a short bullet list of what semantic docs include.
- Replace the per-tool `###` subsections under `## Usage with AI Tools`
  with a single three-column markdown table whose columns are
  **Tool / Description / Prompt** (Chinese: **工具 / 说明 / 提示词**).
  The prompt for every row is a one-line instruction that asks the AI
  to read `https://ant.design/llms-full.txt` and use it when writing
  Ant Design code.

  The table must have one row per tool, in this order, including the
  two new entries marked below:
  1. Cursor
  2. Windsurf
  3. Claude Code
  4. **Codex** *(new)*
  5. Gemini CLI
  6. Trae
  7. Qoder
  8. **Neovate Code** *(new)*

  Drop the trailing "Other AI Tools" subsection — the table replaces it.

## 4. Final-newline hygiene

Every file you touch (CLAUDE.md, both new MCP files, both refactored
LLMs.txt files) must end with a single trailing newline character — the
rule you just added in step 1.

## Code Style Requirements

This task is markdown-only — no linters or formatters are invoked by the
verifier. The repository's `final-newline` lint rule applies, so every
file you author or edit must end with a `\n`.

## What is *not* in scope

- Do not touch any source code under `components/`, `tests/`, build
  scripts, or AGENTS.md.
- Do not modify any other files in `docs/react/` beyond
  `llms.en-US.md`, `llms.zh-CN.md`, `mcp.en-US.md`, and `mcp.zh-CN.md`.
- Do not edit `CHANGELOG.*.md` — the task is documentation authoring,
  not a release.
