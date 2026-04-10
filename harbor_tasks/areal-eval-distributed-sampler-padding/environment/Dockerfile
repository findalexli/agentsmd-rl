FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update &&     apt-get install -y --no-install-recommends         git curl ca-certificates build-essential tmux &&     rm -rf /var/lib/apt/lists/*

# Clone repo at the base commit (before the fix)
ARG REPO_URL=https://github.com/inclusionAI/AReaL.git
ARG BASE_COMMIT=fdca82dc09e76052fd6ee2fe22afcdc5ff044743

RUN git clone "$REPO_URL" /repo &&     cd /repo &&     git checkout "$BASE_COMMIT"

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install CPU-only torch + minimal deps for testing the dataloader module
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu &&     pip install --no-cache-dir torchdata datasets ruff

# Configure git for patch application
RUN git config --global user.email "test@test.com" &&     git config --global user.name "Test"

ENV PYTHONPATH=/repo
