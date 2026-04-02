FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
  && rm -rf /var/lib/apt/lists/*

ARG REPO_URL=https://github.com/sgl-project/sglang.git
ARG BASE_COMMIT=35720d9969ef404566c0d5801c072bf0085255d1

RUN git clone --filter=blob:none "$REPO_URL" /repo \
  && cd /repo \
  && git checkout "$BASE_COMMIT"

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git for potential patches
RUN git config user.email "test@test.com" && git config user.name "Test"

ENV PYTHONPATH="/repo"