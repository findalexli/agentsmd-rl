FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pytest==8.3.4 pytest-json-ctrf==0.3.5 pyyaml==6.0.2

WORKDIR /workspace

# Sparse, blob-filtered shallow clone of PostHog at the PR's base commit.
# We materialize only the files relevant to this markdown-authoring task —
# the agent can still see the repo's instruction surface (AGENTS.md, CLAUDE.md,
# AI_POLICY.md, the PR template) without paying for the 400 MB working tree.
RUN git clone --filter=blob:none --no-checkout --depth=1 \
        --shallow-submodules \
        https://github.com/PostHog/posthog.git posthog || \
    (mkdir -p posthog && cd posthog && git init -q && \
     git remote add origin https://github.com/PostHog/posthog.git)

WORKDIR /workspace/posthog

RUN git fetch --depth=1 --filter=blob:none origin \
        66dd528f2d3b4db785cd4f37e5a319713b8df56c && \
    git config core.sparseCheckout true && \
    git sparse-checkout init --no-cone && \
    printf '%s\n' \
        'AGENTS.md' \
        'AI_POLICY.md' \
        'CLAUDE.md' \
        'CONTRIBUTING.md' \
        'README.md' \
        '.github/pull_request_template.md' \
        '.github/CODEOWNERS' \
        > .git/info/sparse-checkout && \
    git checkout 66dd528f2d3b4db785cd4f37e5a319713b8df56c

RUN mkdir -p /logs/verifier

WORKDIR /workspace/posthog
