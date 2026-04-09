# Read Tool Directory Support

The `Read` tool (`packages/opencode/src/tool/read.ts`) currently only handles reading files. When a directory path is passed, the tool fails with "File not found" because the underlying existence check (`Bun.file(...).exists()`) returns `false` for directories.

## Requirements

1. **Add directory support to the read tool**: When given a directory path, the tool should return a sorted listing of its entries (files and subdirectories) with appropriate pagination using the existing offset/limit parameters. Subdirectories should be visually distinguished from files in the output.

2. **Fix the existence check**: Replace the current existence detection mechanism with one that correctly handles both files and directories.

3. **Modernize the output format**: The current line-numbered output format and XML wrapper should be updated for clarity. The tool description files (`read.txt` and `edit.txt`) must also be updated to accurately describe the new capabilities and output format.

4. **Update agent instructions**: The `.opencode/skill/bun-file-io/SKILL.md` should be updated to document the API behavior that motivated this fix, so future developers avoid the same pitfall.

Look at the existing code in `read.ts` to understand the current architecture before making changes.
