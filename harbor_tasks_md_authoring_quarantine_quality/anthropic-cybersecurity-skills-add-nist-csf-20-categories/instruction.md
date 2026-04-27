# Add NIST CSF 2.0 categories to compliance-governance skills

Source: [mukul975/Anthropic-Cybersecurity-Skills#12](https://github.com/mukul975/Anthropic-Cybersecurity-Skills/pull/12)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/implementing-gdpr-data-protection-controls/SKILL.md`
- `skills/implementing-iso-27001-information-security-management/SKILL.md`
- `skills/implementing-pci-dss-compliance-controls/SKILL.md`
- `skills/performing-nist-csf-maturity-assessment/SKILL.md`
- `skills/performing-soc2-type2-audit-preparation/SKILL.md`

## What to add / change

## Summary

Adds `nist_csf` field to the YAML frontmatter of all 5 compliance-governance skills, mapping each to the relevant NIST Cybersecurity Framework 2.0 categories.

### Skills updated:
- **ISO 27001** → GV.OC, GV.RM, GV.RR, GV.PO, GV.OV, ID.RA, PR.AA, PR.DS
- **PCI DSS** → GV.PO, ID.RA, PR.AA, PR.DS, PR.PS, DE.CM, DE.AE
- **NIST CSF Maturity Assessment** → All 6 functions (GV, ID, PR, DE, RS, RC) with 20 categories
- **SOC 2 Type II** → GV.OC, GV.RM, GV.RR, GV.PO, GV.OV, ID.RA, PR.AA, PR.DS, DE.CM, DE.AE, RS.MA
- **GDPR** → GV.OC, GV.PO, GV.RR, ID.AM, PR.AA, PR.DS, RS.CO, RS.MA

### NIST CSF 2.0 Functions used:
| Function | Code | Focus |
|----------|------|-------|
| Govern | GV | Governance, policy, risk management strategy |
| Identify | ID | Asset management, risk assessment |
| Protect | PR | Access control, data security, training |
| Detect | DE | Continuous monitoring, anomaly detection |
| Respond | RS | Incident management, analysis, communications |
| Recover | RC | Recovery planning, improvements |

Fixes #2

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Chores**
  * Enhanced metadata for five security compliance skill pages by adding NIST CSF mappings to their front-matter (GDPR, ISO 27001, PCI DSS, SOC 2, and NIST CSF maturity assessment). Improves categorization and discoverability; no visible content or behavioral changes.
* **Documentation**
  * Updated the NIST CSF maturity assessment table to

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
