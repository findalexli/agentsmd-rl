There is a crash in SGLang's piecewise CUDA graph initialization when using speculative decoding with certain draft models.

The function `init_piecewise_cuda_graphs()` in `python/sglang/srt/model_executor/model_runner.py` assumes that the resolved language model always has a `.layers` attribute on `language_model.model`. However, some draft models (such as the EAGLE3 draft model architecture) use a different internal structure — for example, a single "midlayer" instead of a standard list of transformer layers.

When `enforce_piecewise_cuda_graph=True` is used alongside EAGLE3 speculative decoding, the draft model's runner also calls `init_piecewise_cuda_graphs()`. Since the draft model lacks the expected `.layers` attribute, the code crashes with an `AttributeError` when it tries to iterate over `language_model.model.layers`.

Fix `init_piecewise_cuda_graphs()` so that it handles models that do not have a `layers` attribute gracefully, rather than crashing.
