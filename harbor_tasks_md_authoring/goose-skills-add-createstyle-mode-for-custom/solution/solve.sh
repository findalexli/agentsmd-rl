#!/usr/bin/env bash
set -euo pipefail

cd /workspace/goose-skills

# Idempotency guard
if grep -qF "- **Create custom style** \u2014 `/goose-graphics --create-style --ref <image>` runs " "skills/composites/goose-graphics/SKILL.md" && grep -qF "The output MUST be in the slim preset format (Palette \u2192 Typography \u2192 Layout \u2192 Do" "skills/composites/goose-graphics/styles/extract-style.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/composites/goose-graphics/SKILL.md b/skills/composites/goose-graphics/SKILL.md
@@ -13,24 +13,28 @@ Everything is self-contained: format templates, style systems, image sourcing in
 
 ## 2. Invocation
 
-This skill supports **three invocation modes** — all-args, partial-args, and interactive. Pick the fastest path for the ask.
+This skill supports **four invocation modes** — all-args, partial-args, interactive, and create-style. Pick the fastest path for the ask.
 
 ### 2.1 Full-args invocation (fastest path)
 
 ```
 /goose-graphics --style <slug> --format <format> [--brief "..."] [--ref <image-path>]
+/goose-graphics --create-style --ref <image-path> [--style-name <slug>]
 ```
 
 - `--style <slug>` — one of the 36 preset slugs (see `styles/index.json` or §6). Required for style-selected generation. Omit to let the user pick interactively.
 - `--format <format>` — one of `carousel`, `story`, `infographic`, `slides`, `poster`, `chart`, `tweet`. Required for format-selected generation.
 - `--brief "..."` — the topic / content description. Replaces the Content Discovery phase.
 - `--ref <image-path>` — if present, extract a custom style from the reference image instead of using a preset. When `--ref` is provided, `--style` is ignored.
+- `--create-style` — create a custom style from a reference image **only** (no format selection, no HTML generation). Requires `--ref`. Optionally accepts `--style-name <slug>` to skip the naming prompt. The extracted style is saved to `styles/<name>.md` alongside the presets.
+- `--style-name <slug>` — used with `--create-style` to pre-set the custom style name (lowercase-kebab-case). Skips the naming prompt in the extract-style workflow.
 
-**Three branches:**
+**Four branches:**
 
 1. **All required args present** (`--style` + `--format` + `--brief` OR `--ref` + `--format` + `--brief`) → skip discovery, skip style selection, proceed directly to §7 (Set Output Path) and §8 (Generate HTML).
 2. **Partial args** → ask only for the missing pieces. If `--style` is set but `--format` is not, ask only for format. If `--brief` is missing, ask only for the topic/content.
 3. **No args** → run the interactive flow from §3 onward.
+4. **`--create-style` present** → read `styles/extract-style.md` and follow its workflow. Skip §6 (Discover Intent), §7 (Select Style preset list), §8-§12. The extract-style workflow handles everything including save. Stop after the style is saved — do not proceed to format selection or HTML generation.
 
 ### 2.2 Examples
 
@@ -46,6 +50,12 @@ This skill supports **three invocation modes** — all-args, partial-args, and i
 
 # No args — full interactive flow
 /goose-graphics
+
+# Create a custom style from a reference image (no HTML generation)
+/goose-graphics --create-style --ref ~/Desktop/mood.png
+
+# Create with a pre-chosen name
+/goose-graphics --create-style --ref ~/Desktop/mood.png --style-name sunset-editorial
 ```
 
 ### 2.3 Defaults when args are partial but unambiguous
@@ -174,7 +184,7 @@ Present the **36 style presets**, grouped by mood. The canonical list lives in `
 **Friendly Corporate**
 36. **Mint Pixel Corporate** — Pale mint + lime pixel-staircase corner decorations.
 
-The user may also say: **"I have a reference image"** — in that case, read `styles/extract-style.md` and follow its workflow to derive a custom style from the provided image.
+The user may also say: **"I have a reference image"** — in that case, read `styles/extract-style.md` and follow its workflow to derive a custom style in slim format from the provided image. The extracted style is saved to `styles/<name>.md` alongside the presets and is immediately usable. After the style is saved, continue the workflow from Step 3 onward using the newly created style.
 
 After the user selects a preset, read the corresponding style file from `styles/<slug>.md` (e.g., `styles/midnight-editorial.md`, `styles/heatwave-orange.md`). Each slim style file contains everything you need to generate: palette, typography, layout, do/don'ts, and ready-to-paste CSS snippets. For the full prose deep-dive (rare — use for extract-style prompting or when nuance is missing), read `styles/_full/<slug>.md`.
 
