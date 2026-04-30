# Fix T5Gemma2 prepare_decoder_input_ids_from_labels

## Problem

The `prepare_decoder_input_ids_from_labels` method in T5Gemma2's model classes does not work correctly with HuggingFace's standard `DataCollatorForSeq2Seq`. The data collator passes the labels tensor as a keyword argument, but the method's parameter signature does not match what the collator provides, causing a `TypeError` at runtime.

## What is broken

When using `DataCollatorForSeq2Seq` to prepare training data for a T5Gemma2 encoder-decoder model, calling `model.prepare_decoder_input_ids_from_labels(labels=labels_tensor)` raises a `TypeError` about an unexpected keyword argument. The data collator passes the labels tensor as a keyword argument named `labels`, but the method's parameter signature does not accept a keyword argument with that name, so the call fails.

## What should happen

The method should accept its input tensor when called with the keyword argument `labels=` (consistent with the method name "from_labels" and with how other models in the library implement this method). The function's internal behavior — shifting input IDs to the right, prepending `decoder_start_token_id`, and replacing `-100` values with `pad_token_id` — should remain unchanged.

## Files to modify

You will need to edit both:
1. The modular definition file for T5Gemma2 (contains the canonical method definition)
2. The generated modeling file for T5Gemma2 (propagated from the modular file)

The method `prepare_decoder_input_ids_from_labels` lives in the `T5Gemma2PreTrainedModel` class. It accesses `self.config.decoder` for `bos_token_id` and `pad_token_id`.

## Verification

After making changes, verify that:
- `model.prepare_decoder_input_ids_from_labels(labels=some_tensor)` works when called with the keyword argument `labels=`
- The output has the same shape as the input
- The first position of each sequence contains the `decoder_start_token_id`
- Positions 1..N contain the input token IDs shifted right
- Any `-100` values in the input are replaced with `pad_token_id`

## Code Style Requirements

- Run `ruff check` on any files you modify. All code must pass the ruff linter checks as configured in the project's `pyproject.toml`.
