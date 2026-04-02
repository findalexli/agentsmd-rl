# Validation Status

Generated: 2026-04-01T20:15:47.954372

| Status | Count |
|--------|-------|
| Pass | 156 |
| Fail | 201 |
| Error/build fail | 73 |
| No validation | 0 |
| **Total** | **430** |

## Passing (156)

| Task | Gold | Nop | Runner |
|------|------|-----|--------|
| areal-config-postinit-validation | None | None | scripts/docker_validate_all.sh |
| areal-cpu-platform-device-fallback | None | None | scripts/docker_validate_all.sh |
| areal-data-proxy-batch-endpoint | None | None | scripts/docker_validate_all.sh |
| areal-eval-distributed-sampler-padding | None | None | scripts/docker_validate_all.sh |
| areal-fsdp-pipeline-weight-sync | None | None | scripts/docker_validate_all.sh |
| areal-integration-test-fixture-reuse | None | None | scripts/docker_validate_all.sh |
| areal-lora-alias-handling | None | None | scripts/docker_validate_all.sh |
| areal-megatron-bridge-duplicate-kwarg | None | None | scripts/docker_validate_all.sh |
| areal-openai-proxy-empty-session | None | None | scripts/docker_validate_all.sh |
| areal-pad-packed-zero-length | None | None | scripts/docker_validate_all.sh |
| areal-pil-image-serialization | None | None | scripts/docker_validate_all.sh |
| areal-platform-numa-cpu-affinity | None | None | scripts/docker_validate_all.sh |
| areal-ppo-kl-divergence-estimators | None | None | scripts/docker_validate_all.sh |
| areal-rpc-error-response-key | None | None | scripts/docker_validate_all.sh |
| areal-rtensor-session-retry | None | None | scripts/docker_validate_all.sh |
| areal-scheduling-literal-omegaconf | None | None | scripts/docker_validate_all.sh |
| areal-socket-bind-failure-cleanup | None | None | scripts/docker_validate_all.sh |
| areal-streaming-response-handler | None | None | scripts/docker_validate_all.sh |
| areal-types-enum-logging-fix | None | None | scripts/docker_validate_all.sh |
| areal-vllm-pause-generation-native | None | None | scripts/docker_validate_all.sh |
| bun-async-iterable-response-crash | None | None | scripts/docker_validate_all.sh |
| bun-bake-client-fixture-crash | None | None | scripts/docker_validate_all.sh |
| bun-compile-metadata-version-deflake | None | None | scripts/docker_validate_all.sh |
| bun-dns-lookup-non-object-crash | None | None | scripts/docker_validate_all.sh |
| bun-dns-stale-cache-refcount | None | None | scripts/docker_validate_all.sh |
| bun-error-format-pending-exception-crash | None | None | scripts/docker_validate_all.sh |
| bun-fd-float-overflow-panic | None | None | scripts/docker_validate_all.sh |
| bun-ffi-viewsource-nonobject-crash | None | None | scripts/docker_validate_all.sh |
| bun-glob-ntfilter-active-set-compile | None | None | scripts/docker_validate_all.sh |
| bun-inspect-env-transpiler-cache | None | None | scripts/docker_validate_all.sh |
| bun-install-scanner-silent-exit | None | None | scripts/docker_validate_all.sh |
| bun-pipeto-abortsignal-leak | None | None | scripts/docker_validate_all.sh |
| bun-stale-pm-log-resolve | None | None | scripts/docker_validate_all.sh |
| bun-throw-pending-exception-crash | None | None | scripts/docker_validate_all.sh |
| bun-vm-script-fetcher-leak | None | None | scripts/docker_validate_all.sh |
| bun-webcore-memory-safety-fixes | None | None | scripts/docker_validate_all.sh |
| gradio-absolute-path-windows | None | None | scripts/docker_validate_all.sh |
| gradio-block-border-inheritance | None | None | scripts/docker_validate_all.sh |
| gradio-button-scale-parameter | None | None | scripts/docker_validate_all.sh |
| gradio-client-sse-deque-perf | None | None | scripts/docker_validate_all.sh |
| gradio-cloudflare-markdown-response-format | None | None | scripts/docker_validate_all.sh |
| gradio-colorpicker-events | None | None | scripts/docker_validate_all.sh |
| gradio-colorpicker-hex-normalization | None | None | scripts/docker_validate_all.sh |
| gradio-connection-lost-error-handling | None | None | scripts/docker_validate_all.sh |
| gradio-custom-component-reload | None | None | scripts/docker_validate_all.sh |
| gradio-dataframe-nan-sort | None | None | scripts/docker_validate_all.sh |
| gradio-docs-table-styling | None | None | scripts/docker_validate_all.sh |
| gradio-dropdown-scroll-detach | None | None | scripts/docker_validate_all.sh |
| gradio-dropdown-slowdown-destructure | None | None | scripts/docker_validate_all.sh |
| gradio-duplicate-block-error-reload | None | None | scripts/docker_validate_all.sh |
| gradio-file-sanitize-empty-stem | None | None | scripts/docker_validate_all.sh |
| gradio-gallery-height-css-mismatch | None | None | scripts/docker_validate_all.sh |
| gradio-guide-right-sidebar-nav | None | None | scripts/docker_validate_all.sh |
| gradio-html-custom-event-getattr | None | None | scripts/docker_validate_all.sh |
| gradio-html-gallery-fixed-css-iframe | None | None | scripts/docker_validate_all.sh |
| gradio-html-watch-prop-observer | None | None | scripts/docker_validate_all.sh |
| gradio-load-event-inactive-tab | None | None | scripts/docker_validate_all.sh |
| gradio-load-fn-recursion-oom | None | None | scripts/docker_validate_all.sh |
| gradio-localfont-css-weight-numeric | None | None | scripts/docker_validate_all.sh |
| gradio-markdown-pending-show-progress | None | None | scripts/docker_validate_all.sh |
| gradio-mobile-menu-ux | None | None | scripts/docker_validate_all.sh |
| gradio-reload-annotated-types | None | None | scripts/docker_validate_all.sh |
| gradio-spaces-reloader-config | None | None | scripts/docker_validate_all.sh |
| gradio-submit-button-example-click | None | None | scripts/docker_validate_all.sh |
| gradio-sync-generator-cancel-valueerror | None | None | scripts/docker_validate_all.sh |
| gradio-tab-i18n-label-translation | None | None | scripts/docker_validate_all.sh |
| gradio-test-event-dispatch-noop | None | None | scripts/docker_validate_all.sh |
| gradio-type-hints-nameerror-crash | None | None | scripts/docker_validate_all.sh |
| gradio-walkthrough-selected-binding | None | None | scripts/docker_validate_all.sh |
| nextjs-napi-rcstr-string-alloc | None | None | scripts/docker_validate_all.sh |
| nextjs-otel-span-route-fallback | None | None | scripts/docker_validate_all.sh |
| nextjs-turbopack-cache-stats-deadlock | None | None | scripts/docker_validate_all.sh |
| nextjs-typed-routes-retry-timeout-flake | None | None | scripts/docker_validate_all.sh |
| nextjs-urlhash-test-retry-flake | None | None | scripts/docker_validate_all.sh |
| openclaw-clawhub-archive-sanitize | None | None | scripts/docker_validate_all.sh |
| openclaw-controlui-bootstrap-payload-trim | None | None | scripts/docker_validate_all.sh |
| openclaw-dotenv-workspace-cred-block | None | None | scripts/docker_validate_all.sh |
| openclaw-zsh-compdef-defer | None | None | scripts/docker_validate_all.sh |
| opencode-auth-enterprise-url-drop | None | None | scripts/docker_validate_all.sh |
| opencode-bash-tool-cache-hit-rate | None | None | scripts/docker_validate_all.sh |
| opencode-config-cached-invalidate-ttl | None | None | scripts/docker_validate_all.sh |
| opencode-home-footer-plugin-slot | None | None | scripts/docker_validate_all.sh |
| opencode-router-instance-provide | None | None | scripts/docker_validate_all.sh |
| opencode-skill-effect-native | None | None | scripts/docker_validate_all.sh |
| opencode-tool-registry-effect-native | None | None | scripts/docker_validate_all.sh |
| prime-rl-ckpt-skip-optimizer-load | None | None | scripts/docker_validate_all.sh |
| prime-rl-nemotron-mamba-expand-mismatch | None | None | scripts/docker_validate_all.sh |
| prime-rl-qwen35-vlm-text-dispatch | None | None | scripts/docker_validate_all.sh |
| prime-rl-remove-tp-trainer-config | None | None | scripts/docker_validate_all.sh |
| prime-rl-toml-none-str-removal | None | None | scripts/docker_validate_all.sh |
| prime-rl-vllm-sampling-args-token-ids | None | None | scripts/docker_validate_all.sh |
| prime-rl-vlm-debug-num-layers-textconfig | None | None | scripts/docker_validate_all.sh |
| pytorch-fakeprocessgroup-allgather-uneven | None | None | scripts/docker_validate_all.sh |
| pytorch-wheel-tag-minos-validation | None | None | scripts/docker_validate_all.sh |
| ruff-ty-union-alias-attribute-error | None | None | scripts/docker_validate_all.sh |
| ruff-up008-nested-class | None | None | scripts/docker_validate_all.sh |
| sglang-customtestcase-circular-ref | None | None | scripts/docker_validate_all.sh |
| sglang-detokenizer-unbound-fix | None | None | scripts/docker_validate_all.sh |
| sglang-diffusion-dtype-log-aggregation | None | None | scripts/docker_validate_all.sh |
| sglang-fp8-weight-loader | None | None | scripts/docker_validate_all.sh |
| sglang-hfrunner-hang-fix | None | None | scripts/docker_validate_all.sh |
| sglang-jit-kernel-ci-registration | None | None | scripts/docker_validate_all.sh |
| sglang-lazy-import-kda-kernel | None | None | scripts/docker_validate_all.sh |
| sglang-lscpu-topology-fix | None | None | scripts/docker_validate_all.sh |
| sglang-mistral-native-format-detection | None | None | scripts/docker_validate_all.sh |
| sglang-pcg-qo-indptr-padding | None | None | scripts/docker_validate_all.sh |
| sglang-qknorm-split-cta | None | None | scripts/docker_validate_all.sh |
| sglang-routed-experts-base64 | None | None | scripts/docker_validate_all.sh |
| sglang-scheduler-ready-cleanup | None | None | scripts/docker_validate_all.sh |
| sglang-session-mm-leak | None | None | scripts/docker_validate_all.sh |
| sglang-streaming-backlog-warning | None | None | scripts/docker_validate_all.sh |
| sglang-tokenizer-cleanup | None | None | scripts/docker_validate_all.sh |
| slime-cuda-ipc-cache-leak | None | None | scripts/docker_validate_all.sh |
| slime-datasource-prompt-none-crash | None | None | scripts/docker_validate_all.sh |
| slime-encoder-only-attr-missing | None | None | scripts/docker_validate_all.sh |
| slime-fla-gradient-inflation | None | None | scripts/docker_validate_all.sh |
| slime-fp8-qwen35-conv-exclusion | None | None | scripts/docker_validate_all.sh |
| slime-glm4v-moe-bridge-layer-spec | None | None | scripts/docker_validate_all.sh |
| slime-httpx-disable-system-proxy | None | None | scripts/docker_validate_all.sh |
| slime-megatron-lr-scheduler-duplicate | None | None | scripts/docker_validate_all.sh |
| slime-misc-bugfix-cleanup | None | None | scripts/docker_validate_all.sh |
| slime-moe-dispatcher-type-propagate | None | None | scripts/docker_validate_all.sh |
| slime-qwen35-multiturn-loss-mask | None | None | scripts/docker_validate_all.sh |
| slime-remote-kwargs-deepgemm-precompile | None | None | scripts/docker_validate_all.sh |
| slime-rope-theta-parameters-dict | None | None | scripts/docker_validate_all.sh |
| slime-router-pd-disagg-circuit-breaker | None | None | scripts/docker_validate_all.sh |
| slime-vision-nonqwen-fallback | None | None | scripts/docker_validate_all.sh |
| transformers-autoprocessor-hub-kwargs | None | None | scripts/docker_validate_all.sh |
| transformers-dtype-guess-state-dict | None | None | scripts/docker_validate_all.sh |
| transformers-fp8-experts-static-activation | None | None | scripts/docker_validate_all.sh |
| transformers-phi3-batchencoding-sdpa-skip | None | None | scripts/docker_validate_all.sh |
| transformers-sizedict-or-operator | None | None | scripts/docker_validate_all.sh |
| transformers-supports-tp-pp-plan | None | None | scripts/docker_validate_all.sh |
| transformers-tokenizer-hub-class-missing | None | None | scripts/docker_validate_all.sh |
| uv-dist-manifest-checksum-patch | None | None | scripts/docker_validate_all.sh |
| uv-flat-index-lock-contention | None | None | scripts/docker_validate_all.sh |
| uv-freethreaded-macos-download-metadata | None | None | scripts/docker_validate_all.sh |
| uv-freethreaded-python-wheel-error | None | None | scripts/docker_validate_all.sh |
| uv-no-emit-package-comma-delimiter | None | None | scripts/docker_validate_all.sh |
| uv-python-discovery-early-installation | None | None | scripts/docker_validate_all.sh |
| uv-python-preference-consolidation | None | None | scripts/docker_validate_all.sh |
| uv-python-source-explicit-method | None | None | scripts/docker_validate_all.sh |
| uv-run-remote-script-unwrap-panic | None | None | scripts/docker_validate_all.sh |
| uv-wheel-error-pretty-platform | None | None | scripts/docker_validate_all.sh |
| vllm-conch-3d-input-reshape | None | None | scripts/docker_validate_all.sh |
| vllm-cpu-ct-w4a16-kernel | None | None | scripts/docker_validate_all.sh |
| vllm-cpu-skip-set-num-threads | None | None | scripts/docker_validate_all.sh |
| vllm-hermes-parser-stream-interval | None | None | scripts/docker_validate_all.sh |
| vllm-mamba-cudagraph-cache-raise | None | None | scripts/docker_validate_all.sh |
| vllm-model-loader-device-context | None | None | scripts/docker_validate_all.sh |
| vllm-multinode-allreduce-fusion | None | None | scripts/docker_validate_all.sh |
| vllm-renderer-workers-mm-cache | None | None | scripts/docker_validate_all.sh |
| vllm-sliding-window-zero-config | None | None | scripts/docker_validate_all.sh |
| vllm-streaming-toolcall-shared-state | None | None | scripts/docker_validate_all.sh |
| vllm-tool-parser-indexerror | None | None | scripts/docker_validate_all.sh |
| vllm-xpu-graph-default-disable | None | None | scripts/docker_validate_all.sh |

