# Bug: CI failures in Language Models Tests after refactoring model loader

## Problem

The `Language Models Tests (Extra Standard) 2` CI suite is failing with memory-related errors. The failures started after a recent change to the model loader infrastructure.

## How to reproduce

The `Language Models Tests (Extra Standard) 2` CI suite fails with memory-related errors. The failures are related to how context managers are used around model initialization and inspection operations.

## Expected behavior

Model inspection/logging operations (like `log_model_inspection`) should not run inside the device context — they should only run within the dtype context. Only model initialization (like `initialize_model`) should happen within the device context scope. The `set_default_torch_dtype` context manager must properly wrap dtype-sensitive operations while the device context wraps only device-specific operations.
