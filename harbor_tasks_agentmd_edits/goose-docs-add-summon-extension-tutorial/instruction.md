# Add Summon Extension Tutorial and Documentation

## Problem

The goose documentation currently references the "Skills" extension in multiple places, but the extension has been renamed to "Summon" in v1.25.0+. This creates confusion for users:

1. The Skills extension documentation needs a deprecation notice
2. A new Summon extension documentation page needs to be created
3. Multiple documentation files still reference "Skills" instead of "Summon"
4. Tutorial files (playwright-skill.md, remotion-video-creation.md) need to reference the new extension name

## Expected Behavior

1. Create a new `summon-mcp.md` file with:
   - Proper YAML frontmatter (title, description)
   - Configuration section showing how to enable the extension
   - Example Usage section with a retro web skill example
   - References to skills, recipes, and subagents

2. Add a deprecation notice to `skills-mcp.md` indicating it's deprecated and only available in v1.16.0 - v1.24.0

3. Update `using-extensions.md` to reference "Summon" instead of "Skills" in the built-in extensions list

4. Update `using-skills.md` to reference the Summon extension (v1.25.0+)

5. Update `playwright-skill.md` to use `extensionName="Summon"` and reference summon-mcp

6. Update `remotion-video-creation.md` to reference summon-mcp and use the new `load | summon` format

7. Add the `summon-retro-site.png` screenshot to the static images directory

## Files to Look At

- `documentation/docs/mcp/skills-mcp.md` — Add deprecation caution notice
- `documentation/docs/getting-started/using-extensions.md` — Update built-in extensions list
- `documentation/docs/guides/context-engineering/using-skills.md` — Update extension reference
- `documentation/docs/tutorials/playwright-skill.md` — Update extension references
- `documentation/docs/tutorials/remotion-video-creation.md` — Update extension references
- `documentation/static/img/` — Add screenshot image

## Files to Create

- `documentation/docs/mcp/summon-mcp.md` — New Summon extension documentation
