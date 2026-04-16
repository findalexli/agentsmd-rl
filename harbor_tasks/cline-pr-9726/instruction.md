# cline CLI: Add `--continue` Flag for Current Directory

## Problem

When running `cline` from a directory, there's no way to resume the most recent task that was started from that same directory. Users must manually find and specify the task ID.

## Expected Behavior

Add a `--continue` flag to the CLI that, when used without arguments, automatically finds and resumes the most recent task from the current working directory.

### Functional Requirements

1. **Task History Utility**: Implement a utility function in `cli/src/utils/task-history.ts` that queries task history and identifies tasks associated with a specific workspace directory.
   - Export a function named `findMostRecentTaskForWorkspace`
   - Task history entries contain workspace path information (such as `cwdOnTaskInitialization` and `shadowGitConfigWorkTree`) and timestamps (`ts`)
   - The function must handle empty or undefined task history, returning null when no valid entries exist
   - The function must sort by timestamp in descending order (newest first), using the expression `b.ts - a.ts` for comparison
   - Filter out history items that lack valid timestamps or task IDs

2. **CLI Flag Implementation**: In `cli/src/index.ts`:
   - Define a `--continue` flag in the CLI options
   - Implement an `async function continueTask` that uses the task history utility
   - When `--continue` is passed without arguments, find and resume the most recent task for the current directory
   - If no previous task exists for the current directory, display a warning and exit with code 1
   - The `--continue` flag should be mutually exclusive with `--taskId`
   - The `--continue` flag should not accept a prompt argument
   - The `--continue` flag should not work with piped stdin

3. **Unit Tests**: Create a test file `cli/src/utils/task-history.test.ts` with tests covering:
   - Finding the newest matching task for a workspace among multiple entries with different timestamps (include patterns like `ts.*200`)
   - Returning null when no matching task exists (use `toBeNull` matcher)

4. **Documentation**: Update CLI documentation (man page and reference docs) to describe the new `--continue` flag.

## Notes

- The task history is stored via the global state manager
- Cross-platform path comparison should handle path normalization
- Follow existing patterns in the codebase for CLI flag handling and task management
- The solution must pass the existing repository lint (biome) and unit tests (vitest) on `cli/src/`
