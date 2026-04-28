#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sundials

# Idempotency guard
if grep -qF "description: Build, install, and test SUNDIALS from source as an end user or as " ".agents/skills/building/SKILL.md" && grep -qF "description: Add a new SUNDIALS module (e.g., NVECTOR_*, SUNMATRIX_*, SUNLINSOL_" ".agents/skills/new-module/SKILL.md" && grep -qF "- `src/` and `include/`: core SUNDIALS C/C++ sources and public headers, organiz" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/building/SKILL.md b/.agents/skills/building/SKILL.md
@@ -0,0 +1,87 @@
+---
+name: building
+description: Build, install, and test SUNDIALS from source as an end user or as a SUNDIALS developer. Use when a request involves configuring CMake, selecting compilers/options (MPI, GPU backends, Fortran), building/installing, running CTest, enabling dev/unit tests, or troubleshooting common build/test issues.
+---
+
+# Build SUNDIALS (user then developer)
+
+Prefer out-of-source CMake builds. Never build in the source tree.
+
+If you need full option details or platform-specific notes, open `doc/shared/sundials/Install.rst` (search for “Configuration options”, “Build Type”, “Compilers”, and “Example Programs”).
+
+For CI-like, multi-config testing use `test/test_driver.sh` (supports `--testtype pr|release|branch` and `--buildjobs/--testjobs`).
+
+Python bindings (sundials4py) are driven by `pyproject.toml` and `scikit-build-core`:
+`python -m pip install -e ".[dev]"` then `pytest`.
+
+## User build (install + consume)
+
+1) Configure (choose an install prefix):
+
+```bash
+cmake -S . -B build \
+  -DCMAKE_BUILD_TYPE=Release \
+  -DCMAKE_INSTALL_PREFIX="$PWD/install"
+```
+
+2) Build and install:
+
+```bash
+cmake --build build -j
+cmake --install build
+```
+
+3) Use SUNDIALS from another CMake project:
+
+- Set `SUNDIALS_DIR` to the SUNDIALS install tree (or to the installed CMake package dir) and use `find_package(SUNDIALS REQUIRED)`; link with exported targets like `SUNDIALS::cvode`. If you link via CMake targets, the required `libsundials_core` dependency is handled automatically.
+
+### Common user options
+
+- **Examples**: examples are usually enabled by default for C; enable others as needed:
+  - `-DSUNDIALS_ENABLE_C_EXAMPLES=ON`
+  - `-DSUNDIALS_ENABLE_CXX_EXAMPLES=ON`
+  - `-DSUNDIALS_ENABLE_FORTRAN_EXAMPLES=ON` (requires Fortran)
+  - `-DSUNDIALS_ENABLE_CUDA_EXAMPLES=ON` (requires CUDA enabled)
+  - If working with older option names, note that `EXAMPLES_ENABLE_C`/`EXAMPLES_ENABLE_CXX`/etc. are deprecated in favor of the `SUNDIALS_ENABLE_*_EXAMPLES` options.
+- **MPI**: `-DSUNDIALS_ENABLE_MPI=ON`
+- **Fortran interfaces**: `-DSUNDIALS_ENABLE_FORTRAN=ON`
+- **Build type**: `Debug` (slow, checks), `Release` (fast), `RelWithDebInfo` (good default)
+
+## Developer build (iterate + test)
+
+Use a separate build directory per configuration (e.g., `build-debug`, `build-gcc`, `build-mpi`).
+
+### Configure for development
+
+```bash
+cmake -S . -B build-dev \
+  -DCMAKE_BUILD_TYPE=Debug \
+  -DBUILD_TESTING=ON \
+  -DSUNDIALS_TEST_ENABLE_DEV_TESTS=ON \
+  -DSUNDIALS_TEST_ENABLE_UNIT_TESTS=ON
+```
+
+Optional tightening (CI-like):
+
+- Warnings: `-DSUNDIALS_ENABLE_ALL_WARNINGS=ON`
+- Warnings as errors: `-DCMAKE_COMPILE_WARNING_AS_ERROR=ON`
+- Sanitizers (compiler support required): `-DSUNDIALS_ENABLE_ADDRESS_SANITIZER=ON` (and/or leak/undefined/thread variants)
+
+### Build and run tests
+
+```bash
+cmake --build build-dev -j
+ctest --test-dir build-dev --output-on-failure
+```
+
+Notes:
+
+- If tests that compare against “answer files” fail due to platform differences, consider rerunning with a locally-generated answer directory using `SUNDIALS_TEST_ANSWER_DIR` (see `doc/superbuild/source/developers/testing/CTest.rst`).
+- To focus on a subset, use CTest filters (e.g., `ctest --test-dir build-dev -R <regex>`).
+
+## Troubleshooting checklist
+
+- **CMake refuses in-source build**: delete any accidental `CMakeCache.txt` in the source tree; configure with `-B <builddir>`.
+- **Changed options not taking effect**: start from a fresh build directory or clear cache (`rm -rf build-dev`).
+- **Wrong compiler/MPI wrapper**: set `CC`, `CXX`, `FC` env vars before configuring, or pass `-DCMAKE_<LANG>_COMPILER=...`.
+- **Link errors after enabling a backend/TPL**: confirm that the corresponding `SUNDIALS_ENABLE_*` option is ON and that required dependencies are discoverable (use `CMAKE_PREFIX_PATH`).
diff --git a/.agents/skills/new-module/SKILL.md b/.agents/skills/new-module/SKILL.md
@@ -0,0 +1,155 @@
+---
+name: new-module
+description: Add a new SUNDIALS module (e.g., NVECTOR_*, SUNMATRIX_*, SUNLINSOL_*, SUNNONLINSOL_*, SUNMEMORY_*, or a new shared component) including source/header layout, CMake wiring, enable/disable options, exported CMake targets, installed component registration, and developer tests/examples/docs updates.
+---
+
+# Create a new SUNDIALS module
+
+Follow existing module patterns; copy the closest neighbor (same category + similar dependencies) and adapt minimally.
+
+Open these files as references when needed:
+
+- `src/<category>/CMakeLists.txt` (how modules are conditionally added)
+- `cmake/SundialsBuildOptionsPost.cmake` (module enable options + `SUNDIALS_BUILD_LIST`)
+- `cmake/macros/SundialsAddLibrary.cmake` (how `sundials_add_library` installs headers and registers components)
+- `doc/shared/sundials/Install.rst` (user-visible options / CMake targets)
+- `test/unit_tests/<category>/` (how unit tests are wired)
+
+## 1) Decide what “module” means
+
+Pick one of these patterns; it determines naming, options, and wiring:
+
+- **Native always-built module** (e.g., `SUNMATRIX_BAND`, `SUNLINSOL_SPGMR`): always enabled; no user option.
+- **Optional module gated by a TPL/backend** (e.g., CUDA/HIP/Kokkos/Ginkgo): add `SUNDIALS_ENABLE_<CATEGORY>_<NAME>` option with `DEPENDS_ON ...`.
+- **Header-only / interface-only module** (rare): uses an `INTERFACE` library; you must manually register it as an installed component.
+- **Internal-only helper**: can be `OBJECT_LIB_ONLY` (no installed component/target intended for end users).
+
+If the module is user-visible, prefer “optional module” (with a CMake option) over ad-hoc logic.
+
+## 2) Choose names (directory, library, headers, CMake target)
+
+Keep names consistent with existing modules in the same category:
+
+- **Source dir**: `src/<category>/<name>/` (e.g., `src/sunlinsol/spgmr/`)
+- **Public header(s)**: `include/<category>/<category>_<name>.<h|hpp>` (e.g., `include/sunlinsol/sunlinsol_spgmr.h`)
+- **CMake/Library target**: `sundials_<category><name>` (e.g., `sundials_sunlinsolspgmr`)
+- **Exported target for consumers**: `SUNDIALS::<category><name>` (auto-created by `sundials_add_library`)
+- **Enable option** (if optional): `SUNDIALS_ENABLE_<CATEGORY>_<NAME>` (e.g., `SUNDIALS_ENABLE_SUNMATRIX_CUSPARSE`)
+
+Use existing capitalization conventions:
+
+- options use `SUNDIALS_ENABLE_<...>` with category in uppercase (NVECTOR/SUNMATRIX/SUNLINSOL/…)
+- messages often say `Added <CATEGORY>_<NAME> module`
+
+## 3) Add sources + headers
+
+Create:
+
+- `src/<category>/<name>/<implementation>.c` (and/or `.cpp` if needed)
+- `include/<category>/<category>_<name>.h` (public API; installable)
+- `src/<category>/<name>/CMakeLists.txt` (module build rules)
+
+Avoid installing “private” headers. If a header is only for the module implementation, keep it under `src/<category>/<name>/` and do not list it in `HEADERS`.
+
+## 4) Add the module CMakeLists.txt
+
+For standard compiled modules, use `sundials_add_library` (preferred):
+
+- `SOURCES ...`
+- `HEADERS ${SUNDIALS_SOURCE_DIR}/include/<category>/<category>_<name>.h`
+- `INCLUDE_SUBDIR <category>`
+- `LINK_LIBRARIES PUBLIC sundials_core` (+ any TPL targets)
+- `OUTPUT_NAME sundials_<category><name>`
+- `VERSION`/`SOVERSION` using the category’s variables (see neighboring modules)
+
+Reference examples:
+
+- `src/nvector/serial/CMakeLists.txt`
+- `src/sunmatrix/band/CMakeLists.txt`
+- `src/sunlinsol/spgmr/CMakeLists.txt`
+
+Notes:
+
+- `sundials_add_library` automatically:
+  - installs the listed headers to `${CMAKE_INSTALL_INCLUDEDIR}/<category>`
+  - registers the module as an installed component for `SUNDIALSConfig.cmake`
+  - creates the `SUNDIALS::<...>` alias for build-tree usage
+- If you add Fortran 2003 wrappers like other modules do, gate them under `if(SUNDIALS_ENABLE_FORTRAN)` and mirror the existing `fmod_int${SUNDIALS_INDEX_SIZE}` pattern.
+
+## 5) Wire the module into the build (add_subdirectory)
+
+Edit `src/<category>/CMakeLists.txt` to include your module:
+
+- Always-built: `add_subdirectory(<name>)`
+- Optional: wrap with `if(SUNDIALS_ENABLE_<CATEGORY>_<NAME>) ... endif()`
+
+For categories that are listed in `src/CMakeLists.txt` (e.g., `nvector`, `sunmatrix`, `sunlinsol`, …), you usually only need to change the category-level `CMakeLists.txt`.
+
+## 6) Add/adjust the enable option and build-list registration
+
+If the module is optional and should appear in `sundials_config.h` (and in build summaries), add an option in `cmake/SundialsBuildOptionsPost.cmake`:
+
+- Add `sundials_option(SUNDIALS_ENABLE_<CATEGORY>_<NAME> BOOL "... module ..." <default> DEPENDS_ON ...)`
+- Append to build list: `list(APPEND SUNDIALS_BUILD_LIST "SUNDIALS_ENABLE_<CATEGORY>_<NAME>")`
+
+Pick appropriate dependencies:
+
+- CUDA modules: `DEPENDS_ON SUNDIALS_ENABLE_CUDA` (and sometimes `CMAKE_CUDA_COMPILER`)
+- MPI modules: `DEPENDS_ON SUNDIALS_ENABLE_MPI`
+- TPL modules: depend on the corresponding `SUNDIALS_ENABLE_<TPL>` option
+
+If the module is required and must not be disabled, follow the pattern:
+
+```cmake
+set(SUNDIALS_ENABLE_<CATEGORY>_<NAME> TRUE)
+list(APPEND SUNDIALS_BUILD_LIST "SUNDIALS_ENABLE_<CATEGORY>_<NAME>")
+```
+
+## 7) Handle “installed components” for INTERFACE-only modules
+
+If you implement a module as an `INTERFACE` library (no `sundials_add_library`), you must manually add it to `_SUNDIALS_INSTALLED_COMPONENTS` so that `find_package(SUNDIALS COMPONENTS ...)` can work.
+
+Reference patterns:
+
+- `src/sunmatrix/CMakeLists.txt` (Ginkgo/KokkosDense interface modules)
+- `src/sunlinsol/CMakeLists.txt` (Ginkgo/KokkosDense interface modules)
+
+## 8) Tests, examples, and docs (when user-visible)
+
+Do the smallest set that proves correctness and prevents regressions:
+
+- **Unit tests**: add under `test/unit_tests/<category>/...` and gate by your enable option if optional.
+- **Examples**: add under `examples/<package>/<lang>_<backend>/...` only if it materially helps users.
+- **Docs**:
+  - If users must know about a new option/target, update `doc/shared/sundials/Install.rst`.
+  - If it’s a user-visible feature, also update `doc/shared/RecentChanges.rst` and/or `CHANGELOG.md` per repo conventions.
+
+## 9) Local validation commands
+
+Configure/build (pick options that enable your module), then run focused tests first:
+
+```bash
+cmake -S . -B build-dev -DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTING=ON
+cmake --build build-dev -j
+ctest --test-dir build-dev --output-on-failure -R <your-module-regex>
+```
+
+If you added a new enable option, confirm it shows up in `build-dev/include/sundials/sundials_config.h`.
+
+## 10) Language bindings
+
+Only add language bindings when they are applicable:
+
+- The module is user-visible (i.e., part of the public API users are expected to call), and
+- The module’s category already has existing Fortran and/or Python bindings.
+
+If Fortran bindings are applicable:
+
+- Add the SWIG interface file in `swig/` and add it to `swig/Makefile` appropriately.
+- Generate the Fortran interface code and commit the generated sources.
+
+If Python bindings are applicable:
+
+- Add the module as a neighbor to the other modules of the same type in `bindings/sundials4py`.
+- Add it to the `generate.yaml` with the appropriate neighbors.
+- Generate the Python binding code to commit, and always format it first.
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,39 @@
+# Repository Guidelines
+
+## Project Structure
+
+- `src/` and `include/`: core SUNDIALS C/C++ sources and public headers, organized by package (e.g., `cvode/`, `ida/`) or module (e.g., `nvector/`, `sunlinsol/`).
+- `examples/`: buildable examples (C, C++, CUDA, etc.) wired into CMake.
+- `test/`: test infrastructure, answer files, and `test/unit_tests/` (optionally includes GoogleTest-based tests).
+- `cmake/`: CMake modules and option definitions (e.g., example/test toggles).
+- `bindings/` and `swig/`: language bindings (notably `bindings/sundials4py`).
+- `doc/`: user/developer documentation sources.
+
+## Build, Test, and Development Commands
+
+Refer to [`.agents/skills/building/SKILL.md`](.agents/skills/building/SKILL.md).
+
+## Coding Style & Naming
+
+- C/C++: follow `.clang-format` (2-space indent); format before pushing.
+- CMake: keep listfile style consistent with `.cmake-format.py`.
+- Fortran: formatted via `fprettify --indent 2`.
+- Python: formatted with Black (configured in `pyproject.toml`).
+
+Formatting helpers:
+`./scripts/format.sh src include cmake test bindings`
+`./scripts/spelling.sh` (uses `codespell` and may edit files).
+
+## Testing Guidelines
+
+- Primary harness: CTest (`ctest --test-dir build`).
+- Unit tests: enable with `-DSUNDIALS_TEST_ENABLE_UNIT_TESTS=ON` (and optionally `-DSUNDIALS_TEST_ENABLE_GTEST=ON`).
+- Keep new features paired with targeted tests; update answer files under `test/answers/` only when output changes are intended.
+
+## Commits & Pull Requests
+
+- Target the `develop` branch.
+- Use clear, scoped subjects; common patterns in history include `CMake: ...`, `CI: ...`, `Docs: ...`, `Tools: ...`.
+- All commits must include a DCO sign-off: use `git commit -s`.
+- PRs should include: what/why, how it was tested, and updates to `CHANGELOG.md` and `doc/shared/RecentChanges.rst` when user-visible.
+
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
