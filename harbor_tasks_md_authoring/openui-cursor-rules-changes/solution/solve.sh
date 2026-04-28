#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openui

# Idempotency guard
if grep -qF "Crayon UI uses a comprehensive design system with SCSS utilities, CSS custom pro" ".cursor/rules/styling-rule.mdc" && grep -qF "Crayon uses **pnpm** as its package manager instead of npm. pnpm provides better" ".cursor/rules/use-pnpm.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/styling-rule.mdc b/.cursor/rules/styling-rule.mdc
@@ -0,0 +1,432 @@
+---
+description: Comprehensive SCSS styling guidelines for the Crayon React UI component library
+globs: *.scss,*.tsx,*.ts
+alwaysApply: true
+---
+
+# Crayon UI Styling System
+
+## Overview
+
+Crayon UI uses a comprehensive design system with SCSS utilities, CSS custom properties, and consistent component patterns. All styling must follow these guidelines to maintain design consistency and component reusability.
+
+## Core Principles
+
+### 1. Use cssUtils.scss for All Design Tokens
+
+**Always import and use `cssUtils.scss` instead of hardcoded values:**
+
+```scss
+@use "../../cssUtils" as cssUtils;
+
+// ✅ Correct - Use design tokens
+.my-component {
+  background-color: cssUtils.$bg-container;
+  color: cssUtils.$primary-text;
+  padding: cssUtils.$spacing-m;
+  border-radius: cssUtils.$rounded-m;
+  @include cssUtils.typography(body, default);
+}
+
+// ❌ Incorrect - Hardcoded values
+.my-component {
+  background-color: #ffffff;
+  color: #000000;
+  padding: 16px;
+  border-radius: 8px;
+  font-family: "Inter", sans-serif;
+}
+```
+
+### 2. Component Architecture
+
+#### File Structure
+
+Each component should follow this structure:
+
+```FileStructure
+components/ComponentName/
+├── ComponentName.tsx      # Main component
+├── ComponentName.scss     # Component styles
+├── index.ts              # Exports
+├── dependencies.ts       # External dependencies
+└── stories/              # Storybook stories
+    └── ComponentName.stories.tsx
+```
+
+#### CSS Class Naming Convention
+
+Use the `.crayon-component-name` prefix with BEM-like modifiers:
+
+```scss
+.crayon-button {
+  // Base styles
+
+  &-primary {
+    // Primary variant styles
+  }
+
+  &-secondary {
+    // Secondary variant styles
+  }
+
+  &-small {
+    // Small size variant
+  }
+
+  &-large {
+    // Large size variant
+  }
+
+  &__icon {
+    // Component element (like icon inside button)
+  }
+
+  &--disabled {
+    // Component state modifier
+  }
+}
+```
+
+### 3. Typography System
+
+#### Available Typography Mixins
+
+```scss
+// Body text variants
+@include cssUtils.typography(body, default); // Regular body text
+@include cssUtils.typography(body, small); // Smaller body text
+@include cssUtils.typography(body, large); // Larger body text
+@include cssUtils.typography(body, heavy); // Bold body text
+
+// Label variants
+@include cssUtils.typography(label, default); // Regular labels
+@include cssUtils.typography(label, small); // Small labels
+@include cssUtils.typography(label, large); // Large labels
+
+// Heading variants
+@include cssUtils.typography(heading, large); // H1 equivalent
+@include cssUtils.typography(heading, medium); // H2 equivalent
+@include cssUtils.typography(heading, small); // H3 equivalent
+
+// Number variants (for data display)
+@include cssUtils.typography(number, default); // Regular numbers
+@include cssUtils.typography(number, large); // Large numbers
+@include cssUtils.typography(number, title); // Title numbers
+```
+
+### 4. Color System
+
+#### Background Colors
+
+```scss
+cssUtils.$bg-fill          // Main background
+cssUtils.$bg-container     // Card/container backgrounds
+cssUtils.$bg-overlay       // Modal/overlay backgrounds
+cssUtils.$bg-sunk          // Input field backgrounds
+cssUtils.$bg-elevated      // Elevated surfaces
+cssUtils.$bg-danger        // Error/danger backgrounds
+cssUtils.$bg-success       // Success backgrounds
+cssUtils.$bg-info          // Info backgrounds
+```
+
+#### Interactive Colors
+
+```scss
+cssUtils.$interactive-default      // Default button background
+cssUtils.$interactive-hover        // Hover state
+cssUtils.$interactive-pressed      // Pressed/active state
+cssUtils.$interactive-disabled     // Disabled state
+cssUtils.$interactive-accent       // Primary action color
+```
+
+#### Text Colors
+
+```scss
+cssUtils.$primary-text      // Main text color
+cssUtils.$secondary-text    // Secondary/muted text
+cssUtils.$disabled-text     // Disabled text
+cssUtils.$accent-primary-text    // Primary accent text
+cssUtils.$success-primary-text   // Success text
+cssUtils.$danger-primary-text    // Error text
+```
+
+#### Stroke/Border Colors
+
+```scss
+cssUtils.$stroke-default           // Default borders
+cssUtils.$stroke-interactive-el    // Interactive element borders
+cssUtils.$stroke-emphasis          // Emphasis borders
+cssUtils.$stroke-accent            // Accent borders
+cssUtils.$stroke-danger            // Error borders
+```
+
+### 5. Spacing System
+
+Use the predefined spacing scale:
+
+```scss
+cssUtils.$spacing-0     // 0px
+cssUtils.$spacing-3xs   // 2px
+cssUtils.$spacing-2xs   // 4px
+cssUtils.$spacing-xs    // 8px
+cssUtils.$spacing-s     // 12px
+cssUtils.$spacing-m     // 16px
+cssUtils.$spacing-l     // 20px
+cssUtils.$spacing-xl    // 24px
+cssUtils.$spacing-2xl   // 32px
+cssUtils.$spacing-3xl   // 40px
+```
+
+### 6. Border Radius System
+
+```scss
+cssUtils.$rounded-0     // 0px (sharp corners)
+cssUtils.$rounded-3xs   // 2px
+cssUtils.$rounded-2xs   // 4px
+cssUtils.$rounded-xs    // 6px
+cssUtils.$rounded-s     // 8px
+cssUtils.$rounded-m     // 12px
+cssUtils.$rounded-l     // 16px
+cssUtils.$rounded-xl    // 20px
+cssUtils.$rounded-full  // 9999px (fully rounded)
+```
+
+### 7. Shadow System
+
+```scss
+cssUtils.$shadow-s      // Small shadow
+cssUtils.$shadow-m      // Medium shadow
+cssUtils.$shadow-l      // Large shadow
+cssUtils.$shadow-xl     // Extra large shadow
+cssUtils.$shadow-2xl    // 2X large shadow
+cssUtils.$shadow-3xl    // 3X large shadow
+```
+
+## Component Patterns
+
+### Standard Component Variants
+
+Most components should support these variants:
+
+#### Size Variants
+
+```scss
+&-small {
+  padding: calc(cssUtils.$spacing-2xs - 1px) cssUtils.$spacing-s;
+  @include cssUtils.typography(body, small);
+}
+
+&-medium {
+  padding: calc(cssUtils.$spacing-xs - 1px) cssUtils.$spacing-m;
+  @include cssUtils.typography(body, default);
+}
+
+&-large {
+  padding: calc(cssUtils.$spacing-s - 1px) cssUtils.$spacing-l;
+  @include cssUtils.typography(body, large);
+}
+```
+
+#### Button Variants
+
+```scss
+&-primary {
+  background-color: cssUtils.$interactive-accent;
+  color: cssUtils.$accent-primary-text;
+  border-color: cssUtils.$stroke-accent;
+
+  &:not(:disabled):hover {
+    background-color: cssUtils.$interactive-accent-hover;
+  }
+
+  &:disabled {
+    background-color: cssUtils.$interactive-accent-disabled;
+    cursor: not-allowed;
+  }
+}
+
+&-secondary {
+  background-color: cssUtils.$interactive-default;
+  color: cssUtils.$primary-text;
+  border-color: cssUtils.$stroke-interactive-el;
+
+  &:not(:disabled):hover {
+    background-color: cssUtils.$interactive-hover;
+  }
+}
+```
+
+### Form Components Pattern
+
+```scss
+.crayon-input {
+  @include cssUtils.typography(body, default);
+  border: 1px solid cssUtils.$stroke-default;
+  border-radius: cssUtils.$rounded-m;
+  background-color: cssUtils.$bg-sunk;
+  color: cssUtils.$primary-text;
+
+  &::placeholder {
+    color: cssUtils.$secondary-text;
+  }
+
+  &:focus {
+    outline: none;
+    border-color: cssUtils.$stroke-emphasis;
+  }
+
+  &:disabled {
+    background-color: cssUtils.$bg-sunk;
+    color: cssUtils.$disabled-text;
+    cursor: not-allowed;
+  }
+
+  &-error {
+    border-color: cssUtils.$stroke-danger-emphasis;
+  }
+}
+```
+
+## Best Practices
+
+### 1. Avoid Magic Numbers
+
+Always use design tokens instead of hardcoded values:
+
+```scss
+// ✅ Good
+padding: cssUtils.$spacing-m;
+border-radius: cssUtils.$rounded-m;
+
+// ❌ Bad
+padding: 16px;
+border-radius: 8px;
+```
+
+### 2. Consistent State Handling
+
+Use the `:not(:disabled)` pattern for hover/active states:
+
+```scss
+&:not(:disabled):hover {
+  background-color: cssUtils.$interactive-hover;
+}
+
+&:not(:disabled):active {
+  background-color: cssUtils.$interactive-pressed;
+}
+```
+
+### 3. Responsive Design
+
+For responsive components, use CSS custom properties that can be controlled via JavaScript:
+
+```scss
+.my-responsive-component {
+  gap: var(--component-gap, cssUtils.$spacing-m);
+  padding: var(--component-padding, cssUtils.$spacing-m);
+}
+```
+
+### 4. Component Composition
+
+Prefer composition over complex variants. Create small, focused components that can be combined:
+
+```tsx
+// ✅ Good - Composable
+<Card>
+  <CardHeader>
+    <Title>Card Title</Title>
+  </CardHeader>
+  <CardContent>
+    <Text>Content</Text>
+    <Button variant="primary">Action</Button>
+  </CardContent>
+</Card>
+
+// ❌ Avoid - Overly complex single component
+<ComplexCard
+  title="Card Title"
+  content="Content"
+  buttonText="Action"
+  buttonVariant="primary"
+  showHeader={true}
+  headerVariant="large"
+/>
+```
+
+### 5. CSS Custom Properties for Theming
+
+Use CSS custom properties for values that might need to be overridden:
+
+```scss
+.crayon-themeable-component {
+  --component-bg: #{cssUtils.$bg-container};
+  --component-text: #{cssUtils.$primary-text};
+
+  background-color: var(--component-bg);
+  color: var(--component-text);
+}
+```
+
+### 6. Accessibility Considerations
+
+- Always include focus states
+- Use appropriate color contrasts (handled by design tokens)
+- Support keyboard navigation
+- Include proper ARIA attributes in component markup
+
+### 7. Performance
+
+- Avoid deeply nested selectors
+- Use efficient CSS selectors
+- Minimize CSS specificity conflicts
+- Consider CSS-in-JS only when necessary (prefer SCSS for static styles)
+
+## When to Create New Components
+
+### ✅ Create a new component when
+
+- The UI pattern is reusable across multiple features
+- It has its own distinct behavior and API
+- It needs specific accessibility features
+- It represents a semantic UI concept (Button, Input, Card, etc.)
+
+### ✅ Extend existing components when
+
+- Adding a variant that fits the existing API
+- Creating a domain-specific version of a generic component
+- The new component is just a styled wrapper
+
+### ❌ Don't create new components for
+
+- One-off styling needs (use CSS classes or inline styles)
+- Layout-only components (use CSS Grid/Flexbox)
+- Text styling (use typography mixins)
+
+## Migration Guide
+
+When updating existing components:
+
+1. **Audit current styles** - Check for hardcoded values
+2. **Replace with tokens** - Use cssUtils variables
+3. **Update naming** - Ensure BEM-like class names
+4. **Add missing states** - Include hover, focus, disabled, active states
+5. **Test thoroughly** - Verify all variants work correctly
+
+## Tooling
+
+- **SCSS Compilation**: `pnpm build:scss`
+- **Linting**: ESLint with custom rules
+- **Storybook**: For component development and testing
+- **Design Tokens**: All available in `cssUtils.scss`
+
+## Questions?
+
+When in doubt:
+
+1. Check existing components for similar patterns
+2. Look at `cssUtils.scss` for available tokens
+3. Ask in #design-system Slack channel
+4. Reference the design system documentation
diff --git a/.cursor/rules/use-pnpm.mdc b/.cursor/rules/use-pnpm.mdc
@@ -0,0 +1,356 @@
+---
+description: Comprehensive pnpm package manager guidelines for the Crayon monorepo
+globs: package.json,*.json,*.toml
+alwaysApply: true
+---
+
+# Crayon Package Management with pnpm
+
+## Overview
+
+Crayon uses **pnpm** as its package manager instead of npm. pnpm provides better performance, disk efficiency, and strict dependency management. This document covers all pnpm usage patterns for the Crayon monorepo.
+
+## Why pnpm?
+
+### Benefits Over npm
+
+- **Faster installs**: Uses hard links for node_modules
+- **Disk efficient**: Single copy of packages across projects
+- **Strict dependency resolution**: No phantom dependencies
+- **Better workspace support**: Native monorepo management
+- **Security**: Prevents dependency confusion attacks
+
+### Key Differences
+
+- `node_modules` structure is different (flat with symlinks)
+- Stricter dependency isolation
+- Faster cold installs and updates
+
+## Core Commands
+
+### Package Installation
+
+```bash
+# Install all dependencies (equivalent to npm install)
+pnpm install
+
+# Install specific package
+pnpm add <package-name>
+
+# Install dev dependency
+pnpm add -D <package-name>
+
+# Install peer dependency
+pnpm add -P <package-name>
+
+# Remove package
+pnpm remove <package-name>
+```
+
+### Running Scripts
+
+```bash
+# Run script from package.json (equivalent to npm run)
+pnpm run <script-name>
+
+# Run script in specific workspace
+pnpm --filter <package-name> run <script-name>
+
+# Run script in all workspaces
+pnpm --recursive run <script-name>
+```
+
+## Workspace Management
+
+Crayon uses pnpm workspaces for its monorepo structure. Here are the key workspace commands:
+
+### Workspace Structure
+
+```fileStructure
+js/
+├── packages/
+│   ├── react-core/
+│   ├── react-ui/
+│   └── stream/
+└── pnpm-workspace.yaml
+```
+
+### Common Workspace Commands
+
+```bash
+# Install all dependencies across workspaces
+pnpm install
+
+# Run command in specific package
+pnpm --filter react-ui run build
+
+# Run command in all packages
+pnpm --recursive run build
+
+# Add dependency to specific package
+pnpm --filter react-ui add lodash
+
+# Run tests across all packages
+pnpm --recursive run test
+```
+
+## Available Scripts by Package
+
+### React UI Package (`js/packages/react-ui/`)
+
+```bash
+# Development
+pnpm storybook              # Start Storybook dev server
+pnpm watch                  # Watch mode with concurrent builds
+
+# Building
+pnpm build                  # Full build (SCSS + TypeScript + Tailwind)
+pnpm build:tsc              # TypeScript compilation only
+pnpm build:scss             # SCSS compilation only
+pnpm build:plugin           # Tailwind plugin build
+pnpm build:storybook        # Storybook production build
+
+# Code Quality
+pnpm lint:check             # Run ESLint
+pnpm lint:fix               # Fix ESLint issues
+pnpm format:check           # Check Prettier formatting
+pnpm format:fix             # Fix Prettier formatting
+pnpm ci                     # CI pipeline (lint + format check)
+```
+
+### React Core Package (`js/packages/react-core/`)
+
+```bash
+# Building
+pnpm build                  # TypeScript compilation
+pnpm watch                  # Watch mode
+
+# Code Quality
+pnpm lint:check
+pnpm lint:fix
+pnpm format:check
+pnpm format:fix
+```
+
+### Stream Package (`js/packages/stream/`)
+
+```bash
+# Building
+pnpm build                  # TypeScript compilation
+pnpm watch                  # Watch mode
+
+# Code Quality
+pnpm lint:check
+pnpm lint:fix
+pnpm format:check
+pnpm format:fix
+```
+
+### Python Package (`py/`)
+
+```bash
+# Using Poetry (not pnpm)
+poetry install              # Install dependencies
+poetry run <command>        # Run commands with Poetry
+poetry shell               # Activate virtual environment
+```
+
+## Common Development Workflows
+
+### Setting Up Development Environment
+
+```bash
+# Clone and setup the project
+git clone <repository-url>
+cd crayon
+
+# Install all dependencies
+pnpm install
+
+# Start development servers
+pnpm --filter react-ui storybook    # UI development
+```
+
+### Building for Production
+
+```bash
+# Build all packages
+pnpm --recursive run build
+
+# Or build specific packages
+pnpm --filter react-ui run build
+pnpm --filter react-core run build
+```
+
+### Code Quality Checks
+
+```bash
+# Check all packages
+pnpm --recursive run lint:check
+pnpm --recursive run format:check
+
+# Fix issues in all packages
+pnpm --recursive run lint:fix
+pnpm --recursive run format:fix
+```
+
+### Adding New Dependencies
+
+```bash
+# Add to specific package
+pnpm --filter react-ui add <package-name>
+pnpm --filter react-ui add -D <package-name>  # dev dependency
+
+# Add to root (shared tooling)
+pnpm add -D -w <package-name>
+```
+
+## Best Practices
+
+### 1. Always Use pnpm
+
+```bash
+# ✅ Correct
+pnpm install
+pnpm add lodash
+
+# ❌ Incorrect
+npm install
+npm install lodash
+yarn add lodash
+```
+
+### 2. Use Workspace Filters
+
+```bash
+# ✅ Specific package operations
+pnpm --filter react-ui run build
+
+# ✅ All packages
+pnpm --recursive run test
+
+# ❌ Avoid running in wrong context
+cd js/packages/react-ui && pnpm run build  # Less efficient
+```
+
+### 3. Dependency Management
+
+```bash
+# ✅ Add dependencies to correct packages
+pnpm --filter react-ui add react-dom  # Runtime dependency
+pnpm --filter react-ui add -D @types/react  # Dev dependency
+
+# ❌ Don't add to wrong package
+pnpm add react  # Would add to root, not to package
+```
+
+### 4. Script Organization
+
+```bash
+# ✅ Use consistent script names across packages
+"build": "tsc"
+"watch": "tsc --watch"
+"lint:check": "eslint ."
+"lint:fix": "eslint --fix ."
+"format:check": "prettier --check ."
+"format:fix": "prettier --write ."
+```
+
+### 5. Lockfile Management
+
+```bash
+# ✅ Always commit pnpm-lock.yaml changes
+git add pnpm-lock.yaml
+
+# ❌ Don't modify lockfile manually
+# ❌ Don't delete lockfile without reason
+```
+
+## Troubleshooting
+
+### Common Issues
+
+#### 1. "ELIFECYCLE" Errors
+
+```bash
+# Clear node_modules and reinstall
+pnpm clean-install
+# or
+rm -rf node_modules pnpm-lock.yaml && pnpm install
+```
+
+#### 2. Workspace Not Found
+
+```bash
+# Check workspace configuration
+cat pnpm-workspace.yaml
+
+# Ensure package has name in package.json
+grep '"name"' packages/*/package.json
+```
+
+#### 3. Dependency Resolution Issues
+
+```bash
+# Clear cache and reinstall
+pnpm store prune
+pnpm install --force
+```
+
+#### 4. Script Not Found
+
+```bash
+# Check available scripts
+pnpm run
+
+# Check package.json scripts section
+cat package.json | jq '.scripts'
+```
+
+### Performance Tips
+
+```bash
+# Use frozen lockfile for CI
+pnpm install --frozen-lockfile
+
+# Skip optional dependencies
+pnpm install --ignore-optional
+
+# Use specific package filters to avoid unnecessary work
+pnpm --filter react-ui run build  # Only build UI package
+```
+
+## Migration from npm/yarn
+
+### npm to pnpm equivalents
+
+| npm                    | pnpm                |
+| ---------------------- | ------------------- |
+| `npm install`          | `pnpm install`      |
+| `npm install <pkg>`    | `pnpm add <pkg>`    |
+| `npm install -D <pkg>` | `pnpm add -D <pkg>` |
+| `npm uninstall <pkg>`  | `pnpm remove <pkg>` |
+| `npm run <script>`     | `pnpm run <script>` |
+| `npm ls`               | `pnpm ls`           |
+| `npm outdated`         | `pnpm outdated`     |
+
+### yarn to pnpm equivalents
+
+| yarn                | pnpm                |
+| ------------------- | ------------------- |
+| `yarn`              | `pnpm install`      |
+| `yarn add <pkg>`    | `pnpm add <pkg>`    |
+| `yarn add -D <pkg>` | `pnpm add -D <pkg>` |
+| `yarn remove <pkg>` | `pnpm remove <pkg>` |
+| `yarn run <script>` | `pnpm run <script>` |
+
+## Questions?
+
+When in doubt:
+
+1. Check this document first
+2. Use `pnpm --help` for command options
+3. Check existing CI/CD scripts for patterns
+4. Ask in #engineering Slack channel
+
+Remember: **Always use pnpm, never npm or yarn** for any package management tasks in this project.
PATCH

echo "Gold patch applied."
