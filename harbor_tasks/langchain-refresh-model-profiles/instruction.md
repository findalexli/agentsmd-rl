# Refresh Model Profile Data for Partner Integrations

## Problem

The model profile data for several LangChain partner integrations is out of date. Model profiles are stored in `_profiles.py` files within each partner package's data directory (under `libs/partners/`) and contain capability metadata for each model (context windows, supported modalities, tool calling, etc.). The `_PROFILES` dictionary in each file maps model IDs to their spec dicts.

Three partner packages need attention: **mistralai**, **openai**, and **openrouter**.

## Issues

### MistralAI — Missing Model and Outdated Specs

1. A recently released model with ID `mistral-small-2603` is missing from the profiles. Its display name is `"Mistral Small 4"`. The required specs for this entry are:
   - `max_input_tokens`: `256000`
   - `max_output_tokens`: `256000`
   - `reasoning_output`: `True`
   - `tool_calling`: `True`

2. The existing `mistral-small-latest` entry has outdated specifications that no longer match the current model. The following fields need to be updated to:
   - `max_input_tokens`: `256000`
   - `max_output_tokens`: `256000`
   - `reasoning_output`: `True`
   - `attachment`: `True`

### OpenAI — Missing Model

3. A recently released model with ID `gpt-5.3-chat-latest` is missing from the profiles. Its display name is `"GPT-5.3 Chat (latest)"`. The required specs for this entry are:
   - `max_input_tokens`: `128000`
   - `max_output_tokens`: `16384`
   - `tool_calling`: `True`
   - `structured_output`: `True`

### OpenRouter — Incorrect Model ID

4. The free variant of the Nemotron model has an incorrect model ID. The current entry uses `nvidia/nemotron-3-super-120b-a12b-free` (hyphen before `free`), but the correct ID is `nvidia/nemotron-3-super-120b-a12b:free` (colon before `free`).

## Data Structure

Each model profile entry is a dictionary with the model ID as the key and a dictionary of specs:

```python
"model-id": {
    "name": "Display Name",
    "release_date": "YYYY-MM-DD",
    "last_updated": "YYYY-MM-DD",
    "open_weights": bool,
    "max_input_tokens": int,
    "max_output_tokens": int,
    "text_inputs": bool,
    "image_inputs": bool,
    "audio_inputs": bool,
    "video_inputs": bool,
    "text_outputs": bool,
    "image_outputs": bool,
    "audio_outputs": bool,
    "video_outputs": bool,
    "reasoning_output": bool,
    "tool_calling": bool,
    "attachment": bool,
    "temperature": bool,
    # OpenAI models also include: structured_output, image_url_inputs, pdf_inputs, pdf_tool_message, image_tool_message, tool_choice
}
```

## Success Criteria

Your changes should:
1. Add the missing model entries with correct specifications
2. Update `mistral-small-latest` with current capability data
3. Fix the OpenRouter model ID
4. Maintain valid Python syntax in all modified files
5. Preserve the ability to import the `_PROFILES` dictionary from each module
