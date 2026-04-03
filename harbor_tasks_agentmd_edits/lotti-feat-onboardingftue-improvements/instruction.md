# Streamline FTUE Prompt Setup and Add Linux Whisper Support

## Problem

The Gemini first-time user experience (FTUE) setup currently creates **18 prompts** — two variants (Flash and Pro) for each of the 9 prompt types. This is excessive; many tasks don't benefit from having both model variants. The setup dialog incorrectly claims it will create 18 prompts.

Additionally, the Gemini setup prompt modal cannot be temporarily dismissed. If a user taps outside the dialog, it counts as a permanent dismissal, meaning they won't see it again on next launch. Users should be able to close the modal without permanently opting out.

Finally, the `whisper_server` only has requirements files for CUDA and Apple Silicon. There is no `requirements_linux.txt` for generic Linux installations without CUDA, and the whisper server README only documents a single installation path.

## Expected Behavior

1. **Reduce FTUE prompts from 18 to 9** with optimized model assignments:
   - **Pro** for tasks needing complex reasoning: Checklists, Coding Prompts, Image Prompts
   - **Flash** for fast processing tasks: Audio Transcription, Task Summary, Image Analysis
   - **Nano Banana Pro (image model)** for Cover Art generation
   - Each prompt type should have only ONE variant, not two

2. **Make the setup modal temporarily dismissible**: tapping outside the dialog should close it without permanently dismissing it (the modal should reappear on next app launch). The dialog should support three states: set up (true), permanently dismiss (false), and temporary dismiss (null/tapped outside).

3. **Add Linux requirements file**: create `whisper_server/requirements_linux.txt` with simplified dependencies appropriate for Linux without CUDA (no flash-attn, no bitsandbytes). After creating the file, update the whisper server documentation to reflect all three platform options.

## Files to Look At

- `lib/features/ai/ui/settings/services/provider_prompt_setup_service.dart` — FTUE prompt config list and auto-selection logic
- `lib/features/ai/ui/settings/widgets/ftue_setup_dialog.dart` — setup dialog UI text showing prompt count
- `lib/features/ai/ui/settings/widgets/gemini_setup_prompt_modal.dart` — modal dismissal behavior
- `whisper_server/requirements.txt` and `whisper_server/requirements_apple_silicon.txt` — existing requirements files to reference
- `whisper_server/README.md` — documentation to update with platform-specific instructions
