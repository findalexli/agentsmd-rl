# Fix Security Vulnerabilities in GitHook

The GitHook class in `providers/git/src/airflow/providers/git/hooks/git.py` has several security vulnerabilities that need to be addressed:

## 1. Command Injection via SSH Arguments

The `_build_ssh_command` method constructs SSH commands by directly interpolating user-controlled values without proper shell escaping:

- `key_path` is inserted directly: `f"-i {key_path}"`
- `known_hosts_file` is inserted directly: `f"-o UserKnownHostsFile={known_hosts_file}"`
- `ssh_config_file` is inserted directly: `f"-F {ssh_config_file}"`
- `host_proxy_cmd` is inserted directly: `f'-o ProxyCommand="{host_proxy_cmd}"'`

If these values contain shell metacharacters (spaces, quotes, semicolons, etc.), they could allow command injection. Fix this by using `shlex.quote()` to properly escape these values.

## 2. Missing Validation for strict_host_key_checking

The `strict_host_key_checking` parameter is passed directly to SSH's `StrictHostKeyChecking` option without validation. Invalid values could cause SSH to fail or behave unexpectedly. Add validation against the standard SSH values: `yes`, `no`, `accept-new`, `off`, `ask`. Raise a `ValueError` for invalid values.

## 3. URL Injection via Unencoded Credentials

In `_process_git_auth_url`, when embedding `user_name` and `auth_token` into HTTP/HTTPS URLs, the values are not URL-encoded:

```python
self.repo_url = self.repo_url.replace("https://", f"https://{self.user_name}:{self.auth_token}@")
```

If these values contain URL-reserved characters (`@`, `:`, `/`, `?`, etc.), they could corrupt the URL or enable injection attacks. Use `urllib.parse.quote` to properly encode these values.

## 4. Logic Bug in URL Protocol Check

There's a logic bug in the protocol check:

```python
elif not self.repo_url.startswith("git@") or not self.repo_url.startswith("https://"):
```

This condition is always true because a URL cannot start with both `git@` AND `https://`. The `or` should be `and`.

## 5. Unbounded String Replacement

The `str.replace` calls for inserting credentials into URLs replace ALL occurrences of the protocol prefix, not just the first. This could corrupt URLs that contain the protocol string elsewhere. Use `str.replace(old, new, 1)` to limit replacement to the first occurrence.

## Files to Modify

- `providers/git/src/airflow/providers/git/hooks/git.py`

## Testing

Run the git hook tests to verify your changes:

```bash
uv run --project providers/git pytest providers/git/tests/unit/git/hooks/test_git.py -xvs
```

Your fix should ensure:
1. All user-controlled values in SSH commands are properly shell-escaped
2. Invalid `strict_host_key_checking` values raise `ValueError`
3. URL credentials are properly URL-encoded
4. The `git@`/`https://` logic correctly handles all URL types
5. URL replacement only affects the first occurrence
