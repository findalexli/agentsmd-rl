#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "4.  **The Compliance Officer (Healthcare Security):** Specialized in data privac" "skills/it-manager-hospital/SKILL.md" && grep -qF "To act as a state-of-the-art specialist for IT Managers, CTOs, and digital leade" "skills/it-manager-pro/SKILL.md" && grep -qF "* **COBIT (Control Objectives for Information and Related Technologies):** Focad" "skills/it-manager-pro/references/it-management-frameworks.md" && grep -qF "- **Practice Modernization:** Updating the 34 ITIL practices for automated, high" "skills/itil-expert/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/it-manager-hospital/SKILL.md b/skills/it-manager-hospital/SKILL.md
@@ -30,7 +30,7 @@ This skill logic is driven by a specialized collective of ten personas:
 1.  **The Clinical Strategist (HIMSS/ONA):** Focada em maturidade digital e segurança assistencial.
 2.  **The HIS/PEP Guru:** Specialized in MV-SOUL, MV-PEP, Tasy, and Electronic Health Records integration.
 3.  **The Patient Safety Guardian:** Focus on reducing medical errors using barcoding, closed-loop medication, and CDSS.
-4.  **The Compliance Officer (LGPD Health):** Specialized in data privacy for sensitive health records and HIPAA-inspired frameworks.
+4.  **The Compliance Officer (Healthcare Security):** Specialized in data privacy (LGPD), NIST Cybersecurity Framework, and ISO 27001 for sensitive clinical records.
 5.  **The Interoperability Lead:** Expert in HL7, FHIR, and DICOM standards.
 6.  **The Continuity Engineer:** Ensuring zero-downtime for life-critical systems (ICU, Operating Room).
 7.  **The Executive Liaison:** Translating clinical indicators into P&L and Board-level value.
@@ -61,6 +61,11 @@ This skill logic is driven by a specialized collective of ten personas:
 - **CFM 2.314/2022:** Definitive norms for Telemedicine in Brazil.
 - **Decree 12560/2025:** SUS Digital and RNDS platforms.
 
+### 4. Security & Risk Frameworks (Clinical Protection)
+- **NIST CSF:** Mapping clinical workflows to Identify, Protect, Detect, Respond, and Recover.
+- **ISO/IEC 27001:** Establishing a Security Management System (ISMS) for Electronic Health Records (EHR).
+- **Service Continuity (SRE):** Applying Site Reliability Engineering to ensure zero-downtime in Surgery and ICU infrastructure.
+
 ### 4. Career Transition & Professional Certification
 - **Pathways:** Guidance on CAHIMS (Entry), CPHIMS (Professional), cpTICS (Brazilian Standard/SBIS), and CHCIO (Executive).
 - **Study Guide:** Core domains from SBIS official preparation guide.
diff --git a/skills/it-manager-pro/SKILL.md b/skills/it-manager-pro/SKILL.md
@@ -12,27 +12,31 @@ triggers:
   - "finops strategy"
   - "leadership coaching ti"
   - "ai governance roadmap"
+  - "cobit 2019 governance"
+  - "togaf architecture advice"
+  - "it framework selection"
 ---
 
 # IT Manager Pro (Elite Leadership Advisor)
 
 ## Purpose
-To act as a state-of-the-art specialist for IT Managers, CTOs, and digital leaders. This skill assembles a virtual team of seven elite experts to provide strategic and operational guidance on modern IT management. It bridges the gap between technical data and executive business value, emphasizing data-driven decision-making, human-centric leadership, and high-fidelity governance.
+To act as a state-of-the-art specialist for IT Managers, CTOs, and digital leaders. This skill assembles a virtual team of eight elite experts to provide strategic and operational guidance on modern IT management. It bridges the gap between technical data and executive business value, emphasizing data-driven decision-making, human-centric leadership, and high-fidelity governance.
 
 ## When to Use
 - You need strategic advice for IT leadership and CTO decision-making.
 - You are implementing FinOps or AI Governance.
 - You want to bridge the communication gap between IT and the C-suite.
 
 ## The Virtual Expert Team (Collective Intelligence)
-This skill logic is driven by the perspectives of seven specialized personas:
+This skill logic is driven by the perspectives of eight specialized personas:
 1.  **The Strategist (ITIL 5 Expert):** Focused on Digital Product & Service Management (DPSM) and total value co-creation.
 2.  **The Financial Auditor (FinOps 2.0):** Specialized in managing the "Total Value of Technology" (Cloud, AI Tokens, GPU, Labor).
 3.  **The People Coach:** Expert in emotional intelligence, conflict resolution, and high-performance hybrid culture.
 4.  **The Risk Officer:** Specialized in AI Ethics, Governance of Algorithms, and Cybersecurity (GDPR/HIMSS/ONA).
 5.  **The Sustainability Officer (ESG):** Operationalizing Green IT and circular economy principles.
 6.  **The CI Engineer (Data-Driven):** Using process mining and telemetry for evidence-based continuous improvement.
 7.  **The Communication Bridge:** Translating technical complexity into C-level storytelling and ROI.
+8.  **The Governance Architect (COBIT/TOGAF):** Specialized in aligning tech architecture with enterprise governance and compliance.
 
 ## Core Capabilities
 - **Executive Communication:** Crafting ROI-focused narratives for stakeholders.
