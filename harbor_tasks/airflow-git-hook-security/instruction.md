# Fix Security Vulnerabilities in GitHook

The GitHook class in `providers/git/src/airflow/providers/git/hooks/git.py` has several security vulnerabilities and logic bugs that need to be addressed.

## 1. Shell Injection via Unescaped SSH Arguments

When building SSH commands, user-supplied file paths and commands are embedded directly into the command string without shell escaping. This affects the identity file (`-i`), known hosts file (`UserKnownHostsFile=`), SSH config file (`-F`), and proxy command (`ProxyCommand=`) arguments.

**Symptom:** A key path containing spaces (e.g., `/path/with spaces/to/key`) breaks SSH command parsing because the path is not treated as a single token. Similarly, a path containing shell metacharacters like semicolons (e.g., `/path/to/key;rm -rf /`) enables shell injection. Each of these arguments must be properly shell-escaped so that values containing special characters are passed as single tokens.

## 2. No Validation of strict_host_key_checking

The `strict_host_key_checking` parameter accepts any arbitrary string and passes it directly to SSH's `StrictHostKeyChecking` option without checking whether the value is valid.

**Expected behavior:** Only the standard SSH values should be accepted: `yes`, `no`, `accept-new`, `off`, and `ask`. When an unsupported value is provided, a `ValueError` must be raised. The error message must contain the text `"Invalid strict_host_key_checking value"` and should indicate the set of valid options.

## 3. Unencoded Credentials in HTTP/HTTPS URLs

When embedding a username and authentication token into HTTP or HTTPS repository URLs, the values are interpolated as-is without URL encoding. Characters that are reserved in URLs (such as `@`, `/`, `:`, `+`, `=`) in the username or token corrupt the URL structure.

**Symptom:** A username like `user@domain.com` causes the `@` to be misinterpreted as the credential/host separator, and a token like `token/with+special=chars` breaks URL parsing. Both values must be fully percent-encoded (including `/` and `+`) before being placed into the URL.

## 4. Logic Bug in URL Protocol Dispatch

The URL processing logic has a conditional chain that dispatches based on URL scheme (HTTPS with auth, HTTP with auth, HTTP without auth, SSH-style `git@` URLs, and local filesystem paths). The final branch, intended only for local filesystem paths, has a boolean condition that always evaluates to true regardless of the input URL. This causes remote URLs not matched by earlier conditions to incorrectly enter the local-path expansion branch. The condition should only be true when the URL is neither a `git@` SSH URL nor an `https://` URL.

## 5. Unbounded Protocol Prefix Replacement

When injecting credentials into URLs, the protocol prefix (e.g., `https://`) is replaced throughout the entire URL string. Since the replacement is not limited to the first occurrence, any URL containing the protocol string more than once will have every occurrence modified, corrupting the URL. Only the first match should be replaced.

## Files to Modify

- `providers/git/src/airflow/providers/git/hooks/git.py`

## Testing

Run the git hook tests to verify your changes:

```bash
uv run --project providers/git pytest providers/git/tests/unit/git/hooks/test_git.py -xvs
```
