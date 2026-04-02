# EPD (Encoder-Prefill-Decode) Disaggregation Support for Slime's SGLang Backend

## Problem

The slime framework's SGLang backend supports prefill-decode (PD) disaggregation, where prefill and decode phases run on separate GPU groups. However, vision-language models with heavy encoder components benefit from further disaggregating the encoder into its own phase — an Encoder-Prefill-Decode (EPD) setup where encoder engines run independently, prefill engines operate in language-only mode, and decode engines handle token generation.

Currently, this is not possible because:

1. **Config validation rejects encoder worker type** — `ServerGroupConfig` in `slime/backends/sglang_utils/sglang_config.py` only accepts `regular`, `prefill`, `decode`, and `placeholder` as valid `worker_type` values. There is no way to declare an encoder-only GPU group in the YAML config.

2. **Engine adapter has no encoder awareness** — `HttpServerEngineAdapter` in `slime/backends/sglang_utils/sglang_engine.py` treats all engines the same: same server launch path, same router registration, same shutdown sequence. Encoder engines need a different launch entry point (`encode_server` instead of `http_server`), should skip router registration, and need a method to expose their URL so prefill engines can connect to them.

3. **Rollout startup is single-phase** — `start_rollout_servers()` in `slime/ray/rollout.py` starts all engine groups in a single pass. For EPD, encoders must start first and complete initialization so their URLs can be collected and passed to prefill engine groups (as `encoder_urls` and `language_only` overrides).

4. **Config override key format mismatch** — The `_compute_server_args()` function in `sglang_engine.py` applies YAML overrides to `ServerArgs` fields, but doesn't account for key format differences. If a YAML config uses one key convention (e.g., with hyphens) while `ServerArgs` uses another (underscores), the override silently fails to match, producing confusing unused-key warnings.

## Scope

The changes span three files:
- `slime/backends/sglang_utils/sglang_config.py` — config model and validation
- `slime/backends/sglang_utils/sglang_engine.py` — engine adapter and server arg computation
- `slime/ray/rollout.py` — rollout server startup orchestration

## Expected Behavior

- YAML configs with `worker_type: encoder` groups should be accepted and correctly parsed
- The config should expose whether EPD disaggregation is active
- Encoder engines should launch with the correct server entry point and skip inapplicable post-init steps
- Engine startup should be phased: encoders first, then non-encoder groups with encoder URLs injected into prefill groups
- Config override keys should be normalized so both hyphenated and underscored styles work
