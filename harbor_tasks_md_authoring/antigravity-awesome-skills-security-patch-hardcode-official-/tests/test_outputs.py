"""Behavioral checks for antigravity-awesome-skills-security-patch-hardcode-official- (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skills/x402-express-wrapper/SKILL.md')
    assert '2. **Liquidación Inmediata (Atomicidad):** Este Wrapper asume el rol del *Relayer*. Por tanto, el propio servidor web se encarga de llamar a `M2MCentEscrow.settle()` on-chain. ESTRICTAMENTE se requier' in text, "expected to find: " + '2. **Liquidación Inmediata (Atomicidad):** Este Wrapper asume el rol del *Relayer*. Por tanto, el propio servidor web se encarga de llamar a `M2MCentEscrow.settle()` on-chain. ESTRICTAMENTE se requier'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skills/x402-express-wrapper/SKILL.md')
    assert 'description: Wrapper oficial de M2MCent (Node.js) para inyectar muros de pago x402 en APIs o servidores Model Context Protocol (MCP). Usar al construir nuevos servicios que requieran monetización máqu' in text, "expected to find: " + 'description: Wrapper oficial de M2MCent (Node.js) para inyectar muros de pago x402 en APIs o servidores Model Context Protocol (MCP). Usar al construir nuevos servicios que requieran monetización máqu'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skills/x402-express-wrapper/SKILL.md')
    assert 'Esta skill te enseña cómo integrar rápidamente muros de cobro x402 en aplicaciones y servidores Node.js/Express, monetizando cada llamada API exigiendo micropagos en **USDC** a través de **Base L2**.' in text, "expected to find: " + 'Esta skill te enseña cómo integrar rápidamente muros de cobro x402 en aplicaciones y servidores Node.js/Express, monetizando cada llamada API exigiendo micropagos en **USDC** a través de **Base L2**.'[:80]

