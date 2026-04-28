#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ordinary-claude-skills

# Idempotency guard
if grep -qF "Algorithmic expression: Flow fields driven by layered Perlin noise. Thousands of" "algorithmic-art/SKILL.md" && grep -qF "To test/visualize the artifact, use available tools (including other Skills or b" "artifacts-builder/SKILL.md" && grep -qF "description: Applies Anthropic's official brand colors and typography to any sor" "brand-guidelines/SKILL.md" && grep -qF "To create museum or magazine quality work, use the design philosophy as the foun" "canvas-design/SKILL.md" && grep -qF "description: \"Comprehensive document creation, editing, and analysis with suppor" "docx/SKILL.md" && grep -qF "description: A set of resources to help me write all kinds of internal communica" "internal-comms/SKILL.md" && grep -qF "Balance comprehensive API endpoint coverage with specialized workflow tools. Wor" "mcp-builder/SKILL.md" && grep -qF "description: Comprehensive PDF manipulation toolkit for extracting text and tabl" "pdf/SKILL.md" && grep -qF "- **Two-column layout (PREFERRED)**: Use a header spanning the full width, then " "pptx/SKILL.md" && grep -qF "- **Avoid duplication**: Information should live in either SKILL.md or reference" "skill-creator/SKILL.md" && grep -qF "description: Knowledge and utilities for creating animated GIFs optimized for Sl" "slack-gif-creator/SKILL.md" && grep -qF "description: Replace with description of the skill and when Claude should use it" "template-skill/SKILL.md" && grep -qF "To handle cases where none of the existing themes work for an artifact, create a" "theme-factory/SKILL.md" && grep -qF "**Always run scripts with `--help` first** to see usage. DO NOT read the source " "webapp-testing/SKILL.md" && grep -qF "description: \"Comprehensive spreadsheet creation, editing, and analysis with sup" "xlsx/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/algorithmic-art/SKILL.md b/algorithmic-art/SKILL.md
@@ -0,0 +1,405 @@
+---
+name: algorithmic-art
+description: Creating algorithmic art using p5.js with seeded randomness and interactive parameter exploration. Use this when users request creating art using code, generative art, algorithmic art, flow fields, or particle systems. Create original algorithmic art rather than copying existing artists' work to avoid copyright violations.
+license: Complete terms in LICENSE.txt
+---
+
+Algorithmic philosophies are computational aesthetic movements that are then expressed through code. Output .md files (philosophy), .html files (interactive viewer), and .js files (generative algorithms).
+
+This happens in two steps:
+1. Algorithmic Philosophy Creation (.md file)
+2. Express by creating p5.js generative art (.html + .js files)
+
+First, undertake this task:
+
+## ALGORITHMIC PHILOSOPHY CREATION
+
+To begin, create an ALGORITHMIC PHILOSOPHY (not static images or templates) that will be interpreted through:
+- Computational processes, emergent behavior, mathematical beauty
+- Seeded randomness, noise fields, organic systems
+- Particles, flows, fields, forces
+- Parametric variation and controlled chaos
+
+### THE CRITICAL UNDERSTANDING
+- What is received: Some subtle input or instructions by the user to take into account, but use as a foundation; it should not constrain creative freedom.
+- What is created: An algorithmic philosophy/generative aesthetic movement.
+- What happens next: The same version receives the philosophy and EXPRESSES IT IN CODE - creating p5.js sketches that are 90% algorithmic generation, 10% essential parameters.
+
+Consider this approach:
+- Write a manifesto for a generative art movement
+- The next phase involves writing the algorithm that brings it to life
+
+The philosophy must emphasize: Algorithmic expression. Emergent behavior. Computational beauty. Seeded variation.
+
+### HOW TO GENERATE AN ALGORITHMIC PHILOSOPHY
+
+**Name the movement** (1-2 words): "Organic Turbulence" / "Quantum Harmonics" / "Emergent Stillness"
+
+**Articulate the philosophy** (4-6 paragraphs - concise but complete):
+
+To capture the ALGORITHMIC essence, express how this philosophy manifests through:
+- Computational processes and mathematical relationships?
+- Noise functions and randomness patterns?
+- Particle behaviors and field dynamics?
+- Temporal evolution and system states?
+- Parametric variation and emergent complexity?
+
+**CRITICAL GUIDELINES:**
+- **Avoid redundancy**: Each algorithmic aspect should be mentioned once. Avoid repeating concepts about noise theory, particle dynamics, or mathematical principles unless adding new depth.
+- **Emphasize craftsmanship REPEATEDLY**: The philosophy MUST stress multiple times that the final algorithm should appear as though it took countless hours to develop, was refined with care, and comes from someone at the absolute top of their field. This framing is essential - repeat phrases like "meticulously crafted algorithm," "the product of deep computational expertise," "painstaking optimization," "master-level implementation."
+- **Leave creative space**: Be specific about the algorithmic direction, but concise enough that the next Claude has room to make interpretive implementation choices at an extremely high level of craftsmanship.
+
+The philosophy must guide the next version to express ideas ALGORITHMICALLY, not through static images. Beauty lives in the process, not the final frame.
+
+### PHILOSOPHY EXAMPLES
+
+**"Organic Turbulence"**
+Philosophy: Chaos constrained by natural law, order emerging from disorder.
+Algorithmic expression: Flow fields driven by layered Perlin noise. Thousands of particles following vector forces, their trails accumulating into organic density maps. Multiple noise octaves create turbulent regions and calm zones. Color emerges from velocity and density - fast particles burn bright, slow ones fade to shadow. The algorithm runs until equilibrium - a meticulously tuned balance where every parameter was refined through countless iterations by a master of computational aesthetics.
+
+**"Quantum Harmonics"**
+Philosophy: Discrete entities exhibiting wave-like interference patterns.
+Algorithmic expression: Particles initialized on a grid, each carrying a phase value that evolves through sine waves. When particles are near, their phases interfere - constructive interference creates bright nodes, destructive creates voids. Simple harmonic motion generates complex emergent mandalas. The result of painstaking frequency calibration where every ratio was carefully chosen to produce resonant beauty.
+
+**"Recursive Whispers"**
+Philosophy: Self-similarity across scales, infinite depth in finite space.
+Algorithmic expression: Branching structures that subdivide recursively. Each branch slightly randomized but constrained by golden ratios. L-systems or recursive subdivision generate tree-like forms that feel both mathematical and organic. Subtle noise perturbations break perfect symmetry. Line weights diminish with each recursion level. Every branching angle the product of deep mathematical exploration.
+
+**"Field Dynamics"**
+Philosophy: Invisible forces made visible through their effects on matter.
+Algorithmic expression: Vector fields constructed from mathematical functions or noise. Particles born at edges, flowing along field lines, dying when they reach equilibrium or boundaries. Multiple fields can attract, repel, or rotate particles. The visualization shows only the traces - ghost-like evidence of invisible forces. A computational dance meticulously choreographed through force balance.
+
+**"Stochastic Crystallization"**
+Philosophy: Random processes crystallizing into ordered structures.
+Algorithmic expression: Randomized circle packing or Voronoi tessellation. Start with random points, let them evolve through relaxation algorithms. Cells push apart until equilibrium. Color based on cell size, neighbor count, or distance from center. The organic tiling that emerges feels both random and inevitable. Every seed produces unique crystalline beauty - the mark of a master-level generative algorithm.
+
+*These are condensed examples. The actual algorithmic philosophy should be 4-6 substantial paragraphs.*
+
+### ESSENTIAL PRINCIPLES
+- **ALGORITHMIC PHILOSOPHY**: Creating a computational worldview to be expressed through code
+- **PROCESS OVER PRODUCT**: Always emphasize that beauty emerges from the algorithm's execution - each run is unique
+- **PARAMETRIC EXPRESSION**: Ideas communicate through mathematical relationships, forces, behaviors - not static composition
+- **ARTISTIC FREEDOM**: The next Claude interprets the philosophy algorithmically - provide creative implementation room
+- **PURE GENERATIVE ART**: This is about making LIVING ALGORITHMS, not static images with randomness
+- **EXPERT CRAFTSMANSHIP**: Repeatedly emphasize the final algorithm must feel meticulously crafted, refined through countless iterations, the product of deep expertise by someone at the absolute top of their field in computational aesthetics
+
+**The algorithmic philosophy should be 4-6 paragraphs long.** Fill it with poetic computational philosophy that brings together the intended vision. Avoid repeating the same points. Output this algorithmic philosophy as a .md file.
+
+---
+
+## DEDUCING THE CONCEPTUAL SEED
+
+**CRITICAL STEP**: Before implementing the algorithm, identify the subtle conceptual thread from the original request.
+
+**THE ESSENTIAL PRINCIPLE**:
+The concept is a **subtle, niche reference embedded within the algorithm itself** - not always literal, always sophisticated. Someone familiar with the subject should feel it intuitively, while others simply experience a masterful generative composition. The algorithmic philosophy provides the computational language. The deduced concept provides the soul - the quiet conceptual DNA woven invisibly into parameters, behaviors, and emergence patterns.
+
+This is **VERY IMPORTANT**: The reference must be so refined that it enhances the work's depth without announcing itself. Think like a jazz musician quoting another song through algorithmic harmony - only those who know will catch it, but everyone appreciates the generative beauty.
+
+---
+
+## P5.JS IMPLEMENTATION
+
+With the philosophy AND conceptual framework established, express it through code. Pause to gather thoughts before proceeding. Use only the algorithmic philosophy created and the instructions below.
+
+### ⚠️ STEP 0: READ THE TEMPLATE FIRST ⚠️
+
+**CRITICAL: BEFORE writing any HTML:**
+
+1. **Read** `templates/viewer.html` using the Read tool
+2. **Study** the exact structure, styling, and Anthropic branding
+3. **Use that file as the LITERAL STARTING POINT** - not just inspiration
+4. **Keep all FIXED sections exactly as shown** (header, sidebar structure, Anthropic colors/fonts, seed controls, action buttons)
+5. **Replace only the VARIABLE sections** marked in the file's comments (algorithm, parameters, UI controls for parameters)
+
+**Avoid:**
+- ❌ Creating HTML from scratch
+- ❌ Inventing custom styling or color schemes
+- ❌ Using system fonts or dark themes
+- ❌ Changing the sidebar structure
+
+**Follow these practices:**
+- ✅ Copy the template's exact HTML structure
+- ✅ Keep Anthropic branding (Poppins/Lora fonts, light colors, gradient backdrop)
+- ✅ Maintain the sidebar layout (Seed → Parameters → Colors? → Actions)
+- ✅ Replace only the p5.js algorithm and parameter controls
+
+The template is the foundation. Build on it, don't rebuild it.
+
+---
+
+To create gallery-quality computational art that lives and breathes, use the algorithmic philosophy as the foundation.
+
+### TECHNICAL REQUIREMENTS
+
+**Seeded Randomness (Art Blocks Pattern)**:
+```javascript
+// ALWAYS use a seed for reproducibility
+let seed = 12345; // or hash from user input
+randomSeed(seed);
+noiseSeed(seed);
+```
+
+**Parameter Structure - FOLLOW THE PHILOSOPHY**:
+
+To establish parameters that emerge naturally from the algorithmic philosophy, consider: "What qualities of this system can be adjusted?"
+
+```javascript
+let params = {
+  seed: 12345,  // Always include seed for reproducibility
+  // colors
+  // Add parameters that control YOUR algorithm:
+  // - Quantities (how many?)
+  // - Scales (how big? how fast?)
+  // - Probabilities (how likely?)
+  // - Ratios (what proportions?)
+  // - Angles (what direction?)
+  // - Thresholds (when does behavior change?)
+};
+```
+
+**To design effective parameters, focus on the properties the system needs to be tunable rather than thinking in terms of "pattern types".**
+
+**Core Algorithm - EXPRESS THE PHILOSOPHY**:
+
+**CRITICAL**: The algorithmic philosophy should dictate what to build.
+
+To express the philosophy through code, avoid thinking "which pattern should I use?" and instead think "how to express this philosophy through code?"
+
+If the philosophy is about **organic emergence**, consider using:
+- Elements that accumulate or grow over time
+- Random processes constrained by natural rules
+- Feedback loops and interactions
+
+If the philosophy is about **mathematical beauty**, consider using:
+- Geometric relationships and ratios
+- Trigonometric functions and harmonics
+- Precise calculations creating unexpected patterns
+
+If the philosophy is about **controlled chaos**, consider using:
+- Random variation within strict boundaries
+- Bifurcation and phase transitions
+- Order emerging from disorder
+
+**The algorithm flows from the philosophy, not from a menu of options.**
+
+To guide the implementation, let the conceptual essence inform creative and original choices. Build something that expresses the vision for this particular request.
+
+**Canvas Setup**: Standard p5.js structure:
+```javascript
+function setup() {
+  createCanvas(1200, 1200);
+  // Initialize your system
+}
+
+function draw() {
+  // Your generative algorithm
+  // Can be static (noLoop) or animated
+}
+```
+
+### CRAFTSMANSHIP REQUIREMENTS
+
+**CRITICAL**: To achieve mastery, create algorithms that feel like they emerged through countless iterations by a master generative artist. Tune every parameter carefully. Ensure every pattern emerges with purpose. This is NOT random noise - this is CONTROLLED CHAOS refined through deep expertise.
+
+- **Balance**: Complexity without visual noise, order without rigidity
+- **Color Harmony**: Thoughtful palettes, not random RGB values
+- **Composition**: Even in randomness, maintain visual hierarchy and flow
+- **Performance**: Smooth execution, optimized for real-time if animated
+- **Reproducibility**: Same seed ALWAYS produces identical output
+
+### OUTPUT FORMAT
+
+Output:
+1. **Algorithmic Philosophy** - As markdown or text explaining the generative aesthetic
+2. **Single HTML Artifact** - Self-contained interactive generative art built from `templates/viewer.html` (see STEP 0 and next section)
+
+The HTML artifact contains everything: p5.js (from CDN), the algorithm, parameter controls, and UI - all in one file that works immediately in claude.ai artifacts or any browser. Start from the template file, not from scratch.
+
+---
+
+## INTERACTIVE ARTIFACT CREATION
+
+**REMINDER: `templates/viewer.html` should have already been read (see STEP 0). Use that file as the starting point.**
+
+To allow exploration of the generative art, create a single, self-contained HTML artifact. Ensure this artifact works immediately in claude.ai or any browser - no setup required. Embed everything inline.
+
+### CRITICAL: WHAT'S FIXED VS VARIABLE
+
+The `templates/viewer.html` file is the foundation. It contains the exact structure and styling needed.
+
+**FIXED (always include exactly as shown):**
+- Layout structure (header, sidebar, main canvas area)
+- Anthropic branding (UI colors, fonts, gradients)
+- Seed section in sidebar:
+  - Seed display
+  - Previous/Next buttons
+  - Random button
+  - Jump to seed input + Go button
+- Actions section in sidebar:
+  - Regenerate button
+  - Reset button
+
+**VARIABLE (customize for each artwork):**
+- The entire p5.js algorithm (setup/draw/classes)
+- The parameters object (define what the art needs)
+- The Parameters section in sidebar:
+  - Number of parameter controls
+  - Parameter names
+  - Min/max/step values for sliders
+  - Control types (sliders, inputs, etc.)
+- Colors section (optional):
+  - Some art needs color pickers
+  - Some art might use fixed colors
+  - Some art might be monochrome (no color controls needed)
+  - Decide based on the art's needs
+
+**Every artwork should have unique parameters and algorithm!** The fixed parts provide consistent UX - everything else expresses the unique vision.
+
+### REQUIRED FEATURES
+
+**1. Parameter Controls**
+- Sliders for numeric parameters (particle count, noise scale, speed, etc.)
+- Color pickers for palette colors
+- Real-time updates when parameters change
+- Reset button to restore defaults
+
+**2. Seed Navigation**
+- Display current seed number
+- "Previous" and "Next" buttons to cycle through seeds
+- "Random" button for random seed
+- Input field to jump to specific seed
+- Generate 100 variations when requested (seeds 1-100)
+
+**3. Single Artifact Structure**
+```html
+<!DOCTYPE html>
+<html>
+<head>
+  <!-- p5.js from CDN - always available -->
+  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.7.0/p5.min.js"></script>
+  <style>
+    /* All styling inline - clean, minimal */
+    /* Canvas on top, controls below */
+  </style>
+</head>
+<body>
+  <div id="canvas-container"></div>
+  <div id="controls">
+    <!-- All parameter controls -->
+  </div>
+  <script>
+    // ALL p5.js code inline here
+    // Parameter objects, classes, functions
+    // setup() and draw()
+    // UI handlers
+    // Everything self-contained
+  </script>
+</body>
+</html>
+```
+
+**CRITICAL**: This is a single artifact. No external files, no imports (except p5.js CDN). Everything inline.
+
+**4. Implementation Details - BUILD THE SIDEBAR**
+
+The sidebar structure:
+
+**1. Seed (FIXED)** - Always include exactly as shown:
+- Seed display
+- Prev/Next/Random/Jump buttons
+
+**2. Parameters (VARIABLE)** - Create controls for the art:
+```html
+<div class="control-group">
+    <label>Parameter Name</label>
+    <input type="range" id="param" min="..." max="..." step="..." value="..." oninput="updateParam('param', this.value)">
+    <span class="value-display" id="param-value">...</span>
+</div>
+```
+Add as many control-group divs as there are parameters.
+
+**3. Colors (OPTIONAL/VARIABLE)** - Include if the art needs adjustable colors:
+- Add color pickers if users should control palette
+- Skip this section if the art uses fixed colors
+- Skip if the art is monochrome
+
+**4. Actions (FIXED)** - Always include exactly as shown:
+- Regenerate button
+- Reset button
+- Download PNG button
+
+**Requirements**:
+- Seed controls must work (prev/next/random/jump/display)
+- All parameters must have UI controls
+- Regenerate, Reset, Download buttons must work
+- Keep Anthropic branding (UI styling, not art colors)
+
+### USING THE ARTIFACT
+
+The HTML artifact works immediately:
+1. **In claude.ai**: Displayed as an interactive artifact - runs instantly
+2. **As a file**: Save and open in any browser - no server needed
+3. **Sharing**: Send the HTML file - it's completely self-contained
+
+---
+
+## VARIATIONS & EXPLORATION
+
+The artifact includes seed navigation by default (prev/next/random buttons), allowing users to explore variations without creating multiple files. If the user wants specific variations highlighted:
+
+- Include seed presets (buttons for "Variation 1: Seed 42", "Variation 2: Seed 127", etc.)
+- Add a "Gallery Mode" that shows thumbnails of multiple seeds side-by-side
+- All within the same single artifact
+
+This is like creating a series of prints from the same plate - the algorithm is consistent, but each seed reveals different facets of its potential. The interactive nature means users discover their own favorites by exploring the seed space.
+
+---
+
+## THE CREATIVE PROCESS
+
+**User request** → **Algorithmic philosophy** → **Implementation**
+
+Each request is unique. The process involves:
+
+1. **Interpret the user's intent** - What aesthetic is being sought?
+2. **Create an algorithmic philosophy** (4-6 paragraphs) describing the computational approach
+3. **Implement it in code** - Build the algorithm that expresses this philosophy
+4. **Design appropriate parameters** - What should be tunable?
+5. **Build matching UI controls** - Sliders/inputs for those parameters
+
+**The constants**:
+- Anthropic branding (colors, fonts, layout)
+- Seed navigation (always present)
+- Self-contained HTML artifact
+
+**Everything else is variable**:
+- The algorithm itself
+- The parameters
+- The UI controls
+- The visual outcome
+
+To achieve the best results, trust creativity and let the philosophy guide the implementation.
+
+---
+
+## RESOURCES
+
+This skill includes helpful templates and documentation:
+
+- **templates/viewer.html**: REQUIRED STARTING POINT for all HTML artifacts.
+  - This is the foundation - contains the exact structure and Anthropic branding
+  - **Keep unchanged**: Layout structure, sidebar organization, Anthropic colors/fonts, seed controls, action buttons
+  - **Replace**: The p5.js algorithm, parameter definitions, and UI controls in Parameters section
+  - The extensive comments in the file mark exactly what to keep vs replace
+
+- **templates/generator_template.js**: Reference for p5.js best practices and code structure principles.
+  - Shows how to organize parameters, use seeded randomness, structure classes
+  - NOT a pattern menu - use these principles to build unique algorithms
+  - Embed algorithms inline in the HTML artifact (don't create separate .js files)
+
+**Critical reminder**:
+- The **template is the STARTING POINT**, not inspiration
+- The **algorithm is where to create** something unique
+- Don't copy the flow field example - build what the philosophy demands
+- But DO keep the exact UI structure and Anthropic branding from the template
\ No newline at end of file
diff --git a/artifacts-builder/SKILL.md b/artifacts-builder/SKILL.md
@@ -0,0 +1,74 @@
+---
+name: web-artifacts-builder
+description: Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui). Use for complex artifacts requiring state management, routing, or shadcn/ui components - not for simple single-file HTML/JSX artifacts.
+license: Complete terms in LICENSE.txt
+---
+
+# Web Artifacts Builder
+
+To build powerful frontend claude.ai artifacts, follow these steps:
+1. Initialize the frontend repo using `scripts/init-artifact.sh`
+2. Develop your artifact by editing the generated code
+3. Bundle all code into a single HTML file using `scripts/bundle-artifact.sh`
+4. Display artifact to user
+5. (Optional) Test the artifact
+
+**Stack**: React 18 + TypeScript + Vite + Parcel (bundling) + Tailwind CSS + shadcn/ui
+
+## Design & Style Guidelines
+
+VERY IMPORTANT: To avoid what is often referred to as "AI slop", avoid using excessive centered layouts, purple gradients, uniform rounded corners, and Inter font.
+
+## Quick Start
+
+### Step 1: Initialize Project
+
+Run the initialization script to create a new React project:
+```bash
+bash scripts/init-artifact.sh <project-name>
+cd <project-name>
+```
+
+This creates a fully configured project with:
+- ✅ React + TypeScript (via Vite)
+- ✅ Tailwind CSS 3.4.1 with shadcn/ui theming system
+- ✅ Path aliases (`@/`) configured
+- ✅ 40+ shadcn/ui components pre-installed
+- ✅ All Radix UI dependencies included
+- ✅ Parcel configured for bundling (via .parcelrc)
+- ✅ Node 18+ compatibility (auto-detects and pins Vite version)
+
+### Step 2: Develop Your Artifact
+
+To build the artifact, edit the generated files. See **Common Development Tasks** below for guidance.
+
+### Step 3: Bundle to Single HTML File
+
+To bundle the React app into a single HTML artifact:
+```bash
+bash scripts/bundle-artifact.sh
+```
+
+This creates `bundle.html` - a self-contained artifact with all JavaScript, CSS, and dependencies inlined. This file can be directly shared in Claude conversations as an artifact.
+
+**Requirements**: Your project must have an `index.html` in the root directory.
+
+**What the script does**:
+- Installs bundling dependencies (parcel, @parcel/config-default, parcel-resolver-tspaths, html-inline)
+- Creates `.parcelrc` config with path alias support
+- Builds with Parcel (no source maps)
+- Inlines all assets into single HTML using html-inline
+
+### Step 4: Share Artifact with User
+
+Finally, share the bundled HTML file in conversation with the user so they can view it as an artifact.
+
+### Step 5: Testing/Visualizing the Artifact (Optional)
+
+Note: This is a completely optional step. Only perform if necessary or requested.
+
+To test/visualize the artifact, use available tools (including other Skills or built-in tools like Playwright or Puppeteer). In general, avoid testing the artifact upfront as it adds latency between the request and when the finished artifact can be seen. Test later, after presenting the artifact, if requested or if issues arise.
+
+## Reference
+
+- **shadcn/ui components**: https://ui.shadcn.com/docs/components
\ No newline at end of file
diff --git a/brand-guidelines/SKILL.md b/brand-guidelines/SKILL.md
@@ -0,0 +1,73 @@
+---
+name: brand-guidelines
+description: Applies Anthropic's official brand colors and typography to any sort of artifact that may benefit from having Anthropic's look-and-feel. Use it when brand colors or style guidelines, visual formatting, or company design standards apply.
+license: Complete terms in LICENSE.txt
+---
+
+# Anthropic Brand Styling
+
+## Overview
+
+To access Anthropic's official brand identity and style resources, use this skill.
+
+**Keywords**: branding, corporate identity, visual identity, post-processing, styling, brand colors, typography, Anthropic brand, visual formatting, visual design
+
+## Brand Guidelines
+
+### Colors
+
+**Main Colors:**
+
+- Dark: `#141413` - Primary text and dark backgrounds
+- Light: `#faf9f5` - Light backgrounds and text on dark
+- Mid Gray: `#b0aea5` - Secondary elements
+- Light Gray: `#e8e6dc` - Subtle backgrounds
+
+**Accent Colors:**
+
+- Orange: `#d97757` - Primary accent
+- Blue: `#6a9bcc` - Secondary accent
+- Green: `#788c5d` - Tertiary accent
+
+### Typography
+
+- **Headings**: Poppins (with Arial fallback)
+- **Body Text**: Lora (with Georgia fallback)
+- **Note**: Fonts should be pre-installed in your environment for best results
+
+## Features
+
+### Smart Font Application
+
+- Applies Poppins font to headings (24pt and larger)
+- Applies Lora font to body text
+- Automatically falls back to Arial/Georgia if custom fonts unavailable
+- Preserves readability across all systems
+
+### Text Styling
+
+- Headings (24pt+): Poppins font
+- Body text: Lora font
+- Smart color selection based on background
+- Preserves text hierarchy and formatting
+
+### Shape and Accent Colors
+
+- Non-text shapes use accent colors
+- Cycles through orange, blue, and green accents
+- Maintains visual interest while staying on-brand
+
+## Technical Details
+
+### Font Management
+
+- Uses system-installed Poppins and Lora fonts when available
+- Provides automatic fallback to Arial (headings) and Georgia (body)
+- No font installation required - works with existing system fonts
+- For best results, pre-install Poppins and Lora fonts in your environment
+
+### Color Application
+
+- Uses RGB color values for precise brand matching
+- Applied via python-pptx's RGBColor class
+- Maintains color fidelity across different systems
diff --git a/canvas-design/SKILL.md b/canvas-design/SKILL.md
@@ -0,0 +1,130 @@
+---
+name: canvas-design
+description: Create beautiful visual art in .png and .pdf documents using design philosophy. You should use this skill when the user asks to create a poster, piece of art, design, or other static piece. Create original visual designs, never copying existing artists' work to avoid copyright violations.
+license: Complete terms in LICENSE.txt
+---
+
+These are instructions for creating design philosophies - aesthetic movements that are then EXPRESSED VISUALLY. Output only .md files, .pdf files, and .png files.
+
+Complete this in two steps:
+1. Design Philosophy Creation (.md file)
+2. Express by creating it on a canvas (.pdf file or .png file)
+
+First, undertake this task:
+
+## DESIGN PHILOSOPHY CREATION
+
+To begin, create a VISUAL PHILOSOPHY (not layouts or templates) that will be interpreted through:
+- Form, space, color, composition
+- Images, graphics, shapes, patterns
+- Minimal text as visual accent
+
+### THE CRITICAL UNDERSTANDING
+- What is received: Some subtle input or instructions by the user that should be taken into account, but used as a foundation; it should not constrain creative freedom.
+- What is created: A design philosophy/aesthetic movement.
+- What happens next: Then, the same version receives the philosophy and EXPRESSES IT VISUALLY - creating artifacts that are 90% visual design, 10% essential text.
+
+Consider this approach:
+- Write a manifesto for an art movement
+- The next phase involves making the artwork
+
+The philosophy must emphasize: Visual expression. Spatial communication. Artistic interpretation. Minimal words.
+
+### HOW TO GENERATE A VISUAL PHILOSOPHY
+
+**Name the movement** (1-2 words): "Brutalist Joy" / "Chromatic Silence" / "Metabolist Dreams"
+
+**Articulate the philosophy** (4-6 paragraphs - concise but complete):
+
+To capture the VISUAL essence, express how the philosophy manifests through:
+- Space and form
+- Color and material
+- Scale and rhythm
+- Composition and balance
+- Visual hierarchy
+
+**CRITICAL GUIDELINES:**
+- **Avoid redundancy**: Each design aspect should be mentioned once. Avoid repeating points about color theory, spatial relationships, or typographic principles unless adding new depth.
+- **Emphasize craftsmanship REPEATEDLY**: The philosophy MUST stress multiple times that the final work should appear as though it took countless hours to create, was labored over with care, and comes from someone at the absolute top of their field. This framing is essential - repeat phrases like "meticulously crafted," "the product of deep expertise," "painstaking attention," "master-level execution."
+- **Leave creative space**: Remain specific about the aesthetic direction, but concise enough that the next Claude has room to make interpretive choices also at a extremely high level of craftmanship.
+
+The philosophy must guide the next version to express ideas VISUALLY, not through text. Information lives in design, not paragraphs.
+
+### PHILOSOPHY EXAMPLES
+
+**"Concrete Poetry"**
+Philosophy: Communication through monumental form and bold geometry.
+Visual expression: Massive color blocks, sculptural typography (huge single words, tiny labels), Brutalist spatial divisions, Polish poster energy meets Le Corbusier. Ideas expressed through visual weight and spatial tension, not explanation. Text as rare, powerful gesture - never paragraphs, only essential words integrated into the visual architecture. Every element placed with the precision of a master craftsman.
+
+**"Chromatic Language"**
+Philosophy: Color as the primary information system.
+Visual expression: Geometric precision where color zones create meaning. Typography minimal - small sans-serif labels letting chromatic fields communicate. Think Josef Albers' interaction meets data visualization. Information encoded spatially and chromatically. Words only to anchor what color already shows. The result of painstaking chromatic calibration.
+
+**"Analog Meditation"**
+Philosophy: Quiet visual contemplation through texture and breathing room.
+Visual expression: Paper grain, ink bleeds, vast negative space. Photography and illustration dominate. Typography whispered (small, restrained, serving the visual). Japanese photobook aesthetic. Images breathe across pages. Text appears sparingly - short phrases, never explanatory blocks. Each composition balanced with the care of a meditation practice.
+
+**"Organic Systems"**
+Philosophy: Natural clustering and modular growth patterns.
+Visual expression: Rounded forms, organic arrangements, color from nature through architecture. Information shown through visual diagrams, spatial relationships, iconography. Text only for key labels floating in space. The composition tells the story through expert spatial orchestration.
+
+**"Geometric Silence"**
+Philosophy: Pure order and restraint.
+Visual expression: Grid-based precision, bold photography or stark graphics, dramatic negative space. Typography precise but minimal - small essential text, large quiet zones. Swiss formalism meets Brutalist material honesty. Structure communicates, not words. Every alignment the work of countless refinements.
+
+*These are condensed examples. The actual design philosophy should be 4-6 substantial paragraphs.*
+
+### ESSENTIAL PRINCIPLES
+- **VISUAL PHILOSOPHY**: Create an aesthetic worldview to be expressed through design
+- **MINIMAL TEXT**: Always emphasize that text is sparse, essential-only, integrated as visual element - never lengthy
+- **SPATIAL EXPRESSION**: Ideas communicate through space, form, color, composition - not paragraphs
+- **ARTISTIC FREEDOM**: The next Claude interprets the philosophy visually - provide creative room
+- **PURE DESIGN**: This is about making ART OBJECTS, not documents with decoration
+- **EXPERT CRAFTSMANSHIP**: Repeatedly emphasize the final work must look meticulously crafted, labored over with care, the product of countless hours by someone at the top of their field
+
+**The design philosophy should be 4-6 paragraphs long.** Fill it with poetic design philosophy that brings together the core vision. Avoid repeating the same points. Keep the design philosophy generic without mentioning the intention of the art, as if it can be used wherever. Output the design philosophy as a .md file.
+
+---
+
+## DEDUCING THE SUBTLE REFERENCE
+
+**CRITICAL STEP**: Before creating the canvas, identify the subtle conceptual thread from the original request.
+
+**THE ESSENTIAL PRINCIPLE**:
+The topic is a **subtle, niche reference embedded within the art itself** - not always literal, always sophisticated. Someone familiar with the subject should feel it intuitively, while others simply experience a masterful abstract composition. The design philosophy provides the aesthetic language. The deduced topic provides the soul - the quiet conceptual DNA woven invisibly into form, color, and composition.
+
+This is **VERY IMPORTANT**: The reference must be refined so it enhances the work's depth without announcing itself. Think like a jazz musician quoting another song - only those who know will catch it, but everyone appreciates the music.
+
+---
+
+## CANVAS CREATION
+
+With both the philosophy and the conceptual framework established, express it on a canvas. Take a moment to gather thoughts and clear the mind. Use the design philosophy created and the instructions below to craft a masterpiece, embodying all aspects of the philosophy with expert craftsmanship.
+
+**IMPORTANT**: For any type of content, even if the user requests something for a movie/game/book, the approach should still be sophisticated. Never lose sight of the idea that this should be art, not something that's cartoony or amateur.
+
+To create museum or magazine quality work, use the design philosophy as the foundation. Create one single page, highly visual, design-forward PDF or PNG output (unless asked for more pages). Generally use repeating patterns and perfect shapes. Treat the abstract philosophical design as if it were a scientific bible, borrowing the visual language of systematic observation—dense accumulation of marks, repeated elements, or layered patterns that build meaning through patient repetition and reward sustained viewing. Add sparse, clinical typography and systematic reference markers that suggest this could be a diagram from an imaginary discipline, treating the invisible subject with the same reverence typically reserved for documenting observable phenomena. Anchor the piece with simple phrase(s) or details positioned subtly, using a limited color palette that feels intentional and cohesive. Embrace the paradox of using analytical visual language to express ideas about human experience: the result should feel like an artifact that proves something ephemeral can be studied, mapped, and understood through careful attention. This is true art. 
+
+**Text as a contextual element**: Text is always minimal and visual-first, but let context guide whether that means whisper-quiet labels or bold typographic gestures. A punk venue poster might have larger, more aggressive type than a minimalist ceramics studio identity. Most of the time, font should be thin. All use of fonts must be design-forward and prioritize visual communication. Regardless of text scale, nothing falls off the page and nothing overlaps. Every element must be contained within the canvas boundaries with proper margins. Check carefully that all text, graphics, and visual elements have breathing room and clear separation. This is non-negotiable for professional execution. **IMPORTANT: Use different fonts if writing text. Search the `./canvas-fonts` directory. Regardless of approach, sophistication is non-negotiable.**
+
+Download and use whatever fonts are needed to make this a reality. Get creative by making the typography actually part of the art itself -- if the art is abstract, bring the font onto the canvas, not typeset digitally.
+
+To push boundaries, follow design instinct/intuition while using the philosophy as a guiding principle. Embrace ultimate design freedom and choice. Push aesthetics and design to the frontier. 
+
+**CRITICAL**: To achieve human-crafted quality (not AI-generated), create work that looks like it took countless hours. Make it appear as though someone at the absolute top of their field labored over every detail with painstaking care. Ensure the composition, spacing, color choices, typography - everything screams expert-level craftsmanship. Double-check that nothing overlaps, formatting is flawless, every detail perfect. Create something that could be shown to people to prove expertise and rank as undeniably impressive.
+
+Output the final result as a single, downloadable .pdf or .png file, alongside the design philosophy used as a .md file.
+
+---
+
+## FINAL STEP
+
+**IMPORTANT**: The user ALREADY said "It isn't perfect enough. It must be pristine, a masterpiece if craftsmanship, as if it were about to be displayed in a museum."
+
+**CRITICAL**: To refine the work, avoid adding more graphics; instead refine what has been created and make it extremely crisp, respecting the design philosophy and the principles of minimalism entirely. Rather than adding a fun filter or refactoring a font, consider how to make the existing composition more cohesive with the art. If the instinct is to call a new function or draw a new shape, STOP and instead ask: "How can I make what's already here more of a piece of art?"
+
+Take a second pass. Go back to the code and refine/polish further to make this a philosophically designed masterpiece.
+
+## MULTI-PAGE OPTION
+
+To create additional pages when requested, create more creative pages along the same lines as the design philosophy but distinctly different as well. Bundle those pages in the same .pdf or many .pngs. Treat the first page as just a single page in a whole coffee table book waiting to be filled. Make the next pages unique twists and memories of the original. Have them almost tell a story in a very tasteful way. Exercise full creative freedom.
\ No newline at end of file
diff --git a/docx/SKILL.md b/docx/SKILL.md
@@ -0,0 +1,197 @@
+---
+name: docx
+description: "Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. When Claude needs to work with professional documents (.docx files) for: (1) Creating new documents, (2) Modifying or editing content, (3) Working with tracked changes, (4) Adding comments, or any other document tasks"
+license: Proprietary. LICENSE.txt has complete terms
+---
+
+# DOCX creation, editing, and analysis
+
+## Overview
+
+A user may ask you to create, edit, or analyze the contents of a .docx file. A .docx file is essentially a ZIP archive containing XML files and other resources that you can read or edit. You have different tools and workflows available for different tasks.
+
+## Workflow Decision Tree
+
+### Reading/Analyzing Content
+Use "Text extraction" or "Raw XML access" sections below
+
+### Creating New Document
+Use "Creating a new Word document" workflow
+
+### Editing Existing Document
+- **Your own document + simple changes**
+  Use "Basic OOXML editing" workflow
+
+- **Someone else's document**
+  Use **"Redlining workflow"** (recommended default)
+
+- **Legal, academic, business, or government docs**
+  Use **"Redlining workflow"** (required)
+
+## Reading and analyzing content
+
+### Text extraction
+If you just need to read the text contents of a document, you should convert the document to markdown using pandoc. Pandoc provides excellent support for preserving document structure and can show tracked changes:
+
+```bash
+# Convert document to markdown with tracked changes
+pandoc --track-changes=all path-to-file.docx -o output.md
+# Options: --track-changes=accept/reject/all
+```
+
+### Raw XML access
+You need raw XML access for: comments, complex formatting, document structure, embedded media, and metadata. For any of these features, you'll need to unpack a document and read its raw XML contents.
+
+#### Unpacking a file
+`python ooxml/scripts/unpack.py <office_file> <output_directory>`
+
+#### Key file structures
+* `word/document.xml` - Main document contents
+* `word/comments.xml` - Comments referenced in document.xml
+* `word/media/` - Embedded images and media files
+* Tracked changes use `<w:ins>` (insertions) and `<w:del>` (deletions) tags
+
+## Creating a new Word document
+
+When creating a new Word document from scratch, use **docx-js**, which allows you to create Word documents using JavaScript/TypeScript.
+
+### Workflow
+1. **MANDATORY - READ ENTIRE FILE**: Read [`docx-js.md`](docx-js.md) (~500 lines) completely from start to finish. **NEVER set any range limits when reading this file.** Read the full file content for detailed syntax, critical formatting rules, and best practices before proceeding with document creation.
+2. Create a JavaScript/TypeScript file using Document, Paragraph, TextRun components (You can assume all dependencies are installed, but if not, refer to the dependencies section below)
+3. Export as .docx using Packer.toBuffer()
+
+## Editing an existing Word document
+
+When editing an existing Word document, use the **Document library** (a Python library for OOXML manipulation). The library automatically handles infrastructure setup and provides methods for document manipulation. For complex scenarios, you can access the underlying DOM directly through the library.
+
+### Workflow
+1. **MANDATORY - READ ENTIRE FILE**: Read [`ooxml.md`](ooxml.md) (~600 lines) completely from start to finish. **NEVER set any range limits when reading this file.** Read the full file content for the Document library API and XML patterns for directly editing document files.
+2. Unpack the document: `python ooxml/scripts/unpack.py <office_file> <output_directory>`
+3. Create and run a Python script using the Document library (see "Document Library" section in ooxml.md)
+4. Pack the final document: `python ooxml/scripts/pack.py <input_directory> <office_file>`
+
+The Document library provides both high-level methods for common operations and direct DOM access for complex scenarios.
+
+## Redlining workflow for document review
+
+This workflow allows you to plan comprehensive tracked changes using markdown before implementing them in OOXML. **CRITICAL**: For complete tracked changes, you must implement ALL changes systematically.
+
+**Batching Strategy**: Group related changes into batches of 3-10 changes. This makes debugging manageable while maintaining efficiency. Test each batch before moving to the next.
+
+**Principle: Minimal, Precise Edits**
+When implementing tracked changes, only mark text that actually changes. Repeating unchanged text makes edits harder to review and appears unprofessional. Break replacements into: [unchanged text] + [deletion] + [insertion] + [unchanged text]. Preserve the original run's RSID for unchanged text by extracting the `<w:r>` element from the original and reusing it.
+
+Example - Changing "30 days" to "60 days" in a sentence:
+```python
+# BAD - Replaces entire sentence
+'<w:del><w:r><w:delText>The term is 30 days.</w:delText></w:r></w:del><w:ins><w:r><w:t>The term is 60 days.</w:t></w:r></w:ins>'
+
+# GOOD - Only marks what changed, preserves original <w:r> for unchanged text
+'<w:r w:rsidR="00AB12CD"><w:t>The term is </w:t></w:r><w:del><w:r><w:delText>30</w:delText></w:r></w:del><w:ins><w:r><w:t>60</w:t></w:r></w:ins><w:r w:rsidR="00AB12CD"><w:t> days.</w:t></w:r>'
+```
+
+### Tracked changes workflow
+
+1. **Get markdown representation**: Convert document to markdown with tracked changes preserved:
+   ```bash
+   pandoc --track-changes=all path-to-file.docx -o current.md
+   ```
+
+2. **Identify and group changes**: Review the document and identify ALL changes needed, organizing them into logical batches:
+
+   **Location methods** (for finding changes in XML):
+   - Section/heading numbers (e.g., "Section 3.2", "Article IV")
+   - Paragraph identifiers if numbered
+   - Grep patterns with unique surrounding text
+   - Document structure (e.g., "first paragraph", "signature block")
+   - **DO NOT use markdown line numbers** - they don't map to XML structure
+
+   **Batch organization** (group 3-10 related changes per batch):
+   - By section: "Batch 1: Section 2 amendments", "Batch 2: Section 5 updates"
+   - By type: "Batch 1: Date corrections", "Batch 2: Party name changes"
+   - By complexity: Start with simple text replacements, then tackle complex structural changes
+   - Sequential: "Batch 1: Pages 1-3", "Batch 2: Pages 4-6"
+
+3. **Read documentation and unpack**:
+   - **MANDATORY - READ ENTIRE FILE**: Read [`ooxml.md`](ooxml.md) (~600 lines) completely from start to finish. **NEVER set any range limits when reading this file.** Pay special attention to the "Document Library" and "Tracked Change Patterns" sections.
+   - **Unpack the document**: `python ooxml/scripts/unpack.py <file.docx> <dir>`
+   - **Note the suggested RSID**: The unpack script will suggest an RSID to use for your tracked changes. Copy this RSID for use in step 4b.
+
+4. **Implement changes in batches**: Group changes logically (by section, by type, or by proximity) and implement them together in a single script. This approach:
+   - Makes debugging easier (smaller batch = easier to isolate errors)
+   - Allows incremental progress
+   - Maintains efficiency (batch size of 3-10 changes works well)
+
+   **Suggested batch groupings:**
+   - By document section (e.g., "Section 3 changes", "Definitions", "Termination clause")
+   - By change type (e.g., "Date changes", "Party name updates", "Legal term replacements")
+   - By proximity (e.g., "Changes on pages 1-3", "Changes in first half of document")
+
+   For each batch of related changes:
+
+   **a. Map text to XML**: Grep for text in `word/document.xml` to verify how text is split across `<w:r>` elements.
+
+   **b. Create and run script**: Use `get_node` to find nodes, implement changes, then `doc.save()`. See **"Document Library"** section in ooxml.md for patterns.
+
+   **Note**: Always grep `word/document.xml` immediately before writing a script to get current line numbers and verify text content. Line numbers change after each script run.
+
+5. **Pack the document**: After all batches are complete, convert the unpacked directory back to .docx:
+   ```bash
+   python ooxml/scripts/pack.py unpacked reviewed-document.docx
+   ```
+
+6. **Final verification**: Do a comprehensive check of the complete document:
+   - Convert final document to markdown:
+     ```bash
+     pandoc --track-changes=all reviewed-document.docx -o verification.md
+     ```
+   - Verify ALL changes were applied correctly:
+     ```bash
+     grep "original phrase" verification.md  # Should NOT find it
+     grep "replacement phrase" verification.md  # Should find it
+     ```
+   - Check that no unintended changes were introduced
+
+
+## Converting Documents to Images
+
+To visually analyze Word documents, convert them to images using a two-step process:
+
+1. **Convert DOCX to PDF**:
+   ```bash
+   soffice --headless --convert-to pdf document.docx
+   ```
+
+2. **Convert PDF pages to JPEG images**:
+   ```bash
+   pdftoppm -jpeg -r 150 document.pdf page
+   ```
+   This creates files like `page-1.jpg`, `page-2.jpg`, etc.
+
+Options:
+- `-r 150`: Sets resolution to 150 DPI (adjust for quality/size balance)
+- `-jpeg`: Output JPEG format (use `-png` for PNG if preferred)
+- `-f N`: First page to convert (e.g., `-f 2` starts from page 2)
+- `-l N`: Last page to convert (e.g., `-l 5` stops at page 5)
+- `page`: Prefix for output files
+
+Example for specific range:
+```bash
+pdftoppm -jpeg -r 150 -f 2 -l 5 document.pdf page  # Converts only pages 2-5
+```
+
+## Code Style Guidelines
+**IMPORTANT**: When generating code for DOCX operations:
+- Write concise code
+- Avoid verbose variable names and redundant operations
+- Avoid unnecessary print statements
+
+## Dependencies
+
+Required dependencies (install if not available):
+
+- **pandoc**: `sudo apt-get install pandoc` (for text extraction)
+- **docx**: `npm install -g docx` (for creating new documents)
+- **LibreOffice**: `sudo apt-get install libreoffice` (for PDF conversion)
+- **Poppler**: `sudo apt-get install poppler-utils` (for pdftoppm to convert PDF to images)
+- **defusedxml**: `pip install defusedxml` (for secure XML parsing)
\ No newline at end of file
diff --git a/internal-comms/SKILL.md b/internal-comms/SKILL.md
@@ -0,0 +1,32 @@
+---
+name: internal-comms
+description: A set of resources to help me write all kinds of internal communications, using the formats that my company likes to use. Claude should use this skill whenever asked to write some sort of internal communications (status reports, leadership updates, 3P updates, company newsletters, FAQs, incident reports, project updates, etc.).
+license: Complete terms in LICENSE.txt
+---
+
+## When to use this skill
+To write internal communications, use this skill for:
+- 3P updates (Progress, Plans, Problems)
+- Company newsletters
+- FAQ responses
+- Status reports
+- Leadership updates
+- Project updates
+- Incident reports
+
+## How to use this skill
+
+To write any internal communication:
+
+1. **Identify the communication type** from the request
+2. **Load the appropriate guideline file** from the `examples/` directory:
+    - `examples/3p-updates.md` - For Progress/Plans/Problems team updates
+    - `examples/company-newsletter.md` - For company-wide newsletters
+    - `examples/faq-answers.md` - For answering frequently asked questions
+    - `examples/general-comms.md` - For anything else that doesn't explicitly match one of the above
+3. **Follow the specific instructions** in that file for formatting, tone, and content gathering
+
+If the communication type doesn't match any existing guideline, ask for clarification or more context about the desired format.
+
+## Keywords
+3P updates, company newsletter, company comms, weekly update, faqs, common questions, updates, internal comms
diff --git a/mcp-builder/SKILL.md b/mcp-builder/SKILL.md
@@ -0,0 +1,236 @@
+---
+name: mcp-builder
+description: Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services, whether in Python (FastMCP) or Node/TypeScript (MCP SDK).
+license: Complete terms in LICENSE.txt
+---
+
+# MCP Server Development Guide
+
+## Overview
+
+Create MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. The quality of an MCP server is measured by how well it enables LLMs to accomplish real-world tasks.
+
+---
+
+# Process
+
+## 🚀 High-Level Workflow
+
+Creating a high-quality MCP server involves four main phases:
+
+### Phase 1: Deep Research and Planning
+
+#### 1.1 Understand Modern MCP Design
+
+**API Coverage vs. Workflow Tools:**
+Balance comprehensive API endpoint coverage with specialized workflow tools. Workflow tools can be more convenient for specific tasks, while comprehensive coverage gives agents flexibility to compose operations. Performance varies by client—some clients benefit from code execution that combines basic tools, while others work better with higher-level workflows. When uncertain, prioritize comprehensive API coverage.
+
+**Tool Naming and Discoverability:**
+Clear, descriptive tool names help agents find the right tools quickly. Use consistent prefixes (e.g., `github_create_issue`, `github_list_repos`) and action-oriented naming.
+
+**Context Management:**
+Agents benefit from concise tool descriptions and the ability to filter/paginate results. Design tools that return focused, relevant data. Some clients support code execution which can help agents filter and process data efficiently.
+
+**Actionable Error Messages:**
+Error messages should guide agents toward solutions with specific suggestions and next steps.
+
+#### 1.2 Study MCP Protocol Documentation
+
+**Navigate the MCP specification:**
+
+Start with the sitemap to find relevant pages: `https://modelcontextprotocol.io/sitemap.xml`
+
+Then fetch specific pages with `.md` suffix for markdown format (e.g., `https://modelcontextprotocol.io/specification/draft.md`).
+
+Key pages to review:
+- Specification overview and architecture
+- Transport mechanisms (streamable HTTP, stdio)
+- Tool, resource, and prompt definitions
+
+#### 1.3 Study Framework Documentation
+
+**Recommended stack:**
+- **Language**: TypeScript (high-quality SDK support and good compatibility in many execution environments e.g. MCPB. Plus AI models are good at generating TypeScript code, benefiting from its broad usage, static typing and good linting tools)
+- **Transport**: Streamable HTTP for remote servers, using stateless JSON (simpler to scale and maintain, as opposed to stateful sessions and streaming responses). stdio for local servers.
+
+**Load framework documentation:**
+
+- **MCP Best Practices**: [📋 View Best Practices](./reference/mcp_best_practices.md) - Core guidelines
+
+**For TypeScript (recommended):**
+- **TypeScript SDK**: Use WebFetch to load `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md`
+- [⚡ TypeScript Guide](./reference/node_mcp_server.md) - TypeScript patterns and examples
+
+**For Python:**
+- **Python SDK**: Use WebFetch to load `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`
+- [🐍 Python Guide](./reference/python_mcp_server.md) - Python patterns and examples
+
+#### 1.4 Plan Your Implementation
+
+**Understand the API:**
+Review the service's API documentation to identify key endpoints, authentication requirements, and data models. Use web search and WebFetch as needed.
+
+**Tool Selection:**
+Prioritize comprehensive API coverage. List endpoints to implement, starting with the most common operations.
+
+---
+
+### Phase 2: Implementation
+
+#### 2.1 Set Up Project Structure
+
+See language-specific guides for project setup:
+- [⚡ TypeScript Guide](./reference/node_mcp_server.md) - Project structure, package.json, tsconfig.json
+- [🐍 Python Guide](./reference/python_mcp_server.md) - Module organization, dependencies
+
+#### 2.2 Implement Core Infrastructure
+
+Create shared utilities:
+- API client with authentication
+- Error handling helpers
+- Response formatting (JSON/Markdown)
+- Pagination support
+
+#### 2.3 Implement Tools
+
+For each tool:
+
+**Input Schema:**
+- Use Zod (TypeScript) or Pydantic (Python)
+- Include constraints and clear descriptions
+- Add examples in field descriptions
+
+**Output Schema:**
+- Define `outputSchema` where possible for structured data
+- Use `structuredContent` in tool responses (TypeScript SDK feature)
+- Helps clients understand and process tool outputs
+
+**Tool Description:**
+- Concise summary of functionality
+- Parameter descriptions
+- Return type schema
+
+**Implementation:**
+- Async/await for I/O operations
+- Proper error handling with actionable messages
+- Support pagination where applicable
+- Return both text content and structured data when using modern SDKs
+
+**Annotations:**
+- `readOnlyHint`: true/false
+- `destructiveHint`: true/false
+- `idempotentHint`: true/false
+- `openWorldHint`: true/false
+
+---
+
+### Phase 3: Review and Test
+
+#### 3.1 Code Quality
+
+Review for:
+- No duplicated code (DRY principle)
+- Consistent error handling
+- Full type coverage
+- Clear tool descriptions
+
+#### 3.2 Build and Test
+
+**TypeScript:**
+- Run `npm run build` to verify compilation
+- Test with MCP Inspector: `npx @modelcontextprotocol/inspector`
+
+**Python:**
+- Verify syntax: `python -m py_compile your_server.py`
+- Test with MCP Inspector
+
+See language-specific guides for detailed testing approaches and quality checklists.
+
+---
+
+### Phase 4: Create Evaluations
+
+After implementing your MCP server, create comprehensive evaluations to test its effectiveness.
+
+**Load [✅ Evaluation Guide](./reference/evaluation.md) for complete evaluation guidelines.**
+
+#### 4.1 Understand Evaluation Purpose
+
+Use evaluations to test whether LLMs can effectively use your MCP server to answer realistic, complex questions.
+
+#### 4.2 Create 10 Evaluation Questions
+
+To create effective evaluations, follow the process outlined in the evaluation guide:
+
+1. **Tool Inspection**: List available tools and understand their capabilities
+2. **Content Exploration**: Use READ-ONLY operations to explore available data
+3. **Question Generation**: Create 10 complex, realistic questions
+4. **Answer Verification**: Solve each question yourself to verify answers
+
+#### 4.3 Evaluation Requirements
+
+Ensure each question is:
+- **Independent**: Not dependent on other questions
+- **Read-only**: Only non-destructive operations required
+- **Complex**: Requiring multiple tool calls and deep exploration
+- **Realistic**: Based on real use cases humans would care about
+- **Verifiable**: Single, clear answer that can be verified by string comparison
+- **Stable**: Answer won't change over time
+
+#### 4.4 Output Format
+
+Create an XML file with this structure:
+
+```xml
+<evaluation>
+  <qa_pair>
+    <question>Find discussions about AI model launches with animal codenames. One model needed a specific safety designation that uses the format ASL-X. What number X was being determined for the model named after a spotted wild cat?</question>
+    <answer>3</answer>
+  </qa_pair>
+<!-- More qa_pairs... -->
+</evaluation>
+```
+
+---
+
+# Reference Files
+
+## 📚 Documentation Library
+
+Load these resources as needed during development:
+
+### Core MCP Documentation (Load First)
+- **MCP Protocol**: Start with sitemap at `https://modelcontextprotocol.io/sitemap.xml`, then fetch specific pages with `.md` suffix
+- [📋 MCP Best Practices](./reference/mcp_best_practices.md) - Universal MCP guidelines including:
+  - Server and tool naming conventions
+  - Response format guidelines (JSON vs Markdown)
+  - Pagination best practices
+  - Transport selection (streamable HTTP vs stdio)
+  - Security and error handling standards
+
+### SDK Documentation (Load During Phase 1/2)
+- **Python SDK**: Fetch from `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`
+- **TypeScript SDK**: Fetch from `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md`
+
+### Language-Specific Implementation Guides (Load During Phase 2)
+- [🐍 Python Implementation Guide](./reference/python_mcp_server.md) - Complete Python/FastMCP guide with:
+  - Server initialization patterns
+  - Pydantic model examples
+  - Tool registration with `@mcp.tool`
+  - Complete working examples
+  - Quality checklist
+
+- [⚡ TypeScript Implementation Guide](./reference/node_mcp_server.md) - Complete TypeScript guide with:
+  - Project structure
+  - Zod schema patterns
+  - Tool registration with `server.registerTool`
+  - Complete working examples
+  - Quality checklist
+
+### Evaluation Guide (Load During Phase 4)
+- [✅ Evaluation Guide](./reference/evaluation.md) - Complete evaluation creation guide with:
+  - Question creation guidelines
+  - Answer verification strategies
+  - XML format specifications
+  - Example questions and answers
+  - Running an evaluation with the provided scripts
diff --git a/pdf/SKILL.md b/pdf/SKILL.md
@@ -0,0 +1,294 @@
+---
+name: pdf
+description: Comprehensive PDF manipulation toolkit for extracting text and tables, creating new PDFs, merging/splitting documents, and handling forms. When Claude needs to fill in a PDF form or programmatically process, generate, or analyze PDF documents at scale.
+license: Proprietary. LICENSE.txt has complete terms
+---
+
+# PDF Processing Guide
+
+## Overview
+
+This guide covers essential PDF processing operations using Python libraries and command-line tools. For advanced features, JavaScript libraries, and detailed examples, see reference.md. If you need to fill out a PDF form, read forms.md and follow its instructions.
+
+## Quick Start
+
+```python
+from pypdf import PdfReader, PdfWriter
+
+# Read a PDF
+reader = PdfReader("document.pdf")
+print(f"Pages: {len(reader.pages)}")
+
+# Extract text
+text = ""
+for page in reader.pages:
+    text += page.extract_text()
+```
+
+## Python Libraries
+
+### pypdf - Basic Operations
+
+#### Merge PDFs
+```python
+from pypdf import PdfWriter, PdfReader
+
+writer = PdfWriter()
+for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
+    reader = PdfReader(pdf_file)
+    for page in reader.pages:
+        writer.add_page(page)
+
+with open("merged.pdf", "wb") as output:
+    writer.write(output)
+```
+
+#### Split PDF
+```python
+reader = PdfReader("input.pdf")
+for i, page in enumerate(reader.pages):
+    writer = PdfWriter()
+    writer.add_page(page)
+    with open(f"page_{i+1}.pdf", "wb") as output:
+        writer.write(output)
+```
+
+#### Extract Metadata
+```python
+reader = PdfReader("document.pdf")
+meta = reader.metadata
+print(f"Title: {meta.title}")
+print(f"Author: {meta.author}")
+print(f"Subject: {meta.subject}")
+print(f"Creator: {meta.creator}")
+```
+
+#### Rotate Pages
+```python
+reader = PdfReader("input.pdf")
+writer = PdfWriter()
+
+page = reader.pages[0]
+page.rotate(90)  # Rotate 90 degrees clockwise
+writer.add_page(page)
+
+with open("rotated.pdf", "wb") as output:
+    writer.write(output)
+```
+
+### pdfplumber - Text and Table Extraction
+
+#### Extract Text with Layout
+```python
+import pdfplumber
+
+with pdfplumber.open("document.pdf") as pdf:
+    for page in pdf.pages:
+        text = page.extract_text()
+        print(text)
+```
+
+#### Extract Tables
+```python
+with pdfplumber.open("document.pdf") as pdf:
+    for i, page in enumerate(pdf.pages):
+        tables = page.extract_tables()
+        for j, table in enumerate(tables):
+            print(f"Table {j+1} on page {i+1}:")
+            for row in table:
+                print(row)
+```
+
+#### Advanced Table Extraction
+```python
+import pandas as pd
+
+with pdfplumber.open("document.pdf") as pdf:
+    all_tables = []
+    for page in pdf.pages:
+        tables = page.extract_tables()
+        for table in tables:
+            if table:  # Check if table is not empty
+                df = pd.DataFrame(table[1:], columns=table[0])
+                all_tables.append(df)
+
+# Combine all tables
+if all_tables:
+    combined_df = pd.concat(all_tables, ignore_index=True)
+    combined_df.to_excel("extracted_tables.xlsx", index=False)
+```
+
+### reportlab - Create PDFs
+
+#### Basic PDF Creation
+```python
+from reportlab.lib.pagesizes import letter
+from reportlab.pdfgen import canvas
+
+c = canvas.Canvas("hello.pdf", pagesize=letter)
+width, height = letter
+
+# Add text
+c.drawString(100, height - 100, "Hello World!")
+c.drawString(100, height - 120, "This is a PDF created with reportlab")
+
+# Add a line
+c.line(100, height - 140, 400, height - 140)
+
+# Save
+c.save()
+```
+
+#### Create PDF with Multiple Pages
+```python
+from reportlab.lib.pagesizes import letter
+from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
+from reportlab.lib.styles import getSampleStyleSheet
+
+doc = SimpleDocTemplate("report.pdf", pagesize=letter)
+styles = getSampleStyleSheet()
+story = []
+
+# Add content
+title = Paragraph("Report Title", styles['Title'])
+story.append(title)
+story.append(Spacer(1, 12))
+
+body = Paragraph("This is the body of the report. " * 20, styles['Normal'])
+story.append(body)
+story.append(PageBreak())
+
+# Page 2
+story.append(Paragraph("Page 2", styles['Heading1']))
+story.append(Paragraph("Content for page 2", styles['Normal']))
+
+# Build PDF
+doc.build(story)
+```
+
+## Command-Line Tools
+
+### pdftotext (poppler-utils)
+```bash
+# Extract text
+pdftotext input.pdf output.txt
+
+# Extract text preserving layout
+pdftotext -layout input.pdf output.txt
+
+# Extract specific pages
+pdftotext -f 1 -l 5 input.pdf output.txt  # Pages 1-5
+```
+
+### qpdf
+```bash
+# Merge PDFs
+qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf
+
+# Split pages
+qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
+qpdf input.pdf --pages . 6-10 -- pages6-10.pdf
+
+# Rotate pages
+qpdf input.pdf output.pdf --rotate=+90:1  # Rotate page 1 by 90 degrees
+
+# Remove password
+qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
+```
+
+### pdftk (if available)
+```bash
+# Merge
+pdftk file1.pdf file2.pdf cat output merged.pdf
+
+# Split
+pdftk input.pdf burst
+
+# Rotate
+pdftk input.pdf rotate 1east output rotated.pdf
+```
+
+## Common Tasks
+
+### Extract Text from Scanned PDFs
+```python
+# Requires: pip install pytesseract pdf2image
+import pytesseract
+from pdf2image import convert_from_path
+
+# Convert PDF to images
+images = convert_from_path('scanned.pdf')
+
+# OCR each page
+text = ""
+for i, image in enumerate(images):
+    text += f"Page {i+1}:\n"
+    text += pytesseract.image_to_string(image)
+    text += "\n\n"
+
+print(text)
+```
+
+### Add Watermark
+```python
+from pypdf import PdfReader, PdfWriter
+
+# Create watermark (or load existing)
+watermark = PdfReader("watermark.pdf").pages[0]
+
+# Apply to all pages
+reader = PdfReader("document.pdf")
+writer = PdfWriter()
+
+for page in reader.pages:
+    page.merge_page(watermark)
+    writer.add_page(page)
+
+with open("watermarked.pdf", "wb") as output:
+    writer.write(output)
+```
+
+### Extract Images
+```bash
+# Using pdfimages (poppler-utils)
+pdfimages -j input.pdf output_prefix
+
+# This extracts all images as output_prefix-000.jpg, output_prefix-001.jpg, etc.
+```
+
+### Password Protection
+```python
+from pypdf import PdfReader, PdfWriter
+
+reader = PdfReader("input.pdf")
+writer = PdfWriter()
+
+for page in reader.pages:
+    writer.add_page(page)
+
+# Add password
+writer.encrypt("userpassword", "ownerpassword")
+
+with open("encrypted.pdf", "wb") as output:
+    writer.write(output)
+```
+
+## Quick Reference
+
+| Task | Best Tool | Command/Code |
+|------|-----------|--------------|
+| Merge PDFs | pypdf | `writer.add_page(page)` |
+| Split PDFs | pypdf | One page per file |
+| Extract text | pdfplumber | `page.extract_text()` |
+| Extract tables | pdfplumber | `page.extract_tables()` |
+| Create PDFs | reportlab | Canvas or Platypus |
+| Command line merge | qpdf | `qpdf --empty --pages ...` |
+| OCR scanned PDFs | pytesseract | Convert to image first |
+| Fill PDF forms | pdf-lib or pypdf (see forms.md) | See forms.md |
+
+## Next Steps
+
+- For advanced pypdfium2 usage, see reference.md
+- For JavaScript libraries (pdf-lib), see reference.md
+- If you need to fill out a PDF form, follow the instructions in forms.md
+- For troubleshooting guides, see reference.md
diff --git a/pptx/SKILL.md b/pptx/SKILL.md
@@ -0,0 +1,484 @@
+---
+name: pptx
+description: "Presentation creation, editing, and analysis. When Claude needs to work with presentations (.pptx files) for: (1) Creating new presentations, (2) Modifying or editing content, (3) Working with layouts, (4) Adding comments or speaker notes, or any other presentation tasks"
+license: Proprietary. LICENSE.txt has complete terms
+---
+
+# PPTX creation, editing, and analysis
+
+## Overview
+
+A user may ask you to create, edit, or analyze the contents of a .pptx file. A .pptx file is essentially a ZIP archive containing XML files and other resources that you can read or edit. You have different tools and workflows available for different tasks.
+
+## Reading and analyzing content
+
+### Text extraction
+If you just need to read the text contents of a presentation, you should convert the document to markdown:
+
+```bash
+# Convert document to markdown
+python -m markitdown path-to-file.pptx
+```
+
+### Raw XML access
+You need raw XML access for: comments, speaker notes, slide layouts, animations, design elements, and complex formatting. For any of these features, you'll need to unpack a presentation and read its raw XML contents.
+
+#### Unpacking a file
+`python ooxml/scripts/unpack.py <office_file> <output_dir>`
+
+**Note**: The unpack.py script is located at `skills/pptx/ooxml/scripts/unpack.py` relative to the project root. If the script doesn't exist at this path, use `find . -name "unpack.py"` to locate it.
+
+#### Key file structures
+* `ppt/presentation.xml` - Main presentation metadata and slide references
+* `ppt/slides/slide{N}.xml` - Individual slide contents (slide1.xml, slide2.xml, etc.)
+* `ppt/notesSlides/notesSlide{N}.xml` - Speaker notes for each slide
+* `ppt/comments/modernComment_*.xml` - Comments for specific slides
+* `ppt/slideLayouts/` - Layout templates for slides
+* `ppt/slideMasters/` - Master slide templates
+* `ppt/theme/` - Theme and styling information
+* `ppt/media/` - Images and other media files
+
+#### Typography and color extraction
+**When given an example design to emulate**: Always analyze the presentation's typography and colors first using the methods below:
+1. **Read theme file**: Check `ppt/theme/theme1.xml` for colors (`<a:clrScheme>`) and fonts (`<a:fontScheme>`)
+2. **Sample slide content**: Examine `ppt/slides/slide1.xml` for actual font usage (`<a:rPr>`) and colors
+3. **Search for patterns**: Use grep to find color (`<a:solidFill>`, `<a:srgbClr>`) and font references across all XML files
+
+## Creating a new PowerPoint presentation **without a template**
+
+When creating a new PowerPoint presentation from scratch, use the **html2pptx** workflow to convert HTML slides to PowerPoint with accurate positioning.
+
+### Design Principles
+
+**CRITICAL**: Before creating any presentation, analyze the content and choose appropriate design elements:
+1. **Consider the subject matter**: What is this presentation about? What tone, industry, or mood does it suggest?
+2. **Check for branding**: If the user mentions a company/organization, consider their brand colors and identity
+3. **Match palette to content**: Select colors that reflect the subject
+4. **State your approach**: Explain your design choices before writing code
+
+**Requirements**:
+- ✅ State your content-informed design approach BEFORE writing code
+- ✅ Use web-safe fonts only: Arial, Helvetica, Times New Roman, Georgia, Courier New, Verdana, Tahoma, Trebuchet MS, Impact
+- ✅ Create clear visual hierarchy through size, weight, and color
+- ✅ Ensure readability: strong contrast, appropriately sized text, clean alignment
+- ✅ Be consistent: repeat patterns, spacing, and visual language across slides
+
+#### Color Palette Selection
+
+**Choosing colors creatively**:
+- **Think beyond defaults**: What colors genuinely match this specific topic? Avoid autopilot choices.
+- **Consider multiple angles**: Topic, industry, mood, energy level, target audience, brand identity (if mentioned)
+- **Be adventurous**: Try unexpected combinations - a healthcare presentation doesn't have to be green, finance doesn't have to be navy
+- **Build your palette**: Pick 3-5 colors that work together (dominant colors + supporting tones + accent)
+- **Ensure contrast**: Text must be clearly readable on backgrounds
+
+**Example color palettes** (use these to spark creativity - choose one, adapt it, or create your own):
+
+1. **Classic Blue**: Deep navy (#1C2833), slate gray (#2E4053), silver (#AAB7B8), off-white (#F4F6F6)
+2. **Teal & Coral**: Teal (#5EA8A7), deep teal (#277884), coral (#FE4447), white (#FFFFFF)
+3. **Bold Red**: Red (#C0392B), bright red (#E74C3C), orange (#F39C12), yellow (#F1C40F), green (#2ECC71)
+4. **Warm Blush**: Mauve (#A49393), blush (#EED6D3), rose (#E8B4B8), cream (#FAF7F2)
+5. **Burgundy Luxury**: Burgundy (#5D1D2E), crimson (#951233), rust (#C15937), gold (#997929)
+6. **Deep Purple & Emerald**: Purple (#B165FB), dark blue (#181B24), emerald (#40695B), white (#FFFFFF)
+7. **Cream & Forest Green**: Cream (#FFE1C7), forest green (#40695B), white (#FCFCFC)
+8. **Pink & Purple**: Pink (#F8275B), coral (#FF574A), rose (#FF737D), purple (#3D2F68)
+9. **Lime & Plum**: Lime (#C5DE82), plum (#7C3A5F), coral (#FD8C6E), blue-gray (#98ACB5)
+10. **Black & Gold**: Gold (#BF9A4A), black (#000000), cream (#F4F6F6)
+11. **Sage & Terracotta**: Sage (#87A96B), terracotta (#E07A5F), cream (#F4F1DE), charcoal (#2C2C2C)
+12. **Charcoal & Red**: Charcoal (#292929), red (#E33737), light gray (#CCCBCB)
+13. **Vibrant Orange**: Orange (#F96D00), light gray (#F2F2F2), charcoal (#222831)
+14. **Forest Green**: Black (#191A19), green (#4E9F3D), dark green (#1E5128), white (#FFFFFF)
+15. **Retro Rainbow**: Purple (#722880), pink (#D72D51), orange (#EB5C18), amber (#F08800), gold (#DEB600)
+16. **Vintage Earthy**: Mustard (#E3B448), sage (#CBD18F), forest green (#3A6B35), cream (#F4F1DE)
+17. **Coastal Rose**: Old rose (#AD7670), beaver (#B49886), eggshell (#F3ECDC), ash gray (#BFD5BE)
+18. **Orange & Turquoise**: Light orange (#FC993E), grayish turquoise (#667C6F), white (#FCFCFC)
+
+#### Visual Details Options
+
+**Geometric Patterns**:
+- Diagonal section dividers instead of horizontal
+- Asymmetric column widths (30/70, 40/60, 25/75)
+- Rotated text headers at 90° or 270°
+- Circular/hexagonal frames for images
+- Triangular accent shapes in corners
+- Overlapping shapes for depth
+
+**Border & Frame Treatments**:
+- Thick single-color borders (10-20pt) on one side only
+- Double-line borders with contrasting colors
+- Corner brackets instead of full frames
+- L-shaped borders (top+left or bottom+right)
+- Underline accents beneath headers (3-5pt thick)
+
+**Typography Treatments**:
+- Extreme size contrast (72pt headlines vs 11pt body)
+- All-caps headers with wide letter spacing
+- Numbered sections in oversized display type
+- Monospace (Courier New) for data/stats/technical content
+- Condensed fonts (Arial Narrow) for dense information
+- Outlined text for emphasis
+
+**Chart & Data Styling**:
+- Monochrome charts with single accent color for key data
+- Horizontal bar charts instead of vertical
+- Dot plots instead of bar charts
+- Minimal gridlines or none at all
+- Data labels directly on elements (no legends)
+- Oversized numbers for key metrics
+
+**Layout Innovations**:
+- Full-bleed images with text overlays
+- Sidebar column (20-30% width) for navigation/context
+- Modular grid systems (3×3, 4×4 blocks)
+- Z-pattern or F-pattern content flow
+- Floating text boxes over colored shapes
+- Magazine-style multi-column layouts
+
+**Background Treatments**:
+- Solid color blocks occupying 40-60% of slide
+- Gradient fills (vertical or diagonal only)
+- Split backgrounds (two colors, diagonal or vertical)
+- Edge-to-edge color bands
+- Negative space as a design element
+
+### Layout Tips
+**When creating slides with charts or tables:**
+- **Two-column layout (PREFERRED)**: Use a header spanning the full width, then two columns below - text/bullets in one column and the featured content in the other. This provides better balance and makes charts/tables more readable. Use flexbox with unequal column widths (e.g., 40%/60% split) to optimize space for each content type.
+- **Full-slide layout**: Let the featured content (chart/table) take up the entire slide for maximum impact and readability
+- **NEVER vertically stack**: Do not place charts/tables below text in a single column - this causes poor readability and layout issues
+
+### Workflow
+1. **MANDATORY - READ ENTIRE FILE**: Read [`html2pptx.md`](html2pptx.md) completely from start to finish. **NEVER set any range limits when reading this file.** Read the full file content for detailed syntax, critical formatting rules, and best practices before proceeding with presentation creation.
+2. Create an HTML file for each slide with proper dimensions (e.g., 720pt × 405pt for 16:9)
+   - Use `<p>`, `<h1>`-`<h6>`, `<ul>`, `<ol>` for all text content
+   - Use `class="placeholder"` for areas where charts/tables will be added (render with gray background for visibility)
+   - **CRITICAL**: Rasterize gradients and icons as PNG images FIRST using Sharp, then reference in HTML
+   - **LAYOUT**: For slides with charts/tables/images, use either full-slide layout or two-column layout for better readability
+3. Create and run a JavaScript file using the [`html2pptx.js`](scripts/html2pptx.js) library to convert HTML slides to PowerPoint and save the presentation
+   - Use the `html2pptx()` function to process each HTML file
+   - Add charts and tables to placeholder areas using PptxGenJS API
+   - Save the presentation using `pptx.writeFile()`
+4. **Visual validation**: Generate thumbnails and inspect for layout issues
+   - Create thumbnail grid: `python scripts/thumbnail.py output.pptx workspace/thumbnails --cols 4`
+   - Read and carefully examine the thumbnail image for:
+     - **Text cutoff**: Text being cut off by header bars, shapes, or slide edges
+     - **Text overlap**: Text overlapping with other text or shapes
+     - **Positioning issues**: Content too close to slide boundaries or other elements
+     - **Contrast issues**: Insufficient contrast between text and backgrounds
+   - If issues found, adjust HTML margins/spacing/colors and regenerate the presentation
+   - Repeat until all slides are visually correct
+
+## Editing an existing PowerPoint presentation
+
+When edit slides in an existing PowerPoint presentation, you need to work with the raw Office Open XML (OOXML) format. This involves unpacking the .pptx file, editing the XML content, and repacking it.
+
+### Workflow
+1. **MANDATORY - READ ENTIRE FILE**: Read [`ooxml.md`](ooxml.md) (~500 lines) completely from start to finish.  **NEVER set any range limits when reading this file.**  Read the full file content for detailed guidance on OOXML structure and editing workflows before any presentation editing.
+2. Unpack the presentation: `python ooxml/scripts/unpack.py <office_file> <output_dir>`
+3. Edit the XML files (primarily `ppt/slides/slide{N}.xml` and related files)
+4. **CRITICAL**: Validate immediately after each edit and fix any validation errors before proceeding: `python ooxml/scripts/validate.py <dir> --original <file>`
+5. Pack the final presentation: `python ooxml/scripts/pack.py <input_directory> <office_file>`
+
+## Creating a new PowerPoint presentation **using a template**
+
+When you need to create a presentation that follows an existing template's design, you'll need to duplicate and re-arrange template slides before then replacing placeholder context.
+
+### Workflow
+1. **Extract template text AND create visual thumbnail grid**:
+   * Extract text: `python -m markitdown template.pptx > template-content.md`
+   * Read `template-content.md`: Read the entire file to understand the contents of the template presentation. **NEVER set any range limits when reading this file.**
+   * Create thumbnail grids: `python scripts/thumbnail.py template.pptx`
+   * See [Creating Thumbnail Grids](#creating-thumbnail-grids) section for more details
+
+2. **Analyze template and save inventory to a file**:
+   * **Visual Analysis**: Review thumbnail grid(s) to understand slide layouts, design patterns, and visual structure
+   * Create and save a template inventory file at `template-inventory.md` containing:
+     ```markdown
+     # Template Inventory Analysis
+     **Total Slides: [count]**
+     **IMPORTANT: Slides are 0-indexed (first slide = 0, last slide = count-1)**
+
+     ## [Category Name]
+     - Slide 0: [Layout code if available] - Description/purpose
+     - Slide 1: [Layout code] - Description/purpose
+     - Slide 2: [Layout code] - Description/purpose
+     [... EVERY slide must be listed individually with its index ...]
+     ```
+   * **Using the thumbnail grid**: Reference the visual thumbnails to identify:
+     - Layout patterns (title slides, content layouts, section dividers)
+     - Image placeholder locations and counts
+     - Design consistency across slide groups
+     - Visual hierarchy and structure
+   * This inventory file is REQUIRED for selecting appropriate templates in the next step
+
+3. **Create presentation outline based on template inventory**:
+   * Review available templates from step 2.
+   * Choose an intro or title template for the first slide. This should be one of the first templates.
+   * Choose safe, text-based layouts for the other slides.
+   * **CRITICAL: Match layout structure to actual content**:
+     - Single-column layouts: Use for unified narrative or single topic
+     - Two-column layouts: Use ONLY when you have exactly 2 distinct items/concepts
+     - Three-column layouts: Use ONLY when you have exactly 3 distinct items/concepts
+     - Image + text layouts: Use ONLY when you have actual images to insert
+     - Quote layouts: Use ONLY for actual quotes from people (with attribution), never for emphasis
+     - Never use layouts with more placeholders than you have content
+     - If you have 2 items, don't force them into a 3-column layout
+     - If you have 4+ items, consider breaking into multiple slides or using a list format
+   * Count your actual content pieces BEFORE selecting the layout
+   * Verify each placeholder in the chosen layout will be filled with meaningful content
+   * Select one option representing the **best** layout for each content section.
+   * Save `outline.md` with content AND template mapping that leverages available designs
+   * Example template mapping:
+      ```
+      # Template slides to use (0-based indexing)
+      # WARNING: Verify indices are within range! Template with 73 slides has indices 0-72
+      # Mapping: slide numbers from outline -> template slide indices
+      template_mapping = [
+          0,   # Use slide 0 (Title/Cover)
+          34,  # Use slide 34 (B1: Title and body)
+          34,  # Use slide 34 again (duplicate for second B1)
+          50,  # Use slide 50 (E1: Quote)
+          54,  # Use slide 54 (F2: Closing + Text)
+      ]
+      ```
+
+4. **Duplicate, reorder, and delete slides using `rearrange.py`**:
+   * Use the `scripts/rearrange.py` script to create a new presentation with slides in the desired order:
+     ```bash
+     python scripts/rearrange.py template.pptx working.pptx 0,34,34,50,52
+     ```
+   * The script handles duplicating repeated slides, deleting unused slides, and reordering automatically
+   * Slide indices are 0-based (first slide is 0, second is 1, etc.)
+   * The same slide index can appear multiple times to duplicate that slide
+
+5. **Extract ALL text using the `inventory.py` script**:
+   * **Run inventory extraction**:
+     ```bash
+     python scripts/inventory.py working.pptx text-inventory.json
+     ```
+   * **Read text-inventory.json**: Read the entire text-inventory.json file to understand all shapes and their properties. **NEVER set any range limits when reading this file.**
+
+   * The inventory JSON structure:
+      ```json
+        {
+          "slide-0": {
+            "shape-0": {
+              "placeholder_type": "TITLE",  // or null for non-placeholders
+              "left": 1.5,                  // position in inches
+              "top": 2.0,
+              "width": 7.5,
+              "height": 1.2,
+              "paragraphs": [
+                {
+                  "text": "Paragraph text",
+                  // Optional properties (only included when non-default):
+                  "bullet": true,           // explicit bullet detected
+                  "level": 0,               // only included when bullet is true
+                  "alignment": "CENTER",    // CENTER, RIGHT (not LEFT)
+                  "space_before": 10.0,     // space before paragraph in points
+                  "space_after": 6.0,       // space after paragraph in points
+                  "line_spacing": 22.4,     // line spacing in points
+                  "font_name": "Arial",     // from first run
+                  "font_size": 14.0,        // in points
+                  "bold": true,
+                  "italic": false,
+                  "underline": false,
+                  "color": "FF0000"         // RGB color
+                }
+              ]
+            }
+          }
+        }
+      ```
+
+   * Key features:
+     - **Slides**: Named as "slide-0", "slide-1", etc.
+     - **Shapes**: Ordered by visual position (top-to-bottom, left-to-right) as "shape-0", "shape-1", etc.
+     - **Placeholder types**: TITLE, CENTER_TITLE, SUBTITLE, BODY, OBJECT, or null
+     - **Default font size**: `default_font_size` in points extracted from layout placeholders (when available)
+     - **Slide numbers are filtered**: Shapes with SLIDE_NUMBER placeholder type are automatically excluded from inventory
+     - **Bullets**: When `bullet: true`, `level` is always included (even if 0)
+     - **Spacing**: `space_before`, `space_after`, and `line_spacing` in points (only included when set)
+     - **Colors**: `color` for RGB (e.g., "FF0000"), `theme_color` for theme colors (e.g., "DARK_1")
+     - **Properties**: Only non-default values are included in the output
+
+6. **Generate replacement text and save the data to a JSON file**
+   Based on the text inventory from the previous step:
+   - **CRITICAL**: First verify which shapes exist in the inventory - only reference shapes that are actually present
+   - **VALIDATION**: The replace.py script will validate that all shapes in your replacement JSON exist in the inventory
+     - If you reference a non-existent shape, you'll get an error showing available shapes
+     - If you reference a non-existent slide, you'll get an error indicating the slide doesn't exist
+     - All validation errors are shown at once before the script exits
+   - **IMPORTANT**: The replace.py script uses inventory.py internally to identify ALL text shapes
+   - **AUTOMATIC CLEARING**: ALL text shapes from the inventory will be cleared unless you provide "paragraphs" for them
+   - Add a "paragraphs" field to shapes that need content (not "replacement_paragraphs")
+   - Shapes without "paragraphs" in the replacement JSON will have their text cleared automatically
+   - Paragraphs with bullets will be automatically left aligned. Don't set the `alignment` property on when `"bullet": true`
+   - Generate appropriate replacement content for placeholder text
+   - Use shape size to determine appropriate content length
+   - **CRITICAL**: Include paragraph properties from the original inventory - don't just provide text
+   - **IMPORTANT**: When bullet: true, do NOT include bullet symbols (•, -, *) in text - they're added automatically
+   - **ESSENTIAL FORMATTING RULES**:
+     - Headers/titles should typically have `"bold": true`
+     - List items should have `"bullet": true, "level": 0` (level is required when bullet is true)
+     - Preserve any alignment properties (e.g., `"alignment": "CENTER"` for centered text)
+     - Include font properties when different from default (e.g., `"font_size": 14.0`, `"font_name": "Lora"`)
+     - Colors: Use `"color": "FF0000"` for RGB or `"theme_color": "DARK_1"` for theme colors
+     - The replacement script expects **properly formatted paragraphs**, not just text strings
+     - **Overlapping shapes**: Prefer shapes with larger default_font_size or more appropriate placeholder_type
+   - Save the updated inventory with replacements to `replacement-text.json`
+   - **WARNING**: Different template layouts have different shape counts - always check the actual inventory before creating replacements
+
+   Example paragraphs field showing proper formatting:
+   ```json
+   "paragraphs": [
+     {
+       "text": "New presentation title text",
+       "alignment": "CENTER",
+       "bold": true
+     },
+     {
+       "text": "Section Header",
+       "bold": true
+     },
+     {
+       "text": "First bullet point without bullet symbol",
+       "bullet": true,
+       "level": 0
+     },
+     {
+       "text": "Red colored text",
+       "color": "FF0000"
+     },
+     {
+       "text": "Theme colored text",
+       "theme_color": "DARK_1"
+     },
+     {
+       "text": "Regular paragraph text without special formatting"
+     }
+   ]
+   ```
+
+   **Shapes not listed in the replacement JSON are automatically cleared**:
+   ```json
+   {
+     "slide-0": {
+       "shape-0": {
+         "paragraphs": [...] // This shape gets new text
+       }
+       // shape-1 and shape-2 from inventory will be cleared automatically
+     }
+   }
+   ```
+
+   **Common formatting patterns for presentations**:
+   - Title slides: Bold text, sometimes centered
+   - Section headers within slides: Bold text
+   - Bullet lists: Each item needs `"bullet": true, "level": 0`
+   - Body text: Usually no special properties needed
+   - Quotes: May have special alignment or font properties
+
+7. **Apply replacements using the `replace.py` script**
+   ```bash
+   python scripts/replace.py working.pptx replacement-text.json output.pptx
+   ```
+
+   The script will:
+   - First extract the inventory of ALL text shapes using functions from inventory.py
+   - Validate that all shapes in the replacement JSON exist in the inventory
+   - Clear text from ALL shapes identified in the inventory
+   - Apply new text only to shapes with "paragraphs" defined in the replacement JSON
+   - Preserve formatting by applying paragraph properties from the JSON
+   - Handle bullets, alignment, font properties, and colors automatically
+   - Save the updated presentation
+
+   Example validation errors:
+   ```
+   ERROR: Invalid shapes in replacement JSON:
+     - Shape 'shape-99' not found on 'slide-0'. Available shapes: shape-0, shape-1, shape-4
+     - Slide 'slide-999' not found in inventory
+   ```
+
+   ```
+   ERROR: Replacement text made overflow worse in these shapes:
+     - slide-0/shape-2: overflow worsened by 1.25" (was 0.00", now 1.25")
+   ```
+
+## Creating Thumbnail Grids
+
+To create visual thumbnail grids of PowerPoint slides for quick analysis and reference:
+
+```bash
+python scripts/thumbnail.py template.pptx [output_prefix]
+```
+
+**Features**:
+- Creates: `thumbnails.jpg` (or `thumbnails-1.jpg`, `thumbnails-2.jpg`, etc. for large decks)
+- Default: 5 columns, max 30 slides per grid (5×6)
+- Custom prefix: `python scripts/thumbnail.py template.pptx my-grid`
+  - Note: The output prefix should include the path if you want output in a specific directory (e.g., `workspace/my-grid`)
+- Adjust columns: `--cols 4` (range: 3-6, affects slides per grid)
+- Grid limits: 3 cols = 12 slides/grid, 4 cols = 20, 5 cols = 30, 6 cols = 42
+- Slides are zero-indexed (Slide 0, Slide 1, etc.)
+
+**Use cases**:
+- Template analysis: Quickly understand slide layouts and design patterns
+- Content review: Visual overview of entire presentation
+- Navigation reference: Find specific slides by their visual appearance
+- Quality check: Verify all slides are properly formatted
+
+**Examples**:
+```bash
+# Basic usage
+python scripts/thumbnail.py presentation.pptx
+
+# Combine options: custom name, columns
+python scripts/thumbnail.py template.pptx analysis --cols 4
+```
+
+## Converting Slides to Images
+
+To visually analyze PowerPoint slides, convert them to images using a two-step process:
+
+1. **Convert PPTX to PDF**:
+   ```bash
+   soffice --headless --convert-to pdf template.pptx
+   ```
+
+2. **Convert PDF pages to JPEG images**:
+   ```bash
+   pdftoppm -jpeg -r 150 template.pdf slide
+   ```
+   This creates files like `slide-1.jpg`, `slide-2.jpg`, etc.
+
+Options:
+- `-r 150`: Sets resolution to 150 DPI (adjust for quality/size balance)
+- `-jpeg`: Output JPEG format (use `-png` for PNG if preferred)
+- `-f N`: First page to convert (e.g., `-f 2` starts from page 2)
+- `-l N`: Last page to convert (e.g., `-l 5` stops at page 5)
+- `slide`: Prefix for output files
+
+Example for specific range:
+```bash
+pdftoppm -jpeg -r 150 -f 2 -l 5 template.pdf slide  # Converts only pages 2-5
+```
+
+## Code Style Guidelines
+**IMPORTANT**: When generating code for PPTX operations:
+- Write concise code
+- Avoid verbose variable names and redundant operations
+- Avoid unnecessary print statements
+
+## Dependencies
+
+Required dependencies (should already be installed):
+
+- **markitdown**: `pip install "markitdown[pptx]"` (for text extraction from presentations)
+- **pptxgenjs**: `npm install -g pptxgenjs` (for creating presentations via html2pptx)
+- **playwright**: `npm install -g playwright` (for HTML rendering in html2pptx)
+- **react-icons**: `npm install -g react-icons react react-dom` (for icons)
+- **sharp**: `npm install -g sharp` (for SVG rasterization and image processing)
+- **LibreOffice**: `sudo apt-get install libreoffice` (for PDF conversion)
+- **Poppler**: `sudo apt-get install poppler-utils` (for pdftoppm to convert PDF to images)
+- **defusedxml**: `pip install defusedxml` (for secure XML parsing)
\ No newline at end of file
diff --git a/skill-creator/SKILL.md b/skill-creator/SKILL.md
@@ -0,0 +1,356 @@
+---
+name: skill-creator
+description: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities with specialized knowledge, workflows, or tool integrations.
+license: Complete terms in LICENSE.txt
+---
+
+# Skill Creator
+
+This skill provides guidance for creating effective skills.
+
+## About Skills
+
+Skills are modular, self-contained packages that extend Claude's capabilities by providing
+specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific
+domains or tasks—they transform Claude from a general-purpose agent into a specialized agent
+equipped with procedural knowledge that no model can fully possess.
+
+### What Skills Provide
+
+1. Specialized workflows - Multi-step procedures for specific domains
+2. Tool integrations - Instructions for working with specific file formats or APIs
+3. Domain expertise - Company-specific knowledge, schemas, business logic
+4. Bundled resources - Scripts, references, and assets for complex and repetitive tasks
+
+## Core Principles
+
+### Concise is Key
+
+The context window is a public good. Skills share the context window with everything else Claude needs: system prompt, conversation history, other Skills' metadata, and the actual user request.
+
+**Default assumption: Claude is already very smart.** Only add context Claude doesn't already have. Challenge each piece of information: "Does Claude really need this explanation?" and "Does this paragraph justify its token cost?"
+
+Prefer concise examples over verbose explanations.
+
+### Set Appropriate Degrees of Freedom
+
+Match the level of specificity to the task's fragility and variability:
+
+**High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.
+
+**Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.
+
+**Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.
+
+Think of Claude as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom).
+
+### Anatomy of a Skill
+
+Every skill consists of a required SKILL.md file and optional bundled resources:
+
+```
+skill-name/
+├── SKILL.md (required)
+│   ├── YAML frontmatter metadata (required)
+│   │   ├── name: (required)
+│   │   └── description: (required)
+│   └── Markdown instructions (required)
+└── Bundled Resources (optional)
+    ├── scripts/          - Executable code (Python/Bash/etc.)
+    ├── references/       - Documentation intended to be loaded into context as needed
+    └── assets/           - Files used in output (templates, icons, fonts, etc.)
+```
+
+#### SKILL.md (required)
+
+Every SKILL.md consists of:
+
+- **Frontmatter** (YAML): Contains `name` and `description` fields. These are the only fields that Claude reads to determine when the skill gets used, thus it is very important to be clear and comprehensive in describing what the skill is, and when it should be used.
+- **Body** (Markdown): Instructions and guidance for using the skill. Only loaded AFTER the skill triggers (if at all).
+
+#### Bundled Resources (optional)
+
+##### Scripts (`scripts/`)
+
+Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.
+
+- **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
+- **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
+- **Benefits**: Token efficient, deterministic, may be executed without loading into context
+- **Note**: Scripts may still need to be read by Claude for patching or environment-specific adjustments
+
+##### References (`references/`)
+
+Documentation and reference material intended to be loaded as needed into context to inform Claude's process and thinking.
+
+- **When to include**: For documentation that Claude should reference while working
+- **Examples**: `references/finance.md` for financial schemas, `references/mnda.md` for company NDA template, `references/policies.md` for company policies, `references/api_docs.md` for API specifications
+- **Use cases**: Database schemas, API documentation, domain knowledge, company policies, detailed workflow guides
+- **Benefits**: Keeps SKILL.md lean, loaded only when Claude determines it's needed
+- **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md
+- **Avoid duplication**: Information should live in either SKILL.md or references files, not both. Prefer references files for detailed information unless it's truly core to the skill—this keeps SKILL.md lean while making information discoverable without hogging the context window. Keep only essential procedural instructions and workflow guidance in SKILL.md; move detailed reference material, schemas, and examples to references files.
+
+##### Assets (`assets/`)
+
+Files not intended to be loaded into context, but rather used within the output Claude produces.
+
+- **When to include**: When the skill needs files that will be used in the final output
+- **Examples**: `assets/logo.png` for brand assets, `assets/slides.pptx` for PowerPoint templates, `assets/frontend-template/` for HTML/React boilerplate, `assets/font.ttf` for typography
+- **Use cases**: Templates, images, icons, boilerplate code, fonts, sample documents that get copied or modified
+- **Benefits**: Separates output resources from documentation, enables Claude to use files without loading them into context
+
+#### What to Not Include in a Skill
+
+A skill should only contain essential files that directly support its functionality. Do NOT create extraneous documentation or auxiliary files, including:
+
+- README.md
+- INSTALLATION_GUIDE.md
+- QUICK_REFERENCE.md
+- CHANGELOG.md
+- etc.
+
+The skill should only contain the information needed for an AI agent to do the job at hand. It should not contain auxilary context about the process that went into creating it, setup and testing procedures, user-facing documentation, etc. Creating additional documentation files just adds clutter and confusion.
+
+### Progressive Disclosure Design Principle
+
+Skills use a three-level loading system to manage context efficiently:
+
+1. **Metadata (name + description)** - Always in context (~100 words)
+2. **SKILL.md body** - When skill triggers (<5k words)
+3. **Bundled resources** - As needed by Claude (Unlimited because scripts can be executed without reading into context window)
+
+#### Progressive Disclosure Patterns
+
+Keep SKILL.md body to the essentials and under 500 lines to minimize context bloat. Split content into separate files when approaching this limit. When splitting out content into other files, it is very important to reference them from SKILL.md and describe clearly when to read them, to ensure the reader of the skill knows they exist and when to use them.
+
+**Key principle:** When a skill supports multiple variations, frameworks, or options, keep only the core workflow and selection guidance in SKILL.md. Move variant-specific details (patterns, examples, configuration) into separate reference files.
+
+**Pattern 1: High-level guide with references**
+
+```markdown
+# PDF Processing
+
+## Quick start
+
+Extract text with pdfplumber:
+[code example]
+
+## Advanced features
+
+- **Form filling**: See [FORMS.md](FORMS.md) for complete guide
+- **API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
+- **Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
+```
+
+Claude loads FORMS.md, REFERENCE.md, or EXAMPLES.md only when needed.
+
+**Pattern 2: Domain-specific organization**
+
+For Skills with multiple domains, organize content by domain to avoid loading irrelevant context:
+
+```
+bigquery-skill/
+├── SKILL.md (overview and navigation)
+└── reference/
+    ├── finance.md (revenue, billing metrics)
+    ├── sales.md (opportunities, pipeline)
+    ├── product.md (API usage, features)
+    └── marketing.md (campaigns, attribution)
+```
+
+When a user asks about sales metrics, Claude only reads sales.md.
+
+Similarly, for skills supporting multiple frameworks or variants, organize by variant:
+
+```
+cloud-deploy/
+├── SKILL.md (workflow + provider selection)
+└── references/
+    ├── aws.md (AWS deployment patterns)
+    ├── gcp.md (GCP deployment patterns)
+    └── azure.md (Azure deployment patterns)
+```
+
+When the user chooses AWS, Claude only reads aws.md.
+
+**Pattern 3: Conditional details**
+
+Show basic content, link to advanced content:
+
+```markdown
+# DOCX Processing
+
+## Creating documents
+
+Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).
+
+## Editing documents
+
+For simple edits, modify the XML directly.
+
+**For tracked changes**: See [REDLINING.md](REDLINING.md)
+**For OOXML details**: See [OOXML.md](OOXML.md)
+```
+
+Claude reads REDLINING.md or OOXML.md only when the user needs those features.
+
+**Important guidelines:**
+
+- **Avoid deeply nested references** - Keep references one level deep from SKILL.md. All reference files should link directly from SKILL.md.
+- **Structure longer reference files** - For files longer than 100 lines, include a table of contents at the top so Claude can see the full scope when previewing.
+
+## Skill Creation Process
+
+Skill creation involves these steps:
+
+1. Understand the skill with concrete examples
+2. Plan reusable skill contents (scripts, references, assets)
+3. Initialize the skill (run init_skill.py)
+4. Edit the skill (implement resources and write SKILL.md)
+5. Package the skill (run package_skill.py)
+6. Iterate based on real usage
+
+Follow these steps in order, skipping only if there is a clear reason why they are not applicable.
+
+### Step 1: Understanding the Skill with Concrete Examples
+
+Skip this step only when the skill's usage patterns are already clearly understood. It remains valuable even when working with an existing skill.
+
+To create an effective skill, clearly understand concrete examples of how the skill will be used. This understanding can come from either direct user examples or generated examples that are validated with user feedback.
+
+For example, when building an image-editor skill, relevant questions include:
+
+- "What functionality should the image-editor skill support? Editing, rotating, anything else?"
+- "Can you give some examples of how this skill would be used?"
+- "I can imagine users asking for things like 'Remove the red-eye from this image' or 'Rotate this image'. Are there other ways you imagine this skill being used?"
+- "What would a user say that should trigger this skill?"
+
+To avoid overwhelming users, avoid asking too many questions in a single message. Start with the most important questions and follow up as needed for better effectiveness.
+
+Conclude this step when there is a clear sense of the functionality the skill should support.
+
+### Step 2: Planning the Reusable Skill Contents
+
+To turn concrete examples into an effective skill, analyze each example by:
+
+1. Considering how to execute on the example from scratch
+2. Identifying what scripts, references, and assets would be helpful when executing these workflows repeatedly
+
+Example: When building a `pdf-editor` skill to handle queries like "Help me rotate this PDF," the analysis shows:
+
+1. Rotating a PDF requires re-writing the same code each time
+2. A `scripts/rotate_pdf.py` script would be helpful to store in the skill
+
+Example: When designing a `frontend-webapp-builder` skill for queries like "Build me a todo app" or "Build me a dashboard to track my steps," the analysis shows:
+
+1. Writing a frontend webapp requires the same boilerplate HTML/React each time
+2. An `assets/hello-world/` template containing the boilerplate HTML/React project files would be helpful to store in the skill
+
+Example: When building a `big-query` skill to handle queries like "How many users have logged in today?" the analysis shows:
+
+1. Querying BigQuery requires re-discovering the table schemas and relationships each time
+2. A `references/schema.md` file documenting the table schemas would be helpful to store in the skill
+
+To establish the skill's contents, analyze each concrete example to create a list of the reusable resources to include: scripts, references, and assets.
+
+### Step 3: Initializing the Skill
+
+At this point, it is time to actually create the skill.
+
+Skip this step only if the skill being developed already exists, and iteration or packaging is needed. In this case, continue to the next step.
+
+When creating a new skill from scratch, always run the `init_skill.py` script. The script conveniently generates a new template skill directory that automatically includes everything a skill requires, making the skill creation process much more efficient and reliable.
+
+Usage:
+
+```bash
+scripts/init_skill.py <skill-name> --path <output-directory>
+```
+
+The script:
+
+- Creates the skill directory at the specified path
+- Generates a SKILL.md template with proper frontmatter and TODO placeholders
+- Creates example resource directories: `scripts/`, `references/`, and `assets/`
+- Adds example files in each directory that can be customized or deleted
+
+After initialization, customize or remove the generated SKILL.md and example files as needed.
+
+### Step 4: Edit the Skill
+
+When editing the (newly-generated or existing) skill, remember that the skill is being created for another instance of Claude to use. Include information that would be beneficial and non-obvious to Claude. Consider what procedural knowledge, domain-specific details, or reusable assets would help another Claude instance execute these tasks more effectively.
+
+#### Learn Proven Design Patterns
+
+Consult these helpful guides based on your skill's needs:
+
+- **Multi-step processes**: See references/workflows.md for sequential workflows and conditional logic
+- **Specific output formats or quality standards**: See references/output-patterns.md for template and example patterns
+
+These files contain established best practices for effective skill design.
+
+#### Start with Reusable Skill Contents
+
+To begin implementation, start with the reusable resources identified above: `scripts/`, `references/`, and `assets/` files. Note that this step may require user input. For example, when implementing a `brand-guidelines` skill, the user may need to provide brand assets or templates to store in `assets/`, or documentation to store in `references/`.
+
+Added scripts must be tested by actually running them to ensure there are no bugs and that the output matches what is expected. If there are many similar scripts, only a representative sample needs to be tested to ensure confidence that they all work while balancing time to completion.
+
+Any example files and directories not needed for the skill should be deleted. The initialization script creates example files in `scripts/`, `references/`, and `assets/` to demonstrate structure, but most skills won't need all of them.
+
+#### Update SKILL.md
+
+**Writing Guidelines:** Always use imperative/infinitive form.
+
+##### Frontmatter
+
+Write the YAML frontmatter with `name` and `description`:
+
+- `name`: The skill name
+- `description`: This is the primary triggering mechanism for your skill, and helps Claude understand when to use the skill.
+  - Include both what the Skill does and specific triggers/contexts for when to use it.
+  - Include all "when to use" information here - Not in the body. The body is only loaded after triggering, so "When to Use This Skill" sections in the body are not helpful to Claude.
+  - Example description for a `docx` skill: "Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. Use when Claude needs to work with professional documents (.docx files) for: (1) Creating new documents, (2) Modifying or editing content, (3) Working with tracked changes, (4) Adding comments, or any other document tasks"
+
+Do not include any other fields in YAML frontmatter.
+
+##### Body
+
+Write instructions for using the skill and its bundled resources.
+
+### Step 5: Packaging a Skill
+
+Once development of the skill is complete, it must be packaged into a distributable .skill file that gets shared with the user. The packaging process automatically validates the skill first to ensure it meets all requirements:
+
+```bash
+scripts/package_skill.py <path/to/skill-folder>
+```
+
+Optional output directory specification:
+
+```bash
+scripts/package_skill.py <path/to/skill-folder> ./dist
+```
+
+The packaging script will:
+
+1. **Validate** the skill automatically, checking:
+
+   - YAML frontmatter format and required fields
+   - Skill naming conventions and directory structure
+   - Description completeness and quality
+   - File organization and resource references
+
+2. **Package** the skill if validation passes, creating a .skill file named after the skill (e.g., `my-skill.skill`) that includes all files and maintains the proper directory structure for distribution. The .skill file is a zip file with a .skill extension.
+
+If validation fails, the script will report the errors and exit without creating a package. Fix any validation errors and run the packaging command again.
+
+### Step 6: Iterate
+
+After testing the skill, users may request improvements. Often this happens right after using the skill, with fresh context of how the skill performed.
+
+**Iteration workflow:**
+
+1. Use the skill on real tasks
+2. Notice struggles or inefficiencies
+3. Identify how SKILL.md or bundled resources should be updated
+4. Implement changes and test again
diff --git a/slack-gif-creator/SKILL.md b/slack-gif-creator/SKILL.md
@@ -0,0 +1,254 @@
+---
+name: slack-gif-creator
+description: Knowledge and utilities for creating animated GIFs optimized for Slack. Provides constraints, validation tools, and animation concepts. Use when users request animated GIFs for Slack like "make me a GIF of X doing Y for Slack."
+license: Complete terms in LICENSE.txt
+---
+
+# Slack GIF Creator
+
+A toolkit providing utilities and knowledge for creating animated GIFs optimized for Slack.
+
+## Slack Requirements
+
+**Dimensions:**
+- Emoji GIFs: 128x128 (recommended)
+- Message GIFs: 480x480
+
+**Parameters:**
+- FPS: 10-30 (lower is smaller file size)
+- Colors: 48-128 (fewer = smaller file size)
+- Duration: Keep under 3 seconds for emoji GIFs
+
+## Core Workflow
+
+```python
+from core.gif_builder import GIFBuilder
+from PIL import Image, ImageDraw
+
+# 1. Create builder
+builder = GIFBuilder(width=128, height=128, fps=10)
+
+# 2. Generate frames
+for i in range(12):
+    frame = Image.new('RGB', (128, 128), (240, 248, 255))
+    draw = ImageDraw.Draw(frame)
+
+    # Draw your animation using PIL primitives
+    # (circles, polygons, lines, etc.)
+
+    builder.add_frame(frame)
+
+# 3. Save with optimization
+builder.save('output.gif', num_colors=48, optimize_for_emoji=True)
+```
+
+## Drawing Graphics
+
+### Working with User-Uploaded Images
+If a user uploads an image, consider whether they want to:
+- **Use it directly** (e.g., "animate this", "split this into frames")
+- **Use it as inspiration** (e.g., "make something like this")
+
+Load and work with images using PIL:
+```python
+from PIL import Image
+
+uploaded = Image.open('file.png')
+# Use directly, or just as reference for colors/style
+```
+
+### Drawing from Scratch
+When drawing graphics from scratch, use PIL ImageDraw primitives:
+
+```python
+from PIL import ImageDraw
+
+draw = ImageDraw.Draw(frame)
+
+# Circles/ovals
+draw.ellipse([x1, y1, x2, y2], fill=(r, g, b), outline=(r, g, b), width=3)
+
+# Stars, triangles, any polygon
+points = [(x1, y1), (x2, y2), (x3, y3), ...]
+draw.polygon(points, fill=(r, g, b), outline=(r, g, b), width=3)
+
+# Lines
+draw.line([(x1, y1), (x2, y2)], fill=(r, g, b), width=5)
+
+# Rectangles
+draw.rectangle([x1, y1, x2, y2], fill=(r, g, b), outline=(r, g, b), width=3)
+```
+
+**Don't use:** Emoji fonts (unreliable across platforms) or assume pre-packaged graphics exist in this skill.
+
+### Making Graphics Look Good
+
+Graphics should look polished and creative, not basic. Here's how:
+
+**Use thicker lines** - Always set `width=2` or higher for outlines and lines. Thin lines (width=1) look choppy and amateurish.
+
+**Add visual depth**:
+- Use gradients for backgrounds (`create_gradient_background`)
+- Layer multiple shapes for complexity (e.g., a star with a smaller star inside)
+
+**Make shapes more interesting**:
+- Don't just draw a plain circle - add highlights, rings, or patterns
+- Stars can have glows (draw larger, semi-transparent versions behind)
+- Combine multiple shapes (stars + sparkles, circles + rings)
+
+**Pay attention to colors**:
+- Use vibrant, complementary colors
+- Add contrast (dark outlines on light shapes, light outlines on dark shapes)
+- Consider the overall composition
+
+**For complex shapes** (hearts, snowflakes, etc.):
+- Use combinations of polygons and ellipses
+- Calculate points carefully for symmetry
+- Add details (a heart can have a highlight curve, snowflakes have intricate branches)
+
+Be creative and detailed! A good Slack GIF should look polished, not like placeholder graphics.
+
+## Available Utilities
+
+### GIFBuilder (`core.gif_builder`)
+Assembles frames and optimizes for Slack:
+```python
+builder = GIFBuilder(width=128, height=128, fps=10)
+builder.add_frame(frame)  # Add PIL Image
+builder.add_frames(frames)  # Add list of frames
+builder.save('out.gif', num_colors=48, optimize_for_emoji=True, remove_duplicates=True)
+```
+
+### Validators (`core.validators`)
+Check if GIF meets Slack requirements:
+```python
+from core.validators import validate_gif, is_slack_ready
+
+# Detailed validation
+passes, info = validate_gif('my.gif', is_emoji=True, verbose=True)
+
+# Quick check
+if is_slack_ready('my.gif'):
+    print("Ready!")
+```
+
+### Easing Functions (`core.easing`)
+Smooth motion instead of linear:
+```python
+from core.easing import interpolate
+
+# Progress from 0.0 to 1.0
+t = i / (num_frames - 1)
+
+# Apply easing
+y = interpolate(start=0, end=400, t=t, easing='ease_out')
+
+# Available: linear, ease_in, ease_out, ease_in_out,
+#           bounce_out, elastic_out, back_out
+```
+
+### Frame Helpers (`core.frame_composer`)
+Convenience functions for common needs:
+```python
+from core.frame_composer import (
+    create_blank_frame,         # Solid color background
+    create_gradient_background,  # Vertical gradient
+    draw_circle,                # Helper for circles
+    draw_text,                  # Simple text rendering
+    draw_star                   # 5-pointed star
+)
+```
+
+## Animation Concepts
+
+### Shake/Vibrate
+Offset object position with oscillation:
+- Use `math.sin()` or `math.cos()` with frame index
+- Add small random variations for natural feel
+- Apply to x and/or y position
+
+### Pulse/Heartbeat
+Scale object size rhythmically:
+- Use `math.sin(t * frequency * 2 * math.pi)` for smooth pulse
+- For heartbeat: two quick pulses then pause (adjust sine wave)
+- Scale between 0.8 and 1.2 of base size
+
+### Bounce
+Object falls and bounces:
+- Use `interpolate()` with `easing='bounce_out'` for landing
+- Use `easing='ease_in'` for falling (accelerating)
+- Apply gravity by increasing y velocity each frame
+
+### Spin/Rotate
+Rotate object around center:
+- PIL: `image.rotate(angle, resample=Image.BICUBIC)`
+- For wobble: use sine wave for angle instead of linear
+
+### Fade In/Out
+Gradually appear or disappear:
+- Create RGBA image, adjust alpha channel
+- Or use `Image.blend(image1, image2, alpha)`
+- Fade in: alpha from 0 to 1
+- Fade out: alpha from 1 to 0
+
+### Slide
+Move object from off-screen to position:
+- Start position: outside frame bounds
+- End position: target location
+- Use `interpolate()` with `easing='ease_out'` for smooth stop
+- For overshoot: use `easing='back_out'`
+
+### Zoom
+Scale and position for zoom effect:
+- Zoom in: scale from 0.1 to 2.0, crop center
+- Zoom out: scale from 2.0 to 1.0
+- Can add motion blur for drama (PIL filter)
+
+### Explode/Particle Burst
+Create particles radiating outward:
+- Generate particles with random angles and velocities
+- Update each particle: `x += vx`, `y += vy`
+- Add gravity: `vy += gravity_constant`
+- Fade out particles over time (reduce alpha)
+
+## Optimization Strategies
+
+Only when asked to make the file size smaller, implement a few of the following methods:
+
+1. **Fewer frames** - Lower FPS (10 instead of 20) or shorter duration
+2. **Fewer colors** - `num_colors=48` instead of 128
+3. **Smaller dimensions** - 128x128 instead of 480x480
+4. **Remove duplicates** - `remove_duplicates=True` in save()
+5. **Emoji mode** - `optimize_for_emoji=True` auto-optimizes
+
+```python
+# Maximum optimization for emoji
+builder.save(
+    'emoji.gif',
+    num_colors=48,
+    optimize_for_emoji=True,
+    remove_duplicates=True
+)
+```
+
+## Philosophy
+
+This skill provides:
+- **Knowledge**: Slack's requirements and animation concepts
+- **Utilities**: GIFBuilder, validators, easing functions
+- **Flexibility**: Create the animation logic using PIL primitives
+
+It does NOT provide:
+- Rigid animation templates or pre-made functions
+- Emoji font rendering (unreliable across platforms)
+- A library of pre-packaged graphics built into the skill
+
+**Note on user uploads**: This skill doesn't include pre-built graphics, but if a user uploads an image, use PIL to load and work with it - interpret based on their request whether they want it used directly or just as inspiration.
+
+Be creative! Combine concepts (bouncing + rotating, pulsing + sliding, etc.) and use PIL's full capabilities.
+
+## Dependencies
+
+```bash
+pip install pillow imageio numpy
+```
diff --git a/template-skill/SKILL.md b/template-skill/SKILL.md
@@ -0,0 +1,6 @@
+---
+name: template-skill
+description: Replace with description of the skill and when Claude should use it.
+---
+
+# Insert instructions below
diff --git a/theme-factory/SKILL.md b/theme-factory/SKILL.md
@@ -0,0 +1,59 @@
+---
+name: theme-factory
+description: Toolkit for styling artifacts with a theme. These artifacts can be slides, docs, reportings, HTML landing pages, etc. There are 10 pre-set themes with colors/fonts that you can apply to any artifact that has been creating, or can generate a new theme on-the-fly.
+license: Complete terms in LICENSE.txt
+---
+
+
+# Theme Factory Skill
+
+This skill provides a curated collection of professional font and color themes themes, each with carefully selected color palettes and font pairings. Once a theme is chosen, it can be applied to any artifact.
+
+## Purpose
+
+To apply consistent, professional styling to presentation slide decks, use this skill. Each theme includes:
+- A cohesive color palette with hex codes
+- Complementary font pairings for headers and body text
+- A distinct visual identity suitable for different contexts and audiences
+
+## Usage Instructions
+
+To apply styling to a slide deck or other artifact:
+
+1. **Show the theme showcase**: Display the `theme-showcase.pdf` file to allow users to see all available themes visually. Do not make any modifications to it; simply show the file for viewing.
+2. **Ask for their choice**: Ask which theme to apply to the deck
+3. **Wait for selection**: Get explicit confirmation about the chosen theme
+4. **Apply the theme**: Once a theme has been chosen, apply the selected theme's colors and fonts to the deck/artifact
+
+## Themes Available
+
+The following 10 themes are available, each showcased in `theme-showcase.pdf`:
+
+1. **Ocean Depths** - Professional and calming maritime theme
+2. **Sunset Boulevard** - Warm and vibrant sunset colors
+3. **Forest Canopy** - Natural and grounded earth tones
+4. **Modern Minimalist** - Clean and contemporary grayscale
+5. **Golden Hour** - Rich and warm autumnal palette
+6. **Arctic Frost** - Cool and crisp winter-inspired theme
+7. **Desert Rose** - Soft and sophisticated dusty tones
+8. **Tech Innovation** - Bold and modern tech aesthetic
+9. **Botanical Garden** - Fresh and organic garden colors
+10. **Midnight Galaxy** - Dramatic and cosmic deep tones
+
+## Theme Details
+
+Each theme is defined in the `themes/` directory with complete specifications including:
+- Cohesive color palette with hex codes
+- Complementary font pairings for headers and body text
+- Distinct visual identity suitable for different contexts and audiences
+
+## Application Process
+
+After a preferred theme is selected:
+1. Read the corresponding theme file from the `themes/` directory
+2. Apply the specified colors and fonts consistently throughout the deck
+3. Ensure proper contrast and readability
+4. Maintain the theme's visual identity across all slides
+
+## Create your Own Theme
+To handle cases where none of the existing themes work for an artifact, create a custom theme. Based on provided inputs, generate a new theme similar to the ones above. Give the theme a similar name describing what the font/color combinations represent. Use any basic description provided to choose appropriate colors/fonts. After generating the theme, show it for review and verification. Following that, apply the theme as described above.
diff --git a/webapp-testing/SKILL.md b/webapp-testing/SKILL.md
@@ -0,0 +1,96 @@
+---
+name: webapp-testing
+description: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.
+license: Complete terms in LICENSE.txt
+---
+
+# Web Application Testing
+
+To test local web applications, write native Python Playwright scripts.
+
+**Helper Scripts Available**:
+- `scripts/with_server.py` - Manages server lifecycle (supports multiple servers)
+
+**Always run scripts with `--help` first** to see usage. DO NOT read the source until you try running the script first and find that a customized solution is abslutely necessary. These scripts can be very large and thus pollute your context window. They exist to be called directly as black-box scripts rather than ingested into your context window.
+
+## Decision Tree: Choosing Your Approach
+
+```
+User task → Is it static HTML?
+    ├─ Yes → Read HTML file directly to identify selectors
+    │         ├─ Success → Write Playwright script using selectors
+    │         └─ Fails/Incomplete → Treat as dynamic (below)
+    │
+    └─ No (dynamic webapp) → Is the server already running?
+        ├─ No → Run: python scripts/with_server.py --help
+        │        Then use the helper + write simplified Playwright script
+        │
+        └─ Yes → Reconnaissance-then-action:
+            1. Navigate and wait for networkidle
+            2. Take screenshot or inspect DOM
+            3. Identify selectors from rendered state
+            4. Execute actions with discovered selectors
+```
+
+## Example: Using with_server.py
+
+To start a server, run `--help` first, then use the helper:
+
+**Single server:**
+```bash
+python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
+```
+
+**Multiple servers (e.g., backend + frontend):**
+```bash
+python scripts/with_server.py \
+  --server "cd backend && python server.py" --port 3000 \
+  --server "cd frontend && npm run dev" --port 5173 \
+  -- python your_automation.py
+```
+
+To create an automation script, include only Playwright logic (servers are managed automatically):
+```python
+from playwright.sync_api import sync_playwright
+
+with sync_playwright() as p:
+    browser = p.chromium.launch(headless=True) # Always launch chromium in headless mode
+    page = browser.new_page()
+    page.goto('http://localhost:5173') # Server already running and ready
+    page.wait_for_load_state('networkidle') # CRITICAL: Wait for JS to execute
+    # ... your automation logic
+    browser.close()
+```
+
+## Reconnaissance-Then-Action Pattern
+
+1. **Inspect rendered DOM**:
+   ```python
+   page.screenshot(path='/tmp/inspect.png', full_page=True)
+   content = page.content()
+   page.locator('button').all()
+   ```
+
+2. **Identify selectors** from inspection results
+
+3. **Execute actions** using discovered selectors
+
+## Common Pitfall
+
+❌ **Don't** inspect the DOM before waiting for `networkidle` on dynamic apps
+✅ **Do** wait for `page.wait_for_load_state('networkidle')` before inspection
+
+## Best Practices
+
+- **Use bundled scripts as black boxes** - To accomplish a task, consider whether one of the scripts available in `scripts/` can help. These scripts handle common, complex workflows reliably without cluttering the context window. Use `--help` to see usage, then invoke directly. 
+- Use `sync_playwright()` for synchronous scripts
+- Always close the browser when done
+- Use descriptive selectors: `text=`, `role=`, CSS selectors, or IDs
+- Add appropriate waits: `page.wait_for_selector()` or `page.wait_for_timeout()`
+
+## Reference Files
+
+- **examples/** - Examples showing common patterns:
+  - `element_discovery.py` - Discovering buttons, links, and inputs on a page
+  - `static_html_automation.py` - Using file:// URLs for local HTML
+  - `console_logging.py` - Capturing console logs during automation
\ No newline at end of file
diff --git a/xlsx/SKILL.md b/xlsx/SKILL.md
@@ -0,0 +1,289 @@
+---
+name: xlsx
+description: "Comprehensive spreadsheet creation, editing, and analysis with support for formulas, formatting, data analysis, and visualization. When Claude needs to work with spreadsheets (.xlsx, .xlsm, .csv, .tsv, etc) for: (1) Creating new spreadsheets with formulas and formatting, (2) Reading or analyzing data, (3) Modify existing spreadsheets while preserving formulas, (4) Data analysis and visualization in spreadsheets, or (5) Recalculating formulas"
+license: Proprietary. LICENSE.txt has complete terms
+---
+
+# Requirements for Outputs
+
+## All Excel files
+
+### Zero Formula Errors
+- Every Excel model MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)
+
+### Preserve Existing Templates (when updating templates)
+- Study and EXACTLY match existing format, style, and conventions when modifying files
+- Never impose standardized formatting on files with established patterns
+- Existing template conventions ALWAYS override these guidelines
+
+## Financial models
+
+### Color Coding Standards
+Unless otherwise stated by the user or existing template
+
+#### Industry-Standard Color Conventions
+- **Blue text (RGB: 0,0,255)**: Hardcoded inputs, and numbers users will change for scenarios
+- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
+- **Green text (RGB: 0,128,0)**: Links pulling from other worksheets within same workbook
+- **Red text (RGB: 255,0,0)**: External links to other files
+- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention or cells that need to be updated
+
+### Number Formatting Standards
+
+#### Required Format Rules
+- **Years**: Format as text strings (e.g., "2024" not "2,024")
+- **Currency**: Use $#,##0 format; ALWAYS specify units in headers ("Revenue ($mm)")
+- **Zeros**: Use number formatting to make all zeros "-", including percentages (e.g., "$#,##0;($#,##0);-")
+- **Percentages**: Default to 0.0% format (one decimal)
+- **Multiples**: Format as 0.0x for valuation multiples (EV/EBITDA, P/E)
+- **Negative numbers**: Use parentheses (123) not minus -123
+
+### Formula Construction Rules
+
+#### Assumptions Placement
+- Place ALL assumptions (growth rates, margins, multiples, etc.) in separate assumption cells
+- Use cell references instead of hardcoded values in formulas
+- Example: Use =B5*(1+$B$6) instead of =B5*1.05
+
+#### Formula Error Prevention
+- Verify all cell references are correct
+- Check for off-by-one errors in ranges
+- Ensure consistent formulas across all projection periods
+- Test with edge cases (zero values, negative numbers)
+- Verify no unintended circular references
+
+#### Documentation Requirements for Hardcodes
+- Comment or in cells beside (if end of table). Format: "Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"
+- Examples:
+  - "Source: Company 10-K, FY2024, Page 45, Revenue Note, [SEC EDGAR URL]"
+  - "Source: Company 10-Q, Q2 2025, Exhibit 99.1, [SEC EDGAR URL]"
+  - "Source: Bloomberg Terminal, 8/15/2025, AAPL US Equity"
+  - "Source: FactSet, 8/20/2025, Consensus Estimates Screen"
+
+# XLSX creation, editing, and analysis
+
+## Overview
+
+A user may ask you to create, edit, or analyze the contents of an .xlsx file. You have different tools and workflows available for different tasks.
+
+## Important Requirements
+
+**LibreOffice Required for Formula Recalculation**: You can assume LibreOffice is installed for recalculating formula values using the `recalc.py` script. The script automatically configures LibreOffice on first run
+
+## Reading and analyzing data
+
+### Data analysis with pandas
+For data analysis, visualization, and basic operations, use **pandas** which provides powerful data manipulation capabilities:
+
+```python
+import pandas as pd
+
+# Read Excel
+df = pd.read_excel('file.xlsx')  # Default: first sheet
+all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets as dict
+
+# Analyze
+df.head()      # Preview data
+df.info()      # Column info
+df.describe()  # Statistics
+
+# Write Excel
+df.to_excel('output.xlsx', index=False)
+```
+
+## Excel File Workflows
+
+## CRITICAL: Use Formulas, Not Hardcoded Values
+
+**Always use Excel formulas instead of calculating values in Python and hardcoding them.** This ensures the spreadsheet remains dynamic and updateable.
+
+### ❌ WRONG - Hardcoding Calculated Values
+```python
+# Bad: Calculating in Python and hardcoding result
+total = df['Sales'].sum()
+sheet['B10'] = total  # Hardcodes 5000
+
+# Bad: Computing growth rate in Python
+growth = (df.iloc[-1]['Revenue'] - df.iloc[0]['Revenue']) / df.iloc[0]['Revenue']
+sheet['C5'] = growth  # Hardcodes 0.15
+
+# Bad: Python calculation for average
+avg = sum(values) / len(values)
+sheet['D20'] = avg  # Hardcodes 42.5
+```
+
+### ✅ CORRECT - Using Excel Formulas
+```python
+# Good: Let Excel calculate the sum
+sheet['B10'] = '=SUM(B2:B9)'
+
+# Good: Growth rate as Excel formula
+sheet['C5'] = '=(C4-C2)/C2'
+
+# Good: Average using Excel function
+sheet['D20'] = '=AVERAGE(D2:D19)'
+```
+
+This applies to ALL calculations - totals, percentages, ratios, differences, etc. The spreadsheet should be able to recalculate when source data changes.
+
+## Common Workflow
+1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
+2. **Create/Load**: Create new workbook or load existing file
+3. **Modify**: Add/edit data, formulas, and formatting
+4. **Save**: Write to file
+5. **Recalculate formulas (MANDATORY IF USING FORMULAS)**: Use the recalc.py script
+   ```bash
+   python recalc.py output.xlsx
+   ```
+6. **Verify and fix any errors**: 
+   - The script returns JSON with error details
+   - If `status` is `errors_found`, check `error_summary` for specific error types and locations
+   - Fix the identified errors and recalculate again
+   - Common errors to fix:
+     - `#REF!`: Invalid cell references
+     - `#DIV/0!`: Division by zero
+     - `#VALUE!`: Wrong data type in formula
+     - `#NAME?`: Unrecognized formula name
+
+### Creating new Excel files
+
+```python
+# Using openpyxl for formulas and formatting
+from openpyxl import Workbook
+from openpyxl.styles import Font, PatternFill, Alignment
+
+wb = Workbook()
+sheet = wb.active
+
+# Add data
+sheet['A1'] = 'Hello'
+sheet['B1'] = 'World'
+sheet.append(['Row', 'of', 'data'])
+
+# Add formula
+sheet['B2'] = '=SUM(A1:A10)'
+
+# Formatting
+sheet['A1'].font = Font(bold=True, color='FF0000')
+sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')
+sheet['A1'].alignment = Alignment(horizontal='center')
+
+# Column width
+sheet.column_dimensions['A'].width = 20
+
+wb.save('output.xlsx')
+```
+
+### Editing existing Excel files
+
+```python
+# Using openpyxl to preserve formulas and formatting
+from openpyxl import load_workbook
+
+# Load existing file
+wb = load_workbook('existing.xlsx')
+sheet = wb.active  # or wb['SheetName'] for specific sheet
+
+# Working with multiple sheets
+for sheet_name in wb.sheetnames:
+    sheet = wb[sheet_name]
+    print(f"Sheet: {sheet_name}")
+
+# Modify cells
+sheet['A1'] = 'New Value'
+sheet.insert_rows(2)  # Insert row at position 2
+sheet.delete_cols(3)  # Delete column 3
+
+# Add new sheet
+new_sheet = wb.create_sheet('NewSheet')
+new_sheet['A1'] = 'Data'
+
+wb.save('modified.xlsx')
+```
+
+## Recalculating formulas
+
+Excel files created or modified by openpyxl contain formulas as strings but not calculated values. Use the provided `recalc.py` script to recalculate formulas:
+
+```bash
+python recalc.py <excel_file> [timeout_seconds]
+```
+
+Example:
+```bash
+python recalc.py output.xlsx 30
+```
+
+The script:
+- Automatically sets up LibreOffice macro on first run
+- Recalculates all formulas in all sheets
+- Scans ALL cells for Excel errors (#REF!, #DIV/0!, etc.)
+- Returns JSON with detailed error locations and counts
+- Works on both Linux and macOS
+
+## Formula Verification Checklist
+
+Quick checks to ensure formulas work correctly:
+
+### Essential Verification
+- [ ] **Test 2-3 sample references**: Verify they pull correct values before building full model
+- [ ] **Column mapping**: Confirm Excel columns match (e.g., column 64 = BL, not BK)
+- [ ] **Row offset**: Remember Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
+
+### Common Pitfalls
+- [ ] **NaN handling**: Check for null values with `pd.notna()`
+- [ ] **Far-right columns**: FY data often in columns 50+ 
+- [ ] **Multiple matches**: Search all occurrences, not just first
+- [ ] **Division by zero**: Check denominators before using `/` in formulas (#DIV/0!)
+- [ ] **Wrong references**: Verify all cell references point to intended cells (#REF!)
+- [ ] **Cross-sheet references**: Use correct format (Sheet1!A1) for linking sheets
+
+### Formula Testing Strategy
+- [ ] **Start small**: Test formulas on 2-3 cells before applying broadly
+- [ ] **Verify dependencies**: Check all cells referenced in formulas exist
+- [ ] **Test edge cases**: Include zero, negative, and very large values
+
+### Interpreting recalc.py Output
+The script returns JSON with error details:
+```json
+{
+  "status": "success",           // or "errors_found"
+  "total_errors": 0,              // Total error count
+  "total_formulas": 42,           // Number of formulas in file
+  "error_summary": {              // Only present if errors found
+    "#REF!": {
+      "count": 2,
+      "locations": ["Sheet1!B5", "Sheet1!C10"]
+    }
+  }
+}
+```
+
+## Best Practices
+
+### Library Selection
+- **pandas**: Best for data analysis, bulk operations, and simple data export
+- **openpyxl**: Best for complex formatting, formulas, and Excel-specific features
+
+### Working with openpyxl
+- Cell indices are 1-based (row=1, column=1 refers to cell A1)
+- Use `data_only=True` to read calculated values: `load_workbook('file.xlsx', data_only=True)`
+- **Warning**: If opened with `data_only=True` and saved, formulas are replaced with values and permanently lost
+- For large files: Use `read_only=True` for reading or `write_only=True` for writing
+- Formulas are preserved but not evaluated - use recalc.py to update values
+
+### Working with pandas
+- Specify data types to avoid inference issues: `pd.read_excel('file.xlsx', dtype={'id': str})`
+- For large files, read specific columns: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
+- Handle dates properly: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`
+
+## Code Style Guidelines
+**IMPORTANT**: When generating Python code for Excel operations:
+- Write minimal, concise Python code without unnecessary comments
+- Avoid verbose variable names and redundant operations
+- Avoid unnecessary print statements
+
+**For Excel files themselves**:
+- Add comments to cells with complex formulas or important assumptions
+- Document data sources for hardcoded values
+- Include notes for key calculations and model sections
\ No newline at end of file
PATCH

echo "Gold patch applied."
