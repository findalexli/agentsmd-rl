# Fix: AutoProcessor.from_pretrained silently dropping hub kwargs

## Problem

When calling `AutoProcessor.from_pretrained` with hub-related keyword arguments, the arguments are silently discarded and never reach the internal file-caching function. This prevents users from controlling caching, authentication, or versioning when loading processors through the auto class.

## Expected Behavior

The following 9 hub kwargs must all be forwarded to the internal `cached_file` function:

- `cache_dir`
- `force_download`
- `proxies`
- `token`
- `revision`
- `local_files_only`
- `subfolder`
- `repo_type`
- `user_agent`

The following kwargs must NOT be forwarded (they are not hub-related):

- `_from_auto`
- `processor_class`
- `task`
- `trust_remote_code`
- `torch_dtype`

## Additional Requirements

- The code must pass `ruff check` linting without errors.
- The code must pass `ruff format --check` without errors.
- Any unused imports in the modified file must be removed.
