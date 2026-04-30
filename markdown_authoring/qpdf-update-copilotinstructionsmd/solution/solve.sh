#!/usr/bin/env bash
set -euo pipefail

cd /workspace/qpdf

# Idempotency guard
if grep -qF "PDF files. It supports linearization, encryption, page splitting/merging, and PD" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -1,7 +1,9 @@
 # Copilot Coding Agent Instructions for qpdf
 
 ## Repository Summary
-qpdf is a command-line tool and C++ library that performs content-preserving transformations on PDF files. It supports linearization, encryption, page splitting/merging, and PDF file inspection. Version: 12.3.0.
+qpdf is a command-line tool and C++ library that performs content-preserving transformations on
+PDF files. It supports linearization, encryption, page splitting/merging, and PDF file inspection.
+Version: 12.3.0.
 
 **Project Type:** C++ library and CLI tool (C++20 standard)  
 **Build System:** CMake 3.16+ with Ninja generator  
@@ -29,10 +31,13 @@ cmake --build --preset maintainer  # Build
 ctest --preset maintainer          # Test
 ```
 
-Available presets: `maintainer`, `maintainer-debug`, `maintainer-coverage`, `maintainer-profile`, `debug`, `release`, `sanitizers`, `msvc`, `msvc-release`. Use `cmake --list-presets` to see all options.
+Available presets: `maintainer`, `maintainer-debug`, `maintainer-coverage`, `maintainer-profile`,
+`debug`, `release`, `sanitizers`, `msvc`, `msvc-release`. Use `cmake --list-presets` to see all
+options.
 
 ### Build Notes
-- **Always build out-of-source** in a subdirectory (e.g., `build/`). In-source builds are explicitly blocked.
+- **Always build out-of-source** in a subdirectory (e.g., `build/`). In-source builds are
+  explicitly blocked.
 - Build time: approximately 2-3 minutes on typical CI runners.
 - Test suite time: approximately 1 minute for all 7 test groups.
 - The `MAINTAINER_MODE` cmake option enables stricter checks and auto-generation of job files.
@@ -54,7 +59,8 @@ ctest -R fuzz        # Fuzzer tests
 ctest --verbose
 ```
 
