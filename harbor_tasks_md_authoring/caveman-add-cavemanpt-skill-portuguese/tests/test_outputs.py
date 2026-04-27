"""Behavioral checks for caveman-add-cavemanpt-skill-portuguese (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/caveman")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('caveman-pt/SKILL.md')
    assert 'Tirar: artigos (o/a/os/as/um/uma), encheção (simplesmente/basicamente/realmente/na verdade), cortesias (claro/com certeza/com prazer/fico feliz em), muletas. Fragmentos OK. Sinônimos curtos (arrumar n' in text, "expected to find: " + 'Tirar: artigos (o/a/os/as/um/uma), encheção (simplesmente/basicamente/realmente/na verdade), cortesias (claro/com certeza/com prazer/fico feliz em), muletas. Fragmentos OK. Sinônimos curtos (arrumar n'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('caveman-pt/SKILL.md')
    assert 'Largar cavernícola pra: avisos de segurança, confirmações de ações irreversíveis, sequências multi-passo onde fragmentos podem confundir, usuário confuso. Retomar cavernícola depois da parte clara.' in text, "expected to find: " + 'Largar cavernícola pra: avisos de segurança, confirmações de ações irreversíveis, sequências multi-passo onde fragmentos podem confundir, usuário confuso. Retomar cavernícola depois da parte clara.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('caveman-pt/SKILL.md')
    assert '| **ultra** | Abreviar (BD/auth/config/req/res/fn/impl), tirar conjunções, setas pra causalidade (X → Y), uma palavra quando uma palavra basta |' in text, "expected to find: " + '| **ultra** | Abreviar (BD/auth/config/req/res/fn/impl), tirar conjunções, setas pra causalidade (X → Y), uma palavra quando uma palavra basta |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/caveman-pt/SKILL.md')
    assert 'Tirar: artigos (o/a/os/as/um/uma), encheção (simplesmente/basicamente/realmente/na verdade), cortesias (claro/com certeza/com prazer/fico feliz em), muletas. Fragmentos OK. Sinônimos curtos (arrumar n' in text, "expected to find: " + 'Tirar: artigos (o/a/os/as/um/uma), encheção (simplesmente/basicamente/realmente/na verdade), cortesias (claro/com certeza/com prazer/fico feliz em), muletas. Fragmentos OK. Sinônimos curtos (arrumar n'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/caveman-pt/SKILL.md')
    assert 'Largar cavernícola pra: avisos de segurança, confirmações de ações irreversíveis, sequências multi-passo onde fragmentos podem confundir, usuário confuso. Retomar cavernícola depois da parte clara.' in text, "expected to find: " + 'Largar cavernícola pra: avisos de segurança, confirmações de ações irreversíveis, sequências multi-passo onde fragmentos podem confundir, usuário confuso. Retomar cavernícola depois da parte clara.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/caveman-pt/SKILL.md')
    assert '| **ultra** | Abreviar (BD/auth/config/req/res/fn/impl), tirar conjunções, setas pra causalidade (X → Y), uma palavra quando uma palavra basta |' in text, "expected to find: " + '| **ultra** | Abreviar (BD/auth/config/req/res/fn/impl), tirar conjunções, setas pra causalidade (X → Y), uma palavra quando uma palavra basta |'[:80]

