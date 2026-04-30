#!/usr/bin/env bash
set -euo pipefail

cd /workspace/riscv-unified-db

# Idempotency guard
if grep -qF "Extract all RISC-V instruction names mentioned in the specified subsection of th" ".agents/skills/extract-instructions-from-subsection/SKILL.md" && grep -qF "The RISC-V Unified Database (UnifiedDB/UDB) is a repository that holds all infor" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/extract-instructions-from-subsection/SKILL.md b/.agents/skills/extract-instructions-from-subsection/SKILL.md
@@ -0,0 +1,113 @@
+---
+name: extract-instructions-from-subsection
+description: Extract RISC-V instruction names from a named subsection of an AsciiDoc file and write them to /tmp/<subsection-title>.yaml.
+argument-hint: <subsection-title> <adoc-file>
+allowed-tools: Read, Bash, Write
+---
+
+Copyright (c) 2026 Qualcomm Technologies, Inc. and/or its subsidiaries.
+SPDX-License-Identifier: BSD-3-Clause-Clear
+
+Extract all RISC-V instruction names mentioned in the specified subsection of the given AsciiDoc file, then write them to `/tmp/<subsection-title>.yaml`, where `<subsection-title>` is argument 1 lowercased with spaces replaced by hyphens (e.g., `"Multiplication Operations"` → `/tmp/multiplication-operations.yaml`).
+
+## Arguments
+
+$ARGUMENTS
+
+- **Argument 1**: The subsection title to search for (e.g., `"Multiplication Operations"` or `"Integer Register-Immediate Instructions"`).
+- **Argument 2**: Path to the AsciiDoc file (e.g., `ext/riscv-isa-manual/src/m-st-ext.adoc`).
+
+If either argument is missing, ask the user to provide it.
+
+## Steps
+
+### 1. Read the AsciiDoc file
+
+Read the full content of the AsciiDoc file given as argument 2.
+
+### 2. Locate the subsection
+
+Find the subsection whose title matches argument 1. AsciiDoc section headings use `=` prefixes:
+- `== Title` — level 1 (chapter)
+- `=== Title` — level 2
+- `==== Title` — level 3
+- `===== Title` — level 4
+
+Match the subsection title case-insensitively. The subsection's content starts on the line after the heading and ends just before the next heading of equal or higher level (i.e., same or fewer `=` characters).
+
+### 3. Identify NOTE blocks to skip
+
+Before scanning for instructions, mark all NOTE blocks in the subsection so they can be excluded. AsciiDoc NOTE blocks appear in two forms:
+
+- **Delimited block**: starts with `[NOTE]` followed by `====` on the next line, and ends at the closing `====`.
+- **Inline note**: a single line starting with `NOTE:` (no delimiter).
+
+Any instruction name that appears **only** inside NOTE blocks — and nowhere else in the subsection — must be excluded from the output. If an instruction appears both inside and outside a NOTE block, include it.
+
+### 4. Extract instruction names
+
+Scan the non-NOTE text of the subsection for RISC-V instruction names. Instruction names appear as **uppercase tokens** in the prose. Use the following rules to identify them:
+
+**Patterns that indicate an instruction name:**
+- All-uppercase tokens of at least 2 characters that consist only of letters, and optionally digits or dots (e.g., `ADD`, `ADDI`, `MULHSU`, `FENCE.TSO`, `LR.W`, `SC.D`, `C.ADD`, `C.ADDI16SP`)
+- Uppercase tokens inside backticks: `` `ADD` ``, `` `JALR` ``
+- Uppercase tokens in AsciiDoc index entries: `(((MUL, MULH)))` — extract each comma-separated token
+- Uppercase tokens in AsciiDoc comment lines like `//.Integer register-register` — skip these (they are labels, not instructions)
+
+**Exclude pseudoinstructions:**
+The prose explicitly signals pseudoinstructions with the phrase "assembler pseudoinstruction" or "pseudoinstruction" adjacent to the name, e.g.:
+- `assembler pseudoinstruction SNEZ _rd, rs_`
+- `assembler pseudoinstruction MV _rd, rs1_`
+- `assembler pseudoinstruction SEQZ _rd, rs_`
+- `assembler pseudoinstruction NOT _rd, rs_`
+- `assembler pseudoinstruction J`
+- `assembler pseudoinstruction RET`
+- `assembler pseudoinstruction JR`
+
+Any token introduced by "pseudoinstruction" (with or without "assembler") must be excluded, even if it appears elsewhere in the subsection outside a pseudoinstruction context. Collect all pseudoinstruction names first, then exclude them from the final list.
+
+**Definitive exclusion list — never treat these as instructions:**
+`XLEN`, `RV32`, `RV64`, `RV32I`, `RV64I`, `RV128I`, `ISA`, `ABI`, `PC`, `CSR`, `IALIGN`, `BTB`, `RAS`, `FPGA`, `MIPS`, `RISC`, `RISCV`, `RISC-V`
+
+Tokens that are register names (`x0`–`x31`, `rd`, `rs1`, `rs2`) — exclude them.
+
+### 5. Deduplicate and normalize
+
+- Convert all extracted names to **lowercase** (matching the RISC-V Unified Database YAML file naming convention, e.g., `ADD` → `add`, `MULHSU` → `mulhsu`, `FENCE.TSO` → `fence.tso`, `LR.W` → `lr.w`)
+- Remove duplicates
+- Sort alphabetically
+
+### 6. Write the output
+
+Derive the output filename from argument 1: lowercase it and replace spaces with hyphens (e.g., `"Multiplication Operations"` → `multiplication-operations`). Write `/tmp/<derived-name>.yaml` with the following format:
+
+```yaml
+instructions:
+  - add
+  - addi
+  - mul
+  - mulh
+```
+
+Use the Write tool to create the file.
+
+### 7. Report
+
+Print a summary:
+- The subsection title found
+- The number of instructions extracted
+- The path written (e.g., `/tmp/multiplication-operations.yaml`)
+- The list of instructions
+
+## Example
+
+For subsection `"Multiplication Operations"` in `ext/riscv-isa-manual/src/m-st-ext.adoc`, the output file is `/tmp/multiplication-operations.yaml`:
+
+```yaml
+instructions:
+  - mul
+  - mulh
+  - mulhsu
+  - mulhu
+  - mulw
+```
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,120 @@
+<!--
+Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
+SPDX-License-Identifier: BSD-3-Clause-Clear
+-->
+
+# AGENTS.md
+
+This file provides guidance to Gen AI agents when working with code in this repository.
+
+## Overview
+
+The RISC-V Unified Database (UnifiedDB/UDB) is a repository that holds all information needed to describe RISC-V: extensions, instructions, CSRs, profiles, and documentation prose. Tools generate artifacts (spec documents, simulators, toolchain inputs) from this data.
+
+**Important:** This project is under rapid development. Schemas and APIs change frequently. Data in `spec/` is a work in progress.
+
+## Common Commands
+
+```bash
+./bin/regress -h              # help on running regression tests
+./bin/generate -h             # help on generating content
+./bin/chore -h                # help on repository development chores
+
+./bin/regress --list          # list all regression tests
+./bin/regress --tag smoke     # run smoke tests (fast subset)
+./bin/regress --tag unit      # run unit tests
+./bin/regress --all           # run full regression suite
+./bin/regress -n <test-name>  # run a single named test
+./bin/regress -n regress-udb-unit-test --matrix=test=conditions  # run a single matrix variant
+
+./do test:idlc:unit           # run IDL compiler unit tests
+./do test:udb:unit            # run UDB library unit tests
+./do test:sorbet              # run Sorbet type checks
+./do test:idl CFG=_           # type-check IDL for a config (also: rv32, rv64, qc_iu)
+./do test:inst_encodings      # check instruction encoding conflicts
+./do test:schema              # validate all arch files against schemas
+
+./do gen:arch                 # generate arch files from layout templates
+./do gen:resolved_arch CFG=_  # resolve a configuration (default: "_" = unconfigured)
+./do gen:schemas              # resolve schema files to gen/schemas/
+
+./bin/generate manual -v all -f html          # generate HTML ISA manual
+./bin/generate ext-doc -h                     # generate extension documentation
+./bin/udb-gen isa-explorer -t ext-browser -o gen/isa_explorer  # ISA explorer
+
+./bin/pre-commit              # run pre-commit checks manually
+```
+
+## Architecture
+
+### Repository Structure
+
+- `spec/std/isa/` — RISC-V standard data (extensions, instructions, CSRs, profiles, etc.)
+- `spec/custom/isa/` — Non-standard/custom extensions
+- `spec/schemas/` — JSON schemas for all data types
+- `cfgs/` — Architecture configurations used by backends
+- `backends/` — Artifact generators (documents, simulators, etc.)
+- `tools/ruby-gems/` — Ruby gem libraries
+- `tools/test/` — Test infrastructure
+- `bin/` — Wrapper scripts for container-aware execution
+- `gen/` — Generated output (gitignored)
+- `ext/` — Git submodules (riscv-isa-manual, riscv-opcodes, riscv-tests, etc.)
+
+### Data Model
+
+All spec data is YAML with JSON schema validation. Every file starts with:
+```yaml
+$schema: "<schema-name>.json#"
+kind: <object-type>
+name: <unique-name>
+```
+
+Key data types and their locations:
+- **Extensions**: `spec/std/isa/ext/<Name>.yaml`
+- **Instructions**: `spec/std/isa/inst/<Extension>/<name>.yaml`
+- **CSRs**: `spec/std/isa/csr/<Extension>/<name>.yaml`
+- **Profiles**: `spec/std/isa/profile/`, `spec/std/isa/profile_release/`, `spec/std/isa/profile_family/`
+
+Some files are auto-generated from `.layout` ERB templates (e.g., AMO variants, HPM counters, PMP registers). Run `./do gen:arch` to regenerate them. Auto-generated files are read-only (chmod 0444).
+
+### Configurations (`cfgs/`)
+
+A configuration YAML specifies which extensions are mandatory/optional and sets parameter values. The special `_` config is the fully unconfigured architecture. Backends use configs to customize output.
+
+### Ruby Library (`tools/ruby-gems/`)
+
+Four gems:
+- **`udb`** — Core database API (`Udb::Architecture`, `Udb::Resolver`, and all object types in `lib/udb/obj/`)
+- **`idlc`** — IDL compiler (parser, type checker, AST, passes)
+- **`udb-gen`** — Generator backends
+- **`udb_helpers`** — Shared utilities
+
+The `Udb::Resolver` class is the entry point: `resolver.cfg_arch_for("rv64")` returns an `Architecture` object. The `Architecture` class provides methods like `extensions()`, `instructions()`, `csrs()`, `profiles()`, etc.
+
+### ISA Description Language (IDL)
+
+IDL is a domain-specific language (C/Verilog-like syntax) used to formally describe instruction behavior and CSR semantics. IDL code appears in `operation():` fields of instruction YAML files and in CSR YAML files.
+
+IDL is compiled by the `idlc` gem. The compiler performs type checking and can generate AsciiDoc documentation, option analysis, and other passes. Key types: `Bits<N>`, `XReg` (alias for `Bits<MXLEN>`), `Boolean`, enums, bitfields, structs.
+
+### Backends (`backends/`)
+
+Each backend has a `tasks.rake` file that registers Rake tasks. Key backends:
+- `cfg_html_doc` — HTML documentation for a specific config
+- `cpp_hart_gen` — C++ ISS (Instruction Set Simulator) hart model
+- `prm_pdf` — Processor Requirements Manual PDF
+- `instructions_appendix` — Instruction appendix AsciiDoc/PDF
+
+### CI / Pre-commit
+
+Pre-commit hooks run automatically on `git commit`. They include YAML/JSON linting, schema validation, and prettier formatting. If a hook auto-fixes files, `git add` the changes and recommit.
+
+CI is split into PR tests (`ci_stage: pr`) and merge-queue deployment tests (`ci_stage: merge_queue`). Test definitions are in `tools/test/regress-tests.yaml`.
+
+## Contribution Notes
+
+- Squash merge policy: PR title/description becomes the commit message
+- Follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0) style (not enforced)
+- PRs require approval from a Code Owner (see `.github/CODEOWNERS`)
+- Link PRs to issues with `Fixes #<number>` or `Closes #<number>` in the PR description
+- All PRs must pass `./bin/regress --all`
PATCH

echo "Gold patch applied."
