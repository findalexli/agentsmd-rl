# Task: Harden GitHook Security

The `GitHook` class in `providers/git/src/airflow/providers/git/hooks/git.py` has several security vulnerabilities that need to be addressed.

## 1. Shell Injection via Unquoted SSH Arguments

The `_build_ssh_command` method constructs an SSH command by directly interpolating filesystem paths and user-supplied strings into shell command arguments without any escaping. This makes the following values vulnerable to shell injection via metacharacters (spaces, `;`, `|`, `$(…)`, etc.):

- The `-i` flag argument (SSH private key path)
- The `UserKnownHostsFile=` option value
- The `-F` flag argument (SSH config file path)
- The `ProxyCommand=` option value

When these values contain shell metacharacters, arbitrary commands can be executed. Each of these four values must be properly shell-escaped before being embedded in the SSH command string. The Python `shlex` module provides a `quote()` function for this purpose.

## 2. Credentials Not URL-Encoded in HTTPS URLs

The `_process_git_auth_url` method builds HTTPS clone URLs with embedded credentials by inserting `self.user_name` and `self.auth_token` directly into the URL. Special characters such as `@`, `/`, `:`, or `#` in a username or token can break the URL structure or be misinterpreted.

Additionally, the `.replace()` call that replaces the protocol prefix with the credential-bearing URL replaces **all** occurrences. When the original URL contains the protocol prefix more than once (e.g., in a query parameter), every occurrence gets replaced, corrupting the URL. Only the first occurrence should be replaced.

The fix must URL-encode the credentials using `urllib.parse.quote` (with `safe=""`) before embedding them and limit the protocol replacement to a single occurrence.

## 3. Unvalidated `strict_host_key_checking` Parameter

The `strict_host_key_checking` connection parameter is passed directly to SSH without validation. SSH recognizes only specific values: `"yes"`, `"no"`, `"accept-new"`, `"off"`, and `"ask"`. Invalid values cause confusing SSH errors instead of being caught early with a clear error message.

The fix should define the accepted values and raise a `ValueError` with a message containing "strict_host_key_checking" when an invalid value is provided.

## 4. Boolean Logic Error in Local-Path Detection

The conditional branch that handles local filesystem paths contains a logic error. The current condition uses `or` between two negated checks: `not self.repo_url.startswith("git@")` and `not self.repo_url.startswith("https://")`.

Since no string can start with both `"git@"` and `"https://"` simultaneously, at least one of these negated checks is always true, making the entire condition always true. As a result, remote SSH and HTTPS URLs are misclassified as local paths, and `os.path.expanduser()` is incorrectly applied to them.

The fix should use the correct logical operator so that local path handling is only applied when the URL is neither an SSH git URL nor an HTTPS URL.