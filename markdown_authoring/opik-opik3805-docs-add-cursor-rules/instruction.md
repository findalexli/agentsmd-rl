# [OPIK-3805] [DOCS] Add Cursor rules for responsive design

Source: [comet-ml/opik#4710](https://github.com/comet-ml/opik/pull/4710)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `apps/opik-frontend/.cursor/rules/frontend_rules.mdc`
- `apps/opik-frontend/.cursor/rules/responsive-design.mdc`

## What to add / change

## Details

Add guidelines on when to use Tailwind CSS `md:` breakpoints vs `useIsPhone` JavaScript hook for responsive design.

This helps developers:
- Choose the right approach for responsive styling
- Avoid unnecessary JavaScript evaluation when CSS would suffice
- Reduce code duplication and inconsistent responsive behavior
- Improve performance by preferring CSS-based solutions

### Changes
- **New file**: `apps/opik-frontend/.cursor/rules/responsive-design.mdc` with:
  - Decision framework for when to use each approach
  - Mobile-first mapping: `md:` = opposite of `isPhonePortrait`
  - Onboarding exception: mobile support required by default for onboarding features
  - Code examples with good/bad patterns
  - Performance considerations
  - Quick reference table
  - Documentation of `useIsPhone`, `useMediaQuery` hooks and responsiveness constants
- **Updated**: `apps/opik-frontend/.cursor/rules/frontend_rules.mdc` - Added reference to new rule
- **Updated**: `AGENTS.md` - Added `responsive-design.mdc` to frontend rules list

## Change checklist
- [x] User facing
- [x] Documentation update

## Issues

- OPIK-3805

## Testing

N/A - This is a documentation-only change (Cursor rules).

## Documentation

- Added new Cursor rule file with comprehensive guidelines
- Cross-references to existing `ui-components.mdc` and `performance.mdc` rules
- Addresses PR feedback: onboarding features should support mobile by default

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
