## Improve SDK Generation Script

The SDK generation script at `src/Appwrite/Platform/Tasks/SDKs.php` has several issues that need to be addressed.

### 1. Version Update Scope Bug
The `updateSdkVersion()` method incorrectly updates version entries when the same SDK key exists under multiple platforms (e.g., both `consoleVersions` and `serverVersions` may have a `nodejs` entry). Currently the first matching entry is replaced globally, which may update the wrong platform's version.

**Observed behavior**: When multiple platforms share the same SDK key, the replacement operation affects whichever platform's entry is found first in the file, rather than the specific platform being processed.

**Expected fix**: Scope the version replacement operation to only the specific platform's version block. The callback function should receive the block content and use pattern matching to find the specific entry within that block.

### 2. Empty Git Commit Crash
When generating SDKs, if there are no changes to commit, the git library throws an exception. This crashes the script instead of being handled gracefully.

**Observed behavior**: The script terminates with an error when there are no changes to commit.

**Expected fix**: Wrap the git commit call in a try-catch block that catches `\Throwable`. When the exception indicates no changes to commit, log an informational message and return `true`. Re-throw other exceptions.

### 3. Missing Version Support
The supported versions list is missing '1.9.x' for the upcoming release. The current versions list ends with `1.8.x` followed by `latest`.

**Expected fix**: Add '1.9.x' to the versions array.

### 4. PR Update Logic Improvements
The `updateExistingPr()` method doesn't leverage the PR URL that `gh pr create` includes in its "already exists" error message. It also has an unused parameter.

**Observed behavior**: When `gh pr create` reports that a PR already exists, the PR URL from the error output is not captured.

**Expected fix**: Extract the PR URL from the gh CLI error output using a regex pattern that matches URLs. Add an `existingPrUrl` parameter to the method signature. Remove any unused parameters from the method signature. Use the extracted URL to avoid making a `gh pr list` API call.

### 5. Console Output Consistency
Console messages throughout the script use inconsistent formatting. Some use inline string concatenation, others use variable interpolation, and indentation varies.

**Expected fix**: Use consistent formatting with double-quoted strings using `{$variable}` interpolation. Hierarchical or logged output should use 2-space indentation.

### 6. Cleanup Method Removal
The `cleanupTarget()` private method should be replaced with inline cleanup calls.

**Expected fix**: Remove the `cleanupTarget()` method entirely. Use inline file system cleanup commands (such as `rm -rf` for recursive removal) instead of calling the removed method. Remove all calls to `$this->cleanupTarget()`.

## Files to Modify

- `src/Appwrite/Platform/Tasks/SDKs.php`

## Notes

- The changes are primarily refactoring and bug fixes - no new dependencies
- Focus on the `updateSdkVersion()`, `pushToGit()`, and `updateExistingPr()` methods
- The git commit exception handling should allow the operation to continue when there are no changes to commit