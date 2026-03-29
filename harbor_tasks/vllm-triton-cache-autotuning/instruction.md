# Enable Triton Autotuning Disk Cache by Default

vllm's Triton kernels re-run autotuning on every process restart, adding significant latency to the first inference request. Enable Triton's autotuning disk cache by default in `vllm/env_override.py` by setting the `TRITON_CACHE_AUTOTUNING` environment variable. Use `os.environ.setdefault` so users can still opt out by explicitly setting `TRITON_CACHE_AUTOTUNING=0`.
