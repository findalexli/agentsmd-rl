#!/usr/bin/env bash
set -euo pipefail

cd /workspace/amrex

# Idempotency guard
if grep -qF "- `AMREX_GPU_DEVICE`/`ParallelFor` lambdas run on the GPU, so never capture host" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,102 +1,90 @@
 # AMReX Agents Guide
 
-Use this guide whenever you orchestrate explorers/workers inside the AMReX repository. It covers both AMReX developers (PR reviews, bug hunts, new features, and documentation) and AMReX users who ask agents for help learning or building with AMReX. AMReX itself is a C++/Fortran framework for block-structured adaptive mesh refinement (AMR) targeting large-scale PDE simulations on CPU and GPU architectures (CUDA, HIP, SYCL).
+Use this guide whenever you orchestrate explorers/workers inside the AMReX repository. It keeps PR reviews, bug hunts, new features, docs, and user support consistent for contributors and AI copilots alike.
 
 ## Purpose & Personas
 
-- **AMReX developers** – structure every agent task (reviews, fixes, features, documentation) so it is scoped, reproducible, and merged with confidence.
-- **AMReX users** – route questions about capabilities, docs, tutorials, builds, or troubleshooting through the authoritative resources already shipped with the repo.
-
-**Navigation tip**: We reference repository docs by section titles rather than line numbers. Use `rg -n "<heading text>" <file>` (or your editor’s outline) to jump to the relevant sections quickly.
-
-## Repository Layout at a Glance
-
-- `Src/` – Primary C++/Fortran implementation. Subfolders group functionality:
-  - `Amr` / `AmrCore` house mesh hierarchy management, tagging, and regridding logic.
-  - `Base` collects runtime essentials (memory arenas, geometry, I/O helpers) shared by every backend.
-  - `Boundary`, `EB`, `LinearSolvers`, `Particle`, `FFT`, etc. provide focused subsystems; check their `CMakeLists.txt` for build toggles before touching code.
-  - `Extern` and `F_Interfaces` bridge external packages and Fortran bindings.
-- `Tests/` – CTest targets and sample drivers organized by topic (EB, GPU, LinearSolvers, Particles, etc.). When enabling `AMReX_ENABLE_TESTS`, these turn into runnable executables (`ctest -N` to list).
-- `Docs/` – Source of all published documentation. The `sphinx_documentation/` tree feeds the public HTML docs; `Doxygen/` supports reference builds. Edit these when updating guides.
-- `Tools/` – Build helpers, scripts, and shared CMake modules (e.g., `Tools/CMake/AMReXOptions.cmake`) and GNU makefiles.
-
-## Operating Principles
-
-- **Branch hygiene**: Work from short-lived branches based on the latest `development`, and never commit directly on the tracking `development` branch (see the “Git workflow” section of `CONTRIBUTING.md`, especially the “Generally speaking” rules about keeping `development` clean).
-- **Single integration branch**: Treat `development` as the one authoritative branch AMReX maintains (see “Development Model” in `CONTRIBUTING.md`). Every PR must target it, monthly releases are tagged from it, and local work should always rebase onto it before review.
-- **Coding style**: Follow the “AMReX Coding Style Guide” for indentation, brace usage, spacing, and member naming (see the “AMReX Coding Style Guide” section in `CONTRIBUTING.md`). If a change touches code and documentation, keep the style fixes local to the edited blocks.
-- **Plan, scope, and delegate**: For any non-trivial task, sketch a plan, assign clear ownership when spawning explorers/workers, and avoid overlapping write scopes. Prefer `rg` for repo searches to stay fast in large trees.
-- **Build and test defaults**: Confirm which build system the target supports. Repository-level libraries and executables use `cmake` as described in `Docs/sphinx_documentation/source/BuildingAMReX.rst` (section “Customization options”), with `ctest` as the default verification step and flags like `-DAMReX_ENABLE_TESTS=ON` plus `-DAMReX_TEST_TYPE=Small` when you only need a light signal (see the “Tests” block inside `Tools/CMake/AMReXOptions.cmake`). Most tests and tutorials also ship a `GNUmakefile`, and a few legacy drivers only expose that path, so `cd` into the test directory and run `make -j` with the variables it expects (e.g., `DIM`, `USE_MPI`, `USE_CUDA`, `COMP`) following `Tools/GNUMake/README.md`.
-- **Documentation sources**: Lean on the curated entry points listed in the “Documentation” section of `README.md`. They point to the public Sphinx build at `https://amrex-codes.github.io/amrex/docs_html/`, which mirrors the sources under `Docs/sphinx_documentation`. Treat the standalone tutorials repository referenced in `Tutorials/README.md` (`https://github.com/AMReX-Codes/amrex-tutorials`) as additional runnable examples you can cite when users ask how to get started.
-- **Issue logging & hand-off**: Keep a personal, untracked scratchpad on each machine (we recommend `agent-notes/<NN>-<component>-<short-description>.md`). Use it to capture open questions, repro notes, or follow-ups, reusing the numbering/component/title convention described below. Include suggested patches whenever possible so the next agent can act quickly.
-- **Learn from past bugs**: If you already keep a local `agent-notes/` notebook, skim it before diving into similar code to refresh common pitfalls—many historical AMReX bugs came from copy-paste mistakes (e.g., duplicated kernels, swapped indices, missing constant updates), so assume near-identical blocks may hide divergences.
-
-## Developer Playbooks
-
-### PR and Bug Reviews
-1. **Sync & inspect** – Update the local branch, note the PR/issue scope, and record file ownership expectations.
-2. **Reproduce & read** – Reproduce the report using the author’s steps or by running the focused tests. While reading diffs, confirm they honor the rules in the “AMReX Coding Style Guide” section of `CONTRIBUTING.md`.
-3. **Hunt for copy-paste drift** – Compare mirrored kernels, dimension-specific code paths, and duplicated tables; historical regressions often stem from edits applied to one block but not its sibling. Look for suspiciously similar snippets that differ only by variable names or miss a constant update.
-4. **Verify** – Configure the project with the appropriate options (for example, GPU flags or `-DAMReX_TEST_TYPE=Small`) and run `ctest --output-on-failure` from the build directory, or use the test’s `make` rule when it only ships a `GNUmakefile`.
-5. **Focus on hot spots** – Use `cmake --build build -j --target <target_name>` for a single executable/test and `ctest --test-dir build -R <regex>` (or `ctest -R <regex>` inside the build tree) to rerun only the impacted cases; for `GNUmakefile` flows, rerun `make -j` (optionally with a target such as `make run` or `make tests`) inside the test directory. Capture the output.
-6. **Report** – Summarize findings (blocking issues first), highlight required tests, and cite files/lines that need attention.
-7. **Log follow-ups** – If more work is required, open or update the matching file in `agent-notes/` (or your local scratchpad) so the next agent inherits context.
+- **AMReX developers** – follow a predictable workflow so fixes/features land quickly and safely.
+- **AMReX users** – receive accurate build/test/docs guidance sourced from the repo.
+
+## Repository Map
+
+- `Src/` – Core C++/Fortran implementation. `Amr*` manage hierarchy/regridding, `Base` hosts runtime utilities, and folders such as `Boundary`, `EB`, `LinearSolvers`, `Particle`, `FFT` contain subsystem code (check local `CMakeLists.txt` for toggles).
+- `Tests/` – Organized by topic; when `AMReX_ENABLE_TESTS=ON`, they expose `ctest` targets. Many tutorials/tests also ship a `GNUmakefile` for standalone runs.
+- `Docs/` – Authoritative Sphinx sources under `Docs/sphinx_documentation/`; Doxygen lives under `Docs/Doxygen/`.
+- `Tools/` – Shared CMake modules, GNU make helpers, scripts.
+
+## Build & Test Reference
+
+- **Default CMake flow**:
+  ```bash
+  cmake -S . -B build \
+    -DAMReX_ENABLE_TESTS=ON \
+    -DAMReX_TEST_TYPE=Small
+  cmake --build build -j
+  ctest --test-dir build --output-on-failure
+  ```
+  Toggle options from `Docs/sphinx_documentation/source/BuildingAMReX.rst` (“Customization options”) and `Tools/CMake/AMReXOptions.cmake` for GPUs, dimensions, debug flags, etc.
+- **Targeted builds/tests**: `cmake --build build -j --target <name>` for individual executables; `ctest --test-dir build -R <regex>` (or `ctest -R <regex>`) to rerun impacted cases only.
+- **GNUmakefile workflows**: When a directory ships a `GNUmakefile`, `cd` there and run `make -j` with required variables (e.g., `DIM`, `USE_MPI`, `USE_CUDA`, `COMP`) as documented in `Docs/sphinx_documentation/source/BuildingAMReX.rst` and `Tools/GNUMake/README.md`.
+- **Log everything**: Capture exact commands plus pass/fail output in PR descriptions or linked issues so reviewers can reproduce without guessing.
+
+## Hard Rules & Defaults
+
+- Work on short-lived topic branches; never commit directly to `development`. Rebase before opening or updating a PR.
+- Plan before you edit. Define scope, owners, and validation steps, and use `rg` (or your editor) for fast searches to avoid wandering.
+- Choose a build workflow from the “Build & Test Reference” and stick to it for the task; don’t restate commands elsewhere—link back and record the actual invocations you ran.
+- Update user-facing docs under `Docs/sphinx_documentation/` whenever behavior changes, and mention the doc edits in the same PR.
+- When adding Doxygen comments or Sphinx docs, write for AMReX users: explain behavior and usage, omit unnecessary implementation details, and keep the tone instructional instead of developer-oriented.
+- Never log work inside `CHANGES.md`; release notes are curated separately, so leave that file untouched unless maintainers ask for a release update.
+- Hand-off context inside PRs/issues (commands run, results, TODOs). Personal scratchpads are optional, local, and should be pruned frequently.
+- AI delegation: assign disjoint write scopes, keep subtasks bounded, and serialize conflicting edits when necessary. Review every AI-generated diff like a teammate’s patch.
+- Safety: never paste secrets, private datasets, or PII into prompts; scrub logs before sharing; cite sources and licensing when in doubt by escalating to maintainers.
+- Testing accountability: every substantive change must state which tests ran (and command lines) in the PR/issue.
+- Historical hotspots: mirrored kernels and dimension-specific paths often drift—compare siblings whenever you touch them.
+
+## GPU Lambda Safety
+
+- `AMREX_GPU_DEVICE`/`ParallelFor` lambdas run on the GPU, so never capture host-only pointers (e.g., `Geometry::CellSize()`, `Geometry::ProbLo()`). Take the device-safe views first—e.g., `auto const dx = geom.CellSizeArray();`, `auto const problo = geom.ProbLoArray();`—and pass those by value into the lambda.
+
+## Task Playbooks
+
+### PR & Bug Review
+1. **Sync & scope** – Update the branch, read the PR/issue description, and note ownership expectations.
+2. **Reproduce** – Follow the reporter’s steps or minimal `ctest`/`make` invocations from the Build & Test Reference.
+3. **Inspect diffs** – Check style, compare mirrored kernels/dimensional variants, and look for missing constant updates.
+4. **Verify** – Run the focused tests (GPU flags, `-DAMReX_TEST_TYPE=Small`, GNU make targets, etc.) and capture output.
+5. **Report** – List blockers first, cite files/lines, and record the commands/tests in the PR.
+6. **Follow-ups** – Document remaining work in the PR/issue; use a scratchpad only for personal reminders.
 
 ### Feature or Fix Implementation
