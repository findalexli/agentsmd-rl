"""Behavioral checks for kalfa-create-skillmd-for-deep-research (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kalfa")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/academic-paper-reviewer/SKILL.md')
    assert 'Uluslararası bir derginin tam akran denetimi (peer review) sürecini simüle eder: Makalenin alanını otomatik olarak tanımlar, 5 hakemi (Genel Yayın Yönetmeni + 3 Hakem + Şeytanın Avukatı) dinamik olara' in text, "expected to find: " + 'Uluslararası bir derginin tam akran denetimi (peer review) sürecini simüle eder: Makalenin alanını otomatik olarak tanımlar, 5 hakemi (Genel Yayın Yönetmeni + 3 Hakem + Şeytanın Avukatı) dinamik olara'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/academic-paper-reviewer/SKILL.md')
    assert 'Makalenin dilini takip eder. Akademik terimler global standartlar gereği İngilizce kalabilir. Kullanıcı aksini belirtirse (Örn: "Türkçe makaleyi İngilizce incele") ona uyum sağlar.' in text, "expected to find: " + 'Makalenin dilini takip eder. Akademik terimler global standartlar gereği İngilizce kalabilir. Kullanıcı aksini belirtirse (Örn: "Türkçe makaleyi İngilizce incele") ona uyum sağlar.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/academic-paper-reviewer/SKILL.md')
    assert '* Karar "Revizyon" ise tetiklenir. EIC, yazarı "En önemli 3 sorunu nasıl çözerdin?" gibi sorularla yönlendirerek revizyon stratejisini geliştirmesine yardımcı olur.' in text, "expected to find: " + '* Karar "Revizyon" ise tetiklenir. EIC, yazarı "En önemli 3 sorunu nasıl çözerdin?" gibi sorularla yönlendirerek revizyon stratejisini geliştirmesine yardımcı olur.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/deep-research/SKILL.md')
    assert 'Temel ilke: Q1 uluslararası dergi genel yayın yönetmeni perspektifinden, Sokratik sorgulama yoluyla kullanıcıların araştırma sorularını netleştirmelerine rehberlik edin. Asla doğrudan cevap vermeyin; ' in text, "expected to find: " + 'Temel ilke: Q1 uluslararası dergi genel yayın yönetmeni perspektifinden, Sokratik sorgulama yoluyla kullanıcıların araştırma sorularını netleştirmelerine rehberlik edin. Asla doğrudan cevap vermeyin; '[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/deep-research/SKILL.md')
    assert 'Evrensel derin araştırma aracı — herhangi bir konuda titiz akademik araştırma için alana bağlı olmayan 13 ajanlı bir ekip. v2.3; sistematik inceleme modunu (isteğe bağlı meta-analiz ile PRISMA uyumlu)' in text, "expected to find: " + 'Evrensel derin araştırma aracı — herhangi bir konuda titiz akademik araştırma için alana bağlı olmayan 13 ajanlı bir ekip. v2.3; sistematik inceleme modunu (isteğe bağlı meta-analiz ile PRISMA uyumlu)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/deep-research/SKILL.md')
    assert '**Türkçe**: araştırma, derin araştırma, literatür taraması, sistematik inceleme, meta-analiz, PRISMA, kanıt sentezi, doğruluk kontrolü, metodoloji, APA raporu, akademik analiz, politika analizi, araşt' in text, "expected to find: " + '**Türkçe**: araştırma, derin araştırma, literatür taraması, sistematik inceleme, meta-analiz, PRISMA, kanıt sentezi, doğruluk kontrolü, metodoloji, APA raporu, akademik analiz, politika analizi, araşt'[:80]

