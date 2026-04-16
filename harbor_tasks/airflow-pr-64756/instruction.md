# Task: Harden GitHook Security

The `GitHook` class in `providers/git/src/airflow/providers/git/hooks/git.py` has several security vulnerabilities that need to be addressed.

## 1. Shell Injection via Unquoted SSH Arguments

The SSH command builder interpolates filesystem paths and user-supplied strings directly into shell command arguments without any escaping. The following values are vulnerable to injection via shell metacharacters (spaces, `;`, `|`, `$(…)`, etc.):

- `key_path` — the `-i` flag argument
- `self.known_hosts_file` — the `UserKnownHostsFile=` option value
- `self.ssh_config_file` — the `-F` flag argument
- `self.host_proxy_cmd` — the `ProxyCommand=` option value

Each of these four values must be properly shell-escaped before being embedded in the SSH command string to prevent arbitrary command execution.

## 2. Credentials Not URL-Encoded in HTTPS URLs

When building HTTPS clone URLs with embedded credentials, `self.user_name` and `self.auth_token` are inserted raw into the URL. Characters such as `@`, `/`, `:`, or `#` in a username or token break the URL structure.

The `quote` function from `urllib.parse` must be imported under the alias `urlquote` and used to encode both `self.user_name` and `self.auth_token` with `safe=""` before they are embedded into the URL.

Additionally, the `.replace()` call that swaps `"https://"` (and similarly `"http://"`) for the credential-bearing URL replaces **all** occurrences in the string. When the original URL contains the protocol prefix more than once (e.g., in a query parameter or path component), every occurrence gets replaced, corrupting the URL. The replacement must be limited to the first match only — pass `count=1` to `.replace()`.

## 3. Unvalidated `strict_host_key_checking` Parameter

The `strict_host_key_checking` connection parameter is passed directly to SSH without any validation. SSH only recognizes the values `"yes"`, `"no"`, `"accept-new"`, `"off"`, and `"ask"`. Any other value causes confusing SSH errors instead of being caught early.

Define the accepted values in a class-level attribute named `_VALID_STRICT_HOST_KEY_CHECKING` (as a `set` or `frozenset`). When the provided value is not in this set, raise a `ValueError` whose message includes the word `strict_host_key_checking`.

## 4. Boolean Logic Error in Local-Path Detection

The conditional branch that handles local filesystem paths (triggering `os.path.expanduser()`) is guarded by two negated `startswith` checks — one for `"git@"` and one for `"https://"`. These two negated conditions are joined with `or`, making the overall disjunction true whenever **either** check fails. Since no string can start with both `"git@"` and `"https://"` simultaneously, at least one negated check always succeeds, so the condition is always true. Remote SSH and HTTPS URLs are therefore misclassified as local paths, and `os.path.expanduser()` is applied to them instead of being reserved for genuine local filesystem paths.
