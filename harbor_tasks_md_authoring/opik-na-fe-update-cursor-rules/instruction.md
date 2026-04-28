# [NA] [FE] Update cursor rules or FE

Source: [comet-ml/opik#3278](https://github.com/comet-ml/opik/pull/3278)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `apps/opik-frontend/.cursor/rules/accessibility-testing.mdc`
- `apps/opik-frontend/.cursor/rules/api-data-fetching.mdc`
- `apps/opik-frontend/.cursor/rules/code-quality.mdc`
- `apps/opik-frontend/.cursor/rules/forms.mdc`
- `apps/opik-frontend/.cursor/rules/performance.mdc`
- `apps/opik-frontend/.cursor/rules/state-management.mdc`
- `apps/opik-frontend/.cursor/rules/tech-stack.mdc`
- `apps/opik-frontend/.cursor/rules/ui-components.mdc`
- `apps/opik-frontend/.cursor/rules/unit-testing.mdc`

## What to add / change

## Details

This PR enhances the frontend development guidelines by significantly expanding the Cursor rules for code quality and UI components. The changes provide comprehensive standards and best practices for TypeScript development, component architecture, and UI design system usage in the Opik frontend.

**Key improvements:**

1. **Enhanced Code Quality Rules** (`code-quality.mdc`):
   - Added comprehensive TypeScript patterns and component type definitions
   - Introduced API response type standards and error handling patterns  
   - Established naming conventions for files, functions, and variables
   - Defined import organization standards
   - Added async/await patterns and promise handling guidelines

2. **Expanded UI Component Guidelines** (`ui-components.mdc`):
   - Detailed button component patterns with all variants and sizes
   - Comprehensive DataTable component usage patterns
   - Form component guidelines and validation patterns
   - Modal and dialog component standards
   - Loading state and empty state component patterns

These rules will help ensure consistent code quality, improve developer experience, and maintain design system compliance across the frontend codebase.

## Change checklist
- [ ] User facing
- [] Documentation update

## Issues
- NA

## Testing

## Documentation

- Updated `apps/opik-frontend/.cursor/rules/code-quality.mdc` with comprehensive TypeScript patterns, naming conventions, and development standard

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
