# fix(requesthunt): address security audit failures on skills.sh

Source: [ReScienceLab/opc-skills#76](https://github.com/ReScienceLab/opc-skills/pull/76)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/requesthunt/SKILL.md`

## What to add / change

## Summary

Fixes security audit failures reported on [skills.sh/requesthunt](https://skills.sh/resciencelab/opc-skills/requesthunt):

- **Gen Agent Trust Hub**: FAIL (HIGH) — REMOTE_CODE_EXECUTION, PROMPT_INJECTION, COMMAND_EXECUTION
- **Socket**: WARN — Anomaly (install trust + external content handling)
- **Snyk**: FAIL (HIGH) — W007 (insecure credential handling), W011 (third-party content exposure), W012 (unverifiable external dependency)

## Changes

All changes are in `skills/requesthunt/SKILL.md`:

### 1. CLI Installer (REMOTE_CODE_EXECUTION / W012 / Anomaly)
- Added note that installer downloads from GitHub Releases and verifies SHA256 checksum
- Added build-from-source alternative (`cargo install --path cli`)

### 2. API Key Handling (W007)
- Changed from plaintext example (`rh_live_your_key`) to variable reference (`$YOUR_KEY`)
- Recommend environment variable (`REQUESTHUNT_API_KEY`) as primary method
- Demoted `config set-key` to secondary option with owner-only permissions note
- Added security callout against hardcoding keys

### 3. Content Safety (PROMPT_INJECTION / W011)
- Added new "Content Safety" section with explicit untrusted-input handling guidelines
- Instructs agents to treat scraped content as untrusted, use boundaries, avoid executing raw content

## Notes

The RequestHunt CLI project itself already implements all these security measures (SHA256 verification in `install.sh`, env var support, file permissions). These changes document existing protecti

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
