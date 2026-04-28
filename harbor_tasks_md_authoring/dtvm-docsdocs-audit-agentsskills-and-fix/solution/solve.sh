#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dtvm

# Idempotency guard
if grep -qF "3. Add a row to the \"Current Entries\" table in `docs/_archive/README.md`" ".agents/skills/archive/SKILL.md" && grep -qF ".agents/skills/dev-workflow/SKILL.md" ".agents/skills/dev-workflow/SKILL.md" && grep -qF "- **EVM-specific**: `evm_umul128_lo` (64\u00d764\u219264, low half) and `evm_umul128_hi` (" ".agents/skills/dmir-compiler-analysis/SKILL.md" && grep -qF "Source: `isRAExpensiveOpcode()` in `src/compiler/evm_frontend/evm_analyzer.h`." ".agents/skills/dmir-compiler-analysis/cost-model.md" && grep -qF "| add/sub/mul/and/or/xor | `CgLowering::lowerBinaryOpExpr` (base in `lowering.h`" ".agents/skills/dmir-compiler-analysis/evm-to-dmir.md" && grep -qF "`<repo>/.agents/skills/dtvm-perf-profile/scripts/perf_profile.sh` \u2014 not" ".agents/skills/dtvm-perf-profile/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/archive/SKILL.md b/.agents/skills/archive/SKILL.md
@@ -59,14 +59,10 @@ After confirmation:
 
 1. Create `docs/_archive/<YYYY-MM>/` if it does not exist
 2. Move the change directory: `docs/changes/YYYY-MM-DD-<slug>/` to `docs/_archive/<YYYY-MM>/<slug>/`
-3. Update the table in `docs/changes/README.md` (remove or mark the entry)
-4. Add the entry to `docs/_archive/README.md`
+3. Add a row to the "Current Entries" table in `docs/_archive/README.md`
 
-### 4. Cleanup (Optional)
-
-Ask the user:
-- **Branch cleanup**: `git branch -d <branch-name>` (if merged)
-- **Worktree cleanup**: `git worktree remove <path>` (if used)
+Branch and worktree cleanup are out of scope for this skill — leave them
+to the user.
 
 ## Batch Archival
 
diff --git a/.agents/skills/dev-workflow/SKILL.md b/.agents/skills/dev-workflow/SKILL.md
@@ -19,8 +19,6 @@ End-to-end workflow for implementing changes: propose, plan, execute, verify, an
 
 3. Fill in the document and set status to `Proposed`
 
-4. Add the entry to the table in `docs/changes/README.md`
-
 ## Phase B - Plan
 
 After the change proposal is accepted:
diff --git a/.agents/skills/dmir-compiler-analysis/SKILL.md b/.agents/skills/dmir-compiler-analysis/SKILL.md
@@ -14,9 +14,9 @@ function names for every EVM opcode handler. The code may have evolved since thi
 skill was written; treat discrepancies as the code being correct.
 
 For each EVM opcode, the complete source trace is:
-1. **Dispatch**: `EVMByteCodeVisitor::decode()` in `src/action/evm_bytecode_visitor.h` (line ~108)
+1. **Dispatch**: `EVMByteCodeVisitor::decode()` in `src/action/evm_bytecode_visitor.h`
 2. **Builder**: `EVMMirBuilder::handle*()` in `src/compiler/evm_frontend/evm_mir_compiler.h` (templates) and `evm_mir_compiler.cpp` (implementations)
-3. **x86 lowering**: `X86CgLowering::lower*()` in `src/compiler/target/x86/x86lowering.cpp`
+3. **x86 lowering**: `X86CgLowering::lower*()` in `src/compiler/target/x86/x86lowering.cpp` (definitions) and `x86lowering.h` (class)
 
 See [evm-to-dmir.md](evm-to-dmir.md) for the full per-opcode source location table.
 
@@ -72,12 +72,12 @@ Defined in `src/compiler/mir/opcodes.def`:
 - **Binary**: `add`, `sub`, `mul`, `sdiv`, `udiv`, `srem`, `urem`, `and`, `or`, `xor`, `shl`, `sshr`, `ushr`, `rotl`, `rotr`, `fpdiv`, `fpmin`, `fpmax`, `fpcopysign`
 - **Overflow**: `wasm_sadd_overflow`, `wasm_uadd_overflow`, `wasm_ssub_overflow`, `wasm_usub_overflow`, `wasm_smul_overflow`, `wasm_umul_overflow`
 - **Conversion**: `inttoptr`, `ptrtoint`, `trunc`, `sext`, `uext`, `fptrunc`, `fpext`, `sitofp`, `uitofp`, `bitcast`, `wasm_fptosi`, `wasm_fptoui`
