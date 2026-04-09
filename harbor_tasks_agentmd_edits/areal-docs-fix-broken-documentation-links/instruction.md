# Fix Broken Documentation Links

## Problem

After the AReaL docs site was restructured for multilingual support (en/zh), all
documentation page URLs without the language prefix now return 404. Deep links like
`https://inclusionai.github.io/AReaL/tutorial/quickstart.html` are broken because they
need an `/en/` (or `/zh/`) prefix to resolve.

This affects links across multiple files: README.md, CONTRIBUTING.md, pyproject.toml,
example READMEs, issue templates, blog posts, version history docs, and a Python error
message in the codebase.

## Expected Behavior

All documentation links should resolve correctly. Deep links to the docs site should
include the `/en/` language prefix (e.g.,
`https://inclusionai.github.io/AReaL/en/tutorial/quickstart.html`). The README doc
section links should use relative paths to the local markdown sources (e.g.,
`docs/en/tutorial/quickstart.md`).

## Files to Look At

- `README.md` — main project README with many doc links
- `CONTRIBUTING.md` — contributor guide with installation/dev links
- `.github/ISSUE_TEMPLATE/config.yml` — issue template contact links
- `areal/api/alloc_mode.py` — Python error message with a docs URL
- `pyproject.toml` — project metadata with Documentation URL
- `blog/AReaL_v0_3.md` — v0.3 release blog post
- `docs/en/version_history.md` — English version history
- `docs/zh/version_history.md` — Chinese version history
- `examples/countdown/README.md` — countdown example prerequisites
- `examples/tau2/README.md` — tau2 example prerequisites
