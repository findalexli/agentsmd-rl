There is a crash bug in sglang's DetokenizerManager error handling. When the `DetokenizerManager` constructor raises an exception inside `run_detokenizer_process()` in `python/sglang/srt/managers/detokenizer_manager.py`, the except block tries to call `manager.maybe_clear_socket_mapping()` -- but if the constructor itself failed, `manager` was never assigned, so Python raises an `UnboundLocalError`.

Fix the error handling path in `run_detokenizer_process()` so that it does not crash with an `UnboundLocalError` when the `DetokenizerManager` constructor fails before `manager` is assigned.
