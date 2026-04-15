# Fix GitInfo handling for modules with missing Origin

## Background

Hugo's GitInfo feature provides version control metadata (commit hash, author, date) for content files. When using Hugo Modules, the system calls `go list` to obtain module metadata, including a `ModuleOrigin` struct with VCS info (URL, VCS type, hash, ref).

## Problem

Due to golang/go#67363, `go list` sometimes returns modules with `Origin` set to nil. The current codebase has several issues when this happens:

1. **No way to detect zero/uninitialized Origin**: The `ModuleOrigin` type has fields `VCS`, `URL`, `Hash`, and `Ref`, but lacks a method to report whether it's zero-valued/uninitialized. A `ModuleOrigin{}` (all fields empty) should be distinguishable from one that has actual data like `ModuleOrigin{URL: "https://github.com/example/repo", VCS: "git"}`.

2. **Origin data available but unused**: The module cache stores `.info` JSON files alongside `.mod` files. These contain Origin data in this structure:
   ```json
   {"Version":"...","Time":"...","Origin":{"VCS":"git","URL":"...","Hash":"..."}}
   ```
   When `go list` returns a module with nil Origin, this data is available in the cache but is never loaded.

3. **False positive in project-is-module detection**: The gitinfo code that determines whether the project itself is a Git module can incorrectly succeed even when the module's Origin data isn't actually available/populated.

4. **Errors silently ignored**: The `loadGitInfo()` function handles failures from `newGitInfo()` by logging them with `h.Log.Errorln("Failed to read Git log:", err)` and continuing execution, rather than propagating the error to the caller.

## Expected Correct Behavior

After the fix, the following must hold:

- `ModuleOrigin` should have an `IsZero() bool` method. When called on `ModuleOrigin{}` (zero value), it should return `true`. When called on a populated origin (e.g., with URL `"https://github.com/example/repo"` and VCS `"git"`), it should return `false`.

- When processing modules, if a module has `m.Origin == nil` and `m.GoMod != ""`, the code should derive the `.info` filename from the `.mod` filename as `strings.TrimSuffix(m.GoMod, ".mod") + ".info"`, read the file, and use `json.Unmarshal` to extract the Origin data from it.

- The gitinfo code should include the check `!mod.Origin().IsZero()` as part of determining whether the project is a Git module, ensuring Origin is actually populated before relying on it.

- The `loadGitInfo()` function should propagate errors from `newGitInfo()` using `return err` rather than the current pattern of `h.Log.Errorln("Failed to read Git log:", err)`.

## Verification

After implementing the fix:
1. The code should compile without errors
2. The modules and hugolib packages should pass their existing tests
3. `go vet` and `gofmt` should pass on the modified packages
