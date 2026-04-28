# feat(skills): add visa-doc-translatefeat(skills): Add visa-doc-translate skill for automated document translation skill

Source: [affaan-m/everything-claude-code#255](https://github.com/affaan-m/everything-claude-code/pull/255)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/visa-doc-translate/README.md`
- `skills/visa-doc-translate/SKILL.md`

## What to add / change

## Description

  Add a new skill for automatically translating visa application documents to English with
   bilingual PDF generation.

  ## Features

  - 🔄 **Multi-OCR Support**: Automatically tries macOS Vision, EasyOCR, and Tesseract
  - 📄 **Bilingual PDF**: Original image + professional English translation
  - 🌍 **Multi-language**: Supports Chinese and other languages
  - 📋 **Professional Format**: Suitable for official visa applications
  - 🚀 **Fully Automated**: No manual intervention required

  ## Supported Documents

  - Bank deposit certificates (存款证明)
  - Employment certificates (在职证明)
  - Retirement certificates (退休证明)
  - Income certificates (收入证明)
  - Property certificates (房产证明)
  - Business licenses (营业执照)
  - ID cards and passports

  ## Usage

  ```bash
  /visa-doc-translate RetirementCertificate.PNG
  /visa-doc-translate BankStatement.HEIC

  Output

  Creates <filename>_Translated.pdf with:
  - Page 1: Original document image (centered, A4 size)
  - Page 2: Professional English translation

  Testing

  Tested successfully with:
  - ✅ Chinese retirement certificates
  - ✅ macOS Vision framework OCR
  - ✅ PDF generation with proper formatting

  Perfect For

  Visa applications to Australia 🇦🇺, USA 🇺🇸, Canada 🇨🇦, UK 🇬🇧, EU 🇪🇺

  Files Added

  - skills/visa-doc-translate/SKILL.md - Main skill definition
  - skills/visa-doc-translate/README.md - Documentation

  ---
  This skill has been battle-tested with

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
