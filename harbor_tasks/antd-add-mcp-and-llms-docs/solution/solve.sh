#!/usr/bin/env bash
# Gold solution: applies the PR 57226 patch to /workspace/antd.
# Idempotent: skips if the distinctive line already present.

set -euo pipefail

cd /workspace/antd

# Idempotency guard — distinctive phrase from the gold diff.
if grep -q "所有文件必须以换行符结尾" CLAUDE.md 2>/dev/null \
   && [ -f docs/react/mcp.en-US.md ]; then
    echo "Patch already applied; skipping."
    exit 0
fi

cat > /tmp/pr_57226.patch <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
index 52f7d9deb906..262b05241dca 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -34,6 +34,7 @@ npm run format         # 代码格式化
 - 属性名使用小驼峰（camelCase）
 - 面板开启状态使用 `open`，避免使用 `visible`
 - 测试覆盖率要求 100%
+- **所有文件必须以换行符结尾**，避免 `final-newline` lint 警告
 
 ---
 
diff --git a/docs/react/llms.en-US.md b/docs/react/llms.en-US.md
index 829d50abf9ac..8a837c24a50f 100644
--- a/docs/react/llms.en-US.md
+++ b/docs/react/llms.en-US.md
@@ -7,57 +7,55 @@ title: LLMs.txt
 tag: New
 ---
 
