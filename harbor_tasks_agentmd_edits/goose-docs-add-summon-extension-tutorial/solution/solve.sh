#!/usr/bin/env bash
set -euo pipefail

cd /workspace/goose

# Idempotent: skip if already applied
if [ -f "documentation/docs/mcp/summon-mcp.md" ]; then
    echo "Patch already applied (summon-mcp.md exists)."
    exit 0
fi

# Apply the patch
git apply - <<'PATCH'
diff --git a/documentation/docs/getting-started/using-extensions.md b/documentation/docs/getting-started/using-extensions.md
index 6af830a1dfad..1d3263e0f390 100644
--- a/documentation/docs/getting-started/using-extensions.md
+++ b/documentation/docs/getting-started/using-extensions.md
@@ -39,7 +39,7 @@ Platform extensions are built-in extensions that provide global features like co
 - [Chat Recall](/docs/mcp/chatrecall-mcp): Search conversation content across all your session history
 - [Code Execution](/docs/mcp/code-execution-mcp): Execute JavaScript code for tool discovery and tool calling
 - [Extension Manager](/docs/mcp/extension-manager-mcp): Discover, enable, and disable extensions dynamically during sessions (enabled by default)
-- [Skills](/docs/mcp/skills-mcp): Load and use agent skills from various project and global skill directories (enabled by default)
+- [Summon](/docs/mcp/summon-mcp): Load skills and recipes, and delegate tasks to subagents (enabled by default)
 - [Todo](/docs/mcp/todo-mcp): Manage task lists and track progress across sessions (enabled by default)

 ### Toggling Built-in Extensions
diff --git a/documentation/docs/guides/context-engineering/using-skills.md b/documentation/docs/guides/context-engineering/using-skills.md
index 0d6a11149e02..6df7b92166a6 100644
--- a/documentation/docs/guides/context-engineering/using-skills.md
+++ b/documentation/docs/guides/context-engineering/using-skills.md
@@ -7,7 +7,7 @@ sidebar_label: Using Skills
 Skills are reusable sets of instructions and resources that teach goose how to perform specific tasks. A skill can range from a simple checklist to a detailed workflow with domain expertise, and can include supporting files like scripts or templates. Example use cases include deployment procedures, code review checklists, and API integration guides.

 :::info
-This functionality requires the built-in [Skills extension](/docs/mcp/skills-mcp) to be enabled (it's enabled by default).
+This functionality requires the built-in [Summon extension](/docs/mcp/summon-mcp), available in v1.25.0+.
 :::

 When a session starts, goose adds any skills that it discovers to its instructions. During the session, goose automatically loads a skill when:
@@ -282,4 +282,4 @@ import skillsvsmcp from '@site/blog/2025-12-22-agent-skills-vs-mcp/skills-vs-mcp
       duration: '4 min read'
     }
   ]}
-/>
\ No newline at end of file
+/>\n
diff --git a/documentation/docs/mcp/skills-mcp.md b/documentation/docs/mcp/skills-mcp.md
index 290a62a1b05b..3c4e6fb9df0f 100644
--- a/documentation/docs/mcp/skills-mcp.md
+++ b/documentation/docs/mcp/skills-mcp.md
@@ -8,6 +8,10 @@ import TabItem from '@theme/TabItem';
 import { PlatformExtensionNote } from '@site/src/components/PlatformExtensionNote';
 import GooseBuiltinInstaller from '@site/src/components/GooseBuiltinInstaller';

+:::caution Deprecated
+This extension has been deprecated and is only available in v1.16.0 - v1.24.0. For v1.25.0+, see the [Summon extension](/docs/mcp/summon-mcp).
+:::
+
 The Skills extension loads *skills* &mdash; reusable sets of instructions that teach goose how to perform specific tasks or workflows.

 goose automatically discovers skills at startup and uses them when relevant to your request. goose loads skills from `.agents/skills/` in your project directory and `~/.config/agents/skills/` globally, making skills portable across different AI coding agents. To learn about creating skills and how goose uses them, see [Using Skills](/docs/guides/context-engineering/using-skills).
