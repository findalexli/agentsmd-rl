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

## Expected Behavior

1. **Inline program detection** — The system must detect when awk/gawk/mawk/nawk is invoked with an inline program passed as a positional argument (not via `-f`/`--file`). Value flags like `-F` (field separator), `-v` (variable assignment), `-i`, `-l`, `-W` and their long-form equivalents should be skipped when scanning for the positional program argument. The `--` double-dash separator marks the end of options; anything after it should be treated as a positional argument.

2. **Interpreter recognition** — Awk-family executables must be recognized as interpreter-like, so they are not persisted to the allow-always allowlist. This includes bare names (`awk`, `gawk`, `mawk`, `nawk`) and paths (e.g., `/usr/bin/awk`, `/usr/local/bin/awk`). Wildcard patterns like `**/gawk` should also be recognized.

3. **Allowlist filtering** — The allow-always persist logic must not store awk-family executable paths.

### Return Value Schema

`detectInterpreterInlineEvalArgv` returns a hit object (a dictionary) with these keys:
- `executable` (string): the executable name as invoked
- `normalizedExecutable` (string): normalized lowercase executable name
- `flag` (string): for flag-based interpreters this is the flag (e.g., `-c`); for awk-style positional programs this is the literal string `'<program>'`
- `argv` (array): the full argument vector

When the hit describes an awk inline program, `describeInterpreterInlineEval` returns a string in the format `'<variant> inline program'`, e.g., `"awk inline program"`, `"gawk inline program"`.

### Edge Cases

- `awk -f script.awk` is file-based execution, NOT inline eval — must NOT be detected
- `awk -F "," '{print $1}' data.csv` — the `-F ","` value flag should be skipped; the positional `{print $1}` is the inline program
- `awk -- '{print $1}'` — the `--` separator means `{print $1}` is a positional program
- `awk --` with nothing following — should NOT detect anything (no inline program present)