-- **Other exprs**: `dread`, `const`, `cmp`, `adc`, `select`, `load`
-- **EVM-specific**: `evm_umul128_lo` (64x64->64 low), `evm_umul128_hi` (extract high 64 from umul128)
+- **Other exprs**: `phi`, `dread`, `const`, `cmp`, `adc`, `sbb`, `select`, `load`, `wasm_sadd128_overflow`, `wasm_uadd128_overflow`, `wasm_ssub128_overflow`, `wasm_usub128_overflow`
+- **EVM-specific**: `evm_umul128_lo` (64×64→64, low half) and `evm_umul128_hi` (extracts the high half from the preceding `evm_umul128_lo`); `evm_u256_mul` (256×256→256 pseudo-op) and `evm_u256_mul_result` (extracts extra limb from the preceding `evm_u256_mul`); `evm_udiv128_by64` (128/64 unsigned quotient) and `evm_urem128_by64` (remainder of the same 128/64 division).
 - **Control flow**: `br`, `br_if`, `switch`, `call`, `icall`, `return`
 - **Statements**: `dassign`, `store`, `wasm_check_memory_access`, `wasm_visit_stack_guard`, `wasm_check_stack_boundary`
 
-Condition codes (`src/compiler/mir/cond_codes.def`): `ieq`, `ine`, `iugt`, `iuge`, `iult`, `iule`, `isgt`, `isge`, `islt`, `isle` (integer); `foeq`, `fogt`, `foge`, `folt`, `fole`, `fone`, `ford`, `funo`, `fueq`, `fugt`, `fuge`, `fult`, `fule`, `fune` (float).
+Condition codes (`src/compiler/mir/cond_codes.def`): `ieq`, `ine`, `iugt`, `iuge`, `iult`, `iule`, `isgt`, `isge`, `islt`, `isle` (integer); `ffalse`, `foeq`, `fogt`, `foge`, `folt`, `fole`, `fone`, `ford`, `funo`, `fueq`, `fugt`, `fuge`, `fult`, `fule`, `fune`, `ftrue` (float; `ffalse`/`ftrue` are always folded).
 
 ## dMIR Textual Format
 
@@ -181,7 +181,8 @@ Read these when deeper analysis is needed:
 | EVM bytecode dispatch | `src/action/evm_bytecode_visitor.h` |
 | EVM analyzer (weights) | `src/compiler/evm_frontend/evm_analyzer.h` |
 | dMIR -> CGIR lowering | `src/compiler/cgir/lowering.h` |
-| x86 lowering | `src/compiler/target/x86/x86lowering.cpp` |
+| x86 lowering class | `src/compiler/target/x86/x86lowering.h` |
+| x86 lowering impl | `src/compiler/target/x86/x86lowering.cpp` (core), `x86lowering_wasm.cpp` (wasm-specific), `x86lowering_fallback.cpp` (fallback paths) |
 | x86 MC emission | `src/compiler/target/x86/x86_mc_lowering.h` |
 | Virtual reg map | `src/compiler/cgir/pass/virt_reg_map.h` |
 | Compiler pipeline | `src/compiler/compiler.cpp` |
@@ -226,6 +227,6 @@ Evaluate overall impact:
 
 ## Additional Resources
 
-- For detailed EVM-to-dMIR pseudocode per opcode with **exact source locations**, see [evm-to-dmir.md](evm-to-dmir.md)
-- For dMIR-to-x86 lowering patterns with **exact lowering functions**, see [dmir-to-x86.md](dmir-to-x86.md)
+- For detailed EVM-to-dMIR pseudocode per opcode with its **source file and handler symbol**, see [evm-to-dmir.md](evm-to-dmir.md)
+- For dMIR-to-x86 lowering patterns with the **lowering function symbol**, see [dmir-to-x86.md](dmir-to-x86.md)
 - For the dMIR instruction x86 cost table and implementation comparison methodology, see [cost-model.md](cost-model.md)
diff --git a/.agents/skills/dmir-compiler-analysis/cost-model.md b/.agents/skills/dmir-compiler-analysis/cost-model.md
@@ -155,13 +155,17 @@ slowly (superlinear cost). This affects JIT compilation latency, not runtime
 execution speed. The `isRAExpensiveOpcode()` heuristic in `evm_analyzer.h`
 tracks this:
 
-| EVM Opcode | Why RA-Expensive | Source |
-|---|---|---|
-| MUL (0x02) | ~80 dMIR, heavy partial-product fan-out | evm_analyzer.h:80 |
-| SIGNEXTEND (0x0B) | ~21 Selects, two dependency chain loops | evm_analyzer.h:81 |
-| SHL (0x1B) | ~92 Selects, nested J,K loops | evm_analyzer.h:82 |
-| SHR (0x1C) | ~96 Selects, nested J,K loops | evm_analyzer.h:83 |
-| SAR (0x1D) | ~52 Selects, sign-extended variant | evm_analyzer.h:84 |
+| EVM Opcode | Why RA-Expensive |
+|---|---|
+| SIGNEXTEND (0x0B) | ~21 Selects, two dependency chain loops |
+| SHL (0x1B) | ~92 Selects, nested J,K loops |
+| SHR (0x1C) | ~96 Selects, nested J,K loops |
+| SAR (0x1D) | ~52 Selects, sign-extended variant |
+
+Source: `isRAExpensiveOpcode()` in `src/compiler/evm_frontend/evm_analyzer.h`.
+MUL (0x02) has a heavy partial-product fan-out (~80 dMIR) but is excluded
+from this heuristic: its `evm_umul128_*` schoolbook pattern does not generate
+the dense Select chains that drive superlinear greedy RA cost.
 
 If an optimization reduces dMIR count enough, these opcodes may no longer trigger
 JIT fallback, which is itself a significant performance improvement (JIT vs interpreter).
