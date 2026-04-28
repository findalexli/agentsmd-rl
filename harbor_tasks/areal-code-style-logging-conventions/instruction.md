# Add Logging Conventions and Color Scheme to Code Style Rules

The project's `CONTRIBUTING.md` previously contained detailed logging conventions and a
color scheme table. These conventions are being removed from `CONTRIBUTING.md` and need
to be documented in the agent instruction file `.claude/rules/code-style.md` so coding
agents continue to follow them.

## What's Missing

The file `.claude/rules/code-style.md` has a `## Logging` section that covers logger
naming (PascalCase) and log levels, but it doesn't document the per-rank logger format,
the logger registration procedure, or the color-to-category mapping.

## What to Add

Extend the Logging section in `.claude/rules/code-style.md` with three additions:

### 1. Per-Rank Logger Convention

For per-rank loggers: use the format `[{Component} Rank {N}]` (e.g.,
`[FSDPEngine Rank 0]`. Add this as a bullet point under the existing logger naming
rules.

### 2. Logger Registration and Testing

Register new loggers in `areal/utils/logging.py` under either `LOGGER_COLORS_EXACT` or
`LOGGER_PATTERNS` for consistent coloring. The command to test logger colors is
`python -m areal.utils.logging`. Add these as bullet points.

### 3. Color Scheme Table

Add a table titled **Color Scheme** that documents which color each logger category
receives. The categories, their assigned colors, and example loggers are:

| Category | Color | Examples |
|---|---|---|
| Infrastructure (Schedulers, Launchers) | blue | `LocalScheduler`, `RayLauncher` |
| Orchestration (Controllers, RPC) | white | `TrainController`, `SGLangWrapper` |
| RL-specific (Workflows, Rewards) | purple | `RLVRWorkflow`, `GSM8KReward` |
| Data/Metrics (Stats, Dataset) | green | `StatsLogger`, `RLTrainer` |
| Compute backends (Engines, Platforms) | cyan | `FSDPEngine`, `CUDAPlatform` |
| Warning/Error levels (override) | yellow/red | Any logger at WARNING+ |

The table should use pipe-delimited markdown format with a separator row. Follow the
style of the existing Logging section: bullet points for rules, followed by tables or
examples.

## Existing Style to Match

The Logging section uses this pattern:
- Short bullet points stating the rule
- Concrete examples prefixed with "Good:" and "Avoid:"
- Inline code formatting with backticks

Your additions should blend in with this existing format. Do not change or remove any
existing rules in the file.
