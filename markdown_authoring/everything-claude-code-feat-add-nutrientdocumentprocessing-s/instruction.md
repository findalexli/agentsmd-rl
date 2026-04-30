# feat: add nutrient-document-processing skill

Source: [affaan-m/everything-claude-code#166](https://github.com/affaan-m/everything-claude-code/pull/166)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/nutrient-document-processing/SKILL.md`

## What to add / change

## What

Adds a document processing skill powered by the [Nutrient DWS API](https://www.nutrient.io/api/).

## Capabilities

| Operation | Description |
|-----------|-------------|
| **Convert** | PDF ↔ DOCX/XLSX/PPTX, HTML → PDF, images → PDF |
| **Extract** | Text, tables, and key-value pairs from PDFs |
| **OCR** | Multi-language OCR for scanned documents (25+ languages) |
| **Redact** | Pattern-based presets (SSN, email, credit card) + regex + AI-powered |
| **Watermark** | Text or image watermarks with styling control |
| **Sign** | CMS and CAdES digital signatures |
| **Fill Forms** | Programmatic PDF form filling |

## Structure

```
skills/nutrient-document-processing/
└── SKILL.md    # Setup + curl examples for all operations + MCP config
```

## Setup

Free API key at https://dashboard.nutrient.io/sign_up/?product=processor

## Checklist

- [x] Focused on one domain (document processing)
- [x] Includes practical code examples (curl for every operation)
- [x] Under 500 lines (165 lines)
- [x] Uses clear section headers
- [x] Tested with Claude Code

## Links

- [Agent Skill Repo](https://github.com/PSPDFKit-labs/nutrient-agent-skill)
- [MCP Server](https://www.npmjs.com/package/@nutrient-sdk/dws-mcp-server)
- [API Playground](https://dashboard.nutrient.io/processor-api/playground/)

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Added a comprehensive guide for the Nutrient Document Processi

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