@@ -226,7 +230,7 @@ This illustrates why the current ADD+ADC chain is already near-optimal for x86.
 ## Source Reference
 
 For current implementation weights used by the JIT suitability checker:
-`MIR_OPCODE_WEIGHT[256]` in `src/compiler/evm_frontend/evm_analyzer.h:31`.
+`MIR_OPCODE_WEIGHT[256]` in `src/compiler/evm_frontend/evm_analyzer.h`.
 
 Note: this weight table reflects the **current** handler implementations. When you
 optimize a handler and change its dMIR output count, this table should also be
diff --git a/.agents/skills/dmir-compiler-analysis/evm-to-dmir.md b/.agents/skills/dmir-compiler-analysis/evm-to-dmir.md
@@ -9,192 +9,205 @@ for every EVM opcode.
 
 ## 0. Source Trace Table (Authoritative)
 
-Every EVM opcode is dispatched in `EVMByteCodeVisitor::decode()` at
-`src/action/evm_bytecode_visitor.h:108`. The visitor calls local `handle*()` wrappers
-that pop/push the EVM stack and delegate to `EVMMirBuilder::handle*()` for dMIR generation.
+Every EVM opcode is dispatched from `EVMByteCodeVisitor::decode()` in
+`src/action/evm_bytecode_visitor.h` (a big `switch` over `evmc_opcode`). Each
+opcode ends up in a handler on `EVMMirBuilder`. Unless noted:
+
+- Non-template handlers live in `src/compiler/evm_frontend/evm_mir_compiler.cpp`.
+- Templated handlers `handleBinaryArithmetic<...>`, `handleBitwiseOp<...>`,
+  `handleShift<...>`, `handleCompareOp<...>` are defined inline in
+  `src/compiler/evm_frontend/evm_mir_compiler.h`. `handleLogWithTopics<N>`
+  is a template but its definition lives in the `.cpp`.
+
+Grep the symbol name to find the current definition; line numbers drift.
 
 ### Arithmetic
 
-| EVM Opcode | Hex | Visitor Dispatch (evm_bytecode_visitor.h) | Builder Function | Builder Location |
-|---|---|---|---|---|
-| STOP | 0x00 | :109 `handleStop()` | `EVMMirBuilder::handleStop` | evm_mir_compiler.cpp:879 |
-| ADD | 0x01 | :113 `handleBinaryArithmetic<BO_ADD>()` | `EVMMirBuilder::handleBinaryArithmetic<BO_ADD>` | evm_mir_compiler.h:225 (template, inline) |
-| MUL | 0x02 | :117 `handleMul()` | `EVMMirBuilder::handleMul` | evm_mir_compiler.cpp:1301 |
-| SUB | 0x03 | :120 `handleBinaryArithmetic<BO_SUB>()` | `EVMMirBuilder::handleBinaryArithmetic<BO_SUB>` | evm_mir_compiler.h:225 (template, inline) |
-| DIV | 0x04 | :122 `handleDiv()` | `EVMMirBuilder::handleDiv` | evm_mir_compiler.cpp:1400 |
-| SDIV | 0x05 | :125 `handleSDiv()` | `EVMMirBuilder::handleSDiv` | evm_mir_compiler.cpp:1408 |
-| MOD | 0x06 | :128 `handleMod()` | `EVMMirBuilder::handleMod` | evm_mir_compiler.cpp:1416 |
-| SMOD | 0x07 | :131 `handleSMod()` | `EVMMirBuilder::handleSMod` | evm_mir_compiler.cpp:1424 |
-| ADDMOD | 0x08 | :134 `handleAddMod()` | `EVMMirBuilder::handleAddMod` | evm_mir_compiler.cpp:1432 |
-| MULMOD | 0x09 | :137 `handleMulMod()` | `EVMMirBuilder::handleMulMod` | evm_mir_compiler.cpp:1442 |
-| EXP | 0x0A | :140 `handleExp()` | `EVMMirBuilder::handleExp` | evm_mir_compiler.cpp:1450 |
-| SIGNEXTEND | 0x0B | :143 `handleSignextend()` | `EVMMirBuilder::handleSignextend` | evm_mir_compiler.cpp:2348 |
+| EVM Opcode | Hex | Builder Function |
+|---|---|---|
+| STOP | 0x00 | `handleStop` |
+| ADD | 0x01 | `handleBinaryArithmetic<BO_ADD>` |
+| MUL | 0x02 | `handleMul` |
+| SUB | 0x03 | `handleBinaryArithmetic<BO_SUB>` |
+| DIV | 0x04 | `handleDiv` |
+| SDIV | 0x05 | `handleSDiv` |
+| MOD | 0x06 | `handleMod` |
+| SMOD | 0x07 | `handleSMod` |
+| ADDMOD | 0x08 | `handleAddMod` |
+| MULMOD | 0x09 | `handleMulMod` |
+| EXP | 0x0A | `handleExp` |
+| SIGNEXTEND | 0x0B | `handleSignextend` |
 
 ### Comparison
 
