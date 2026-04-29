# Test-coverage audit — `harbor_tasks/`

Static audit of each task's `tests/test_outputs.py` and `eval_manifest.yaml`. Reports whether tests call real CI/CD test runners (`pytest` / `vitest` / `jest` / `cargo test` / `go test`) and whether every declared `fail_to_pass` check has a matching `def test_*` function in the test file.

*Snapshot 2026-04-27, harbor_tasks/ corpus = 610 tasks at the time of audit. Current Part-1 corpus is 609 (one corrupted task moved off-tree on 2026-04-28); the percentages below are still representative.*

## Aggregate (610 tasks)

| Metric | Count | % |
|---|---:|---:|
| Tasks calling a real test runner via `subprocess.run(...)` | 278 | 45.6% |
| Tasks with a real-runner p2p test (`origin: repo_tests`) | 269 | 44.1% |
| Tasks with no behavioral assertions | 0 | — |
| Tasks dominated by structural / AST inspection | 0 | — |
| Tasks with minimal tests (≤ 2 assertions) | 3 | — |
| Total `fail_to_pass` checks declared but not matched in test file | 1218 | — |

### Real-runner mix

| Runner | Tasks |
|---|---:|
| `pytest` | 96 |
| `vitest` | 82 |
| `cargo check` | 38 |
| `jest` | 27 |
| `tsc --noemit` | 14 |
| `go test` | 12 |
| `unittest` | 11 |
| `cargo test` | 11 |
| `mypy` | 9 |
| `pnpm test` | 4 |
| `npm test` | 2 |
| `yarn test` | 2 |
| `mocha` | 1 |


## f2p coverage drill-down

The `1,218 unmatched f2p checks` from the table above is misleading — most are naming variance, not genuinely missing tests. After a token-overlap re-audit:

| Bucket | Count | % | What it is |
|---|---:|---:|---|
| `soft_match` (≥2 shared tokens) | 1,153 | 94.7 % | Test exists, name shares 2+ tokens with `check_id`. e.g. manifest `test_x_returns_y`, code `test_x_y_value` |
| `partial_keyword_match` (long substring) | 26 | 2.1 % | Test name contains a 6+ char substring of the check_id |
| `manifest_only` (genuinely missing) | **39** | **3.2 %** | Manifest declares a `fail_to_pass` check but no `def test_*` implements it |
| `subprocess_only` | 0 | 0 % | n/a (would mean a test_outputs.py with no `def test_*` but yes-runner) |

The actual manifest-test sync gap is **39 checks across the corpus** — tractable per-task fix-up. Full drill-down at `pipeline_logs/f2p_unmatched_breakdown.jsonl`.

## Weakest tasks (top 50 of 211)

Quality flag legend:
- `no_behavioral_assertions`: zero `assert*` / `expect()` calls in test_outputs.py
- `mostly_structural`: tests inspect source via AST or string-matching, don't run code
- `minimal`: ≤ 2 behavioral assertions and no real runner
- `unmatched_f2p`: declared f2p check has no matching `def test_*` function

