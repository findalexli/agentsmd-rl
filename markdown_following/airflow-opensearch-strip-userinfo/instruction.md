# Strip credentials from the OpenSearch host URL when it appears as a task-log key

You are working in the Apache Airflow monorepo at `/workspace/airflow`.
The repository is checked out at the commit immediately before PR #65509
landed; nothing from that PR is applied.

## Background

Airflow's OpenSearch provider ships a task-log handler in
`providers/opensearch/src/airflow/providers/opensearch/log/`. The handler is
configured with an `[opensearch] host` URL — operators commonly embed
credentials in it, e.g.

```
https://elastic:supersecret@opensearch.example.com:9200
```

The OpenSearch client itself uses this full URL (including credentials) to
authenticate with the cluster, and that must keep working.

When the handler renders task logs in the UI, it groups log records by the
host they came from. Each individual log record may carry its own `host`
attribute; when it does, that attribute is used as the group key. When it
does not, the handler falls back to the configured `[opensearch] host`
value as the group key.

## The bug

Because the configured host is used **verbatim** as the fallback group key,
log records that lack a `host` attribute end up keyed by a URL that still
contains `user:password@…`. Those keys are visible in task-log output,
leaking the credentials. (This mirrors a credential-leak fix that already
landed in `providers/elasticsearch` in PR #65349.)

There are **two** call sites that exhibit the bug — the same fallback
logic appears in both
`OpensearchTaskHandler._group_logs_by_host` and
`OpensearchRemoteLogIO._group_logs_by_host`. Both must be fixed.

## Required behaviour

1. The fallback group-key produced by both `_group_logs_by_host`
   methods MUST NOT contain a `user:password@` (or `user@` or `:password@`)
   userinfo segment when the configured host embeds credentials.
2. If the configured host has no userinfo, the fallback key is the host
   string unchanged.
3. The OpenSearch client connection must continue to use the full,
   unredacted host URL — authentication must keep working.
4. Implement the redaction as a **module-level helper named `_strip_userinfo`**
   in `os_task_handler.py` (this name is required because the existing
   non-public test surface for this provider's helper functions imports
   helpers by their module-level names — see the existing imports of
   `_render_log_id`, `_build_log_fields`, `_format_error_detail`,
   `getattr_nested`, `get_os_kwargs_from_config` in
   `providers/opensearch/tests/unit/opensearch/log/test_os_task_handler.py`).

The helper takes a single `url: str` and returns a `str`. It must satisfy
the following input → output contract:

| Input                                                | Output                                       |
| ---------------------------------------------------- | -------------------------------------------- |
| `https://user:pass@opensearch.example.com:9200`      | `https://opensearch.example.com:9200`        |
| `http://USER:PASS@opensearch.example.com`            | `http://opensearch.example.com`              |
| `https://opensearch.example.com:9200`                | `https://opensearch.example.com:9200`        |
| `http://localhost:9200`                              | `http://localhost:9200`                      |
| `https://user@opensearch.example.com`                | `https://opensearch.example.com`             |
| `https://:secret@opensearch.example.com`             | `https://opensearch.example.com`             |
| `not-a-url`                                          | `not-a-url`                                  |
| `""` (empty string)                                  | `""`                                         |

In other words: when the input parses as a URL **with** any userinfo
component, return the URL with the userinfo removed (preserving scheme,
host, port, path, query, fragment); when the input parses as a URL with
no userinfo, or is not URL-shaped at all, return it unchanged.

## Cross-provider documentation

OpenSearch was forked from Elasticsearch and the two providers' task-log
handler code is structurally near-identical. Add an `AGENTS.md` to
**both** `providers/opensearch/` and `providers/elasticsearch/`
documenting the fork relationship, so future agents working on either
side know to check for the equivalent change on the other side.

Each of those `AGENTS.md` files should:

- State that the two providers share most of their task-log handler code.
- Map the mirrored file/class names: `os_task_handler.py` ↔
  `es_task_handler.py`, `os_response.py` ↔ `es_response.py`,
  `os_json_formatter.py` ↔ `es_json_formatter.py`,
  `OpensearchTaskHandler` ↔ `ElasticsearchTaskHandler`,
  `OpensearchRemoteLogIO` ↔ `ElasticsearchRemoteLogIO`.
- Tell future agents that bug fixes / behaviour changes here usually need
  to be cross-applied to the sibling provider, especially for task-log
  handler logic, log grouping/formatting, connection handling,
  URL/credential treatment, and response parsing.
- List legitimate reasons to diverge: upstream client API differences
  (`opensearchpy` vs `elasticsearch`), provider-specific features that
  only one side has, config-gated changes.

These two AGENTS.md files should be near-mirror images of each other
(swap "OpenSearch"/"Elasticsearch" and the file-pair table direction).

## Changelog

Add a note above the latest version header in
`providers/opensearch/docs/changelog.rst` (i.e. between the `Changelog`
heading and the `1.9.0` version section) describing the redaction
behaviour change. The note should make clear that:

- when the `[opensearch] host` config embeds credentials, the log-source
  label in task logs is now the host URL with the `user:password@` portion
  stripped;
- previously the full URL (including credentials) could appear as a
  dictionary key in task-log output when log-hits did not carry a `host`
  field;
- the OpenSearch client itself still connects using the full URL, so
  authentication is unaffected.

No newsfragment is required — this is a provider-package fix, not a core
Airflow change.

## Code Style Requirements

Tests in this task invoke `ruff check` and `ruff format --check` on the
file you edit. Per the repository's root `AGENTS.md`, format and lint every
Python file you modify with `ruff` before finishing:

```
uv run ruff format <file>
uv run ruff check --fix <file>
```

(Plain `ruff check <file>` and `ruff format --check <file>` work too if
`uv` is unavailable.)

Per `AGENTS.md`, imports must remain at the top of the file (no inline
imports). Per `AGENTS.md`, do not use bare `assert` statements in
production code.

## Out of scope

- Don't modify the OpenSearch client construction (`_create_opensearch_client`,
  `format_url`) — connection handling must keep using the full URL.
- Don't change `host_field` semantics — the per-hit `host` attribute, when
  present, still wins over the fallback.
- Don't add a newsfragment.
