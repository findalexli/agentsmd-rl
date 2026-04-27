#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-skills

# Idempotency guard
if grep -qF "- Do not send sensitive source documents to third-party services unless the user" "skills/elegant-reports/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/elegant-reports/SKILL.md b/skills/elegant-reports/SKILL.md
@@ -1,42 +1,53 @@
 ---
 name: elegant-reports
 description: Generate beautifully designed PDF reports with a Nordic/Scandinavian aesthetic. Use when creating polished executive briefings, analysis reports, or presentation-style PDF outputs from markdown and HTML via Nutrient DWS.
+metadata: {"clawdbot":{"requires":{"bins":["node","npm"]}}}
+permissions:
+  - exec: "Runs the local Node generator to list templates, render preview HTML, and create PDF outputs when the user asks."
+  - file_read: "Reads bundled templates, themes, examples, and design references inside the skill directory plus user-approved input markdown files."
+  - file_write: "Writes generated HTML/PDF outputs and user-requested template or theme files inside approved working directories."
+  - network: "Calls Nutrient DWS and any hosted font assets used by the bundled templates when the user requests report generation."
 ---
 
 # elegant-reports
 
-Generate minimalist, elegant PDF reports inspired by Scandinavian design principles.
+Generate minimalist PDF reports inspired by Scandinavian editorial design.
 
-## Quick Start
-
-```bash
-cd /path/to/elegant-reports
+## When to Use
 
-# Generate a report (dense layout)
-node generate.js report.md output.pdf --template report
+Use this skill when the user wants:
+- polished executive briefings or board-style reports
+- presentation-like PDFs generated from markdown
+- a clean Nordic visual language instead of default developer styling
+- a reusable report template system that can be extended carefully
 
-# Generate a presentation (bold slides)
-node generate.js data.md slides.pdf --template presentation
+## Quick Start
 
-# Dark mode
-node generate.js report.md --template report --theme dark
+Install the pinned dependencies from `package-lock.json`, then run:
 
-# List templates
-node generate.js --list
+```bash
+cd /path/to/elegant-reports
+node ./generate.js --list
+node ./generate.js examples/sample-executive.md output.pdf --template executive --theme light
 ```
 
-## Templates
+For HTML debugging, add `--output-html` so the generator saves the rendered HTML alongside the PDF.
+
+## Available Templates
 
-| Template | Style | Use Case |
-|----------|-------|----------|
-| `report` | Dense, multi-column | Deep dives, analysis, competitive intel |
-| `presentation` | Big & bold, one idea/page | Exec briefings, board decks |
+| Template | Use Case |
+|----------|----------|
+| `executive` | polished briefings and compact executive summaries |
+| `report` | denser narrative reports and analysis writeups |
+| `presentation` | bold slide-like outputs with one idea per page |
+| `report-demo` | legacy report variant for comparison/testing |
+| `presentation-demo` | legacy presentation variant for comparison/testing |
 
-Each template supports `--theme light` (default) or `--theme dark`.
+Each template supports `light` and `dark` themes where available.
 
 ## Frontmatter
 
-Add YAML frontmatter to control output:
+Add YAML frontmatter to control the rendered output:
 
 ```markdown
 ---
