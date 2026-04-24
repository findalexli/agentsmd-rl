FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
  && rm -rf /var/lib/apt/lists/*

# Install matplotlib for chart generation tests
RUN pip install --no-cache-dir matplotlib

ARG REPO_URL=https://github.com/sgl-project/sglang.git
ARG BASE_COMMIT=9b4dd274787ce4a778b7688c65c33598282a6559

RUN git clone --filter=blob:none "$REPO_URL" /repo \
  && cd /repo \
  && git checkout "$BASE_COMMIT"

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git for potential patches
RUN git config user.email "test@test.com" && git config user.name "Test"

ENV PYTHONPATH="/repo"

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages black flake8 isort 2>/dev/null || pip install --no-cache-dir black flake8 isort
