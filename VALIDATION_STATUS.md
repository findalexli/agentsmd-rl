# Validated Tasks Summary

Generated: 2026-03-29T02:01:55-07:00

## Passing Tasks (oracle=1.0, nop<1.0): 55

| Task | Oracle | Nop | Repo |
|------|--------|-----|------|
| areal-lora-alias-handling | 1.0000 | 0.5000 | areal |
| areal-pil-image-serialization | 1.0000 | 0.0000 | areal |
| areal-ppo-token-stats-cp | 1.00 | 0.20 | areal |
| areal-rpc-error-response-key | 1.0000 | 0.2500 | areal |
| areal-socket-bind-failure-cleanup | 1.0000 | 0.5000 | areal |
| areal-streaming-response-handler | 1.0000 | 0.5000 | areal |
| gradio-checkbox-group-api-info | 1.00 | 0.45 | gradio |
| gradio-dataframe-nan-sort | 1.00 | 0.30 | gradio |
| gradio-duplicate-block-error-reload | 1.00 | 0.35 | gradio |
| gradio-generator-cancel-chatinterface | 1.00 | 0.45 | gradio |
| gradio-mcp-tool-call-latency | 1.00 | 0.45 | gradio |
| gradio-on-triggers-type-hints | 1.00 | 0.20 | gradio |
| gradio-spaces-reloader-config | 1.00 | 0.45 | gradio |
| gradio-submit-button-example-click | 1.00 | 0.70 | gradio |
| gradio-sync-generator-cancel-valueerror | 1.00 | 0.25 | gradio |
| nextjs-ts6-baseurl-deprecation | 1.00 | 0.25 | nextjs |
| opencode-overflow-error-patterns | 1.00 | 0.30 | opencode |
| opencode-persist-queued-followups | 1.00 | 0.25 | opencode |
| opencode-plugin-async-hooks | 1.00 | 0.35 | opencode |
| ruff-furb142-parenthesize-generator | 1.0000 | 0.1000 | ruff |
| ruff-ruf050-parenthesize | 1.0000 | 0.3000 | ruff |
| ruff-up008-lambda-scope | 1.0000 | 0.3000 | ruff |
| ruff-up008-nested-class | 1.0000 | 0.1000 | ruff |
| sglang-benchmark-empty-prompt | 1.00 | 0.45 | sglang |
| sglang-benchmark-random-len-fix | 1.0 | 0.45 | sglang |
| sglang-dbrx-model-bug | 1.0 | 0.45 | sglang |
| sglang-detokenizer-unbound-fix | 1.0000 | 0.3500 | sglang |
| sglang-flux2-tokenization-length | 1.00 | 0.60 | sglang |
| sglang-hfrunner-hang-fix | 1.00 | 0.65 | sglang |
| sglang-lazy-import-kda-kernel | 1.0 | 0.45 | sglang |
| sglang-lscpu-topology-fix | 1.0 | 0.6 | sglang |
| slime-encoder-only-attr-missing | 1.0000 | 0.3500 | slime |
| slime-fla-gradient-inflation | 1.0000 | 0.0000 | slime |
| slime-httpx-disable-system-proxy | 1.0000 | 0.0000 | slime |
| slime-misc-bugfix-cleanup | 1.0000 | 0.3500 | slime |
| slime-rope-theta-from-parameters | 1.0000 | 0.0000 | slime |
| transformers-afmoe-layer-types-hint | 1.00 | 0.20 | transformers |
| transformers-autoprocessor-hub-kwargs | 1.00 | 0.65 | transformers |
| transformers-deepseek-tokenizer-class | 1.00 | 0.20 | transformers |
| transformers-dtype-guess-state-dict | 1.00 | 0.45 | transformers |
| transformers-fast-image-processor-import | 1.0000 | 0.3500 | transformers |
| transformers-gptneox-rotary-pct-save | 1.00 | 0.20 | transformers |
| transformers-granite-config-type-hints | 1.00 | 0.20 | transformers |
| transformers-jit-script-comment-py313 | 1.0000 | 0.3000 | transformers |
| transformers-perceiver-interpolate-pos | 1.0000 | 0.3000 | transformers |
| transformers-processor-deepcopy-perf | 1.0000 | 0.3000 | transformers |
| transformers-rope-params-kwargs | 1.00 | 0.20 | transformers |
| transformers-serve-kv-cache-indexing | 1.00 | 0.40 | transformers |
| transformers-set-encoder-fix | 1.00 | 0.45 | transformers |
| transformers-xlnet-rope-cpu-forward | 1.00 | 0.15 | transformers |
| vllm-hermes-parser-stream-interval | 1.0 | 0.6 | vllm |
| vllm-renderer-workers-mm-cache | 1.00 | 0.60 | vllm |
| vllm-tool-parser-indexerror | 1.00 | 0.40 | vllm |
| vllm-triton-cache-autotuning | 1.0000 | 0.6000 | vllm |
| vllm-xgrammar-fstring-prefix | 1.0 | 0.45 | vllm |