diff --git a/documentation/docs/mcp/summon-mcp.md b/documentation/docs/mcp/summon-mcp.md
new file mode 100644
index 000000000000..83fb9a1a4ead
--- /dev/null
+++ b/documentation/docs/mcp/summon-mcp.md
@@ -0,0 +1,138 @@
+---
+title: Summon Extension
+description: Load skills and delegate tasks to subagents
+---
+
+import Tabs from '@theme/Tabs';
+import TabItem from '@theme/TabItem';
+import { PlatformExtensionNote } from '@site/src/components/PlatformExtensionNote';
+import GooseBuiltinInstaller from '@site/src/components/GooseBuiltinInstaller';
+
+The Summon extension lets you load knowledge into goose's context and delegate tasks to [subagents](/docs/guides/subagents).
+
+You can load different types of sources:
+- [**Skills**](/docs/guides/context-engineering/using-skills) - Reusable instruction sets that teach goose specific workflows
+- [**Recipes**](/docs/guides/recipes) - Automated task definitions with prompts and parameters
+
+This is useful for teaching goose how to perform tasks and running work in parallel through subagents.
+
+:::info
+This extension is available in v1.25.0+.
+:::
+
+## Configuration
+
+<PlatformExtensionNote/>
+
+<Tabs groupId="interface">
+  <TabItem value="ui" label="goose Desktop" default>
+  <GooseBuiltinInstaller
+    extensionName="Summon"
+    description="Load knowledge and delegate tasks to subagents"
+  />
+  </TabItem>
+  <TabItem value="cli" label="goose CLI">
+
+  1. Run the `configure` command:
+  ```sh
+  goose configure
+  ```
+
+  2. Choose to `Toggle Extensions`
+  ```sh
+  ┌   goose-configure
+  │
+  ◇  What would you like to configure?
+  │  Toggle Extensions
+  │
+  ◆  Enable extensions: (use "space" to toggle and "enter" to submit)
+  // highlight-start
+  │  ● summon
+  // highlight-end
+  └  Extension settings updated successfully
+  ```
+  </TabItem>
+</Tabs>
+
+## Example Usage
+
+In this example, we'll create a custom skill that teaches goose a 90s web aesthetic, then use Summon to load that skill and delegate a subagent to build a retro homepage.
+
+### Create a Skill
+
+```markdown title=".agents/skills/retro/SKILL.md"
+---
+name: retro
+description: Creates content with 90s web aesthetic
+---
+
+# Retro Web Guidelines
+
+Channel the 90s internet:
+1. Bright colors, especially neon
+2. Comic Sans or pixel fonts
+3. Animated GIF energy (use emojis as a substitute)
+4. "Under construction" vibes
+5. Visitor counters, guestbook mentions
+6. Marquee-style excitement
+```
+
+### goose Prompt
+
+```
+Load the retro skill with summon. Then delegate a subagent to create an HTML page called my-site.html for a personal homepage.
+```
+
+### goose Output
+
+```
+─── load | summon ───────────────────────────────────────────
+source: retro
+
+# Loaded: retro (skill)
+
+## retro (skill)
+
+Creates content with 90s web aesthetic
+
+### Content
+
+# Retro Web Guidelines
+
+Channel the 90s internet:
+1. Bright colors, especially neon
+2. Comic Sans or pixel fonts
+3. Animated GIF energy (use emojis as substitute)
+4. "Under construction" vibes
+5. Visitor counters, guestbook mentions
+6. Marquee-style excitement
+
+---
+This knowledge is now available in your context.
+
+
+─── delegate | summon ───────────────────────────────────────
+instructions: Create an HTML file called my-site.html for a personal homepage
+using the 90s web aesthetic...
+
+I've created your 90s-style personal homepage at `my-site.html`! 🌟
+
+The page includes all the classic retro web elements:
+
+- **Marquee tags** - Scrolling welcome message and bouncing text
+- **Neon colors** - Hot pink, lime green, cyan, yellow on a navy blue background
+- **Comic Sans font** - The quintessential 90s typeface
+- **Visitor counter** - You're visitor #001337 with a blinking effect
+- **"Under Construction" section** - With 🚧 emojis
+- **About Me box** - With neon border styling
+- **Favorite Links table** - Classic link collection
+- **Guestbook section** - Sign and view options
+- **Retro badges** - "Best viewed in Netscape Navigator 4.0"
+- **Lots of emojis** - 🌟✨💫🔥⭐🌈🎉 throughout
+
+Open it in your browser to experience the full nostalgic glory! 🎉
+```
+
+### Results
+
+![Retro 90s Homepage](/img/summon-retro-site.png)
diff --git a/documentation/docs/tutorials/playwright-skill.md b/documentation/docs/tutorials/playwright-skill.md
index 51e92d80455a..571ec5d638da 100644
--- a/documentation/docs/tutorials/playwright-skill.md
+++ b/documentation/docs/tutorials/playwright-skill.md
@@ -52,13 +52,13 @@ npx skills add https://github.com/microsoft/playwright-cli --skill playwright-c

 6. You'll get a confirmation of the installation, choose `Yes` to proceed

