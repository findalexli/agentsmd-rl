# improve model docs

Source: [browser-use/browser-use#4616](https://github.com/browser-use/browser-use/pull/4616)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/open-source/references/models.md`

## What to add / change

In response to #4214

<!-- This is an auto-generated description by cubic. -->
## Summary by cubic
Revamped the LLM model docs with a quick-reference table, use‑case recommendations, and clearer provider setup. Adds native coverage for more providers, updates examples, and improves env/installation guidance.

- **Refactors**
  - Added Quick Reference (provider → class → env) and use‑case picks based on benchmarks.
  - Renamed to “Browser Use Cloud,” updated pricing/models, and listed `browser-use/bu-30b-a3b-preview`.
  - Expanded provider docs: DeepSeek, Mistral, Cerebras, OpenRouter, LiteLLM; improved OpenAI/Anthropic/Gemini/Azure/Bedrock/Vercel/OCI guidance with links.
  - Standardized examples to `Agent` + `Chat*` classes and noted key env vars.
  - Moved OpenRouter out of OpenAI-compatible section; trimmed/reorganized OpenAI-compatible examples.
  - Minor fixes: `GOOGLE_API_KEY` deprecation note, Anthropic coordinate clicking note, “LangChain” capitalization.

<sup>Written for commit c1151715d35810aa7149f2b66af035e3be76c540. Summary will update on new commits.</sup>

<!-- End of auto-generated description by cubic. -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
