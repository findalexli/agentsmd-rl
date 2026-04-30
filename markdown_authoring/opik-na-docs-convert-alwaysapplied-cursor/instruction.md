# [NA] [DOCS] Convert always-applied cursor rules to auto-attached rules

Source: [comet-ml/opik#3602](https://github.com/comet-ml/opik/pull/3602)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `apps/opik-backend/.cursor/rules/api_design.mdc`
- `apps/opik-backend/.cursor/rules/architecture.mdc`
- `apps/opik-backend/.cursor/rules/business_logic.mdc`
- `apps/opik-backend/.cursor/rules/code_quality.mdc`
- `apps/opik-backend/.cursor/rules/db_migration_script.mdc`
- `apps/opik-backend/.cursor/rules/error_handling.mdc`
- `apps/opik-backend/.cursor/rules/general.mdc`
- `apps/opik-backend/.cursor/rules/logging.mdc`
- `apps/opik-backend/.cursor/rules/mysql.mdc`
- `apps/opik-backend/.cursor/rules/tech_stack.mdc`
- `apps/opik-backend/.cursor/rules/testing.mdc`
- `apps/opik-frontend/.cursor/rules/accessibility-testing.mdc`
- `apps/opik-frontend/.cursor/rules/api-data-fetching.mdc`
- `apps/opik-frontend/.cursor/rules/code-quality.mdc`
- `apps/opik-frontend/.cursor/rules/forms.mdc`
- `apps/opik-frontend/.cursor/rules/frontend_rules.mdc`
- `apps/opik-frontend/.cursor/rules/performance.mdc`
- `apps/opik-frontend/.cursor/rules/state-management.mdc`
- `apps/opik-frontend/.cursor/rules/tech-stack.mdc`
- `apps/opik-frontend/.cursor/rules/ui-components.mdc`
- `apps/opik-frontend/.cursor/rules/unit-testing.mdc`
- `sdks/python/.cursor/rules/api-design.mdc`
- `sdks/python/.cursor/rules/architecture.mdc`
- `sdks/python/.cursor/rules/code-structure.mdc`
- `sdks/python/.cursor/rules/dependencies.mdc`
- `sdks/python/.cursor/rules/design-principles.mdc`
- `sdks/python/.cursor/rules/documentation-style.mdc`
- `sdks/python/.cursor/rules/error-handling.mdc`
- `sdks/python/.cursor/rules/logging.mdc`
- `sdks/python/.cursor/rules/method-refactoring-patterns.mdc`
- `sdks/python/.cursor/rules/test-best-practices.mdc`
- `sdks/python/.cursor/rules/test-implementation.mdc`
- `sdks/python/.cursor/rules/test-organization.mdc`
- `sdks/typescript/.cursor/rules/architecture.mdc`
- `sdks/typescript/.cursor/rules/code-structure.mdc`
- `sdks/typescript/.cursor/rules/integrations.mdc`
- `sdks/typescript/.cursor/rules/logging.mdc`
- `sdks/typescript/.cursor/rules/overview.mdc`
- `sdks/typescript/.cursor/rules/test-best-practices.mdc`

## What to add / change

## Details

This PR converts 39 cursor rules from "always-applied" to "agent-requestable" format to reduce context usage and improve model performance through context-aware rule fetching.

**Background:**

Cursor supports two types of workspace rules:
1. **Always-applied rules**: Automatically injected into every conversation (uses significant context tokens)
2. **Agent-requestable rules**: Listed by name only; AI fetches full content when needed based on file context

Previously, all component-specific rules (backend, frontend, and SDK rules) were marked as "always-applied", meaning their full content was injected into every conversation regardless of whether you were working on a Python file, Java file, or React component. This consumed significant context tokens unnecessarily and created noise in unrelated conversations.

**Directory-Based Rule Organization:**

Our rules are already organized by directory structure:
```
.cursor/rules/                    # Global rules (git workflow, project structure)
sdks/python/.cursor/rules/        # Python SDK-specific rules
sdks/typescript/.cursor/rules/    # TypeScript SDK-specific rules
apps/opik-backend/.cursor/rules/  # Backend-specific rules (Java/Dropwizard)
apps/opik-frontend/.cursor/rules/ # Frontend-specific rules (React/TypeScript)
```

This structure enables **context-aware rule fetching**: when the AI is working on a Python SDK file, it should only fetch Python SDK rules, not TypeScript or backend ru

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
