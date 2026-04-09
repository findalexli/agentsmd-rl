#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotent: skip if already applied
if grep -q 'train_sampling_strategy' src/transformers/training_args.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply all code + doc changes via Python for reliable multi-line handling
python3 << 'PYEOF'
from pathlib import Path

# === src/transformers/training_args.py ===
f = Path('src/transformers/training_args.py')
src = f.read_text()

# 1. Replace docstring for group_by_length -> train_sampling_strategy
src = src.replace(
    '        group_by_length (`bool`, *optional*, defaults to `False`):\n'
    '            Whether or not to group together samples of roughly the same length in the training dataset (to minimize\n'
    '            padding applied and be more efficient). Only useful if applying dynamic padding.',
    '        train_sampling_strategy (`str`, *optional*, defaults to `"random"`):\n'
    '            The sampler to use for the training dataloader. Possible values are:\n'
    '\n'
    '                - `"random"`: Uses `RandomSampler` (default).\n'
    '                - `"sequential"`: Uses `SequentialSampler`.\n'
    '                - `"group_by_length"`: Uses `LengthGroupedSampler` to group samples of roughly the same length\n'
    '                  together (to minimize padding and be more efficient).\n'
    '\n'
    '            Note: When using an `IterableDataset`, this argument is ignored.',
    1
)

# 2. Replace length_column_name docstring reference
src = src.replace(
    'than computing them on train startup. Ignored unless `group_by_length` is `True` and the dataset is an\n'
    '            instance of `Dataset`.',
    'than computing them on train startup. Ignored unless `train_sampling_strategy` is `"group_by_length"` and the dataset\n'
    '            is an instance of `Dataset`.',
    1
)

# 3. Replace field definition
src = src.replace(
    '    group_by_length: bool = field(\n'
    '        default=False,\n'
    '        metadata={\n'
    '            "help": "Whether or not to group samples of roughly the same length together when batching. Only useful if applying dynamic padding."\n'
    '        },\n'
    '    )',
    '    train_sampling_strategy: str = field(\n'
    '        default="random",\n'
    '        metadata={\n'
    '            "help": "Sampler for training: \'random\' (default), \'sequential\', or \'group_by_length\'.",\n'
    '            "choices": ["random", "sequential", "group_by_length"],\n'
    '        },\n'
    '    )',
    1
)

# 4. Replace length_column_name metadata
src = src.replace(
    '        metadata={"help": "Column name for precomputed lengths. Ignored unless `group_by_length` is True."},',
    '        metadata={\n'
    '            "help": "Column name for precomputed lengths. Ignored unless `train_sampling_strategy` is \'group_by_length\'."\n'
    '        },',
    1
)

f.write_text(src)
print(f"Updated {f}")

# === src/transformers/trainer.py ===
f = Path('src/transformers/trainer.py')
src = f.read_text()

# 1. Replace _validate_args: ValueError -> logger.info
src = src.replace(
    '        if (\n'
    '            self.train_dataset is not None\n'
    '            and isinstance(self.train_dataset, torch.utils.data.IterableDataset)\n'
    '            and args.group_by_length\n'
    '        ):\n'
    '            raise ValueError("the `--group_by_length` option is only available for `Dataset`, not `IterableDataset")',
    '\n'
    '        if self.train_dataset is not None and isinstance(self.train_dataset, torch.utils.data.IterableDataset):\n'
    '            logger.info(\n'
    "                f\"The `train_sampling_strategy='{args.train_sampling_strategy}'` option is ignored when using an `IterableDataset`. \"\n"
    '                "Samplers cannot be used with IterableDataset as they require indexed access to the dataset."\n'
    '            )',
    1
)

# 2. Replace _get_train_sampler: group_by_length -> train_sampling_strategy
src = src.replace(
    '        if self.args.group_by_length:\n'
    '            if is_datasets_available() and isinstance(train_dataset, datasets.Dataset)',
    '        if self.args.train_sampling_strategy == "group_by_length":\n'
    '            if is_datasets_available() and isinstance(train_dataset, datasets.Dataset)',
    1
)

# 3. Add sequential sampler branch (remove blank line, add elif)
src = src.replace(
    '                model_input_name=model_input_name,\n'
    '            )\n'
    '\n'
    '        else:\n'
    '            return RandomSampler(train_dataset)',
    '                model_input_name=model_input_name,\n'
    '            )\n'
    '        elif self.args.train_sampling_strategy == "sequential":\n'
    '            return SequentialSampler(train_dataset)\n'
    '        else:\n'
    '            return RandomSampler(train_dataset)',
    1
)

# 4. Replace _get_eval_sampler: group_by_length -> train_sampling_strategy
src = src.replace(
    '        if self.args.group_by_length:\n'
    '            if is_datasets_available() and isinstance(eval_dataset, datasets.Dataset)',
    '        if self.args.train_sampling_strategy == "group_by_length":\n'
    '            if is_datasets_available() and isinstance(eval_dataset, datasets.Dataset)',
    1
)

f.write_text(src)
print(f"Updated {f}")

# === Documentation: ASR docs across all languages ===
for lang in ['en', 'es', 'ja', 'ko', 'zh']:
    f = Path(f'docs/source/{lang}/tasks/asr.md')
    src = f.read_text()
    src = src.replace('group_by_length=True', 'train_sampling_strategy="group_by_length"', 1)
    f.write_text(src)
    print(f"Updated {f}")

# === Documentation: Speech recognition README ===
f = Path('examples/pytorch/speech-recognition/README.md')
src = f.read_text()
src = src.replace('\t--group_by_length', '\t--train_sampling_strategy group_by_length')
f.write_text(src)
print(f"Updated {f}")

# === Test files ===
for tf in ['tests/deepspeed/test_deepspeed.py', 'tests/extended/test_trainer_ext.py']:
    f = Path(tf)
    src = f.read_text()
    src = src.replace('--group_by_length', '--train_sampling_strategy group_by_length')
    f.write_text(src)
    print(f"Updated {f}")

print("All files updated successfully.")
PYEOF

echo "Patch applied successfully."
