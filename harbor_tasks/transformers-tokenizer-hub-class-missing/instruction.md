# Missing model types in tokenizer Hub compatibility override list

## Bug description

When `AutoTokenizer.from_pretrained()` is called for certain model families, the Hub-hosted `tokenizer_config.json` file specifies an incorrect or outdated `tokenizer_class` value. To handle this, the library maintains an override mechanism: model types whose Hub configs have incorrect tokenizer classes are registered in a set; when such a model type is encountered, `AutoTokenizer` falls back to `TokenizersBackend` instead of using the Hub's class name.

Several model type identifiers are missing from this override set, causing tokenizer loading failures for those model families.

## Expected behavior

All model type identifiers with known incorrect Hub tokenizer classes must be present in the override set so that `AutoTokenizer` falls back to `TokenizersBackend` for these models. Specifically, the following identifiers must be added:

- `deepseek_v2`
- `deepseek_v3`
- `modernbert`

Existing entries must be preserved (do not remove): `arctic`, `chameleon`, `deepseek_vl`, `deepseek_vl_v2`, `fuyu`, `jamba`, `llava`, `phi3`.