# Refactor Bazel test-target indexing to operate at the file level

The Selenium repo uses a Bazel rake task (`rake_tasks/bazel.rake`,
namespaced under `bazel:` in the Rakefile) to compute which test
targets are affected by a set of changed files in a CI run. Two tasks
are involved:

- `bazel:build_test_index` builds an index file used for fast lookups.
- `bazel:affected_targets` consumes that index plus a list of changed
  files and emits the affected test targets.

Today the index is **package-level**: it maps each Bazel package (e.g.
`"py"`) to the set of test targets that depend on anything in that
package. That works well for Java (where one package roughly equals
one Java module), is OK for Ruby, and is poor for Python — any change
to any file under `py/` invalidates every Python test target. Issue
context: see #17012 and PR #17033.

Refactor the index to be **file-level**: keys are *relative source-file
paths* (e.g. `"py/some/dir/file.py"`), values are the lists of test
targets that depend on that file.

## Required behavior

### 1. High-impact directory short-circuit

Some directories are shared infrastructure whose contents transitively
affect every binding. Changes to any file under one of these
directories must trigger ALL bindings — without consulting the index:

- `common/` (any depth)
- `rust/src/` (note: `rust/src/`, *not* `rust/` — files under `rust/`
  but outside `rust/src/`, such as `rust/Cargo.toml`, are NOT
  high-impact)
- `javascript/atoms/`
- `javascript/webdriver/atoms/`

Implement this as two top-level Ruby constants in `rake_tasks/bazel.rake`:

- **`HIGH_IMPACT_DIRS`** — a frozen array of the four directory strings
  above, exactly: `"common"`, `"rust/src"`, `"javascript/atoms"`,
  `"javascript/webdriver/atoms"`. The list must NOT contain plain
  `"rust"`.
- **`HIGH_IMPACT_PATTERN`** — a `Regexp` derived from `HIGH_IMPACT_DIRS`
  that matches when, and only when, a path begins with one of those
  directories at a directory boundary. That is:
  - `"common/foo.txt"` matches; `"mycommon/foo.txt"` does NOT.
  - `"rust/src/main.rs"` and `"rust/src/handler/mod.rs"` match;
    `"rust/foo.rs"` does NOT.
  - `"javascript/atoms/foo.js"` matches;
    `"javascript/atoms-helper/foo.js"` does NOT.
  - `"javascript/webdriver/atoms/bar.js"` matches.
  - Files under `java/`, `py/`, `rb/` (other than via the above) do NOT
    match.

The `bazel:affected_targets` task must, before any index lookup, check
whether any changed file matches `HIGH_IMPACT_PATTERN`; if so, return
all binding targets (`BINDING_TARGETS.values` from
`rake_tasks/common.rb`) without further work.

### 2. File-level lookup in `affected_targets_with_index`

Given an index whose keys are full relative file paths, looking up an
indexed file must return its mapped test targets directly. Concrete
contract: with index

```json
{
  "py/some_source.py": ["//py:test_a", "//py:test_b"],
  "rb/lib/foo.rb":     ["//rb:tests"]
}
```

calling the helper with changed file `"py/some_source.py"` must
include `"//py:test_a"` and `"//py:test_b"` in the affected set; with
multiple changed files, each file's mapped tests must be unioned into
the affected set (so `["py/file_a.py", "rb/file_b.rb"]` against an
index mapping each yields both `"//py:test_a"` and `"//rb:test_b"`).

This is a behavioral change from the previous package-level lookup —
the previous code would resolve a changed file to its containing
Bazel package and look the package up in the index; now the changed
file path itself is the lookup key.

### 3. File-level index produced by `bazel:build_test_index`

After this change, the JSON index produced by `bazel:build_test_index`
must be keyed by relative source-file paths (every key contains a `/`
separator — e.g. `"py/source.py"`), not by bare Bazel package names
(e.g. `"py"`).

To go from package-level to file-level, the index builder must, for
each test target's dependencies, enumerate the source files of each
dependency and add an entry per source file. Use a Bazel query that
returns the labels of a target's `srcs` attribute (the canonical query
verb is `labels(srcs, <target>)`); the test harness recognises that
form. For example, given test `//py:foo_test` whose deps include
`//py:lib`, and `labels(srcs, //py:lib)` returns
`//py:source.py` and `//py:other.py`, the resulting index must
contain entries `"py/source.py" → [..., "//py:foo_test", ...]` and
`"py/other.py" → [..., "//py:foo_test", ...]` — the leading `//` is
stripped and the `:` separator is replaced with `/`.

Cache the per-dep source enumeration so each unique dep is queried
once per index build (many tests share the same deps such as
`//py:common`).

## Existing helpers and where to put things

- The rake file is `rake_tasks/bazel.rake`. Its rake tasks live under
  the `bazel:` namespace (e.g. invoked via
  `./go bazel:build_test_index <output>` and
  `./go bazel:affected_targets`).
- `BINDING_TARGETS` is defined in `rake_tasks/common.rb` and is in
  scope when the rake file is loaded by the top-level `Rakefile`.
- `Bazel.execute(kind, args, target) { |out| ... }` (defined in
  `rake_tasks/bazel.rb`) is the existing wrapper around the `bazel`
  CLI; pass the query string as `target` and parse the captured output
  inside the block.

## Out of scope

- The CI workflow files (`.github/workflows/ci.yml`,
  `.github/workflows/ci-build-index.yml`) reference the artifact /
  cache name for the produced index. Renaming those references is
  fine but is not graded.
- Existing top-level helpers that are not required by the file-level
  flow may be removed if they have no remaining callers.
