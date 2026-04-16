# Fix AttributeError in embeddings utils module

When processing image URLs for embedding functions in the LanceDB Python SDK, attempting to download images from HTTP URLs raises `AttributeError: module 'urllib' has no attribute 'request'`.

## The Problem

The embeddings utility module contains code that attempts to call `urllib.request.urlopen()` to download images, but the `urllib.request` submodule is not available, causing an AttributeError for any HTTP URL input.

## What You Need To Do

1. Locate the embeddings utils module in the Python SDK
2. Identify where `urllib.request.urlopen()` is being called
3. Fix the missing import so that `urllib.request.urlopen()` can be called without AttributeError
4. Ensure the fix follows standard Python import conventions (stdlib imports should be in alphabetical order)

## Expected Behavior

After the fix, the code that downloads images from HTTP URLs should work without raising `AttributeError: module 'urllib' has no attribute 'request'`. The solution must:
- Allow `urllib.request.urlopen()` to be called successfully
- Have imports ordered properly (alphabetically within the standard library section)
- Pass ruff lint and format checks
