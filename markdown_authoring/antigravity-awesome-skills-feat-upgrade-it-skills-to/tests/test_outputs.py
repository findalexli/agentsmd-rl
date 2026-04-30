"""Behavioral checks for antigravity-awesome-skills-feat-upgrade-it-skills-to (markdown_authoring task).

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
    text = _read('skills/it-manager-hospital/SKILL.md')
    assert '4.  **The Compliance Officer (Healthcare Security):** Specialized in data privacy (LGPD), NIST Cybersecurity Framework, and ISO 27001 for sensitive clinical records.' in text, "expected to find: " + '4.  **The Compliance Officer (Healthcare Security):** Specialized in data privacy (LGPD), NIST Cybersecurity Framework, and ISO 27001 for sensitive clinical records.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-hospital/SKILL.md')
    assert '- **Service Continuity (SRE):** Applying Site Reliability Engineering to ensure zero-downtime in Surgery and ICU infrastructure.' in text, "expected to find: " + '- **Service Continuity (SRE):** Applying Site Reliability Engineering to ensure zero-downtime in Surgery and ICU infrastructure.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-hospital/SKILL.md')
    assert '- **ISO/IEC 27001:** Establishing a Security Management System (ISMS) for Electronic Health Records (EHR).' in text, "expected to find: " + '- **ISO/IEC 27001:** Establishing a Security Management System (ISMS) for Electronic Health Records (EHR).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-pro/SKILL.md')
    assert 'To act as a state-of-the-art specialist for IT Managers, CTOs, and digital leaders. This skill assembles a virtual team of eight elite experts to provide strategic and operational guidance on modern I' in text, "expected to find: " + 'To act as a state-of-the-art specialist for IT Managers, CTOs, and digital leaders. This skill assembles a virtual team of eight elite experts to provide strategic and operational guidance on modern I'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-pro/SKILL.md')
    assert '8.  **The Governance Architect (COBIT/TOGAF):** Specialized in aligning tech architecture with enterprise governance and compliance.' in text, "expected to find: " + '8.  **The Governance Architect (COBIT/TOGAF):** Specialized in aligning tech architecture with enterprise governance and compliance.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-pro/SKILL.md')
    assert '- **Project Choice:** Recommend **PMBOK** for predictable compliance projects and **Agile/Scrum** for innovative/uncertain products.' in text, "expected to find: " + '- **Project Choice:** Recommend **PMBOK** for predictable compliance projects and **Agile/Scrum** for innovative/uncertain products.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-pro/references/it-management-frameworks.md')
    assert '* **COBIT (Control Objectives for Information and Related Technologies):** Focado em governança corporativa de TI. Ajuda a alinhar a tecnologia aos objetivos estratégicos da empresa, gerenciar riscos ' in text, "expected to find: " + '* **COBIT (Control Objectives for Information and Related Technologies):** Focado em governança corporativa de TI. Ajuda a alinhar a tecnologia aos objetivos estratégicos da empresa, gerenciar riscos '[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-pro/references/it-management-frameworks.md')
    assert '* **TOGAF (The Open Group Architecture Framework):** Especializado no design, planejamento e implementação de arquiteturas empresariais para garantir que a fundação tecnológica suporte a escalabilidad' in text, "expected to find: " + '* **TOGAF (The Open Group Architecture Framework):** Especializado no design, planejamento e implementação de arquiteturas empresariais para garantir que a fundação tecnológica suporte a escalabilidad'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-pro/references/it-management-frameworks.md')
    assert '* **ITIL (Information Technology Infrastructure Library):** O padrão mundial para gestão de serviços. Foca no ciclo de vida do serviço, desde a estratégia e desenho até a melhoria contínua (CSI).' in text, "expected to find: " + '* **ITIL (Information Technology Infrastructure Library):** O padrão mundial para gestão de serviços. Foca no ciclo de vida do serviço, desde a estratégia e desenho até a melhoria contínua (CSI).'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/itil-expert/SKILL.md')
    assert '- **Practice Modernization:** Updating the 34 ITIL practices for automated, high-velocity, and cloud-native environments (DevOps/SRE/AIOps).' in text, "expected to find: " + '- **Practice Modernization:** Updating the 34 ITIL practices for automated, high-velocity, and cloud-native environments (DevOps/SRE/AIOps).'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/itil-expert/SKILL.md')
    assert '- **ISO/IEC 20000 Compliance:** Aligning digital product management with international service quality standards.' in text, "expected to find: " + '- **ISO/IEC 20000 Compliance:** Aligning digital product management with international service quality standards.'[:80]

