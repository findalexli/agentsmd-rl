# Bazel test targets shadow test/ directories in JavaScript packages

## Problem

The JavaScript atoms, chrome-driver, and webdriver packages each define a `closure_test_suite` target named `test` in their `BUILD.bazel` files. This name collides with the `test/` directory that contains the actual HTML test files.

When Bazel builds the runfiles tree, the `test` target binary occupies the `test` path as a file, preventing the `test/` directory (with the HTML test files) from existing at the same path. As a result, `Files.find()` discovers zero test files and no tests actually run.

## Expected Behavior

The `closure_test_suite` targets should have names that don't shadow the `test/` directories, allowing the test HTML files to be properly discovered and executed in the runfiles tree.

## Files to Look At

- `javascript/atoms/BUILD.bazel` — closure_test_suite target definition
- `javascript/chrome-driver/BUILD.bazel` — closure_test_suite target definition
- `javascript/webdriver/BUILD.bazel` — closure_test_suite target definition

After fixing the BUILD files, update any documentation that references the old target names so the examples remain correct. Check `javascript/atoms/README.md` — it contains example commands for running and debugging the tests.