## Failing (201)

| Task | Verdict | Gold | Nop |
|------|---------|------|-----|
| areal-batch-rtensor-http-fetch | fail | None | None |
| areal-fsdp-optimizer-platform-abstraction | fail | None | None |
| areal-lora-xccl-versioning | fail | None | None |
| areal-ppo-token-stats-cp | fail | None | None |
| areal-router-gate-dtensor-hook | fail | None | None |
| areal-rtensor-serialize-interaction-id | fail | None | None |
| bun-braces-empty-input-oob | fail | None | None |
| bun-bundler-barrel-namespace-reexport | fail | None | None |
| bun-capturestacktrace-async-frames | fail | None | None |
| bun-capturestacktrace-materialized-assert | fail | None | None |
| bun-cookiemap-tojson-numeric-crash | fail | None | None |
| bun-domurl-invalid-url-crash | fail | None | None |
| bun-expect-extend-numeric-key-crash | fail | None | None |
| bun-ffi-linksymbols-nonobject-crash | fail | None | None |
| bun-hot-test-stderr-buffer-loss | fail | None | None |
| bun-mysql-per-query-memory-leak | fail | None | None |
| bun-partialdeepstrictequal-array-crash | fail | None | None |
| bun-pipe-objectmode-write-crash | fail | None | None |
| bun-puppeteer-macos-headless-shell | fail | None | None |
| bun-serve-body-leak-asan-skip | fail | None | None |
| bun-stdout-end-flush-truncation | fail | None | None |
| bun-toml-parse-log-deinit-leak | fail | None | None |
| bun-urlpattern-regexp-match-direct | fail | None | None |
| gradio-audio-multimodal-textbox | fail | None | None |
| gradio-browserstate-pydantic-serialization | fail | None | None |
| gradio-cancel-iterator-leak | fail | None | None |
| gradio-chatinterface-edit-disappear | fail | None | None |
| gradio-chatinterface-fill-height-scale | fail | None | None |
| gradio-checkbox-group-api-info | fail | None | None |
| gradio-debug-flag-forward | fail | None | None |
| gradio-generator-cancel-chatinterface | fail | None | None |
| gradio-image-fullscreen-onclick | fail | None | None |
| gradio-mcp-tool-call-latency | fail | None | None |
| gradio-node-server-readiness-race | fail | None | None |
| gradio-on-triggers-type-hints | fail | None | None |
| gradio-tab-toggle-interactivity | fail | None | None |
| gradio-website-markdown-subrequest | fail | None | None |
| nextjs-adapter-dead-suffix-code | fail | None | None |
| nextjs-app-route-encoded-segment | fail | None | None |
| nextjs-cna-skip-prompts-with-flags | fail | None | None |
| nextjs-docker-cache-turbo-corruption | fail | None | None |
| nextjs-instant-navs-devtools-deflake | fail | None | None |
| nextjs-layout-segment-optimization | fail | None | None |
| nextjs-pages-data-content-length-etag | fail | None | None |
| nextjs-prefetch-uri-assertion-flake | fail | None | None |
| nextjs-ts6-baseurl-deprecation | fail | None | None |
| nextjs-turbo-persistence-mmap-alignment | fail | None | None |
| nextjs-turbopack-cell-read-toplevel | fail | None | None |
| nextjs-turbopack-cli-persistent-cache | fail | None | None |
| nextjs-turbopack-graph-span-modules | fail | None | None |
| nextjs-turbopack-lazy-metadata-tla | fail | None | None |
| nextjs-turbopack-loader-runner-layer | fail | None | None |
| openclaw-ci-test-boundary-path-canon | fail | None | None |
| openclaw-config-audit-exec-override | fail | None | None |
| openclaw-debounce-null-text | fail | None | None |
| openclaw-discord-reconnect-crash | fail | None | None |
| openclaw-exec-awk-interpreter-allowlist | fail | None | None |
| openclaw-gemini-provider-aliases | fail | None | None |
| openclaw-media-local-roots-source-expansion | fail | None | None |
| openclaw-msteams-stream-reset | fail | None | None |
| openclaw-msteams-thread-history-authz | fail | None | None |
| openclaw-openai-http-nonowner-ingress | fail | None | None |
| openclaw-plugin-scan-block-install | fail | None | None |
| openclaw-preserve-reply-indentation | fail | None | None |
| openclaw-subagent-duration-display-inflation | fail | None | None |
| openclaw-subagent-tool-resolution | fail | None | None |
| openclaw-synology-webhook-inflight-guard | fail | None | None |
| openclaw-telegram-empty-reply-crash | fail | None | None |
| openclaw-telegram-message-split | fail | None | None |
| openclaw-test-planner-include-file-sharding | fail | None | None |
| openclaw-unhandled-stop-reasons | fail | None | None |
| opencode-changelog-deterministic-commit-range | fail | None | None |
| opencode-effect-timeout-option-rename | fail | None | None |
| opencode-filetree-default-closed-width | fail | None | None |
| opencode-format-childprocess-spawner | fail | None | None |
| opencode-gpt-prompt-model-routing | fail | None | None |
| opencode-markdown-stream-partial-format | fail | None | None |
| opencode-plugin-effect-native | fail | None | None |
| opencode-plugin-install-jsonc-preserve | fail | None | None |
| opencode-plugin-theme-stale-update | fail | None | None |
| opencode-prompt-footer-variant-strip | fail | None | None |
| opencode-session-context-prompt-footer | fail | None | None |
| opencode-session-followup-persist | fail | None | None |
| opencode-slash-cmd-image-preserve | fail | None | None |
| opencode-tui-worker-sse-bypass | fail | None | None |
| opencode-ui-streaming-markdown-cadence | fail | None | None |
| opencode-variant-menu-subagent-info | fail | None | None |
| opencode-vcs-native-spawner | fail | None | None |
| opencode-webui-bundle-win-paths | fail | None | None |
| prime-rl-clean-exit-async-hang | fail | None | None |
| prime-rl-config-none-toml-serialize | fail | None | None |
| prime-rl-dp-pause-resume-deadlock | fail | None | None |
| prime-rl-eval-failed-rollouts-metric | fail | None | None |
| prime-rl-eval-rollout-crash-resilience | fail | None | None |
| prime-rl-eval-samples-table | fail | None | None |
| prime-rl-quack-sft-loss-rmsnorm | fail | None | None |
| prime-rl-sft-hybrid-cp-model-ordering | fail | None | None |
| prime-rl-sft-messages-column-format | fail | None | None |
| prime-rl-sft-vlm-dtype-validation | fail | None | None |
| prime-rl-toml-none-list-serialize | fail | None | None |
| pytorch-from-blob-lambda-deleter | fail | None | None |
| pytorch-graphpickler-ignorerawnode-tests | fail | None | None |
| pytorch-hip-stream-masquerading-include | fail | None | None |
| pytorch-inductor-identity-evalf | fail | None | None |
| pytorch-inductor-mps-half-precision-cast | fail | None | None |
| pytorch-mix-order-reduction-multistage-oom | fail | None | None |
| pytorch-mps-modular-indexing-safe-mod | fail | None | None |
| pytorch-stream-context-reentrance | fail | None | None |
| pytorch-sycl-msvc-include-filter | fail | None | None |
| pytorch-wheel-tag-freethreaded-abi | fail | None | None |
| ruff-annotate-render-perf | fail | None | None |
| ruff-async115-anyio-submodule-import | fail | None | None |
| ruff-era001-ty-ignore-allowlist | fail | None | None |
| ruff-f507-percent-format-nontuple | fail | None | None |
| ruff-furb142-parenthesize-generator | fail | None | None |
| ruff-ipython-percent-foo-parsing | fail | None | None |
| ruff-parser-benchmark-dealloc | fail | None | None |
| ruff-ruf050-parenthesize | fail | None | None |
| sglang-benchmark-random-len-fix | fail | None | None |
| sglang-eagle3-piecewise-cuda-crash | fail | None | None |
| sglang-flux2-tokenization-length | fail | None | None |
| sglang-gc-threshold-arg | fail | None | None |
| sglang-lora-auto-detect-target-modules | fail | None | None |
| sglang-qwen35-pp-cache-moe-fix | fail | None | None |
| sglang-rerun-ut-duplicate-urls | fail | None | None |
| sglang-shm-pointer-repickle-broadcast | fail | None | None |
| sglang-tensor-mismatch-pause | fail | None | None |
| sglang-zmq-localhost-bind | fail | None | None |
| slime-glm4moe-mtp-bridge-dynamic | fail | None | None |
| slime-mla-indexcache-skip-topk | fail | None | None |
| slime-placeholder-metrics-gpqa | fail | None | None |
| slime-qwen35-dense-tp-allreduce-fusion | fail | None | None |
| slime-rollout-make-group-router-params | fail | None | None |
| slime-rope-theta-from-parameters | fail | None | None |
| slime-sglang-epd-encoder-support | fail | None | None |
| slime-sglang-metrics-always-enable | fail | None | None |
| slime-wandb-sglang-metrics | fail | None | None |
| transformers-autoconfig-model-type-override | fail | None | None |
| transformers-camembert-tied-weights | fail | None | None |
| transformers-cb-cudagraph-thread-safety | fail | None | None |
| transformers-cb-return-logprobs | fail | None | None |
| transformers-check-model-inputs-bc-alias | fail | None | None |
| transformers-checkrepo-nested-class-kwargs | fail | None | None |
| transformers-ci-multirunner-failure-check | fail | None | None |
| transformers-ci-testshub-empty-skip | fail | None | None |
| transformers-config-classvar-rope-validation | fail | None | None |
| transformers-config-tokenizer-class-removal | fail | None | None |
| transformers-cpu-grouped-mm-alignment | fail | None | None |
| transformers-dequantize-save-reverse-op | fail | None | None |
| transformers-detr-loss-amp-dtype-crash | fail | None | None |
| transformers-docstring-checker-ast-cache | fail | None | None |
| transformers-embedding-vlm-missing-head | fail | None | None |
| transformers-fa4-kernel-fallback | fail | None | None |
| transformers-fast-image-processor-import | fail | None | None |
| transformers-flash-attn-version-compat | fail | None | None |
| transformers-incorrect-model-list-update | fail | None | None |
| transformers-jitscript-copied-comment-py313 | fail | None | None |
| transformers-lfm2-conv-cache-alignment | fail | None | None |
| transformers-mistral-query-scaling-positions | fail | None | None |
| transformers-model-linter-cache | fail | None | None |
| transformers-mxfp4-dependency-checks | fail | None | None |
| transformers-nemotron-config-docstrings | fail | None | None |
| transformers-nemotron-h-compile-stream | fail | None | None |
| transformers-nemotron-h-tied-weights-modular | fail | None | None |
| transformers-perceiver-interpolate-pos | fail | None | None |
| transformers-qwen2vl-tie-word-embeddings | fail | None | None |
| transformers-rope-params-kwargs | fail | None | None |
| transformers-smollm3-dosample-test-fix | fail | None | None |
| transformers-tokenizer-redundant-parse | fail | None | None |
| transformers-vidproc-pil-import-crash | fail | None | None |
| transformers-xlnet-rope-cpu-forward | fail | None | None |
| uv-abi3-wheel-python-lower-bound | fail | None | None |
| uv-audit-service-format-url | fail | None | None |
| uv-auth-bearer-incomplete-credentials | fail | None | None |
| uv-direct-url-streaming-fallback | fail | None | None |
| uv-dynamic-field-case-sensitive | fail | None | None |
| uv-export-conflict-workspace-deps | fail | None | None |
| uv-index-cache-control-header-error | fail | None | None |
| uv-jj-snapshot-rebuild-churn | fail | None | None |
| uv-publish-hash-progress-bar | fail | None | None |
| uv-remove-dep-comment-preservation | fail | None | None |
| uv-self-update-mirror-fallback | fail | None | None |
| uv-self-update-official-version-resolve | fail | None | None |
| uv-self-update-quiet-stderr-important | fail | None | None |
| uv-system-check-which-portability | fail | None | None |
| uv-tool-list-outdated-settings | fail | None | None |
| uv-torch-rocm72-backend | fail | None | None |
| vllm-abort-test-race-condition | fail | None | None |
| vllm-audio-video-test-determinism | fail | None | None |
| vllm-cohere-embed-system-prompt | fail | None | None |
| vllm-conv3d-torch-version-check | fail | None | None |
| vllm-corrupt-image-valueerror | fail | None | None |
| vllm-eagle-fullcudagraph-stale-attn | fail | None | None |
| vllm-gptq-compile-correctness | fail | None | None |
| vllm-mistral-processor-mm-dispatch | fail | None | None |
| vllm-pooling-cpu-token-ids | fail | None | None |
| vllm-qwen3-dual-stream-compile-regression | fail | None | None |
| vllm-rocm-aiter-state-leak | fail | None | None |
| vllm-transformers-v5-config-fixes | fail | None | None |
| zeroclaw-preserve-channel-config | fail | None | None |
| zeroclaw-trim-oldest-images | fail | None | None |