-**Test Framework:** Tests use `qtest` (a Perl-based test framework). Tests are invoked via `ctest` and compare outputs against expected files. Test coverage uses `QTC::TC` macros.
+**Test Framework:** Tests use `qtest` (a Perl-based test framework). Tests are invoked via `ctest`
+and compare outputs against expected files. Test coverage uses `QTC::TC` macros.
 
 ## Code Formatting
 ```bash
@@ -86,7 +92,8 @@ ctest --verbose
 | `job.yml` | Command-line argument definitions (auto-generates code) |
 | `generate_auto_job` | Python script that generates argument parsing code |
 | `.clang-format` | Code formatting rules |
-| `README-maintainer.md` | Detailed maintainer and coding guidelines |
+| `README-developer.md` | Developer guidelines for modifying qpdf |
+| `README-maintainer.md` | Maintainer notes for release preparation and maintainers |
 
 ### Auto-Generated Files
 When modifying `job.yml` or CLI options, regenerate with:
@@ -110,36 +117,60 @@ When modifying `job.yml` or CLI options, regenerate with:
 ## Coding Conventions
 
 ### Must Follow
-1. **Assertions**: Test code should include `qpdf/assert_test.h` first. Debug code should include `qpdf/assert_debug.h` and use `qpdf_assert_debug` instead of `assert`. Use `qpdf_expect`, `qpdf_ensures`, `qpdf_invariant` for pre/post-conditions. Never use raw `assert()`. The `check-assert` test enforces this.
+1. **Assertions**: Test code should include `qpdf/assert_test.h` first. Debug code should include
+   `qpdf/assert_debug.h` and use `qpdf_assert_debug` instead of `assert`. Use `qpdf_expect`,
+   `qpdf_ensures`, `qpdf_invariant` for pre/post-conditions. Never use raw `assert()` in non-test
+   code. The `check-assert` test enforces this.
 2. **Use `QIntC` for type conversions** - Required for safe integer casting.
 3. **Avoid `operator[]`** - Use `.at()` for std::string and std::vector (see README-hardening.md).
 4. **Include order**: Include the class's own header first, then a blank line, then other includes.
 5. **Use `std::to_string`** instead of QUtil::int_to_string.
+6. **Preserve existing symbols by default**: Do not remove or rename existing functions, methods,
+   constructors, enum values, or CLI option names unless explicitly requested in the task.
+7. **Locale-safe number output** - Always imbue `ostringstream` with `std::locale::classic()`
+   before outputting numbers, to prevent the user's global locale from altering numeric output.
+8. **DLL export annotation** - New public methods in `include/qpdf/` must be annotated with
+   `QPDF_DLL`; use `QPDF_DLL_CLASS` for classes whose type info is needed across the shared
+   library boundary.
+9. **Avoid `atoi`** - Use `QUtil::string_to_int` instead; it provides overflow/underflow checking.
+10. **Avoid `min`/`max` macros** - Use `std::min`/`std::max` with `<algorithm>` included.
 
 ### New Code Style (See `libqpdf/qpdf/AcroForm.hh` FormNode class for examples)
-1. **PIMPL Pattern**: New public classes should use the PIMPL (Pointer to Implementation) pattern with a full implementation class. See `QPDFAcroFormDocumentHelper::Members` as an example.
+1. **PIMPL Pattern**: New public classes should use the PIMPL (Pointer to Implementation) pattern
+   with a full implementation class. See `QPDFAcroFormDocumentHelper::Members` as an example.
 2. **Avoid `this->`**: Do not use `this->` and remove it when updating existing code.
-3. **QTC::TC Calls**: Remove simple `QTC::TC` calls (those with 2 parameters) unless they are the only executable statement in a branch.
+3. **QTC::TC Calls**: Remove simple `QTC::TC` calls (those with 2 parameters) unless they are the
+   only executable statement in a branch.
    - When removing a `QTC::TC` call:
       - Use the first parameter to find the corresponding `.testcov` file.
-      - Remove the line in the `.testcov` (or related coverage file) that includes the second parameter.
-4. **Doxygen Comments**: Use `///` style comments with appropriate tags (`@brief`, `@param`, `@return`, `@tparam`, `@since`).
+      - Remove the line in the `.testcov` (or related coverage file) that includes the second
+        parameter.
+4. **Doxygen Comments**: Use `///` style comments with appropriate tags (`@brief`, `@param`,
+   `@return`, `@tparam`, `@since`).
    ```cpp
    /// @brief Retrieves the field value.
    ///
    /// @param inherit If true, traverse parent hierarchy.
    /// @return The field value or empty string if not found.
    std::string value() const;
    ```
-5. **Member Variables**: Use trailing underscores for member variables (e.g., `cache_valid_`, `fields_`).
+5. **Member Variables**: Use trailing underscores for member variables (e.g., `cache_valid_`,
+   `fields_`).
 6. **Naming Conventions**:
-   - Use `snake_case` for new function and variable names (e.g., `fully_qualified_name()`, `root_field()`).
-   - **Exception**: PDF dictionary entry accessors and variables use the exact capitalization from the PDF spec (e.g., `FT()`, `TU()`, `DV()` for `/FT`, `/TU`, `/DV`).
-7. **Getters/Setters**: Simple getters/setters use the attribute name without "get" or "set" prefixes:
+   - Use `snake_case` for new function and variable names (e.g., `fully_qualified_name()`,
+     `root_field()`).
+   - **Exception**: PDF dictionary entry accessors and variables use the exact capitalization from
+     the PDF spec (e.g., `FT()`, `TU()`, `DV()` for `/FT`, `/TU`, `/DV`).
+   - Legacy class names often start with `QPDF` (e.g., `QPDFParser`) and should be preserved.
+   - New classes should be defined in namespace `qpdf`; in `.cc` files, add
+     `using namespace qpdf;` after includes unless no `qpdf` symbols are used.
+7. **Getters/Setters**: Simple getters/setters use the attribute name without "get" or "set"
+   prefixes:
    ```cpp
    String TU() const { return {get("/TU")}; }
    ```
