"""
Task: lotti-feat-onboardingftue-improvements
Repo: lotti @ ec20c573a3147a0d5d68fcb7bbd76023bf6727f2
PR:   2590

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/lotti"

SETUP_SERVICE = Path(REPO) / "lib/features/ai/ui/settings/services/provider_prompt_setup_service.dart"
FTUE_DIALOG = Path(REPO) / "lib/features/ai/ui/settings/widgets/ftue_setup_dialog.dart"
MODAL = Path(REPO) / "lib/features/ai/ui/settings/widgets/gemini_setup_prompt_modal.dart"
REQUIREMENTS_LINUX = Path(REPO) / "whisper_server/requirements_linux.txt"
WHISPER_README = Path(REPO) / "whisper_server/README.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structural checks
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified Dart files parse without obvious syntax errors."""
    for dart_file in [SETUP_SERVICE, FTUE_DIALOG, MODAL]:
        content = dart_file.read_text()
        assert content.count("{") == content.count("}"), \
            f"Unbalanced braces in {dart_file.name}"
        assert content.count("(") == content.count(")"), \
            f"Unbalanced parentheses in {dart_file.name}"


def test_existing_requirements_intact():
    """Existing requirements files must not be deleted or emptied."""
    for name in ["requirements.txt", "requirements_apple_silicon.txt"]:
        req_file = Path(REPO) / "whisper_server" / name
        content = req_file.read_text()
        assert "torch" in content, f"{name} must still contain torch dependency"
        assert "fastapi" in content, f"{name} must still contain fastapi dependency"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — FTUE prompt streamlining
# ---------------------------------------------------------------------------

def test_ftue_prompt_configs_reduced_to_nine():
    """_getFtuePromptConfigs must return exactly 9 FtuePromptConfig entries (not 18)."""
    content = SETUP_SERVICE.read_text()

    match = re.search(
        r'List<FtuePromptConfig>\s+_getFtuePromptConfigs\(\)\s*\{(.*?)\n\s{2}\}',
        content,
        re.DOTALL,
    )
    assert match, "_getFtuePromptConfigs method not found"

    method_body = match.group(1)
    config_count = len(re.findall(r'FtuePromptConfig\(', method_body))
    assert config_count == 9, \
        f"Expected 9 FtuePromptConfig entries, got {config_count}"


def test_image_prompt_uses_pro_model():
    """Image Prompt Generation must be assigned to 'pro' variant (was 'flash')."""
    content = SETUP_SERVICE.read_text()

    match = re.search(
        r"template:\s*imagePromptGenerationPrompt,\s*\n\s*modelVariant:\s*'(\w+)'",
        content,
    )
    assert match, "imagePromptGenerationPrompt FtuePromptConfig not found"
    variant = match.group(1)
    assert variant == "pro", \
        f"Image Prompt Generation should use 'pro' model, got '{variant}'"


def test_image_prompt_auto_selection_uses_pro():
    """_buildFtueAutomaticPrompts must route image_prompt_generation to proModelId."""
    content = SETUP_SERVICE.read_text()

    match = re.search(
        r"findPromptId\('image_prompt_generation',\s*(\w+)\)",
        content,
    )
    assert match, "image_prompt_generation findPromptId call not found"
    model_param = match.group(1)
    assert model_param == "proModelId", \
        f"image_prompt_generation should use proModelId, got '{model_param}'"


def test_cover_art_prompt_name_updated():
    """Cover Art prompt must be named 'Cover Art Nano Banana Pro'."""
    content = SETUP_SERVICE.read_text()

    assert "Cover Art Nano Banana Pro" in content, \
        "Cover Art prompt should be renamed to 'Cover Art Nano Banana Pro'"
    assert "promptName: 'Cover Art Gemini Pro'" not in content, \
        "Old prompt name 'Cover Art Gemini Pro' should be removed"


def test_dialog_shows_nine_prompts():
    """FtueSetupDialog must show '9 Prompts' (not '18 Prompts')."""
    content = FTUE_DIALOG.read_text()

    assert "'9 Prompts'" in content or '"9 Prompts"' in content, \
        "Dialog should display '9 Prompts'"
    assert "'18 Prompts'" not in content and '"18 Prompts"' not in content, \
        "Dialog should no longer display '18 Prompts'"


def test_modal_barrier_dismissible():
    """GeminiSetupPromptModal must allow barrier dismissal."""
    content = MODAL.read_text()

    assert "barrierDismissible: false" not in content, \
        "Modal should not set barrierDismissible to false"


def test_modal_handles_null_result():
    """Modal must handle null result (temporary dismiss) separately from false (permanent)."""
    content = MODAL.read_text()

    assert "showDialog<bool?>" in content, \
        "showDialog should use nullable bool (bool?) to support temporary dismissal"
    assert "case null:" in content, \
        "Modal must handle null case for temporary dismissal"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — whisper_server requirements_linux.txt
# ---------------------------------------------------------------------------


    content = REQUIREMENTS_LINUX.read_text()

    assert "torch" in content, "requirements_linux.txt must include torch"
    assert "fastapi" in content, "requirements_linux.txt must include fastapi"
    assert "transformers" in content, "requirements_linux.txt must include transformers"
    assert "uvicorn" in content, "requirements_linux.txt must include uvicorn"

    assert "flash-attn" not in content, \
        "requirements_linux.txt should not include flash-attn (CUDA-only)"
    assert "bitsandbytes" not in content, \
        "requirements_linux.txt should not include bitsandbytes (CUDA-only)"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — whisper_server README update
# ---------------------------------------------------------------------------


    assert "requirements_linux" in content, \
        "README must reference requirements_linux.txt"
    assert "requirements_apple_silicon" in content, \
        "README must reference requirements_apple_silicon.txt"

    assert "cuda" in content.lower() or "nvidia" in content.lower(), \
        "README must mention CUDA/NVIDIA platform"
    assert "apple silicon" in content.lower() or "mps" in content.lower(), \
        "README must mention Apple Silicon/MPS platform"
    assert "linux" in content.lower(), \
        "README must mention Linux platform"



    lower = content.lower()
    has_cuda_explanation = ("flash attention" in lower or "quantization" in lower) and "cuda" in lower
    has_linux_explanation = "linux" in lower and ("simplified" in lower or "without cuda" in lower or "cpu" in lower)

    assert has_cuda_explanation, \
        "README should explain CUDA-specific features (flash attention / quantization)"
    assert has_linux_explanation, \
        "README should explain that Linux requirements are simplified (no CUDA deps)"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — AGENTS.md: changelog entry rule
# ---------------------------------------------------------------------------

def test_changelog_updated():
    """CHANGELOG.md must contain an entry for the FTUE changes."""
    changelog = Path(REPO) / "CHANGELOG.md"
    content = changelog.read_text()

    lower = content.lower()
    assert "ftue" in lower or ("prompt" in lower and "18" in content and "9" in content), \
        "CHANGELOG must mention FTUE or prompt count change (18 to 9)"