-| EVM Opcode | Hex | Visitor Dispatch | Builder Function | Builder Location |
-|---|---|---|---|---|
-| LT | 0x10 | :147 `handleCompare<CO_LT>()` | `handleCompareOp<CO_LT>` -> `handleCompareGT_LT` | .h:311 (template) -> .cpp:1784 |
-| GT | 0x11 | :150 `handleCompare<CO_GT>()` | `handleCompareOp<CO_GT>` -> `handleCompareGT_LT` | .h:311 -> .cpp:1784 |
-| SLT | 0x12 | :153 `handleCompare<CO_LT_S>()` | `handleCompareOp<CO_LT_S>` -> `handleCompareGT_LT` | .h:311 -> .cpp:1784 |
-| SGT | 0x13 | :156 `handleCompare<CO_GT_S>()` | `handleCompareOp<CO_GT_S>` -> `handleCompareGT_LT` | .h:311 -> .cpp:1784 |
-| EQ | 0x14 | :159 `handleCompare<CO_EQ>()` | `handleCompareOp<CO_EQ>` -> `handleCompareEQ` | .h:311 -> .cpp:1752 |
-| ISZERO | 0x15 | :162 `handleCompare<CO_EQZ>()` | `handleCompareOp<CO_EQZ>` -> `handleCompareEQZ` | .h:311 -> .cpp:1720 |
+All six opcodes go through `handleCompareOp<Op>` (template in `.h`) which
+dispatches to one of three concrete handlers in `.cpp`:
+
+| EVM Opcode | Hex | Dispatcher → Concrete handler |
+|---|---|---|
+| LT | 0x10 | `handleCompareOp<CO_LT>` → `handleCompareGT_LT` |
+| GT | 0x11 | `handleCompareOp<CO_GT>` → `handleCompareGT_LT` |
+| SLT | 0x12 | `handleCompareOp<CO_LT_S>` → `handleCompareGT_LT` |
+| SGT | 0x13 | `handleCompareOp<CO_GT_S>` → `handleCompareGT_LT` |
+| EQ | 0x14 | `handleCompareOp<CO_EQ>` → `handleCompareEQ` |
+| ISZERO | 0x15 | `handleCompareOp<CO_EQZ>` → `handleCompareEQZ` |
 
 ### Bitwise
 
-| EVM Opcode | Hex | Visitor Dispatch | Builder Function | Builder Location |
-|---|---|---|---|---|
-| AND | 0x16 | :164 `handleBitwiseOp<BO_AND>()` | `EVMMirBuilder::handleBitwiseOp<BO_AND>` | evm_mir_compiler.h:318 (template, inline) |
-| OR | 0x17 | :167 `handleBitwiseOp<BO_OR>()` | `EVMMirBuilder::handleBitwiseOp<BO_OR>` | evm_mir_compiler.h:318 |
-| XOR | 0x18 | :170 `handleBitwiseOp<BO_XOR>()` | `EVMMirBuilder::handleBitwiseOp<BO_XOR>` | evm_mir_compiler.h:318 |
-| NOT | 0x19 | :174 `handleNot()` | `EVMMirBuilder::handleNot` | evm_mir_compiler.cpp:1856 |
-| BYTE | 0x1A | :177 `handleByte()` | `EVMMirBuilder::handleByte` | evm_mir_compiler.cpp:2273 |
-| SHL | 0x1B | :180 `handleShift<BO_SHL>()` | `handleShift<BO_SHL>` -> `handleLeftShift` | .h:341 -> .cpp:1880 |
-| SHR | 0x1C | :183 `handleShift<BO_SHR_U>()` | `handleShift<BO_SHR_U>` -> `handleLogicalRightShift` | .h:341 -> .cpp:2014 |
-| SAR | 0x1D | :186 `handleShift<BO_SHR_S>()` | `handleShift<BO_SHR_S>` -> `handleArithmeticRightShift` | .h:341 -> .cpp:2142 |
-| CLZ | 0x1E | :189 `handleClz()` | `EVMMirBuilder::handleClz` | evm_mir_compiler.cpp:1873 |
+| EVM Opcode | Hex | Builder Function |
+|---|---|---|
+| AND | 0x16 | `handleBitwiseOp<BO_AND>` |
+| OR | 0x17 | `handleBitwiseOp<BO_OR>` |
+| XOR | 0x18 | `handleBitwiseOp<BO_XOR>` |
+| NOT | 0x19 | `handleNot` |
+| BYTE | 0x1A | `handleByte` |
+| SHL | 0x1B | `handleShift<BO_SHL>` → `handleLeftShift` |
+| SHR | 0x1C | `handleShift<BO_SHR_U>` → `handleLogicalRightShift` |
+| SAR | 0x1D | `handleShift<BO_SHR_S>` → `handleArithmeticRightShift` |
+| CLZ | 0x1E | `handleClz` |
 
 ### Stack
 
-| EVM Opcode | Hex | Visitor Dispatch | Builder Function | Builder Location |
-|---|---|---|---|---|
-| POP | 0x50 | :192 `handlePop()` | (visitor-level only, pops eval stack) | evm_bytecode_visitor.h |
-| PUSH0-32 | 0x5F-0x7F | :195-231 `handlePush(N)` | `EVMMirBuilder::handlePush` | evm_mir_compiler.cpp:1143 |
-| DUP1-16 | 0x80-0x8F | :234-252 `handleDup(N)` | `EVMMirBuilder::stackGet` | evm_mir_compiler.cpp:855 |
-| SWAP1-16 | 0x90-0x9F | :255-273 `handleSwap(N)` | `EVMMirBuilder::stackGet/stackSet` | evm_mir_compiler.cpp:835/855 |
+POP is visitor-level only (pops the eval stack). PUSH/DUP/SWAP route through
+`handlePush` / `stackGet` / `stackSet` in the builder.
 
