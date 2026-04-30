# docs: add hierarchical AGENTS.md knowledge base

Source: [cloudflare/quiche#2363](https://github.com/cloudflare/quiche/pull/2363)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `h3i/AGENTS.md`
- `qlog-dancer/AGENTS.md`
- `qlog/AGENTS.md`
- `quiche/AGENTS.md`
- `quiche/src/h3/AGENTS.md`
- `quiche/src/recovery/AGENTS.md`
- `tokio-quiche/AGENTS.md`
- `tokio-quiche/src/http3/driver/AGENTS.md`
- `tokio-quiche/src/quic/AGENTS.md`

## What to add / change

## Summary

- Add 10 AGENTS.md files forming a hierarchical knowledge base for AI coding agents
- Root covers workspace overview, dependency graph, conventions, feature flags, and commands
- Subdirectory files cover crate-specific structure, anti-patterns, and navigation pointers

## Files

```
./AGENTS.md                              (root: workspace overview)
├── quiche/AGENTS.md                     (core QUIC+H3 crate)
│   ├── quiche/src/recovery/AGENTS.md    (dual CC: congestion + gcongestion)
│   └── quiche/src/h3/AGENTS.md          (HTTP/3 module, own Error types)
├── tokio-quiche/AGENTS.md               (async wrapper, ApplicationOverQuic)
│   ├── tokio-quiche/src/http3/driver/   (sealed DriverHooks, channels)
│   └── tokio-quiche/src/quic/           (IoWorker FSM, router)
├── h3i/AGENTS.md                        (H3 testing tool)
├── qlog/AGENTS.md                       (event schema library)
└── qlog-dancer/AGENTS.md               (visualization, native + wasm)
```

Child files never repeat parent content. Small leaf crates (octets, buffer-pool, datagram-socket, netlog, task-killswitch) are covered by root and skipped.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