-This guide explains how to enable AI tools like Cursor, Windsurf, and Claude to better understand Ant Design.
+This guide explains how to enable AI tools to better understand Ant Design.
 
 ## What is LLMs.txt?
 
 We support [LLMs.txt](https://llmstxt.org/) files for making the Ant Design documentation available to large language models (LLMs). This feature helps AI tools better understand our component library, its APIs, and usage patterns.
 
-## Available Routes
+## Available Resources
 
-We provide several LLMs.txt routes to help AI tools access our documentation:
+### LLMs.txt Aggregated Files
 
-- [llms.txt](https://ant.design/llms.txt) - Contains a structured overview of all components and their documentation links
-- [llms-full.txt](https://ant.design/llms-full.txt) - Provides comprehensive documentation including implementation details and examples
+We provide several aggregated files to help AI tools access our documentation:
 
-## Usage with AI Tools
-
-### Cursor
-
-Use the `@Docs` feature in Cursor to include the LLMs.txt files in your project. This helps Cursor provide more accurate code suggestions and documentation for Ant Design components.
-
-[Read more about @Docs in Cursor](https://docs.cursor.com/context/@-symbols/@-docs)
-
-### Windsurf
-
-Reference the LLMs.txt files using `@` or in your `.windsurf/rules` files to enhance Windsurf's understanding of Ant Design components.
+| File | Description |
+| --- | --- |
+| [llms.txt](https://ant.design/llms.txt) | Navigation file with links to all documentation and components |
+| [llms-full.txt](https://ant.design/llms-full.txt) | Complete component documentation (English) with implementation details and examples |
+| [llms-full-cn.txt](https://ant.design/llms-full-cn.txt) | Complete component documentation (Chinese) |
+| [llms-semantic.md](https://ant.design/llms-semantic.md) | Semantic component descriptions (English) with DOM structure and usage patterns |
+| [llms-semantic-cn.md](https://ant.design/llms-semantic-cn.md) | Semantic component descriptions (Chinese) |
 
-[Read more about Windsurf Memories](https://docs.windsurf.com/windsurf/cascade/memories)
+### Single Component Documentation
 
-### Claude Code
+Access individual component documentation with `.md` suffix:
 
-In Claude Code, add `LLMs.txt` to the workspace Knowledge Base (Docs / Context Files) configuration. This allows the file to be referenced during code completion and explanation, improving understanding of Ant Design components.
+- `https://ant.design/components/button.md` (English)
+- `https://ant.design/components/button-cn.md` (Chinese)
 
-[Learn more about Claude Code document context configuration](https://code.claude.com/docs)
+### Semantic Documentation
 
-### Gemini CLI
+Each component has a semantic description file:
 
-In Gemini CLI, you can specify the `LLMs.txt` file path with the `--context` parameter or in `.gemini/config.json`, enabling Gemini to reference the document when answering or generating code.
+- `https://ant.design/components/button/semantic.md` (English)
+- `https://ant.design/components/button-cn/semantic.md` (Chinese)
 
-[Learn more about Gemini CLI context configuration](https://ai.google.dev/gemini-api/docs?hl=en)
+Semantic documentation includes:
+- Component parts and their purposes
+- Usage examples and best practices
+- DOM structure overview
 
-### Trae
-
-In Trae, place the `LLMs.txt` file into the project’s knowledge sources and enable referencing in the settings. This allows Trae to better support Ant Design components when generating or analyzing code.
-
-[Learn more about Trae knowledge sources](https://trae.ai/docs)
-
-### Qoder
-
-In Qoder, you can add `LLMs.txt` as an external knowledge file in `.qoder/config.yml`, or temporarily reference it in a conversation with `@docs LLMs.txt`, enhancing support for Ant Design components.
-
-[Learn more about Qoder configuration](https://docs.qoder.com/)
+## Usage with AI Tools
 
-### Other AI Tools
+| Tool | Description | Prompt |
+| --- | --- | --- |
+| **Cursor** | Use `@Docs` feature to include LLMs.txt, or add prompt to `.cursor/rules`. [Documentation](https://docs.cursor.com/context/@-symbols/@-docs) | `Read https://ant.design/llms-full.txt and understand Ant Design components. Use this knowledge when writing code with Ant Design.` |
+| **Windsurf** | Add prompt to `.windsurf/rules` or use cascade memories. [Documentation](https://docs.windsurf.com/windsurf/cascade/memories) | `Read https://ant.design/llms-full.txt and understand Ant Design components. Use this knowledge when writing code with Ant Design.` |
+| **Claude Code** | Add to CLAUDE.md or use `/memory` to persist. [Documentation](https://docs.anthropic.com/en/docs/claude-code) | `Read https://ant.design/llms-full.txt and understand Ant Design components. Use this knowledge when writing code with Ant Design.` |
+| **Codex** | Add to `.codex/settings.json` or AGENTS.md. [Documentation](https://github.com/openai/codex) | `Read https://ant.design/llms-full.txt and understand Ant Design components. Use this knowledge when writing code with Ant Design.` |
+| **Gemini CLI** | Use `--context` parameter or add to `.gemini/config.json`. [Documentation](https://ai.google.dev/gemini-api/docs?hl=en) | `Read https://ant.design/llms-full.txt and understand Ant Design components. Use this knowledge when writing code with Ant Design.` |
+| **Trae** | Add to project's knowledge sources in settings. [Documentation](https://trae.ai/docs) | `Read https://ant.design/llms-full.txt and understand Ant Design components. Use this knowledge when writing code with Ant Design.` |
+| **Qoder** | Add to `.qoder/config.yml` or use `@docs` in conversation. [Documentation](https://docs.qoder.com/) | `Read https://ant.design/llms-full.txt and understand Ant Design components. Use this knowledge when writing code with Ant Design.` |
+| **Neovate Code** | Run `neovate` and describe task with prompt. [Documentation](https://github.com/neovateai/neovate-code) | `Read https://ant.design/llms-full.txt and understand Ant Design components. Use this knowledge when writing code with Ant Design.` |
 
-Any AI tool that supports LLMs.txt can use these routes to better understand Ant Design. Simply point your tool to any of the routes above.
diff --git a/docs/react/llms.zh-CN.md b/docs/react/llms.zh-CN.md
index a9e81cb11620..bd3663062ae2 100644
--- a/docs/react/llms.zh-CN.md
+++ b/docs/react/llms.zh-CN.md
@@ -7,7 +7,7 @@ title: LLMs.txt
 tag: New
 ---
 
-本指南介绍如何让 Cursor、Windsurf 和 Claude 等 AI 工具更好地理解 Ant Design。
+本指南介绍如何让 AI 工具更好地理解 Ant Design。
 
 ## 什么是 LLMs.txt？
 
@@ -15,49 +15,47 @@ tag: New
 
 ## 可用资源
 
-我们提供多个 LLMs.txt 路由来帮助 AI 工具访问文档：
+### LLMs.txt 聚合文件
 
-- [llms.txt](https://ant.design/llms.txt) - 包含所有组件及其文档链接的结构化概览
-- [llms-full.txt](https://ant.design/llms-full.txt) - 提供包含实现细节和示例的完整文档
+我们提供多个聚合文件来帮助 AI 工具访问文档：
 
-## 在 AI 工具中的使用
-
-### Cursor
-
-在 Cursor 中使用 `@Docs` 功能将 LLMs.txt 文件包含到您的项目中。这有助于 Cursor 为 Ant Design 组件提供更准确的代码建议和文档。
-
-[详细了解 Cursor 中的 @Docs 功能](https://docs.cursor.com/zh/context/@-symbols/@-docs)
-
-### Windsurf
-
-通过 `@` 引用或在 `.windsurf/rules` 文件中配置 LLMs.txt 文件，以增强 Windsurf 对 Ant Design 组件的理解。
+| 文件 | 说明 |
+| --- | --- |
+| [llms.txt](https://ant.design/llms.txt) | 导航文件，包含所有文档和组件的链接 |
+| [llms-full.txt](https://ant.design/llms-full.txt) | 完整的组件文档（英文），包含实现细节和示例 |
+| [llms-full-cn.txt](https://ant.design/llms-full-cn.txt) | 完整的组件文档（中文） |
+| [llms-semantic.md](https://ant.design/llms-semantic.md) | 组件语义描述（英文），包含 DOM 结构和使用模式 |
+| [llms-semantic-cn.md](https://ant.design/llms-semantic-cn.md) | 组件语义描述（中文） |
 
-[详细了解 Windsurf Memories 功能](https://docs.windsurf.com/windsurf/cascade/memories)
+### 单个组件文档
 
-### Claude Code
+通过 `.md` 后缀直接访问单个组件文档：
 
-在 Claude Code 中，将 `LLMs.txt` 添加到工作区的知识库（Docs / Context Files）配置中，即可在代码补全与解释时引用其中的内容，从而提升对 Ant Design 组件的理解。
+- `https://ant.design/components/button.md`（英文）
+- `https://ant.design/components/button-cn.md`（中文）
 
-[详细了解 Claude Code 文档上下文配置](https://code.claude.com/docs)
+### 语义文档
 
-### Gemini CLI
+每个组件都有对应的语义描述文件：
 
-在 Gemini CLI 中，可以通过 `--context` 参数或在 `.gemini/config.json` 中指定 `LLMs.txt` 文件路径，让 Gemini 在回答和生成代码时参考该文档。
+- `https://ant.design/components/button/semantic.md`（英文）
+- `https://ant.design/components/button-cn/semantic.md`（中文）
 
-[详细了解 Gemini CLI 上下文配置](https://ai.google.dev/gemini-api/docs?hl=zh-cn)
+语义文档包含：
+- 组件部件及其用途
+- 使用示例和最佳实践
+- DOM 结构概览
 
-### Trae
-
-在 Trae 中，将 `LLMs.txt` 文件放入项目的 knowledge sources 并在设置里开启引用，即可让 Trae 在生成或分析代码时更好地支持 Ant Design 组件。
-
-[详细了解 Trae 的知识源功能](https://trae.ai/docs)
-
-### Qoder
-
-在 Qoder 中，可以在 `.qoder/config.yml` 中添加 `LLMs.txt` 作为外部知识文件，或在对话中通过 `@docs LLMs.txt` 进行临时引用，增强对 Ant Design 组件的支持。
-
-[详细了解 Qoder 配置方法](https://docs.qoder.com/)
+## 在 AI 工具中的使用
 
-### 其他 AI 工具
+| 工具 | 说明 | 提示词 |
+| --- | --- | --- |
+| **Cursor** | 使用 `@Docs` 功能引入 LLMs.txt，或添加提示词到 `.cursor/rules`。[文档](https://docs.cursor.com/zh/context/@-symbols/@-docs) | `阅读 https://ant.design/llms-full.txt 并理解 Ant Design 组件库，在编写 Ant Design 代码时使用这些知识。` |
+| **Windsurf** | 添加提示词到 `.windsurf/rules` 或使用 cascade memories。[文档](https://docs.windsurf.com/windsurf/cascade/memories) | `阅读 https://ant.design/llms-full.txt 并理解 Ant Design 组件库，在编写 Ant Design 代码时使用这些知识。` |
+| **Claude Code** | 添加到 CLAUDE.md 或使用 `/memory` 持久化。[文档](https://docs.anthropic.com/en/docs/claude-code) | `阅读 https://ant.design/llms-full.txt 并理解 Ant Design 组件库，在编写 Ant Design 代码时使用这些知识。` |
+| **Codex** | 添加到 `.codex/settings.json` 或 AGENTS.md。[文档](https://github.com/openai/codex) | `阅读 https://ant.design/llms-full.txt 并理解 Ant Design 组件库，在编写 Ant Design 代码时使用这些知识。` |
+| **Gemini CLI** | 使用 `--context` 参数或添加到 `.gemini/config.json`。[文档](https://ai.google.dev/gemini-api/docs?hl=zh-cn) | `阅读 https://ant.design/llms-full.txt 并理解 Ant Design 组件库，在编写 Ant Design 代码时使用这些知识。` |
+| **Trae** | 添加到项目的知识源设置中。[文档](https://trae.ai/docs) | `阅读 https://ant.design/llms-full.txt 并理解 Ant Design 组件库，在编写 Ant Design 代码时使用这些知识。` |
+| **Qoder** | 添加到 `.qoder/config.yml` 或在对话中使用 `@docs`。[文档](https://docs.qoder.com/) | `阅读 https://ant.design/llms-full.txt 并理解 Ant Design 组件库，在编写 Ant Design 代码时使用这些知识。` |
+| **Neovate Code** | 运行 `neovate` 并使用提示词描述任务。[文档](https://github.com/neovateai/neovate-code) | `阅读 https://ant.design/llms-full.txt 并理解 Ant Design 组件库，在编写 Ant Design 代码时使用这些知识。` |
 
-任何支持 LLMs.txt 的 AI 工具均可使用以上路径来更好地理解 Ant Design。
diff --git a/docs/react/mcp.en-US.md b/docs/react/mcp.en-US.md
new file mode 100644
index 000000000000..7c496c4a8cdb
--- /dev/null
+++ b/docs/react/mcp.en-US.md
@@ -0,0 +1,52 @@
+---
+group:
+  title: AI
+  order: 0.9
+order: 2
+title: MCP Server
+tag: New
+---
+
+This guide explains how to use Ant Design with AI tools through Model Context Protocol (MCP).
+
+## What is MCP?
+
+[Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is an open protocol that enables AI models to interact with external tools and data sources. Through MCP, AI assistants can access real-time documentation, code examples, and API references.
+
+## Community MCP Server
+
+Ant Design recommends the community-maintained MCP server: [`@jzone-mcp/antd-components-mcp`](https://www.npmjs.com/package/@jzone-mcp/antd-components-mcp)
+
+This MCP server provides the following capabilities:
+
+- **list-components** - List all available Ant Design components
+- **get-component-docs** - Get detailed documentation for a specific component
+- **list-component-examples** - Get code examples for a component
+- **get-component-changelog** - Get the changelog for a component
+
+## Usage with AI Tools
+
+| Tool | Description | Prompt |
+| --- | --- | --- |
+| **Cursor** | Add to `.cursor/mcp.json` or Settings → Features → MCP. [Documentation](https://docs.cursor.com/context/@-symbols/@-docs) | `Add Ant Design MCP server. Configuration: { "mcpServers": { "antd-components": { "command": "npx", "args": ["-y", "@jzone-mcp/antd-components-mcp"] } } }` |
+| **Windsurf** | Add to `~/.codeium/windsurf/mcp_config.json`. [Documentation](https://docs.windsurf.com/windsurf/cascade/memories) | `Add Ant Design MCP server. Configuration: { "mcpServers": { "antd-components": { "command": "npx", "args": ["-y", "@jzone-mcp/antd-components-mcp"] } } }` |
+| **Claude Code** | Add to `mcpServers` in Claude settings. [Documentation](https://docs.anthropic.com/en/docs/claude-code) | `Add Ant Design MCP server. Configuration: { "mcpServers": { "antd-components": { "command": "npx", "args": ["-y", "@jzone-mcp/antd-components-mcp"] } } }` |
+| **Codex** | Add to `.codex/mcp.json`. [Documentation](https://github.com/openai/codex) | `Add Ant Design MCP server. Configuration: { "mcpServers": { "antd-components": { "command": "npx", "args": ["-y", "@jzone-mcp/antd-components-mcp"] } } }` |
+| **Gemini CLI** | Add to MCP configuration. [Documentation](https://ai.google.dev/gemini-api/docs?hl=en) | `Add Ant Design MCP server. Configuration: { "mcpServers": { "antd-components": { "command": "npx", "args": ["-y", "@jzone-mcp/antd-components-mcp"] } } }` |
+| **Trae** | Add to MCP settings. [Documentation](https://www.trae.ai/docs) | `Add Ant Design MCP server. Configuration: { "mcpServers": { "antd-components": { "command": "npx", "args": ["-y", "@jzone-mcp/antd-components-mcp"] } } }` |
+| **Qoder** | Add to MCP configuration. [Documentation](https://docs.qoder.com/) | `Add Ant Design MCP server. Configuration: { "mcpServers": { "antd-components": { "command": "npx", "args": ["-y", "@jzone-mcp/antd-components-mcp"] } } }` |
+| **Neovate Code** | Configure MCP in settings or describe task with prompt. [Documentation](https://github.com/neovateai/neovate-code) | `Add Ant Design MCP server. Configuration: { "mcpServers": { "antd-components": { "command": "npx", "args": ["-y", "@jzone-mcp/antd-components-mcp"] } } }` |
+
+## Alternative: Using LLMs.txt
+
+If your AI tool doesn't support MCP, you can use our [LLMs.txt](/docs/react/llms-en-US) support instead. We provide:
+
+- [llms.txt](https://ant.design/llms.txt) - Structured overview of all components
+- [llms-full.txt](https://ant.design/llms-full.txt) - Complete documentation with examples
+
+## Learn More
+
+- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
+- [Ant Design LLMs.txt Guide](/docs/react/llms-en-US)
+- [@jzone-mcp/antd-components-mcp on npm](https://www.npmjs.com/package/@jzone-mcp/antd-components-mcp)
+
diff --git a/docs/react/mcp.zh-CN.md b/docs/react/mcp.zh-CN.md
new file mode 100644
index 000000000000..5c7e49621a62
--- /dev/null
+++ b/docs/react/mcp.zh-CN.md
@@ -0,0 +1,52 @@
+---
+group:
+  title: AI
+  order: 0.9
+order: 2
+title: MCP Server
+tag: New
+---
+
+本指南介绍如何通过 Model Context Protocol (MCP) 在 AI 工具中使用 Ant Design。
+
+## 什么是 MCP？
+
+[Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 是一个开放协议，使 AI 模型能够与外部工具和数据源进行交互。通过 MCP，AI 助手可以访问实时文档、代码示例和 API 参考资料。
+
+## 社区 MCP Server
+
+Ant Design 推荐使用社区维护的 MCP server：[`@jzone-mcp/antd-components-mcp`](https://www.npmjs.com/package/@jzone-mcp/antd-components-mcp)
+
+该 MCP server 提供以下功能：
+
+- **list-components** - 列出所有可用的 Ant Design 组件
+- **get-component-docs** - 获取指定组件的详细文档
+- **list-component-examples** - 获取组件的代码示例
+- **get-component-changelog** - 获取组件的更新日志
+
+## 在 AI 工具中的使用
+
+| 工具 | 说明 | 提示词 |
+| --- | --- | --- |
+| **Cursor** | 添加到 `.cursor/mcp.json` 或设置 → 功能 → MCP。[文档](https://docs.cursor.com/zh/context/@-symbols/@-docs) | `添加 Ant Design MCP 服务器。配置: { "mcpServers": { "antd-components": { "command": "npx", "args": ["-y", "@jzone-mcp/antd-components-mcp"] } } }` |
+| **Windsurf** | 添加到 `~/.codeium/windsurf/mcp_config.json`。[文档](https://docs.windsurf.com/windsurf/cascade/memories) | `添加 Ant Design MCP 服务器。配置: { "mcpServers": { "antd-components": { "command": "npx", "args": ["-y", "@jzone-mcp/antd-components-mcp"] } } }` |
+| **Claude Code** | 添加到 Claude 设置的 `mcpServers`。[文档](https://docs.anthropic.com/en/docs/claude-code) | `添加 Ant Design MCP 服务器。配置: { "mcpServers": { "antd-components": { "command": "npx", "args": ["-y", "@jzone-mcp/antd-components-mcp"] } } }` |
+| **Codex** | 添加到 `.codex/mcp.json`。[文档](https://github.com/openai/codex) | `添加 Ant Design MCP 服务器。配置: { "mcpServers": { "antd-components": { "command": "npx", "args": ["-y", "@jzone-mcp/antd-components-mcp"] } } }` |
+| **Gemini CLI** | 添加到 MCP 配置。[文档](https://ai.google.dev/gemini-api/docs?hl=zh-cn) | `添加 Ant Design MCP 服务器。配置: { "mcpServers": { "antd-components": { "command": "npx", "args": ["-y", "@jzone-mcp/antd-components-mcp"] } } }` |
+| **Trae** | 添加到 MCP 设置。[文档](https://www.trae.ai/docs) | `添加 Ant Design MCP 服务器。配置: { "mcpServers": { "antd-components": { "command": "npx", "args": ["-y", "@jzone-mcp/antd-components-mcp"] } } }` |
+| **Qoder** | 添加到 MCP 配置。[文档](https://docs.qoder.com/) | `添加 Ant Design MCP 服务器。配置: { "mcpServers": { "antd-components": { "command": "npx", "args": ["-y", "@jzone-mcp/antd-components-mcp"] } } }` |
+| **Neovate Code** | 在设置中配置 MCP 或使用提示词描述任务。[文档](https://github.com/neovateai/neovate-code) | `添加 Ant Design MCP 服务器。配置: { "mcpServers": { "antd-components": { "command": "npx", "args": ["-y", "@jzone-mcp/antd-components-mcp"] } } }` |
+
+## 备选方案：使用 LLMs.txt
+
+如果您的 AI 工具不支持 MCP，可以使用我们的 [LLMs.txt](/docs/react/llms-zh-CN) 支持。我们提供：
+
+- [llms.txt](https://ant.design/llms.txt) - 所有组件的结构化概览
+- [llms-full.txt](https://ant.design/llms-full.txt) - 包含示例的完整文档
+
+## 了解更多
+
+- [Model Context Protocol 文档](https://modelcontextprotocol.io/)
+- [Ant Design LLMs.txt 指南](/docs/react/llms-zh-CN)
+- [@jzone-mcp/antd-components-mcp npm 地址](https://www.npmjs.com/package/@jzone-mcp/antd-components-mcp)
+
PATCH

# Apply the patch. Use git apply (works on a git working tree).
git apply --whitespace=nowarn /tmp/pr_57226.patch

echo "Gold patch applied."
