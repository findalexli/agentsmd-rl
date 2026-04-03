# Consolidate Python Browser Test Targets in BUILD.bazel

## Problem

The Python test configuration in `py/BUILD.bazel` has significant duplication. Each browser (chrome, edge, firefox, ie, safari) has its own hardcoded `py_test_suite` block, and there are separate `common-<browser>` targets that only run common tests without browser-specific ones. This means:

1. Adding a new browser requires copying ~20 lines of boilerplate
2. The `common-<browser>` and `test-<browser>` targets are confusingly separate — `common-<browser>` runs common tests, while `test-<browser>` runs only browser-specific tests
3. The BiDi test targets (`common-<browser>-bidi`) are generated for all browsers even though only some support BiDi

Additionally, `py/private/browsers.bzl` passes `--headless=true` but the correct Selenium CLI flag is just `--headless`.

## Expected Behavior

- A single browser configuration dict should define which browsers exist, their test sources, and their capabilities (e.g., BiDi support)
- Test targets should be generated from this dict via list comprehension, combining both common and browser-specific test sources into unified `test-<browser>` targets
- BiDi targets should only be generated for browsers that actually support BiDi
- The `--headless` flag in `browsers.bzl` should not include `=true`

After making these build system changes, update the project's `README.md` to reflect the new test target names and document headless test execution. The Python test documentation currently references `//py:common-<browsername>` targets that will no longer exist.

## Files to Look At

- `py/BUILD.bazel` — Python test target definitions; the main file to refactor
- `py/private/browsers.bzl` — Headless flag configuration
- `README.md` — Python test commands documentation (search for "Python Test Commands")
