#!/usr/bin/env bash
set -euo pipefail

cd /workspace/console

# Idempotency guard
if grep -qF "npx nx run-many --all --target=lint --parallel  # Lint all projects" ".cursor/rules/development-commands.mdc" && grep -qF "- **Types/Interfaces**: PascalCase with `Props` suffix for interfaces if needed" ".cursor/rules/naming-conventions.mdc" && grep -qF "This project uses **semantic-release** with conventional commit format:" ".cursor/rules/pre-commit-workflow.mdc" && grep -qF "description: Qovery Console project architecture and structure guidelines" ".cursor/rules/project-architecture.mdc" && grep -qF "- ALWAYS use inline type imports: `import { type MyType, myFunction } from './mo" ".cursor/rules/react-typescript-standards.mdc" && grep -qF "- Use `clsx` or `twMerge` from `@qovery/shared/util-js` for conditional classes" ".cursor/rules/styling-standards.mdc" && grep -qF "globs: ['**/*.spec.ts', '**/*.spec.tsx', '**/*.test.ts', '**/*.test.tsx']" ".cursor/rules/testing-standards.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/development-commands.mdc b/.cursor/rules/development-commands.mdc
@@ -0,0 +1,59 @@
+---
+description: Common development commands and workflows
+globs: []
+alwaysApply: false
+---
+
+# Development Commands & Workflows
+
+## Daily Development
+
+```bash
+# Start development server
+yarn start                    # Start console app
+yarn storybook               # Start Storybook
+
+# Code quality
+yarn test                    # Run all tests
+npx nx format:write          # Format code
+npx nx run-many --all --target=lint --parallel  # Lint all projects
+
+# Build
+yarn build                   # Production build
+```
+
+## Nx Commands
+
+```bash
+# Generate new components/libs
+npx nx generate @nx/react:component MyComponent
+npx nx generate @nx/react:library my-lib
+
+# Run specific project commands
+npx nx test my-project
+npx nx lint my-project
+npx nx build my-project
+
+# Dependency graph
+npx nx graph
+```
+
+## Package Management
+
+- **Package Manager**: Yarn (lockfile present)
+- Always use `yarn` instead of `npm`
+- Run `yarn install` after pulling changes
+- Update dependencies carefully and test thoroughly
+
+## Git Workflow
+
+- Conventional commits recommended
+- Create feature branches from `staging`
+- Use descriptive commit messages
+- Squash commits when merging PRs
+
+## Environment Setup
+
+- Node.js version defined in `.nvmrc` (if present)
+- Use `nvm use` to switch to correct Node version
+- IDE configurations for ESLint and Prettier are included
diff --git a/.cursor/rules/naming-conventions.mdc b/.cursor/rules/naming-conventions.mdc
@@ -0,0 +1,37 @@
+---
+description: Naming conventions for files, components, and variables
+globs: ['**/*']
+alwaysApply: true
+---
+
+# Naming Conventions
+
+## File Naming
+
+- **Components**: Snake case (`user-profile.tsx`)
+- **Hooks**: Snake case with `use` prefix (`use-user.ts`)
+- **Utilities**: Snake case (`format-date.ts`)
+- **Types/Interfaces**: PascalCase with `Props` suffix for interfaces if needed
+- **Types**: PascalCase with `Type` suffix
+- **Enums**: PascalCase
+- **Constants**: UPPER_SNAKE_CASE
+
+## Variable Naming
+
+- **Variables**: camelCase
+- **Functions**: camelCase
+- **Classes**: PascalCase
+- **Constants**: UPPER_SNAKE_CASE
+- **Private members**: prefix with underscore `_privateMember`
+
+## Component Structure
+
+- Export components as named exports
+- Props interface should match component name + `Props`
+- Use descriptive, self-documenting names
+- Avoid abbreviations unless commonly understood
+
+## Comments
+
+- Avoid comments unless absolutely necessary
+- Comments in English only
diff --git a/.cursor/rules/pre-commit-workflow.mdc b/.cursor/rules/pre-commit-workflow.mdc
@@ -0,0 +1,134 @@
+---
+description: Pre-commit verification workflow and quality checks
+globs: []
+alwaysApply: false
+---
+
+# Pre-commit Verification Workflow
+
+## Commit Message Format
+
+This project uses **semantic-release** with conventional commit format:
+
+### Format Structure
+
+```
+<type>(<scope>): <description>
+
+[optional body]
+
+[optional footer(s)]
+```
+
+### Examples
+
+```bash
+# Features
+feat(button): add loading state animation
+feat(auth): implement OAuth2 login flow
+
+# Bug fixes
+fix(modal): prevent background scroll when open
+fix(api): handle network timeout errors
+
+# Other types
+docs(readme): update installation instructions
+style(header): improve responsive layout
+refactor(utils): simplify date formatting function
+test(user-service): add integration tests
+chore(deps): update react to v18.2.0
+```
+
+### Required Types
+
+- **feat**: New feature
+- **fix**: Bug fix
+- **docs**: Documentation changes
+- **style**: Code style changes (formatting, etc.)
+- **refactor**: Code refactoring
+- **test**: Adding or updating tests
+- **chore**: Maintenance tasks, dependency updates
+
+### Scope Guidelines
+
+- Use component name: `button`, `modal`, `header`
+- Use feature area: `auth`, `api`, `routing`
+- Use domain: `user-management`, `billing`
+
+## Required Checks Before Commit
+
+### 1. Format Check
+
+```bash
+npx nx format:check
+```
+
+If failed: Run `npx nx format:write` to fix formatting
+
+### 2. Tests
+
+```bash
+yarn test --passWithNoTests
+```
+
+All tests must pass before committing
+
+### 3. Snapshot Verification
+
+```bash
+git diff --name-only --cached | grep -E '\.snap$'
+```
+
+Review any snapshot changes carefully
+
+### 4. Lint Check
+
+```bash
+npx nx run-many --all --target=lint --parallel
+```
+
+Fix all linting errors before committing
+
+## Complete Pre-commit Script
+
+```bash
+#!/bin/bash
+
+# 1. Format check
+npx nx format:check
+if [ $? -ne 0 ]; then
+  echo "❌ Format check failed. Run 'npx nx format:write' to fix."
+  exit 1
+fi
+
+# 2. Tests
+yarn test --passWithNoTests
+if [ $? -ne 0 ]; then
+  echo "❌ Tests failed. Fix failing tests before committing."
+  exit 1
+fi
+
+# 3. Snapshot check
+git diff --name-only --cached | grep -E '\.snap$'
+if [ $? -eq 0 ]; then
+  echo "⚠️  Snapshot files detected. Review changes carefully."
+  echo "Updated snapshots:"
+  git diff --name-only --cached | grep -E '\.snap$'
+fi
+
+# 4. Lint check
+npx nx run-many --all --target=lint --parallel
+if [ $? -ne 0 ]; then
+  echo "❌ Lint failed. Fix linting errors before committing."
+  exit 1
+fi
+
+echo "✅ All pre-commit checks passed!"
+```
+
+## Quality Standards
+
+- No linting errors allowed
+- All tests must pass
+- Code must be properly formatted
+- Snapshot changes must be intentional and reviewed
diff --git a/.cursor/rules/project-architecture.mdc b/.cursor/rules/project-architecture.mdc
@@ -0,0 +1,38 @@
+---
+description: Qovery Console project architecture and structure guidelines
+globs: ['**/*']
+alwaysApply: true
+---
+
+# Qovery Console Architecture
+
+## Project Structure
+
+This project uses:
+
+- **Nx monorepo** with apps/ and libs/
+- **React 18** with TypeScript
+- **TailwindCSS** for styling
+- **React Query** for state management
+- **Jest** for testing
+- **ESLint** with strict rules
+
+## Directory Organization
+
+```
+libs/
+├── domains/         # Business logic by domain
+├── pages/           # Application pages/routes
+├── shared/          # Shared code
+│   ├── ui/          # Reusable UI components
+│   ├── util-*/      # Specialized utilities
+│   └── interfaces/  # Shared types
+```
+
+## Important Notes
+
+- Respect Nx architecture (no circular imports)
+- Use Nx generators to create new components/libs
+- `data-access` libs contain API logic
+- `feature` libs contain business components
+- `ui` libs contain reusable components
diff --git a/.cursor/rules/react-typescript-standards.mdc b/.cursor/rules/react-typescript-standards.mdc
@@ -0,0 +1,32 @@
+---
+description: React and TypeScript coding standards for Qovery Console
+globs: ['**/*.tsx', '**/*.ts']
+alwaysApply: false
+---
+
+# React & TypeScript Standards
+
+## Import Rules
+
+- ALWAYS use inline type imports: `import { type MyType, myFunction } from './module'`
+- Respect import order according to `.eslintrc.json`
+- Use `@qovery/*` aliases defined in `tsconfig.base.json`
+- DO NOT import directly from `react` (destructure React)
+- Use `@qovery/shared/util-tests` instead of `@testing-library/react`
+
+## React Components
+
+- Functional components only
+- No explicit `React.FC`
+- Destructure props directly in parameters
+- Use `clsx` or `twMerge` from `@qovery/shared/util-js` for conditional classes
+- Prefer Radix UI components when available
+
+## State Management
+
+- Use React Query for API calls
+
+## Performance
+
+- Use `React.memo()` for expensive components
+- `useCallback` and `useMemo` only when necessary
diff --git a/.cursor/rules/styling-standards.mdc b/.cursor/rules/styling-standards.mdc
@@ -0,0 +1,36 @@
+---
+description: Styling and design standards using TailwindCSS
+globs: ['**/*.tsx']
+alwaysApply: false
+---
+
+# Styling Standards
+
+## TailwindCSS Usage
+
+- TailwindCSS only (no CSS modules or styled-components in new code)
+- Use utilities from `@qovery/shared/ui` when available
+- Mobile-first responsive design
+- Use `clsx` or `twMerge` from `@qovery/shared/util-js` for conditional classes
+
+## Component Styling
+
+- Prefer Radix UI components for accessibility
+- Consistent spacing using Tailwind scale
+- Use CSS variables for theme colors
+- Avoid inline styles
+
+## Responsive Design
+
+- Mobile-first approach
+- Use Tailwind breakpoints: `sm:`, `md:`, `lg:`, `xl:`
+- Test on multiple screen sizes
+- Ensure touch-friendly interfaces
+
+## Accessibility
+
+- Follow `jsx-a11y` rules
+- Use semantic HTML elements
+- Provide proper ARIA labels
+- Test with screen readers
+- Ensure keyboard navigation works
diff --git a/.cursor/rules/testing-standards.mdc b/.cursor/rules/testing-standards.mdc
@@ -0,0 +1,32 @@
+---
+description: Testing standards and practices for Qovery Console
+globs: ['**/*.spec.ts', '**/*.spec.tsx', '**/*.test.ts', '**/*.test.tsx']
+alwaysApply: false
+---
+
+# Testing Standards
+
+## Test Setup
+
+- Use `renderWithProviders` from `@qovery/shared/util-tests`
+- Prefer `userEvent` over `fireEvent`
+- Unit tests are mandatory for business logic
+- Snapshots for complex UI components
+
+## Test Structure
+
+- Arrange-Act-Assert pattern
+- Descriptive test names
+- Group related tests with `describe` blocks
+- Use `beforeEach` for common setup
+
+## Mocking
+
+- Mock external dependencies appropriately
+- Avoid over-mocking - test real behavior when possible
+
+## Coverage
+
+- Focus on critical paths and edge cases
+- Test user interactions, not implementation details
+- Ensure error states are covered
PATCH

echo "Gold patch applied."
