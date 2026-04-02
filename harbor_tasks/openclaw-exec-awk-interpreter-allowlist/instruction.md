# Exec Approvals: awk-family interpreters bypass allow-always security

## Bug Description

The exec approval system has a security gap in its interpreter detection. When a user selects "allow always" for a command, the system persists the executable path to an allowlist so future invocations are auto-approved. For interpreters like `python`, `node`, `ruby`, and `perl`, the system correctly identifies them as programs that can execute arbitrary inline code (via flags like `-c`, `-e`, `--eval`) and refuses to persist them — because allowing the interpreter binary would auto-approve _any_ inline code passed to it.

However, **awk-family programs** (`awk`, `gawk`, `mawk`, `nawk`) are not handled. Unlike the other interpreters, awk accepts inline programs as **positional arguments** rather than through flags. For example:

```
awk '{print $1}' data.csv
```

Here, `{print $1}` is an inline awk program — but the system doesn't detect it as inline code execution.

This creates a security bypass scenario:

1. User runs `awk '{print $1}' data.csv` and clicks "Allow Always"
2. The awk executable path gets persisted to the allowlist
3. Later, `awk 'BEGIN{system("rm -rf /")}'` is auto-approved because `awk` is on the allowlist

## Affected Files

- `src/infra/exec-inline-eval.ts` — Contains `detectInterpreterInlineEvalArgv()` which identifies interpreters with inline code execution, and `isInterpreterLikeAllowlistPattern()` which checks if an executable path is an interpreter. Neither handles the awk family.
- `src/infra/exec-approvals-allowlist.ts` — Contains `collectAllowAlwaysPatterns()` which decides what to persist. It needs to filter out awk interpreters using the detection from `exec-inline-eval.ts`.

## Expected Behavior

1. `detectInterpreterInlineEvalArgv` should detect awk inline programs passed as positional arguments (but NOT flag-based file references like `awk -f script.awk`)
2. `isInterpreterLikeAllowlistPattern` should recognize awk/gawk/mawk/nawk executable paths as interpreter-like
3. `collectAllowAlwaysPatterns` should not persist awk-family executable paths to the allow-always list

## Notes

- awk uses `-f` / `--file` to specify a script file — this is NOT inline eval and should not be flagged
- awk also accepts value flags like `-F` (field separator), `-v` (variable assignment) that take arguments and should be skipped when scanning for the positional program argument
- The existing interpreter detection uses a flag-based approach (looking for `-c`, `-e`, `--eval`); awk needs a different strategy since the program is positional
