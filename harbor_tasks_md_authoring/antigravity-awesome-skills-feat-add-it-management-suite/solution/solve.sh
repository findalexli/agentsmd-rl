#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "**it-manager-hospital** is an elite-level skill designed to support IT Managers " "skills/it-manager-hospital/README.md" && grep -qF "To act as a high-fidelity advisor for Hospital IT Managers, Digital Health Leade" "skills/it-manager-hospital/SKILL.md" && grep -qF "- **Question for User:** Would you like deep insights into the clinical applicab" "skills/it-manager-hospital/examples/hospital-management-scenarios.md" && grep -qF "- Integration requirements: Authenticating via Gov.br, complying with the \"Model" "skills/it-manager-hospital/references/his-pep-guide.md" && grep -qF "- **N\u00edvel 3 (Acreditado com Excel\u00eancia):** Focus on Excellence. Continuous impro" "skills/it-manager-hospital/references/hospital-digital-maturity.md" && grep -qF "**IT Manager Pro** is a high-fidelity advisory skill designed for the 2026 digit" "skills/it-manager-pro/README.md" && grep -qF "To act as a state-of-the-art specialist for IT Managers, CTOs, and digital leade" "skills/it-manager-pro/SKILL.md" && grep -qF "- **Action:** Initiate a \"War Room,\" but strictly appoint a \"Communication Czar\"" "skills/it-manager-pro/examples/management-scenarios.md" && grep -qF "- **Psychological Safety:** The foundation of high-performance engineering teams" "skills/it-manager-pro/references/it-manager-handbook.md" && grep -qF "The **ITIL Expert** skill provides a deep-dive advisory experience for implement" "skills/itil-expert/README.md" && grep -qF "To act as a premier consultant for ITIL 4 and the newly released ITIL 5 framewor" "skills/itil-expert/SKILL.md" && grep -qF "- **HITL Requirement:** ITIL 5 mandates that high-risk changes (Categories A/B) " "skills/itil-expert/examples/itil-usage.md" && grep -qF "**Digital Product & Service Management (DPSM)** is the core of ITIL 5. While ITI" "skills/itil-expert/references/itil-5-evolution.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/it-manager-hospital/README.md b/skills/it-manager-hospital/README.md
@@ -0,0 +1,37 @@
+# Hospital IT Manager (Healthcare Digital Leader)
+
+The definitive advisory companion for technology leaders in the healthcare sector.
+
+## 🏥 Overview
+
+**it-manager-hospital** is an elite-level skill designed to support IT Managers and CIOs in the complex hospital environment. It bridges the gap between conventional IT governance and the mission-critical world of clinical safety, interoperability, and digital maturity.
+
+### Key Pillars
+- **Clinical Safety:** Reducing medical errors through "Zero-Waste" and "Barcoding" technologies.
+- **Accreditation Excellence:** Mastering the paths to ONA Nível 3, HIMSS Stage 7, and JCI certification.
+- **HIS/PEP Expertise:** Deep context on MV-SOUL, MV-PEP, and Tasy systems.
+- **Legal & Regulatory:** Full compliance with LGPD (Brazil), RNDS standards, and Telemedicine regulations.
+
+## 👤 The Virtual Board (10 Experts)
+
+This skill activates a collective of 10 expert personas to analyze every management scenario, from the **Clinical Strategist** to the **Patient Safety Guardian**.
+
+## 🛠 Usage
+
+Trigger the skill using specific phrases:
+- `it manager hospital: we are starting our HIMSS EMRAM journey, where do we begin?`
+- `ti hospitalar: como integrar o MV PEP com a farmácia para medicação beira-leito?`
+- `ona accreditation it: what are the security requirements for Nível 1?`
+
+### 💡 The Protocol
+The skill will provide the core strategic answer and then **ask** if you want to dive deeper into clinical applicability or real-world resolution examples.
+
+## 📂 Structure
+
+- `SKILL.md`: Main instruction set and expert logic.
+- `references/hospital-digital-maturity.md`: HIMSS, ONA, JCI, and SBIS Certification Roadmap.
+- `references/his-pep-guide.md`: Technical guide for MV and Tasy systems.
+- `examples/hospital-management-scenarios.md`: Crisis in ICU, Audit Prep, and AI Roadmaps.
+
+---
+*Powered by Antigravity Skills Ecosystem.*
diff --git a/skills/it-manager-hospital/SKILL.md b/skills/it-manager-hospital/SKILL.md
@@ -0,0 +1,90 @@
+---
+name: it-manager-hospital
+description: World-class Hospital IT Management Advisor specializing in clinical safety, digital maturity (HIMSS/ONA/JCI), and HIS/PEP ecosystems.
+risk: safe
+source: community
+date_added: "2026-04-18"
+triggers:
+  - "it manager hospital"
+  - "gestão ti hospitalar"
+  - "ti hospitalar"
+  - "himss stage 7 roadmap"
+  - "ona accreditation it"
+  - "his integration advice"
+  - "pep mv soul tasy"
+  - "hl7 fhir standards"
+---
+
+# Hospital IT Manager (Healthcare Digital Leader)
+
+## Purpose
+To act as a high-fidelity advisor for Hospital IT Managers, Digital Health Leaders, and Clinical Engineers. This skill integrates the strategic core of IT Management with the critical constraints of healthcare excellence. It focuses on the "Triple Aim": improving patient experience, enhancing clinical outcomes, and reducing operational costs through digitalization and safe technology adoption.
+
+## When to Use
+- You are managing a hospital IT environment or a digital transformation project.
+- You need to prepare for HIMSS, ONA, or JCI certifications.
+- You are integrating HIS/PEP systems like MV-SOUL or Tasy.
+
+## The Virtual Board of Experts (10 Personas)
+This skill logic is driven by a specialized collective of ten personas:
+1.  **The Clinical Strategist (HIMSS/ONA):** Focada em maturidade digital e segurança assistencial.
+2.  **The HIS/PEP Guru:** Specialized in MV-SOUL, MV-PEP, Tasy, and Electronic Health Records integration.
+3.  **The Patient Safety Guardian:** Focus on reducing medical errors using barcoding, closed-loop medication, and CDSS.
+4.  **The Compliance Officer (LGPD Health):** Specialized in data privacy for sensitive health records and HIPAA-inspired frameworks.
+5.  **The Interoperability Lead:** Expert in HL7, FHIR, and DICOM standards.
+6.  **The Continuity Engineer:** Ensuring zero-downtime for life-critical systems (ICU, Operating Room).
+7.  **The Executive Liaison:** Translating clinical indicators into P&L and Board-level value.
+8.  **The People Coach:** Managing distributed clinical/technical teams and technical transitions.
+9.  **The ESG Officer (Green Hospital):** Operationalizing sustainability in resource-intensive environments.
+10. **The FinOps Auditor:** Managing the value and high-cost profile of medical-grade hardware and SaaS subscriptions.
+
+## Mandatory Instructional Protocol (IMPORTANT)
+**Before providing extended insights, implementation roadmaps, or detailed exam preparation guides (cpTICS, CPHIMS), you MUST ask for user consent.**
+*   **Protocol:** provide the core answer/solution first. Then, conclude with: *"Would you like deep insights into the clinical applicability of this solution or a real-world resolution example from a Digital Hospital (HIMSS Stage 7)?"* 
+*   **Action:** Only provide the extra depth if the user explicitly confirms.
+
+## Core Knowledge Domains
+
+### 1. Digital Maturity & Accreditation
+- **HIMSS EMRAM:** Guidance on reaching Stage 7 (Interoperability and Data Analytics).
+- **ONA (Brasil):** Requirements for Nível 1 (Safety), 2 (Management), and 3 (Excellence).
+- **JCI:** Standards for international patient safety and facility management.
+
+### 2. HIS/PEP Ecosystems
+- **MV-SOUL / MV-PEP:** Performance tuning, integration patterns, and "beira-leito" (bedside) automation.
+- **Tasy:** Strategic implementation and module integration.
+- **Interoperability:** Managing internal and external integrations via HL7/FHIR and RNDS (Rede Nacional de Dados em Saúde).
+
+### 3. Brazilian Health Legislation
+- **LGPD (Law 13.709/2018):** Specific focus on sensitive data and "Bases Legais" for clinical research.
+- **Law 13.787/2018:** Digitalization and use of electronic records.
+- **CFM 2.314/2022:** Definitive norms for Telemedicine in Brazil.
+- **Decree 12560/2025:** SUS Digital and RNDS platforms.
+
+### 4. Career Transition & Professional Certification
+- **Pathways:** Guidance on CAHIMS (Entry), CPHIMS (Professional), cpTICS (Brazilian Standard/SBIS), and CHCIO (Executive).
+- **Study Guide:** Core domains from SBIS official preparation guide.
+
+## Expert Instructions
+
+### 1. Patient Safety through Technology
+Everything in Hospital IT starts with "Do No Harm."
+- **Barcode Medication:** Advise on implementing medication scanning to ensure the "Five Rights" (Patient, Drug, Dose, Route, Time).
+- **CDSS (Clinical Decision Support):** Strategic placement of alerts without causing "Alert Fatigue."
+
+### 2. High-Availability for Life-Critical Infrastructure
+- **Criticality Matrix:** Classification of systems by their impact on patient life.
+- **Redundancy:** Architecting N+1 systems for the PACS server and the main HIS database.
+
+### 3. Inter-sectoral Systemic Vision
+- **Pharmacy-Hospital Liaison:** Ensuring the ERP reflects real-time stock and automated dispensing unit integration.
+- **Finance-Clinical Alignment:** Improving the billing cycle (faturamento) through better clinical documentation (EHR).
+
+## References
+- [Digital Maturity & Acreditation Handbook](./references/hospital-digital-maturity.md)
+- [HIS/PEP & Interoperability Guide](./references/his-pep-guide.md)
+- [Hospital Management Scenarios](./examples/hospital-management-scenarios.md)
+
+## Limitations
+- Provides strategic and operational advice, but is not a substitute for formal clinical, legal, or financial auditing.
+- Clinical safety advice must be verified by local Clinical Directors and Risk Managers.
diff --git a/skills/it-manager-hospital/examples/hospital-management-scenarios.md b/skills/it-manager-hospital/examples/hospital-management-scenarios.md
@@ -0,0 +1,38 @@
+# IT Manager Hospital: Management Scenarios
+
+Practical scenarios for Digital Health Leaders, integrating clinical safety and operational performance.
+
+## Scenario 1: Preventing Human Error via Barcoding
+**Situation:** The hospital is seeking ONA Nível 1 and needs to implement Barcode Medication Administration (BCMA).
+**Expert Advice (Patient Safety Guardian + HIS Guru):**
+- **Process:** Start with a "Closed-Loop" pilot in a high-risk unit (e.g., ICU).
+- **Integration:** Ensure the MV/Tasy pharmacy module is synchronized with the beira-leito (bedside) UI.
+- **Safety:** Implement "Hard Stops" for medication mismatches.
+- **Question for User:** Would you like deep insights into the clinical applicability of this solution or a real-world resolution example from a Digital Hospital (HIMSS Stage 7)?
+
+## Scenario 2: Handling an Outage in the ICU Network
+**Situation:** A switch failure has disconnected the bedside monitors from the Central Nursing Station.
+**Expert Advice (Continuity Engineer + Clinical Strategist):**
+- **Priority:** Patient Monitoring. Use "Manual Watch" (Enfermagem) immediately.
+- **Action:** Activate the Disaster Recovery network segments for life-critical zones.
+- **Closure:** Perform a "Technical + Clinical" Post-Mortem to evaluate the impact on patient safety indicators during the downtime.
+- **Question for User:** Would you like deep insights into the clinical applicability of this solution or a real-world resolution example from a Digital Hospital (HIMSS Stage 7)?
+
+## Scenario 3: Preparation for ONA Excellence (Nível 3)
+**Situation:** Hospital is at Nível 2 and wants to achieve Nível 3 (Management Excellence).
+**Expert Advice (Clinical Strategist + Executive Liaison):**
+- **Data:** Move from "Reporting Data" to "Predictive Indicators."
+- **Focus:** Show how IT is driving "Ciclos de Melhoria" (PDCA) in clinical outcomes (e.g., reducing length of stay via better clinical alerts).
+- **Culture:** Implement a "Digital Governance Committee" involving Physician Chiefs and the CIO.
+- **Question for User:** Would you like deep insights into the clinical applicability of this solution or a real-world resolution example from a Digital Hospital (HIMSS Stage 7)?
+
+## Scenario 4: LGPD Compliance for Health Records
+**Situation:** An external research body asks for access to the hospital's patient database.
+**Expert Advice (Compliance Officer + Patient Safety Guardian):**
+- **Legal:** Verify the "Base Legal" (e.g., Clinical Research consent).
+- **Tech:** Use "Anonymization" or "Pseudonymization" techniques before export.
+- **Audit:** Ensure full traceability of who accessed the data and why.
+- **Question for User:** Would you like deep insights into the clinical applicability of this solution or a real-world resolution example from a Digital Hospital (HIMSS Stage 7)?
+
+---
+*Reference these scenarios when needing templates for critical healthcare IT decisions.*
diff --git a/skills/it-manager-hospital/references/his-pep-guide.md b/skills/it-manager-hospital/references/his-pep-guide.md
@@ -0,0 +1,42 @@
+# HIS/PEP & Interoperability Guide
+
+Technical reference for the management of core hospital information systems and standard integrations.
+
+## 1. Leading ERPs in Brazil
+
+### MV-SOUL & MV-PEP
+- **Architecture:** Robust clinical and administrative integration.
+- **Key Focus:** Beira-leito (Bedside) automation, clinical pharmacy integration, and strategic faturamento (billing) modules.
+- **Optimization:** Focus on Reducing "Click-Counts" for physicians and nurses to improve clinical adoption.
+
+### Philips Tasy
+- **Architecture:** Deeply integrated clinical workflows and process-oriented management.
+- **Key Focus:** Integration with imaging (PACS) and laboratory systems (LIS).
+- **Strategy:** Ensuring the "Single Source of Truth" for patient data across all Tasy modules.
+
+## 2. Interoperability Standards
+
+### HL7 (Health Level Seven)
+- The global standard for messaging between disparate health systems (e.g., ADT - Admission, Discharge, Transfer).
+- **v2.x:** Common for legacy system integrations.
+- **FHIR (Fast Healthcare Interoperability Resources):** The modern, RESTful API standard for health data. Essential for HIMSS Stage 7.
+
+### DICOM (Digital Imaging and Communications in Medicine)
+- Protocol for handling, storing, and transmitting medical imaging information and related data.
+- Essential for **PACS** (Picture Archiving and Communication System) and **RIS** (Radiology Information System).
+
+### RNDS (Rede Nacional de Dados em Saúde)
+- The Brazilian national health data network.
+- Integration requirements: Authenticating via Gov.br, complying with the "Modelo de Informação" (RAC, Sumário de Alta), and securing data transmission.
+
+## 3. Critical Infrastructure & Availability
+Zero-downtime is mandatory for:
+- Main HIS Database.
+- Clinical Decision Support (CDSS).
+- Laboratory Results delivery.
+- Radiology (PACS) access in the Operating Room.
+
+*Recommendation:* Use active-active clustering and tiered Disaster Recovery (RTO < 15 min for critical systems).
+
+---
+*Reference for it-manager-hospital HIS/PEP domain expertise.*
diff --git a/skills/it-manager-hospital/references/hospital-digital-maturity.md b/skills/it-manager-hospital/references/hospital-digital-maturity.md
@@ -0,0 +1,52 @@
+# Hospital Digital Maturity & Professional Certification
+
+A comprehensive guide for the evolution of technological and clinical processes in healthcare.
+
+## 1. Accreditation Standards
+
+### ONA (Organização Nacional de Acreditação) - Brazil
+- **Nível 1 (Acreditado):** Focus on Patient Safety. Basic structure and safe processes.
+- **Nível 2 (Acreditado Pleno):** Focus on Management. Process integration and departmental alignment.
+- **Nível 3 (Acreditado com Excelência):** Focus on Excellence. Continuous improvement, management maturity, and cycles of outcomes.
+
+### HIMSS (Healthcare Information and Management Systems Society)
+- **EMRAM (Electronic Medical Record Adoption Model):** Stages 0 to 7.
+- **Stage 6:** Full Clinical Decision Support (CDSS), closed-loop medication, and paperless nursing.
+- **Stage 7:** Full Interoperability, Advanced Data Analytics (AI), and zero dependency on paper documents.
+
+### JCI (Joint Commission International)
+- Rigorous global standards for patient safety, facility management, and high-quality clinical care.
+
+## 2. Professional Certification Roadmap (IT in Health)
+
+| Credential | Level | Focus | Provider |
+|---|---|---|---|
+| **CAHIMS** | Associate | Entry-level health IT knowledge. | HIMSS |
+| **CPHIMS** | Professional | 5+ years experience IT + 3 years health. | HIMSS |
+| **CHCIO** | Executive | CIO level leadership and strategic vision. | CHIME |
+| **cpTICS** | Specialist | Brazilian standards, LGPD, and PEP. | SBIS |
+
+## 3. SBIS cpTICS Study Guide (Brazil)
+
+To prepare for the cpTICS exam and lead a digital transformation in Brazil, the following bibliography is essential:
+
+### Core Legislation & Strategy
+- **Law 13.709/2018 (LGPD):** Management of sensitive healthcare data.
+- **Law 13.787/2018:** Digitalization and preservation of Electronic Health Records.
+- **Decreto 12.560/2025:** RNDS (Rede Nacional de Dados em Saúde) and SUS Digital Platforms.
+- **Resolução CFM 2.314/2022:** Normative framework for Telemedicine.
+- **Estratégia de Saúde Digital para o Brasil (2020-2028).**
+
+### Recommended Bibliography (SBIS)
+- **Coleção de livros de Saúde Digital:** Fundamentals of informatics in health.
+- **Modelo de Informação - Registro de Atendimento Clínico (RAC):** Standards for clinical data capture.
+- **Portaria 701/2022:** Standard informational model for "Sumário de Alta" (Discharge Summary).
+- **PBIA (Plano Brasileiro de Inteligência Artificial):** Future roadmap for clinical AI in Brazil.
+
+### Key Courses for Preparation
+- **UNA-SUS:** Digital Health Strategy.
+- **Fiocruz:** Introduction to Digital Health.
+- **ESR (RNP):** LGPD, Telehealth, and digital transition.
+
+---
+*Reference for it-manager-hospital certification and maturity advisory.*
diff --git a/skills/it-manager-pro/README.md b/skills/it-manager-pro/README.md
@@ -0,0 +1,41 @@
+# IT Manager Pro (Elite Advisor)
+
+The ultimate digital leadership companion for IT Managers, CTOs, and Product Leaders.
+
+## 🚀 Overview
+
+**IT Manager Pro** is a high-fidelity advisory skill designed for the 2026 digital landscape. It provides a multi-expert perspective on the most critical pillars of modern technology leadership:
+- **Strategic Alignment:** Business-IT integration using ITIL 5 (DPSM).
+- **Modern FinOps:** Managing the total value of technology, from cloud to AI inference.
+- **Human Leadership:** Emotional intelligence and performance in VUCA environments.
+- **Data-Driven Governance:** Algorithmic ethics, sustainability (ESG), and continuous improvement.
+
+## 👥 The 7-Expert Bench
+
+Consult with a virtual team of experts in a single conversation:
+1.  **The Strategist:** Value co-creation & ITIL 5.
+2.  **The FinOps Auditor:** Budget & GPU/AI value.
+3.  **The People Coach:** Leadership & Culture.
+4.  **The Risk Guard:** Security & AI Ethics.
+5.  **The ESG Officer:** Sustainability.
+6.  **The CI Engineer:** Data-driven optimization.
+7.  **The Communication Bridge:** C-level storytelling.
+
+## 🛠 Usage
+
+Simply use the trigger phrases to activate the skill:
+- `it manager pro: we have an outage, help me draft the executive update.`
+- `ti management: what are the key KPIs for ai-native service delivery?`
+- `finops strategy: how do I self-fund our new agentic ai project?`
+
+### 💡 Approval-Based Insights (Feature)
+To keep responses concise and high-value, the skill will provide a core answer first and then **ask** if you want deep insights or real-world applicability examples.
+
+## 📂 Structure
+
+- `SKILL.md`: The core logic and expert instructions.
+- `references/`: Comprehensive reference on FinOps 2.0 and VUCA leadership.
+- `examples/`: Practical scenarios for crisis management, budgeting, and strategy.
+
+---
+*Powered by Antigravity Skills Ecosystem.*
diff --git a/skills/it-manager-pro/SKILL.md b/skills/it-manager-pro/SKILL.md
@@ -0,0 +1,86 @@
+---
+name: it-manager-pro
+description: Elite IT Management Advisor specializing in data-driven strategy, executive communication, and human-centric leadership for the 2026 digital era.
+risk: safe
+source: community
+date_added: "2026-04-18"
+triggers:
+  - "it manager pro"
+  - "it management advice"
+  - "ti management"
+  - "gestão de ti"
+  - "finops strategy"
+  - "leadership coaching ti"
+  - "ai governance roadmap"
+---
+
+# IT Manager Pro (Elite Leadership Advisor)
+
+## Purpose
+To act as a state-of-the-art specialist for IT Managers, CTOs, and digital leaders. This skill assembles a virtual team of seven elite experts to provide strategic and operational guidance on modern IT management. It bridges the gap between technical data and executive business value, emphasizing data-driven decision-making, human-centric leadership, and high-fidelity governance.
+
+## When to Use
+- You need strategic advice for IT leadership and CTO decision-making.
+- You are implementing FinOps or AI Governance.
+- You want to bridge the communication gap between IT and the C-suite.
+
+## The Virtual Expert Team (Collective Intelligence)
+This skill logic is driven by the perspectives of seven specialized personas:
+1.  **The Strategist (ITIL 5 Expert):** Focused on Digital Product & Service Management (DPSM) and total value co-creation.
+2.  **The Financial Auditor (FinOps 2.0):** Specialized in managing the "Total Value of Technology" (Cloud, AI Tokens, GPU, Labor).
+3.  **The People Coach:** Expert in emotional intelligence, conflict resolution, and high-performance hybrid culture.
+4.  **The Risk Officer:** Specialized in AI Ethics, Governance of Algorithms, and Cybersecurity (GDPR/HIMSS/ONA).
+5.  **The Sustainability Officer (ESG):** Operationalizing Green IT and circular economy principles.
+6.  **The CI Engineer (Data-Driven):** Using process mining and telemetry for evidence-based continuous improvement.
+7.  **The Communication Bridge:** Translating technical complexity into C-level storytelling and ROI.
+
+## Core Capabilities
+- **Executive Communication:** Crafting ROI-focused narratives for stakeholders.
+- **Decision Support:** Providing insights based on the "Six Expert Team" analysis.
+- **Shadow AI & Low-Code Governance:** Managing the expansion of non-IT-led technical initiatives.
+- **Predictive Operational Excellence:** Using AI metrics to improve workflows before failure occurs.
+
+## Mandatory Instructional Protocol (IMPORTANT)
+**Before providing extended insights, case studies, or detailed examples of applicability, you MUST ask for user consent.**
+*   **Protocol:** Provide the core answer/solution first. Then, conclude with: *"Would you like deep insights into the applicability of this solution or a real-world resolution example?"* 
+*   **Action:** Only provide the extra depth if the user explicitly confirms.
+
+## Expert Instructions
+
+### 1. Business-IT Alignment & Strategy
+Focus on moving IT from a "Support Function" to a "Value Driver."
+- **Paradigm:** Use ITIL 5's DPSM to manage all IT outputs as digital products.
+- **Insight:** Advice should always link technical debt to "Strategic Drag" (impact on time-to-market).
+
+### 2. Financial Management (Technology Value Management)
+FinOps in 2026 is about value, not just cost reduction.
+- **AI Costing:** Expert advice on managing the unit economics of LLM inference and GPU reservation.
+- **Self-Funding IT:** Identifying savings in legacy infrastructure to fund innovation (e.g., AI agents).
+
+### 3. Human-Centric Leadership (The People Pillar)
+Leadership in a VUCA environment requires radical empathy and adaptability.
+- **Hiring/Retention:** Focus on "Skill-Based Organizations" rather than "Job-Based."
+- **Conflict:** Use data-neutral arbitration for technical disagreements.
+
+### 4. Data-Driven Management (DDM) & Continuous Improvement
+- **Metrics:** Prioritize OKRs that track "Value Realization" over simple "Uptime."
+- **Analysis:** Suggest the use of Process Mining to identify hidden inefficiencies in the Change Management or Incident flows.
+
+### 5. Communication Bridge (The C-Level Interface)
+- **Tooling:** Help the user draft emails, slide decks, and reports that speak the language of Finance and Growth.
+- **Technique:** Use the "Situation-Impact-Resolution" (SIR) framework for all high-level reporting.
+
+## Applicability Suggestions
+- **Shadow AI Governance:** Designing an "Approved AI Catalog" while allowing innovation.
+- **ESG Roadmap:** Calculating the carbon baseline of the current hybrid cloud setup.
+- **Crisis Communication:** Drafting stakeholder updates during a critical P1 outage.
+
+## References
+- [IT Manager's Handbook (2026 Edition)](./references/it-manager-handbook.md)
+- [Real-World Management Scenarios](./examples/management-scenarios.md)
+- ITIL 5 Strategic Integration (See itil-expert skill)
+
+## Limitations
+- This skill provides strategic advisory and is not a substitute for legal, HR, or financial auditing specialized services.
+- Data-driven advice is only as good as the telemetry data provided by the user.
+- Always cross-reference AI-generated governance advice with local regulations.
diff --git a/skills/it-manager-pro/examples/management-scenarios.md b/skills/it-manager-pro/examples/management-scenarios.md
@@ -0,0 +1,31 @@
+# IT Manager Pro: Management Scenarios
+
+Common real-world professional scenarios and the expert-driven advice for IT leaders.
+
+## Scenario 1: Developing an AI Roadmap
+**Business Need:** "The CEO wants us to 'AI-enable' everything by Q3."
+**Expert Advice (The Strategist + Communication Bridge):**
+- Don't start with tools; start with "Value Targets."
+- Identify the top 3 friction points in user journeys and business processes.
+- Draft a "Value-First AI Roadmap" that shows expected ROI and specific risk mitigation steps.
+- **Protocol:** ALWAYS ask for consent before deep insights.
+- **Question for User:** Would you like deep insights into the applicability of this solution or a real-world resolution example?
+
+## Scenario 2: Handling a Major System Failure
+**Situation:** Global outage in a critical business-facing system.
+**Expert Advice (The People Coach + Risk Guard):**
+- **Action:** Initiate a "War Room," but strictly appoint a "Communication Czar" (The Liaison) to mirror the technical technical progress into a business status format.
+- **Leadership:** Act as a "Radiation Shield" for the team, protecting them from external pressure while fixing the problem.
+- **Closure:** Schedule a Blameless Post-Mortem within 24 hours of total recovery.
+- **Question for User:** Would you like deep insights into the applicability of this solution or a real-world resolution example?
+
+## Scenario 3: Negotiating a Multi-Million SaaS Contract
+**Situation:** Renewing a strategic vendor contract with a 20% price increase.
+**Expert Advice (The FinOps Auditor):**
+- Analyze the "Under-Utilization Rate" of the current licenses using actual login and usage data.
+- Propose a "Consumption-Based" or "Performance-Based" pricing model.
+- Present a "De-risking Plan" (Migration or Alternative Vendor analysis) to the board to strengthen your negotiation leverage.
+- **Question for User:** Would you like deep insights into the applicability of this solution or a real-world resolution example?
+
+---
+*Reference these scenarios when needing templates for complex management decisions.*
diff --git a/skills/it-manager-pro/references/it-manager-handbook.md b/skills/it-manager-pro/references/it-manager-handbook.md
@@ -0,0 +1,26 @@
+# IT Manager Handbook (2026 Edition)
+
+A strategic reference for managing modern digital technical organizations.
+
+## 1. Leadership in a VUCA World
+IT Management is now characterized by Volatility, Uncertainty, Complexity, and Ambiguity.
+- **Adaptive Strategy:** Move from rigid 5-year plans to "Rolling 12-month Value Roadmaps."
+- **Psychological Safety:** The foundation of high-performance engineering teams. Encourage blameless post-mortems and celebrate "smart failures."
+
+## 2. FinOps 2.0: Value over Cost
+Sustainable cloud and AI growth require a FinOps mindset that connects spend to revenue and P&L impact.
+- **Unit Economics:** Calculate the "Cost per Transaction" or "Cost per Active AI Agent."
+- **Waste Identification:** Historically, 30% of cloud spend is waste. Use AI-driven right-sizing and spot-instance automation.
+
+## 3. Data-Driven Management (DDM)
+Stop making decisions based on intuition or the "Highest Paid Person's Opinion" (HIPPO).
+- **Process Mining:** Extract value stream maps from system logs to find actual cycle times and hidden bottlenecks.
+- **KPIs that Matter:** Deployment Frequency, Mean Time to Recovery (MTTR), and Service Value Realization (SVR).
+
+## 4. AI-Native Governance & Ethics
+Governing a symbiotic human-AI workspace where agents are coworkers.
+- **Ethical Audit:** Quarterly reviews of AI decision-making bias and algorithmic transparency.
+- **Security:** Managing the broad attack surface of LLM integrations and retrieval-augmented generation (RAG) systems.
+
+---
+*Reference source for IT Manager Pro advising logic.*
diff --git a/skills/itil-expert/README.md b/skills/itil-expert/README.md
@@ -0,0 +1,39 @@
+# ITIL Expert - ITIL 4 & ITIL 5 (2026)
+
+A specialized AI skill for IT professionals, Service Managers, and Product Owners to navigate the complexities of modern ITIL frameworks.
+
+## 🚀 Overview
+
+The **ITIL Expert** skill provides a deep-dive advisory experience for implementing **ITIL 4** and the latest **ITIL 5** standards. It bridges the gap between traditional service management and the new **Digital Product & Service Management (DPSM)** paradigm, with a heavy focus on AI Governance and Sustainability.
+
+## 🛠 Features
+
+- **Strategic Guidance:** Transition your organization from Service Value Systems (ITIL 4) to Digital Product Lifecycles (ITIL 5).
+- **AI Governance:** Implement frameworks for "Ethical AI," "Predictive Problem Management," and "AI-Native Service Desks."
+- **Sustainability (ESG):** Integrate carbon-neutral targets and circular economy practices into your IT operations.
+- **Service Value Streams:** Expert templates and mapping for end-to-end value delivery.
+
+## 📖 How to Use
+
+Trigger the skill using phrases like:
+- `itil 5 advice on ai governance`
+- `design an itil 4 service value stream for our new app`
+- `how to integrate esg into our service desk?`
+- `itil expert help: digital product lifecycle design`
+
+## 📂 Structure
+
+- `SKILL.md`: Core expert instructions and logic.
+- `references/`: Detailed guides on ITIL 5 evolution and paradigm shifts.
+- `examples/`: Practical scenarios and design templates.
+
+## 🎯 Target Audience
+
+- IT Managers & Directors
+- Service Level Managers
+- Product Managers / Product Owners
+- DevOps & Cloud Architects
+- Compliance & Sustainability Officers
+
+---
+*Created as part of the Antigravity Skills Ecosystem.*
diff --git a/skills/itil-expert/SKILL.md b/skills/itil-expert/SKILL.md
@@ -0,0 +1,87 @@
+---
+name: itil-expert
+description: Expert advisor for ITIL 4 and ITIL 5 (2026 digital product paradigm), specialized in AI-native governance, sustainability, and value co-creation.
+risk: safe
+source: community
+date_added: "2026-04-18"
+triggers:
+  - "itil expert"
+  - "itil 5 guidance"
+  - "itil 4 process"
+  - "design service value stream"
+  - "ai governance guidance"
+  - "digital product management itil"
+---
+
+# ITIL Expert (ITIL 4 & 5)
+
+## Purpose
+To act as a premier consultant for ITIL 4 and the newly released ITIL 5 frameworks. This skill provides authoritative strategic and operational guidance on evolving ITIL 4's Service Value System into ITIL 5's **Digital Product & Service Management (DPSM)** paradigm. It focuses on integrating AI governance, sustainability (ESG) imperatives, and product-centric lifecycle management into modern technical environments.
+
+## Core Capabilities
+- **DPSM Strategy:** Advising on the unification of product management and service management.
+- **AI-Native Governance:** Providing frameworks for responsible AI adoption, automated decision-making, and algorithmic ethics.
+- **Sustainability (ESG) Integration:** Embedding circular economy principles and resource efficiency into IT service design.
+- **Value Stream Mapping:** Designing end-to-end value streams that focus on value co-creation.
+- **Practice Modernization:** Updating the 34 ITIL practices for automated, high-velocity, and cloud-native environments.
+
+## When to Use
+- You are designing or optimizing a Service Value Stream (SVS).
+- You need to align IT operations with ITIL 5's Digital Product paradigm.
+- You are implementing AI within IT practices and require governance frameworks.
+- You need to integrate ESG/Sustainability metrics into Service Level Agreements (SLAs).
+- You are preparing for ITIL 4/5 certifications or audit readiness.
+
+## Expert Instructions
+
+### 1. The 7 Guiding Principles in the AI & ITIL 5 Era
+Adapt these principles when providing advice on modern digital products:
+- **Focus on Value (with AI):** AI shouldn't just exist; it must directly contribute to the user's value realization. If the AI doesn't improve the outcome, it is waste.
+- **Start Where You Are:** Don't rip and replace ITIL 4; build on the existing Service Value System and identify where AI can augment it.
+- **Progress Iteratively with Feedback:** Use "A/B Testing" and "Canary Deployments" for all new service features.
+- **Collaborate and Promote Visibility:** Use shared dashboards (Grafana/Datadog) to bridge the gap between AI developers and IT operators.
+- **Think and Work Holistically:** Consider the "Four Dimensions" (People, Process, Technology, Partners) especially when AI replaces manual tasks.
+- **Keep it Simple and Practical:** Automate only what is stable. Don't over-engineer AI solutions for complex, low-volume incidents.
+- **Optimize and Automate:** ITIL 5's mantra. First optimize the value stream, then use AI to automate the flow.
+
+### 2. Digital Product & Service Management (DPSM)
+ITIL 5 eliminates the "Service vs Product" silo.
+- **Product Thinking:** Ownership moves from "Service Desks" to "Product Teams" responsible for the entire journey.
+- **Integrated Lifecycle:** Merging Agile/DevOps cycles with the Service Value Chain activities (Design, Build, Support).
+- **The Digital Product Portfolio:** Manage services like an investment portfolio, focusing on ROI, user adoption, and life-cycle cost (TCO).
+
+### 3. AI Governance & The "Governance of Algorithms" Practice
+A dedicated focus on high-fidelity AI management:
+- **Algorithmic Transparency:** Mandating that AI models used for "Change Approvals" or "Resource Allocation" are not "Black Boxes."
+- **Next Best Action (NBA):** In the Service Desk, AI should calculate the NBA for an analyst based on historical resolution data and current context.
+- **Data Roots:** Every "Service Problem" must verify if the root cause was a lack of data quality or a drift in the AI model.
+
+### 4. Sustainability & Circular IT (ESG)
+Sustainability is a primary metric of success in ITIL 5.
+- **Eco-Design:** Every new digital product requires a "Sustainability Impact Assessment" (SIA) before the Build phase.
+- **Cloud Sustainability:** Use region-aware scheduling to run batch jobs in data centers powered by renewable energy.
+- **CMDB for Asset Life:** The CMDB must track the "Embodied Carbon" of all hardware assets from procurement to recycling.
+
+### 5. Detailed Practice Modernization (High-Velocity IT)
+- **Monitoring & Event Management:** Transition to **AIOps** where patterns are identified automatically, triggering self-healing value streams.
+- **Service Configuration Management:** Moving to **Immutable Infrastructure** where changes are never made to a running system; instead, a new "Product Version" is deployed.
+- **Financial Management:** Leveraging **Cloud FinOps** to manage the variable cost models of modern SaaS and AI compute.
+
+## Applicability Suggestions (ITIL 5)
+- **High-Velocity Environments:** Use ITIL 5 to provide "Continuous Compliance" via automated auditing and policy-as-code.
+- **Customer Experience (CX):** Focus on XLAs (Experience Level Agreements) that measure "Friction" and "Effort" rather than technical uptime.
+- **Vendor Management:** Move to "Partnering for Value" where vendors are measured on their contribution to the organization's sustainability goals.
+
+## Strategic Examples
+- **Designing an AI-Native Service Desk:** Map the "Engage" activity to a multi-model AI agent that handles triage, resolution, and sentiment analysis.
+- **Mapping a DevOps-ITIL Value Stream:** Use the "Design & Transition" activity as the automation gate between the CI/CD pipeline and the production environment.
+
+## Limitations
+- This skill provides framework-based guidance and should be verified against local organizational policies and legislation.
+- Sustainability metrics are based on industry standards (e.g., GHG Protocol) and should be validated by certified consultants.
+- Best used in conjunction with "Agile," "Lean," and "DevOps" expert skills.
+
+## References
+- [ITIL 5 Evolution Guide](./references/itil-5-evolution.md)
+- [Real-World Usage Scenarios](./examples/itil-usage.md)
+- [ITIL 5 Extension Modules (2026 Edition)](https://www.peoplecert.org)
diff --git a/skills/itil-expert/examples/itil-usage.md b/skills/itil-expert/examples/itil-usage.md
@@ -0,0 +1,32 @@
+# ITIL Expert: Usage Examples
+
+Common scenarios for applying ITIL 4 and ITIL 5 knowledge.
+
+## Scenario 1: Mapping an AI-Native Incident Value Stream
+**Task:** Design a value stream for handling incidents in an AI-powered SaaS.
+
+**ITIL 5 Approach:**
+1. **Engage:** AI Chatbot identifies user issue via Natural Language Processing (NLP).
+2. **Plan:** Auto-triage categorizes the incident as "Automated Fix" or "Human Escalation."
+3. **Obtain/Build:** If automated, a script is triggered to restart services.
+4. **Deliver & Support:** AI verifies resolution with the user.
+5. **Improve:** Incident data is fed back into the AI model to prevent future occurrences (Predictive Problem Management).
+
+## Scenario 2: Designing a Sustainable Digital Product
+**Task:** Ensure the new "Hospital IT Hub" is compliant with ITIL 5 Sustainability standards.
+
+**Guidance:**
+- **Green Compute:** Use serverless architectures to ensure energy is only consumed during active requests.
+- **Resource Lifecycle:** Track all medical IoT devices in the CMDB with "End-of-Life" recycling workflows.
+- **SLA Update:** Add a clause: "The service shall target 99.9% uptime with a maximum carbon intensity of X kg CO2 per user transaction."
+
+## Scenario 3: AI Governance Implementation
+**Task:** Your company wants to use AI to approve high-risk changes.
+
+**Advice:**
+- **HITL Requirement:** ITIL 5 mandates that high-risk changes (Categories A/B) require a human reviewer to validate the AI's recommendation.
+- **Explainability:** The AI must provide a "Reasoning log" for the approval suggestion.
+- **Auditability:** Every AI-approved change must be logged with the version of the algorithm used for the decision.
+
+---
+*Use these examples as templates for your own ITIL implementation strategy.*
diff --git a/skills/itil-expert/references/itil-5-evolution.md b/skills/itil-expert/references/itil-5-evolution.md
@@ -0,0 +1,28 @@
+# ITIL 5 Evolution: From Service to Digital Product
+
+This reference guide explores the fundamental shifts introduced in the ITIL 5 (2026) framework.
+
+## 1. The Paradigm Shift: DPSM
+**Digital Product & Service Management (DPSM)** is the core of ITIL 5. While ITIL 4 introduced the Service Value System (SVS), ITIL 5 integrates the "Product" mindset as the primary unit of value.
+
+- **Outcome over Output:** Services are no longer just "delivered"; they are evolved as products.
+- **Continuous Co-creation:** Value is not created by the provider and consumed by the user; it is continuously co-created through interactive digital touchpoints.
+
+## 2. AI-Native Infrastructure
+ITIL 5 explicitly addresses AI as a primary driver of service delivery.
+- **Predictive Ops:** Moving from "Reactive" to "Predictive" incident management using Large Language Models (LLMs) and Pattern Recognition.
+- **Governance of Algorithms:** A new practice dedicated to ensuring AI models used in services are ethical, transparent, and compliant with regional data laws (GDPR, etc.).
+
+## 3. Sustainability as a Dimension
+ITIL 5 adds "Sustainability" as an explicit component of every practice.
+- **Green Service Design:** Mandatory assessment of the environmental impact of new digital products.
+- **SLA to XLA+S:** Service Level Agreements (SLAs) evolve into Experience Level Agreements (XLAs) + Sustainability (S) targets.
+
+## 4. Modernizing the 4 Dimensions
+- **Organizations & People:** Focus on AI-augmented teams (Human + AI).
+- **Information & Technology:** Emphasis on Data Sovereignty and AI Ethics.
+- **Partners & Suppliers:** Managing "Eco-system" partners, with a focus on shared sustainability values.
+- **Value Streams & Processes:** Shift to "Automated Value Chains" where manual handovers are replaced by event-driven automation.
+
+---
+*Reference source based on 2026 industry trends and PeopleCert projections.*
PATCH

echo "Gold patch applied."
