#!/usr/bin/env bash
set -euo pipefail

cd /workspace/anthropic-cybersecurity-skills

# Idempotency guard
if grep -qF "nist_csf: [GV.OC, GV.PO, GV.RR, ID.AM, PR.AA, PR.DS, RS.CO, RS.MA]" "skills/implementing-gdpr-data-protection-controls/SKILL.md" && grep -qF "nist_csf: [GV.OC, GV.RM, GV.RR, GV.PO, GV.OV, ID.RA, PR.AA, PR.DS]" "skills/implementing-iso-27001-information-security-management/SKILL.md" && grep -qF "nist_csf: [GV.PO, ID.RA, PR.AA, PR.DS, PR.PS, DE.CM, DE.AE]" "skills/implementing-pci-dss-compliance-controls/SKILL.md" && grep -qF "nist_csf: [GV.OC, GV.RM, GV.RR, GV.PO, GV.OV, GV.SC, ID.AM, ID.RA, ID.IM, PR.AA," "skills/performing-nist-csf-maturity-assessment/SKILL.md" && grep -qF "nist_csf: [GV.OC, GV.RM, GV.RR, GV.PO, GV.OV, ID.RA, PR.AA, PR.DS, DE.CM, DE.AE," "skills/performing-soc2-type2-audit-preparation/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/implementing-gdpr-data-protection-controls/SKILL.md b/skills/implementing-gdpr-data-protection-controls/SKILL.md
@@ -4,6 +4,7 @@ description: The General Data Protection Regulation (EU) 2016/679 (GDPR) is the
 domain: cybersecurity
 subdomain: compliance-governance
 tags: [compliance, governance, gdpr, privacy, data-protection, eu-regulation]
+nist_csf: [GV.OC, GV.PO, GV.RR, ID.AM, PR.AA, PR.DS, RS.CO, RS.MA]
 version: "1.0"
 author: mahipal
 license: Apache-2.0
diff --git a/skills/implementing-iso-27001-information-security-management/SKILL.md b/skills/implementing-iso-27001-information-security-management/SKILL.md
@@ -4,6 +4,7 @@ description: ISO/IEC 27001:2022 is the international standard for establishing,
 domain: cybersecurity
 subdomain: compliance-governance
 tags: [compliance, governance, iso27001, isms, risk-management, certification]
+nist_csf: [GV.OC, GV.RM, GV.RR, GV.PO, GV.OV, ID.RA, PR.AA, PR.DS]
 version: "1.0"
 author: mahipal
 license: Apache-2.0
diff --git a/skills/implementing-pci-dss-compliance-controls/SKILL.md b/skills/implementing-pci-dss-compliance-controls/SKILL.md
@@ -4,6 +4,7 @@ description: PCI DSS 4.0.1 establishes 12 requirements across 6 control objectiv
 domain: cybersecurity
 subdomain: compliance-governance
 tags: [compliance, governance, pci-dss, payment-security, cardholder-data]
+nist_csf: [GV.PO, ID.RA, PR.AA, PR.DS, PR.PS, DE.CM, DE.AE]
 version: "1.0"
 author: mahipal
 license: Apache-2.0
diff --git a/skills/performing-nist-csf-maturity-assessment/SKILL.md b/skills/performing-nist-csf-maturity-assessment/SKILL.md
@@ -4,6 +4,7 @@ description: The NIST Cybersecurity Framework (CSF) 2.0, released in February 20
 domain: cybersecurity
 subdomain: compliance-governance
 tags: [compliance, governance, nist, csf, maturity-assessment, risk-management]
+nist_csf: [GV.OC, GV.RM, GV.RR, GV.PO, GV.OV, GV.SC, ID.AM, ID.RA, ID.IM, PR.AA, PR.AT, PR.DS, PR.PS, PR.IR, DE.CM, DE.AE, RS.MA, RS.CO, RS.AN, RS.MI, RC.RP, RC.CO]
 version: "1.0"
 author: mahipal
 license: Apache-2.0
@@ -26,11 +27,11 @@ The NIST Cybersecurity Framework (CSF) 2.0, released in February 2024, provides
 | Function | Code | Categories | Purpose |
 |----------|------|-----------|---------|
 | **Govern** | GV | 6 | Establish and monitor cybersecurity risk management strategy |
-| **Identify** | ID | 4 | Determine current cybersecurity risk to the organization |
+| **Identify** | ID | 3 | Determine current cybersecurity risk to the organization |
 | **Protect** | PR | 5 | Implement safeguards to prevent or reduce risk |
 | **Detect** | DE | 2 | Find and analyze possible cybersecurity attacks |
 | **Respond** | RS | 4 | Take action regarding detected cybersecurity incidents |
-| **Recover** | RC | 1 | Restore capabilities impaired by cybersecurity incidents |
+| **Recover** | RC | 2 | Restore capabilities impaired by cybersecurity incidents |
 
 ### Govern Function (New in CSF 2.0)
 - GV.OC: Organizational Context
diff --git a/skills/performing-soc2-type2-audit-preparation/SKILL.md b/skills/performing-soc2-type2-audit-preparation/SKILL.md
@@ -4,6 +4,7 @@ description: SOC 2 Type II audit preparation involves designing, implementing, a
 domain: cybersecurity
 subdomain: compliance-governance
 tags: [compliance, governance, soc2, audit, trust-services-criteria, aicpa]
+nist_csf: [GV.OC, GV.RM, GV.RR, GV.PO, GV.OV, ID.RA, PR.AA, PR.DS, DE.CM, DE.AE, RS.MA]
 version: "1.0"
 author: mahipal
 license: Apache-2.0
PATCH

echo "Gold patch applied."
