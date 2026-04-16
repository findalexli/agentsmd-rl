# Improve SDK Generation Script

## Problem Description

The SDK generation script at `src/Appwrite/Platform/Tasks/SDKs.php` has several issues that need to be addressed.

### 1. Version Update Scope Bug
The `updateSdkVersion()` method incorrectly updates version entries when the same SDK key exists under multiple platforms (e.g., both `consoleVersions` and `serverVersions` may have a `nodejs` entry). Currently the first matching entry is replaced globally, which may update the wrong platform's version.

**Observed behavior**: When multiple platforms share the same SDK key, the replacement operation affects whichever platform's entry is found first in the file, rather than the specific platform being processed.

**Expected fix**: Scope the version replacement operation to only the specific platform's version block.

### 2. Empty Git Commit Crash
When generating SDKs, if there are no changes to commit, the git library throws an exception. This crashes the script instead of being handled gracefully.

**Observed behavior**: The script terminates with an error when there are no changes to commit.

**Expected fix**: Handle the empty-commit case gracefully and continue execution. When no changes exist, log an appropriate informational message and treat it as a successful operation.

### 3. Missing Version Support
The supported versions list is missing '1.9.x' for the upcoming release. The current versions are: '0.6.x', '0.7.x', '0.8.x', '0.9.x', '0.10.x', '0.11.x', '0.12.x', '0.13.x', '0.14.x', '0.15.x', '1.0.x', '1.1.x', '1.2.x', '1.3.x', '1.4.x', '1.5.x', '1.6.x', '1.7.x', '1.8.x', 'latest'.

**Expected fix**: Add '1.9.x' to the versions array after '1.8.x'.

### 4. PR Update Logic Improvements
The `updateExistingPr()` method doesn't leverage the PR URL that `gh pr create` includes in its "already exists" error message. It also has an unused parameter.

**Observed behavior**: When `gh pr create` reports that a PR already exists, the PR URL from the error output is not captured.

**Expected fix**: Extract the PR URL from the gh CLI error output. Remove the unused parameter from the method signature.

### 5. Console Output Consistency
Console messages throughout the script use inconsistent formatting. Some use inline string concatenation, others use variable interpolation, and indentation varies.

**Expected fix**: Use consistent formatting with double-quoted strings using `{$variable}` interpolation. Hierarchical or logged output should use 2-space indentation.

### 6. Cleanup Method Removal
The `cleanupTarget()` private method should be replaced with inline cleanup calls.

**Expected fix**: Remove the `cleanupTarget()` method entirely. Use inline file system cleanup commands.

## Files to Modify

- `src/Appwrite/Platform/Tasks/SDKs.php`

## Notes

- The changes are primarily refactoring and bug fixes - no new dependencies
- Focus on the `updateSdkVersion()`, `pushToGit()`, and `updateExistingPr()` methods
- The git commit exception handling should allow the operation to continue when there are no changes to commit
