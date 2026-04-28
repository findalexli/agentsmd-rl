#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "description: Connects Figma design components to code components using Code Conn" "skills/.curated/figma-code-connect-components/SKILL.md" && grep -qF "description: Generates custom design system rules for the user's codebase. Use w" "skills/.curated/figma-create-design-system-rules/SKILL.md" && grep -qF "description: Translates Figma designs into production-ready code with 1:1 visual" "skills/.curated/figma-implement-design/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/.curated/figma-code-connect-components/SKILL.md b/skills/.curated/figma-code-connect-components/SKILL.md
@@ -0,0 +1,390 @@
+---
+name: figma-code-connect-components
+description: Connects Figma design components to code components using Code Connect. Use when user says "code connect", "connect this component to code", "connect Figma to code", "map this component", "link component to code", "create code connect mapping", "add code connect", "connect design to code", or wants to establish mappings between Figma designs and code implementations. Requires Figma MCP server connection.
+---
+
+# Code Connect Components
+
+## Overview
+
+This skill helps you connect Figma design components to their corresponding code implementations using Figma's Code Connect feature. It analyzes the Figma design structure, searches your codebase for matching components, and establishes mappings that maintain design-code consistency.
+
+## Prerequisites
+
+- Figma MCP server must be connected and accessible
+- User must provide a Figma URL with node ID: `https://figma.com/design/:fileKey/:fileName?node-id=1-2`
+  - **IMPORTANT:** The Figma URL must include the `node-id` parameter. Code Connect mapping will fail without it.
+- **OR** when using `figma-desktop` MCP: User can select a node directly in the Figma desktop app (no URL required)
+- **IMPORTANT:** The Figma component must be published to a team library. Code Connect only works with published components or component sets.
+- Access to the project codebase for component scanning
+
+## Required Workflow
+
+**Follow these steps in order. Do not skip steps.**
+
+### Step 1: Get Node ID and Extract Metadata
+
+#### Option A: Parse from Figma URL
+
+When the user provides a Figma URL with file key and node ID, first run `get_metadata` to fetch the node structure and identify all Figma components.
+
+**IMPORTANT:** When extracting the node ID from a Figma URL, convert the format:
+
+- URL format uses hyphens: `node-id=1-2`
+- Tool expects colons: `nodeId=1:2`
+
+**Parse the Figma URL:**
+
+- URL format: `https://figma.com/design/:fileKey/:fileName?node-id=1-2`
+- Extract file key: `:fileKey` (segment after `/design/`)
+- Extract node ID: `1-2` from URL, then convert to `1:2` for the tool
+
+**Note:** When using the local desktop MCP (`figma-desktop`), `fileKey` is not passed as a parameter to tool calls. The server automatically uses the currently open file, so only `nodeId` is needed.
+
+**Example:**
+
+```
+get_metadata(fileKey=":fileKey", nodeId="1:2")
+```
+
+#### Option B: Use Current Selection from Figma Desktop App (figma-desktop MCP only)
+
+When using the `figma-desktop` MCP and the user has NOT provided a URL, the tools automatically use the currently selected node from the open Figma file in the desktop app.
+
+**Note:** Selection-based prompting only works with the `figma-desktop` MCP server. The remote server requires a link to a frame or layer to extract context. The user must have the Figma desktop app open with a node selected.
+
+This returns:
+
+- Node structure and hierarchy in XML format
+- Node types (identify `<symbol>` nodes as Figma components)
+- Node IDs, layer names, positions, and sizes
+- Child nodes that may also be components
+
+**Identify components:** For each node or child node returned, if the type is `<symbol>`, that indicates it's a Figma component that can be code connected.
+
+### Step 2: Check Existing Code Connect Mappings
+
+For each Figma component identified (nodes with type `<symbol>`), check if it's already code connected using `get_code_connect_map`.
+
+**Example:**
+
+```
+get_code_connect_map(fileKey=":fileKey", nodeId="1:2")
+```
+
+**If the component is already connected:**
+
+- Skip to the next component
+- Inform the user that this component is already mapped
+
+**If not connected:**
+
+- Proceed to Step 3 to analyze the component and create a mapping
+
+### Step 3: Get Design Context for Un-Connected Components
+
+For components that are not yet code connected, run `get_design_context` to fetch detailed component structure.
+
+**Example:**
+
+```
+get_design_context(fileKey=":fileKey", nodeId="1:2")
+```
+
+This returns:
+
+- Component structure and hierarchy
+- Layout properties and styling
+- Text content and variants
+- Design properties that map to code props
+
+### Step 4: Scan Codebase for Matching Component
+
+Using the output from `get_design_context`, scan the codebase to find a component with similar structure.
+
+**What to look for:**
+
+- Component names that match or are similar to the Figma component name
+- Component structure that aligns with the Figma hierarchy
+- Props that correspond to Figma properties (variants, text, styles)
+- Files in typical component directories (`src/components/`, `components/`, `ui/`, etc.)
+
+**Search strategy:**
+
+1. Search for component files with matching names
+2. Read candidate files to check structure and props
+3. Compare the code component's props with Figma design properties
+4. Detect the programming language (TypeScript, JavaScript) and framework (React, Vue, etc.)
+5. Identify the best match based on structural similarity, weighing:
+   - Prop names and their correspondence to Figma properties
+   - Default values that match Figma defaults
+   - CSS classes or style objects
+   - Descriptive comments that clarify intent
+6. If multiple candidates are equally good, pick the one with the closest prop-interface match and document your reasoning in a 1–2 sentence comment before your tool call
+
+**Example search patterns:**
+
+- If Figma component is "PrimaryButton", search for `Button.tsx`, `PrimaryButton.tsx`, `Button.jsx`
+- Check common component paths: `src/components/`, `app/components/`, `lib/ui/`
+- Look for variant props like `variant`, `size`, `color` that match Figma variants
+
+### Step 5: Offer Code Connect Mapping
+
+Present your findings to the user and offer to create the Code Connect mapping.
+
+**What to communicate:**
+
+- Which code component you found that matches the Figma component
+- File path of the component
+- Component name
+- Language and framework detected
+
+**Example message:**
+
+```
+I found a matching component in your codebase:
+- File: src/components/Button.tsx
+- Component: Button
+- Language: TypeScript/JavaScript
+- Framework: React
+
+Would you like me to create a Code Connect mapping for this component?
+```
+
+**If no exact match is found:**
+
+- Show the 2 closest candidates
+- Explain the differences
+- Ask the user to confirm which component to use or provide the correct path
+
+### Step 6: Create the Code Connect Mapping
+
+If the user accepts, run `add_code_connect_map` to establish the connection.
+
+**Tool parameters:**
+
+```
+add_code_connect_map(
+  nodeId="1:2",
+  source="src/components/Button.tsx",
+  componentName="Button",
+  clientLanguages="typescript,javascript",
+  clientFrameworks="react"
+)
+```
+
+**Key parameters:**
+
+- `nodeId`: The Figma node ID (with colon format: `1:2`)
+- `source`: Path to the code component file (relative to project root)
+- `componentName`: Name of the component to connect (e.g., "Button", "Card")
+- `clientLanguages`: Comma-separated list of languages (e.g., "typescript,javascript", "javascript")
+- `clientFrameworks`: Framework being used (e.g., "react", "vue", "svelte", "angular")
+- `label`: The framework or language label for this Code Connect mapping. Valid values include:
+  - Web: 'React', 'Web Components', 'Vue', 'Svelte', 'Storybook', 'Javascript'
+  - iOS: 'Swift UIKit', 'Objective-C UIKit', 'SwiftUI'
+  - Android: 'Compose', 'Java', 'Kotlin', 'Android XML Layout'
+  - Cross-platform: 'Flutter'
+
+### Step 7: Repeat for All Un-Connected Components
+
+After successfully connecting one component, return to Step 2 and repeat the process for all other un-connected Figma components identified in the node tree from Step 1.
+
+**Workflow for multiple components:**
+
+1. From the metadata obtained in Step 1, identify all nodes with type `<symbol>`
+2. For each component node:
+   - Check if already code connected (Step 2)
+   - If not connected, proceed with Steps 3-6
+   - Track which components have been processed
+3. After processing all components, provide a summary:
+   - Total components found
+   - Components successfully connected
+   - Components skipped (already connected)
+   - Components that could not be connected (with reasons)
+
+**Example summary:**
+
+```
+Code Connect Summary:
+- Total components found: 5
+- Successfully connected: 3
+  - Button (1:2) → src/components/Button.tsx
+  - Card (1:5) → src/components/Card.tsx
+  - Input (1:8) → src/components/Input.tsx
+- Already connected: 1
+  - Icon (1:3) → src/icons/Icon.tsx
+- Could not connect: 1
+  - CustomWidget (1:10) - No matching component found in codebase
+```
+
+## Examples
+
+### Example 1: Connecting a Button Component
+
+User says: "Connect this Figma button to my code: https://figma.com/design/kL9xQn2VwM8pYrTb4ZcHjF/DesignSystem?node-id=42-15"
+
+**Actions:**
+
+1. Parse URL: fileKey=`kL9xQn2VwM8pYrTb4ZcHjF`, nodeId=`42-15` (from URL)
+2. Convert node ID: `42-15` → `42:15`
+3. Run `get_metadata(fileKey="kL9xQn2VwM8pYrTb4ZcHjF", nodeId="42:15")` to get node structure
+4. Metadata shows: Node type is `<symbol>` (Figma component), name is "Button"
+5. Run `get_code_connect_map(fileKey="kL9xQn2VwM8pYrTb4ZcHjF", nodeId="42:15")` to check existing mappings
+6. Result: No existing mapping found
+7. Run `get_design_context(fileKey="kL9xQn2VwM8pYrTb4ZcHjF", nodeId="42:15")` to get detailed structure
+8. Design context shows: Button component with `variant` (primary/secondary) and `size` (sm/md/lg) properties
+9. Search codebase for Button components: Find `src/components/Button.tsx`
+10. Read `Button.tsx` and confirm it has `variant` and `size` props
+11. Offer mapping: "I found Button.tsx with matching variant and size props. Connect?"
+12. User confirms: "Yes"
+13. Detect that it's a TypeScript React component
+14. Run `add_code_connect_map(nodeId="42:15", source="src/components/Button.tsx", componentName="Button", clientLanguages="typescript,javascript", clientFrameworks="react")`
+
+**Result:** Figma button component is now connected to the code Button component.
+
+### Example 2: Multiple Candidates Scenario
+
+User says: "Connect this card: https://figma.com/design/pR8mNv5KqXzGwY2JtCfL4D/Components?node-id=10-50"
+
+**Actions:**
+
+1. Parse URL: fileKey=`pR8mNv5KqXzGwY2JtCfL4D`, nodeId=`10-50` → convert to `10:50`
+2. Run `get_metadata(fileKey="pR8mNv5KqXzGwY2JtCfL4D", nodeId="10:50")` to get node structure
+3. Metadata shows: Node type is `<symbol>` (Figma component), name is "ProductCard"
+4. Run `get_code_connect_map(fileKey="pR8mNv5KqXzGwY2JtCfL4D", nodeId="10:50")` to check existing mappings
+5. Result: No existing mapping found
+6. Run `get_design_context(fileKey="pR8mNv5KqXzGwY2JtCfL4D", nodeId="10:50")`
+7. Design context shows: Card with title, description, image, and action button
+8. Search codebase: Find two candidates:
+   - `src/components/Card.tsx` (basic card)
+   - `src/components/ProductCard.tsx` (card with image and CTA)
+9. Read both files and compare structure
+10. Present to user: "Found two card components:
+
+- Card.tsx: Basic card with title and description
+- ProductCard.tsx: Card with image, title, description, and action button (closer match)
+
+Which should I connect?"
+
+11. User: "ProductCard.tsx"
+12. Detect that it's a TypeScript React component
+13. Run `add_code_connect_map(nodeId="10:50", source="src/components/ProductCard.tsx", componentName="ProductCard", clientLanguages="typescript,javascript", clientFrameworks="react")`
+
+**Result:** User-selected ProductCard component is successfully connected to the Figma design.
+
+### Example 3: Component Needs Creation
+
+User says: "Connect this icon: https://figma.com/design/8yJDMeWDyBz71EnMOSuUiw/Icons?node-id=5-20"
+
+**Actions:**
+
+1. Parse URL: fileKey=`8yJDMeWDyBz71EnMOSuUiw`, nodeId=`5-20` → convert to `5:20`
+2. Run `get_metadata(fileKey="8yJDMeWDyBz71EnMOSuUiw", nodeId="5:20")` to get node structure
+3. Metadata shows: Node type is `<symbol>` (Figma component), name is "CheckIcon"
+4. Run `get_code_connect_map(fileKey="8yJDMeWDyBz71EnMOSuUiw", nodeId="5:20")` to check existing mappings
+5. Result: No existing mapping found
+6. Run `get_design_context(fileKey="8yJDMeWDyBz71EnMOSuUiw", nodeId="5:20")`
+7. Design context shows: CheckIcon with color and size variants
+8. Search codebase for CheckIcon: No matches found
+9. Search for generic Icon components: Find `src/icons/` directory with other icons
+10. Report to user: "I couldn't find a CheckIcon component, but I found an icons directory at src/icons/. Would you like to:
+
+- Create a new CheckIcon.tsx component first, then connect it
+- Connect to a different existing icon
+- Provide the path to the CheckIcon if it exists elsewhere"
+
+11. User provides path: "src/icons/CheckIcon.tsx"
+12. Detect language and framework from the file
+13. Run `add_code_connect_map(nodeId="5:20", source="src/icons/CheckIcon.tsx", componentName="CheckIcon", clientLanguages="typescript,javascript", clientFrameworks="react")`
+
+**Result:** CheckIcon component is successfully connected to the Figma design.
+
+## Best Practices
+
+### Proactive Component Discovery
+
+Don't just ask the user for the file path — actively search their codebase to find matching components. This provides a better experience and catches potential mapping opportunities.
+
+### Accurate Structure Matching
+
+When comparing Figma components to code components, look beyond just names. Check that:
+
+- Props align (variant types, size options, etc.)
+- Component hierarchy matches (nested elements)
+- The component serves the same purpose
+
+### Clear Communication
+
+When offering to create a mapping, clearly explain:
+
+- What you found
+- Why it's a good match
+- What the mapping will do
+- How props will be connected
+
+### Handle Ambiguity
+
+If multiple components could match, present options rather than guessing. Let the user make the final decision about which component to connect.
+
+### Graceful Degradation
+
+If you can't find an exact match, provide helpful next steps:
+
+- Show close candidates
+- Suggest component creation
+- Ask for user guidance
+
+## Common Issues and Solutions
+
+### Issue: "Failed to map node to Code Connect. Please ensure the component or component set is published to the team library"
+
+**Cause:** The Figma component is not published to a team library. Code Connect only works with published components.
+**Solution:** The user needs to publish the component to a team library in Figma:
+
+1. In Figma, select the component or component set
+2. Right-click and choose "Publish to library" or use the Team Library publish modal
+3. Publish the component
+4. Once published, retry the Code Connect mapping with the same node ID
+
+### Issue: No matching component found in codebase
+
+**Cause:** The codebase search did not find a component with a matching name or structure.
+**Solution:** Ask the user if the component exists under a different name or in a different location. They may need to create the component first, or it might be located in an unexpected directory.
+
+### Issue: Code Connect map creation fails with "component not found"
+
+**Cause:** The source file path is incorrect, the component doesn't exist at that location, or the componentName doesn't match the actual export.
+**Solution:** Verify the source path is correct and relative to the project root. Check that the component is properly exported from the file with the exact componentName specified.
+
+### Issue: Wrong language or framework detected
+
+**Cause:** The clientLanguages or clientFrameworks parameters don't match the actual component implementation.
+**Solution:** Inspect the component file to verify the language (TypeScript, JavaScript) and framework (React, Vue, etc.). Update the parameters accordingly. For TypeScript React components, use `clientLanguages="typescript,javascript"` and `clientFrameworks="react"`.
+
+### Issue: Code Connect mapping fails with URL errors
+
+**Cause:** The Figma URL format is incorrect or missing the `node-id` parameter.
+**Solution:** Verify the URL follows the required format: `https://figma.com/design/:fileKey/:fileName?node-id=1-2`. The `node-id` parameter is required. Also ensure you convert `1-2` to `1:2` when calling tools.
+
+### Issue: Multiple similar components found
+
+**Cause:** The codebase contains multiple components that could match the Figma component.
+**Solution:** Present all candidates to the user with their file paths and let them choose which one to connect. Different components might be used in different contexts (e.g., `Button.tsx` vs `LinkButton.tsx`).
+
+## Understanding Code Connect
+
+Code Connect establishes a bidirectional link between design and code:
+
+**For designers:** See which code component implements a Figma component
+**For developers:** Navigate from Figma designs directly to the code that implements them
+**For teams:** Maintain a single source of truth for component mappings
+
+The mapping you create helps keep design and code in sync by making these connections explicit and discoverable.
+
+## Additional Resources
+
+For more information about Code Connect:
+
+- [Code Connect Documentation](https://help.figma.com/hc/en-us/articles/23920389749655-Code-Connect)
+- [Figma MCP Server Tools and Prompts](https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/)
diff --git a/skills/.curated/figma-create-design-system-rules/SKILL.md b/skills/.curated/figma-create-design-system-rules/SKILL.md
@@ -0,0 +1,515 @@
+---
+name: figma-create-design-system-rules
+description: Generates custom design system rules for the user's codebase. Use when user says "create design system rules", "generate rules for my project", "set up design rules", "customize design system guidelines", or wants to establish project-specific conventions for Figma-to-code workflows. Requires Figma MCP server connection.
+---
+
+# Create Design System Rules
+
+## Overview
+
+This skill helps you generate custom design system rules tailored to your project's specific needs. These rules guide Codex to produce consistent, high-quality code when implementing Figma designs, ensuring that your team's conventions, component patterns, and architectural decisions are followed automatically.
+
+## What Are Design System Rules?
+
+Design system rules are project-level instructions that encode the "unwritten knowledge" of your codebase - the kind of expertise that experienced developers know and would pass on to new team members:
+
+- Which layout primitives and components to use
+- Where component files should be located
+- How components should be named and structured
+- What should never be hardcoded
+- How to handle design tokens and styling
+- Project-specific architectural patterns
+
+Once defined, these rules dramatically reduce repetitive prompting and ensure consistent output across all Figma implementation tasks.
+
+## Prerequisites
+
+- Figma MCP server must be connected and accessible
+- Access to the project codebase for analysis
+- Understanding of your team's component conventions (or willingness to establish them)
+
+## When to Use This Skill
+
+Use this skill when:
+
+- Starting a new project that will use Figma designs
+- Onboarding Codex to an existing project with established patterns
+- Standardizing Figma-to-code workflows across your team
+- Updating or refining existing design system conventions
+- Users explicitly request: "create design system rules", "set up Figma guidelines", "customize rules for my project"
+
+## Required Workflow
+
+**Follow these steps in order. Do not skip steps.**
+
+### Step 1: Run the Create Design System Rules Tool
+
+Call the Figma MCP server's `create_design_system_rules` tool to get the foundational prompt and template.
+
+**Parameters:**
+
+- `clientLanguages`: Comma-separated list of languages used in the project (e.g., "typescript,javascript", "python", "javascript")
+- `clientFrameworks`: Framework being used (e.g., "react", "vue", "svelte", "angular", "unknown")
+
+This tool returns guidance and a template for creating design system rules.
+
+Structure your design system rules following the template format provided in the tool's response.
+
+### Step 2: Analyze the Codebase
+
+Before finalizing rules, analyze the project to understand existing patterns:
+
+**Component Organization:**
+
+- Where are UI components located? (e.g., `src/components/`, `app/ui/`, `lib/components/`)
+- Is there a dedicated design system directory?
+- How are components organized? (by feature, by type, flat structure)
+
+**Styling Approach:**
+
+- What CSS framework or approach is used? (Tailwind, CSS Modules, styled-components, etc.)
+- Where are design tokens defined? (CSS variables, theme files, config files)
+- Are there existing color, typography, or spacing tokens?
+
+**Component Patterns:**
+
+- What naming conventions are used? (PascalCase, kebab-case, prefixes)
+- How are component props typically structured?
+- Are there common composition patterns?
+
+**Architecture Decisions:**
+
+- How is state management handled?
+- What routing system is used?
+- Are there specific import patterns or path aliases?
+
+### Step 3: Generate Project-Specific Rules
+
+Based on your codebase analysis, create a comprehensive set of rules. Include:
+
+#### General Component Rules
+
+```markdown
+- IMPORTANT: Always use components from `[YOUR_PATH]` when possible
+- Place new UI components in `[COMPONENT_DIRECTORY]`
+- Follow `[NAMING_CONVENTION]` for component names
+- Components must export as `[EXPORT_PATTERN]`
+```
+
+#### Styling Rules
+
+```markdown
+- Use `[CSS_FRAMEWORK/APPROACH]` for styling
+- Design tokens are defined in `[TOKEN_LOCATION]`
+- IMPORTANT: Never hardcode colors - always use tokens from `[TOKEN_FILE]`
+- Spacing values must use the `[SPACING_SYSTEM]` scale
+- Typography follows the scale defined in `[TYPOGRAPHY_LOCATION]`
+```
+
+#### Figma MCP Integration Rules
+
+```markdown
+## Figma MCP Integration Rules
+
+These rules define how to translate Figma inputs into code for this project and must be followed for every Figma-driven change.
+
+### Required Flow (do not skip)
+
+1. Run get_design_context first to fetch the structured representation for the exact node(s)
+2. If the response is too large or truncated, run get_metadata to get the high-level node map, then re-fetch only the required node(s) with get_design_context
+3. Run get_screenshot for a visual reference of the node variant being implemented
+4. Only after you have both get_design_context and get_screenshot, download any assets needed and start implementation
+5. Translate the output (usually React + Tailwind) into this project's conventions, styles, and framework
+6. Validate against Figma for 1:1 look and behavior before marking complete
+
+### Implementation Rules
+
+- Treat the Figma MCP output (React + Tailwind) as a representation of design and behavior, not as final code style
+- Replace Tailwind utility classes with `[YOUR_STYLING_APPROACH]` when applicable
+- Reuse existing components from `[COMPONENT_PATH]` instead of duplicating functionality
+- Use the project's color system, typography scale, and spacing tokens consistently
+- Respect existing routing, state management, and data-fetch patterns
+- Strive for 1:1 visual parity with the Figma design
+- Validate the final UI against the Figma screenshot for both look and behavior
+```
+
+#### Asset Handling Rules
+
+```markdown
+## Asset Handling
+
+- The Figma MCP server provides an assets endpoint which can serve image and SVG assets
+- IMPORTANT: If the Figma MCP server returns a localhost source for an image or SVG, use that source directly
+- IMPORTANT: DO NOT import/add new icon packages - all assets should be in the Figma payload
+- IMPORTANT: DO NOT use or create placeholders if a localhost source is provided
+- Store downloaded assets in `[ASSET_DIRECTORY]`
+```
+
+#### Project-Specific Conventions
+
+```markdown
+## Project-Specific Conventions
+
+- [Add any unique architectural patterns]
+- [Add any special import requirements]
+- [Add any testing requirements]
+- [Add any accessibility standards]
+- [Add any performance considerations]
+```
+
+### Step 4: Save Rules to AGENTS.md
+
+Guide the user to save the generated rules to the `AGENTS.md` file in their project root:
+
+```markdown
+# MCP Servers
+
+## Figma MCP Server Rules
+
+[Paste generated rules here]
+```
+
+After saving, the rules will be automatically loaded by Codex and applied to all Figma implementation tasks.
+
+### Step 5: Validate and Iterate
+
+After creating rules:
+
+1. Test with a simple Figma component implementation
+2. Verify Codex follows the rules correctly
+3. Refine any rules that aren't working as expected
+4. Share with team members for feedback
+5. Update rules as the project evolves
+
+## Rule Categories and Examples
+
+### Essential Rules (Always Include)
+
+**Component Discovery:**
+
+```markdown
+- UI components are located in `src/components/ui/`
+- Feature components are in `src/components/features/`
+- Layout primitives are in `src/components/layout/`
+```
+
+**Design Token Usage:**
+
+```markdown
+- Colors are defined as CSS variables in `src/styles/tokens.css`
+- Never hardcode hex colors - use `var(--color-*)` tokens
+- Spacing uses the 4px base scale: `--space-1` (4px), `--space-2` (8px), etc.
+```
+
+**Styling Approach:**
+
+```markdown
+- Use Tailwind utility classes for styling
+- Custom styles go in component-level CSS modules
+- Theme customization is in `tailwind.config.js`
+```
+
+### Recommended Rules (Highly Valuable)
+
+**Component Patterns:**
+
+```markdown
+- All components must accept a `className` prop for composition
+- Variant props should use union types: `variant: 'primary' | 'secondary'`
+- Icon components should accept `size` and `color` props
+```
+
+**Import Conventions:**
+
+```markdown
+- Use path aliases: `@/components`, `@/styles`, `@/utils`
+- Group imports: React, third-party, internal, types
+- No relative imports beyond parent directory
+```
+
+**Code Quality:**
+
+```markdown
+- Add JSDoc comments for exported components
+- Include PropTypes or TypeScript types for all props
+- Extract magic numbers to named constants
+```
+
+### Optional Rules (Project-Specific)
+
+**Accessibility:**
+
+```markdown
+- All interactive elements must have aria-labels
+- Color contrast must meet WCAG AA standards
+- Keyboard navigation required for all interactions
+```
+
+**Performance:**
+
+```markdown
+- Lazy load images with the `Image` component from `@/components/Image`
+- Use React.memo for components that receive complex props
+- Icons should be SVG components, not icon fonts
+```
+
+**Testing:**
+
+```markdown
+- Include unit tests for new components in `__tests__/` directory
+- Use Testing Library queries (getByRole, getByLabelText)
+- Test all interactive states and variants
+```
+
+## Examples
+
+### Example 1: React + Tailwind Project
+
+User says: "Create design system rules for my React project"
+
+**Actions:**
+
+1. Run `create_design_system_rules(clientLanguages="typescript,javascript", clientFrameworks="react")`
+2. Analyze codebase structure
+3. Generate rules:
+
+```markdown
+# Figma MCP Integration Rules
+
+## Component Organization
+
+- UI components are in `src/components/ui/`
+- Page components are in `src/app/`
+- Use Tailwind for styling
+
+## Figma Implementation Flow
+
+1. Run get_design_context for the node
+2. Run get_screenshot for visual reference
+3. Map Figma colors to Tailwind colors defined in `tailwind.config.js`
+4. Reuse components from `src/components/ui/` when possible
+5. Validate against screenshot before completing
+
+## Styling Rules
+
+- IMPORTANT: Use Tailwind utility classes, not inline styles
+- Colors are defined in `tailwind.config.js` theme.colors
+- Spacing uses Tailwind's default scale
+- Custom components go in `src/components/ui/`
+
+## Asset Rules
+
+- IMPORTANT: Use localhost sources from Figma MCP server directly
+- Store static assets in `public/assets/`
+- DO NOT install new icon libraries
+```
+
+4. Save to `AGENTS.md` in project root
+5. Test with a simple button implementation
+
+**Result:** Codex now consistently follows the project's conventions when implementing Figma designs.
+
+### Example 2: Vue + Custom CSS Project
+
+User says: "Set up Figma rules for my Vue app"
+
+**Actions:**
+
+1. Run `create_design_system_rules(clientLanguages="typescript,javascript", clientFrameworks="vue")`
+2. Discover that project uses CSS modules and a custom design token system
+3. Generate rules:
+
+```markdown
+# Figma MCP Integration Rules
+
+## Component Organization
+
+- Components are in `src/components/`
+- Composables are in `src/composables/`
+- Vue SFC structure: <script setup>, <template>, <style scoped>
+
+## Design Tokens
+
+- IMPORTANT: All colors defined in `src/styles/tokens.css` as CSS variables
+- Use `var(--color-primary)`, `var(--color-secondary)`, etc.
+- Spacing: `var(--space-xs)` through `var(--space-xl)`
+- Typography: `var(--text-sm)` through `var(--text-2xl)`
+
+## Figma Implementation Flow
+
+1. Run get_design_context and get_screenshot
+2. Translate React output to Vue 3 Composition API
+3. Map Figma colors to CSS variables in `src/styles/tokens.css`
+4. Use CSS Modules for component styles
+5. Check for existing components in `src/components/` before creating new ones
+
+## Styling Rules
+
+- Use CSS Modules (`.module.css` files)
+- IMPORTANT: Reference design tokens, never hardcode values
+- Scoped styles with CSS modules
+```
+
+4. Save to `AGENTS.md` in project root
+5. Validate with a card component
+
+**Result:** Codex now correctly translates Figma designs to Vue components using the project's design token system.
+
+### Example 3: Design System Team
+
+User says: "Generate rules for our design system library"
+
+**Actions:**
+
+1. Run `create_design_system_rules(clientLanguages="typescript", clientFrameworks="react")`
+2. Analyze the monorepo structure with design system package
+3. Generate comprehensive rules:
+
+```markdown
+# Design System Rules
+
+## Repository Structure
+
+- Design system components: `packages/design-system/src/components/`
+- Documentation: `packages/docs/`
+- Design tokens: `packages/tokens/src/`
+
+## Component Development
+
+- IMPORTANT: All components must be in `packages/design-system/src/components/`
+- Component file structure: `ComponentName/index.tsx`, `ComponentName.stories.tsx`, `ComponentName.test.tsx`
+- Export all components from `packages/design-system/src/index.ts`
+
+## Design Tokens
+
+- Colors: `packages/tokens/src/colors.ts`
+- Typography: `packages/tokens/src/typography.ts`
+- Spacing: `packages/tokens/src/spacing.ts`
+- IMPORTANT: Never hardcode values - import from tokens package
+
+## Documentation Requirements
+
+- Add Storybook story for every component
+- Include JSDoc with @example
+- Document all props with descriptions
+- Add accessibility notes
+
+## Figma Integration
+
+1. Get design context and screenshot from Figma
+2. Map Figma tokens to design system tokens
+3. Create or extend component in design system package
+4. Add Storybook stories showing all variants
+5. Validate against Figma screenshot
+6. Update documentation
+```
+
+4. Save to `AGENTS.md` and share with team
+5. Add to team documentation
+
+**Result:** Entire team follows consistent patterns when adding components from Figma to the design system.
+
+## Best Practices
+
+### Start Simple, Iterate
+
+Don't try to capture every rule upfront. Start with the most important conventions and add rules as you encounter inconsistencies.
+
+### Be Specific
+
+Instead of: "Use the design system"
+Write: "Always use Button components from `src/components/ui/Button.tsx` with variant prop ('primary' | 'secondary' | 'ghost')"
+
+### Make Rules Actionable
+
+Each rule should tell Codex exactly what to do, not just what to avoid.
+
+Good: "Colors are defined in `src/theme/colors.ts` - import and use these constants"
+Bad: "Don't hardcode colors"
+
+### Use IMPORTANT for Critical Rules
+
+Prefix rules that must never be violated with "IMPORTANT:" to ensure Codex prioritizes them.
+
+```markdown
+- IMPORTANT: Never expose API keys in client-side code
+- IMPORTANT: Always sanitize user input before rendering
+```
+
+### Document the Why
+
+When rules seem arbitrary, explain the reasoning:
+
+```markdown
+- Place all data-fetching in server components (reduces client bundle size and improves performance)
+- Use absolute imports with `@/` alias (makes refactoring easier and prevents broken relative paths)
+```
+
+## Common Issues and Solutions
+
+### Issue: Codex isn't following the rules
+
+**Cause:** Rules may be too vague or not properly loaded into the IDE/MCP client.
+**Solution:**
+
+- Make rules more specific and actionable
+- Verify rules are saved in the correct configuration file
+- Restart your IDE or MCP client to reload rules
+- Add "IMPORTANT:" prefix to critical rules
+
+### Issue: Rules conflict with each other
+
+**Cause:** Contradictory or overlapping rules.
+**Solution:**
+
+- Review all rules for conflicts
+- Establish a clear priority hierarchy
+- Remove redundant rules
+- Consolidate related rules into single, clear statements
+
+### Issue: Too many rules make Codex slow
+
+**Cause:** Excessive rules increase context size and processing time.
+**Solution:**
+
+- Focus on the 20% of rules that solve 80% of consistency issues
+- Remove overly specific rules that rarely apply
+- Combine related rules
+- Use progressive disclosure (basic rules first, advanced rules in linked files)
+
+### Issue: Rules become outdated as project evolves
+
+**Cause:** Codebase changes but rules don't.
+**Solution:**
+
+- Schedule periodic rule reviews (monthly or quarterly)
+- Update rules when architectural decisions change
+- Version control your rule files
+- Document rule changes in commit messages
+
+## Understanding Design System Rules
+
+Design system rules transform how Codex works with your Figma designs:
+
+**Before rules:**
+
+- Codex makes assumptions about component structure
+- Inconsistent styling approaches across implementations
+- Hardcoded values that don't match design tokens
+- Components created in random locations
+- Repetitive explanations of project conventions
+
+**After rules:**
+
+- Codex automatically follows your conventions
+- Consistent component structure and styling
+- Proper use of design tokens from the start
+- Components organized correctly
+- Zero repetitive prompting
+
+The time invested in creating good rules pays off exponentially across every Figma implementation task.
+
+## Additional Resources
+
+- [Figma MCP Server Documentation](https://developers.figma.com/docs/figma-mcp-server/)
+- [Figma Variables and Design Tokens](https://help.figma.com/hc/en-us/articles/15339657135383-Guide-to-variables-in-Figma)
diff --git a/skills/.curated/figma-implement-design/SKILL.md b/skills/.curated/figma-implement-design/SKILL.md
@@ -0,0 +1,250 @@
+---
+name: figma-implement-design
+description: Translates Figma designs into production-ready code with 1:1 visual fidelity. Use when implementing UI from Figma files, when user mentions "implement design", "generate code", "implement component", "build Figma design", provides Figma URLs, or asks to build components matching Figma specs. Requires Figma MCP server connection.
+---
+
+# Implement Design
+
+## Overview
+
+This skill provides a structured workflow for translating Figma designs into production-ready code with pixel-perfect accuracy. It ensures consistent integration with the Figma MCP server, proper use of design tokens, and 1:1 visual parity with designs.
+
+## Prerequisites
+
+- Figma MCP server must be connected and accessible
+- User must provide a Figma URL in the format: `https://figma.com/design/:fileKey/:fileName?node-id=1-2`
+  - `:fileKey` is the file key
+  - `1-2` is the node ID (the specific component or frame to implement)
+- **OR** when using `figma-desktop` MCP: User can select a node directly in the Figma desktop app (no URL required)
+- Project should have an established design system or component library (preferred)
+
+## Required Workflow
+
+**Follow these steps in order. Do not skip steps.**
+
+### Step 1: Get Node ID
+
+#### Option A: Parse from Figma URL
+
+When the user provides a Figma URL, extract the file key and node ID to pass as arguments to MCP tools.
+
+**URL format:** `https://figma.com/design/:fileKey/:fileName?node-id=1-2`
+
+**Extract:**
+
+- **File key:** `:fileKey` (the segment after `/design/`)
+- **Node ID:** `1-2` (the value of the `node-id` query parameter)
+
+**Note:** When using the local desktop MCP (`figma-desktop`), `fileKey` is not passed as a parameter to tool calls. The server automatically uses the currently open file, so only `nodeId` is needed.
+
+**Example:**
+
+- URL: `https://figma.com/design/kL9xQn2VwM8pYrTb4ZcHjF/DesignSystem?node-id=42-15`
+- File key: `kL9xQn2VwM8pYrTb4ZcHjF`
+- Node ID: `42-15`
+
+#### Option B: Use Current Selection from Figma Desktop App (figma-desktop MCP only)
+
+When using the `figma-desktop` MCP and the user has NOT provided a URL, the tools automatically use the currently selected node from the open Figma file in the desktop app.
+
+**Note:** Selection-based prompting only works with the `figma-desktop` MCP server. The remote server requires a link to a frame or layer to extract context. The user must have the Figma desktop app open with a node selected.
+
+### Step 2: Fetch Design Context
+
+Run `get_design_context` with the extracted file key and node ID.
+
+```
+get_design_context(fileKey=":fileKey", nodeId="1-2")
+```
+
+This provides the structured data including:
+
+- Layout properties (Auto Layout, constraints, sizing)
+- Typography specifications
+- Color values and design tokens
+- Component structure and variants
+- Spacing and padding values
+
+**If the response is too large or truncated:**
+
+1. Run `get_metadata(fileKey=":fileKey", nodeId="1-2")` to get the high-level node map
+2. Identify the specific child nodes needed from the metadata
+3. Fetch individual child nodes with `get_design_context(fileKey=":fileKey", nodeId=":childNodeId")`
+
+### Step 3: Capture Visual Reference
+
+Run `get_screenshot` with the same file key and node ID for a visual reference.
+
+```
+get_screenshot(fileKey=":fileKey", nodeId="1-2")
+```
+
+This screenshot serves as the source of truth for visual validation. Keep it accessible throughout implementation.
+
+### Step 4: Download Required Assets
+
+Download any assets (images, icons, SVGs) returned by the Figma MCP server.
+
+**IMPORTANT:** Follow these asset rules:
+
+- If the Figma MCP server returns a `localhost` source for an image or SVG, use that source directly
+- DO NOT import or add new icon packages - all assets should come from the Figma payload
+- DO NOT use or create placeholders if a `localhost` source is provided
+- Assets are served through the Figma MCP server's built-in assets endpoint
+
+### Step 5: Translate to Project Conventions
+
+Translate the Figma output into this project's framework, styles, and conventions.
+
+**Key principles:**
+
+- Treat the Figma MCP output (typically React + Tailwind) as a representation of design and behavior, not as final code style
+- Replace Tailwind utility classes with the project's preferred utilities or design system tokens
+- Reuse existing components (buttons, inputs, typography, icon wrappers) instead of duplicating functionality
+- Use the project's color system, typography scale, and spacing tokens consistently
+- Respect existing routing, state management, and data-fetch patterns
+
+### Step 6: Achieve 1:1 Visual Parity
+
+Strive for pixel-perfect visual parity with the Figma design.
+
+**Guidelines:**
+
+- Prioritize Figma fidelity to match designs exactly
+- Avoid hardcoded values - use design tokens from Figma where available
+- When conflicts arise between design system tokens and Figma specs, prefer design system tokens but adjust spacing or sizes minimally to match visuals
+- Follow WCAG requirements for accessibility
+- Add component documentation as needed
+
+### Step 7: Validate Against Figma
+
+Before marking complete, validate the final UI against the Figma screenshot.
+
+**Validation checklist:**
+
+- [ ] Layout matches (spacing, alignment, sizing)
+- [ ] Typography matches (font, size, weight, line height)
+- [ ] Colors match exactly
+- [ ] Interactive states work as designed (hover, active, disabled)
+- [ ] Responsive behavior follows Figma constraints
+- [ ] Assets render correctly
+- [ ] Accessibility standards met
+
+## Implementation Rules
+
+### Component Organization
+
+- Place UI components in the project's designated design system directory
+- Follow the project's component naming conventions
+- Avoid inline styles unless truly necessary for dynamic values
+
+### Design System Integration
+
+- ALWAYS use components from the project's design system when possible
+- Map Figma design tokens to project design tokens
+- When a matching component exists, extend it rather than creating a new one
+- Document any new components added to the design system
+
+### Code Quality
+
+- Avoid hardcoded values - extract to constants or design tokens
+- Keep components composable and reusable
+- Add TypeScript types for component props
+- Include JSDoc comments for exported components
+
+## Examples
+
+### Example 1: Implementing a Button Component
+
+User says: "Implement this Figma button component: https://figma.com/design/kL9xQn2VwM8pYrTb4ZcHjF/DesignSystem?node-id=42-15"
+
+**Actions:**
+
+1. Parse URL to extract fileKey=`kL9xQn2VwM8pYrTb4ZcHjF` and nodeId=`42-15`
+2. Run `get_design_context(fileKey="kL9xQn2VwM8pYrTb4ZcHjF", nodeId="42-15")`
+3. Run `get_screenshot(fileKey="kL9xQn2VwM8pYrTb4ZcHjF", nodeId="42-15")` for visual reference
+4. Download any button icons from the assets endpoint
+5. Check if project has existing button component
+6. If yes, extend it with new variant; if no, create new component using project conventions
+7. Map Figma colors to project design tokens (e.g., `primary-500`, `primary-hover`)
+8. Validate against screenshot for padding, border radius, typography
+
+**Result:** Button component matching Figma design, integrated with project design system.
+
+### Example 2: Building a Dashboard Layout
+
+User says: "Build this dashboard: https://figma.com/design/pR8mNv5KqXzGwY2JtCfL4D/Dashboard?node-id=10-5"
+
+**Actions:**
+
+1. Parse URL to extract fileKey=`pR8mNv5KqXzGwY2JtCfL4D` and nodeId=`10-5`
+2. Run `get_metadata(fileKey="pR8mNv5KqXzGwY2JtCfL4D", nodeId="10-5")` to understand the page structure
+3. Identify main sections from metadata (header, sidebar, content area, cards) and their child node IDs
+4. Run `get_design_context(fileKey="pR8mNv5KqXzGwY2JtCfL4D", nodeId=":childNodeId")` for each major section
+5. Run `get_screenshot(fileKey="pR8mNv5KqXzGwY2JtCfL4D", nodeId="10-5")` for the full page
+6. Download all assets (logos, icons, charts)
+7. Build layout using project's layout primitives
+8. Implement each section using existing components where possible
+9. Validate responsive behavior against Figma constraints
+
+**Result:** Complete dashboard matching Figma design with responsive layout.
+
+## Best Practices
+
+### Always Start with Context
+
+Never implement based on assumptions. Always fetch `get_design_context` and `get_screenshot` first.
+
+### Incremental Validation
+
+Validate frequently during implementation, not just at the end. This catches issues early.
+
+### Document Deviations
+
+If you must deviate from the Figma design (e.g., for accessibility or technical constraints), document why in code comments.
+
+### Reuse Over Recreation
+
+Always check for existing components before creating new ones. Consistency across the codebase is more important than exact Figma replication.
+
+### Design System First
+
+When in doubt, prefer the project's design system patterns over literal Figma translation.
+
+## Common Issues and Solutions
+
+### Issue: Figma output is truncated
+
+**Cause:** The design is too complex or has too many nested layers to return in a single response.
+**Solution:** Use `get_metadata` to get the node structure, then fetch specific nodes individually with `get_design_context`.
+
+### Issue: Design doesn't match after implementation
+
+**Cause:** Visual discrepancies between the implemented code and the original Figma design.
+**Solution:** Compare side-by-side with the screenshot from Step 3. Check spacing, colors, and typography values in the design context data.
+
+### Issue: Assets not loading
+
+**Cause:** The Figma MCP server's assets endpoint is not accessible or the URLs are being modified.
+**Solution:** Verify the Figma MCP server's assets endpoint is accessible. The server serves assets at `localhost` URLs. Use these directly without modification.
+
+### Issue: Design token values differ from Figma
+
+**Cause:** The project's design system tokens have different values than those specified in the Figma design.
+**Solution:** When project tokens differ from Figma values, prefer project tokens for consistency but adjust spacing/sizing to maintain visual fidelity.
+
+## Understanding Design Implementation
+
+The Figma implementation workflow establishes a reliable process for translating designs to code:
+
+**For designers:** Confidence that implementations will match their designs with pixel-perfect accuracy.
+**For developers:** A structured approach that eliminates guesswork and reduces back-and-forth revisions.
+**For teams:** Consistent, high-quality implementations that maintain design system integrity.
+
+By following this workflow, you ensure that every Figma design is implemented with the same level of care and attention to detail.
+
+## Additional Resources
+
+- [Figma MCP Server Documentation](https://developers.figma.com/docs/figma-mcp-server/)
+- [Figma MCP Server Tools and Prompts](https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/)
+- [Figma Variables and Design Tokens](https://help.figma.com/hc/en-us/articles/15339657135383-Guide-to-variables-in-Figma)
PATCH

echo "Gold patch applied."