| Task | Quality | Real runner | f2p declared | f2p matched | f2p unmatched |
|---|---|---:|---:|---:|---:|
| `superset-mcp-chart-type-schema` | calls_real_runner | yes | 25 | 0 | 25 |
| `openhands-resolve-provider-llm-base-url` | calls_real_runner | yes | 17 | 0 | 17 |
| `airflow-git-hook-security` | calls_real_runner | yes | 15 | 0 | 15 |
| `bun-pr-28838` | calls_real_runner | yes | 15 | 0 | 15 |
| `openhands-restore-notification-sound-tab-flash` | calls_real_runner | yes | 11 | 0 | 11 |
| `clickhouse-fs-cache-loading-optimization` | calls_real_runner | yes | 11 | 0 | 11 |
| `litellm-bulk-team-permissions-endpoint` | calls_real_runner | yes | 11 | 0 | 11 |
| `efcore-remove-provider-config-apis` | calls_real_runner | yes | 11 | 0 | 11 |
| `workers-sdk-local-explorer-agent-prompt` | calls_real_runner | yes | 10 | 0 | 10 |
| `prime-rl-max-total-completion-tokens` | calls_real_runner | yes | 10 | 0 | 10 |
| `superset-chart-composition-class-to-fc` | calls_real_runner | yes | 10 | 0 | 10 |
| `kotlin-swift-export-flow-nullable` | calls_real_runner | yes | 9 | 0 | 9 |
| `superset-echarts-responsive-yaxis` | calls_real_runner | yes | 9 | 0 | 9 |
| `ant-design-changelog-emoji-rule` | calls_real_runner | yes | 8 | 0 | 8 |
| `airflow-pr-64759` | calls_real_runner | yes | 8 | 0 | 8 |
| `clickhouse-s3queue-processing-nodes-cleanup` | calls_real_runner | yes | 8 | 0 | 8 |
| `litellm-no-close-on-cache-eviction` | calls_real_runner | yes | 7 | 0 | 7 |
| `openai-agents-js-parallelize-verification-runner` | calls_real_runner | yes | 7 | 0 | 7 |
| `superset-pr-39099` | calls_real_runner | yes | 7 | 0 | 7 |
| `ant-design-add-claude-md` | calls_real_runner | yes | 6 | 0 | 6 |
| `selenium-json-unify-number-parsing` | calls_real_runner | yes | 6 | 0 | 6 |
| `posthog-featcloudagent-added-sandboxenvironmentid-ext-caller` | calls_real_runner | yes | 6 | 0 | 6 |
| `uv-run-remote-script-unwrap-panic` | calls_real_runner | yes | 6 | 0 | 6 |
| `ant-design-input-search-icon` | calls_real_runner | yes | 6 | 0 | 6 |
| `infisical-posthog-org-enrichment` | calls_real_runner | yes | 5 | 0 | 5 |
| `ant-design-changelog-skill-agents-md-refs` | calls_real_runner | yes | 5 | 0 | 5 |
| `superset-embedded-default-light-theme` | calls_real_runner | yes | 5 | 0 | 5 |
| `transformers-fix-dtype-mismatch-router-timm` | calls_real_runner | yes | 5 | 0 | 5 |
| `excalidraw-clipboard-copy-no-event` | calls_real_runner | yes | 5 | 0 | 5 |
| `superset-saml-login-bootstrap` | calls_real_runner | yes | 5 | 0 | 5 |
| `effect-decodetext-streaming` | calls_real_runner | yes | 4 | 0 | 4 |
| `openai-agents-js-runstate-history` | calls_real_runner | yes | 4 | 0 | 4 |
| `superset-custom-label-tokens` | calls_real_runner | yes | 4 | 0 | 4 |
| `ruff-ty-callable-overload-no-panic` | calls_real_runner | yes | 4 | 0 | 4 |
| `effect-openrouter-reasoning-dedup` | calls_real_runner | yes | 4 | 0 | 4 |
| `uv-cache-clear-alias` | calls_real_runner | yes | 4 | 0 | 4 |
| `clickhouse-use-after-scope-fix` | calls_real_runner | yes | 4 | 0 | 4 |
| `superset-bignumber-subtitle-fontsize` | calls_real_runner | yes | 4 | 0 | 4 |
| `pulumi-closure-importstar-modules` | calls_real_runner | yes | 4 | 0 | 4 |
| `sui-benchmark-min-tps` | calls_real_runner | yes | 4 | 0 | 4 |
| `airflow-mypy-uv-sync-frozen` | calls_real_runner | yes | 4 | 0 | 4 |
| `ClickHouse-pr-102169` | calls_real_runner | yes | 4 | 0 | 4 |
| `storybook-hmr-stale-play-functions` | calls_real_runner | yes | 4 | 0 | 4 |
| `superset-escape-like-wildcards-extra-metadata` | calls_real_runner | yes | 3 | 0 | 3 |
| `uv-workspace-member-scripts-warning` | calls_real_runner | yes | 3 | 0 | 3 |
| `effect-ai-bedrock-cache-point` | calls_real_runner | yes | 3 | 0 | 3 |
| `effect-openrouter-streaming-tool-name-optional` | calls_real_runner | yes | 3 | 0 | 3 |
| `posthog-stickiness-axis-labels` | calls_real_runner | yes | 6 | 3 | 3 |
| `ant-design-upload-ref-typing` | calls_real_runner | yes | 2 | 0 | 2 |
| `effect-managed-runtime-sync-build` | calls_real_runner | yes | 2 | 0 | 2 |
