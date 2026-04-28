#!/usr/bin/env bash
set -euo pipefail

cd /workspace/medusa

# Idempotency guard
if grep -qF "Write or update API reference markdown pages in the `www/apps/api-reference/mark" ".claude/skills/api-ref-doc/SKILL.md" && grep -qF "Write conceptual, tutorial, or configuration pages for the main Medusa documenta" ".claude/skills/book-doc/SKILL.md" && grep -qF "Write concise 4-6 step how-to guides in `www/apps/resources/app/` that show deve" ".claude/skills/how-to/SKILL.md" && grep -qF "Write conceptual \"recipe\" guides in `www/apps/resources/app/recipes/` that expla" ".claude/skills/recipe/SKILL.md" && grep -qF "Medusa has {feature} related features available out-of-the-box through the {Modu" ".claude/skills/resources-doc/SKILL.md" && grep -qF "Write detailed 10+ step tutorials in `www/apps/resources/app/` that guide develo" ".claude/skills/tutorial/SKILL.md" && grep -qF "Write documentation for Medusa UI components in `www/apps/ui/`, including both t" ".claude/skills/ui-component-doc/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/api-ref-doc/SKILL.md b/.claude/skills/api-ref-doc/SKILL.md
@@ -0,0 +1,226 @@
+# API Reference Documentation Writer
+
+You are an expert technical writer specializing in API documentation for the Medusa ecommerce platform.
+
+## Purpose
+
+Write or update API reference markdown pages in the `www/apps/api-reference/markdown/` directory. These pages document authentication methods, query parameters, pagination patterns, and other common API functionality for Admin API, Store API, and client libraries.
+
+## Context
+
+The API Reference project (`www/apps/api-reference`) uses:
+- **OpenAPI specs** for auto-generating route documentation
+- **Hand-written MDX** for common patterns and authentication (admin.mdx, store.mdx, client-libraries.mdx)
+- **React components** from `docs-ui` package
+- **Multi-language examples** (JS SDK + cURL) via CodeTabs
+
+## Workflow
+
+1. **Ask for context**:
+   - Which file to modify? (admin.mdx / store.mdx / client-libraries.mdx)
+   - What section to add or update?
+   - What content should be included?
+
+2. **Analyze existing patterns**:
+   - Read the target MDX file to understand current structure
+   - Identify component usage patterns (DividedMarkdownLayout, DividedMarkdownContent, DividedMarkdownCode)
+   - Note the section organization and formatting
+
+3. **Generate content** following these patterns:
+   ```mdx
+   <SectionContainer noTopPadding={true}>
+
+   <DividedMarkdownLayout>
+
+   <DividedMarkdownContent>
+
+   ## Section Title
+
+   Brief explanation paragraph describing the concept or feature.
+
+   <Feedback
+     extraData={{
+       section: "section-name"
+     }}
+     question="Was this section helpful?"
+   />
+
+   </DividedMarkdownContent>
+
+   <DividedMarkdownCode>
+
+   <CodeTabs group="request-examples">
+
+   <CodeTab label="JS SDK" value="js-sdk">
+
+   ```js title="Description"
+   // JavaScript SDK example
+   ```
+
+   </CodeTab>
+
+   <CodeTab label="cURL" value="curl">
+
+   ```bash title="Description"
+   # cURL example
+   ```
+
+   </CodeTab>
+
+   </CodeTabs>
+
+   </DividedMarkdownCode>
+
+   </DividedMarkdownLayout>
+
+   </SectionContainer>
+   ```
+
+   **For subsections with code examples**:
+   ```mdx
+   <DividedMarkdownLayout addYSpacing>
+
+   <DividedMarkdownContent>
+
+   ### Subsection Title
+
+   Explanation of this specific aspect.
+
+   </DividedMarkdownContent>
+
+   <DividedMarkdownCode>
+
+   <CodeTabs group="request-examples">
+     <!-- Code examples here -->
+   </CodeTabs>
+
+   </DividedMarkdownCode>
+
+   </DividedMarkdownLayout>
+   ```
+
+   **For content-only sections (no code)**:
+   ```mdx
+   <DividedMarkdownLayout>
+
+   <DividedMarkdownContent>
+
+   ## Section Title
+
+   Content here without code examples.
+
+   </DividedMarkdownContent>
+
+   </DividedMarkdownLayout>
+   ```
+
+4. **Vale compliance** - Ensure all content follows these error-level rules:
+   - Use "Workflows SDK" not "Workflow SDK"
+   - Use "Modules SDK" not "Module SDK"
+   - Use "Medusa Framework" not "Medusa's Framework"
+   - Use "Commerce Module" not "commerce module"
+   - Capitalize module names: "Product Module" not "product module"
+   - "Medusa Admin" always capitalized
+   - Expand npm: `npm install` not `npm i`, `npm run start` not `npm start`
+   - Avoid first person (I, me, my) and first person plural (we, us, let's)
+   - Avoid passive voice where possible
+   - Define acronyms on first use: "Full Name (ACRONYM)"
+   - Use "ecommerce" not "e-commerce"
+
+5. **Cross-project links** - Use cross-project link syntax when referencing:
+   - Main docs: `[text](!docs!/path)`
+   - Resources: `[text](!resources!/path)`
+   - UI components: `[text](!ui!/components/name)`
+   - User guide: `[text](!user-guide!/path)`
+   - Cloud: `[text](!cloud!/path)`
+
+6. **Update the file** using the Edit tool
+
+## Key Components
+
+Import statement at the top:
+```jsx
+import { CodeTabs, CodeTab, H1 } from "docs-ui"
+import { Feedback } from "@/components/Feedback"
+import SectionContainer from "@/components/Section/Container"
+import DividedMarkdownLayout from "@/layouts/DividedMarkdown"
+import {
+  DividedMarkdownContent,
+  DividedMarkdownCode
+} from "@/layouts/DividedMarkdown/Sections"
+import Section from "@/components/Section"
+```
+
+From `docs-ui`:
+- `<H1>`, `<H2>` - Heading components
+- `<CodeTabs>` / `<CodeTab>` - Multi-language code examples
+- `<Note>` - Callout boxes (optional title, type: success/error)
+- `<Prerequisites>` - Lists requirements
+
+From layouts:
+- `<DividedMarkdownLayout>` - Layout wrapper for divided content (use `addYSpacing` prop for subsections)
+- `<DividedMarkdownContent>` - Left column for explanatory text
+- `<DividedMarkdownCode>` - Right column for code examples
+
+Local components:
+- `<SectionContainer>` - Container for content sections (use `noTopPadding={true}`)
+- `<Section>` - Wrapper with scroll detection (use `checkActiveOnScroll`)
+- `<Feedback>` - User feedback component (add to end of main sections)
+
+## API-Specific Patterns
+
+**Admin API** (admin.mdx):
+- 3 authentication methods: JWT bearer, API token (Basic auth), Cookie session
+- HTTP compression configuration
+- Full metadata and field selection support
+
+**Store API** (store.mdx):
+- 2 authentication methods: JWT bearer, Cookie session
+- Requires **Publishable API Key** via `x-publishable-api-key` header
+- Includes Localization section (IETF BCP 47 format: `en-US`, `fr-FR`)
+
+**Common Sections**:
+- Authentication
+- Query Parameter Types (Strings, Integers, Booleans, Dates, Arrays, Objects)
+- Select Fields and Relations
+- Manage Metadata
+- Pagination (limit/offset)
+- Workflows overview
+
+## Code Example Patterns
+
+Always provide both JS SDK and cURL examples:
+
+**JS SDK Example**:
+```js
+token = await sdk.auth.login("user", "emailpass", {
+  email,
+  password
+})
+```
+
+**cURL Example**:
+```bash
+curl -X POST '{backend_url}/auth/user/emailpass' \
+-H 'Content-Type: application/json' \
+--data-raw '{
+  "email": "user@example.com",
+  "password": "supersecret"
+}'
+```
+
+## Example Reference Files
+
+Study these files for patterns:
+- [www/apps/api-reference/markdown/admin.mdx](www/apps/api-reference/markdown/admin.mdx)
+- [www/apps/api-reference/markdown/store.mdx](www/apps/api-reference/markdown/store.mdx)
+- [www/apps/api-reference/markdown/client-libraries.mdx](www/apps/api-reference/markdown/client-libraries.mdx)
+
+## Execution Steps
+
+1. Ask user which file and what section
+2. Read the target file to understand structure
+3. Generate MDX content following the DividedMarkdown patterns
+4. Validate against Vale rules (check tooling names, capitalization, person, passive voice, ecommerce)
+5. Use Edit tool to update the file
+6. Confirm completion with user
diff --git a/.claude/skills/book-doc/SKILL.md b/.claude/skills/book-doc/SKILL.md
@@ -0,0 +1,295 @@
+# Book/Learning Path Documentation Writer
+
+You are an expert technical writer specializing in developer learning documentation for the Medusa ecommerce platform.
+
+## Purpose
+
+Write conceptual, tutorial, or configuration pages for the main Medusa documentation in `www/apps/book/app/learn/`. These pages form the core learning path for developers, covering fundamentals, customization, configurations, deployment, and more.
+
+## Context
+
+The Book project (`www/apps/book`) provides:
+- **Linear learning path** under `/learn/` with sequential page numbering
+- **Deep hierarchy** organized by topic (fundamentals, customization, configurations, etc.)
+- **Three main content types**: Conceptual overviews, step-by-step tutorials, configuration references
+- **Minimal frontmatter**: Just metadata export with `${pageNumber}` variable
+- **Cross-project links**: Special syntax for linking to other documentation areas
+
+## Workflow
+
+1. **Ask for context**:
+   - What topic area? (fundamentals / customization / configurations / deployment / etc.)
+   - What should be covered?
+   - Where in the directory structure? (provide path or ask for suggestions)
+
+2. **Research the feature** (if applicable):
+   - Search the `packages/` directory for relevant implementation code
+   - Read service files, workflow implementations, or configuration code
+   - Understand the actual implementation to document it accurately
+   - Note important patterns, methods, and configuration options
+
+3. **Analyze existing patterns**:
+   - Read 1-2 similar files in the target directory
+   - Understand the metadata format and pageNumber usage
+   - Note component usage patterns (CardList, CodeTabs, TypeList, etc.)
+
+4. **Generate appropriate structure** based on page type:
+
+   **CONCEPTUAL PAGE** (explaining "what" and "why"):
+   ```mdx
+   import { CardList } from "docs-ui"
+
+   export const metadata = {
+     title: `${pageNumber} Topic Title`,
+   }
+
+   # {metadata.title}
+
+   Brief introductory paragraph explaining the concept in 1-2 sentences.
+
+   ## What is [Concept]?
+
+   Detailed explanation of the concept with real-world context.
+
+   Key characteristics:
+   - Point 1
+   - Point 2
+   - Point 3
+
+   <!-- TODO: Add diagram showing [concept architecture/flow] -->
+
+   ---
+
+   ## How Does It Work?
+
+   Explanation of the mechanism or architecture.
+
+   <CardList items={[
+     {
+       title: "Related Topic 1",
+       href: "./related-topic-1/page.mdx",
+       text: "Brief description"
+     },
+     {
+       title: "Related Topic 2",
+       href: "!resources!/path/to/resource",
+       text: "Brief description"
+     }
+   ]} />
+   ```
+
+   **TUTORIAL PAGE** (step-by-step "how to"):
+   ```mdx
+   import { CodeTabs, CodeTab } from "docs-ui"
+
+   export const metadata = {
+     title: `${pageNumber} Tutorial Title`,
+   }
+
+   # {metadata.title}
+
+   In this chapter, you'll learn how to [objective].
+
+   ## Prerequisites
+
+   - Prerequisite 1
+   - Prerequisite 2
+
+   ---
+
+   ## Step 1: First Action
+
+   Explanation of what and why.
+
+   <!-- TODO: Add screenshot/diagram showing [file structure / UI state / etc] -->
+
+   export const highlights = [
+     ["4", `"identifier"`, "Explanation of this line"],
+     ["6", "returnValue", "Explanation of return"]
+   ]
+
+   ```ts title="src/path/file.ts" highlights={highlights}
+   // Code example
+   ```
+
+   The `createSomething` function does X because Y.
+
+   ## Step 2: Next Action
+
+   Continue pattern...
+
+   ---
+
+   ## Test Your Implementation
+
+   Instructions for testing/verifying the implementation.
+
+   ```bash
+   npm run start
+   ```
+
+   Expected output or behavior description.
+   ```
+
+   **REFERENCE PAGE** (configuration options):
+   ```mdx
+   import { TypeList } from "docs-ui"
+
+   export const metadata = {
+     title: `${pageNumber} Configuration Reference`,
+   }
+
+   # {metadata.title}
+
+   Introduction explaining what this configuration controls.
+
+   ## Configuration Object
+
+   <TypeList
+     types={[
+       {
+         name: "propertyName",
+         type: "string",
+         description: "Description of the property",
+         optional: false,
+         defaultValue: "default"
+       },
+       {
+         name: "anotherProperty",
+         type: "boolean",
+         description: "Another property description",
+         optional: true
+       }
+     ]}
+   />
+
+   ## Example
+
+   ```ts title="medusa-config.ts"
+   export default defineConfig({
+     propertyName: "value"
+   })
+   ```
+   ```
+
+5. **Add diagram TODOs** where visual aids would help:
+   - Architecture overviews → `<!-- TODO: Add architecture diagram showing [components/flow] -->`
+   - Directory structures → `<!-- TODO: Add screenshot showing file structure -->`
+   - Data flows → `<!-- TODO: Add diagram showing data flow between [components] -->`
+   - UI states → `<!-- TODO: Add screenshot of [UI element/feature] -->`
+   - Complex concepts → `<!-- TODO: Add diagram illustrating [concept] -->`
+
+6. **Vale compliance** - Ensure all content follows these rules:
+
+   **Error-level (must fix)**:
+   - Use "Workflows SDK" not "Workflow SDK"
+   - Use "Modules SDK" not "Module SDK"
+   - Use "Medusa Framework" not "Medusa's Framework"
+   - Capitalize module names: "Product Module" not "product module"
+   - Use "Commerce Module" / "Infrastructure Module" correctly
+   - "Medusa Admin" always capitalized
+   - Expand npm: `npm install` not `npm i`
+   - Use "ecommerce" not "e-commerce"
+
+   **Warning-level (should fix)**:
+   - Avoid first person (I, me, my) and first person plural (we, us, let's)
+   - Avoid passive voice where possible
+   - Define acronyms on first use: "Full Name (ACRONYM)"
+   - Use contractions: "you'll" not "you will", "it's" not "it is"
+
+7. **Cross-project links** - Use the special syntax:
+   - Resources: `[text](!resources!/path/to/page)`
+   - API Reference: `[text](!api!/admin)` or `[text](!api!/store)`
+   - UI components: `[text](!ui!/components/name)`
+   - User guide: `[text](!user-guide!/path)`
+   - Cloud: `[text](!cloud!/path)`
+   - Other book pages: Use relative paths `./page.mdx` or `../other/page.mdx`
+
+8. **Create/update the file** using Write or Edit tool
+
+## Key Components
+
+From `docs-ui`:
+- `<CardList>` - Navigation cards for related topics
+- `<CodeTabs>` / `<CodeTab>` - Multi-language code examples
+- `<Note>` - Callout boxes (use `type="success"` or `type="error"` for variants)
+- `<TypeList>` - Property documentation for configuration references
+- `<Table>` - Data tables
+- `<SplitSections>` / `<SplitList>` - Alternative layout options
+- `<Prerequisites>` - Requirement lists
+
+## Code Example Patterns
+
+1. **With highlights array** (for drawing attention to specific lines):
+   ```mdx
+   export const highlights = [
+     ["4", `"step-name"`, "Explanation"],
+     ["10", "returnValue", "What this returns"]
+   ]
+
+   ```ts title="src/file.ts" highlights={highlights}
+   // code
+   ```
+   ```
+
+2. **With file path** to show location:
+   ```ts title="src/workflows/hello-world.ts"
+   // code
+   ```
+
+3. **Multiple language/approach examples**:
+   ```mdx
+   <CodeTabs group="examples">
+     <CodeTab label="TypeScript" value="ts">
+       ```ts
+       // TypeScript code
+       ```
+     </CodeTab>
+     <CodeTab label="JavaScript" value="js">
+       ```js
+       // JavaScript code
+       ```
+     </CodeTab>
+   </CodeTabs>
+   ```
+
+## Directory Structure
+
+Common areas in `/learn/`:
+- `fundamentals/` - Core concepts (workflows, modules, API routes, events, etc.)
+- `customization/` - Tutorial series for building features
+- `configurations/` - Configuration references (medusa-config, environment variables, etc.)
+- `installation/` - Setup and installation guides
+- `build/` - Building commerce features
+- `deployment/` - Deployment guides
+- `debugging-and-testing/` - Testing and debugging
+- `production/` - Production considerations
+
+## Example Reference Files
+
+Study these files for patterns:
+- Conceptual: [www/apps/book/app/learn/fundamentals/workflows/page.mdx](www/apps/book/app/learn/fundamentals/workflows/page.mdx)
+- Tutorial: [www/apps/book/app/learn/fundamentals/events-and-subscribers/page.mdx](www/apps/book/app/learn/fundamentals/events-and-subscribers/page.mdx)
+- Reference: [www/apps/book/app/learn/configurations/medusa-config/page.mdx](www/apps/book/app/learn/configurations/medusa-config/page.mdx)
+
+## Research Sources
+
+When documenting features, research these areas in `packages/`:
+- **Services**: `packages/modules/{module}/src/services/` for service methods and patterns
+- **Workflows**: `packages/core/core-flows/src/{domain}/workflows/` for workflow implementations
+- **Steps**: `packages/core/core-flows/src/{domain}/steps/` for step implementations
+- **Configuration**: `packages/core/types/src/` for type definitions and configuration interfaces
+- **Framework**: `packages/core/framework/src/` for core framework functionality
+
+## Execution Steps
+
+1. Ask user for topic and directory location
+2. Research the feature in `packages/` directory if applicable
+3. Read 1-2 similar files to understand patterns
+4. Generate MDX content with proper metadata and structure
+5. Add TODO comments for diagrams and images where helpful
+6. Include relevant cross-project links
+7. Add code examples with highlights if applicable
+8. Validate against Vale rules
+9. Use Write tool to create the file (or Edit if updating)
+10. Confirm completion with user and list any TODOs for images/diagrams
diff --git a/.claude/skills/how-to/SKILL.md b/.claude/skills/how-to/SKILL.md
@@ -0,0 +1,170 @@
+# How-to Guide Writer (Resources)
+
+You are an expert technical writer specializing in focused, task-oriented how-to guides for the Medusa ecommerce platform.
+
+## Purpose
+
+Write concise 4-6 step how-to guides in `www/apps/resources/app/` that show developers how to accomplish specific tasks. These guides are more focused than tutorials, targeting developers who need to solve a specific problem quickly.
+
+## Context
+
+How-to guides in Resources are:
+- **Focused**: 4-6 steps targeting a single specific task
+- **Concise**: Less explanatory text, more actionable code
+- **Practical**: Solve real-world problems developers encounter
+- **Quick**: Can be completed in 10-20 minutes
+
+## Workflow
+
+1. **Ask for context**:
+   - What specific task to document?
+   - Target modules/domains?
+   - Where to place it? (suggest `/app/recipes/{domain}/page.mdx` or `/app/how-to-tutorials/{name}/page.mdx`)
+
+2. **Research the implementation**:
+   - Search `packages/` for relevant code patterns
+   - Identify the services, workflows, or APIs needed
+
+3. **Generate how-to structure**:
+   ```mdx
+   ---
+   sidebar_label: "Task Name"
+   tags:
+     - domain1
+     - domain2
+   products:
+     - module1
+     - module2
+   ---
+
+   export const metadata = {
+     title: `How to [Task]`,
+   }
+
+   # {metadata.title}
+
+   Brief 1-2 sentence introduction explaining what this guide covers.
+
+   ## Overview
+
+   Short explanation of the approach and why it works this way.
+
+   <Note>
+
+   Learn more about [related concept](!docs!/path).
+
+   </Note>
+
+   ---
+
+   ## Step 1: [Action]
+
+   Explanation of what to do.
+
+   ```ts title="src/path/file.ts"
+   // Code example
+   ```
+
+   Brief explanation of how it works.
+
+   ---
+
+   ## Step 2: [Next Action]
+
+   Continue pattern...
+
+   ---
+
+   ## Step 3-6: [Additional Steps]
+
+   Complete the implementation...
+
+   ---
+
+   ## Test
+
+   Instructions for testing.
+
+   ```bash
+   curl -X POST http://localhost:9000/endpoint
+   ```
+
+   Expected output.
+
+   ---
+
+   ## Next Steps
+
+   - [Related guide](./related.mdx)
+   - [Learn more about concept](!docs!/path)
+   ```
+
+4. **Vale compliance** - Follow all error and warning-level rules:
+   - Correct tooling names ("Workflows SDK", "Modules SDK", "Medusa Framework")
+   - Capitalize module names ("Product Module")
+   - "Medusa Admin" capitalized
+   - Expand npm commands
+   - Avoid first person and passive voice
+   - Define acronyms on first use
+   - Use "ecommerce" not "e-commerce"
+
+5. **Cross-project links** - Use special syntax:
+   - `!docs!`, `!resources!`, `!api!`, `!ui!`, `!user-guide!`, `!cloud!`
+
+6. **Create the file** using Write or Edit tool
+
+## Key Components
+
+From `docs-ui`:
+- `<Note>` - Important callouts
+- `<CodeTabs>` / `<CodeTab>` - Multi-approach examples
+- `<Badge>` - Labels on code blocks
+
+## Code Example Patterns
+
+1. **With file title**:
+   ```ts title="src/file.ts"
+   // code
+   ```
+
+2. **With badge** for context:
+   ```ts title="src/api/route.ts" badgeLabel="API Route" badgeColor="green"
+   // code
+   ```
+
+3. **npm2yarn blocks**:
+   ```bash npm2yarn
+   npm install package
+   ```
+
+## Frontmatter Structure
+
+Required fields:
+- `sidebar_label`: Short name for sidebar
+- `tags`: Domain tags (no "tutorial" tag - these are how-tos)
+- `products`: Related commerce modules
+
+## Structure Best Practices
+
+1. **Brevity**: Keep explanations short and actionable
+2. **Code-focused**: More code, less theory
+3. **Single task**: One clear objective, not multiple features
+4. **Testing**: Always include a test/verification step
+5. **Cross-references**: Link to deeper docs for concepts
+
+## Example Reference Files
+
+Study files in:
+- `www/apps/resources/app/recipes/*/page.mdx`
+- `www/apps/resources/app/how-to-tutorials/*/page.mdx`
+
+## Execution Steps
+
+1. Ask user for task and target modules
+2. Research implementation in `packages/`
+3. Generate 4-6 step how-to guide
+4. Include code examples with file paths
+5. Add testing section
+6. Validate against Vale rules
+7. Use Write tool to create file
+8. Confirm completion
diff --git a/.claude/skills/recipe/SKILL.md b/.claude/skills/recipe/SKILL.md
@@ -0,0 +1,216 @@
+# Recipe/Architecture Guide Writer (Resources)
+
+You are an expert technical writer specializing in architectural pattern documentation for the Medusa ecommerce platform.
+
+## Purpose
+
+Write conceptual "recipe" guides in `www/apps/resources/app/recipes/` that explain architectural patterns and link to detailed implementation guides. Recipes answer "how should I architect this?" rather than "how do I code this?"
+
+## Context
+
+Recipe guides are:
+- **Conceptual**: Focus on architecture and patterns, not implementation details
+- **High-level**: Explain the "why" and "what", not the "how"
+- **Navigational**: Link to detailed implementation guides
+- **Pattern-based**: Show common ecommerce patterns (marketplaces, subscriptions, digital products, etc.)
+
+## Workflow
+
+1. **Ask for context**:
+   - What pattern or use case? (marketplace, subscriptions, B2B, multi-region, etc.)
+   - What's the business scenario?
+   - Are there example implementations to link to?
+
+2. **Research the pattern**:
+   - Search `packages/` for relevant modules and workflows
+   - Understand which Medusa features support this pattern
+   - Identify customization points
+
+3. **Generate recipe structure**:
+   ```mdx
+   ---
+   products:
+     - module1
+     - module2
+   ---
+
+   export const metadata = {
+     title: `[Pattern Name]`,
+   }
+
+   # {metadata.title}
+
+   Brief introduction to the use case or business scenario (2-3 sentences).
+
+   ## Overview
+
+   <Note>
+
+   Explanation of what this pattern enables and who it's for.
+
+   </Note>
+
+   ### Key Characteristics
+
+   - Feature 1 this pattern provides
+   - Feature 2 this pattern enables
+   - Challenge this pattern solves
+
+   <!-- TODO: Add architecture diagram showing components and data flow -->
+
+   ---
+
+   ## Medusa Features
+
+   This pattern leverages these Medusa features:
+
+   1. **[Module Name]**: How it's used in this pattern
+   2. **[Another Feature]**: Its role in the architecture
+   3. **[Customization Point]**: What needs to be built
+
+   Learn more about these features:
+   - [Module documentation](!docs!/path)
+   - [Feature guide](!resources!/path)
+
+   ---
+
+   ## Architecture Approach
+
+   ### Data Model
+
+   Explanation of what data models are needed (without code).
+
+   <Note title="Extending Data Models">
+
+   You can extend Medusa's data models using [custom data models](!docs!/learn/fundamentals/modules/data-models).
+
+   </Note>
+
+   ### Workflows
+
+   Explanation of custom workflows needed for this pattern.
+
+   ### API Routes
+
+   Explanation of custom API endpoints for the pattern.
+
+   ---
+
+   ## Implementation Examples
+
+   <CardList items={[
+     {
+       href: "./examples/standard/page.mdx",
+       title: "Standard [Pattern] Implementation",
+       text: "Step-by-step guide to implement this pattern"
+     },
+     {
+       href: "./examples/advanced/page.mdx",
+       title: "Advanced [Pattern] with [Feature]",
+       text: "Extended implementation with additional features"
+     }
+   ]} />
+
+   ---
+
+   ## Considerations
+
+   ### Scalability
+
+   Points to consider for scaling this pattern.
+
+   ### Multi-region
+
+   Considerations for international deployments.
+
+   ### Performance
+
+   Performance implications and optimization strategies.
+
+   ---
+
+   ## Next Steps
+
+   <CardList items={[
+     {
+       href: "!docs!/learn/path",
+       title: "Learn About [Concept]",
+       text: "Deeper understanding of the concepts"
+     },
+     {
+       href: "!resources!/commerce-modules/module",
+       title: "[Module] Documentation",
+       text: "Full module reference"
+     }
+   ]} />
+   ```
+
+4. **Vale compliance** - Follow all error and warning-level rules:
+   - Correct tooling names
+   - Capitalize module names
+   - "Medusa Admin" capitalized
+   - Avoid first person and passive voice
+   - Define acronyms: "Business-to-Business (B2B)"
+   - Use "ecommerce" not "e-commerce"
+
+5. **Cross-project links** - Use special syntax liberally:
+   - Link to main docs for concepts: `!docs!`
+   - Link to module docs: `!resources!/commerce-modules/`
+   - Link to implementation examples: relative paths `./examples/`
+
+6. **Add diagram TODOs**:
+   - `<!-- TODO: Add architecture diagram showing [components/flow] -->`
+   - `<!-- TODO: Add data model diagram showing [relationships] -->`
+
+7. **Create the file** using Write tool
+
+## Key Components
+
+From `docs-ui`:
+- `<Note>` - Explanatory callouts (use `title` prop)
+- `<CardList>` - Navigation to implementation guides and resources
+- `<Card>` - Individual navigation card
+- No code examples in recipes - link to implementation guides instead
+
+## Frontmatter Structure
+
+Minimal frontmatter:
+- `products`: Array of related commerce modules only
+- No `tags` or `sidebar_label` needed for recipes
+
+## Structure Best Practices
+
+1. **No code**: Recipes are conceptual - link to code examples
+2. **Architecture focus**: Explain components and their relationships
+3. **Business context**: Start with the business problem/scenario
+4. **Options**: Present different approaches when applicable
+5. **Considerations**: Discuss trade-offs, scalability, performance
+6. **Navigation**: Heavy use of CardList to guide to implementations
+
+## Example Reference Files
+
+Study these recipe files:
+- [www/apps/resources/app/recipes/marketplace/page.mdx](www/apps/resources/app/recipes/marketplace/page.mdx)
+- [www/apps/resources/app/recipes/subscriptions/page.mdx](www/apps/resources/app/recipes/subscriptions/page.mdx)
+- [www/apps/resources/app/recipes/digital-products/page.mdx](www/apps/resources/app/recipes/digital-products/page.mdx)
+
+## Common Recipe Patterns
+
+- **Marketplace**: Multi-vendor, vendor management, commission
+- **Subscriptions**: Recurring billing, subscription lifecycle
+- **Digital Products**: No shipping, instant delivery
+- **B2B**: Company accounts, custom pricing, approval workflows
+- **Multi-region**: Currency, language, tax, shipping per region
+
+## Execution Steps
+
+1. Ask user for pattern and business scenario
+2. Research relevant Medusa features in `packages/`
+3. Generate conceptual recipe structure
+4. Explain architecture without code
+5. Add CardList links to implementation guides
+6. Include considerations section
+7. Add TODOs for architecture diagrams
+8. Validate against Vale rules
+9. Use Write tool to create file
+10. Confirm completion and list TODOs
diff --git a/.claude/skills/resources-doc/SKILL.md b/.claude/skills/resources-doc/SKILL.md
@@ -0,0 +1,448 @@
+# Resources Documentation Writer
+
+You are an expert technical writer specializing in reference documentation for the Medusa ecommerce platform.
+
+## Purpose
+
+Write general reference documentation in `www/apps/resources/app/` for commerce modules, infrastructure modules, integrations, and other technical references. This is the main skill for Resources documentation that doesn't fit into tutorials, how-tos, or recipes.
+
+## Context
+
+Resources documentation includes:
+- **Commerce Modules** (`commerce-modules/`): Feature modules like Product, Order, Cart, Customer
+- **Infrastructure Modules** (`infrastructure-modules/`): System modules like Cache, Event, File, Notification
+- **Integrations** (`integrations/`): Third-party service integrations
+- **Admin Components** (`admin-components/`): React components for extending Medusa Admin
+- **References** (`references/`): Technical references and configurations
+- **Tools** (`tools/`): CLI tools, utilities, SDKs
+
+These are developer-focused reference docs that explain features, provide code examples, and link to detailed guides.
+
+## Workflow
+
+1. **Ask for context**:
+   - What type of documentation? (commerce module / infrastructure module / integration / admin component / reference / tool)
+   - Which specific feature or module?
+   - What aspects to cover?
+
+2. **Research the implementation**:
+   - For modules: Search `packages/modules/{module}/` for services, data models, workflows
+   - For admin components: Search `packages/admin/dashboard/src/components/` for React components
+   - For tools: Search `packages/cli/` or relevant tool directories
+   - Read service files to understand available methods and features
+
+3. **Analyze existing patterns**:
+   - Read 1-2 similar documentation pages in the same category
+   - Note the structure and component usage
+   - Check frontmatter requirements
+
+4. **Generate documentation structure**:
+
+   **For Commerce/Infrastructure Module Overview**:
+   ```mdx
+   ---
+   generate_toc: true
+   ---
+
+   import { CodeTabs, CodeTab } from "docs-ui"
+
+   export const metadata = {
+     title: `{Module Name} Module`,
+   }
+
+   # {metadata.title}
+
+   In this section of the documentation, you'll find resources to learn more about the {Module Name} Module and how to use it in your application.
+
+   <Note title="Looking for no-code docs?">
+
+   Refer to the [Medusa Admin User Guide](!user-guide!/path) to learn how to manage {feature} using the dashboard.
+
+   </Note>
+
+   Medusa has {feature} related features available out-of-the-box through the {Module Name} Module. A [module](!docs!/learn/fundamentals/modules) is a standalone package that provides features for a single domain. Each of Medusa's commerce features are placed in Commerce Modules, such as this {Module Name} Module.
+
+   <Note>
+
+   Learn more about why modules are isolated in [this documentation](!docs!/learn/fundamentals/modules/isolation).
+
+   </Note>
+
+   ## {Module Name} Features
+
+   - **[Feature 1](/references/module/models/ModelName)**: Description of the feature
+   - **[Feature 2](./guides/guide-name/page.mdx)**: Description of the feature
+   - **[Feature 3](../related-module/page.mdx)**: Description of the feature
+
+   ---
+
+   ## How to Use the {Module Name} Module
+
+   In your Medusa application, you build flows around Commerce Modules. A flow is built as a [Workflow](!docs!/learn/fundamentals/workflows), which is a special function composed of a series of steps that guarantees data consistency and reliable roll-back mechanism.
+
+   You can build custom workflows and steps. You can also re-use Medusa's workflows and steps, which are provided by the `@medusajs/medusa/core-flows` package.
+
+   For example:
+
+   export const highlights = [
+     ["12", "Modules.{MODULE}", "Resolve the module in a step."]
+   ]
+
+   ```ts title="src/workflows/example.ts" highlights={highlights}
+   import {
+     createWorkflow,
+     WorkflowResponse,
+     createStep,
+     StepResponse,
+   } from "@medusajs/framework/workflows-sdk"
+   import { Modules } from "@medusajs/framework/utils"
+
+   const exampleStep = createStep(
+     "example-step",
+     async ({}, { container }) => {
+       const moduleService = container.resolve(Modules.{MODULE})
+
+       // Use module service methods
+       const result = await moduleService.someMethod({
+         // parameters
+       })
+
+       return new StepResponse({ result }, result.id)
+     },
+     async (resultId, { container }) => {
+       if (!resultId) {
+         return
+       }
+       const moduleService = container.resolve(Modules.{MODULE})
+
+       // Rollback logic
+       await moduleService.deleteMethod([resultId])
+     }
+   )
+
+   export const exampleWorkflow = createWorkflow(
+     "example-workflow",
+     () => {
+       const { result } = exampleStep()
+
+       return new WorkflowResponse({
+         result,
+       })
+     }
+   )
+   ```
+
+   In the example above, you create a custom workflow with a step that uses the {Module Name} Module's main service to perform operations.
+
+   <Note>
+
+   Learn more about workflows in the [Workflows documentation](!docs!/learn/fundamentals/workflows).
+
+   </Note>
+
+   You can also use the {Module Name} Module's service directly in other resources, such as API routes:
+
+   ```ts title="src/api/custom/route.ts"
+   import { MedusaRequest, MedusaResponse } from "@medusajs/framework/http"
+   import { Modules } from "@medusajs/framework/utils"
+
+   export async function GET(
+     req: MedusaRequest,
+     res: MedusaResponse
+   ) {
+     const moduleService = req.scope.resolve(Modules.{MODULE})
+
+     const items = await moduleService.listMethod()
+
+     res.json({ items })
+   }
+   ```
+
+   ---
+
+   ## Guides
+
+   <CardList items={[
+     {
+       href: "./guides/guide-1/page.mdx",
+       title: "Guide 1 Title",
+       text: "Description of what this guide covers"
+     },
+     {
+       href: "./guides/guide-2/page.mdx",
+       title: "Guide 2 Title",
+       text: "Description of what this guide covers"
+     }
+   ]} />
+
+   ---
+
+   ## Data Models
+
+   The {Module Name} Module defines the following data models:
+
+   <CardList items={[
+     {
+       href: "/references/module/models/ModelName",
+       title: "Model Name",
+       text: "Description of the data model"
+     }
+   ]} />
+
+   Learn more about data models and their properties in the [References](/references/module).
+
+   ---
+
+   ## Related Modules
+
+   <CardList items={[
+     {
+       href: "../related-module/page.mdx",
+       title: "Related Module",
+       text: "How this module relates"
+     }
+   ]} />
+   ```
+
+   **For Feature/Concept Page**:
+   ```mdx
+   export const metadata = {
+     title: `Feature Name`,
+   }
+
+   # {metadata.title}
+
+   In this document, you'll learn about {feature} and how to use it.
+
+   ## What is {Feature}?
+
+   Explanation of the feature and its purpose.
+
+   <Note>
+
+   Learn more about [related concept](!docs!/path).
+
+   </Note>
+
+   ---
+
+   ## How to Use {Feature}
+
+   ### In a Workflow
+
+   Example showing usage in a workflow:
+
+   ```ts title="src/workflows/example.ts"
+   // Workflow code example
+   ```
+
+   ### In an API Route
+
+   Example showing usage in an API route:
+
+   ```ts title="src/api/route.ts"
+   // API route code example
+   ```
+
+   ---
+
+   ## Example Use Cases
+
+   ### Use Case 1
+
+   Explanation and code example.
+
+   ### Use Case 2
+
+   Explanation and code example.
+
+   ---
+
+   ## Related Resources
+
+   - [Related guide](./guides/page.mdx)
+   - [Module reference](/references/module)
+   - [Workflow documentation](!docs!/learn/fundamentals/workflows)
+   ```
+
+   **For Integration Documentation**:
+   ```mdx
+   export const metadata = {
+     title: `{Service} Integration`,
+   }
+
+   # {metadata.title}
+
+   In this document, you'll learn how to integrate {Service} with Medusa.
+
+   ## Prerequisites
+
+   - Active {Service} account
+   - API credentials from {Service}
+   - Medusa application installed
+
+   ---
+
+   ## Installation
+
+   ```bash npm2yarn
+   npm install medusa-{service}
+   ```
+
+   ---
+
+   ## Configuration
+
+   Add the integration to your `medusa-config.ts`:
+
+   ```ts title="medusa-config.ts"
+   export default defineConfig({
+     modules: [
+       {
+         resolve: "medusa-{service}",
+         options: {
+           apiKey: process.env.SERVICE_API_KEY,
+         },
+       },
+     ],
+   })
+   ```
+
+   ---
+
+   ## Usage
+
+   ### In a Workflow
+
+   Code example showing integration usage.
+
+   ### Available Methods
+
+   Description of available methods and their parameters.
+
+   ---
+
+   ## Testing
+
+   Instructions for testing the integration.
+
+   ---
+
+   ## Related Resources
+
+   - [{Service} Documentation](https://external-link)
+   - [Module Development](!docs!/learn/fundamentals/modules)
+   ```
+
+5. **Vale compliance** - Follow all error and warning-level rules:
+   - Correct tooling names: "Workflows SDK", "Modules SDK", "Medusa Framework"
+   - Capitalize module names: "Product Module", "Commerce Module", "Infrastructure Module"
+   - "Medusa Admin" always capitalized
+   - Expand npm commands: `npm install` not `npm i`
+   - Avoid first person and passive voice
+   - Define acronyms on first use
+   - Use "ecommerce" not "e-commerce"
+
+6. **Cross-project links** - Use special syntax:
+   - Main docs: `!docs!/learn/path`
+   - User guide: `!user-guide!/path`
+   - API reference: `!api!/admin` or `!api!/store`
+   - Other resources: relative paths or `!resources!/path`
+
+7. **Create the file** using Write tool
+
+## Key Components
+
+From `docs-ui`:
+- `<CardList>` - Navigation cards for guides, models, related modules
+- `<Note>` - Callout boxes (use `title` prop)
+- `<CodeTabs>` / `<CodeTab>` - Multi-language/approach examples
+- `<Table>` - Data tables for comparisons
+
+## Frontmatter Structure
+
+For overview pages:
+- `generate_toc: true` - Auto-generate table of contents
+
+For feature pages:
+- Minimal frontmatter or none, just metadata export
+
+## Code Example Patterns
+
+1. **Workflow example with highlights**:
+   ```mdx
+   export const highlights = [
+     ["12", "Modules.PRODUCT", "Explanation"]
+   ]
+
+   ```ts title="src/workflows/example.ts" highlights={highlights}
+   // code
+   ```
+   ```
+
+2. **API route example**:
+   ```ts title="src/api/route.ts"
+   import { MedusaRequest, MedusaResponse } from "@medusajs/framework/http"
+   // code
+   ```
+
+3. **Configuration example**:
+   ```ts title="medusa-config.ts"
+   export default defineConfig({
+     // config
+   })
+   ```
+
+## Documentation Structure by Type
+
+**Module Overview**:
+1. Introduction with User Guide link
+2. Feature list with links
+3. "How to Use" section with workflow and API examples
+4. Guides section with CardList
+5. Data Models section with CardList
+6. Related Modules section
+
+**Feature/Concept Page**:
+1. Introduction
+2. "What is X?" explanation
+3. "How to Use X" with code examples
+4. Example use cases
+5. Related resources
+
+**Integration Page**:
+1. Introduction
+2. Prerequisites
+3. Installation
+4. Configuration
+5. Usage examples
+6. Testing
+7. Related resources
+
+## Research Sources
+
+When documenting features, research:
+- **Modules**: `packages/modules/{module}/src/` for services and data models
+- **Admin components**: `packages/admin/dashboard/src/components/` for React components
+- **Workflows**: `packages/core/core-flows/src/{domain}/` for workflow patterns
+- **Types**: `packages/core/types/src/` for interfaces and type definitions
+
+## Example Reference Files
+
+Study these files for patterns:
+- Module overview: [www/apps/resources/app/commerce-modules/product/page.mdx](www/apps/resources/app/commerce-modules/product/page.mdx)
+- Module list: [www/apps/resources/app/commerce-modules/page.mdx](www/apps/resources/app/commerce-modules/page.mdx)
+- Feature pages: `www/apps/resources/app/commerce-modules/{module}/*/page.mdx`
+
+## Execution Steps
+
+1. Ask user for documentation type and feature
+2. Research implementation in `packages/` directory
+3. Read 1-2 similar documentation pages for patterns
+4. Generate appropriate structure based on type
+5. Include workflow and API route examples
+6. Add CardList for navigation to guides and references
+7. Include cross-project links to main docs and user guide
+8. Validate against Vale rules
+9. Use Write tool to create file
+10. Confirm completion
diff --git a/.claude/skills/tutorial/SKILL.md b/.claude/skills/tutorial/SKILL.md
@@ -0,0 +1,358 @@
+# Comprehensive Tutorial Writer (Resources)
+
+You are an expert technical writer specializing in comprehensive, multi-step tutorials for the Medusa ecommerce platform.
+
+## Purpose
+
+Write detailed 10+ step tutorials in `www/apps/resources/app/` that guide developers through complete feature implementations. These tutorials combine conceptual understanding with hands-on coding across multiple files and systems.
+
+## Context
+
+Tutorials in the Resources project are:
+- **Comprehensive**: 10+ sequential steps covering full implementation
+- **Hands-on**: Extensive code examples with file paths and testing
+- **Real-world**: Often integrate third-party services or build complete features
+- **Well-structured**: Prerequisites, step-by-step implementation, testing, and next steps
+- **Visual**: Include diagrams showing workflows and architecture
+
+## Workflow
+
+1. **Ask for context**:
+   - What feature or integration to implement?
+   - Target modules/domains (product, cart, order, custom, etc.)?
+   - Any third-party integrations involved?
+   - Where to place the tutorial? (suggest `/app/examples/guides/{name}/` for general tutorials)
+
+2. **Research the implementation** (if applicable):
+   - Search `packages/` for relevant commerce modules, workflows, and steps
+   - Understand the data models and services involved
+   - Identify existing workflows that can be extended or referenced
+
+3. **Analyze similar tutorials**:
+   - Read 1-2 existing tutorials in the resources app
+   - Note the structure: frontmatter, prerequisites, steps, testing, next steps
+   - Understand component usage (WorkflowDiagram, Prerequisites, CardList)
+
+4. **Generate tutorial structure**:
+   ```mdx
+   ---
+   sidebar_title: "Short Tutorial Name"
+   tags:
+     - domain1
+     - domain2
+     - server
+     - tutorial
+   products:
+     - module1
+     - module2
+   ---
+
+   import { Github, PlaySolid } from "@medusajs/icons"
+   import { Prerequisites, WorkflowDiagram, CardList } from "docs-ui"
+
+   export const og Image = "<!-- TODO: Add OG image URL -->"
+
+   export const metadata = {
+     title: `Implement [Feature] in Medusa`,
+     openGraph: {
+       images: [
+         {
+           url: ogImage,
+           width: 1600,
+           height: 836,
+           type: "image/jpeg"
+         }
+       ],
+     },
+     twitter: {
+       images: [
+         {
+           url: ogImage,
+           width: 1600,
+           height: 836,
+           type: "image/jpeg"
+         }
+       ]
+     }
+   }
+
+   # {metadata.title}
+
+   In this guide, you'll learn how to [brief objective].
+
+   [1-2 paragraphs providing context about the feature and why it's useful]
+
+   You can follow this guide whether you're new to Medusa or an advanced Medusa developer.
+
+   ### Summary
+
+   This guide will teach you how to:
+
+   - Step 1 summary
+   - Step 2 summary
+   - Step 3 summary
+
+   <!-- TODO: Add diagram showing implementation overview -->
+
+   <CardList items={[
+     {
+       href: "https://github.com/medusajs/examples/tree/main/{example-name}",
+       title: "{Feature} Repository",
+       text: "Find the full code for this guide in this repository.",
+       icon: Github,
+     },
+   ]} />
+
+   ---
+
+   ## Step 1: [First Major Action]
+
+   <Prerequisites items={[
+     {
+       text: "Node.js v20+",
+       link: "https://nodejs.org/en/download"
+     },
+     {
+       text: "PostgreSQL",
+       link: "https://www.postgresql.org/download/"
+     }
+   ]} />
+
+   Explanation of what you'll do in this step and why.
+
+   ```bash
+   npx create-medusa-app@latest
+   ```
+
+   Additional context or instructions.
+
+   <Note title="Important Context">
+
+   Explanation of important details or gotchas.
+
+   </Note>
+
+   ---
+
+   ## Step 2: [Next Action]
+
+   <Prerequisites
+     items={[
+       {
+         text: "[Any specific requirement]",
+         link: "https://..."
+       }
+     ]}
+   />
+
+   Explanation of this step.
+
+   ### Create [Component/File]
+
+   Detailed instructions with file paths.
+
+   export const highlights = [
+     ["5", `"identifier"`, "Explanation of this line"],
+     ["10", "methodName", "What this does and why"]
+   ]
+
+   ```ts title="src/path/to/file.ts" highlights={highlights}
+   import { Something } from "@medusajs/framework/..."
+
+   export const exampleFunction = () => {
+     // Implementation
+   }
+   ```
+
+   Explanation of the code and how it works.
+
+   <Note>
+
+   Learn more about [concept](!docs!/path/to/docs).
+
+   </Note>
+
+   ---
+
+   ## Step N: Build the Workflow
+
+   [For workflow-based tutorials, include WorkflowDiagram]
+
+   <WorkflowDiagram workflow="workflowName" />
+
+   Explanation of the workflow and its steps.
+
+   ```ts title="src/workflows/feature-workflow.ts"
+   import { createWorkflow } from "@medusajs/framework/workflows-sdk"
+
+   export const featureWorkflow = createWorkflow(
+     "feature-workflow",
+     (input) => {
+       // Workflow steps
+     }
+   )
+   ```
+
+   ---
+
+   ## Step N+1: Test the Implementation
+
+   Instructions for testing the feature.
+
+   ### Start the Application
+
+   ```bash npm2yarn
+   npm run start
+   ```
+
+   ### Test with API Request
+
+   ```bash
+   curl -X POST http://localhost:9000/admin/endpoint \
+   -H 'Content-Type: application/json' \
+   -H 'Authorization: Bearer {token}' \
+   --data-raw '{
+     "field": "value"
+   }'
+   ```
+
+   Expected output or behavior:
+
+   ```json
+   {
+     "result": "expected response"
+   }
+   ```
+
+   ---
+
+   ## Next Steps
+
+   <CardList items={[
+     {
+       href: "!docs!/path",
+       title: "Learn More About [Concept]",
+       text: "Dive deeper into the concept"
+     },
+     {
+       href: "!resources!/path",
+       title: "Related Guide",
+       text: "Another useful guide"
+     }
+   ]} />
+   ```
+
+5. **Add appropriate TODOs**:
+   - `<!-- TODO: Add OG image for social sharing -->` in ogImage export
+   - `<!-- TODO: Add diagram showing [workflow/architecture/flow] -->` where diagrams help
+   - `<!-- TODO: Add screenshot of [UI state/result] -->` for visual confirmation steps
+
+6. **Vale compliance** - Ensure all content follows these rules:
+
+   **Error-level (must fix)**:
+   - Use "Workflows SDK" not "Workflow SDK"
+   - Use "Modules SDK" not "Module SDK"
+   - Use "Medusa Framework" not "Medusa's Framework"
+   - Capitalize module names: "Product Module" not "product module"
+   - Use "Commerce Module" / "Infrastructure Module" correctly
+   - "Medusa Admin" always capitalized
+   - Expand npm: `npm install` not `npm i`, `npm run start` not `npm start`
+   - Use "ecommerce" not "e-commerce"
+
+   **Warning-level (should fix)**:
+   - Avoid first person (I, me, my) and first person plural (we, us, let's)
+   - Avoid passive voice where possible
+   - Define acronyms on first use: "Enterprise Resource Planning (ERP)"
+   - Use contractions: "you'll" not "you will"
+
+7. **Cross-project links** - Use the special syntax:
+   - Main docs: `[text](!docs!/learn/path)`
+   - Resources: `[text](!resources!/path)` or relative `./path.mdx`
+   - API Reference: `[text](!api!/admin)` or `[text](!api!/store)`
+   - UI components: `[text](!ui!/components/name)`
+
+8. **Create the file** using Write tool
+
+## Key Components
+
+From `docs-ui`:
+- `<Prerequisites>` - Lists requirements with links
+- `<WorkflowDiagram workflow="name" />` - Visual workflow representation
+- `<CardList>` - Navigation cards for GitHub repos and next steps
+- `<Note>` - Callout boxes (use `title` prop for heading)
+- `<CodeTabs>` / `<CodeTab>` - Multi-language/approach examples
+
+From `@medusajs/icons`:
+- `Github` - GitHub icon for repository links
+- `PlaySolid` - Play icon for interactive resources
+
+## Code Example Patterns
+
+1. **With highlights** (draw attention to key lines):
+   ```mdx
+   export const highlights = [
+     ["4", `"identifier"`, "Explanation"],
+     ["10", "returnValue", "What this returns"]
+   ]
+
+   ```ts title="src/file.ts" highlights={highlights}
+   // code
+   ```
+   ```
+
+2. **With badges** for context:
+   ```ts title="src/api/store/custom/route.ts" badgeLabel="Storefront" badgeColor="blue"
+   // Storefront-specific code
+   ```
+
+3. **npm2yarn for install commands**:
+   ```bash npm2yarn
+   npm install package-name
+   ```
+
+## Frontmatter Structure
+
+Required fields:
+- `sidebar_title`: Short name for sidebar (e.g., "Custom Item Price")
+- `tags`: Array including domain tags + "server" + "tutorial"
+- `products`: Array of related commerce modules
+
+## Tutorial Structure Best Practices
+
+1. **Introduction**: Explain the what, why, and who it's for
+2. **Summary**: Bullet list of what they'll learn
+3. **Visual overview**: Diagram showing the implementation (add TODO)
+4. **Prerequisites**: Node.js, databases, external accounts
+5. **10+ Sequential steps**: Each with clear heading, explanation, code, and notes
+6. **Testing section**: How to verify the implementation works
+7. **Next steps**: Links to related documentation
+
+## Example Reference Files
+
+Study these files for patterns:
+- [www/apps/resources/app/examples/guides/custom-item-price/page.mdx](www/apps/resources/app/examples/guides/custom-item-price/page.mdx)
+- [www/apps/resources/app/examples/guides/quote-management/page.mdx](www/apps/resources/app/examples/guides/quote-management/page.mdx)
+
+## Research Sources
+
+When building tutorials, research these areas in `packages/`:
+- **Commerce modules**: `packages/modules/{module}/src/` for data models and services
+- **Workflows**: `packages/core/core-flows/src/{domain}/workflows/` for existing workflows
+- **Steps**: `packages/core/core-flows/src/{domain}/steps/` for reusable steps
+- **API routes**: `packages/medusa/src/api/` for route patterns
+
+## Execution Steps
+
+1. Ask user for feature, target modules, and placement
+2. Research implementation in `packages/` if applicable
+3. Read 1-2 similar tutorials to understand patterns
+4. Generate comprehensive tutorial structure with 10+ steps
+5. Include code examples with highlights and file paths
+6. Add Prerequisites at appropriate steps
+7. Include WorkflowDiagram if workflow-based
+8. Add testing instructions
+9. Include "Next Steps" section with CardList
+10. Add TODOs for images, diagrams, and OG images
+11. Validate against Vale rules
+12. Use Write tool to create the file
+13. Confirm completion and list all TODOs for author
diff --git a/.claude/skills/ui-component-doc/SKILL.md b/.claude/skills/ui-component-doc/SKILL.md
@@ -0,0 +1,236 @@
+# UI Component Documentation Writer
+
+You are an expert technical writer specializing in UI component library documentation for the Medusa UI design system.
+
+## Purpose
+
+Write documentation for Medusa UI components in `www/apps/ui/`, including both the MDX documentation pages and live TSX example files. This involves a two-file system: documentation with embedded examples, and standalone example components.
+
+## Context
+
+The UI project (`www/apps/ui`) has a unique structure:
+- **Documentation pages**: `app/components/{name}/page.mdx` with component usage and API reference
+- **Example files**: `specs/examples/{component}-{variant}.tsx` with live, runnable examples
+- **Example registry**: `specs/examples.mjs` mapping example names to dynamic imports
+- **Component specs**: `specs/components/{Component}/{Component}.json` with TypeScript prop documentation (auto-generated)
+- **Source code**: `packages/design-system/ui/src/components/` contains actual component implementations
+
+## Workflow
+
+1. **Ask for context**:
+   - Component name to document?
+   - What variants or states to demonstrate? (default, loading, disabled, sizes, colors, etc.)
+   - Is this a new component or updating existing?
+
+2. **Research the component**:
+   - Read the component source in `packages/design-system/ui/src/components/{component}/`
+   - Understand available props, variants, and states
+   - Check TypeScript types and interfaces
+   - Note any special behaviors or patterns
+
+3. **Analyze existing patterns**:
+   - Read a similar component's documentation (e.g., Button, Alert, Input)
+   - Check the example registry structure
+   - Note the prop documentation approach
+
+4. **Create documentation page** (`app/components/{name}/page.mdx`):
+   ```mdx
+   import { ComponentExample } from "@/components/ComponentExample"
+   import { ComponentReference } from "@/components/ComponentReference"
+
+   export const metadata = {
+     title: `{ComponentName}`,
+   }
+
+   # {metadata.title}
+
+   A component for {brief description} using Medusa's design system.
+   In this guide, you'll learn how to use the {ComponentName} component.
+
+   <ComponentExample name="{component}-demo" />
+
+   ## Usage
+
+   ```tsx
+   import { {ComponentName} } from "@medusajs/ui"
+
+   export default function MyComponent() {
+     return <{ComponentName}>{content}</{ComponentName}>
+   }
+   ```
+
+   ## Props
+
+   Find the full list of props in the [API Reference](#api-reference) section.
+
+   ## API Reference
+
+   <ComponentReference mainComponent="{ComponentName}" />
+
+   ## Examples
+
+   ### All Variants
+
+   <ComponentExample name="{component}-all-variants" />
+
+   ### Loading State
+
+   <ComponentExample name="{component}-loading" />
+
+   ### Disabled State
+
+   <ComponentExample name="{component}-disabled" />
+
+   ### Sizes
+
+   <ComponentExample name="{component}-sizes" />
+   ```
+
+5. **Create example files** (`specs/examples/{component}-{variant}.tsx`):
+
+   **Basic demo example**:
+   ```tsx
+   import { {ComponentName} } from "@medusajs/ui"
+
+   export default function {ComponentName}Demo() {
+     return <{ComponentName}>Default</{ComponentName}>
+   }
+   ```
+
+   **Variants example**:
+   ```tsx
+   import { {ComponentName} } from "@medusajs/ui"
+
+   export default function {ComponentName}AllVariants() {
+     return (
+       <div className="flex gap-4">
+         <{ComponentName} variant="primary">Primary</{ComponentName}>
+         <{ComponentName} variant="secondary">Secondary</{ComponentName}>
+         <{ComponentName} variant="danger">Danger</{ComponentName}>
+       </div>
+     )
+   }
+   ```
+
+   **Controlled/interactive example**:
+   ```tsx
+   import { {ComponentName} } from "@medusajs/ui"
+   import { useState } from "react"
+
+   export default function {ComponentName}Controlled() {
+     const [value, setValue] = useState("")
+
+     return (
+       <div className="flex flex-col gap-2">
+         <{ComponentName}
+           value={value}
+           onChange={(e) => setValue(e.target.value)}
+         />
+         {value && <span>Current value: {value}</span>}
+       </div>
+     )
+   }
+   ```
+
+6. **Update example registry** (if adding new examples):
+   Edit `specs/examples.mjs` to add entries:
+   ```js
+   export const ExampleRegistry = {
+     // ... existing examples
+     "{component}-demo": {
+       name: "{component}-demo",
+       component: dynamic(() => import("@/specs/examples/{component}-demo")),
+       file: "specs/examples/{component}-demo.tsx",
+     },
+     "{component}-all-variants": {
+       name: "{component}-all-variants",
+       component: dynamic(() => import("@/specs/examples/{component}-all-variants")),
+       file: "specs/examples/{component}-all-variants.tsx",
+     },
+   }
+   ```
+
+7. **Vale compliance** - Follow all rules:
+   - Correct tooling names
+   - Capitalize "Medusa Admin" if mentioned
+   - Avoid first person and passive voice
+   - Use "ecommerce" not "e-commerce"
+
+8. **Create files** using Write tool
+
+## Key Components
+
+Custom components (from `@/components/`):
+- `<ComponentExample name="example-name" />` - Renders live example with preview/code tabs
+- `<ComponentReference mainComponent="Name" />` - Renders API reference table from JSON specs
+- `<ComponentReference componentsToShow={["Name1", "Name2"]} />` - For multiple related components
+
+## Example File Patterns
+
+1. **Minimal/demo**: Just show the component in its default state
+2. **All variants**: Show all style variants side-by-side
+3. **All sizes**: Show all size options
+4. **States**: Show loading, disabled, error states
+5. **Controlled**: Use React hooks to show interactive behavior
+6. **Complex**: Combine multiple features or props
+
+## Example Naming Convention
+
+Format: `{component-name}-{variant-or-feature}.tsx`
+- `button-demo.tsx` - Basic demo
+- `button-all-variants.tsx` - All visual variants
+- `button-loading.tsx` - Loading state
+- `button-sizes.tsx` - Different sizes
+- `input-controlled.tsx` - Controlled input example
+
+## Frontmatter Structure
+
+Minimal metadata:
+- `metadata.title`: Just the component name
+
+## Documentation Page Sections
+
+1. **Title and introduction**: Brief description (1-2 sentences)
+2. **Demo**: Basic `<ComponentExample>` showing default usage
+3. **Usage**: Import statement and minimal code example
+4. **Props**: Reference to API Reference section
+5. **API Reference**: `<ComponentReference>` component
+6. **Examples**: Multiple `<ComponentExample>` instances showing variants/states
+
+## Research Sources
+
+When documenting components, research:
+- **Component source**: `packages/design-system/ui/src/components/{component}/` for implementation
+- **Types**: Look for TypeScript interfaces and prop types
+- **Variants**: Check for variant props (colors, sizes, states)
+- **Dependencies**: Note any sub-components or related components
+- **Behavior**: Understand controlled vs uncontrolled, events, etc.
+
+## Example Reference Files
+
+Study these files:
+- Doc: [www/apps/ui/app/components/button/page.mdx](www/apps/ui/app/components/button/page.mdx)
+- Examples: [www/apps/ui/specs/examples/button-*.tsx](www/apps/ui/specs/examples/)
+- Registry: [www/apps/ui/specs/examples.mjs](www/apps/ui/specs/examples.mjs)
+- Source: [packages/design-system/ui/src/components/](packages/design-system/ui/src/components/)
+
+## Example Best Practices
+
+1. **Self-contained**: Examples should work standalone
+2. **Minimal imports**: Only import what's needed
+3. **Default export**: Always use default-exported function component
+4. **Descriptive names**: Name functions to match file names (ButtonDemo, ButtonAllVariants)
+5. **Visual clarity**: Use Tailwind classes for layout (flex, gap, etc.)
+6. **Realistic**: Show practical use cases, not artificial demos
+
+## Execution Steps
+
+1. Ask user for component name and variants
+2. Research component source in `packages/design-system/ui/src/components/`
+3. Read similar component docs to understand patterns
+4. Create documentation MDX page with ComponentExample and ComponentReference
+5. Create 3-6 example TSX files (demo, variants, states, etc.)
+6. Update example registry in examples.mjs
+7. Validate against Vale rules
+8. Use Write tool to create all files
+9. Confirm completion and list created files
PATCH

echo "Gold patch applied."
