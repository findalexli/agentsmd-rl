# Add brand-strategy skill

Source: [jeremylongshore/claude-code-plugins-plus-skills#292](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/292)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/brand-strategy/SKILL.md`

## What to add / change

# Pull Request

## Type of Change

<!-- Select all that apply -->

- [x] 🔌 New plugin submission
- [ ] ⬆️ Plugin update/enhancement
- [ ] 📚 Documentation improvement
- [ ] 🐛 Bug fix
- [ ] 🏗️ Infrastructure/CI improvement
- [ ] 🎨 Marketplace website update
- [ ] 🔧 Configuration change
- [ ] 🧪 Tests added/updated
- [ ] 🔐 Security fix
- [ ] 🚀 Performance improvement
- [ ] ♻️ Refactoring
- [ ] 🌐 Translation/i18n
- [ ] 🗑️ Deprecation/removal
- [ ] 📦 Dependency update
- [ ] 🎯 Other (please describe)

## Description
A 7-part brand strategy framework for building comprehensive brand foundations — from brand truth to measurement. Same methodology agencies use with Fortune 500 clients, now available as an AI skill.

**Summary:**
Adds a 7-part brand strategy framework skill to the skills collection.

**Motivation:**
Bringing professional brand strategy methodology to AI agents — useful for founders, marketers, and agency strategists


## Security
- Related alerts: GHSA-/CVE-
- Impact assessment: None / Low / Medium / High

## Plugin Details (for plugin submissions/updates)

**Plugin Name:** brand-strategy
**Category:** marketing/business
**Version:** 1.0
**Keywords:** brand strategy, marketing, positioning, messaging, brand guidelines

## Checklist

### For All PRs
- [x] I have read the [CONTRIBUTING.md](../000-docs/007-DR-GUID-contributing.md) guidelines
- [x] My code follows the project's style and conventions
- [x] I have performed a se

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
