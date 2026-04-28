"""Behavioral checks for constantine-add-common-agent-skills-peerdas (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/constantine")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/debugging/SKILL.md')
    assert 'Use the `toHex()` functions for quick inspection of cryptographic values. **You must import the corresponding IO module**:' in text, "expected to find: " + 'Use the `toHex()` functions for quick inspection of cryptographic values. **You must import the corresponding IO module**:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/debugging/SKILL.md')
    assert 'Code guarded by `debug:` from `constantine/platforms/primitives.nim` is only compiled when `-d:CTT_DEBUG` is defined:' in text, "expected to find: " + 'Code guarded by `debug:` from `constantine/platforms/primitives.nim` is only compiled when `-d:CTT_DEBUG` is defined:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/debugging/SKILL.md')
    assert 'In release mode, code is optimized and stack traces may be incomplete. Use `-d:linetrace` for full stack traces:' in text, "expected to find: " + 'In release mode, code is optimized and stack traces may be incomplete. Use `-d:linetrace` for full stack traces:'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/performance-investigation/SKILL.md')
    assert 'description: Profile and identify performance bottlenecks in Constantine cryptographic code using metering and benchmarking tools' in text, "expected to find: " + 'description: Profile and identify performance bottlenecks in Constantine cryptographic code using metering and benchmarking tools'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/performance-investigation/SKILL.md')
    assert '- **Metering overhead**: Metering adds ~10-20% overhead; use for relative comparison, not absolute timing' in text, "expected to find: " + '- **Metering overhead**: Metering adds ~10-20% overhead; use for relative comparison, not absolute timing'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/performance-investigation/SKILL.md')
    assert 'Help identify and analyze performance bottlenecks in Constantine cryptographic implementations through:' in text, "expected to find: " + 'Help identify and analyze performance bottlenecks in Constantine cryptographic implementations through:'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/seq-arrays-openarrays-slicing-views/SKILL.md')
    assert 'When memory allocation is necessary, for example for multithreading, GPU computing or succinct or zero-knowledge proof protocol, we use custom allocators from `constantine/platforms/allocs.nim`. Those' in text, "expected to find: " + 'When memory allocation is necessary, for example for multithreading, GPU computing or succinct or zero-knowledge proof protocol, we use custom allocators from `constantine/platforms/allocs.nim`. Those'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/seq-arrays-openarrays-slicing-views/SKILL.md')
    assert 'Avoid Nim slicing syntax `..<` slice syntax on arrays, sequences and openarrays as it creates an intermediate seq, which:' in text, "expected to find: " + 'Avoid Nim slicing syntax `..<` slice syntax on arrays, sequences and openarrays as it creates an intermediate seq, which:'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/seq-arrays-openarrays-slicing-views/SKILL.md')
    assert "Emphasizes avoiding `seq` in favor of auditable memory management through Constantine's shim over the system allocator." in text, "expected to find: " + "Emphasizes avoiding `seq` in favor of auditable memory management through Constantine's shim over the system allocator."[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/serialization-hex-debugging/SKILL.md')
    assert 'func serializeBatchUncompressed_vartime*(dst: ptr UncheckedArray[array[64, byte]], points: ptr UncheckedArray[EC_TwEdw_Prj[Fp[Banderwagon]]], N: int): CttCodecEccStatus' in text, "expected to find: " + 'func serializeBatchUncompressed_vartime*(dst: ptr UncheckedArray[array[64, byte]], points: ptr UncheckedArray[EC_TwEdw_Prj[Fp[Banderwagon]]], N: int): CttCodecEccStatus'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/serialization-hex-debugging/SKILL.md')
    assert 'func serializeBatch_vartime*(dst: ptr UncheckedArray[array[32, byte]], points: ptr UncheckedArray[EC_TwEdw_Prj[Fp[Banderwagon]]], N: int): CttCodecEccStatus' in text, "expected to find: " + 'func serializeBatch_vartime*(dst: ptr UncheckedArray[array[32, byte]], points: ptr UncheckedArray[EC_TwEdw_Prj[Fp[Banderwagon]]], N: int): CttCodecEccStatus'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/serialization-hex-debugging/SKILL.md')
    assert 'func serialize_scalar*(dst: var array[32, byte], scalar: Fr[Banderwagon].getBigInt(), order: static Endianness = bigEndian): CttCodecScalarStatus' in text, "expected to find: " + 'func serialize_scalar*(dst: var array[32, byte], scalar: Fr[Banderwagon].getBigInt(), order: static Endianness = bigEndian): CttCodecScalarStatus'[:80]

