# Added CLAUDE.md

Source: [wvabrinskas/Neuron#122](https://github.com/wvabrinskas/Neuron/pull/122)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Added CLAUDE.md rules file

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> Adds `CLAUDE.md` documenting build/test commands, architecture, debugging, and performance guidance for the Neuron Swift ML framework.
> 
> - **Documentation**:
>   - Adds `CLAUDE.md` with:
>     - **Build & Test**: Commands for building, testing, and release performance notes; onboarding script.
>     - **Architecture Overview**: `Tensor`, `Layers`, `Trainable` (`Sequential`), `Optimizers` (`Adam`, `SGD`, `RMSProp`), `Models`, `Devices`.
>     - **Gradient System**: Tensor graph/backprop, gradient retrieval, multi-branch support.
>     - **Development Guides**: Templates/instructions for new layers, optimizers, trainables; code style; dependencies; branch strategy.
>     - **Debugging Guide**: Gradient flow, shape mismatches, training/loss/metrics tips, weight init, multithreading.
>     - **Performance & Memory Profiling**: Timing, memory practices, concurrency, Instruments setup, optimization checkpoints/examples.
> 
> <sup>Written by [Cursor Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit 6a2771cb9280ee790b8374320b75fcd8f3e2ddab. This will update automatically on new commits. Configure [here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
