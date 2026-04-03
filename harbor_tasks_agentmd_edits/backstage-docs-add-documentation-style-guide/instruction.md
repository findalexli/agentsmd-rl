# Add a Documentation Style Guide

## Problem

Backstage has contribution guidelines (`CONTRIBUTING.md`) with a documentation section, but there is no dedicated style guide that standardizes tone, formatting, and terminology for documentation contributions. Contributors currently have to reverse-engineer the preferred writing style from existing docs, leading to inconsistent documentation quality.

## Expected Behavior

Create a comprehensive documentation style guide at `docs/contribute/doc-style-guide.md` that covers:

- **Tone and voice**: How documentation should sound (approachable yet professional)
- **Formatting standards**: When to use bold, italics, code style, etc.
- **Writing practices**: Active voice, present tense, addressing the reader
- **Code snippet formatting**: How to format code blocks and commands
- **Backstage-specific terminology**: A word list for consistent term usage (TechDocs, Scaffolder, Software Catalog, etc.)

The style guide should be adapted to the Backstage project specifically — reference Backstage tools, use Backstage examples, and follow the Docusaurus conventions used by the documentation site.

After creating the style guide, update the relevant project configuration files to reference it so that contributors (both human and AI) can find it. The sidebar should also be updated so the guide appears in the documentation site navigation under the "Contribute" section.

## Files to Look At

- `docs/contribute/` — where existing contribution docs live
- `AGENTS.md` — agent configuration that guides AI contributors
- `CONTRIBUTING.md` — contributor guidelines (Documentation Guidelines section)
- `microsite/sidebars.ts` — documentation site sidebar configuration