-### Memory
+| EVM Opcode | Hex | Builder Function |
+|---|---|---|
+| POP | 0x50 | (visitor-level only) |
+| PUSH0-32 | 0x5F-0x7F | `handlePush` |
+| DUP1-16 | 0x80-0x8F | `stackGet` |
+| SWAP1-16 | 0x90-0x9F | `stackGet` / `stackSet` |
 
-| EVM Opcode | Hex | Visitor Dispatch | Builder Function | Builder Location |
-|---|---|---|---|---|
-| MLOAD | 0x51 | :471 | `EVMMirBuilder::handleMLoad` | evm_mir_compiler.cpp:2690 |
-| MSTORE | 0x52 | :478 | `EVMMirBuilder::handleMStore` | evm_mir_compiler.cpp:2734 |
-| MSTORE8 | 0x53 | :485 | `EVMMirBuilder::handleMStore8` | evm_mir_compiler.cpp:2793 |
-| MCOPY | 0x5E | :526 | `EVMMirBuilder::handleMCopy` | evm_mir_compiler.cpp:2838 |
-| MSIZE | 0x59 | :506 | `EVMMirBuilder::handleMSize` | evm_mir_compiler.cpp:2642 |
+### Memory / Storage
 
-### Storage
+These opcodes are called directly from the visitor switch (no `handle*()`
+wrapper) into `Builder.handle*()`.
 
-| EVM Opcode | Hex | Visitor Dispatch | Builder Function | Builder Location |
-|---|---|---|---|---|
-| SLOAD | 0x54 | :492 | `EVMMirBuilder::handleSLoad` | evm_mir_compiler.cpp:3183 |
-| SSTORE | 0x55 | :499 | `EVMMirBuilder::handleSStore` | evm_mir_compiler.cpp:3195 |
-| TLOAD | 0x5C | :512 | `EVMMirBuilder::handleTLoad` | evm_mir_compiler.cpp:3207 |
-| TSTORE | 0x5D | :519 | `EVMMirBuilder::handleTStore` | evm_mir_compiler.cpp:3212 |
+| EVM Opcode | Hex | Builder Function |
+|---|---|---|
+| MLOAD | 0x51 | `handleMLoad` |
+| MSTORE | 0x52 | `handleMStore` |
+| MSTORE8 | 0x53 | `handleMStore8` |
+| MSIZE | 0x59 | `handleMSize` |
+| MCOPY | 0x5E | `handleMCopy` |
+| SLOAD | 0x54 | `handleSLoad` |
+| SSTORE | 0x55 | `handleSStore` |
+| TLOAD | 0x5C | `handleTLoad` |
+| TSTORE | 0x5D | `handleTStore` |
 
 ### Environment
 