-   Note: Names like `setFieldAttribute()` are legacy naming; new code should use `snake_case` (e.g., `set_field_attribute()`).
+   Note: Names like `setFieldAttribute()` are legacy naming; new code should use `snake_case`
+   (e.g., `set_field_attribute()`).
 
 The qpdf API is being actively updated. Prefer the new internal APIs in code in the libqpdf and
 libtests directories:
@@ -148,14 +179,65 @@ libtests directories:
    initially. Do not use in code in other directories, e.g. examples
 9. **Prefer typed handles** - Use `BaseHandle` methods and typed object handles (`Integer`,
    `Array`, `Dictionary`, `String`) over generic `QPDFObjectHandle`
-10. **Use PIMPL pattern** - Prefer private implementation classes (`Members` classes) for
-   internal use
-11. **Array semantics** - Array methods treat scalars as single-element arrays and null as empty
-   array (per PDF spec)
-12. **Map semantics** - Map methods treat null values as missing entries (per PDF spec)
-13. **Object references** - Methods often return references; avoid unnecessary copying but copy
-   if reference may become stale
-14. **Thread safety** - Object handles cannot be shared across threads
+10. **Prefer private API over public `QPDFObjectHandle` methods** - In `libqpdf/` and `libtests/`,
+    use typed handles from `libqpdf/qpdf/QPDFObjectHandle_private.hh` or `BaseHandle` methods
+    defined in `include/qpdf/ObjectHandle.hh` in preference to public `QPDFObjectHandle` methods:
+
+    | Avoid (`QPDFObjectHandle`)    | Prefer                                     |
+    |-------------------------------|--------------------------------------------|
+    | `appendItem(item)`            | `Array(obj).push_back(item)`               |
+    | `aitems()`                    | `for (auto item : Array(obj))`             |
+    | `ditems()`                    | `for (auto& [k, v] : Dictionary(obj))`     |
+    | `eraseItem(at)`               | `Array(obj).erase(at)`                     |
+    | `getArrayAsVector()`          | `Array(obj)`                               |
+    | `getArrayItem(n)`             | `obj[n]`                                   |
+    | `getArrayNItems()`            | `size()`                                   |
+    | `getDict()` (stream)          | `Stream(obj).getDict()`                    |
+    | `getDictAsMap()`              | `Dictionary(obj)`                          |
+    | `getIntValue()`               | `Integer(obj).value()`                     |
+    | `getIntValueAsInt()`          | `Integer(obj).value<int>()`                |
+    | `getKey(key)`                 | `obj[key]`                                 |
+    | `getKeys()`                   | `Dictionary(obj)`                          |
+    | `getName()`                   | `Name(obj).value()`                        |
+    | `getStringValue()`            | `String(obj).value()`                      |
+    | `getTypeCode()`               | `type_code()`                              |
+    | `getUTF8Value()`              | `String(obj).utf8_value()`                 |
+    | `hasKey(key)`                 | `contains(key)`                            |
+    | `insertItem(at, item)`        | `Array(obj).insert(at, item)`              |
+    | `isArray()`                   | `if (Array a = obj)`                       |
+    | `isDictionary()`              | `if (Dictionary d = obj)`                  |
+    | `isIndirect()`                | `indirect()`                               |
+    | `isInteger()`                 | `if (Integer n = obj)`                     |
+    | `isName()`                    | `if (Name n = obj)`                        |
+    | `isNameAndEquals(name)`       | `Name(obj) == name`                        |
+    | `isNull()`                    | `null()`                                   |
+    | `isSameObjectAs(other)`       | `obj == other`                             |
+    | `isStream()`                  | `if (Stream s = obj)`                      |
+    | `isString()`                  | `if (String s = obj)`                      |
+    | `removeKey(key)`              | `erase(key)`                               |
+    | `replaceKey(key, value)`      | `replace(key, value)`                      |
+    | `setArrayFromVector(items)`   | `Array(obj).setFromVector(items)`          |
+    | `setArrayItem(n, oh)`         | `Array(obj).set(n, oh)`                    |
+
+11. **Typed-handle control flow** - Prefer `if` initializers for typed extraction
+    (e.g., `if (Stream stream = obj)`) and direct typed iteration
+    (e.g., `for (Dictionary font: Array(...))`), unless this causes excessive nesting, or when
+    the `if` part is long and the `else` part is short, especially if `else` exits. Avoid
+    low-value typed-handle churn: don't pair generic probes with redundant recasts (for example,
+    `isDictionary()` followed by `Dictionary dict = obj` in the same block, or repeated casts of
+    the same object); extract once and reuse.
+12. **Avoid single-use temporaries** - Don't introduce a named variable solely to pass it to one
+    expression; use the value directly unless it aids readability or is reused.
+13. **Minimize refactor scope**: When implementing a focused change, avoid unrelated style or
+    structural refactors in the same edit unless explicitly requested.
+14. **Use PIMPL pattern** - Prefer private implementation classes (`Members` classes) for
+    internal use
+15. **Array semantics** - Array methods treat scalars as single-element arrays and null as empty
+    array (per PDF spec)
+16. **Map semantics** - Map methods treat null values as missing entries (per PDF spec)
+17. **Object references** - Methods often return references; avoid unnecessary copying but copy
+    if reference may become stale
+18. **Thread safety** - Object handles cannot be shared across threads
 
 ### Style
 - Column limit: 100 characters
