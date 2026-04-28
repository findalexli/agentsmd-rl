# feat(agents): Optimize AGENTS.md (758→94 lines, 86% reduction)

Source: [automagik-dev/genie#118](https://github.com/automagik-dev/genie/pull/118)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## 🔗 Linked Issue/Wish

**Resolves:** #111
**Wish:** `.genie/wishes/agents-optimization/agents-optimization-wish.md`

---

## 📝 Summary

This PR optimizes AGENTS.md by **86% reduction (758 → 94 lines)** through intelligent extraction of verbose content into focused @ references. The optimization maintains 100% knowledge preservation while dramatically improving maintainability and token efficiency.

**Key Achievement:** Exceeded target of ≤500 lines with final size of **94 lines**

---

## 🔧 Changes Implemented

### 1. **Core Architecture Consolidation**
- Reduced repository self-awareness section (verbose → concise)
- Streamlined core purpose definition
- Consolidated primary references into clean @ pointer list

### 2. **Skills Architecture Reorganization**
Replaced verbose inline skill descriptions with **tier-based priority system**:

**Tier 1 (Identity):**
- `know-yourself.md`

**Tier 2 (Decision Framework):**
- `evidence-based-thinking.md`
- `routing-decision-matrix.md`

**Tier 3 (System Coordination):**
- `execution-integrity-protocol.md`
- `persistent-tracking-protocol.md`
- `meta-learn-protocol.md`
- `wish-initiation-rule.md`

**Tier 4 (Discovery & Tools):**
- 6 discovery/execution skills

**Tier 5 (Guardrails):**
- `sequential-questioning.md`
- `no-backwards-compatibility.md`

**Reference-Only Skills:**
- 15 additional skills for specific scenarios

**Total:** 30 skills organized by priority (vs. 150+ lines of inline descriptions)

### 3. **Workflow Architecture Sim

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