## Errors (73)

- areal-fsdp-qwenvl-rope-dtype: fail_build
- bun-bundler-css-entrypoint-crash: fail_build
- bun-glob-scan-double-visit: fail_build
- bun-listen-empty-hostname-crash: fail_build
- bun-mock-module-nonstring-crash: fail_build
- gradio-brush-preview-dead-zone: fail_build
- gradio-ci-venv-cache-symlink: fail_build
- gradio-dev-console-log-noise: fail_build
- gradio-heartbeat-task-leak: fail_build
- gradio-subtab-accordion-lazy-load: fail_build
- nextjs-edge-als-test-timeout-race: fail_build
- nextjs-server-action-fallback-shell: fail_build
- nextjs-ts6-module-resolution-defaults: fail_build
- nextjs-turbopack-compact-span-hierarchy: fail_build
- nextjs-turbopack-worker-eval-resolve: fail_build
- nextjs-waitforelement-cross-router-timeout: fail_build
- openclaw-embeddings-http-write-scope: fail_build
- openclaw-http-tool-invoke-auth: fail_build
- openclaw-openresponses-http-owner-escalation: fail_build
- opencode-embedded-webui-serve: fail_build
- opencode-file-appfilesystem-migration: fail_build
- opencode-markdown-streaming-jank: fail_build
- opencode-mockmodule-test-pollution: fail_build
- opencode-model-variant-dialog: error
- opencode-session-token-double-count: fail_build
- opencode-subagent-footer-restore: fail_build
- opencode-theme-kv-default-fallback: fail_build
- pytorch-einops-lrucache-logspam: fail_build
- pytorch-inductor-addmm-half-unfuse: fail_build
- pytorch-inductor-mixorder-contiguity-guard: fail_build
- ruff-f507-zero-placeholder-format: fail_build
- ruff-f811-annotated-redeclaration: fail_build
- ruff-imara-diff-api-upgrade: fail_build
- ruff-lsp-markdown-preview-warning: fail_build
- ruff-ruf073-fstring-percent-format: fail_build
- ruff-sim113-sibling-loop-false-negative: fail_build
- ruff-ty-args-completion-before-paren: fail_build
- ruff-ty-await-type-context: fail_build
- ruff-ty-dataclass-transform-kwargs: fail_build
- ruff-ty-final-declaration-source-span: fail_build
- ruff-ty-functional-typeddict-inherit: fail_build
- ruff-ty-functional-typeddict-qualifiers: fail_build
- ruff-ty-generic-call-expression-cache: fail_build
- ruff-ty-intern-inferable-typevars: fail_build
- ruff-ty-keyword-attribute-completion: fail_build
- ruff-ty-materialize-divergent-alias: fail_build
- ruff-ty-nonterminal-call-shortcut: fail_build
- ruff-ty-pep695-type-qualifier-ban: fail_build
- ruff-ty-remove-multi-inference-state: fail_build
- ruff-ty-typeddict-get-default-context: fail_build
- ruff-ty-typeddict-pop-default-context: fail_build
- ruff-ty-typeddict-union-dict-eager-diag: fail_build
- ruff-typeddict-name-mismatch-diagnostic: fail_build
- ruff-up008-lambda-scope: fail_build
- ruff-w391-consecutive-empty-cell-panic: fail_build
- sglang-amd-ci-git-safe-directory: fail_build
- sglang-diffusion-ci-import-path: fail_build
- sglang-diffusion-dashboard-charts: fail_build
- sglang-flashmla-version-rollback: fail_build
- sglang-mistral-ci-ratelimit-patch: fail_build
- sglang-wheel-metadata-cuda-suffix: fail_build
- slime-opd-multimodal-image-payload: fail_build
- transformers-granite-config-int-multiplier: fail_build
- transformers-imgproc-fast-import-compat: fail_build
- transformers-processor-chat-template-kwargs: fail_build
- transformers-processor-deepcopy-perf: fail_build
- transformers-sizedict-get-size-dict-input: fail_build
- uv-cpuinfo-aarch64-hardfloat-detect: fail_build
- uv-trampoline-pe-write-error: fail_build
- vllm-rocm-uv-curl-failure: fail_build
- vllm-splade-pooler-test-metadata: fail_build
- zeroclaw-atomic-tool-history-pruning: fail_build
- zeroclaw-max-history-messages: fail_build