@@ -50,331 +61,51 @@ theme: dark
 Your content here...
 ```
 
-## Design Philosophy
-
-Based on Nordic/Scandinavian design principles:
-- **Bold typography** — Poppins for headlines, Inter for body
-- **High contrast** — Dark headers, clear hierarchy
-- **Generous whitespace** — Content breathes
-- **One accent color** — Blue (#2563EB) used sparingly
-- **Functional beauty** — Form follows function
-
-See `references/nordic-design-research.md` for complete design documentation.
-
----
-
-# Creating New Templates
-
-## The Visual Iteration Workflow
-
-This is how to create new templates with visual feedback:
-
-### Step 1: Research References
-
-```bash
-# Use browser tool to study design examples
-browser navigate https://www.canva.com/templates/...
-browser screenshot
-
-# Look for:
-# - Typography choices (font, size, weight)
-# - Color palette (backgrounds, text, accents)
-# - Layout patterns (grids, spacing)
-# - Component styles (cards, tables, callouts)
-```
-
-### Step 2: Create Theme CSS
-
-Create a new CSS file in `themes/`:
-
-```css
-/* themes/my-theme.css */
-
-@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800&family=Inter:wght@400;500&display=swap');
-
-:root {
-  /* Color tokens */
-  --color-bg: #FAFAFA;
-  --color-surface: #FFFFFF;
-  --color-text-primary: #0A0A0A;
-  --color-text-secondary: #404040;
-  --color-accent: #2563EB;
-  
-  /* Typography tokens */
-  --font-display: 'Poppins', sans-serif;
-  --font-body: 'Inter', sans-serif;
-  
-  /* Spacing tokens */
-  --space-4: 1rem;
-  --space-6: 1.5rem;
-  --space-8: 2rem;
-}
-
-/* Component styles... */
-```
-
-### Step 3: Create Template HTML
-
-Create HTML in `templates/`:
-
-```html
-<!-- templates/my-template.html -->
-<!DOCTYPE html>
-<html lang="en">
-<head>
-  <meta charset="UTF-8">
-  <title>{{title}}</title>
-  <style>
-{{styles}}
-  </style>
-</head>
-<body>
-  <div class="page">
-    <h1>{{title}}</h1>
-    <p>{{subtitle}}</p>
-    {{content}}
-  </div>
-</body>
-</html>
-```
-
-Available variables: `{{title}}`, `{{subtitle}}`, `{{author}}`, `{{date}}`, `{{content}}`, `{{styles}}`
-
-### Step 4: Test with Visual Feedback
-
-```bash
-# Generate test HTML manually
-node -e "
-const fs = require('fs');
-const css = fs.readFileSync('themes/my-theme.css', 'utf8');
-let html = fs.readFileSync('templates/my-template.html', 'utf8');
-html = html.replace('{{styles}}', css);
-html = html.replace(/\{\{title\}\}/g, 'Test Title');
-html = html.replace(/\{\{subtitle\}\}/g, 'Test Subtitle');
-html = html.replace(/\{\{date\}\}/g, 'January 2026');
-html = html.replace(/\{\{author\}\}/g, 'Report Author');
-html = html.replace(/\{\{content\}\}/g, '<p>Test content</p>');
-fs.writeFileSync('test-output.html', html);
-"
-
-# Preview in browser
-browser navigate file://$(pwd)/test-output.html
-browser screenshot
-
-# See what's wrong, fix it, repeat
-```
-
-### Step 5: Register in Generator
-
-Add to `TEMPLATES` object in `generate.js`:
-
-```javascript
-const TEMPLATES = {
-  // ...existing templates...
-  
-  'my-template': {
-    description: 'My custom template description',
-    template: 'my-template.html',
-    themes: {
-      light: 'my-theme.css',
-      dark: 'my-theme-dark.css'
-    }
-  }
-};
-```
-
-### Step 6: Test PDF Generation
-
-```bash
-node generate.js test.md output.pdf --template my-template --output-html
-```
-
----
-
-## Design Tokens Reference
-
-### Typography Scale
-
-| Token | Size | Use |
-|-------|------|-----|
-| `--text-xs` | 11-12px | Labels, captions |
-| `--text-sm` | 13-14px | Body (dense) |
-| `--text-base` | 14-16px | Body (normal) |
-| `--text-lg` | 16-18px | Lead paragraphs |
-| `--text-xl` | 18-20px | Section headers |
-| `--text-2xl` | 20-24px | H3 |
-| `--text-3xl` | 24-32px | H2 |
-| `--text-4xl` | 32-40px | H1 (report) |
-| `--text-5xl` | 48-56px | H1 (presentation) |
-| `--text-6xl` | 64-72px | Hero text |
-
-### Spacing Scale
-
-| Token | Size | Use |
-|-------|------|-----|
-| `--space-1` | 2-4px | Tight gaps |
-| `--space-2` | 4-8px | Inline spacing |
-| `--space-3` | 8-12px | Component padding |
-| `--space-4` | 12-16px | Card padding |
-| `--space-6` | 20-24px | Section gaps |
-| `--space-8` | 28-32px | Major sections |
-| `--space-10` | 36-40px | Page sections |
-| `--space-12` | 44-48px | Page margins |
-
-### Color Palette
-
-**Light Mode:**
-```css
---color-bg: #FAFAFA;
---color-surface: #FFFFFF;
---color-text-primary: #0A0A0A;
---color-text-secondary: #404040;
---color-text-muted: #737373;
---color-accent: #2563EB;
-```
-
-**Dark Mode:**
-```css
---color-bg: #09090B;
---color-surface: #18181B;
---color-text-primary: #FAFAFA;
---color-text-secondary: #D4D4D8;
---color-text-muted: #A1A1AA;
---color-accent: #3B82F6;
-```
-
----
-
-## Component Patterns
-
-### KPI Strip (horizontal metrics)
-```html
-<div class="kpi-strip">
-  <div class="kpi-item">
-    <div class="kpi-value">$10.8M</div>
-    <div class="kpi-label">Revenue</div>
-    <div class="kpi-change positive">+12%</div>
-  </div>
-  <!-- more items -->
-</div>
-```
-
-### Key Findings Box
-```html
-<div class="key-findings">
-  <div class="key-findings-title">Key Points</div>
-  <ul>
-    <li><strong>Point 1</strong> — Details</li>
-    <li><strong>Point 2</strong> — Details</li>
-  </ul>
-</div>
-```
-
-### Two-Column Layout
-```html
-<div class="two-col">
-  <div>Left column content</div>
-  <div>Right column content</div>
-</div>
-```
-
-### Callouts
-```html
-<div class="callout callout-tip">
-  <div class="callout-title">Tip</div>
-  <p>Content here</p>
-</div>
-```
-Types: `callout-tip` (green), `callout-warning` (amber), `callout-danger` (red)
-
-### ASCII Diagrams
-
-ASCII diagrams are automatically styled with an elegant light background when using the `text`, `diagram`, or `ascii` language in fenced code blocks:
-
-~~~markdown
-```text
-┌────────────────────────────────────┐
-│         ARCHITECTURE               │
-├────────────────────────────────────┤
-│  Layer 1  │  Layer 2  │  Layer 3   │
-└────────────────────────────────────┘
-```
-~~~
-
-Features:
-- **Light paper-like background** — Clean gradient instead of dark code block
-- **Subtle border and shadow** — Elegant container styling
-- **Optimized typography** — JetBrains Mono with disabled ligatures for proper box-drawing
-- **Automatic detection** — Works with `text`, `diagram`, or `ascii` language tags
-
-Use box-drawing characters (`─`, `│`, `┌`, `┐`, `└`, `┘`, `├`, `┤`, `┬`, `┴`, `┼`) for professional-looking architecture diagrams, flowcharts, and positioning maps.
-
-### Tables with Dark Headers
-```html
-<table class="no-break">
-  <thead>
-    <tr><th>Header</th><th class="num">Value</th></tr>
-  </thead>
-  <tbody>
-    <tr><td>Row</td><td class="num">123</td></tr>
-  </tbody>
-</table>
-```
+## Workflow
 
----
-
-## Page Break Control
+1. Pick the closest existing template instead of starting from scratch.
+2. Write or refine the source markdown.
+3. Generate a PDF.
+4. If layout tuning is needed, inspect the emitted HTML with `--output-html` and adjust the corresponding template/theme pair.
+5. Re-run until the design is clean and the PDF is stable.
 
-Add these classes to prevent awkward breaks:
+## Extending the Skill
 
-```html
-<div class="no-break">This won't split across pages</div>
-<div class="page-break">Forces new page before this</div>
-```
+When authoring a new visual variant:
+- start from the nearest bundled template and theme
+- keep token names and spacing scales consistent with the existing system
+- make one visual change at a time and regenerate after each step
+- prefer additive variants over rewriting the whole design language
+- keep legacy/demo templates available until the replacement is verified
 
-Tables, cards, callouts, and KPI strips have `page-break-inside: avoid` by default.
+The bundled Nordic design research note is the canonical reference for the visual system. Read it only when you need deeper design rationale.
 
----
+## Safety Boundaries
 
-## Files Structure
-
-```
-elegant-reports/
-├── SKILL.md                    # This file
-├── references/
-│   └── nordic-design-research.md # Design principles documentation
-├── generate.js                 # Main generator script
-├── package.json
-├── themes/
-│   ├── nordic-v2.css           # Presentation light
-│   ├── nordic-report.css       # Report light
-│   └── nordic-report-dark.css  # Report dark
-├── templates/
-│   ├── executive-v2.html       # Presentation template
-│   └── report-v2.html          # Report template
-└── examples/
-    └── sample-executive.md     # Example input
-```
-
----
+- Do not send sensitive source documents to third-party services unless the user explicitly requested PDF generation through Nutrient DWS and accepts that network boundary.
+- Do not browse arbitrary local files. Limit reads to the skill bundle and user-approved input/output paths.
+- Do not overwrite or delete files outside the user-approved working directory.
+- Do not install extra packages, change dependency versions, or add new external services unless the user explicitly asks for that setup work.
+- Do not claim a report was generated successfully unless the output artifact exists and the generator completed without error.
+- Do not fetch external design inspiration or web references unless the user explicitly wants fresh visual research.
 
 ## Dependencies
 
 - Node.js 18+
-- axios, form-data (`npm install`)
-- Nutrient DWS API key available via the `NUTRIENT_DWS_API_KEY` environment variable
+- pinned npm dependencies from `package-lock.json`
+- `NUTRIENT_DWS_API_KEY` environment variable for PDF generation
 
-## API Usage
+## File Map
 
-```javascript
-const { generateReport } = require('./generate.js');
+- main generator CLI and module entrypoint
+- bundled HTML templates
+- bundled visual themes
+- sample markdown input
+- optional deeper design rationale bundled with the skill
 
-await generateReport({
-  input: 'report.md',
-  output: 'report.pdf',
-  template: 'report',
-  theme: 'dark',
-  title: 'My Report',
-  author: 'Report Author'
-});
-```
+## Validation
+
+Before calling the skill done:
+- run `node ./generate.js --list`
+- run `npm test`
+- verify the expected PDF or HTML artifact exists in the requested output path
PATCH

echo "Gold patch applied."
