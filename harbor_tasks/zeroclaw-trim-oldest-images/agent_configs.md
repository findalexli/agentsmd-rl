# Agent Config Files

Repo: zeroclaw-labs/zeroclaw
Commit: 3e02e68ec0e26b2c43593c40d660e2298c8cb332

Files found:
- CLAUDE.md (root)
- AGENTS.md (root)
- src/providers/CLAUDE.md
- src/providers/AGENTS.md
- src/agent/CLAUDE.md, src/agent/AGENTS.md
- src/channels/CLAUDE.md, src/channels/AGENTS.md
- src/gateway/CLAUDE.md, src/gateway/AGENTS.md
- src/memory/CLAUDE.md, src/memory/AGENTS.md
- src/security/CLAUDE.md, src/security/AGENTS.md
- src/tools/CLAUDE.md, src/tools/AGENTS.md
- extensions/movie/CLAUDE.md, extensions/movie/AGENTS.md
- .claude/skills/github-issue/SKILL.md
- .claude/skills/github-pr/SKILL.md
- .claude/skills/skill-creator/SKILL.md
- .claude/skills/zeroclaw/SKILL.md

Task modifies: src/multimodal.rs (root src/ directory, no subdirectory config)
Relevant configs: root CLAUDE.md, root AGENTS.md

---

## CLAUDE.md (root)

```
1  # CLAUDE.md — ZeroClaw (Claude Code)
2
3  > **Shared instructions live in `@AGENTS.md`.**
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
17
18 ## Linked References
19
20 - `@AGENTS.md` — primary agent instruction file (cross-tool)
21 - `@docs/contributing/change-playbooks.md` — adding providers, channels, tools, peripherals; security/gateway changes; architecture boundaries
22 - `@docs/contributing/pr-discipline.md` — privacy rules, superseded-PR attribution/templates, handoff template
23 - `@docs/contributing/docs-contract.md` — docs system contract, i18n rules, locale parity
```

## AGENTS.md (root)

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
67 4. **Queue hygiene** — stacked PR: declare `Depends on #...`. Replacing old PR: declare `Supersedes #...`.
68
69 Branch/commit/PR rules:
70 - Work from a non-`master` branch. Open a PR to `master`; do not push directly.
71 - Use conventional commit titles. Prefer small PRs (`size: XS/S/M`).
72 - Follow `.github/pull_request_template.md` fully.
73 - Never commit secrets, personal data, or real identity information (see `@docs/contributing/pr-discipline.md`).
74
75 ## Anti-Patterns
76
77 - Do not add heavy dependencies for minor convenience.
78 - Do not silently weaken security policy or access constraints.
79 - Do not add speculative config/feature flags "just in case".
80 - Do not mix massive formatting-only changes with functional changes.
81 - Do not modify unrelated modules "while here".
82 - Do not bypass failing checks without explicit explanation.
83 - Do not hide behavior-changing side effects in refactor commits.
84 - Do not include personal identity or sensitive information in test data, examples, docs, or commits.
85
86 ## Linked References
87
88 - `@docs/contributing/change-playbooks.md` — adding providers, channels, tools, peripherals; security/gateway changes; architecture boundaries
89 - `@docs/contributing/pr-discipline.md` — privacy rules, superseded-PR attribution/templates, handoff template
90 - `@docs/contributing/docs-contract.md` — docs system contract, i18n rules, locale parity
```
