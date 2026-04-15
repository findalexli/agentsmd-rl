# Fix Security Vulnerabilities in GitHook

The `GitHook` class in the Airflow git provider package has several security vulnerabilities and logic bugs that need to be addressed. This class handles SSH command construction and git URL processing for repository operations.

## 1. Shell Injection via Unescaped SSH Arguments

When building SSH commands, user-supplied file paths and commands are embedded directly into the command string without shell escaping. This affects the identity file (`-i`), known hosts file (`UserKnownHostsFile=`), SSH config file (`-F`), and proxy command (`ProxyCommand=`) arguments.

**Symptom:** A key path containing spaces (e.g., `/path/with spaces/to/key`) breaks SSH command parsing because the path is not treated as a single token. Similarly, a path containing shell metacharacters like semicolons (e.g., `/path/to/key;rm -rf /`) enables shell injection. Each of these arguments must be properly shell-escaped so that values containing special characters appear as single-quoted tokens in the command string. For example:

- Key path `/path/with spaces/to/key`: the SSH command should contain the fragment `-i '/path/with spaces/to/key'`
- Key path `/path/to/key;rm -rf /`: the SSH command should contain the fragment `-i '/path/to/key;rm -rf /'`
- Known hosts path `/path/with spaces/known_hosts`: the command should contain `UserKnownHostsFile='/path/with spaces/known_hosts'`
- SSH config path `/path/with spaces/config`: the command should contain `-F '/path/with spaces/config'`
- Proxy command `ssh -W %h:%p bastion.example.com`: the command should contain `ProxyCommand='ssh -W %h:%p bastion.example.com'`

## 2. No Validation of strict_host_key_checking

The `strict_host_key_checking` parameter accepts any arbitrary string and passes it directly to SSH's `StrictHostKeyChecking` option without checking whether the value is valid.

**Expected behavior:** Only the standard SSH values should be accepted: `yes`, `no`, `accept-new`, `off`, and `ask`. When an unsupported value is provided, a `ValueError` must be raised. The error message must contain the text `"Invalid strict_host_key_checking value"` and should indicate the set of valid options. Accepted values should appear in the SSH command as `StrictHostKeyChecking=<value>`.

## 3. Unencoded Credentials in HTTP/HTTPS URLs

When embedding a username and authentication token into HTTP or HTTPS repository URLs, the values are interpolated as-is without URL encoding. Characters that are reserved in URLs (such as `@`, `/`, `:`, `+`, `=`) in the username or token corrupt the URL structure.

**Symptom:** A username like `user@domain.com` causes the `@` to be misinterpreted as the credential/host separator, and a token like `token/with+special=chars` breaks URL parsing.

**Expected behavior:** Both values must be fully percent-encoded with no characters treated as safe (i.e., every reserved character must be encoded, including `/` and `+`). For example:
- `user@domain.com` should be encoded as `user%40domain.com` (the `@` becomes `%40`)
- `token/with+special=chars` should be encoded as `token%2Fwith%2Bspecial%3Dchars` (`/` → `%2F`, `+` → `%2B`, `=` → `%3D`)

## 4. Logic Bug in URL Protocol Dispatch

The URL processing method handles different types of repository URLs (HTTPS, HTTP, SSH-style `git@`, and local paths). There is a logic error in how the method decides whether a URL is a local filesystem path. Some non-local URLs are incorrectly routed through `os.path.expanduser`, when they should be left alone. The condition that guards the local-path branch is too broad and matches URLs it should not.

**Expected behavior:**
- A path like `~/repos/myrepo` (starting with `~`) should be expanded via `os.path.expanduser`
- A path like `/path/to/repo/~user/branch` should remain unchanged (tilde is not at the start, this is not a home directory path)
- Only URLs that are neither `git@` SSH-style URLs nor `https://` or `http://` URLs should enter the local-path expansion branch

## 5. Unbounded Protocol Prefix Replacement

When injecting credentials into URLs, the protocol prefix (e.g., `https://`) is replaced throughout the entire URL string rather than only at the beginning. A URL containing the protocol string more than once will have every occurrence modified, corrupting the URL.

**Expected behavior:** Only the first occurrence of the protocol prefix should be replaced. For a URL like `https://github.com/apache/airflow.git` with auth credentials injected, the resulting URL should contain exactly one `https://` prefix (and zero standalone `http://` prefixes).

## Testing

Run the git hook tests to verify your changes:

```bash
uv run --project providers/git pytest providers/git/tests/unit/git/hooks/test_git.py -xvs
```
