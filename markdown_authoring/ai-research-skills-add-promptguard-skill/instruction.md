# Add prompt-guard skill

Source: [Orchestra-Research/AI-Research-SKILLs#19](https://github.com/Orchestra-Research/AI-Research-SKILLs/pull/19)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `07-safety-alignment/prompt-guard/SKILL.md`

## What to add / change

#### Coverage

This skill provides comprehensive guidance for implementing **Meta's Prompt Guard (86M)**. It covers:

* Real-time jailbreak detection for user inputs.
* Indirect injection filtering for RAG pipelines and third-party API data.
* Batch processing workflows for high-throughput document scanning.
* Multi-layered defense strategies combining Prompt Guard with LlamaGuard.
* Technical solutions for common issues like 512-token truncation and false positives in security contexts.

#### Source

* **Documentation**: Meta Llama-Cookbook (Responsible AI section)
* **GitHub**: meta-llama/llama-cookbook
* **Model**: meta-llama/Prompt-Guard-86M on HuggingFace

#### Documentation Size

* **SKILL.md**: ~300 lines

#### Key Features Included

* ✅ **YAML Frontmatter**: Fully compliant with kebab-case name and Title Case tags.
* ✅ **Actionable Workflows**: 3 distinct, copy-pasteable Python workflows for different security layers.
* ✅ **Performance Benchmarks**: Detailed TPR/FPR stats and hardware requirement tables (CPU vs GPU).
* ✅ **Threshold Guidance**: Recommended settings for Banking (High Security) vs. Research (Low Friction) use cases.
* ✅ **Best Practices**: Sliding window implementation for long-form content.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
