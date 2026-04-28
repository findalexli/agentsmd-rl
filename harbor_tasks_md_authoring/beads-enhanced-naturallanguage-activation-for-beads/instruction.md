# Enhanced Natural-Language Activation for Beads Skills

Source: [gastownhall/beads#718](https://github.com/gastownhall/beads/pull/718)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/beads/SKILL.md`

## What to add / change

# Enhanced Natural-Language Activation for Beads Skills

Hey Steve! 👋

I'm **Jeremy Longshore** - I run [claudecodeplugins.io](https://claudecodeplugins.io), a marketplace with 258 Claude Code plugins. I discovered Beads and immediately saw how powerful it is for persistent task memory across sessions. This tool is **exactly** what AI agents need.

## What This PR Does

I've consolidated your 30 slash commands into **ONE comprehensive SKILL.md** that enables **natural-language activation** while **keeping all slash commands as backup**.

**Before**: Users need to remember `/bd-create`, `/bd-ready`, `/bd-show`, etc. (30 commands, 1,521 lines)
**After**: Users can say "create a task for this bug" or "what's ready to work on?" - Claude handles it naturally

**Your slash commands still work** - they're now a **backup option** for power users who prefer explicit control.

---

## Who I Am & What I Do

**Jeremy Longshore**
**Founder**: [Intent Solutions IO](https://intentsolutions.io)
**Marketplace**: [claudecodeplugins.io](https://claudecodeplugins.io) (258 plugins, 241 Agent Skills)

I specialize in **production-grade Claude Code plugins** that follow **Anthropic's 2025 Skills Specification** to the letter. I've built validators, workflows, and standards to ensure skills work reliably across all Claude platforms (web, CLI, API).

**My Method**:
1. Study official Anthropic docs obsessively
2. Build enterprise-grade validators (based on Anthropic + my own production standards)
3. T

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