## Failing Tasks (need fix): 28

| Task | Oracle | Nop | Issue |
|------|--------|-----|-------|
| areal-batch-rtensor-http-fetch | 0.55 | 0.20 | oracle!=1.0 |
| areal-lora-xccl-versioning | 0.4500 | 0.4500 | oracle!=1.0 |
| gradio-absolute-path-windows | 0.75 | 0.55 | oracle!=1.0 |
| gradio-browserstate-pydantic-serialization | 0.30 | 0.20 | oracle!=1.0 |
| gradio-button-scale-parameter | 0.80 | 0.00 | oracle!=1.0 |
| gradio-connection-lost-error-handling | 0.35 | 0.35 | oracle!=1.0 |
| nextjs-layout-segment-optimization | 0.30 | 0.00 | oracle!=1.0 |
| nextjs-turbopack-duplicate-module-bail | 0.75 | 0.35 | oracle!=1.0 |
| openclaw-clawhub-archive-sanitize |  |  | oracle!=1.0 |
| openclaw-debounce-null-text |  |  | oracle!=1.0 |
| openclaw-discord-require-mention-bypass |  |  | oracle!=1.0 |
| openclaw-gemini-provider-aliases |  |  | oracle!=1.0 |
| openclaw-preserve-reply-indentation |  |  | oracle!=1.0 |
| openclaw-subagent-tool-resolution |  |  | oracle!=1.0 |
| openclaw-telegram-empty-reply-crash |  |  | oracle!=1.0 |
| openclaw-telegram-message-split |  |  | oracle!=1.0 |
| openclaw-unhandled-stop-reasons |  | 0.0 | oracle!=1.0 |
| openclaw-zsh-compdef-defer |  |  | oracle!=1.0 |
| pytorch-fakeprocessgroup-allgather-uneven | 0.1500 | 0.1500 | oracle!=1.0 |
| pytorch-inductor-identity-evalf | 0.4000 | 0.2500 | oracle!=1.0 |
| sglang-tensor-mismatch-pause | 0.60 | 0.60 | oracle!=1.0 |
| slime-megatron-lr-scheduler-duplicate | 0.7000 | 0.0000 | oracle!=1.0 |
| slime-moe-dispatcher-type-propagate | 0.0000 | 0.0000 | oracle!=1.0 |
| slime-wandb-sglang-metrics | 0.40 | 0.20 | oracle!=1.0 |
| transformers-camembert-tied-weights | 0.20 | 0.20 | oracle!=1.0 |
| transformers-mxfp4-dependency-checks | 0.3500 | 0.3500 | oracle!=1.0 |
| transformers-supports-tp-pp-plan | 0.20 | 0.20 | oracle!=1.0 |
| vllm-eagle3-norm-before-fc | 0.0 | 0.4 | oracle!=1.0 |

## Error Tasks: 9
- areal-router-gate-dtensor-hook
- nextjs-turbo-persistence-mmap-alignment
- openclaw-discord-reconnect-crash
- openclaw-msteams-stream-reset
- pytorch-stream-context-reentrance
- ruff-f507-percent-format-nontuple
- slime-rope-theta-parameters-dict
- vllm-cohere-embed-system-prompt
- vllm-multinode-allreduce-fusion
