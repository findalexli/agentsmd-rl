# Strengthen agent guardrails on the Copilot provider package

The Copilot provider package at `packages/opencode/src/provider/sdk/copilot/`
is a small compatibility shim used **only** for GitHub Copilot. Other
providers — including all OpenAI-compatible providers and the majority of
providers that talk to completions/responses APIs — do **not** use this
code path.

The current README in that directory has a short note telling agents not
to edit these files, but agents keep modifying them anyway because the
warnings are weak and easy to miss. Two changes are needed.

## What's wrong today

`packages/opencode/src/provider/sdk/copilot/README.md` currently reads:

> This is a temporary package used primarily for GitHub Copilot compatibility.
>
> Avoid making changes to these files unless you only want to affect the Copilot provider.
>
> Also, this should ONLY be used for the Copilot provider.

Two problems:

1. The wording is too soft. Agents working on a generic provider change
   (e.g., adding behavior to OpenAI-compatible providers) edit these
   Copilot-only files because nothing makes the scope unmistakable.
2. The directory has no `AGENTS.md`, which is the file most coding agents
   look for when entering a sub-tree. So agents that scan for an
   `AGENTS.md` per-directory never see the warning at all.

## What you need to do

### 1. Add an `AGENTS.md` in the Copilot directory

Create a new file at
`packages/opencode/src/provider/sdk/copilot/AGENTS.md` whose **content
is the same as the directory's `README.md`**. The reading agent (and
any tooling that resolves it via `cat`) should see identical text from
either path. A symlink whose target is `README.md` is a clean way to do
this — agents that look for `AGENTS.md` will then read the same
warnings without you having to keep two files in sync. A regular file
with the same content is also acceptable.

### 2. Rewrite the warnings in `README.md`

The intro line must stay:

> This is a temporary package used primarily for GitHub Copilot compatibility.

Replace the two warning lines with these (preserve the exact wording —
the sharpness of the message is the point):

- Replace `Avoid making changes to these files unless you only want to affect the Copilot provider.` with:

  > These DO NOT apply for openai-compatible providers or majority of providers supporting completions/responses apis. THIS IS ONLY FOR GITHUB COPILOT!!!

- Replace `Also, this should ONLY be used for the Copilot provider.` with:

  > Avoid making edits to these files

Do not modify any other files in the repository.

## Required content (verbatim)

`packages/opencode/src/provider/sdk/copilot/README.md` must contain
each of the following as substrings:

- `This is a temporary package used primarily for GitHub Copilot compatibility.`
- `These DO NOT apply for openai-compatible providers or majority of providers supporting completions/responses apis. THIS IS ONLY FOR GITHUB COPILOT!!!`
- `Avoid making edits to these files`

It must **not** contain either of the old phrases:

- `Avoid making changes to these files unless you only want to affect the Copilot provider.`
- `Also, this should ONLY be used for the Copilot provider.`

`packages/opencode/src/provider/sdk/copilot/AGENTS.md` must exist and,
when read, must yield the same content as the README in that directory.
