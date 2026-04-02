# Agent Config Files

Repo: zeroclaw-labs/zeroclaw
Commit: 753d4fc65f32b45797e7aba52db6c8eb3a24ad89

## AGENTS.md

```
1  # AGENTS.md — ZeroClaw
2
3  Cross-tool agent instructions for any AI coding assistant working on this repository.
4
5  ## Commands
6
7  ```bash
8  cargo fmt --all -- --check
9  cargo clippy --all-targets -- -D warnings
10 cargo test
11 ```
12
13 Full pre-PR validation (recommended):
14
15 ```bash
16 ./dev/ci.sh all
17 ```
18
19 Docs-only changes: run markdown lint and link-integrity checks. If touching bootstrap scripts: `bash -n install.sh`.
20
21 ## Project Snapshot
22
23 ZeroClaw is a Rust-first autonomous agent runtime optimized for performance, efficiency, stability, extensibility, sustainability, and security.
24
25 Core architecture is trait-driven and modular. Extend by implementing traits and registering in factory modules.
26
27 Key extension points:
28
29 - `src/providers/traits.rs` (`Provider`)
30 - `src/channels/traits.rs` (`Channel`)
31 - `src/tools/traits.rs` (`Tool`)
32 - `src/memory/traits.rs` (`Memory`)
33 - `src/observability/traits.rs` (`Observer`)
34 - `src/runtime/traits.rs` (`RuntimeAdapter`)
35 - `src/peripherals/traits.rs` (`Peripheral`) — hardware boards (STM32, RPi GPIO)
36
37 ## Repository Map
38
39 - `src/main.rs` — CLI entrypoint and command routing
40 - `src/lib.rs` — module exports and shared command enums
41 - `src/config/` — schema + config loading/merging
42 - `src/agent/` — orchestration loop
43 - `src/gateway/` — webhook/gateway server
44 - `src/security/` — policy, pairing, secret store
45 - `src/memory/` — markdown/sqlite memory backends + embeddings/vector merge
46 - `src/providers/` — model providers and resilient wrapper
47 - `src/channels/` — Telegram/Discord/Slack/etc channels
48 - `src/tools/` — tool execution surface (shell, file, memory, browser)
49 - `src/peripherals/` — hardware peripherals (STM32, RPi GPIO)
50 - `src/runtime/` — runtime adapters (currently native)
51 - `docs/` — topic-based documentation (setup-guides, reference, ops, security, hardware, contributing, maintainers)
52 - `.github/` — CI, templates, automation workflows
53
54 ## Risk Tiers
55
56 - **Low risk**: docs/chore/tests-only changes
57 - **Medium risk**: most `src/**` behavior changes without boundary/security impact
58 - **High risk**: `src/security/**`, `src/runtime/**`, `src/gateway/**`, `src/tools/**`, `.github/workflows/**`, access-control boundaries
59
60 When uncertain, classify as higher risk.
61
62 ## Workflow
63
64 1. **Read before write** — inspect existing module, factory wiring, and adjacent tests before editing.
65 2. **One concern per PR** — avoid mixed feature+refactor+infra patches.
66 3. **Implement minimal patch** — no speculative abstractions, no config keys without a concrete use case.
67 4. **Validate by risk tier** — docs-only: lightweight checks. Code changes: full relevant checks.
68 5. **Document impact** — update PR notes for behavior, risk, side effects, and rollback.
69 6. **Queue hygiene** — stacked PR: declare `Depends on #...`. Replacing old PR: declare `Supersedes #...`.
70
71 Branch/commit/PR rules:
72 - Work from a non-`master` branch. Open a PR to `master`; do not push directly.
73 - Use conventional commit titles. Prefer small PRs (`size: XS/S/M`).
74 - Follow `.github/pull_request_template.md` fully.
75 - Never commit secrets, personal data, or real identity information (see `@docs/contributing/pr-discipline.md`).
76
77 ## Anti-Patterns
78
79 - Do not add heavy dependencies for minor convenience.
80 - Do not silently weaken security policy or access constraints.
81 - Do not add speculative config/feature flags "just in case".
82 - Do not mix massive formatting-only changes with functional changes.
83 - Do not modify unrelated modules "while here".
84 - Do not bypass failing checks without explicit explanation.
85 - Do not hide behavior-changing side effects in refactor commits.
86 - Do not include personal identity or sensitive information in test data, examples, docs, or commits.
87
88 ## Linked References
89
90 - `@docs/contributing/change-playbooks.md` — adding providers, channels, tools, peripherals; security/gateway changes; architecture boundaries
91 - `@docs/contributing/pr-discipline.md` — privacy rules, superseded-PR attribution/templates, handoff template
92 - `@docs/contributing/docs-contract.md` — docs system contract, i18n rules, locale parity
```

## CLAUDE.md

```
1  # CLAUDE.md — ZeroClaw (Claude Code)
2
3  > **Shared instructions live in [`AGENTS.md`](./AGENTS.md).**
4  > This file contains only Claude Code-specific directives.
5
6  ## Claude Code Settings
7
8  Claude Code should read and follow all instructions in `AGENTS.md` at the repository root for project conventions, commands, risk tiers, workflow rules, and anti-patterns.
9
10 ## Hooks
11
12 _No custom hooks defined yet._
13
14 ## Slash Commands
15
16 _No custom slash commands defined yet._
```

## .claude/skills/github-issue/SKILL.md

(Skill definition for filing GitHub issues. Not relevant to src/agent/ code changes.)

## .claude/skills/github-pr/SKILL.md

(Skill definition for creating PRs. Not relevant to src/agent/ code changes.)

## .claude/skills/skill-creator/SKILL.md

(Skill definition for creating new skills. Not relevant to src/agent/ code changes.)

## .claude/skills/zeroclaw/SKILL.md

(Skill definition for operating ZeroClaw interactively. Not relevant to src/agent/ code changes.)
