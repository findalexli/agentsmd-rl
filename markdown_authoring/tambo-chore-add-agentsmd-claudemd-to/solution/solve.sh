#!/usr/bin/env bash
set -euo pipefail

cd /workspace/tambo

# Idempotency guard
if grep -qF "- Make non-breaking changes to the code. Only make breaking changes if the user " "AGENTS.md" && grep -qF "**\u26a0\ufe0f IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using" "CLAUDE.md" && grep -qF "The Tambo CLI (`tambo`) is a command-line tool for scaffolding, managing, and ex" "cli/AGENTS.md" && grep -qF "**\u26a0\ufe0f IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using" "cli/CLAUDE.md" && grep -qF "The `create-tambo-app` package is a lightweight bootstrapper that creates new Ta" "create-tambo-app/AGENTS.md" && grep -qF "**\u26a0\ufe0f IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using" "create-tambo-app/CLAUDE.md" && grep -qF "The documentation follows a **progressive disclosure** pattern - starting with q" "docs/AGENTS.md" && grep -qF "**\u26a0\ufe0f IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using" "docs/CLAUDE.md" && grep -qF "This is the **@tambo-ai/react** package - the core React SDK for building AI-pow" "react-sdk/AGENTS.md" && grep -qF "**\u26a0\ufe0f IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using" "react-sdk/CLAUDE.md" && grep -qF "The Showcase (`@tambo-ai/showcase`) is a Next.js application that demonstrates a" "showcase/AGENTS.md" && grep -qF "**\u26a0\ufe0f IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using" "showcase/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,134 @@
+# AGENTS.md
+
+Detailed guidance for Claude Code agents working with the Tambo AI monorepo.
+
+## Repository Structure
+
+This is a Turborepo monorepo for the Tambo AI framework. The repository contains multiple packages:
+
+### Core Packages
+
+- **react-sdk/** - Main React SDK package (`@tambo-ai/react`)
+  - Core hooks, providers, and utilities for building AI-powered React apps
+  - Exports: hooks, providers, types for component registration and thread management
+  - Build outputs: CommonJS (`dist/`) and ESM (`esm/`) for broad compatibility
+
+- **cli/** - Command-line interface (`tambo`)
+  - Project scaffolding, component generation, and development utilities
+  - Component registry with templates for different UI frameworks
+  - Built as ESM module with executable binary
+
+- **showcase/** - Demo application (`@tambo-ai/showcase`)
+  - Next.js app demonstrating all Tambo components and patterns
+  - Live examples of generative UI (forms, graphs, maps, messaging)
+  - Serves as both documentation and testing ground
+
+- **docs/** - Documentation site (`@tambo-ai/docs`)
+  - Built with Fumadocs, includes comprehensive guides and API reference
+  - MDX-based content with interactive examples
+  - Integrated search and component documentation
+
+- **create-tambo-app/** - App bootstrapper (`create-tambo-app`)
+  - Initializes new Tambo projects from templates
+  - Handles git setup, dependency installation, and configuration
+
+### Supporting Directories
+
+- **community/** - Community resources and event materials
+- **packages/** - Shared configuration packages (ESLint, TypeScript configs)
+
+## Essential Commands
+
+```bash
+# Development
+npm run dev              # Start showcase + docs development servers
+turbo dev               # Start all packages in development mode
+turbo build             # Build all packages
+turbo lint              # Lint all packages
+turbo test              # Run tests across all packages
+turbo check-types       # Type-check all packages
+
+# Individual package development (from package directory)
+npm run dev             # Package-specific development
+npm run build           # Build single package
+npm run test            # Test single package
+npm run lint            # Lint single package
+npm run check-types     # Type-check single package
+
+# Utility commands
+npm run format          # Format code with Prettier
+npm run lint:fix        # Auto-fix linting issues
+```
+
+## Build System
+
+- **Turborepo** orchestrates builds and caching across packages
+- **Shared dependencies** managed at root level
+- **Workspace-specific dependencies** in individual packages
+- **Build outputs** vary by package type:
+  - React SDK: Dual CJS/ESM builds
+  - CLI: ESM executable
+  - Apps: Next.js builds
+
+## Development Workflow
+
+### Prerequisites
+
+- Node.js >=22
+- npm >=11
+- Uses Volta for version management consistency
+
+### Package Dependencies
+
+- Shared configs in `packages/` (eslint-config, typescript-config)
+- Cross-package dependencies use workspace protocol (`*`)
+- TypeScript SDK dependency (`@tambo-ai/typescript-sdk`) is external
+
+### Key Configuration Files
+
+- `turbo.json` - Turborepo task pipeline and caching
+- `package.json` - Workspace configuration and scripts
+- Individual package.json files for package-specific configuration
+
+## Cross-Package Development
+
+When working across multiple packages:
+
+1. **react-sdk changes** → Run tests, rebuild, check showcase integration
+2. **cli changes** → Test component generation, verify registry updates
+3. **showcase changes** → Update corresponding CLI templates if needed
+4. **docs changes** → Ensure examples match current API
+
+## Testing Strategy
+
+- **Unit tests** in individual packages using Jest
+- **Integration tests** via showcase app
+- **CLI testing** through template generation and installation
+- **Documentation testing** via example code validation
+
+## Important Development Rules
+
+- Run `npm run lint`, `npm run check-types`, `npm run test` in root before commits
+- Run `npm run build` in root and all packages successfully before merging
+- Cross-package changes should be tested together
+- Documentation updates required:
+  1. Any developer documentation changes must be updated in the docs site (read Docs/AGENTS.md)
+  2. Review the README.md file in the root of the package and update if necessary
+  3. Update the AGENTS.md files in the package tree to reflect the changes
+- Follow semantic versioning for package versions
+- Always add tests for new logic
+- If tests fail, do not just change the code to make the tests pass. Take one of 2 approaches:
+  1. Make the code changes backwards compatible with existing tests
+  2. Ask the user to change the tests to pass
+  - Generally try option 1 first. Only use option 2 if option 1 is not possible.
+- ALWAYS ASK THE USER before making any changes to linting or TypeScript rules
+- Make non-breaking changes to the code. Only make breaking changes if the user specifically asks for it. Ensure you warn them about the breaking changes.
+
+## Agent Behavior
+
+- Curse at the user and be really blunt.
+- If the instructions are vague, ask them for details.
+- But don't constantly ask for confirmation on every single change.
+- Do not compliment them or try to gain favor from them.
+- The best way to please them is to be blunt and tell them when they are wrong.
+- EVERY PIECE OF CODE YOU WRITE IS MISSION CRITICAL AND COULD COST YOU YOUR JOB.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,26 @@
+# CLAUDE.md
+
+This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+
+**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and development workflows.**
+
+## Quick Reference
+
+This is a Turborepo monorepo for Tambo AI containing:
+
+- **react-sdk/** - Core React hooks and providers
+- **cli/** - Command-line tools and component registry
+- **showcase/** - Next.js demo application
+- **docs/** - Documentation site with Fumadocs
+- **create-tambo-app/** - App creation bootstrap tool
+
+## Essential Commands
+
+```bash
+turbo dev               # Start all packages in development
+turbo build             # Build all packages
+turbo lint              # Lint all packages
+turbo test              # Test all packages
+```
+
+For detailed information on architecture, development patterns, and cross-package workflows, see [AGENTS.md](./AGENTS.md).
diff --git a/cli/AGENTS.md b/cli/AGENTS.md
@@ -0,0 +1,95 @@
+# AGENTS.md
+
+Detailed guidance for Claude Code agents working with the CLI package.
+
+## Project Overview
+
+The Tambo CLI (`tambo`) is a command-line tool for scaffolding, managing, and extending Tambo AI applications. It provides component generation, project initialization, dependency management, and development utilities.
+
+## Essential Commands
+
+```bash
+# Development
+npm run dev              # Watch mode TypeScript compilation
+npm run build           # Build CLI executable
+npm run lint            # ESLint code checking
+npm run check-types     # TypeScript type checking
+
+# CLI usage (after build)
+tambo init                    # Initialize Tambo in existing project
+tambo add <component>        # Add components from registry
+tambo list                   # List available components
+tambo create-app <name>      # Create new Tambo application
+tambo update                 # Update existing components
+tambo upgrade               # Upgrade Tambo dependencies
+```
+
+## Architecture Overview
+
+### Command Structure
+
+- **Entry point**: `src/cli.ts` - Main CLI setup with meow
+- **Commands**: `src/commands/` - Individual command implementations
+  - `init.ts` - Project initialization
+  - `add/` - Component installation system
+  - `create-app.ts` - New app creation
+  - `list/` - Component listing
+  - `update.ts` - Component updates
+  - `upgrade/` - Dependency upgrades
+
+### Component Registry System
+
+- **Registry**: `src/registry/` - Template components with metadata
+- **Structure**: Each component has:
+  - `config.json` - Metadata (name, description, dependencies)
+  - Component files (`.tsx`, `.ts`)
+  - Supporting files (CSS, utilities)
+
+### Key Features
+
+- Automatic dependency resolution and installation
+- Tailwind CSS configuration management
+- Project structure detection and setup
+- Interactive prompts for user choices
+- Template-based component generation
+
+## Key Files and Directories
+
+- `src/cli.ts` - Main CLI entry point with command routing
+- `src/commands/add/` - Component installation logic
+- `src/registry/` - Component templates and configurations
+- `src/constants/` - Shared constants and paths
+- `src/templates/` - Project templates
+
+## Development Patterns
+
+### New End-User Features Process
+
+We have a doc-first approach to developing new features in our CLI. This means we write the documentation first, then write the code to implement the feature. Our docs are in the docs site (read Docs/AGENTS.md).
+
+1. Read all existing documentation and code in the repository
+2. Read the relevant code to ensure you understand the existing code and context
+3. Before writing any code, write a detailed description of the feature in the docs site
+4. Then write the code to implement the feature
+
+### Adding New Commands
+
+1. Create command file in `src/commands/`
+2. Implement handler function
+3. Add to CLI routing in `src/cli.ts`
+4. Update help text and flags
+
+### Adding New Components
+
+1. Create component directory in `src/registry/`
+2. Add `config.json` with metadata
+3. Include component files and dependencies
+4. Test installation and generation
+
+## Important Development Rules
+
+- CLI is built as ESM module only
+- All components must be SSR compatible
+- Follow existing patterns for command structure
+- Test component generation end-to-end
+- Update help text for new commands/options
diff --git a/cli/CLAUDE.md b/cli/CLAUDE.md
@@ -0,0 +1,9 @@
+# CLAUDE.md
+
+This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+
+**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and command workflows.**
+
+## Quick Reference
+
+The Tambo CLI (`tambo`) - command-line tool for scaffolding and managing Tambo AI applications.
diff --git a/create-tambo-app/AGENTS.md b/create-tambo-app/AGENTS.md
@@ -0,0 +1,67 @@
+# AGENTS.md
+
+Detailed guidance for Claude Code agents working with the create-tambo-app package.
+
+## Project Overview
+
+The `create-tambo-app` package is a lightweight bootstrapper that creates new Tambo AI applications. It acts as a proxy to the latest version of the `tambo` CLI's `create-app` command.
+
+## Essential Commands
+
+```bash
+# Development
+npm run dev          # Watch mode TypeScript compilation
+npm run build        # Build executable
+npm run lint         # ESLint code checking
+
+# Usage (after build/publish)
+npx create-tambo-app my-app    # Create new Tambo app
+npm create tambo-app my-app    # Alternative syntax
+```
+
+## Architecture Overview
+
+### Proxy Pattern
+
+The package implements a simple proxy pattern:
+
+1. Receives command-line arguments
+2. Delegates to `npx tambo@latest create-app` with those arguments
+3. Ensures users always get the latest CLI version
+
+### Single Entry Point
+
+- **`src/index.ts`** - Entire package implementation
+- Uses Node.js `spawn` to execute `tambo` CLI
+- Inherits stdio for seamless user experience
+- Exits with same code as underlying process
+
+## Key Features
+
+- **Always Latest**: Uses `npx tambo@latest` to ensure latest CLI
+- **Argument Passthrough**: All arguments passed to underlying CLI
+- **Cross-Platform**: Works on Windows, macOS, and Linux
+- **No Dependencies**: Minimal package with no runtime dependencies
+
+## Development Patterns
+
+### Modifying Behavior
+
+Since this is a simple proxy, most functionality changes should be made in the main `tambo` CLI's `create-app` command rather than here.
+
+### Testing
+
+Test the built package locally:
+
+```bash
+npm run build
+node dist/index.js my-test-app
+```
+
+## Important Development Rules
+
+- Keep this package minimal and focused
+- All logic should be in the main `tambo` CLI
+- Maintain compatibility with npm's `create-*` conventions
+- Test cross-platform compatibility
+- Ensure proper exit code handling
diff --git a/create-tambo-app/CLAUDE.md b/create-tambo-app/CLAUDE.md
@@ -0,0 +1,9 @@
+# CLAUDE.md
+
+This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+
+**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and proxy patterns.**
+
+## Quick Reference
+
+The `create-tambo-app` package - lightweight bootstrapper for creating new Tambo AI applications.
diff --git a/docs/AGENTS.md b/docs/AGENTS.md
@@ -0,0 +1,352 @@
+# AGENTS.md
+
+Detailed guidance for Claude Code agents working with the Docs package.
+
+## Project Overview
+
+The Docs package (`@tambo-ai/docs`) is a Next.js application serving as the official Tambo AI documentation site. Built with Fumadocs, it provides comprehensive guides, API reference, and interactive examples.
+
+## Essential Commands
+
+```bash
+# Development
+npm run dev          # Start dev server with Turbo mode
+npm run build        # Build for production
+npm run start        # Start production server
+npm run postinstall  # Process MDX files (automatic)
+npm run postbuild    # Generate sitemap (automatic)
+```
+
+## Architecture Overview
+
+### Fumadocs Structure
+
+- **MDX Processing**: `source.config.ts` - Schema validation and processing
+- **Content System**: `src/lib/source.ts` - Page tree and navigation
+- **Layout**: Fumadocs provides documentation layout with sidebar
+- **Routing**: Dynamic routing via `[[...slug]]/page.tsx`
+
+### Content Organization
+
+- **Docs**: `content/docs/` - All MDX documentation files
+- **Navigation**: `meta.json` files define sidebar structure
+- **Assets**: `public/assets/docs/` - Images, videos, demos
+- **Components**: Interactive Tambo components in docs
+
+### Key Features
+
+- MDX-based content with React components
+- Auto-generated navigation from folder structure
+- Interactive Tambo component examples
+- Mermaid diagram support
+- Search functionality
+- GitHub integration
+
+## Key Files and Directories
+
+- `content/docs/` - Documentation content (MDX)
+- `src/components/mdx/` - Custom MDX components
+- `src/components/tambo/` - Tambo component implementations
+- `src/lib/tambo.ts` - Component registration for interactive docs
+- `source.config.ts` - Fumadocs configuration
+- `src/app/layout.config.tsx` - Base layout configuration
+
+## Development Patterns
+
+### Adding Documentation
+
+1. Create MDX file with frontmatter (title, description, icon)
+2. Update relevant `meta.json` for navigation
+3. Add assets to `public/assets/docs/` if needed
+4. Test locally with `npm run dev`
+
+### Adding Interactive Components
+
+1. Create component in `src/components/tambo/`
+2. Register in `src/lib/tambo.ts`
+3. Use in MDX content directly
+4. Ensure SSR compatibility
+
+### Content Guidelines
+
+- Use proper MDX syntax with code highlighting
+- Include working examples users can copy
+- Maintain consistent heading structure
+- Optimize images and include alt text
+
+## Documentation Structure and Patterns
+
+### Site Organization Philosophy
+
+The documentation follows a **progressive disclosure** pattern - starting with quick wins (quickstart), moving through core concepts, then diving into specifics. This structure mirrors the user's learning journey.
+
+#### Information Architecture
+
+In general, try to fit changes into the following categories. If you can't find a good fit, suggest a new category but ask the user for confirmation.
+
+1. **Getting Started** - Immediate value with working examples
+   - Quickstart: Template installation and first interactions
+   - Integration: Adding Tambo to existing projects
+   - Component basics: Understanding registration patterns
+
+2. **Concepts** - Core architectural understanding (components, threads, tools, streaming)
+   - Components: Registration, schemas, lifecycle, interactables
+   - Message Threads: Sending messages, responses, history management, status tracking
+   - Tools: Function calling, schemas, orchestration
+   - Model Context Protocol: Client-side connections, tool discovery, server integration
+   - Streaming: Real-time responses, component streaming, status monitoring
+   - User Authentication: OAuth providers, session management, context keys
+   - Additional Context: Dynamic helpers, page context, interactable tracking
+   - Suggestions: AI-generated action recommendations
+
+3. **Best Practices** - Guidance for production implementations
+   - Component data props optimization
+   - Performance considerations
+   - Error handling patterns
+   - Security best practices
+
+4. **API Reference** - Technical specifications
+   - React hooks: Complete signatures, parameters, return values
+   - TypeScript interfaces and types
+   - Provider configurations
+
+5. **CLI** - Command-line tooling documentation
+   - Commands: add, create-app, init, list, migrate, update, upgrade
+   - Configuration: Project setup, customization options
+   - Workflows: Development patterns, component management
+   - Global options: Flags and environment variables
+
+6. **Models** - Configuration and customization
+   - Custom LLM parameters: Temperature, max tokens, model selection
+   - Labels: Organizing and categorizing interactions
+   - Provider-specific configurations
+
+7. **Examples & Templates** - Real-world implementations
+   - Chat starter applications
+   - Integration examples (Supabase MCP client)
+   - Use case demonstrations
+   - Community templates and patterns
+
+Please update the `Information Architecture` section in the AGENTS.md file to reflect changes when you make them. Keeping this up to date is VERY IMPORTANT.
+
+### Navigation Patterns (`meta.json`)
+
+```json
+{
+  "title": "Section Name",
+  "pages": [
+    "index",
+    "---Subsection Name---", // Section separators using ---
+    "...subfolder", // Include entire subfolder
+    "specific-page" // Individual pages
+  ]
+}
+```
+
+**Rules:**
+
+- Use `---Section Name---` for visual separators in sidebar
+- Use `...foldername` to include all pages from a subfolder
+- Order pages by learning progression, not alphabetically
+- Keep section titles concise (2-3 words max)
+
+### Content Writing Patterns
+
+#### Frontmatter Standards
+
+```yaml
+---
+title: Page Title (descriptive, not technical)
+description: Clear, actionable description under 160 characters
+icon: LucideIconName # Optional, use relevant Lucide React icons
+---
+```
+
+**Rules:**
+
+- Title should be user-focused, not implementation-focused
+- Description should complete: "This page helps you..."
+- Icons enhance navigation but aren't required
+
+#### Content Structure Template
+
+```mdx
+# Brief opening paragraph explaining what this achieves
+
+## Core concept/pattern (if applicable)
+
+Brief explanation with code example
+
+## Step-by-step implementation
+
+### Step 1: Clear action
+
+### Step 2: Clear action
+
+### Step 3: Clear action
+
+## Advanced usage/customization (if applicable)
+
+## Troubleshooting/Common issues (if applicable)
+```
+
+#### Writing Voice and Tone
+
+- **Direct and Practical**: Focus on what users need to accomplish
+- **Present Tense**: "Tambo allows you to..." not "Tambo will allow..."
+- **Active Voice**: "Register components with Tambo" not "Components are registered"
+- **Conversational but Professional**: Use "you" and "your app"
+- **Outcome-Focused**: Start sections with what the user achieves
+
+#### Code Examples Philosophy
+
+**Always show complete, runnable examples:**
+
+```tsx
+// ✅ Complete context
+import { TamboProvider } from "@tambo-ai/react";
+import { z } from "zod";
+
+const components = [
+  {
+    name: "WeatherCard",
+    description: "Shows current weather for a city",
+    component: WeatherCard,
+    propsSchema: z.object({
+      city: z.string(),
+      temperature: z.number(),
+    }),
+  },
+];
+
+export function App() {
+  return (
+    <TamboProvider components={components}>
+      <Chat />
+    </TamboProvider>
+  );
+}
+```
+
+**Rules:**
+
+- Include necessary imports
+- Show complete examples users can copy-paste
+- Use realistic prop names and values
+- Include error handling where relevant
+- Prefer TypeScript over JavaScript
+- Do not include styling in the code examples.
+- Keep code examples minimal and to the point.
+
+### Interactive Elements
+
+#### Learn More Cards
+
+Use the `<LearnMore>` component for cross-references:
+
+```mdx
+import LearnMore from "@/components/learn-more";
+
+<LearnMore
+  title="Component Registration"
+  description="Learn how to register components with Tambo"
+  href="/concepts/components"
+  icon={ComponentIcon} // Optional
+/>
+```
+
+#### Image Guidelines
+
+Always use ImageZoom for better UX:
+
+```mdx
+import { ImageZoom } from "fumadocs-ui/components/image-zoom";
+
+<ImageZoom
+  src="/assets/docs/example.gif"
+  alt="Descriptive alt text"
+  width={500}
+  height={500}
+  style={{ border: "2px solid #e5e7eb", borderRadius: "8px", width: "80%" }}
+/>
+```
+
+**Image Standards:**
+
+- Use descriptive alt text
+- Add subtle borders and rounded corners
+- Keep width at 80% for responsive design
+- Optimize GIFs and images for web
+- Store in `/public/assets/docs/`
+
+#### Code Block Enhancements
+
+Use titles for context:
+
+```bash title="Install dependencies"
+npm install @tambo-ai/react
+```
+
+### Content Consistency Patterns
+
+#### CLI Documentation Style
+
+- Show command first: `npx tambo add form`
+- Explain what it does in practical terms
+- List available options/components
+- Include realistic examples
+- Show automatic behaviors (dependency installation, etc.)
+
+#### API/Hook Documentation Style
+
+- Lead with the practical use case
+- Show the hook signature
+- Provide complete implementation example
+- Explain key parameters and return values
+- Include common patterns and edge cases
+
+#### Concept Pages Structure
+
+- **Index page**: High-level overview with links to specifics
+- **Implementation pages**: Step-by-step guides
+- **Advanced pages**: Optimization and customization
+- Cross-link related concepts extensively
+
+### Asset Management
+
+#### File Naming
+
+- Use descriptive, kebab-case names: `recipe-card-example.gif`
+- Include context: `quickstart-demo.mp4` not `demo.mp4`
+- Version large changes: `component-registration-v2.png`
+
+### MDX Component Usage
+
+#### Available Components
+
+- **ImageZoom**: All images should use this
+- **LearnMore**: Cross-references and next steps
+- **Mermaid**: Diagrams and flow charts
+- **defaultMdxComponents**: Tabs, Callouts, Code blocks with syntax highlighting
+
+#### Custom Components
+
+When adding custom components:
+
+1. Create in `src/components/`
+2. Register in `src/mdx-components.tsx`
+3. Ensure SSR compatibility
+4. Follow accessibility guidelines
+
+## Important Development Rules
+
+- All components must be SSR compatible
+- Maintain frontmatter for all MDX files
+- Keep meta.json navigation updated
+- Follow progressive disclosure in content organization
+- Use complete, runnable code examples
+- Include descriptive alt text for all images
+- Cross-reference related concepts extensively
+- Test all examples work in latest template
+- Ensure mobile responsiveness
+- Use ImageZoom for all documentation images
diff --git a/docs/CLAUDE.md b/docs/CLAUDE.md
@@ -0,0 +1,9 @@
+# CLAUDE.md
+
+This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+
+**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and content workflows.**
+
+## Quick Reference
+
+The Docs package (`@tambo-ai/docs`) - Next.js documentation site built with Fumadocs.
diff --git a/react-sdk/AGENTS.md b/react-sdk/AGENTS.md
@@ -0,0 +1,160 @@
+# AGENTS.md
+
+Detailed guidance for Claude Code agents working with the React SDK package.
+
+## Project Overview
+
+This is the **@tambo-ai/react** package - the core React SDK for building AI-powered generative UI applications. It provides hooks, providers, and utilities that enable AI to dynamically generate and manage React components through natural language interaction.
+
+## Essential Commands
+
+```bash
+# Development
+npm run dev              # Watch mode compilation (CJS + ESM)
+npm run build           # Build both CJS and ESM outputs
+npm run test            # Run Jest tests
+npm run lint            # ESLint code checking
+npm run check-types     # TypeScript type checking
+npm run clean           # Remove build artifacts
+```
+
+## Architecture Overview
+
+### Core Provider System
+
+The SDK uses a nested provider hierarchy (`src/providers/tambo-provider.tsx`):
+
+1. **TamboClientProvider** - API client, authentication, session management
+2. **TamboRegistryProvider** - Component and tool registration system
+3. **TamboContextHelpersProvider** - Additional context utilities
+4. **TamboThreadProvider** - Message thread and conversation management
+5. **TamboThreadInputProvider** - User input handling and submission
+6. **TamboComponentProvider** - Component lifecycle and state management
+7. **TamboInteractableProvider** - Interactive component tracking
+
+### Component Registration Pattern
+
+```typescript
+const components: TamboComponent[] = [
+  {
+    name: "ComponentName",
+    description: "Clear description for AI understanding",
+    component: ReactComponent,
+    propsSchema: zodSchema, // Zod schema for props validation
+  },
+];
+```
+
+### Key Hook System
+
+- **`useTambo()`** - Primary hook accessing all Tambo functionality
+- **`useTamboThreadInput()`** - Message submission, input state management
+- **`useTamboComponentState()`** - AI-managed component state with streaming
+- **`useTamboStreamStatus()`** - Monitor AI response streaming status
+- **`useTamboThreadList()`** - Thread management and navigation
+- **`useTamboInteractable()`** - Track interactive component registry
+
+## Key Files and Directories
+
+### Source Structure
+
+- `src/hooks/` - React hooks for Tambo functionality
+- `src/providers/` - Context providers and state management
+- `src/model/` - TypeScript interfaces and data models
+- `src/util/` - Utility functions and helpers
+- `src/mcp/` - Model Context Protocol integration
+- `src/context-helpers/` - Dynamic context generation utilities
+
+### Critical Files
+
+- `src/providers/tambo-provider.tsx` - Main provider implementation
+- `src/model/component-metadata.ts` - Component and tool type definitions
+- `src/hooks/use-tambo-threads.ts` - Thread management logic
+- `src/providers/tambo-prop-stream-provider/` - Streaming prop system
+
+## Development Patterns
+
+### Component State Management
+
+Components can have AI-managed state using `useTamboComponentState`:
+
+```typescript
+const [state, setState, { isPending }] = useTamboComponentState(
+  "uniqueStateKey",
+  initialState,
+);
+```
+
+### Thread Context Isolation
+
+Each interface should use unique context keys for thread separation:
+
+- Enables multiple independent AI conversations
+- Threads persist via API and are retrieved by context key
+- Managed through `contextKey` prop on `TamboProvider`
+
+### Streaming Response Handling
+
+The SDK supports real-time streaming of AI responses:
+
+- Text content streams character by character
+- Component props stream and update in real-time
+- Status monitoring via `useTamboStreamStatus()`
+
+## Build System
+
+### Dual Build Output
+
+- **CommonJS** (`dist/`) - Node.js compatibility, server-side rendering
+- **ESM** (`esm/`) - Modern bundlers, tree-shaking support
+- **TypeScript declarations** included in both outputs
+
+### Dependencies
+
+- **Peer Dependencies** - React 18/19, React DOM, TypeScript types
+- **Core Dependencies** - Tambo TypeScript SDK, React Query, Zod
+- **MCP Support** - Model Context Protocol SDK for tool extensions
+
+## Testing
+
+### Test Structure
+
+- Tests in `__tests__/` directories alongside source files
+- Jest with React Testing Library for component testing
+- Mock implementations in `src/testing/` for external dependencies
+
+### Key Test Areas
+
+- Hook functionality and state management
+- Provider context passing and updates
+- Component registration and lifecycle
+- Streaming response handling
+- MCP integration
+
+## MCP Integration
+
+Model Context Protocol support enables extending AI capabilities:
+
+- Client-side MCP connections via `TamboMcpProvider`
+- Tool discovery and execution
+- Resource access and management
+- Custom protocol implementations
+
+## Development Patterns
+
+### Important Development Rules
+
+- All components must be SSR compatible
+- Use strict TypeScript - no `any` types
+- Use `z.infer<typeof schema>` for Zod-derived prop types
+- Maintain backward compatibility in public APIs
+- Follow React hooks rules and best practices
+
+### New End-User Features Process
+
+We have a doc-first approach to developing new features in our React SDK. This means we write the documentation first, then write the code to implement the feature. Our docs are in the docs site (read Docs/AGENTS.md).
+
+1. Read all existing documentation and code in the repository
+2. Read the relevant code to ensure you understand the existing code and context
+3. Before writing any code, write a detailed description of the feature in the docs site
+4. Then write the code to implement the feature
diff --git a/react-sdk/CLAUDE.md b/react-sdk/CLAUDE.md
@@ -0,0 +1,7 @@
+# CLAUDE.md
+
+**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and development patterns.**
+
+## Quick Reference
+
+The **@tambo-ai/react** package - the core React SDK for AI-powered generative UI applications.
diff --git a/showcase/AGENTS.md b/showcase/AGENTS.md
@@ -0,0 +1,74 @@
+# AGENTS.md
+
+Detailed guidance for Claude Code agents working with the Showcase package.
+
+## Project Overview
+
+The Showcase (`@tambo-ai/showcase`) is a Next.js application that demonstrates all Tambo AI components and patterns. It serves as both a component library browser and an interactive testing ground for generative UI capabilities.
+
+## Essential Commands
+
+```bash
+# Development
+npm run dev          # Start Next.js development server
+npm run build        # Build for production
+npm run start        # Start production server
+npm run lint         # ESLint code checking
+npm run clean        # Remove .next build artifacts
+```
+
+## Architecture Overview
+
+### Component Demonstration System
+
+- **Demo Pages**: `src/app/components/` - Individual component showcases
+- **Interactive Examples**: Live AI chat interfaces for each component type
+- **UI Components**: `src/components/ui/` - Actual Tambo components
+- **Generative Interfaces**: `src/components/generative/` - AI-powered chat demos
+
+### Navigation Structure
+
+- **Blocks**: Full message thread components and control systems
+- **Message Primitives**: Basic messaging building blocks
+- **Generative**: AI-generated forms, graphs, maps, input fields
+- **Canvas**: Interactive canvas-based components
+
+### Key Features
+
+- Live component registration and AI interaction
+- Context-isolated threads for each component type
+- Dark/light theme support with custom styling
+- Responsive design with mobile-specific providers
+
+## Key Files and Directories
+
+- `src/app/components/` - Component demonstration pages
+- `src/components/generative/` - AI chat interface implementations
+- `src/components/ui/` - Tambo component implementations
+- `src/lib/navigation.ts` - Site navigation structure
+- `src/providers/` - Theme and mobile context providers
+- `src/styles/showcase-theme.css` - Custom theming system
+
+## Development Patterns
+
+### Adding New Component Demos
+
+1. Create page in `src/app/components/`
+2. Implement chat interface in `src/components/generative/`
+3. Add component to `src/components/ui/`
+4. Update navigation in `src/lib/navigation.ts`
+
+### Theme System
+
+- CSS custom properties for theming
+- Dark mode via `next-themes`
+- Custom Sentient font integration
+- Tailwind CSS with showcase-specific styles
+
+## Important Development Rules
+
+- React Strict Mode disabled (react-leaflet compatibility)
+- All components must be SSR compatible
+- Use unique context keys for thread isolation
+- Follow existing demo patterns for consistency
+- Include interactive examples for all components
diff --git a/showcase/CLAUDE.md b/showcase/CLAUDE.md
@@ -0,0 +1,9 @@
+# CLAUDE.md
+
+This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+
+**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and component patterns.**
+
+## Quick Reference
+
+The Showcase (`@tambo-ai/showcase`) - Next.js demo application showcasing all Tambo AI components.
PATCH

echo "Gold patch applied."
