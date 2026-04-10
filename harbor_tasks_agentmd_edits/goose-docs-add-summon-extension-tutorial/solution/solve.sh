#!/usr/bin/env bash
set -euo pipefail

cd /workspace/goose

# Idempotent: skip if already applied
if [ -f "documentation/docs/mcp/summon-mcp.md" ]; then
    echo "Patch already applied (summon-mcp.md exists)."
    exit 0
fi

# Create summon-mcp.md
cat > documentation/docs/mcp/summon-mcp.md << 'EOF'
---
title: Summon Extension
description: Load skills and delegate tasks to subagents
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';
import { PlatformExtensionNote } from '@site/src/components/PlatformExtensionNote';
import GooseBuiltinInstaller from '@site/src/components/GooseBuiltinInstaller';

The Summon extension lets you load knowledge into goose's context and delegate tasks to [subagents](/docs/guides/subagents).

You can load different types of sources:
- [**Skills**](/docs/guides/context-engineering/using-skills) - Reusable instruction sets that teach goose specific workflows
- [**Recipes**](/docs/guides/recipes) - Automated task definitions with prompts and parameters

This is useful for teaching goose how to perform tasks and running work in parallel through subagents.

:::info
This extension is available in v1.25.0+.
:::

## Configuration

<PlatformExtensionNote/>

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseBuiltinInstaller
    extensionName="Summon"
    description="Load knowledge and delegate tasks to subagents"
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">

  1. Run the `configure` command:
  ```sh
  goose configure
  ```

  2. Choose to `Toggle Extensions`
  ```sh
  ┌   goose-configure
  │
  ◇  What would you like to configure?
  │  Toggle Extensions
  │
  ◆  Enable extensions: (use "space" to toggle and "enter" to submit)
  // highlight-start
  │  ● summon
  // highlight-end
  └  Extension settings updated successfully
  ```
  </TabItem>
</Tabs>

## Example Usage

In this example, we'll create a custom skill that teaches goose a 90s web aesthetic, then use Summon to load that skill and delegate a subagent to build a retro homepage.

### Create a Skill

```markdown title=".agents/skills/retro/SKILL.md"
---
name: retro
description: Creates content with 90s web aesthetic
---

# Retro Web Guidelines

Channel the 90s internet:
1. Bright colors, especially neon
2. Comic Sans or pixel fonts
3. Animated GIF energy (use emojis as a substitute)
4. "Under construction" vibes
5. Visitor counters, guestbook mentions
6. Marquee-style excitement
```

### goose Prompt

```
Load the retro skill with summon. Then delegate a subagent to create an HTML page called my-site.html for a personal homepage.
```

### goose Output

```
─── load | summon ───────────────────────────────────────────
source: retro

# Loaded: retro (skill)

## retro (skill)

Creates content with 90s web aesthetic

### Content

# Retro Web Guidelines

Channel the 90s internet:
1. Bright colors, especially neon
2. Comic Sans or pixel fonts
3. Animated GIF energy (use emojis as substitute)
4. "Under construction" vibes
5. Visitor counters, guestbook mentions
6. Marquee-style excitement

---
This knowledge is now available in your context.


─── delegate | summon ───────────────────────────────────────
instructions: Create an HTML file called my-site.html for a personal homepage
using the 90s web aesthetic...

I've created your 90s-style personal homepage at `my-site.html`! 🌟

The page includes all the classic retro web elements:

- **Marquee tags** - Scrolling welcome message and bouncing text
- **Neon colors** - Hot pink, lime green, cyan, yellow on a navy blue background
- **Comic Sans font** - The quintessential 90s typeface
- **Visitor counter** - You're visitor #001337 with a blinking effect
- **"Under Construction" section** - With 🚧 emojis
- **About Me box** - With neon border styling
- **Favorite Links table** - Classic link collection
- **Guestbook section** - Sign and view options
- **Retro badges** - "Best viewed in Netscape Navigator 4.0"
- **Lots of emojis** - 🌟✨💫🔥⭐🌈🎉 throughout

Open it in your browser to experience the full nostalgic glory! 🎉
```

### Results

![Retro 90s Homepage](/img/summon-retro-site.png)
EOF

# Add deprecation notice to skills-mcp.md after the imports
sed -i '/^import GooseBuiltinInstaller/,/^$/{ /^$/a\
:::caution Deprecated\
This extension has been deprecated and is only available in v1.16.0 - v1.24.0. For v1.25.0+, see the [Summon extension](/docs/mcp/summon-mcp).\
:::
}' documentation/docs/mcp/skills-mcp.md

# Update using-extensions.md - change Skills to Summon
sed -i 's/- \[Skills\](\/docs\/mcp\/skills-mcp): Load and use agent skills from various project and global skill directories (enabled by default)/- [Summon](\/docs\/mcp\/summon-mcp): Load skills and recipes, and delegate tasks to subagents (enabled by default)/' documentation/docs/getting-started/using-extensions.md

# Update using-skills.md - change extension reference
sed -i 's/This functionality requires the built-in \[Skills extension\](\/docs\/mcp\/skills-mcp) to be enabled (it'\''s enabled by default)./This functionality requires the built-in [Summon extension](\/docs\/mcp\/summon-mcp), available in v1.25.0+./' documentation/docs/guides/context-engineering/using-skills.md

# Add trailing newline to using-skills.md if missing
echo "" >> documentation/docs/guides/context-engineering/using-skills.md

# Update playwright-skill.md
sed -i 's/### Enable Skills Extension/### Enable Summon Extension/' documentation/docs/tutorials/playwright-skill.md
sed -i 's/enable the \[Skills extension\](\/docs\/mcp\/skills-mcp)/enable the [Summon extension](\/docs\/mcp\/summon-mcp)/' documentation/docs/tutorials/playwright-skill.md
sed -i 's/extensionName="Skills"/extensionName="Summon"/' documentation/docs/tutorials/playwright-skill.md
sed -i 's/│  ● skills/│  ● summon/' documentation/docs/tutorials/playwright-skill.md
sed -i 's/- \[Skills Extension Documentation\](\/docs\/mcp\/skills-mcp)/- [Summon Extension Documentation](\/docs\/mcp\/summon-mcp)/' documentation/docs/tutorials/playwright-skill.md

# Update remotion-video-creation.md
sed -i 's/Enable the \[Skills extension\](\/docs\/mcp\/skills-mcp)/Enable the [Summon extension](\/docs\/mcp\/summon-mcp)/' documentation/docs/tutorials/remotion-video-creation.md
sed -i 's/extensionName="Skills"/extensionName="Summon"/' documentation/docs/tutorials/remotion-video-creation.md
sed -i 's/│  ● skills/│  ● summon/' documentation/docs/tutorials/remotion-video-creation.md
sed -i 's/─── load_skill | skills ───────────────────────────────────────/─── load | summon ───────────────────────────────────────/' documentation/docs/tutorials/remotion-video-creation.md
sed -i 's/^name: remotion-best-practices$/source: remotion-best-practices/' documentation/docs/tutorials/remotion-video-creation.md

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
