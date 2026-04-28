#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mfc

# Idempotency guard
if grep -qF "- Tests are generated **programmatically** in `toolchain/mfc/test/cases.py`, not" ".claude/rules/common-pitfalls.md" && grep -qF "- `dsqrt`, `dexp`, `dlog`, `dble`, `dabs`, `dcos`, `dsin`, `dtan`, etc. \u2192 use ge" ".claude/rules/fortran-conventions.md" && grep -qF "- `@:ACC_SETUP_VFs(...)` / `@:ACC_SETUP_SFs(...)` \u2014 GPU pointer setup for vector" ".claude/rules/gpu-and-mpi.md" && grep -qF "MFC has ~3,400 simulation parameters defined in Python and read by Fortran via n" ".claude/rules/parameter-system.md" && grep -qF "* Only `simulation` (plus its `common` dependencies) is GPU-accelerated via **Op" ".github/copilot-instructions.md" && grep -qF "./mfc.sh build -j 8                        # Build all 3 targets (pre_process, s" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/rules/common-pitfalls.md b/.claude/rules/common-pitfalls.md
@@ -0,0 +1,63 @@
+# Common Pitfalls
+
+## Array Bounds & Ghost Cells
+- Grid dimensions: `m`, `n`, `p` (cells in x, y, z). 1D: n=p=0. 2D: p=0.
+- Interior domain: `0:m`, `0:n`, `0:p`
+- Buffer/ghost region: `-buff_size:m+buff_size` (similar for n, p in multi-D)
+- `buff_size` depends on WENO order and features (typically `2*weno_polyn + 2`)
+- Domain bounds: `idwint(1:3)` (interior `0:m`), `idwbuff(1:3)` (with ghost cells)
+- Cell-center coords: `x_cc(-buff_size:m+buff_size)`, `y_cc(...)`, `z_cc(...)`
+- Cell-boundary coords: `x_cb(-1-buff_size:m+buff_size)`
+- Riemann solver indexing: left state at `j`, right state at `j+1`
+- Off-by-one errors in ghost cell regions are a common source of bugs
+
+## Field Variable Indexing
+- Conserved variables: `q_cons_vf(1:sys_size)`. Primitive: `q_prim_vf(1:sys_size)`.
+- Index ranges depend on `model_eqns` and enabled features (set in `m_global_parameters.fpp`):
+  - `cont_idx` — continuity (partial densities, one per fluid)
+  - `mom_idx` — momentum components
+  - `E_idx` — total energy (scalar)
+  - `adv_idx` — volume fractions (advection equations)
+  - `bub_idx`, `stress_idx`, `xi_idx`, `species_idx`, `B_idx`, `c_idx` — optional
+- Shorthand scalars: `momxb`/`momxe`, `contxb`/`contxe`, `advxb`/`advxe`, etc.
+- `sys_size` = total number of conserved variables (computed at startup)
+- Changing `model_eqns` or enabling features changes ALL index positions
+
+## Blast Radius
+- `src/common/` is shared by ALL three executables (pre_process, simulation, post_process)
+- Any change to common/ requires testing all three targets
+- Public subroutine signature changes affect all callers across all targets
+- Parameter default changes affect all existing case files
+
+## Physics Consistency
+- Pressure formula MUST match `model_eqns` setting
+- Model-specific conservative ↔ primitive conversion paths exist
+- Volume fractions must sum to 1.0
+- Boundary condition symmetry requirements must be maintained
+
+## Compiler-Specific Issues
+- Code must compile on gfortran, nvfortran, Cray ftn, and Intel ifx
+- Each compiler has different strictness levels and warning behavior
+- Fypp macros must expand correctly for both GPU and CPU builds
+- GPU builds only work with nvfortran, Cray ftn, and AMD flang
+
+## Test System
+- Tests are generated **programmatically** in `toolchain/mfc/test/cases.py`, not standalone files
+- Each test is a parameter modification on top of `BASE_CFG` defaults
+- Test UUID = CRC32 hash of the test's trace string; `./mfc.sh test -l` lists all
+- To add a test: modify `cases.py` using `CaseGeneratorStack` push/pop pattern
+- Golden files: `tests/<UUID>/golden.txt` — tolerance-based comparison, not exact match
+- If your change intentionally modifies output, regenerate golden files:
+  `./mfc.sh test --generate --only <affected_tests> -j 8`
+- Do not regenerate ALL golden files unless you understand every output change
+
+## PR Checklist
+Before submitting a PR:
+- [ ] `./mfc.sh format -j 8` (auto-format)
+- [ ] `./mfc.sh precheck -j 8` (5 CI lint checks)
+- [ ] `./mfc.sh build -j 8` (compiles)
+- [ ] `./mfc.sh test --only <relevant> -j 8` (tests pass)
+- [ ] If adding parameters: all 4 locations updated
+- [ ] If modifying `src/common/`: all three targets tested
+- [ ] If changing output: golden files regenerated for affected tests
+- [ ] One logical change per commit
diff --git a/.claude/rules/fortran-conventions.md b/.claude/rules/fortran-conventions.md
@@ -0,0 +1,63 @@
+# Fortran Conventions
+
+## File Format
+- Source files use `.fpp` extension (Fortran + Fypp preprocessor macros)
+- Fypp preprocesses `.fpp` → `.f90` at build time via CMake
+- Fypp supports conditional compilation, code generation, and regex macros
+
+## Module Structure
+Every Fortran module follows this pattern:
+- File: `m_<feature>.fpp`
+- Module: `module m_<feature>`
+- `implicit none` required
+- Explicit `intent(in)`, `intent(out)`, or `intent(inout)` on ALL subroutine/function arguments
+- Initialization subroutine: `s_initialize_<feature>_module`
+- Finalization subroutine: `s_finalize_<feature>_module`
+
+## Naming
+- Modules: `m_<feature>`
+- Public subroutines: `s_<verb>_<noun>`
+- Public functions: `f_<verb>_<noun>`
+- Private/local variables: no prefix required
+- Constants: descriptive names, not ALL_CAPS
+
+## Forbidden Patterns
+
+Caught by `./mfc.sh precheck` (source lint step 4/5):
+- `dsqrt`, `dexp`, `dlog`, `dble`, `dabs`, `dcos`, `dsin`, `dtan`, etc. → use generic intrinsics
+- `1.0d0`, `2.5d-3` (Fortran `d` exponent literals) → use `1.0_wp`, `2.5e-3_wp`
+- `double precision` → use `real(wp)` or `real(stp)`
+- `real(8)`, `real(4)` → use `wp` or `stp` kind parameters
+- Raw `!$acc` or `!$omp` directives → use Fypp GPU_* macros from `parallel_macros.fpp`
+- Full list of forbidden patterns: `toolchain/bootstrap/precheck.sh`
+
+Enforced by convention/code review (not automated):
+- `goto`, `COMMON` blocks, global `save` variables
+- `stop`, `error stop` → use `call s_mpi_abort()` or `@:PROHIBIT()`/`@:ASSERT()`
+
+## Error Checking Macros (from macros.fpp)
+- `@:PROHIBIT(condition, message)` — Runtime constraint check; aborts with file/line info
+- `@:ASSERT(predicate, message)` — Invariant assertion; aborts if predicate is false
+- `@:LOG(expr)` — Debug logging, active only in `MFC_DEBUG` builds
+- Fortran-side runtime validation also exists in `m_checker*.fpp` files using `@:PROHIBIT`
+
+## Precision Types
+- `wp` (working precision): used for computation. Double by default.
+- `stp` (storage precision): used for field data arrays and I/O. Double by default.
+- In single-precision mode (`--single`): both become single.
+- In mixed-precision mode (`--mixed`): wp=double, stp=half.
+- MPI type matching: `mpi_p` must match `wp`, `mpi_io_p` must match `stp`.
+- Always use generic intrinsics: `sqrt` not `dsqrt`, `abs` not `dabs`.
+- Cast with `real(..., wp)` or `real(..., stp)`, never `dble(...)`.
+
+Key derived types (`m_derived_types.fpp`):
+- `scalar_field` — `real(stp), pointer :: sf(:,:,:)`. Uses `stp`, NOT `wp`.
+- `vector_field` — allocatable array of `scalar_field` components.
+- New field arrays MUST use `stp` for storage precision consistency.
+
+## Size Guidelines (soft)
+- Subroutine: ≤500 lines
+- Helper routine: ≤150 lines
+- Function: ≤100 lines
+- File: ≤1000 lines
+- Arguments: ≤6 preferred
diff --git a/.claude/rules/gpu-and-mpi.md b/.claude/rules/gpu-and-mpi.md
@@ -0,0 +1,124 @@
+# GPU and MPI Patterns
+
+## GPU Offloading Architecture
+
+Only `src/simulation/` is GPU-accelerated. Pre/post_process run on CPU only.
+
+MFC uses a **backend-agnostic GPU abstraction** via Fypp macros. The same source code
+compiles to either OpenACC or OpenMP target offload depending on the build flag:
+
+- `./mfc.sh build --gpu acc` → OpenACC backend (NVIDIA nvfortran, Cray ftn)
+- `./mfc.sh build --gpu mp`  → OpenMP target offload backend (Cray ftn, AMD flang)
+- `./mfc.sh build` (no --gpu) → CPU-only, GPU macros expand to plain Fortran
+
+### Macro Layers (in src/common/include/)
+- `parallel_macros.fpp` — **Use these.** Generic `GPU_*` macros that dispatch to the
+  correct backend based on `MFC_OpenACC` / `MFC_OpenMP` compile definitions.
+- `acc_macros.fpp` — OpenACC-specific `ACC_*` implementations (do not call directly)
+- `omp_macros.fpp` — OpenMP target offload `OMP_*` implementations (do not call directly)
+  - OMP macros generate **compiler-specific** directives: NVIDIA uses `target teams loop`,
+    Cray uses `target teams distribute parallel do simd`, AMD uses
+    `target teams distribute parallel do`
+- `shared_parallel_macros.fpp` — Shared helpers (collapse, private, reduction generators)
+
+### Key GPU Macros (always use the `GPU_*` prefix)
+
+Inline macros (use `$:` prefix):
+- `$:GPU_PARALLEL_LOOP(collapse=N, private=[...], reduction=[...], reductionOp='+')` —
+  Parallel loop over GPU threads. Most common GPU macro.
+- `$:END_GPU_PARALLEL_LOOP()` — Required closing for GPU_PARALLEL_LOOP.
+- `$:GPU_LOOP(collapse=N, ...)` — Inner loop within a GPU parallel region.
+- `$:GPU_ENTER_DATA(create=[...])` — Allocate device memory (unscoped).
+- `$:GPU_EXIT_DATA(delete=[...])` — Free device memory.
+- `$:GPU_UPDATE(host=[...])` — Copy device → host (before MPI send).
+- `$:GPU_UPDATE(device=[...])` — Copy host → device (after MPI receive).
+- `$:GPU_ROUTINE(parallelism='[seq]')` — Mark routine for device compilation.
+- `$:GPU_DECLARE(create=[...])` — Declare device-resident data.
+- `$:GPU_ATOMIC(atomic='update')` — Atomic operation on device.
+- `$:GPU_WAIT()` — Synchronization barrier.
+
+Block macros (use `#:call`/`#:endcall`):
+- `GPU_PARALLEL(...)` — GPU parallel region wrapping a code block.
+- `GPU_DATA(copy=..., create=..., ...)` — Scoped data region.
+- `GPU_HOST_DATA(use_device_addr=[...])` — Host code with device pointers.
+
+Block macro usage:
+```
+#:call GPU_PARALLEL(copyin='[var1]', copyout='[var2]')
+  $:GPU_LOOP(collapse=N)
+  do k = 0, n; do j = 0, m
+    ! loop body
+  end do; end do
+#:endcall GPU_PARALLEL
+```
+
+NEVER write raw `!$acc` or `!$omp` directives. Always use `GPU_*` Fypp macros.
+The precheck source lint will catch raw directives and fail.
+
+### Memory Management Macros (from macros.fpp)
+- `@:ALLOCATE(var1, var2, ...)` — Fortran allocate + `GPU_ENTER_DATA(create=...)`
+- `@:DEALLOCATE(var1, var2, ...)` — `GPU_EXIT_DATA(delete=...)` + Fortran deallocate
+- `@:PREFER_GPU(var1, var2, ...)` — NVIDIA unified memory page placement hint
+- Every `@:ALLOCATE` MUST have a matching `@:DEALLOCATE` in finalization
+- Conditional allocation MUST have conditional deallocation
+
+### GPU Field Setup (Cray-specific, from macros.fpp)
+- `@:ACC_SETUP_VFs(...)` / `@:ACC_SETUP_SFs(...)` — GPU pointer setup for vector/scalar fields
+- These compile only for Cray (`_CRAYFTN`); other compilers skip them
+
+### Compiler-Backend Matrix
+| Compiler        | `--gpu acc` (OpenACC) | `--gpu mp` (OpenMP) | CPU-only |
+|-----------------|----------------------|---------------------|----------|
+| GNU gfortran    | No                   | No                  | Yes      |
+| NVIDIA nvfortran| Yes (primary)        | Yes                 | Yes      |
+| Cray ftn (CCE)  | Yes                  | Yes (primary)       | Yes      |
+| Intel ifx       | No                   | No                  | Yes      |
+| AMD flang       | No                   | Yes                 | Yes      |
+
+## Preprocessor Defines (`#ifdef` / `#ifndef`)
+
+Raw `#ifdef` / `#ifndef` preprocessor guards are **normal and expected** in MFC.
+They are NOT the same as raw `!$acc`/`!$omp` pragmas (which are forbidden).
+
+Use `#ifdef` for feature, target, compiler, and library gating:
+
+### Feature gating
+- `MFC_MPI` — MPI-enabled build (`--mpi` flag, default ON)
+- `MFC_OpenACC` — OpenACC GPU backend (`--gpu acc`)
+- `MFC_OpenMP` — OpenMP target offload backend (`--gpu mp`)
+- `MFC_GPU` — Any GPU build (either OpenACC or OpenMP)
+- `MFC_DEBUG` — Debug build (`--debug`)
+- `MFC_SINGLE_PRECISION` — Single-precision mode (`--single`)
+- `MFC_MIXED_PRECISION` — Mixed-precision mode (`--mixed`)
+
+### Target gating (for code in `src/common/` shared across executables)
+- `MFC_PRE_PROCESS` — Only in pre_process builds
+- `MFC_SIMULATION` — Only in simulation builds
+- `MFC_POST_PROCESS` — Only in post_process builds
+
+### Compiler gating (for compiler-specific workarounds)
+- `_CRAYFTN` — Cray Fortran compiler
+- `__NVCOMPILER_GPU_UNIFIED_MEM` — NVIDIA unified memory (GH-200 / `--unified`)
+- `__PGI` — Legacy PGI/NVIDIA compiler
+- `__INTEL_COMPILER` — Intel compiler
+- `FRONTIER_UNIFIED` — Frontier HPC unified memory
+
+### Library-specific code
+- FFTW (`m_fftw.fpp`) uses heavy `#ifdef` gating for `MFC_GPU` and `__PGI`
+- CUDA Fortran (`cudafor` module) is gated behind `__NVCOMPILER_GPU_UNIFIED_MEM`
+- SILO/HDF5 interfaces may have conditional paths
+
+When adding new `#ifdef` blocks, always provide an `#else` or `#endif` path so
+the code compiles in all configurations (CPU-only, GPU-ACC, GPU-OMP, with/without MPI).
+
+## MPI
+
+### Halo Exchange
+- Pack/unpack offset calculations are error-prone — verify carefully
+- Buffer sizing depends on dimensionality and QBMM state
+- GPU coherence: always `GPU_UPDATE(host=...)` before MPI send,
+  `GPU_UPDATE(device=...)` after MPI receive
+
+### Error Handling
+- Use `call s_mpi_abort()` for fatal errors, never `stop` or `error stop`
+- MPI must be finalized before program exit
diff --git a/.claude/rules/parameter-system.md b/.claude/rules/parameter-system.md
@@ -0,0 +1,66 @@
+# Parameter System
+
+## Overview
+MFC has ~3,400 simulation parameters defined in Python and read by Fortran via namelist files.
+
+## Parameter Flow: Python → Fortran
+
+1. **Definition**: `toolchain/mfc/params/definitions.py` — source of truth
+   - Parameters are indexed families: `patch_icpp(i)%attr`, `fluid_pp(i)%attr`, etc.
+   - Each has type, default, constraints, and tags
+
+2. **Validation** (two layers):
+   - `toolchain/mfc/case.py` / `toolchain/mfc/params/registry.py` — JSON schema validation
+     via fastjsonschema (type checking, defaults)
+   - `toolchain/mfc/case_validator.py` — Physics constraint checking
+     (e.g., volume fractions sum to 1, dependency validation)
+
+3. **Input Generation**: `toolchain/mfc/run/input.py`
+   - Python case dict → Fortran namelist `.inp` file
+   - Format: `&user_inputs` ... `&end/`
+
+4. **Fortran Reading**: `src/*/m_start_up.fpp`
+   - Reads `&user_inputs` namelist
+   - Each parameter must be declared in the namelist statement
+
+## Adding a New Parameter (4-location checklist)
+
+YOU MUST update the first 3 locations. Missing any causes silent failures or compile errors.
+Location 4 is required only if the parameter has physics constraints.
+
+1. **`toolchain/mfc/params/definitions.py`**: Add parameter with type, default, constraints
+2. **`src/*/m_global_parameters.fpp`**: Declare the Fortran variable in the relevant
+   target(s). If the param is used by simulation only, add it there. If shared, add to
+   all three targets' m_global_parameters.fpp.
+3. **`src/*/m_start_up.fpp`**: Add to the Fortran `namelist` declaration in the relevant
+   target(s).
+4. **`toolchain/mfc/case_validator.py`**: Add validation rules if the parameter has
+   physics constraints. Include `PHYSICS_DOCS` entry with title, category, explanation.
+
+## Case Files
+- Case files are Python scripts (`.py`) that define a dict of parameters
+- Validated with `./mfc.sh validate case.py`
+- Examples in `examples/` directory
+- Create new cases with `./mfc.sh new <name>`
+- Search parameters with `./mfc.sh params <query>`
+
+## Fortran-Side Runtime Validation
+Each target has `m_checker*.fpp` files (e.g., `src/simulation/m_checker.fpp`,
+`src/common/m_checker_common.fpp`) containing runtime parameter validation using
+`@:PROHIBIT(condition, message)`. When adding parameters with physics constraints,
+add Fortran-side checks here in addition to `case_validator.py`.
+
+## Analytical Initial Conditions
+String expressions in parameters become Fortran code via `case.py.__get_analytic_ic_fpp()`.
+These are compiled into the binary, so syntax errors cause build failures, not runtime errors.
+
+Available variables in analytical IC expressions:
+- `x`, `y`, `z` — cell-center coordinates (mapped to `x_cc(i)`, `y_cc(j)`, `z_cc(k)`)
+- `xc`, `yc`, `zc` — patch centroid coordinates
+- `lx`, `ly`, `lz` — patch lengths
+- `r` — patch radius; `eps`, `beta` — vortex parameters
+- `e` — Euler's number (2.71828...)
+- Standard Fortran math intrinsics available: `sin`, `cos`, `exp`, `sqrt`, `abs`, etc.
+- For moving immersed boundaries: `t` (simulation time) is also available
+
+Example: `'patch_icpp(1)%vel(2)': '(x - xc) * exp(-((x-xc)**2 + (y-yc)**2))'`
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -16,7 +16,7 @@ Formatting and linting are enforced by pre-commit hooks. Focus review effort on
   * Sources in `src/`, tests in `tests/`, examples in `examples/`, Python toolchain in `toolchain/`.
   * Most source files are `.fpp` (Fypp templates); CMake transpiles them to `.f90`.
 * **Fypp macros** are in `src/<subprogram>/include/`, where `<subprogram>` is `simulation`, `common`, `pre_process`, or `post_process`.