-| EVM Opcode | Hex | Builder Function | Builder Location |
-|---|---|---|---|
-| ADDRESS | 0x30 | `handleAddress` | evm_mir_compiler.cpp:2474 |
-| BALANCE | 0x31 | `handleBalance` | evm_mir_compiler.cpp:2479 |
-| ORIGIN | 0x32 | `handleOrigin` | evm_mir_compiler.cpp:2492 |
-| CALLER | 0x33 | `handleCaller` | evm_mir_compiler.cpp:2497 |
-| CALLVALUE | 0x34 | `handleCallValue` | evm_mir_compiler.cpp:2502 |
-| CALLDATALOAD | 0x35 | `handleCallDataLoad` | evm_mir_compiler.cpp:2508 |
-| CALLDATASIZE | 0x36 | `handleCallDataSize` | evm_mir_compiler.cpp:2521 |
-| CALLDATACOPY | 0x37 | `handleCallDataCopy` | evm_mir_compiler.cpp:3933 |
-| CODESIZE | 0x38 | `handleCodeSize` | evm_mir_compiler.cpp:2526 |
-| CODECOPY | 0x39 | `handleCodeCopy` | evm_mir_compiler.cpp:2531 |
-| GASPRICE | 0x3A | `handleGasPrice` | evm_mir_compiler.cpp:2516 |
-| EXTCODESIZE | 0x3B | `handleExtCodeSize` | evm_mir_compiler.cpp:2551 |
-| EXTCODECOPY | 0x3C | `handleExtCodeCopy` | evm_mir_compiler.cpp:3953 |
-| RETURNDATASIZE | 0x3D | `handleReturnDataSize` | evm_mir_compiler.cpp:4000 |
-| RETURNDATACOPY | 0x3E | `handleReturnDataCopy` | evm_mir_compiler.cpp:3977 |
-| EXTCODEHASH | 0x3F | `handleExtCodeHash` | evm_mir_compiler.cpp:2565 |
-| BLOCKHASH | 0x40 | `handleBlockHash` | evm_mir_compiler.cpp:2579 |
-| COINBASE | 0x41 | `handleCoinBase` | evm_mir_compiler.cpp:2587 |
-| TIMESTAMP | 0x42 | `handleTimestamp` | evm_mir_compiler.cpp:2592 |
-| NUMBER | 0x43 | `handleNumber` | evm_mir_compiler.cpp:2597 |
-| PREVRANDAO | 0x44 | `handlePrevRandao` | evm_mir_compiler.cpp:2602 |
-| GASLIMIT | 0x45 | `handleGasLimit` | evm_mir_compiler.cpp:2607 |
-| CHAINID | 0x46 | `handleChainId` | evm_mir_compiler.cpp:2612 |
-| SELFBALANCE | 0x47 | `handleSelfBalance` | evm_mir_compiler.cpp:2617 |
-| BASEFEE | 0x48 | `handleBaseFee` | evm_mir_compiler.cpp:2622 |
-| BLOBHASH | 0x49 | `handleBlobHash` | evm_mir_compiler.cpp:2627 |
-| BLOBBASEFEE | 0x4A | `handleBlobBaseFee` | evm_mir_compiler.cpp:2637 |
-| PC | 0x58 | `handlePC` | evm_mir_compiler.cpp:2457 |
-| GAS | 0x5A | `handleGas` | evm_mir_compiler.cpp:2466 |
+| EVM Opcode | Hex | Builder Function |
+|---|---|---|
+| ADDRESS | 0x30 | `handleAddress` |
+| BALANCE | 0x31 | `handleBalance` |
+| ORIGIN | 0x32 | `handleOrigin` |
+| CALLER | 0x33 | `handleCaller` |
+| CALLVALUE | 0x34 | `handleCallValue` |
+| CALLDATALOAD | 0x35 | `handleCallDataLoad` |
+| CALLDATASIZE | 0x36 | `handleCallDataSize` |
+| CALLDATACOPY | 0x37 | `handleCallDataCopy` |
+| CODESIZE | 0x38 | `handleCodeSize` |
+| CODECOPY | 0x39 | `handleCodeCopy` |
+| GASPRICE | 0x3A | `handleGasPrice` |
+| EXTCODESIZE | 0x3B | `handleExtCodeSize` |
+| EXTCODECOPY | 0x3C | `handleExtCodeCopy` |
+| RETURNDATASIZE | 0x3D | `handleReturnDataSize` |
+| RETURNDATACOPY | 0x3E | `handleReturnDataCopy` |
+| EXTCODEHASH | 0x3F | `handleExtCodeHash` |
+| BLOCKHASH | 0x40 | `handleBlockHash` |
+| COINBASE | 0x41 | `handleCoinBase` |
+| TIMESTAMP | 0x42 | `handleTimestamp` |
+| NUMBER | 0x43 | `handleNumber` |
+| PREVRANDAO | 0x44 | `handlePrevRandao` |
+| GASLIMIT | 0x45 | `handleGasLimit` |
+| CHAINID | 0x46 | `handleChainId` |
+| SELFBALANCE | 0x47 | `handleSelfBalance` |
+| BASEFEE | 0x48 | `handleBaseFee` |
+| BLOBHASH | 0x49 | `handleBlobHash` |
+| BLOBBASEFEE | 0x4A | `handleBlobBaseFee` |
+| PC | 0x58 | `handlePC` |
+| GAS | 0x5A | `handleGas` |
 
 ### Control Flow
 
-| EVM Opcode | Hex | Builder Function | Builder Location |
-|---|---|---|---|
-| JUMP | 0x56 | `handleJump` | evm_mir_compiler.cpp:1150 |
-| JUMPI | 0x57 | `handleJumpI` | evm_mir_compiler.cpp:1185 |
-| JUMPDEST | 0x5B | `handleJumpDest` | evm_mir_compiler.cpp:1255 |
-| Jump table setup | -- | `createJumpTable` | evm_mir_compiler.cpp:956 |
-| Constant jump | -- | `implementConstantJump` | evm_mir_compiler.cpp:1079 |
-| Indirect jump | -- | `implementIndirectJump` | evm_mir_compiler.cpp:1090 |
+| EVM Opcode | Hex | Builder Function |
+|---|---|---|
+| JUMP | 0x56 | `handleJump` |
+| JUMPI | 0x57 | `handleJumpI` |
+| JUMPDEST | 0x5B | `handleJumpDest` |
+| Jump table setup | -- | `createJumpTable` |
+| Constant jump | -- | `implementConstantJump` |
+| Indirect jump | -- | `implementIndirectJump` |
 
 ### Calls and Creates
 
-| EVM Opcode | Hex | Builder Function | Builder Location |
-|---|---|---|---|
-| CREATE | 0xF0 | `handleCreate` | evm_mir_compiler.cpp:2969 |
-| CALL | 0xF1 | `handleCall` | evm_mir_compiler.cpp:3005 |
-| CALLCODE | 0xF2 | `handleCallCode` | evm_mir_compiler.cpp:3032 |
-| RETURN | 0xF3 | `handleReturn` | evm_mir_compiler.cpp:3058 |
-| DELEGATECALL | 0xF4 | `handleDelegateCall` | evm_mir_compiler.cpp:3083 |
-| CREATE2 | 0xF5 | `handleCreate2` | evm_mir_compiler.cpp:2985 |
-| STATICCALL | 0xFA | `handleStaticCall` | evm_mir_compiler.cpp:3109 |
-| REVERT | 0xFD | `handleRevert` | evm_mir_compiler.cpp:3134 |
-| INVALID | 0xFE | `handleInvalid` | evm_mir_compiler.cpp:3157 |
-| SELFDESTRUCT | 0xFF | `handleSelfDestruct` | evm_mir_compiler.cpp:3217 |
+| EVM Opcode | Hex | Builder Function |
+|---|---|---|
+| CREATE | 0xF0 | `handleCreate` |
+| CALL | 0xF1 | `handleCall` |
+| CALLCODE | 0xF2 | `handleCallCode` |
+| RETURN | 0xF3 | `handleReturn` |
+| DELEGATECALL | 0xF4 | `handleDelegateCall` |
+| CREATE2 | 0xF5 | `handleCreate2` |
+| STATICCALL | 0xFA | `handleStaticCall` |
+| REVERT | 0xFD | `handleRevert` |
+| INVALID | 0xFE | `handleInvalid` |
+| SELFDESTRUCT | 0xFF | `handleSelfDestruct` |
 
 ### Other
 
