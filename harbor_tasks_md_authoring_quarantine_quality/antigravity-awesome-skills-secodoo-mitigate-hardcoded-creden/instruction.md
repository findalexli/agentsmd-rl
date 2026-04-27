# sec(odoo): mitigate hardcoded credentials via os.getenv

Source: [sickn33/antigravity-awesome-skills#413](https://github.com/sickn33/antigravity-awesome-skills/pull/413)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/odoo-woocommerce-bridge/SKILL.md`

## What to add / change

# Pull Request Description

This PR hardens the `odoo-woocommerce-bridge` skill by mitigating **CWE-798 (Use of Hard-coded Credentials)**. 

### 🛡️ Why This Fix is Critical
The original code contained hard-coded API keys and passwords. Leaving these in plain text leads to **API Key Leakage**, where sensitive credentials are permanently stored in the Git history. If pushed to a public repository, an attacker could use these keys to:
* **Steal Customer Data**: Access WooCommerce order and billing details.
* **Manipulate Inventory**: Change product pricing or stock levels.
* **ERP Access**: Gain unauthorized entry into the Odoo backend.

### 🟢 The Hardening Solution
We have replaced all sensitive strings with `os.getenv()` lookups. This ensures credentials stay in the local environment and never touch the source code. 

**Verification:** I have confirmed the fix with a local terminal test:
`python3 -c "import os; print('Security Check:', 'PASS' if os.getenv('ODOO_PASSWORD') == 'security_test_passed' else 'FAIL')"`
**Result: Security Check: PASS**

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

`Fixes # Manual Security Audit`

## Quality Bar Checklist ✅

- [x] **Standards**: I have read `docs/contributors/quality-bar.md` and `docs/contributors/security-guardrails.md`.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `npm run validate`).
- [x] **Risk Label**: I have confirmed the 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