-* Only `simulation` (plus its `common` dependencies) is GPU-accelerated via **OpenACC**.
+* Only `simulation` (plus its `common` dependencies) is GPU-accelerated via **OpenACC** or **OpenMP target offload** (`--gpu acc` or `--gpu mp`). GPU code uses backend-agnostic `GPU_*` Fypp macros (in `src/common/include/parallel_macros.fpp`) that dispatch to the correct backend at compile time.
 * Code must compile with **GNU gfortran**, **NVIDIA nvfortran**, **Cray ftn**, and **Intel ifx**.
 * Precision modes: double (default), single, and mixed (`wp` = working precision, `stp` = storage precision).
 * **Python toolchain** requires **Python 3.10+** — do not suggest `from __future__` imports or other backwards-compatibility shims.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,170 @@
+# MFC — Multi-component Flow Code
+
+MFC is an exascale multi-physics CFD solver written in modern Fortran 2008+ with Fypp
+preprocessing. It has three executables (pre_process, simulation, post_process), a Python
+toolchain for building/running/testing, and supports GPU acceleration via OpenACC and
+OpenMP target offload. It must compile with gfortran, nvfortran, Cray ftn, and Intel ifx.
+
+## Commands
+
+Prefer using `./mfc.sh` as the entry point for building, running, testing, formatting,
+and linting. It handles virtual environments, module loading, dependency bootstrapping,
+and build configuration. Avoid invoking CMake, Python toolchain scripts, or Fortran
+compilers directly unless you have a specific reason.
+
+All commands run from the repo root via `./mfc.sh`.
+
+```bash
+# Building
+./mfc.sh build -j 8                        # Build all 3 targets (pre_process, simulation, post_process)
+./mfc.sh build -t simulation -j 8          # Build only simulation
+./mfc.sh build --gpu acc -j 8              # Build with OpenACC GPU support
+./mfc.sh build --gpu mp -j 8              # Build with OpenMP target offload GPU support
+./mfc.sh build --debug -j 8                # Debug build
+./mfc.sh build -i case.py --case-optimization -j 8  # Case-optimized build (10x speedup)
+
+# Running
+./mfc.sh run case.py -n 4                  # Run case with 4 MPI ranks
+./mfc.sh run case.py --no-build            # Run without rebuilding
+./mfc.sh run case.py -e batch -N 2 -n 4 -c phoenix -a ACCOUNT  # Batch submit on Phoenix
+
+# Testing
+./mfc.sh test -j 8                         # Run full test suite (560+ tests)
+./mfc.sh test --only 1D -j 8              # Only 1D tests
+./mfc.sh test --only 2D Bubbles -j 8      # Only 2D bubble tests
+./mfc.sh test --only <UUID> -j 8          # Run one specific test by UUID
+./mfc.sh test -l                           # List all tests with UUIDs and traces
+./mfc.sh test -% 10 -j 8                  # Run 10% random sample
+./mfc.sh test --generate --only <feature>  # Regenerate golden files after intentional output change
+
+# Verification (pre-commit CI checks)
+./mfc.sh precheck -j 8                     # Run all 5 lint checks (same as CI gate)
+./mfc.sh format -j 8                       # Auto-format Fortran (.fpp/.f90) + Python
+./mfc.sh lint                              # Pylint + Python unit tests
+./mfc.sh spelling                          # Spell check
+
+# Module loading (HPC clusters only — must use `source`)
+source ./mfc.sh load -c p -m g             # Load Phoenix GPU modules
+source ./mfc.sh load -c f -m g             # Load Frontier GPU modules
+source ./mfc.sh load -c p -m c             # Load Phoenix CPU modules
+
+# Other
+./mfc.sh validate case.py                  # Validate case file without running
+./mfc.sh params <query>                    # Search ~3,400 case parameters
+./mfc.sh clean                             # Remove build artifacts
+./mfc.sh new <name>                        # Create new case from template
+```
+
+## System Identification and Module Loading
+
+MFC targets HPC clusters. Before building on a cluster, load the correct modules
+via `source ./mfc.sh load -c <slug> -m <mode>`.
+
+To identify the current system, check multiple signals — hostname alone is not always
+sufficient (compute nodes may differ from login nodes):
+
+```bash
+hostname                    # e.g., login-phoenix-gnr-2.pace.gatech.edu
+echo $LMOD_SYSHOST          # e.g., "phoenix" (most reliable when set)
+echo $CRAY_LD_LIBRARY_PATH  # Non-empty → Cray system (Frontier, Carpenter Cray)
+echo $MODULESHOME           # Confirms module system is available
+```
+
+Supported systems and their slugs (full list in `toolchain/modules`):
+
+| Slug | System | GPU Backend | Example |
+|------|--------|-------------|---------|
+| `p` | GT Phoenix | OpenACC (nvfortran) | `source ./mfc.sh load -c p -m g` |
+| `f` | OLCF Frontier | OpenACC/OpenMP (Cray ftn) | `source ./mfc.sh load -c f -m g` |
+| `tuo` | LLNL Tuolumne | OpenMP (Cray ftn) | `source ./mfc.sh load -c tuo -m g` |
+| `d` | NCSA Delta | OpenACC (nvfortran) | `source ./mfc.sh load -c d -m g` |
+| `b` | PSC Bridges2 | OpenACC (nvfortran) | `source ./mfc.sh load -c b -m g` |
+| `cc` | DoD Carpenter (Cray) | CPU only | `source ./mfc.sh load -c cc -m c` |
+| `c` | DoD Carpenter (GNU) | CPU only | `source ./mfc.sh load -c c -m c` |
+| `o` | Brown Oscar | OpenACC (nvfortran) | `source ./mfc.sh load -c o -m g` |
+| `h` | UF HiPerGator | OpenACC (nvfortran) | `source ./mfc.sh load -c h -m g` |
+
+The `-m` flag selects mode: `g`/`gpu` for GPU builds, `c`/`cpu` for CPU-only.
+Batch job templates for `./mfc.sh run -e batch -c <system>` are in `toolchain/templates/`.
+
+IMPORTANT: `source` (or `.`) is required for `load` — it sets environment variables
+in the current shell. Using `./mfc.sh load` without `source` will error.
+
+## Development Workflow Contract
+
+IMPORTANT: Follow this loop for ALL code changes. Do not skip steps.
+
+1. **Read first** — Read and understand relevant code before modifying it.
+2. **Plan** — For multi-file changes, outline your approach before implementing.
+3. **Implement** — Make small, focused changes. One logical change per commit.
+4. **Format** — Run `./mfc.sh format -j 8` to auto-format.
+5. **Verify** — Run `./mfc.sh precheck -j 8` (same 5 checks as CI lint gate).
+6. **Build** — Run `./mfc.sh build -j 8` to verify compilation.
+7. **Test** — Run relevant tests: `./mfc.sh test --only <feature> -j 8`.
+   For changes to `src/common/`, test ALL three targets: `./mfc.sh test -j 8`.
+8. **Commit** — Only after steps 4-7 pass. Do not commit untested code.
+
+YOU MUST run `./mfc.sh precheck` before any commit. This is enforced by pre-commit hooks.
+YOU MUST run tests relevant to your changes before claiming work is done.
+NEVER commit code that does not compile or fails tests.
+
+## Architecture
+
+```
+src/
+  common/         # Shared code (used by ALL three executables — wide blast radius)
+  pre_process/    # Grid generation and initial conditions
+  simulation/     # CFD solver (GPU-accelerated via OpenACC / OpenMP target offload)
+  post_process/   # Data output and visualization
+toolchain/        # Python CLI, build system, testing, parameter management
+  mfc/params/definitions.py   # ~3,400 parameter definitions (source of truth)
+  mfc/case_validator.py       # Physics constraint validation
+  mfc/test/                   # Test runner and case generation
+examples/         # Example simulation cases (case.py files)
+tests/            # 560+ regression test golden files
+```
+
+Source files are `.fpp` (Fortran + Fypp macros), preprocessed to `.f90` by CMake.
+
+## Critical Rules
+
+NEVER use raw OpenACC/OpenMP pragmas (`!$acc`, `!$omp`). Use `GPU_*` Fypp macros instead.
+  Raw `#ifdef`/`#ifndef` preprocessor guards for feature/compiler/library gating ARE normal.
+NEVER use double-precision intrinsics: `dsqrt`, `dexp`, `dlog`, `dble`, `dabs`, `real(8)`, `real(4)`.
+  Use generic intrinsics (`sqrt`, `exp`, `log`) and precision types (`wp`, `stp`).
+NEVER use `d` exponent literals (`1.0d0`). Use `1.0_wp` instead.
+NEVER use `stop` or `error stop`. Use `call s_mpi_abort()` or `@:PROHIBIT()`/`@:ASSERT()`.
+NEVER use `goto`, `COMMON` blocks, or global `save` variables.
+
+Every `@:ALLOCATE(...)` MUST have a matching `@:DEALLOCATE(...)`.
+Every new parameter MUST be added in at least 3 places (4 if it has constraints):
+  1. `toolchain/mfc/params/definitions.py` (parameter definition)
+  2. Fortran variable declaration in `src/*/m_global_parameters.fpp`
+  3. Fortran namelist in `src/*/m_start_up.fpp` (namelist binding)
+  4. `toolchain/mfc/case_validator.py` (only if parameter has physics constraints)
+
+Changes to `src/common/` affect ALL three executables. Test comprehensively.
+
+## Naming Conventions
+
+- Modules: `m_<feature>` (e.g., `m_bubbles`)
+- Public subroutines: `s_<verb>_<noun>` (e.g., `s_compute_pressure`)
+- Public functions: `f_<verb>_<noun>`
+- 2-space indentation, lowercase keywords, explicit `intent` on all arguments
+
+## Precision System
+
+- `wp` = working precision (computation). `stp` = storage precision (field data arrays and I/O).
+- Default: both double. Single mode: both single. Mixed: wp=double, stp=half.
+- MPI types must match: `mpi_p` ↔ `wp`, `mpi_io_p` ↔ `stp`.
+
+## Code Review Priorities
+
+When reviewing PRs, prioritize in this order:
+1. Correctness (logic bugs, numerical issues, array bounds)
+2. Precision discipline (stp vs wp mixing)
+3. Memory management (@:ALLOCATE/@:DEALLOCATE pairing, GPU pointer setup)
+4. MPI correctness (halo exchange, buffer sizing, GPU_UPDATE calls)
+5. GPU code (GPU_* Fypp macros only, no raw pragmas)
+6. Physics consistency (pressure formula matches model_eqns)
+7. Compiler portability (all four compilers)
PATCH

echo "Gold patch applied."
