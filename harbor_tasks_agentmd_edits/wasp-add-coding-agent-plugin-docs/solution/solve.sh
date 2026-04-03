#!/usr/bin/env bash
set -euo pipefail

cd /workspace/wasp

# Idempotent: skip if already applied
if grep -q 'AI Agent Plugins' README.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Remove old binary files
rm -f web/docs/wasp-ai/wasp-ai-1.png web/docs/wasp-ai/wasp-ai-2.png

# Apply text changes
git apply --whitespace=fix - <<'PATCH'
diff --git a/README.md b/README.md
index 3cda51680e..8faf4ee062 100644
--- a/README.md
+++ b/README.md
@@ -123,9 +123,9 @@ For a quick start, check out [this docs page](https://wasp.sh/docs/quick-start).

 If you have a Wasp application running in production, we'd love to send some swag your way! Fill out [this form](https://e44cy1h4s0q.typeform.com/to/EPJCwsMi), and we'll make it happen.

-## Wasp AI / Mage
+## AI Agent Plugins

-Wasp comes with experimental AI code generator to help you kickstart your next Wasp project. You can use it via `wasp new` in the CLI (select the `ai-generated` option) if you provide your OpenAI keys. Alternatively, you can use our [Mage web app](https://usemage.ai), in which case our OpenAI keys are used in the background.
+Wasp has official AI agent plugins to help you kickstart your next Wasp project. You can use them with your favorite AI-assisted coding tool (Cursor, Claude Code, etc.) to get a better result and development experience. Check out the [Wasp Agent Plugins](https://wasp.sh/docs/wasp-ai/coding-agent-plugin) page for more details.

 ## Project status

diff --git a/web/docs/introduction/quick-start.md b/web/docs/introduction/quick-start.md
index 4306b8e768..11b8d659b1 100644
--- a/web/docs/introduction/quick-start.md
+++ b/web/docs/introduction/quick-start.md
@@ -32,16 +32,32 @@ Let's create and run our first Wasp app in 3 short steps:
    wasp start
    ```

-That's it 🎉 You have successfully created and served a new full-stack web app at [http://localhost:3000](http://localhost:3000) and Wasp is serving both frontend and backend for you.
+That's it 🎉 You have successfully created a new full-stack web app at [http://localhost:3000](http://localhost:3000) and Wasp is serving both frontend and backend for you.
+
+But don't stop there! Turn your coding agent into a Wasp framework expert in the next step.
+
+4. **Install Agent Plugin / Skills:**
+
+   **Claude Code:**
+    ```bash
+    claude plugin marketplace add wasp-lang/wasp-agent-plugins
+    claude plugin install wasp@wasp-agent-plugins --scope project
+    ```
+   **Other Agents (Cursor, Codex, Gemini, Copilot, OpenCode, etc.):**
+    ```bash
+    npx skills add wasp-lang/wasp-agent-plugins
+    ```
+    **Initialize the plugin / skills:**
+    Invoke the `/wasp-plugin-init` skill to add Wasp knowledge to your agent's memory file (e.g. `CLAUDE.md`, `AGENTS.md`):
+    ```bash
+    Run the '/wasp-plugin-init' skill.
+    ```
+   For more info check out the [Wasp Agent Plugin / Skills](../wasp-ai/coding-agent-plugin.md) page.

 :::note Something Unclear?
 Check [More Details](#more-details) section below if anything went wrong with the installation, or if you have additional questions.
 :::

-:::tip Want an even faster start?
-Try out [Wasp AI](../wasp-ai/creating-new-app.md) 🤖 to generate a new Wasp app in minutes just from a title and short description!
-:::
-
 :::tip Having trouble running Wasp?
   If you get stuck with a weird error while developing with Wasp, try running `wasp clean` - this is the Wasp equivalent of "turning it off and on again"!
   Do however let us know about the issue on our GitHub repo or Discord server.
diff --git a/web/docs/wasp-ai/creating-new-app.md b/web/docs/wasp-ai/creating-new-app.md
deleted file mode 100644
index ecbd29105d..0000000000
--- a/web/docs/wasp-ai/creating-new-app.md
+++ /dev/null
@@ -1,45 +0,0 @@
----
-title: Creating New App with AI
----
-
-import useBaseUrl from '@docusaurus/useBaseUrl';
-
-import { ImgWithCaption } from '@site/blog/components/ImgWithCaption'
-
-Wasp comes with its own AI: Wasp AI, aka Mage (**M**agic web **A**pp **GE**nerator).
-
-Wasp AI allows you to create a new Wasp app **from only a title and a short description** (using GPT in the background)!
-
-There are two main ways to create a new Wasp app with Wasp AI:
-
-1. Free, open-source online app [usemage.ai](https://usemage.ai).
-2. Running `wasp new` on your machine and picking AI generation. For this you need to provide your own OpenAI API keys, but it allows for more flexibility (choosing GPT models).
-
-They both use the same logic in the background, so both approaches are equally "smart", the difference is just in the UI / settings.
-
-:::info
-Wasp AI is an experimental feature. Apps that Wasp AI generates can have mistakes (proportional to their complexity), but even then they can often serve as a great starting point (once you fix the mistakes) or an interesting way to explore how to implement stuff in Wasp.
-:::
-
-## usemage.ai
-
-<ImgWithCaption source="img/gpt-wasp/how-it-works.gif" caption="1. Describe your app 2. Pick the color 3. Generate your app 🚀" />
-
-[Mage](https://usemage.ai) is an open-source app with which you can create new Wasp apps from just a short title and description.
-
-It is completely free for you - it uses our OpenAI API keys and we take on the costs.
-
-Once you provide an app title, app description, and choose some basic settings, your new Wasp app will be created for you in a matter of minutes and you will be able to download it to your machine and keep working on it!
-
-If you want to know more, check this [blog post](/blog/2023/07/10/gpt-web-app-generator) for more details on how Mage works, or this [blog post](/blog/2023/07/17/how-we-built-gpt-web-app-generator) for a high-level overview of how we implemented it.
-
-## Wasp CLI
-
-You can create a new Wasp app using Wasp AI by running `wasp new` in your terminal and picking AI generation.
-
-If you don't have them set yet, `wasp` will ask you to provide (via ENV vars) your OpenAI API keys (which it will use to query GPT).
-
-Then, after providing a title and description for your Wasp app, the new app will be generated on your disk!
-
-![wasp-cli-ai-input](./wasp-ai-1.png)
-![wasp-cli-ai-generation](./wasp-ai-2.png)
diff --git a/web/docs/wasp-ai/developing-existing-app.md b/web/docs/wasp-ai/developing-existing-app.md
deleted file mode 100644
index b9e3566292..0000000000
--- a/web/docs/wasp-ai/developing-existing-app.md
+++ /dev/null
@@ -1,9 +0,0 @@
----
-title: Developing Existing App with AI
----
-
-import useBaseUrl from '@docusaurus/useBaseUrl';
-
-While Wasp AI doesn't at the moment offer any additional help for developing your Wasp app with AI beyond initial generation, this is something we are exploring actively.
-
-In the meantime, while waiting for Wasp AI to add support for this, we suggest checking out [aider](https://github.com/paul-gauthier/aider), which is an AI pair programming tool in your terminal. This is a third-party tool, not affiliated with Wasp in any way, but we and some of Wasp users have found that it can be helpful when working on Wasp apps.
diff --git a/web/sidebars.ts b/web/sidebars.ts
index 7f94357696..ba8edac7e0 100644
--- a/web/sidebars.ts
+++ b/web/sidebars.ts
@@ -157,10 +157,10 @@ const sidebars: SidebarsConfig = {
     },
     {
       type: "category",
-      label: "Wasp AI",
+      label: "AI & Coding Agents",
       collapsed: false,
       collapsible: true,
-      items: ["wasp-ai/creating-new-app", "wasp-ai/developing-existing-app"],
+      items: ["wasp-ai/coding-agent-plugin"],
     },
     {
       type: "category",

PATCH

# Create the new coding-agent-plugin.md page
cat > web/docs/wasp-ai/coding-agent-plugin.md <<'NEWPAGE'
---
title: Agent Plugin / Skills
---

Wasp provides an official plugin for coding agents that transforms them into Wasp framework experts.

The plugin gives your agent curated access to Wasp docs, workflows, and best practices so it can develop full-stack web apps (React, Node.js, Prisma) more effectively.

The plugin / skills work with just about all the popular coding agents, such as [Claude Code](https://claude.com/product/claude-code), [Cursor](https://www.cursor.com/), [Codex](https://openai.com/codex/), [Gemini CLI](https://geminicli.com/), [GitHub Copilot](https://github.com/features/copilot/cli), [OpenCode](https://opencode.ai/), and more.

## Features

- **Wasp Documentation** — Ensures your agent always accesses LLM-friendly Wasp docs in sync with your current project's Wasp version.
- **Wasp Knowledge** — Imports Wasp best practices and conventions into your project's memory file (e.g. `CLAUDE.md`, `AGENTS.md`).
- **Feature Configuration** — Easily add Wasp features like authentication, database, email, styling (Tailwind, shadcn/ui), and other integrations through your agent.
- **Deployment Guidance** — Your agent will guide you through deploying your Wasp app to Railway or Fly.io via the Wasp CLI, or manually to your favorite cloud provider.

## Installation

### Claude Code

First, add the Wasp plugin marketplace:

```bash
claude plugin marketplace add wasp-lang/wasp-agent-plugins
```

Then install the Wasp plugin:

```bash
claude plugin install wasp@wasp-agent-plugins --scope project
```

:::tip
We recommend installing with `project` scope so the settings are committed to git (via `settings.json`). Use `local` scope if you prefer settings that aren't committed (via `settings.local.json`).
:::

### Other Agents (Cursor, Codex, Gemini, Copilot, OpenCode, etc.)

Run the following command and select all the skills:

```bash
npx skills add wasp-lang/wasp-agent-plugins
```

## Setup

After installing, initialize the plugin in an active agent session by explicitly invoking the `/wasp-plugin-init` skill:

```
Run the '/wasp-plugin-init' skill.
```

This adds Wasp knowledge to your project's `CLAUDE.md` or `AGENTS.md` file.

Next, start the development server as a background task so your agent has full insight into the running app while developing:

```
Run the 'start-dev-server' skill.
```

To see all available features and skills:

```
/wasp-plugin-help
```

## Learn More

Check out the [Wasp Agent Plugins repository](https://github.com/wasp-lang/wasp-agent-plugins) for more details.
NEWPAGE

echo "Patch applied successfully."
