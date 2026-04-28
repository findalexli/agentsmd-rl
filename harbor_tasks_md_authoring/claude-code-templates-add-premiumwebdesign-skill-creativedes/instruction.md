# Add premium-web-design skill (creative-design)

Source: [davila7/claude-code-templates#526](https://github.com/davila7/claude-code-templates/pull/526)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `cli-tool/components/skills/creative-design/premium-web-design/SKILL.md`

## What to add / change

## Summary

Adds a new skill, `premium-web-design`, under `cli-tool/components/skills/creative-design/`. It teaches Claude to produce Awwwards-quality landing pages as React (.jsx) components — the kind of work a top-tier agency billing $50k+ produces. It's a sibling to the existing `frontend-design`, `web-design-guidelines`, and `ui-design-system` skills, but opinionated specifically about *premium / editorial / luxury* aesthetics and includes a structural-uniqueness system so multiple builds in a session don't look alike.

## What the skill teaches Claude

- An **AI-aesthetic blacklist** — banned fonts (Inter, Poppins, Montserrat, etc.), banned palettes (purple-to-blue gradients), banned layouts (the generic SaaS hero template), banned motions.
- A **15-entry Structural DNA Catalog** (Index Manuscript, Pinned Narrative, Horizontal Navigation, Conversation Timeline, Dashboard Tile Grid, etc.) so no two sites in a batch share a template.
- **Deep industry research** — study at least 5 reference sites per project, pull specific patterns, compose a design brief before writing any JSX.
- **A Spline 3D playbook** — the 4-format URL reference table, the `<spline-viewer>` `background` attribute for theme-matching, the rule against real-branded-product scenes, per-session scene uniqueness, layered fallback hierarchy (Spline → photography → SVG), and a mandatory post-build render-size check.
- **A 15-point prompt checklist** every build must answer before writing JSX.

## Files

- `c

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