-| EVM Opcode | Hex | Builder Function | Builder Location |
-|---|---|---|---|
-| KECCAK256 | 0x20 | `handleKeccak256` | evm_mir_compiler.cpp:3238 |
-| LOG0-LOG4 | 0xA0-A4 | `handleLogWithTopics<N>` | evm_mir_compiler.cpp:2935 (template) |
+| EVM Opcode | Hex | Builder Function |
+|---|---|---|
+| KECCAK256 | 0x20 | `handleKeccak256` |
+| LOG0-LOG4 | 0xA0-A4 | `handleLogWithTopics<N>` (template) |
 
-### Gas Metering (Injected at chunk boundaries)
+### Gas Metering (injected at chunk boundaries)
 
-| Function | Location |
-|---|---|
-| `EVMMirBuilder::meterOpcode` | evm_mir_compiler.cpp:411 |
-| `EVMMirBuilder::meterOpcodeRange` | evm_mir_compiler.cpp:426 |
-| `EVMMirBuilder::meterGas` | evm_mir_compiler.cpp:489 |
+`EVMMirBuilder::meterOpcode`, `meterOpcodeRange`, `meterGas` — all in
+`evm_mir_compiler.cpp`.
 
 ### x86 Lowering Functions (for reference)
 
-Each dMIR opcode is lowered by `X86CgLowering` in `src/compiler/target/x86/x86lowering.cpp`:
+Most `X86CgLowering::*` definitions live in
+`src/compiler/target/x86/x86lowering.cpp`. A smaller set lives in
+`x86lowering_wasm.cpp` (wasm-specific lowerings) and
+`x86lowering_fallback.cpp` (fallback / slow paths). The generic base
+lives in `src/compiler/cgir/lowering.h`.
 
