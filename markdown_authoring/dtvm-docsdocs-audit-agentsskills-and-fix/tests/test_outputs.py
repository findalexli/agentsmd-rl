"""Behavioral checks for dtvm-docsdocs-audit-agentsskills-and-fix (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dtvm")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/archive/SKILL.md')
    assert '3. Add a row to the "Current Entries" table in `docs/_archive/README.md`' in text, "expected to find: " + '3. Add a row to the "Current Entries" table in `docs/_archive/README.md`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/archive/SKILL.md')
    assert 'Branch and worktree cleanup are out of scope for this skill — leave them' in text, "expected to find: " + 'Branch and worktree cleanup are out of scope for this skill — leave them'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/archive/SKILL.md')
    assert 'to the user.' in text, "expected to find: " + 'to the user.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/dev-workflow/SKILL.md')
    assert '.agents/skills/dev-workflow/SKILL.md' in text, "expected to find: " + '.agents/skills/dev-workflow/SKILL.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/dmir-compiler-analysis/SKILL.md')
    assert '- **EVM-specific**: `evm_umul128_lo` (64×64→64, low half) and `evm_umul128_hi` (extracts the high half from the preceding `evm_umul128_lo`); `evm_u256_mul` (256×256→256 pseudo-op) and `evm_u256_mul_re' in text, "expected to find: " + '- **EVM-specific**: `evm_umul128_lo` (64×64→64, low half) and `evm_umul128_hi` (extracts the high half from the preceding `evm_umul128_lo`); `evm_u256_mul` (256×256→256 pseudo-op) and `evm_u256_mul_re'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/dmir-compiler-analysis/SKILL.md')
    assert 'Condition codes (`src/compiler/mir/cond_codes.def`): `ieq`, `ine`, `iugt`, `iuge`, `iult`, `iule`, `isgt`, `isge`, `islt`, `isle` (integer); `ffalse`, `foeq`, `fogt`, `foge`, `folt`, `fole`, `fone`, `' in text, "expected to find: " + 'Condition codes (`src/compiler/mir/cond_codes.def`): `ieq`, `ine`, `iugt`, `iuge`, `iult`, `iule`, `isgt`, `isge`, `islt`, `isle` (integer); `ffalse`, `foeq`, `fogt`, `foge`, `folt`, `fole`, `fone`, `'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/dmir-compiler-analysis/SKILL.md')
    assert '- **Other exprs**: `phi`, `dread`, `const`, `cmp`, `adc`, `sbb`, `select`, `load`, `wasm_sadd128_overflow`, `wasm_uadd128_overflow`, `wasm_ssub128_overflow`, `wasm_usub128_overflow`' in text, "expected to find: " + '- **Other exprs**: `phi`, `dread`, `const`, `cmp`, `adc`, `sbb`, `select`, `load`, `wasm_sadd128_overflow`, `wasm_uadd128_overflow`, `wasm_ssub128_overflow`, `wasm_usub128_overflow`'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/dmir-compiler-analysis/cost-model.md')
    assert 'Source: `isRAExpensiveOpcode()` in `src/compiler/evm_frontend/evm_analyzer.h`.' in text, "expected to find: " + 'Source: `isRAExpensiveOpcode()` in `src/compiler/evm_frontend/evm_analyzer.h`.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/dmir-compiler-analysis/cost-model.md')
    assert 'from this heuristic: its `evm_umul128_*` schoolbook pattern does not generate' in text, "expected to find: " + 'from this heuristic: its `evm_umul128_*` schoolbook pattern does not generate'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/dmir-compiler-analysis/cost-model.md')
    assert 'MUL (0x02) has a heavy partial-product fan-out (~80 dMIR) but is excluded' in text, "expected to find: " + 'MUL (0x02) has a heavy partial-product fan-out (~80 dMIR) but is excluded'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/dmir-compiler-analysis/evm-to-dmir.md')
    assert '| add/sub/mul/and/or/xor | `CgLowering::lowerBinaryOpExpr` (base in `lowering.h`) → `fastEmit_rr` |' in text, "expected to find: " + '| add/sub/mul/and/or/xor | `CgLowering::lowerBinaryOpExpr` (base in `lowering.h`) → `fastEmit_rr` |'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/dmir-compiler-analysis/evm-to-dmir.md')
    assert '- Non-template handlers live in `src/compiler/evm_frontend/evm_mir_compiler.cpp`.' in text, "expected to find: " + '- Non-template handlers live in `src/compiler/evm_frontend/evm_mir_compiler.cpp`.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/dmir-compiler-analysis/evm-to-dmir.md')
    assert '`src/action/evm_bytecode_visitor.h` (a big `switch` over `evmc_opcode`). Each' in text, "expected to find: " + '`src/action/evm_bytecode_visitor.h` (a big `switch` over `evmc_opcode`). Each'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/dtvm-perf-profile/SKILL.md')
    assert '`<repo>/.agents/skills/dtvm-perf-profile/scripts/perf_profile.sh` — not' in text, "expected to find: " + '`<repo>/.agents/skills/dtvm-perf-profile/scripts/perf_profile.sh` — not'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/dtvm-perf-profile/SKILL.md')
    assert '.agents/skills/dtvm-perf-profile/scripts/perf_profile.sh \\' in text, "expected to find: " + '.agents/skills/dtvm-perf-profile/scripts/perf_profile.sh \\'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/dtvm-perf-profile/SKILL.md')
    assert '--perf ./perf --output-dir perf_results -- \\' in text, "expected to find: " + '--perf ./perf --output-dir perf_results -- \\'[:80]

