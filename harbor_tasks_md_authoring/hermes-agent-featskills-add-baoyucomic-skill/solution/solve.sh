#!/usr/bin/env bash
set -euo pipefail

cd /workspace/hermes-agent

# Idempotency guard
if grep -qF "- **Character sheet PNG** is still generated for multi-page comics, but it is re" "skills/creative/baoyu-comic/PORT_NOTES.md" && grep -qF "**7.1 Character sheet** \u2014 generate it (to `characters/characters.png`, aspect `l" "skills/creative/baoyu-comic/SKILL.md" && grep -qF "1. **YAML Front Matter**: Metadata (title, topic, time_span, source_language, us" "skills/creative/baoyu-comic/references/analysis-framework.md" && grep -qF "Classic classroom chalkboard aesthetic with hand-drawn chalk illustrations. Nost" "skills/creative/baoyu-comic/references/art-styles/chalk.md" && grep -qF "Traditional Chinese ink brush painting style adapted for comics. Combines callig" "skills/creative/baoyu-comic/references/art-styles/ink-brush.md" && grep -qF "Classic European comic style originating from Herg\u00e9's Tintin. Characterized by c" "skills/creative/baoyu-comic/references/art-styles/ligne-claire.md" && grep -qF "Japanese manga art style characterized by large expressive eyes, dynamic poses, " "skills/creative/baoyu-comic/references/art-styles/manga.md" && grep -qF "Minimalist cartoon illustration characterized by clean black line art on white b" "skills/creative/baoyu-comic/references/art-styles/minimalist.md" && grep -qF "Full-color realistic manga style using digital painting techniques. Features ana" "skills/creative/baoyu-comic/references/art-styles/realistic.md" && grep -qF "- **Triggers**: Psychology, motivation, self-help, business narrative, managemen" "skills/creative/baoyu-comic/references/auto-selection.md" && grep -qF "- Camera angles vary: eye level, bird's eye, low angle, close-up, wide shot" "skills/creative/baoyu-comic/references/base-prompt.md" && grep -qF "- Front view: Young man, 30s, short dark wavy hair, thoughtful expression, weari" "skills/creative/baoyu-comic/references/character-template.md" && grep -qF "- **Structure**: Horizontal emphasis, wide aspect panels" "skills/creative/baoyu-comic/references/layouts/cinematic.md" && grep -qF "Technical explanations, complex narratives, timelines" "skills/creative/baoyu-comic/references/layouts/dense.md" && grep -qF "- Reading flow: Z-pattern \u2014 Panel 1 (top-left) \u2192 Panel 2 (top-right) \u2192 Panel 3 (" "skills/creative/baoyu-comic/references/layouts/four-panel.md" && grep -qF "Action sequences, emotional arcs, complex stories" "skills/creative/baoyu-comic/references/layouts/mixed.md" && grep -qF "- Reading flow: Splash dominates, supporting panels accent" "skills/creative/baoyu-comic/references/layouts/splash.md" && grep -qF "- **Structure**: Regular grid with occasional variation" "skills/creative/baoyu-comic/references/layouts/standard.md" && grep -qF "- **Gutters**: Generous vertical spacing (20-40px), panels often bleed horizonta" "skills/creative/baoyu-comic/references/layouts/webtoon.md" && grep -qF "Custom characters: ask the user for role \u2192 name mappings (e.g., `Student:\u5c0f\u660e, Men" "skills/creative/baoyu-comic/references/ohmsha-guide.md" && grep -qF "Options to run specific parts of the workflow. Trigger these via natural languag" "skills/creative/baoyu-comic/references/partial-workflows.md" && grep -qF "**IMPORTANT**: Characters are created fresh each time based on the source conten" "skills/creative/baoyu-comic/references/presets/concept-story.md" && grep -qF "> A minimalist, clean line art digital comic strip in a four-panel grid layout (" "skills/creative/baoyu-comic/references/presets/four-panel.md" && grep -qF "**IMPORTANT**: These Doraemon characters ARE the default for ohmsha preset. Gene" "skills/creative/baoyu-comic/references/presets/ohmsha.md" && grep -qF "This preset includes special rules beyond the art+tone combination. When the `sh" "skills/creative/baoyu-comic/references/presets/shoujo.md" && grep -qF "This preset includes special rules beyond the art+tone combination. When the `wu" "skills/creative/baoyu-comic/references/presets/wuxia.md" && grep -qF "- Composition hinting at core theme (character silhouette, iconic symbol, concep" "skills/creative/baoyu-comic/references/storyboard-template.md" && grep -qF "High-impact action atmosphere with dynamic movement, combat effects, and powerfu" "skills/creative/baoyu-comic/references/tones/action.md" && grep -qF "High-impact dramatic tone for pivotal moments, conflicts, and breakthroughs. Use" "skills/creative/baoyu-comic/references/tones/dramatic.md" && grep -qF "High-energy atmosphere for exciting, discovery-filled content. Bright colors, dy" "skills/creative/baoyu-comic/references/tones/energetic.md" && grep -qF "Default balanced tone suitable for educational and informative content. Neither " "skills/creative/baoyu-comic/references/tones/neutral.md" && grep -qF "Soft, dreamy atmosphere for romantic and emotionally delicate content. Features " "skills/creative/baoyu-comic/references/tones/romantic.md" && grep -qF "Historical atmosphere with aged paper effects and period-appropriate aesthetics." "skills/creative/baoyu-comic/references/tones/vintage.md" && grep -qF "Warm, inviting atmosphere for personal stories and nostalgic content. Creates em" "skills/creative/baoyu-comic/references/tones/warm.md" && grep -qF "**Important**: the downloaded sheet is a **human-facing review artifact** (so th" "skills/creative/baoyu-comic/references/workflow.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/creative/baoyu-comic/PORT_NOTES.md b/skills/creative/baoyu-comic/PORT_NOTES.md
@@ -0,0 +1,77 @@
+# Port Notes — baoyu-comic
+
+Ported from [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) v1.56.1.
+
+## Changes from upstream
+
+### SKILL.md adaptations
+
+| Change | Upstream | Hermes |
+|--------|----------|--------|
+| Metadata namespace | `openclaw` | `hermes` (with `tags` + `homepage`) |
+| Trigger | Slash commands / CLI flags | Natural language skill matching |
+| User config | EXTEND.md file (project/user/XDG paths) | Removed — not part of Hermes infra |
+| User prompts | `AskUserQuestion` (batched) | `clarify` tool (one question at a time) |
+| Image generation | baoyu-imagine (Bun/TypeScript, supports `--ref`) | `image_generate` — **prompt-only**, returns a URL; no reference image input; agent must download the URL to the output directory |
+| PDF assembly | `scripts/merge-to-pdf.ts` (Bun + `pdf-lib`) | Removed — the PDF merge step is out of scope for this port; pages are delivered as PNGs only |
+| Platform support | Linux/macOS/Windows/WSL/PowerShell | Linux/macOS only |
+| File operations | Generic instructions | Hermes file tools (`write_file`, `read_file`) |
+
+### Structural removals
+
+- **`references/config/` directory** (removed entirely):
+  - `first-time-setup.md` — blocking first-time setup flow for EXTEND.md
+  - `preferences-schema.md` — EXTEND.md YAML schema
+  - `watermark-guide.md` — watermark config (tied to EXTEND.md)
+- **`scripts/` directory** (removed entirely): upstream's `merge-to-pdf.ts` depended on `pdf-lib`, which is not declared anywhere in the Hermes repo. Rather than add a new dependency, the port drops PDF assembly and delivers per-page PNGs.
+- **Workflow Step 8 (Merge to PDF)** removed from `workflow.md`; Step 9 (Completion report) renumbered to Step 8.
+- **Workflow Step 1.1** — "Load Preferences (EXTEND.md)" section removed from `workflow.md`; steps 1.2/1.3 renumbered to 1.1/1.2.
+- **Generic "User Input Tools" and "Image Generation Tools" preambles** — SKILL.md no longer lists fallback rules for multiple possible tools; it references `clarify` and `image_generate` directly.
+
+### Image generation strategy changes
+
+`image_generate`'s schema accepts only `prompt` and `aspect_ratio` (`landscape` | `portrait` | `square`). Upstream's reference-image flow (`--ref characters.png` for character consistency, plus user-supplied refs for style/palette/scene) does not map to this tool, so the workflow was restructured:
+
+- **Character sheet PNG** is still generated for multi-page comics, but it is repositioned as a **human-facing review artifact** (for visual verification) and a reference for later regenerations / manual prompt edits. Page prompts themselves are built from the **text descriptions** in `characters/characters.md` (embedded inline during Step 5). `image_generate` never sees the PNG as a visual input.
+- **User-supplied reference images** are reduced to `style` / `palette` / `scene` trait extraction — traits are embedded in the prompt body; the image files themselves are kept only for provenance under `refs/`.
+- **Page prompts** now mandate that character descriptions are embedded inline (copied from `characters/characters.md`) — this is the only mechanism left to enforce cross-page character consistency.
+- **Download step** — after every `image_generate` call, the returned URL is fetched to disk (e.g., `curl -fsSL "<url>" -o <target>.png`) and verified before the workflow advances.
+
+### SKILL.md reductions
+
+- CLI option columns (`--art`, `--tone`, `--layout`, `--aspect`, `--lang`, `--ref`, `--storyboard-only`, `--prompts-only`, `--images-only`, `--regenerate`) converted to plain-English option descriptions.
+- Preset files (`presets/*.md`) and `ohmsha-guide.md`: `` `--style X` `` / `` `--art X --tone Y` `` shorthand rewritten to `art=X, tone=Y` + natural-language references.
+- `partial-workflows.md`: per-skill slash command invocations rewritten as user-intent cues; PDF-related outputs removed.
+- `auto-selection.md`: priority order dropped the EXTEND.md tier.
+- `analysis-framework.md`: language-priority comment updated (user option → conversation → source).
+
+### File naming convention
+
+Source content pasted by the user is saved as `source-{slug}.md`, where `{slug}` is the kebab-case topic slug used for the output directory. Backups follow the same pattern with a `-backup-YYYYMMDD-HHMMSS` suffix. SKILL.md and `workflow.md` now agree on this single convention.
+
+### What was preserved verbatim
+
+- All 6 art-style definitions (`references/art-styles/`)
+- All 7 tone definitions (`references/tones/`)
+- All 7 layout definitions (`references/layouts/`)
+- Core templates: `character-template.md`, `storyboard-template.md`, `base-prompt.md`
+- Preset bodies (only the first few intro lines adapted; special rules unchanged)
+- Author, version, homepage attribution
+
+## Syncing with upstream
+
+To pull upstream updates:
+
+```bash
+# Compare versions
+curl -sL https://raw.githubusercontent.com/JimLiu/baoyu-skills/main/skills/baoyu-comic/SKILL.md | head -5
+# Look for the version: line
+
+# Diff a reference file
+diff <(curl -sL https://raw.githubusercontent.com/JimLiu/baoyu-skills/main/skills/baoyu-comic/references/art-styles/manga.md) \
+     references/art-styles/manga.md
+```
+
+Art-style, tone, and layout reference files can usually be overwritten directly (they're upstream-verbatim). `SKILL.md`, `references/workflow.md`, `references/partial-workflows.md`, `references/auto-selection.md`, `references/analysis-framework.md`, `references/ohmsha-guide.md`, and `references/presets/*.md` must be manually merged since they contain Hermes-specific adaptations.
+
+If upstream adds a Hermes-compatible PDF merge step (no extra npm deps), restore `scripts/` and reintroduce Step 8 in `workflow.md`.
diff --git a/skills/creative/baoyu-comic/SKILL.md b/skills/creative/baoyu-comic/SKILL.md
@@ -0,0 +1,236 @@
+---
+name: baoyu-comic
+description: Knowledge comic creator supporting multiple art styles and tones. Creates original educational comics with detailed panel layouts and sequential image generation. Use when user asks to create "知识漫画", "教育漫画", "biography comic", "tutorial comic", or "Logicomix-style comic".
+version: 1.56.1
+author: 宝玉 (JimLiu)
+license: MIT
+metadata:
+  hermes:
+    tags: [comic, knowledge-comic, creative, image-generation]
+    homepage: https://github.com/JimLiu/baoyu-skills#baoyu-comic
+---
+
+# Knowledge Comic Creator
+
+Adapted from [baoyu-comic](https://github.com/JimLiu/baoyu-skills) for Hermes Agent's tool ecosystem.
+
+Create original knowledge comics with flexible art style × tone combinations.
+
+## When to Use
+
+Trigger this skill when the user asks to create a knowledge/educational comic, biography comic, tutorial comic, or uses terms like "知识漫画", "教育漫画", or "Logicomix-style". The user provides content (text, file path, URL, or topic) and optionally specifies art style, tone, layout, aspect ratio, or language.
+
+## Reference Images
+
+Hermes' `image_generate` tool is **prompt-only** — it accepts a text prompt and an aspect ratio, and returns an image URL. It does **NOT** accept reference images. When the user supplies a reference image, use it to **extract traits in text** that get embedded in every page prompt:
+
+**Intake**: Accept file paths when the user provides them (or pastes images in conversation).
+- File path(s) → copy to `refs/NN-ref-{slug}.{ext}` alongside the comic output for provenance
+- Pasted image with no path → ask the user for the path via `clarify`, or extract style traits verbally as a text fallback
+- No reference → skip this section
+
+**Usage modes** (per reference):
+
+| Usage | Effect |
+|-------|--------|
+| `style` | Extract style traits (line treatment, texture, mood) and append to every page's prompt body |
+| `palette` | Extract hex colors and append to every page's prompt body |
+| `scene` | Extract scene composition or subject notes and append to the relevant page(s) |
+
+**Record in each page's prompt frontmatter** when refs exist:
+
+```yaml
+references:
+  - ref_id: 01
+    filename: 01-ref-scene.png
+    usage: style
+    traits: "muted earth tones, soft-edged ink wash, low-contrast backgrounds"
+```
+
+Character consistency is driven by **text descriptions** in `characters/characters.md` (written in Step 3) that get embedded inline in every page prompt (Step 5). The optional PNG character sheet generated in Step 7.1 is a human-facing review artifact, not an input to `image_generate`.
+
+## Options
+
+### Visual Dimensions
+
+| Option | Values | Description |
+|--------|--------|-------------|
+| Art | ligne-claire (default), manga, realistic, ink-brush, chalk, minimalist | Art style / rendering technique |
+| Tone | neutral (default), warm, dramatic, romantic, energetic, vintage, action | Mood / atmosphere |
+| Layout | standard (default), cinematic, dense, splash, mixed, webtoon, four-panel | Panel arrangement |
+| Aspect | 3:4 (default, portrait), 4:3 (landscape), 16:9 (widescreen) | Page aspect ratio |
+| Language | auto (default), zh, en, ja, etc. | Output language |
+| Refs | File paths | Reference images used for style / palette trait extraction (not passed to the image model). See [Reference Images](#reference-images) above. |
+
+### Partial Workflow Options
+
+| Option | Description |
+|--------|-------------|
+| Storyboard only | Generate storyboard only, skip prompts and images |
+| Prompts only | Generate storyboard + prompts, skip images |
+| Images only | Generate images from existing prompts directory |
+| Regenerate N | Regenerate specific page(s) only (e.g., `3` or `2,5,8`) |
+
+Details: [references/partial-workflows.md](references/partial-workflows.md)
+
+### Art, Tone & Preset Catalogue
+
+- **Art styles** (6): `ligne-claire`, `manga`, `realistic`, `ink-brush`, `chalk`, `minimalist`. Full definitions at `references/art-styles/<style>.md`.
+- **Tones** (7): `neutral`, `warm`, `dramatic`, `romantic`, `energetic`, `vintage`, `action`. Full definitions at `references/tones/<tone>.md`.
+- **Presets** (5) with special rules beyond plain art+tone:
+
+  | Preset | Equivalent | Hook |
+  |--------|-----------|------|
+  | `ohmsha` | manga + neutral | Visual metaphors, no talking heads, gadget reveals |
+  | `wuxia` | ink-brush + action | Qi effects, combat visuals, atmospheric |
+  | `shoujo` | manga + romantic | Decorative elements, eye details, romantic beats |
+  | `concept-story` | manga + warm | Visual symbol system, growth arc, dialogue+action balance |
+  | `four-panel` | minimalist + neutral + four-panel layout | 起承转合 structure, B&W + spot color, stick-figure characters |
+
+  Full rules at `references/presets/<preset>.md` — load the file when a preset is picked.
+
+- **Compatibility matrix** and **content-signal → preset** table live in [references/auto-selection.md](references/auto-selection.md). Read it before recommending combinations in Step 2.
+
+## File Structure
+
+Output directory: `comic/{topic-slug}/`
+- Slug: 2-4 words kebab-case from topic (e.g., `alan-turing-bio`)
+- Conflict: append timestamp (e.g., `turing-story-20260118-143052`)
+
+**Contents**:
+| File | Description |
+|------|-------------|
+| `source-{slug}.md` | Saved source content (kebab-case slug matches the output directory) |
+| `analysis.md` | Content analysis |
+| `storyboard.md` | Storyboard with panel breakdown |
+| `characters/characters.md` | Character definitions |
+| `characters/characters.png` | Character reference sheet (downloaded from `image_generate`) |
+| `prompts/NN-{cover\|page}-[slug].md` | Generation prompts |
+| `NN-{cover\|page}-[slug].png` | Generated images (downloaded from `image_generate`) |
+| `refs/NN-ref-{slug}.{ext}` | User-supplied reference images (optional, for provenance) |
+
+## Language Handling
+
+**Detection Priority**:
+1. User-specified language (explicit option)
+2. User's conversation language
+3. Source content language
+
+**Rule**: Use user's input language for ALL interactions:
+- Storyboard outlines and scene descriptions
+- Image generation prompts
+- User selection options and confirmations
+- Progress updates, questions, errors, summaries
+
+Technical terms remain in English.
+
+## Workflow
+
+### Progress Checklist
+
+```
+Comic Progress:
+- [ ] Step 1: Setup & Analyze
+  - [ ] 1.1 Analyze content
+  - [ ] 1.2 Check existing directory
+- [ ] Step 2: Confirmation - Style & options ⚠️ REQUIRED
+- [ ] Step 3: Generate storyboard + characters
+- [ ] Step 4: Review outline (conditional)
+- [ ] Step 5: Generate prompts
+- [ ] Step 6: Review prompts (conditional)
+- [ ] Step 7: Generate images
+  - [ ] 7.1 Generate character sheet (if needed) → characters/characters.png
+  - [ ] 7.2 Generate pages (with character descriptions embedded in prompt)
+- [ ] Step 8: Completion report
+```
+
+### Flow
+
+```
+Input → Analyze → [Check Existing?] → [Confirm: Style + Reviews] → Storyboard → [Review?] → Prompts → [Review?] → Images → Complete
+```
+
+### Step Summary
+
+| Step | Action | Key Output |
+|------|--------|------------|
+| 1.1 | Analyze content | `analysis.md`, `source-{slug}.md` |
+| 1.2 | Check existing directory | Handle conflicts |
+| 2 | Confirm style, focus, audience, reviews | User preferences |
+| 3 | Generate storyboard + characters | `storyboard.md`, `characters/` |
+| 4 | Review outline (if requested) | User approval |
+| 5 | Generate prompts | `prompts/*.md` |
+| 6 | Review prompts (if requested) | User approval |
+| 7.1 | Generate character sheet (if needed) | `characters/characters.png` |
+| 7.2 | Generate pages | `*.png` files |
+| 8 | Completion report | Summary |
+
+### User Questions
+
+Use the `clarify` tool to confirm options. Since `clarify` handles one question at a time, ask the most important question first and proceed sequentially. See [references/workflow.md](references/workflow.md) for the full Step 2 question set.
+
+### Step 7: Image Generation
+
+Use Hermes' built-in `image_generate` tool for all image rendering. Its schema accepts only `prompt` and `aspect_ratio` (`landscape` | `portrait` | `square`); it **returns a URL**, not a local file. Every generated page or character sheet must therefore be downloaded to the output directory.
+
+**Prompt file requirement (hard)**: write each image's full, final prompt to a standalone file under `prompts/` (naming: `NN-{type}-[slug].md`) BEFORE calling `image_generate`. The prompt file is the reproducibility record.
+
+**Aspect ratio mapping** — the storyboard's `aspect_ratio` field maps to `image_generate`'s format as follows:
+
+| Storyboard ratio | `image_generate` format |
+|------------------|-------------------------|
+| `3:4`, `9:16`, `2:3` | `portrait` |
+| `4:3`, `16:9`, `3:2` | `landscape` |
+| `1:1` | `square` |
+
+**Download step** — after every `image_generate` call:
+1. Read the URL from the tool result
+2. Fetch the image bytes (e.g., `curl -fsSL "<url>" -o <target>.png`)
+3. Verify the file exists and is non-empty before proceeding to the next page
+
+**7.1 Character sheet** — generate it (to `characters/characters.png`, aspect `landscape`) when the comic is multi-page with recurring characters. Skip for simple presets (e.g., four-panel minimalist) or single-page comics. The prompt file at `characters/characters.md` must exist before invoking `image_generate`. The rendered PNG is a **human-facing review artifact** (so the user can visually verify character design) and a reference for later regenerations or manual prompt edits — it does **not** drive Step 7.2. Page prompts are already written in Step 5 from the **text descriptions** in `characters/characters.md`; `image_generate` cannot accept images as visual input.
+
+**7.2 Pages** — each page's prompt MUST already be at `prompts/NN-{cover|page}-[slug].md` before invoking `image_generate`. Because `image_generate` is prompt-only, character consistency is enforced by **embedding character descriptions (sourced from `characters/characters.md`) inline in every page prompt during Step 5**. The embedding is done uniformly whether or not a PNG sheet is produced in 7.1; the PNG is only a review/regeneration aid.
+
+**Backup rule**: existing `prompts/…md` and `…png` files → rename with `-backup-YYYYMMDD-HHMMSS` suffix before regenerating.
+
+Full step-by-step workflow (analysis, storyboard, review gates, regeneration variants): [references/workflow.md](references/workflow.md).
+
+## References
+
+**Core Templates**:
+- [analysis-framework.md](references/analysis-framework.md) - Deep content analysis
+- [character-template.md](references/character-template.md) - Character definition format
+- [storyboard-template.md](references/storyboard-template.md) - Storyboard structure
+- [ohmsha-guide.md](references/ohmsha-guide.md) - Ohmsha manga specifics
+
+**Style Definitions**:
+- `references/art-styles/` - Art styles (ligne-claire, manga, realistic, ink-brush, chalk, minimalist)
+- `references/tones/` - Tones (neutral, warm, dramatic, romantic, energetic, vintage, action)
+- `references/presets/` - Presets with special rules (ohmsha, wuxia, shoujo, concept-story, four-panel)
+- `references/layouts/` - Layouts (standard, cinematic, dense, splash, mixed, webtoon, four-panel)
+
+**Workflow**:
+- [workflow.md](references/workflow.md) - Full workflow details
+- [auto-selection.md](references/auto-selection.md) - Content signal analysis
+- [partial-workflows.md](references/partial-workflows.md) - Partial workflow options
+
+## Page Modification
+
+| Action | Steps |
+|--------|-------|
+| **Edit** | **Update prompt file FIRST** → regenerate image → download new PNG |
+| **Add** | Create prompt at position → generate with character descriptions embedded → renumber subsequent → update storyboard |
+| **Delete** | Remove files → renumber subsequent → update storyboard |
+
+**IMPORTANT**: When updating pages, ALWAYS update the prompt file (`prompts/NN-{cover|page}-[slug].md`) FIRST before regenerating. This ensures changes are documented and reproducible.
+
+## Pitfalls
+
+- Image generation: 10-30 seconds per page; auto-retry once on failure
+- **Always download** the URL returned by `image_generate` to a local PNG — downstream tooling (and the user's review) expects files in the output directory, not ephemeral URLs
+- Use stylized alternatives for sensitive public figures
+- **Step 2 confirmation required** - do not skip
+- **Steps 4/6 conditional** - only if user requested in Step 2
+- **Step 7.1 character sheet** - recommended for multi-page comics, optional for simple presets. The PNG is a review/regeneration aid; page prompts (written in Step 5) use the text descriptions in `characters/characters.md`, not the PNG. `image_generate` does not accept images as visual input
+- **Strip secrets** — scan source content for API keys, tokens, or credentials before writing any output file
diff --git a/skills/creative/baoyu-comic/references/analysis-framework.md b/skills/creative/baoyu-comic/references/analysis-framework.md
@@ -0,0 +1,176 @@
+# Comic Content Analysis Framework
+
+Deep analysis framework for transforming source content into effective visual storytelling.
+
+## Purpose
+
+Before creating a comic, thoroughly analyze the source material to:
+- Identify the target audience and their needs
+- Determine what value the comic will deliver
+- Extract narrative potential for visual storytelling
+- Plan character arcs and key moments
+
+## Analysis Dimensions
+
+### 1. Core Content (Understanding "What")
+
+**Central Message**
+- What is the single most important idea readers should take away?
+- Can you express it in one sentence?
+
+**Key Concepts**
+- What are the essential concepts readers must understand?
+- How should these concepts be visualized?
+- Which concepts need simplified explanations?
+
+**Content Structure**
+- How is the source material organized?
+- What is the natural narrative arc?
+- Where are the climax and turning points?
+
+**Evidence & Examples**
+- What concrete examples, data, or stories support the main ideas?
+- Which examples translate well to visual panels?
+- What can be shown rather than told?
+
+### 2. Context & Background (Understanding "Why")
+
+**Source Origin**
+- Who created this content? What is their perspective?
+- What was the original purpose?
+- Is there bias to be aware of?
+
+**Historical/Cultural Context**
+- When and where does the story take place?
+- What background knowledge do readers need?
+- What period-specific visual elements are required?
+
+**Underlying Assumptions**
+- What does the source assume readers already know?
+- What implicit beliefs or values are present?
+- Should the comic challenge or reinforce these?
+
+### 3. Audience Analysis
+
+**Primary Audience**
+- Who will read this comic?
+- What is their existing knowledge level?
+- What are their interests and motivations?
+
+**Secondary Audiences**
+- Who else might benefit from this comic?
+- How might their needs differ?
+
+**Reader Questions**
+- What questions will readers have?
+- What misconceptions might they bring?
+- What "aha moments" can we create?
+
+### 4. Value Proposition
+
+**Knowledge Value**
+- What will readers learn?
+- What new perspectives will they gain?
+- How will this change their understanding?
+
+**Emotional Value**
+- What emotions should readers feel?
+- What connections will they make with characters?
+- What will make this memorable?
+
+**Practical Value**
+- Can readers apply what they learn?
+- What actions might this inspire?
+- What conversations might it spark?
+
+### 5. Narrative Potential
+
+**Story Arc Candidates**
+- What natural narratives exist in the content?
+- Where is the conflict or tension?
+- What transformations occur?
+
+**Character Potential**
+- Who are the key figures?
+- What are their motivations and obstacles?
+- How do they change throughout?
+
+**Visual Opportunities**
+- What scenes have strong visual potential?
+- Where can abstract concepts become concrete images?
+- What metaphors can be visualized?
+
+**Dramatic Moments**
+- What are the breakthrough/revelation moments?
+- Where are the emotional peaks?
+- What creates tension and release?
+
+### 6. Adaptation Considerations
+
+**What to Keep**
+- Essential facts and ideas
+- Key quotes or moments
+- Core emotional beats
+
+**What to Simplify**
+- Complex explanations
+- Dense technical details
+- Lengthy descriptions
+
+**What to Expand**
+- Brief mentions that deserve more attention
+- Implied emotions or relationships
+- Visual details not in source
+
+**What to Omit**
+- Tangential information
+- Redundant examples
+- Content that doesn't serve the narrative
+
+## Output Format
+
+Analysis results should be saved to `analysis.md` with:
+
+1. **YAML Front Matter**: Metadata (title, topic, time_span, source_language, user_language, aspect_ratio, recommended_page_count, recommended_art, recommended_tone, recommended_layout)
+2. **Target Audience**: Primary, secondary, tertiary audiences with their needs
+3. **Value Proposition**: What readers will gain (knowledge, emotional, practical)
+4. **Core Themes**: Table with theme, narrative potential, visual opportunity
+5. **Key Figures & Story Arcs**: Character profiles with arcs, visual identity, key moments
+6. **Content Signals**: Style and layout recommendations based on content type
+7. **Recommended Approaches**: Narrative approaches ranked by suitability
+
+### YAML Front Matter Example
+
+```yaml
+---
+title: "Alan Turing: The Father of Computing"
+topic: alan-turing-biography
+time_span: 1912-1954
+source_language: en
+user_language: zh  # User-specified or detected from conversation
+aspect_ratio: "3:4"
+recommended_page_count: 16
+recommended_art: ligne-claire  # ligne-claire|manga|realistic|ink-brush|chalk
+recommended_tone: neutral      # neutral|warm|dramatic|romantic|energetic|vintage|action
+recommended_layout: mixed      # standard|cinematic|dense|splash|mixed|webtoon
+---
+```
+
+### Language Fields
+
+| Field | Description |
+|-------|-------------|
+| `source_language` | Detected language of source content |
+| `user_language` | Output language for comic (user-specified option > conversation language > source_language) |
+
+## Analysis Checklist
+
+Before proceeding to storyboard:
+
+- [ ] Can I state the core message in one sentence?
+- [ ] Do I know exactly who will read this comic?
+- [ ] Have I identified at least 3 ways this comic provides value?
+- [ ] Are there clear protagonists with compelling arcs?
+- [ ] Have I found at least 5 visually powerful moments?
+- [ ] Do I understand what to keep, simplify, expand, and omit?
+- [ ] Have I identified the emotional peaks and valleys?
diff --git a/skills/creative/baoyu-comic/references/art-styles/chalk.md b/skills/creative/baoyu-comic/references/art-styles/chalk.md
@@ -0,0 +1,101 @@
+# chalk
+
+粉笔画风 - Chalkboard aesthetic with hand-drawn warmth
+
+## Overview
+
+Classic classroom chalkboard aesthetic with hand-drawn chalk illustrations. Nostalgic educational feel with imperfect, sketchy lines that capture the warmth of traditional teaching.
+
+## Line Work
+
+- Sketchy, imperfect hand-drawn lines
+- Chalk texture on all strokes
+- Varying line weight from chalk pressure
+- Soft edges, no sharp digital lines
+- Visible chalk dust effects
+
+## Character Design
+
+- Simplified, friendly character designs
+- Stick figures to semi-detailed range
+- Expressive through simple gestures
+- Approachable, non-intimidating
+- Educational presenter style
+
+## Background
+
+- Chalkboard Black (#1A1A1A) or Dark Green-Black (#1C2B1C)
+- Realistic chalkboard texture
+- Subtle scratches and dust particles
+- Faint eraser marks for authenticity
+- Wooden frame border optional
+
+## Typography
+
+- Hand-drawn chalk lettering style
+- Visible chalk texture on text
+- Imperfect baseline adds authenticity
+- White or bright colored chalk for emphasis
+
+## Visual Elements
+
+- Hand-drawn chalk illustrations
+- Chalk dust effects around elements
+- Doodles: stars, arrows, underlines, circles
+- Mathematical formulas and diagrams
+- Eraser smudges and chalk residue
+- Stick figures and simple icons
+- Connection lines with hand-drawn feel
+
+## Default Color Palette
+
+| Role | Color | Hex |
+|------|-------|-----|
+| Background | Chalkboard Black | #1A1A1A |
+| Alt Background | Green-Black | #1C2B1C |
+| Primary Text | Chalk White | #F5F5F5 |
+| Accent 1 | Chalk Yellow | #FFE566 |
+| Accent 2 | Chalk Pink | #FF9999 |
+| Accent 3 | Chalk Blue | #66B3FF |
+| Accent 4 | Chalk Green | #90EE90 |
+| Accent 5 | Chalk Orange | #FFB366 |
+
+## Style Rules
+
+### Do
+- Maintain authentic chalk texture on all elements
+- Use imperfect, hand-drawn quality throughout
+- Add subtle chalk dust and smudge effects
+- Create visual hierarchy with color variety
+- Include playful doodles and annotations
+
+### Don't
+- Use perfect geometric shapes
+- Create clean digital-looking lines
+- Add photorealistic elements
+- Use gradients or glossy effects
+
+## Quality Markers
+
+- ✓ Authentic chalk texture throughout
+- ✓ Imperfect, hand-drawn quality
+- ✓ Readable despite sketchy style
+- ✓ Nostalgic classroom feel
+- ✓ Effective color hierarchy
+- ✓ Playful educational aesthetic
+
+## Compatibility
+
+| Tone | Fit | Notes |
+|------|-----|-------|
+| neutral | ✓✓ | Classic educational |
+| warm | ✓✓ | Nostalgic feel |
+| dramatic | ✗ | Style mismatch |
+| vintage | ✓ | Old school feel |
+| romantic | ✗ | Style mismatch |
+| energetic | ✓✓ | Fun learning |
+| action | ✗ | Style mismatch |
+
+## Best For
+
+Educational content, tutorials, classroom themes, teaching materials, workshops, informal learning, knowledge sharing
diff --git a/skills/creative/baoyu-comic/references/art-styles/ink-brush.md b/skills/creative/baoyu-comic/references/art-styles/ink-brush.md
@@ -0,0 +1,97 @@
+# ink-brush
+
+水墨画风 - Chinese ink brush aesthetics with dynamic strokes
+
+## Overview
+
+Traditional Chinese ink brush painting style adapted for comics. Combines calligraphic brush strokes with ink wash effects. Creates atmospheric, artistic visuals rooted in East Asian aesthetics.
+
+## Line Work
+
+- 2-3px dynamic brush strokes with varying weight
+- Ink wash effects, traditional Chinese brush feel
+- Bold, confident strokes with sharp edges
+- Flowing lines for fabric and hair
+- Pressure-sensitive stroke variation
+
+## Character Design
+
+- Realistic human proportions (7.5-8 head heights)
+- Defined features with ink brush definition
+- Dynamic poses capturing movement
+- Flowing hair and clothing in motion
+- Traditional attire options (robes, hanfu)
+- Intense, expressive faces
+
+## Brush Techniques
+
+| Technique | Usage |
+|-----------|-------|
+| Bold strokes | Character outlines |
+| Fine lines | Details, hair |
+| Ink wash | Atmosphere, shadows |
+| Dry brush | Texture, aging |
+| Splatter | Impact, drama |
+
+## Background Treatment
+
+- Dramatic landscapes: mountains, waterfalls, temples
+- Ink wash atmospheric effects
+- Misty, layered depth
+- Traditional architecture elements
+- High contrast silhouettes
+- Negative space as design element
+
+## Color Approach
+
+- Ink gradients as primary
+- Limited accent colors
+- Traditional Chinese palette
+- Atmospheric color washes
+- High contrast compositions
+
+## Default Color Palette
+
+| Role | Color | Hex |
+|------|-------|-----|
+| Primary | Deep black ink | #1A1A1A |
+| Accent | Crimson red | #8B0000 |
+| Accent | Imperial gold | #D4AF37 |
+| Skin | Natural tan | #D4A574 |
+| Background | Misty gray | #9CA3AF |
+| Background | Earth tone | #8B7355 |
+| Wash | Ink gradient | #2D3748 |
+
+## Visual Elements
+
+- Calligraphic text integration
+- Seal stamps (optional)
+- Ink splatter effects
+- Flowing fabric trails
+- Atmospheric mist
+- Mountain silhouettes
+
+## Quality Markers
+
+- ✓ Dynamic brush stroke quality
+- ✓ Authentic ink wash atmosphere
+- ✓ High contrast compositions
+- ✓ Flowing movement in fabric/hair
+- ✓ Traditional aesthetic elements
+- ✓ Atmospheric depth
+
+## Compatibility
+
+| Tone | Fit | Notes |
+|------|-----|-------|
+| neutral | ✓ | Contemplative stories |
+| warm | ✓ | Nostalgic, gentle |
+| dramatic | ✓✓ | High contrast |
+| vintage | ✓✓ | Historical pieces |
+| romantic | ✗ | Style mismatch |
+| energetic | ✗ | Too refined |
+| action | ✓✓ | Martial arts |
+
+## Best For
+
+Chinese historical stories, martial arts, traditional tales, contemplative narratives, artistic adaptations
diff --git a/skills/creative/baoyu-comic/references/art-styles/ligne-claire.md b/skills/creative/baoyu-comic/references/art-styles/ligne-claire.md
@@ -0,0 +1,75 @@
+# ligne-claire
+
+清线画风 - Uniform lines, flat colors, European comic tradition
+
+## Overview
+
+Classic European comic style originating from Hergé's Tintin. Characterized by clean, uniform outlines and flat color fills without gradients. Creates a timeless, accessible aesthetic suitable for educational and narrative content.
+
+## Line Work
+
+- Uniform, clean outlines with consistent weight (2px)
+- No hatching or cross-hatching for shading
+- Sharp, precise edges on all elements
+- Black ink outlines on all figures and objects
+- Shadows indicated through flat color areas, not line techniques
+
+## Character Design
+
+- Slightly stylized/cartoonish characters with realistic proportions
+- Distinctive, recognizable facial features
+- Expressive faces with clear emotions
+- Period-appropriate clothing with attention to detail
+- Consistent character appearance across panels
+- 6-7 head height proportions
+
+## Background Treatment
+
+- Detailed, realistic backgrounds with architectural accuracy
+- Period-specific props and technology
+- Clear spatial depth and perspective
+- Environmental storytelling through details
+- Contrast between simplified characters and detailed backgrounds
+
+## Color Approach
+
+- Flat colors without gradients (true to Ligne Claire tradition)
+- Limited palette per page for cohesion
+- Colors support narrative mood
+- Consistent lighting logic within scenes
+
+## Default Color Palette
+
+| Role | Color | Hex |
+|------|-------|-----|
+| Primary Blue | Clean blue | #3182CE |
+| Primary Red | Classic red | #E53E3E |
+| Primary Yellow | Warm yellow | #ECC94B |
+| Skin | Warm tan | #F7CFAE |
+| Background Light | Light cream | #FFFAF0 |
+| Background Sky | Sky blue | #BEE3F8 |
+
+## Quality Markers
+
+- ✓ Clean, uniform line weight throughout
+- ✓ Flat colors without gradients
+- ✓ Detailed backgrounds, stylized characters
+- ✓ Clear panel borders and reading flow
+- ✓ Hand-drawn text style
+- ✓ Proper perspective in environments
+
+## Compatibility
+
+| Tone | Fit | Notes |
+|------|-----|-------|
+| neutral | ✓✓ | Classic combination |
+| warm | ✓✓ | Nostalgic stories |
+| dramatic | ✓ | Works with high contrast |
+| vintage | ✓ | Period pieces |
+| romantic | ✗ | Style mismatch |
+| energetic | ✓ | Lighter stories |
+| action | ✗ | Lacks dynamic lines |
+
+## Best For
+
+Educational content, balanced narratives, biography comics, historical stories
diff --git a/skills/creative/baoyu-comic/references/art-styles/manga.md b/skills/creative/baoyu-comic/references/art-styles/manga.md
@@ -0,0 +1,93 @@
+# manga
+
+日漫画风 - Anime/manga aesthetics with expressive characters
+
+## Overview
+
+Japanese manga art style characterized by large expressive eyes, dynamic poses, and visual emotion indicators. Versatile style that works across genres from educational to romantic to action.
+
+## Line Work
+
+- Clean, smooth lines (1.5-2px)
+- Expressive weight variation for emphasis
+- Smooth curves, dynamic strokes
+- Speed lines and motion effects available
+- Screen tone effects for atmosphere
+
+## Character Design
+
+- Anime/manga proportions: larger eyes, expressive faces
+- 5-7 head height proportions (varies by sub-style)
+- Clear emotional indicators (！, ？, sweat drops, sparkles)
+- Dynamic poses and gestures
+- Detailed hair with individual strands
+- Fashionable clothing with natural folds
+
+## Eye Styles
+
+| Type | Description |
+|------|-------------|
+| Standard | Medium-large, 2-3 highlights |
+| Educational | Friendly, approachable eyes |
+| Dramatic | Intense, detailed irises |
+| Cute | Very large, sparkly eyes |
+
+## Background Treatment
+
+- Simplified during dialogue/explanation
+- Detailed for establishing shots
+- Screen tone gradients for mood
+- Abstract backgrounds for emotional moments
+- Technical diagrams styled as displays
+
+## Color Approach
+
+- Clean, bright anime colors
+- Soft gradients on skin
+- Vibrant palette options
+- Light and shadow with soft transitions
+- Color coding for character identification
+
+## Default Color Palette
+
+| Role | Color | Hex |
+|------|-------|-----|
+| Primary Blue | Bright blue | #4299E1 |
+| Primary Orange | Warm orange | #ED8936 |
+| Primary Green | Soft green | #68D391 |
+| Skin | Anime warm | #FEEBC8 |
+| Background | Clean white | #FFFFFF |
+| Highlight | Golden | #FFD700 |
+
+## Visual Elements
+
+- Speech bubbles: rounded (normal), spiky (excitement)
+- Sound effects integrated visually
+- Emotion symbols (sweat drops, anger marks, hearts)
+- Speed lines and motion blur
+- Sparkle and glow effects
+
+## Quality Markers
+
+- ✓ Expressive character faces
+- ✓ Clean, consistent line work
+- ✓ Dynamic poses and compositions
+- ✓ Appropriate use of manga conventions
+- ✓ Readable panel flow
+- ✓ Consistent character designs
+
+## Compatibility
+
+| Tone | Fit | Notes |
+|------|-----|-------|
+| neutral | ✓✓ | Educational manga |
+| warm | ✓ | Slice of life |
+| dramatic | ✓ | Intense moments |
+| romantic | ✓✓ | Shoujo style |
+| energetic | ✓✓ | Shonen style |
+| vintage | ✗ | Style mismatch |
+| action | ✓✓ | Battle manga |
+
+## Best For
+
+Educational tutorials, romance, action, coming-of-age, technical explanations, youth-oriented content
diff --git a/skills/creative/baoyu-comic/references/art-styles/minimalist.md b/skills/creative/baoyu-comic/references/art-styles/minimalist.md
@@ -0,0 +1,84 @@
+# minimalist
+
+极简画风 - Clean black line art, limited spot color, simplified stick-figure characters
+
+## Overview
+
+Minimalist cartoon illustration characterized by clean black line art on white background with very limited spot color for emphasis. Characters are simplified to near-stick-figure abstraction, focusing on gesture and concept rather than anatomical detail. Designed for business allegory, quick-read educational content, and concept illustration.
+
+## Line Work
+
+- Clean, uniform black lines (1.5-2px)
+- No hatching, cross-hatching, or shading techniques
+- Minimal detail — every line serves a purpose
+- Bold outlines for characters, thinner lines for props/labels
+- No decorative flourishes or ornamental lines
+
+## Character Design
+
+- Highly simplified, stick-figure-like business characters
+- Circle or oval heads with minimal facial features (dot eyes, simple line mouth)
+- Body as simple geometric shapes or line constructions
+- Distinguishing features through props only (tie, hat, briefcase, glasses)
+- No anatomical detail — expressive through posture and gesture
+- 4-5 head height proportions (squat, iconic)
+
+## Background Treatment
+
+- Mostly blank/white — negative space is a design element
+- Minimal environmental cues (a line for ground, simple desk outline)
+- Concept labels and text annotations replace detailed environments
+- Icons and symbols over realistic rendering
+- No perspective or spatial depth
+
+## Color Approach
+
+- Primarily black and white (90%+ of the image)
+- 1-2 spot accent colors for emphasis on key concepts
+- Accent color used sparingly: highlighting key objects, text labels, concept indicators
+- No gradients, no shading, no color fills on backgrounds
+- Color draws the eye to the most important element in each panel
+
+## Default Color Palette
+
+| Role | Color | Hex |
+|------|-------|-----|
+| Primary | Black ink | `#1A1A1A` |
+| Background | Clean white | `#FFFFFF` |
+| Accent 1 | Spot orange | `#FF6B35` |
+| Accent 2 | Spot blue (optional) | `#3182CE` |
+| Text labels | Dark gray | `#4A4A4A` |
+| Panel border | Medium gray | `#666666` |
+
+## Visual Elements
+
+- Text labels with accent-color backgrounds or underlines for key terms
+- Simple icons: arrows, circles, checkmarks, crosses
+- Concept highlight boxes with spot color
+- Minimal speech bubbles (simple oval or rectangle, thin black outline)
+- No sound effects, no motion lines, no screen tones
+
+## Quality Markers
+
+- ✓ Clean, purposeful line work with no unnecessary detail
+- ✓ 90%+ black-and-white with strategic spot color
+- ✓ Simplified characters readable at small sizes
+- ✓ Text labels integrated naturally into panels
+- ✓ Strong negative space usage
+- ✓ Every element serves the narrative point
+
+## Compatibility
+
+| Tone | Fit | Notes |
+|------|-----|-------|
+| neutral | ✓✓ | Ideal for business/educational content |
+| warm | ✓ | Works for gentle stories, slight warmth in accent |
+| energetic | ✓ | Works for punchy, high-energy content |
+| dramatic | ✗ | Style too stripped down for dramatic intensity |
+| vintage | ✗ | Minimalist aesthetic conflicts with aged/textured look |
+| romantic | ✗ | No capacity for decorative/soft elements |
+| action | ✗ | No dynamic line capability for speed/impact |
+
+## Best For
+
+Business allegory, management fables, short concept illustration, four-panel comic strips, quick-insight education, social media content
diff --git a/skills/creative/baoyu-comic/references/art-styles/realistic.md b/skills/creative/baoyu-comic/references/art-styles/realistic.md
@@ -0,0 +1,89 @@
+# realistic
+
+写实画风 - Digital painting with realistic proportions and lighting
+
+## Overview
+
+Full-color realistic manga style using digital painting techniques. Features anatomically accurate characters, rich gradients, and detailed environmental rendering. Sophisticated aesthetic for mature audiences.
+
+## Line Work
+
+- Clean, precise outlines with clear contours
+- Uniform line weight for character definition
+- No excessive hatching - rely on color for depth
+- Smooth curves and realistic anatomical lines
+- Ligne Claire influence: clean but not simplified
+
+## Character Design
+
+- Realistic human proportions (7-8 head heights)
+- Anatomically accurate features and expressions
+- Detailed facial structure without exaggeration
+- Natural poses and body language
+- Consistent appearance across panels
+- Subtle expressions rather than manga-style
+
+## Rendering Style
+
+- Full-color digital painting with rich gradients
+- Soft shadow transitions on skin and fabric
+- Realistic material textures (glass, liquid, fabric, wood)
+- Detailed hair with natural shine and volume
+- Environmental lighting affects all elements
+- NOT flat cel-shading - smooth color blending
+
+## Background Treatment
+
+- Highly detailed, realistic environments
+- Accurate perspective and spatial depth
+- Atmospheric lighting (warm indoor, cool outdoor)
+- Professional settings rendered with precision
+- Props and objects with realistic textures
+
+## Color Approach
+
+- Rich gradients for depth and volume
+- Realistic lighting with warm/cool contrast
+- Material-specific rendering
+- Subtle color temperature shifts
+- Professional, sophisticated palette
+
+## Default Color Palette
+
+| Role | Color | Hex |
+|------|-------|-----|
+| Skin Light | Natural warm | #F5D6C6 |
+| Skin Shadow | Warm shadow | #E8C4B0 |
+| Environment | Warm wood | #8B7355 |
+| Environment Cool | Cool stone | #9CA3AF |
+| Accent | Wine red | #722F37 |
+| Accent Gold | Gold | #D4AF37 |
+| Light Warm | Amber | #FFB347 |
+| Light Cool | Cool blue | #B0C4DE |
+
+## Quality Markers
+
+- ✓ Anatomically accurate proportions
+- ✓ Smooth color gradients (not flat fills)
+- ✓ Realistic material textures
+- ✓ Detailed, atmospheric backgrounds
+- ✓ Natural lighting with soft shadows
+- ✓ Expressive but subtle expressions
+- ✓ Professional aesthetic
+- ✓ Clean speech bubbles
+
+## Compatibility
+
+| Tone | Fit | Notes |
+|------|-----|-------|
+| neutral | ✓✓ | Professional content |
+| warm | ✓✓ | Nostalgic stories |
+| dramatic | ✓✓ | High drama |
+| vintage | ✓✓ | Period pieces |
+| romantic | ✗ | Style mismatch |
+| energetic | ✗ | Too refined |
+| action | ✓ | Serious action |
+
+## Best For
+
+Professional topics (wine, food, business), lifestyle content, adult narratives, documentary-style, mature educational guides
diff --git a/skills/creative/baoyu-comic/references/auto-selection.md b/skills/creative/baoyu-comic/references/auto-selection.md
@@ -0,0 +1,71 @@
+# Auto Selection
+
+Content signals determine default art + tone + layout (or preset).
+
+## Content Signal Matrix
+
+| Content Signals | Art Style | Tone | Layout | Preset |
+|-----------------|-----------|------|--------|--------|
+| Tutorial, how-to, beginner | manga | neutral | webtoon | **ohmsha** |
+| Computing, AI, programming | manga | neutral | dense | **ohmsha** |
+| Technical explanation, educational | manga | neutral | webtoon | **ohmsha** |
+| Pre-1950, classical, ancient | realistic | vintage | cinematic | - |
+| Personal story, mentor | ligne-claire | warm | standard | - |
+| Psychology, motivation, self-help, coaching | manga | warm | standard | **concept-story** |
+| Business narrative, management, leadership | manga | warm | standard | **concept-story** |
+| Conflict, breakthrough | (inherit) | dramatic | splash | - |
+| Wine, food, lifestyle | realistic | neutral | cinematic | - |
+| Martial arts, wuxia, xianxia | ink-brush | action | splash | **wuxia** |
+| Romance, love, school life | manga | romantic | standard | **shoujo** |
+| Business allegory, fable, parable, short insight, 四格 | minimalist | neutral | four-panel | **four-panel** |
+| Biography, balanced | ligne-claire | neutral | mixed | - |
+
+## Preset Recommendation Rules
+
+**When preset is recommended**: Load `presets/{preset}.md` and apply all special rules.
+
+### ohmsha
+- **Triggers**: Tutorial, technical, educational, computing, programming, how-to, beginner
+- **Special rules**: Visual metaphors, NO talking heads, gadget reveals, Doraemon-style characters
+- **Base**: manga + neutral + webtoon/dense
+
+### wuxia
+- **Triggers**: Martial arts, wuxia, xianxia, cultivation, swordplay
+- **Special rules**: Qi effects, combat visuals, atmospheric elements
+- **Base**: ink-brush + action + splash
+
+### shoujo
+- **Triggers**: Romance, love story, school life, emotional drama
+- **Special rules**: Decorative elements, eye details, romantic beats
+- **Base**: manga + romantic + standard
+
+### concept-story
+- **Triggers**: Psychology, motivation, self-help, business narrative, management, leadership, personal growth, coaching, soft skills, abstract concept through story
+- **Special rules**: Visual symbol system, growth arc, dialogue+action balance, original characters
+- **Base**: manga + warm + standard
+
+### four-panel
+- **Triggers**: Business allegory, fable, parable, short insight, four-panel, 四格, 四格漫画, single-page comic, minimalist comic strip
+- **Special rules**: Strict 起承转合 4-panel structure, B&W + spot color, simplified stick-figure characters, single-page story
+- **Base**: minimalist + neutral + four-panel
+
+## Compatibility Matrix
+
+Art Style × Tone combinations work best when matched appropriately:
+
+| Art Style | ✓✓ Best | ✓ Works | ✗ Avoid |
+|-----------|---------|---------|---------|
+| ligne-claire | neutral, warm | dramatic, vintage, energetic | romantic, action |
+| manga | neutral, romantic, energetic, action | warm, dramatic | vintage |
+| realistic | neutral, warm, dramatic, vintage | action | romantic, energetic |
+| ink-brush | neutral, dramatic, action, vintage | warm | romantic, energetic |
+| chalk | neutral, warm, energetic | vintage | dramatic, action, romantic |
+| minimalist | neutral | warm, energetic | dramatic, vintage, romantic, action |
+
+**Note**: Art Style × Tone × Layout can be freely combined. Incompatible combinations work but may produce unexpected results.
+
+## Priority Order
+
+1. User-specified options (art / tone / style)
+2. Content signal analysis → auto-selection
+3. Fallback: ligne-claire + neutral + standard
diff --git a/skills/creative/baoyu-comic/references/base-prompt.md b/skills/creative/baoyu-comic/references/base-prompt.md
@@ -0,0 +1,98 @@
+Create a knowledge biography comic page following these guidelines:
+
+## Image Specifications
+
+- **Type**: Comic book page with multiple panels
+- **Orientation**: Portrait (vertical)
+- **Aspect Ratio**: 2:3
+- **Style**: See style-specific reference for visual guidelines
+
+## Panel Structure
+
+### Panel Borders
+- Clean black lines (1-2px) around each panel
+- White gutters between panels (8-12px)
+- Panels arranged for clear reading flow
+- Variety in panel sizes for visual rhythm
+
+### Panel Composition
+- Clear focal points in each panel
+- Proper use of foreground, midground, background
+- Camera angles vary: eye level, bird's eye, low angle, close-up, wide shot
+- Action flows logically between panels
+- Negative space used intentionally
+
+## Text Elements
+
+### Speech Bubbles
+- **Dialogue**: Oval/elliptical bubbles with pointed tails
+- White fill with thin black outline
+- Tail points clearly to speaker
+- Hand-lettered style font (not computer-generated)
+
+### Narrator Boxes
+- **Fourth Wall/Narrator**: Rectangular boxes
+- Often positioned at panel edges (top or bottom)
+- Slightly different fill color (cream or light yellow)
+- Used for commentary, time jumps, explanations
+
+### Thought Bubbles
+- Cloud-shaped with bubble trail leading to thinker
+- Softer outline than speech bubbles
+- For internal monologue
+
+### Caption Bars
+- Rectangular bars at panel edges
+- Time and place information
+- "Meanwhile...", "Three years later..." type transitions
+- Darker fill with white text, or vice versa
+
+### Typography
+- Hand-drawn lettering style throughout
+- Bold for emphasis and key terms
+- Consistent letter sizing
+- Chinese text: use full-width punctuation ""，。！
+- Clear hierarchy: titles > dialogue > captions
+
+## Scientific/Concept Visualization
+
+When depicting abstract concepts:
+
+| Concept | Visual Metaphor |
+|---------|----------------|
+| Neural networks | Glowing nodes connected by clean lines |
+| Data flow | Luminous particles along simple paths |
+| Algorithms | Geometric patterns, building blocks |
+| Logic/proof | Interlocking puzzle pieces |
+| Discovery | Light breaking through darkness |
+| Uncertainty | Forking paths, question marks |
+| Time | Clock motifs, calendar pages |
+
+- Integrate diagrams naturally into narrative panels
+- Use inset panels or thought-bubble style for explanations
+- Simplified iconography over realistic depiction
+
+## Fourth Wall / Narrator Character
+
+When depicting narrator characters addressing the reader:
+- Character may look directly out of panel
+- Can appear in "present day" framing scenes
+- Distinct visual treatment from main timeline
+- Often at page edges or in dedicated panels
+- May comment on or question the events shown
+
+## Historical Accuracy
+
+- Research period-specific details: costumes, technology, architecture
+- Show aging naturally for characters across time periods
+- Iconic items and locations rendered recognizably
+- Balance accuracy with stylization
+
+## Language
+
+- All text in Chinese (中文) unless source material is in another language
+- Use Chinese full-width punctuation: ""，。！
+
+---
+
+Please generate the comic page based on the content provided below:
diff --git a/skills/creative/baoyu-comic/references/character-template.md b/skills/creative/baoyu-comic/references/character-template.md
@@ -0,0 +1,180 @@
+# Character Definition Template
+
+## Character Document Format
+
+Create `characters/characters.md` with the following structure:
+
+```markdown
+# Character Definitions - [Comic Title]
+
+**Style**: [selected style]
+**Art Direction**: [Ligne Claire / Manga / etc.]
+
+---
+
+## Character 1: [Name]
+
+**Role**: [Protagonist / Mentor / Antagonist / Narrator]
+**Age**: [approximate age or age range in story]
+
+**Appearance**:
+- Face shape: [oval/square/round]
+- Hair: [color, style, length]
+- Eyes: [color, shape, distinctive features]
+- Build: [height, body type]
+- Distinguishing features: [glasses, beard, scar, etc.]
+
+**Costume**:
+- Default outfit: [detailed description]
+- Color palette: [primary colors for this character]
+- Accessories: [hat, bag, tools, etc.]
+
+**Expression Range**:
+- Neutral: [description]
+- Happy/Excited: [description]
+- Thinking/Confused: [description]
+- Determined: [description]
+
+**Visual Reference Notes**:
+[Any specific artistic direction]
+
+---
+
+## Character 2: [Name]
+...
+```
+
+## Reference Sheet Image Prompt
+
+After character definitions, include a prompt for generating the reference sheet:
+
+```markdown
+## Reference Sheet Prompt
+
+Character reference sheet in [style] style, clean lines, flat colors:
+
+[ROW 1 - Character Name]:
+- Front view: [detailed description]
+- 3/4 view: [description]
+- Expression sheet: Neutral | Happy | Focused | Worried
+
+[ROW 2 - Character Name]:
+...
+
+COLOR PALETTE:
+- [Character 1]: [colors]
+- [Character 2]: [colors]
+
+White background, clear labels under each character.
+```
+
+## Example: Turing Biography
+
+```markdown
+# Character Definitions - The Imitation Game
+
+**Style**: classic (Ligne Claire)
+**Art Direction**: Clean lines, muted colors, period-accurate details
+
+---
+
+## Character 1: Alan Turing
+
+**Role**: Protagonist
+**Age**: 25-40 (varies across story)
+
+**Appearance**:
+- Face shape: Oval, slightly angular
+- Hair: Dark brown, wavy, slightly disheveled
+- Eyes: Deep-set, intense gaze
+- Build: Tall, lean, slightly awkward posture
+- Distinguishing features: Prominent brow, thoughtful expression
+
+**Costume**:
+- Default outfit: Tweed jacket with elbow patches, white shirt, no tie
+- Color palette: Muted browns, navy blue, cream
+- Accessories: Occasionally a pipe, papers/notebooks
+
+**Expression Range**:
+- Neutral: Thoughtful, slightly distant
+- Happy/Excited: Eureka moment, eyes bright, subtle smile
+- Thinking/Confused: Furrowed brow, looking at abstract space
+- Determined: Jaw set, focused eyes
+
+---
+
+## Character 2: The Bombe Machine
+
+**Role**: Supporting (anthropomorphized)
+**Appearance**:
+- Large brass and wood cabinet
+- Dial "eyes" that can express states
+- Paper tape "mouth"
+- Indicator lights for emotions
+
+**Expression Range**:
+- Processing: Spinning dials, humming
+- Success: Lights up warmly
+- Stuck: Smoke wisps, stuttering
+
+---
+
+## Reference Sheet Prompt
+
+Character reference sheet in Ligne Claire style, clean lines, flat colors:
+
+TOP ROW - Alan Turing:
+- Front view: Young man, 30s, short dark wavy hair, thoughtful expression, wearing tweed jacket with elbow patches, white shirt
+- 3/4 view: Same character, slight smile, showing profile of nose
+- Expression sheet: Neutral | Excited (eureka moment) | Focused (working) | Worried
+
+BOTTOM ROW - The Bombe Machine (anthropomorphized):
+- Bombe machine as character: Large, brass and wood, dial "eyes", paper tape "mouth"
+- Expressions: Processing (spinning dials) | Success (lights up) | Stuck (smoke wisps)
+
+COLOR PALETTE:
+- Turing: Muted browns (#8B7355), navy blue (#2C3E50), cream (#F5F5DC)
+- Machine: Brass (#B5A642), mahogany (#4E2728), emerald indicators (#2ECC71)
+
+White background, clear labels under each character.
+```
+
+## Handling Age Variants
+
+For biographies spanning many years, define age variants:
+
+```markdown
+## Alan Turing - Age Variants
+
+### Young (1920s, age 10-18)
+- Boyish features, round face
+- School uniform (Sherborne)
+- Curious, eager expression
+
+### Adult (1930s-40s, age 25-35)
+- Angular face, defined jaw
+- Tweed jacket, rumpled appearance
+- Intense, focused expression
+
+### Later (1950s, age 40+)
+- Slightly weathered
+- More casual dress
+- Thoughtful, sometimes melancholic
+```
+
+## Best Practices
+
+| Practice | Description |
+|----------|-------------|
+| Be specific | "Short dark wavy hair, parted left" not just "dark hair" |
+| Use distinguishing features | Glasses, scars, accessories that identify character |
+| Define color codes | Use specific color names or hex codes |
+| Include age markers | Wrinkles, posture, clothing style matching era |
+| Reference real people | For historical figures, note "based on 1940s photographs" |
+
+## Why Character Reference Matters
+
+Without unified character definition, AI generates inconsistent appearances. The reference sheet provides:
+1. Visual anchors for consistent features
+2. Color palettes for consistent coloring
+3. Expression documentation for emotional portrayals
diff --git a/skills/creative/baoyu-comic/references/layouts/cinematic.md b/skills/creative/baoyu-comic/references/layouts/cinematic.md
@@ -0,0 +1,23 @@
+# cinematic
+
+Wide panels, filmic feel
+
+## Panel Structure
+
+- **Panels per page**: 2-4
+- **Structure**: Horizontal emphasis, wide aspect panels
+- **Gutters**: Generous spacing (12-15px)
+
+## Grid Configuration
+
+- 1-2 columns, horizontal emphasis
+- Panel sizes: Wide aspect ratios (3:1, 4:1)
+- Reading flow: Horizontal sweep, filmic rhythm
+
+## Best For
+
+Establishing shots, dramatic moments, landscapes
+
+## Best Style Pairings
+
+dramatic, classic, sepia
diff --git a/skills/creative/baoyu-comic/references/layouts/dense.md b/skills/creative/baoyu-comic/references/layouts/dense.md
@@ -0,0 +1,23 @@
+# dense
+
+Information-rich, educational focus
+
+## Panel Structure
+
+- **Panels per page**: 6-9
+- **Structure**: Compact grid, smaller panels
+- **Gutters**: Tight spacing (4-6px)
+
+## Grid Configuration
+
+- 3 columns × 3 rows
+- Panel sizes: Compact, uniform
+- Reading flow: Rapid progression, information-rich
+
+## Best For
+
+Technical explanations, complex narratives, timelines
+
+## Best Style Pairings
+
+ohmsha, vibrant
diff --git a/skills/creative/baoyu-comic/references/layouts/four-panel.md b/skills/creative/baoyu-comic/references/layouts/four-panel.md
@@ -0,0 +1,40 @@
+# four-panel
+
+四格漫画 - Strict 2×2 grid, single-page story
+
+## Panel Structure
+
+- **Panels per page**: 4 (exactly, no variation)
+- **Structure**: Strict 2×2 equal grid
+- **Gutters**: Consistent white space (8-10px), uniform on all sides
+
+## Grid Configuration
+
+- 2 columns × 2 rows, all panels identical size
+- Panel sizes: Exactly equal (each panel = 25% of content area)
+- Reading flow: Z-pattern — Panel 1 (top-left) → Panel 2 (top-right) → Panel 3 (bottom-left) → Panel 4 (bottom-right)
+
+## Narrative Structure
+
+Each panel serves a specific narrative role (起承转合 / kishōtenketsu):
+
+| Panel | Position | Role | Purpose |
+|-------|----------|------|---------|
+| 1 | Top-left | 起 Setup | Establish situation, introduce characters/problem |
+| 2 | Top-right | 承 Development | Build on setup, add complication or attempt |
+| 3 | Bottom-left | 转 Turn | Twist, key insight, or reversal — the pivotal moment |
+| 4 | Bottom-right | 合 Conclusion | Resolution, punchline, or takeaway |
+
+## Aspect Ratio
+
+- Recommended page aspect: **4:3** (landscape)
+- Landscape gives each panel a comfortable wide rectangle
+- Portrait (3:4) makes panels tall and narrow — avoid for this layout
+
+## Best For
+
+Business allegory, quick-insight education, social media comics, fables, parables, single-concept explanation
+
+## Best Style Pairings
+
+minimalist, ligne-claire, chalk
diff --git a/skills/creative/baoyu-comic/references/layouts/mixed.md b/skills/creative/baoyu-comic/references/layouts/mixed.md
@@ -0,0 +1,23 @@
+# mixed
+
+Dynamic, varied rhythm
+
+## Panel Structure
+
+- **Panels per page**: 3-7 (varies)
+- **Structure**: Intentionally varied for pacing
+- **Gutters**: Dynamic spacing
+
+## Grid Configuration
+
+- Intentionally irregular
+- Panel sizes: Varied for pacing and emphasis
+- Reading flow: Guides eye through varied rhythm
+
+## Best For
+
+Action sequences, emotional arcs, complex stories
+
+## Best Style Pairings
+
+dramatic, vibrant, ohmsha
diff --git a/skills/creative/baoyu-comic/references/layouts/splash.md b/skills/creative/baoyu-comic/references/layouts/splash.md
@@ -0,0 +1,23 @@
+# splash
+
+Impact-focused, key moments
+
+## Panel Structure
+
+- **Panels per page**: 1-2 large + 2-3 small
+- **Structure**: Dominant splash with supporting panels
+- **Gutters**: Varied for emphasis
+
+## Grid Configuration
+
+- 1 dominant panel + 2-3 supporting
+- Panel sizes: 50-70% splash, remainder small
+- Reading flow: Splash dominates, supporting panels accent
+
+## Best For
+
+Revelations, breakthroughs, chapter openings
+
+## Best Style Pairings
+
+dramatic, classic, vibrant
diff --git a/skills/creative/baoyu-comic/references/layouts/standard.md b/skills/creative/baoyu-comic/references/layouts/standard.md
@@ -0,0 +1,23 @@
+# standard
+
+Classic comic grid, versatile
+
+## Panel Structure
+
+- **Panels per page**: 4-6
+- **Structure**: Regular grid with occasional variation
+- **Gutters**: Consistent white space (8-10px)
+
+## Grid Configuration
+
+- 2-3 columns × 2-3 rows
+- Panel sizes: Mostly equal, occasional variation
+- Reading flow: Left→right, top→bottom (Z-pattern)
+
+## Best For
+
+Narrative flow, dialogue scenes
+
+## Best Style Pairings
+
+classic, warm, sepia
diff --git a/skills/creative/baoyu-comic/references/layouts/webtoon.md b/skills/creative/baoyu-comic/references/layouts/webtoon.md
@@ -0,0 +1,30 @@
+# webtoon
+
+Vertical scrolling comic (竖版条漫)
+
+## Panel Structure
+
+- **Panels per page**: 3-5 vertically stacked
+- **Structure**: Single column, vertical flow optimized for scrolling
+- **Gutters**: Generous vertical spacing (20-40px), panels often bleed horizontally
+
+## Grid Configuration
+
+- Single column, vertical stack
+- Panel sizes: Full width, variable height (1:1 to 1:2 aspect)
+- Reading flow: Top→bottom continuous scroll
+
+## Special Features
+
+- Panels can extend beyond frame for dramatic effect
+- Generous whitespace between beats
+- Character close-ups alternate with wide explanation panels
+- "Float" effect - elements can exist between panels
+
+## Best For
+
+Ohmsha-style tutorials, mobile reading, step-by-step guides
+
+## Best Style Pairings
+
+ohmsha, vibrant
diff --git a/skills/creative/baoyu-comic/references/ohmsha-guide.md b/skills/creative/baoyu-comic/references/ohmsha-guide.md
@@ -0,0 +1,85 @@
+# Ohmsha Manga Guide Style
+
+Guidelines for educational manga comics using the `ohmsha` preset.
+
+## Character Setup
+
+| Role | Default | Traits |
+|------|---------|--------|
+| Student (Role A) | 大雄 | Confused, asks basic but crucial questions, represents reader |
+| Mentor (Role B) | 哆啦A梦 | Knowledgeable, patient, uses gadgets as technical metaphors |
+| Antagonist (Role C, optional) | 胖虎 | Represents misunderstanding, or "noise" in the data |
+
+Custom characters: ask the user for role → name mappings (e.g., `Student:小明, Mentor:教授, Antagonist:Bug怪`).
+
+## Character Reference Sheet Style
+
+For Ohmsha style, use manga/anime style with:
+- Exaggerated expressions for educational clarity
+- Simple, distinctive silhouettes
+- Bright, saturated color palettes
+- Chibi/SD (super-deformed) variants for comedic reactions
+
+## Outline Spec Block
+
+Every ohmsha outline must start with:
+
+```markdown
+【漫画规格单】
+- Language: [Same as input content]
+- Style: Ohmsha (Manga Guide), Full Color
+- Layout: Vertical Scrolling Comic (竖版条漫)
+- Characters: [List character names and roles]
+- Character Reference: characters/characters.png
+- Page Limit: ≤20 pages
+```
+
+## Visual Metaphor Rules (Critical)
+
+**NEVER** create "talking heads" panels. Every technical concept must become:
+
+1. **A tangible gadget/prop** - Something characters can hold, use, demonstrate
+2. **An action scene** - Characters doing something that illustrates the concept
+3. **A visual environment** - Stepping into a metaphorical space
+
+### Examples
+
+| Concept | Bad (Talking Heads) | Good (Visual Metaphor) |
+|---------|---------------------|------------------------|
+| Word embeddings | Characters discussing vectors | 哆啦A梦拿出"词向量压缩机"，把书本压缩成彩色小球 |
+| Gradient descent | Explaining math formula | 大雄在山谷地形上滚球，寻找最低点 |
+| Neural network | Diagram on whiteboard | 角色走进由发光节点组成的网络迷宫 |
+
+## Page Title Convention
+
+Avoid AI-style "Title: Subtitle" format. Use narrative descriptions:
+
+- ❌ "Page 3: Introduction to Neural Networks"
+- ✓ "Page 3: 大雄被海量单词淹没，哆啦A梦拿出'词向量压缩机'"
+
+## Ending Requirements
+
+- NO generic endings ("What will you choose?", "Thanks for reading")
+- End with: Technical summary moment OR character achieving a small goal
+- Final panel: Sense of accomplishment, not open-ended question
+
+### Good Endings
+
+- Student successfully applies learned concept
+- Visual callback to opening problem, now solved
+- Mentor gives summary while student demonstrates understanding
+
+### Bad Endings
+
+- "What do you think?" open questions
+- "Thanks for reading this tutorial"
+- Cliffhanger without resolution
+
+## Layout Preference
+
+Ohmsha style typically uses:
+- `webtoon` (vertical scrolling) - Primary choice
+- `dense` - For information-heavy sections
+- `mixed` - For varied pacing
+
+Avoid `cinematic` and `splash` for educational content.
diff --git a/skills/creative/baoyu-comic/references/partial-workflows.md b/skills/creative/baoyu-comic/references/partial-workflows.md
@@ -0,0 +1,106 @@
+# Partial Workflows
+
+Options to run specific parts of the workflow. Trigger these via natural language (e.g., "just the storyboard", "regenerate page 3").
+
+## Options Summary
+
+| Option | Steps Executed | Output |
+|--------|----------------|--------|
+| Storyboard only | 1-3 | `storyboard.md` + `characters/` |
+| Prompts only | 1-5 | + `prompts/*.md` |
+| Images only | 7-8 | + images |
+| Regenerate N | 7 (partial) | Specific page(s) |
+
+---
+
+## Storyboard-only
+
+Generate storyboard and characters without prompts or images.
+
+**User cue**: "storyboard only", "just the outline", "don't generate images yet".
+
+**Workflow**: Steps 1-3 only (stop after storyboard + characters)
+
+**Output**:
+- `analysis.md`
+- `storyboard.md`
+- `characters/characters.md`
+
+**Use case**: Review and edit the storyboard before generating images. Useful for:
+- Getting feedback on the narrative structure
+- Making manual adjustments to panel layouts
+- Defining custom characters
+
+---
+
+## Prompts-only
+
+Generate storyboard, characters, and prompts without images.
+
+**User cue**: "prompts only", "write the prompts but don't generate yet".
+
+**Workflow**: Steps 1-5 (generate prompts, skip images)
+
+**Output**:
+- `analysis.md`
+- `storyboard.md`
+- `characters/characters.md`
+- `prompts/*.md`
+
+**Use case**: Review and edit prompts before image generation. Useful for:
+- Fine-tuning image generation prompts
+- Ensuring visual consistency before committing to generation
+- Making style adjustments at the prompt level
+
+---
+
+## Images-only
+
+Generate images from existing prompts (starts at Step 7).
+
+**User cue**: "generate images from existing prompts", "run the images now" (pointing at an existing `comic/topic-slug/` directory).
+
+**Workflow**: Skip to Step 7, then 8
+
+**Prerequisites** (must exist in directory):
+- `prompts/` directory with page prompt files
+- `storyboard.md` with style information
+- `characters/characters.md` with character definitions
+
+**Output**:
+- `characters/characters.png` (if not exists)
+- `NN-{cover|page}-[slug].png` images
+
+**Use case**: Re-generate images after editing prompts. Useful for:
+- Recovering from failed image generation
+- Trying different image generation settings
+- Regenerating after manual prompt edits
+
+---
+
+## Regenerate
+
+Regenerate specific pages only.
+
+**User cue**: "regenerate page 3", "redo pages 2, 5, 8", "regenerate the cover".
+
+**Workflow**:
+1. Read existing prompts for specified pages
+2. Regenerate images only for those pages via `image_generate`
+3. Download each returned URL and overwrite the existing PNG
+
+**Prerequisites** (must exist):
+- `prompts/NN-{cover|page}-[slug].md` for specified pages
+- `characters/characters.md` (for agent-side consistency checks, if it was used originally)
+
+**Output**:
+- Regenerated `NN-{cover|page}-[slug].png` for specified pages
+
+**Use case**: Fix specific pages without regenerating entire comic. Useful for:
+- Fixing a single problematic page
+- Iterating on specific visuals
+- Regenerating pages after prompt edits
+
+**Page numbering**:
+- `0` = Cover page
+- `1-N` = Content pages
diff --git a/skills/creative/baoyu-comic/references/presets/concept-story.md b/skills/creative/baoyu-comic/references/presets/concept-story.md
@@ -0,0 +1,121 @@
+# concept-story
+
+概念故事预设 - Narrative comics that visualize abstract concepts through character-driven stories
+
+## Base Configuration
+
+| Dimension | Value |
+|-----------|-------|
+| Art Style | manga |
+| Tone | warm |
+| Layout | standard (default) |
+
+Equivalent to: art=manga, tone=warm
+
+## Unique Rules
+
+This preset includes special rules beyond the art+tone combination. When the `concept-story` preset is selected, ALL rules below must be applied.
+
+### Concept Visualization System (CRITICAL)
+
+Each major abstract concept SHOULD have a recurring visual symbol/metaphor:
+
+| Concept Type | Visualization Approach |
+|-------------|----------------------|
+| Psychological need | Tangible object character holds or discovers (e.g., glowing energy ball = competence) |
+| Management principle | Environmental metaphor character navigates (e.g., ship wheel = autonomy) |
+| Growth/development | Living organic symbol that transforms (e.g., seed → flowering plant = relatedness) |
+| Abstract framework | Spatial structure characters can enter or observe |
+| Emotional state | Color/lighting shift in the scene atmosphere |
+
+**Unlike ohmsha**: Dialogue panels are allowed and expected. The goal is to COMBINE visual metaphors WITH dialogue, not replace dialogue entirely.
+
+**Pattern**: "Dialogue introduces idea" → "Visual metaphor illustrates it" → "Character reacts/applies it"
+
+### Visual Symbol Continuity
+
+Symbols must persist across the story:
+
+| Stage | Treatment |
+|-------|-----------|
+| Introduction | Symbol appears with soft glow effect when concept is first mentioned |
+| Recurrence | Same symbol reappears in background or character interaction when concept is referenced |
+| Resolution | ALL symbols gather in the final composition, showing integration of learned concepts |
+
+**Storyboard requirement**: Include a Symbol Mapping Table defining concept → visual symbol before panel breakdown.
+
+### Character Archetypes (Flexible)
+
+Create original characters based on content domain. No fixed defaults:
+
+| Role | Archetype | Visual Cues |
+|------|-----------|------------|
+| Protagonist | Learner/worker facing a challenge | Modern professional or student, relatable, starts with constrained posture |
+| Mentor | Experienced guide who teaches through experience | Slightly older, calm demeanor, warm color accents |
+| Catalyst | Person or event that triggers transformation | Can be a colleague, situation, challenge, or opportunity |
+
+**IMPORTANT**: Characters are created fresh each time based on the source content's domain (business, psychology, education, etc.). No default character set.
+
+### Narrative Arc Structure
+
+Enforce a five-stage growth arc:
+
+| Act | Structure | Visual Tone |
+|-----|-----------|------------|
+| Opening | Protagonist stuck in routine, faces frustration | Muted warm tones, tight framing, constrained compositions |
+| Inciting moment | Mentor appears or opportunity arrives | Brightness increases, panels open up |
+| Learning | Concepts introduced through visual metaphors | Rich warm palette, symbols introduced one by one |
+| Turning point | Protagonist applies knowledge, faces test | Contrast increases, dynamic compositions |
+| Transformation | Growth demonstrated, new understanding visible | Full warm palette, expansive composition, all symbols present |
+
+### Dialogue + Action Balance
+
+- Dialogue is encouraged and expected (unlike ohmsha's NO talking heads rule)
+- Every page should combine at least one dialogue panel with at least one visual/action panel
+- Avoid pure "lecture" pages where a character explains for 4+ panels straight
+- When a character explains a concept verbally, the NEXT panel should visualize it
+
+**Wrong approach**: Four consecutive panels of mentor lecturing at protagonist
+**Right approach**: Mentor introduces concept → visual metaphor panel → protagonist reacts → applies understanding
+
+### Scene Atmosphere Rules
+
+| Scene Type | Atmosphere |
+|------------|-----------|
+| Problem/frustration | Cool muted tones over warm base, tight framing, cluttered environment |
+| Mentoring moment | Golden hour lighting, open composition, warm indoor glow |
+| Concept visualization | Soft glow effects, clean simplified backgrounds, symbol spotlight |
+| Growth/transformation | Warm light expanding outward, character posture opening up |
+| Resolution | Full warm palette, spacious composition, all visual symbols visible |
+
+### Ending Requirements
+
+Final page MUST include:
+
+1. Protagonist demonstrating transformed understanding (not just being told)
+2. Visual callback showing contrast with opening state (e.g., wilted plant → thriving plant)
+3. All concept symbols visible together in the composition
+4. A forward-looking element suggesting ongoing growth (not a closed ending)
+
+### Page Title Convention
+
+Every page MUST have a narrative title:
+
+**Wrong**: "Chapter 3: Self-Determination Theory"
+**Right**: "The Day Xiao Ming Found His Own Engine"
+
+## Quality Markers
+
+- ✓ Each major concept has a recurring visual symbol
+- ✓ Dialogue and visual metaphors work together (not one replacing the other)
+- ✓ Clear growth arc from problem to transformation
+- ✓ Original characters suited to the content domain
+- ✓ Warm, professional atmosphere throughout
+- ✓ Visual symbols recur and accumulate through the story
+- ✓ Final page integrates all concept symbols with transformation callback
+
+## Best For
+
+Psychology concepts, business/management principles, motivation theory, personal development,
+self-help content, leadership frameworks, coaching narratives, soft skill education,
+abstract concept explanation through character-driven stories
diff --git a/skills/creative/baoyu-comic/references/presets/four-panel.md b/skills/creative/baoyu-comic/references/presets/four-panel.md
@@ -0,0 +1,107 @@
+# four-panel
+
+四格漫画预设 - Minimalist four-panel business allegory comics
+
+## Base Configuration
+
+| Dimension | Value |
+|-----------|-------|
+| Art Style | minimalist |
+| Tone | neutral |
+| Layout | four-panel (default) |
+| Aspect | 4:3 (landscape) |
+
+Equivalent to: art=minimalist, tone=neutral, layout=four-panel, aspect=4:3
+
+## Unique Rules
+
+This preset includes special rules beyond the art+tone combination. When the `four-panel` preset is selected, ALL rules below must be applied.
+
+### 起承转合 Narrative Structure (CRITICAL)
+
+Every comic MUST follow the four-panel 起承转合 structure:
+
+| Panel | Role | Requirements |
+|-------|------|-------------|
+| 1 (起 Setup) | Introduce the situation | Show character(s) in a recognizable context. Establish the "normal" state or problem |
+| 2 (承 Development) | Build on the setup | Add complication, show an attempt, or introduce the concept. Stakes become clearer |
+| 3 (转 Turn) | The twist or key insight | **Most important panel.** Show the unexpected reversal, contrast, or "aha" moment that makes the allegory work |
+| 4 (合 Conclusion) | Resolution and takeaway | Show the result, consequence, or lesson learned. Can be a visual punchline or summary |
+
+**CRITICAL**: Do NOT deviate from exactly 4 panels. No 5th panel, no title panel, no footer panel within the image.
+
+### Single-Page Story Rule (CRITICAL)
+
+- The entire story is told in ONE page with exactly 4 panels
+- Page count: always 1 (plus optional cover)
+- No multi-page four-panel stories — if content requires more, create multiple separate four-panel comics
+- Storyboard structure: Cover (optional) + 1 page
+
+### Accent Color System
+
+- The image is primarily black-and-white line art
+- Use exactly 1-2 spot colors per strip (default: orange `#FF6B35`)
+- Rules:
+  - Key concept label or object: filled with accent color or outlined in accent
+  - Panel 3 (转 Turn) should have the strongest color emphasis
+  - Characters remain B&W — color is for concepts/objects/labels only
+  - Consistent accent color across all 4 panels (do not switch colors between panels)
+
+### Character Design Rules
+
+- Simplified stick-figure-like characters
+- Distinguish characters through simple props: ties, glasses, hats, briefcases, aprons
+- No detailed faces — dot eyes, line mouth at most
+- Characters should be generic enough to represent archetypes (the manager, the employee, the customer)
+- Maximum 2-3 characters per strip
+
+### Text in Panels
+
+- Chinese text for dialogue and labels (or match source language)
+- Keep text minimal — 1-2 short lines per panel maximum
+- Key concept terms can be highlighted with accent color background
+- No narrator boxes — dialogue and labels only
+- Speech bubbles: simple rectangles or ovals, thin black outline
+
+### Optional Title & Caption
+
+- A brief descriptive title above the 4 panels
+- An optional one-line caption/moral below the panels
+- These are part of the page composition, not separate panels
+
+### Character Archetypes (Flexible)
+
+Create simple stick-figure characters based on content. No fixed defaults:
+
+| Role | Archetype | Visual Cues |
+|------|-----------|------------|
+| Protagonist | Worker/employee facing a situation | Simple figure, minimal distinguishing feature (glasses, tie) |
+| Authority | Boss/manager/expert | Slightly larger figure, or prop like pointer/clipboard |
+| Object | The concept itself | Labeled object, icon, or highlighted text with accent color |
+
+### Prompt Template
+
+When generating image prompts for four-panel comics, include these keywords:
+
+> A minimalist, clean line art digital comic strip in a four-panel grid layout (2×2). The style is simplified cartoon illustration with clear black outlines and a minimal color palette of black, white, and specific spot [accent color] for key concepts.
+
+Each panel description should specify:
+- Panel position (Top Left / Top Right / Bottom Left / Bottom Right)
+- Character poses and gestures (simple, stick-figure style)
+- Dialogue text in Chinese (hand-drawn style)
+- Any accent-colored elements (concept labels, key objects)
+
+## Quality Markers
+
+- ✓ Exactly 4 panels in strict 2×2 grid
+- ✓ 起承转合 narrative arc clearly present
+- ✓ 90%+ black-and-white with strategic spot color
+- ✓ Simplified stick-figure characters
+- ✓ Key concept visually highlighted with accent color
+- ✓ Text is minimal and in Chinese (or source language)
+- ✓ Single complete story in one page
+- ✓ Panel 3 delivers a clear "turn" or insight
+
+## Best For
+
+Business allegory, management fables, short insights, workplace parables, concept contrasts, social media educational content, quick-read comics
diff --git a/skills/creative/baoyu-comic/references/presets/ohmsha.md b/skills/creative/baoyu-comic/references/presets/ohmsha.md
@@ -0,0 +1,114 @@
+# ohmsha
+
+Ohmsha预设 - Educational manga with visual metaphors
+
+## Base Configuration
+
+| Dimension | Value |
+|-----------|-------|
+| Art Style | manga |
+| Tone | neutral |
+| Layout | webtoon (default) |
+
+Equivalent to: art=manga, tone=neutral
+
+## Unique Rules
+
+This preset includes special rules beyond the art+tone combination. When the `ohmsha` preset is selected, ALL rules below must be applied.
+
+### Visual Metaphor Requirements (CRITICAL)
+
+Every technical concept MUST be visualized as a metaphor:
+
+| Concept Type | Visualization Approach |
+|-------------|----------------------|
+| Algorithm | Gadget/machine that demonstrates the process |
+| Data structure | Physical space characters can enter/explore |
+| Mathematical formula | Transformation visible in environment |
+| Abstract process | Tangible flow of particles/objects |
+
+**Wrong approach**: Character points at blackboard explaining
+**Right approach**: Character uses "Concept Visualizer" gadget, steps into metaphorical space
+
+### Visual Metaphor Examples
+
+| Concept | Wrong (Talking Head) | Right (Visual Metaphor) |
+|---------|---------------------|------------------------|
+| Attention mechanism | Character points at formula on blackboard | "Attention Flashlight" gadget illuminates key words in dark room |
+| Gradient descent | "The algorithm minimizes loss" | Character rides ball rolling down mountain valley |
+| Neural network | Diagram with arrows | Living network of glowing creatures passing messages |
+| Overfitting | "The model memorized the data" | Character wearing clothes that fit only one specific pose |
+
+### Character Roles (Required)
+
+**DEFAULT: Use Doraemon characters** unless user explicitly specifies custom characters.
+
+| Role | Default Character | Visual | Traits |
+|------|-------------------|--------|--------|
+| Student (Role A) | 大雄 (Nobita) | Boy, 10yo, round glasses, black hair, yellow shirt, navy shorts | Confused, asks basic but crucial questions, represents reader |
+| Mentor (Role B) | 哆啦A梦 (Doraemon) | Blue robot cat, white belly, 4D pocket, red nose, golden bell | Knowledgeable, patient, uses gadgets as technical metaphors |
+| Challenge (Role C) | 胖虎 (Gian) | Stocky boy, small eyes, orange shirt | Represents misunderstanding, or "noise" in the data |
+| Support (Role D) | 静香 (Shizuka) | Cute girl, black short hair, pink dress | Asks clarifying questions, provides alternative perspectives |
+
+**IMPORTANT**: These Doraemon characters ARE the default for ohmsha preset. Generate character definitions using these exact characters unless user requests otherwise.
+
+To use custom characters: ask the user to provide role → character mappings (e.g., `Student:小明, Mentor:教授`).
+
+### Page Title Convention
+
+Every page MUST have a narrative title (not section header):
+
+**Wrong**: "Chapter 1: Introduction to Transformers"
+**Right**: "The Day Nobita Couldn't Understand Anyone"
+
+### Gadget Reveal Pattern
+
+When introducing a concept:
+
+1. Student expresses confusion with visual indicator (？, spiral eyes)
+2. Mentor dramatically produces gadget with sparkle effects
+3. Gadget name announced in bold with explanation
+4. Demonstration begins - student enters metaphorical space
+
+### Ending Requirements
+
+Final page MUST include:
+
+1. Student demonstrating understanding (applying the concept)
+2. Callback to opening problem (now resolved)
+3. Mentor's satisfied expression
+4. Optional: hint at next topic
+
+### NO Talking Heads Rule
+
+**Critical**: Characters must DO things, not just explain.
+
+Every panel should show:
+- Action being performed
+- Metaphor being demonstrated
+- Character interaction with concept-space
+- NOT: two characters facing each other talking
+
+### Special Visual Elements
+
+| Element | Usage |
+|---------|-------|
+| Gadget reveals | Dramatic unveiling with sparkle effects |
+| Concept spaces | Rounded borders, glowing edges for "imagination mode" |
+| Information displays | Holographic UI style for technical details |
+| Aha moments | Radial lines, light burst effects |
+| Confusion | Spiral eyes, question marks floating above head |
+
+## Quality Markers
+
+- ✓ Every concept is a visual metaphor
+- ✓ Characters are DOING things, not just talking
+- ✓ Clear student/mentor dynamic
+- ✓ Gadgets and props drive the explanation
+- ✓ Expressive manga-style emotions
+- ✓ Information density through visual design, not text walls
+- ✓ Narrative page titles
+
+## Reference
+
+For complete guidelines, see `references/ohmsha-guide.md`
diff --git a/skills/creative/baoyu-comic/references/presets/shoujo.md b/skills/creative/baoyu-comic/references/presets/shoujo.md
@@ -0,0 +1,116 @@
+# shoujo
+
+少女预设 - Classic shoujo manga with romantic aesthetics
+
+## Base Configuration
+
+| Dimension | Value |
+|-----------|-------|
+| Art Style | manga |
+| Tone | romantic |
+| Layout | standard (default) |
+
+Equivalent to: art=manga, tone=romantic
+
+## Unique Rules
+
+This preset includes special rules beyond the art+tone combination. When the `shoujo` preset is selected, ALL rules below must be applied.
+
+### Decorative Elements (Required)
+
+Every emotional moment must include decorative elements:
+
+| Emotion | Required Decorations |
+|---------|---------------------|
+| Love | Floating hearts, sparkles, rose petals |
+| Longing | Feathers, bubbles, distant sparkles |
+| Joy | Flowers blooming, light bursts, stars |
+| Sadness | Falling petals, fading sparkles |
+| Shyness | Soft sparkles, floating bubbles |
+| Realization | Radiating lines with sparkles |
+
+### Eye Detail Requirements
+
+Eyes are critical in shoujo style:
+
+| Aspect | Treatment |
+|--------|-----------|
+| Size | Larger than standard manga (1.2x) |
+| Highlights | Multiple (3-5), placed for emotion |
+| Reflection | Scene reflection in emotional moments |
+| Sparkle | Built-in sparkle effects |
+| Tears | Crystalline, detailed teardrops |
+
+### Character Beauty Standards
+
+| Feature | Treatment |
+|---------|-----------|
+| Hair | Flowing, detailed strands, shine highlights |
+| Skin | Porcelain, soft blush on cheeks |
+| Lips | Soft, slightly glossy |
+| Hands | Elegant, expressive gestures |
+| Posture | Graceful, elegant poses |
+
+### Background Effects
+
+**Abstract backgrounds** for emotional moments:
+
+| Moment Type | Background |
+|-------------|-----------|
+| Love confession | Soft gradient + floating flowers |
+| Shock | Screen tone speed lines + sparkles |
+| Memory | Dreamy blur + scattered petals |
+| Realization | Radial lines + light burst |
+| Intimate | Soft focus + floating elements |
+
+### Panel Flow
+
+- Overlap panels for intimate moments
+- Break panel borders for emotional impact
+- Float decorative elements between panels
+- Use screen tone gradients for mood
+- Irregular panel shapes for drama
+
+### Emotional Beat Timing
+
+Slow down pacing for emotional impact:
+
+| Scene Type | Panel Treatment |
+|------------|-----------------|
+| Confession | Multiple small panels, then splash |
+| Eye contact | Close-up sequence |
+| Touch | Slow-motion panel breakdown |
+| Realization | Build-up panels then impact |
+
+### Color Palette Application
+
+| Scene Type | Palette |
+|------------|---------|
+| Romantic | Pink, lavender, rose gold |
+| Happy | Soft yellow, peach, sky blue |
+| Sad | Pale blue, silver, gray lavender |
+| Dramatic | Deep rose, purple, contrast |
+
+### Screen Tone Usage
+
+| Mood | Tone Pattern |
+|------|-------------|
+| Neutral | Clean, minimal |
+| Romantic | Soft gradient overlays |
+| Dramatic | Heavy contrast tones |
+| Dreamy | Soft dot patterns |
+
+## Quality Markers
+
+- ✓ Large, sparkling detailed eyes
+- ✓ Decorative elements in emotional moments
+- ✓ Flowing, beautiful character designs
+- ✓ Soft, pastel color palette
+- ✓ Elegant panel compositions
+- ✓ Screen tone mood effects
+- ✓ Romantic atmosphere throughout
+- ✓ Beautiful, expressive poses
+
+## Best For
+
+Romance stories, coming-of-age, friendship narratives, school life, emotional drama, love stories
diff --git a/skills/creative/baoyu-comic/references/presets/wuxia.md b/skills/creative/baoyu-comic/references/presets/wuxia.md
@@ -0,0 +1,110 @@
+# wuxia
+
+武侠预设 - Hong Kong martial arts comic style
+
+## Base Configuration
+
+| Dimension | Value |
+|-----------|-------|
+| Art Style | ink-brush |
+| Tone | action |
+| Layout | splash (default) |
+
+Equivalent to: art=ink-brush, tone=action
+
+## Unique Rules
+
+This preset includes special rules beyond the art+tone combination. When the `wuxia` preset is selected, ALL rules below must be applied.
+
+### Qi/Energy Effects (Required)
+
+Martial arts power must be visible through qi effects:
+
+| Effect Type | Visual Treatment |
+|-------------|-----------------|
+| Internal qi | Glowing aura around character |
+| External qi | Visible energy projection |
+| Qi clash | Radiating impact waves |
+| Qi absorption | Flowing particles toward character |
+| Hidden power | Subtle glow in eyes/fists |
+
+### Energy Colors
+
+| Qi Type | Color |
+|---------|-------|
+| Righteous | Blue (#4299E1), Gold (#FFD700) |
+| Fierce | Red (#DC2626), Orange (#EA580C) |
+| Evil | Purple (#7C3AED), Green (#16A34A) |
+| Pure | White, Silver |
+| Ancient | Gold with particles |
+
+### Combat Visual Language
+
+**Impact moments** must include:
+
+1. Speed lines radiating from impact point
+2. Flying debris (stone, wood, cloth)
+3. Shockwave rings
+4. Dust/energy clouds
+5. Hair and clothing blown back
+
+### Movement Depiction
+
+| Speed Level | Visual Treatment |
+|-------------|-----------------|
+| Normal | Standard pose |
+| Fast | Motion blur, speed lines |
+| Lightning | Afterimages, multiple positions |
+| Teleport | Fade effect, particle trail |
+
+### Environmental Integration
+
+Backgrounds must support action:
+
+| Environment | Combat Enhancement |
+|-------------|-------------------|
+| Mountains | Crumbling peaks from impacts |
+| Forest | Exploding trees, flying leaves |
+| Water | Dramatic splashes, walking on water |
+| Temple | Breaking pillars, flying tiles |
+| Cliff | Dramatic falls, wind effects |
+
+### Character Pose Guidelines
+
+- Dynamic warrior stances with weight distribution
+- Flowing robes and hair showing movement
+- Muscle tension visible in action
+- Feet planted or in dynamic motion
+- Traditional martial arts postures
+
+### Weapon Effects
+
+| Weapon | Visual Treatment |
+|--------|-----------------|
+| Sword | Trailing light arc, blade glow |
+| Palm | Qi projection, wind effect |
+| Staff | Spinning blur, impact ripples |
+| Whip | Flowing energy trail |
+
+### Atmospheric Elements
+
+Always include:
+- Floating particles (leaves, petals, dust)
+- Ink wash mist for depth
+- Wind direction indicators
+- Dramatic sky/weather when appropriate
+
+## Quality Markers
+
+- ✓ Dynamic action poses with sense of motion
+- ✓ Ink brush aesthetic in line work
+- ✓ Visible qi/energy effects
+- ✓ High contrast dramatic lighting
+- ✓ Atmospheric backgrounds with Chinese elements
+- ✓ Flowing fabric and hair movement
+- ✓ Impactful combat moments
+- ✓ Speed lines and impact effects
+
+## Best For
+
+Martial arts stories, Chinese historical fiction, wuxia/xianxia adaptations, action-heavy narratives
diff --git a/skills/creative/baoyu-comic/references/storyboard-template.md b/skills/creative/baoyu-comic/references/storyboard-template.md
@@ -0,0 +1,143 @@
+# Storyboard Template
+
+## Storyboard Document Format
+
+```markdown
+---
+title: "[Comic Title]"
+topic: "[topic description]"
+time_span: "[e.g., 1912-1954]"
+narrative_approach: "[chronological/thematic/character-focused]"
+recommended_style: "[style name]"
+recommended_layout: "[layout name or varies]"
+aspect_ratio: "3:4"    # 3:4 (portrait), 4:3 (landscape), 16:9 (widescreen)
+language: "[zh/en/ja/etc.]"
+page_count: [N]
+generated: "YYYY-MM-DD HH:mm"
+---
+
+# [Comic Title] - Knowledge Comic Storyboard
+
+**Character Reference**: characters/characters.png
+
+---
+
+## Cover
+
+**Filename**: 00-cover-[slug].png
+**Core Message**: [one-liner]
+
+**Visual Design**:
+- Title typography style
+- Main visual composition
+- Color scheme
+- Subtitle / time span notation
+
+**Visual Prompt**:
+[Detailed image generation prompt]
+
+---
+
+## Page 1 / N
+
+**Filename**: 01-page-[slug].png
+**Layout**: [standard/cinematic/dense/splash/mixed]
+**Narrative Layer**: [Main narrative / Narrator layer / Mixed]
+**Core Message**: [What this page conveys]
+
+### Panel Layout
+
+**Panel Count**: X
+**Layout Type**: [grid/irregular/splash]
+
+#### Panel 1 (Size: 1/3 page, Position: Top)
+
+**Scene**: [Time, location]
+**Image Description**:
+- Camera angle: [bird's eye / low angle / eye level / close-up / wide shot]
+- Characters: [pose, expression, action]
+- Environment: [scene details, period markers]
+- Lighting: [atmosphere description]
+- Color tone: [palette reference]
+
+**Text Elements**:
+- Dialogue bubble (oval): "Character line"
+- Narrator box (rectangular): 「Narrator commentary」
+- Caption bar: [Background info text]
+
+#### Panel 2...
+
+**Page Hook**: [Cliffhanger or transition at page end]
+
+**Visual Prompt**:
+[Full page image generation prompt]
+
+---
+
+## Page 2 / N
+...
+```
+
+## Cover Design Principles
+
+- Academic gravitas with visual appeal
+- Title typography reflecting knowledge/science theme
+- Composition hinting at core theme (character silhouette, iconic symbol, concept diagram)
+- Subtitle or time span for epic scope
+
+## Panel Composition Guidelines
+
+| Panel Type | Recommended Count | Usage |
+|-----------|-------------------|-------|
+| Main narrative | 3-5 per page | Story progression |
+| Concept diagram | 1-2 per page | Visualize abstractions |
+| Narrator panel | 0-1 per page | Commentary, transition |
+| Splash (full/half) | Occasional | Major moments |
+
+## Panel Size Reference
+
+- **Full page (Splash)**: Major moments, key breakthroughs
+- **Half page**: Important scenes, turning points
+- **1/3 page**: Standard narrative panels
+- **1/4 or smaller**: Quick progression, sequential action
+
+## Concept Visualization Techniques
+
+Transform abstract concepts into concrete visuals:
+
+| Abstract Concept | Visual Approach |
+|-----------------|-----------------|
+| Neural network | Glowing nodes with connecting lines |
+| Gradient descent | Ball rolling down valley terrain |
+| Data flow | Luminous particles flowing through pipes |
+| Algorithm iteration | Ascending spiral staircase |
+| Breakthrough moment | Shattering barrier, piercing light |
+| Logical proof | Building blocks assembling |
+| Uncertainty | Forking paths, fog, multiple shadows |
+
+## Text Element Design
+
+| Text Type | Style | Usage |
+|-----------|-------|-------|
+| Character dialogue | Oval speech bubble | Main narrative speech |
+| Narrator commentary | Rectangular box | Explanation, commentary |
+| Caption bar | Edge-mounted rectangle | Time, location info |
+| Thought bubble | Cloud shape | Character inner monologue |
+| Term label | Bold / special color | First appearance of technical terms |
+
+## Prompt Structure for Consistency
+
+Each page prompt should include character reference:
+
+```
+[CHARACTER REFERENCE]
+(Key details from characters.md for characters in this page)
+
+[PAGE CONTENT]
+(Specific scene, panel layout, and visual elements)
+
+[CONSISTENCY REMINDER]
+Maintain exact character appearances as defined in character reference.
+- [Character A]: [key identifying features]
+- [Character B]: [key identifying features]
+```
diff --git a/skills/creative/baoyu-comic/references/tones/action.md b/skills/creative/baoyu-comic/references/tones/action.md
@@ -0,0 +1,110 @@
+# action
+
+动作基调 - Speed, impact, power
+
+## Overview
+
+High-impact action atmosphere with dynamic movement, combat effects, and powerful visual energy. Creates visceral, exciting sequences.
+
+## Mood Characteristics
+
+- Speed and motion
+- Power and impact
+- Combat intensity
+- Physical energy
+- Visceral excitement
+
+## Color Modifiers
+
+When applied to any art style:
+
+| Adjustment | Direction |
+|------------|-----------|
+| Saturation | High contrast |
+| Contrast | Maximum |
+| Temperature | Variable per effect |
+| Brightness | Dynamic range |
+
+## Action Effects
+
+**Combat/motion effects** (apply liberally):
+
+| Effect | Usage |
+|--------|-------|
+| Speed lines | Motion, velocity |
+| Impact bursts | Hits, collisions |
+| Shockwaves | Powerful impacts |
+| Flying debris | Environmental destruction |
+| Dust clouds | Ground impacts |
+| Motion blur | Fast movement |
+| Afterimages | Super speed |
+
+## Special Effects
+
+| Effect Type | Visual Approach |
+|------------|-----------------|
+| Energy attacks | Glowing, radiating |
+| Physical impacts | Radiating lines, debris |
+| Movement | Speed lines, blur |
+| Atmosphere | Flying particles, wind |
+
+## Effect Colors
+
+| Effect | Color | Hex |
+|--------|-------|-----|
+| Energy glow | Blue | #4299E1 |
+| Fire/power | Gold | #FFD700 |
+| Impact | White burst | #FFFFFF |
+| Blood/intensity | Deep red | #8B0000 |
+
+## Lighting
+
+- Dynamic, shifting
+- Impact flashes
+- Energy glow sources
+- Rim lighting on figures
+- Dramatic contrast
+
+## Emotional Range
+
+| Emotion | Expression |
+|---------|-----------|
+| Determination | Fierce focus |
+| Rage | Intense, powerful |
+| Triumph | Victorious pose |
+| Struggle | Strained effort |
+
+## Composition
+
+- Dynamic angles
+- Extreme perspectives
+- Panel-breaking layouts
+- Asymmetric designs
+- Impact-focused framing
+
+## Pose Guidelines
+
+- Dynamic warrior poses
+- Weight and momentum visible
+- Muscle tension shown
+- Flow of movement captured
+- Impact points emphasized
+
+## Best For
+
+- Martial arts combat
+- Action sequences
+- Sports moments
+- Physical challenges
+- Battle scenes
+- Climactic confrontations
+
+## Combination Notes
+
+Works especially well with:
+- ink-brush: wuxia combat
+- manga: shonen battles
+
+Avoid with:
+- chalk: style mismatch
+- ligne-claire: style mismatch (too static)
diff --git a/skills/creative/baoyu-comic/references/tones/dramatic.md b/skills/creative/baoyu-comic/references/tones/dramatic.md
@@ -0,0 +1,95 @@
+# dramatic
+
+戏剧基调 - High contrast, intense, powerful moments
+
+## Overview
+
+High-impact dramatic tone for pivotal moments, conflicts, and breakthroughs. Uses strong contrast and intense compositions to create emotional power.
+
+## Mood Characteristics
+
+- Tension and intensity
+- Pivotal moments
+- Conflict and resolution
+- Breakthrough discoveries
+- Emotional climaxes
+
+## Color Modifiers
+
+When applied to any art style:
+
+| Adjustment | Direction |
+|------------|-----------|
+| Saturation | High (vibrant or deep) |
+| Contrast | Maximum |
+| Temperature | Varies for effect |
+| Brightness | Strong highlights, deep shadows |
+
+## Contrast Approach
+
+- Sharp light/dark divisions
+- Minimal mid-tones
+- Stark compositions
+- Silhouette potential
+- Rim lighting effects
+
+## Accent Colors
+
+- Deep navy (#1A365D)
+- Crimson (#9B2C2C)
+- Stark white
+- Heavy blacks
+- Limited palette per scene
+
+## Lighting
+
+- Dramatic single-source
+- High contrast shadows
+- Rim lighting on characters
+- Spotlight effects
+- Chiaroscuro influence
+
+## Emotional Range
+
+| Emotion | Expression |
+|---------|-----------|
+| Anger | Intense, defined features |
+| Determination | Strong, focused gaze |
+| Shock | Wide eyes, stark lighting |
+| Triumph | Powerful, elevated pose |
+
+## Composition
+
+- Angular, dynamic layouts
+- Dramatic camera angles
+- Low/high viewpoints
+- Diagonal compositions
+- Negative space for impact
+
+## Visual Elements
+
+- Speed lines for tension
+- Impact effects
+- Dramatic backgrounds (storms, fire)
+- Silhouettes
+- Light burst effects
+- Environmental drama
+
+## Best For
+
+- Pivotal discoveries
+- Conflict scenes
+- Climactic moments
+- Breakthrough realizations
+- Emotional confrontations
+- Historical turning points
+
+## Combination Notes
+
+Works especially well with:
+- realistic: powerful drama
+- ink-brush: martial arts climax
+- ligne-claire: historical pivots
+- manga: shonen battles
+
+Avoid with: chalk (style mismatch)
diff --git a/skills/creative/baoyu-comic/references/tones/energetic.md b/skills/creative/baoyu-comic/references/tones/energetic.md
@@ -0,0 +1,105 @@
+# energetic
+
+活力基调 - Bright, dynamic, exciting
+
+## Overview
+
+High-energy atmosphere for exciting, discovery-filled content. Bright colors, dynamic compositions, and movement create engaging visuals for younger audiences.
+
+## Mood Characteristics
+
+- Excitement and wonder
+- Discovery and learning
+- Energy and enthusiasm
+- Movement and action
+- Youthful spirit
+
+## Color Modifiers
+
+When applied to any art style:
+
+| Adjustment | Direction |
+|------------|-----------|
+| Saturation | High (vibrant) |
+| Contrast | Medium-high |
+| Temperature | Variable, punchy |
+| Brightness | Bright, clean |
+
+## Color Palette
+
+Shift toward vibrant tones:
+
+| Role | Color | Hex |
+|------|-------|-----|
+| Primary Red | Bright red | #F56565 |
+| Primary Yellow | Sunny yellow | #F6E05E |
+| Primary Blue | Sky blue | #63B3ED |
+| Accent 1 | Magenta | #D53F8C |
+| Accent 2 | Lime green | #68D391 |
+| Background | Clean white | #FFFFFF |
+| Background Alt | Bright pastels | Various |
+
+## Lighting
+
+- Bright, clear lighting
+- Clean shadows
+- High energy
+- Spotlight effects for emphasis
+- Dynamic light sources
+
+## Dynamic Elements
+
+**Energy effects** (add to compositions):
+
+| Element | Usage |
+|---------|-------|
+| Speed lines | Motion, excitement |
+| Sparkles | Discoveries |
+| Burst effects | Aha moments |
+| Motion blur | Fast action |
+| Star bursts | Emphasis |
+| Sweat drops | Effort/surprise |
+
+## Emotional Range
+
+| Emotion | Expression |
+|---------|-----------|
+| Excitement | Wide eyes, big smile |
+| Surprise | Dramatic reaction |
+| Determination | Intense focus |
+| Wonder | Sparkling eyes |
+
+## Composition
+
+- Dynamic angles
+- Action-oriented layouts
+- Movement emphasis
+- Clean, punchy designs
+- Energy flows
+
+## Visual Style
+
+- Expressive, animated characters
+- Wide eyes, big reactions
+- Dynamic poses
+- Motion and action focus
+- Simplified backgrounds for energy
+
+## Best For
+
+- Science explanations
+- "Aha" moments
+- Young audience content
+- Discovery narratives
+- Learning adventures
+- Action tutorials
+
+## Combination Notes
+
+Works especially well with:
+- manga: shonen energy
+- chalk: fun education
+
+Avoid with:
+- realistic: style mismatch
+- ink-brush: style mismatch
diff --git a/skills/creative/baoyu-comic/references/tones/neutral.md b/skills/creative/baoyu-comic/references/tones/neutral.md
@@ -0,0 +1,63 @@
+# neutral
+
+中性基调 - Balanced, rational, educational
+
+## Overview
+
+Default balanced tone suitable for educational and informative content. Neither overly emotional nor cold - creates accessible, professional atmosphere.
+
+## Mood Characteristics
+
+- Balanced emotional register
+- Clear, rational presentation
+- Educational focus
+- Professional but approachable
+- Objective storytelling
+
+## Color Modifiers
+
+When applied to any art style:
+
+| Adjustment | Direction |
+|------------|-----------|
+| Saturation | Standard (no shift) |
+| Contrast | Balanced |
+| Temperature | Neutral |
+| Brightness | Slightly bright |
+
+## Lighting
+
+- Even, clear lighting
+- Minimal dramatic shadows
+- Consistent across panels
+- Natural light sources
+- No extreme contrast
+
+## Emotional Range
+
+| Emotion | Expression Level |
+|---------|-----------------|
+| Joy | Moderate smile |
+| Concern | Thoughtful expression |
+| Surprise | Mild widening of eyes |
+| Frustration | Slight frown |
+
+## Composition
+
+- Balanced panel layouts
+- Clear focal points
+- Readable hierarchies
+- Standard framing
+- Functional compositions
+
+## Best For
+
+- Educational content
+- Technical tutorials
+- Informative biographies
+- Documentary style
+- Professional topics
+
+## Usage Notes
+
+Neutral is the default tone. Combine with any art style for baseline professional output. Most versatile tone option.
diff --git a/skills/creative/baoyu-comic/references/tones/romantic.md b/skills/creative/baoyu-comic/references/tones/romantic.md
@@ -0,0 +1,100 @@
+# romantic
+
+浪漫基调 - Soft, beautiful, emotionally delicate
+
+## Overview
+
+Soft, dreamy atmosphere for romantic and emotionally delicate content. Features decorative elements, sparkles, and beautiful compositions that emphasize feeling and beauty.
+
+## Mood Characteristics
+
+- Romance and love
+- Beauty and elegance
+- Emotional delicacy
+- Dreams and hopes
+- Youth and idealism
+
+## Color Modifiers
+
+When applied to any art style:
+
+| Adjustment | Direction |
+|------------|-----------|
+| Saturation | Soft pastels |
+| Contrast | Low, gentle |
+| Temperature | Slightly warm pink |
+| Brightness | Soft, glowing |
+
+## Color Palette
+
+Shift toward romantic tones:
+
+| Role | Color | Hex |
+|------|-------|-----|
+| Primary | Soft pink | #FFB6C1 |
+| Secondary | Lavender | #E6E6FA |
+| Accent | Rose | #FF69B4 |
+| Highlight | Pearl white | #FFFAF0 |
+| Gold | Gold sparkle | #FFD700 |
+| Skin | Porcelain | #FFF5EE |
+| Blush | Soft blush | #FFE4E1 |
+| Background | Soft cream | #FFF8DC |
+
+## Lighting
+
+- Soft, diffused light
+- Glowing effects
+- Backlighting halos
+- Sparkle highlights
+- Dreamy atmospheres
+
+## Decorative Elements
+
+**Essential decorations** (add to compositions):
+
+| Element | Usage |
+|---------|-------|
+| Flower petals | Floating, framing |
+| Sparkles | Emotional highlights |
+| Bubbles | Dreamy moments |
+| Feathers | Gentle floating |
+| Stars | Night scenes, wonder |
+| Hearts | Love emphasis |
+| Light halos | Character highlights |
+
+## Emotional Range
+
+| Emotion | Expression |
+|---------|-----------|
+| Love | Soft gaze, blush |
+| Longing | Distant, beautiful sadness |
+| Joy | Radiant smile, sparkles |
+| Shyness | Downcast eyes, blush |
+
+## Composition
+
+- Elegant, flowing layouts
+- Soft focus backgrounds
+- Characters framed by decorations
+- Beautiful angles (3/4 profiles)
+- Screen tone gradients
+
+## Best For
+
+- Romance stories
+- Coming-of-age
+- Friendship narratives
+- Emotional drama
+- School life
+- Beautiful moments
+
+## Combination Notes
+
+Works especially well with:
+- manga: classic shoujo style
+
+Avoid with:
+- realistic: style mismatch
+- ink-brush: style mismatch
+- ligne-claire: style mismatch
+- chalk: style mismatch
diff --git a/skills/creative/baoyu-comic/references/tones/vintage.md b/skills/creative/baoyu-comic/references/tones/vintage.md
@@ -0,0 +1,104 @@
+# vintage
+
+复古基调 - Historical, aged, period authenticity
+
+## Overview
+
+Historical atmosphere with aged paper effects and period-appropriate aesthetics. Creates sense of time, authenticity, and historical distance.
+
+## Mood Characteristics
+
+- Historical authenticity
+- Period distance
+- Archival quality
+- Time and memory
+- Classical elegance
+
+## Color Modifiers
+
+When applied to any art style:
+
+| Adjustment | Direction |
+|------------|-----------|
+| Saturation | Reduced, muted |
+| Contrast | Medium, aged |
+| Temperature | Sepia shift |
+| Brightness | Slightly faded |
+
+## Color Palette
+
+Shift toward aged tones:
+
+| Role | Color | Hex |
+|------|-------|-----|
+| Primary | Sepia brown | #8B7355 |
+| Background | Aged paper | #F5E6D3 |
+| Accent 1 | Faded teal | #6B8E8E |
+| Accent 2 | Muted burgundy | #7B3F3F |
+| Ink | Aged black | #3D3D3D |
+| Yellowed | Paper yellow | #F5DEB3 |
+
+## Visual Effects
+
+**Aging effects** (apply subtly):
+
+| Effect | Application |
+|--------|-------------|
+| Paper aging | Background texture |
+| Faded edges | Vignette effect |
+| Dust specks | Subtle overlay |
+| Yellowing | Color shift |
+| Wear marks | Corner/edge details |
+
+## Period Elements
+
+- Historical typography
+- Period-accurate details
+- Archival presentation
+- Classical compositions
+- Formal framing
+
+## Lighting
+
+- Natural, period-appropriate
+- Oil lamp/candle warmth
+- Soft, diffused light
+- Indoor historical lighting
+- Photographic quality
+
+## Emotional Range
+
+| Emotion | Expression |
+|---------|-----------|
+| Dignity | Formal, composed |
+| Sorrow | Restrained, elegant |
+| Pride | Classical posture |
+| Wisdom | Aged grace |
+
+## Composition
+
+- Classical framing
+- Formal compositions
+- Period-appropriate staging
+- Documentary style
+- Historical accuracy priority
+
+## Best For
+
+- Pre-1950s stories
+- Classical science history
+- Historical biographies
+- Period pieces
+- Documentary comics
+- Archival narratives
+
+## Combination Notes
+
+Works especially well with:
+- realistic: period drama
+- ligne-claire: historical adventure
+- ink-brush: classical Asian stories
+
+Avoid with:
+- manga: style mismatch (too modern)
+- chalk: style mismatch (modern educational)
diff --git a/skills/creative/baoyu-comic/references/tones/warm.md b/skills/creative/baoyu-comic/references/tones/warm.md
@@ -0,0 +1,94 @@
+# warm
+
+温馨基调 - Nostalgic, personal, comforting
+
+## Overview
+
+Warm, inviting atmosphere for personal stories and nostalgic content. Creates emotional connection through cozy aesthetics and comforting visuals.
+
+## Mood Characteristics
+
+- Nostalgic feeling
+- Personal, intimate atmosphere
+- Comforting and healing
+- Memory and reflection
+- Gentle emotional warmth
+
+## Color Modifiers
+
+When applied to any art style:
+
+| Adjustment | Direction |
+|------------|-----------|
+| Saturation | Slightly reduced |
+| Contrast | Softer |
+| Temperature | Warm shift (+15%) |
+| Brightness | Soft, golden |
+
+## Color Temperature
+
+Shift palette toward warm tones:
+
+| Original | Warm Shift |
+|----------|-----------|
+| Cool blue | Soft teal |
+| Pure white | Cream |
+| Gray | Warm gray |
+| Black | Soft charcoal |
+
+## Accent Colors
+
+- Golden yellow (#D69E2E)
+- Soft orange (#DD6B20)
+- Warm brown (#8B6F47)
+- Sunset tones
+
+## Lighting
+
+- Golden hour lighting
+- Soft, diffused light
+- Warm indoor glow
+- Candle/lamp warmth
+- Gentle shadows
+
+## Emotional Range
+
+| Emotion | Expression |
+|---------|-----------|
+| Joy | Genuine warm smile |
+| Sadness | Gentle melancholy |
+| Love | Soft, tender expressions |
+| Memory | Distant, reflective gaze |
+
+## Composition
+
+- Intimate framing
+- Cozy environments
+- Soft focus backgrounds
+- Welcoming spaces
+- Personal moments highlighted
+
+## Visual Elements
+
+- Warm light rays
+- Soft edges
+- Nostalgic props (old photos, keepsakes)
+- Comfort objects (blankets, tea cups)
+- Nature elements (autumn leaves, sunset)
+
+## Best For
+
+- Personal stories
+- Childhood memories
+- Mentorship narratives
+- Family histories
+- Gentle biographies
+- Healing journeys
+
+## Combination Notes
+
+Works especially well with:
+- ligne-claire: nostalgic European comics
+- realistic: touching human stories
+- manga: slice-of-life warmth
+- chalk: nostalgic education
diff --git a/skills/creative/baoyu-comic/references/workflow.md b/skills/creative/baoyu-comic/references/workflow.md
@@ -0,0 +1,399 @@
+# Complete Workflow
+
+Full workflow for generating knowledge comics.
+
+## Progress Checklist
+
+Copy and track progress:
+
+```
+Comic Progress:
+- [ ] Step 1: Setup & Analyze
+  - [ ] 1.1 Analyze content
+  - [ ] 1.2 Check existing ⚠️ REQUIRED
+- [ ] Step 2: Confirmation - Style & options ⚠️ REQUIRED
+- [ ] Step 3: Generate storyboard + characters
+- [ ] Step 4: Review outline (conditional)
+- [ ] Step 5: Generate prompts
+- [ ] Step 6: Review prompts (conditional)
+- [ ] Step 7: Generate images
+  - [ ] 7.1 Character sheet (if needed)
+  - [ ] 7.2 Generate pages
+- [ ] Step 8: Completion report
+```
+
+## Flow Diagram
+
+```
+Input → Analyze → [Check Existing?] → [Confirm: Style + Reviews] → Storyboard → [Review Outline?] → Prompts → [Review Prompts?] → Images → Complete
+```
+
+---
+
+## Step 1: Setup & Analyze
+
+### 1.1 Analyze Content → `analysis.md`
+
+Read source content, save it if needed, and perform deep analysis.
+
+**Actions**:
+1. **Save source content** (if not already a file):
+   - If user provides a file path: use as-is
+   - If user pastes content: save to `source-{slug}.md` in the target directory using `write_file`, where `{slug}` is the kebab-case topic slug used for the output directory
+   - **Backup rule**: If `source-{slug}.md` already exists, rename it to `source-{slug}-backup-YYYYMMDD-HHMMSS.md` before writing
+2. Read source content
+3. **Deep analysis** following `analysis-framework.md`:
+   - Target audience identification
+   - Value proposition for readers
+   - Core themes and narrative potential
+   - Key figures and their story arcs
+4. Detect source language
+5. **Determine language**:
+   - If user specified a language → use it
+   - Else → use detected source language or user's conversation language
+6. Determine recommended page count:
+   - Short story: 5-8 pages
+   - Medium complexity: 9-15 pages
+   - Full biography: 16-25 pages
+7. Analyze content signals for art/tone/layout recommendations
+8. **Save to `analysis.md`** using `write_file`
+
+**analysis.md Format**: YAML front matter (title, topic, time_span, source_language, user_language, aspect_ratio, recommended_page_count, recommended_art, recommended_tone) + sections for Target Audience, Value Proposition, Core Themes, Key Figures & Story Arcs, Content Signals, Recommended Approaches. See `analysis-framework.md` for full template.
+
+### 1.2 Check Existing Content ⚠️ REQUIRED
+
+**MUST execute before proceeding to Step 2.**
+
+Check if the output directory exists (e.g., via `test -d "comic/{topic-slug}"`).
+
+**If directory exists**, use `clarify`:
+
+```
+question: "Existing content found at comic/{topic-slug}. How to proceed?"
+options:
+  - "Regenerate storyboard — Keep images, regenerate storyboard and characters only"
+  - "Regenerate images — Keep storyboard, regenerate images only"
+  - "Backup and regenerate — Backup to {slug}-backup-{timestamp}, then regenerate all"
+  - "Exit — Cancel, keep existing content unchanged"
+```
+
+Save result and handle accordingly:
+- **Regenerate storyboard**: Skip to Step 3, preserve `prompts/` and images
+- **Regenerate images**: Skip to Step 7, use existing prompts
+- **Backup and regenerate**: Move directory, start fresh from Step 2
+- **Exit**: End workflow immediately
+
+---
+
+## Step 2: Confirmation - Style & Options ⚠️
+
+**Purpose**: Select visual style + decide whether to review outline before generation. **Do NOT skip.**
+
+**Display summary first**:
+- Content type + topic identified
+- Key figures extracted
+- Time span detected
+- Recommended page count
+- Language (detected or user-specified)
+- **Recommended style**: [art] + [tone] (based on content signals)
+
+**Use `clarify` one question at a time**, in priority order:
+
+### Question 1: Visual Style
+
+If a preset is recommended (see `auto-selection.md`), show it first:
+
+```
+question: "Which visual style for this comic?"
+options:
+  - "[preset name] preset (Recommended) — [preset description] with special rules"
+  - "[recommended art] + [recommended tone] (Recommended) — Best match for your content"
+  - "ligne-claire + neutral — Classic educational, Logicomix style"
+  - "ohmsha preset — Educational manga with visual metaphors, gadgets, NO talking heads"
+  - "Custom — Specify your own art + tone or preset"
+```
+
+**Preset vs Art+Tone**: Presets include special rules beyond art+tone. `ohmsha` = manga + neutral + visual metaphor rules + character roles + NO talking heads. Plain `manga + neutral` does NOT include these rules.
+
+### Question 2: Narrative Focus
+
+```
+question: "What should the comic emphasize? (Pick the primary focus; mention others in a follow-up if needed)"
+options:
+  - "Biography/life story — Follow a person's journey through key life events"
+  - "Concept explanation — Break down complex ideas visually"
+  - "Historical event — Dramatize important historical moments"
+  - "Tutorial/how-to — Step-by-step educational guide"
+```
+
+### Question 3: Target Audience
+
+```
+question: "Who is the primary reader?"
+options:
+  - "General readers — Broad appeal, accessible content"
+  - "Students/learners — Educational focus, clear explanations"
+  - "Industry professionals — Technical depth, domain knowledge"
+  - "Children/young readers — Simplified language, engaging visuals"
+```
+
+### Question 4: Outline Review
+
+```
+question: "Do you want to review the outline before image generation?"
+options:
+  - "Yes, let me review (Recommended) — Review storyboard and characters before generating images"
+  - "No, generate directly — Skip outline review, start generating immediately"
+```
+
+### Question 5: Prompt Review
+
+```
+question: "Review prompts before generating images?"
+options:
+  - "Yes, review prompts (Recommended) — Review image generation prompts before generating"
+  - "No, skip prompt review — Proceed directly to image generation"
+```
+
+**After responses**:
+1. Update `analysis.md` with user preferences
+2. **Store `skip_outline_review`** flag based on Question 4 response
+3. **Store `skip_prompt_review`** flag based on Question 5 response
+4. → Step 3
+
+---
+
+## Step 3: Generate Storyboard + Characters
+
+Create storyboard and character definitions using the confirmed style from Step 2.
+
+**Loading Style References**:
+- Art style: `art-styles/{art}.md`
+- Tone: `tones/{tone}.md`
+- If preset (ohmsha/wuxia/shoujo/concept-story/four-panel): also load `presets/{preset}.md`
+
+**Generate**:
+
+1. **Storyboard** (`storyboard.md`):
+   - YAML front matter with art_style, tone, layout, aspect_ratio
+   - Cover design
+   - Each page: layout, panel breakdown, visual prompts
+   - **Written in user's preferred language** (from Step 1)
+   - Reference: `storyboard-template.md`
+   - **If using preset**: Load and apply preset rules from `presets/`
+
+2. **Character definitions** (`characters/characters.md`):
+   - Visual specs matching the art style (in user's preferred language)
+   - Include Reference Sheet Prompt for later image generation
+   - Reference: `character-template.md`
+   - **If using ohmsha preset**: Use default Doraemon characters (see below)
+
+**Ohmsha Default Characters** (use these unless user specifies custom characters):
+
+| Role | Character | Visual Description |
+|------|-----------|-------------------|
+| Student | 大雄 (Nobita) | Japanese boy, 10yo, round glasses, black hair parted in middle, yellow shirt, navy shorts |
+| Mentor | 哆啦 A 梦 (Doraemon) | Round blue robot cat, big white eyes, red nose, whiskers, white belly with 4D pocket, golden bell, no ears |
+| Challenge | 胖虎 (Gian) | Stocky boy, rough features, small eyes, orange shirt |
+| Support | 静香 (Shizuka) | Cute girl, black short hair, pink dress, gentle expression |
+
+These are the canonical ohmsha-style characters. Do NOT create custom characters for ohmsha unless explicitly requested.
+
+**After generation**:
+- If `skip_outline_review` is true → Skip Step 4, go directly to Step 5
+- If `skip_outline_review` is false → Continue to Step 4
+
+---
+
+## Step 4: Review Outline (Conditional)
+
+**Skip this step** if user selected "No, generate directly" in Step 2.
+
+**Purpose**: User reviews and confirms storyboard + characters before generation.
+
+**Display**:
+- Page count and structure
+- Art style + Tone combination
+- Page-by-page summary (Cover → P1 → P2...)
+- Character list with brief descriptions
+
+**Use `clarify`**:
+
+```
+question: "Ready to generate images with this outline?"
+options:
+  - "Yes, proceed (Recommended) — Generate character sheet and comic pages"
+  - "Edit storyboard first — I'll modify storyboard.md before continuing"
+  - "Edit characters first — I'll modify characters/characters.md before continuing"
+  - "Edit both — I'll modify both files before continuing"
+```
+
+**After response**:
+1. If user wants to edit → Wait for user to finish editing, then ask again
+2. If user confirms → Continue to Step 5
+
+---
+
+## Step 5: Generate Prompts
+
+Create image generation prompts for all pages.
+
+**Style Reference Loading**:
+- Read `art-styles/{art}.md` for rendering guidelines
+- Read `tones/{tone}.md` for mood/color adjustments
+- If preset: Read `presets/{preset}.md` for special rules
+
+**For each page (cover + pages)**:
+1. Create prompt following art style + tone guidelines
+2. **Embed character descriptions** inline (copy relevant traits from `characters/characters.md`) — `image_generate` is prompt-only, so the prompt text is the sole vehicle for character consistency
+3. Save to `prompts/NN-{cover|page}-[slug].md` using `write_file`
+   - **Backup rule**: If prompt file exists, rename to `prompts/NN-{cover|page}-[slug]-backup-YYYYMMDD-HHMMSS.md`
+
+**Prompt File Format**:
+```markdown
+# Page NN: [Title]
+
+## Visual Style
+Art: [art style] | Tone: [tone] | Layout: [layout type]
+
+## Character Reference (embedded inline — maintain exact traits below)
+- [Character A]: [detailed visual traits from characters/characters.md]
+- [Character B]: [detailed visual traits from characters/characters.md]
+
+## Panel Breakdown
+[From storyboard.md - panel descriptions, actions, dialogue]
+
+## Generation Prompt
+[Combined prompt passed to image_generate]
+```
+
+**After generation**:
+- If `skip_prompt_review` is true → Skip Step 6, go directly to Step 7
+- If `skip_prompt_review` is false → Continue to Step 6
+
+---
+
+## Step 6: Review Prompts (Conditional)
+
+**Skip this step** if user selected "No, skip prompt review" in Step 2.
+
+**Purpose**: User reviews and confirms prompts before image generation.
+
+**Display prompt summary table**:
+
+| Page | Title | Key Elements |
+|------|-------|--------------|
+| Cover | [title] | [main visual] |
+| P1 | [title] | [key elements] |
+| ... | ... | ... |
+
+**Use `clarify`**:
+
+```
+question: "Ready to generate images with these prompts?"
+options:
+  - "Yes, proceed (Recommended) — Generate all comic page images"
+  - "Edit prompts first — I'll modify prompts/*.md before continuing"
+  - "Regenerate prompts — Regenerate all prompts with different approach"
+```
+
+**After response**:
+1. If user wants to edit → Wait for user to finish editing, then ask again
+2. If user wants to regenerate → Go back to Step 5
+3. If user confirms → Continue to Step 7
+
+---
+
+## Step 7: Generate Images
+
+With confirmed prompts from Step 5/6, use the `image_generate` tool. The tool accepts only `prompt` and `aspect_ratio` (`landscape` | `portrait` | `square`) and **returns a URL** — it does not accept reference images and does not write local files. Every invocation must be followed by a download step.
+
+**Aspect ratio mapping** — map the storyboard's `aspect_ratio` to the tool's enum:
+
+| Storyboard ratio | `image_generate` format |
+|------------------|-------------------------|
+| `3:4`, `9:16`, `2:3` | `portrait` |
+| `4:3`, `16:9`, `3:2` | `landscape` |
+| `1:1` | `square` |
+
+**Download procedure** (run after every successful `image_generate` call):
+
+1. Extract the `url` field from the tool result
+2. Fetch it to disk, e.g. `curl -fsSL "<url>" -o comic/{slug}/<target>.png`
+3. Verify the file is non-empty (`test -s <target>.png`); on failure, retry the generation once
+
+### 7.1 Generate Character Reference Sheet (conditional)
+
+Character sheet is recommended for multi-page comics with recurring characters, but **NOT required** for all presets.
+
+**When to generate**:
+
+| Condition | Action |
+|-----------|--------|
+| Multi-page comic with detailed/recurring characters | Generate character sheet (recommended) |
+| Preset with simplified characters (e.g., four-panel minimalist) | Skip — prompt descriptions are sufficient |
+| Single-page comic | Skip unless characters are complex |
+
+**When generating**:
+1. Use Reference Sheet Prompt from `characters/characters.md`
+2. **Backup rule**: If `characters/characters.png` exists, rename to `characters/characters-backup-YYYYMMDD-HHMMSS.png`
+3. Call `image_generate` with `landscape` format
+4. Download the returned URL → save to `characters/characters.png`
+
+**Important**: the downloaded sheet is a **human-facing review artifact** (so the user can visually verify character design) and a reference for later regenerations or manual prompt edits. It does **not** drive Step 7.2 — page prompts were already written in Step 5 from the text descriptions in `characters/characters.md`. `image_generate` cannot accept images as visual input, so the text is the sole cross-page consistency mechanism.
+
+### 7.2 Generate Comic Pages
+
+**Before generating any page**:
+1. Confirm each prompt file exists at `prompts/NN-{cover|page}-[slug].md`
+2. Confirm that each prompt has character descriptions embedded inline (see Step 5). `image_generate` is prompt-only, so the prompt text is the sole consistency mechanism.
+
+**Page Generation Strategy**: every page prompt must embed character descriptions (sourced from `characters/characters.md`) inline. This is done during Step 5, uniformly whether or not the PNG sheet was produced in 7.1 — the PNG is only a review/regeneration aid, never a generation input.
+
+**Example embedded prompt** (`prompts/01-page-xxx.md`):
+
+```markdown
+# Page 01: [Title]
+
+## Character Reference (embedded inline — maintain consistency)
+- 大雄：Japanese boy, round glasses, yellow shirt, navy shorts, worried expression...
+- 哆啦 A 梦：Round blue robot cat, white belly, red nose, golden bell, 4D pocket...
+
+## Page Content
+[Original page prompt body — panels, dialogue, visual metaphors]
+```
+
+**For each page (cover + pages)**:
+1. Read prompt from `prompts/NN-{cover|page}-[slug].md`
+2. **Backup rule**: If image file exists, rename to `NN-{cover|page}-[slug]-backup-YYYYMMDD-HHMMSS.png`
+3. Call `image_generate` with the prompt text and mapped aspect ratio
+4. Download the returned URL → save to `NN-{cover|page}-[slug].png`
+5. Report progress after each generation: "Generated X/N: [page title]"
+
+---
+
+## Step 8: Completion Report
+
+```
+Comic Complete!
+Title: [title] | Art: [art] | Tone: [tone] | Pages: [count] | Aspect: [ratio] | Language: [lang]
+Location: [path]
+✓ source-{slug}.md (if content was pasted)
+✓ analysis.md
+✓ characters.png (if generated)
+✓ 00-cover-[slug].png ... NN-page-[slug].png
+```
+
+---
+
+## Page Modification
+
+| Action | Steps |
+|--------|-------|
+| **Edit** | Update prompt → Regenerate image → Download new PNG |
+| **Add** | Create prompt at position → Generate image → Download PNG → Renumber subsequent (NN+1) → Update storyboard |
+| **Delete** | Remove files → Renumber subsequent (NN-1) → Update storyboard |
+
+**File naming**: `NN-{cover|page}-[slug].png` (e.g., `03-page-enigma-machine.png`)
+- Slugs: kebab-case, unique, derived from content
+- Renumbering: Update NN prefix only, slugs unchanged
PATCH

echo "Gold patch applied."
