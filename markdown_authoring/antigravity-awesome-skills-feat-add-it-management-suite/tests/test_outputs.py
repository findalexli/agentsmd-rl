"""Behavioral checks for antigravity-awesome-skills-feat-add-it-management-suite (markdown_authoring task).

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
    text = _read('skills/it-manager-hospital/README.md')
    assert '**it-manager-hospital** is an elite-level skill designed to support IT Managers and CIOs in the complex hospital environment. It bridges the gap between conventional IT governance and the mission-crit' in text, "expected to find: " + '**it-manager-hospital** is an elite-level skill designed to support IT Managers and CIOs in the complex hospital environment. It bridges the gap between conventional IT governance and the mission-crit'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-hospital/README.md')
    assert 'This skill activates a collective of 10 expert personas to analyze every management scenario, from the **Clinical Strategist** to the **Patient Safety Guardian**.' in text, "expected to find: " + 'This skill activates a collective of 10 expert personas to analyze every management scenario, from the **Clinical Strategist** to the **Patient Safety Guardian**.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-hospital/README.md')
    assert 'The skill will provide the core strategic answer and then **ask** if you want to dive deeper into clinical applicability or real-world resolution examples.' in text, "expected to find: " + 'The skill will provide the core strategic answer and then **ask** if you want to dive deeper into clinical applicability or real-world resolution examples.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-hospital/SKILL.md')
    assert 'To act as a high-fidelity advisor for Hospital IT Managers, Digital Health Leaders, and Clinical Engineers. This skill integrates the strategic core of IT Management with the critical constraints of h' in text, "expected to find: " + 'To act as a high-fidelity advisor for Hospital IT Managers, Digital Health Leaders, and Clinical Engineers. This skill integrates the strategic core of IT Management with the critical constraints of h'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-hospital/SKILL.md')
    assert '*   **Protocol:** provide the core answer/solution first. Then, conclude with: *"Would you like deep insights into the clinical applicability of this solution or a real-world resolution example from a' in text, "expected to find: " + '*   **Protocol:** provide the core answer/solution first. Then, conclude with: *"Would you like deep insights into the clinical applicability of this solution or a real-world resolution example from a'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-hospital/SKILL.md')
    assert '**Before providing extended insights, implementation roadmaps, or detailed exam preparation guides (cpTICS, CPHIMS), you MUST ask for user consent.**' in text, "expected to find: " + '**Before providing extended insights, implementation roadmaps, or detailed exam preparation guides (cpTICS, CPHIMS), you MUST ask for user consent.**'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-hospital/examples/hospital-management-scenarios.md')
    assert '- **Question for User:** Would you like deep insights into the clinical applicability of this solution or a real-world resolution example from a Digital Hospital (HIMSS Stage 7)?' in text, "expected to find: " + '- **Question for User:** Would you like deep insights into the clinical applicability of this solution or a real-world resolution example from a Digital Hospital (HIMSS Stage 7)?'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-hospital/examples/hospital-management-scenarios.md')
    assert '- **Focus:** Show how IT is driving "Ciclos de Melhoria" (PDCA) in clinical outcomes (e.g., reducing length of stay via better clinical alerts).' in text, "expected to find: " + '- **Focus:** Show how IT is driving "Ciclos de Melhoria" (PDCA) in clinical outcomes (e.g., reducing length of stay via better clinical alerts).'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-hospital/examples/hospital-management-scenarios.md')
    assert '- **Closure:** Perform a "Technical + Clinical" Post-Mortem to evaluate the impact on patient safety indicators during the downtime.' in text, "expected to find: " + '- **Closure:** Perform a "Technical + Clinical" Post-Mortem to evaluate the impact on patient safety indicators during the downtime.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-hospital/references/his-pep-guide.md')
    assert '- Integration requirements: Authenticating via Gov.br, complying with the "Modelo de Informação" (RAC, Sumário de Alta), and securing data transmission.' in text, "expected to find: " + '- Integration requirements: Authenticating via Gov.br, complying with the "Modelo de Informação" (RAC, Sumário de Alta), and securing data transmission.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-hospital/references/his-pep-guide.md')
    assert '- **FHIR (Fast Healthcare Interoperability Resources):** The modern, RESTful API standard for health data. Essential for HIMSS Stage 7.' in text, "expected to find: " + '- **FHIR (Fast Healthcare Interoperability Resources):** The modern, RESTful API standard for health data. Essential for HIMSS Stage 7.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-hospital/references/his-pep-guide.md')
    assert '- **Key Focus:** Beira-leito (Bedside) automation, clinical pharmacy integration, and strategic faturamento (billing) modules.' in text, "expected to find: " + '- **Key Focus:** Beira-leito (Bedside) automation, clinical pharmacy integration, and strategic faturamento (billing) modules.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-hospital/references/hospital-digital-maturity.md')
    assert '- **Nível 3 (Acreditado com Excelência):** Focus on Excellence. Continuous improvement, management maturity, and cycles of outcomes.' in text, "expected to find: " + '- **Nível 3 (Acreditado com Excelência):** Focus on Excellence. Continuous improvement, management maturity, and cycles of outcomes.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-hospital/references/hospital-digital-maturity.md')
    assert 'To prepare for the cpTICS exam and lead a digital transformation in Brazil, the following bibliography is essential:' in text, "expected to find: " + 'To prepare for the cpTICS exam and lead a digital transformation in Brazil, the following bibliography is essential:'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-hospital/references/hospital-digital-maturity.md')
    assert '- **Stage 7:** Full Interoperability, Advanced Data Analytics (AI), and zero dependency on paper documents.' in text, "expected to find: " + '- **Stage 7:** Full Interoperability, Advanced Data Analytics (AI), and zero dependency on paper documents.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-pro/README.md')
    assert '**IT Manager Pro** is a high-fidelity advisory skill designed for the 2026 digital landscape. It provides a multi-expert perspective on the most critical pillars of modern technology leadership:' in text, "expected to find: " + '**IT Manager Pro** is a high-fidelity advisory skill designed for the 2026 digital landscape. It provides a multi-expert perspective on the most critical pillars of modern technology leadership:'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-pro/README.md')
    assert 'To keep responses concise and high-value, the skill will provide a core answer first and then **ask** if you want deep insights or real-world applicability examples.' in text, "expected to find: " + 'To keep responses concise and high-value, the skill will provide a core answer first and then **ask** if you want deep insights or real-world applicability examples.'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-pro/README.md')
    assert '- **Data-Driven Governance:** Algorithmic ethics, sustainability (ESG), and continuous improvement.' in text, "expected to find: " + '- **Data-Driven Governance:** Algorithmic ethics, sustainability (ESG), and continuous improvement.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-pro/SKILL.md')
    assert 'To act as a state-of-the-art specialist for IT Managers, CTOs, and digital leaders. This skill assembles a virtual team of seven elite experts to provide strategic and operational guidance on modern I' in text, "expected to find: " + 'To act as a state-of-the-art specialist for IT Managers, CTOs, and digital leaders. This skill assembles a virtual team of seven elite experts to provide strategic and operational guidance on modern I'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-pro/SKILL.md')
    assert '*   **Protocol:** Provide the core answer/solution first. Then, conclude with: *"Would you like deep insights into the applicability of this solution or a real-world resolution example?"*' in text, "expected to find: " + '*   **Protocol:** Provide the core answer/solution first. Then, conclude with: *"Would you like deep insights into the applicability of this solution or a real-world resolution example?"*'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-pro/SKILL.md')
    assert 'description: Elite IT Management Advisor specializing in data-driven strategy, executive communication, and human-centric leadership for the 2026 digital era.' in text, "expected to find: " + 'description: Elite IT Management Advisor specializing in data-driven strategy, executive communication, and human-centric leadership for the 2026 digital era.'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-pro/examples/management-scenarios.md')
    assert '- **Action:** Initiate a "War Room," but strictly appoint a "Communication Czar" (The Liaison) to mirror the technical technical progress into a business status format.' in text, "expected to find: " + '- **Action:** Initiate a "War Room," but strictly appoint a "Communication Czar" (The Liaison) to mirror the technical technical progress into a business status format.'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-pro/examples/management-scenarios.md')
    assert '- **Question for User:** Would you like deep insights into the applicability of this solution or a real-world resolution example?' in text, "expected to find: " + '- **Question for User:** Would you like deep insights into the applicability of this solution or a real-world resolution example?'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-pro/examples/management-scenarios.md')
    assert '- Present a "De-risking Plan" (Migration or Alternative Vendor analysis) to the board to strengthen your negotiation leverage.' in text, "expected to find: " + '- Present a "De-risking Plan" (Migration or Alternative Vendor analysis) to the board to strengthen your negotiation leverage.'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-pro/references/it-manager-handbook.md')
    assert '- **Psychological Safety:** The foundation of high-performance engineering teams. Encourage blameless post-mortems and celebrate "smart failures."' in text, "expected to find: " + '- **Psychological Safety:** The foundation of high-performance engineering teams. Encourage blameless post-mortems and celebrate "smart failures."'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-pro/references/it-manager-handbook.md')
    assert '- **Waste Identification:** Historically, 30% of cloud spend is waste. Use AI-driven right-sizing and spot-instance automation.' in text, "expected to find: " + '- **Waste Identification:** Historically, 30% of cloud spend is waste. Use AI-driven right-sizing and spot-instance automation.'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/it-manager-pro/references/it-manager-handbook.md')
    assert '- **Security:** Managing the broad attack surface of LLM integrations and retrieval-augmented generation (RAG) systems.' in text, "expected to find: " + '- **Security:** Managing the broad attack surface of LLM integrations and retrieval-augmented generation (RAG) systems.'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/itil-expert/README.md')
    assert 'The **ITIL Expert** skill provides a deep-dive advisory experience for implementing **ITIL 4** and the latest **ITIL 5** standards. It bridges the gap between traditional service management and the ne' in text, "expected to find: " + 'The **ITIL Expert** skill provides a deep-dive advisory experience for implementing **ITIL 4** and the latest **ITIL 5** standards. It bridges the gap between traditional service management and the ne'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/itil-expert/README.md')
    assert 'A specialized AI skill for IT professionals, Service Managers, and Product Owners to navigate the complexities of modern ITIL frameworks.' in text, "expected to find: " + 'A specialized AI skill for IT professionals, Service Managers, and Product Owners to navigate the complexities of modern ITIL frameworks.'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/itil-expert/README.md')
    assert '- **Strategic Guidance:** Transition your organization from Service Value Systems (ITIL 4) to Digital Product Lifecycles (ITIL 5).' in text, "expected to find: " + '- **Strategic Guidance:** Transition your organization from Service Value Systems (ITIL 4) to Digital Product Lifecycles (ITIL 5).'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/itil-expert/SKILL.md')
    assert "To act as a premier consultant for ITIL 4 and the newly released ITIL 5 frameworks. This skill provides authoritative strategic and operational guidance on evolving ITIL 4's Service Value System into " in text, "expected to find: " + "To act as a premier consultant for ITIL 4 and the newly released ITIL 5 frameworks. This skill provides authoritative strategic and operational guidance on evolving ITIL 4's Service Value System into "[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/itil-expert/SKILL.md')
    assert '- **Service Configuration Management:** Moving to **Immutable Infrastructure** where changes are never made to a running system; instead, a new "Product Version" is deployed.' in text, "expected to find: " + '- **Service Configuration Management:** Moving to **Immutable Infrastructure** where changes are never made to a running system; instead, a new "Product Version" is deployed.'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/itil-expert/SKILL.md')
    assert "- **Focus on Value (with AI):** AI shouldn't just exist; it must directly contribute to the user's value realization. If the AI doesn't improve the outcome, it is waste." in text, "expected to find: " + "- **Focus on Value (with AI):** AI shouldn't just exist; it must directly contribute to the user's value realization. If the AI doesn't improve the outcome, it is waste."[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/itil-expert/examples/itil-usage.md')
    assert "- **HITL Requirement:** ITIL 5 mandates that high-risk changes (Categories A/B) require a human reviewer to validate the AI's recommendation." in text, "expected to find: " + "- **HITL Requirement:** ITIL 5 mandates that high-risk changes (Categories A/B) require a human reviewer to validate the AI's recommendation."[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/itil-expert/examples/itil-usage.md')
    assert '- **SLA Update:** Add a clause: "The service shall target 99.9% uptime with a maximum carbon intensity of X kg CO2 per user transaction."' in text, "expected to find: " + '- **SLA Update:** Add a clause: "The service shall target 99.9% uptime with a maximum carbon intensity of X kg CO2 per user transaction."'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/itil-expert/examples/itil-usage.md')
    assert '5. **Improve:** Incident data is fed back into the AI model to prevent future occurrences (Predictive Problem Management).' in text, "expected to find: " + '5. **Improve:** Incident data is fed back into the AI model to prevent future occurrences (Predictive Problem Management).'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/itil-expert/references/itil-5-evolution.md')
    assert '**Digital Product & Service Management (DPSM)** is the core of ITIL 5. While ITIL 4 introduced the Service Value System (SVS), ITIL 5 integrates the "Product" mindset as the primary unit of value.' in text, "expected to find: " + '**Digital Product & Service Management (DPSM)** is the core of ITIL 5. While ITIL 4 introduced the Service Value System (SVS), ITIL 5 integrates the "Product" mindset as the primary unit of value.'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/itil-expert/references/itil-5-evolution.md')
    assert '- **Governance of Algorithms:** A new practice dedicated to ensuring AI models used in services are ethical, transparent, and compliant with regional data laws (GDPR, etc.).' in text, "expected to find: " + '- **Governance of Algorithms:** A new practice dedicated to ensuring AI models used in services are ethical, transparent, and compliant with regional data laws (GDPR, etc.).'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/itil-expert/references/itil-5-evolution.md')
    assert '- **Continuous Co-creation:** Value is not created by the provider and consumed by the user; it is continuously co-created through interactive digital touchpoints.' in text, "expected to find: " + '- **Continuous Co-creation:** Value is not created by the provider and consumed by the user; it is continuously co-created through interactive digital touchpoints.'[:80]