@@ -171,19 +253,26 @@ libtests directories:
 
 ## Adding Global Options and Limits
 
-Global options and limits are qpdf-wide settings in the `qpdf::global` namespace that affect behavior across all operations. See `README-maintainer.md` section "HOW TO ADD A GLOBAL OPTION OR LIMIT" for complete details.
+Global options and limits are qpdf-wide settings in the `qpdf::global` namespace that affect
+behavior across all operations. See `README-developer.md` for complete details on implementing
+global options, limits, and state items.
 
 ### Quick Reference for Global Options
 
 Global options are boolean settings (e.g., `inspection_mode`, `preserve_invalid_attributes`):
 
-1. **Add enum**: Add `qpdf_p_option_name` to `qpdf_param_e` enum in `include/qpdf/Constants.h` (use `0x11xxx` range)
-2. **Add members**: Add `bool option_name_{false};` and optionally `bool option_name_set_{false};` to `Options` class in `libqpdf/qpdf/global_private.hh`
+1. **Add enum**: Add `qpdf_p_option_name` to `qpdf_param_e` enum in `include/qpdf/Constants.h`
+   (use `0x11xxx` range)
+2. **Add members**: Add `bool option_name_{false};` and optionally `bool option_name_set_{false};`
+   to `Options` class in `libqpdf/qpdf/global_private.hh`
 3. **Add methods**: Add static getter/setter to `Options` class in same file
-4. **Add cases**: Add cases to `qpdf_global_get_uint32()` and `qpdf_global_set_uint32()` in `libqpdf/global.cc`
-5. **Add public API**: Add inline getter/setter with Doxygen docs in `include/qpdf/global.hh` under `namespace options`
+4. **Add cases**: Add cases to `qpdf_global_get_uint32()` and `qpdf_global_set_uint32()` in
+   `libqpdf/global.cc`
+5. **Add public API**: Add inline getter/setter with Doxygen docs in `include/qpdf/global.hh`
+   under `namespace options`
 6. **Add tests**: Add tests in `libtests/objects.cc`
-7. **CLI integration** (optional): Add to `job.yml` global section, regenerate, implement in `QPDFJob_config.cc`, document in `manual/cli.rst`
+7. **CLI integration** (optional): Add to `job.yml` global section, regenerate, implement in
+   `QPDFJob_config.cc`, document in `manual/cli.rst`
 
 ### Quick Reference for Global Limits
 
