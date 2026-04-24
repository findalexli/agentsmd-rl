# Fix Vimeo Shortcode Test

## Problem

The `TestVimeoShortcode` integration test in `tpl/tplimpl/shortcodes_integration_test.go` is failing. The Vimeo video ID used in the test returns unavailable data when fetched, causing the remote data lookup to fail.

Additionally, part of the test (simple mode tests) is currently commented out with a note referencing issue #14649.

## Investigation Steps

1. Run `go test -run TestVimeoShortcode ./tpl/tplimpl/...` to observe the current failure
2. Examine the test code in `tpl/tplimpl/shortcodes_integration_test.go` and the Vimeo template at `tpl/tplimpl/embedded/templates/_shortcodes/vimeo.html`
3. Determine a video ID that returns valid embed data from Vimeo's API
4. Update the test and template to use the working video ID
5. After fixing the video ID, run the test again to determine correct expected values
6. Re-enable the commented simple mode tests

## Expected Behavior

- Running `go test -run TestVimeoShortcode ./tpl/tplimpl/...` should pass
- All test cases (regular mode and simple mode) should execute
- The test should use a video ID that returns valid embed data from Vimeo's API

## Notes

- The test validates output using hash assertions — determine the correct expected values by running the test after fixing the video ID
- When a video ID is not found, the test expects a log warning message
- See `AGENTS.md` in the repo root for coding conventions:
  - Use brief, self-explanatory code
  - Use qt matchers in tests
  - Use latest Hugo layout specifications
  - Run `./check.sh` when done

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `gofmt (Go formatter)`
