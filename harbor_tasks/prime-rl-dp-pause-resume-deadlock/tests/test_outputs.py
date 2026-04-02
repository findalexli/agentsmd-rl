"""
Task: prime-rl-dp-pause-resume-deadlock
Repo: PrimeIntellect-ai/prime-rl @ c2b99e69ce31c71261f56c97fbd2ed467258f940
PR:   #2099

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import enum
import importlib
import inspect
import queue
import sys
import types
from pathlib import Path

REPO = "/workspace/prime-rl"
PATCHES = f"{REPO}/src/prime_rl/inference/patches.py"

# ---------------------------------------------------------------------------
# Mock vllm modules (vllm/torch not installed; tests use lightweight mocks)
# ---------------------------------------------------------------------------


class PauseState(enum.Enum):
    UNPAUSED = 0
    PAUSED = 1


class EngineCoreOutputs:
    def __init__(self, **kwargs):
        self.start_wave = kwargs.get("start_wave")


class Request:
    pass


class EngineCore:
    def __init__(self):
        self.has_coordinator = True
        self.current_wave = 1
        self.engines_running = False
        self.scheduler = types.SimpleNamespace(pause_state=PauseState.UNPAUSED)
        self.output_queue = queue.Queue()

    def add_request(self, request, request_wave=0):
        """Base implementation: no-op (mirrors upstream skeleton)."""
        pass


class DPEngineCoreProc(EngineCore):
    pass


_mock_modules = {
    "vllm": types.ModuleType("vllm"),
    "vllm.v1": types.ModuleType("vllm.v1"),
    "vllm.v1.core": types.ModuleType("vllm.v1.core"),
    "vllm.v1.core.sched": types.ModuleType("vllm.v1.core.sched"),
    "vllm.v1.core.sched.interface": types.ModuleType("vllm.v1.core.sched.interface"),
    "vllm.v1.engine": types.ModuleType("vllm.v1.engine"),
    "vllm.v1.engine.core": types.ModuleType("vllm.v1.engine.core"),
    "vllm.v1.request": types.ModuleType("vllm.v1.request"),
}
_mock_modules["vllm.v1.core.sched.interface"].PauseState = PauseState
_mock_modules["vllm.v1.engine"].EngineCoreOutputs = EngineCoreOutputs
_mock_modules["vllm.v1.engine.core"].EngineCore = EngineCore
_mock_modules["vllm.v1.engine.core"].DPEngineCoreProc = DPEngineCoreProc
_mock_modules["vllm.v1.request"].Request = Request

for _name, _mod in _mock_modules.items():
    sys.modules[_name] = _mod

# ---------------------------------------------------------------------------
# Discover and apply the agent's patch function (name-agnostic)
# ---------------------------------------------------------------------------

BASE_FUNCTIONS = {
    "transformers_v5_compat",
    "_patch_qwen35_lora",
    "monkey_patch_prometheus_stat_logger_for_lora_in_dp_mode",
    "monkey_patch_load_lora_adapter",
    "monkey_patch_LRUCacheWorkerLoRAManager",
    "monkey_patch_tokenize_params_validation",
    "monkey_patch_hermes_tool_parser_thread_safety",
    "monkey_patch_tokenizer_thread_safety",
    "monkey_patch_minimax_m2_for_lora",
    "monkey_patch_harmony_stop_token_propagation",
    "monkey_patch_fused_moe_lora_dp",
}

sys.path.insert(0, f"{REPO}/src")

_patches_mod = importlib.import_module("prime_rl.inference.patches")

for _fname in sorted(dir(_patches_mod)):
    if _fname.startswith("__") or _fname in BASE_FUNCTIONS:
        continue
    _obj = getattr(_patches_mod, _fname)
    if not (inspect.isfunction(_obj) and _obj.__module__ == _patches_mod.__name__):
        continue
    try:
        _obj()
    except Exception:
        pass
    if "add_request" in DPEngineCoreProc.__dict__:
        break


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_engine(current_wave=5, engines_running=False, pause_state=PauseState.UNPAUSED):
    engine = DPEngineCoreProc()
    engine.has_coordinator = True
    engine.current_wave = current_wave
    engine.engines_running = engines_running
    engine.scheduler = types.SimpleNamespace(pause_state=pause_state)
    engine.output_queue = queue.Queue()
    return engine


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """patches.py must be valid Python syntax."""
    src = Path(PATCHES).read_text()
    compile(src, "patches.py", "exec")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_unpaused_old_wave_sends_notification():
    """Unpaused + old wave → sends start_wave notification with engines_running=True."""
    for current, request in [(5, 3), (10, 1), (100, 50)]:
        engine = _make_engine(current_wave=current, engines_running=False,
                              pause_state=PauseState.UNPAUSED)
        engine.add_request(Request(), request_wave=request)

        assert not engine.output_queue.empty(), (
            f"No notification sent for old wave (current={current}, request={request})"
        )
        item = engine.output_queue.get()
        assert isinstance(item, tuple) and item[0] == -1, (
            f"Wrong notification format: {item}"
        )
        assert item[1].start_wave == current, (
            f"start_wave={item[1].start_wave}, expected {current}"
        )
        assert engine.engines_running, "engines_running not set to True"


# [pr_diff] fail_to_pass
def test_new_wave_updates_current_wave():
    """current_wave updated to request_wave when request_wave > current_wave."""
    for pause_state in [PauseState.UNPAUSED, PauseState.PAUSED]:
        for current, request in [(5, 7), (1, 10), (0, 1)]:
            engine = _make_engine(current_wave=current, pause_state=pause_state)
            engine.add_request(Request(), request_wave=request)
            assert engine.current_wave == request, (
                f"current_wave={engine.current_wave}, expected {request} "
                f"(pause={pause_state}, was {current})"
            )


# [pr_diff] pass_to_pass
def test_paused_old_wave_no_notification():
    """Paused + old wave → does NOT send notification (avoids deadlock)."""
    for current, request in [(5, 3), (10, 1), (100, 50)]:
        engine = _make_engine(current_wave=current, engines_running=False,
                              pause_state=PauseState.PAUSED)
        engine.add_request(Request(), request_wave=request)

        assert engine.output_queue.empty(), (
            f"Notification sent when paused (current={current}, request={request}) — "
            "this would cause a deadlock"
        )
        assert not engine.engines_running, (
            "engines_running set to True while paused"
        )


# [pr_diff] pass_to_pass
def test_already_running_no_duplicate():
    """Already running + old wave → does NOT send duplicate notification."""
    for current, request in [(5, 3), (10, 1), (100, 50)]:
        engine = _make_engine(current_wave=current, engines_running=True,
                              pause_state=PauseState.UNPAUSED)
        engine.add_request(Request(), request_wave=request)

        assert engine.output_queue.empty(), (
            f"Duplicate notification sent when already running "
            f"(current={current}, request={request})"
        )
        assert engine.engines_running, "engines_running unexpectedly changed"


# [pr_diff] pass_to_pass
def test_same_wave_noop():
    """Same wave → no notification, no state change."""
    for wave in [0, 1, 5, 100]:
        engine = _make_engine(current_wave=wave, engines_running=False,
                              pause_state=PauseState.UNPAUSED)
        engine.add_request(Request(), request_wave=wave)

        assert engine.output_queue.empty(), (
            f"Notification sent for same wave={wave}"
        )
        assert engine.current_wave == wave, (
            f"current_wave changed to {engine.current_wave} for same wave={wave}"
        )
        assert not engine.engines_running, (
            f"engines_running changed for same wave={wave}"
        )


# [pr_diff] pass_to_pass
def test_no_coordinator_noop():
    """has_coordinator=False means no wave logic runs at all."""
    for current, request in [(5, 3), (5, 7), (5, 5)]:
        engine = _make_engine(current_wave=current, engines_running=False,
                              pause_state=PauseState.UNPAUSED)
        engine.has_coordinator = False
        engine.add_request(Request(), request_wave=request)

        assert engine.output_queue.empty(), (
            f"Notification sent without coordinator (current={current}, request={request})"
        )
        # current_wave and engines_running should be untouched
        assert engine.current_wave == current, (
            f"current_wave changed without coordinator"
        )
        assert not engine.engines_running, (
            "engines_running changed without coordinator"
        )


# ---------------------------------------------------------------------------
# Structural (pr_diff) — integration
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_wired_into_compat():
    """New patch function is called from transformers_v5_compat."""
    src = Path(PATCHES).read_text()
    tree = ast.parse(src)

    base_calls = {"_patch_qwen35_lora"}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "transformers_v5_compat":
            for child in ast.walk(node):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                    if child.func.id not in base_calls and not child.func.id.startswith("_"):
                        return  # Found a new function call — pass
            raise AssertionError(
                "transformers_v5_compat does not call the new patch function"
            )
    raise AssertionError("transformers_v5_compat not found")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_functions_present():
    """transformers_v5_compat and _patch_qwen35_lora still defined."""
    src = Path(PATCHES).read_text()
    tree = ast.parse(src)

    func_names = {node.name for node in ast.walk(tree)
                  if isinstance(node, ast.FunctionDef)}
    for required in ["transformers_v5_compat", "_patch_qwen35_lora"]:
        assert required in func_names, f"Function {required} missing from patches.py"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md rules
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:5 @ c2b99e69
def test_no_unnecessary_try_except():
    """New patch function does not use try/except blocks (AGENTS.md:5)."""
    src = Path(PATCHES).read_text()
    tree = ast.parse(src)

    found_new_func = False
    for node in ast.walk(tree):
        if (isinstance(node, ast.FunctionDef)
                and node.name not in BASE_FUNCTIONS
                and not node.name.startswith("_")):
            found_new_func = True
            for child in ast.walk(node):
                assert not isinstance(child, (ast.Try, ast.ExceptHandler)), (
                    f"Function {node.name} contains unnecessary try/except "
                    "(AGENTS.md: avoid try/except unless really necessary)"
                )
    assert found_new_func, "No new public patch function found in patches.py"