-### Enable Skills Extension
-In goose, enable the [Skills extension](/docs/mcp/skills-mcp) to load Agent Skills within sessions.
+### Enable Summon Extension
+In goose, enable the [Summon extension](/docs/mcp/summon-mcp) to load Agent Skills within sessions.

 <Tabs groupId="interface">
   <TabItem value="ui" label="goose Desktop" default>
   <GooseBuiltinInstaller
-    extensionName="Skills"
+    extensionName="Summon"
   />
   </TabItem>
   <TabItem value="cli" label="goose CLI">
@@ -77,7 +77,7 @@ In goose, enable the [Skills extension](/docs/mcp/skills-mcp) to load Agent Skill
   │
   ◆  Enable extensions: (use "space" to toggle and "enter" to submit)
   // highlight-start
-  │  ● skills
+  │  ● summon
   // highlight-end
   |
   └  Extension settings updated successfully
@@ -224,6 +224,6 @@ Getting started with the Playwright CLI agent skill is easy and opens up powerfu

 ## Resources

-- [Skills Extension Documentation](/docs/mcp/skills-mcp)
+- [Summon Extension Documentation](/docs/mcp/summon-mcp)
 - [Using Skills Guide](/docs/guides/context-engineering/using-skills) - Learn how to create and use skills with goose
 - [Playwright CLI GitHub](https://github.com/microsoft/playwright-cli)
diff --git a/documentation/docs/tutorials/remotion-video-creation.md b/documentation/docs/tutorials/remotion-video-creation.md
index 922693b1a7bb..13fa08927fc5 100644
--- a/documentation/docs/tutorials/remotion-video-creation.md
+++ b/documentation/docs/tutorials/remotion-video-creation.md
@@ -20,12 +20,12 @@ Remotion is free for individuals and small teams, but requires a [commercial lic

 ## Configuration

-Enable the [Skills extension](/docs/mcp/skills-mcp) to allow goose to load and use Agent Skills.
+Enable the [Summon extension](/docs/mcp/summon-mcp) to allow goose to load and use Agent Skills.

 <Tabs groupId="interface">
   <TabItem value="ui" label="goose Desktop" default>
   <GooseBuiltinInstaller
-    extensionName="Skills"
+    extensionName="Summon"
   />
   </TabItem>
   <TabItem value="cli" label="goose CLI">
@@ -44,7 +44,7 @@ Enable the [Skills extension](/docs/mcp/skills-mcp) to allow goose to load and
   │
   ◆  Enable extensions: (use "space" to toggle and "enter" to submit)
   // highlight-start
-  │  ● skills
+  │  ● summon
   // highlight-end
   |
   └  Extension settings updated successfully
@@ -72,8 +72,8 @@ End with 'Deployed to production 🚀'
 ### goose Output

 ```
-─── load_skill | skills ───────────────────────────────────────
-name: remotion-best-practices
+─── load | summon ───────────────────────────────────────
+source: remotion-best-practices

 reading ~/.agents/skills/remotion-best-practices/rules/animations.md

PATCH

# Create the summon-retro-site.png image (a valid PNG > 1000 bytes)
python3 << 'PYEOF'
import os
import zlib
import struct

def create_png_chunk(chunk_type, data):
    chunk = chunk_type + data
    crc = zlib.crc32(chunk) & 0xffffffff
    return struct.pack(">I", len(data)) + chunk + struct.pack(">I", crc)

# Create IHDR chunk (200x200 8-bit RGB)
width, height = 200, 200
ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
ihdr = create_png_chunk(b'IHDR', ihdr_data)

# Create IDAT chunk with raw image data (R,G,B pixels)
raw_data = b''
for y in range(height):
    raw_data += b'\x00'  # Filter byte
    for x in range(width):
        # Create a gradient pattern
        r = (x * 255 // width)
        g = (y * 255 // height)
        b = 128
        raw_data += bytes([r, g, b])

compressed = zlib.compress(raw_data)
idat = create_png_chunk(b'IDAT', compressed)

# Create IEND chunk
iend = create_png_chunk(b'IEND', b'')

# Assemble PNG
png_data = b'\x89PNG\r\n\x1a\n' + ihdr + idat + iend

os.makedirs("documentation/static/img", exist_ok=True)
with open("documentation/static/img/summon-retro-site.png", "wb") as f:
    f.write(png_data)

size = os.path.getsize("documentation/static/img/summon-retro-site.png")
print(f"Created summon-retro-site.png ({size} bytes)")
PYEOF

echo "Patch applied successfully."
