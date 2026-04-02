# Mistral Multimodal Processors Broken Under Transformers v5

## Problem

After upgrading to Transformers v5, Pixtral (vision) and Voxtral (audio) models fail to process multimodal inputs. The image processor and audio feature extractor are silently skipped — text tokens are generated but no multimodal keyword arguments are produced.

Errors observed:

```
RuntimeError: Expected there to be 3 image items in keyword arguments
corresponding to 3 image data items, but only found 0!
```

```
IndexError: list index out of range
```

The root cause is how Transformers v5's `ProcessorMixin` decides which processor components to invoke. It inspects the processor class constructor signature to discover components. If a component (like `image_processor` or `feature_extractor`) isn't visible as a constructor parameter, Transformers assumes it doesn't exist and skips calling it entirely.

## Affected Files

- `vllm/transformers_utils/processors/pixtral.py` — `MistralCommonPixtralProcessor` class
- `vllm/transformers_utils/processors/voxtral.py` — `MistralCommonVoxtralProcessor` class
- `vllm/model_executor/models/pixtral.py` — Pixtral model info class
- `vllm/model_executor/models/voxtral.py` — Voxtral model info class

## What Needs to Change

The processor classes need their constructors updated so that Transformers v5 can discover the multimodal components through signature introspection. The model info classes that instantiate these processors also need corresponding updates to provide the components correctly.