@@ -198,14 +287,18 @@ Global limits are uint32_t values (e.g., `parser_max_nesting`, `parser_max_error
 
 Global state items are read-only values (e.g., `version_major`, `invalid_attribute_errors`):
 
-1. **Add enum**: Add `qpdf_p_state_item` to enum in Constants.h (use `0x10xxx` range for global state)
-2. **Add member**: Add `uint32_t state_item_{initial_value};` to `State` class in `global_private.hh`
+1. **Add enum**: Add `qpdf_p_state_item` to enum in Constants.h (use `0x10xxx` range for global
+   state)
+2. **Add member**: Add `uint32_t state_item_{initial_value};` to `State` class in
+   `global_private.hh`
 3. **Add getter**: Add `static uint32_t const& state_item()` getter in `State` class
 4. **For error counters**: Also add `static void error_type()` incrementer method
-5. **Add public API**: Add read-only getter at top level of `qpdf::global` namespace in `global.hh`
+5. **Add public API**: Add read-only getter at top level of `qpdf::global` namespace in
+   `global.hh`
 6. **Add case**: Add case to `qpdf_global_get_uint32()` in `global.cc` (read-only, no setter)
 7. **Add tests**: Add tests in `libtests/objects.cc`
-8. **For error counters**: Add warning in `QPDFJob.cc` and call `global::State::error_type()` where errors occur
+8. **For error counters**: Add warning in `QPDFJob.cc` and call `global::State::error_type()`
+   where errors occur
 
 ### Example
 
@@ -218,7 +311,8 @@ The `preserve_invalid_attributes` feature demonstrates all patterns:
 
 When reviewing pull requests and providing feedback with recommended changes:
 
-1. **Open a new pull request with your comments and recommended changes** - Do not comment on the existing PR. Create a new PR that:
+1. **Open a new pull request with your comments and recommended changes** - Do not comment on the
+   existing PR. Create a new PR that:
    - Forks from the PR branch being reviewed
    - Includes your recommended changes as commits
    - Links back to the original PR in the description
@@ -229,6 +323,9 @@ When reviewing pull requests and providing feedback with recommended changes:
    - Changes to be tested in CI before being accepted
    - A clear history of who made which changes
    - Easy cherry-picking of specific suggestions
+3. In review responses, prioritize findings by severity (behavioral regressions, API/ABI risk,
+   missing tests) before style suggestions; keep style feedback non-blocking unless it violates
+   documented rules.
 
 ## Validation Checklist
 Before submitting changes:
@@ -240,17 +337,20 @@ Before submitting changes:
 ## Troubleshooting
 
 ### Common Issues
-1. **"clang-format version >= 20 is required"**: The `format-code` script automatically tries `clang-format-20` if available. Install clang-format 20 or newer via your package manager.
+1. **"clang-format version >= 20 is required"**: The `format-code` script automatically tries
+   `clang-format-20` if available. Install clang-format 20 or newer via your package manager.
 2. **Build fails in source directory**: Always use out-of-source builds (`cmake -B build`).
-3. **Tests fail with file comparison errors**: May be due to zlib version differences. Use `qpdf-test-compare` for comparisons.
+3. **Tests fail with file comparison errors**: May be due to zlib version differences. Use
+   `qpdf-test-compare` for comparisons.
 4. **generate_auto_job errors**: Ensure Python 3 and PyYAML are installed.
 
 ### Environment Variables for Extended Tests
 - `QPDF_TEST_COMPARE_IMAGES=1`: Enable image comparison tests
 - `QPDF_LARGE_FILE_TEST_PATH=/path`: Enable large file tests (needs 11GB free)
 
 ## Trust These Instructions
-These instructions have been validated against the actual repository. Only search for additional information if:
+These instructions have been validated against the actual repository. Only search for additional
+information if:
 - Instructions appear outdated or incomplete
 - Build commands fail unexpectedly
 - Test patterns don't match current code structure
PATCH

echo "Gold patch applied."
