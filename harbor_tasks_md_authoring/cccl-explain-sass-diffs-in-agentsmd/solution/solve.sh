#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cccl

# Idempotency guard
if grep -qF "Detect relevant changes in generated CUDA machine code (i.e. SASS) while filteri" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -273,6 +273,54 @@ Test organization:
 
 ---
 
+## SASS Diffs
+
+Use this test when asked to check for SASS changes between commits, branches or a local changeset.
+
+### Goal
+
+Detect relevant changes in generated CUDA machine code (i.e. SASS) while filtering noise from addresses, symbols, metadata, etc.
+Any non-trivial change must be detected.
+
+### Inputs to establish
+
+* Compiled binary under test
+* The CUDA SM architectures to compile for. Try to detect this from the code and offer the user a list of suggestions.
+  The user must conform or provide this list.
+* Baseline disassembly (from the previous commit/branch or the current commit without the changes in the working copy).
+* Comparison disassembly (form the current commit/branch or the current commit with the changes in the working copy).
+* By default, prefer `cuobjdump -sass` to inspect SASS changes.
+  Use `cuobjdump -ptx` if the request is to check for PTX changes instead.
+
+### Normalization rules (strip known noise)
+
+Apply these transforms to both baseline and candidate listings before diffing.
+Write the normalized listings to separate files.
+
+* Remove addresses/offsets/hex location prefixes.
+* Remove build IDs, timestamps, absolute paths, temp directories, and compiler banners.
+* Normalize whitespace and alignment to single spaces.
+* Remove empty lines and purely comment lines.
+
+### Comparison rules (what matters)
+
+Ignore as trivial:
+
+* Register renaming with identical instruction sequence and operands.
+* Pure label renumbering or reordering of identical basic blocks.
+* Formatting-only differences or reordered symbol tables.
+
+### Reporting
+
+* If any non-trivial change was detected, the top 5 regions where a non-trivial change was detected,
+  including the name of the kernel they appeared in.
+* A short summary of the diff type (opcode change, memory access size change, size delta, control-flow, etc.).
+* Explicitly state if only noise was detected after normalization.
+* If you are not sure if the differences are impactful, show it and ask the user for guidance.
+* Keep the disassembly dumps available for reference and show the command to the user to generate a diff.
+
+---
+
 ## Continuous Integration (CI)
 
 See `ci-overview.md` for detailed examples and troubleshooting guidance.
PATCH

echo "Gold patch applied."