-1. **Understand scope** – Capture requirements, physics context, and success criteria from the originating issue/PR.
-2. **Configure builds quickly** – Choose the workflow the directory expects. Use the standard `cmake` pattern below, adding any extra `-D` knobs listed in the “Customization options” portion of `Docs/sphinx_documentation/source/BuildingAMReX.rst`.
-
-   ```bash
-   cmake -S . -B build \
-     -DAMReX_ENABLE_TESTS=ON \
-     -DAMReX_TEST_TYPE=Small
-   cmake --build build -j
-   ctest --test-dir build --output-on-failure
-   ```
-
-   When only one binary or test matters, leverage `cmake --build build -j --target <target_name>` and `ctest --test-dir build -R <regex>` to keep feedback loops short.
-
-   Directories that rely on `GNUmakefile` (many tutorials/tests, plus a handful of legacy drivers) follow the guidance in `Docs/sphinx_documentation/source/BuildingAMReX.rst` and `Tools/GNUMake/README.md`. Set only the variables that the specific example requires (`DIM`, `USE_MPI`, `USE_CUDA`, `COMP`, etc.) so they reflect the hardware/features you intend to exercise. Edit the local `GNUmakefile` or pass those variables on the command line, then build with `make`. For instance, a 3D CNS run that enables both MPI and CUDA would be:
-
-   ```bash
-   cd Tests/GPU/CNS
-   make -j8 DIM=3 USE_MPI=TRUE USE_CUDA=TRUE
-   ```
-
-3. **Implement with traceability** – Touch only the files you own in this task, annotate complex code with succinct comments, and reference relevant issue IDs.
-4. **Document** – Update user-facing docs whenever behavior changes. Pull content from the “Documentation” section of `README.md` (User’s Guide, Example Codes, Guided Tutorials, Technical Reference) so users know where to look.
-5. **Hand off** – Record remaining questions, test logs, or benchmarking data inside `agent-notes/` (or your local scratchpad) or the PR description, including exact commands run and their outcomes.
-
-### Documentation and Tutorial Updates
-- For feature additions, mirror the doc hierarchy described in the “Documentation” section of `README.md` so the User’s Guide, Example Codes, and Guided Tutorials stay synchronized.
-- Surface new build options or workflows in `Docs/sphinx_documentation/source/BuildingAMReX.rst` so the `Customization options` table stays authoritative.
+1. **Confirm requirements** – Capture physics context, success metrics, and acceptance tests from the originating ticket.
+2. **Configure builds** – Apply the Build & Test Reference workflow that matches the directory; use targeted targets/tests for fast iteration.
+3. **Implement carefully** – Touch only owned files, note tricky code with short comments, and maintain coding-style guidelines.
+4. **Update docs** – When behavior or UX changes, add/adjust content in the relevant `Docs/sphinx_documentation/` section (User’s Guide, Technical Reference, tutorials, etc.).
+5. **Validate** – Run and record the necessary `ctest`/`make` commands plus any benchmarking or profiling relevant to the change.
+6. **Hand off** – Summarize status, remaining risks, and next steps in the PR description; attach log excerpts only if scrubbed.
+
+### Documentation & Tutorial Updates
+- Mirror the hierarchy noted in `README.md` (User’s Guide, Example Codes, Guided Tutorials, Technical Reference) so published docs stay synchronized.
+- Surface any new build knobs/workflows in `Docs/sphinx_documentation/source/BuildingAMReX.rst`.
+- Reference runnable examples in `Tutorials/README.md` or `https://github.com/AMReX-Codes/amrex-tutorials` when guiding users.
 
 ## Guidance for AMReX Users Working with Agents
 