@@ -240,6 +250,7 @@ Present the results to the user:
 - **"Surprise me"** — Pick the carousel format and a random style preset from `styles/index.json`. Ask the user only for content/topic, then generate everything else automatically.
 - **Multi-format** — If the user says "make this as both a carousel and an infographic," run the full workflow twice using the same content and style but different format skills. Save outputs in separate subdirectories.
 - **Style preview** — Before committing to full generation, produce a single sample slide or section so the user can approve the visual direction. If they want changes, adjust the style or switch presets before generating the rest.
+- **Create custom style** — `/goose-graphics --create-style --ref <image>` runs only the style extraction workflow from `styles/extract-style.md`. Analyzes the reference image, maps fonts to Google Fonts equivalents, generates a slim-format style file, and saves it to `styles/<name>.md`. No format selection or HTML generation. The saved style is immediately available for future `/goose-graphics --style <name>` calls.
 
 ## 14. File Reference
 
@@ -258,6 +269,8 @@ Present the results to the user:
 
 The canonical list of all 36 style presets lives in `styles/index.json` (slug, display name, mood group, one-line tagline). Individual slim style files at `styles/<slug>.md` give you the full spec (palette, typography, layout, do/don't, CSS snippets). Archived full-prose versions live in `styles/_full/<slug>.md` if you need the deeper atmospheric reference.
 
+Custom styles created via `--create-style` or the "I have a reference image" interactive option are saved to `styles/<name>.md` in the same slim format as presets. They are not added to `index.json` (which tracks only the 36 shipped presets) but are fully usable via `--style <name>`.
+
 ### Image Sources
 | File | Description |
 |------|-------------|
diff --git a/skills/composites/goose-graphics/styles/extract-style.md b/skills/composites/goose-graphics/styles/extract-style.md
@@ -1,12 +1,12 @@
-# Skill: Extract Style from Reference Image
+# Skill: Create Custom Style from Reference Image
 
-Extract the visual design language from a reference image and produce a reusable DESIGN.md style definition file.
+Extract the visual design language from a reference image and produce a reusable slim-format style preset file — the same format used by all 36 built-in presets (e.g., `brutalist.md`, `matt-gray.md`).
 
 ---
 
 ## When to Use
 
-The user provides a reference image -- a screenshot, design mockup, mood board, website capture, or any visual reference -- and wants to capture its design language as a reusable style preset. The output is a complete 9-section DESIGN.md file that can be used by other graphic design skills to produce on-brand content.
+The user provides a reference image — a screenshot, design mockup, mood board, website capture, or any visual reference — and wants to capture its design language as a reusable style preset. The output is a slim-format `.md` style file (4-8KB) that is immediately usable via `--style <name>` in the goose-graphics workflow.
 
 ---
 
@@ -128,119 +128,202 @@ Construct the `<link>` tag with the selected fonts and the specific weights need
 
 ---
 
-## Phase 3: Generate the DESIGN.md
+## Phase 3: Generate the Slim Style File
 
-Produce a complete file with all 9 sections, following the exact structure and depth of the existing style presets (e.g., midnight-editorial.md). Every section must be substantive -- not placeholder text.
+Generate a style file in the **slim preset format** — the same structure used by all 36 built-in presets. Do NOT generate the verbose 9-section DESIGN.md format. If you need a structural reference, read `styles/brutalist.md` or `styles/matt-gray.md`.
 
-### Section 1: Visual Theme & Atmosphere
+The output should be **4-8KB** and contain these sections in order:
 
-Write a 2-3 paragraph narrative description of the extracted style. This is prose, not a list. Cover:
-- What tradition or design school this style draws from
-- How the color palette creates its specific mood
-- How the typography pairing works and why
-- What the accent color does for the composition
-- 2-3 real-world analogies (e.g., "the design language of a Scandinavian furniture catalog," "the feel of a fintech dashboard")
+### Section 1: Header
 
-End with a **Key Characteristics** bullet list (8-12 items) summarizing the most important rules, each with specific values (hex codes, pixel sizes, weights).
+```markdown
+# Style Name
 
-### Section 2: Color Palette & Roles
+2-4 sentence prose description of the style's visual identity. Describe the mood, the palette logic,
+the typography pairing, and what makes this style distinctive. Reference real-world analogies
+(e.g., "the feel of a Scandinavian furniture catalog," "fintech dashboard energy").
 
-Organize colors into these groups with the same structure as the reference:
+> Custom style — extracted from reference image
+```
+
+### Section 2: Palette
+
+A flat table with 6-12 rows. Every color gets a hex code and a role description. Include: background, primary text, accent, secondary accent (if present), card/surface colors, border colors, and any secondary text tones.
 
-- **Primary** (3 colors): Background, primary text, primary accent -- with hex codes and usage descriptions.
-- **Accent** (2-3 colors): Secondary accent, hover states, tertiary tones.
-- **Neutral Scale** (4-6 colors): Surface variations from darkest to lightest (for dark themes) or lightest to darkest (for light themes). Include disabled text, placeholder, and metadata colors.
-- **Surface & Borders**: Surface primary, surface inset, border default (with alpha), border accent, border strong, divider rule.
-- **Shadow Colors**: 3-4 shadow definitions using RGBA values that stay on-palette.
+```markdown
+## Palette
+
+| Hex | Role |
+|-----|------|
+| `#xxxxxx` | Background (primary canvas) |
+| `#xxxxxx` | Primary text |
+| `#xxxxxx` | Accent — emphasis, CTAs, highlights |
+| ... | ... |
+```
 
 **Color quality rules:**
-- Never use pure black (`#000000`) or pure white (`#ffffff`) unless the reference clearly does.
-- Text-on-background contrast must meet WCAG AA (4.5:1 ratio minimum). Mentally verify this.
-- Keep the total palette to 12-16 named colors. More than that creates inconsistency.
-- Shadow colors should use tinted RGBA from the accent color for warm palettes, or neutral RGBA for cool palettes.
+- Don't use pure black (`#000000`) or pure white (`#ffffff`) unless the reference clearly does.
+- Text-on-background contrast must meet WCAG AA (4.5:1 minimum). Mentally verify.
+- Keep total palette to 6-12 named colors.
+
+### Section 3: Typography
+
+Include the Google Fonts `<link>` tag (if using webfonts), Display and Body font-family declarations with fallback stacks, a hierarchy table with 8-9 rows, and 3-5 Principles bullets.
+
+```markdown
+## Typography
+
+**Google Fonts**
 
-### Section 3: Typography Rules
+\`\`\`html
+<link href="https://fonts.googleapis.com/css2?family=..." rel="stylesheet">
+\`\`\`
 
-Include:
-- **Font Families** block with the Google Fonts CDN link and CSS font-family declarations with full fallback stacks.
-- **Hierarchy table** with columns: Role | Font | Size | Weight | Line Height | Letter Spacing | Notes. Include at minimum: Display Hero, Section Heading, Sub-heading, Body Large, Body, Small/Caption, Big Numbers, Numbered Label, CTA Text.
-- **Principles** (5-6 bullet points) explaining the typographic logic: why these pairings, how tracking changes across sizes, when to use uppercase, line height rationale.
+- **Display:** `'Font Name', fallback, sans-serif`
+- **Body:** `'Font Name', fallback, sans-serif`
 
-### Section 4: Component Patterns
+| Role | Font | Size | Weight | Line-height | Tracking | Transform |
+|------|------|------|--------|-------------|----------|-----------|
+| Display Hero | ... | 72px | 700 | 1.10 | -1px | none |
+| Section Heading | ... | 48px | 700 | 1.15 | -0.5px | none |
+| Sub-heading | ... | 32px | 600 | 1.20 | 0 | none |
+| Body Large | ... | 22px | 500 | 1.55 | 0 | none |
+| Body | ... | 18px | 400 | 1.55 | 0 | none |
+| Caption | ... | 12-14px | 400 | 1.40 | ... | ... |
+| Big Number | ... | 64-100px | 800 | 1.00 | ... | none |
+| Label | ... | 14px | 500-600 | 1.00 | ... | ... |
+| CTA | ... | 16-18px | 700 | 1.00 | ... | ... |
 
-Provide 6-8 HTML/CSS component snippets using CSS custom properties (`var(--color-*)`, `var(--font-*)`). Each should be a self-contained, inline-styled HTML block. Include at minimum:
-- Title Block (hero/header section)
-- Numbered Item
-- Stat Display
-- Comparison Grid (2-column)
-- List Item
-- Quote Block
-- CTA Block
+**Principles**
 
-Adapt each component's structure to match the reference's design language. For example, if the reference is light and airy, components should have generous padding and minimal borders. If the reference is dense and technical, components should be compact with visible structure.
+- 3-5 bullets explaining the typographic logic (why these pairings, tracking behavior, uppercase rules, etc.)
+```
+
+### Section 4: Layout
+
+Bullet list covering format padding, border rules, radius, alignment, spacing, and any special layout elements (grids, textures, decorative patterns).
 
-### Section 5: Layout Principles
+```markdown
+## Layout
+
+- Format padding: carousel Xpx · infographic X/X · slides Xpx · poster X/X.
+- Border rules (thickness, color, style).
+- Border-radius rules.
+- Alignment rules (left, center, mixed).
+- Card/container rules (bg, border, padding, radius).
+- Any special elements (dot grids, background patterns, decorative shapes).
+- Vertical rhythm and spacing between sections.
+```
 
-Include:
-- **Spacing Scale** (8-10 values from micro to max) with pixel values and usage descriptions.
-- **Format Padding** table for 4 formats: Carousel (1080x1080), Infographic (1080xN), Slides (1920x1080), Poster (1080x1350).
-- **Alignment & Grid** rules: primary alignment, grid column guidance, rule/divider conventions, vertical rhythm, content gravity.
+### Section 5: Do / Don't
 
-### Section 6: Depth & Elevation
+5-6 Do rules and 5-6 Don't rules. Each must be specific and actionable with exact values (hex codes, px sizes, font names, weights). These encode the guardrails that prevent drifting off-style.
 
-Include:
-- **Elevation table** with 5 levels (Flat, Subtle, Card, Featured, Overlay) showing CSS shadow values and use cases.
-- **Border Treatments** (4 types): standard, active, accent rule, divider line -- with exact CSS values.
-- **Surface Hierarchy** explanation of how depth is communicated (lightness steps for dark themes, shadow intensity for light themes).
+```markdown
+## Do / Don't
 
-### Section 7: Do's and Don'ts
+**Do**
+
+- [Specific rule with exact values]
+- ...
+
+**Don't**
+
+- [Specific rule with exact values]
+- ...
+```
 
-Write 8-12 **Do** rules and 8-12 **Don't** rules. Each must be specific and actionable, referencing exact values (hex codes, pixel sizes, font names, weights). These should encode the guardrails that prevent someone from drifting off-style. Base them on what you observed in the reference -- if the reference never uses rounded corners, that is a Don't. If the reference uses a specific spacing rhythm, that is a Do.
+### Section 6: CSS Snippets
 
-### Section 8: Format Adaptation Notes
+A `:root` variables block defining all CSS custom properties, followed by 4-5 self-contained component patterns as inline-styled HTML blocks. Each component must use the style's colors, fonts, and spacing directly (inline styles, not CSS variables in the HTML — the `:root` block is for reference).
 
-For each of the 4 formats (Carousel, Infographic, Slides, Poster), provide:
-- Typography scale adjustments (which sizes change and to what values)
-- Padding values
-- Layout notes (single column vs. multi-column, content placement)
-- Format-specific conventions (e.g., swipe indicators for carousels, vertical rhythm for infographics)
+Required components:
+1. **Title block** — hero/header with headline, optional subtitle, optional label
+2. **Numbered item or step** — stat, step number, or numbered list element
+3. **Card** — bordered or surfaced container with content
+4. **CTA block** — call-to-action button
+5. **One style-specific component** — whatever is most distinctive about this style (quote block, stat display, tag system, grid pattern, etc.)
 
-### Section 9: Agent Prompt Guide
+```markdown
+## CSS snippets
 
-Include:
-- **Quick Color Reference** table: Name | Hex | Usage
-- **Font Declarations** as CSS code block
-- **Google Fonts Link** as HTML code block
-- **CSS Root Variables** -- a complete `:root` block defining every variable: colors (primary, accent, neutral, surfaces, borders, shadows), typography (families, sizes, weights, line heights), spacing, borders, and composed shadows.
-- **System Font Fallbacks**
+### `:root` variables
+
+\`\`\`css
+:root {
+  --color-bg: #...;
+  --color-text: #...;
+  --color-accent: #...;
+  /* all palette colors */
+
+  --font-display: '...', fallback;
+  --font-body: '...', fallback;
+
+  /* borders, radius, shadows, spacing as needed */
+}
+\`\`\`
+
+### Title block (brief description)
+
+\`\`\`html
+<div style="...">...</div>
+\`\`\`
+
+### Numbered item (brief description)
+
+\`\`\`html
+<div style="...">...</div>
+\`\`\`
+
+[...3 more components...]
+```
+
+**Important:** Study the component snippets in `brutalist.md` and `matt-gray.md` for the right level of detail. Each snippet should be a complete, copy-pasteable HTML block with all styles inline.
 
 ---
 
 ## Phase 4: Save & Confirm
 
-### Step 1 -- Ask for a name
+### Step 1 — Ask for a name
+
+Ask the user what they want to name this style. Suggest 2-3 descriptive names based on the mood and palette (e.g., "arctic-minimal", "warm-startup", "dark-technical", "sunset-editorial"). The name must be lowercase-kebab-case.
 
-Ask the user what they want to name this style. Suggest a descriptive name based on the mood and palette (e.g., "arctic-minimal", "warm-startup", "dark-technical", "sunset-editorial"). The name should be lowercase-kebab-case.
+**Name collision guard:** Before saving, check whether `styles/<name>.md` already exists in the styles directory. If it does and is a shipped preset (listed in `styles/index.json`), warn the user and suggest an alternative name. Do not overwrite shipped presets.
 
-### Step 2 -- Determine save location
+### Step 2 — Determine save location
 
-The default save path is the same directory as the other style presets. If you can detect the goose-graphics styles directory from context, use it. Otherwise, ask the user where to save.
+Save the style file alongside the existing presets in the goose-graphics styles directory. Resolve the path relative to this skill file:
 
-Default path pattern:
 ```
-[project-root]/goose-graphics/styles/[name].md
+[skill-pack-dir]/styles/<name>.md
 ```
 
-### Step 3 -- Save the file
+Where `[skill-pack-dir]` is the directory containing `SKILL.md` — the root of the goose-graphics skill pack. This is the same directory that contains `styles/brutalist.md`, `styles/matt-gray.md`, etc.
+
+**Host-specific paths (for reference):**
+
+| Host | Typical styles directory |
+|------|------------------------|
+| Claude Code / Desktop / Cowork | `~/.claude/skills/goose-graphics/styles/` |
+| Codex (OpenAI) | `~/.codex/skills/goose-graphics/styles/` |
+| Cursor | Styles embedded in `.cursor/rules/` (not applicable — Cursor uses a single `.mdc` file) |
+| Local dev / project install | `./skills/goose-graphics/styles/` or wherever the pack was cloned |
 
-Write the complete DESIGN.md file using the Write tool.
+In most cases, the skill is already running from the installed location, so saving to the `styles/` directory relative to this file is correct.
 
-### Step 4 -- Confirm
+### Step 3 — Save the file
+
+Write the complete style file using the Write tool.
+
+### Step 4 — Confirm
 
 Tell the user:
 - The file was saved and its full path
-- A 3-4 line summary of the extracted style: theme (dark/light), primary palette (background + text + accent), font pairing, and overall mood
-- That the style is now ready for use with other graphic design skills
+- A 3-4 line summary of the extracted style: theme (dark/light), primary palette (background + text + accent hex codes), font pairing, and overall mood
+- How to use it immediately:
+  ```
+  /goose-graphics --style <name> --format <format> --brief "..."
+  ```
 
 ---
 
@@ -262,4 +345,8 @@ The goal is **typographic equivalence**, not exact matching. A geometric sans is
 
 ### On Completeness
 
-Every section of the output DESIGN.md must be filled with substantive, specific content. Do not leave any section with placeholder text like "TBD" or "adjust as needed." The file should be immediately usable by another agent or skill without further editing.
+Every section of the output style file must be filled with substantive, specific content. Do not leave any section with placeholder text like "TBD" or "adjust as needed." The file should be immediately usable via `--style <name>` without further editing.
+
+### On Format
+
+The output MUST be in the slim preset format (Palette → Typography → Layout → Do/Don't → CSS snippets). Do NOT generate the verbose 9-section DESIGN.md format with sections like "Visual Theme & Atmosphere," "Depth & Elevation," or "Format Adaptation Notes." Those belong to the `_full/` archive versions. The slim format is what the generation pipeline reads.
PATCH

echo "Gold patch applied."