-| dMIR opcode | x86 Lowering Function | Line |
-|---|---|---|
-| add/sub/mul/and/or/xor | `CgLowering::lowerBinaryOpExpr` (base) -> `fastEmit_rr` | lowering.h (generic) |
-| not | `X86CgLowering::lowerNotExpr` | x86lowering.cpp:23 |
-| sdiv/udiv/srem/urem | `X86CgLowering::lowerDivRemExpr` | x86lowering.cpp:95 |
-| shl/sshr/ushr/rotl/rotr | `X86CgLowering::lowerShiftExpr` | x86lowering.cpp:197 |
-| cmp | `X86CgLowering::lowerCmpExpr` | x86lowering.cpp:858 |
-| adc | `X86CgLowering::lowerAdcExpr` | x86lowering.cpp:906 |
-| evm_umul128_lo | `X86CgLowering::lowerEvmUmul128Expr` | x86lowering.cpp:946 |
-| evm_umul128_hi | `X86CgLowering::lowerEvmUmul128HiExpr` | x86lowering.cpp:991 |
-| select | `X86CgLowering::lowerSelectExpr` | x86lowering.cpp:999 |
-| load | `X86CgLowering::lowerLoadExpr` | x86lowering.cpp:1159 |
-| store | `X86CgLowering::lowerStoreStmt` | x86lowering.cpp:1195 |
-| br | `X86CgLowering::lowerBrStmt` | x86lowering.cpp:1251 |
-| br_if | `X86CgLowering::lowerBrIfStmt` | x86lowering.cpp:1258 |
-| switch | `X86CgLowering::lowerSwitchStmt` | x86lowering.cpp:1291 |
-| call/icall | `X86CgLowering::lowerCall` | x86lowering.cpp:1531 |
-| return | `X86CgLowering::lowerReturnStmt` | x86lowering.cpp:1708 |
-| trunc | `X86CgLowering::lowerIntTruncExpr` | x86lowering.cpp:392 |
-| uext | `X86CgLowering::lowerUExtExpr` | x86lowering.cpp:408 |
-| fpabs | `X86CgLowering::lowerFPAbsExpr` | x86lowering.cpp:33 |
-| fpneg | `X86CgLowering::lowerFPNegExpr` | x86lowering.cpp:51 |
-| fpsqrt | `X86CgLowering::lowerFPSqrtExpr` | x86lowering.cpp:60 |
-| fpround_* | `X86CgLowering::lowerFPRoundExpr` | x86lowering.cpp:67 |
-| fpmin/fpmax | `X86CgLowering::lowerFPMinMaxExpr` | x86lowering.cpp:260 |
-| fpcopysign | `X86CgLowering::lowerFPCopySignExpr` | x86lowering.cpp:360 |
-| sitofp | `X86CgLowering::lowerSIToFPExpr` | x86lowering.cpp:546 |
-| uitofp | `X86CgLowering::lowerUIToFPExpr` | x86lowering.cpp:455 |
-| fpext | `X86CgLowering::lowerFPExtExpr` | x86lowering.cpp:447 |
-| fptrunc | `X86CgLowering::lowerFPTruncExpr` | x86lowering.cpp:451 |
-| dread (variable) | `X86CgLowering::lowerVariable` | x86lowering.cpp:565 |
-| const (int) | `X86CgLowering::X86MaterializeInt` | x86lowering.cpp:585/596 |
-| const (float) | `X86CgLowering::X86MaterializeFP` | x86lowering.cpp:644 |
+| dMIR opcode | x86 Lowering Function |
+|---|---|
+| add/sub/mul/and/or/xor | `CgLowering::lowerBinaryOpExpr` (base in `lowering.h`) → `fastEmit_rr` |
+| not | `X86CgLowering::lowerNotExpr` |
+| sdiv/udiv/srem/urem | `X86CgLowering::lowerDivRemExpr` |
+| shl/sshr/ushr/rotl/rotr | `X86CgLowering::lowerShiftExpr` |
+| cmp | `X86CgLowering::lowerCmpExpr` |
+| adc | `X86CgLowering::lowerAdcExpr` |
+| evm_umul128_lo | `X86CgLowering::lowerEvmUmul128Expr` |
+| evm_umul128_hi | `X86CgLowering::lowerEvmUmul128HiExpr` |
+| select | `X86CgLowering::lowerSelectExpr` |
+| load | `X86CgLowering::lowerLoadExpr` |
+| store | `X86CgLowering::lowerStoreStmt` |
+| br | `X86CgLowering::lowerBrStmt` |
+| br_if | `X86CgLowering::lowerBrIfStmt` |
+| switch | `X86CgLowering::lowerSwitchStmt` |
+| call/icall | `X86CgLowering::lowerCall` |
+| return | `X86CgLowering::lowerReturnStmt` |
+| trunc | `X86CgLowering::lowerIntTruncExpr` |
+| uext | `X86CgLowering::lowerUExtExpr` |
+| fpabs | `X86CgLowering::lowerFPAbsExpr` |
+| fpneg | `X86CgLowering::lowerFPNegExpr` |
+| fpsqrt | `X86CgLowering::lowerFPSqrtExpr` |
+| fpround_* | `X86CgLowering::lowerFPRoundExpr` |
+| fpmin/fpmax | `X86CgLowering::lowerFPMinMaxExpr` |
+| fpcopysign | `X86CgLowering::lowerFPCopySignExpr` |
+| sitofp | `X86CgLowering::lowerSIToFPExpr` |
+| uitofp | `X86CgLowering::lowerUIToFPExpr` |
+| fpext | `X86CgLowering::lowerFPExtExpr` |
+| fptrunc | `X86CgLowering::lowerFPTruncExpr` |
+| dread (variable) | `X86CgLowering::lowerVariable` |
+| const (int) | `X86CgLowering::X86MaterializeInt` |
+| const (float) | `X86CgLowering::X86MaterializeFP` |
 
 ---
 
@@ -548,9 +561,10 @@ store $nth[0..3] to stack[0]
 
 ### POP (0x50)
 
-Handler: `handlePop`
+Handler: `handlePop` (visitor-level only; the builder is not called)
 
-Just decrements the virtual stack pointer. ~2 dMIR instructions.
+The visitor just pops the evaluation stack and returns. Emits 0 dMIR
+instructions.
 
 ---
 
diff --git a/.agents/skills/dtvm-perf-profile/SKILL.md b/.agents/skills/dtvm-perf-profile/SKILL.md
@@ -31,7 +31,8 @@ Check `CMakeCache.txt` for `ZEN_ENABLE_LINUX_PERF:BOOL=ON`. If OFF, reconfigure
 ### 2. Run the profiling script
 
 ```bash
-./scripts/perf_profile.sh --perf ./perf --output-dir perf_results -- \
+.agents/skills/dtvm-perf-profile/scripts/perf_profile.sh \
+  --perf ./perf --output-dir perf_results -- \
   ./build/dtvm -m multipass --format evm --gas-limit 0xFFFFFFFFFFFF \
   <bytecode.hex> \
   --calldata <hex> \
@@ -40,7 +41,9 @@ Check `CMakeCache.txt` for `ZEN_ENABLE_LINUX_PERF:BOOL=ON`. If OFF, reconfigure
   --num-extra-compilations=0 --num-extra-executions=99999
 ```
 
-The script path is relative to this skill: use the absolute path `<repo>/.claude/skills/dtvm-perf-profile/scripts/perf_profile.sh`.
+The script lives under the skill SSOT at
+`<repo>/.agents/skills/dtvm-perf-profile/scripts/perf_profile.sh` — not
+under the `.claude/skills/` mirror.
 
 Key flags for the dtvm command:
 - `--num-extra-executions=N`: More iterations = better sampling of execution (vs compilation). Use 99999+ for meaningful data.
PATCH

echo "Gold patch applied."
