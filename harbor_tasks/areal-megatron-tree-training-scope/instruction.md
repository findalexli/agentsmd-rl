# Tree Training Broken in MegatronEngine

## Problem

When running MegatronEngine with tree training enabled (`enable_tree_training=true` and `bridge_cls="mbridge"`), the tree-training behavior is silently skipped during model construction. The `patch_bridge_for_tree_training` context manager is used to configure bridge behavior for tree training, but the model construction via `make_mcore_model` happens outside that context. This means the model is built without the tree-training patches applied, leading to incorrect initialization — tree attention and related configurations are not activated.

The issue is in the `initialize` method of `MegatronEngine`. The context manager scope does not cover all the operations that need tree-training patching.

## Expected Behavior

All operations that depend on tree-training bridge patching — including bridge building, config creation, and model construction — should execute within the `patch_bridge_for_tree_training` context. When tree training is enabled, `make_mcore_model` should run with the tree-training patches active, so tree attention is properly initialized.

## Files to Look At

- `areal/engine/megatron_engine.py` — Contains the `MegatronEngine.initialize()` method where the tree-training context manager and model construction occur
