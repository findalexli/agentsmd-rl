FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global advice.detachedHead false

ARG REPO_URL=https://github.com/THUDM/slime.git
ARG BASE_COMMIT=e8e4b64872a469e1c0b85653650a3f76154c88dd

RUN git clone "$REPO_URL" /workspace/slime && \
    cd /workspace/slime && \
    git checkout "$BASE_COMMIT"

# Install minimal deps: transformers for AutoTokenizer type import in mask_utils.py
RUN pip install --no-cache-dir transformers

ENV PYTHONPATH=/workspace/slime

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/slime