-- **Getting oriented**: Summarize AMReX capabilities using the “Overview,” “Features,” and “Documentation” sections in `README.md`. Link users to the appropriate resource (User’s Guide, Example Codes, Guided Tutorials, Technical Reference).
-- **Building & testing quickly**: Start with whichever build system the example ships. Walk users through the `cmake` workflow highlighted in the “Customization options” part of `Docs/sphinx_documentation/source/BuildingAMReX.rst` (showing how to toggle features with the `-D<var>=<value>` syntax), and when they are inside a tutorial or test directory that provides a `GNUmakefile`, point them to the same doc plus `Tools/GNUMake/README.md` so they can run `make -j` with variables such as `DIM`, `USE_MPI`, and `USE_CUDA`.
-- **Learning resources**: Direct users to the standalone tutorials repository noted in `Tutorials/README.md` (`https://github.com/AMReX-Codes/amrex-tutorials`) and supplement with the slides/videos featured near the “Documentation” section of `README.md`.
-- **Consult Sphinx sources**: When clarifying documentation or preparing local updates, read directly from `Docs/sphinx_documentation` (especially the `source/` subtree). This is the exact content published online, so citing it keeps agent answers aligned with the official docs.
-- **Getting help or contributing back**: Encourage questions through GitHub Discussions and remind users that contributions go through `CONTRIBUTING.md`, as described in the “Get Help” and “Contribute” sections of `README.md`.
-
-## Agent Notes & Hand-off
-
-Agents rely on a lightweight, per-machine scratchpad to capture ephemeral context (repro steps, local experiments, or future TODOs) without polluting the repo. This is an agent-side convention, not an upstream AMReX requirement—keep it untracked so you can jot candid notes and prune freely.
+- **Orientation** – Summarize capabilities using the “Overview,” “Features,” and “Documentation” sections of `README.md`, then link users to the best resource (User’s Guide, Example Codes, Guided Tutorials, Technical Reference).
+- **Build help** – Walk through the Build & Test Reference commands, clarifying how to toggle features via `-DVAR=value` or `make` variables the tutorial expects.
+- **Learning resources** – Point to the tutorials repo plus any slides/videos referenced near the Documentation section of `README.md`.
+- **Authoritative sources** – Read directly from `Docs/sphinx_documentation/` when answering doc questions so citations match the published site.
+- **Support channels** – Encourage GitHub Discussions/issues for unresolved questions and remind users that contributions follow `CONTRIBUTING.md`.
 
