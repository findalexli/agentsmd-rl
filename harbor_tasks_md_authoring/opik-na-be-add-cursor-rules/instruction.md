# [NA] [BE] Add Cursor rules for backend test best practices

Source: [comet-ml/opik#3709](https://github.com/comet-ml/opik/pull/3709)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `apps/opik-backend/.cursor/rules/code_quality.mdc`
- `apps/opik-backend/.cursor/rules/code_style.mdc`
- `apps/opik-backend/.cursor/rules/general.mdc`
- `apps/opik-backend/.cursor/rules/test_assertions.mdc`
- `apps/opik-backend/.cursor/rules/test_async_patterns.mdc`
- `apps/opik-backend/.cursor/rules/testing.mdc`

## What to add / change

## Details

Added comprehensive Cursor rules for backend testing based on code review feedback from PR #3566 (OPIK-2598). These rules codify best practices for writing maintainable, effective tests and clean code style.

### New Rules Added:

1. **test-parameterization.mdc**
   - Use `@ParameterizedTest` to reduce test duplication
   - Ensure all factory fields are covered in tests
   - Use `Comparator<T>` instead of `Function` extractors
   - Proper import usage (avoid fully qualified names)
   - Single parameterized test for pagination scenarios
   - References to `AnnotationQueuesResourceTest` and `AlertResourceTest` as examples

2. **test-async-patterns.mdc**
   - When to use/avoid Awaitility (only for truly async operations)
   - Don't use Awaitility for synchronous MySQL operations
   - Avoid `Thread.sleep()` in tests
   - Troubleshooting timing issues between local and CI environments
   - Test performance best practices

3. **test-assertions.mdc**
   - Proper sorting test assertions (avoid self-fulfilling prophecy)
   - Test against known data order or use AssertJ's `.isSorted()`
   - Don't sort actual values and compare them to themselves
   - Three valid approaches for testing sorting
   - Proper filtering test patterns

4. **code-style.mdc**
   - Define reusable string templates (e.g., `RULE_PREFIX = "rule.%s"`)
   - Always use proper imports instead of fully qualified class names
   - Organize constants by category
   - Clean up commented-out code
   - Consistent 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
