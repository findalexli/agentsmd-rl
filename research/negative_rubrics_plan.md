# Research Plan: Negative Rubrics & Distractor Instructions

Date: 2026-04-10

## Core Research Question

Can we train coding agents to REASON about which repository instructions apply to a specific task, rather than blindly following all of them?

## Motivation

Current SWE benchmarks (SWE-bench, Terminal Bench, SWE-smith) assume instructions are clear and complete. In reality, repos have hierarchical config files (AGENTS.md, CLAUDE.md, SKILL.md) with 20-200+ rules at multiple directory levels. Many rules are irrelevant to a specific PR. An agent that blindly follows everything wastes time or introduces errors.

### Literature Support

- **NoisyBench** (2601.07226): 80% performance drop from hard negative distractors. Models disproportionately attend to distractor tokens. Inverse scaling: more reasoning steps amplify noise.
- **RARE** (Rationale-Aware Reward): Outcome-only RL marginally helps. Need reward that explicitly incentivizes identifying helpful vs noisy information.
- **GSM-DC** (2505.18761): Training with strong distractors improves both in-distribution and out-of-distribution robustness.
- **DIM-Bench**: LLMs vulnerable to negative/distractor requirements in instruction-following tasks.
- **SkillsBench** (2602.12670): Tests whether agents correctly select relevant skills AND ignore distractor skills.
- **AGENTS.md v1.1 Proposal**: Hierarchy is accumulative (child extends parent), conflict resolution requires judgment, "Guidance Not Governance."

## Approach: 4-Track Evaluation

### Track 1: Code Correctness (existing)
- test.sh → nop=0, gold=1
- Binary, deterministic

### Track 2: Config Edit Quality (existing)
- config_edits extracted from solve.sh
- Gemini semantic comparison of gold vs agent config changes

### Track 3: Positive Rubric Compliance (existing, improved)
- Rules from config files the gold solution FOLLOWS
- Must cite real file + lines, verified by Gemini

### Track 4: Negative Rubric Discrimination (NEW)
- Rules from config files the gold solution deliberately IGNORES
- Tests whether agent can identify and skip irrelevant instructions
- Categories:
  - **Wrong subsystem**: Database rules applied to UI code
  - **Wrong language**: Python rules applied to TypeScript files
  - **Wrong scope**: Package-level rules applied to a different package
  - **Conflicting hierarchy**: Child AGENTS.md overrides parent rule
  - **Irrelevant skill**: Skill description matches keywords but task doesn't need it

## Implementation Plan

### Phase 1: Hierarchy Context Extraction (DONE)
- `hierarchy_context.py` extracts full config hierarchy per task
- Finds all AGENTS.md/CLAUDE.md from root → edited file directories
- Identifies skills with heuristic relevance scoring

### Phase 2: Gemini Rubric Constructor
- Feed full config hierarchy + gold solution + instruction to Gemini 3.1 Pro (1M context)
- Gemini extracts:
  - Positive rubrics (with source file + evidence from gold)
  - Negative rubrics (with source file + reason for non-applicability)
  - Skill relevance decisions
  - Hierarchy conflict resolutions
- Output: structured JSON per task

### Phase 3: Kimi Integration
- Kimi agent calls Gemini rubric constructor programmatically
- Kimi validates and iterates on Gemini's output
- Final rubric stored in eval_manifest.yaml with new fields:
  ```yaml
  positive_rubrics:
    - rule: "Prefer single-word variable names"
      source: {path: "AGENTS.md", lines: "28-32"}
      evidence_in_gold: "Uses `question` not `shouldEnableQuestion`"
  
  negative_rubrics:
    - rule: "Reduce variable count by inlining single-use values"
      source: {path: "AGENTS.md", lines: "45-50"}
      why_not_applicable: "Readability: extracted variable clarifies conditional logic"
      category: "judgment_override"
  ```

### Phase 4: Evaluation & Training
- At eval time: agent gets the full config hierarchy (all tracks)
- Scoring: binary (all checks pass) + ICR for rubric tracks
- For RL training: reward signal includes positive rubric compliance AND negative rubric avoidance
- Connects to RARE: our task structure naturally provides the "rationale" signal

### Phase 5: Scale
- Target repos with deep hierarchies (OpenAI: 88 AGENTS.md, monorepos with nested packages)
- Scout PRs where config rules conflict or don't apply
- Goal: 500+ tasks with negative rubrics

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| PR author choices aren't always correct | Only create negatives for CLEAR non-applicability (wrong language/subsystem) |
| Agent learns to ignore all tangential instructions | Positive rubrics must outnumber negatives 3:1+ |
| Gemini judge bias in both generation and evaluation | Use programmatic gold diff as ground truth where possible |
| Sparse negative signal per task (2-3 negatives) | Focus on repos with deep hierarchies for more signal |
| Binary RL reward insufficient for discrimination | Task structure encodes discrimination (nop=0 when following distractor) |

## E2E Validation Results (2026-04-10)

Tested on 3 tasks with full hierarchy context → Gemini 3.1 Pro:

**opencode-acp-question-tool-flag:**
- Positive: "single word names" (gold uses `question`), "const over let" (gold uses `const`)
- Negative: "inline single-use variables" (gold keeps `question` for readability), "database guide" (irrelevant subsystem)

**biome-docs-break-down-skills:**
- Positive: "AI disclosure in PRs", "changeset formatting rules"
- Negative: "create a .changeset/ file" (internal docs, not code change), "Fixes #1234 comment" (meta-level, not applicable to itself)

**remix-supersede-pr-skill:**
- Positive: "TypeScript strict mode", "Prettier formatting rules"
- Negative: "runtime-agnostic" (task explicitly asks for Node-specific), "package exports" (internal tooling, not published package)