-- **Where**: Create an `agent-notes/` folder at the repo root. If you already standardized on another name, that’s acceptable—just stay consistent on that machine. File names follow `NN-component-short-description.md`, where `NN` is a zero-padded counter unique per workstation.
-- **What to include**:
-  - Title line summarizing the issue or follow-up.
-  - Metadata bullets for `Type` (Bug/Feature/Docs), `Severity`, `Component`, and an approximate `Location` (file:line or directory).
-  - Sections for `Problem`, `Impact`, and `Next steps` or `Suggested patch`. Link to relevant PRs, branches, or external tickets if applicable.
-  - Exact reproduce/build/test commands and outputs to save the next agent time.
-- **Sharing**: Because the folder is local-only, copy the relevant markdown snippet into a PR description, long-form review, or upstream issue whenever collaborators need visibility.
+## Optional Personal Notes
 
-Include ready-to-apply patches or diff hunks whenever possible so other agents (or future you) can fast-track the fix.
+A local scratchpad can help you capture quick reminders, but keep it untracked, short-lived, and private. Anything others need to know belongs in PR descriptions, issues, or review comments.
 
 ## Quick Checklist
 
-1. Confirm you are on a task-specific branch that tracks `development` cleanly (see the “Git workflow” guidance in `CONTRIBUTING.md`).
-2. Plan the task, noting deliverables, ownership, and validation steps before spawning sub-agents.
-3. Build with the workflow the directory expects: either run the standard `cmake`/`ctest` flow (with `AMReX_ENABLE_TESTS` and `AMReX_TEST_TYPE` toggles per “Customization options” in `Docs/sphinx_documentation/source/BuildingAMReX.rst` and the “Tests” block in `Tools/CMake/AMReXOptions.cmake`) or `cd` into the `GNUmakefile` tree and run `make -j` with the required variables (e.g., `DIM`, `USE_MPI`, `USE_CUDA`).
-4. Update documentation and user guidance by referencing the resources enumerated in the “Documentation” section of `README.md`.
-5. Capture unresolved work, context, and suggested patches in `agent-notes/` (or your local scratchpad) so future agents can pick up where you left off.
+1. On a topic branch rebased on `development`? If not, fix it.
+2. Do you have a written plan that names owners, validation, and Build & Test commands? If not, write one before editing.
+3. Are tests/docs updated and the exact commands/results logged in the PR/issue? If not, add them.
+4. Are delegation, safety, and hand-off notes captured in canonical threads (not just scratchpads)? If not, update them now.
PATCH

echo "Gold patch applied."
