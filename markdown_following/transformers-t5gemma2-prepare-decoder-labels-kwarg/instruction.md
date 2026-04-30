# T5Gemma2: `prepare_decoder_input_ids_from_labels` is broken when called from `DataCollatorForSeq2Seq`

You are working in the `huggingface/transformers` repository. The repo is
checked out at `/workspace/transformers`.

## Symptom

`DataCollatorForSeq2Seq` (in `src/transformers/data/data_collator.py`) calls
the model's `prepare_decoder_input_ids_from_labels` method with the keyword
argument `labels=...`:

```python
decoder_input_ids = self.model.prepare_decoder_input_ids_from_labels(labels=batch["labels"])
```

For the **T5Gemma2** model, this call raises `TypeError`:

```
TypeError: T5Gemma2PreTrainedModel.prepare_decoder_input_ids_from_labels()
got an unexpected keyword argument 'labels'
```

The method is otherwise behaviorally correct: when called positionally with
a tensor, it shifts the tensor right, prepends `decoder_start_token_id`
(the decoder's `bos_token_id`), and replaces any `-100` entries (introduced
by the loss-masking convention) with `pad_token_id`. That shift behavior
must be preserved exactly.

The expected contract:
- Calling the method with a `labels=<tensor>` kwarg must succeed.
- For `bos_token_id=0`, `pad_token_id=1`, and input `[[10, 20, 30, 40]]`,
  the returned tensor must equal `[[0, 10, 20, 30]]`.
- For input `[[1, 2, -100, 4]]` with `bos=0, pad=7`, the returned tensor
  must equal `[[0, 1, 2, 7]]` (the `-100` is shifted into position 3 and
  replaced with `pad_token_id=7`).

Other models in the repo (e.g. `T5`) name this method's parameter `labels`,
which is what makes them compatible with the data collator. T5Gemma2 is the
outlier — bring it in line.

## Scope

- The fix lives in the T5Gemma2 model files under
  `src/transformers/models/t5gemma2/`.
- Per repository convention (see `.ai/AGENTS.md` and
  `.github/copilot-instructions.md`), when a `modular_<name>.py` file is
  present, source edits should be made in the modular file and
  `make fixup` / `make fix-repo` is responsible for syncing the generated
  `modeling_<name>.py`. Both files must remain consistent with each other.
- Do **not** alter the shift / pad-replacement behavior; only the calling
  contract is broken.
- Do not modify `DataCollatorForSeq2Seq` or any other model's
  `prepare_decoder_input_ids_from_labels` — only T5Gemma2 is affected.

## Code Style Requirements

The repo enforces style and consistency in CI. Before considering the
patch done, ensure:

- The modular file (`modular_t5gemma2.py`) and the generated modeling file
  (`modeling_t5gemma2.py`) are in sync. Run `make fixup` (or
  `make fix-repo`) if you have only edited the modular file.
- `ruff` formatting and linting must still pass (`make style`).
