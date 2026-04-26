FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git init /workspace/slime && \
    cd /workspace/slime && \
    git remote add origin https://github.com/THUDM/slime.git && \
    git fetch --depth=1 origin 887fba113b512156098509c808b7bc93a8386b47 && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/slime

ENV PYTHONPATH="/workspace/slime"

# psutil is needed by the fix (import psutil) and by tests for verification
# pytest and pytest-json-ctrf needed for test reporting
# ruff, isort, black needed for pass-to-pass linting tests
# Additional dependencies for repo tests
RUN pip install --no-cache-dir \
    psutil pytest pytest-json-ctrf ruff isort black \
    torch numpy packaging pyyaml omegaconf \
    tqdm httpx pybase64 pylatexenc sympy aiohttp pillow \
    transformers

RUN mkdir -p /logs/verifier
