FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

RUN mkdir -p /workspace/Ghost /logs/verifier

# Pin Ghost AGENTS.md and CLAUDE.md to the base commit of TryGhost/Ghost#27177
# (parent of merge commit 04df2dd8ec4b3bd2957e0170cfd0d68e56c00ce9).
ARG GHOST_BASE_SHA=1dc488a0e5846ea537aa6c5cceee10ac629a1080
RUN curl -fsSL "https://raw.githubusercontent.com/TryGhost/Ghost/${GHOST_BASE_SHA}/AGENTS.md" \
        -o /workspace/Ghost/AGENTS.md \
 && curl -fsSL "https://raw.githubusercontent.com/TryGhost/Ghost/${GHOST_BASE_SHA}/CLAUDE.md" \
        -o /workspace/Ghost/CLAUDE.md

# Initialize as a tiny git repo so the agent can run `git diff` while editing.
RUN cd /workspace/Ghost \
 && git init -q -b main \
 && git -c user.email=task@local -c user.name=task add -A \
 && git -c user.email=task@local -c user.name=task commit -q -m "base"

WORKDIR /workspace/Ghost