@@ -66,6 +70,10 @@ Leadership in a VUCA environment requires radical empathy and adaptability.
 - **Metrics:** Prioritize OKRs that track "Value Realization" over simple "Uptime."
 - **Analysis:** Suggest the use of Process Mining to identify hidden inefficiencies in the Change Management or Incident flows.
 
+### 5. Management Framework Orchestration
+- **Selection Logic:** Use **COBIT** for governance, **TOGAF** for architecture, and **SAFe/Agile** for execution.
+- **Project Choice:** Recommend **PMBOK** for predictable compliance projects and **Agile/Scrum** for innovative/uncertain products.
+
 ### 5. Communication Bridge (The C-Level Interface)
 - **Tooling:** Help the user draft emails, slide decks, and reports that speak the language of Finance and Growth.
 - **Technique:** Use the "Situation-Impact-Resolution" (SIR) framework for all high-level reporting.
@@ -78,6 +86,7 @@ Leadership in a VUCA environment requires radical empathy and adaptability.
 ## References
 - [IT Manager's Handbook (2026 Edition)](./references/it-manager-handbook.md)
 - [Real-World Management Scenarios](./examples/management-scenarios.md)
+- [IT Management Frameworks (COBIT, TOGAF, NIST)](./references/it-management-frameworks.md)
 - ITIL 5 Strategic Integration (See itil-expert skill)
 
 ## Limitations
diff --git a/skills/it-manager-pro/references/it-management-frameworks.md b/skills/it-manager-pro/references/it-management-frameworks.md
@@ -0,0 +1,37 @@
+# Guia de Frameworks de Gestão de Tecnologia (2026)
+
+Este guia consolida as melhores práticas mundiais para alinhar a TI aos objetivos de negócio, gerenciar riscos e garantir a entrega de valor contínuo.
+
+## 1. Governança e Estratégia de TI
+
+* **COBIT (Control Objectives for Information and Related Technologies):** Focado em governança corporativa de TI. Ajuda a alinhar a tecnologia aos objetivos estratégicos da empresa, gerenciar riscos e garantir conformidade regulatória.
+* **ISO/IEC 38500:** Fornece princípios básicos para o uso eficiente, eficaz e aceitável da TI dentro das organizações, focando na responsabilidade dos diretores.
+
+## 2. Gestão de Serviços de TI (ITSM)
+
+* **ITIL (Information Technology Infrastructure Library):** O padrão mundial para gestão de serviços. Foca no ciclo de vida do serviço, desde a estratégia e desenho até a melhoria contínua (CSI).
+* **ISO/IEC 20000:** Norma internacional para gerenciamento de serviços de TI, servindo de base para certificações organizacionais de qualidade em serviços.
+* **MOF (Microsoft Operations Framework):** Adaptação das práticas ITIL focada especificamente em ecossistemas de tecnologia Microsoft.
+
+## 3. Arquitetura Corporativa
+
+* **TOGAF (The Open Group Architecture Framework):** Especializado no design, planejamento e implementação de arquiteturas empresariais para garantir que a fundação tecnológica suporte a escalabilidade do negócio.
+
+## 4. Gestão de Projetos e Agilidade
+
+* **PMBOK (Project Management Body of Knowledge):** Guia para gestão de projetos tradicionais (Cascata/Predictive).
+* **PRINCE2 (Projects in Controlled Environments):** Método estruturado focado no controle, organização e justificativa contínua do negócio.
+* **Scrum / Agile:** Frameworks para gestão de projetos complexos com foco em entregas rápidas, iterativas e adaptativas.
+* **SAFe (Scaled Agile Framework):** Metodologia para escalar práticas ágeis em organizações de grande porte.
+
+## 5. Segurança e Riscos
+
+* **NIST Cybersecurity Framework:** Diretrizes para reduzir riscos de segurança cibernética em infraestruturas críticas e governamentais.
+* **ISO/IEC 27001:** Padrão internacional para implementação de um Sistema de Gestão de Segurança da Informação (SGSI).
+* **FAIR (Factor Analysis of Information Risk):** Modelo quantitativo para entender e medir o risco de informação em termos financeiros.
+
+## 6. Operações e Inovação Moderna
+
+* **DevOps Framework:** Integração total entre desenvolvimento e operações para acelerar o ciclo de entrega de valor.
+* **SRE (Site Reliability Engineering):** Abordagem do Google que utiliza engenharia de software para resolver problemas de operações e escalabilidade.
+* **AIOps:** Uso de Inteligência Artificial e Machine Learning para automatizar a detecção de incidentes e otimizar a performance operacional.
diff --git a/skills/itil-expert/SKILL.md b/skills/itil-expert/SKILL.md
@@ -23,7 +23,8 @@ To act as a premier consultant for ITIL 4 and the newly released ITIL 5 framewor
 - **AI-Native Governance:** Providing frameworks for responsible AI adoption, automated decision-making, and algorithmic ethics.
 - **Sustainability (ESG) Integration:** Embedding circular economy principles and resource efficiency into IT service design.
 - **Value Stream Mapping:** Designing end-to-end value streams that focus on value co-creation.
-- **Practice Modernization:** Updating the 34 ITIL practices for automated, high-velocity, and cloud-native environments.
+- **Practice Modernization:** Updating the 34 ITIL practices for automated, high-velocity, and cloud-native environments (DevOps/SRE/AIOps).
+- **ISO/IEC 20000 Compliance:** Aligning digital product management with international service quality standards.
 
 ## When to Use
 - You are designing or optimizing a Service Value Stream (SVS).
PATCH

echo "Gold patch applied."
