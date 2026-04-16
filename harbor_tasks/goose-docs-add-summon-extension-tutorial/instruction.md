# Update Documentation for Skills-to-Summon Extension Rename

## Background

In goose v1.25.0, the "Skills" built-in extension was renamed to "Summon". The documentation repository needs updates to reflect this change across multiple files.

## Problem

Multiple documentation files still reference the old "Skills" extension name and link to `skills-mcp` documentation. The documentation needs:
1. A new documentation page for the Summon extension with YAML frontmatter containing `title` and `description` fields
2. A deprecation notice on the existing Skills extension page
3. Updated references across tutorials and guides, including the exact component attribute `extensionName="Summon"`

## Tasks

### 1. Create Summon extension documentation

Create `documentation/docs/mcp/summon-mcp.md` — a new documentation page for the Summon extension. The page must:
- Include YAML frontmatter with `title` and `description` fields, referencing "Summon" in the title
- Be comprehensive (substantial content, well over 500 characters)
- Follow the same documentation structure and conventions as other extension pages in the `documentation/docs/mcp/` directory
- Include a section titled exactly `## Configuration` explaining how to enable the extension
- Include a section titled exactly `## Example Usage` demonstrating the extension (e.g., loading a skill and delegating to a subagent)
- Reference the three key concepts the extension provides: skills, recipes, and subagents
- Include a reference to the screenshot image `summon-retro-site.png` in the results section

### 2. Deprecate Skills extension documentation

Update `documentation/docs/mcp/skills-mcp.md` to add a deprecation notice:
- Indicate that the Skills extension is deprecated
- Point users to the Summon extension as a replacement, linking to summon-mcp

### 3. Update the built-in extensions list

Update `documentation/docs/getting-started/using-extensions.md`:
- Replace references to the Skills extension with Summon
- Update links from skills-mcp to summon-mcp

### 4. Update the skills usage guide

Update `documentation/docs/guides/context-engineering/using-skills.md`:
- Replace the Skills extension reference with the Summon extension (noting v1.25.0+)
- Link to summon-mcp documentation

### 5. Update the Playwright tutorial

Update `documentation/docs/tutorials/playwright-skill.md`:
- Replace all references to the Skills extension with Summon
- Update any code blocks or component references that use the old extension name to use the new one
- The extension component must use the exact attribute format: `extensionName="Summon"`
- Update links from skills-mcp to summon-mcp

### 6. Update the Remotion tutorial

Update `documentation/docs/tutorials/remotion-video-creation.md`:
- Replace all references to the Skills extension with Summon
- Update any code blocks or command examples to reflect the Summon extension
- Update links from skills-mcp to summon-mcp

### 7. Add screenshot image

Place a valid PNG image file named `summon-retro-site.png` in `documentation/static/img/`. The image should be at least 1000 bytes.

## Files

- `documentation/docs/mcp/` — Extension documentation directory
- `documentation/docs/getting-started/using-extensions.md` — Built-in extensions list
- `documentation/docs/guides/context-engineering/using-skills.md` — Skills usage guide
- `documentation/docs/tutorials/playwright-skill.md` — Playwright tutorial
- `documentation/docs/tutorials/remotion-video-creation.md` — Remotion tutorial
- `documentation/static/img/` — Static images directory
