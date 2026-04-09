# Self-Audit Report

## Test Summary

**Total Tests: 16**
- Fail-to-pass: 9
- Pass-to-pass: 7

### Fail-to-Pass Tests (must fail on base commit)
1. `test_ssh_command_quotes_key_path_with_spaces` - shlex.quote not used on base
2. `test_ssh_command_quotes_key_path_with_shell_chars` - shlex.quote not used on base
3. `test_ssh_command_quotes_known_hosts_file` - shlex.quote not used on base
4. `test_ssh_command_quotes_ssh_config_file` - shlex.quote not used on base
5. `test_ssh_command_quotes_proxy_command` - shlex.quote not used on base
6. `test_strict_host_key_checking_validation_rejects_invalid` - no validation on base
7. `test_url_encoding_of_username_and_token_https` - no urlquote on base
8. `test_url_encoding_of_username_and_token_http` - no urlquote on base
9. `test_proxy_command_formatting` - uses double quotes on base, single on fixed

### Pass-to-Pass Tests (work on both commits)
1. `test_strict_host_key_checking_accepts_valid_yes` - valid values work on both
2. `test_strict_host_key_checking_accepts_valid_no` - valid values work on both
3. `test_strict_host_key_checking_accepts_valid_accept_new` - valid values work on both
4. `test_url_replace_only_first_occurrence` - only one occurrence in test URL
5. `test_local_path_expanded` - expanduser called correctly on both
6. `test_url_with_tilde_in_middle_unchanged` - expanduser doesn't affect mid-string ~

## Anti-Pattern Check

| Pattern | Status |
|---------|--------|
| 1. Self-referential constant extraction | ✓ None - comparing against shlex.quote/urlquote |
| 2. Import fallback to AST | ✓ None - imports fail = test fails |
| 3. Grep-only frontend tests | ✓ None - calling actual functions |
| 4. Stub-passable tests | ✓ None - asserting return values |
| 5. Superficial guard checks | ✓ None - asserting state changes |
| 6. Single parameter value | ✓ None - multiple test cases |
| 7. Ungated structural tests | ✓ None - all behavioral |
| 8. Compilation-ungated structural | ✓ N/A - Python |
| 9. Keyword stuffing | ✓ None - checking coherence |
| 10. File-exists fallback | ✓ None - no existence checks |

## Alternative Fix Check

An alternative fix that:
- Uses shlex.quote for all user-controlled SSH values ✓
- Validates strict_host_key_checking against allowlist ✓
- URL-encodes username and token ✓
- Fixes the `or` → `and` logic bug ✓
- Limits str.replace to first occurrence ✓

All tests would pass with any correct implementation.

## Manifest Sync

✓ All 16 test functions have matching check entries in eval_manifest.yaml
