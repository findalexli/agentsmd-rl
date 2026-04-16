"""Tests for transformers generation typing fix task.

This task verifies:
1. Code changes: type annotations, new protocols, import fixes
2. Config changes: AGENTS.md updated to mention type checker
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/transformers")
SRC = REPO / "src" / "transformers"

def test_agents_md_updated_for_type_checker():
    """AGENTS.md must be updated to mention type checker in make style description.

    Origin: pr_diff - This is part of the PR changes to documentation.
    The AGENTS.md file should reflect that make style now runs type checking.
    """
    agents_md = REPO / "AGENTS.md"
    content = agents_md.read_text()

    # Base commit: "make style`: runs formatters and linters"
    # Gold patch: "make style`: runs formatters, linters and type checker"
    assert "type checker" in content, "AGENTS.md should mention 'type checker' in make style description"
    assert "linters and type checker" in content or "linters, and type checker" in content, \
        "AGENTS.md should mention that make style runs linters AND type checker"


def test_typing_module_moved_to_root():
    """_typing.py must be moved from utils/ to src/transformers/ root.

    Origin: pr_diff - Part of the code refactoring in the PR.
    The module was moved and expanded with new protocols.
    """
    # New location should exist
    new_location = SRC / "_typing.py"
    assert new_location.exists(), f"_typing.py should exist at {new_location}"

    # Old location should NOT exist (or should have different content)
    old_location = SRC / "utils" / "_typing.py"
    if old_location.exists():
        # If it still exists, it should be different (git rename tracking)
        content = old_location.read_text()
        # Check if it's the old short version (no GenerativePreTrainedModel)
        assert "GenerativePreTrainedModel" not in content, \
            "Old location should not have the new protocol classes"


def test_generative_protocol_exists():
    """GenerativePreTrainedModel protocol must be defined in _typing.py.

    Origin: pr_diff - New protocol added for type checking generation module.
    This protocol documents the interface that GenerationMixin expects.
    """
    typing_module = SRC / "_typing.py"
    content = typing_module.read_text()

    assert "class GenerativePreTrainedModel(Protocol)" in content, \
        "GenerativePreTrainedModel protocol should be defined"
    assert "config: Any" in content, "Protocol should have config attribute"
    assert "def forward" in content, "Protocol should have forward method"


def test_whisper_config_protocol_exists():
    """WhisperGenerationConfigLike protocol must be defined in _typing.py.

    Origin: pr_diff - New protocol for Whisper-specific generation config.
    """
    typing_module = SRC / "_typing.py"
    content = typing_module.read_text()

    assert "class WhisperGenerationConfigLike(Protocol)" in content, \
        "WhisperGenerationConfigLike protocol should be defined"
    assert "no_timestamps_token_id" in content, \
        "Protocol should have no_timestamps_token_id field"


def test_check_types_script_created():
    """utils/check_types.py wrapper script must be created.

    Origin: pr_diff - New utility script for running ty type checker.
    This wrapper handles the type checking invocation.
    """
    check_types = REPO / "utils" / "check_types.py"
    assert check_types.exists(), "utils/check_types.py should exist"

    content = check_types.read_text()
    assert "ty check" in content, "Script should invoke 'ty check'"
    assert "subprocess.run" in content, "Script should use subprocess to run ty"


def test_logging_import_updated():
    """logging.py must import from new _typing location.

    Origin: pr_diff - Import path updated after module move.
    """
    logging_file = SRC / "utils" / "logging.py"
    content = logging_file.read_text()

    # Should import from new location (parent package)
    assert "from .._typing import TransformersLogger" in content, \
        "logging.py should import from .._typing (new location)"

    # Should NOT import from old location
    assert "from ._typing import TransformersLogger" not in content, \
        "logging.py should not import from old utils/_typing location"


def test_generation_utils_has_self_annotations():
    """Generation utils.py must have self: GenerativePreTrainedModel annotations.

    Origin: pr_diff - Type annotations added for the ty type checker.
    The self parameter should be annotated with the protocol.
    """
    utils_file = SRC / "generation" / "utils.py"
    content = utils_file.read_text()

    # Should import the protocol
    assert "from .._typing import GenerativePreTrainedModel" in content, \
        "utils.py should import GenerativePreTrainedModel"

    # Should have at least one self annotation with the protocol
    assert 'self: "GenerativePreTrainedModel"' in content, \
        "Methods should have self: GenerativePreTrainedModel type annotation"


def test_candidate_generator_has_cast():
    """candidate_generator.py should use typing.cast for type safety.

    Origin: pr_diff - Type cast added for prev_assistant_ids access.
    """
    candidate_file = SRC / "generation" / "candidate_generator.py"
    content = candidate_file.read_text()

    assert "from typing import" in content and "cast" in content, \
        "Should import cast from typing"

    assert "cast(torch.LongTensor, self.prev_assistant_ids)" in content or \
           "prev_assistant_ids = cast" in content, \
        "Should use cast() for prev_assistant_ids type narrowing"


def test_streamers_has_proper_annotations():
    """streamers.py should have updated type annotations.

    Origin: pr_diff - Type annotations for tokenizer and token_cache.
    """
    streamers_file = SRC / "generation" / "streamers.py"
    content = streamers_file.read_text()

    # Should import from proper location
    assert "from ..tokenization_utils_base import PreTrainedTokenizerBase" in content, \
        "Should import PreTrainedTokenizerBase (not AutoTokenizer)"

    # Should have typed token_cache
    assert "token_cache: list[int]" in content, \
        "token_cache should be typed as list[int]"


def test_makefile_updated():
    """Makefile should use new check_types.py wrapper.

    Origin: pr_diff - Makefile updated to use new type checking wrapper.
    """
    makefile = REPO / "Makefile"
    content = makefile.read_text()

    # Should use new wrapper script
    assert "python utils/check_types.py" in content, \
        "Makefile should use utils/check_types.py wrapper"

    # Should define ty_check_dirs
    assert "ty_check_dirs" in content, \
        "Makefile should define ty_check_dirs variable"

    # Should NOT use old direct ty invocation pattern in style/check-repo
    assert "ty check $(call get_py_files" not in content, \
        "Should not use old ty invocation with get_py_files"


def test_imports_resolve():
    """Critical imports should resolve without errors.

    Origin: static - Verify the module structure is valid.
    This is a pass_to_pass test that verifies basic functionality.
    """
    # Test that we can import the main modules
    result = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, 'src'); " +
         "from transformers._typing import TransformersLogger; " +
         "print('TransformersLogger imported successfully')"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"Import failed: {result.stderr}"
    assert "TransformersLogger imported successfully" in result.stdout


def test_generation_config_has_tensor_annotations():
    """GenerationConfig should have tensor type annotations.

    Origin: pr_diff - New tensor type annotations added.
    """
    config_file = SRC / "generation" / "configuration_utils.py"
    content = config_file.read_text()

    # Should have tensor type annotations for special tokens
    assert "_bos_token_tensor" in content, "Should have _bos_token_tensor annotation"
    assert "_eos_token_tensor" in content, "Should have _eos_token_tensor annotation"


def test_stopping_criteria_tensor_type():
    """stopping_criteria.py should use torch.Tensor not torch.tensor.

    Origin: pr_diff - Fixed incorrect torch.tensor (function) vs torch.Tensor (type).
    """
    stopping_file = SRC / "generation" / "stopping_criteria.py"
    content = stopping_file.read_text()

    # Should use torch.Tensor (the type) not torch.tensor (the function)
    assert "-> dict[str, torch.Tensor]" in content, \
        "Should use torch.Tensor (capital T) as the return type"

    # Should NOT have torch.tensor as type annotation
    lines = content.split('\n')
    for line in lines:
        if 'torch.tensor' in line and '->' in line:
            assert False, f"Found torch.tensor (function) used as type annotation: {line}"


def test_model_signature_alignments():
    """Model files should have aligned method signatures.

    Origin: pr_diff - clvp, musicgen, musicgen_melody signatures aligned.
    """
    # Check clvp
    clvp_file = SRC / "models" / "clvp" / "modeling_clvp.py"
    if clvp_file.exists():
        content = clvp_file.read_text()
        # Should have non-None default for model_kwargs (removed = None)
        assert "model_kwargs: dict[str, torch.Tensor]," in content or \
               "model_kwargs: dict[str, torch.Tensor]" in content, \
            "clvp _prepare_model_inputs should have updated signature"

    # Check musicgen
    musicgen_file = SRC / "models" / "musicgen" / "modeling_musicgen.py"
    if musicgen_file.exists():
        content = musicgen_file.read_text()
        assert "model_kwargs: dict[str, torch.Tensor]," in content or \
               "model_kwargs: dict[str, torch.Tensor]" in content, \
            "musicgen _maybe_initialize_input_ids_for_generation should have updated signature"

    # Check musicgen_melody
    musicgen_melody_file = SRC / "models" / "musicgen_melody" / "modeling_musicgen_melody.py"
    if musicgen_melody_file.exists():
        content = musicgen_melody_file.read_text()
        assert "model_kwargs: dict[str, torch.Tensor]," in content or \
               "model_kwargs: dict[str, torch.Tensor]" in content, \
            "musicgen_melody should have updated signature"
