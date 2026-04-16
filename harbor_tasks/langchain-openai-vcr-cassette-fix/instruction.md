# Fix VCR Cassette Playback in langchain-openai Tests

## Problem

The VCR (Video Cassette Recorder) cassette playback is broken in `langchain-openai` integration tests. VCR is used to record and replay HTTP interactions, allowing tests to run without making real API calls.

## Symptoms

VCR-backed tests fail when running in playback-only mode (no API key needed). The test suite uses pre-recorded cassettes, but playback matching fails due to two issues:

1. **Request matching mismatch**: The VCR configuration in `conftest.py` uses a request matcher that compares URI (URL) values, but the URIs in recorded cassettes are redacted to `**REDACTED**` by a `before_record_request` hook. This causes every request to fail matching.

2. **Cassette content mismatch**: Some test input strings in `test_responses_api.py` do not match what was recorded in the cassettes. The cassettes contain specific strings that must be used exactly as recorded.

## Files to Examine

### `libs/partners/openai/tests/conftest.py`

Contains the VCR configuration fixture `vcr_config()` that sets up request/response recording and matching. The issue involves how `match_on` interacts with `before_record_request`.

### `libs/partners/openai/tests/integration_tests/chat_models/test_responses_api.py`

Contains integration tests using VCR cassettes. The test input strings used when invoking the LLM must match the content recorded in the cassettes exactly.

## Required Changes

1. In `conftest.py`: Modify the VCR configuration to exclude URI matching from `match_on`, since URIs are redacted during recording and cannot be matched during playback.

2. In `test_responses_api.py`: Update test input strings to match the exact content in the pre-recorded cassettes. Inspect the cassettes to find the correct strings.

## Verification

After fixing, run VCR tests in playback-only mode:

```bash
cd libs/partners/openai
OPENAI_API_KEY=sk-fake uv run --group test pytest --record-mode=none -m vcr --ignore=tests/integration_tests/chat_models/test_azure_standard.py tests/integration_tests/ -v
```

The tests should pass without making real API calls.

## Notes

- The cassettes are pre-recorded with specific content
- URIs are redacted to `**REDACTED**` during recording
- Test input strings must match the cassettes exactly for playback to work
- Look for cassette files in the `tests/cassettes/` directory to find the recorded strings
